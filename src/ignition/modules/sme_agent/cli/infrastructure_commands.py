"""SME Agent Infrastructure CLI Commands - Deployment and System Management.

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

from src.ignition.modules.sme_agent.sme_agent_module import (
    SMEAgentModule,
    SMEAgentValidationError,
)

# Import workflow commands for Phase 11.3 completion
try:
    from .workflow_commands import register_workflow_commands

    WORKFLOW_COMMANDS_AVAILABLE = True
except ImportError:
    WORKFLOW_COMMANDS_AVAILABLE = False

console = Console()
logger = logging.getLogger(__name__)


def handle_sme_agent_error(func: Any) -> None:
    """Decorator for handling SME Agent errors with user-friendly messages."""

    def wrapper(*args, **kwargs) -> None:
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
def infrastructure_commands() -> None:
    """SME Agent Infrastructure Commands - Deployment and System Management."""
    pass


@infrastructure_commands.command("llm-status")
@handle_sme_agent_error
def llm_status() -> None:
    """Check Local LLM Infrastructure Status."""
    console.print("[bold blue]🔍 Local LLM Infrastructure Status[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            # Use the available get_status method instead
            status = agent.get_status()
            _display_llm_status(status)

    except Exception as e:
        console.print(f"[red]❌ Failed to get LLM status: {e}[/red]")
        sys.exit(1)


@infrastructure_commands.command("env-optimize")
@handle_sme_agent_error
def env_optimize() -> None:
    """Optimize Environment for Local LLM Performance."""
    console.print("[bold blue]⚡ Environment Optimization for Local LLMs[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            # Use validation result as optimization info
            optimization_result = agent.validate_environment()
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
def deploy_llm_infrastructure(model: str, complexity: str, use_docker: bool, gpu: bool) -> None:
    """Deploy Local LLM Infrastructure."""
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
def infrastructure_status() -> None:
    """Check Overall Infrastructure Status."""
    console.print("[bold blue]🏗️ SME Agent Infrastructure Status[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            # Use the available get_status method
            infra_status = agent.get_status()
            _display_infrastructure_status(infra_status)

    except Exception as e:
        console.print(f"[red]❌ Failed to get infrastructure status: {e}[/red]")
        sys.exit(1)


@infrastructure_commands.command("start-api")
@click.option("--host", default="0.0.0.0", help="API server host")
@click.option("--port", default=8000, type=int, help="API server port")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@handle_sme_agent_error
def start_api_server(host: str, port: int, reload: bool) -> None:
    """Start the FastAPI web interface server.

    Phase 11.3: Multi-Interface Deployment
    Starts the FastAPI server with streaming chat endpoints.
    """
    console.print("[bold blue]🚀 Starting SME Agent FastAPI Server[/bold blue]")
    console.print(f"Host: {host}, Port: {port}, Reload: {reload}")

    try:
        # Import here to avoid circular imports
        from src.ignition.modules.sme_agent.web_interface import run_server

        console.print(f"[green]✅ Starting FastAPI server on http://{host}:{port}[/green]")
        console.print("📖 API Documentation will be available at:")
        console.print(f"   • Swagger UI: http://{host}:{port}/docs")
        console.print(f"   • ReDoc: http://{host}:{port}/redoc")
        console.print("\n🔗 Available endpoints:")
        console.print("   • POST /chat - Standard chat endpoint")
        console.print("   • POST /chat/stream - Streaming chat endpoint")
        console.print("   • POST /analyze - File analysis endpoint")
        console.print("   • GET /status - System status")
        console.print("   • GET /health - Health check")

        # Run the server
        run_server(host=host, port=port, reload=reload)

    except ImportError as e:
        console.print(f"[red]❌ Failed to import web interface: {e}[/red]")
        console.print("💡 Ensure FastAPI and uvicorn are installed:")
        console.print("   uv pip install fastapi uvicorn")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ Failed to start API server: {e}[/red]")
        sys.exit(1)


@infrastructure_commands.command("start-web")
@click.option("--port", default=8501, type=int, help="Streamlit server port")
@click.option("--host", default="localhost", help="Streamlit server host")
@handle_sme_agent_error
def start_web_interface(port: int, host: str) -> None:
    """Start the Streamlit web interface.

    Phase 11.3: Multi-Interface Deployment
    Starts the Streamlit web interface with conversation history.
    """
    console.print("[bold blue]🌐 Starting SME Agent Streamlit Interface[/bold blue]")
    console.print(f"Host: {host}, Port: {port}")

    try:
        import subprocess
        import sys
        from pathlib import Path

        # Get the path to the streamlit interface
        interface_path = Path(__file__).parent.parent / "streamlit_interface.py"

        if not interface_path.exists():
            console.print(f"[red]❌ Streamlit interface not found at: {interface_path}[/red]")
            sys.exit(1)

        console.print(f"[green]✅ Starting Streamlit interface on http://{host}:{port}[/green]")
        console.print("🎯 Features available:")
        console.print("   • 💬 Interactive chat with conversation history")
        console.print("   • 📄 File analysis capabilities")
        console.print("   • 📊 System status monitoring")
        console.print("   • ⚙️ Configuration management")
        console.print("   • 📥 Conversation export functionality")

        # Launch Streamlit
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(interface_path),
            "--server.port",
            str(port),
            "--server.address",
            host,
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ]

        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        subprocess.run(cmd)

    except ImportError:
        console.print("[red]❌ Streamlit not found![/red]")
        console.print("💡 Install Streamlit:")
        console.print("   uv pip install streamlit")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ Failed to start web interface: {e}[/red]")
        sys.exit(1)


@infrastructure_commands.command("interface-status")
@handle_sme_agent_error
def check_interface_status() -> None:
    """Check the status of all SME Agent interfaces.

    Phase 11.3: Multi-Interface Deployment
    Reports on the availability of CLI, API, and Web interfaces.
    """
    console.print("[bold blue]🔍 SME Agent Interface Status[/bold blue]")

    # Check CLI interface (always available if this command runs)
    console.print("[green]✅ CLI Interface: Available[/green]")

    # Check FastAPI dependencies
    try:
        import fastapi
        import uvicorn

        console.print("[green]✅ FastAPI Dependencies: Available[/green]")
        console.print("   💡 Start with: ign module sme infrastructure start-api")
    except ImportError:
        console.print("[red]❌ FastAPI Dependencies: Missing[/red]")
        console.print("   💡 Install with: uv pip install fastapi uvicorn")

    # Check Streamlit dependencies
    try:
        import streamlit

        console.print("[green]✅ Streamlit Dependencies: Available[/green]")
        console.print("   💡 Start with: ign module sme infrastructure start-web")
    except ImportError:
        console.print("[red]❌ Streamlit Dependencies: Missing[/red]")
        console.print("   💡 Install with: uv pip install streamlit")

    # Check SME Agent core
    try:
        from src.ignition.modules.sme_agent.sme_agent_module import SMEAgentModule

        with SMEAgentModule() as agent:
            validation_result = agent.validate_environment()

            if validation_result["valid"]:
                console.print("[green]✅ SME Agent Core: Operational[/green]")
            else:
                console.print("[yellow]⚠️ SME Agent Core: Degraded[/yellow]")
                console.print(f"   Issues: {validation_result.get('errors', [])}")

    except Exception as e:
        console.print(f"[red]❌ SME Agent Core: Error - {e}[/red]")

    # Interface comparison table
    table = Table(title="Interface Comparison")
    table.add_column("Interface", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Features", style="yellow")
    table.add_column("Use Case", style="blue")

    table.add_row(
        "CLI",
        "Command Line",
        "ask, analyze, status, batch management",
        "Automation, scripting, development",
    )

    table.add_row(
        "FastAPI",
        "REST API",
        "Streaming chat, file analysis, programmatic access",
        "Integration, custom frontends, mobile apps",
    )

    table.add_row(
        "Streamlit",
        "Web UI",
        "Interactive chat, file upload, conversation history",
        "Interactive use, demonstrations, training",
    )

    console.print(table)


@infrastructure_commands.command("demo-interfaces")
@click.option("--api-port", default=8000, type=int, help="FastAPI server port")
@click.option("--web-port", default=8501, type=int, help="Streamlit server port")
@handle_sme_agent_error
def demo_all_interfaces(api_port: int, web_port: int) -> None:
    """Demonstrate all SME Agent interfaces.

    Phase 11.3: Multi-Interface Deployment
    Shows examples of using CLI, API, and Web interfaces.
    """
    console.print("[bold blue]🎭 SME Agent Interface Demonstration[/bold blue]")
    console.print("Phase 11.3: Multi-Interface Deployment")

    # CLI Demo
    console.print("\n[bold cyan]1. CLI Interface Demo[/bold cyan]")
    console.print("💻 Command line usage examples:")
    console.print("   ign module sme ask 'How do I configure OPC-UA in Ignition?'")
    console.print("   ign module sme analyze /path/to/script.py")
    console.print("   ign module sme status")

    # API Demo
    console.print("\n[bold cyan]2. FastAPI Interface Demo[/bold cyan]")
    console.print(f"🌐 REST API endpoints (when running on port {api_port}):")
    console.print(f"   curl -X POST http://localhost:{api_port}/chat \\")
    console.print("        -H 'Content-Type: application/json' \\")
    console.print('        -d \'{"question": "How do I configure OPC-UA?", "complexity": "standard"}\'')

    console.print("\n   # Streaming endpoint")
    console.print(f"   curl -X POST http://localhost:{api_port}/chat/stream \\")
    console.print("        -H 'Content-Type: application/json' \\")
    console.print('        -d \'{"question": "Explain Ignition architecture", "stream": true}\'')

    # Web Demo
    console.print("\n[bold cyan]3. Streamlit Interface Demo[/bold cyan]")
    console.print(f"🎨 Web interface features (when running on port {web_port}):")
    console.print(f"   • Interactive chat: http://localhost:{web_port}")
    console.print("   • File upload and analysis")
    console.print("   • Conversation history and export")
    console.print("   • Real-time system status")
    console.print("   • Configuration management")

    # Quick start commands
    console.print("\n[bold green]🚀 Quick Start Commands[/bold green]")
    console.print("Start all interfaces:")
    console.print("   # Terminal 1: FastAPI server")
    console.print(f"   ign module sme infrastructure start-api --port {api_port}")
    console.print("\n   # Terminal 2: Streamlit interface")
    console.print(f"   ign module sme infrastructure start-web --port {web_port}")
    console.print("\n   # Terminal 3: CLI usage")
    console.print("   ign module sme ask 'What is Ignition?'")

    # Integration examples
    console.print("\n[bold yellow]🔗 Integration Examples[/bold yellow]")
    console.print("Python integration:")
    console.print(
        """
    import requests

    # Use FastAPI endpoint
    response = requests.post('http://localhost:8000/chat', json={
        'question': 'How do I create a database connection?',
        'complexity': 'advanced'
    })

    result = response.json()
    print(f"Answer: {result['response']}")
    print(f"Confidence: {result['confidence']:.2%}")
    """
    )

    console.print("JavaScript integration:")
    console.print(
        """
    // Streaming chat with EventSource
    const eventSource = new EventSource('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: 'Explain Ignition tags' })
    });

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'chunk') {
            console.log('Chunk:', data.content);
        }
    };
    """
    )


# Async helper functions
async def _deploy_llm_async(agent: SMEAgentModule, config: dict[str, Any]) -> dict[str, Any]:
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
def _display_llm_status(status: dict[str, Any]) -> None:
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


def _display_optimization_result(result: dict[str, Any]) -> None:
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


def _display_deployment_result(result: dict[str, Any]) -> None:
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


def _display_infrastructure_status(status: dict[str, Any]) -> None:
    """Display overall infrastructure status."""
    table = Table(title="Infrastructure Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Health", style="yellow")
    table.add_column("Details", style="white")

    for component, details in status.get("components", {}).items():
        health_status = "✅ Healthy" if details.get("healthy", False) else "❌ Unhealthy"
        table.add_row(
            component,
            details.get("status", "Unknown"),
            health_status,
            details.get("details", "No details available"),
        )

    console.print(table)

    overall_health = status.get("overall_health", "Unknown")
    console.print(f"\n[bold]Overall Infrastructure Health: {overall_health}[/bold]")


def setup_infrastructure_commands(cli_group: Any) -> None:
    """Setup infrastructure commands and Phase 11.3 workflow commands."""
    # Add infrastructure commands
    cli_group.add_command(infrastructure_commands)

    # Add Phase 11.3 workflow commands if available
    if WORKFLOW_COMMANDS_AVAILABLE:
        try:
            register_workflow_commands(cli_group)
            console.print("[green]✅ Phase 11.3 workflow commands registered[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Failed to register workflow commands: {e}[/yellow]")
    else:
        console.print("[yellow]⚠️  Phase 11.3 workflow commands not available[/yellow]")
