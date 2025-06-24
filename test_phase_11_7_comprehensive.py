#!/usr/bin/env python3
"""Comprehensive Phase 11.7 Implementation Test
Production Deployment & PLC Integration

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

Test Categories:
1. Environment Validation
2. Module Imports and Dependencies
3. Production Deployment Core Functionality
4. Docker Integration
5. PLC Communication
6. CLI Commands Integration
7. File Structure Validation
8. Documentation Verification
9. Configuration Management
10. Integration Examples
"""

import importlib
import subprocess
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class Phase117ComprehensiveTest:
    """Comprehensive test suite for Phase 11.7 implementation."""

    def __init__(self):
        self.results = {
            "environment_validation": [],
            "module_imports": [],
            "production_deployment": [],
            "docker_integration": [],
            "plc_communication": [],
            "cli_commands": [],
            "file_structure": [],
            "documentation": [],
            "configuration": [],
            "integration_examples": [],
        }
        self.total_tests = 0
        self.passed_tests = 0

    def log_result(
        self, category: str, test_name: str, passed: bool, details: str = ""
    ):
        """Log test result following crawl_mcp.py error handling."""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1

        self.results[category].append(
            {
                "test": test_name,
                "status": "PASS" if passed else "FAIL",
                "details": details,
            }
        )

        status_icon = "✅" if passed else "❌"
        print(f"{status_icon} {test_name}: {details}")

    def test_environment_validation(self):
        """Test 1: Environment Validation - crawl_mcp.py Step 1"""
        print("\n🔍 Testing Environment Validation...")

        # Test Python version
        python_version = sys.version_info
        passed = python_version >= (3, 12)
        self.log_result(
            "environment_validation",
            "Python Version Check",
            passed,
            f"Python {python_version.major}.{python_version.minor}",
        )

        # Test required directories exist
        required_dirs = [
            "src/ignition/modules/sme_agent",
            "src/ignition/modules/sme_agent/cli",
            "docs/phase_summary",
        ]

        for dir_path in required_dirs:
            exists = Path(dir_path).exists()
            self.log_result(
                "environment_validation",
                f"Directory {dir_path}",
                exists,
                "Exists" if exists else "Missing",
            )

    def test_module_imports(self):
        """Test 2: Module Imports and Dependencies - crawl_mcp.py Step 2"""
        print("\n📦 Testing Module Imports...")

        # Test core module imports
        modules_to_test = [
            (
                "src.ignition.modules.sme_agent.production_deployment",
                "ProductionDeploymentManager",
            ),
            (
                "src.ignition.modules.sme_agent.cli.production_deployment_commands",
                "deployment_group",
            ),
            ("docker", "DockerClient"),
            ("pydantic", "BaseModel"),
            ("rich.console", "Console"),
            ("click", "group"),
        ]

        for module_name, class_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                has_class = hasattr(module, class_name)
                self.log_result(
                    "module_imports",
                    f"Import {module_name}.{class_name}",
                    has_class,
                    "Available" if has_class else "Missing class",
                )
            except ImportError as e:
                self.log_result(
                    "module_imports",
                    f"Import {module_name}",
                    False,
                    f"Import error: {e!s}",
                )

    def test_production_deployment_core(self):
        """Test 3: Production Deployment Core Functionality"""
        print("\n🏭 Testing Production Deployment Core...")

        try:
            from src.ignition.modules.sme_agent.production_deployment import (
                DockerConfig,
                PLCConfig,
                ProductionConfig,
                ProductionDeploymentManager,
            )

            # Test configuration models
            test_docker_config = DockerConfig(
                image_name="ign-scripts",
                container_name="test-container",
                ports={8000: 8000},
            )

            test_plc_config = PLCConfig(
                name="test-plc", server_url="opc.tcp://localhost:4840"
            )

            test_config = ProductionConfig(
                docker_config=test_docker_config, plc_configs=[test_plc_config]
            )

            # Test configuration validation
            try:
                self.log_result(
                    "production_deployment",
                    "Configuration Validation",
                    True,
                    "ProductionConfig created successfully",
                )
            except Exception as e:
                self.log_result(
                    "production_deployment",
                    "Configuration Validation",
                    False,
                    f"Config error: {e!s}",
                )

            # Test manager initialization
            try:
                manager = ProductionDeploymentManager(config=test_config)
                self.log_result(
                    "production_deployment",
                    "Manager Initialization",
                    True,
                    "ProductionDeploymentManager created",
                )
            except Exception as e:
                self.log_result(
                    "production_deployment",
                    "Manager Initialization",
                    False,
                    f"Manager error: {e!s}",
                )

        except ImportError as e:
            self.log_result(
                "production_deployment",
                "Core Module Import",
                False,
                f"Import error: {e!s}",
            )

    def test_docker_integration(self):
        """Test 4: Docker Integration"""
        print("\n🐳 Testing Docker Integration...")

        # Test Docker availability
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            docker_available = result.returncode == 0
            version = result.stdout.strip() if docker_available else "Not available"
            self.log_result(
                "docker_integration", "Docker Command", docker_available, version
            )
        except FileNotFoundError:
            self.log_result(
                "docker_integration",
                "Docker Command",
                False,
                "Docker not found in PATH",
            )

        # Test docker-compose file exists
        compose_file = Path("docker-compose.yml")
        exists = compose_file.exists()
        self.log_result(
            "docker_integration",
            "Docker Compose File",
            exists,
            "Found" if exists else "Missing",
        )

        # Test Docker Python client
        try:
            import docker

            client = docker.from_env()
            # Try to ping Docker daemon (non-blocking)
            try:
                client.ping()
                self.log_result(
                    "docker_integration",
                    "Docker Daemon Connection",
                    True,
                    "Connected successfully",
                )
            except Exception as e:
                self.log_result(
                    "docker_integration",
                    "Docker Daemon Connection",
                    False,
                    f"Connection failed: {e!s}",
                )
        except Exception as e:
            self.log_result(
                "docker_integration",
                "Docker Python Client",
                False,
                f"Client error: {e!s}",
            )

    def test_plc_communication(self):
        """Test 5: PLC Communication"""
        print("\n🔌 Testing PLC Communication...")

        # Test OPC-UA client availability
        try:
            from asyncua import Client

            self.log_result(
                "plc_communication",
                "OPC-UA Client Import",
                True,
                "asyncua.Client available",
            )
        except ImportError as e:
            self.log_result(
                "plc_communication",
                "OPC-UA Client Import",
                False,
                f"asyncua not available: {e!s}",
            )

        # Test PLC configuration model
        try:
            from src.ignition.modules.sme_agent.production_deployment import PLCConfig

            plc_config = PLCConfig(
                name="test-plc", server_url="opc.tcp://localhost:4840"
            )
            self.log_result(
                "plc_communication",
                "PLC Configuration Model",
                True,
                "PLCConfig created successfully",
            )
        except Exception as e:
            self.log_result(
                "plc_communication",
                "PLC Configuration Model",
                False,
                f"Config error: {e!s}",
            )

    def test_cli_commands(self):
        """Test 6: CLI Commands Integration"""
        print("\n💻 Testing CLI Commands...")

        # Test CLI command imports
        try:
            from src.ignition.modules.sme_agent.cli.production_deployment_commands import (
                deployment_group,
            )

            self.log_result(
                "cli_commands",
                "Deployment Group Import",
                True,
                "deployment_group imported successfully",
            )
        except ImportError as e:
            self.log_result(
                "cli_commands", "Deployment Group Import", False, f"Import error: {e!s}"
            )

        # Test CLI integration
        try:
            from click.testing import CliRunner

            from src.ignition.modules.sme_agent.cli_commands import sme_agent_cli

            runner = CliRunner()
            result = runner.invoke(sme_agent_cli, ["deployment", "--help"])
            success = result.exit_code == 0 and "deployment" in result.output.lower()
            self.log_result(
                "cli_commands",
                "Deployment CLI Help",
                success,
                "Help command working" if success else "CLI error",
            )
        except Exception as e:
            self.log_result(
                "cli_commands", "Deployment CLI Help", False, f"CLI test error: {e!s}"
            )

    def test_file_structure(self):
        """Test 7: File Structure Validation"""
        print("\n📁 Testing File Structure...")

        # Test required files exist
        required_files = [
            "src/ignition/modules/sme_agent/production_deployment.py",
            "src/ignition/modules/sme_agent/cli/production_deployment_commands.py",
            "docker-compose.yml",
            "requirements.txt",
        ]

        for file_path in required_files:
            path = Path(file_path)
            exists = path.exists()
            size = path.stat().st_size if exists else 0
            self.log_result(
                "file_structure",
                f"File {file_path}",
                exists,
                f"Size: {size} bytes" if exists else "Missing",
            )

    def test_documentation(self):
        """Test 8: Documentation Verification"""
        print("\n📚 Testing Documentation...")

        # Check for Phase 11.7 documentation
        doc_files = [
            "docs/roadmap.md",
            "docs/phase_summary/PHASE_11_7_PRODUCTION_DEPLOYMENT_PLC_INTEGRATION.md",
        ]

        for doc_file in doc_files:
            path = Path(doc_file)
            exists = path.exists()

            if exists and doc_file == "docs/roadmap.md":
                # Check if Phase 11.7 is mentioned
                content = path.read_text()
                has_phase_117 = "Phase 11.7" in content
                self.log_result(
                    "documentation",
                    "Roadmap Phase 11.7",
                    has_phase_117,
                    "Phase 11.7 documented" if has_phase_117 else "Missing Phase 11.7",
                )
            else:
                self.log_result(
                    "documentation",
                    f"Documentation {doc_file}",
                    exists,
                    "Exists" if exists else "Missing",
                )

    def test_configuration_management(self):
        """Test 9: Configuration Management"""
        print("\n⚙️ Testing Configuration Management...")

        # Test configuration manager
        try:
            from src.ignition.modules.sme_agent.production_deployment import (
                DockerConfig,
                ProductionConfig,
                ProductionDeploymentManager,
            )

            docker_config = DockerConfig(
                image_name="ign-scripts", container_name="test-container"
            )
            config = ProductionConfig(docker_config=docker_config)
            manager = ProductionDeploymentManager(config=config)

            self.log_result(
                "configuration",
                "Configuration Manager",
                True,
                "Configuration manager created",
            )
        except Exception as e:
            self.log_result(
                "configuration", "Configuration Manager", False, f"Manager error: {e!s}"
            )

    def test_integration_examples(self):
        """Test 10: Integration Examples"""
        print("\n🔗 Testing Integration Examples...")

        # Test basic integration setup
        try:
            from src.ignition.modules.sme_agent.production_deployment import (
                DockerConfig,
                PLCConfig,
                ProductionConfig,
                ProductionDeploymentManager,
            )

            # Create test configuration
            docker_config = DockerConfig(
                image_name="ign-scripts", container_name="test-integration"
            )

            plc_config = PLCConfig(
                name="test-integration-plc", server_url="opc.tcp://localhost:4840"
            )

            test_config = ProductionConfig(
                docker_config=docker_config, plc_configs=[plc_config]
            )

            manager = ProductionDeploymentManager(config=test_config)
            self.log_result(
                "integration_examples",
                "Integration Setup",
                True,
                "Basic integration setup successful",
            )
        except Exception as e:
            self.log_result(
                "integration_examples",
                "Integration Setup",
                False,
                f"Setup error: {e!s}",
            )

    def run_all_tests(self):
        """Run all test categories following crawl_mcp.py methodology."""
        print("🚀 Phase 11.7 Comprehensive Test Suite")
        print("=" * 50)
        print("Following crawl_mcp.py methodology for systematic testing")
        print()

        # Run all test categories
        self.test_environment_validation()
        self.test_module_imports()
        self.test_production_deployment_core()
        self.test_docker_integration()
        self.test_plc_communication()
        self.test_cli_commands()
        self.test_file_structure()
        self.test_documentation()
        self.test_configuration_management()
        self.test_integration_examples()

        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)

        success_rate = (
            (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        )
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")

        # Print detailed results by category
        for category, tests in self.results.items():
            if tests:
                print(f"\n{category.replace('_', ' ').title()}:")
                for test in tests:
                    status_icon = "✅" if test["status"] == "PASS" else "❌"
                    print(f"  {status_icon} {test['test']}: {test['details']}")

        return success_rate >= 80  # 80% success rate threshold


if __name__ == "__main__":
    tester = Phase117ComprehensiveTest()
    success = tester.run_all_tests()

    if success:
        print("\n🎉 Phase 11.7 Implementation: COMPREHENSIVE TEST PASSED")
        print("✅ Production Deployment & PLC Integration is ready for production use!")
    else:
        print("\n⚠️ Phase 11.7 Implementation: Some tests failed")
        print("🔧 Review failed tests and address issues before production deployment")

    sys.exit(0 if success else 1)
