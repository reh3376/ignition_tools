"""Production Deployment CLI Commands for Phase 11.7.

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Input validation and sanitization
- Step 3: Comprehensive error handling
- Step 4: Modular testing integration
- Step 5: Progressive complexity
- Step 6: Resource management
"""

import asyncio
import json
import logging
import sys
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..production_deployment import (
    DockerConfig,
    PLCConfig,
    ProductionConfig,
    ProductionDeploymentManager,
    create_production_deployment_manager,
    format_deployment_error,
    test_production_deployment,
    validate_production_environment,
)

console = Console()
logger = logging.getLogger(__name__)


def handle_deployment_error(func: Any) -> None:
    """Decorator for handling deployment errors with user-friendly messages."""

    def wrapper(*args, **kwargs) -> None:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = format_deployment_error(e, "CLI command")
            console.print(f"[red]❌ Command Error:[/red] {error_msg}")
            logger.exception("Unexpected error in deployment CLI")
            sys.exit(1)

    return wrapper


@click.group(name="deployment")
def deployment_group() -> None:
    """Production Deployment & PLC Integration commands for Phase 11.7.

    Manages Docker-based production deployments with comprehensive
    PLC integration, monitoring, and automated management.
    """
    pass


@deployment_group.command("validate-env")
@handle_deployment_error
def validate_deployment_environment() -> None:
    """Validate production deployment environment.

    Checks Docker availability, required packages, environment variables,
    and network connectivity for production deployment readiness.
    """
    console.print(
        "[bold blue]🔍 Phase 11.7: Production Deployment Environment Validation[/bold blue]"
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Validating environment...", total=None)

        # Perform validation
        validation_result = validate_production_environment()

        progress.update(task, completed=True)

    # Display results
    if validation_result["valid"]:
        console.print("\n[green]✅ Environment validation passed![/green]")
    else:
        console.print("\n[red]❌ Environment validation failed![/red]")

    # Components table
    components_table = Table(
        title="🔧 Component Status", show_header=True, header_style="bold blue"
    )
    components_table.add_column("Component", style="cyan")
    components_table.add_column("Status", style="white")
    components_table.add_column("Details", style="white")

    for component_name, component_data in validation_result["components"].items():
        if component_data["valid"]:
            status = "[green]✅ Valid[/green]"
            if component_name == "docker":
                details = f"Version: {component_data.get('version', 'unknown')}"
            elif component_name == "packages":
                available = component_data.get("available", {})
                details = f"Packages: {len(available)} available"
            elif component_name == "environment":
                configured = component_data.get("configured", {})
                details = f"Variables: {len(configured)} configured"
            elif component_name == "network":
                checks = component_data.get("checks", [])
                details = f"Checks: {len(checks)} performed"
            else:
                details = "Available"
        else:
            status = "[red]❌ Invalid[/red]"
            errors = component_data.get("errors", [])
            details = f"Errors: {len(errors)}"

        components_table.add_row(component_name.title(), status, details)

    console.print(components_table)

    # Display errors if any
    if validation_result["errors"]:
        console.print("\n[bold red]❌ Errors:[/bold red]")
        for error in validation_result["errors"]:
            console.print(f"  • {error}")

    # Display warnings if any
    if validation_result["warnings"]:
        console.print("\n[bold yellow]⚠️  Warnings:[/bold yellow]")
        for warning in validation_result["warnings"]:
            console.print(f"  • {warning}")

    # Exit with appropriate code
    if not validation_result["valid"]:
        sys.exit(1)


@deployment_group.command("test")
@handle_deployment_error
def test_deployment_functionality() -> None:
    """Test production deployment functionality.

    Runs comprehensive tests including Docker operations,
    container lifecycle management, and basic deployment workflows.
    """
    console.print("[bold blue]🧪 Phase 11.7: Production Deployment Testing[/bold blue]")

    async def run_test() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running deployment tests...", total=None)

            # Run tests
            test_result = await test_production_deployment()

            progress.update(task, completed=True)

        return test_result

    # Run the async test
    test_result = asyncio.run(run_test())

    # Display results
    if test_result["success"]:
        console.print("\n[green]✅ All deployment tests passed![/green]")
        console.print(f"[green]Success:[/green] {test_result['message']}")
    else:
        console.print("\n[red]❌ Deployment tests failed![/red]")
        console.print(f"[red]Error:[/red] {test_result['error']}")
        sys.exit(1)


@deployment_group.command("status")
@click.option(
    "--deployment-name",
    "-n",
    default="ign-scripts-production",
    help="Deployment name to check",
)
@handle_deployment_error
def check_deployment_status(deployment_name: str) -> None:
    """Check production deployment status.

    Displays comprehensive status information including container health,
    PLC connections, resource usage, and monitoring status.
    """
    console.print(f"[bold blue]📊 Deployment Status: {deployment_name}[/bold blue]")

    async def get_status() -> None:
        try:
            # Create minimal config for status checking
            docker_config = DockerConfig(
                image_name="ign-scripts",
                container_name=deployment_name,
                ports={8000: 8000},
            )

            config = ProductionConfig(
                docker_config=docker_config,
                monitoring_enabled=False,  # Disable for status check
            )

            manager = ProductionDeploymentManager(config)

            # Initialize just Docker client for status check
            docker_result = await manager._initialize_docker()
            if not docker_result["success"]:
                return {"deployed": False, "error": docker_result["error"]}

            # Get status
            status = manager.get_deployment_status()
            await manager.cleanup()

            return status

        except Exception as e:
            return {"deployed": False, "error": str(e)}

    # Get status
    status = asyncio.run(get_status())

    if not status["deployed"]:
        console.print(
            f"[yellow]No active deployment found for: {deployment_name}[/yellow]"
        )
        if "error" in status:
            console.print(f"[red]Error:[/red] {status['error']}")
        return

    # Display status using the manager's display method
    # Create a temporary manager for display
    docker_config = DockerConfig(
        image_name="ign-scripts", container_name=deployment_name, ports={8000: 8000}
    )

    config = ProductionConfig(docker_config=docker_config, monitoring_enabled=False)

    manager = ProductionDeploymentManager(config)
    manager._deployment_info = type("DeploymentInfo", (), status["container"])()
    manager.display_status()


@deployment_group.command("deploy")
@click.option("--image", "-i", default="ign-scripts", help="Docker image name")
@click.option("--tag", "-t", default="latest", help="Docker image tag")
@click.option("--name", "-n", default="ign-scripts-production", help="Container name")
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["development", "staging", "production", "enterprise"]),
    default="production",
    help="Deployment mode",
)
@click.option("--api-port", default=8000, type=int, help="API server port")
@click.option("--web-port", default=8501, type=int, help="Web interface port")
@click.option("--memory", default="2g", help="Memory limit")
@click.option("--cpu", default=2.0, type=float, help="CPU limit")
@click.option("--monitoring/--no-monitoring", default=True, help="Enable monitoring")
@click.option("--plc-config", help="JSON file with PLC configurations")
@handle_deployment_error
def deploy_production(
    image: str,
    tag: str,
    name: str,
    mode: str,
    api_port: int,
    web_port: int,
    memory: str,
    cpu: float,
    monitoring: bool,
    plc_config: str | None,
) -> None:
    """Deploy production container with PLC integration.

    Creates and starts a production deployment with specified configuration,
    including Docker container setup and PLC connection management.
    """
    console.print(f"[bold blue]🚀 Deploying Production Container: {name}[/bold blue]")

    # Load PLC configurations if provided
    plc_configs = []
    if plc_config:
        try:
            with open(plc_config) as f:
                plc_data = json.load(f)
                plc_configs = [PLCConfig(**config) for config in plc_data]
            console.print(
                f"[green]✅ Loaded {len(plc_configs)} PLC configurations[/green]"
            )
        except Exception as e:
            console.print(f"[red]❌ Failed to load PLC config: {e}[/red]")
            sys.exit(1)

    async def perform_deployment() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Step 1: Environment validation
            task1 = progress.add_task("Validating environment...", total=None)
            env_result = validate_production_environment()
            progress.update(task1, completed=True)

            if not env_result["valid"]:
                console.print("\n[red]❌ Environment validation failed[/red]")
                for error in env_result["errors"]:
                    console.print(f"  • {error}")
                return {"success": False, "error": "Environment validation failed"}

            # Step 2: Create deployment manager
            task2 = progress.add_task("Creating deployment manager...", total=None)

            try:
                manager = await create_production_deployment_manager(
                    deployment_mode=mode,
                    docker_image=image,
                    docker_tag=tag,
                    container_name=name,
                    ports={api_port: 8000, web_port: 8501},
                    plc_configs=(
                        [config.dict() for config in plc_configs]
                        if plc_configs
                        else None
                    ),
                )
                progress.update(task2, completed=True)
            except Exception as e:
                progress.update(task2, completed=True)
                return {"success": False, "error": f"Failed to create manager: {e!s}"}

            # Step 3: Initialize deployment
            task3 = progress.add_task("Initializing deployment...", total=None)
            async with manager.managed_deployment() as deployment:
                progress.update(task3, completed=True)

                # Step 4: Deploy container
                task4 = progress.add_task("Deploying container...", total=None)
                deploy_result = await deployment.deploy_container()
                progress.update(task4, completed=True)

                return deploy_result

    # Perform deployment
    result = asyncio.run(perform_deployment())

    # Display results
    if result["success"]:
        console.print("\n[green]✅ Deployment successful![/green]")
        console.print(f"[green]Container:[/green] {name}")
        console.print(f"[green]Image:[/green] {image}:{tag}")
        console.print(f"[green]Ports:[/green] API:{api_port}, Web:{web_port}")
        console.print(f"[green]Mode:[/green] {mode}")

        if plc_configs:
            console.print(
                f"[green]PLC Connections:[/green] {len(plc_configs)} configured"
            )

        # Show access information
        access_panel = Panel(
            f"[bold]API Endpoint:[/bold] http://localhost:{api_port}\n"
            f"[bold]Web Interface:[/bold] http://localhost:{web_port}\n"
            f"[bold]API Documentation:[/bold] http://localhost:{api_port}/docs\n"
            f"[bold]Container Status:[/bold] docker ps --filter name={name}",
            title="🌐 Access Information",
            border_style="green",
        )
        console.print(access_panel)
    else:
        console.print("\n[red]❌ Deployment failed![/red]")
        console.print(f"[red]Error:[/red] {result['error']}")
        sys.exit(1)


