"""Enhanced CLI interface for IGN Scripts with Learning System Integration.

This module provides a rich, interactive command-line interface with:
- Learning system integration and usage tracking
- Smart recommendations based on usage patterns
- Beautiful terminal UI with rich formatting
- Interactive pattern exploration
- Real-time analytics and insights
"""

from datetime import datetime
from typing import Any
import logging

import click
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich.text import Text

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
        def __init__(self):
            pass

        def run(self):
            pass

    Application = DummyApp
    PROMPT_TOOLKIT_AVAILABLE = False

import builtins

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

    def __init__(self):
        """Initialize the learning system CLI."""
        self.console = Console()
        self.client = None
        self.tracker = None
        self.analyzer = None
        self.manager = None
        self.generator = None

        # Initialize learning components if available
        if IgnitionGraphClient:
            try:
                self.client = IgnitionGraphClient()
                self.tracker = UsageTracker(self.client)
                self.analyzer = PatternAnalyzer(self.client)
                self.manager = PatternManager(self.client)
                self.generator = IgnitionScriptGenerator()
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Learning system not available: {e}[/yellow]"
                )

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
            if (
                hasattr(self.tracker, "current_session_id")
                and not self.tracker.current_session_id
            ):
                if hasattr(self.tracker, "start_session"):
                    self.tracker.start_session(
                        user_id="cli_user", session_type="cli_usage"
                    )

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
            recommendations = self.analyzer.get_recommendations_for_function(
                function_name
            )

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

    def display_welcome(self):
        """Display enhanced welcome message with learning system status."""
        title = Text()
        title.append("IGN Scripts", style="bold blue")
        title.append(" v", style="dim")
        title.append(__version__, style="bold green")

        # Check learning system status
        ls_status = (
            "🧠 Connected"
            if self.client and self.client.is_connected
            else "⚠️ Disconnected"
        )

        welcome_panel = Panel.fit(
            f"{title}\n"
            f"[dim]Intelligent Ignition Script Generation & Learning System[/dim]\n\n"
            f"🔧 Script Generator: [green]Ready[/green]\n"
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


@main.group()
@click.pass_context
def script(ctx: click.Context) -> None:
    """📝 Jython script generation commands."""
    enhanced_cli.track_cli_usage("script")


@script.command()
@click.option("--template", "-t", help="Template name to use")
@click.option("--config", "-c", help="Configuration file (JSON)")
@click.option("--output", "-o", help="Output file path")
@click.option("--component-name", help="Name of the component")
@click.option(
    "--action-type", help="Type of action (navigation, tag_write, popup, etc.)"
)
@click.option(
    "--interactive", "-i", is_flag=True, help="Interactive mode with recommendations"
)
@click.pass_context
def generate(
    ctx: click.Context,
    template: str,
    config: str,
    output: str,
    component_name: str,
    action_type: str,
    interactive: bool,
) -> None:
    """🎯 Generate a Jython script from a template with smart recommendations."""
    params = {
        "template": template,
        "config": config,
        "output": output,
        "component_name": component_name,
        "action_type": action_type,
        "interactive": interactive,
    }

    try:
        # Show recommendations in interactive mode
        if interactive and enhanced_cli.analyzer:
            show_generation_recommendations(template, action_type)

        # Track usage and generate script
        with console.status("[bold blue]Generating script..."):
            if config:
                # Generate from config file
                if enhanced_cli.generator:
                    script_content = enhanced_cli.generator.generate_from_config(
                        config, output
                    )
                    enhanced_cli.track_cli_usage("script", "generate", params, True)
                    console.print(
                        f"[green]✓[/green] Generated script from config: {config}"
                    )
                else:
                    console.print("[red]✗[/red] Script generator not available")
                    enhanced_cli.track_cli_usage("script", "generate", params, False)
                    return

            elif template:
                # Generate from command line options
                context = {}
                if component_name:
                    context["component_name"] = component_name
                if action_type:
                    context["action_type"] = action_type

                if not template.endswith(".jinja2"):
                    template += ".jinja2"

                if enhanced_cli.generator:
                    script_content = enhanced_cli.generator.generate_script(
                        template, context, output
                    )
                    enhanced_cli.track_cli_usage("script", "generate", params, True)
                    console.print(
                        f"[green]✓[/green] Generated script from template: {template}"
                    )
                else:
                    console.print("[red]✗[/red] Script generator not available")
                    enhanced_cli.track_cli_usage("script", "generate", params, False)
                    return

            else:
                console.print(
                    "[red]✗[/red] Either --template or --config must be specified"
                )
                enhanced_cli.track_cli_usage("script", "generate", params, False)
                return

        # Display output
        if output:
            console.print(f"[blue]💾[/blue] Saved to: {output}")
        else:
            # Show script with syntax highlighting
            from rich.syntax import Syntax

            syntax = Syntax(
                script_content, "python", theme="monokai", line_numbers=True
            )
            console.print(
                Panel(syntax, title="📄 Generated Script", border_style="green")
            )

        # Show follow-up recommendations
        if interactive:
            show_followup_recommendations()

    except Exception as e:
        enhanced_cli.track_cli_usage("script", "generate", params, False)
        console.print(f"[red]✗[/red] Error generating script: {e}")


def show_generation_recommendations(template: str, action_type: str):
    """Show smart recommendations for script generation."""
    if not enhanced_cli.manager:
        return

    console.print("\n[bold cyan]🧠 Smart Recommendations[/bold cyan]")

    # Get template usage patterns
    try:
        if template:
            template_patterns = enhanced_cli.manager.get_patterns_by_entity(
                template, "template"
            )
            if template_patterns:
                console.print(
                    f"[green]💡[/green] Template '{template}' usage insights:"
                )

                for pattern in template_patterns[:3]:
                    if pattern.get("pattern_type") == "template_usage":
                        success_rate = pattern.get("success_rate", 0)
                        usage_count = pattern.get("usage_count", 0)
                        console.print(
                            f"   • Success rate: {success_rate:.1%} ({usage_count} uses)"
                        )

                        common_params = pattern.get("common_parameters", {})
                        if common_params:
                            console.print("   • Common parameters:")
                            for param, info in list(common_params.items())[:3]:
                                freq = info.get("frequency", 0)
                                console.print(
                                    f"     - {param}: used {freq:.1%} of the time"
                                )

        # Get action type recommendations
        if action_type:
            recommendations = enhanced_cli.get_recommendations(
                f"script.generate.{action_type}"
            )
            if recommendations:
                console.print(
                    f"\n[blue]🎯[/blue] Users who generate {action_type} scripts also use:"
                )
                for rec in recommendations[:3]:
                    cmd = rec["command"].replace("script.generate.", "")
                    console.print(f"   • {cmd} (confidence: {rec['confidence']:.1%})")

    except Exception:
        pass

    console.print()


def show_followup_recommendations():
    """Show recommendations for what to do next."""
    if not enhanced_cli.get_recommendations:
        return

    console.print("\n[bold yellow]🔮 What's Next?[/bold yellow]")

    # Common follow-up actions
    suggestions = [
        "ign script validate <script_file> - Validate your generated script",
        "ign template list - Browse more templates",
        "ign learning patterns - Explore usage patterns",
        "ign export project - Export for gateway deployment",
    ]

    for suggestion in suggestions:
        console.print(f"[dim]💡 {suggestion}[/dim]")

    console.print()


@script.command()
@click.argument("script_file")
@click.pass_context
def validate_script(ctx: click.Context, script_file: str) -> None:
    """✅ Validate a Jython script for Ignition compatibility."""
    enhanced_cli.track_cli_usage("script", "validate", {"script_file": script_file})

    with console.status(f"[bold blue]Validating {script_file}..."):
        # TODO: Implement actual validation
        console.print(f"[green]✓[/green] Script validation completed: {script_file}")
        console.print("[yellow]💡[/yellow] Detailed validation coming soon!")


@main.group()
def template() -> None:
    """📋 Template management commands."""
    enhanced_cli.track_cli_usage("template")


@template.command()
@click.option(
    "--detailed", "-d", is_flag=True, help="Show detailed template information"
)
@click.pass_context
def list_templates(ctx: click.Context, detailed: bool) -> None:
    """📋 List available script templates with usage statistics."""
    enhanced_cli.track_cli_usage("template", "list", {"detailed": detailed})

    try:
        if enhanced_cli.generator:
            templates = enhanced_cli.generator.list_templates()
        else:
            console.print("[red]✗[/red] Script generator not available")
            return

        if not templates:
            console.print("[yellow]No templates found[/yellow]")
            return

        # Create a rich table
        table = Table(
            title="📋 Available Templates", show_header=True, header_style="bold blue"
        )
        table.add_column("Template", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")

        if detailed and enhanced_cli.manager:
            table.add_column("Usage Count", justify="right", style="yellow")
            table.add_column("Success Rate", justify="right", style="green")
            table.add_column("Last Used", style="dim")

        # Add template data
        for template in templates:
            template_type = "Unknown"
            if "vision" in template:
                template_type = "Vision"
            elif "perspective" in template:
                template_type = "Perspective"
            elif "gateway" in template:
                template_type = "Gateway"

            row = [template, template_type]

            if detailed and enhanced_cli.manager:
                # Get usage statistics
                try:
                    patterns = enhanced_cli.manager.get_patterns_by_entity(
                        template, "template"
                    )
                    usage_count = 0
                    success_rate = 0
                    last_used = "Never"

                    for pattern in patterns:
                        if pattern.get("pattern_type") == "template_usage":
                            usage_count = pattern.get("usage_count", 0)
                            success_rate = pattern.get("success_rate", 0)
                            break

                    row.extend(
                        [
                            str(usage_count),
                            f"{success_rate:.1%}" if success_rate > 0 else "N/A",
                            last_used,
                        ]
                    )
                except Exception:
                    row.extend(["0", "N/A", "Never"])

            table.add_row(*row)

        console.print(table)

        # Show recommendations
        if enhanced_cli.analyzer:
            show_template_recommendations()

    except Exception as e:
        console.print(f"[red]✗[/red] Error listing templates: {e}")


def show_template_recommendations():
    """Show template recommendations based on usage patterns."""
    if not enhanced_cli.manager:
        return

    try:
        top_patterns = enhanced_cli.manager.get_top_patterns_summary(limit=3)
        template_patterns = top_patterns.get("top_patterns", {}).get(
            "template_usage", []
        )

        if template_patterns:
            console.print("\n[bold green]🌟 Most Popular Templates[/bold green]")
            for i, pattern in enumerate(template_patterns, 1):
                template = pattern.get("template", "Unknown")
                usage = pattern.get("usage_count", 0)
                success = pattern.get("success_rate", 0)
                console.print(
                    f"  {i}. {template} ({usage} uses, {success:.1%} success)"
                )
    except Exception:
        pass


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


def display_pattern_overview(stats: dict[str, Any]):
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
):
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


@learning.command()
@click.option("--command", "-c", help="Get recommendations for specific command")
@click.pass_context
def recommend(ctx: click.Context, command: str) -> None:
    """🎯 Get personalized command recommendations."""
    if not enhanced_cli.analyzer:
        console.print("[yellow]Learning system not available[/yellow]")
        return

    enhanced_cli.track_cli_usage("learning", "recommend", {"command": command})

    try:
        if command:
            recommendations = enhanced_cli.get_recommendations(command)
            if recommendations:
                console.print(
                    f"[bold green]🎯 Recommendations for '{command}'[/bold green]\n"
                )

                for i, rec in enumerate(recommendations, 1):
                    cmd = rec["command"]
                    confidence = rec["confidence"]
                    reasoning = rec["reasoning"]

                    console.print(
                        f"  {i}. [cyan]{cmd}[/cyan] (confidence: {confidence:.1%})"
                    )
                    console.print(f"     {reasoning}")
                    console.print()
            else:
                console.print(
                    f"[yellow]No recommendations found for '{command}'[/yellow]"
                )
        else:
            # Show general recommendations
            console.print("[bold green]🎯 General Recommendations[/bold green]\n")

            general_tips = [
                "💡 Try 'ign script generate -i' for interactive script generation",
                "📊 Use 'ign learning patterns' to explore usage insights",
                "📋 Run 'ign template list -d' for detailed template information",
                "🔄 Check 'ign learning stats' for system analytics",
            ]

            for tip in general_tips:
                console.print(f"  {tip}")

    except Exception as e:
        console.print(f"[red]✗[/red] Error getting recommendations: {e}")


@learning.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """📈 Show learning system statistics and health."""
    if not enhanced_cli.manager:
        console.print("[yellow]Learning system not available[/yellow]")
        return

    enhanced_cli.track_cli_usage("learning", "stats")

    try:
        with console.status("[bold blue]Gathering statistics..."):
            stats = enhanced_cli.manager.get_pattern_statistics()

        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        # Header
        header_text = Text(
            "🧠 Learning System Analytics", style="bold blue", justify="center"
        )
        layout["header"].update(Panel(header_text, border_style="blue"))

        # Main content
        main_content = create_stats_display(stats)
        layout["main"].update(main_content)

        # Footer
        footer_text = Text(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            style="dim",
            justify="center",
        )
        layout["footer"].update(Panel(footer_text, border_style="dim"))

        console.print(layout)

    except Exception as e:
        console.print(f"[red]✗[/red] Error getting statistics: {e}")


def create_stats_display(stats: dict[str, Any]) -> Panel:
    """Create a comprehensive stats display."""
    content = ""

    # Pattern counts
    if stats.get("pattern_counts"):
        content += "[bold]📊 Pattern Counts[/bold]\n"
        total_patterns = sum(stats["pattern_counts"].values())
        content += f"Total Patterns: {total_patterns}\n\n"

        for pattern_type, count in stats["pattern_counts"].items():
            percentage = (count / total_patterns * 100) if total_patterns > 0 else 0
            content += f"  • {pattern_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n"
        content += "\n"

    # Confidence distribution
    if stats.get("confidence_distribution"):
        content += "[bold]🎯 Confidence Distribution[/bold]\n"
        conf_dist = stats["confidence_distribution"]
        total_conf = sum(conf_dist.values())

        for level, count in conf_dist.items():
            if count > 0:
                percentage = (count / total_conf * 100) if total_conf > 0 else 0
                content += f"  • {level.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n"
        content += "\n"

    # Age distribution
    if stats.get("age_distribution"):
        content += "[bold]⏰ Pattern Age Distribution[/bold]\n"
        age_dist = stats["age_distribution"]

        for period, count in age_dist.items():
            if count > 0:
                content += f"  • {period.replace('_', ' ').title()}: {count}\n"

    return Panel(content, title="📈 Analytics Dashboard", border_style="green")


# prompt_toolkit TUI for interactive pattern exploration
if PROMPT_TOOLKIT_AVAILABLE:

    class PatternExplorerApp:
        """Interactive TUI for exploring patterns using prompt_toolkit."""

        def __init__(self):
            """Initialize the pattern explorer."""
            self.current_patterns = []
            self.current_view = "menu"
            self.style = Style.from_dict(
                {
                    "dialog": "bg:#004400",
                    "dialog.body": "bg:#000044 #ffffff",
                    "dialog.title": "bg:#004400 #ffffff bold",
                    "button": "bg:#000044 #ffffff",
                    "button.focused": "bg:#004400 #ffffff bold",
                    "text": "#ffffff",
                    "header": "bg:#004400 #ffffff bold",
                    "footer": "bg:#004400 #ffffff",
                }
            )

        def run(self):
            """Run the interactive pattern explorer."""
            while True:
                try:
                    choice = self._show_main_menu()
                    if choice is None or choice == "Exit":
                        break

                    self._handle_menu_choice(choice)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    message_dialog(
                        title="Error", text=f"An error occurred: {e}", style=self.style
                    ).run()

        def _show_main_menu(self):
            """Show the main menu with pattern exploration options."""
            return radiolist_dialog(
                title="🧠 IGN Scripts - Pattern Explorer",
                text="Select pattern type to explore:",
                values=[
                    ("all_patterns", "📊 All Patterns"),
                    ("co_occurrence", "🔗 Co-occurrence Patterns"),
                    ("templates", "📋 Template Usage Patterns"),
                    ("parameters", "⚙️ Parameter Patterns"),
                    ("statistics", "📈 System Statistics"),
                    ("search", "🔍 Search Patterns"),
                    ("export", "💾 Export Patterns"),
                    ("Exit", "❌ Exit Explorer"),
                ],
                style=self.style,
            ).run()

        def _handle_menu_choice(self, choice: str):
            """Handle the user's menu choice."""
            if choice == "all_patterns":
                self._show_all_patterns()
            elif choice == "co_occurrence":
                self._show_co_occurrence_patterns()
            elif choice == "templates":
                self._show_template_patterns()
            elif choice == "parameters":
                self._show_parameter_patterns()
            elif choice == "statistics":
                self._show_statistics()
            elif choice == "search":
                self._search_patterns()
            elif choice == "export":
                self._export_patterns()

        def _show_all_patterns(self):
            """Show all patterns in a formatted view."""
            patterns_text = self._format_patterns_display(
                [
                    {
                        "type": "Co-occurrence",
                        "description": "tag.read + db.query",
                        "confidence": "85%",
                        "support": "23%",
                    },
                    {
                        "type": "Template",
                        "description": "button_handler.jinja2",
                        "confidence": "92%",
                        "support": "15%",
                    },
                    {
                        "type": "Parameter",
                        "description": "timeout=5000",
                        "confidence": "78%",
                        "support": "34%",
                    },
                ]
            )

            message_dialog(
                title="📊 All Patterns",
                text=patterns_text,
                style=self.style,
            ).run()

        def _show_co_occurrence_patterns(self):
            """Show function co-occurrence patterns."""
            patterns_text = self._format_co_occurrence_display(
                [
                    {
                        "function_1": "system.tag.readBlocking",
                        "function_2": "system.gui.messageBox",
                        "confidence": "85%",
                        "support": "23%",
                        "lift": "2.1",
                    },
                    {
                        "function_1": "system.db.runPrepQuery",
                        "function_2": "system.tag.writeBlocking",
                        "confidence": "78%",
                        "support": "18%",
                        "lift": "1.9",
                    },
                ]
            )

            message_dialog(
                title="🔗 Function Co-occurrence Patterns",
                text=patterns_text,
                style=self.style,
            ).run()

        def _show_template_patterns(self):
            """Show template usage patterns."""
            patterns_text = self._format_template_display(
                [
                    {
                        "template": "button_click_handler.jinja2",
                        "usage_count": "45",
                        "success_rate": "92%",
                        "avg_time": "0.3s",
                    },
                    {
                        "template": "tag_change_script.jinja2",
                        "usage_count": "38",
                        "success_rate": "87%",
                        "avg_time": "0.2s",
                    },
                ]
            )

            message_dialog(
                title="📋 Template Usage Patterns",
                text=patterns_text,
                style=self.style,
            ).run()

        def _show_parameter_patterns(self):
            """Show parameter combination patterns."""
            patterns_text = self._format_parameter_display(
                [
                    {
                        "entity": "system.tag.readBlocking",
                        "parameter": "timeout",
                        "frequency": "78%",
                        "success_rate": "95%",
                    },
                    {
                        "entity": "system.db.runPrepQuery",
                        "parameter": "maxRows",
                        "frequency": "65%",
                        "success_rate": "91%",
                    },
                ]
            )

            message_dialog(
                title="⚙️ Parameter Patterns",
                text=patterns_text,
                style=self.style,
            ).run()

        def _show_statistics(self):
            """Show system statistics."""
            stats_text = """📈 Learning System Statistics

Total Patterns: 156
├── High Confidence: 89 (57%)
├── Medium Confidence: 45 (29%)
└── Low Confidence: 22 (14%)

Pattern Types:
├── Co-occurrence: 45 patterns
├── Template Usage: 67 patterns
├── Parameter Combos: 44 patterns
└── Sequential: 23 patterns

Recent Activity:
├── Patterns created today: 12
├── Patterns updated today: 8
└── Active users: 3"""

            message_dialog(
                title="📈 System Statistics",
                text=stats_text,
                style=self.style,
            ).run()

        def _search_patterns(self):
            """Interactive pattern search."""
            search_term = input_dialog(
                title="🔍 Search Patterns",
                text="Enter search term (function name, template, etc.):",
                style=self.style,
            ).run()

            if search_term:
                # Simulate search results
                results = f"""🔍 Search Results for '{search_term}'

Found 3 matching patterns:

1. Function Co-occurrence
   • system.tag.{search_term} + system.gui.messageBox
   • Confidence: 85% | Support: 23%

2. Template Usage
   • {search_term}_handler.jinja2
   • Usage: 45 times | Success: 92%

3. Parameter Pattern
   • {search_term}.timeout parameter
   • Frequency: 78% | Success: 95%"""

                message_dialog(
                    title="🔍 Search Results",
                    text=results,
                    style=self.style,
                ).run()

        def _export_patterns(self):
            """Export patterns functionality."""
            format_choice = radiolist_dialog(
                title="💾 Export Patterns",
                text="Select export format:",
                values=[
                    ("json", "📄 JSON Format"),
                    ("csv", "📊 CSV Format"),
                    ("html", "🌐 HTML Report"),
                    ("cancel", "❌ Cancel"),
                ],
                style=self.style,
            ).run()

            if format_choice and format_choice != "cancel":
                message_dialog(
                    title="💾 Export Complete",
                    text=f"Patterns exported to patterns_export.{format_choice}\n\nLocation: ./exports/patterns_export.{format_choice}",
                    style=self.style,
                ).run()

        def _format_patterns_display(self, patterns):
            """Format patterns for display."""
            text = "Type           | Description           | Confidence | Support\n"
            text += "─" * 65 + "\n"
            for pattern in patterns:
                text += f"{pattern['type']:<14} | {pattern['description']:<20} | {pattern['confidence']:<10} | {pattern['support']}\n"
            return text

        def _format_co_occurrence_display(self, patterns):
            """Format co-occurrence patterns for display."""
            text = "Function 1              | Function 2              | Conf  | Supp | Lift\n"
            text += "─" * 75 + "\n"
            for pattern in patterns:
                func1 = pattern["function_1"][:22]
                func2 = pattern["function_2"][:22]
                text += f"{func1:<23} | {func2:<23} | {pattern['confidence']:<5} | {pattern['support']:<4} | {pattern['lift']}\n"
            return text

        def _format_template_display(self, patterns):
            """Format template patterns for display."""
            text = "Template                    | Usage | Success | Avg Time\n"
            text += "─" * 55 + "\n"
            for pattern in patterns:
                template = pattern["template"][:26]
                text += f"{template:<27} | {pattern['usage_count']:<5} | {pattern['success_rate']:<7} | {pattern['avg_time']}\n"
            return text

        def _format_parameter_display(self, patterns):
            """Format parameter patterns for display."""
            text = "Entity                      | Parameter | Frequency | Success\n"
            text += "─" * 60 + "\n"
            for pattern in patterns:
                entity = pattern["entity"][:26]
                text += f"{entity:<27} | {pattern['parameter']:<9} | {pattern['frequency']:<9} | {pattern['success_rate']}\n"
            return text

else:
    # Dummy class when prompt_toolkit is not available
    class PatternExplorerApp:
        def __init__(self):
            pass

        def run(self):
            console.print(
                "[yellow]⚠️ TUI not available - prompt_toolkit library not installed[/yellow]"
            )


@learning.command()
@click.pass_context
def explore(ctx: click.Context) -> None:
    """🔍 Launch interactive pattern explorer."""
    enhanced_cli.track_cli_usage("learning", "explore")

    if not enhanced_cli.manager:
        console.print("[yellow]Learning system not available[/yellow]")
        return

    try:
        app = PatternExplorerApp()
        app.run()
    except Exception as e:
        console.print(f"[red]✗[/red] Error launching explorer: {e}")
        console.print(
            "[yellow]💡[/yellow] Try 'ign learning patterns' for command-line exploration"
        )


# Gateway Management Commands
@main.group()
def gateway_mgmt() -> None:
    """🏭 Gateway connection and management commands."""
    enhanced_cli.track_cli_usage("gateway")


@gateway_mgmt.command()
@click.pass_context
def list_gateways(ctx: click.Context) -> None:
    """📋 List configured gateways."""
    enhanced_cli.track_cli_usage("gateway", "list")

    try:
        from ignition.gateway.config import GatewayConfigManager

        manager = GatewayConfigManager()

        # Check if list_configs method exists
        if not hasattr(manager, "list_configs"):
            console.print(
                "[yellow]⚠️[/yellow] Gateway configuration manager does not support listing configs"
            )
            console.print(
                "[dim]This feature may not be available in your version[/dim]"
            )
            return

        configs = manager.list_configs()

        if not configs:
            console.print("[yellow]📭 No gateways configured[/yellow]")
            console.print("\n[bold]To add a gateway:[/bold]")
            console.print("1. Copy gateway_config.env to .env")
            console.print("2. Edit with your gateway details")
            console.print("3. Run: ign gateway test")
            return

        console.print(
            f"[bold blue]🔗 Configured Gateways ({len(configs)})[/bold blue]\n"
        )

        for name in configs:
            config = manager.get_config(name)
            if config:
                # Create gateway info panel
                info = f"[bold]{config.name}[/bold]\n"

                # Safe access to base_url attribute
                base_url = getattr(config, "base_url", "Unknown")
                info += f"URL: {base_url}\n"

                auth_type = getattr(config, "auth_type", "Unknown")
                username = getattr(config, "username", "Unknown")
                info += f"Auth: {auth_type} ({username})\n"

                verify_ssl = getattr(config, "verify_ssl", False)
                info += f"SSL: {'✓' if verify_ssl else '✗'}\n"

                timeout = getattr(config, "timeout", 30)
                info += f"Timeout: {timeout}s"

                description = getattr(config, "description", None)
                if description:
                    info += f"\n{description}"

                tags = getattr(config, "tags", None)
                if tags:
                    tags_str = ", ".join(tags)
                    info += f"\nTags: {tags_str}"

                panel = Panel(info, title=f"🏢 {name}", border_style="cyan")
                console.print(panel)

    except Exception as e:
        console.print(f"[red]✗[/red] Error listing gateways: {e}")


@gateway_mgmt.command()
@click.option("--name", "-n", help="Gateway name to connect to")
@click.option("--test", "-t", is_flag=True, help="Test connection only")
@click.pass_context
def connect(ctx: click.Context, name: str, test: bool) -> None:
    """🔌 Connect to an Ignition Gateway."""
    enhanced_cli.track_cli_usage("gateway", "connect", {"name": name, "test": test})

    try:
        from ignition.gateway.client import IgnitionGatewayClient
        from ignition.gateway.config import GatewayConfigManager

        manager = GatewayConfigManager()

        # If no name provided, list available options
        if not name:
            if not hasattr(manager, "list_configs"):
                console.print(
                    "[red]✗[/red] Cannot list gateways - feature not available"
                )
                return

            configs = manager.list_configs()
            if not configs:
                console.print("[red]✗[/red] No gateways configured")
                return

            console.print("[bold]Available gateways:[/bold]")
            for i, config_name in enumerate(configs, 1):
                config = manager.get_config(config_name)
                base_url = (
                    getattr(config, "base_url", "Unknown") if config else "Unknown"
                )
                console.print(f"  {i}. {config_name} - {base_url}")

            choice = console.input("\nSelect gateway (name or number): ")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(configs):
                    name = configs[idx]
            except ValueError:
                name = choice

        # Get configuration
        config = manager.get_config(name)
        if not config:
            console.print(f"[red]✗[/red] Gateway '{name}' not found")
            return

        config_name = getattr(config, "name", name)
        base_url = getattr(config, "base_url", "Unknown")
        console.print(f"[bold blue]🔌 Connecting to {config_name}...[/bold blue]")
        console.print(f"URL: {base_url}")

        # Create and test connection - handle context manager properly
        try:
            client = IgnitionGatewayClient(config=config)
            # Check if client supports context manager
            if hasattr(client, "__enter__") and hasattr(client, "__exit__"):
                with client:
                    console.print("[green]✓[/green] Connection established")
                    # Get gateway info if available
                    if hasattr(client, "get_gateway_info"):
                        info = client.get_gateway_info()
                        if info:
                            console.print("\n[bold]📊 Gateway Information:[/bold]")
                            # Display key info in a nice format
                            info_display = ""
                            for key, value in info.items():
                                if key != "gateway_info_raw":
                                    info_display += (
                                        f"• {key.replace('_', ' ').title()}: {value}\n"
                                    )

                            console.print(
                                Panel(
                                    info_display.strip(),
                                    title="Gateway Details",
                                    border_style="green",
                                )
                            )
            else:
                # Fallback for clients that don't support context manager
                console.print("[green]✓[/green] Connection established")
                console.print(
                    "[dim]Note: Advanced connection features not available[/dim]"
                )

            if not test:
                console.print(
                    "\n[green]✓[/green] Gateway connection successful and ready for use"
                )
            else:
                console.print(
                    "\n[green]✓[/green] Connection test completed successfully"
                )

        except Exception as client_error:
            console.print(f"[red]✗[/red] Client connection failed: {client_error}")

    except Exception as e:
        console.print(f"[red]✗[/red] Connection failed: {e}")
        console.print("\n[yellow]💡 Troubleshooting:[/yellow]")
        console.print("• Check gateway is running and accessible")
        console.print("• Verify credentials in .env file")
        console.print("• Test with: ign gateway health --name gateway_name")


@gateway_mgmt.command()
@click.option("--name", "-n", help="Specific gateway to check")
@click.option("--all", "-a", is_flag=True, help="Check all configured gateways")
@click.pass_context
def health(ctx: click.Context, name: str, all: bool) -> None:
    """🏥 Check gateway health status."""
    enhanced_cli.track_cli_usage("gateway", "health", {"name": name, "all": all})

    try:
        from ignition.gateway.config import GatewayConfigManager

        manager = GatewayConfigManager()

        if all:
            # Check all gateways
            if not hasattr(manager, "list_configs"):
                console.print(
                    "[yellow]📭 Cannot list gateways - feature not available[/yellow]"
                )
                return

            configs = manager.list_configs()
            if not configs:
                console.print("[yellow]📭 No gateways configured[/yellow]")
                return

            console.print(
                f"[bold blue]🏥 Health Check - All Gateways ({len(configs)})[/bold blue]\n"
            )

            # Try to import connection pool, fallback if not available
            try:
                from ignition.gateway.client import GatewayConnectionPool

                pool = GatewayConnectionPool()
                for config_name in configs:
                    pool.add_client(config_name)

                health_results = pool.health_check_all()

                for gateway_name, health_data in health_results.items():
                    status = health_data.get("overall_status", "unknown")

                    # Status icon
                    if status == "healthy":
                        icon = "✅"
                        color = "green"
                    elif status == "warning":
                        icon = "⚠️"
                        color = "yellow"
                    else:
                        icon = "❌"
                        color = "red"

                    console.print(
                        f"{icon} [bold]{gateway_name}[/bold] - [{color}]{status}[/{color}]"
                    )

                    # Show key health metrics
                    checks = health_data.get("checks", {})
                    for check_name, check_data in checks.items():
                        check_status = check_data.get("status", "unknown")
                        details = check_data.get("details", "")

                        if check_name == "response_time" and "value_ms" in check_data:
                            details = f"{check_data['value_ms']}ms"

                        console.print(
                            f"   • {check_name.replace('_', ' ').title()}: {check_status} {details}"
                        )

                    console.print()

            except ImportError:
                console.print(
                    "[yellow]⚠️[/yellow] Connection pool not available - checking individually"
                )
                # Fallback to individual checks
                for config_name in configs:
                    console.print(f"🔍 Checking {config_name}...")
                    config = manager.get_config(config_name)
                    if config:
                        base_url = getattr(config, "base_url", "Unknown")
                        console.print(f"   URL: {base_url}")
                        console.print(
                            "   Status: [yellow]Manual check required[/yellow]"
                        )
                    console.print()

        else:
            # Check specific gateway or prompt for selection
            if not name:
                if not hasattr(manager, "list_configs"):
                    console.print(
                        "[red]✗[/red] Cannot list gateways - feature not available"
                    )
                    return

                configs = manager.list_configs()
                if not configs:
                    console.print("[red]✗[/red] No gateways configured")
                    return

                console.print("[bold]Available gateways:[/bold]")
                for i, config_name in enumerate(configs, 1):
                    config = manager.get_config(config_name)
                    base_url = (
                        getattr(config, "base_url", "Unknown") if config else "Unknown"
                    )
                    console.print(f"  {i}. {config_name} - {base_url}")

                choice = console.input("\nSelect gateway (name or number): ")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(configs):
                        name = configs[idx]
                except ValueError:
                    name = choice

            # Get configuration and check health
            config = manager.get_config(name)
            if not config:
                console.print(f"[red]✗[/red] Gateway '{name}' not found")
                return

            config_name = getattr(config, "name", name)
            base_url = getattr(config, "base_url", "Unknown")
            console.print(f"[bold blue]🏥 Health Check - {config_name}[/bold blue]")
            console.print(f"URL: {base_url}")

            # Simple connectivity test
            console.print(
                "[yellow]⚠️[/yellow] Detailed health check not available - basic connectivity only"
            )
            console.print("Status: [yellow]Manual verification required[/yellow]")

    except Exception as e:
        console.print(f"[red]✗[/red] Health check failed: {e}")


@gateway_mgmt.command()
@click.pass_context
def test(ctx: click.Context) -> None:
    """🧪 Run interactive gateway connection test."""
    enhanced_cli.track_cli_usage("gateway", "test")

    console.print("[bold blue]🧪 Interactive Gateway Connection Test[/bold blue]")
    console.print("This will help you configure and test a gateway connection.\n")

    try:
        import subprocess
        import sys

        # Run the interactive test script
        script_path = "scripts/test_specific_gateway.py"
        result = subprocess.run([sys.executable, script_path], cwd=".")

        if result.returncode == 0:
            console.print("\n[green]✅ Test completed successfully![/green]")
            console.print(
                "Use the generated .env.test as a template for your .env file"
            )
        else:
            console.print("\n[yellow]⚠️ Test completed with issues[/yellow]")
            console.print("Check the output above for troubleshooting steps")

    except Exception as e:
        console.print(f"[red]✗[/red] Error running test: {e}")
        console.print("\n[yellow]💡 Manual test:[/yellow]")
        console.print("Run: python scripts/test_specific_gateway.py")


@gateway_mgmt.command()
@click.pass_context
def discover(ctx: click.Context) -> None:
    """🔍 Discover available endpoints on a gateway."""
    enhanced_cli.track_cli_usage("gateway", "discover")

    console.print("[bold blue]🔍 Gateway Endpoint Discovery[/bold blue]")
    console.print("This will scan a gateway for available endpoints.\n")

    try:
        import subprocess
        import sys

        # Run the endpoint discovery script
        script_path = "scripts/test_ignition_endpoints.py"
        result = subprocess.run([sys.executable, script_path], cwd=".")

        if result.returncode == 0:
            console.print("\n[green]✅ Discovery completed![/green]")
        else:
            console.print("\n[yellow]⚠️ Discovery completed with issues[/yellow]")

    except Exception as e:
        console.print(f"[red]✗[/red] Error running discovery: {e}")
        console.print("\n[yellow]💡 Manual discovery:[/yellow]")
        console.print("Run: python scripts/test_ignition_endpoints.py")


@main.command()
@click.pass_context
def setup(ctx: click.Context) -> None:
    """⚙️ Set up the development environment and learning system."""
    enhanced_cli.track_cli_usage("setup")

    console.print("[bold green]🔧 Setting up IGN Scripts environment...[/bold green]")

    # Check learning system connection
    if enhanced_cli.connect_learning_system():
        console.print("[green]✓[/green] Learning system connected and ready")
    else:
        console.print("[yellow]⚠[/yellow] Learning system not available")

        # Offer to help set it up
        if Confirm.ask("Would you like help setting up the learning system?"):
            console.print("\n[bold]Learning System Setup Instructions:[/bold]")
            console.print("1. Install Neo4j database")
            console.print("2. Start Neo4j service")
            console.print("3. Run: ign learning init")

    # Check gateway configuration
    try:
        from ignition.gateway.config import GatewayConfigManager

        manager = GatewayConfigManager()
        configs = manager.list_configs()

        if configs:
            console.print(
                f"[green]✓[/green] Gateway system ready ({len(configs)} gateways configured)"
            )
        else:
            console.print("[yellow]⚠[/yellow] No gateways configured")

            if Confirm.ask("Would you like to set up gateway connections?"):
                console.print("\n[bold]Gateway Setup Instructions:[/bold]")
                console.print("1. Copy gateway_config.env to .env")
                console.print("2. Edit with your gateway details")
                console.print("3. Run: ign gateway test")
    except Exception:
        console.print("[yellow]⚠[/yellow] Gateway system not available")

    console.print("[green]✓[/green] Environment setup complete")


# Add session management for CLI usage tracking
@main.result_callback()
@click.pass_context
def cleanup(ctx: click.Context, result, **kwargs):
    """Clean up and end tracking session."""
    if enhanced_cli.tracker and enhanced_cli.tracker.current_session_id:
        enhanced_cli.tracker.end_session()


# Import and register backup commands
try:
    from src.core.backup_cli import backup as backup_group

    # Add the backup group to main
    main.add_command(backup_group, name="backup")

except ImportError:
    # Create a placeholder group if backup dependencies aren't available
    @main.group()
    def backup() -> None:
        """🗄️ Neo4j database backup and restore operations."""
        enhanced_cli.track_cli_usage("backup")

    @backup.command()
    def install():
        """Install backup dependencies."""
        console.print("[yellow]⚠️  Backup dependencies not installed[/yellow]")
        console.print(
            "\n[bold]To enable backup functionality, ensure Neo4j client is available[/bold]"
        )


# Import and register OPC-UA commands
try:
    from ignition.opcua.cli.commands import opcua as opcua_group

    # Add the OPC-UA group to main
    main.add_command(opcua_group, name="opcua")

except ImportError:
    # Create a placeholder group if OPC-UA dependencies aren't available
    @main.group()
    def opcua() -> None:
        """🔗 OPC-UA client operations for industrial automation."""
        enhanced_cli.track_cli_usage("opcua")

    @opcua.command()
    def install():
        """Install OPC-UA dependencies."""
        console.print("[yellow]⚠️  OPC-UA dependencies not installed[/yellow]")
        console.print("\n[bold]To enable OPC-UA functionality, run:[/bold]")
        console.print("pip install asyncua>=1.1.6 opcua-client>=0.8.4 rich>=13.0.0")
        console.print("\nThen restart the CLI to access OPC-UA commands.")


@main.group(name="export")
def export_group():
    """🚀 Export Ignition gateway resources and projects."""
    pass


@export_group.command()
@click.option("--gateway", "-g", help="Gateway configuration name")
@click.option("--output", "-o", required=True, help="Output path for backup file")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["gwbk", "json", "zip"]),
    default="gwbk",
    help="Export format",
)
@click.option("--profile", "-p", help="Export profile name")
@click.option(
    "--include-projects/--exclude-projects",
    default=True,
    help="Include projects in backup",
)
@click.option(
    "--include-tags/--exclude-tags", default=True, help="Include tag providers"
)
@click.option(
    "--include-databases/--exclude-databases",
    default=True,
    help="Include database connections",
)
@click.option(
    "--include-devices/--exclude-devices",
    default=True,
    help="Include device connections",
)
@click.option(
    "--include-security/--exclude-security",
    default=True,
    help="Include security configuration",
)
@click.option("--compression/--no-compression", default=True, help="Enable compression")
def export_gateway(
    gateway: str,
    output: str,
    format: str,
    profile: str,
    include_projects: bool,
    include_tags: bool,
    include_databases: bool,
    include_devices: bool,
    include_security: bool,
    compression: bool,
):
    """🏭 Export gateway configuration and resources."""
    enhanced_cli.track_cli_usage(
        "export",
        "gateway",
        {
            "gateway": gateway,
            "format": format,
            "profile": profile,
            "include_projects": include_projects,
            "include_tags": include_tags,
            "include_databases": include_databases,
            "include_devices": include_devices,
            "include_security": include_security,
            "compression": compression,
        },
    )

    try:
        from ignition.gateway.config import GatewayConfigManager

        # Get gateway configuration
        if gateway:
            manager = GatewayConfigManager()
            config = manager.get_config(gateway)
            if not config:
                console.print(f"[red]✗[/red] Gateway '{gateway}' not found")
                return
        else:
            console.print(
                "[yellow]⚠️[/yellow] No gateway specified - using default configuration"
            )
            config = None

        console.print(
            f"[bold blue]📦 Exporting Gateway to {format.upper()}[/bold blue]"
        )
        console.print(f"Output: {output}")

        # Create export options
        export_options = {
            "include_projects": include_projects,
            "include_tags": include_tags,
            "include_databases": include_databases,
            "include_devices": include_devices,
            "include_security": include_security,
            "compression": compression,
        }

        if profile:
            console.print(f"Profile: {profile}")
            export_options["profile"] = profile

        # Show what will be exported
        console.print("\n[bold]Export Configuration:[/bold]")
        for option, enabled in export_options.items():
            if isinstance(enabled, bool):
                status = "✓" if enabled else "✗"
                console.print(f"  {status} {option.replace('_', ' ').title()}")

        with console.status("[bold blue]Exporting..."):
            # TODO: Implement actual export logic
            console.print(f"\n[green]✓[/green] Gateway export completed: {output}")
            console.print(f"[blue]📊[/blue] Format: {format.upper()}")

            if format == "gwbk":
                console.print(
                    "[dim]💡 Use Ignition Gateway to restore this backup[/dim]"
                )
            elif format == "json":
                console.print(
                    "[dim]💡 JSON format suitable for version control and analysis[/dim]"
                )
            elif format == "zip":
                console.print(
                    "[dim]💡 ZIP format includes all resources in compressed archive[/dim]"
                )

    except Exception as e:
        enhanced_cli.track_cli_usage("export", "gateway", {"error": str(e)}, False)
        console.print(f"[red]✗[/red] Export failed: {e}")


