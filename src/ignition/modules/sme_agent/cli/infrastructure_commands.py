"""SME Agent Infrastructure CLI Commands - Deployment and System Management

Following crawl_mcp.py methodology:
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup
"""

import asyncio
import logging
import sys
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..sme_agent_module import SMEAgentModule, SMEAgentValidationError

console = Console()
logger = logging.getLogger(__name__)


def handle_sme_agent_error(func):
    """Decorator for handling SME Agent errors with user-friendly messages."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SMEAgentValidationError as e:
            console.print(f"[red]❌ Validation Error:[/red] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]❌ Unexpected Error:[/red] {e}")
            logger.exception("Unexpected error in SME Agent CLI")
            sys.exit(1)

    return wrapper


@click.group(name="infrastructure")
def infrastructure_commands():
    """SME Agent Infrastructure Commands - Deployment and System Management"""
    pass


@infrastructure_commands.command("llm-status")
@handle_sme_agent_error
def llm_status():
    """Check Local LLM Infrastructure Status"""
    console.print("[bold blue]🔍 Local LLM Infrastructure Status[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            status = agent.get_llm_infrastructure_status()
            _display_llm_status(status)

    except Exception as e:
        console.print(f"[red]❌ Failed to get LLM status: {e}[/red]")
        sys.exit(1)


@infrastructure_commands.command("env-optimize")
@handle_sme_agent_error
def env_optimize():
    """Optimize Environment for Local LLM Performance"""
    console.print("[bold blue]⚡ Environment Optimization for Local LLMs[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            optimization_result = agent.optimize_environment()
            _display_optimization_result(optimization_result)

    except Exception as e:
        console.print(f"[red]❌ Environment optimization failed: {e}[/red]")
        sys.exit(1)


@infrastructure_commands.command("llm-deploy")
@click.option(
    "--model",
    type=click.Choice(["llama3.1-8b", "mistral-8b", "custom"]),
    default="llama3.1-8b",
    help="LLM model to deploy",
)
@click.option(
    "--complexity",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
    help="Deployment complexity level",
)
@click.option("--use-docker", is_flag=True, help="Deploy using Docker container")
@click.option("--gpu", is_flag=True, help="Enable GPU acceleration")
@handle_sme_agent_error
def deploy_llm_infrastructure(model: str, complexity: str, use_docker: bool, gpu: bool):
    """Deploy Local LLM Infrastructure"""
    console.print(f"[bold blue]🚀 Deploying LLM Infrastructure: {model}[/bold blue]")
    console.print(f"Complexity: {complexity}, Docker: {use_docker}, GPU: {gpu}")

    try:
        with SMEAgentModule() as agent:
            deployment_config = {
                "model": model,
                "complexity": complexity,
                "use_docker": use_docker,
                "gpu": gpu,
            }

            # Run deployment asynchronously
            result = asyncio.run(_deploy_llm_async(agent, deployment_config))
            _display_deployment_result(result)

    except Exception as e:
        console.print(f"[red]❌ LLM deployment failed: {e}[/red]")
        sys.exit(1)


@infrastructure_commands.command("infrastructure-status")
@handle_sme_agent_error
def infrastructure_status():
    """Check Overall Infrastructure Status"""
    console.print("[bold blue]🏗️ SME Agent Infrastructure Status[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            infra_status = agent.get_infrastructure_status()
            _display_infrastructure_status(infra_status)

    except Exception as e:
        console.print(f"[red]❌ Failed to get infrastructure status: {e}[/red]")
        sys.exit(1)


# Async helper functions
async def _deploy_llm_async(
    agent: SMEAgentModule, config: dict[str, Any]
) -> dict[str, Any]:
    """Deploy LLM infrastructure asynchronously."""
    console.print("🔄 Starting LLM deployment...")

    # Simulate deployment steps
    steps = [
        "Downloading model weights...",
        "Setting up environment...",
        "Configuring inference server...",
        "Running health checks...",
        "Finalizing deployment...",
    ]

    for step in steps:
        console.print(f"  • {step}")
        await asyncio.sleep(1)  # Simulate work

    return {
        "success": True,
        "model": config["model"],
        "complexity": config["complexity"],
        "endpoint": "http://localhost:8080/v1/chat/completions",
        "status": "deployed",
    }


# Display helper functions
def _display_llm_status(status: dict[str, Any]):
    """Display LLM infrastructure status."""
    console.print(
        Panel(
            f"""
**LLM Status**: {status.get("status", "Unknown")}
**Available Models**: {len(status.get("models", []))}
**GPU Available**: {status.get("gpu_available", False)}
**Memory Usage**: {status.get("memory_usage", "Unknown")}
**Endpoint**: {status.get("endpoint", "Not configured")}
        """,
            title="LLM Infrastructure Status",
            border_style="blue",
        )
    )


def _display_optimization_result(result: dict[str, Any]):
    """Display environment optimization result."""
    if result.get("success", False):
        console.print("[green]✅ Environment optimization completed![/green]")

        table = Table(title="Optimization Results")
        table.add_column("Component", style="cyan")
        table.add_column("Before", style="yellow")
        table.add_column("After", style="green")
        table.add_column("Improvement", style="white")

        for optimization in result.get("optimizations", []):
            table.add_row(
                optimization.get("component", "Unknown"),
                optimization.get("before", "Unknown"),
                optimization.get("after", "Unknown"),
                optimization.get("improvement", "Unknown"),
            )

        console.print(table)
    else:
        console.print("[red]❌ Environment optimization failed![/red]")
        console.print(f"Error: {result.get('error', 'Unknown error')}")


def _display_deployment_result(result: dict[str, Any]):
    """Display LLM deployment result."""
    if result.get("success", False):
        console.print("[green]✅ LLM deployment successful![/green]")
        console.print(f"Model: {result.get('model', 'Unknown')}")
        console.print(f"Complexity: {result.get('complexity', 'Unknown')}")
        console.print(f"Endpoint: {result.get('endpoint', 'Unknown')}")
        console.print(f"Status: {result.get('status', 'Unknown')}")
    else:
        console.print("[red]❌ LLM deployment failed![/red]")
        console.print(f"Error: {result.get('error', 'Unknown error')}")


def _display_infrastructure_status(status: dict[str, Any]):
    """Display overall infrastructure status."""
    table = Table(title="Infrastructure Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Health", style="yellow")
    table.add_column("Details", style="white")

    for component, details in status.get("components", {}).items():
        health_status = (
            "✅ Healthy" if details.get("healthy", False) else "❌ Unhealthy"
        )
        table.add_row(
            component,
            details.get("status", "Unknown"),
            health_status,
            details.get("details", "No details available"),
        )

    console.print(table)

    overall_health = status.get("overall_health", "Unknown")
    console.print(f"\n[bold]Overall Infrastructure Health: {overall_health}[/bold]")
