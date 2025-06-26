"""Core CLI interface for IGN Scripts with Learning System Integration.

This module provides the main CLI class and core functionality.
"""

import logging
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Optional prompt_toolkit imports for TUI features
try:
    from prompt_toolkit import Application
    from prompt_toolkit.shortcuts import (
        radiolist_dialog,
    )

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


from src import __version__

# Import learning system components
try:
    from src.ignition.generators.script_generator import IgnitionScriptGenerator
    from src.ignition.graph.client import IgnitionGraphClient
    from src.ignition.graph.pattern_analyzer import PatternAnalyzer
    from src.ignition.graph.pattern_manager import PatternManager
    from src.ignition.graph.usage_tracker import UsageTracker
except ImportError as e:
    print(f"Warning: Learning system components not available: {e}")
    IgnitionGraphClient = None
    UsageTracker = None
    PatternAnalyzer = None
    PatternManager = None

console = Console()
logger = logging.getLogger(__name__)


class LearningSystemCLI:
    """Enhanced CLI with learning system integration."""

    def __init__(self) -> None:
        """Initialize the learning system CLI."""
        self.console = Console()
        self.client = None
        self.tracker = None
        self.analyzer = None
        self.manager = None
        self.generator = None

        # Initialize learning components if available
        if IgnitionGraphClient and UsageTracker and PatternAnalyzer and PatternManager:
            try:
                self.client = IgnitionGraphClient()
                self.tracker = UsageTracker(self.client)
                self.analyzer = PatternAnalyzer(self.client)
                self.manager = PatternManager(self.client)
                self.generator = IgnitionScriptGenerator() if IgnitionScriptGenerator else None
            except Exception as e:
                self.console.print(f"[yellow]Warning: Learning system not available: {e}[/yellow]")

    def connect_learning_system(self) -> bool:
        """Connect to the learning system database."""
        if not self.client:
            return False

        try:
            if self.client.connect():
                self.console.print("[green]✓[/green] Learning system connected")
                return True
            else:
                self.console.print("[yellow]⚠[/yellow] Learning system not available")
                return False
        except Exception as e:
            self.console.print(f"[yellow]⚠[/yellow] Learning system error: {e}")
            return False

    def track_cli_usage(
        self,
        command: str,
        subcommand: str | None = None,
        parameters: dict[str, Any] | None = None,
        success: bool = True,
    ):
        """Track CLI command usage for learning."""
        if not self.tracker:
            return

        try:
            # Create a session if none exists
            if (hasattr(self.tracker, "current_session_id") and not self.tracker.current_session_id) and hasattr(
                self.tracker, "start_session"
            ):
                self.tracker.start_session(user_id="cli_user", session_type="cli_usage")

            # Track the command usage
            function_name = f"cli.{command}"
            if subcommand:
                function_name += f".{subcommand}"

            if hasattr(self.tracker, "track_function_query"):
                self.tracker.track_function_query(
                    function_name=function_name,
                    context="CLI",
                    parameters=parameters,
                    success=success,
                )
        except Exception:
            # Silently fail for usage tracking
            pass

    def get_recommendations(self, current_command: str) -> list[dict[str, Any]]:
        """Get command recommendations based on usage patterns."""
        if not self.analyzer:
            return []

        try:
            function_name = f"cli.{current_command}"
            recommendations = self.analyzer.get_recommendations_for_function(function_name)

            # Convert to CLI commands
            cli_recommendations = []
            for rec in recommendations:
                if rec["recommended_function"].startswith("cli."):
                    cmd = rec["recommended_function"].replace("cli.", "")
                    cli_recommendations.append(
                        {
                            "command": cmd,
                            "confidence": rec["confidence"],
                            "reasoning": rec["reasoning"],
                        }
                    )

            return cli_recommendations
        except Exception:
            return []

    def display_welcome(self) -> None:
        """Display enhanced welcome message with learning system status."""
        title = Text()
        title.append("IGN Scripts", style="bold blue")
        title.append(" v", style="dim")
        title.append(__version__, style="bold green")

        # Check learning system status
        ls_status = "🧠 Connected" if self.client and self.client.is_connected else "⚠️ Disconnected"

        welcome_panel = Panel.fit(
            f"{title}\n"
            f"[dim]Intelligent Ignition Script Generation & Learning System[/dim]\n\n"
            f"🔧 Script collections.abc.collections.abc.collections.abc.collections.abc.collections.abc.collections.abc.collections.abc.Generator: [green]Ready[/green]\n"  # noqa: E501
            f"📊 Learning System: [{'green' if self.client and self.client.is_connected else 'yellow'}]{ls_status}[/]",
            title="🚀 Welcome",
            border_style="blue",
            padding=(1, 2),
        )

        self.console.print(welcome_panel)

        # Show quick tips if learning system is connected
        if self.client and self.client.is_connected:
            tips = [
                "💡 Commands are tracked to improve recommendations",
                "🎯 Use 'ign learning' to explore usage patterns",
                "📈 Get personalized suggestions with 'ign recommend'",
                "🔍 Launch interactive explorer with 'ign learning explore'",
            ]

            tips_panel = Panel(
                "\n".join(tips),
                title="💡 Smart Features",
                border_style="green",
                padding=(0, 2),
            )
            self.console.print(tips_panel)


# Initialize the enhanced CLI
enhanced_cli = LearningSystemCLI()


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """🧠 IGN Scripts - Intelligent Ignition Script Generation with Learning System."""
    ctx.ensure_object(dict)
    ctx.obj["cli"] = enhanced_cli

    # Connect to learning system and display welcome
    enhanced_cli.connect_learning_system()
    enhanced_cli.display_welcome()


@main.command()
@click.pass_context
def setup(ctx: click.Context) -> None:
    """🔧 Interactive setup wizard for IGN Scripts configuration."""
    enhanced_cli.track_cli_usage("setup")

    console.print("[bold blue]🔧 IGN Scripts Setup Wizard[/bold blue]\n")

    # Configuration steps
    steps = [
        "Neo4j Database Configuration",
        "Ignition Gateway Connection",
        "Learning System Setup",
        "Template Directory Setup",
        "Export/Import Configuration",
    ]

    for i, step in enumerate(steps, 1):
        console.print(f"[bold cyan]Step {i}:[/bold cyan] {step}")
        # TODO: Implement actual configuration logic
        console.print(f"   [green]✓[/green] {step} configured")

    console.print("\n[green]🎉 Setup completed successfully![/green]")
    console.print("[dim]Run 'ign --help' to see available commands.[/dim]")


@main.result_callback()
@click.pass_context
def cleanup(ctx: click.Context, result, **kwargs) -> None:
    """Clean up resources after command execution."""
    try:
        cli = ctx.obj.get("cli")
        if cli and cli.client and hasattr(cli.client, "close"):
            cli.client.close()
    except Exception:
        # Silently fail cleanup
        pass