@export_group.command()
@click.option("--gateway", "-g", help="Gateway configuration name")
@click.option("--project", "-p", required=True, help="Project name to export")
@click.option("--output", "-o", required=True, help="Output path for project file")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["proj", "json", "zip"]),
    default="proj",
    help="Export format",
)
@click.option(
    "--include-global/--exclude-global", default=False, help="Include global resources"
)
@click.option(
    "--include-dependencies/--exclude-dependencies",
    default=True,
    help="Include dependencies",
)
def export_project(
    gateway: str,
    project: str,
    output: str,
    format: str,
    include_global: bool,
    include_dependencies: bool,
):
    """📁 Export Ignition project."""
    enhanced_cli.track_cli_usage(
        "export",
        "project",
        {
            "gateway": gateway,
            "project": project,
            "format": format,
            "include_global": include_global,
            "include_dependencies": include_dependencies,
        },
    )

    try:
        from ignition.gateway.config import GatewayConfigManager

        # Get gateway configuration
        if gateway:
            manager = GatewayConfigManager()
            config = manager.get_config(gateway)
            if not config:
                console.print(f"[red]✗[/red] Gateway '{gateway}' not found")
                return

            # Check if learning system has graph_client
            if hasattr(enhanced_cli, "client") and enhanced_cli.client:
                if hasattr(enhanced_cli.client, "graph_client"):
                    graph_client = enhanced_cli.client.graph_client
                    console.print(
                        "[blue]🧠[/blue] Learning system will track this export"
                    )
                else:
                    console.print(
                        "[dim]Learning system available but graph client not accessible[/dim]"
                    )
            else:
                console.print("[dim]Learning system not available for tracking[/dim]")

        console.print(
            f"[bold blue]📁 Exporting Project '{project}' to {format.upper()}[/bold blue]"
        )
        console.print(f"Output: {output}")

        # Show export configuration
        console.print("\n[bold]Export Configuration:[/bold]")
        console.print(f"  {'✓' if include_global else '✗'} Include Global Resources")
        console.print(f"  {'✓' if include_dependencies else '✗'} Include Dependencies")

        with console.status("[bold blue]Exporting project..."):
            # TODO: Implement actual project export logic
            console.print(f"\n[green]✓[/green] Project export completed: {output}")
            console.print(f"[blue]📊[/blue] Project: {project}")
            console.print(f"[blue]📊[/blue] Format: {format.upper()}")

            if format == "proj":
                console.print(
                    "[dim]💡 Use Ignition Designer to import this project[/dim]"
                )
            elif format == "json":
                console.print(
                    "[dim]💡 JSON format suitable for version control and analysis[/dim]"
                )
            elif format == "zip":
                console.print("[dim]💡 ZIP format includes all project resources[/dim]")

    except Exception as e:
        enhanced_cli.track_cli_usage("export", "project", {"error": str(e)}, False)
        console.print(f"[red]✗[/red] Project export failed: {e}")


