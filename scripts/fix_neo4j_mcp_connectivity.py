#!/usr/bin/env python3
"""Fix Neo4j Connectivity for MCP Containers.

This script diagnoses and fixes connectivity issues between MCP containers
and the Neo4j database, ensuring proper network configuration and authentication.
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Neo4jMCPConnectivityFixer:
    """Fixes Neo4j connectivity issues for MCP containers."""

    def __init__(self) -> None:
        """Initialize the connectivity fixer."""
        self.project_root = Path(__file__).parent.parent
        self.cursor_dir = self.project_root / ".cursor"

    def get_neo4j_container_info(self) -> dict | None:
        """Get information about the running Neo4j container."""
        try:
            # Find Neo4j container
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=neo4j", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True,
            )

            containers = result.stdout.strip().split("\n")
            neo4j_containers = [c for c in containers if c and "neo4j" in c]

            if not neo4j_containers:
                logger.error("No Neo4j container found running")
                return None

            container_name = neo4j_containers[0]

            # Get detailed container information
            inspect_result = subprocess.run(
                ["docker", "inspect", container_name],
                capture_output=True,
                text=True,
                check=True,
            )

            container_info = json.loads(inspect_result.stdout)[0]

            return {
                "name": container_name,
                "network": next(
                    iter(container_info["NetworkSettings"]["Networks"].keys())
                ),
                "ip_address": next(
                    iter(container_info["NetworkSettings"]["Networks"].values())
                )["IPAddress"],
                "aliases": next(
                    iter(container_info["NetworkSettings"]["Networks"].values())
                )["Aliases"],
                "env": container_info["Config"]["Env"],
            }

        except Exception as e:
            logger.error(f"Failed to get Neo4j container info: {e}")
            return None

    def extract_neo4j_auth(self, env_vars: list[str]) -> tuple[str, str]:
        """Extract Neo4j authentication from container environment."""
        for env_var in env_vars:
            if env_var.startswith("NEO4J_AUTH="):
                auth_string = env_var.split("=", 1)[1]
                if "/" in auth_string:
                    username, password = auth_string.split("/", 1)
                    return username, password
        return "neo4j", "neo4j"  # defaults

    def test_neo4j_connectivity_from_host(self, container_info: dict) -> bool:
        """Test Neo4j connectivity from host using environment variables."""
        try:
            import neo4j

            # Load environment variables
            env_file = self.project_root / ".env"
            env_vars = {}
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key] = value

            uri = env_vars.get("NEO4J_URI", "bolt://localhost:7687")
            username = env_vars.get("NEO4J_USERNAME", "neo4j")
            password = env_vars.get("NEO4J_PASSWORD", "neo4j")

            driver = neo4j.GraphDatabase.driver(uri, auth=(username, password))

            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                logger.info(f"✅ Host connectivity test passed: {test_value}")

            driver.close()
            return True

        except Exception as e:
            logger.error(f"❌ Host connectivity test failed: {e}")
            return False

    def test_neo4j_connectivity_from_container(self, container_info: dict) -> bool:
        """Test Neo4j connectivity from within the Docker network."""
        try:
            network_name = container_info["network"]
            neo4j_host = (
                "neo4j"
                if "neo4j" in container_info["aliases"]
                else container_info["name"]
            )

            # Extract auth from container
            username, password = self.extract_neo4j_auth(container_info["env"])

            # Test connection using a temporary container
            test_cmd = [
                "docker",
                "run",
                "--rm",
                "--network",
                network_name,
                "neo4j:5.15-community",
                "cypher-shell",
                "-a",
                f"bolt://{neo4j_host}:7687",
                "-u",
                username,
                "-p",
                password,
                "RETURN 1 as test",
            ]

            result = subprocess.run(
                test_cmd, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0 and "1" in result.stdout:
                logger.info("✅ Container network connectivity test passed")
                return True
            else:
                logger.error(f"❌ Container network test failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Container connectivity test failed: {e}")
            return False

    def start_mcp_server_with_fixes(self, server_name: str) -> bool:
        """Start an MCP server with proper network configuration."""
        try:
            # Load MCP configuration
            config_file = self.cursor_dir / "mcp_servers.json"
            with open(config_file) as f:
                config = json.load(f)

            server_config = config["mcpServers"].get(server_name)
            if not server_config:
                logger.error(f"Server configuration not found: {server_name}")
                return False

            # Build Docker command
            cmd = [server_config["command"]] + server_config["args"]

            # Set up environment variables
            env = {}
            if "env" in server_config:
                # Load .env file for variable substitution
                env_file = self.project_root / ".env"
                env_vars = {}
                if env_file.exists():
                    with open(env_file) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                key, value = line.split("=", 1)
                                env_vars[key] = value

                # Substitute environment variables
                for key, value in server_config["env"].items():
                    if value.startswith("${") and value.endswith("}"):
                        var_name = value[2:-1]
                        env[key] = env_vars.get(var_name, value)
                    else:
                        env[key] = value

            logger.info(f"Starting {server_name} with command: {' '.join(cmd)}")

            # Remove existing container if it exists
            subprocess.run(
                ["docker", "rm", "-f", server_name],
                capture_output=True,
                stderr=subprocess.DEVNULL,
            )

            # Start the container
            env_vars = {**dict(os.environ), **env}
            subprocess.run(cmd, env=env_vars, capture_output=True, text=True)

            # Wait a moment for startup
            time.sleep(3)

            # Check if container is running
            check_result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={server_name}",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
            )

            is_running = server_name in check_result.stdout

            if is_running:
                logger.info(f"✅ {server_name} started successfully")
                return True
            else:
                # Check logs for errors
                logs_result = subprocess.run(
                    ["docker", "logs", server_name], capture_output=True, text=True
                )
                logger.error(
                    f"❌ {server_name} failed to start. Logs: {logs_result.stdout}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to start {server_name}: {e}")
            return False

    def test_mcp_server_functionality(self, server_name: str) -> dict:
        """Test the functionality of an MCP server."""
        result = {"running": False, "logs": "", "error": None}

        try:
            # Check if container is running
            check_result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={server_name}",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
            )

            result["running"] = server_name in check_result.stdout

            # Get logs
            logs_result = subprocess.run(
                ["docker", "logs", "--tail", "20", server_name],
                capture_output=True,
                text=True,
            )
            result["logs"] = logs_result.stdout

            if not result["running"]:
                result["error"] = "Container not running"
            elif (
                "error" in result["logs"].lower() or "failed" in result["logs"].lower()
            ):
                result["error"] = "Errors found in logs"

        except Exception as e:
            result["error"] = str(e)

        return result

    def fix_all_neo4j_connectivity(self) -> dict:
        """Comprehensive fix for all Neo4j MCP connectivity issues."""
        logger.info("🔧 Starting comprehensive Neo4j MCP connectivity fix...")

        results = {
            "neo4j_container": None,
            "host_connectivity": False,
            "container_connectivity": False,
            "mcp_servers": {},
            "summary": {},
        }

        # Step 1: Get Neo4j container information
        logger.info("📊 Getting Neo4j container information...")
        container_info = self.get_neo4j_container_info()
        results["neo4j_container"] = container_info

        if not container_info:
            results["summary"]["error"] = "Neo4j container not found"
            return results

        logger.info(f"Found Neo4j container: {container_info['name']}")
        logger.info(f"Network: {container_info['network']}")
        logger.info(f"Aliases: {container_info['aliases']}")

        # Step 2: Test host connectivity
        logger.info("🔗 Testing Neo4j connectivity from host...")
        results["host_connectivity"] = self.test_neo4j_connectivity_from_host(
            container_info
        )

        # Step 3: Test container network connectivity
        logger.info("🐳 Testing Neo4j connectivity from container network...")
        results["container_connectivity"] = self.test_neo4j_connectivity_from_container(
            container_info
        )

        # Step 4: Start and test Neo4j MCP servers
        neo4j_servers = ["neo4j-memory", "neo4j-cypher"]

        for server_name in neo4j_servers:
            logger.info(f"🚀 Starting and testing {server_name}...")

            start_success = self.start_mcp_server_with_fixes(server_name)
            time.sleep(5)  # Wait for startup

            test_result = self.test_mcp_server_functionality(server_name)

            results["mcp_servers"][server_name] = {
                "start_success": start_success,
                "test_result": test_result,
            }

        # Step 5: Generate summary
        successful_servers = sum(
            1
            for server_data in results["mcp_servers"].values()
            if server_data["test_result"]["running"]
            and not server_data["test_result"]["error"]
        )

        results["summary"] = {
            "neo4j_found": bool(container_info),
            "host_connectivity": results["host_connectivity"],
            "container_connectivity": results["container_connectivity"],
            "servers_tested": len(neo4j_servers),
            "servers_successful": successful_servers,
            "success_rate": f"{successful_servers}/{len(neo4j_servers)}",
        }

        return results

    def print_results(self, results: dict) -> None:
        """Print a comprehensive results report."""
        print("\n" + "=" * 80)
        print("🔧 NEO4J MCP CONNECTIVITY FIX REPORT")
        print("=" * 80)

        # Neo4j Container Info
        print("\n📊 NEO4J CONTAINER")
        print("-" * 40)
        if results["neo4j_container"]:
            container = results["neo4j_container"]
            print(f"✅ Container: {container['name']}")
            print(f"   Network: {container['network']}")
            print(f"   IP: {container['ip_address']}")
            print(f"   Aliases: {', '.join(container['aliases'])}")
        else:
            print("❌ Neo4j container not found")

        # Connectivity Tests
        print("\n🔗 CONNECTIVITY TESTS")
        print("-" * 40)
        print(
            f"Host connectivity: {'✅ PASS' if results['host_connectivity'] else '❌ FAIL'}"
        )
        print(
            f"Container network: {'✅ PASS' if results['container_connectivity'] else '❌ FAIL'}"
        )

        # MCP Servers
        print("\n🖥️ MCP SERVERS")
        print("-" * 40)
        for server_name, server_data in results["mcp_servers"].items():
            test_result = server_data["test_result"]
            status = (
                "✅ RUNNING"
                if test_result["running"] and not test_result["error"]
                else "❌ FAILED"
            )
            print(f"{server_name}: {status}")

            if test_result["error"]:
                print(f"   Error: {test_result['error']}")

            if test_result["logs"]:
                # Show last few lines of logs
                log_lines = test_result["logs"].strip().split("\n")[-3:]
                for line in log_lines:
                    if line.strip():
                        print(f"   Log: {line.strip()}")

        # Summary
        print("\n📊 SUMMARY")
        print("-" * 40)
        summary = results["summary"]
        if summary.get("error"):
            print(f"❌ Error: {summary['error']}")
        else:
            print(f"Neo4j Container: {'✅' if summary['neo4j_found'] else '❌'}")
            print(
                f"Host Connectivity: {'✅' if summary['host_connectivity'] else '❌'}"
            )
            print(
                f"Container Connectivity: {'✅' if summary['container_connectivity'] else '❌'}"
            )
            print(f"MCP Servers: {summary['success_rate']} successful")

            if summary["servers_successful"] == summary["servers_tested"]:
                print("🎉 All Neo4j MCP connectivity issues resolved!")
            else:
                print("⚠️ Some issues remain - check individual server logs")

        print("=" * 80)


def main() -> int:
    """Run the Neo4j MCP connectivity fixer."""

    fixer = Neo4jMCPConnectivityFixer()

    try:
        results = fixer.fix_all_neo4j_connectivity()
        fixer.print_results(results)

        # Save results to file
        results_file = Path("neo4j_mcp_fix_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"📄 Detailed results saved to: {results_file}")

        # Return appropriate exit code
        summary = results["summary"]
        if summary.get("error"):
            return 1
        elif summary["servers_successful"] == summary["servers_tested"]:
            return 0
        else:
            return 1

    except Exception as e:
        logger.error(f"❌ Fix process failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
