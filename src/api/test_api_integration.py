"""Phase 12.1 API Integration Tests

Following crawl_mcp.py methodology:
- Environment validation first
- Comprehensive input validation
- Robust error handling testing
- Modular testing approach
- Progressive complexity validation
"""

import asyncio
import json
import os
import sys
from typing import Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    CLIResponse,
    format_error_message,
    run_cli_command,
    validate_environment,
)


class Phase12APITester:
    """Comprehensive API testing following crawl_mcp.py methodology"""

    def __init__(self):
        self.test_results = {
            "environment_validation": False,
            "error_handling": False,
            "cli_mapping": False,
            "input_validation": False,
            "progressive_complexity": False,
        }
        self.detailed_results = []

    def validate_environment_first(self) -> bool:
        """Step 1: Environment validation (crawl_mcp.py methodology)"""
        try:
            print("🔍 Step 1: Environment Validation")
            env_status = validate_environment()

            required_components = [
                "neo4j_available",
                "neo4j_user",
                "python_version",
                "cli_available",
            ]
            all_valid = all(
                env_status.get(component, False) for component in required_components
            )

            print(f"   ✅ Neo4j Available: {env_status.get('neo4j_available', False)}")
            print(f"   ✅ Neo4j User: {env_status.get('neo4j_user', False)}")
            print(f"   ✅ Python Version: {env_status.get('python_version', False)}")
            print(f"   ✅ CLI Available: {env_status.get('cli_available', False)}")
            print(f"   ✅ API Version: {env_status.get('api_version', 'Unknown')}")

            self.test_results["environment_validation"] = all_valid
            self.detailed_results.append(
                {
                    "test": "environment_validation",
                    "success": all_valid,
                    "details": env_status,
                }
            )

            return all_valid

        except Exception as e:
            print(f"   ❌ Environment validation failed: {e}")
            return False

    def test_error_handling(self) -> bool:
        """Step 2: Comprehensive error handling testing"""
        try:
            print("\n🔍 Step 2: Error Handling Testing")

            # Test error message formatting
            test_errors = [
                ("authentication failed", "Authentication failed"),
                ("connection refused", "Connection failed"),
                ("permission denied", "Permission denied"),
                ("file not found", "Required resource not found"),
                ("timeout expired", "Operation timed out"),
                ("random error", "random error"),  # Should pass through
            ]

            all_passed = True
            for error_input, expected_pattern in test_errors:
                formatted = format_error_message(error_input)
                passed = expected_pattern.lower() in formatted.lower()
                print(
                    f"   {'✅' if passed else '❌'} Error '{error_input}' -> '{formatted}'"
                )
                if not passed:
                    all_passed = False

            self.test_results["error_handling"] = all_passed
            self.detailed_results.append(
                {
                    "test": "error_handling",
                    "success": all_passed,
                    "details": {"test_cases": len(test_errors), "passed": all_passed},
                }
            )

            return all_passed

        except Exception as e:
            print(f"   ❌ Error handling test failed: {e}")
            return False

    async def test_cli_mapping(self) -> bool:
        """Step 3: CLI to API mapping validation"""
        try:
            print("\n🔍 Step 3: CLI Mapping Testing")

            # Test basic CLI command execution
            test_commands = [
                ["python", "-m", "src.main", "--version"],
                ["python", "-m", "src.main", "--help"],
            ]

            all_passed = True
            for command in test_commands:
                try:
                    result = await run_cli_command(command)
                    passed = isinstance(result, CLIResponse)
                    print(
                        f"   {'✅' if passed else '❌'} Command {' '.join(command[:3])}... -> {result.success if passed else 'Failed'}"
                    )
                    if not passed:
                        all_passed = False
                except Exception as e:
                    print(f"   ❌ Command {' '.join(command[:3])}... failed: {e}")
                    all_passed = False

            self.test_results["cli_mapping"] = all_passed
            self.detailed_results.append(
                {
                    "test": "cli_mapping",
                    "success": all_passed,
                    "details": {"commands_tested": len(test_commands)},
                }
            )

            return all_passed

        except Exception as e:
            print(f"   ❌ CLI mapping test failed: {e}")
            return False

    def test_input_validation(self) -> bool:
        """Step 4: Input validation testing"""
        try:
            print("\n🔍 Step 4: Input Validation Testing")

            # Test Pydantic model validation
            from main import ModuleCreateRequest, ScriptGenerationRequest

            validation_tests = [
                {
                    "model": ScriptGenerationRequest,
                    "valid_data": {
                        "template_type": "opcua_client",
                        "parameters": {"server_url": "opc.tcp://localhost:4840"},
                        "output_format": "python",
                    },
                    "invalid_data": {
                        "template_type": "invalid_template",
                        "parameters": {},
                        "output_format": "python",
                    },
                },
                {
                    "model": ModuleCreateRequest,
                    "valid_data": {
                        "name": "test_module",
                        "description": "Test module",
                        "template": "basic",
                    },
                    "invalid_data": {
                        "name": "invalid@name",
                        "description": "Test module",
                        "template": "basic",
                    },
                },
            ]

            all_passed = True
            for test in validation_tests:
                model = test["model"]

                # Test valid data
                try:
                    valid_instance = model(**test["valid_data"])
                    print(f"   ✅ {model.__name__} valid data accepted")
                except Exception as e:
                    print(f"   ❌ {model.__name__} valid data rejected: {e}")
                    all_passed = False

                # Test invalid data
                try:
                    invalid_instance = model(**test["invalid_data"])
                    print(
                        f"   ❌ {model.__name__} invalid data accepted (should be rejected)"
                    )
                    all_passed = False
                except Exception:
                    print(f"   ✅ {model.__name__} invalid data properly rejected")

            self.test_results["input_validation"] = all_passed
            self.detailed_results.append(
                {
                    "test": "input_validation",
                    "success": all_passed,
                    "details": {"models_tested": len(validation_tests)},
                }
            )

            return all_passed

        except Exception as e:
            print(f"   ❌ Input validation test failed: {e}")
            return False

    def test_progressive_complexity(self) -> bool:
        """Step 5: Progressive complexity validation"""
        try:
            print("\n🔍 Step 5: Progressive Complexity Testing")

            # Test API endpoint structure follows progressive complexity
            from main import app

            endpoint_categories = {
                "basic": ["/health", "/api/v1/environment/validate"],
                "standard": ["/api/v1/sme/status", "/api/v1/templates/list"],
                "advanced": ["/api/v1/refactor/workflow", "/api/v1/modules/create"],
                "enterprise": ["/api/v1/setup/configure", "/api/v1/advanced/features"],
            }

            total_endpoints = sum(
                len(endpoints) for endpoints in endpoint_categories.values()
            )
            print(f"   ✅ Total API endpoints: {total_endpoints}")

            for category, endpoints in endpoint_categories.items():
                print(f"   ✅ {category.title()} endpoints: {len(endpoints)}")
                for endpoint in endpoints:
                    print(f"      - {endpoint}")

            # Validate API versioning
            versioned_endpoints = [
                route.path for route in app.routes if "/api/v1/" in route.path
            ]
            print(f"   ✅ Versioned endpoints: {len(versioned_endpoints)}")

            complexity_valid = (
                total_endpoints >= 20
            )  # Should have at least 20 endpoints

            self.test_results["progressive_complexity"] = complexity_valid
            self.detailed_results.append(
                {
                    "test": "progressive_complexity",
                    "success": complexity_valid,
                    "details": {
                        "total_endpoints": total_endpoints,
                        "versioned_endpoints": len(versioned_endpoints),
                        "categories": list(endpoint_categories.keys()),
                    },
                }
            )

            return complexity_valid

        except Exception as e:
            print(f"   ❌ Progressive complexity test failed: {e}")
            return False

    async def run_comprehensive_test(self) -> dict[str, Any]:
        """Run complete test suite following crawl_mcp.py methodology"""
        print("🚀 Phase 12.1 API Integration Testing")
        print("📋 Following crawl_mcp.py methodology")
        print("=" * 60)

        # Step 1: Environment validation first (crawl_mcp.py principle)
        env_valid = self.validate_environment_first()
        if not env_valid:
            print("\n❌ Environment validation failed. Cannot proceed with testing.")
            return self.generate_test_report()

        # Step 2: Error handling testing
        error_handling_valid = self.test_error_handling()

        # Step 3: CLI mapping testing
        cli_mapping_valid = await self.test_cli_mapping()

        # Step 4: Input validation testing
        input_validation_valid = self.test_input_validation()

        # Step 5: Progressive complexity testing
        complexity_valid = self.test_progressive_complexity()

        return self.generate_test_report()

    def generate_test_report(self) -> dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print("\n📊 Test Results Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")

        overall_success = success_rate >= 80  # 80% pass rate required
        print(
            f"\n🎯 Overall Result: {'✅ SUCCESS' if overall_success else '❌ NEEDS IMPROVEMENT'}"
        )

        if overall_success:
            print("🎉 Phase 12.1 API Layer Development: COMPLETE")
            print("✅ Ready for Phase 12.2: Repository Separation")
        else:
            print("⚠️  Some tests failed. Review and fix issues before proceeding.")

        return {
            "overall_success": overall_success,
            "success_rate": success_rate,
            "test_results": self.test_results,
            "detailed_results": self.detailed_results,
            "phase_12_1_complete": overall_success,
        }


async def main():
    """Main test execution"""
    tester = Phase12APITester()
    results = await tester.run_comprehensive_test()

    # Save results to file
    with open("phase_12_1_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n📄 Detailed results saved to: phase_12_1_test_results.json")
    return results


if __name__ == "__main__":
    # Run the comprehensive test suite
    asyncio.run(main())
