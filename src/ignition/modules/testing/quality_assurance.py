"""Quality Assurance Pipeline for Ignition Module Testing.

Provides comprehensive code quality checks, security scanning, and
quality assurance pipeline management following patterns from crawl_mcp.py
for validation, error handling, and resource management.
"""

import asyncio
import json
import os
import subprocess
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


class QualityCheckStatus(Enum):
    """Status of quality check."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class QualityCheckType(Enum):
    """Type of quality check."""

    CODE_STYLE = "code_style"
    TYPE_CHECKING = "type_checking"
    SECURITY_SCAN = "security_scan"
    COMPLEXITY_ANALYSIS = "complexity_analysis"
    DOCUMENTATION = "documentation"
    LICENSING = "licensing"
    DEPENDENCY_AUDIT = "dependency_audit"
    PERFORMANCE = "performance"


@dataclass
class QualityCheck:
    """Quality check configuration and results."""

    name: str
    check_type: QualityCheckType
    command: str
    working_dir: str | None = None
    timeout: int = 300
    required: bool = True
    status: QualityCheckStatus = QualityCheckStatus.PENDING
    output: str = ""
    error_output: str = ""
    exit_code: int | None = None
    duration: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    """Quality assurance report."""

    module_path: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    skipped_checks: int
    error_checks: int
    overall_status: str
    duration: float
    checks: list[QualityCheck] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def validate_qa_environment() -> dict[str, Any]:
    """Validate QA environment configuration.

    Following patterns from crawl_mcp.py for environment validation.

    Returns:
        Dictionary with validation results
    """
    required_tools = {
        "ruff": "Python linting and formatting",
        "mypy": "Static type checking",
        "bandit": "Security vulnerability scanning",
    }

    optional_tools = {
        "black": "Code formatting",
        "isort": "Import sorting",
        "pytest": "Testing framework",
        "coverage": "Code coverage analysis",
        "safety": "Dependency vulnerability scanning",
    }

    missing_required = []
    available_tools = {}

    for tool, description in required_tools.items():
        if _check_tool_available(tool):
            available_tools[tool] = description
        else:
            missing_required.append(f"{tool} ({description})")

    for tool, description in optional_tools.items():
        if _check_tool_available(tool):
            available_tools[tool] = description

    if missing_required:
        return {
            "valid": False,
            "error": f"Missing required tools: {', '.join(missing_required)}",
            "available": available_tools,
        }

    return {"valid": True, "tools": available_tools}


def _check_tool_available(tool: str) -> bool:
    """Check if a tool is available in the system.

    Args:
        tool: Name of the tool

    Returns:
        True if tool is available
    """
    try:
        result = subprocess.run(
            [tool, "--version"], capture_output=True, timeout=10, check=False
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def format_qa_error(error: Exception) -> str:
    """Format QA errors for user-friendly messages.

    Following patterns from crawl_mcp.py for error formatting.

    Args:
        error: The exception to format

    Returns:
        Formatted error message
    """
    error_str = str(error).lower()

    if "timeout" in error_str:
        return (
            "Quality check timed out. Consider increasing timeout or optimizing checks."
        )
    elif "permission" in error_str or "access" in error_str:
        return "Permission denied. Check file permissions and user access rights."
    elif "not found" in error_str or "command not found" in error_str:
        return "Required tool not found. Install missing quality assurance tools."
    elif "syntax error" in error_str or "parse error" in error_str:
        return "Code syntax error detected. Fix syntax issues before running QA checks."
    else:
        return f"Quality assurance error: {error!s}"


class QualityAssurancePipeline:
    """Quality assurance pipeline for Ignition modules.

    Following patterns from crawl_mcp.py for robust validation,
    error handling, and resource management.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the QA pipeline.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.temp_dir: Path | None = None
        self.checks: list[QualityCheck] = []
        self.report: QualityReport | None = None

        # Load configuration from environment
        self.timeout = int(os.getenv("QA_TIMEOUT", "600"))
        self.parallel_checks = int(os.getenv("QA_PARALLEL_CHECKS", "4"))
        self.fail_fast = os.getenv("QA_FAIL_FAST", "false").lower() == "true"

    @asynccontextmanager
    async def qa_context(
        self, module_path: str
    ) -> AsyncIterator["QualityAssurancePipeline"]:
        """Create QA context with resource management.

        Following patterns from crawl_mcp.py for context management.

        Args:
            module_path: Path to the module

        Yields:
            QualityAssurancePipeline instance
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)

            try:
                await self.initialize_checks(module_path)
                yield self
            finally:
                self.temp_dir = None

    async def initialize_checks(self, module_path: str) -> None:
        """Initialize quality checks for the module.

        Args:
            module_path: Path to the module
        """
        module_file = Path(module_path)
        working_dir = str(module_file.parent)

        # Define standard quality checks
        self.checks = [
            QualityCheck(
                name="Code Style Check",
                check_type=QualityCheckType.CODE_STYLE,
                command=f"ruff check {module_path}",
                working_dir=working_dir,
                timeout=120,
                required=True,
            ),
            QualityCheck(
                name="Type Checking",
                check_type=QualityCheckType.TYPE_CHECKING,
                command=f"mypy {module_path}",
                working_dir=working_dir,
                timeout=180,
                required=True,
            ),
            QualityCheck(
                name="Security Scan",
                check_type=QualityCheckType.SECURITY_SCAN,
                command=f"bandit -r {module_path}",
                working_dir=working_dir,
                timeout=120,
                required=True,
            ),
            QualityCheck(
                name="Complexity Analysis",
                check_type=QualityCheckType.COMPLEXITY_ANALYSIS,
                command=f"radon cc {module_path} --min B",
                working_dir=working_dir,
                timeout=60,
                required=False,
            ),
            QualityCheck(
                name="Documentation Check",
                check_type=QualityCheckType.DOCUMENTATION,
                command=f"pydocstyle {module_path}",
                working_dir=working_dir,
                timeout=60,
                required=False,
            ),
            QualityCheck(
                name="Dependency Audit",
                check_type=QualityCheckType.DEPENDENCY_AUDIT,
                command="safety check",
                working_dir=working_dir,
                timeout=120,
                required=False,
            ),
        ]

        # Filter checks based on available tools
        available_checks = []
        for check in self.checks:
            tool_name = check.command.split()[0]
            if _check_tool_available(tool_name):
                available_checks.append(check)
            else:
                check.status = QualityCheckStatus.SKIPPED
                check.output = f"Tool '{tool_name}' not available"

        self.checks = available_checks

    async def run_checks(self) -> QualityReport:
        """Run all quality checks.

        Returns:
            QualityReport with results
        """
        if not self.checks:
            raise RuntimeError("No quality checks initialized")

        start_time = asyncio.get_event_loop().time()

        # Run checks in parallel with semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.parallel_checks)
        tasks = [
            asyncio.create_task(self._run_single_check(check, semaphore))
            for check in self.checks
        ]

        try:
            await asyncio.gather(*tasks, return_exceptions=not self.fail_fast)
        except Exception as e:
            if self.fail_fast:
                # Cancel running tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                raise RuntimeError(format_qa_error(e)) from e

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        # Generate report
        self.report = self._generate_report(duration)
        return self.report

    async def _run_single_check(
        self, check: QualityCheck, semaphore: asyncio.Semaphore
    ) -> None:
        """Run a single quality check.

        Args:
            check: QualityCheck to run
            semaphore: Semaphore for concurrency control
        """
        async with semaphore:
            if check.status == QualityCheckStatus.SKIPPED:
                return

            check.status = QualityCheckStatus.RUNNING
            start_time = asyncio.get_event_loop().time()

            try:
                # Run the check command
                process = await asyncio.create_subprocess_shell(
                    check.command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=check.working_dir,
                )

                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=check.timeout
                )

                check.exit_code = process.returncode
                check.output = stdout.decode("utf-8") if stdout else ""
                check.error_output = stderr.decode("utf-8") if stderr else ""

                # Determine status based on exit code
                if check.exit_code == 0:
                    check.status = QualityCheckStatus.PASSED
                else:
                    check.status = QualityCheckStatus.FAILED

            except TimeoutError:
                check.status = QualityCheckStatus.ERROR
                check.error_output = f"Check timed out after {check.timeout} seconds"
                if process:
                    process.kill()
                    await process.wait()

            except Exception as e:
                check.status = QualityCheckStatus.ERROR
                check.error_output = format_qa_error(e)

            finally:
                end_time = asyncio.get_event_loop().time()
                check.duration = end_time - start_time

    def _generate_report(self, total_duration: float) -> QualityReport:
        """Generate quality assurance report.

        Args:
            total_duration: Total time taken for all checks

        Returns:
            QualityReport with results
        """
        passed_checks = sum(
            1 for check in self.checks if check.status == QualityCheckStatus.PASSED
        )
        failed_checks = sum(
            1 for check in self.checks if check.status == QualityCheckStatus.FAILED
        )
        skipped_checks = sum(
            1 for check in self.checks if check.status == QualityCheckStatus.SKIPPED
        )
        error_checks = sum(
            1 for check in self.checks if check.status == QualityCheckStatus.ERROR
        )

        # Determine overall status
        if error_checks > 0:
            overall_status = "error"
        elif failed_checks > 0:
            required_failures = sum(
                1
                for check in self.checks
                if check.status == QualityCheckStatus.FAILED and check.required
            )
            overall_status = "failed" if required_failures > 0 else "warning"
        else:
            overall_status = "passed"

        return QualityReport(
            module_path="",  # Will be set by caller
            total_checks=len(self.checks),
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            skipped_checks=skipped_checks,
            error_checks=error_checks,
            overall_status=overall_status,
            duration=total_duration,
            checks=self.checks.copy(),
            recommendations=self._generate_recommendations(),
            metadata={
                "parallel_checks": self.parallel_checks,
                "fail_fast": self.fail_fast,
                "timeout": self.timeout,
            },
        )

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on check results.

        Returns:
            list of recommendations
        """
        recommendations = []

        failed_checks = [
            check for check in self.checks if check.status == QualityCheckStatus.FAILED
        ]
        error_checks = [
            check for check in self.checks if check.status == QualityCheckStatus.ERROR
        ]

        if failed_checks:
            recommendations.append(
                "Fix code quality issues identified by failed checks"
            )

            # Specific recommendations based on check types
            for check in failed_checks:
                if check.check_type == QualityCheckType.CODE_STYLE:
                    recommendations.append(
                        "Run 'ruff check --fix' to automatically fix style issues"
                    )
                elif check.check_type == QualityCheckType.TYPE_CHECKING:
                    recommendations.append(
                        "Add type annotations and fix type-related issues"
                    )
                elif check.check_type == QualityCheckType.SECURITY_SCAN:
                    recommendations.append("Review and fix security vulnerabilities")

        if error_checks:
            recommendations.append("Investigate and resolve errors in quality checks")
            missing_tools = [
                check.name
                for check in error_checks
                if "not found" in check.error_output.lower()
            ]
            if missing_tools:
                recommendations.append(
                    f"Install missing tools: {', '.join(missing_tools)}"
                )

        skipped_checks = [
            check for check in self.checks if check.status == QualityCheckStatus.SKIPPED
        ]
        if skipped_checks:
            tools = [check.command.split()[0] for check in skipped_checks]
            recommendations.append(
                f"Install optional tools for comprehensive checks: {', '.join(set(tools))}"
            )

        if not recommendations:
            recommendations.append(
                "All quality checks passed - module meets quality standards"
            )

        return recommendations

    def export_report(self, output_path: str | None = None) -> dict[str, Any]:
        """Export quality report to file or return as dict.

        Args:
            output_path: Optional path to save report

        Returns:
            Report data as dictionary
        """
        if not self.report:
            raise RuntimeError("No report available - run checks first")

        report_data = {
            "module_path": self.report.module_path,
            "timestamp": asyncio.get_event_loop().time(),
            "summary": {
                "overall_status": self.report.overall_status,
                "total_checks": self.report.total_checks,
                "passed_checks": self.report.passed_checks,
                "failed_checks": self.report.failed_checks,
                "skipped_checks": self.report.skipped_checks,
                "error_checks": self.report.error_checks,
                "duration": self.report.duration,
            },
            "checks": [
                {
                    "name": check.name,
                    "type": check.check_type.value,
                    "status": check.status.value,
                    "command": check.command,
                    "duration": check.duration,
                    "exit_code": check.exit_code,
                    "output": check.output,
                    "error_output": check.error_output,
                    "required": check.required,
                }
                for check in self.report.checks
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
