#!/usr/bin/env python3
"""Phase 16.3 CLI Integration for Scalable Deployment & Enterprise Integration.

Following crawl_mcp.py methodology for systematic CLI development:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

CLI Commands for Phase 16.3:
- phase16-3 validate-env - Validate Phase 16.3 environment
- phase16-3 deploy-cloud <complexity> - Deploy to cloud with complexity level
- phase16-3 integration register <type> - Register enterprise integration
- phase16-3 integration status - Show integration status
- phase16-3 integration test <name> - Test specific integration
- phase16-3 k8s-status - Show Kubernetes deployment status
- phase16-3 k8s-cleanup - Cleanup Kubernetes resources
- phase16-3 enterprise-sync - Sync data with enterprise systems
"""

import asyncio
import logging
import os
import sys
from typing import Any, Self

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .phase_16_3_cloud_native_deployment import CloudNativeDeployment, DeploymentConfig
from .phase_16_3_enterprise_integration import (
    EnterpriseIntegrationManager,
    IntegrationConfig,
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
console = Console()


class Phase163CLIManager:
    """CLI Manager for Phase 16.3 Scalable Deployment & Enterprise Integration.

    Following crawl_mcp.py methodology for systematic CLI management.
    """

    def __init__(self: Self):
        """Initialize Phase 16.3 CLI Manager."""
        # Step 1: Environment Validation First
        self.logger = logging.getLogger(__name__)
        self.cloud_deployment: CloudNativeDeployment | None = None
        self.integration_manager: EnterpriseIntegrationManager | None = None

        # Configuration
        self.config = {
            "deployment_enabled": os.getenv(
                "PHASE16_CLOUD_DEPLOYMENT_ENABLED", "true"
            ).lower()
            == "true",
            "integration_enabled": os.getenv(
                "PHASE16_ENTERPRISE_INTEGRATION_ENABLED", "true"
            ).lower()
            == "true",
            "default_namespace": os.getenv(
                "PHASE16_DEPLOYMENT_NAMESPACE", "sme-agents"
            ),
            "default_registry": os.getenv(
                "PHASE16_CONTAINER_REGISTRY", "localhost:5000"
            ),
            "log_level": os.getenv("PHASE16_LOG_LEVEL", "INFO"),
        }

        # Initialize components
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize cloud deployment and integration components."""
        try:
            if self.config["deployment_enabled"]:
                self.cloud_deployment = CloudNativeDeployment()

            if self.config["integration_enabled"]:
                self.integration_manager = EnterpriseIntegrationManager()

        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")

    async def validate_environment(self) -> dict[str, Any]:
        """Step 1: Environment Validation First (crawl_mcp.py methodology)."""
        console.print("🔍 [bold blue]Validating Phase 16.3 environment...[/bold blue]")

        validation_result: dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "components": {},
            "tools": {},
        }

        try:
            # Step 1.1: Validate cloud deployment environment
            if self.cloud_deployment:
                cloud_validation = await self.cloud_deployment.validate_environment()
                validation_result["components"]["cloud_deployment"] = cloud_validation

                if not cloud_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].extend(cloud_validation["errors"])
                    validation_result["warnings"].extend(cloud_validation["warnings"])

            # Step 1.2: Validate enterprise integration environment
            if self.integration_manager:
                integration_validation = (
                    await self.integration_manager.validate_environment()
                )
                validation_result["components"][
                    "enterprise_integration"
                ] = integration_validation

                if not integration_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].extend(integration_validation["errors"])
                    validation_result["warnings"].extend(
                        integration_validation["warnings"]
                    )

            # Step 1.3: Validate required tools and dependencies
            required_tools = ["kubectl", "helm", "docker"]
            optional_tools = ["terraform", "ansible"]

            for tool in required_tools + optional_tools:
                try:
                    import subprocess

                    result = subprocess.run(
                        [tool, "version"], capture_output=True, text=True, timeout=10
                    )
                    validation_result["tools"][tool] = {
                        "available": result.returncode == 0,
                        "version": (
                            result.stdout.split("\n")[0]
                            if result.returncode == 0
                            else None
                        ),
                        "required": tool in required_tools,
                    }

                    if tool in required_tools and result.returncode != 0:
                        validation_result["valid"] = False
                        validation_result["errors"].append(
                            f"Required tool {tool} not available"
                        )

                except (subprocess.TimeoutExpired, FileNotFoundError):
                    validation_result["tools"][tool] = {
                        "available": False,
                        "error": "Not found or timeout",
                        "required": tool in required_tools,
                    }

                    if tool in required_tools:
                        validation_result["valid"] = False
                        validation_result["errors"].append(
                            f"Required tool {tool} not found"
                        )

            # Step 1.4: Display validation results
            self._display_validation_results(validation_result)

            return validation_result

        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {e}")
            return validation_result

    def _display_validation_results(self, validation: dict[str, Any]) -> None:
        """Display validation results in a formatted table."""
        table = Table(title="Phase 16.3 Environment Validation")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="dim")

        # Cloud deployment status
        if "cloud_deployment" in validation["components"]:
            cloud_val = validation["components"]["cloud_deployment"]
            status = "✅ Valid" if cloud_val["valid"] else "❌ Invalid"
            details = f"Tools: {len(cloud_val.get('tools_available', {}))}"
            table.add_row("Cloud Deployment", status, details)

        # Enterprise integration status
        if "enterprise_integration" in validation["components"]:
            int_val = validation["components"]["enterprise_integration"]
            status = "✅ Valid" if int_val["valid"] else "❌ Invalid"
            integrations = int_val.get("integrations_available", {})
            available_count = sum(
                1 for i in integrations.values() if i.get("available")
            )
            details = f"Integrations: {available_count}/{len(integrations)}"
            table.add_row("Enterprise Integration", status, details)

        # Tools status
        for tool, info in validation.get("tools", {}).items():
            status = "✅ Available" if info["available"] else "❌ Missing"
            details = info.get("version", info.get("error", ""))
            required = " (Required)" if info.get("required") else " (Optional)"
            table.add_row(f"Tool: {tool}{required}", status, details)

        console.print(table)

        # Display errors and warnings
        if validation["errors"]:
            console.print("\n❌ [bold red]Errors:[/bold red]")
            for error in validation["errors"]:
                console.print(f"  • {error}")

        if validation["warnings"]:
            console.print("\n⚠️ [bold yellow]Warnings:[/bold yellow]")
            for warning in validation["warnings"]:
                console.print(f"  • {warning}")

    async def deploy_to_cloud(
        self, complexity: str, dry_run: bool = False
    ) -> dict[str, Any]:
        """Step 5: Deploy to cloud with specified complexity (crawl_mcp.py methodology)."""
        if not self.cloud_deployment:
            return {"success": False, "error": "Cloud deployment not enabled"}

        console.print(
            f"🚀 [bold blue]{'Validating' if dry_run else 'Deploying'} Phase 16.3 to cloud ({complexity} complexity)...[/bold blue]"
        )

        try:
            # Step 5.1: Create deployment configuration based on complexity
            config = self._create_deployment_config(complexity)
            self.cloud_deployment.config = config

            # Step 5.2: Generate Kubernetes manifests
            console.print("📝 Generating Kubernetes manifests...")
            manifests = await self.cloud_deployment.generate_kubernetes_manifests()
            console.print(f"✅ Generated {len(manifests)} manifests")

            # Step 5.3: Deploy to Kubernetes
            deployment_result = await self.cloud_deployment.deploy_to_kubernetes(
                dry_run=dry_run
            )

            # Step 5.4: Display deployment results
            self._display_deployment_results(deployment_result, dry_run)

            return deployment_result

        except Exception as e:
            error_msg = f"Cloud deployment failed: {e}"
            self.logger.error(error_msg)
            console.print(f"❌ [bold red]{error_msg}[/bold red]")
            return {"success": False, "error": error_msg}

    def _create_deployment_config(self, complexity: str) -> DeploymentConfig:
        """Create deployment configuration based on complexity level."""
        complexity_configs = {
            "basic": {
                "replicas": 2,
                "min_replicas": 1,
                "max_replicas": 5,
                "cpu_request": "250m",
                "cpu_limit": "1000m",
                "memory_request": "512Mi",
                "memory_limit": "2Gi",
            },
            "standard": {
                "replicas": 3,
                "min_replicas": 2,
                "max_replicas": 10,
                "cpu_request": "500m",
                "cpu_limit": "2000m",
                "memory_request": "1Gi",
                "memory_limit": "4Gi",
            },
            "advanced": {
                "replicas": 5,
                "min_replicas": 3,
                "max_replicas": 20,
                "cpu_request": "1000m",
                "cpu_limit": "4000m",
                "memory_request": "2Gi",
                "memory_limit": "8Gi",
            },
            "enterprise": {
                "replicas": 10,
                "min_replicas": 5,
                "max_replicas": 50,
                "cpu_request": "2000m",
                "cpu_limit": "8000m",
                "memory_request": "4Gi",
                "memory_limit": "16Gi",
            },
        }

        config_params = complexity_configs.get(
            complexity, complexity_configs["standard"]
        )

        return DeploymentConfig(
            deployment_name=f"sme-agents-{complexity}",
            namespace=self.config["default_namespace"],
            **config_params,
        )

    def _display_deployment_results(
        self, result: dict[str, Any], dry_run: bool
    ) -> None:
        """Display deployment results in a formatted panel."""
        if result["success"]:
            title = "Deployment Validation Results" if dry_run else "Deployment Results"
            content = []

            if not dry_run:
                content.append(
                    f"🚀 Deployment Time: {result.get('deployment_time', 0):.2f} seconds"
                )

            content.append(
                f"📦 Manifests Applied: {len(result.get('manifests_applied', []))}"
            )

            if result.get("manifests_applied"):
                content.append("   • " + "\n   • ".join(result["manifests_applied"]))

            if result.get("warnings"):
                content.append("\n⚠️ Warnings:")
                content.extend([f"   • {w}" for w in result["warnings"]])

            panel = Panel("\n".join(content), title=f"✅ {title}", border_style="green")
        else:
            title = "Deployment Failed"
            content = []

            if result.get("errors"):
                content.extend([f"❌ {e}" for e in result["errors"]])

            panel = Panel(
                "\n".join(content) if content else "Unknown error occurred",
                title=title,
                border_style="red",
            )

        console.print(panel)

    async def register_enterprise_integration(
        self, system_type: str, config_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Register enterprise system integration."""
        if not self.integration_manager:
            return {"success": False, "error": "Enterprise integration not enabled"}

        console.print(
            f"📝 [bold blue]Registering {system_type} integration...[/bold blue]"
        )

        try:
            # Create integration configuration
            config = IntegrationConfig(
                integration_name=config_data.get(
                    "name", f"{system_type.lower()}_integration"
                ),
                system_type=system_type,
                endpoint_url=config_data["endpoint_url"],
                auth_type=config_data.get("auth_type", "basic"),
                username=config_data.get("username"),
                password=config_data.get("password"),
                api_key=config_data.get("api_key"),
                token=config_data.get("token"),
            )

            # Register integration
            result = await self.integration_manager.register_integration(
                config.integration_name, config
            )

            if result["success"]:
                console.print(
                    f"✅ [bold green]{system_type} integration registered successfully[/bold green]"
                )
            else:
                console.print(
                    f"❌ [bold red]Registration failed: {result['error']}[/bold red]"
                )

            return result

        except Exception as e:
            error_msg = f"Integration registration failed: {e}"
            self.logger.error(error_msg)
            console.print(f"❌ [bold red]{error_msg}[/bold red]")
            return {"success": False, "error": error_msg}

    async def get_integration_status(self) -> dict[str, Any]:
        """Get status of all enterprise integrations."""
        if not self.integration_manager:
            return {"success": False, "error": "Enterprise integration not enabled"}

        console.print(
            "🔍 [bold blue]Checking enterprise integration status...[/bold blue]"
        )

        try:
            status = await self.integration_manager.get_integration_status()

            if status["success"]:
                self._display_integration_status(status)
            else:
                console.print(
                    f"❌ [bold red]Status check failed: {status['error']}[/bold red]"
                )

            return status

        except Exception as e:
            error_msg = f"Status check failed: {e}"
            self.logger.error(error_msg)
            console.print(f"❌ [bold red]{error_msg}[/bold red]")
            return {"success": False, "error": error_msg}

    def _display_integration_status(self, status: dict[str, Any]) -> None:
        """Display integration status in a formatted table."""
        table = Table(title="Enterprise Integration Status")
        table.add_column("Integration", style="cyan")
        table.add_column("System Type", style="blue")
        table.add_column("Status", style="bold")
        table.add_column("Connection", style="green")
        table.add_column("Last Activity", style="dim")

        integrations = status.get("integrations", {})
        for name, info in integrations.items():
            connection_test = info.get("connection_test", {})
            connection_status = (
                "✅ Connected" if connection_test.get("success") else "❌ Failed"
            )

            table.add_row(
                name,
                info["system_type"],
                info["status"],
                connection_status,
                info.get("last_activity", "N/A"),
            )

        console.print(table)

        # Display statistics
        stats = status.get("statistics", {})
        if stats:
            stats_panel = Panel(
                f"Total Integrations: {stats.get('total_integrations', 0)}\n"
                f"Active Connections: {stats.get('active_connections', 0)}\n"
                f"Successful Operations: {stats.get('successful_operations', 0)}\n"
                f"Failed Operations: {stats.get('failed_operations', 0)}",
                title="📊 Statistics",
                border_style="blue",
            )
            console.print(stats_panel)

    async def get_kubernetes_status(self) -> dict[str, Any]:
        """Get Kubernetes deployment status."""
        if not self.cloud_deployment:
            return {"success": False, "error": "Cloud deployment not enabled"}

        console.print(
            "🔍 [bold blue]Checking Kubernetes deployment status...[/bold blue]"
        )

        try:
            status = await self.cloud_deployment.get_deployment_status()
            self._display_kubernetes_status(status)
            return {"success": True, "status": status}

        except Exception as e:
            error_msg = f"Kubernetes status check failed: {e}"
            self.logger.error(error_msg)
            console.print(f"❌ [bold red]{error_msg}[/bold red]")
            return {"success": False, "error": error_msg}

    def _display_kubernetes_status(self, status: dict[str, Any]) -> None:
        """Display Kubernetes status in a formatted panel."""
        content = []

        content.append(f"Status: {status.get('status', 'Unknown')}")
        content.append(f"Replicas Ready: {status.get('replicas_ready', 0)}")

        if status.get("replicas_total"):
            content.append(f"Total Replicas: {status['replicas_total']}")

        if status.get("deployment_time"):
            content.append(f"Deployment Time: {status['deployment_time']}")

        if status.get("last_health_check"):
            content.append(f"Last Health Check: {status['last_health_check']}")

        if status.get("error"):
            content.append(f"❌ Error: {status['error']}")

        panel_style = "green" if status.get("status") == "deployed" else "yellow"
        panel = Panel(
            "\n".join(content),
            title="☸️ Kubernetes Deployment Status",
            border_style=panel_style,
        )

        console.print(panel)

    async def cleanup_resources(self) -> dict[str, Any]:
        """Step 6: Resource Management and Cleanup (crawl_mcp.py methodology)."""
        console.print("🧹 [bold blue]Cleaning up Phase 16.3 resources...[/bold blue]")

        cleanup_result = {
            "success": True,
            "cloud_cleanup": {},
            "integration_cleanup": {},
            "errors": [],
        }

        try:
            # Cleanup cloud deployment
            if self.cloud_deployment:
                console.print("🧹 Cleaning up Kubernetes resources...")
                cloud_cleanup = await self.cloud_deployment.cleanup_deployment()
                cleanup_result["cloud_cleanup"] = cloud_cleanup

                if not cloud_cleanup["success"]:
                    cleanup_result["success"] = False
                    cleanup_result["errors"].extend(cloud_cleanup.get("errors", []))

            # Cleanup enterprise integrations
            if self.integration_manager:
                console.print("🧹 Cleaning up enterprise integrations...")
                integration_cleanup = (
                    await self.integration_manager.cleanup_integrations()
                )
                cleanup_result["integration_cleanup"] = integration_cleanup

                if not integration_cleanup["success"]:
                    cleanup_result["success"] = False
                    cleanup_result["errors"].extend(
                        integration_cleanup.get("errors", [])
                    )

            if cleanup_result["success"]:
                console.print(
                    "✅ [bold green]Cleanup completed successfully[/bold green]"
                )
            else:
                console.print(
                    "⚠️ [bold yellow]Cleanup completed with errors[/bold yellow]"
                )
                for error in cleanup_result["errors"]:
                    console.print(f"  • {error}")

            return cleanup_result

        except Exception as e:
            error_msg = f"Cleanup failed: {e}"
            self.logger.error(error_msg)
            cleanup_result["success"] = False
            cleanup_result["errors"].append(error_msg)
            console.print(f"❌ [bold red]{error_msg}[/bold red]")
            return cleanup_result


# CLI Manager instance
cli_manager = Phase163CLIManager()


# CLI Commands using Click
@click.group(name="phase16-3")
def phase16_3():
    """Phase 16.3 Scalable Deployment & Enterprise Integration CLI."""
    pass


@phase16_3.command()
def validate_env():
    """Validate Phase 16.3 environment."""

    async def _validate():
        result = await cli_manager.validate_environment()
        if result["valid"]:
            console.print("✅ [bold green]Environment validation passed[/bold green]")
            sys.exit(0)
        else:
            console.print("❌ [bold red]Environment validation failed[/bold red]")
            sys.exit(1)

    asyncio.run(_validate())


@phase16_3.command()
@click.argument(
    "complexity", type=click.Choice(["basic", "standard", "advanced", "enterprise"])
)
@click.option(
    "--dry-run", is_flag=True, help="Validate deployment without applying changes"
)
def deploy_cloud(complexity, dry_run):
    """Deploy to cloud with specified complexity level."""

    async def _deploy():
        result = await cli_manager.deploy_to_cloud(complexity, dry_run)
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)

    asyncio.run(_deploy())