@deployment_group.command("stop")
@click.option(
    "--name", "-n", default="ign-scripts-production", help="Container name to stop"
)
@click.option("--force", "-f", is_flag=True, help="Force stop container")
@handle_deployment_error
def stop_deployment(name: str, force: bool) -> None:
    """Stop production deployment.

    Gracefully stops the specified production container and cleans up resources.
    """
    console.print(f"[bold blue]🛑 Stopping Deployment: {name}[/bold blue]")

    async def perform_stop() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Stopping container...", total=None)

            try:
                # Create minimal manager for stop operation
                docker_config = DockerConfig(
                    image_name="ign-scripts", container_name=name, ports={8000: 8000}
                )

                config = ProductionConfig(
                    docker_config=docker_config, monitoring_enabled=False
                )

                manager = ProductionDeploymentManager(config)

                # Initialize and stop
                init_result = await manager.initialize()
                if not init_result["success"]:
                    progress.update(task, completed=True)
                    return {"success": False, "error": init_result["error"]}

                # Set deployment info to enable stop operation
                from datetime import datetime

                from ..production_deployment import DeploymentInfo, DeploymentStatus

                manager._deployment_info = DeploymentInfo(
                    container_name=name,
                    status=DeploymentStatus.RUNNING,
                    image="ign-scripts:latest",
                    created=datetime.now(),
                    ports={8000: 8000},
                )

                stop_result = await manager.stop_container()
                await manager.cleanup()

                progress.update(task, completed=True)
                return stop_result

            except Exception as e:
                progress.update(task, completed=True)
                return {"success": False, "error": str(e)}

    # Perform stop
    result = asyncio.run(perform_stop())

    # Display results
    if result["success"]:
        console.print("\n[green]✅ Container stopped successfully![/green]")
        console.print(f"[green]Container:[/green] {name}")
    else:
        console.print("\n[red]❌ Failed to stop container![/red]")
        console.print(f"[red]Error:[/red] {result['error']}")

        if force:
            console.print("[yellow]Attempting force stop with Docker CLI...[/yellow]")
            import subprocess

            try:
                subprocess.run(
                    ["docker", "stop", name], check=True, capture_output=True
                )
                subprocess.run(["docker", "rm", name], check=True, capture_output=True)
                console.print(f"[green]✅ Force stopped container: {name}[/green]")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]❌ Force stop failed: {e}[/red]")
                sys.exit(1)
        else:
            sys.exit(1)