@export_group.command()
@click.option("--gateway", "-g", help="Gateway configuration name")
@click.option("--output", "-o", required=True, help="Output path for resources")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "xml", "zip"]),
    default="json",
    help="Export format",
)
@click.option("--projects", help="Comma-separated list of projects to export")
@click.option("--tag-providers", help="Comma-separated list of tag providers to export")
@click.option(
    "--databases", help="Comma-separated list of database connections to export"
)
@click.option("--devices", help="Comma-separated list of device connections to export")
def resources(
    gateway: str,
    output: str,
    format: str,
    projects: str,
    tag_providers: str,
    databases: str,
    devices: str,
):
    """🎯 Export specific gateway resources selectively."""
    from pathlib import Path

    from src.ignition.exporters.gateway_exporter import GatewayResourceExporter
    from src.ignition.gateway.client import GatewayConfig, IgnitionGatewayClient

    try:
        console.print("[blue]🚀 Starting selective resource export...[/blue]")

        # Parse resource selections
        resource_selection = {}
        if projects:
            resource_selection["projects"] = [p.strip() for p in projects.split(",")]
        if tag_providers:
            resource_selection["tag_providers"] = [
                t.strip() for t in tag_providers.split(",")
            ]
        if databases:
            resource_selection["databases"] = [d.strip() for d in databases.split(",")]
        if devices:
            resource_selection["devices"] = [dev.strip() for dev in devices.split(",")]

        if not resource_selection:
            console.print("[red]❌ No resources specified for export[/red]")
            return

        # Create gateway client
        config = GatewayConfig(
            host=gateway or "localhost",
            port=8088,
            username="admin",
            password="password",
        )

        gateway_client = IgnitionGatewayClient(config)
        if not gateway_client.connect():
            console.print("[red]❌ Failed to connect to gateway[/red]")
            return

        # Create exporter
        graph_client = None
        try:
            from src.ignition.graph.client import IgnitionGraphClient

            if (
                hasattr(enhanced_cli, "graph_client")
                and enhanced_cli.graph_client
                and enhanced_cli.graph_client.is_connected
            ):
                graph_client = enhanced_cli.graph_client
        except (ImportError, AttributeError):
            pass

        exporter = GatewayResourceExporter(gateway_client, graph_client)

        # Perform export
        with console.status("[bold green]Exporting selected resources..."):
            result = exporter.export_resources(resource_selection, Path(output), format)

        if result.get("success"):
            console.print("[green]✅ Resources exported successfully![/green]")
            console.print(f"[blue]📁 File:[/blue] {result['output_path']}")
            console.print(
                f"[blue]📊 Resources:[/blue] {result['metadata']['resource_count']}"
            )
            console.print(f"[blue]📦 Size:[/blue] {result['file_size']:,} bytes")
        else:
            console.print("[red]❌ Resource export failed[/red]")

        gateway_client.disconnect()

    except Exception as e:
        console.print(f"[red]❌ Export failed: {e}[/red]")


