#!/usr/bin/env python3
"""Comprehensive Test Suite for Phase 11.3: SME Agent Integration & Interfaces
Following crawl_mcp.py methodology for thorough validation.

This test suite validates:
1. FastAPI Web Interface
2. Streamlit Web Interface
3. CLI Integration
4. Development Workflow Integration
5. Real-Time Knowledge Updates
6. Multi-Interface Deployment
7. Integration Examples
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Test configuration
TEST_CONFIG = {
    "verbose": True,
    "timeout": 30,
    "api_port": 8000,
    "streamlit_port": 8501,
}


class Phase11_3TestSuite:
    """Comprehensive test suite for Phase 11.3 functionality."""

    def __init__(self):
        """Initialize test suite."""
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "details": [],
        }
        self.project_root = Path(__file__).parent

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        self.test_results["total"] += 1

        if passed:
            self.test_results["passed"] += 1
            status = "✅ PASS"
            color = "\033[92m"  # Green
        else:
            self.test_results["failed"] += 1
            status = "❌ FAIL"
            color = "\033[91m"  # Red

        reset_color = "\033[0m"

        result_entry = {
            "test": test_name,
            "status": "PASS" if passed else "FAIL",
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.test_results["details"].append(result_entry)

        if TEST_CONFIG["verbose"]:
            print(f"{color}{status}{reset_color} {test_name}")
            if details and not passed:
                print(f"    Details: {details}")

    def test_module_imports(self):
        """Test 1: Validate all Phase 11.3 module imports."""
        try:
            # Test FastAPI interface import
            from src.ignition.modules.sme_agent.web_interface import app

            self.log_test("FastAPI Interface Import", True)
        except ImportError as e:
            self.log_test("FastAPI Interface Import", False, str(e))

        try:
            # Test Streamlit interface import
            import src.ignition.modules.sme_agent.streamlit_interface

            self.log_test("Streamlit Interface Import", True)
        except ImportError as e:
            self.log_test("Streamlit Interface Import", False, str(e))

        try:
            # Test development workflow integration
            from src.ignition.modules.sme_agent.development_workflow_integration import (
                DevelopmentWorkflowIntegrator,
            )

            self.log_test("Development Workflow Integration Import", True)
        except ImportError as e:
            self.log_test("Development Workflow Integration Import", False, str(e))

        try:
            # Test real-time knowledge updates
            from src.ignition.modules.sme_agent.real_time_knowledge_updates import (
                RealTimeKnowledgeUpdater,
            )

            self.log_test("Real-Time Knowledge Updates Import", True)
        except ImportError as e:
            self.log_test("Real-Time Knowledge Updates Import", False, str(e))

        try:
            # Test workflow CLI commands
            from src.ignition.modules.sme_agent.cli.workflow_commands import (
                knowledge_group,
                workflow_group,
            )

            self.log_test("Workflow CLI Commands Import", True)
        except ImportError as e:
            self.log_test("Workflow CLI Commands Import", False, str(e))

    def test_fastapi_interface(self):
        """Test 2: Validate FastAPI interface functionality."""
        try:
            from fastapi.testclient import TestClient

            from src.ignition.modules.sme_agent.web_interface import app

            client = TestClient(app)

            # Test health endpoint
            response = client.get("/health")
            health_ok = response.status_code == 200
            self.log_test("FastAPI Health Endpoint", health_ok, f"Status: {response.status_code}")

            # Test status endpoint
            response = client.get("/status")
            status_ok = response.status_code == 200
            self.log_test("FastAPI Status Endpoint", status_ok, f"Status: {response.status_code}")

            # Test docs endpoint
            response = client.get("/docs")
            docs_ok = response.status_code == 200
            self.log_test(
                "FastAPI Documentation Endpoint",
                docs_ok,
                f"Status: {response.status_code}",
            )

        except ImportError as e:
            self.log_test("FastAPI Interface Test", False, f"Import error: {e}")
        except Exception as e:
            self.log_test("FastAPI Interface Test", False, f"Test error: {e}")

    def test_development_workflow_integration(self):
        """Test 3: Validate development workflow integration."""
        try:
            from src.ignition.modules.sme_agent.development_workflow_integration import (
                DevelopmentWorkflowIntegrator,
                get_development_workflow_info,
                validate_development_workflow_environment,
            )

            # Test environment validation
            async def test_validation():
                result = await validate_development_workflow_environment()
                return result["validation_percentage"] > 0

            validation_ok = asyncio.run(test_validation())
            self.log_test("Development Workflow Environment Validation", validation_ok)

            # Test info retrieval
            info = get_development_workflow_info()
            info_ok = "features" in info and "requirements" in info
            self.log_test("Development Workflow Info Retrieval", info_ok)

            # Test integrator initialization
            async def test_integrator():
                integrator = DevelopmentWorkflowIntegrator()
                # Test basic initialization without full setup
                return hasattr(integrator, "config") and hasattr(integrator, "project_root")

            integrator_ok = asyncio.run(test_integrator())
            self.log_test("Development Workflow Integrator Initialization", integrator_ok)

        except Exception as e:
            self.log_test("Development Workflow Integration Test", False, str(e))

    def test_real_time_knowledge_updates(self):
        """Test 4: Validate real-time knowledge updates."""
        try:
            from src.ignition.modules.sme_agent.real_time_knowledge_updates import (
                RealTimeKnowledgeUpdater,
                get_knowledge_update_info,
                validate_knowledge_update_environment,
            )

            # Test environment validation
            async def test_validation():
                result = await validate_knowledge_update_environment()
                return result["validation_percentage"] > 0

            validation_ok = asyncio.run(test_validation())
            self.log_test("Knowledge Updates Environment Validation", validation_ok)

            # Test info retrieval
            info = get_knowledge_update_info()
            info_ok = "features" in info and "requirements" in info
            self.log_test("Knowledge Updates Info Retrieval", info_ok)

            # Test updater initialization
            async def test_updater():
                updater = RealTimeKnowledgeUpdater()
                result = await updater.initialize()
                return result["status"] == "success"

            updater_ok = asyncio.run(test_updater())
            self.log_test("Real-Time Knowledge Updater Initialization", updater_ok)

        except Exception as e:
            self.log_test("Real-Time Knowledge Updates Test", False, str(e))

    def test_cli_commands(self):
        """Test 5: Validate CLI command availability."""
        try:
            from src.ignition.modules.sme_agent.cli.workflow_commands import (
                knowledge_group,
                register_workflow_commands,
                workflow_group,
            )

            # Test workflow group
            workflow_ok = hasattr(workflow_group, "commands") and len(workflow_group.commands) > 0
            self.log_test("Workflow CLI Group", workflow_ok)

            # Test knowledge group
            knowledge_ok = hasattr(knowledge_group, "commands") and len(knowledge_group.commands) > 0
            self.log_test("Knowledge CLI Group", knowledge_ok)

            # Test command registration function
            register_ok = callable(register_workflow_commands)
            self.log_test("CLI Command Registration Function", register_ok)

        except Exception as e:
            self.log_test("CLI Commands Test", False, str(e))

    def test_file_structure(self):
        """Test 6: Validate Phase 11.3 file structure."""
        required_files = [
            "src/ignition/modules/sme_agent/web_interface.py",
            "src/ignition/modules/sme_agent/streamlit_interface.py",
            "src/ignition/modules/sme_agent/development_workflow_integration.py",
            "src/ignition/modules/sme_agent/real_time_knowledge_updates.py",
            "src/ignition/modules/sme_agent/cli/workflow_commands.py",
            "scripts/start_api_server.py",
            "scripts/test_api_endpoints.py",
            "scripts/demo_uvicorn_testing.py",
            "docs/uvicorn_api_guide.md",
            "docs/UVICORN_API_TESTING_SETUP.md",
            "docs/phase_summary/PHASE_11_3_SME_AGENT_INTEGRATION_INTERFACES.md",
        ]

        for file_path in required_files:
            file_exists = (self.project_root / file_path).exists()
            self.log_test(f"File Structure: {file_path}", file_exists)

    def test_documentation_completeness(self):
        """Test 7: Validate documentation completeness."""
        try:
            # Test Phase 11.3 documentation
            phase_doc = self.project_root / "docs/phase_summary/PHASE_11_3_SME_AGENT_INTEGRATION_INTERFACES.md"
            if phase_doc.exists():
                content = phase_doc.read_text()
                has_implementation = "Implementation Summary" in content
                has_architecture = "Technical Architecture" in content
                has_examples = "Integration Examples" in content

                doc_complete = has_implementation and has_architecture and has_examples
                self.log_test("Phase 11.3 Documentation Completeness", doc_complete)
            else:
                self.log_test("Phase 11.3 Documentation Exists", False, "File not found")

            # Test uvicorn documentation
            uvicorn_doc = self.project_root / "docs/uvicorn_api_guide.md"
            uvicorn_exists = uvicorn_doc.exists()
            self.log_test("Uvicorn API Guide Documentation", uvicorn_exists)

        except Exception as e:
            self.log_test("Documentation Completeness Test", False, str(e))

    def test_integration_examples(self):
        """Test 8: Validate integration examples."""
        try:
            # Test API testing scripts
            api_test_script = self.project_root / "scripts/test_api_endpoints.py"
            if api_test_script.exists():
                content = api_test_script.read_text()
                has_test_class = "APITester" in content
                has_endpoints = "/chat" in content and "/status" in content

                script_ok = has_test_class and has_endpoints
                self.log_test("API Testing Script Completeness", script_ok)
            else:
                self.log_test("API Testing Script Exists", False)

            # Test demo script
            demo_script = self.project_root / "scripts/demo_uvicorn_testing.py"
            demo_exists = demo_script.exists()
            self.log_test("Uvicorn Demo Script Exists", demo_exists)

        except Exception as e:
            self.log_test("Integration Examples Test", False, str(e))

    def test_dependencies(self):
        """Test 9: Validate required dependencies."""
        required_packages = [
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"),
            ("streamlit", "Web interface framework"),
            ("click", "CLI framework"),
            ("rich", "Terminal formatting"),
            ("pydantic", "Data validation"),
        ]

        for package, description in required_packages:
            try:
                __import__(package)
                self.log_test(f"Dependency: {package}", True)
            except ImportError:
                self.log_test(f"Dependency: {package}", False, f"Missing: {description}")

    def test_configuration_validation(self):
        """Test 10: Validate configuration and settings."""
        try:
            # Test development workflow configuration
            from src.ignition.modules.sme_agent.development_workflow_integration import (
                DevelopmentToolConfig,
            )

            config = DevelopmentToolConfig()
            config_ok = (
                hasattr(config, "enable_ide_integration")
                and hasattr(config, "enable_git_integration")
                and hasattr(config, "enable_code_intelligence")
            )
            self.log_test("Development Workflow Configuration", config_ok)

            # Test knowledge update configuration
            from src.ignition.modules.sme_agent.real_time_knowledge_updates import (
                KnowledgeUpdateConfig,
            )

            knowledge_config = KnowledgeUpdateConfig()
            knowledge_config_ok = (
                hasattr(knowledge_config, "enable_release_monitoring")
                and hasattr(knowledge_config, "enable_community_integration")
                and hasattr(knowledge_config, "enable_pattern_learning")
            )
            self.log_test("Knowledge Update Configuration", knowledge_config_ok)

        except Exception as e:
            self.log_test("Configuration Validation Test", False, str(e))

    def run_all_tests(self):
        """Run all Phase 11.3 tests."""
        print("🧪 Starting Phase 11.3 Comprehensive Test Suite")
        print("=" * 60)

        # Run all test methods
        test_methods = [
            self.test_module_imports,
            self.test_fastapi_interface,
            self.test_development_workflow_integration,
            self.test_real_time_knowledge_updates,
            self.test_cli_commands,
            self.test_file_structure,
            self.test_documentation_completeness,
            self.test_integration_examples,
            self.test_dependencies,
            self.test_configuration_validation,
        ]

        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                test_name = test_method.__name__.replace("_", " ").title()
                self.log_test(test_name, False, f"Test execution error: {e}")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("🏁 Phase 11.3 Test Summary")
        print("=" * 60)

        total = self.test_results["total"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        skipped = self.test_results["skipped"]

        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📊 Success Rate: {success_rate:.1f}%")

        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results["details"]:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")

        # Overall assessment
        if success_rate >= 90:
            print("\n🎉 Phase 11.3 implementation is EXCELLENT!")
        elif success_rate >= 80:
            print("\n✅ Phase 11.3 implementation is GOOD!")
        elif success_rate >= 70:
            print("\n⚠️  Phase 11.3 implementation needs MINOR improvements")
        else:
            print("\n❌ Phase 11.3 implementation needs MAJOR improvements")

        # Save detailed results
        self.save_test_results()

    def save_test_results(self):
        """Save detailed test results to file."""
        try:
            results_file = self.project_root / "test_results_phase_11_3.json"
            with open(results_file, "w") as f:
                json.dump(self.test_results, f, indent=2)
            print(f"\n📄 Detailed results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️  Failed to save test results: {e}")


def main():
    """Main test execution function."""
    print("🚀 Phase 11.3: SME Agent Integration & Interfaces")
    print("   Comprehensive Test Suite")
    print("   Following crawl_mcp.py methodology")

    test_suite = Phase11_3TestSuite()
    test_suite.run_all_tests()

    return test_suite.test_results["failed"] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
