#!/usr/bin/env python3
"""Comprehensive MCP Tools Testing Script.

This script provides a complete assessment of MCP (Model Context Protocol) tools
and servers defined in Cursor settings, including connectivity tests, configuration
validation, and functionality reports.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MCPTestSuite:
    """Comprehensive MCP testing suite."""

    def __init__(self) -> None:
        """Initialize the MCP test suite."""
        self.project_root = Path(__file__).parent.parent
        self.cursor_dir = self.project_root / ".cursor"
        self.results: dict[str, Any] = {
            "configuration": {},
            "docker": {},
            "servers": {},
            "connectivity": {},
            "environment": {},
            "issues": [],
            "recommendations": [],
        }

    def load_environment_variables(self) -> dict[str, str]:
        """Load environment variables from .env file."""
        env_file = self.project_root / ".env"
        env_vars = {}

        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key] = value

        return env_vars

    def test_docker_availability(self) -> tuple[bool, str]:
        """Test if Docker is available and running."""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True)
            version = result.stdout.strip()

            # Test if Docker daemon is running
            subprocess.run(["docker", "info"], capture_output=True, text=True, check=True)

            return True, version
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return False, str(e)

    def test_mcp_configuration(self) -> dict[str, Any]:
        """Test MCP server configuration."""
        config_file = self.cursor_dir / "mcp_servers.json"

        if not config_file.exists():
            return {
                "valid": False,
                "error": f"Configuration file not found: {config_file}",
            }

        try:
            with open(config_file) as f:
                config = json.load(f)

            servers = config.get("mcpServers", {})

            return {
                "valid": True,
                "servers_count": len(servers),
                "servers": list(servers.keys()),
                "config": config,
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def test_docker_images(self) -> dict[str, Any]:
        """Test availability of Docker images for MCP servers."""
        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
                capture_output=True,
                text=True,
                check=True,
            )

            available_images = result.stdout.strip().split("\n")

            # Filter MCP-related images
            mcp_images = [
                img
                for img in available_images
                if any(keyword in img.lower() for keyword in ["mcp", "neo4j", "github", "context", "commander"])
            ]

            return {
                "available": True,
                "total_images": len(available_images),
                "mcp_images": mcp_images,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def test_running_containers(self) -> dict[str, Any]:
        """Test currently running MCP-related containers."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Image}}"],
                capture_output=True,
                text=True,
                check=True,
            )

            containers = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        name, status, image = parts[0], parts[1], parts[2]
                        containers.append({"name": name, "status": status, "image": image})

            # Filter MCP-related containers
            mcp_containers = [
                c
                for c in containers
                if any(
                    keyword in c["name"].lower() or keyword in c["image"].lower()
                    for keyword in ["mcp", "neo4j", "github", "context", "commander"]
                )
            ]

            return {
                "available": True,
                "total_containers": len(containers),
                "mcp_containers": mcp_containers,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def test_neo4j_connectivity(self, env_vars: dict[str, str]) -> dict[str, Any]:
        """Test Neo4j connectivity."""
        try:
            # Try to import neo4j driver
            import neo4j

            uri = env_vars.get("NEO4J_URI", "bolt://localhost:7687")
            username = env_vars.get("NEO4J_USERNAME", "neo4j")
            password = env_vars.get("NEO4J_PASSWORD", "")

            if not password:
                return {
                    "connected": False,
                    "error": "Neo4j password not configured in environment variables",
                }

            driver = neo4j.GraphDatabase.driver(uri, auth=(username, password))

            # Test connection
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]

                # Get database info
                db_info = session.run("CALL dbms.components() YIELD name, versions").data()

            driver.close()

            return {
                "connected": True,
                "uri": uri,
                "username": username,
                "test_result": test_value,
                "db_info": db_info,
            }

        except ImportError:
            return {"connected": False, "error": "neo4j driver not installed"}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def test_server_accessibility(self, config: dict[str, Any]) -> dict[str, Any]:
        """Test accessibility of configured MCP servers."""
        servers = config.get("config", {}).get("mcpServers", {})
        server_tests = {}

        for server_name, server_config in servers.items():
            test_result = self.test_individual_server(server_name, server_config)
            server_tests[server_name] = test_result

        return server_tests

    def test_individual_server(self, server_name: str, server_config: dict[str, Any]) -> dict[str, Any]:
        """Test an individual MCP server."""
        if server_config.get("command") != "docker":
            return {
                "accessible": False,
                "error": "Non-docker servers not supported in this test",
            }

        # Check if required image exists
        args = server_config.get("args", [])
        if len(args) < 4:  # docker run -d --name container-name image-name
            return {"accessible": False, "error": "Invalid Docker command arguments"}

        try:
            # Extract image name from args
            image_name = None
            for _i, arg in enumerate(args):
                if arg.startswith("ghcr.io/") or ":" in arg:
                    image_name = arg
                    break

            if not image_name:
                return {
                    "accessible": False,
                    "error": "Could not determine image name from configuration",
                }

            # Check if image exists locally
            result = subprocess.run(
                [
                    "docker",
                    "images",
                    image_name,
                    "--format",
                    "{{.Repository}}:{{.Tag}}",
                ],
                capture_output=True,
                text=True,
            )

            if result.stdout.strip():
                return {
                    "accessible": True,
                    "image_available": True,
                    "image_name": image_name,
                }
            else:
                return {
                    "accessible": False,
                    "image_available": False,
                    "image_name": image_name,
                    "error": f"Docker image not available locally: {image_name}",
                }

        except Exception as e:
            return {"accessible": False, "error": str(e)}

    def check_environment_variables(self, env_vars: dict[str, str]) -> dict[str, Any]:
        """Check required environment variables."""
        required_vars = [
            "NEO4J_URI",
            "NEO4J_USERNAME",
            "NEO4J_PASSWORD",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
        ]

        missing_vars = []
        present_vars = []

        for var in required_vars:
            if env_vars.get(var):
                present_vars.append(var)
            else:
                missing_vars.append(var)

        # Check for alternative GitHub token
        if "GITHUB_PERSONAL_ACCESS_TOKEN" in missing_vars and env_vars.get("GITHUB_TOKEN"):
            missing_vars.remove("GITHUB_PERSONAL_ACCESS_TOKEN")
            present_vars.append("GITHUB_TOKEN (alternative)")

        return {
            "all_present": len(missing_vars) == 0,
            "present_vars": present_vars,
            "missing_vars": missing_vars,
            "total_env_vars": len(env_vars),
        }

    def generate_recommendations(self) -> list[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Docker recommendations
        if not self.results["docker"].get("available"):
            recommendations.append("Install and start Docker to enable MCP server functionality")

        # Configuration recommendations
        if not self.results["configuration"].get("valid"):
            recommendations.append("Fix MCP server configuration in .cursor/mcp_servers.json")

        # Environment variable recommendations
        env_check = self.results["environment"]
        if env_check.get("missing_vars"):
            recommendations.append(f"Add missing environment variables: {', '.join(env_check['missing_vars'])}")

        # Neo4j recommendations
        neo4j_test = self.results["connectivity"].get("neo4j", {})
        if not neo4j_test.get("connected"):
            recommendations.append("Fix Neo4j connectivity for MCP memory functionality")

        # Server accessibility recommendations
        servers = self.results["servers"]
        inaccessible_servers = [name for name, test in servers.items() if not test.get("accessible")]
        if inaccessible_servers:
            recommendations.append(f"Fix accessibility for MCP servers: {', '.join(inaccessible_servers)}")

        # Image availability recommendations
        docker_images = self.results["docker"].get("images", {})
        if docker_images.get("available") and len(docker_images.get("mcp_images", [])) == 0:
            recommendations.append("Pull required Docker images for MCP servers")

        return recommendations

    def run_comprehensive_test(self) -> dict[str, Any]:
        """Run comprehensive MCP testing suite."""
        logger.info("🧪 Starting comprehensive MCP testing suite...")

        # Load environment variables
        env_vars = self.load_environment_variables()
        self.results["environment"] = self.check_environment_variables(env_vars)

        # Test Docker
        docker_available, docker_info = self.test_docker_availability()
        self.results["docker"]["available"] = docker_available
        self.results["docker"]["info"] = docker_info

        if docker_available:
            self.results["docker"]["images"] = self.test_docker_images()
            self.results["docker"]["containers"] = self.test_running_containers()

        # Test MCP configuration
        config_test = self.test_mcp_configuration()
        self.results["configuration"] = config_test

        # Test server accessibility
        if config_test.get("valid"):
            self.results["servers"] = self.test_server_accessibility(config_test)

        # Test Neo4j connectivity
        self.results["connectivity"]["neo4j"] = self.test_neo4j_connectivity(env_vars)

        # Generate recommendations
        self.results["recommendations"] = self.generate_recommendations()

        return self.results

    def print_report(self) -> None:
        """Print a comprehensive test report."""
        print("\n" + "=" * 80)
        print("🔍 MCP TOOLS COMPREHENSIVE TEST REPORT")
        print("=" * 80)

        # Environment Variables Section
        print("\n📋 ENVIRONMENT VARIABLES")
        print("-" * 40)
        env = self.results["environment"]
        if env.get("all_present"):
            print("✅ All required environment variables are present")
        else:
            print(f"❌ Missing variables: {', '.join(env.get('missing_vars', []))}")
        print(f"   Present: {', '.join(env.get('present_vars', []))}")
        print(f"   Total environment variables: {env.get('total_env_vars', 0)}")

        # Docker Section
        print("\n🐳 DOCKER STATUS")
        print("-" * 40)
        docker = self.results["docker"]
        if docker.get("available"):
            print(f"✅ Docker is available: {docker.get('info', '')}")

            images = docker.get("images", {})
            if images.get("available"):
                print(f"   📦 Total images: {images.get('total_images', 0)}")
                print(f"   🔧 MCP-related images: {len(images.get('mcp_images', []))}")
                for img in images.get("mcp_images", [])[:5]:  # Show first 5
                    print(f"      • {img}")

            containers = docker.get("containers", {})
            if containers.get("available"):
                print(f"   🏃 Running containers: {containers.get('total_containers', 0)}")
                print(f"   🔧 MCP-related containers: {len(containers.get('mcp_containers', []))}")
                for container in containers.get("mcp_containers", []):
                    print(f"      • {container['name']}: {container['status']}")
        else:
            print(f"❌ Docker not available: {docker.get('info', '')}")

        # Configuration Section
        print("\n⚙️  MCP CONFIGURATION")
        print("-" * 40)
        config = self.results["configuration"]
        if config.get("valid"):
            print("✅ Configuration is valid")
            print(f"   📊 Configured servers: {config.get('servers_count', 0)}")
            for server in config.get("servers", []):
                print(f"      • {server}")
        else:
            print(f"❌ Configuration invalid: {config.get('error', '')}")

        # Server Accessibility Section
        print("\n🖥️  MCP SERVER ACCESSIBILITY")
        print("-" * 40)
        servers = self.results["servers"]
        for server_name, test in servers.items():
            if test.get("accessible"):
                print(f"✅ {server_name}: Accessible")
                if test.get("image_available"):
                    print(f"   📦 Image available: {test.get('image_name', '')}")
            else:
                print(f"❌ {server_name}: {test.get('error', 'Not accessible')}")

        # Connectivity Section
        print("\n🔗 CONNECTIVITY TESTS")
        print("-" * 40)
        connectivity = self.results["connectivity"]
        neo4j = connectivity.get("neo4j", {})
        if neo4j.get("connected"):
            print(f"✅ Neo4j: Connected to {neo4j.get('uri', '')}")
            print(f"   👤 User: {neo4j.get('username', '')}")
            if neo4j.get("db_info"):
                print(f"   📊 Database components: {len(neo4j.get('db_info', []))}")
        else:
            print(f"❌ Neo4j: {neo4j.get('error', 'Connection failed')}")

        # Recommendations Section
        print("\n💡 RECOMMENDATIONS")
        print("-" * 40)
        recommendations = self.results.get("recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("🎉 No issues found! All MCP tools are properly configured.")

        # Summary Section
        print("\n📊 SUMMARY")
        print("-" * 40)
        total_issues = len(recommendations)
        if total_issues == 0:
            print("✅ All MCP tools are functioning correctly")
        else:
            print(f"⚠️  Found {total_issues} issue(s) that need attention")

        print("=" * 80)


def main() -> int:
    """Run the comprehensive MCP test suite."""
    test_suite = MCPTestSuite()

    try:
        results = test_suite.run_comprehensive_test()
        test_suite.print_report()

        # Save detailed results to file
        results_file = Path("mcp_test_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"📄 Detailed results saved to: {results_file}")

        # Return exit code based on issues found
        issues_count = len(results.get("recommendations", []))
        return 0 if issues_count == 0 else 1

    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
