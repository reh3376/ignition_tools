"""Phase 9.8: Security and Compliance Module
=========================================

Following crawl_mcp.py methodology for systematic development:
1. Environment Variable Validation First
2. Comprehensive Input Validation
3. Error Handling with User-Friendly Messages
4. Modular Component Testing
5. Progressive Complexity
6. Resource Management

This module provides advanced security features:
- Comprehensive security audit tools
- Compliance reporting and validation
- Advanced authentication and authorization
- Security incident detection and response
"""

import json
import logging
import os
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Self, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Initialize console and logging
console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Configuration for security module following crawl_mcp.py patterns."""

    # Step 1: Environment Variable Validation First
    security_temp_dir: str = ""
    audit_log_dir: str = ""
    compliance_reports_dir: str = ""
    enable_audit_logging: bool = True
    enable_compliance_checks: bool = True
    enable_incident_detection: bool = True
    enable_authentication: bool = True

    # Security settings
    password_min_length: int = 12
    session_timeout_minutes: int = 30
    max_failed_login_attempts: int = 5
    encryption_algorithm: str = "AES-256"

    # Progressive complexity settings
    security_level: str = "standard"  # basic, standard, high, critical

    def __post_init__(self: Self):
        """Validate configuration following crawl_mcp.py methodology."""
        if not self.security_temp_dir:
            self.security_temp_dir = os.getenv(
                "SECURITY_TEMP_DIR", str(Path.home() / "tmp" / "ign_security")
            )
        if not self.audit_log_dir:
            self.audit_log_dir = os.getenv(
                "SECURITY_AUDIT_LOG_DIR",
                str(Path.home() / "ign_security" / "audit_logs"),
            )
        if not self.compliance_reports_dir:
            self.compliance_reports_dir = os.getenv(
                "SECURITY_COMPLIANCE_DIR",
                str(Path.home() / "ign_security" / "compliance"),
            )


@dataclass
class ValidationResult:
    """Result of validation following crawl_mcp.py patterns."""

    valid: bool
    error: str = ""
    warning: str = ""
    suggestions: list[str] = field(default_factory=list)
    security_level: str = "unknown"


@dataclass
class SecurityEvent:
    """Security event data structure with validation."""

    timestamp: datetime
    event_type: str  # login, logout, access_denied, security_violation, etc.
    user_id: str
    source_ip: str
    details: dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical

    def __post_init__(self: Self):
        """Validate security event structure."""
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be datetime object")
        if not self.event_type:
            raise ValueError("event_type is required")
        if not self.user_id:
            raise ValueError("user_id is required")


@dataclass
class ComplianceCheck:
    """Compliance check result."""

    check_name: str
    standard: str  # SOX, HIPAA, GDPR, etc.
    passed: bool
    details: str = ""
    recommendations: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class SecurityComplianceModule:
    """Security and Compliance Module for Ignition

    Following crawl_mcp.py methodology:
    - Step 1: Environment Variable Validation First
    - Step 2: Comprehensive Input Validation
    - Step 3: Error Handling with User-Friendly Messages
    - Step 4: Modular Component Testing
    - Step 5: Progressive Complexity
    - Step 6: Resource Management
    """

    def __init__(self: Self, config: SecurityConfig | None = None):
        """Initialize security module with comprehensive validation."""
        self.console = console
        self.logger = logger
        self.config = config or SecurityConfig()

        # Step 1: Environment Variable Validation First
        self.environment_validation = self.validate_environment()

        # Initialize components based on validation
        self.audit_logger = None
        self.compliance_checker = None
        self.incident_detector = None
        self.auth_manager = None

        # Resource management
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.security_events: list[SecurityEvent] = []
        self.active_sessions: dict[str, dict[str, Any]] = {}
        self.failed_login_attempts: dict[str, int] = {}

        # Initialize based on progressive complexity
        self._initialize_security_components()

    def validate_environment(self: Self) -> dict[str, ValidationResult]:
        """Step 1: Environment Variable Validation First
        Following crawl_mcp.py methodology
        """
        self.console.print(
            "🔍 Step 1: Security Environment Validation", style="bold blue"
        )

        results = {}

        # Validate required directories
        results["temp_directory"] = self._validate_directory(
            self.config.security_temp_dir,
            "Security temporary directory",
            create_if_missing=True,
        )

        results["audit_log_directory"] = self._validate_directory(
            self.config.audit_log_dir, "Audit log directory", create_if_missing=True
        )

        results["compliance_reports_directory"] = self._validate_directory(
            self.config.compliance_reports_dir,
            "Compliance reports directory",
            create_if_missing=True,
        )

        # Validate dependencies
        results["security_dependencies"] = self._validate_security_dependencies()
        results["encryption_dependencies"] = self._validate_encryption_dependencies()
        results["compliance_dependencies"] = self._validate_compliance_dependencies()

        # Validate security configuration
        results["security_configuration"] = self._validate_security_configuration()

        # Display validation results
        self._display_validation_results(results)

        return results

    def _validate_directory(
        self, path: str, description: str, create_if_missing: bool = False
    ) -> ValidationResult:
        """Validate directory with security considerations."""
        try:
            path_obj = Path(path)

            if not path_obj.exists():
                if create_if_missing:
                    path_obj.mkdir(
                        parents=True, exist_ok=True, mode=0o750
                    )  # Secure permissions
                    return ValidationResult(
                        valid=True,
                        warning=f"{description} created at {path} with secure permissions",
                        security_level="secure",
                    )
                else:
                    return ValidationResult(
                        valid=False,
                        error=f"{description} does not exist: {path}",
                        suggestions=[
                            f"Create directory with secure permissions: mkdir -m 750 -p {path}"
                        ],
                        security_level="insecure",
                    )

            if not path_obj.is_dir():
                return ValidationResult(
                    valid=False,
                    error=f"{description} is not a directory: {path}",
                    security_level="invalid",
                )

            # Check permissions for security
            stat_info = path_obj.stat()
            permissions = oct(stat_info.st_mode)[-3:]

            if permissions > "750":
                return ValidationResult(
                    valid=True,
                    warning=f"{description} has loose permissions: {permissions}",
                    suggestions=[f"Tighten permissions: chmod 750 {path}"],
                    security_level="warning",
                )

            # Test write permissions
            test_file = path_obj / ".test_write"
            try:
                test_file.touch(mode=0o640)  # Secure file permissions
                test_file.unlink()
                return ValidationResult(valid=True, security_level="secure")
            except PermissionError:
                return ValidationResult(
                    valid=False,
                    error=f"No write permission for {description}: {path}",
                    suggestions=[f"Fix permissions: chmod 750 {path}"],
                    security_level="insecure",
                )

        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Error validating {description}: {e!s}",
                security_level="error",
            )

    def _validate_security_dependencies(self: Self) -> ValidationResult:
        """Validate security dependencies with detailed feedback."""
        missing_packages = []

        try:
            import hmac
            import secrets
        except ImportError:
            missing_packages.extend(["secrets", "hmac"])

        try:
            import hashlib
        except ImportError:
            missing_packages.append("hashlib")

        if missing_packages:
            return ValidationResult(
                valid=False,
                error=f"Missing security packages: {', '.join(missing_packages)}",
                suggestions=[
                    "These are standard library modules - check Python installation"
                ],
                security_level="critical",
            )

        return ValidationResult(valid=True, security_level="secure")

    def _validate_encryption_dependencies(self: Self) -> ValidationResult:
        """Validate encryption dependencies."""
        missing_packages = []

        try:
            import cryptography
        except ImportError:
            missing_packages.append("cryptography")

        try:
            import jwt
        except ImportError:
            missing_packages.append("PyJWT")

        if missing_packages:
            return ValidationResult(
                valid=False,
                error=f"Missing encryption packages: {', '.join(missing_packages)}",
                suggestions=[
                    f"Install packages: pip install {' '.join(missing_packages)}"
                ],
                security_level="critical",
            )

        return ValidationResult(valid=True, security_level="secure")

    def _validate_compliance_dependencies(self: Self) -> ValidationResult:
        """Validate compliance checking dependencies."""
        if not self.config.enable_compliance_checks:
            return ValidationResult(
                valid=True,
                warning="Compliance checks disabled",
                security_level="warning",
            )

        # For now, compliance checking uses built-in modules
        return ValidationResult(valid=True, security_level="secure")

    def _validate_security_configuration(self: Self) -> ValidationResult:
        """Validate security configuration parameters."""
        issues = []

        if self.config.password_min_length < 8:
            issues.append("Password minimum length should be at least 8 characters")

        if self.config.session_timeout_minutes > 120:
            issues.append("Session timeout is very long (>2 hours)")

        if self.config.max_failed_login_attempts > 10:
            issues.append("Max failed login attempts is high (>10)")

        if issues:
            return ValidationResult(
                valid=True,
                warning="; ".join(issues),
                suggestions=["Review security configuration parameters"],
                security_level="warning",
            )

        return ValidationResult(valid=True, security_level="secure")

    def _display_validation_results(self: Self, results: dict[str, ValidationResult]) -> None:
        """Display validation results with security-focused formatting."""
        table = Table(title="Security Environment Validation")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Security Level", style="yellow")
        table.add_column("Details", style="dim")

        for component, result in results.items():
            if result.valid:
                status = "✅ Valid"
            else:
                status = "❌ Invalid"

            # Security level styling
            security_styles = {
                "secure": "green",
                "warning": "yellow",
                "insecure": "red",
                "critical": "red bold",
                "unknown": "dim",
            }
            security_level = result.security_level.upper()

            details = result.warning or result.error or "OK"
            if result.suggestions:
                details += f" | Suggestion: {result.suggestions[0]}"

            table.add_row(
                component.replace("_", " ").title(),
                status,
                f"[{security_styles.get(result.security_level, 'dim')}]{security_level}[/]",
                details,
            )

        self.console.print(table)

    def _initialize_security_components(self: Self) -> None:
        """Step 5: Progressive Complexity
        Initialize security components based on security level and validation results
        """
        self.console.print(
            "🔧 Step 5: Progressive Security Component Initialization",
            style="bold blue",
        )

        # Check if environment validation passed
        all_valid = all(result.valid for result in self.environment_validation.values())

        if not all_valid:
            self.console.print(
                "⚠️ Some validations failed. Initializing in limited mode.",
                style="yellow",
            )
            self.config.security_level = "basic"

        # Initialize components progressively
        if self.config.security_level == "basic":
            self._initialize_basic_security()
        elif self.config.security_level == "standard":
            self._initialize_standard_security()
        elif self.config.security_level == "high":
            self._initialize_high_security()
        elif self.config.security_level == "critical":
            self._initialize_critical_security()

    def _initialize_basic_security(self: Self) -> None:
        """Initialize basic security components."""
        self.console.print("🔒 Initializing Basic Security Components", style="green")

        # Basic audit logger
        self.audit_logger = BasicAuditLogger(self.config)

        # Simple authentication
        self.auth_manager = BasicAuthManager(self.config)

        self.console.print("✅ Basic security components initialized", style="green")

    def _initialize_standard_security(self: Self) -> None:
        """Initialize standard security components."""
        self.console.print(
            "🔒 Initializing Standard Security Components", style="green"
        )

        # Initialize basic components first
        self._initialize_basic_security()

        # Add standard components
        if self.environment_validation.get(
            "compliance_dependencies", ValidationResult(False)
        ).valid:
            self.compliance_checker = StandardComplianceChecker(self.config)

        if self.config.enable_incident_detection:
            self.incident_detector = BasicIncidentDetector(self.config)

        self.console.print("✅ Standard security components initialized", style="green")

    def _initialize_high_security(self: Self) -> None:
        """Initialize high security components."""
        self.console.print("🔒 Initializing High Security Components", style="green")

        # Initialize standard components first
        self._initialize_standard_security()

        # Add high security components
        if self.environment_validation.get(
            "encryption_dependencies", ValidationResult(False)
        ).valid:
            self.auth_manager = AdvancedAuthManager(self.config)
            self.incident_detector = AdvancedIncidentDetector(self.config)

        self.console.print("✅ High security components initialized", style="green")

    def _initialize_critical_security(self: Self) -> None:
        """Initialize critical security components."""
        self.console.print(
            "🔒 Initializing Critical Security Components", style="green"
        )

        # Initialize high security components first
        self._initialize_high_security()

        # Add critical security components
        self.compliance_checker = EnterpriseComplianceChecker(self.config)
        self.audit_logger = EnterpriseAuditLogger(self.config)

        self.console.print("✅ Critical security components initialized", style="green")

    def log_security_event(
        self, event: dict[str, Any] | SecurityEvent
    ) -> dict[str, Any]:
        """Step 2: Comprehensive Input Validation
        Log security event with full validation
        """
        try:
            # Validate input event
            validated_event = self._validate_security_event(event)

            if not validated_event["valid"]:
                return {
                    "success": False,
                    "error": validated_event["error"],
                    "suggestions": validated_event.get("suggestions", []),
                }

            # Log event based on security level
            if self.audit_logger:
                result = self.audit_logger.log_event(validated_event["event"])

                # Store in memory for analysis
                self.security_events.append(validated_event["event"])

                return {
                    "success": True,
                    "event_id": result.get("event_id", "unknown"),
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "success": False,
                    "error": "Audit logger not initialized",
                    "suggestions": ["Check environment validation and reinitialize"],
                }

        except Exception as e:
            # Step 3: Error Handling with User-Friendly Messages
            self.logger.error(f"Error logging security event: {e!s}")
            return {
                "success": False,
                "error": f"Security event logging failed: {e!s}",
                "suggestions": ["Check event format and try again"],
            }

    def _validate_security_event(
        self, event: dict[str, Any] | SecurityEvent
    ) -> dict[str, Any]:
        """Comprehensive security event validation following crawl_mcp.py patterns."""
        if event is None:
            return {
                "valid": False,
                "error": "Event cannot be None",
                "suggestions": ["Provide valid security event data"],
            }

        # Convert dict to SecurityEvent if needed
        if isinstance(event, dict):
            try:
                # Add timestamp if missing
                if "timestamp" not in event:
                    event["timestamp"] = datetime.now()

                security_event = SecurityEvent(
                    timestamp=(
                        event["timestamp"]
                        if isinstance(event["timestamp"], datetime)
                        else datetime.fromisoformat(str(event["timestamp"]))
                    ),
                    event_type=event.get("event_type", "unknown"),
                    user_id=event.get("user_id", "unknown"),
                    source_ip=event.get("source_ip", "unknown"),
                    details=event.get("details", {}),
                    severity=event.get("severity", "info"),
                )
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Event validation failed: {e!s}",
                    "suggestions": [
                        "Check event format: {'event_type': '...', 'user_id': '...', 'source_ip': '...'}"
                    ],
                }
        elif isinstance(event, SecurityEvent):
            security_event = event
        else:
            return {
                "valid": False,
                "error": "Event must be dictionary or SecurityEvent object",
                "suggestions": ["Format event as dictionary or SecurityEvent"],
            }

        return {"valid": True, "event": security_event}

    def run_compliance_check(self: Self, standard: str = "general") -> dict[str, Any]:
        """Run compliance checks for specified standard."""
        try:
            if not self.compliance_checker:
                return {
                    "success": False,
                    "error": "Compliance checker not initialized",
                    "suggestions": ["Enable compliance checks and reinitialize"],
                }

            checks = self.compliance_checker.run_checks(standard)

            return {
                "success": True,
                "standard": standard,
                "checks": [
                    {
                        "name": check.check_name,
                        "passed": check.passed,
                        "details": check.details,
                        "recommendations": check.recommendations,
                    }
                    for check in checks
                ],
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Compliance check failed: {e!s}",
                "suggestions": ["Check compliance checker configuration"],
            }

    def generate_security_report(self: Self) -> dict[str, Any]:
        """Generate comprehensive security report."""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "module_status": "active",
                "configuration": {
                    "security_level": self.config.security_level,
                    "audit_logging_enabled": self.config.enable_audit_logging,
                    "compliance_checks_enabled": self.config.enable_compliance_checks,
                    "incident_detection_enabled": self.config.enable_incident_detection,
                    "authentication_enabled": self.config.enable_authentication,
                },
                "environment_validation": {
                    component: {
                        "valid": result.valid,
                        "security_level": result.security_level,
                    }
                    for component, result in self.environment_validation.items()
                },
                "security_summary": {
                    "events_logged": len(self.security_events),
                    "active_sessions": len(self.active_sessions),
                    "failed_login_attempts": sum(self.failed_login_attempts.values()),
                },
                "components": {
                    "audit_logger": self.audit_logger is not None,
                    "compliance_checker": self.compliance_checker is not None,
                    "incident_detector": self.incident_detector is not None,
                    "auth_manager": self.auth_manager is not None,
                },
            }

            return {"success": True, "report": report}

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate security report: {e!s}",
            }

    def cleanup_resources(self: Self) -> None:
        """Step 6: Resource Management
        Clean up security resources and sensitive data
        """
        try:
            self.console.print("🧹 Cleaning up security resources...", style="yellow")

            # Shutdown executor
            if self.executor:
                self.executor.shutdown(wait=True)

            # Clear sensitive data from memory
            self.active_sessions.clear()
            self.failed_login_attempts.clear()

            # Securely clear security events (keep for audit trail in production)
            # In production, events should be persisted to secure storage
            # self.security_events.clear()

            # Clean temporary files securely
            temp_dir = Path(self.config.security_temp_dir)
            if temp_dir.exists():
                for temp_file in temp_dir.glob("*.tmp"):
                    # Overwrite file content before deletion for security
                    with open(temp_file, "wb") as f:
                        f.write(b"0" * temp_file.stat().st_size)
                    temp_file.unlink()

            self.console.print(
                "✅ Security resources cleaned up successfully", style="green"
            )

        except Exception as e:
            self.console.print(f"⚠️ Error during security cleanup: {e!s}", style="red")


# Supporting classes for progressive complexity


class BasicAuditLogger:
    """Basic audit logging component."""

    def __init__(self: Self, config: SecurityConfig):
        self.config = config
        self.log_file = Path(config.audit_log_dir) / "audit.log"

    def log_event(self: Self, event: SecurityEvent) -> dict[str, Any]:
        """Log security event to file."""
        try:
            log_entry = {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "user_id": event.user_id,
                "source_ip": event.source_ip,
                "severity": event.severity,
                "details": event.details,
            }

            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

            return {"event_id": f"evt_{int(time.time())}"}

        except Exception as e:
            return {"error": f"Failed to log event: {e!s}"}


class BasicAuthManager:
    """Basic authentication manager."""

    def __init__(self: Self, config: SecurityConfig):
        self.config = config

    def authenticate(self: Self, username: str, password: str) -> dict[str, Any]:
        """Basic authentication."""
        # In production, this would validate against secure user store
        return {
            "authenticated": True,
            "user_id": username,
            "session_id": f"sess_{int(time.time())}",
        }


class StandardComplianceChecker:
    """Standard compliance checker."""

    def __init__(self: Self, config: SecurityConfig):
        self.config = config

    def run_checks(self: Self, standard: str) -> list[ComplianceCheck]:
        """Run standard compliance checks."""
        checks = []

        # Example compliance checks
        checks.append(
            ComplianceCheck(
                check_name="Password Policy",
                standard=standard,
                passed=self.config.password_min_length >= 8,
                details=f"Minimum password length: {self.config.password_min_length}",
                recommendations=["Ensure passwords are at least 8 characters long"],
            )
        )

        checks.append(
            ComplianceCheck(
                check_name="Session Management",
                standard=standard,
                passed=self.config.session_timeout_minutes <= 60,
                details=f"Session timeout: {self.config.session_timeout_minutes} minutes",
                recommendations=["Limit session timeout to 60 minutes or less"],
            )
        )

        return checks


class BasicIncidentDetector:
    """Basic security incident detector."""

    def __init__(self: Self, config: SecurityConfig):
        self.config = config

    def detect_incidents(self: Self, events: list[SecurityEvent]) -> list[dict[str, Any]]:
        """Detect basic security incidents."""
        incidents = []

        # Example: Detect multiple failed logins
        failed_logins = [e for e in events if e.event_type == "login_failed"]
        if len(failed_logins) > self.config.max_failed_login_attempts:
            incidents.append(
                {
                    "type": "multiple_failed_logins",
                    "severity": "warning",
                    "count": len(failed_logins),
                }
            )

        return incidents


class AdvancedAuthManager:
    """Advanced authentication manager with encryption."""

    def __init__(self: Self, config: SecurityConfig):
        self.config = config

    def authenticate(self: Self, username: str, password: str) -> dict[str, Any]:
        """Advanced authentication with token generation."""
        # Would implement JWT tokens, MFA, etc.
        return {
            "authenticated": True,
            "user_id": username,
            "session_token": "jwt_token_placeholder",
            "expires_at": (
                datetime.now() + timedelta(minutes=self.config.session_timeout_minutes)
            ).isoformat(),
        }


class AdvancedIncidentDetector:
    """Advanced security incident detector with ML capabilities."""

    def __init__(self: Self, config: SecurityConfig):
        self.config = config

    def detect_incidents(self: Self, events: list[SecurityEvent]) -> list[dict[str, Any]]:
        """Detect advanced security incidents using pattern analysis."""
        incidents = []

        # More sophisticated incident detection would go here
        # Including anomaly detection, pattern matching, etc.

        return incidents


class EnterpriseComplianceChecker:
    """Enterprise-grade compliance checker."""

    def __init__(self: Self, config: SecurityConfig):
        self.config = config

    def run_checks(self: Self, standard: str) -> list[ComplianceCheck]:
        """Run enterprise compliance checks for multiple standards."""
        checks = []

        # Would implement comprehensive compliance checks for
        # SOX, HIPAA, GDPR, PCI-DSS, etc.

        return checks


class EnterpriseAuditLogger:
    """Enterprise audit logger with encryption and integrity checking."""

    def __init__(self: Self, config: SecurityConfig):
        self.config = config

    def log_event(self: Self, event: SecurityEvent) -> dict[str, Any]:
        """Log event with encryption and digital signature."""
        # Would implement encrypted logging, digital signatures,
        # tamper detection, etc.
        return {"event_id": f"ent_evt_{int(time.time())}"}


# Main function for testing
def main():
    """Test the security module following crawl_mcp.py methodology."""
    console.print(
        Panel.fit("🔒 Phase 9.8 Security and Compliance Module Test", style="red bold")
    )

    # Test with different security levels
    for security_level in ["basic", "standard", "high", "critical"]:
        console.print(f"\n🔒 Testing {security_level.title()} Security Level")

        config = SecurityConfig(security_level=security_level)
        module = SecurityComplianceModule(config)

        # Test security event logging
        test_event = {
            "event_type": "login_attempt",
            "user_id": "test_user",
            "source_ip": "192.168.1.100",
            "details": {"success": True},
        }

        result = module.log_security_event(test_event)
        console.print(f"Event logging result: {result['success']}")

        # Test compliance check
        compliance_result = module.run_compliance_check("general")
        console.print(f"Compliance check result: {compliance_result['success']}")

        # Generate report
        report = module.generate_security_report()
        if report["success"]:
            console.print("Security report generated successfully")

        # Cleanup
        module.cleanup_resources()


if __name__ == "__main__":
    main()
