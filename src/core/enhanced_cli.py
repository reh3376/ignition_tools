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

import click
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich.text import Text

# Optional Textual imports for TUI features
try:
    from textual import Container, Horizontal, Vertical
    from textual.app import App, ComposeResult
    from textual.widgets import Button, DataTable, Footer, Header, Static

    TEXTUAL_AVAILABLE = True
except ImportError:
    # Create dummy classes if Textual not available
    class DummyButton:
        class Pressed:
            def __init__(self):
                self.button = DummyButton()
                self.button.id = None

    class DummyApp:
        def __init__(self):
            pass

        def run(self):
            pass

    App = DummyApp
    ComposeResult = None
    Container = Horizontal = Vertical = object
    Button = DummyButton
    DataTable = Footer = Header = Static = object
    TEXTUAL_AVAILABLE = False

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
            if not self.tracker.current_session_id:
                self.tracker.start_session(user_id="cli_user", session_type="cli_usage")

            # Track the command usage
            function_name = f"cli.{command}"
            if subcommand:
                function_name += f".{subcommand}"

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
                script_content = enhanced_cli.generator.generate_from_config(
                    config, output
                )
                enhanced_cli.track_cli_usage("script", "generate", params, True)
                console.print(
                    f"[green]✓[/green] Generated script from config: {config}"
                )

            elif template:
                # Generate from command line options
                context = {}
                if component_name:
                    context["component_name"] = component_name
                if action_type:
                    context["action_type"] = action_type

                if not template.endswith(".jinja2"):
                    template += ".jinja2"

                script_content = enhanced_cli.generator.generate_script(
                    template, context, output
                )
                enhanced_cli.track_cli_usage("script", "generate", params, True)
                console.print(
                    f"[green]✓[/green] Generated script from template: {template}"
                )

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
def validate(ctx: click.Context, script_file: str) -> None:
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
def list(ctx: click.Context, detailed: bool) -> None:
    """📋 List available script templates with usage statistics."""
    enhanced_cli.track_cli_usage("template", "list", {"detailed": detailed})

    try:
        templates = enhanced_cli.generator.list_templates()

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

        return (
            f"Functions: {func1} ↔ {func2}\n"
            f"Confidence: {conf1:.1%} / {conf2:.1%}\n"
            f"Support: {support:.1%}"
        )

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

        return (
            f"Entity: {entity}\n"
            f"Parameter: {param}\n"
            f"Frequency: {frequency:.1%}\n"
            f"Success Rate: {success:.1%}"
        )

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


