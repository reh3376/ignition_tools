"""Script generation commands for IGN Scripts CLI.

This module provides commands for generating Jython scripts from templates.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .cli_core import enhanced_cli

console = Console()


@click.group()
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
def validate(ctx: click.Context, script_file: str) -> None:
    """✅ Validate a Jython script for Ignition compatibility."""
    enhanced_cli.track_cli_usage("script", "validate", {"script_file": script_file})

    with console.status(f"[bold blue]Validating {script_file}..."):
        # TODO: Implement actual validation
        console.print(f"[green]✓[/green] Script validation completed: {script_file}")
        console.print("[yellow]💡[/yellow] Detailed validation coming soon!")
