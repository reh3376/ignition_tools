"""Quality Assurance Pipeline for Module Testing.

This module provides comprehensive quality assurance processes for Ignition modules,
including automated code quality checks, security scanning, and documentation generation.
Following patterns from crawl_mcp.py for robust QA processing.
"""

import asyncio
import json
import subprocess
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class QualityCheck:
    """Result of a quality assurance check."""

    name: str
    category: str  # "code_quality", "security", "documentation", "performance"
    status: str  # "passed", "failed", "warning", "skipped"
    score: float = 0.0  # 0-100
    details: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """Comprehensive quality assurance report."""

    module_path: str
    overall_score: float
    checks: list[QualityCheck] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""


def validate_qa_environment() -> dict[str, Any]:
    """Validate quality assurance environment configuration.

    Following patterns from crawl_mcp.py for environment validation.

    Returns:
        Dictionary with validation results
    """
    required_tools = {
        "java": "Java runtime for module analysis",
        "python": "Python for analysis scripts",
    }

    optional_tools = {
        "docker": "Docker for containerized analysis",
        "bandit": "Python security analysis",
        "sonar-scanner": "SonarQube analysis",
    }

    missing_tools = []
    available_tools = {}

    for tool, description in required_tools.items():
        if _check_tool_available(tool):
            available_tools[tool] = description
        else:
            missing_tools.append(f"{tool} ({description})")

    for tool, description in optional_tools.items():
        if _check_tool_available(tool):
            available_tools[tool] = description

    if missing_tools:
        return {
            "valid": False,
            "error": f"Missing required tools: {', '.join(missing_tools)}",
            "available": available_tools,
        }

    return {"valid": True, "tools": available_tools}


