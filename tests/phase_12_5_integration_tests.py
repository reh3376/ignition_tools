#!/usr/bin/env python3
"""Phase 12.5: CLI-to-API Integration Testing

Following crawl_mcp.py methodology for integration testing:
1. Environment validation first
2. CLI command validation
3. API endpoint validation
4. CLI-to-API mapping consistency
5. Contract testing
6. Error handling consistency
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

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
CLI_BASE_PATH = os.getenv("CLI_BASE_PATH", ".")


class IntegrationTestResult(BaseModel):
    """Integration test result model"""

    test_name: str
    cli_command: str
    api_endpoint: str
    cli_success: bool
    api_success: bool
    mapping_consistent: bool
    cli_output: str
    api_response: dict[str, Any]
    execution_time: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class Phase125IntegrationTester:
    """Integration testing suite following crawl_mcp.py methodology"""

    def __init__(self):
        self.api_base = API_BASE_URL
        self.cli_base = CLI_BASE_PATH
        self.results: list[IntegrationTestResult] = []

    async def test_cli_api_mapping(
        self, cli_command: list[str], api_endpoint: str, test_name: str
    ) -> IntegrationTestResult:
        """Test CLI command to API endpoint mapping"""
        start_time = time.time()

        cli_success = False
        api_success = False
        cli_output = ""
        api_response = {}

        # Test CLI command
        try:
            cli_result = subprocess.run(
                cli_command,
                cwd=self.cli_base,
                capture_output=True,
                text=True,
                timeout=30,
            )
            cli_success = cli_result.returncode == 0
            cli_output = cli_result.stdout if cli_result.stdout else cli_result.stderr
        except Exception as e:
            cli_output = f"Error: {e}"

        # Test API endpoint
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{self.api_base}{api_endpoint}")
                api_success = response.status_code in [200, 201]
                api_response = (
                    response.json()
                    if response.headers.get("content-type", "").startswith("application/json")
                    else {"status_code": response.status_code}
                )
        except Exception as e:
            api_response = {"error": str(e)}

        # Check mapping consistency
        mapping_consistent = cli_success == api_success

        result = IntegrationTestResult(
            test_name=test_name,
            cli_command=" ".join(cli_command),
            api_endpoint=api_endpoint,
            cli_success=cli_success,
            api_success=api_success,
            mapping_consistent=mapping_consistent,
            cli_output=cli_output[:500],  # Truncate for readability
            api_response=api_response,
            execution_time=time.time() - start_time,
        )

        self.results.append(result)

        # Log result
        status = "✅ CONSISTENT" if mapping_consistent else "❌ INCONSISTENT"
        print(f"   {status} {test_name}")
        print(f"     CLI: {'✅' if cli_success else '❌'} | API: {'✅' if api_success else '❌'}")

        return result

    async def run_comprehensive_integration_tests(self) -> dict[str, Any]:
        """Run comprehensive integration test suite"""
        print("=" * 80)
        print("PHASE 12.5: CLI-TO-API INTEGRATION TESTING")
        print("Following crawl_mcp.py methodology for integration validation")
        print("=" * 80)

        start_time = time.time()

        # Define CLI-to-API mappings based on roadmap
        cli_api_mappings = [
            {
                "test_name": "SME Environment Validation",
                "cli_command": [
                    "python",
                    "-m",
                    "src.main",
                    "module",
                    "sme",
                    "validate-env",
                ],
                "api_endpoint": "/api/v1/sme/validate-env",
            },
            {
                "test_name": "SME Status Check",
                "cli_command": ["python", "-m", "src.main", "module", "sme", "status"],
                "api_endpoint": "/api/v1/sme/status",
            },
            {
                "test_name": "SME Core Validate Environment",
                "cli_command": [
                    "python",
                    "-m",
                    "src.main",
                    "module",
                    "sme",
                    "core",
                    "validate-env",
                ],
                "api_endpoint": "/api/v1/sme/core/validate-env",
            },
            {
                "test_name": "Refactoring Detection",
                "cli_command": ["python", "-m", "src.main", "refactor", "detect"],
                "api_endpoint": "/api/v1/refactor/detect",
            },
            {
                "test_name": "Refactoring Statistics",
                "cli_command": ["python", "-m", "src.main", "refactor", "statistics"],
                "api_endpoint": "/api/v1/refactor/statistics",
            },
            {
                "test_name": "System Information",
                "cli_command": ["python", "-m", "src.main", "system", "info"],
                "api_endpoint": "/api/v1/system/info",
            },
        ]

        print("🔍 Testing CLI-to-API Mappings")
        integration_results = []

        for mapping in cli_api_mappings:
            try:
                result = await self.test_cli_api_mapping(
                    mapping["cli_command"],
                    mapping["api_endpoint"],
                    mapping["test_name"],
                )
                integration_results.append(result)
            except Exception as e:
                print(f"   ❌ FAILED {mapping['test_name']}: {e}")

        # Test additional API endpoints for consistency
        print("\n🔍 Testing API-Only Endpoints")
        api_only_tests = [
            {
                "test_name": "Health Check",
                "endpoint": "/health",
                "expected_status": 200,
            },
            {
                "test_name": "Environment Validation",
                "endpoint": "/api/v1/environment/validate",
                "expected_status": 200,
            },
            {
                "test_name": "Knowledge Graph Status",
                "endpoint": "/api/v1/knowledge/status",
                "expected_status": 200,
            },
        ]

        api_only_results = []
        async with httpx.AsyncClient(timeout=30) as client:
            for test in api_only_tests:
                test_start = time.time()
                try:
                    response = await client.get(f"{self.api_base}{test['endpoint']}")
                    success = response.status_code == test["expected_status"]

                    result = {
                        "test_name": test["test_name"],
                        "endpoint": test["endpoint"],
                        "expected_status": test["expected_status"],
                        "actual_status": response.status_code,
                        "success": success,
                        "execution_time": time.time() - test_start,
                    }
                    api_only_results.append(result)

                    status = "✅ PASS" if success else "❌ FAIL"
                    print(f"   {status} {test['test_name']}: {response.status_code}")

                except Exception as e:
                    print(f"   ❌ FAILED {test['test_name']}: {e}")

        # Calculate results
        consistent_mappings = sum(1 for r in integration_results if r.mapping_consistent)
        total_mappings = len(integration_results)
        mapping_consistency_rate = consistent_mappings / total_mappings * 100 if total_mappings > 0 else 0

        api_successes = sum(1 for r in api_only_results if r["success"])
        total_api_tests = len(api_only_results)
        api_success_rate = api_successes / total_api_tests * 100 if total_api_tests > 0 else 0

        overall_success = mapping_consistency_rate >= 70 and api_success_rate >= 80
        execution_time = time.time() - start_time

        # Generate report
        report = {
            "phase": "12.5 - CLI-to-API Integration Testing",
            "methodology": "crawl_mcp.py integration testing",
            "execution_time": round(execution_time, 2),
            "timestamp": datetime.now().isoformat(),
            "mapping_consistency_rate": round(mapping_consistency_rate, 1),
            "api_success_rate": round(api_success_rate, 1),
            "overall_success": overall_success,
            "integration_results": [result.dict() for result in integration_results],
            "api_only_results": api_only_results,
            "summary": {
                "consistent_mappings": consistent_mappings,
                "total_mappings": total_mappings,
                "successful_api_tests": api_successes,
                "total_api_tests": total_api_tests,
            },
            "recommendations": self._generate_recommendations(integration_results, api_only_results),
        }

        # Print summary
        print("\n" + "=" * 80)
        print("INTEGRATION TESTING RESULTS")
        print("=" * 80)

        print(f"CLI-to-API Mapping Consistency: {mapping_consistency_rate:.1f}%")
        print(f"API-Only Endpoint Success: {api_success_rate:.1f}%")
        print(f"Consistent Mappings: {consistent_mappings}/{total_mappings}")
        print(f"Successful API Tests: {api_successes}/{total_api_tests}")

        if overall_success:
            print("\n🎯 INTEGRATION TESTING PASSED")
            print("✅ CLI-to-API integration is consistent")
            print("✅ API endpoints are functioning correctly")
        else:
            print("\n⚠️  INTEGRATION ISSUES DETECTED")
            print("❌ Some CLI-API mappings or endpoints need attention")

        return report

    def _generate_recommendations(
        self, integration_results: list[IntegrationTestResult], api_results: list[dict]
    ) -> list[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Check for inconsistent mappings
        inconsistent = [r for r in integration_results if not r.mapping_consistent]
        if inconsistent:
            recommendations.append(
                f"🔗 Fix {len(inconsistent)} inconsistent CLI-API mappings: "
                + ", ".join([r.test_name for r in inconsistent[:3]])
                + ("..." if len(inconsistent) > 3 else "")
            )

        # Check for failing API endpoints
        failing_apis = [r for r in api_results if not r["success"]]
        if failing_apis:
            recommendations.append(
                f"🔧 Fix {len(failing_apis)} failing API endpoints: "
                + ", ".join([r["test_name"] for r in failing_apis[:3]])
                + ("..." if len(failing_apis) > 3 else "")
            )

        # Check for CLI-only failures
        cli_only_failures = [r for r in integration_results if not r.cli_success and r.api_success]
        if cli_only_failures:
            recommendations.append(
                f"⚙️  Fix {len(cli_only_failures)} CLI command issues while API works: "
                + ", ".join([r.test_name for r in cli_only_failures[:3]])
                + ("..." if len(cli_only_failures) > 3 else "")
            )

        # Check for API-only failures
        api_only_failures = [r for r in integration_results if r.cli_success and not r.api_success]
        if api_only_failures:
            recommendations.append(
                f"🌐 Fix {len(api_only_failures)} API endpoint issues while CLI works: "
                + ", ".join([r.test_name for r in api_only_failures[:3]])
                + ("..." if len(api_only_failures) > 3 else "")
            )

        if not recommendations:
            recommendations.append("🎉 Excellent! All CLI-API integration tests passed successfully.")

        return recommendations


async def main():
    """Main integration testing function"""
    print("🚀 Phase 12.5: CLI-to-API Integration Testing")
    print("   Following crawl_mcp.py methodology")
    print()

    tester = Phase125IntegrationTester()
    results = await tester.run_comprehensive_integration_tests()

    # Save results
    results_file = "phase_12_5_integration_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Integration results saved to: {results_file}")

    # Exit code
    exit_code = 0 if results.get("overall_success", False) else 1
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
