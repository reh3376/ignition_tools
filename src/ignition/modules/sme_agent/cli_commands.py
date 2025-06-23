"""SME Agent CLI Commands - Modular Architecture

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

This modular design splits the original 1,425-line file into focused modules:
- core_commands.py: Basic operations (validate-env, status, initialize, ask, analyze)
- evaluation_commands.py: Testing and batch management
- infrastructure_commands.py: Deployment and system management
- knowledge_commands.py: Knowledge extraction and vector enhancement
"""

import click
from rich.console import Console

from .cli import (
    core_commands,
    evaluation_commands,
    infrastructure_commands,
    knowledge_commands,
)

console = Console()


@click.group(name="sme")
@click.pass_context
def sme_agent_cli(ctx):
    """SME Agent CLI - Ignition Subject Matter Expert Assistant

    Phase 11: Process SME Agent & AI Enhancement Platform
    Following crawl_mcp.py methodology for systematic operation.

    Modular Architecture:
    • Core: Basic operations and validation
    • Evaluation: Testing and batch management
    • Infrastructure: Deployment and system management
    • Knowledge: Knowledge extraction and vector enhancement
    """
    ctx.ensure_object(dict)

    # Display modular architecture information
    if ctx.invoked_subcommand is None:
        console.print("[bold blue]🤖 SME Agent CLI - Modular Architecture[/bold blue]")
        console.print("\nAvailable command groups:")
        console.print("  • [cyan]core[/cyan] - Basic operations and validation")
        console.print("  • [cyan]evaluation[/cyan] - Testing and batch management")
        console.print(
            "  • [cyan]infrastructure[/cyan] - Deployment and system management"
        )
        console.print(
            "  • [cyan]knowledge[/cyan] - Knowledge extraction and vector enhancement"
        )
        console.print(
            "\nUse 'ign module sme <group> --help' for group-specific commands"
        )


# Add all sub-command groups to the main CLI
sme_agent_cli.add_command(core_commands)
sme_agent_cli.add_command(evaluation_commands)
sme_agent_cli.add_command(infrastructure_commands)
sme_agent_cli.add_command(knowledge_commands)


# Backward compatibility aliases for commonly used commands
@sme_agent_cli.command("validate-env")
@click.pass_context
def validate_env_alias(ctx):
    """Alias for core validate-env command"""
    ctx.invoke(core_commands.commands["validate-env"])


@sme_agent_cli.command("status")
@click.pass_context
def status_alias(ctx):
    """Alias for core status command"""
    ctx.invoke(core_commands.commands["status"])


@sme_agent_cli.command("ask")
@click.argument("question", required=True)
@click.option("--context", help="Optional context for the question")
@click.option(
    "--complexity",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    default="basic",
)
@click.pass_context
def ask_alias(ctx, question: str, context: str | None, complexity: str):
    """Alias for core ask command"""
    ctx.invoke(
        core_commands.commands["ask"],
        question=question,
        context=context,
        complexity=complexity,
    )