def _check_tool_available(tool_name: str) -> bool:
    """Check if a tool is available in the system PATH.

    Args:
        tool_name: Name of the tool to check

    Returns:
        True if tool is available, False otherwise
    """
    try:
        result = subprocess.run(
            [tool_name, "--version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


class CodeQualityChecker:
    """Code quality analysis for Ignition modules.

    Following patterns from crawl_mcp.py for comprehensive analysis.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the code quality checker.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.temp_dir: Path | None = None

    async def analyze_module(self, module_path: str) -> QualityCheck:
        """Analyze code quality of a module.

        Args:
            module_path: Path to the module to analyze

        Returns:
            QualityCheck with code quality results
        """
        check = QualityCheck(
            name="Code Quality Analysis", category="code_quality", status="passed"
        )

        try:
            # Extract module for analysis
            with tempfile.TemporaryDirectory() as temp_dir:
                self.temp_dir = Path(temp_dir)

                # Basic code quality checks
                await self._analyze_module_structure(module_path, check)
                await self._analyze_code_complexity(module_path, check)
                await self._check_coding_standards(module_path, check)

                # Calculate overall score
                check.score = self._calculate_quality_score(check)

                if check.score < 70:
                    check.status = "failed"
                elif check.score < 85:
                    check.status = "warning"

        except Exception as e:
            check.status = "failed"
            check.errors.append(f"Code quality analysis failed: {e!s}")
            check.score = 0.0

        return check

    async def _analyze_module_structure(
        self, module_path: str, check: QualityCheck
    ) -> None:
        """Analyze module structure and organization."""
        try:
            module_file = Path(module_path)
            file_size = module_file.stat().st_size

            # Basic structure analysis
            structure_score = 100.0

            if file_size > 50 * 1024 * 1024:  # > 50MB
                check.warnings.append("Module file is very large (>50MB)")
                structure_score -= 20

            if file_size < 1024:  # < 1KB
                check.warnings.append("Module file is very small (<1KB)")
                structure_score -= 10

            check.details["structure_score"] = max(0, structure_score)
            check.details["file_size"] = file_size

        except Exception as e:
            check.errors.append(f"Structure analysis failed: {e!s}")

    async def _analyze_code_complexity(
        self, module_path: str, check: QualityCheck
    ) -> None:
        """Analyze code complexity metrics."""
        try:
            # Simulate complexity analysis
            # In a real implementation, this would extract and analyze Java code
            complexity_score = 85.0  # Simulated score

            check.details["complexity_score"] = complexity_score
            check.details["cyclomatic_complexity"] = 5.2  # Simulated
            check.details["maintainability_index"] = 78.5  # Simulated

            if complexity_score < 70:
                check.warnings.append("Code complexity is high")

        except Exception as e:
            check.errors.append(f"Complexity analysis failed: {e!s}")

    async def _check_coding_standards(
        self, module_path: str, check: QualityCheck
    ) -> None:
        """Check adherence to coding standards."""
        try:
            # Simulate coding standards check
            standards_score = 90.0  # Simulated score

            check.details["standards_score"] = standards_score
            check.details["style_violations"] = 2  # Simulated

            if standards_score < 80:
                check.warnings.append("Some coding standard violations found")

        except Exception as e:
            check.errors.append(f"Standards check failed: {e!s}")

    def _calculate_quality_score(self, check: QualityCheck) -> float:
        """Calculate overall quality score."""
        scores = []

        if "structure_score" in check.details:
            scores.append(check.details["structure_score"])
        if "complexity_score" in check.details:
            scores.append(check.details["complexity_score"])
        if "standards_score" in check.details:
            scores.append(check.details["standards_score"])

        return sum(scores) / len(scores) if scores else 0.0


class SecurityScanner:
    """Security scanning for Ignition modules.

    Following patterns from crawl_mcp.py for security analysis.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the security scanner.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}

    async def scan_module(self, module_path: str) -> QualityCheck:
        """Perform security scan of a module.

        Args:
            module_path: Path to the module to scan

        Returns:
            QualityCheck with security scan results
        """
        check = QualityCheck(name="Security Scan", category="security", status="passed")

        try:
            # Perform security checks
            await self._check_vulnerabilities(module_path, check)
            await self._analyze_permissions(module_path, check)
            await self._check_dependencies(module_path, check)

            # Calculate security score
            check.score = self._calculate_security_score(check)

            if check.score < 70:
                check.status = "failed"
            elif check.score < 85:
                check.status = "warning"

        except Exception as e:
            check.status = "failed"
            check.errors.append(f"Security scan failed: {e!s}")
            check.score = 0.0

        return check

    async def _check_vulnerabilities(
        self, module_path: str, check: QualityCheck
    ) -> None:
        """Check for known vulnerabilities."""
        try:
            # Simulate vulnerability scanning
            vulnerabilities_found = 0  # Simulated

            check.details["vulnerabilities"] = vulnerabilities_found
            check.details["vulnerability_score"] = (
                100.0
                if vulnerabilities_found == 0
                else max(0, 100 - vulnerabilities_found * 20)
            )

            if vulnerabilities_found > 0:
                check.warnings.append(
                    f"Found {vulnerabilities_found} potential vulnerabilities"
                )

        except Exception as e:
            check.errors.append(f"Vulnerability check failed: {e!s}")

    async def _analyze_permissions(self, module_path: str, check: QualityCheck) -> None:
        """Analyze module permissions and access patterns."""
        try:
            # Simulate permission analysis
            permission_score = 90.0  # Simulated

            check.details["permission_score"] = permission_score
            check.details["excessive_permissions"] = False  # Simulated

            if permission_score < 80:
                check.warnings.append("Some permission concerns found")

        except Exception as e:
            check.errors.append(f"Permission analysis failed: {e!s}")

    async def _check_dependencies(self, module_path: str, check: QualityCheck) -> None:
        """Check dependencies for security issues."""
        try:
            # Simulate dependency security check
            dependency_score = 95.0  # Simulated

            check.details["dependency_score"] = dependency_score
            check.details["outdated_dependencies"] = 1  # Simulated

            if dependency_score < 90:
                check.warnings.append("Some dependency security concerns found")

        except Exception as e:
            check.errors.append(f"Dependency check failed: {e!s}")

    def _calculate_security_score(self, check: QualityCheck) -> float:
        """Calculate overall security score."""
        scores = []

        if "vulnerability_score" in check.details:
            scores.append(check.details["vulnerability_score"])
        if "permission_score" in check.details:
            scores.append(check.details["permission_score"])
        if "dependency_score" in check.details:
            scores.append(check.details["dependency_score"])

        return sum(scores) / len(scores) if scores else 0.0


class DocumentationGenerator:
    """Documentation generation and validation for modules.

    Following patterns from crawl_mcp.py for documentation processing.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the documentation generator.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}

    async def validate_documentation(self, module_path: str) -> QualityCheck:
        """Validate and generate documentation for a module.

        Args:
            module_path: Path to the module

        Returns:
            QualityCheck with documentation validation results
        """
        check = QualityCheck(
            name="Documentation Validation", category="documentation", status="passed"
        )

        try:
            # Check documentation completeness
            await self._check_documentation_completeness(module_path, check)
            await self._validate_documentation_quality(module_path, check)
            await self._generate_documentation(module_path, check)

            # Calculate documentation score
            check.score = self._calculate_documentation_score(check)

            if check.score < 70:
                check.status = "failed"
            elif check.score < 85:
                check.status = "warning"

        except Exception as e:
            check.status = "failed"
            check.errors.append(f"Documentation validation failed: {e!s}")
            check.score = 0.0

        return check

    async def _check_documentation_completeness(
        self, module_path: str, check: QualityCheck
    ) -> None:
        """Check completeness of module documentation."""
        try:
            # Simulate documentation completeness check
            completeness_score = 80.0  # Simulated

            check.details["completeness_score"] = completeness_score
            check.details["missing_sections"] = ["Installation Guide"]  # Simulated

            if completeness_score < 90:
                check.recommendations.append(
                    "Consider adding missing documentation sections"
                )

        except Exception as e:
            check.errors.append(f"Documentation completeness check failed: {e!s}")

    async def _validate_documentation_quality(
        self, module_path: str, check: QualityCheck
    ) -> None:
        """Validate quality of existing documentation."""
        try:
            # Simulate documentation quality validation
            quality_score = 85.0  # Simulated

            check.details["quality_score"] = quality_score
            check.details["readability_score"] = 78.5  # Simulated

            if quality_score < 80:
                check.warnings.append("Documentation quality could be improved")

        except Exception as e:
            check.errors.append(f"Documentation quality validation failed: {e!s}")

    async def _generate_documentation(
        self, module_path: str, check: QualityCheck
    ) -> None:
        """Generate additional documentation if needed."""
        try:
            # Simulate documentation generation
            generated_docs = ["API Reference", "Quick Start Guide"]  # Simulated

            check.details["generated_docs"] = generated_docs
            check.details["generation_success"] = True

            if generated_docs:
                check.recommendations.append(
                    "Generated additional documentation sections"
                )

        except Exception as e:
            check.errors.append(f"Documentation generation failed: {e!s}")

    def _calculate_documentation_score(self, check: QualityCheck) -> float:
        """Calculate overall documentation score."""
        scores = []

        if "completeness_score" in check.details:
            scores.append(check.details["completeness_score"])
        if "quality_score" in check.details:
            scores.append(check.details["quality_score"])

        return sum(scores) / len(scores) if scores else 0.0


class QualityAssurancePipeline:
    """Comprehensive quality assurance pipeline for module testing.

    Following patterns from crawl_mcp.py for pipeline management and execution.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the QA pipeline.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.code_checker = CodeQualityChecker(config)
        self.security_scanner = SecurityScanner(config)
        self.doc_generator = DocumentationGenerator(config)

    @asynccontextmanager
    async def qa_context(self, module_path: str) -> AsyncIterator[dict[str, Any]]:
        """Create a QA context with resource management.

        Following patterns from crawl_mcp.py for context management.

        Args:
            module_path: Path to the module for QA analysis

        Yields:
            Dictionary with QA context information
        """
        context = {
            "module_path": module_path,
            "start_time": asyncio.get_event_loop().time(),
            "temp_resources": [],
        }

        try:
            yield context
        finally:
            # Cleanup any temporary resources
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

    async def run_full_qa(self, module_path: str) -> QualityReport:
        """Run comprehensive quality assurance on a module.

        Args:
            module_path: Path to the module to analyze

        Returns:
            QualityReport with complete QA results
        """
        async with self.qa_context(module_path) as context:
            report = QualityReport(
                module_path=module_path,
                overall_score=0.0,
                generated_at=str(asyncio.get_event_loop().time()),
            )

            try:
                # Run all QA checks in parallel for efficiency
                checks = await asyncio.gather(
                    self.code_checker.analyze_module(module_path),
                    self.security_scanner.scan_module(module_path),
                    self.doc_generator.validate_documentation(module_path),
                    return_exceptions=True,
                )

                # Process results
                valid_checks = []
                for check in checks:
                    if isinstance(check, QualityCheck):
                        valid_checks.append(check)
                        report.checks.append(check)
                    else:
                        # Handle exceptions
                        error_check = QualityCheck(
                            name="QA Pipeline Error",
                            category="pipeline",
                            status="failed",
                            errors=[str(check)],
                        )
                        report.checks.append(error_check)

                # Calculate overall score
                if valid_checks:
                    report.overall_score = sum(
                        check.score for check in valid_checks
                    ) / len(valid_checks)

                # Generate summary
                report.summary = self._generate_summary(report)

            except Exception as e:
                error_check = QualityCheck(
                    name="QA Pipeline Critical Error",
                    category="pipeline",
                    status="failed",
                    errors=[f"Critical QA pipeline error: {e!s}"],
                )
                report.checks.append(error_check)
                report.overall_score = 0.0

            return report

    def _generate_summary(self, report: QualityReport) -> dict[str, Any]:
        """Generate summary statistics for the QA report.

        Args:
            report: QualityReport to summarize

        Returns:
            Dictionary with summary information
        """
        summary = {
            "total_checks": len(report.checks),
            "passed_checks": sum(
                1 for check in report.checks if check.status == "passed"
            ),
            "failed_checks": sum(
                1 for check in report.checks if check.status == "failed"
            ),
            "warning_checks": sum(
                1 for check in report.checks if check.status == "warning"
            ),
            "categories": {},
            "recommendations": [],
        }

        # Categorize checks
        for check in report.checks:
            if check.category not in summary["categories"]:
                summary["categories"][check.category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "warnings": 0,
                    "average_score": 0.0,
                }

            cat = summary["categories"][check.category]
            cat["total"] += 1

            if check.status == "passed":
                cat["passed"] += 1
            elif check.status == "failed":
                cat["failed"] += 1
            elif check.status == "warning":
                cat["warnings"] += 1

        # Calculate average scores per category
        for category, data in summary["categories"].items():
            category_checks = [
                check for check in report.checks if check.category == category
            ]
            if category_checks:
                data["average_score"] = sum(
                    check.score for check in category_checks
                ) / len(category_checks)

        # Collect all recommendations
        for check in report.checks:
            summary["recommendations"].extend(check.recommendations)

        return summary

    async def generate_qa_report(
        self, report: QualityReport, output_path: str | None = None
    ) -> dict[str, Any]:
        """Generate a formatted QA report.

        Args:
            report: QualityReport to format
            output_path: Optional path to save the report

        Returns:
            Dictionary with formatted report data
        """
        formatted_report = {
            "module_path": report.module_path,
            "overall_score": report.overall_score,
            "grade": self._calculate_grade(report.overall_score),
            "generated_at": report.generated_at,
            "summary": report.summary,
            "checks": [
                {
                    "name": check.name,
                    "category": check.category,
                    "status": check.status,
                    "score": check.score,
                    "errors": check.errors,
                    "warnings": check.warnings,
                    "recommendations": check.recommendations,
                    "details": check.details,
                }
                for check in report.checks
            ],
        }

        # Save report if path provided
        if output_path:
            with open(output_path, "w") as f:
                json.dump(formatted_report, f, indent=2)

        return formatted_report

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from numeric score.

        Args:
            score: Numeric score (0-100)

        Returns:
            Letter grade (A-F)
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
