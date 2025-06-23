#!/usr/bin/env python3
"""
Phase 9.8 Advanced Module Features Comprehensive Testing Report
==============================================================

Following crawl_mcp.py methodology for systematic validation:
1. Environment Variable Validation First
2. Comprehensive Input Validation
3. Error Handling with User-Friendly Messages
4. Modular Component Testing
5. Progressive Complexity
6. Resource Management

This report validates all Phase 9.8 components:
- Real-time Analytics Module
- Security and Compliance Module
- Integration Hub Module
- CLI Commands Integration
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ignition.modules.advanced_features.analytics_module import (
    AnalyticsConfig,
    RealTimeAnalyticsModule,
)
from ignition.modules.advanced_features.integration_hub import (
    IntegrationConfig,
    IntegrationHubModule,
)
from ignition.modules.advanced_features.security_module import (
    SecurityComplianceModule,
    SecurityConfig,
)

console = Console()


class Phase98ComprehensiveTestReporter:
    """
    Phase 9.8 Comprehensive Test Reporter
    Following crawl_mcp.py methodology for systematic validation
    """

    def __init__(self):
        """Initialize test reporter with crawl_mcp.py patterns."""
        self.console = console
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "phase": "9.8",
            "methodology": "crawl_mcp.py systematic approach",
            "test_summary": {},
            "detailed_results": {},
        }
        self.start_time = time.time()

    def log_test_start(self, test_name: str) -> None:
        """Log test start following crawl_mcp.py patterns."""
        self.console.print(f"🔍 Testing: {test_name}", style="blue")

    def log_test_result(self, test_name: str, passed: bool, details: str = "") -> None:
        """Log test result following crawl_mcp.py patterns."""
        status = "✅ PASSED" if passed else "❌ FAILED"
        self.console.print(
            f"  {status}: {test_name}", style="green" if passed else "red"
        )
        if details:
            self.console.print(f"    Details: {details}", style="dim")

    def test_analytics_module(self) -> dict[str, Any]:
        """
        Test 1: Analytics Module (crawl_mcp.py pattern)
        Step 1: Environment Variable Validation First
        """
        self.log_test_start("Analytics Module Comprehensive Validation")

        try:
            # Test different complexity levels
            test_results = {}

            for complexity in ["basic", "intermediate", "advanced"]:
                self.console.print(f"  📊 Testing {complexity} complexity level")

                config = AnalyticsConfig(complexity_level=complexity)
                module = RealTimeAnalyticsModule(config)

                # Test environment validation
                env_valid = all(
                    result.valid for result in module.environment_validation.values()
                )
                test_results[f"{complexity}_environment"] = env_valid

                # Test data processing
                test_data = {
                    "timestamp": datetime.now().isoformat(),
                    "values": {
                        "temperature": 25.5,
                        "pressure": 101.3,
                        "humidity": 60.2,
                        "flow_rate": 15.8,
                    },
                }

                process_result = module.process_data(test_data)
                test_results[f"{complexity}_processing"] = process_result["success"]

                # Test error handling
                error_result = module.process_data(None)
                test_results[f"{complexity}_error_handling"] = not error_result[
                    "success"
                ]

                # Test report generation
                report_result = module.generate_analytics_report()
                test_results[f"{complexity}_reporting"] = report_result["success"]

                # Cleanup
                module.cleanup_resources()

                self.log_test_result(
                    f"Analytics {complexity} level",
                    all(
                        [
                            test_results[f"{complexity}_environment"],
                            test_results[f"{complexity}_processing"],
                            test_results[f"{complexity}_error_handling"],
                            test_results[f"{complexity}_reporting"],
                        ]
                    ),
                )

            # Overall analytics score
            passed_tests = sum(1 for v in test_results.values() if v)
            total_tests = len(test_results)
            score = (passed_tests / total_tests) * 100

            self.log_test_result(
                "Analytics Module Overall",
                score >= 80,
                f"Score: {score:.1f}% ({passed_tests}/{total_tests})",
            )

            return {
                "passed": score >= 80,
                "score": score,
                "details": test_results,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
            }

        except Exception as e:
            self.log_test_result("Analytics Module", False, f"Exception: {e!s}")
            return {"passed": False, "error": str(e)}

    def test_security_module(self) -> dict[str, Any]:
        """
        Test 2: Security Module (crawl_mcp.py pattern)
        Step 2: Comprehensive Input Validation
        """
        self.log_test_start("Security Module Comprehensive Validation")

        try:
            test_results = {}

            # Test different security levels
            for security_level in ["basic", "standard", "high", "critical"]:
                self.console.print(f"  🔒 Testing {security_level} security level")

                config = SecurityConfig(security_level=security_level)
                module = SecurityComplianceModule(config)

                # Test environment validation
                env_valid = all(
                    result.valid for result in module.environment_validation.values()
                )
                test_results[f"{security_level}_environment"] = env_valid

                # Test event logging
                test_event = {
                    "event_type": "login_attempt",
                    "user_id": f"test_user_{security_level}",
                    "source_ip": "192.168.1.100",
                    "details": {"success": True, "method": "password"},
                }

                event_result = module.log_security_event(test_event)
                test_results[f"{security_level}_event_logging"] = event_result[
                    "success"
                ]

                # Test compliance checking
                compliance_result = module.run_compliance_check("general")
                test_results[f"{security_level}_compliance"] = compliance_result[
                    "success"
                ]

                # Test error handling
                error_result = module.log_security_event(None)
                test_results[f"{security_level}_error_handling"] = not error_result[
                    "success"
                ]

                # Test report generation
                report_result = module.generate_security_report()
                test_results[f"{security_level}_reporting"] = report_result["success"]

                # Cleanup
                module.cleanup_resources()

                self.log_test_result(
                    f"Security {security_level} level",
                    all(
                        [
                            test_results[f"{security_level}_environment"],
                            test_results[f"{security_level}_event_logging"],
                            test_results[f"{security_level}_compliance"],
                            test_results[f"{security_level}_error_handling"],
                            test_results[f"{security_level}_reporting"],
                        ]
                    ),
                )

            # Overall security score
            passed_tests = sum(1 for v in test_results.values() if v)
            total_tests = len(test_results)
            score = (passed_tests / total_tests) * 100

            self.log_test_result(
                "Security Module Overall",
                score >= 80,
                f"Score: {score:.1f}% ({passed_tests}/{total_tests})",
            )

            return {
                "passed": score >= 80,
                "score": score,
                "details": test_results,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
            }

        except Exception as e:
            self.log_test_result("Security Module", False, f"Exception: {e!s}")
            return {"passed": False, "error": str(e)}

    def test_integration_module(self) -> dict[str, Any]:
        """
        Test 3: Integration Hub Module (crawl_mcp.py pattern)
        Step 3: Error Handling with User-Friendly Messages
        """
        self.log_test_start("Integration Hub Comprehensive Validation")

        try:
            test_results = {}

            # Test different integration levels
            for integration_level in ["basic", "standard", "advanced", "enterprise"]:
                self.console.print(
                    f"  🔌 Testing {integration_level} integration level"
                )

                config = IntegrationConfig(integration_level=integration_level)
                module = IntegrationHubModule(config)

                # Test environment validation
                env_valid = all(
                    result.valid for result in module.environment_validation.values()
                )
                test_results[f"{integration_level}_environment"] = env_valid

                # Test endpoint registration
                test_endpoint = {
                    "name": f"test_endpoint_{integration_level}",
                    "url": "https://jsonplaceholder.typicode.com/posts/1",
                    "method": "GET",
                }

                endpoint_result = module.register_api_endpoint(test_endpoint)
                test_results[f"{integration_level}_endpoint_registration"] = (
                    endpoint_result["success"]
                )

                # Test webhook processing
                test_webhook = {
                    "source": f"test_system_{integration_level}",
                    "event": "test_event",
                    "data": {"key": "value", "level": integration_level},
                }

                webhook_result = module.process_webhook(test_webhook)
                test_results[f"{integration_level}_webhook_processing"] = (
                    webhook_result["success"]
                )

                # Test error handling
                error_result = module.register_api_endpoint(None)
                test_results[f"{integration_level}_error_handling"] = not error_result[
                    "success"
                ]

                # Test report generation
                report_result = module.generate_integration_report()
                test_results[f"{integration_level}_reporting"] = report_result[
                    "success"
                ]

                # Cleanup
                module.cleanup_resources()

                self.log_test_result(
                    f"Integration {integration_level} level",
                    all(
                        [
                            test_results[f"{integration_level}_environment"],
                            test_results[f"{integration_level}_endpoint_registration"],
                            test_results[f"{integration_level}_webhook_processing"],
                            test_results[f"{integration_level}_error_handling"],
                            test_results[f"{integration_level}_reporting"],
                        ]
                    ),
                )

            # Overall integration score
            passed_tests = sum(1 for v in test_results.values() if v)
            total_tests = len(test_results)
            score = (passed_tests / total_tests) * 100

            self.log_test_result(
                "Integration Module Overall",
                score >= 80,
                f"Score: {score:.1f}% ({passed_tests}/{total_tests})",
            )

            return {
                "passed": score >= 80,
                "score": score,
                "details": test_results,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
            }

        except Exception as e:
            self.log_test_result("Integration Module", False, f"Exception: {e!s}")
            return {"passed": False, "error": str(e)}

    def test_cli_integration(self) -> dict[str, Any]:
        """
        Test 4: CLI Integration (crawl_mcp.py pattern)
        Step 4: Modular Component Testing
        """
        self.log_test_start("CLI Integration Validation")

        try:
            from click.testing import CliRunner

            from ignition.modules.advanced_features.cli_commands import (
                advanced_features_cli,
            )

            runner = CliRunner()
            test_results = {}

            # Test main CLI command
            result = runner.invoke(advanced_features_cli, ["--help"])
            test_results["main_help"] = result.exit_code == 0

            # Test analytics commands
            result = runner.invoke(advanced_features_cli, ["analytics", "--help"])
            test_results["analytics_help"] = result.exit_code == 0

            # Test security commands
            result = runner.invoke(advanced_features_cli, ["security", "--help"])
            test_results["security_help"] = result.exit_code == 0

            # Test integration commands
            result = runner.invoke(advanced_features_cli, ["integration", "--help"])
            test_results["integration_help"] = result.exit_code == 0

            # Test comprehensive testing command
            result = runner.invoke(advanced_features_cli, ["test-all", "--help"])
            test_results["test_all_help"] = result.exit_code == 0

            # Test report generation command
            result = runner.invoke(advanced_features_cli, ["generate-report", "--help"])
            test_results["generate_report_help"] = result.exit_code == 0

            # Test environment validation commands
            result = runner.invoke(
                advanced_features_cli,
                ["analytics", "validate-env", "--complexity", "basic"],
            )
            test_results["analytics_validate_env"] = result.exit_code == 0

            result = runner.invoke(
                advanced_features_cli,
                ["security", "validate-env", "--security-level", "basic"],
            )
            test_results["security_validate_env"] = result.exit_code == 0

            result = runner.invoke(
                advanced_features_cli,
                ["integration", "validate-env", "--integration-level", "basic"],
            )
            test_results["integration_validate_env"] = result.exit_code == 0

            # Overall CLI score
            passed_tests = sum(1 for v in test_results.values() if v)
            total_tests = len(test_results)
            score = (passed_tests / total_tests) * 100

            self.log_test_result(
                "CLI Integration Overall",
                score >= 90,
                f"Score: {score:.1f}% ({passed_tests}/{total_tests})",
            )

            return {
                "passed": score >= 90,
                "score": score,
                "details": test_results,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
            }

        except Exception as e:
            self.log_test_result("CLI Integration", False, f"Exception: {e!s}")
            return {"passed": False, "error": str(e)}

    def test_progressive_complexity(self) -> dict[str, Any]:
        """
        Test 5: Progressive Complexity (crawl_mcp.py pattern)
        Step 5: Progressive Complexity
        """
        self.log_test_start("Progressive Complexity Validation")

        try:
            test_results = {}

            # Test analytics complexity progression
            analytics_levels = ["basic", "intermediate", "advanced"]
            for i, level in enumerate(analytics_levels):
                config = AnalyticsConfig(complexity_level=level)
                module = RealTimeAnalyticsModule(config)

                # Higher complexity should have more components
                component_count = sum(
                    module.generate_analytics_report()["report"]["components"].values()
                )
                test_results[f"analytics_{level}_components"] = component_count >= i + 1

                module.cleanup_resources()

            # Test security level progression
            security_levels = ["basic", "standard", "high", "critical"]
            for i, level in enumerate(security_levels):
                config = SecurityConfig(security_level=level)
                module = SecurityComplianceModule(config)

                # Higher security should have more components
                component_count = sum(
                    module.generate_security_report()["report"]["components"].values()
                )
                test_results[f"security_{level}_components"] = component_count >= i + 1

                module.cleanup_resources()

            # Test integration level progression
            integration_levels = ["basic", "standard", "advanced", "enterprise"]
            for i, level in enumerate(integration_levels):
                config = IntegrationConfig(integration_level=level)
                module = IntegrationHubModule(config)

                # Higher integration should have more components
                component_count = sum(
                    module.generate_integration_report()["report"][
                        "components"
                    ].values()
                )
                test_results[f"integration_{level}_components"] = (
                    component_count >= i + 1
                )

                module.cleanup_resources()

            # Overall progressive complexity score
            passed_tests = sum(1 for v in test_results.values() if v)
            total_tests = len(test_results)
            score = (passed_tests / total_tests) * 100

            self.log_test_result(
                "Progressive Complexity Overall",
                score >= 75,
                f"Score: {score:.1f}% ({passed_tests}/{total_tests})",
            )

            return {
                "passed": score >= 75,
                "score": score,
                "details": test_results,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
            }

        except Exception as e:
            self.log_test_result("Progressive Complexity", False, f"Exception: {e!s}")
            return {"passed": False, "error": str(e)}

    def test_resource_management(self) -> dict[str, Any]:
        """
        Test 6: Resource Management (crawl_mcp.py pattern)
        Step 6: Resource Management
        """
        self.log_test_start("Resource Management Validation")

        try:
            test_results = {}

            # Test analytics resource cleanup
            analytics_module = RealTimeAnalyticsModule()
            analytics_module.cleanup_resources()
            test_results["analytics_cleanup"] = True  # No exception means success

            # Test security resource cleanup
            security_module = SecurityComplianceModule()
            security_module.cleanup_resources()
            test_results["security_cleanup"] = True  # No exception means success

            # Test integration resource cleanup
            integration_module = IntegrationHubModule()
            integration_module.cleanup_resources()
            test_results["integration_cleanup"] = True  # No exception means success

            # Test temporary directory cleanup
            temp_dirs = [
                Path.home() / "tmp" / "ign_analytics",
                Path.home() / "tmp" / "ign_security",
                Path.home() / "tmp" / "ign_integration",
            ]

            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    # Check if temp files are cleaned up
                    temp_files = list(temp_dir.glob("*.tmp"))
                    test_results[f"{temp_dir.name}_temp_cleanup"] = len(temp_files) == 0
                else:
                    test_results[f"{temp_dir.name}_temp_cleanup"] = True

            # Overall resource management score
            passed_tests = sum(1 for v in test_results.values() if v)
            total_tests = len(test_results)
            score = (passed_tests / total_tests) * 100

            self.log_test_result(
                "Resource Management Overall",
                score >= 90,
                f"Score: {score:.1f}% ({passed_tests}/{total_tests})",
            )

            return {
                "passed": score >= 90,
                "score": score,
                "details": test_results,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
            }

        except Exception as e:
            self.log_test_result("Resource Management", False, f"Exception: {e!s}")
            return {"passed": False, "error": str(e)}

    def generate_comprehensive_report(self) -> dict[str, Any]:
        """Generate comprehensive test report following crawl_mcp.py methodology."""

        self.console.print(
            Panel.fit(
                "🧪 Phase 9.8 Comprehensive Testing Report\nFollowing crawl_mcp.py methodology",
                style="magenta bold",
            )
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            # Run all tests
            task = progress.add_task("Running comprehensive tests...", total=6)

            # Test 1: Analytics Module
            analytics_results = self.test_analytics_module()
            self.test_results["detailed_results"]["analytics"] = analytics_results
            progress.advance(task)

            # Test 2: Security Module
            security_results = self.test_security_module()
            self.test_results["detailed_results"]["security"] = security_results
            progress.advance(task)

            # Test 3: Integration Module
            integration_results = self.test_integration_module()
            self.test_results["detailed_results"]["integration"] = integration_results
            progress.advance(task)

            # Test 4: CLI Integration
            cli_results = self.test_cli_integration()
            self.test_results["detailed_results"]["cli_integration"] = cli_results
            progress.advance(task)

            # Test 5: Progressive Complexity
            complexity_results = self.test_progressive_complexity()
            self.test_results["detailed_results"][
                "progressive_complexity"
            ] = complexity_results
            progress.advance(task)

            # Test 6: Resource Management
            resource_results = self.test_resource_management()
            self.test_results["detailed_results"][
                "resource_management"
            ] = resource_results
            progress.advance(task)

        # Calculate overall scores
        test_categories = [
            ("Analytics Module", analytics_results),
            ("Security Module", security_results),
            ("Integration Module", integration_results),
            ("CLI Integration", cli_results),
            ("Progressive Complexity", complexity_results),
            ("Resource Management", resource_results),
        ]

        # Overall summary
        total_score = 0
        total_weight = 0
        category_scores = {}

        for category, results in test_categories:
            if "score" in results:
                weight = 1.0
                if category == "CLI Integration":
                    weight = 1.5  # CLI integration is more important
                elif category == "Resource Management":
                    weight = 1.2  # Resource management is important

                category_scores[category] = results["score"]
                total_score += results["score"] * weight
                total_weight += weight

        overall_score = total_score / total_weight if total_weight > 0 else 0

        # Test summary
        self.test_results["test_summary"] = {
            "overall_score": round(overall_score, 1),
            "category_scores": category_scores,
            "total_tests_run": sum(
                r.get("total_tests", 0)
                for r in [
                    analytics_results,
                    security_results,
                    integration_results,
                    cli_results,
                    complexity_results,
                    resource_results,
                ]
            ),
            "total_tests_passed": sum(
                r.get("passed_tests", 0)
                for r in [
                    analytics_results,
                    security_results,
                    integration_results,
                    cli_results,
                    complexity_results,
                    resource_results,
                ]
            ),
            "test_duration_seconds": round(time.time() - self.start_time, 2),
            "methodology_compliance": "Full crawl_mcp.py methodology compliance",
            "phase_status": "COMPLETE" if overall_score >= 80 else "NEEDS_IMPROVEMENT",
        }

        # Display summary table
        self.display_summary_table()

        return self.test_results

    def display_summary_table(self) -> None:
        """Display comprehensive test summary table."""

        summary = self.test_results["test_summary"]

        # Overall status table
        status_table = Table(title="Phase 9.8 Comprehensive Test Summary")
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="green")

        status_table.add_row("Overall Score", f"{summary['overall_score']}/100")
        status_table.add_row("Phase Status", summary["phase_status"])
        status_table.add_row(
            "Total Tests",
            f"{summary['total_tests_passed']}/{summary['total_tests_run']}",
        )
        status_table.add_row("Test Duration", f"{summary['test_duration_seconds']}s")
        status_table.add_row("Methodology", summary["methodology_compliance"])

        self.console.print(status_table)

        # Category scores table
        category_table = Table(title="Category Scores")
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Score", style="green")
        category_table.add_column("Status", style="yellow")

        for category, score in summary["category_scores"].items():
            status = (
                "✅ PASSED"
                if score >= 80
                else "⚠️ NEEDS IMPROVEMENT" if score >= 60 else "❌ FAILED"
            )
            category_table.add_row(category, f"{score:.1f}/100", status)

        self.console.print(category_table)

        # Final assessment
        if summary["overall_score"] >= 90:
            self.console.print(
                "🎉 EXCELLENT: Phase 9.8 implementation exceeds expectations!",
                style="green bold",
            )
        elif summary["overall_score"] >= 80:
            self.console.print(
                "✅ GOOD: Phase 9.8 implementation meets requirements!", style="green"
            )
        elif summary["overall_score"] >= 60:
            self.console.print(
                "⚠️ ACCEPTABLE: Phase 9.8 implementation needs some improvements",
                style="yellow",
            )
        else:
            self.console.print(
                "❌ NEEDS WORK: Phase 9.8 implementation requires significant improvements",
                style="red",
            )


def main():
    """Main function to run comprehensive Phase 9.8 testing."""

    # Initialize test reporter
    reporter = Phase98ComprehensiveTestReporter()

    # Generate comprehensive report
    results = reporter.generate_comprehensive_report()

    # Save results to file
    output_file = Path(__file__).parent / "phase_98_comprehensive_test_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    console.print(
        f"\n💾 Comprehensive test results saved to: {output_file}", style="dim"
    )

    return results


if __name__ == "__main__":
    main()
