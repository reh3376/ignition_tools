"""Test Scenario Runner for Ignition Module Testing.

Provides orchestration and integration of all testing components including
module validation, compatibility testing, performance testing, and user
acceptance testing. Following patterns from crawl_mcp.py for comprehensive
testing workflow management.
"""

import asyncio
import json
import os
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .compatibility import CompatibilityTester
from .module_validator import ModuleValidator
from .performance import ModulePerformanceTester
from .quality_assurance import QualityAssurancePipeline
from .test_environment import TestEnvironmentManager
from .user_acceptance import UserAcceptanceTestManager

# Load environment variables
load_dotenv()


class TestPhase(Enum):
    """Test execution phases."""

    VALIDATION = "validation"
    QUALITY_ASSURANCE = "quality_assurance"
    COMPATIBILITY = "compatibility"
    PERFORMANCE = "performance"
    USER_ACCEPTANCE = "user_acceptance"


class TestSuite(Enum):
    """Test suite types."""

    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"


class TestResult(Enum):
    """Overall test result status."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestScenarioConfig:
    """Configuration for test scenario execution."""

    suite_type: TestSuite = TestSuite.STANDARD
    enabled_phases: list[TestPhase] = field(default_factory=lambda: list(TestPhase))
    parallel_execution: bool = True
    fail_fast: bool = False
    timeout: int = 3600  # seconds
    environment_type: str = "local"  # "local", "docker", "cloud"
    custom_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseResult:
    """Result of a single test phase."""

    phase: TestPhase
    status: TestResult
    duration: float
    report: Any  # ValidationReport, CompatibilityReport, etc.
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestScenarioReport:
    """Comprehensive test scenario report."""

    module_path: str
    scenario_config: TestScenarioConfig
    overall_status: TestResult
    total_duration: float
    phase_results: list[PhaseResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    generated_at: float = 0.0


def validate_scenario_environment() -> dict[str, Any]:
    """Validate test scenario environment.

    Returns:
        Dictionary with validation results
    """
    # No strictly required vars for scenario runner

    optional_vars = {
        "TEST_SCENARIO_SUITE": "Default test suite type",
        "TEST_SCENARIO_TIMEOUT": "Default scenario timeout",
        "TEST_SCENARIO_PARALLEL": "Enable parallel test execution",
        "TEST_RESULTS_PATH": "Path for test results",
        "TEST_ENVIRONMENT_TYPE": "Default test environment type",
    }

    available_vars = {}

    for var, _description in optional_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = value

    return {"valid": True, "variables": available_vars}


def format_scenario_error(error: Exception) -> str:
    """Format scenario errors for user-friendly messages.

    Args:
        error: The exception to format

    Returns:
        Formatted error message
    """
    error_str = str(error).lower()

    if "timeout" in error_str:
        return "Test scenario timed out. Consider increasing timeout or reducing test scope."
    elif "memory" in error_str:
        return "Memory error during test scenario. Reduce test complexity or system load."
    elif "environment" in error_str:
        return "Test environment error. Check environment setup and configuration."
    elif "validation" in error_str:
        return "Module validation failed. Fix validation issues before continuing."
    elif "compatibility" in error_str:
        return "Compatibility test failed. Review compatibility requirements."
    else:
        return f"Test scenario error: {error!s}"


class TestScenarioRunner:
    """Comprehensive test scenario runner for Ignition modules.

    Following patterns from crawl_mcp.py for orchestration,
    error handling, and resource management.
    """

    def __init__(self, config: TestScenarioConfig | None = None):
        """Initialize the test scenario runner.

        Args:
            config: Optional test scenario configuration
        """
        self.config = config or TestScenarioConfig()
        self.phase_results: list[PhaseResult] = []
        self.report: TestScenarioReport | None = None

        # Load configuration from environment
        self._load_environment_config()

        # Initialize test components
        self.env_manager = TestEnvironmentManager()
        self.module_validator = ModuleValidator()
        self.qa_pipeline = QualityAssurancePipeline()
        self.compatibility_tester = CompatibilityTester()
        self.performance_tester = ModulePerformanceTester()
        self.uat_manager = UserAcceptanceTestManager()

        # Results storage
        self.results_path = Path(os.getenv("TEST_RESULTS_PATH", "./test_results"))

    def _load_environment_config(self) -> None:
        """Load configuration from environment variables."""
        # Override config with environment variables if available
        suite_env = os.getenv("TEST_SCENARIO_SUITE")
        if suite_env:
            with suppress(ValueError):
                self.config.suite_type = TestSuite(suite_env.lower())

        timeout_env = os.getenv("TEST_SCENARIO_TIMEOUT")
        if timeout_env:
            with suppress(ValueError):
                self.config.timeout = int(timeout_env)

        parallel_env = os.getenv("TEST_SCENARIO_PARALLEL")
        if parallel_env:
            self.config.parallel_execution = parallel_env.lower() in (
                "true",
                "1",
                "yes",
            )

        env_type = os.getenv("TEST_ENVIRONMENT_TYPE")
        if env_type:
            self.config.environment_type = env_type

        # Set default enabled phases based on suite type
        if not self.config.enabled_phases:
            self.config.enabled_phases = self._get_default_phases()

    def _get_default_phases(self) -> list[TestPhase]:
        """Get default phases for suite type."""
        if self.config.suite_type == TestSuite.QUICK:
            return [TestPhase.VALIDATION, TestPhase.QUALITY_ASSURANCE]
        elif self.config.suite_type == TestSuite.STANDARD:
            return [
                TestPhase.VALIDATION,
                TestPhase.QUALITY_ASSURANCE,
                TestPhase.COMPATIBILITY,
                TestPhase.PERFORMANCE,
            ]
        elif self.config.suite_type == TestSuite.COMPREHENSIVE:
            return list(TestPhase)
        else:  # CUSTOM
            return list(TestPhase)  # All phases, user can disable specific ones

    @asynccontextmanager
    async def scenario_context(self, module_path: str) -> AsyncIterator["TestScenarioRunner"]:
        """Create test scenario context with resource management.

        Args:
            module_path: Path to the module

        Yields:
            TestScenarioRunner instance
        """
        # Store module path for reference
        self._module_path = module_path

        # Ensure results directory exists
        self.results_path.mkdir(parents=True, exist_ok=True)

        try:
            yield self
        finally:
            await self.cleanup()

    async def run_scenario(self, module_path: str) -> TestScenarioReport:
        """Run complete test scenario for a module.

        Args:
            module_path: Path to the module to test

        Returns:
            TestScenarioReport with comprehensive results
        """
        async with self.scenario_context(module_path):
            start_time = time.time()
            self.phase_results = []

            try:
                if self.config.parallel_execution:
                    await self._run_phases_parallel()
                else:
                    await self._run_phases_sequential()

            except Exception as e:
                # Handle critical scenario errors
                error_result = PhaseResult(
                    phase=TestPhase.VALIDATION,  # Default phase for errors
                    status=TestResult.ERROR,
                    duration=0.0,
                    report=None,
                    issues=[format_scenario_error(e)],
                )
                self.phase_results.append(error_result)

            end_time = time.time()
            total_duration = end_time - start_time

            # Generate comprehensive report
            self.report = self._generate_scenario_report(module_path, total_duration)
            return self.report

    async def _run_phases_sequential(self) -> None:
        """Run test phases sequentially."""
        for phase in self.config.enabled_phases:
            try:
                result = await self._run_single_phase(phase)
                self.phase_results.append(result)

                # Stop on first failure if fail_fast is enabled
                if self.config.fail_fast and result.status == TestResult.FAILED:
                    break

            except Exception as e:
                error_result = PhaseResult(
                    phase=phase,
                    status=TestResult.ERROR,
                    duration=0.0,
                    report=None,
                    issues=[format_scenario_error(e)],
                )
                self.phase_results.append(error_result)

                if self.config.fail_fast:
                    break

    async def _run_phases_parallel(self) -> None:
        """Run test phases in parallel where possible."""
        # Group phases by dependency requirements
        independent_phases = [TestPhase.VALIDATION, TestPhase.QUALITY_ASSURANCE]
        dependent_phases = [
            TestPhase.COMPATIBILITY,
            TestPhase.PERFORMANCE,
            TestPhase.USER_ACCEPTANCE,
        ]

        # Run independent phases first in parallel
        if any(phase in self.config.enabled_phases for phase in independent_phases):
            tasks = []
            for phase in independent_phases:
                if phase in self.config.enabled_phases:
                    task = asyncio.create_task(self._run_single_phase(phase))
                    tasks.append((phase, task))

            # Wait for independent phases
            for phase, task in tasks:
                try:
                    result = await task
                    self.phase_results.append(result)
                except Exception as e:
                    error_result = PhaseResult(
                        phase=phase,
                        status=TestResult.ERROR,
                        duration=0.0,
                        report=None,
                        issues=[format_scenario_error(e)],
                    )
                    self.phase_results.append(error_result)

        # Check if we should continue (fail_fast check)
        if self.config.fail_fast and any(r.status == TestResult.FAILED for r in self.phase_results):
            return

        # Run dependent phases sequentially (they may depend on validation results)
        for phase in dependent_phases:
            if phase in self.config.enabled_phases:
                try:
                    result = await self._run_single_phase(phase)
                    self.phase_results.append(result)

                    if self.config.fail_fast and result.status == TestResult.FAILED:
                        break

                except Exception as e:
                    error_result = PhaseResult(
                        phase=phase,
                        status=TestResult.ERROR,
                        duration=0.0,
                        report=None,
                        issues=[format_scenario_error(e)],
                    )
                    self.phase_results.append(error_result)

                    if self.config.fail_fast:
                        break

    async def _run_single_phase(self, phase: TestPhase) -> PhaseResult:
        """Run a single test phase.

        Args:
            phase: TestPhase to run

        Returns:
            PhaseResult with execution results
        """
        start_time = time.time()
        module_path = getattr(self, "_module_path", "")

        try:
            if phase == TestPhase.VALIDATION:
                # validate_module handles its own context
                report = await self.module_validator.validate_module(module_path)
                status = TestResult.PASSED if report.success else TestResult.FAILED

                return PhaseResult(
                    phase=phase,
                    status=status,
                    duration=time.time() - start_time,
                    report=report,
                    issues=report.errors,  # ValidationResult has errors, not issues
                    warnings=report.warnings,
                )

            elif phase == TestPhase.QUALITY_ASSURANCE:
                async with self.qa_pipeline.qa_context(module_path) as qa:
                    report = await qa.run_checks()
                    status = TestResult.PASSED if report.overall_status == "passed" else TestResult.FAILED

                    return PhaseResult(
                        phase=phase,
                        status=status,
                        duration=time.time() - start_time,
                        report=report,
                        issues=[],  # QA report structure may differ
                        warnings=[],
                    )

            elif phase == TestPhase.COMPATIBILITY:
                async with self.compatibility_tester.compatibility_context(module_path) as tester:
                    report = await tester.run_all_tests()
                    status = TestResult.PASSED if report.overall_status == "compatible" else TestResult.FAILED

                    return PhaseResult(
                        phase=phase,
                        status=status,
                        duration=time.time() - start_time,
                        report=report,
                        issues=[],  # Compatibility issues are in test results
                        warnings=[],
                    )

            elif phase == TestPhase.PERFORMANCE:
                async with self.performance_tester.performance_context(module_path) as tester:
                    report = await tester.run_all_tests()
                    status = TestResult.PASSED if report.overall_status == "completed" else TestResult.FAILED

                    return PhaseResult(
                        phase=phase,
                        status=status,
                        duration=time.time() - start_time,
                        report=report,
                        issues=[],  # Performance issues are in test results
                        warnings=[],
                    )

            elif phase == TestPhase.USER_ACCEPTANCE:
                async with self.uat_manager.uat_context(module_path) as uat:
                    report = await uat.run_all_scenarios()
                    status = TestResult.PASSED if report.overall_status == "passed" else TestResult.FAILED

                    return PhaseResult(
                        phase=phase,
                        status=status,
                        duration=time.time() - start_time,
                        report=report,
                        issues=[],  # UAT issues are in test results
                        warnings=[],
                    )

            else:
                raise ValueError(f"Unknown test phase: {phase}")

        except Exception as e:
            return PhaseResult(
                phase=phase,
                status=TestResult.ERROR,
                duration=time.time() - start_time,
                report=None,
                issues=[format_scenario_error(e)],
            )

    def _generate_scenario_report(self, module_path: str, total_duration: float) -> TestScenarioReport:
        """Generate comprehensive test scenario report.

        Args:
            module_path: Path to the tested module
            total_duration: Total scenario execution time

        Returns:
            TestScenarioReport with all results
        """
        # Determine overall status
        overall_status = self._determine_overall_status()

        # Generate summary statistics
        summary = self._generate_summary()

        # Generate recommendations
        recommendations = self._generate_recommendations()

        return TestScenarioReport(
            module_path=module_path,
            scenario_config=self.config,
            overall_status=overall_status,
            total_duration=total_duration,
            phase_results=self.phase_results.copy(),
            summary=summary,
            recommendations=recommendations,
            metadata={
                "suite_type": self.config.suite_type.value,
                "enabled_phases": [p.value for p in self.config.enabled_phases],
                "parallel_execution": self.config.parallel_execution,
                "environment_type": self.config.environment_type,
                "total_phases": len(self.config.enabled_phases),
                "executed_phases": len(self.phase_results),
            },
            generated_at=time.time(),
        )

    def _determine_overall_status(self) -> TestResult:
        """Determine overall scenario status from phase results."""
        if not self.phase_results:
            return TestResult.ERROR

        # Check for errors first
        if any(r.status == TestResult.ERROR for r in self.phase_results):
            return TestResult.ERROR

        # Check for failures
        if any(r.status == TestResult.FAILED for r in self.phase_results):
            return TestResult.FAILED

        # Check for warnings
        if any(r.status == TestResult.WARNING for r in self.phase_results):
            return TestResult.WARNING

        # Check if all expected phases completed
        if len(self.phase_results) < len(self.config.enabled_phases):
            return TestResult.WARNING

        # All phases passed
        return TestResult.PASSED

    def _generate_summary(self) -> dict[str, Any]:
        """Generate summary statistics from phase results."""
        phase_status_counts: dict[str, int] = {}
        total_issues = 0
        total_warnings = 0

        for result in self.phase_results:
            status = result.status.value
            phase_status_counts[status] = phase_status_counts.get(status, 0) + 1
            total_issues += len(result.issues)
            total_warnings += len(result.warnings)

        return {
            "total_phases": len(self.config.enabled_phases),
            "executed_phases": len(self.phase_results),
            "phase_status_counts": phase_status_counts,
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "success_rate": (phase_status_counts.get("passed", 0) / max(1, len(self.phase_results)) * 100),
            "phase_durations": {result.phase.value: result.duration for result in self.phase_results},
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on scenario results."""
        recommendations = []

        failed_phases = [r for r in self.phase_results if r.status == TestResult.FAILED]
        error_phases = [r for r in self.phase_results if r.status == TestResult.ERROR]

        if error_phases:
            recommendations.append("Resolve critical errors preventing test execution")
            error_phase_names = [r.phase.value for r in error_phases]
            recommendations.append(f"Failed phases: {', '.join(error_phase_names)}")

        if failed_phases:
            recommendations.append("Address failing test phases before deployment")
            failed_phase_names = [r.phase.value for r in failed_phases]
            recommendations.append(f"Fix issues in: {', '.join(failed_phase_names)}")

        # Phase-specific recommendations
        validation_result = next((r for r in self.phase_results if r.phase == TestPhase.VALIDATION), None)
        if validation_result and validation_result.status == TestResult.FAILED:
            recommendations.append("Fix module validation issues - these are critical for deployment")

        performance_result = next((r for r in self.phase_results if r.phase == TestPhase.PERFORMANCE), None)
        if performance_result and performance_result.status == TestResult.FAILED:
            recommendations.append("Address performance issues to ensure module scalability")

        compatibility_result = next((r for r in self.phase_results if r.phase == TestPhase.COMPATIBILITY), None)
        if compatibility_result and compatibility_result.status == TestResult.FAILED:
            recommendations.append("Fix compatibility issues for broader deployment support")

        # Suite-specific recommendations
        if self.config.suite_type == TestSuite.QUICK and not failed_phases and not error_phases:
            recommendations.append("Consider running standard test suite for more comprehensive validation")

        if not recommendations:
            recommendations.append("All test phases passed - module ready for deployment")

        return recommendations

    async def cleanup(self) -> None:
        """Clean up test scenario resources."""
        # Context managers handle cleanup automatically
        # No explicit cleanup needed for components using async context managers
        pass

    def export_report(self, output_path: str | None = None) -> dict[str, Any]:
        """Export test scenario report to file or return as dict.

        Args:
            output_path: Optional path to save report

        Returns:
            Report data as dictionary
        """
        if not self.report:
            raise RuntimeError("No report available - run scenario first")

        report_data = {
            "module_path": self.report.module_path,
            "timestamp": self.report.generated_at,
            "scenario_config": {
                "suite_type": self.report.scenario_config.suite_type.value,
                "enabled_phases": [p.value for p in self.report.scenario_config.enabled_phases],
                "parallel_execution": self.report.scenario_config.parallel_execution,
                "fail_fast": self.report.scenario_config.fail_fast,
                "timeout": self.report.scenario_config.timeout,
                "environment_type": self.report.scenario_config.environment_type,
            },
            "summary": {
                "overall_status": self.report.overall_status.value,
                "total_duration": self.report.total_duration,
                **self.report.summary,
            },
            "phase_results": [
                {
                    "phase": result.phase.value,
                    "status": result.status.value,
                    "duration": result.duration,
                    "issues_count": len(result.issues),
                    "warnings_count": len(result.warnings),
                    "has_report": result.report is not None,
                }
                for result in self.report.phase_results
            ],
            "recommendations": self.report.recommendations,
            "metadata": self.report.metadata,
        }

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(report_data, f, indent=2)

        return report_data

    def get_phase_report(self, phase: TestPhase) -> Any:
        """Get detailed report for a specific phase.

        Args:
            phase: TestPhase to get report for

        Returns:
            Phase-specific report object or None
        """
        phase_result = next((r for r in self.phase_results if r.phase == phase), None)
        return phase_result.report if phase_result else None
