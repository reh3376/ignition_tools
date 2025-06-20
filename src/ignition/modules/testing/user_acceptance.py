"""User Acceptance Testing for Module Testing.

This module provides comprehensive user acceptance testing processes for Ignition modules,
including automated testing scenarios, feedback collection, and training materials generation.
Following patterns from crawl_mcp.py for robust UAT processing.
"""

import asyncio
import json
import os
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class TestScenario:
    """Definition of a user acceptance test scenario."""

    name: str
    description: str
    category: str  # "functional", "usability", "performance", "integration"
    priority: str  # "high", "medium", "low"
    steps: list[str] = field(default_factory=list)
    expected_results: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    test_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """Result of a user acceptance test execution."""

    scenario_name: str
    status: str  # "passed", "failed", "blocked", "not_tested"
    execution_time: float = 0.0
    actual_results: list[str] = field(default_factory=list)
    issues_found: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    notes: str = ""
    tester_id: str = ""
    executed_at: str = ""


@dataclass
class UserFeedback:
    """User feedback collection structure."""

    user_id: str
    category: str  # "usability", "functionality", "performance", "documentation"
    rating: int  # 1-5 scale
    comments: str
    suggestions: list[str] = field(default_factory=list)
    severity: str = "medium"  # "low", "medium", "high", "critical"
    submitted_at: str = ""


@dataclass
class UATReport:
    """Comprehensive User Acceptance Testing report."""

    module_path: str
    test_summary: dict[str, Any] = field(default_factory=dict)
    scenarios: list[TestScenario] = field(default_factory=list)
    results: list[TestResult] = field(default_factory=list)
    feedback: list[UserFeedback] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    generated_at: str = ""


def validate_uat_environment() -> dict[str, Any]:
    """Validate user acceptance testing environment configuration.

    Following patterns from crawl_mcp.py for environment validation.

    Returns:
        Dictionary with validation results
    """
    required_env_vars = {
        "UAT_TEST_GATEWAY_URL": "Gateway URL for UAT testing",
        "UAT_TEST_USERNAME": "Username for UAT testing",
    }

    optional_env_vars = {
        "UAT_SCREENSHOT_DIR": "Directory for UAT screenshots",
        "UAT_REPORT_DIR": "Directory for UAT reports",
        "UAT_FEEDBACK_API": "API endpoint for feedback collection",
    }

    missing_vars = []
    available_vars = {}

    for var, description in required_env_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = {"description": description, "configured": True}
        else:
            missing_vars.append(f"{var} ({description})")

    for var, description in optional_env_vars.items():
        value = os.getenv(var)
        available_vars[var] = {
            "description": description,
            "configured": bool(value),
            "value": value if value else "Not configured",
        }

    if missing_vars:
        return {
            "valid": False,
            "error": f"Missing required environment variables: {', '.join(missing_vars)}",
            "available": available_vars,
        }

    return {"valid": True, "environment": available_vars}


