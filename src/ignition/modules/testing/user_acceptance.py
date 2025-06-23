"""User Acceptance Testing Framework for Ignition Modules.

Provides comprehensive user acceptance testing infrastructure including
scenario management, feedback collection, and UAT pipeline management
following patterns from crawl_mcp.py for validation, error handling,
and resource management.
"""

import asyncio
import json
import os
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TestScenarioStatus(Enum):
    """Status of test scenario."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TestScenarioType(Enum):
    """Type of test scenario."""

    FUNCTIONAL = "functional"
    USABILITY = "usability"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    COMPATIBILITY = "compatibility"
    REGRESSION = "regression"
    INTEGRATION = "integration"


class FeedbackType(Enum):
    """Type of user feedback."""

    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    USABILITY_ISSUE = "usability_issue"
    PERFORMANCE_ISSUE = "performance_issue"
    GENERAL_FEEDBACK = "general_feedback"


@dataclass
class TestScenario:
    """User acceptance test scenario definition."""

    id: str
    name: str
    description: str
    scenario_type: TestScenarioType
    priority: str = "medium"  # "low", "medium", "high", "critical"
    preconditions: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    expected_result: str = ""
    acceptance_criteria: list[str] = field(default_factory=list)
    estimated_duration: int = 30  # minutes
    status: TestScenarioStatus = TestScenarioStatus.PENDING
    actual_result: str = ""
    notes: str = ""
    tester_id: str = ""
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """Result of test scenario execution."""

    scenario_id: str
    status: TestScenarioStatus
    actual_result: str
    execution_time: float
    tester_id: str
    timestamp: float
    notes: str = ""
    screenshots: list[str] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    issues_found: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UserFeedback:
    """User feedback during testing."""

    id: str
    feedback_type: FeedbackType
    title: str
    description: str
    severity: str = "medium"  # "low", "medium", "high", "critical"
    user_id: str = ""
    scenario_id: str = ""
    timestamp: float = 0.0
    status: str = "open"  # "open", "acknowledged", "resolved", "closed"
    tags: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UATReport:
    """User acceptance testing report."""

    module_path: str
    total_scenarios: int
    executed_scenarios: int
    passed_scenarios: int
    failed_scenarios: int
    blocked_scenarios: int
    skipped_scenarios: int
    overall_status: str
    duration: float
    scenarios: list[TestScenario] = field(default_factory=list)
    results: list[TestResult] = field(default_factory=list)
    feedback: list[UserFeedback] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


def validate_uat_environment() -> dict[str, Any]:
    """Validate UAT environment configuration.

    Following patterns from crawl_mcp.py for environment validation.

    Returns:
        Dictionary with validation results
    """
    required_vars = {
        "UAT_IGNITION_VERSION": "Ignition version for UAT",
        "UAT_GATEWAY_URL": "UAT Gateway URL",
    }

    optional_vars = {
        "UAT_TESTER_COUNT": "Number of concurrent testers",
        "UAT_TIMEOUT": "UAT timeout in seconds",
        "UAT_FEEDBACK_WEBHOOK": "Webhook for feedback notifications",
        "UAT_SCREENSHOT_PATH": "Path for screenshot storage",
        "UAT_LOG_LEVEL": "Logging level for UAT",
    }

    missing_required = []
    available_vars = {}

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = value
        else:
            missing_required.append(f"{var} ({description})")

    for var, _description in optional_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = value

    if missing_required:
        return {
            "valid": False,
            "error": f"Missing required environment variables: {', '.join(missing_required)}",
            "available": available_vars,
        }

    return {"valid": True, "variables": available_vars}


def format_uat_error(error: Exception) -> str:
    """Format UAT errors for user-friendly messages.

    Following patterns from crawl_mcp.py for error formatting.

    Args:
        error: The exception to format

    Returns:
        Formatted error message
    """
    error_str = str(error).lower()

    if "timeout" in error_str:
        return "UAT scenario timed out. Consider increasing timeout or simplifying test steps."
    elif "connection" in error_str:
        return "Connection to UAT environment failed. Check Gateway status and connectivity."
    elif "authentication" in error_str or "authorization" in error_str:
        return "Authentication failed. Check UAT user credentials and permissions."
    elif "scenario" in error_str and "not found" in error_str:
        return "Test scenario not found. Check scenario ID and availability."
    elif "tester" in error_str and "not available" in error_str:
        return "Tester not available. Check tester assignment and availability."
    else:
        return f"UAT error: {error!s}"


class UserAcceptanceTestManager:
    """User acceptance test manager for Ignition modules.

    Following patterns from crawl_mcp.py for robust testing,
    error handling, and resource management.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the UAT manager.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.temp_dir: Path | None = None
        self.scenarios: list[TestScenario] = []
        self.results: list[TestResult] = []
        self.feedback: list[UserFeedback] = []
        self.report: UATReport | None = None

        # Load configuration from environment
        self.ignition_version = os.getenv("UAT_IGNITION_VERSION", "8.1.0")
        self.gateway_url = os.getenv("UAT_GATEWAY_URL", "http://localhost:8088")
        self.max_testers = int(os.getenv("UAT_TESTER_COUNT", "5"))
        self.timeout = int(os.getenv("UAT_TIMEOUT", "3600"))
        self.screenshot_path = Path(
            os.getenv("UAT_SCREENSHOT_PATH", "./uat_screenshots")
        )
        self.log_level = os.getenv("UAT_LOG_LEVEL", "INFO")

    @asynccontextmanager
    async def uat_context(
        self, module_path: str
    ) -> AsyncIterator["UserAcceptanceTestManager"]:
        """Create UAT context with resource management.

        Following patterns from crawl_mcp.py for context management.

        Args:
            module_path: Path to the module

        Yields:
            UserAcceptanceTestManager instance
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)

            # Ensure screenshot directory exists
            self.screenshot_path.mkdir(parents=True, exist_ok=True)

            try:
                await self.initialize_scenarios(module_path)
                yield self
            finally:
                await self.cleanup()

    async def initialize_scenarios(self, module_path: str) -> None:
        """Initialize test scenarios for the module.

        Args:
            module_path: Path to the module
        """
        # Store module path for reference
        self._module_path = module_path
        # Define standard UAT scenarios
        self.scenarios = [
            TestScenario(
                id="uat_001",
                name="Module Installation",
                description="Verify module can be installed successfully",
                scenario_type=TestScenarioType.FUNCTIONAL,
                priority="high",
                preconditions=[
                    "Clean Ignition Gateway installation",
                    "Administrator access to Gateway",
                ],
                steps=[
                    "Navigate to Gateway Config > Modules",
                    "Click 'Install or Upgrade a Module'",
                    "Select the module file",
                    "Follow installation wizard",
                    "Restart Gateway if required",
                ],
                expected_result="Module appears in installed modules list with 'Running' status",
                acceptance_criteria=[
                    "Module installs without errors",
                    "No error messages in Gateway logs",
                    "Module status shows as 'Running'",
                ],
                estimated_duration=15,
            ),
            TestScenario(
                id="uat_002",
                name="Basic Functionality",
                description="Verify core module functionality works as expected",
                scenario_type=TestScenarioType.FUNCTIONAL,
                priority="critical",
                preconditions=[
                    "Module successfully installed",
                    "Gateway running normally",
                ],
                steps=[
                    "Open Designer",
                    "Create new project",
                    "Test module features",
                    "Save project",
                ],
                expected_result="All core module features work without errors",
                acceptance_criteria=[
                    "Module features accessible in Designer",
                    "No runtime errors during testing",
                    "Expected outputs produced",
                ],
                estimated_duration=45,
            ),
            TestScenario(
                id="uat_003",
                name="Gateway Web Interface",
                description="Verify module configuration through Gateway web interface",
                scenario_type=TestScenarioType.USABILITY,
                priority="medium",
                preconditions=[
                    "Module installed and running",
                    "Web browser access to Gateway",
                ],
                steps=[
                    "Open Gateway web interface",
                    "Navigate to module configuration",
                    "Modify module settings",
                    "Save configuration",
                    "Verify changes applied",
                ],
                expected_result="Module configuration interface is intuitive and functional",
                acceptance_criteria=[
                    "Configuration pages load without errors",
                    "Settings can be modified and saved",
                    "Help documentation is accessible",
                ],
                estimated_duration=30,
            ),
            TestScenario(
                id="uat_004",
                name="Performance Under Load",
                description="Verify module performs adequately under typical load",
                scenario_type=TestScenarioType.PERFORMANCE,
                priority="medium",
                preconditions=[
                    "Module installed and configured",
                    "Test data available",
                ],
                steps=[
                    "Generate typical workload",
                    "Monitor module performance",
                    "Check system resource usage",
                    "Verify response times",
                ],
                expected_result="Module maintains acceptable performance under load",
                acceptance_criteria=[
                    "Response times within acceptable limits",
                    "No memory leaks detected",
                    "System remains stable",
                ],
                estimated_duration=60,
            ),
            TestScenario(
                id="uat_005",
                name="Module Uninstallation",
                description="Verify module can be uninstalled cleanly",
                scenario_type=TestScenarioType.FUNCTIONAL,
                priority="medium",
                preconditions=[
                    "Module installed and tested",
                    "Administrator access",
                ],
                steps=[
                    "Navigate to Gateway Config > Modules",
                    "Select installed module",
                    "Click 'Uninstall'",
                    "Confirm uninstallation",
                    "Restart Gateway if required",
                ],
                expected_result="Module is completely removed from system",
                acceptance_criteria=[
                    "Module no longer appears in modules list",
                    "No error messages during uninstallation",
                    "System operates normally after removal",
                ],
                estimated_duration=10,
            ),
        ]

    async def execute_scenario(self, scenario_id: str, tester_id: str) -> TestResult:
        """Execute a single test scenario.

        Args:
            scenario_id: ID of the scenario to execute
            tester_id: ID of the tester executing the scenario

        Returns:
            TestResult with execution results
        """
        scenario = next((s for s in self.scenarios if s.id == scenario_id), None)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        scenario.status = TestScenarioStatus.RUNNING
        start_time = asyncio.get_event_loop().time()

        try:
            # Create test result
            result = TestResult(
                scenario_id=scenario_id,
                status=TestScenarioStatus.PENDING,
                actual_result="",
                execution_time=0.0,
                tester_id=tester_id,
                timestamp=start_time,
            )

            # Simulate scenario execution
            # In a real implementation, this would involve actual testing
            await asyncio.sleep(2)  # Simulate test execution time

            # For demo purposes, randomly determine result
            import random

            success_rate = 0.8  # 80% success rate
            if random.random() < success_rate:
                result.status = TestScenarioStatus.PASSED
                result.actual_result = scenario.expected_result
                scenario.status = TestScenarioStatus.PASSED
            else:
                result.status = TestScenarioStatus.FAILED
                result.actual_result = "Test failed - see notes for details"
                result.notes = "Example failure for demonstration"
                scenario.status = TestScenarioStatus.FAILED

            end_time = asyncio.get_event_loop().time()
            result.execution_time = end_time - start_time
            scenario.execution_time = result.execution_time

            self.results.append(result)
            return result

        except Exception as e:
            scenario.status = TestScenarioStatus.FAILED
            result = TestResult(
                scenario_id=scenario_id,
                status=TestScenarioStatus.FAILED,
                actual_result="",
                execution_time=0.0,
                tester_id=tester_id,
                timestamp=start_time,
                notes=format_uat_error(e),
            )
            self.results.append(result)
            raise RuntimeError(format_uat_error(e)) from e

    async def run_all_scenarios(
        self, tester_assignments: dict[str, str] | None = None
    ) -> UATReport:
        """Run all test scenarios.

        Args:
            tester_assignments: Optional mapping of scenario_id to tester_id

        Returns:
            UATReport with all results
        """
        if not self.scenarios:
            raise RuntimeError("No scenarios initialized")

        start_time = asyncio.get_event_loop().time()

        # Default tester assignments
        assignments = tester_assignments or {
            scenario.id: f"tester_{i % self.max_testers + 1}"
            for i, scenario in enumerate(self.scenarios)
        }

        # Execute scenarios with concurrency control
        semaphore = asyncio.Semaphore(self.max_testers)
        tasks = []

        for scenario in self.scenarios:
            tester_id = assignments.get(scenario.id, "default_tester")
            task = asyncio.create_task(
                self._execute_with_semaphore(scenario.id, tester_id, semaphore)
            )
            tasks.append(task)

        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            raise RuntimeError(format_uat_error(e)) from e

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        # Generate report
        self.report = self._generate_report(duration)
        return self.report

    async def _execute_with_semaphore(
        self, scenario_id: str, tester_id: str, semaphore: asyncio.Semaphore
    ) -> None:
        """Execute scenario with semaphore control.

        Args:
            scenario_id: ID of the scenario
            tester_id: ID of the tester
            semaphore: Semaphore for concurrency control
        """
        import contextlib

        async with semaphore:
            with contextlib.suppress(Exception):
                await self.execute_scenario(scenario_id, tester_id)

    def add_feedback(self, feedback: UserFeedback) -> None:
        """Add user feedback.

        Args:
            feedback: UserFeedback to add
        """
        feedback.timestamp = asyncio.get_event_loop().time()
        if not feedback.id:
            feedback.id = f"feedback_{len(self.feedback) + 1}"
        self.feedback.append(feedback)

    def get_scenario_status(self, scenario_id: str) -> TestScenarioStatus | None:
        """Get status of a scenario.

        Args:
            scenario_id: ID of the scenario

        Returns:
            TestScenarioStatus or None if not found
        """
        scenario = next((s for s in self.scenarios if s.id == scenario_id), None)
        return scenario.status if scenario else None

    def _generate_report(self, total_duration: float) -> UATReport:
        """Generate UAT report.

        Args:
            total_duration: Total time taken for all scenarios

        Returns:
            UATReport with results
        """
        executed_scenarios = len(self.results)
        passed_scenarios = sum(
            1 for r in self.results if r.status == TestScenarioStatus.PASSED
        )
        failed_scenarios = sum(
            1 for r in self.results if r.status == TestScenarioStatus.FAILED
        )
        blocked_scenarios = sum(
            1 for s in self.scenarios if s.status == TestScenarioStatus.BLOCKED
        )
        skipped_scenarios = sum(
            1 for s in self.scenarios if s.status == TestScenarioStatus.SKIPPED
        )

        # Determine overall status
        if failed_scenarios > 0:
            overall_status = "failed"
        elif blocked_scenarios > 0:
            overall_status = "blocked"
        elif executed_scenarios == len(self.scenarios):
            overall_status = "passed"
        else:
            overall_status = "in_progress"

        # Calculate metrics
        pass_rate = (
            (passed_scenarios / executed_scenarios * 100)
            if executed_scenarios > 0
            else 0
        )
        avg_execution_time = (
            sum(r.execution_time for r in self.results) / len(self.results)
            if self.results
            else 0
        )

        return UATReport(
            module_path="",  # Will be set by caller
            total_scenarios=len(self.scenarios),
            executed_scenarios=executed_scenarios,
            passed_scenarios=passed_scenarios,
            failed_scenarios=failed_scenarios,
            blocked_scenarios=blocked_scenarios,
            skipped_scenarios=skipped_scenarios,
            overall_status=overall_status,
            duration=total_duration,
            scenarios=self.scenarios.copy(),
            results=self.results.copy(),
            feedback=self.feedback.copy(),
            recommendations=self._generate_recommendations(),
            metrics={
                "pass_rate": pass_rate,
                "average_execution_time": avg_execution_time,
                "max_testers": self.max_testers,
                "total_feedback": len(self.feedback),
            },
            metadata={
                "ignition_version": self.ignition_version,
                "gateway_url": self.gateway_url,
                "timeout": self.timeout,
            },
        )

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on UAT results.

        Returns:
            list of recommendations
        """
        recommendations = []

        failed_results = [
            r for r in self.results if r.status == TestScenarioStatus.FAILED
        ]
        blocked_scenarios = [
            s for s in self.scenarios if s.status == TestScenarioStatus.BLOCKED
        ]

        if failed_results:
            recommendations.append(
                "Review and fix failed test scenarios before release"
            )

            # Specific recommendations based on scenario types
            failed_types = {
                next(s for s in self.scenarios if s.id == r.scenario_id).scenario_type
                for r in failed_results
            }

            if TestScenarioType.FUNCTIONAL in failed_types:
                recommendations.append(
                    "Address functional issues - core features not working correctly"
                )
            if TestScenarioType.PERFORMANCE in failed_types:
                recommendations.append(
                    "Optimize performance - module not meeting performance requirements"
                )
            if TestScenarioType.USABILITY in failed_types:
                recommendations.append("Improve user interface and user experience")

        if blocked_scenarios:
            recommendations.append("Resolve blocking issues preventing test execution")

        # Feedback-based recommendations
        critical_feedback = [f for f in self.feedback if f.severity == "critical"]
        if critical_feedback:
            recommendations.append("Address critical user feedback before release")

        bug_reports = [
            f for f in self.feedback if f.feedback_type == FeedbackType.BUG_REPORT
        ]
        if len(bug_reports) > 3:
            recommendations.append("Review and fix multiple bug reports from testers")

        if not recommendations:
            recommendations.append(
                "All UAT scenarios passed - module ready for release"
            )

        return recommendations

    async def cleanup(self) -> None:
        """Clean up UAT resources."""
        # Clean up temporary files and resources
        if self.temp_dir and self.temp_dir.exists():
            import shutil

            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

    def export_report(self, output_path: str | None = None) -> dict[str, Any]:
        """Export UAT report to file or return as dict.

        Args:
            output_path: Optional path to save report

        Returns:
            Report data as dictionary
        """
        if not self.report:
            raise RuntimeError("No report available - run scenarios first")

        report_data = {
            "module_path": self.report.module_path,
            "timestamp": asyncio.get_event_loop().time(),
            "summary": {
                "overall_status": self.report.overall_status,
                "total_scenarios": self.report.total_scenarios,
                "executed_scenarios": self.report.executed_scenarios,
                "passed_scenarios": self.report.passed_scenarios,
                "failed_scenarios": self.report.failed_scenarios,
                "blocked_scenarios": self.report.blocked_scenarios,
                "skipped_scenarios": self.report.skipped_scenarios,
                "duration": self.report.duration,
            },
            "scenarios": [
                {
                    "id": scenario.id,
                    "name": scenario.name,
                    "type": scenario.scenario_type.value,
                    "priority": scenario.priority,
                    "status": scenario.status.value,
                    "estimated_duration": scenario.estimated_duration,
                    "execution_time": scenario.execution_time,
                }
                for scenario in self.report.scenarios
            ],
            "results": [
                {
                    "scenario_id": result.scenario_id,
                    "status": result.status.value,
                    "tester_id": result.tester_id,
                    "execution_time": result.execution_time,
                    "notes": result.notes,
                }
                for result in self.report.results
            ],
            "feedback": [
                {
                    "id": feedback.id,
                    "type": feedback.feedback_type.value,
                    "title": feedback.title,
                    "severity": feedback.severity,
                    "status": feedback.status,
                    "user_id": feedback.user_id,
                    "scenario_id": feedback.scenario_id,
                }
                for feedback in self.report.feedback
            ],
            "recommendations": self.report.recommendations,
            "metrics": self.report.metrics,
            "metadata": self.report.metadata,
        }

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(report_data, f, indent=2)

        return report_data