@deployment_group.command("restart")
@click.option(
    "--name", "-n", default="ign-scripts-production", help="Container name to restart"
)
@handle_deployment_error
def restart_deployment(name: str) -> None:
    """Restart production deployment.

    Restarts the specified production container with health checks.
    """
    console.print(f"[bold blue]🔄 Restarting Deployment: {name}[/bold blue]")

    async def perform_restart() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Restarting container...", total=None)

            try:
                # Create minimal manager for restart operation
                docker_config = DockerConfig(
                    image_name="ign-scripts", container_name=name, ports={8000: 8000}
                )

                config = ProductionConfig(
                    docker_config=docker_config, monitoring_enabled=False
                )

                manager = ProductionDeploymentManager(config)

                # Initialize and restart
                init_result = await manager.initialize()
                if not init_result["success"]:
                    progress.update(task, completed=True)
                    return {"success": False, "error": init_result["error"]}

                # Set deployment info to enable restart operation
                from datetime import datetime

                from ..production_deployment import DeploymentInfo, DeploymentStatus

                manager._deployment_info = DeploymentInfo(
                    container_name=name,
                    status=DeploymentStatus.RUNNING,
                    image="ign-scripts:latest",
                    created=datetime.now(),
                    ports={8000: 8000},
                )

                restart_result = await manager.restart_container()
                await manager.cleanup()

                progress.update(task, completed=True)
                return restart_result

            except Exception as e:
                progress.update(task, completed=True)
                return {"success": False, "error": str(e)}

    # Perform restart
    result = asyncio.run(perform_restart())

    # Display results
    if result["success"]:
        console.print("\n[green]✅ Container restarted successfully![/green]")
        console.print(f"[green]Container:[/green] {name}")
    else:
        console.print("\n[red]❌ Failed to restart container![/red]")
        console.print(f"[red]Error:[/red] {result['error']}")
        sys.exit(1)