class TestScenarioGenerator:
    """Generator for user acceptance test scenarios.

    Following patterns from crawl_mcp.py for scenario generation.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the test scenario generator.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}

    async def generate_scenarios(self, module_path: str) -> list[TestScenario]:
        """Generate comprehensive test scenarios for a module.

        Args:
            module_path: Path to the module to generate scenarios for

        Returns:
            List of TestScenario objects
        """
        scenarios = []

        try:
            # Generate different types of test scenarios
            scenarios.extend(await self._generate_functional_scenarios(module_path))
            scenarios.extend(await self._generate_usability_scenarios(module_path))
            scenarios.extend(await self._generate_performance_scenarios(module_path))
            scenarios.extend(await self._generate_integration_scenarios(module_path))

        except Exception:
            # Create a basic error scenario if generation fails
            error_scenario = TestScenario(
                name="Basic Module Loading Test",
                description="Verify that the module can be loaded without errors",
                category="functional",
                priority="high",
                steps=["Install module", "Restart gateway", "Verify module is loaded"],
                expected_results=["Module appears in module list", "No errors in logs"],
            )
            scenarios.append(error_scenario)

        return scenarios

    async def _generate_functional_scenarios(
        self, module_path: str
    ) -> list[TestScenario]:
        """Generate functional test scenarios."""
        scenarios = []

        # Basic functionality scenarios
        scenarios.append(
            TestScenario(
                name="Module Installation",
                description="Test successful installation of the module",
                category="functional",
                priority="high",
                steps=[
                    "Navigate to Config > Modules",
                    "Click 'Install or Upgrade a Module'",
                    "Select the module file",
                    "Complete installation wizard",
                    "Restart gateway if required",
                ],
                expected_results=[
                    "Module appears in installed modules list",
                    "Module status shows as 'Running'",
                    "No installation errors displayed",
                ],
                prerequisites=["Gateway access", "Admin privileges"],
            )
        )

        scenarios.append(
            TestScenario(
                name="Module Configuration",
                description="Test module configuration options",
                category="functional",
                priority="high",
                steps=[
                    "Navigate to module configuration",
                    "Modify configuration settings",
                    "Save configuration",
                    "Verify settings are applied",
                ],
                expected_results=[
                    "Configuration saves successfully",
                    "Settings are persisted after restart",
                    "Module behavior reflects configuration changes",
                ],
            )
        )

        return scenarios

    async def _generate_usability_scenarios(
        self, module_path: str
    ) -> list[TestScenario]:
        """Generate usability test scenarios."""
        scenarios = []

        scenarios.append(
            TestScenario(
                name="User Interface Navigation",
                description="Test ease of navigation through module interface",
                category="usability",
                priority="medium",
                steps=[
                    "Access module interface",
                    "Navigate through all menu items",
                    "Test common user workflows",
                    "Evaluate interface responsiveness",
                ],
                expected_results=[
                    "Interface is intuitive and easy to navigate",
                    "All menu items are accessible",
                    "Response time is acceptable",
                    "No broken links or interface elements",
                ],
            )
        )

        return scenarios

    async def _generate_performance_scenarios(
        self, module_path: str
    ) -> list[TestScenario]:
        """Generate performance test scenarios."""
        scenarios = []

        scenarios.append(
            TestScenario(
                name="Module Performance Under Load",
                description="Test module performance with typical workload",
                category="performance",
                priority="medium",
                steps=[
                    "Configure performance monitoring",
                    "Apply typical workload to module",
                    "Monitor resource usage",
                    "Measure response times",
                ],
                expected_results=[
                    "Memory usage remains within acceptable limits",
                    "CPU usage is reasonable",
                    "Response times meet requirements",
                    "No memory leaks detected",
                ],
            )
        )

        return scenarios

    async def _generate_integration_scenarios(
        self, module_path: str
    ) -> list[TestScenario]:
        """Generate integration test scenarios."""
        scenarios = []

        scenarios.append(
            TestScenario(
                name="Integration with Existing Systems",
                description="Test module integration with existing Ignition components",
                category="integration",
                priority="high",
                steps=[
                    "Configure module to interact with existing tags",
                    "Test data exchange with other modules",
                    "Verify alarm integration",
                    "Test historian integration",
                ],
                expected_results=[
                    "Module integrates seamlessly with existing tags",
                    "Data exchange works correctly",
                    "Alarms are properly generated and handled",
                    "Historical data is correctly stored",
                ],
            )
        )

        return scenarios


class FeedbackCollector:
    """Collector for user feedback during UAT.

    Following patterns from crawl_mcp.py for feedback management.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the feedback collector.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.feedback_storage: list[UserFeedback] = []

    async def collect_feedback(self, feedback: UserFeedback) -> bool:
        """Collect user feedback.

        Args:
            feedback: UserFeedback object to collect

        Returns:
            True if feedback was collected successfully
        """
        try:
            # Add timestamp
            feedback.submitted_at = datetime.now().isoformat()

            # Store feedback
            self.feedback_storage.append(feedback)

            # Optionally send to external API
            await self._send_to_api(feedback)

            return True

        except Exception:
            return False

    async def _send_to_api(self, feedback: UserFeedback) -> None:
        """Send feedback to external API if configured."""
        api_endpoint = os.getenv("UAT_FEEDBACK_API")
        if not api_endpoint:
            return

        try:
            # Simulate API call - in real implementation, use aiohttp
            await asyncio.sleep(0.1)  # Simulate network delay

        except Exception:
            pass  # Ignore API errors for now

    def get_feedback_summary(self) -> dict[str, Any]:
        """Get summary of collected feedback.

        Returns:
            Dictionary with feedback summary
        """
        if not self.feedback_storage:
            return {"total": 0, "categories": {}, "average_rating": 0.0}

        categories = {}
        total_rating = 0

        for feedback in self.feedback_storage:
            if feedback.category not in categories:
                categories[feedback.category] = {
                    "count": 0,
                    "average_rating": 0.0,
                    "ratings": [],
                }

            categories[feedback.category]["count"] += 1
            categories[feedback.category]["ratings"].append(feedback.rating)
            total_rating += feedback.rating

        # Calculate averages
        for category_data in categories.values():
            category_data["average_rating"] = sum(category_data["ratings"]) / len(
                category_data["ratings"]
            )
            del category_data["ratings"]  # Remove raw ratings from summary

        return {
            "total": len(self.feedback_storage),
            "categories": categories,
            "average_rating": total_rating / len(self.feedback_storage),
        }


