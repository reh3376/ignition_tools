"""Phase 9.7 Environment Setup System
==================================

Following crawl_mcp.py methodology for systematic environment configuration:
1. Environment Variable Validation First
2. Comprehensive Input Validation
3. Error Handling with User-Friendly Messages
4. Modular Component Testing
5. Progressive Complexity
6. Resource Management

This module provides comprehensive environment setup and validation for
the Phase 9.7 Module Deployment & Distribution system.
"""

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table


@dataclass
class EnvironmentRequirement:
    """Represents a single environment requirement."""

    name: str
    env_var: str
    description: str
    required: bool = True
    default_value: str | None = None
    validation_type: str = "path"  # path, url, boolean, string
    setup_instructions: str = ""


@dataclass
class ValidationResult:
    """Result of environment validation."""

    valid: bool
    error: str = ""
    warning: str = ""
    value: str | None = None
    suggestions: list[str] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


class Phase97EnvironmentSetup:
    """Phase 9.7 Environment Setup System

    Following crawl_mcp.py methodology:
    - Step 1: Environment Variable Validation First
    - Step 2: Comprehensive Input Validation
    - Step 3: Error Handling with User-Friendly Messages
    - Step 4: Modular Component Testing
    - Step 5: Progressive Complexity
    - Step 6: Resource Management
    """

    def __init__(self):
        self.console = Console()
        self.setup_results: dict[str, Any] = {
            "environment_validation": {},
            "component_setup": {},
            "integration_validation": {},
            "setup_summary": {},
        }

        # Define environment requirements following crawl_mcp.py patterns
        self.requirements = self._define_environment_requirements()

        # Load existing environment
        load_dotenv(override=False)

    def _define_environment_requirements(self) -> list[EnvironmentRequirement]:
        """Define all environment requirements for Phase 9.7."""
        return [
            # Core deployment directories
            EnvironmentRequirement(
                name="Deployment Temporary Directory",
                env_var="DEPLOYMENT_TEMP_DIR",
                description="Temporary directory for deployment operations",
                required=True,
                default_value=str(Path.home() / "tmp" / "ign_deployment"),
                validation_type="path",
                setup_instructions="Directory will be created automatically if it doesn't exist",
            ),
            EnvironmentRequirement(
                name="Deployment Output Directory",
                env_var="DEPLOYMENT_OUTPUT_DIR",
                description="Output directory for built modules",
                required=True,
                default_value=str(Path.home() / "ign_modules"),
                validation_type="path",
                setup_instructions="Directory will be created automatically if it doesn't exist",
            ),
            # Java and Gradle environment
            EnvironmentRequirement(
                name="Java Home Directory",
                env_var="JAVA_HOME",
                description="Java Development Kit installation directory",
                required=True,
                validation_type="path",
                setup_instructions="Install OpenJDK 11+ and set JAVA_HOME to installation directory",
            ),
            EnvironmentRequirement(
                name="Gradle Home Directory",
                env_var="GRADLE_HOME",
                description="Gradle build tool installation directory",
                required=True,
                validation_type="path",
                setup_instructions="Install Gradle 7+ and set GRADLE_HOME to installation directory",
            ),
            # Module signing configuration
            EnvironmentRequirement(
                name="Module Signing Enabled",
                env_var="MODULE_SIGNING_ENABLED",
                description="Enable/disable module signing",
                required=False,
                default_value="true",
                validation_type="boolean",
                setup_instructions="Set to 'true' to enable module signing, 'false' to disable",
            ),
            EnvironmentRequirement(
                name="Signing Certificate Path",
                env_var="SIGNING_CERT_PATH",
                description="Path to X.509 signing certificate",
                required=False,
                validation_type="path",
                setup_instructions="Generate or provide X.509 certificate for module signing",
            ),
            EnvironmentRequirement(
                name="Signing Private Key Path",
                env_var="SIGNING_KEY_PATH",
                description="Path to private key for signing",
                required=False,
                validation_type="path",
                setup_instructions="Generate or provide private key matching the certificate",
            ),
            # Repository configuration
            EnvironmentRequirement(
                name="Module Repository URL",
                env_var="MODULE_REPOSITORY_URL",
                description="URL for module repository",
                required=False,
                validation_type="url",
                setup_instructions="Configure module repository URL (e.g., Nexus, Artifactory)",
            ),
            EnvironmentRequirement(
                name="Module Repository Token",
                env_var="MODULE_REPOSITORY_TOKEN",
                description="Authentication token for repository",
                required=False,
                validation_type="string",
                setup_instructions="Obtain authentication token from repository administrator",
            ),
            # Optional webhook configuration
            EnvironmentRequirement(
                name="Deployment Webhook URL",
                env_var="DEPLOYMENT_WEBHOOK_URL",
                description="Webhook URL for deployment notifications",
                required=False,
                validation_type="url",
                setup_instructions="Configure webhook URL for deployment notifications (optional)",
            ),
        ]

    def validate_environment_variables(self) -> dict[str, ValidationResult]:
        """Step 1: Environment Variable Validation First
        Following crawl_mcp.py methodology
        """
        self.console.print(
            "🔍 Step 1: Environment Variable Validation", style="bold blue"
        )

        results = {}

        for req in self.requirements:
            value = os.getenv(req.env_var)
            result = self._validate_single_requirement(req, value)
            results[req.env_var] = result

            # Display result with user-friendly formatting
            status = "✅" if result.valid else "❌" if req.required else "⚠️"
            self.console.print(
                f"  {status} {req.name}: {self._format_validation_message(result)}"
            )

        self.setup_results["environment_validation"] = results
        return results

    def _validate_single_requirement(
        self, req: EnvironmentRequirement, value: str | None
    ) -> ValidationResult:
        """Validate a single environment requirement with comprehensive checks."""
        if not value:
            if req.required:
                return ValidationResult(
                    valid=False,
                    error=f"{req.env_var} is required but not set",
                    suggestions=[
                        f"Set {req.env_var} environment variable",
                        req.setup_instructions,
                    ],
                )
            elif req.default_value:
                return ValidationResult(
                    valid=True,
                    warning=f"Using default value: {req.default_value}",
                    value=req.default_value,
                    suggestions=[f"Consider setting {req.env_var} explicitly"],
                )
            else:
                return ValidationResult(
                    valid=True,
                    warning="Optional variable not set",
                    suggestions=[
                        f"Set {req.env_var} if needed: {req.setup_instructions}"
                    ],
                )

        # Validate based on type
        if req.validation_type == "path":
            return self._validate_path(value, req)
        elif req.validation_type == "url":
            return self._validate_url(value, req)
        elif req.validation_type == "boolean":
            return self._validate_boolean(value, req)
        else:  # string
            return ValidationResult(valid=True, value=value)

    def _validate_path(
        self, path_str: str, req: EnvironmentRequirement
    ) -> ValidationResult:
        """Validate path with user-friendly error messages."""
        try:
            path = Path(path_str).expanduser().resolve()

            # For directories that should exist (like JAVA_HOME, GRADLE_HOME)
            if req.env_var in ["JAVA_HOME", "GRADLE_HOME"]:
                if not path.exists():
                    return ValidationResult(
                        valid=False,
                        error=f"Directory does not exist: {path}",
                        suggestions=[
                            f"Install {req.name.split()[0]} and set {req.env_var}",
                            req.setup_instructions,
                            "Use package manager (brew, apt, etc.) for installation",
                        ],
                    )
                if not path.is_dir():
                    return ValidationResult(
                        valid=False,
                        error=f"Path is not a directory: {path}",
                        suggestions=[f"Ensure {req.env_var} points to a directory"],
                    )

            # For certificate/key files
            elif req.env_var in ["SIGNING_CERT_PATH", "SIGNING_KEY_PATH"]:
                if not path.exists():
                    return ValidationResult(
                        valid=False,
                        error=f"File does not exist: {path}",
                        suggestions=[
                            "Generate signing certificate and key",
                            "Use openssl or keytool to create certificates",
                            req.setup_instructions,
                        ],
                    )
                if not path.is_file():
                    return ValidationResult(
                        valid=False,
                        error=f"Path is not a file: {path}",
                        suggestions=[f"Ensure {req.env_var} points to a file"],
                    )

            # For directories that can be created (temp, output dirs)
            else:
                parent = path.parent
                if not parent.exists():
                    return ValidationResult(
                        valid=False,
                        error=f"Parent directory does not exist: {parent}",
                        suggestions=[
                            f"Create parent directory: mkdir -p {parent}",
                            "Ensure you have write permissions",
                        ],
                    )

            return ValidationResult(valid=True, value=str(path))

        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Invalid path format: {e}",
                suggestions=["Use absolute path format", "Check path syntax"],
            )

    def _validate_url(self, url: str, req: EnvironmentRequirement) -> ValidationResult:
        """Validate URL with comprehensive checks."""
        url = url.strip()

        if not (url.startswith("http://") or url.startswith("https://")):
            return ValidationResult(
                valid=False,
                error="URL must start with http:// or https://",
                suggestions=[
                    "Use full URL format: https://example.com",
                    req.setup_instructions,
                ],
            )

        # Basic URL format validation
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            if not parsed.netloc:
                return ValidationResult(
                    valid=False,
                    error="Invalid URL format",
                    suggestions=["Ensure URL has valid domain name"],
                )
        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"URL parsing failed: {e}",
                suggestions=["Check URL format and syntax"],
            )

        return ValidationResult(valid=True, value=url)

    def _validate_boolean(
        self, value: str, req: EnvironmentRequirement
    ) -> ValidationResult:
        """Validate boolean value."""
        value = value.lower().strip()
        if value in ["true", "false", "1", "0", "yes", "no"]:
            return ValidationResult(valid=True, value=value)
        else:
            return ValidationResult(
                valid=False,
                error=f"Invalid boolean value: {value}",
                suggestions=["Use: true/false, 1/0, yes/no", req.setup_instructions],
            )

    def _format_validation_message(self, result: ValidationResult) -> str:
        """Format validation result for display."""
        if result.valid:
            if result.warning:
                return f"[yellow]{result.warning}[/yellow]"
            else:
                return "[green]Valid[/green]"
        else:
            return f"[red]{result.error}[/red]"

    def check_system_requirements(self) -> dict[str, ValidationResult]:
        """Step 2: Comprehensive System Requirements Validation
        Check Java, Gradle, and other system dependencies
        """
        self.console.print(
            "\n🔍 Step 2: System Requirements Validation", style="bold blue"
        )

        results = {}

        # Check Java installation
        java_result = self._check_java_installation()
        results["java"] = java_result
        status = "✅" if java_result.valid else "❌"
        self.console.print(
            f"  {status} Java: {self._format_validation_message(java_result)}"
        )

        # Check Gradle installation
        gradle_result = self._check_gradle_installation()
        results["gradle"] = gradle_result
        status = "✅" if gradle_result.valid else "❌"
        self.console.print(
            f"  {status} Gradle: {self._format_validation_message(gradle_result)}"
        )

        # Check OpenSSL for certificate generation
        openssl_result = self._check_openssl_installation()
        results["openssl"] = openssl_result
        status = "✅" if openssl_result.valid else "⚠️"
        self.console.print(
            f"  {status} OpenSSL: {self._format_validation_message(openssl_result)}"
        )

        self.setup_results["system_requirements"] = results
        return results

    def _check_java_installation(self) -> ValidationResult:
        """Check Java installation and version."""
        try:
            # Check if java command is available
            result = subprocess.run(
                ["java", "-version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                return ValidationResult(
                    valid=False,
                    error="Java command not found",
                    suggestions=[
                        "Install OpenJDK 11 or later",
                        "Add Java to system PATH",
                        "Set JAVA_HOME environment variable",
                    ],
                )

            # Parse version from output
            version_output = result.stderr  # Java outputs version to stderr
            if (
                "11." in version_output
                or "17." in version_output
                or "21." in version_output
            ):
                return ValidationResult(
                    valid=True,
                    value=f"Java found: {version_output.split()[0] if version_output.split() else 'Unknown version'}",
                )
            else:
                return ValidationResult(
                    valid=False,
                    error="Java version 11+ required",
                    warning=f"Found: {version_output.split()[0] if version_output.split() else 'Unknown'}",
                    suggestions=[
                        "Install OpenJDK 11, 17, or 21",
                        "Update JAVA_HOME to point to newer version",
                    ],
                )

        except subprocess.TimeoutExpired:
            return ValidationResult(
                valid=False,
                error="Java command timed out",
                suggestions=["Check Java installation"],
            )
        except FileNotFoundError:
            return ValidationResult(
                valid=False,
                error="Java not found in PATH",
                suggestions=[
                    "Install OpenJDK 11+",
                    "Add Java bin directory to PATH",
                    "Set JAVA_HOME environment variable",
                ],
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Java check failed: {e}",
                suggestions=["Verify Java installation"],
            )

    def _check_gradle_installation(self) -> ValidationResult:
        """Check Gradle installation and version."""
        try:
            result = subprocess.run(
                ["gradle", "--version"], capture_output=True, text=True, timeout=15
            )

            if result.returncode != 0:
                return ValidationResult(
                    valid=False,
                    error="Gradle command not found",
                    suggestions=[
                        "Install Gradle 7.0+",
                        "Add Gradle to system PATH",
                        "Set GRADLE_HOME environment variable",
                    ],
                )

            # Parse version
            version_line = next(
                (line for line in result.stdout.split("\n") if "Gradle" in line), ""
            )
            if version_line:
                return ValidationResult(
                    valid=True, value=f"Gradle found: {version_line.strip()}"
                )
            else:
                return ValidationResult(
                    valid=True,
                    warning="Gradle found but version unclear",
                    suggestions=["Verify Gradle version is 7.0+"],
                )

        except subprocess.TimeoutExpired:
            return ValidationResult(
                valid=False,
                error="Gradle command timed out",
                suggestions=["Check Gradle installation"],
            )
        except FileNotFoundError:
            return ValidationResult(
                valid=False,
                error="Gradle not found in PATH",
                suggestions=[
                    "Install Gradle 7.0+",
                    "Add Gradle bin directory to PATH",
                    "Set GRADLE_HOME environment variable",
                ],
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Gradle check failed: {e}",
                suggestions=["Verify Gradle installation"],
            )

    def _check_openssl_installation(self) -> ValidationResult:
        """Check OpenSSL for certificate generation."""
        try:
            result = subprocess.run(
                ["openssl", "version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                return ValidationResult(
                    valid=True, value=f"OpenSSL found: {result.stdout.strip()}"
                )
            else:
                return ValidationResult(
                    valid=False,
                    warning="OpenSSL not available",
                    suggestions=[
                        "Install OpenSSL for certificate generation",
                        "Alternatively, use Java keytool for certificates",
                    ],
                )

        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            return ValidationResult(
                valid=False,
                warning="OpenSSL not found",
                suggestions=[
                    "Install OpenSSL (optional for certificate generation)",
                    "Use Java keytool as alternative",
                ],
            )

    def setup_development_environment(self, interactive: bool = True) -> dict[str, Any]:
        """Step 3: Progressive Environment Setup
        Set up development environment with user guidance
        """
        self.console.print(
            "\n🔧 Step 3: Development Environment Setup", style="bold blue"
        )

        setup_results = {}

        # Create required directories
        directory_results = self._setup_directories(interactive)
        setup_results["directories"] = directory_results

        # Generate certificates if needed
        cert_results = self._setup_certificates(interactive)
        setup_results["certificates"] = cert_results

        # Create .env file with settings
        env_results = self._setup_environment_file(interactive)
        setup_results["environment_file"] = env_results

        self.setup_results["environment_setup"] = setup_results
        return setup_results

    def _setup_directories(self, interactive: bool) -> dict[str, ValidationResult]:
        """Set up required directories."""
        self.console.print("  📁 Setting up directories...")

        results = {}
        directories = [
            ("DEPLOYMENT_TEMP_DIR", "Deployment temporary directory"),
            ("DEPLOYMENT_OUTPUT_DIR", "Deployment output directory"),
        ]

        for env_var, description in directories:
            req = next(r for r in self.requirements if r.env_var == env_var)

            # Get path from environment or use default
            path_str = os.getenv(env_var) or req.default_value
            if not path_str:
                results[env_var] = ValidationResult(
                    valid=False, error=f"No path specified for {env_var}"
                )
                continue

            try:
                path = Path(path_str).expanduser().resolve()

                if path.exists():
                    results[env_var] = ValidationResult(
                        valid=True, value=str(path), warning="Directory already exists"
                    )
                else:
                    if interactive:
                        create = Confirm.ask(f"Create directory {path}?", default=True)
                        if not create:
                            results[env_var] = ValidationResult(
                                valid=False, error="Directory creation declined"
                            )
                            continue

                    path.mkdir(parents=True, exist_ok=True)
                    results[env_var] = ValidationResult(valid=True, value=str(path))
                    self.console.print(f"    ✅ Created: {path}")

            except Exception as e:
                results[env_var] = ValidationResult(
                    valid=False,
                    error=f"Failed to create directory: {e}",
                    suggestions=["Check permissions", "Verify parent directory exists"],
                )

        return results

    def _setup_certificates(self, interactive: bool) -> dict[str, ValidationResult]:
        """Set up signing certificates."""
        self.console.print("  🔐 Setting up certificates...")

        results = {}

        # Check if signing is enabled
        signing_enabled = os.getenv("MODULE_SIGNING_ENABLED", "true").lower() == "true"

        if not signing_enabled:
            results["signing"] = ValidationResult(
                valid=True,
                warning="Module signing disabled",
                suggestions=["Enable signing by setting MODULE_SIGNING_ENABLED=true"],
            )
            return results

        # Check existing certificates
        cert_path = os.getenv("SIGNING_CERT_PATH")
        key_path = os.getenv("SIGNING_KEY_PATH")

        if (
            cert_path
            and key_path
            and Path(cert_path).exists()
            and Path(key_path).exists()
        ):
            results["certificates"] = ValidationResult(
                valid=True,
                value="Existing certificates found",
                warning="Using existing certificates",
            )
            return results

        # Offer to generate certificates
        if interactive:
            generate = Confirm.ask(
                "Generate self-signed certificates for development?", default=True
            )
            if not generate:
                results["certificates"] = ValidationResult(
                    valid=False,
                    error="Certificate generation declined",
                    suggestions=[
                        "Provide existing certificates via SIGNING_CERT_PATH and SIGNING_KEY_PATH",
                        "Generate certificates manually with openssl or keytool",
                    ],
                )
                return results

        # Generate certificates
        cert_result = self._generate_development_certificates()
        results["certificates"] = cert_result

        return results

    def _generate_development_certificates(self) -> ValidationResult:
        """Generate self-signed certificates for development."""
        try:
            # Create certificates directory
            cert_dir = Path.home() / ".ign_scripts" / "certificates"
            cert_dir.mkdir(parents=True, exist_ok=True)

            cert_path = cert_dir / "module_signing.crt"
            key_path = cert_dir / "module_signing.key"

            # Generate certificate using openssl
            cmd = [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-keyout",
                str(key_path),
                "-out",
                str(cert_path),
                "-days",
                "365",
                "-nodes",
                "-subj",
                "/CN=IGN Scripts Module Signing/O=Development/C=US",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.console.print(f"    ✅ Generated certificate: {cert_path}")
                self.console.print(f"    ✅ Generated private key: {key_path}")

                return ValidationResult(
                    valid=True,
                    value=f"Generated certificates in {cert_dir}",
                    suggestions=[
                        f"Set SIGNING_CERT_PATH={cert_path}",
                        f"Set SIGNING_KEY_PATH={key_path}",
                    ],
                )
            else:
                return ValidationResult(
                    valid=False,
                    error=f"Certificate generation failed: {result.stderr}",
                    suggestions=[
                        "Install OpenSSL",
                        "Use Java keytool as alternative",
                        "Provide existing certificates",
                    ],
                )

        except FileNotFoundError:
            return ValidationResult(
                valid=False,
                error="OpenSSL not found",
                suggestions=[
                    "Install OpenSSL for certificate generation",
                    "Use Java keytool: keytool -genkeypair -alias module-signing -keyalg RSA",
                    "Provide existing certificates",
                ],
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Certificate generation failed: {e}",
                suggestions=[
                    "Check OpenSSL installation",
                    "Verify write permissions",
                    "Use alternative certificate generation method",
                ],
            )

    def _setup_environment_file(self, interactive: bool) -> ValidationResult:
        """Create or update .env file with configuration."""
        self.console.print("  📝 Setting up environment file...")

        try:
            env_file = Path(".env")

            # Read existing .env if it exists
            existing_vars = {}
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            existing_vars[key] = value

            # Prepare new variables
            new_vars = {}

            # Add directory paths
            for req in self.requirements:
                if req.env_var in ["DEPLOYMENT_TEMP_DIR", "DEPLOYMENT_OUTPUT_DIR"]:
                    if req.env_var not in existing_vars:
                        new_vars[req.env_var] = req.default_value or ""

            # Add certificate paths if generated
            cert_dir = Path.home() / ".ign_scripts" / "certificates"
            if (cert_dir / "module_signing.crt").exists():
                new_vars["SIGNING_CERT_PATH"] = str(cert_dir / "module_signing.crt")
                new_vars["SIGNING_KEY_PATH"] = str(cert_dir / "module_signing.key")

            # Add signing enabled
            if "MODULE_SIGNING_ENABLED" not in existing_vars:
                new_vars["MODULE_SIGNING_ENABLED"] = "true"

            # Write to .env file
            if new_vars:
                with open(env_file, "a") as f:
                    f.write(
                        f"\n# Phase 9.7 Environment Setup - {datetime.now().isoformat()}\n"
                    )
                    for key, value in new_vars.items():
                        f.write(f"{key}={value}\n")

                self.console.print(
                    f"    ✅ Updated .env file with {len(new_vars)} variables"
                )

                return ValidationResult(
                    valid=True,
                    value=f"Added {len(new_vars)} environment variables",
                    suggestions=[
                        "Review .env file for additional configuration",
                        "Set JAVA_HOME and GRADLE_HOME manually",
                        "Configure MODULE_REPOSITORY_URL if needed",
                    ],
                )
            else:
                return ValidationResult(
                    valid=True,
                    warning="No new variables to add",
                    suggestions=["Review existing .env configuration"],
                )

        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Failed to update .env file: {e}",
                suggestions=["Check write permissions", "Manually create .env file"],
            )

    def generate_setup_report(self) -> dict[str, Any]:
        """Step 4: Generate comprehensive setup report"""
        self.console.print("\n📊 Step 4: Generating Setup Report", style="bold blue")

        # Validate current state
        env_results = self.validate_environment_variables()
        sys_results = self.check_system_requirements()

        # Calculate scores
        env_score = self._calculate_environment_score(env_results)
        sys_score = self._calculate_system_score(sys_results)
        overall_score = (env_score + sys_score) / 2

        report = {
            "setup_date": datetime.now().isoformat(),
            "methodology": "crawl_mcp.py systematic approach",
            "overall_score": round(overall_score, 1),
            "environment_score": round(env_score, 1),
            "system_score": round(sys_score, 1),
            "environment_results": env_results,
            "system_results": sys_results,
            "setup_results": self.setup_results,
            "recommendations": self._generate_setup_recommendations(
                env_results, sys_results
            ),
            "next_steps": self._generate_next_steps(env_results, sys_results),
        }

        self.setup_results["final_report"] = report

        # Display summary
        self._display_setup_summary(report)

        return report

    def _calculate_environment_score(
        self, results: dict[str, ValidationResult]
    ) -> float:
        """Calculate environment setup score."""
        total_weight = 0
        achieved_weight = 0

        weights = {
            "DEPLOYMENT_TEMP_DIR": 10,
            "DEPLOYMENT_OUTPUT_DIR": 10,
            "JAVA_HOME": 25,
            "GRADLE_HOME": 25,
            "MODULE_SIGNING_ENABLED": 5,
            "SIGNING_CERT_PATH": 10,
            "SIGNING_KEY_PATH": 10,
            "MODULE_REPOSITORY_URL": 5,
        }

        for env_var, result in results.items():
            weight = weights.get(env_var, 0)
            total_weight += weight
            if result.valid:
                achieved_weight += weight

        return (achieved_weight / total_weight * 100) if total_weight > 0 else 0

    def _calculate_system_score(self, results: dict[str, ValidationResult]) -> float:
        """Calculate system requirements score."""
        weights = {"java": 50, "gradle": 40, "openssl": 10}
        total_weight = sum(weights.values())
        achieved_weight = 0

        for component, result in results.items():
            weight = weights.get(component, 0)
            if result.valid:
                achieved_weight += weight

        return (achieved_weight / total_weight * 100) if total_weight > 0 else 0

    def _generate_setup_recommendations(
        self,
        env_results: dict[str, ValidationResult],
        sys_results: dict[str, ValidationResult],
    ) -> list[str]:
        """Generate setup recommendations."""
        recommendations = []

        # System requirements
        if not sys_results.get("java", ValidationResult(False)).valid:
            recommendations.append("🔴 Install Java 11+ and set JAVA_HOME")
        if not sys_results.get("gradle", ValidationResult(False)).valid:
            recommendations.append("🔴 Install Gradle 7+ and set GRADLE_HOME")

        # Environment variables
        critical_vars = ["DEPLOYMENT_TEMP_DIR", "DEPLOYMENT_OUTPUT_DIR"]
        for var in critical_vars:
            if not env_results.get(var, ValidationResult(False)).valid:
                recommendations.append(f"🟡 Configure {var}")

        # Optional but recommended
        if not env_results.get("SIGNING_CERT_PATH", ValidationResult(False)).valid:
            recommendations.append("🟡 Set up signing certificates for production")

        if not recommendations:
            recommendations.append("✅ Environment setup is complete!")

        return recommendations

    def _generate_next_steps(
        self,
        env_results: dict[str, ValidationResult],
        sys_results: dict[str, ValidationResult],
    ) -> list[str]:
        """Generate next steps."""
        steps = []

        # Immediate critical steps
        if not sys_results.get("java", ValidationResult(False)).valid:
            steps.append("Install Java Development Kit 11+")
        if not sys_results.get("gradle", ValidationResult(False)).valid:
            steps.append("Install Gradle 7+")

        # Configuration steps
        missing_critical = [
            var
            for var in ["JAVA_HOME", "GRADLE_HOME"]
            if not env_results.get(var, ValidationResult(False)).valid
        ]
        if missing_critical:
            steps.append(f"Set environment variables: {', '.join(missing_critical)}")

        # Testing steps
        if all(
            sys_results.get(comp, ValidationResult(False)).valid
            for comp in ["java", "gradle"]
        ):
            steps.append("Run Phase 9.7 validation tests")
            steps.append("Test module packaging with sample project")

        return steps

    def _display_setup_summary(self, report: dict[str, Any]) -> None:
        """Display setup summary with Rich formatting."""
        # Create summary table
        table = Table(title="Phase 9.7 Environment Setup Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Score", justify="center")
        table.add_column("Status", justify="center")

        table.add_row(
            "Environment Variables",
            f"{report['environment_score']}/100",
            (
                "✅ Ready"
                if report["environment_score"] >= 80
                else (
                    "⚠️ Partial"
                    if report["environment_score"] >= 50
                    else "❌ Needs Setup"
                )
            ),
        )
        table.add_row(
            "System Requirements",
            f"{report['system_score']}/100",
            (
                "✅ Ready"
                if report["system_score"] >= 80
                else "⚠️ Partial" if report["system_score"] >= 50 else "❌ Needs Setup"
            ),
        )
        table.add_row(
            "Overall",
            f"{report['overall_score']}/100",
            (
                "✅ Ready"
                if report["overall_score"] >= 80
                else "⚠️ Partial" if report["overall_score"] >= 50 else "❌ Needs Setup"
            ),
        )

        self.console.print(table)

        # Show recommendations
        if report["recommendations"]:
            self.console.print("\n📋 Recommendations:", style="bold yellow")
            for rec in report["recommendations"]:
                self.console.print(f"  {rec}")

        # Show next steps
        if report["next_steps"]:
            self.console.print("\n🎯 Next Steps:", style="bold green")
            for step in report["next_steps"]:
                self.console.print(f"  • {step}")


def main():
    """Main function for interactive environment setup."""
    setup = Phase97EnvironmentSetup()

    setup.console.print(
        Panel.fit(
            "Phase 9.7 Environment Setup\nFollowing crawl_mcp.py methodology",
            title="🚀 IGN Scripts",
            border_style="blue",
        )
    )

    # Step 1: Validate current environment
    env_results = setup.validate_environment_variables()

    # Step 2: Check system requirements
    sys_results = setup.check_system_requirements()

    # Step 3: Setup development environment
    setup_results = setup.setup_development_environment(interactive=True)

    # Step 4: Generate final report
    report = setup.generate_setup_report()

    # Save report
    import json

    with open("phase_97_environment_setup_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    setup.console.print(
        "\n📄 Complete setup report saved to: phase_97_environment_setup_report.json"
    )


if __name__ == "__main__":
    main()
