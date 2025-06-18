"""Template management commands for IGN Scripts CLI.

This module provides commands for managing and exploring script templates.
"""

import click
from rich.console import Console
from rich.table import Table

from .cli_core import enhanced_cli

console = Console()


@click.group()
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