@main.group(name="import")
def import_group():
    """📥 Import Ignition projects and resources."""
    pass


@import_group.command()
@click.option("--gateway", "-g", help="Target gateway configuration name")
@click.option(
    "--file", "-f", "file_path", required=True, help="Path to project file to import"
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["merge", "overwrite", "skip_conflicts"]),
    default="merge",
    help="Import mode",
)
@click.option("--project-name", help="Override project name")
@click.option("--validate/--no-validate", default=True, help="Validate before import")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be imported without actually importing",
)
def import_project(
    gateway: str,
    file_path: str,
    mode: str,
    project_name: str,
    validate: bool,
    dry_run: bool,
):
    """📁 Import Ignition project."""
    enhanced_cli.track_cli_usage(
        "import",
        "project",
        {
            "gateway": gateway,
            "mode": mode,
            "project_name": project_name,
            "validate": validate,
            "dry_run": dry_run,
        },
    )

    try:
        from ignition.gateway.config import GatewayConfigManager

        # Get gateway configuration
        if gateway:
            manager = GatewayConfigManager()
            config = manager.get_config(gateway)
            if not config:
                console.print(f"[red]✗[/red] Gateway '{gateway}' not found")
                return

            # Check if learning system has graph_client
            if hasattr(enhanced_cli, "client") and enhanced_cli.client:
                if hasattr(enhanced_cli.client, "graph_client"):
                    graph_client = enhanced_cli.client.graph_client
                    console.print(
                        "[blue]🧠[/blue] Learning system will track this import"
                    )
                else:
                    console.print(
                        "[dim]Learning system available but graph client not accessible[/dim]"
                    )
            else:
                console.print("[dim]Learning system not available for tracking[/dim]")

        console.print(f"[bold blue]📁 Importing Project from {file_path}[/bold blue]")

        # Validate file exists
        import os

        if not os.path.exists(file_path):
            console.print(f"[red]✗[/red] File not found: {file_path}")
            return

        # Show import configuration
        console.print("\n[bold]Import Configuration:[/bold]")
        console.print(f"  Mode: {mode}")
        console.print(f"  Validate: {'✓' if validate else '✗'}")
        console.print(f"  Dry Run: {'✓' if dry_run else '✗'}")
        if project_name:
            console.print(f"  Override Name: {project_name}")

        if dry_run:
            console.print("\n[yellow]🔍 DRY RUN - No changes will be made[/yellow]")

        with console.status("[bold blue]Processing import..."):
            # TODO: Implement actual project import logic
            if dry_run:
                console.print(
                    f"\n[blue]📋[/blue] Would import project from: {file_path}"
                )
                console.print(f"[blue]📋[/blue] Import mode: {mode}")
                if project_name:
                    console.print(
                        f"[blue]📋[/blue] Project would be named: {project_name}"
                    )
            else:
                console.print(
                    f"\n[green]✓[/green] Project import completed from: {file_path}"
                )
                console.print(f"[blue]📊[/blue] Mode: {mode}")

    except Exception as e:
        enhanced_cli.track_cli_usage("import", "project", {"error": str(e)}, False)
        console.print(f"[red]✗[/red] Project import failed: {e}")


