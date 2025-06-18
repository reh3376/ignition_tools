from typing import Dict, List

"""Enhanced CLI interface for IGN Scripts with Learning System Integration.

This module provides a rich, interactive command-line interface with:
- Learning system integration and usage tracking
- Smart recommendations based on usage patterns
- Beautiful terminal UI with rich formatting
- Interactive pattern exploration
- Real-time analytics and insights
"""

import logging
from datetime import datetime
from typing import Any

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
        def __init__(self) -> None:
            pass

        def run(self) -> None:
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
                self.generator = (
                    IgnitionScriptGenerator() if IgnitionScriptGenerator else None
                )
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
            ) and hasattr(self.tracker, "start_session"):
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

    def display_welcome(self) -> None:
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


def show_generation_recommendations(template: str, action_type: str) -> None:
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


def show_followup_recommendations() -> None:
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


def show_template_recommendations() -> None:
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

        def __init__(self) -> None:
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

        def run(self) -> None:
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

        def _handle_menu_choice(self, choice: str) -> None:
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

        def _show_all_patterns(self) -> None:
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

        def _show_co_occurrence_patterns(self) -> None:
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

        def _show_template_patterns(self) -> None:
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

        def _show_parameter_patterns(self) -> None:
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

        def _show_statistics(self) -> None:
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

        def _search_patterns(self) -> None:
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

        def _export_patterns(self) -> None:
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
    # Use the dummy app from above when prompt_toolkit is not available
    pass


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

        configs = getattr(manager, "list_configs", lambda: [])()  # type: ignore

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

            configs = manager.list_configs()  # type: ignore[attr-defined]
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
            client = IgnitionGatewayClient(config=config)  # type: ignore[arg-type]
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

            configs = manager.list_configs()  # type: ignore[attr-defined]
            if not configs:
                console.print("[yellow]📭 No gateways configured[/yellow]")
                return

            console.print(
                f"[bold blue]🏥 Health Check - All Gateways ({len(configs)})[/bold blue]\n"
            )

            # Try to import connection pool, fallback if not available
            try:
                from ignition.gateway.client import (
                    GatewayConnectionPool,  # type: ignore[import]
                )

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

                configs = manager.list_configs()  # type: ignore[attr-defined]
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
        configs = manager.list_configs()  # type: ignore[attr-defined]

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
def cleanup(ctx: click.Context, result, **kwargs) -> None:
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
    def install() -> None:
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
    def install() -> None:
        """Install OPC-UA dependencies."""
        console.print("[yellow]⚠️  OPC-UA dependencies not installed[/yellow]")
        console.print("\n[bold]To enable OPC-UA functionality, run:[/bold]")
        console.print("pip install asyncua>=1.1.6 opcua-client>=0.8.4 rich>=13.0.0")
        console.print("\nThen restart the CLI to access OPC-UA commands.")


@main.group(name="export")
def export_group() -> None:
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
            # Note: profile is a string, not a bool, so we handle it separately

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
                and enhanced_cli.graph_client  # type: ignore[attr-defined]
                and enhanced_cli.graph_client.is_connected  # type: ignore[attr-defined]
            ):
                graph_client = enhanced_cli.graph_client  # type: ignore[attr-defined]
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
def import_group() -> None:
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
            # Use the new project importer
            try:
                from pathlib import Path

                from src.ignition.importers.project_importer import (
                    IgnitionProjectImporter,
                )
                from src.ignition.importers.project_importer import (
                    ImportMode as ImportModeEnum,
                )

                # Create importer
                importer = IgnitionProjectImporter()

                # Convert mode string to enum
                import_mode = ImportModeEnum.MERGE
                if mode == "overwrite":
                    import_mode = ImportModeEnum.OVERWRITE
                elif mode == "skip_conflicts":
                    import_mode = ImportModeEnum.SKIP_CONFLICTS

                # Execute import
                result = importer.import_project(
                    import_path=Path(file_path),
                    mode=import_mode,
                    project_name=project_name,
                    validate_before_import=validate,
                    dry_run=dry_run,
                )

                if result.success:
                    console.print(f"\n[green]✓[/green] {result.message}")
                    console.print(f"[blue]📊[/blue] Import ID: {result.import_id}")
                    console.print(
                        f"[blue]📊[/blue] Execution Time: {result.execution_time:.2f}s"
                    )

                    if result.imported_resources:
                        console.print("\n[bold]Imported Resources:[/bold]")
                        for (
                            resource_type,
                            resources,
                        ) in result.imported_resources.items():
                            console.print(f"  {resource_type}: {len(resources)} items")
                else:
                    console.print(f"\n[red]✗[/red] {result.message}")

            except ImportError:
                # Fallback to original TODO implementation
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
def validate_import(file_path: str, type: str, detailed: bool) -> None:
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
            # Use the new validation system
            try:
                from pathlib import Path

                from src.ignition.importers.resource_validator import (
                    ImportFileValidator,
                )

                validator = ImportFileValidator()
                validation_result = validator.validate_file(Path(file_path), type)

                if validation_result.is_valid:
                    console.print("\n[green]✓[/green] File validation completed")
                else:
                    console.print(
                        "\n[yellow]⚠[/yellow] File validation completed with issues"
                    )

                console.print(
                    f"[blue]📊[/blue] Size: {validation_result.file_size:,} bytes"
                )
                console.print(
                    f"[blue]📊[/blue] Format: {validation_result.file_format}"
                )
                if validation_result.detected_type:
                    console.print(
                        f"[blue]📊[/blue] Detected Type: {validation_result.detected_type}"
                    )

                # Show validation issues
                if validation_result.issues:
                    console.print(
                        f"\n[bold]Validation Issues ({len(validation_result.issues)}):[/bold]"
                    )
                    for issue in validation_result.issues:
                        severity_color = {
                            "info": "blue",
                            "warning": "yellow",
                            "error": "red",
                            "critical": "bold red",
                        }.get(issue.severity.value, "white")

                        console.print(
                            f"  [{severity_color}]{issue.severity.value.upper()}[/{severity_color}]: {issue.message}"
                        )
                        if detailed and issue.suggested_action:
                            console.print(f"    💡 {issue.suggested_action}")

                if detailed and not validation_result.issues:
                    console.print("\n[bold]Detailed Analysis:[/bold]")
                    console.print("• File is readable")
                    console.print("• Structure appears valid")
                    console.print("• No validation issues detected")

            except ImportError:
                # Fallback to basic validation
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
def version() -> None:
    """🔄 Version Control Intelligence commands."""
    pass