@phase16_3.group()
def integration():
    """Enterprise integration management commands."""
    pass


@integration.command()
@click.argument("system_type", type=click.Choice(["SAP", "SCADA", "Oracle"]))
@click.option("--endpoint", required=True, help="System endpoint URL")
@click.option("--username", help="Username for authentication")
@click.option("--password", help="Password for authentication")
@click.option("--api-key", help="API key for authentication")
def register(system_type, endpoint, username, password, api_key):
    """Register enterprise system integration."""

    async def _register():
        config_data = {
            "endpoint_url": endpoint,
            "username": username,
            "password": password,
            "api_key": api_key,
        }

        result = await cli_manager.register_enterprise_integration(
            system_type, config_data
        )
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)

    asyncio.run(_register())


@integration.command()
def status():
    """Show enterprise integration status."""

    async def _status():
        result = await cli_manager.get_integration_status()
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)

    asyncio.run(_status())


@phase16_3.command()
def k8s_status():
    """Show Kubernetes deployment status."""

    async def _status():
        result = await cli_manager.get_kubernetes_status()
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)

    asyncio.run(_status())


@phase16_3.command()
def cleanup():
    """Cleanup all Phase 16.3 resources."""

    async def _cleanup():
        result = await cli_manager.cleanup_resources()
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)

    asyncio.run(_cleanup())


if __name__ == "__main__":
    phase16_3()