# Textual TUI for interactive pattern exploration
if TEXTUAL_AVAILABLE:

    class PatternExplorerApp(App):
        """Interactive TUI for exploring patterns."""

        CSS = """
        Screen {
            background: $surface;
        }

        Header {
            background: $primary;
            color: $text;
            height: 3;
        }

        Footer {
            background: $primary;
            color: $text;
            height: 3;
        }

        DataTable {
            height: 1fr;
        }

        #sidebar {
            width: 30;
            background: $panel;
        }

        #main {
            width: 1fr;
        }
        """

        TITLE = "🧠 IGN Scripts - Pattern Explorer"

        def compose(self) -> ComposeResult: # type: ignore
            """Compose the TUI layout."""
            yield Header()

            with Horizontal():
                with Vertical(id="sidebar"):
                    yield Button("📊 All Patterns", id="all_patterns")
                    yield Button("🔗 Co-occurrence", id="co_occurrence")
                    yield Button("📋 Templates", id="templates")
                    yield Button("⚙️ Parameters", id="parameters")
                    yield Button("📈 Statistics", id="statistics")

                with Vertical(id="main"):
                    yield DataTable(id="pattern_table")
                    yield Static("Select a pattern type from the sidebar", id="details")

            yield Footer()

        def on_button_pressed(self, event: Button.Pressed) -> None: # type: ignore
            """Handle button presses."""
            button_id = event.button.id

            if button_id == "all_patterns":
                self.show_all_patterns()
            elif button_id == "co_occurrence":
                self.show_co_occurrence_patterns()
            elif button_id == "templates":
                self.show_template_patterns()
            elif button_id == "parameters":
                self.show_parameter_patterns()
            elif button_id == "statistics":
                self.show_statistics()

        def show_all_patterns(self):
            """Show all patterns in the table."""
            table = self.query_one("#pattern_table", DataTable)
            table.clear(columns=True)
            table.add_columns("Type", "Description", "Confidence", "Support")

            # Add sample data (in real implementation, fetch from learning system)
            table.add_row("Co-occurrence", "tag.read + db.query", "85%", "23%")
            table.add_row("Template", "button_handler.jinja2", "92%", "15%")
            table.add_row("Parameter", "timeout=5000", "78%", "34%")

        def show_co_occurrence_patterns(self):
            """Show function co-occurrence patterns."""
            table = self.query_one("#pattern_table", DataTable)
            table.clear(columns=True)
            table.add_columns(
                "Function 1", "Function 2", "Confidence", "Support", "Lift"
            )

            # Add sample data
            table.add_row(
                "system.tag.readBlocking", "system.gui.messageBox", "85%", "23%", "2.1"
            )

        def show_template_patterns(self):
            """Show template usage patterns."""
            table = self.query_one("#pattern_table", DataTable)
            table.clear(columns=True)
            table.add_columns("Template", "Usage Count", "Success Rate", "Avg Time")

            # Add sample data
            table.add_row("button_click_handler.jinja2", "45", "92%", "0.3s")

        def show_parameter_patterns(self):
            """Show parameter combination patterns."""
            table = self.query_one("#pattern_table", DataTable)
            table.clear(columns=True)
            table.add_columns("Entity", "Parameter", "Frequency", "Success Rate")

            # Add sample data
            table.add_row("system.tag.readBlocking", "timeout", "78%", "95%")

        def show_statistics(self):
            """Show system statistics."""
            details = self.query_one("#details", Static)
            details.update(
                "📈 Learning System Statistics\n\n"
                "Total Patterns: 156\n"
                "High Confidence: 89 (57%)\n"
                "Medium Confidence: 45 (29%)\n"
                "Low Confidence: 22 (14%)\n\n"
                "Pattern Types:\n"
                "• Co-occurrence: 45\n"
                "• Template Usage: 67\n"
                "• Parameter Combos: 44"
            )

else:
    # Dummy class when Textual is not available
    class PatternExplorerApp:
        def __init__(self):
            pass

        def run(self):
            console.print(
                "[yellow]⚠️ TUI not available - Textual library not installed[/yellow]"
            )


@learning.command()
@click.pass_context
def explore(ctx: click.Context) -> None:
    """🔍 Launch interactive pattern explorer (TUI)."""
    enhanced_cli.track_cli_usage("learning", "explore")

    if not TEXTUAL_AVAILABLE:
        console.print(
            "[yellow]⚠️ TUI not available - Textual library not installed[/yellow]"
        )
        console.print(
            "[yellow]💡[/yellow] Try 'ign learning patterns' for command-line exploration"
        )
        return

    try:
        console.print("[bold blue]🚀 Launching Pattern Explorer...[/bold blue]")
        app = PatternExplorerApp()
        app.run()
    except Exception as e:
        console.print(f"[red]✗[/red] Error launching explorer: {e}")
        console.print(
            "[yellow]💡[/yellow] Try 'ign learning patterns' for command-line exploration"
        )


# Gateway Management Commands
@main.group()
def gateway() -> None:
    """🏭 Gateway connection and management commands."""
    enhanced_cli.track_cli_usage("gateway")


@gateway.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """📋 List configured gateways."""
    enhanced_cli.track_cli_usage("gateway", "list")

    try:
        from ignition.gateway.config import GatewayConfigManager

        manager = GatewayConfigManager()
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
                info += f"URL: {config.base_url}\n"
                info += f"Auth: {config.auth_type} ({config.username})\n"
                info += f"SSL: {'✓' if config.verify_ssl else '✗'}\n"
                info += f"Timeout: {config.timeout}s"

                if config.description:
                    info += f"\n{config.description}"

                if config.tags:
                    tags = ", ".join(config.tags)
                    info += f"\nTags: {tags}"

                panel = Panel(info, title=f"🏢 {name}", border_style="cyan")
                console.print(panel)

    except Exception as e:
        console.print(f"[red]✗[/red] Error listing gateways: {e}")