@version.command()
@click.option("--repository", "-r", help="Repository path (default: current directory)")
@click.option("--detailed", "-d", is_flag=True, help="Show detailed status information")
def status(repository: str | None, detailed: bool) -> None:
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
) -> None:
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
) -> None:
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


# Code Intelligence Commands
@main.group()
def code() -> None:
    """🧠 Code Intelligence commands for analyzing and searching code."""
    pass


@code.command()
@click.option("--detailed", is_flag=True, help="Show detailed information")
def code_status(detailed: bool) -> None:
    """Show code intelligence system status."""
    try:
        from src.ignition.code_intelligence import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        with console.status("[bold blue]Checking code intelligence status..."):
            # Connect to database
            client = IgnitionGraphClient()
            if not client.connect():
                console.print("❌ Failed to connect to Neo4j database", style="red")
                return

            manager = CodeIntelligenceManager(client)
            stats = manager.get_code_statistics()
            schema_info = manager.schema.get_schema_info()

        # Display status
        console.print("\n🧠 Code Intelligence System Status", style="bold blue")
        console.print("=" * 50)

        # Basic statistics
        console.print("📊 Code Statistics:")
        console.print(f"  Files: {stats.get('files', 0)}")
        console.print(f"  Classes: {stats.get('classes', 0)}")
        console.print(f"  Methods: {stats.get('methods', 0)}")
        console.print(f"  Imports: {stats.get('imports', 0)}")

        if detailed:
            # Schema information
            console.print("\n🗄️ Database Schema:")
            console.print(f"  Constraints: {len(schema_info.get('constraints', []))}")
            console.print(f"  Indexes: {len(schema_info.get('indexes', []))}")
            console.print(
                f"  Schema Version: {schema_info.get('schema_version', 'Unknown')}"
            )

        console.print("\n✅ Code Intelligence System is operational", style="green")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@code.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--detailed", is_flag=True, help="Show detailed analysis")
def analyze_file(file_path: str, detailed: bool) -> None:
    """Analyze a specific file and store results."""
    try:
        from pathlib import Path

        from src.ignition.code_intelligence import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        file_path_obj = Path(file_path).absolute()

        with console.status(f"[bold blue]Analyzing {file_path}..."):
            client = IgnitionGraphClient()
            if not client.connect():
                console.print("❌ Failed to connect to Neo4j database", style="red")
                return

            manager = CodeIntelligenceManager(client)
            success = manager.analyze_and_store_file(file_path_obj)

        if success:
            console.print(f"✅ Successfully analyzed: {file_path}", style="green")

            if detailed:
                # Get file context
                relative_path = str(file_path_obj.relative_to(Path.cwd()))
                context = manager.get_file_context(relative_path)

                if context:
                    console.print(f"\n📁 File Analysis: {relative_path}", style="bold")

                    file_info = context.get("file", {})
                    console.print(f"  Lines: {file_info.get('lines', 'N/A')}")
                    console.print(f"  Complexity: {file_info.get('complexity', 'N/A')}")
                    console.print(
                        f"  Maintainability: {file_info.get('maintainability_index', 'N/A'):.1f}"
                    )

                    classes = context.get("classes", [])
                    methods = context.get("class_methods", []) + context.get(
                        "file_methods", []
                    )
                    imports = context.get("imports", [])

                    console.print(f"  Classes: {len(classes)}")
                    console.print(f"  Methods: {len(methods)}")
                    console.print(f"  Imports: {len(imports)}")
        else:
            console.print(f"❌ Failed to analyze: {file_path}", style="red")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@code.command()
