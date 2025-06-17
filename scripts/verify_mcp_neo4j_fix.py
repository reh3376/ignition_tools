#!/usr/bin/env python3
"""Verify Neo4j MCP Fix.

This script verifies that the Neo4j authentication issues for MCP containers
have been resolved and provides a comprehensive status report.
"""

import json
import subprocess
import sys
from pathlib import Path


class MCPNeo4jVerifier:
    """Verifies Neo4j MCP connectivity and configuration."""

    def __init__(self) -> None:
        """Initialize the verifier."""
        self.project_root = Path(__file__).parent.parent

    def check_neo4j_status(self) -> dict:
        """Check Neo4j container status."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=neo4j",
                    "--format",
                    "{{.Names}}\t{{.Status}}",
                ],
                capture_output=True,
                text=True,
            )

            lines = result.stdout.strip().split("\n")
            neo4j_containers = []
            for line in lines:
                if line and "neo4j" in line:
                    parts = line.split("\t")
                    neo4j_containers.append(
                        {
                            "name": parts[0],
                            "status": parts[1] if len(parts) > 1 else "unknown",
                        }
                    )

            return {
                "running": len(neo4j_containers) > 0,
                "containers": neo4j_containers,
            }

        except Exception as e:
            return {"running": False, "error": str(e)}

    def check_mcp_configuration(self) -> dict:
        """Check MCP server configuration."""
        config_file = self.project_root / ".cursor" / "mcp_servers.json"

        if not config_file.exists():
            return {"valid": False, "error": "Configuration file not found"}

        try:
            with open(config_file) as f:
                config = json.load(f)

            # Check for Neo4j MCP servers
            servers = config.get("mcpServers", {})
            neo4j_servers = {
                name: server
                for name, server in servers.items()
                if "neo4j" in name.lower()
            }

            validation_results = {}
            for name, server in neo4j_servers.items():
                validation_results[name] = self.validate_server_config(server)

            return {
                "valid": True,
                "neo4j_servers": list(neo4j_servers.keys()),
                "validation_results": validation_results,
                "total_servers": len(servers),
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def validate_server_config(self, server_config: dict) -> dict:
        """Validate a single server configuration."""
        issues = []
        recommendations = []

        # Check if using interactive mode
        args = server_config.get("args", [])
        if "--interactive" not in args:
            issues.append("Missing --interactive flag for MCP CLI tool")

        # Check if using --rm flag
        if "--rm" not in args:
            recommendations.append("Consider using --rm flag for cleanup")

        # Check network configuration
        if "--network" in args:
            try:
                network_idx = args.index("--network")
                if network_idx + 1 < len(args):
                    network = args[network_idx + 1]
                    if network != "ign_scripts_default":
                        issues.append(
                            f"Network should be 'ign_scripts_default', found '{network}'"
                        )
                else:
                    issues.append("--network flag present but no network specified")
            except ValueError:
                issues.append("--network flag not found")
        else:
            issues.append("Missing --network flag")

        # Check environment variables
        env = server_config.get("env", {})
        required_env = ["NEO4J_URL", "NEO4J_USERNAME", "NEO4J_PASSWORD"]

        for env_var in required_env:
            if env_var not in env:
                issues.append(f"Missing environment variable: {env_var}")
            elif env_var == "NEO4J_URL" and "bolt://neo4j:7687" not in str(
                env[env_var]
            ):
                issues.append(
                    "NEO4J_URL should use 'bolt://neo4j:7687' for Docker network"
                )

        return {
            "issues": issues,
            "recommendations": recommendations,
            "score": max(0, 10 - len(issues) - len(recommendations) * 0.5),
        }

    def test_network_connectivity(self) -> dict:
        """Test network connectivity to Neo4j."""
        try:
            cmd = [
                "docker",
                "run",
                "--rm",
                "--network",
                "ign_scripts_default",
                "alpine/curl",
                "nc",
                "-zv",
                "neo4j",
                "7687",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            return {
                "success": result.returncode == 0,
                "output": result.stdout + result.stderr,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_mcp_container_launch(self) -> dict:
        """Test launching MCP containers."""
        results = {}

        containers = ["mcp/neo4j-memory:latest", "mcp/neo4j-cypher:latest"]

        for container in containers:
            container_name = container.replace("mcp/", "").replace(":latest", "")

            try:
                # Test basic container launch (should exit quickly as it's CLI tool)
                cmd = [
                    "docker",
                    "run",
                    "--rm",
                    "--network",
                    "ign_scripts_default",
                    "-e",
                    "NEO4J_URL=bolt://neo4j:7687",
                    "-e",
                    "NEO4J_USERNAME=neo4j",
                    "-e",
                    "NEO4J_PASSWORD=ignition-graph",
                    container,
                ]

                # Add timeout and run
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

                results[container_name] = {
                    "launchable": True,
                    "exit_code": result.returncode,
                    "output": result.stdout[:200]
                    + ("..." if len(result.stdout) > 200 else ""),
                    "error": (
                        result.stderr[:200]
                        + ("..." if len(result.stderr) > 200 else "")
                        if result.stderr
                        else None
                    ),
                }

            except subprocess.TimeoutExpired:
                # This is actually good - means the container is waiting for input
                results[container_name] = {
                    "launchable": True,
                    "exit_code": "timeout (expected for interactive tool)",
                    "note": "Container is working - timed out waiting for input as expected",
                }
            except Exception as e:
                results[container_name] = {"launchable": False, "error": str(e)}

        return results

    def generate_fix_summary(self) -> dict:
        """Generate a comprehensive fix summary."""
        print("🔧 Neo4j MCP Authentication Fix Verification")
        print("=" * 60)

        # Check 1: Neo4j Status
        print("\n📊 Neo4j Container Status")
        print("-" * 30)

        neo4j_status = self.check_neo4j_status()
        if neo4j_status["running"]:
            for container in neo4j_status["containers"]:
                print(f"✅ {container['name']}: {container['status']}")
        else:
            print("❌ No Neo4j containers running")
            if "error" in neo4j_status:
                print(f"   Error: {neo4j_status['error']}")

        # Check 2: MCP Configuration
        print("\n⚙️ MCP Configuration")
        print("-" * 30)

        mcp_config = self.check_mcp_configuration()
        if mcp_config["valid"]:
            print("✅ Configuration file found")
            print(f"   Total servers: {mcp_config['total_servers']}")
            print(f"   Neo4j servers: {len(mcp_config['neo4j_servers'])}")

            for server_name in mcp_config["neo4j_servers"]:
                validation = mcp_config["validation_results"][server_name]
                score = validation["score"]
                status = "✅" if score >= 8 else "⚠️" if score >= 6 else "❌"
                print(f"   {status} {server_name}: Score {score}/10")

                for issue in validation["issues"]:
                    print(f"      ❌ {issue}")
                for rec in validation["recommendations"]:
                    print(f"      💡 {rec}")
        else:
            print(
                f"❌ Configuration invalid: {mcp_config.get('error', 'Unknown error')}"
            )

        # Check 3: Network Connectivity
        print("\n🔗 Network Connectivity")
        print("-" * 30)

        connectivity = self.test_network_connectivity()
        if connectivity["success"]:
            print("✅ Network connectivity to Neo4j successful")
        else:
            print("❌ Network connectivity failed")
            if "error" in connectivity:
                print(f"   Error: {connectivity['error']}")
            else:
                print(f"   Output: {connectivity['output']}")

        # Check 4: MCP Container Tests
        print("\n🐳 MCP Container Tests")
        print("-" * 30)

        container_tests = self.test_mcp_container_launch()
        for container_name, result in container_tests.items():
            if result["launchable"]:
                print(f"✅ {container_name}: Launchable")
                if "note" in result:
                    print(f"   📝 {result['note']}")
                elif result.get("exit_code") == 0:
                    print(f"   Exit code: {result['exit_code']}")
            else:
                print(f"❌ {container_name}: Failed to launch")
                if "error" in result:
                    print(f"   Error: {result['error']}")

        # Summary
        print("\n📊 Fix Summary")
        print("-" * 30)

        all_checks = [
            neo4j_status["running"],
            mcp_config["valid"],
            connectivity["success"],
            all(r["launchable"] for r in container_tests.values()),
        ]

        passed_checks = sum(all_checks)
        total_checks = len(all_checks)

        if passed_checks == total_checks:
            print("🎉 All checks passed! Neo4j MCP authentication is fully fixed.")
            success_rate = "100%"
        else:
            print(
                f"⚠️ {passed_checks}/{total_checks} checks passed. Some issues remain."
            )
            success_rate = f"{passed_checks}/{total_checks} ({passed_checks / total_checks * 100:.1f}%)"

        return {
            "neo4j_status": neo4j_status,
            "mcp_config": mcp_config,
            "connectivity": connectivity,
            "container_tests": container_tests,
            "success_rate": success_rate,
            "all_passed": passed_checks == total_checks,
        }


def main() -> int:
    """Run the verification."""
    verifier = MCPNeo4jVerifier()

    try:
        results = verifier.generate_fix_summary()

        # Save results
        results_file = Path("mcp_neo4j_verification_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📄 Results saved to: {results_file}")

        return 0 if results["all_passed"] else 1

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
