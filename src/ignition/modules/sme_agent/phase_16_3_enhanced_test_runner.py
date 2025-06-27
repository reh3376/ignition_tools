#!/usr/bin/env python3
"""Enhanced Phase 16.3 Test Runner following crawl_mcp.py methodology.

This module provides comprehensive test execution and reporting for Phase 16.3
components following the systematic approach defined in crawl_mcp.py.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from .phase_16_3_test_framework import run_phase_16_3_tests

logger = logging.getLogger(__name__)


class Phase163TestRunner:
    """Enhanced test runner for Phase 16.3 following crawl_mcp.py methodology."""

    def __init__(self):
        """Initialize test runner with crawl_mcp.py methodology."""
        self.logger = logging.getLogger(__name__)
        self.test_results: dict[str, Any] = {}
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None

    async def validate_test_environment(self) -> dict[str, Any]:
        """Step 1: Environment Validation First (crawl_mcp.py methodology)."""
        self.logger.info("🔍 Validating Phase 16.3 test environment...")

        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "components": {},
            "prerequisites": {},
        }

        # Check required environment variables
        required_env_vars = [
            "PHASE16_TEST_NAMESPACE",
            "PHASE16_TEST_REGISTRY",
            "PHASE16_SAP_TEST_ENDPOINT",
            "PHASE16_SCADA_TEST_ENDPOINT",
        ]

        for env_var in required_env_vars:
            value = os.getenv(env_var)
            validation_result["prerequisites"][env_var] = {
                "configured": value is not None,
                "value": value if value else "Not configured",
            }

            if not value:
                validation_result["warnings"].append(
                    f"Environment variable {env_var} not set"
                )

        # Check test dependencies
        try:
            from unittest.mock import patch

            import pytest
            import yaml

            validation_result["components"]["test_dependencies"] = {
                "available": True,
                "pytest_version": pytest.__version__,
            }
        except ImportError as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing test dependencies: {e}")

        return validation_result

    async def run_comprehensive_tests(self) -> dict[str, Any]:
        """Run comprehensive Phase 16.3 tests following crawl_mcp.py methodology."""
        self.start_time = datetime.now()
        self.logger.info("🚀 Starting comprehensive Phase 16.3 test execution...")

        # Step 1: Environment Validation First
        validation = await self.validate_test_environment()
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Test environment validation failed",
                "validation_errors": validation["errors"],
                "execution_time": 0,
            }

        try:
            # Step 4: Modular Component Testing
            test_results = run_phase_16_3_tests()

            self.end_time = datetime.now()
            execution_time = (self.end_time - self.start_time).total_seconds()

            # Enhance results with additional metadata
            enhanced_results = {
                **test_results,
                "environment_validation": validation,
                "execution_metadata": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.end_time.isoformat(),
                    "execution_time": execution_time,
                    "test_runner_version": "1.0.0",
                    "methodology": "crawl_mcp.py",
                },
            }

            # Step 6: Resource Management and Cleanup
            await self._cleanup_test_resources()

            return enhanced_results

        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": 0,
            }

    async def _cleanup_test_resources(self) -> None:
        """Step 6: Resource Management and Cleanup (crawl_mcp.py methodology)."""
        self.logger.info("🧹 Cleaning up test resources...")

        # Cleanup any temporary files, connections, etc.
        # This follows the crawl_mcp.py principle of proper resource management
        pass

    def generate_test_report(self, results: dict[str, Any]) -> str:
        """Generate comprehensive test report."""
        report_lines = [
            "=" * 80,
            "PHASE 16.3 COMPREHENSIVE TEST REPORT",
            "=" * 80,
            f"Test Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Methodology: crawl_mcp.py systematic testing approach",
            "",
            "SUMMARY:",
            f"  Overall Success: {'✅ PASSED' if results.get('success') else '❌ FAILED'}",
            f"  Total Test Categories: {len(results.get('test_categories', {}))}",
            f"  Execution Time: {results.get('execution_time', 0):.2f} seconds",
            "",
            "DETAILED RESULTS:",
        ]

        # Add detailed results for each test category
        for category, category_results in results.get("test_categories", {}).items():
            status = "✅ PASSED" if category_results.get("success") else "❌ FAILED"
            report_lines.extend(
                [
                    f"  {category}: {status}",
                    f"    Tests Run: {category_results.get('tests_run', 0)}",
                    f"    Failures: {category_results.get('failures', 0)}",
                    f"    Errors: {category_results.get('errors', 0)}",
                    "",
                ]
            )

        # Add environment validation results
        if "environment_validation" in results:
            env_val = results["environment_validation"]
            report_lines.extend(
                [
                    "ENVIRONMENT VALIDATION:",
                    f"  Status: {'✅ VALID' if env_val.get('valid') else '❌ INVALID'}",
                    f"  Errors: {len(env_val.get('errors', []))}",
                    f"  Warnings: {len(env_val.get('warnings', []))}",
                    "",
                ]
            )

        report_lines.extend(["=" * 80, "END OF REPORT", "=" * 80])

        return "\n".join(report_lines)

    async def save_test_results(
        self, results: dict[str, Any], output_dir: str = "test-results"
    ) -> None:
        """Save test results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON results
        json_file = output_path / f"phase_16_3_test_results_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save human-readable report
        report = self.generate_test_report(results)
        report_file = output_path / f"phase_16_3_test_report_{timestamp}.txt"
        with open(report_file, "w") as f:
            f.write(report)

        self.logger.info(f"Test results saved to {output_path}")


async def main():
    """Main function to run Phase 16.3 comprehensive tests."""
    runner = Phase163TestRunner()

    print("🚀 Starting Phase 16.3 Comprehensive Test Suite")
    print("Following crawl_mcp.py methodology for systematic testing")
    print("=" * 60)

    # Run comprehensive tests
    results = await runner.run_comprehensive_tests()

    # Generate and display report
    report = runner.generate_test_report(results)
    print(report)

    # Save results
    await runner.save_test_results(results)

    # Return appropriate exit code
    return 0 if results.get("success") else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