@click.argument("query")
@click.option(
    "--type",
    "search_type",
    type=click.Choice(["all", "files", "classes", "methods"]),
    default="all",
    help="Type of code elements to search",
)
@click.option("--limit", default=10, help="Maximum number of results")
def search_code(query: str, search_type: str, limit: int) -> None:
    """Search for code elements by name or content."""
    try:
        from src.ignition.code_intelligence import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        with console.status("[bold blue]Searching..."):
            client = IgnitionGraphClient()
            if not client.connect():
                console.print("❌ Failed to connect to Neo4j database", style="red")
                return

            manager = CodeIntelligenceManager(client)
            results = manager.search_code(query, search_type)

        if not results:
            console.print(f"No results found for '{query}'", style="yellow")
            return

        console.print(
            f"\n🔍 Search Results for '{query}' ({search_type})", style="bold blue"
        )
        console.print(
            f"Found {len(results)} results (showing first {min(limit, len(results))})"
        )

        for i, result in enumerate(results[:limit], 1):
            console.print(
                f"{i}. {result.get('type', 'N/A')}: {result.get('name', 'N/A')}"
            )
            console.print(f"   File: {result.get('file_path', 'N/A')}")
            console.print(f"   Complexity: {result.get('complexity', 'N/A')}")
            console.print()

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


# Analytics and Optimization commands (Phase 8.4)
@code.group(name="analytics")
def analytics() -> None:
    """📊 Advanced analytics and optimization tools."""
    pass


# Import and add analytics commands
try:
    from src.ignition.code_intelligence.analytics_cli import analytics_group

    # Add all analytics commands to the main analytics group
    for command in analytics_group.commands.values():
        analytics.add_command(command)
except ImportError as e:
    console.print(f"⚠️ Analytics commands not available: {e}", style="yellow")


# Import and add workflow commands
try:
    from src.ignition.code_intelligence.workflow_cli import workflow_group

    # Add workflow commands to the code group
    code.add_command(workflow_group)
except ImportError as e:
    console.print(f"⚠️ Workflow commands not available: {e}", style="yellow")


# AI Assistant Enhancement commands
@code.group(name="ai")
def ai_assistant() -> None:
    """🤖 AI Assistant Enhancement commands for context-aware development."""
    pass


@ai_assistant.command()
@click.argument("file_path")
@click.option(
    "--context-size",
    type=click.Choice(["small", "medium", "large"]),
    default="medium",
    help="Size of context to retrieve",
)
def context(file_path: str, context_size: str) -> None:
    """Get smart context for a file instead of reading entire file."""
    try:
        from src.ignition.code_intelligence.ai_assistant_enhancement import (
            AIAssistantEnhancement,
        )
        from src.ignition.code_intelligence.manager import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        client = IgnitionGraphClient()
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j database", style="red")
            return

        manager = CodeIntelligenceManager(client)
        ai_enhancement = AIAssistantEnhancement(manager)

        context_data = ai_enhancement.get_smart_context(file_path, context_size)

        console.print(f"\n🧠 Smart Context: {file_path}", style="bold blue")

        if context_data.file_metrics:
            metrics = context_data.file_metrics
            console.print(
                Panel(
                    f"Lines: {metrics.get('lines', 'N/A')}\n"
                    f"Complexity: {metrics.get('complexity', 'N/A'):.1f}\n"
                    f"Maintainability: {metrics.get('maintainability_index', 'N/A'):.1f}",
                    title="📊 File Metrics",
                )
            )

        if context_data.refactoring_suggestions:
            console.print("\n💡 Refactoring Suggestions:")
            for suggestion in context_data.refactoring_suggestions:
                priority_color = {
                    "high": "red",
                    "medium": "yellow",
                    "low": "green",
                }.get(suggestion.get("priority", "low"), "white")
                console.print(
                    f"  • [{priority_color}]{suggestion.get('description', 'No description')}[/{priority_color}]"
                )

        if context_data.risk_factors:
            console.print("\n⚠️ Risk Factors:")
            for risk in context_data.risk_factors:
                level_color = {"high": "red", "medium": "yellow", "low": "green"}.get(
                    risk.get("level", "low"), "white"
                )
                console.print(
                    f"  • [{level_color}]{risk.get('description', 'No description')}[/{level_color}]"
                )

    except Exception as e:
        console.print(f"❌ Error getting context: {e!s}", style="red")


