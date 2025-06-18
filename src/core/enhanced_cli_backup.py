"""Enhanced CLI interface for IGN Scripts with Learning System Integration.

This module provides a rich, interactive command-line interface with:
- Learning system integration and usage tracking
- Smart recommendations based on usage patterns
- Beautiful terminal UI with rich formatting
- Interactive pattern exploration
- Real-time analytics and insights
"""

# Import the main CLI group and enhanced_cli instance from core
from .cli_core import enhanced_cli, main

# Import all command modules to register them with the main group
from .cli_script_commands import script
from .cli_template_commands import template

# Register command groups with main CLI
main.add_command(script)
main.add_command(template)

# Import all remaining commands that haven't been split yet
# These will be moved to separate modules in subsequent iterations

import logging
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Optional prompt_toolkit imports for TUI features
try:
    from prompt_toolkit import Application
    from prompt_toolkit.shortcuts import (
        input_dialog,
        message_dialog,
        radiolist_dialog,
    )
    from prompt_toolkit.styles import Style

    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    # Create dummy classes if prompt_toolkit not available
    class DummyApp:
        def __init__(self) -> None:
            pass

        def run(self) -> None:
            pass

    Application = DummyApp
    PROMPT_TOOLKIT_AVAILABLE = False

import builtins

console = Console()
logger = logging.getLogger(__name__)

# TODO: The following commands will be moved to separate modules in the next iteration
# For now, keeping them here to maintain functionality


@main.group()
def learning() -> None:
    """🧠 Learning system and analytics commands."""
    enhanced_cli.track_cli_usage("learning")


@learning.command()
@click.option("--days", "-d", default=30, help="Days of data to analyze")
@click.option("--pattern-type", "-t", help="Specific pattern type to show")
@click.pass_context
def patterns(ctx: click.Context, days: int, pattern_type: str) -> None:
    """📊 Explore usage patterns and insights."""
    if not enhanced_cli.manager:
        console.print("[yellow]Learning system not available[/yellow]")
        return

    enhanced_cli.track_cli_usage(
        "learning", "patterns", {"days": days, "pattern_type": pattern_type}
    )

    try:
        with console.status("[bold blue]Analyzing patterns..."):
            if pattern_type:
                patterns = enhanced_cli.manager.get_patterns_by_type(
                    pattern_type, limit=10
                )
                display_specific_patterns(pattern_type, patterns)
            else:
                stats = enhanced_cli.manager.get_pattern_statistics()
                display_pattern_overview(stats)

    except Exception as e:
        console.print(f"[red]✗[/red] Error analyzing patterns: {e}")


def display_pattern_overview(stats: dict[str, Any]) -> None:
    """Display overview of all patterns."""
    console.print("[bold cyan]📊 Pattern Analysis Overview[/bold cyan]\n")

    # Pattern counts
    if stats.get("pattern_counts"):
        counts_table = Table(title="Pattern Counts by Type", show_header=True)
        counts_table.add_column("Pattern Type", style="cyan")
        counts_table.add_column("Count", justify="right", style="green")

        for pattern_type, count in stats["pattern_counts"].items():
            counts_table.add_row(pattern_type.replace("_", " ").title(), str(count))

        console.print(counts_table)

    # Confidence distribution
    if stats.get("confidence_distribution"):
        console.print("\n[bold]📈 Confidence Distribution[/bold]")
        conf_dist = stats["confidence_distribution"]

        for level, count in conf_dist.items():
            if count > 0:
                bar = "█" * min(int(count / 5), 20)  # Simple bar chart
                console.print(f"  {level.replace('_', ' ').title()}: {count} {bar}")


def display_specific_patterns(
    pattern_type: str, patterns: builtins.list[dict[str, Any]]
) -> None:
    """Display specific pattern type details."""
    title = f"📊 {pattern_type.replace('_', ' ').title()} Patterns"
    console.print(f"[bold cyan]{title}[/bold cyan]\n")

    if not patterns:
        console.print("[yellow]No patterns found for this type[/yellow]")
        return

    for i, pattern in enumerate(patterns, 1):
        panel_content = create_pattern_display(pattern)
        console.print(Panel(panel_content, title=f"Pattern {i}", border_style="blue"))


def create_pattern_display(pattern: dict[str, Any]) -> str:
    """Create a formatted display for a pattern."""
    pattern_type = pattern.get("pattern_type", "unknown")

    if pattern_type == "function_co_occurrence":
        func1 = pattern.get("function_1", "")
        func2 = pattern.get("function_2", "")
        conf1 = pattern.get("confidence_1_to_2", 0)
        conf2 = pattern.get("confidence_2_to_1", 0)
        support = pattern.get("support", 0)

        return f"Functions: {func1} ↔ {func2}\nConfidence: {conf1:.1%} / {conf2:.1%}\nSupport: {support:.1%}"

    elif pattern_type == "template_usage":
        template = pattern.get("template_name", "")
        usage = pattern.get("usage_count", 0)
        success = pattern.get("success_rate", 0)

        return (
            f"Template: {template}\nUsage Count: {usage}\nSuccess Rate: {success:.1%}"
        )

    elif pattern_type == "parameter_combination":
        entity = pattern.get("entity_name", "")
        param = pattern.get("parameter_key", "")
        frequency = pattern.get("frequency", 0)
        success = pattern.get("success_rate", 0)

        return f"Entity: {entity}\nParameter: {param}\nFrequency: {frequency:.1%}\nSuccess Rate: {success:.1%}"

    return str(pattern)


# TODO: Continue with remaining commands - this file will be further split in next iteration
# For now, preserving the original structure to maintain functionality

# Export the main CLI group and enhanced_cli for external imports
__all__ = ["enhanced_cli", "main"]
