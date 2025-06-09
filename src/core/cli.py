"""Command-line interface for IGN Scripts."""

import click
from rich.console import Console
from rich.panel import Panel

from src import __version__

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """IGN Scripts - Data processing, automation, and analytics workflows."""
    ctx.ensure_object(dict)
    
    # Display welcome message
    console.print(
        Panel.fit(
            f"[bold blue]IGN Scripts v{__version__}[/bold blue]\n"
            "[dim]Data processing, automation, and analytics workflows[/dim]",
            title="Welcome",
            border_style="blue"
        )
    )


@main.group()
def script() -> None:
    """Jython script generation commands."""
    pass


@script.command()
@click.option("--template", "-t", help="Template name to use")
@click.option("--config", "-c", help="Configuration file (JSON)")
@click.option("--output", "-o", help="Output file path")
@click.option("--component-name", help="Name of the component")
@click.option("--action-type", help="Type of action (navigation, tag_write, popup, etc.)")
def generate(template: str, config: str, output: str, component_name: str, action_type: str) -> None:
    """Generate a Jython script from a template."""
    try:
        from src.ignition.generators.script_generator import IgnitionScriptGenerator
        
        generator = IgnitionScriptGenerator()
        
        if config:
            # Generate from config file
            script_content = generator.generate_from_config(config, output)
            console.print(f"[green]✓[/green] Generated script from config: {config}")
        elif template:
            # Generate from command line options
            context = {}
            if component_name:
                context["component_name"] = component_name
            if action_type:
                context["action_type"] = action_type
            
            if not template.endswith(".jinja2"):
                template += ".jinja2"
            
            script_content = generator.generate_script(template, context, output)
            console.print(f"[green]✓[/green] Generated script from template: {template}")
        else:
            console.print("[red]✗[/red] Either --template or --config must be specified")
            return
        
        if output:
            console.print(f"[blue]→[/blue] Saved to: {output}")
        else:
            console.print("\n[dim]Generated script:[/dim]")
            console.print(script_content)
            
    except Exception as e:
        console.print(f"[red]✗[/red] Error generating script: {e}")


@script.command()
@click.argument("script_file")
def validate(script_file: str) -> None:
    """Validate a Jython script for Ignition compatibility."""
    console.print(f"[yellow]Validating script: {script_file}[/yellow]")
    console.print("[yellow]Script validation not yet implemented[/yellow]")


@main.group()
def template() -> None:
    """Template management commands."""
    pass


@template.command()
def list() -> None:
    """List available script templates."""
    try:
        from src.ignition.generators.script_generator import IgnitionScriptGenerator
        
        generator = IgnitionScriptGenerator()
        templates = generator.list_templates()
        
        if templates:
            console.print("[bold]Available Templates:[/bold]")
            for template in templates:
                console.print(f"  • {template}")
        else:
            console.print("[yellow]No templates found[/yellow]")
    except Exception as e:
        console.print(f"[red]✗[/red] Error listing templates: {e}")


@template.command()
@click.argument("template_name")
@click.argument("config_file")
def validate(template_name: str, config_file: str) -> None:
    """Validate a configuration against a template."""
    try:
        import json
        from src.ignition.generators.script_generator import IgnitionScriptGenerator
        
        generator = IgnitionScriptGenerator()
        
        with open(config_file, "r") as f:
            config = json.load(f)
        
        errors = generator.validate_config(config, template_name)
        
        if errors:
            console.print("[red]✗[/red] Configuration validation failed:")
            for error in errors:
                console.print(f"  • {error}")
        else:
            console.print("[green]✓[/green] Configuration is valid")
            
    except Exception as e:
        console.print(f"[red]✗[/red] Error validating configuration: {e}")


@main.group()
def export() -> None:
    """Ignition project export commands."""
    pass


@export.command()
@click.option("--source", "-s", help="Source project directory")
@click.option("--output", "-o", required=True, help="Output file path")
@click.option("--format", "-f", default="zip", help="Export format (zip, json)")
def project(source: str, output: str, format: str) -> None:
    """Export an Ignition project."""
    console.print(f"[yellow]Exporting project from {source or 'current directory'} to {output}[/yellow]")
    console.print("[yellow]Project export not yet implemented[/yellow]")


@main.command()
def setup() -> None:
    """Set up the development environment."""
    console.print("[green]Setting up IGN Scripts environment...[/green]")
    console.print("[yellow]Environment setup not yet implemented[/yellow]")


if __name__ == "__main__":
    main() 