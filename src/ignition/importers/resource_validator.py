"""Import File Validator for Ignition projects and resources.

This module provides basic validation for import files before they are
imported into Ignition gateways.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during validation."""

    severity: ValidationSeverity
    message: str
    resource_type: str
    resource_name: str
    details: dict[str, Any] | None = None
    suggested_action: str | None = None


@dataclass
class ValidationResult:
    """Result of import file validation."""

    issues: list[ValidationIssue] = field(default_factory=list)
    file_format: str | None = None
    file_size: int = 0
    detected_type: str | None = None
    is_valid: bool = True

    def has_critical_issues(self) -> bool:
        """Check if there are any critical validation issues."""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)

    def add_issue(
        self,
        severity: ValidationSeverity,
        message: str,
        resource_type: str = "file",
        resource_name: str = "",
        details: dict[str, Any] | None = None,
        suggested_action: str | None = None,
    ) -> None:
        """Add a validation issue."""
        self.issues.append(
            ValidationIssue(
                severity=severity,
                message=message,
                resource_type=resource_type,
                resource_name=resource_name,
                details=details,
                suggested_action=suggested_action,
            )
        )

        # Mark as invalid if critical or error issues
        if severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]:
            self.is_valid = False


class ImportFileValidator:
    """Validates import files for Ignition projects and resources."""

    def __init__(self) -> Any:
        """Initialize the validator."""
        self.supported_formats = {".json", ".zip", ".proj", ".gwbk"}

    def validate_file(self, file_path: Path, expected_type: str | None = None) -> ValidationResult:
        """Validate an import file.

        Args:
            file_path: Path to the file to validate
            expected_type: Expected file type ("project", "gateway_backup", "resources")

        Returns:
            ValidationResult with detailed validation information
        """
        result = ValidationResult()

        try:
            # Basic file validation
            self._validate_file_basics(file_path, result)

            if not result.is_valid:
                return result

            # Detect file type
            detected_type = self._detect_file_type(file_path, result)
            result.detected_type = detected_type

            # Validate against expected type
            if expected_type and detected_type != expected_type:
                result.add_issue(
                    ValidationSeverity.WARNING,
                    f"Expected {expected_type} but detected {detected_type}",
                    "file",
                    str(file_path),
                    suggested_action=f"Verify file is correct {expected_type} format",
                )

            logger.info(f"Validation completed for {file_path}: {len(result.issues)} issues found")
            return result

        except Exception as e:
            logger.error(f"Validation failed for {file_path}: {e}")
            result.add_issue(
                ValidationSeverity.CRITICAL,
                f"Validation failed: {e}",
                "file",
                str(file_path),
            )
            return result

    def _validate_file_basics(self, file_path: Path, result: ValidationResult) -> None:
        """Validate basic file properties."""
        # Check file exists
        if not file_path.exists():
            result.add_issue(
                ValidationSeverity.CRITICAL,
                f"File does not exist: {file_path}",
                "file",
                str(file_path),
            )
            return

        # Check file is readable
        if not file_path.is_file():
            result.add_issue(
                ValidationSeverity.CRITICAL,
                f"Path is not a file: {file_path}",
                "file",
                str(file_path),
            )
            return

        # Check file format
        file_format = file_path.suffix.lower()
        result.file_format = file_format

        if file_format not in self.supported_formats:
            result.add_issue(
                ValidationSeverity.ERROR,
                f"Unsupported file format: {file_format}",
                "file",
                str(file_path),
                suggested_action=f"Use one of: {', '.join(self.supported_formats)}",
            )
            return

        # Check file size
        try:
            file_size = file_path.stat().st_size
            result.file_size = file_size

            if file_size == 0:
                result.add_issue(ValidationSeverity.CRITICAL, "File is empty", "file", str(file_path))
            elif file_size > 100 * 1024 * 1024:  # 100MB
                result.add_issue(
                    ValidationSeverity.WARNING,
                    f"Large file size: {file_size:,} bytes",
                    "file",
                    str(file_path),
                    suggested_action="Consider splitting large imports",
                )
        except Exception as e:
            result.add_issue(
                ValidationSeverity.ERROR,
                f"Cannot read file properties: {e}",
                "file",
                str(file_path),
            )

    def _detect_file_type(self, file_path: Path, result: ValidationResult) -> str:
        """Detect the type of import file based on content."""
        # Simple detection based on file extension for now
        ext = file_path.suffix.lower()

        if ext == ".proj":
            return "project"
        elif ext == ".gwbk":
            return "gateway_backup"
        elif ext in [".json", ".zip"]:
            # Could be any type, return generic
            return "unknown"
        else:
            result.add_issue(
                ValidationSeverity.WARNING,
                "Cannot determine file type from extension",
                "file",
                str(file_path),
            )
            return "unknown"