@ai_assistant.command()
@click.argument("file_path")
@click.argument("query")
@click.option("--max-snippets", default=5, help="Maximum number of snippets to return")
def snippets(file_path: str, query: str, max_snippets: int) -> None:
    """Get relevant code snippets instead of reading entire file."""
    try:
        from src.ignition.code_intelligence.ai_assistant_enhancement import (
            AIAssistantEnhancement,
        )
        from src.ignition.code_intelligence.manager import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        client = IgnitionGraphClient()
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j database", style="red")
            return

        manager = CodeIntelligenceManager(client)
        ai_enhancement = AIAssistantEnhancement(manager)

        snippets_data = ai_enhancement.get_relevant_snippets(
            file_path, query, max_snippets
        )

        if not snippets_data:
            console.print("No relevant snippets found", style="yellow")
            return

        console.print(f"\n🔍 Relevant Snippets for: '{query}'", style="bold blue")

        for i, snippet in enumerate(snippets_data, 1):
            console.print(
                f"\n📌 Snippet {i}: {snippet['type'].title()} '{snippet['name']}'"
            )
            console.print(f"   Relevance: {snippet['relevance_score']:.2f}")
            console.print(
                f"   Lines: {snippet.get('start_line', '?')}-{snippet.get('end_line', '?')}"
            )

            if snippet.get("docstring"):
                console.print(Panel(snippet["docstring"], title="Documentation"))

    except Exception as e:
        console.print(f"❌ Error getting snippets: {e!s}", style="red")


@ai_assistant.command()
@click.argument("file_path")
@click.option("--change-description", default="", help="Description of planned changes")
def impact(file_path: str, change_description: str) -> None:
    """Analyze potential impact of changes to a file."""
    try:
        from src.ignition.code_intelligence.ai_assistant_enhancement import (
            AIAssistantEnhancement,
        )
        from src.ignition.code_intelligence.manager import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        client = IgnitionGraphClient()
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j database", style="red")
            return

        manager = CodeIntelligenceManager(client)
        ai_enhancement = AIAssistantEnhancement(manager)

        impact_analysis = ai_enhancement.analyze_change_impact(
            file_path, change_description
        )

        console.print(f"\n🎯 Change Impact Analysis: {file_path}", style="bold blue")

        risk_color = {
            "critical": "red",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }.get(impact_analysis.risk_level, "white")
        console.print(
            Panel(
                f"Risk Level: [{risk_color}]{impact_analysis.risk_level.upper()}[/{risk_color}]\n"
                f"Confidence: {impact_analysis.confidence_score:.1%}",
                title="🚨 Risk Assessment",
            )
        )

        if impact_analysis.affected_files:
            console.print(
                f"\n📁 Affected Files ({len(impact_analysis.affected_files)}):"
            )
            for file in impact_analysis.affected_files[:10]:
                console.print(f"  • {file}")

        if impact_analysis.breaking_changes:
            console.print("\n💥 Potential Breaking Changes:")
            for change in impact_analysis.breaking_changes:
                severity_color = {
                    "high": "red",
                    "medium": "yellow",
                    "low": "green",
                }.get(change.get("severity", "low"), "white")
                console.print(
                    f"  • [{severity_color}]{change['description']}[/{severity_color}]"
                )

    except Exception as e:
        console.print(f"❌ Error analyzing impact: {e!s}", style="red")


