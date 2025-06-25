"""SME Agent Core CLI Commands - Basic Operations

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup
"""

import logging
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..sme_agent_module import SMEAgentModule, SMEAgentValidationError

console = Console()
logger = logging.getLogger(__name__)


def handle_sme_agent_error(func: Any) -> Any:
    """Decorator for handling SME Agent errors with user-friendly messages."""

    def wrapper(*args, **kwargs) -> Any:
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


@click.group(name="core")
def core_commands() -> None:
    """SME Agent Core Commands - Basic Operations"""
    pass


@core_commands.command("validate-env")
@handle_sme_agent_error
def validate_environment() -> None:
    """Step 1: Environment Validation First

    Validate SME Agent environment and dependencies.
    """
    console.print("[bold blue]🔍 SME Agent Environment Validation[/bold blue]")
    console.print(
        "Following crawl_mcp.py methodology - Step 1: Environment Validation First"
    )

    try:
        # Create temporary SME Agent instance for validation
        with SMEAgentModule() as agent:
            validation_result = agent.validate_environment()

            # Display validation results
            if validation_result["valid"]:
                console.print("[green]✅ Environment validation successful![/green]")
            else:
                console.print("[red]❌ Environment validation failed![/red]")

            # Show detailed results
            _display_validation_results(validation_result)

    except Exception as e:
        console.print(f"[red]❌ Environment validation failed: {e}[/red]")
        sys.exit(1)


@core_commands.command("status")
@handle_sme_agent_error
def get_status() -> None:
    """Step 4: Modular Component Testing

    Get current status of SME Agent components.
    """
    console.print("[bold blue]📊 SME Agent Status[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            status = agent.get_status()
            _display_status(status)

    except Exception as e:
        console.print(f"[red]❌ Failed to get status: {e}[/red]")
        sys.exit(1)


@core_commands.command("initialize")
@click.option(
    "--complexity",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="basic",
    help="Complexity level for initialization",
)
@handle_sme_agent_error
def initialize_components(complexity: str) -> None:
    """Step 5: Progressive Complexity Support

    Initialize SME Agent components with specified complexity level.
    """
    console.print(
        f"[bold blue]🚀 SME Agent Initialization - {complexity.title()} Level[/bold blue]"
    )
    console.print(
        "Following crawl_mcp.py methodology - Step 5: Progressive Complexity Support"
    )

    try:
        with SMEAgentModule() as agent:
            result = agent.initialize_components(complexity_level=complexity)
            _display_initialization_results(result)

    except Exception as e:
        console.print(f"[red]❌ Initialization failed: {e}[/red]")
        sys.exit(1)


@core_commands.command("ask")
@click.argument("question", required=True)
@click.option("--context", help="Optional context for the question")
@click.option(
    "--complexity",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="basic",
)
@handle_sme_agent_error
def ask_question(question: str, context: str | None, complexity: str) -> None:
    """Step 2: Comprehensive Input Validation
    Step 3: Error Handling and User-Friendly Messages

    Ask a question to the SME Agent.
    """
    console.print("[bold blue]💬 SME Agent Question Processing[/bold blue]")
    console.print(f"Question: [italic]{question}[/italic]")
    if context:
        console.print(f"Context: [italic]{context}[/italic]")

    try:
        with SMEAgentModule() as agent:
            # Initialize with specified complexity
            init_result = agent.initialize_components(complexity_level=complexity)
            if not init_result["success"]:
                console.print("[red]❌ Failed to initialize SME Agent[/red]")
                return

            # Process question
            response = agent.ask_question(question, context)
            _display_response(response)

    except Exception as e:
        console.print(f"[red]❌ Question processing failed: {e}[/red]")
        sys.exit(1)


@core_commands.command("analyze")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--complexity",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="standard",
)
@handle_sme_agent_error
def analyze_file(file_path: str, complexity: str) -> None:
    """Analyze a file using SME Agent capabilities."""
    console.print("[bold blue]🔍 SME Agent File Analysis[/bold blue]")
    console.print(f"Analyzing: [italic]{file_path}[/italic]")

    try:
        # Read file content
        file_content = Path(file_path).read_text()

        # Create analysis question
        question = "Please analyze this file and provide insights about its structure, purpose, and potential improvements."
        context = f"File: {file_path}\nContent:\n{file_content[:2000]}..."  # Limit context size

        with SMEAgentModule() as agent:
            # Initialize with specified complexity
            init_result = agent.initialize_components(complexity_level=complexity)
            if not init_result["success"]:
                console.print("[red]❌ Failed to initialize SME Agent[/red]")
                return

            # Process analysis
            response = agent.ask_question(question, context)
            _display_response(response)

    except Exception as e:
        console.print(f"[red]❌ File analysis failed: {e}[/red]")
        sys.exit(1)


# Display helper functions
def _display_validation_results(validation_result: dict[str, Any]) -> None:
    """Display environment validation results in a formatted table."""
    table = Table(title="Environment Validation Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")

    for component, details in validation_result.get("components", {}).items():
        status = "✅ Valid" if details.get("valid", False) else "❌ Invalid"
        detail_text = details.get("message", "No details available")
        table.add_row(component, status, detail_text)

    console.print(table)


def _display_status(status: dict[str, Any]) -> None:
    """Display SME Agent status in a formatted panel."""
    status_text = f"""
**Overall Status**: {status.get("status", "Unknown")}
**Components**: {status.get("component_count", 0)} active
**Last Updated**: {status.get("last_updated", "Unknown")}
**Memory Usage**: {status.get("memory_usage", "Unknown")}
"""
    console.print(Panel(status_text, title="SME Agent Status", border_style="blue"))


def _display_initialization_results(result: dict[str, Any]) -> None:
    """Display initialization results."""
    if result.get("success", False):
        console.print(
            "[green]✅ SME Agent initialization completed successfully![/green]"
        )
        console.print(f"Initialized components: {result.get('component_count', 0)}")
    else:
        console.print("[red]❌ SME Agent initialization failed![/red]")
        console.print(f"Error: {result.get('error', 'Unknown error')}")


def _display_response(response: Any) -> None:
    """Display SME Agent response."""
    if isinstance(response, dict):
        if "answer" in response:
            console.print(
                Panel(
                    response["answer"], title="SME Agent Response", border_style="green"
                )
            )
        if "confidence" in response:
            console.print(f"Confidence: {response['confidence']:.2%}")
    else:
        console.print(
            Panel(str(response), title="SME Agent Response", border_style="green")
        )
