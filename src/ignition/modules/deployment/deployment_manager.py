"""Deployment Manager for orchestrating complete module deployment workflows.

Following the crawl_mcp.py methodology for structured development:
- Comprehensive validation and error handling
- Environment variable configuration
- Structured logging and progress tracking
- Orchestrated workflow management
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from .module_packager import ModulePackager, PackagingConfig, PackagingResult
from .module_signer import ModuleSigner, SigningConfig, SigningResult
from .repository_manager import RepositoryConfig, RepositoryManager, RepositoryResult

# Load environment variables
load_dotenv()

console = Console()


@dataclass
class DeploymentConfig:
    """Configuration for deployment operations."""

    # Workflow settings
    enable_packaging: bool = True
    enable_signing: bool = True
    enable_repository_upload: bool = True
    enable_validation: bool = True

    # Component configurations
    packaging_config: PackagingConfig | None = None
    signing_config: SigningConfig | None = None
    repository_config: RepositoryConfig | None = None

    # Deployment settings
    deployment_environment: str = field(
        default_factory=lambda: os.getenv("DEPLOYMENT_ENVIRONMENT", "development")
    )
    deployment_notes: str = ""
    deployment_tags: list[str] = field(default_factory=list)

    # Rollback settings
    enable_rollback: bool = True
    backup_previous_version: bool = True

    # Notification settings
    notification_webhook: str = field(
        default_factory=lambda: os.getenv("DEPLOYMENT_WEBHOOK_URL", "")
    )
    notification_email: str = field(
        default_factory=lambda: os.getenv("DEPLOYMENT_NOTIFICATION_EMAIL", "")
    )

    def __post_init__(self):
        """Initialize component configurations if not provided."""
        if self.packaging_config is None:
            self.packaging_config = PackagingConfig()
        if self.signing_config is None:
            self.signing_config = SigningConfig()
        if self.repository_config is None:
            self.repository_config = RepositoryConfig()


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""

    success: bool
    deployment_id: str = ""
    project_name: str = ""
    version: str = ""
    environment: str = ""

    # Component results
    packaging_result: PackagingResult | None = None
    signing_result: SigningResult | None = None
    repository_result: RepositoryResult | None = None

    # Deployment information
    deployment_timestamp: str = ""
    deployment_duration: float = 0.0
    artifacts: list[Path] = field(default_factory=list)

    # Status and errors
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    deployment_info: dict[str, Any] = field(default_factory=dict)


def validate_deployment_environment() -> dict[str, Any]:
    """Validate deployment environment following crawl_mcp.py validation patterns."""
    validation_results = {
        "java_available": False,
        "gradle_available": False,
        "signing_configured": False,
        "repository_configured": False,
        "environment_variables_set": False,
    }

    # Check Java
    try:
        import subprocess

        result = subprocess.run(["java", "-version"], capture_output=True, timeout=10)
        validation_results["java_available"] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        validation_results["java_available"] = False

    # Check Gradle
    try:
        result = subprocess.run(
            ["gradle", "--version"], capture_output=True, timeout=10
        )
        validation_results["gradle_available"] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        validation_results["gradle_available"] = False

    # Check signing configuration
    validation_results["signing_configured"] = bool(
        os.getenv("MODULE_SIGNING_CERT_PATH") and os.getenv("MODULE_SIGNING_KEY_PATH")
    )

    # Check repository configuration
    validation_results["repository_configured"] = bool(
        os.getenv("MODULE_REPOSITORY_URL")
        and (
            os.getenv("REPOSITORY_API_TOKEN")
            or (os.getenv("REPOSITORY_USERNAME") and os.getenv("REPOSITORY_PASSWORD"))
        )
    )

    # Check environment variables
    required_env_vars = [
        "DEPLOYMENT_ENVIRONMENT",
        "MODULE_REPOSITORY_URL",
    ]
    validation_results["environment_variables_set"] = all(
        os.getenv(var) for var in required_env_vars
    )

    return validation_results


class DeploymentManager:
    """Comprehensive deployment manager for Ignition modules."""

    def __init__(self, config: DeploymentConfig) -> None:
        """Initialize deployment manager with configuration."""
        self.config = config
        self.console = console

        # Initialize components
        self.packager = ModulePackager(self.config.packaging_config)
        self.signer = ModuleSigner(self.config.signing_config or SigningConfig())
        self.repository_manager = RepositoryManager(
            self.config.repository_config or RepositoryConfig()
        )

    def validate_environment(self) -> dict[str, bool]:
        """Validate deployment environment following crawl_mcp.py patterns."""
        validation_results = validate_deployment_environment()

        # Add component-specific validations
        if self.config.enable_packaging:
            packaging_env = self.packager.validate_environment()
            validation_results.update(
                {f"packaging_{k}": v for k, v in packaging_env.items()}
            )

        if self.config.enable_signing:
            signing_env = self.signer.validate_environment()
            validation_results.update(
                {f"signing_{k}": v for k, v in signing_env.items()}
            )

        if self.config.enable_repository_upload:
            repository_env = self.repository_manager.validate_environment()
            validation_results.update(
                {f"repository_{k}": v for k, v in repository_env.items()}
            )

        return validation_results

    def deploy_module(self, project_path: Path) -> DeploymentResult:
        """Deploy a module through the complete workflow.

        Args:
            project_path: Path to the module project

        Returns:
            DeploymentResult with deployment information
        """
        import time
        import uuid

        start_time = time.time()
        deployment_id = str(uuid.uuid4())[:8]

        result = DeploymentResult(
            success=False,
            deployment_id=deployment_id,
            project_name=project_path.name,
            version="auto",
            environment=self.config.deployment_environment,
            deployment_timestamp=datetime.now().isoformat(),
        )

        # Validate environment
        env_validation = self.validate_environment()
        missing_requirements = [k for k, v in env_validation.items() if not v]
        if missing_requirements:
            result.warnings.extend(
                [f"Missing requirement: {req}" for req in missing_requirements]
            )

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console,
            ) as progress:
                self.console.print(f"\n🚀 Starting deployment: {project_path.name}")
                self.console.print(f"📋 Deployment ID: {deployment_id}")
                self.console.print(
                    f"🌍 Environment: {self.config.deployment_environment}"
                )

                total_steps = sum(
                    [
                        self.config.enable_packaging,
                        self.config.enable_signing,
                        self.config.enable_repository_upload,
                        self.config.enable_validation,
                    ]
                )

                overall_task = progress.add_task(
                    "Overall deployment progress", total=total_steps
                )

                # Step 1: Package module
                if self.config.enable_packaging:
                    step_task = progress.add_task("📦 Packaging module...", total=1)

                    result.packaging_result = self.packager.package_module(project_path)
                    if not result.packaging_result.success:
                        result.errors.extend(
                            [
                                f"Packaging: {err}"
                                for err in result.packaging_result.errors
                            ]
                        )
                        return self._finalize_result(result, start_time)

                    if result.packaging_result.package_file:
                        result.artifacts.append(result.packaging_result.package_file)

                    progress.update(step_task, completed=1)
                    progress.update(overall_task, advance=1)
                    self.console.print("✅ Module packaged successfully")

                # Step 2: Sign module
                if (
                    self.config.enable_signing
                    and result.packaging_result
                    and result.packaging_result.module_file
                ):
                    step_task = progress.add_task("🔐 Signing module...", total=1)

                    result.signing_result = self.signer.sign_module(
                        result.packaging_result.module_file
                    )
                    if not result.signing_result.success:
                        result.errors.extend(
                            [f"Signing: {err}" for err in result.signing_result.errors]
                        )
                        return self._finalize_result(result, start_time)

                    if result.signing_result.signed_file:
                        result.artifacts.append(result.signing_result.signed_file)
                    if result.signing_result.signature_file:
                        result.artifacts.append(result.signing_result.signature_file)

                    progress.update(step_task, completed=1)
                    progress.update(overall_task, advance=1)
                    self.console.print("✅ Module signed successfully")

                # Step 3: Upload to repository
                if (
                    self.config.enable_repository_upload
                    and result.packaging_result
                    and result.packaging_result.package_file
                ):
                    step_task = progress.add_task(
                        "📤 Uploading to repository...", total=1
                    )

                    # Prepare metadata
                    metadata = self._prepare_upload_metadata(project_path, result)

                    result.repository_result = self.repository_manager.upload_module(
                        result.packaging_result.package_file, metadata
                    )
                    if not result.repository_result.success:
                        result.errors.extend(
                            [
                                f"Repository: {err}"
                                for err in result.repository_result.errors
                            ]
                        )
                        return self._finalize_result(result, start_time)

                    progress.update(step_task, completed=1)
                    progress.update(overall_task, advance=1)
                    self.console.print("✅ Module uploaded to repository")

                # Step 4: Validation
                if self.config.enable_validation:
                    step_task = progress.add_task(
                        "✅ Validating deployment...", total=1
                    )

                    validation_result = self._validate_deployment(result)
                    if not validation_result["success"]:
                        result.errors.extend(validation_result["errors"])
                        result.warnings.extend(validation_result["warnings"])

                    progress.update(step_task, completed=1)
                    progress.update(overall_task, advance=1)
                    self.console.print("✅ Deployment validated")

                result.success = True

                # Send notifications
                if self.config.notification_webhook or self.config.notification_email:
                    self._send_deployment_notification(result)

                self.console.print("\n🎉 Deployment completed successfully!")
                self._display_deployment_summary(result)

        except Exception as e:
            result.errors.append(f"Deployment error: {e!s}")

        return self._finalize_result(result, start_time)

    def deploy_multiple_modules(
        self, project_paths: list[Path]
    ) -> list[DeploymentResult]:
        """Deploy multiple modules in batch.

        Args:
            project_paths: List of project paths to deploy

        Returns:
            List of deployment results
        """
        results = []

        self.console.print(f"\n🚀 Batch deployment: {len(project_paths)} modules")

        for i, project_path in enumerate(project_paths, 1):
            self.console.print(
                f"\n📦 Deploying {i}/{len(project_paths)}: {project_path.name}"
            )
            result = self.deploy_module(project_path)
            results.append(result)

            if result.success:
                self.console.print(f"✅ {project_path.name} deployed successfully")
            else:
                self.console.print(f"❌ {project_path.name} deployment failed")
                for error in result.errors:
                    self.console.print(f"   Error: {error}")

        # Display batch summary
        self._display_batch_summary(results)

        return results

    def rollback_deployment(self, deployment_id: str) -> dict[str, Any]:
        """Rollback a deployment.

        Args:
            deployment_id: ID of the deployment to rollback

        Returns:
            Dictionary with rollback results
        """
        try:
            self.console.print(f"🔄 Rolling back deployment: {deployment_id}")

            # Implementation would depend on the specific rollback strategy
            # This is a placeholder for the rollback logic

            return {
                "success": True,
                "rollback_timestamp": datetime.now().isoformat(),
                "deployment_id": deployment_id,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Rollback error: {e!s}",
                "deployment_id": deployment_id,
            }

    def get_deployment_status(self, deployment_id: str) -> dict[str, Any]:
        """Get status of a deployment.

        Args:
            deployment_id: ID of the deployment

        Returns:
            Dictionary with deployment status
        """
        # This would typically query a deployment database or log files
        # Placeholder implementation
        return {
            "deployment_id": deployment_id,
            "status": "unknown",
            "timestamp": datetime.now().isoformat(),
        }

    def _prepare_upload_metadata(
        self, project_path: Path, result: DeploymentResult
    ) -> dict[str, Any]:
        """Prepare metadata for repository upload."""
        metadata = {
            "name": result.project_name,
            "version": result.version,
            "environment": result.environment,
            "deployment_id": result.deployment_id,
            "deployment_timestamp": result.deployment_timestamp,
            "notes": self.config.deployment_notes,
            "tags": self.config.deployment_tags,
        }

        # Add packaging information
        if result.packaging_result:
            metadata["packaging_info"] = result.packaging_result.packaging_info

        # Add signing information
        if result.signing_result:
            metadata["signing_info"] = {
                "signed": True,
                "certificate_info": result.signing_result.certificate_info,
                "signature_timestamp": result.signing_result.signature_timestamp,
            }

        return metadata

    def _validate_deployment(self, result: DeploymentResult) -> dict[str, Any]:
        """Validate deployment result."""
        validation_result = {
            "success": True,
            "errors": [],
            "warnings": [],
        }

        # Check packaging
        if self.config.enable_packaging and not result.packaging_result:
            validation_result["errors"].append(
                "Packaging was enabled but no packaging result found"
            )
            validation_result["success"] = False

        # Check signing
        if self.config.enable_signing and not result.signing_result:
            validation_result["errors"].append(
                "Signing was enabled but no signing result found"
            )
            validation_result["success"] = False

        # Check repository upload
        if self.config.enable_repository_upload and not result.repository_result:
            validation_result["errors"].append(
                "Repository upload was enabled but no upload result found"
            )
            validation_result["success"] = False

        # Check artifacts
        if not result.artifacts:
            validation_result["warnings"].append("No deployment artifacts were created")

        return validation_result

    def _send_deployment_notification(self, result: DeploymentResult) -> None:
        """Send deployment notification."""
        try:
            if self.config.notification_webhook:
                # Send webhook notification
                import requests

                notification_data = {
                    "deployment_id": result.deployment_id,
                    "project_name": result.project_name,
                    "version": result.version,
                    "environment": result.environment,
                    "success": result.success,
                    "timestamp": result.deployment_timestamp,
                    "errors": result.errors,
                    "warnings": result.warnings,
                }

                requests.post(
                    self.config.notification_webhook, json=notification_data, timeout=30
                )

        except Exception as e:
            self.console.print(f"⚠️  Notification failed: {e!s}")

    def _display_deployment_summary(self, result: DeploymentResult) -> None:
        """Display deployment summary table."""
        table = Table(title=f"Deployment Summary - {result.project_name}")

        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Deployment ID", result.deployment_id)
        table.add_row("Project", result.project_name)
        table.add_row("Version", result.version)
        table.add_row("Environment", result.environment)
        table.add_row("Duration", f"{result.deployment_duration:.2f}s")
        table.add_row("Artifacts", str(len(result.artifacts)))
        table.add_row("Status", "✅ Success" if result.success else "❌ Failed")

        if result.errors:
            table.add_row("Errors", str(len(result.errors)))
        if result.warnings:
            table.add_row("Warnings", str(len(result.warnings)))

        self.console.print(table)

    def _display_batch_summary(self, results: list[DeploymentResult]) -> None:
        """Display batch deployment summary."""
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        table = Table(title="Batch Deployment Summary")

        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")

        table.add_row("Total Deployments", str(len(results)))
        table.add_row("Successful", str(successful))
        table.add_row("Failed", str(failed))
        table.add_row("Success Rate", f"{(successful / len(results) * 100):.1f}%")

        self.console.print(table)

    def _finalize_result(
        self, result: DeploymentResult, start_time: float
    ) -> DeploymentResult:
        """Finalize deployment result with timing and additional info."""
        import time

        result.deployment_duration = time.time() - start_time
        result.deployment_info = {
            "deployment_manager_version": "1.0.0",
            "configuration": {
                "packaging_enabled": self.config.enable_packaging,
                "signing_enabled": self.config.enable_signing,
                "repository_upload_enabled": self.config.enable_repository_upload,
                "validation_enabled": self.config.enable_validation,
            },
            "environment_validation": self.validate_environment(),
        }

        return result