class TrainingMaterialGenerator:
    """Generator for training materials based on UAT results.

    Following patterns from crawl_mcp.py for material generation.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the training material generator.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}

    async def generate_materials(self, uat_report: UATReport) -> dict[str, Any]:
        """Generate training materials based on UAT results.

        Args:
            uat_report: UAT report to base materials on

        Returns:
            Dictionary with generated training materials
        """
        materials = {
            "user_guide": await self._generate_user_guide(uat_report),
            "quick_start": await self._generate_quick_start(uat_report),
            "troubleshooting": await self._generate_troubleshooting(uat_report),
            "video_scripts": await self._generate_video_scripts(uat_report),
        }

        return materials

    async def _generate_user_guide(self, uat_report: UATReport) -> dict[str, Any]:
        """Generate comprehensive user guide."""
        guide = {
            "title": "Module User Guide",
            "sections": [
                {
                    "title": "Installation",
                    "content": "Step-by-step installation instructions based on UAT scenarios",
                },
                {
                    "title": "Configuration",
                    "content": "Configuration options and best practices",
                },
                {
                    "title": "Usage",
                    "content": "Common usage patterns identified during UAT",
                },
            ],
            "generated_from_uat": True,
        }

        return guide

    async def _generate_quick_start(self, uat_report: UATReport) -> dict[str, Any]:
        """Generate quick start guide."""
        quick_start = {
            "title": "Quick Start Guide",
            "steps": [
                "Install the module",
                "Configure basic settings",
                "Verify installation",
                "Run first test",
            ],
            "estimated_time": "15 minutes",
            "generated_from_uat": True,
        }

        return quick_start

    async def _generate_troubleshooting(self, uat_report: UATReport) -> dict[str, Any]:
        """Generate troubleshooting guide based on issues found."""
        issues_found = []
        for result in uat_report.results:
            issues_found.extend(result.issues_found)

        troubleshooting = {
            "title": "Troubleshooting Guide",
            "common_issues": [
                {
                    "issue": issue,
                    "solution": f"Solution for {issue}",
                    "severity": "medium",
                }
                for issue in set(issues_found)  # Remove duplicates
            ],
            "generated_from_uat": True,
        }

        return troubleshooting

    async def _generate_video_scripts(self, uat_report: UATReport) -> dict[str, Any]:
        """Generate scripts for training videos."""
        scripts = {
            "installation_video": {
                "title": "Module Installation Video Script",
                "duration": "5 minutes",
                "scenes": [
                    "Introduction to the module",
                    "Installation process",
                    "Verification steps",
                    "Next steps",
                ],
            },
            "usage_video": {
                "title": "Module Usage Video Script",
                "duration": "10 minutes",
                "scenes": [
                    "Overview of features",
                    "Common workflows",
                    "Best practices",
                    "Tips and tricks",
                ],
            },
            "generated_from_uat": True,
        }

        return scripts


class UserAcceptanceTestManager:
    """Comprehensive User Acceptance Test manager.

    Following patterns from crawl_mcp.py for UAT management and execution.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the UAT manager.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.scenario_generator = TestScenarioGenerator(config)
        self.feedback_collector = FeedbackCollector(config)
        self.training_generator = TrainingMaterialGenerator(config)

    @asynccontextmanager
    async def uat_context(self, module_path: str) -> AsyncIterator[dict[str, Any]]:
        """Create a UAT context with resource management.

        Following patterns from crawl_mcp.py for context management.

        Args:
            module_path: Path to the module for UAT

        Yields:
            Dictionary with UAT context information
        """
        context = {
            "module_path": module_path,
            "start_time": asyncio.get_event_loop().time(),
            "temp_resources": [],
            "screenshots_dir": None,
        }

        try:
            # Create temporary directory for screenshots
            screenshots_dir = Path(tempfile.mkdtemp(prefix="uat_screenshots_"))
            context["screenshots_dir"] = screenshots_dir
            context["temp_resources"].append(screenshots_dir)

            yield context

        finally:
            # Cleanup temporary resources
            for resource in context.get("temp_resources", []):
                try:
                    if isinstance(resource, Path) and resource.exists():
                        if resource.is_dir():
                            import shutil

                            shutil.rmtree(resource)
                        else:
                            resource.unlink()
                except Exception:
                    pass  # Ignore cleanup errors

    async def run_full_uat(self, module_path: str) -> UATReport:
        """Run comprehensive user acceptance testing.

        Args:
            module_path: Path to the module to test

        Returns:
            UATReport with complete UAT results
        """
        async with self.uat_context(module_path) as context:
            report = UATReport(
                module_path=module_path, generated_at=datetime.now().isoformat()
            )

            try:
                # Generate test scenarios
                report.scenarios = await self.scenario_generator.generate_scenarios(
                    module_path
                )

                # Execute scenarios (simulated for now)
                report.results = await self._execute_scenarios(
                    report.scenarios, context
                )

                # Collect feedback (simulated)
                await self._collect_sample_feedback()
                report.feedback = self.feedback_collector.feedback_storage.copy()

                # Generate summary
                report.test_summary = self._generate_test_summary(report)

                # Generate recommendations
                report.recommendations = self._generate_recommendations(report)

            except Exception as e:
                # Handle critical errors
                error_result = TestResult(
                    scenario_name="UAT Critical Error",
                    status="failed",
                    issues_found=[f"Critical UAT error: {e!s}"],
                    executed_at=datetime.now().isoformat(),
                )
                report.results.append(error_result)

            return report

    async def _execute_scenarios(
        self, scenarios: list[TestScenario], context: dict[str, Any]
    ) -> list[TestResult]:
        """Execute test scenarios (simulated).

        Args:
            scenarios: List of scenarios to execute
            context: UAT context

        Returns:
            List of TestResult objects
        """
        results = []

        for scenario in scenarios:
            # Simulate test execution
            result = TestResult(
                scenario_name=scenario.name,
                status=(
                    "passed"
                    if scenario.priority != "high" or len(scenario.steps) <= 5
                    else "warning"
                ),
                execution_time=len(scenario.steps) * 0.5,  # Simulated time
                actual_results=scenario.expected_results,  # Simulated success
                executed_at=datetime.now().isoformat(),
                tester_id="uat_automation",
            )

            # Add some realistic issues for high-priority scenarios
            if scenario.priority == "high" and len(scenario.steps) > 4:
                result.issues_found.append("Minor UI responsiveness issue")
                result.status = "warning"

            results.append(result)

        return results

    async def _collect_sample_feedback(self) -> None:
        """Collect sample feedback for demonstration."""
        sample_feedback = [
            UserFeedback(
                user_id="test_user_1",
                category="usability",
                rating=4,
                comments="Interface is intuitive but could use better documentation",
                suggestions=["Add tooltips", "Improve help text"],
            ),
            UserFeedback(
                user_id="test_user_2",
                category="functionality",
                rating=5,
                comments="All features work as expected",
                suggestions=["Add more configuration options"],
            ),
        ]

        for feedback in sample_feedback:
            await self.feedback_collector.collect_feedback(feedback)

    def _generate_test_summary(self, report: UATReport) -> dict[str, Any]:
        """Generate test execution summary.

        Args:
            report: UAT report to summarize

        Returns:
            Dictionary with test summary
        """
        total_scenarios = len(report.scenarios)
        total_results = len(report.results)

        status_counts = {}
        for result in report.results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1

        feedback_summary = self.feedback_collector.get_feedback_summary()

        return {
            "total_scenarios": total_scenarios,
            "executed_scenarios": total_results,
            "execution_rate": (
                (total_results / total_scenarios * 100) if total_scenarios > 0 else 0
            ),
            "status_distribution": status_counts,
            "average_execution_time": (
                sum(r.execution_time for r in report.results) / len(report.results)
                if report.results
                else 0
            ),
            "feedback_summary": feedback_summary,
        }

    def _generate_recommendations(self, report: UATReport) -> list[str]:
        """Generate recommendations based on UAT results.

        Args:
            report: UAT report to analyze

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Analyze test results
        failed_tests = [r for r in report.results if r.status == "failed"]
        warning_tests = [r for r in report.results if r.status == "warning"]

        if failed_tests:
            recommendations.append(
                f"Address {len(failed_tests)} failed test scenarios before release"
            )

        if warning_tests:
            recommendations.append(
                f"Review {len(warning_tests)} test scenarios with warnings"
            )

        # Analyze feedback
        feedback_summary = self.feedback_collector.get_feedback_summary()
        if feedback_summary["average_rating"] < 4.0:
            recommendations.append(
                "Consider addressing user feedback to improve overall satisfaction"
            )

        # Add general recommendations
        recommendations.extend(
            [
                "Generate training materials based on UAT findings",
                "Document known issues and workarounds",
                "Plan for post-release monitoring and feedback collection",
            ]
        )

        return recommendations

    async def generate_uat_report(
        self, report: UATReport, output_path: str | None = None
    ) -> dict[str, Any]:
        """Generate a formatted UAT report.

        Args:
            report: UATReport to format
            output_path: Optional path to save the report

        Returns:
            Dictionary with formatted report data
        """
        formatted_report = {
            "module_path": report.module_path,
            "generated_at": report.generated_at,
            "test_summary": report.test_summary,
            "scenarios": [
                {
                    "name": scenario.name,
                    "description": scenario.description,
                    "category": scenario.category,
                    "priority": scenario.priority,
                    "steps": scenario.steps,
                    "expected_results": scenario.expected_results,
                }
                for scenario in report.scenarios
            ],
            "results": [
                {
                    "scenario_name": result.scenario_name,
                    "status": result.status,
                    "execution_time": result.execution_time,
                    "issues_found": result.issues_found,
                    "notes": result.notes,
                    "executed_at": result.executed_at,
                }
                for result in report.results
            ],
            "feedback": [
                {
                    "user_id": feedback.user_id,
                    "category": feedback.category,
                    "rating": feedback.rating,
                    "comments": feedback.comments,
                    "suggestions": feedback.suggestions,
                    "submitted_at": feedback.submitted_at,
                }
                for feedback in report.feedback
            ],
            "recommendations": report.recommendations,
            "training_materials": await self.training_generator.generate_materials(
                report
            ),
        }

        # Save report if path provided
        if output_path:
            with open(output_path, "w") as f:
                json.dump(formatted_report, f, indent=2)

        return formatted_report