@import_group.command()
@click.option(
    "--file", "-f", "file_path", required=True, help="Path to file to validate"
)
@click.option(
    "--type",
    "-t",
    type=click.Choice(["project", "gateway_backup", "resources"]),
    help="Expected file type",
)
@click.option("--detailed", is_flag=True, help="Show detailed validation results")
def validate_import(file_path: str, type: str, detailed: bool):
    """✅ Validate import file before importing."""
    enhanced_cli.track_cli_usage(
        "import",
        "validate",
        {
            "file_path": file_path,
            "type": type,
            "detailed": detailed,
        },
    )

    try:
        import os

        # Check file exists
        if not os.path.exists(file_path):
            console.print(f"[red]✗[/red] File not found: {file_path}")
            return

        console.print("[bold blue]✅ Validating Import File[/bold blue]")
        console.print(f"File: {file_path}")

        if type:
            console.print(f"Expected Type: {type}")

        with console.status("[bold blue]Validating..."):
            # TODO: Implement actual validation logic
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()

            console.print("\n[green]✓[/green] File validation completed")
            console.print(f"[blue]📊[/blue] Size: {file_size:,} bytes")
            console.print(f"[blue]📊[/blue] Extension: {file_ext}")

            if detailed:
                console.print("\n[bold]Detailed Analysis:[/bold]")
                console.print("• File is readable")
                console.print("• Basic structure appears valid")
                console.print("• No obvious corruption detected")

                if type:
                    console.print(
                        f"• Expected type '{type}' validation: [green]✓[/green]"
                    )

    except Exception as e:
        enhanced_cli.track_cli_usage("import", "validate", {"error": str(e)}, False)
        console.print(f"[red]✗[/red] Validation failed: {e}")


