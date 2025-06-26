#!/usr/bin/env python3
"""Phase 12.5: Testing & Validation - Comprehensive Test Suite

Following crawl_mcp.py methodology for systematic testing:
1. Environment validation first
2. Comprehensive input validation
3. Robust error handling testing
4. Modular testing approach
5. Progressive complexity validation
6. Proper resource management
7. Performance benchmarking
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Any

try:
    import httpx
except ImportError:
    print("⚠️  httpx not installed. Installing...")
    subprocess.run(["pip", "install", "httpx"])
    import httpx

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Test configuration following crawl_mcp.py patterns
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
CLI_BASE_PATH = os.getenv("CLI_BASE_PATH", ".")
TEST_TIMEOUT = 30


class TestResult(BaseModel):
    """Test result model following crawl_mcp.py patterns"""

    test_name: str
    category: str
    success: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    execution_time: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class Phase125ComprehensiveTester:
    """Comprehensive testing suite following crawl_mcp.py methodology"""

    def __init__(self):
        self.api_base = API_BASE_URL
        self.cli_base = CLI_BASE_PATH
        self.test_results: list[TestResult] = []
        self.start_time = time.time()

    def log_test_result(
        self,
        test_name: str,
        category: str,
        success: bool,
        message: str,
        details: dict[str, Any] | None = None,
        execution_time: float | None = None,
    ):
        """Log test result following crawl_mcp.py logging patterns"""
        result = TestResult(
            test_name=test_name,
            category=category,
            success=success,
            message=message,
            details=details or {},
            execution_time=execution_time or 0.0,
        )
        self.test_results.append(result)

        # Console output
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}: {message}")

    # === STEP 1: ENVIRONMENT VALIDATION FIRST ===
    async def test_environment_validation(self) -> bool:
        """Test environment validation (crawl_mcp.py Step 1)"""
        print("🔍 Step 1: Environment Validation Testing")
        start_time = time.time()

        try:
            validation_results = {
                "api_server_running": False,
                "neo4j_available": False,
                "cli_commands_available": False,
                "required_packages": False,
                "environment_variables": False,
            }

            # Test API server availability
            try:
                async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                    response = await client.get(f"{self.api_base}/health")
                    validation_results["api_server_running"] = response.status_code == 200
                    self.log_test_result(
                        "API Server Health Check",
                        "environment",
                        validation_results["api_server_running"],
                        f"API server status: {response.status_code}",
                        {
                            "url": f"{self.api_base}/health",
                            "status": response.status_code,
                        },
                        time.time() - start_time,
                    )
            except Exception as e:
                self.log_test_result(
                    "API Server Health Check",
                    "environment",
                    False,
                    f"API server unreachable: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Test Neo4j availability
            try:
                neo4j_env = {
                    "uri": os.getenv("NEO4J_URI"),
                    "user": os.getenv("NEO4J_USER"),
                    "password": os.getenv("NEO4J_PASSWORD"),
                }
                validation_results["neo4j_available"] = all(neo4j_env.values())
                self.log_test_result(
                    "Neo4j Environment Variables",
                    "environment",
                    validation_results["neo4j_available"],
                    f"Neo4j credentials available: {validation_results['neo4j_available']}",
                    {"env_vars": {k: bool(v) for k, v in neo4j_env.items()}},
                    time.time() - start_time,
                )
            except Exception as e:
                self.log_test_result(
                    "Neo4j Environment Variables",
                    "environment",
                    False,
                    f"Neo4j environment check failed: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Test CLI commands availability
            try:
                result = subprocess.run(
                    ["python", "-m", "src.main", "--help"],
                    cwd=self.cli_base,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                validation_results["cli_commands_available"] = result.returncode == 0
                self.log_test_result(
                    "CLI Commands Availability",
                    "environment",
                    validation_results["cli_commands_available"],
                    f"CLI help command status: {result.returncode}",
                    {"output_length": len(result.stdout) if result.stdout else 0},
                    time.time() - start_time,
                )
            except Exception as e:
                self.log_test_result(
                    "CLI Commands Availability",
                    "environment",
                    False,
                    f"CLI test failed: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Test required packages
            try:
                required_packages = ["fastapi", "uvicorn", "pydantic", "httpx"]
                missing_packages = []
                for package in required_packages:
                    try:
                        __import__(package)
                    except ImportError:
                        missing_packages.append(package)

                validation_results["required_packages"] = len(missing_packages) == 0
                self.log_test_result(
                    "Required Packages",
                    "environment",
                    validation_results["required_packages"],
                    (f"Missing packages: {missing_packages}" if missing_packages else "All packages available"),
                    {
                        "missing": missing_packages,
                        "total_required": len(required_packages),
                    },
                    time.time() - start_time,
                )
            except Exception as e:
                self.log_test_result(
                    "Required Packages",
                    "environment",
                    False,
                    f"Package check failed: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Test environment variables
            try:
                required_env_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]
                missing_env_vars = [var for var in required_env_vars if not os.getenv(var)]
                validation_results["environment_variables"] = len(missing_env_vars) == 0
                self.log_test_result(
                    "Environment Variables",
                    "environment",
                    validation_results["environment_variables"],
                    (f"Missing env vars: {missing_env_vars}" if missing_env_vars else "All env vars present"),
                    {
                        "missing": missing_env_vars,
                        "total_required": len(required_env_vars),
                    },
                    time.time() - start_time,
                )
            except Exception as e:
                self.log_test_result(
                    "Environment Variables",
                    "environment",
                    False,
                    f"Environment variable check failed: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Overall environment validation result
            overall_success = sum(validation_results.values()) >= 3  # At least 3/5 must pass
            success_rate = sum(validation_results.values()) / len(validation_results) * 100

            print(f"   📊 Environment Validation: {success_rate:.1f}% success rate")
            return overall_success

        except Exception as e:
            self.log_test_result(
                "Environment Validation Overall",
                "environment",
                False,
                f"Environment validation failed: {e}",
                {"error": str(e)},
                time.time() - start_time,
            )
            return False

    # === STEP 2: API FUNCTIONALITY TESTING ===
    async def test_api_functionality(self) -> bool:
        """Test API functionality following crawl_mcp.py Step 2"""
        print("🔍 Step 2: API Functionality Testing")
        start_time = time.time()

        try:
            functionality_tests = [
                {
                    "name": "Health Check Endpoint",
                    "endpoint": "/health",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "Environment Validation Endpoint",
                    "endpoint": "/api/v1/environment/validate",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "SME Status Endpoint",
                    "endpoint": "/api/v1/sme/status",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "Knowledge Graph Status",
                    "endpoint": "/api/v1/knowledge/status",
                    "method": "GET",
                    "expected_status": 200,
                },
            ]

            passed_tests = 0
            total_tests = len(functionality_tests)

            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                for test in functionality_tests:
                    test_start = time.time()
                    try:
                        response = await client.get(f"{self.api_base}{test['endpoint']}")
                        success = response.status_code == test["expected_status"]
                        if success:
                            passed_tests += 1

                        self.log_test_result(
                            test["name"],
                            "api_functionality",
                            success,
                            f"Status: {response.status_code}, Expected: {test['expected_status']}",
                            {
                                "status_code": response.status_code,
                                "expected": test["expected_status"],
                                "endpoint": test["endpoint"],
                                "response_time_ms": round((time.time() - test_start) * 1000, 2),
                            },
                            time.time() - test_start,
                        )

                    except Exception as e:
                        self.log_test_result(
                            test["name"],
                            "api_functionality",
                            False,
                            f"API functionality test failed: {e}",
                            {"error": str(e), "endpoint": test["endpoint"]},
                            time.time() - test_start,
                        )

            success_rate = passed_tests / total_tests * 100
            print(f"   📊 API Functionality: {success_rate:.1f}% success rate")
            return success_rate >= 75

        except Exception as e:
            self.log_test_result(
                "API Functionality Overall",
                "api_functionality",
                False,
                f"API functionality testing failed: {e}",
                {"error": str(e)},
                time.time() - start_time,
            )
            return False

    # === MAIN TEST EXECUTION ===
    async def run_comprehensive_test_suite(self) -> dict[str, Any]:
        """Run complete test suite following crawl_mcp.py methodology"""
        print("=" * 80)
        print("PHASE 12.5: TESTING & VALIDATION - COMPREHENSIVE TEST SUITE")
        print("Following crawl_mcp.py methodology for systematic validation")
        print("=" * 80)

        start_time = time.time()

        test_results = {}

        try:
            # Step 1: Environment validation first (critical)
            test_results["environment_validation"] = await self.test_environment_validation()

            # Step 2: API functionality testing
            test_results["api_functionality"] = await self.test_api_functionality()

        except Exception as e:
            print(f"❌ Test suite execution failed: {e}")
            test_results["execution_error"] = str(e)

        # Calculate overall results
        passed_categories = sum(1 for v in test_results.values() if isinstance(v, bool) and v)
        total_categories = len([k for k, v in test_results.items() if isinstance(v, bool)])
        overall_success_rate = passed_categories / total_categories * 100 if total_categories > 0 else 0
        overall_success = overall_success_rate >= 75

        execution_time = time.time() - start_time

        # Generate comprehensive report
        report = {
            "phase": "12.5 - Testing & Validation",
            "methodology": "crawl_mcp.py systematic testing",
            "execution_time": round(execution_time, 2),
            "timestamp": datetime.now().isoformat(),
            "overall_success_rate": round(overall_success_rate, 1),
            "categories_passed": passed_categories,
            "categories_total": total_categories,
            "completion_status": ("COMPLETED" if overall_success else "NEEDS_IMPROVEMENT"),
            "test_results": test_results,
            "detailed_results": [result.dict() for result in self.test_results],
            "recommendations": self._generate_recommendations(test_results),
        }

        # Print final summary
        print("\n" + "=" * 80)
        print("PHASE 12.5 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)

        for category, result in test_results.items():
            if isinstance(result, bool):
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {category.replace('_', ' ').title()}")

        print(f"\nOverall Success Rate: {overall_success_rate:.1f}%")
        print(f"Categories Passed: {passed_categories}/{total_categories}")
        print(f"Total Execution Time: {execution_time:.2f} seconds")
        print(f"Total Individual Tests: {len(self.test_results)}")

        if overall_success:
            print("\n🎯 PHASE 12.5 COMPLETION CRITERIA MET")
            print("✅ Testing & Validation implementation successful")
            print("✅ Ready to proceed to Phase 12.6: Deployment & Infrastructure")
        else:
            print("\n⚠️  PHASE 12.5 NEEDS ADDITIONAL WORK")
            print("❌ Some test categories require attention")

        return report

    def _generate_recommendations(self, test_results: dict[str, bool]) -> list[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if not test_results.get("environment_validation", True):
            recommendations.append(
                "🔧 Fix environment setup: Ensure API server, Neo4j, and CLI commands are properly configured"
            )

        if not test_results.get("api_functionality", True):
            recommendations.append("⚙️ Fix API functionality: Debug failing endpoints and ensure proper responses")

        if not recommendations:
            recommendations.append("🎉 Excellent! All test categories passed. Ready for Phase 12.6 deployment.")

        return recommendations


async def main():
    """Main test execution function following crawl_mcp.py patterns"""
    print("🚀 Phase 12.5: Testing & Validation")
    print("   Comprehensive Test Suite")
    print("   Following crawl_mcp.py methodology")
    print()

    tester = Phase125ComprehensiveTester()
    results = await tester.run_comprehensive_test_suite()

    # Save results to file
    results_file = "phase_12_5_test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Detailed results saved to: {results_file}")

    # Exit with appropriate code
    exit_code = 0 if results["completion_status"] == "COMPLETED" else 1
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