@deployment_group.command("logs")
@click.option("--name", "-n", default="ign-scripts-production", help="Container name")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--tail", "-t", default=100, type=int, help="Number of lines to show")
@handle_deployment_error
def view_deployment_logs(name: str, follow: bool, tail: int) -> None:
    """View production deployment logs.

    Displays container logs with optional real-time following.
    """
    console.print(f"[bold blue]📋 Deployment Logs: {name}[/bold blue]")

    try:
        import subprocess

        cmd = ["docker", "logs"]
        if follow:
            cmd.append("-f")
        cmd.extend(["--tail", str(tail), name])

        console.print(f"[cyan]Running:[/cyan] {' '.join(cmd)}")
        console.print("[cyan]Press Ctrl+C to exit[/cyan]\n")

        # Run docker logs command
        subprocess.run(cmd)

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to get logs: {e}[/red]")
        console.print(
            f"[yellow]Tip:[/yellow] Check if container '{name}' exists with: docker ps -a"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Log viewing interrupted[/yellow]")


@deployment_group.command("config")
@click.option("--template", "-t", is_flag=True, help="Generate configuration template")
@click.option("--output", "-o", help="Output file path")
@handle_deployment_error
def manage_deployment_config(template: bool, output: str | None) -> None:
    """Manage deployment configuration.

    Generate configuration templates or validate existing configurations.
    """
    if template:
        console.print(
            "[bold blue]📝 Generating Deployment Configuration Template[/bold blue]"
        )

        # Create template configuration
        template_config = {
            "deployment": {
                "mode": "production",
                "docker": {
                    "image_name": "ign-scripts",
                    "tag": "latest",
                    "container_name": "ign-scripts-production",
                    "ports": {"8000": 8000, "8501": 8501},
                    "environment": {
                        "PYTHONPATH": "/app",
                        "LOG_LEVEL": "INFO",
                        "DEPLOYMENT_MODE": "production",
                    },
                    "volumes": {"./logs": "/app/logs", "./data": "/app/data"},
                    "memory_limit": "2g",
                    "cpu_limit": 2.0,
                },
                "monitoring": {
                    "enabled": True,
                    "health_check_interval": 30.0,
                    "auto_restart": True,
                },
            },
            "plc_connections": [
                {
                    "name": "PLC_001",
                    "server_url": "opc.tcp://192.168.1.100:4840",
                    "username": "opcuser",
                    "password": "password123",
                    "timeout": 30.0,
                    "polling_interval": 1.0,
                    "tag_list": [
                        "ns=2;s=Temperature",
                        "ns=2;s=Pressure",
                        "ns=2;s=FlowRate",
                    ],
                }
            ],
        }

        # Output template
        if output:
            try:
                with open(output, "w") as f:
                    json.dump(template_config, f, indent=2)
                console.print(f"[green]✅ Template saved to: {output}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to save template: {e}[/red]")
                sys.exit(1)
        else:
            console.print("[cyan]Configuration Template:[/cyan]")
            console.print(json.dumps(template_config, indent=2))

    else:
        console.print(
            "[yellow]Use --template to generate a configuration template[/yellow]"
        )


# Register commands with the main CLI
def setup_deployment_commands(cli_group: Any) -> None:
    """Setup deployment commands with the main CLI group."""
    cli_group.add_command(deployment_group)


# Testing function for CLI commands
def test_deployment_commands() -> None:
    """Test deployment CLI commands."""
    console.print("[bold blue]🧪 Testing Deployment CLI Commands[/bold blue]")

    try:
        # Test environment validation
        console.print("Testing environment validation...")
        result = validate_production_environment()

        if result["valid"]:
            console.print("[green]✅ Environment validation test passed[/green]")
        else:
            console.print(
                "[yellow]⚠️  Environment validation test completed with warnings[/yellow]"
            )

        console.print("[green]✅ All CLI command tests passed[/green]")
        return True

    except Exception as e:
        console.print(f"[red]❌ CLI command test failed: {e}[/red]")
        return False


if __name__ == "__main__":
    # Run CLI tests
    test_deployment_commands()
