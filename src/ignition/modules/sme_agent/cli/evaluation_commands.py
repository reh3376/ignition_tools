"""SME Agent Evaluation CLI Commands - Testing and Batch Management.

Following crawl_mcp.py methodology:
- Step 4: Modular component testing
- Step 6: Resource management and cleanup
"""

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


@click.group(name="evaluation")
def evaluation_commands() -> None:
    """SME Agent Evaluation Commands - Testing and Batch Management."""
    pass


@evaluation_commands.command("test-all")
@handle_sme_agent_error
def test_all_components() -> None:
    """Step 4: Modular Component Testing.

    Run comprehensive tests on all SME Agent components.
    """
    console.print("[bold blue]🧪 SME Agent Comprehensive Testing[/bold blue]")
    console.print("Following crawl_mcp.py methodology - Step 4: Modular Component Testing")

    try:
        with SMEAgentModule() as agent:
            test_results = agent.run_comprehensive_tests()
            _display_test_results(test_results)

    except Exception as e:
        console.print(f"[red]❌ Testing failed: {e}[/red]")
        sys.exit(1)


@evaluation_commands.command("list-batches")
@handle_sme_agent_error
def list_evaluation_batches() -> None:
    """List all evaluation batches."""
    console.print("[bold blue]📋 SME Agent Evaluation Batches[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            batches = agent.list_evaluation_batches()
            _display_evaluation_batches(batches)

    except Exception as e:
        console.print(f"[red]❌ Failed to list batches: {e}[/red]")
        sys.exit(1)


@evaluation_commands.command("export-batch")
@click.argument("batch_id", required=True)
@click.option(
    "--format",
    "export_format",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Export format",
)
@handle_sme_agent_error
def export_evaluation_batch(batch_id: str, export_format: str) -> None:
    """Export evaluation batch for human review."""
    console.print(f"[bold blue]📤 Exporting Evaluation Batch: {batch_id}[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            export_result = agent.export_evaluation_batch(batch_id, export_format)
            _display_export_result(export_result)

    except Exception as e:
        console.print(f"[red]❌ Export failed: {e}[/red]")
        sys.exit(1)


@evaluation_commands.command("import-evaluation")
@click.argument("batch_id", required=True)
@click.argument("evaluation_file", type=click.Path(exists=True), required=True)
@click.option("--sme-id", required=True, help="ID of the human SME who performed the evaluation")
@handle_sme_agent_error
def import_human_evaluation(batch_id: str, evaluation_file: str, sme_id: str) -> None:
    """Import human evaluation results."""
    console.print(f"[bold blue]📥 Importing Human Evaluation: {batch_id}[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            import_result = agent.import_human_evaluation(batch_id, evaluation_file, sme_id)
            _display_import_result(import_result)

    except Exception as e:
        console.print(f"[red]❌ Import failed: {e}[/red]")
        sys.exit(1)


@evaluation_commands.command("rl-summary")
@handle_sme_agent_error
def reinforcement_learning_summary() -> None:
    """Display reinforcement learning insights and progress."""
    console.print("[bold blue]🧠 Reinforcement Learning Summary[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            rl_insights = agent.get_reinforcement_learning_insights()
            _display_reinforcement_learning_insights(rl_insights)

    except Exception as e:
        console.print(f"[red]❌ Failed to get RL insights: {e}[/red]")
        sys.exit(1)


@evaluation_commands.command("create-test-batch")
@click.option("--size", default=5, help="Number of test decisions to create")
@handle_sme_agent_error
def create_test_evaluation_batch(size: int) -> None:
    """Create a test evaluation batch for human review."""
    console.print(f"[bold blue]🎯 Creating Test Evaluation Batch (Size: {size})[/bold blue]")

    try:
        with SMEAgentModule() as agent:
            batch_result = agent.create_test_evaluation_batch(size)
            _display_batch_creation_result(batch_result)

    except Exception as e:
        console.print(f"[red]❌ Batch creation failed: {e}[/red]")
        sys.exit(1)


# Display helper functions
def _display_test_results(test_results: dict[str, Any]) -> None:
    """Display comprehensive test results."""
    table = Table(title="SME Agent Test Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Score", style="yellow")
    table.add_column("Details", style="white")

    for component, result in test_results.get("components", {}).items():
        status = "✅ Pass" if result.get("passed", False) else "❌ Fail"
        score = f"{result.get('score', 0):.1%}"
        details = result.get("details", "No details available")
        table.add_row(component, status, score, details)

    console.print(table)

    overall_score = test_results.get("overall_score", 0)
    console.print(f"\n[bold]Overall Test Score: {overall_score:.1%}[/bold]")


def _display_evaluation_batches(batches: list[dict[str, Any]]) -> None:
    """Display evaluation batches."""
    table = Table(title="Evaluation Batches")
    table.add_column("Batch ID", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Created", style="white")

    for batch in batches:
        table.add_row(
            batch.get("id", "Unknown"),
            batch.get("status", "Unknown"),
            str(batch.get("size", 0)),
            batch.get("created_at", "Unknown"),
        )

    console.print(table)


def _display_export_result(export_result: dict[str, Any]) -> None:
    """Display export result."""
    if export_result.get("success", False):
        console.print("[green]✅ Export successful![/green]")
        console.print(f"File: {export_result.get('file_path', 'Unknown')}")
        console.print(f"Records: {export_result.get('record_count', 0)}")
    else:
        console.print("[red]❌ Export failed![/red]")
        console.print(f"Error: {export_result.get('error', 'Unknown error')}")


def _display_import_result(import_result: dict[str, Any]) -> None:
    """Display import result."""
    if import_result.get("success", False):
        console.print("[green]✅ Import successful![/green]")
        console.print(f"Records processed: {import_result.get('processed_count', 0)}")
        console.print(f"SME ID: {import_result.get('sme_id', 'Unknown')}")
    else:
        console.print("[red]❌ Import failed![/red]")
        console.print(f"Error: {import_result.get('error', 'Unknown error')}")


def _display_reinforcement_learning_insights(insights: dict[str, Any]) -> None:
    """Display reinforcement learning insights."""
    console.print(
        Panel(
            f"""
**Learning Progress**: {insights.get("progress", "Unknown")}
**Total Evaluations**: {insights.get("total_evaluations", 0)}
**Accuracy Improvement**: {insights.get("accuracy_improvement", 0):.1%}
**Recent Performance**: {insights.get("recent_performance", "Unknown")}
**Next Training**: {insights.get("next_training", "Unknown")}
        """,
            title="Reinforcement Learning Insights",
            border_style="green",
        )
    )


def _display_batch_creation_result(batch_result: dict[str, Any]) -> None:
    """Display batch creation result."""
    if batch_result.get("success", False):
        console.print("[green]✅ Test batch created successfully![/green]")
        console.print(f"Batch ID: {batch_result.get('batch_id', 'Unknown')}")
        console.print(f"Size: {batch_result.get('size', 0)} decisions")
        console.print("Ready for human evaluation")
    else:
        console.print("[red]❌ Batch creation failed![/red]")
        console.print(f"Error: {batch_result.get('error', 'Unknown error')}")
