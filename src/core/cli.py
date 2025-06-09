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
def dataset() -> None:
    """Dataset management commands."""
    pass


@dataset.command()
def validate() -> None:
    """Validate dataset against schema."""
    console.print("[yellow]Dataset validation not yet implemented[/yellow]")


@dataset.command()
def create() -> None:
    """Create a new dataset."""
    console.print("[yellow]Dataset creation not yet implemented[/yellow]")


@main.group()
def schema() -> None:
    """Schema management commands."""
    pass


@schema.command()
def list() -> None:
    """List available schemas."""
    console.print("[yellow]Schema listing not yet implemented[/yellow]")


@schema.command()
def validate() -> None:
    """Validate a schema definition."""
    console.print("[yellow]Schema validation not yet implemented[/yellow]")


@main.command()
def setup() -> None:
    """Set up the development environment."""
    console.print("[green]Setting up IGN Scripts environment...[/green]")
    console.print("[yellow]Environment setup not yet implemented[/yellow]")


if __name__ == "__main__":
    main() 