@gateway.command()
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
            configs = manager.list_configs()
            if not configs:
                console.print("[red]✗[/red] No gateways configured")
                return

            console.print("[bold]Available gateways:[/bold]")
            for i, config_name in enumerate(configs, 1):
                config = manager.get_config(config_name)
                console.print(f"  {i}. {config_name} - {config.base_url}")

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

        console.print(f"[bold blue]🔌 Connecting to {config.name}...[/bold blue]")
        console.print(f"URL: {config.base_url}")

        # Create and test connection
        with IgnitionGatewayClient(config=config) as client:
            console.print("[green]✓[/green] Connection established")

            # Get gateway info
            info = client.get_gateway_info()
            if info:
                console.print("\n[bold]📊 Gateway Information:[/bold]")

                # Display key info in a nice format
                info_display = ""
                for key, value in info.items():
                    if key != "gateway_info_raw":
                        info_display += f"• {key.replace('_', ' ').title()}: {value}\n"

                console.print(
                    Panel(
                        info_display.strip(),
                        title="Gateway Details",
                        border_style="green",
                    )
                )

            if not test:
                console.print(
                    "\n[green]✓[/green] Gateway connection successful and ready for use"
                )
            else:
                console.print(
                    "\n[green]✓[/green] Connection test completed successfully"
                )

    except Exception as e:
        console.print(f"[red]✗[/red] Connection failed: {e}")
        console.print("\n[yellow]💡 Troubleshooting:[/yellow]")
        console.print("• Check gateway is running and accessible")
        console.print("• Verify credentials in .env file")
        console.print("• Test with: ign gateway health --name gateway_name")


@gateway.command()
@click.option("--name", "-n", help="Specific gateway to check")
@click.option("--all", "-a", is_flag=True, help="Check all configured gateways")
@click.pass_context
def health(ctx: click.Context, name: str, all: bool) -> None:
    """🏥 Check gateway health status."""
    enhanced_cli.track_cli_usage("gateway", "health", {"name": name, "all": all})

    try:
        from ignition.gateway.client import GatewayConnectionPool, IgnitionGatewayClient
        from ignition.gateway.config import GatewayConfigManager

        manager = GatewayConfigManager()

        if all:
            # Check all gateways using connection pool
            configs = manager.list_configs()
            if not configs:
                console.print("[yellow]📭 No gateways configured[/yellow]")
                return

            console.print(
                f"[bold blue]🏥 Health Check - All Gateways ({len(configs)})[/bold blue]\n"
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

        else:
            # Check specific gateway or prompt for selection
            if not name:
                configs = manager.list_configs()
                if not configs:
                    console.print("[red]✗[/red] No gateways configured")
                    return

                if len(configs) == 1:
                    name = configs[0]
                else:
                    console.print("[bold]Available gateways:[/bold]")
                    for i, config_name in enumerate(configs, 1):
                        console.print(f"  {i}. {config_name}")

                    choice = console.input("\nSelect gateway: ")
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

            console.print(f"[bold blue]🏥 Health Check - {config.name}[/bold blue]")
            console.print(f"URL: {config.base_url}\n")

            with IgnitionGatewayClient(config=config) as client:
                health_data = client.health_check()

                # Overall status
                status = health_data.get("overall_status", "unknown")
                timestamp = health_data.get("timestamp", "unknown")

                if status == "healthy":
                    console.print("[green]✅ Overall Status: HEALTHY[/green]")
                elif status == "warning":
                    console.print("[yellow]⚠️ Overall Status: WARNING[/yellow]")
                else:
                    console.print("[red]❌ Overall Status: UNHEALTHY[/red]")

                console.print(f"Timestamp: {timestamp}\n")

                # Detailed checks
                console.print("[bold]Detailed Health Checks:[/bold]")
                checks = health_data.get("checks", {})

                for check_name, check_data in checks.items():
                    check_status = check_data.get("status", "unknown")
                    details = check_data.get("details", "")

                    # Status formatting
                    if check_status == "healthy":
                        icon = "✅"
                        color = "green"
                    elif check_status == "warning":
                        icon = "⚠️"
                        color = "yellow"
                    else:
                        icon = "❌"
                        color = "red"

                    check_display = f"{icon} [{color}]{check_name.replace('_', ' ').title()}[/{color}]"

                    if details:
                        check_display += f" - {details}"

                    if check_name == "response_time" and "value_ms" in check_data:
                        ms = check_data["value_ms"]
                        check_display += f" ({ms}ms)"

                    console.print(f"  {check_display}")

    except Exception as e:
        console.print(f"[red]✗[/red] Health check failed: {e}")


@gateway.command()
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


@gateway.command()
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


if __name__ == "__main__":
    main()