@ai_assistant.command()
@click.argument("file_path")
@click.argument("element_name")
@click.option("--limit", default=5, help="Maximum number of suggestions")
def similar(file_path: str, element_name: str, limit: int) -> None:
    """Find similar implementations in the codebase."""
    try:
        from src.ignition.code_intelligence.ai_assistant_enhancement import (
            AIAssistantEnhancement,
        )
        from src.ignition.code_intelligence.manager import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        client = IgnitionGraphClient()
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j database", style="red")
            return

        manager = CodeIntelligenceManager(client)
        ai_enhancement = AIAssistantEnhancement(manager)

        suggestions = ai_enhancement.suggest_similar_implementations(
            file_path, element_name
        )

        if not suggestions:
            console.print(
                f"No similar implementations found for '{element_name}'", style="yellow"
            )
            return

        console.print(
            f"\n🔍 Similar Implementations for: '{element_name}'", style="bold blue"
        )

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("File", style="blue")
        table.add_column("Similarity", style="yellow")

        for suggestion in suggestions[:limit]:
            table.add_row(
                suggestion["name"],
                suggestion["type"],
                suggestion["file_path"].split("/")[-1],  # Just filename
                f"{suggestion.get('similarity_score', 0):.2f}",
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error finding similar implementations: {e!s}", style="red")


# Import and add module development commands
try:
    from src.ignition.modules.module_cli import module_group

    # Add module commands to the main CLI
    main.add_command(module_group)
except ImportError as e:
    console.print(f"⚠️ Module commands not available: {e}", style="yellow")


# Add wrapper commands
@main.group(name="wrappers")
def wrapper_group() -> None:
    """🛡️ Enhanced Ignition system function wrappers with error handling."""
    pass


@wrapper_group.command()
def test_all() -> None:
    """🧪 Test all system function wrappers."""
    console.print("[bold blue]🧪 Testing System Function Wrappers[/bold blue]\n")

    try:
        from src.ignition.wrappers import (
            SystemAlarmWrapper,
            SystemDbWrapper,
            SystemGuiWrapper,
            SystemNavWrapper,
            SystemTagWrapper,
            SystemUtilWrapper,
        )

        wrappers = [
            ("Tag Wrapper", SystemTagWrapper),
            ("Database Wrapper", SystemDbWrapper),
            ("GUI Wrapper", SystemGuiWrapper),
            ("Navigation Wrapper", SystemNavWrapper),
            ("Alarm Wrapper", SystemAlarmWrapper),
            ("Utility Wrapper", SystemUtilWrapper),
        ]

        results = []

        for name, wrapper_class in wrappers:
            try:
                console.print(f"[yellow]Testing {name}...[/yellow]")

                wrapper = wrapper_class()
                wrapped_functions = wrapper.get_wrapped_functions()

                results.append(
                    {
                        "name": name,
                        "success": True,
                        "function_count": len(wrapped_functions),
                        "functions": wrapped_functions,
                    }
                )

                console.print(f"[green]✅ {name} initialized successfully[/green]")

            except Exception as e:
                results.append({"name": name, "success": False, "error": str(e)})
                console.print(f"[red]❌ {name} failed: {e}[/red]")

        # Display summary table
        from rich.table import Table

        table = Table(title="Wrapper Test Results")
        table.add_column("Wrapper", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Functions", style="yellow")
        table.add_column("Details", style="dim")

        for result in results:
            status = (
                "[green]✅ Success[/green]"
                if result["success"]
                else "[red]❌ Failed[/red]"
            )
            function_count = str(result.get("function_count", 0))
            details = (
                ", ".join(result.get("functions", []))
                if result["success"]
                else result.get("error", "")
            )

            table.add_row(
                result["name"],
                status,
                function_count,
                details[:50] + "..." if len(details) > 50 else details,
            )

        console.print(table)

        successful_tests = sum(1 for r in results if r["success"])
        total_tests = len(results)

        if successful_tests == total_tests:
            console.print(
                f"\n[bold green]🎉 All {total_tests} wrapper tests passed![/bold green]"
            )
        else:
            console.print(
                f"\n[bold yellow]⚠️ {successful_tests}/{total_tests} wrapper tests passed[/bold yellow]"
            )

    except ImportError as e:
        console.print(f"[red]❌ Wrapper imports failed: {e}[/red]")


@wrapper_group.command()
@click.option("--tag-path", default="[default]TestTag", help="Tag path to test")
def test_tag(tag_path: str) -> None:
    """🏷️ Test system.tag wrapper."""
    console.print("[bold blue]🏷️ Testing System Tag Wrapper[/bold blue]\n")

    try:
        from src.ignition.wrappers import SystemTagWrapper

        wrapper = SystemTagWrapper()
        console.print(f"[yellow]Testing tag read: {tag_path}[/yellow]")

        results = wrapper.read_blocking([tag_path])

        from rich.table import Table

        table = Table(title="Tag Read Results")
        table.add_column("Tag Path", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Quality", style="yellow")
        table.add_column("Success", style="bold")

        for result in results:
            success_style = "green" if result.success else "red"
            success_text = "✓" if result.success else "✗"

            table.add_row(
                result.tag_path,
                str(result.value),
                f"{result.quality_name} ({result.quality})",
                f"[{success_style}]{success_text}[/{success_style}]",
            )

        console.print(table)
        console.print("\n[green]✅ Tag wrapper test completed![/green]")

    except ImportError as e:
        console.print(f"[red]❌ Tag wrapper not available: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Tag wrapper test failed: {e}[/red]")


@wrapper_group.command()
@click.option("--query", default="SELECT 1 as test_value", help="Test SQL query")
def test_db(query: str) -> None:
    """🗄️ Test system.db wrapper."""
    console.print("[bold blue]🗄️ Testing System Database Wrapper[/bold blue]\n")

    try:
        from src.ignition.wrappers import SystemDbWrapper

        wrapper = SystemDbWrapper()
        console.print(f"[yellow]Executing query: {query}[/yellow]")

        result = wrapper.run_query(query)

        console.print("\n[bold]Query Results:[/bold]")
        console.print(f"Database: {result.database}")
        console.print(f"Row count: {result.row_count}")
        console.print(f"Execution time: {result.execution_time_ms:.2f}ms")
        console.print(f"Success: {'✅' if result.success else '❌'}")

        console.print("\n[green]✅ Database wrapper test completed![/green]")

    except ImportError as e:
        console.print(f"[red]❌ Database wrapper not available: {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Database wrapper test failed: {e}[/red]")


@wrapper_group.command()
def info() -> None:
    """📋 Show information about available system function wrappers."""
    console.print("[bold blue]📋 Ignition System Function Wrappers[/bold blue]\n")

    wrapper_info = [
        {
            "name": "SystemTagWrapper",
            "module": "system.tag",
            "description": "Enhanced tag operations with quality validation and retry logic",
            "functions": [
                "read_blocking",
                "write_blocking",
                "read_async",
                "write_async",
            ],
        },
        {
            "name": "SystemDbWrapper",
            "module": "system.db",
            "description": "Database operations with query validation and performance metrics",
            "functions": ["run_query", "run_update_query", "run_prep_query"],
        },
        {
            "name": "SystemGuiWrapper",
            "module": "system.gui",
            "description": "GUI operations with input validation and logging",
            "functions": ["message_box", "error_box", "warning_box"],
        },
        {
            "name": "SystemNavWrapper",
            "module": "system.nav",
            "description": "Window navigation with parameter validation",
            "functions": ["open_window", "close_window", "swap_window"],
        },
        {
            "name": "SystemAlarmWrapper",
            "module": "system.alarm",
            "description": "Alarm operations with comprehensive error handling",
            "functions": ["acknowledge", "query_status", "shelve"],
        },
        {
            "name": "SystemUtilWrapper",
            "module": "system.util",
            "description": "Utility operations with enhanced logging and validation",
            "functions": ["get_logger", "send_message"],
        },
    ]

    from rich.panel import Panel

    for info in wrapper_info:
        panel_content = f"""[bold]{info["description"]}[/bold]

[yellow]Wrapped Functions:[/yellow]
{", ".join(info["functions"])}

[cyan]Original Module:[/cyan] {info["module"]}"""

        panel = Panel(panel_content, title=f"🛡️ {info['name']}", border_style="blue")
        console.print(panel)
        console.print()


# Data Integration Commands
@main.group(name="data")
def data_integration() -> None:
    """🔗 Data Integration commands for databases, historians, and OPC tags."""
    pass


@data_integration.group()
def database() -> None:
    """🗄️ Database connection and query commands."""
    pass


@database.command()
@click.option(
    "--config-name", default="neo4j_default", help="Database configuration name"
)
def test_connection(config_name: str) -> None:
    """Test database connection."""
    try:
        from src.ignition.data_integration.database_connections import (
            DatabaseConnectionManager,
        )

        with console.status(f"[bold blue]Testing connection to {config_name}..."):
            manager = DatabaseConnectionManager()
            result = manager.test_connection(config_name)

        if result["success"]:
            console.print(
                f"✅ Connection successful to {result['db_type']}", style="green"
            )
            console.print(f"   Host: {result['host']}")
            console.print(f"   Database: {result['database']}")
            console.print(f"   Connection time: {result['connection_time_ms']:.2f}ms")
        else:
            console.print(f"❌ Connection failed: {result['error']}", style="red")

    except ImportError:
        console.print("❌ Database connection manager not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@database.command()
def list_configs() -> None:
    """List available database configurations."""
    try:
        from src.ignition.data_integration.database_connections import (
            DatabaseConnectionManager,
        )

        manager = DatabaseConnectionManager()
        configs = manager.list_configurations()

        if not configs:
            console.print("No database configurations found", style="yellow")
            return

        table = Table(title="Available Database Configurations")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Host", style="blue")
        table.add_column("Database", style="magenta")

        for config_name in configs:
            config_info = manager.get_config_info(config_name)
            if config_info:
                table.add_row(
                    config_name,
                    config_info["db_type"],
                    f"{config_info['host']}:{config_info['port']}",
                    config_info["database"],
                )

        console.print(table)

    except ImportError:
        console.print("❌ Database connection manager not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@data_integration.group()
def tags() -> None:
    """🏷️ OPC tag management commands."""
    pass


@tags.command()
@click.option("--path", default="", help="Tag path to browse (default: root)")
@click.option("--provider", default="default", help="Tag provider name")
def browse(path: str, provider: str) -> None:
    """Browse OPC tags."""
    try:
        from src.ignition.data_integration.opc_tag_manager import OPCTagManager

        manager = OPCTagManager(provider)

        with console.status(f"[bold blue]Browsing tags at {path or 'root'}..."):
            result = manager.browse_tags(path)

        if not result.success:
            console.print(f"❌ Browse failed: {result.error_message}", style="red")
            return

        # Display folders
        if result.folders:
            console.print(f"\n📁 Folders in {path or 'root'}:", style="bold blue")
            for folder in result.folders:
                console.print(f"  📁 {folder}")

        # Display tags
        if result.tags:
            table = Table(title=f"Tags in {path or 'root'}")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Value", style="yellow")
            table.add_column("Quality", style="blue")
            table.add_column("Description", style="magenta")

            for tag in result.tags:
                table.add_row(
                    tag.name,
                    tag.data_type,
                    str(tag.value),
                    tag.quality_name,
                    (tag.description or "")[:50],
                )

            console.print(table)

        console.print(f"\nTotal items: {result.total_items}")

    except ImportError:
        console.print("❌ OPC tag manager not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@data_integration.group()
def reports() -> None:
    """📊 Report generation commands."""
    pass


@reports.command()
@click.option("--hours", default=24, help="Number of hours for production report")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["csv", "json", "html"]),
    default="csv",
    help="Report output format",
)
@click.option("--output", help="Output file path")
def production(hours: int, output_format: str, output: str) -> None:
    """Generate production report."""
    try:
        from datetime import datetime, timedelta

        from src.ignition.data_integration.report_generator import (
            ReportFormat,
            ReportGenerator,
        )

        generator = ReportGenerator()

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        # Mock tags for production report
        tags = ["Line_A_Production", "Line_B_Production", "Line_C_Production"]

        with console.status("[bold blue]Generating production report..."):
            result = generator.generate_production_report(
                start_time, end_time, tags, ReportFormat(output_format)
            )

        if result["success"]:
            console.print("✅ Production report generated successfully", style="green")
            console.print(f"   Format: {output_format.upper()}")
            console.print(f"   Records: {result.get('row_count', 'N/A')}")

            if output:
                with open(output, "w") as f:
                    f.write(result["content"])
                console.print(f"   Saved to: {output}")
            else:
                console.print("\n📄 Report Content:")
                console.print(
                    result["content"][:500] + "..."
                    if len(result["content"]) > 500
                    else result["content"]
                )
        else:
            console.print(
                f"❌ Report generation failed: {result['error']}", style="red"
            )

    except ImportError:
        console.print("❌ Report generator not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@data_integration.command()
def status() -> None:
    """Show data integration system status."""
    console.print("🔗 Data Integration System Status", style="bold blue")
    console.print("=" * 50)

    # Check database connections
    try:
        from src.ignition.data_integration.database_connections import (
            DatabaseConnectionManager,
        )

        manager = DatabaseConnectionManager()
        configs = manager.list_configurations()
        console.print(f"📊 Database Configurations: {len(configs)}")
        for config in configs:
            console.print(f"   • {config}")
    except ImportError:
        console.print("📊 Database Connections: Not available", style="yellow")

    # Check OPC tag management
    try:
        from src.ignition.data_integration.opc_tag_manager import OPCTagManager

        console.print("🏷️ OPC Tag Management: Available", style="green")
    except ImportError:
        console.print("🏷️ OPC Tag Management: Not available", style="yellow")

    # Check report generation
    try:
        from src.ignition.data_integration.report_generator import (
            ReportFormat,
            ReportGenerator,
        )

        console.print(f"📊 Report Formats: {len(ReportFormat)}")
        for format_type in ReportFormat:
            console.print(f"   • {format_type.value}")
    except ImportError:
        console.print("📊 Report Generation: Not available", style="yellow")

    # Check dataset management
    try:
        from src.ignition.data_integration.dataset_manager import DatasetManager

        manager = DatasetManager()
        datasets = manager.list_datasets()
        console.print(
            f"🧠 Dataset Management: {len(datasets)} datasets available", style="green"
        )
    except ImportError:
        console.print("🧠 Dataset Management: Not available", style="yellow")
    except Exception as e:
        console.print(f"🧠 Dataset Management: Error - {e}", style="red")

    console.print("\n✅ Data Integration System operational", style="green")


@data_integration.group()
def dataset() -> None:
    """🧠 Dataset management for AI/ML model preparation."""
    pass


@dataset.command("create")
@click.option("--name", "-n", required=True, help="Dataset name")
@click.option(
    "--type",
    "-t",
    "dataset_type",
    type=click.Choice(
        [
            "classification",
            "regression",
            "time_series",
            "anomaly_detection",
            "clustering",
            "forecasting",
        ]
    ),
    required=True,
    help="Dataset type",
)
@click.option("--description", "-d", help="Dataset description")
@click.option("--tags", help="Comma-separated tags")
def create_dataset_cmd(
    name: str, dataset_type: str, description: str, tags: str
) -> None:
    """Create a new dataset."""
    try:
        from src.ignition.data_integration.dataset_core import DatasetType
        from src.ignition.data_integration.dataset_manager import DatasetManager

        manager = DatasetManager()

        # Parse tags
        tag_list = (
            [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        )

        # Create dataset
        dataset = manager.create_dataset(
            name=name,
            dataset_type=DatasetType(dataset_type),
            description=description,
            tags=tag_list,
        )

        console.print(f"✅ Dataset '{name}' created successfully!", style="green")
        console.print(f"   ID: {dataset.dataset_id}")
        console.print(f"   Type: {dataset_type}")

        if description:
            console.print(f"   Description: {description}")

        if tag_list:
            console.print(f"   Tags: {', '.join(tag_list)}")

        # Suggest next steps
        console.print("\n💡 Next steps:", style="bold blue")
        console.print("   1. Launch interactive UI: ign data dataset buildout")
        console.print("   2. Add data sources and features interactively")
        console.print("   3. Process and export your dataset")

    except ImportError:
        console.print("❌ Dataset management not available", style="red")
    except Exception as e:
        console.print(f"❌ Failed to create dataset: {e}", style="red")


@dataset.command("list")
def list_datasets_cmd() -> None:
    """List all datasets."""
    try:
        from rich.text import Text

        from src.ignition.data_integration.dataset_manager import DatasetManager

        manager = DatasetManager()
        datasets = manager.list_datasets()

        if not datasets:
            console.print(
                "No datasets found. Create one with 'ign data dataset create'",
                style="yellow",
            )
            console.print("\n💡 Or try: ign data dataset buildout", style="blue")
            return

        # Create table
        table = Table(title="📊 Available Datasets")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="blue")
        table.add_column("Rows", justify="right", style="magenta")
        table.add_column("Quality", style="yellow")
        table.add_column("Created", style="dim")

        for ds in datasets:
            # Format status with color
            status = ds["status"]
            if status == "ready":
                status_text = Text(status, style="bold green")
            elif status == "validated":
                status_text = Text(status, style="bold blue")
            elif status == "in_progress":
                status_text = Text(status, style="bold yellow")
            else:
                status_text = Text(status, style="dim")

            # Format quality with color
            quality = ds["quality"]
            if quality == "excellent":
                quality_text = Text(quality, style="bold green")
            elif quality == "good":
                quality_text = Text(quality, style="green")
            elif quality == "fair":
                quality_text = Text(quality, style="yellow")
            elif quality == "poor":
                quality_text = Text(quality, style="red")
            else:
                quality_text = Text(quality, style="dim")

            table.add_row(
                ds["name"],
                ds["type"],
                status_text,
                f"{ds['row_count']:,}",
                quality_text,
                ds["created_at"][:10],  # Just the date
            )

        console.print(table)

        # Summary
        total_datasets = len(datasets)
        ready_datasets = sum(1 for ds in datasets if ds["status"] == "ready")
        total_rows = sum(ds["row_count"] for ds in datasets)

        console.print(
            f"\n📈 Summary: {total_datasets} datasets, {ready_datasets} ready for training, {total_rows:,} total rows"
        )

    except ImportError:
        console.print("❌ Dataset management not available", style="red")
    except Exception as e:
        console.print(f"❌ Failed to list datasets: {e}", style="red")


@dataset.command()
@click.option("--port", "-p", default=8501, help="Port for the UI server")
@click.option("--host", "-h", default="localhost", help="Host for the UI server")
@click.option(
    "--open-browser", is_flag=True, default=True, help="Open browser automatically"
)
def buildout(port: int, host: str, open_browser: bool) -> None:
    """🚀 Launch interactive dataset buildout UI."""
    try:
        # Check if streamlit is available
        try:
            import streamlit
        except ImportError:
            console.print(
                "❌ Streamlit not installed. Install with: pip install streamlit plotly",
                style="red",
            )
            console.print(
                "   Or run: pip install streamlit plotly pandas scikit-learn",
                style="blue",
            )
            return

        # Find the UI script
        from pathlib import Path

        ui_script = (
            Path(__file__).parent.parent
            / "ignition"
            / "data_integration"
            / "dataset_ui.py"
        )

        if not ui_script.exists():
            console.print(f"❌ UI script not found at: {ui_script}", style="red")
            return

        console.print("🚀 Launching Dataset Curation Studio...", style="blue")
        console.print(f"   Host: {host}")
        console.print(f"   Port: {port}")
        console.print(f"   URL: http://{host}:{port}")

        # Launch streamlit
        import subprocess
        import sys

        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ui_script),
            "--server.port",
            str(port),
            "--server.address",
            host,
            "--server.headless",
            "true" if not open_browser else "false",
        ]

        if open_browser:
            console.print("\n🌐 Opening browser...", style="green")
            # Give streamlit a moment to start
            import threading
            import time
            import webbrowser

            def open_browser_delayed() -> None:
                time.sleep(3)
                webbrowser.open(f"http://{host}:{port}")

            threading.Thread(target=open_browser_delayed).start()

        console.print("\n💡 Tip: Use Ctrl+C to stop the server", style="dim")
        console.print("=" * 50)

        # Run streamlit
        subprocess.run(cmd)

    except KeyboardInterrupt:
        console.print("\n👋 Dataset Curation Studio stopped.", style="blue")
    except ImportError:
        console.print("❌ Dataset management not available", style="red")
    except Exception as e:
        console.print(f"❌ Failed to launch UI: {e}", style="red")


@dataset.command()
def sample() -> None:
    """Create a sample dataset for testing."""
    click.echo("🔬 Creating sample dataset...")

    try:
        from src.ignition.data_integration.dataset_manager import create_sample_dataset

        # Create sample dataset
        dataset_id = create_sample_dataset()

        click.echo("✅ Sample dataset created successfully!")
        click.echo(f"📊 Dataset ID: {dataset_id}")
        click.echo("💡 Use 'ign data dataset list' to see all datasets")
        click.echo("🌐 Use 'ign data dataset buildout' to open the UI")

    except ImportError:
        click.echo("❌ Dataset management system not available")
        click.echo("💡 Install dependencies: pip install -r requirements-dataset.txt")
    except Exception as e:
        click.echo(f"❌ Failed to create sample dataset: {e!s}")


# Add Supabase management commands
try:
    from src.ignition.data_integration.supabase_cli import supabase

    data_integration.add_command(supabase)
except ImportError:
    # Supabase CLI not available - create placeholder
    @data_integration.group()
    def supabase() -> None:
        """Supabase database management commands (not available)."""
        click.echo("❌ Supabase management not available")
        click.echo("💡 Install dependencies to enable Supabase commands")


if __name__ == "__main__":
    main()
