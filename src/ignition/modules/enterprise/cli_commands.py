"""Phase 10: Enterprise Integration & Deployment CLI Commands."""

import contextlib
import json
import logging

import click
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from .analytics_platform import AdvancedAnalyticsPlatformModule
from .cloud_integration import CloudIntegrationModule

# Import enterprise modules
from .enterprise_architecture import EnterpriseArchitectureModule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize console
console = Console()


@click.group(name="enterprise")
def enterprise_cli() -> None:
    """Phase 10: Enterprise Integration & Deployment commands."""
    pass


@enterprise_cli.group(name="architecture")
def architecture_group() -> None:
    """Enterprise Architecture commands (Phase 10.1)."""
    pass


@architecture_group.command(name="validate-env")
@click.option(
    "--output-format",
    default="table",
    type=click.Choice(["table", "json"]),
    help="Output format for validation results",
)
def validate_architecture_env(output_format: str) -> None:
    """Validate enterprise architecture environment variables."""
    try:
        console.print(
            "🏗️ Phase 10.1: Enterprise Architecture Environment Validation",
            style="bold blue",
        )

        # Initialize module
        architecture_module = EnterpriseArchitectureModule()

        # Get validation results
        validation_results = architecture_module.env_validation

        if output_format == "json":
            console.print(json.dumps(validation_results, indent=2))

        # Display overall status
        if validation_results["overall_valid"]:
            console.print(
                "✅ Enterprise Architecture environment validation passed!",
                style="bold green",
            )
        else:
            console.print(
                "❌ Enterprise Architecture environment validation failed!",
                style="bold red",
            )
            console.print(f"Score: {validation_results['validation_score']:.1f}%", style="yellow")

    except Exception as e:
        console.print(f"❌ Validation failed: {e!s}", style="bold red")
        logger.error(f"Architecture environment validation failed: {e}")