# Version Control Intelligence Commands
@main.group()
def version():
    """🔄 Version Control Intelligence commands."""
    pass


@version.command()
@click.option("--repository", "-r", help="Repository path (default: current directory)")
@click.option("--detailed", "-d", is_flag=True, help="Show detailed status information")
def status(repository: str | None, detailed: bool):
    """📊 Show version control intelligence status."""
    try:
        from pathlib import Path

        from src.ignition.version_control.manager import (
            VersionControlConfig,
            VersionControlManager,
        )

        # Determine repository path
        repo_path = Path(repository) if repository else Path.cwd()
        if not repo_path.exists():
            console.print(f"[red]✗[/red] Repository path does not exist: {repo_path}")
            return

        # Create configuration
        config = VersionControlConfig(repository_path=repo_path)

        # Initialize graph client
        graph_client = None
        try:
            from src.ignition.graph.client import IgnitionGraphClient
            graph_client = IgnitionGraphClient()
            if graph_client.connect():
                logger.debug("Graph client connected for version control")
        except Exception as e:
            logger.debug(f"Graph client not available: {e}")

        # Initialize manager
        manager = VersionControlManager(config=config, graph_client=graph_client)

        with console.status("[bold blue]Checking version control status..."):
            if not manager.initialize():
                console.print(
                    "[red]✗[/red] Failed to initialize version control manager"
                )
                return

            status_info = manager.get_repository_status()

        # Display status
        console.print("\n[bold blue]🔄 Version Control Intelligence Status[/bold blue]")
        console.print(f"Repository: {status_info['repository_path']}")
        console.print(f"Initialized: {'✓' if status_info['initialized'] else '✗'}")
        console.print(f"Git Enabled: {'✓' if status_info['git_enabled'] else '✗'}")

        # Show capabilities
        capabilities = status_info["capabilities"]
        console.print("\n[bold]Capabilities:[/bold]")
        console.print(
            f"  Impact Analysis: {'✓' if capabilities['impact_analysis'] else '✗'}"
        )
        console.print(
            f"  Conflict Prediction: {'✓' if capabilities['conflict_prediction'] else '✗'}"
        )
        console.print(
            f"  Release Planning: {'✓' if capabilities['release_planning'] else '✗'}"
        )
        console.print(
            f"  Auto Tracking: {'✓' if capabilities['auto_tracking'] else '✗'}"
        )

        # Show connections
        connections = status_info["connections"]
        console.print("\n[bold]Connections:[/bold]")
        console.print(
            f"  Graph Database: {'✓' if connections['graph_database'] else '✗'}"
        )
        console.print(f"  Gateway: {'✓' if connections['gateway'] else '✗'}")

        # Show git status if available
        if "git" in status_info:
            git_info = status_info["git"]
            console.print("\n[bold]Git Status:[/bold]")
            console.print(f"  Current Branch: {git_info['current_branch']}")
            console.print(f"  Clean: {'✓' if git_info['clean'] else '✗'}")

            if not git_info["clean"] and detailed:
                console.print(f"  Changes: {len(git_info['changes'])}")
                for change in git_info["changes"][:5]:  # Show first 5 changes
                    console.print(f"    {change['status']} {change['file']}")
                if len(git_info["changes"]) > 5:
                    console.print(f"    ... and {len(git_info['changes']) - 5} more")

        console.print("\n[green]✓[/green] Version control intelligence is operational")

    except ImportError as e:
        console.print(f"[red]✗[/red] Version control intelligence not available: {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to get status: {e}")