@architecture_group.command(name="deploy")
@click.option(
    "--complexity",
    default="basic",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def deploy_architecture(complexity: str) -> None:
    """Deploy enterprise architecture with progressive complexity."""
    try:
        console.print(
            f"🚀 Phase 10.1: Deploying Enterprise Architecture ({complexity} complexity)",
            style="bold blue",
        )

        # Initialize module
        architecture_module = EnterpriseArchitectureModule()

        # Check environment validation first
        if not architecture_module.env_validation["overall_valid"]:
            console.print(
                "❌ Environment validation failed. Please fix environment variables first.",
                style="bold red",
            )
            console.print("Run: enterprise architecture validate-env", style="yellow")
            return

        # Perform deployment
        deployment_result = architecture_module.deploy_architecture(complexity)

        # Display results
        if deployment_result["success"]:
            console.print(
                "✅ Enterprise Architecture deployment completed successfully!",
                style="bold green",
            )
            console.print(
                f"Complexity Level: {deployment_result['complexity_level']}",
                style="cyan",
            )
        else:
            console.print("❌ Enterprise Architecture deployment failed!", style="bold red")
            console.print(f"Error: {deployment_result.get('error', 'Unknown error')}", style="red")

    except Exception as e:
        console.print(f"❌ Deployment failed: {e!s}", style="bold red")
        logger.error(f"Architecture deployment failed: {e}")
    finally:
        with contextlib.suppress(Exception):
            architecture_module.cleanup_resources()


@enterprise_cli.group(name="cloud")
def cloud_group() -> None:
    """Cloud Integration commands (Phase 10.2)."""
    pass


@cloud_group.command(name="validate-env")
def validate_cloud_env() -> None:
    """Validate cloud integration environment variables."""
    try:
        console.print("☁️ Phase 10.2: Cloud Integration Environment Validation", style="bold blue")

        # Initialize module
        cloud_module = CloudIntegrationModule()

        # Get validation results
        validation_results = cloud_module.validate_environment()

        # Display overall status
        if validation_results["overall_valid"]:
            console.print(
                "✅ Cloud Integration environment validation passed!",
                style="bold green",
            )
        else:
            console.print("❌ Cloud Integration environment validation failed!", style="bold red")

    except Exception as e:
        console.print(f"❌ Validation failed: {e!s}", style="bold red")
        logger.error(f"Cloud environment validation failed: {e}")


@cloud_group.command(name="deploy")
@click.option(
    "--complexity",
    default="basic",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def deploy_cloud(complexity: str) -> None:
    """Deploy cloud infrastructure with progressive complexity."""
    try:
        console.print(
            f"☁️ Phase 10.2: Deploying Cloud Infrastructure ({complexity} complexity)",
            style="bold blue",
        )

        # Initialize module
        cloud_module = CloudIntegrationModule()

        # Perform deployment
        deployment_result = cloud_module.deploy_cloud_infrastructure(complexity)

        # Display results
        if deployment_result["success"]:
            console.print(
                "✅ Cloud Infrastructure deployment completed successfully!",
                style="bold green",
            )
            console.print(
                f"Complexity Level: {deployment_result['complexity_level']}",
                style="cyan",
            )
        else:
            console.print("❌ Cloud Infrastructure deployment failed!", style="bold red")
            console.print(f"Error: {deployment_result.get('error', 'Unknown error')}", style="red")

    except Exception as e:
        console.print(f"❌ Deployment failed: {e!s}", style="bold red")
        logger.error(f"Cloud deployment failed: {e}")


@enterprise_cli.group(name="analytics")
def analytics_group() -> None:
    """Advanced Analytics Platform commands (Phase 10.3)."""
    pass


@analytics_group.command(name="validate-env")
def validate_analytics_env() -> None:
    """Validate analytics platform environment variables."""
    try:
        console.print(
            "📊 Phase 10.3: Advanced Analytics Platform Environment Validation",
            style="bold blue",
        )

        # Initialize module
        analytics_module = AdvancedAnalyticsPlatformModule()

        # Get validation results
        validation_results = analytics_module.validate_environment()

        # Display overall status
        if validation_results["overall_valid"]:
            console.print(
                "✅ Analytics Platform environment validation passed!",
                style="bold green",
            )
        else:
            console.print("❌ Analytics Platform environment validation failed!", style="bold red")

    except Exception as e:
        console.print(f"❌ Validation failed: {e!s}", style="bold red")
        logger.error(f"Analytics environment validation failed: {e}")


@analytics_group.command(name="deploy")
@click.option(
    "--complexity",
    default="basic",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def deploy_analytics(complexity: str) -> None:
    """Deploy analytics platform with progressive complexity."""
    try:
        console.print(
            f"📊 Phase 10.3: Deploying Advanced Analytics Platform ({complexity} complexity)",
            style="bold blue",
        )

        # Initialize module
        analytics_module = AdvancedAnalyticsPlatformModule()

        # Perform deployment
        deployment_result = analytics_module.deploy_analytics_platform(complexity)

        # Display results
        if deployment_result["success"]:
            console.print(
                "✅ Analytics Platform deployment completed successfully!",
                style="bold green",
            )
            console.print(
                f"Complexity Level: {deployment_result['complexity_level']}",
                style="cyan",
            )
        else:
            console.print("❌ Analytics Platform deployment failed!", style="bold red")
            console.print(f"Error: {deployment_result.get('error', 'Unknown error')}", style="red")

    except Exception as e:
        console.print(f"❌ Deployment failed: {e!s}", style="bold red")
        logger.error(f"Analytics deployment failed: {e}")


@enterprise_cli.command(name="test-all")
@click.option(
    "--complexity",
    default="basic",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Test complexity level",
)
def test_all_components(complexity: str) -> Any:
    """Test all enterprise components comprehensively."""
    try:
        console.print(
            f"🧪 Phase 10: Comprehensive Enterprise Testing ({complexity} complexity)",
            style="bold blue",
        )

        test_results = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Testing enterprise components...", total=100)

            # Test 1: Enterprise Architecture (33%)
            progress.update(task, advance=33, description="Testing Enterprise Architecture...")
            try:
                architecture_module = EnterpriseArchitectureModule()
                arch_validation = architecture_module.env_validation
                test_results["enterprise_architecture"] = {
                    "environment_validation": arch_validation,
                    "status": ("passed" if arch_validation["overall_valid"] else "failed"),
                }
                architecture_module.cleanup_resources()
            except Exception as e:
                test_results["enterprise_architecture"] = {
                    "status": "failed",
                    "error": str(e),
                }

            # Test 2: Cloud Integration (33%)
            progress.update(task, advance=33, description="Testing Cloud Integration...")
            try:
                cloud_module = CloudIntegrationModule()
                cloud_validation = cloud_module.validate_environment()
                test_results["cloud_integration"] = {
                    "environment_validation": cloud_validation,
                    "status": ("passed" if cloud_validation["overall_valid"] else "failed"),
                }
                cloud_module.cleanup_resources()
            except Exception as e:
                test_results["cloud_integration"] = {
                    "status": "failed",
                    "error": str(e),
                }

            # Test 3: Advanced Analytics Platform (34%)
            progress.update(task, advance=34, description="Testing Advanced Analytics Platform...")
            try:
                analytics_module = AdvancedAnalyticsPlatformModule()
                analytics_validation = analytics_module.validate_environment()
                test_results["advanced_analytics"] = {
                    "environment_validation": analytics_validation,
                    "status": ("passed" if analytics_validation["overall_valid"] else "failed"),
                }
            except Exception as e:
                test_results["advanced_analytics"] = {
                    "status": "failed",
                    "error": str(e),
                }

            progress.update(task, completed=100, description="Testing completed!")

        # Calculate overall results
        passed_tests = sum(1 for result in test_results.values() if result["status"] == "passed")
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100

        # Display results
        console.print("\n📊 Test Results Summary:", style="bold blue")

        results_table = Table(title="Phase 10 Enterprise Testing Results")
        results_table.add_column("Component", style="cyan")
        results_table.add_column("Status", style="bold")
        results_table.add_column("Details", style="white")

        for component, result in test_results.items():
            status = "✅ PASSED" if result["status"] == "passed" else "❌ FAILED"
            details = (
                result.get("error", "All tests passed")
                if result["status"] == "failed"
                else "All validations successful"
            )
            results_table.add_row(component.replace("_", " ").title(), status, details)

        # Add overall status
        overall_status = "✅ ALL PASSED" if success_rate == 100 else f"⚠️ {passed_tests}/{total_tests} PASSED"
        results_table.add_row("Overall Status", overall_status, f"Success Rate: {success_rate:.1f}%")

        console.print(results_table)

        # Final status message
        if success_rate == 100:
            console.print("🎉 All enterprise components tested successfully!", style="bold green")
        else:
            console.print(
                f"⚠️ {passed_tests}/{total_tests} components passed testing",
                style="bold yellow",
            )

    except Exception as e:
        console.print(f"❌ Testing failed: {e!s}", style="bold red")
        logger.error(f"Enterprise testing failed: {e}")


# Export the CLI group
def get_enterprise_cli() -> Any:
    """Get the enterprise CLI group for integration with main CLI."""
    return enterprise_cli


if __name__ == "__main__":
    enterprise_cli()