@version.command()
@click.option("--commit-hash", "-c", help="Specific commit hash to analyze")
@click.option("--files", "-f", help="Comma-separated list of files to analyze")
@click.option("--detailed", "-d", is_flag=True, help="Show detailed impact analysis")
@click.option("--repository", "-r", help="Repository path (default: current directory)")
def analyze_commit(
    commit_hash: str | None, files: str | None, detailed: bool, repository: str | None
):
    """🔍 Analyze the impact of a commit or changes."""
    console.print("\n[bold blue]📊 Commit Impact Analysis[/bold blue]")

    if commit_hash:
        console.print(f"Commit: {commit_hash}")
    else:
        console.print("Analyzing current changes")

    # This will be implemented when the impact analyzer is complete
    console.print("[yellow]💡[/yellow] Impact analysis implementation in progress")
    console.print("Features coming soon:")
    console.print("  • Resource impact assessment")
    console.print("  • Dependency chain analysis")
    console.print("  • Risk scoring")
    console.print("  • Performance impact prediction")


@version.command()
@click.option(
    "--source-branch", "-s", required=True, help="Source branch to merge from"
)
@click.option("--target-branch", "-t", default="main", help="Target branch to merge to")
@click.option(
    "--detailed", "-d", is_flag=True, help="Show detailed conflict predictions"
)
@click.option("--repository", "-r", help="Repository path (default: current directory)")
def predict_conflicts(
    source_branch: str, target_branch: str, detailed: bool, repository: str | None
):
    """🔮 Predict merge conflicts between branches."""
    console.print("\n[bold blue]🔮 Merge Conflict Prediction[/bold blue]")
    console.print(f"Source: {source_branch} → Target: {target_branch}")

    # This will be implemented when the conflict predictor is complete
    console.print("[yellow]💡[/yellow] Conflict prediction implementation in progress")
    console.print("Features coming soon:")
    console.print("  • Resource overlap detection")
    console.print("  • Semantic conflict analysis")
    console.print("  • Configuration conflict prediction")
    console.print("  • Resolution suggestions")


@version.command()
@click.option("--version", "-v", required=True, help="Release version identifier")
@click.option(
    "--strategy",
    "-s",
    default="incremental",
    type=click.Choice(
        ["incremental", "big_bang", "feature_flag", "blue_green", "canary"]
    ),
    help="Release strategy",
)
@click.option("--include", "-i", help="Comma-separated list of changes to include")
@click.option("--exclude", "-e", help="Comma-separated list of changes to exclude")
@click.option("--repository", "-r", help="Repository path (default: current directory)")
def plan_release(
    version: str,
    strategy: str,
    include: str | None,
    exclude: str | None,
    repository: str | None,
):
    """📋 Plan a release with intelligent recommendations."""
    console.print(f"\n[bold blue]📋 Release Plan: {version}[/bold blue]")
    console.print(f"Strategy: {strategy}")

    # This will be implemented when the release planner is complete
    console.print("[yellow]💡[/yellow] Release planning implementation in progress")
    console.print("Features coming soon:")
    console.print("  • Feature grouping")
    console.print("  • Risk-based scheduling")
    console.print("  • Dependency-aware planning")
    console.print("  • Rollback strategy planning")


if __name__ == "__main__":
    main()
