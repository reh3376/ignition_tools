"""CLI commands for development workflow integration."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .workflow_integration import (
    DevelopmentWorkflowIntegrator,
    WorkflowIntegrationConfig,
)

console = Console()


def _initialize_workflow_systems():
    """Initialize the workflow integration systems."""
    try:
        from src.ignition.graph.client import IgnitionGraphClient

        from .ai_assistant_enhancement import AIAssistantEnhancement
        from .analytics_dashboard import CodeIntelligenceDashboard
        from .manager import CodeIntelligenceManager

        client = IgnitionGraphClient()
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j database")
            return None, None, None, None

        manager = CodeIntelligenceManager(client)
        dashboard = CodeIntelligenceDashboard(manager)
        ai_assistant = AIAssistantEnhancement(manager)
        integrator = DevelopmentWorkflowIntegrator(manager, dashboard, ai_assistant)

        return client, manager, dashboard, integrator
    except Exception as e:
        console.print(f"❌ Failed to initialize workflow systems: {e}")
        return None, None, None, None


@click.group(name="workflow")
def workflow_group() -> None:
    """🔄 Development workflow integration commands."""
    pass


@workflow_group.command()
@click.option(
    "--enable-hooks/--disable-hooks", default=True, help="Enable or disable git hooks"
)
@click.option(
    "--enable-pre-commit/--disable-pre-commit",
    default=True,
    help="Enable or disable pre-commit checks",
)
@click.option(
    "--complexity-threshold",
    type=float,
    default=50.0,
    help="Complexity threshold for quality gates",
)
@click.option(
    "--debt-threshold", type=float, default=0.6, help="Technical debt threshold"
)
@click.option(
    "--file-size-threshold", type=int, default=1000, help="File size threshold (lines)"
)
def setup(
    enable_hooks: bool,
    enable_pre_commit: bool,
    complexity_threshold: float,
    debt_threshold: float,
    file_size_threshold: int,
) -> None:
    """Set up development workflow integration."""
    console.print("🔄 Setting up development workflow integration...")

    client, manager, dashboard, integrator = _initialize_workflow_systems()
    if not integrator:
        return

    # Configure the integrator
    config = WorkflowIntegrationConfig(
        enable_git_hooks=enable_hooks,
        enable_pre_commit=enable_pre_commit,
        complexity_threshold=complexity_threshold,
        debt_threshold=debt_threshold,
        file_size_threshold=file_size_threshold,
    )
    integrator.config = config

    # set up git hooks if enabled
    if enable_hooks:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing git hooks...", total=None)

            if integrator.setup_git_hooks():
                progress.update(task, description="✅ Git hooks installed")
            else:
                progress.update(task, description="❌ Failed to install git hooks")

    # Save configuration
    config_path = Path(".workflow_config.json")
    if integrator.export_workflow_config(str(config_path)):
        console.print(f"✅ Configuration saved to {config_path}")

    # Display summary
    summary_panel = Panel(
        f"""[green]✅ Workflow integration setup complete![/green]

[bold]Configuration:[/bold]
• Git hooks: {"✅ Enabled" if enable_hooks else "❌ Disabled"}
• Pre-commit checks: {"✅ Enabled" if enable_pre_commit else "❌ Disabled"}
• Complexity threshold: {complexity_threshold}
• Debt threshold: {debt_threshold}
• File size threshold: {file_size_threshold} lines

[bold]Next steps:[/bold]
• Run [cyan]ign code workflow check[/cyan] to test quality gates
• Use [cyan]ign code workflow review[/cyan] for code review assistance
• Configure thresholds with [cyan]ign code workflow config[/cyan]
""",
        title="🔄 Workflow Integration",
        border_style="green",
    )
    console.print(summary_panel)


@workflow_group.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--all-staged", is_flag=True, help="Check all staged files")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "detailed"]),
    default="table",
    help="Output format",
)
def check(files: tuple[str], all_staged: bool, output_format: str) -> None:
    """Run quality gate checks on files."""
    console.print("🔍 Running quality gate checks...")

    client, manager, dashboard, integrator = _initialize_workflow_systems()
    if not integrator:
        return

    # Determine files to check
    files_to_check = []
    if all_staged:
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
            )
            files_to_check = [
                f
                for f in result.stdout.strip().split("\n")
                if f.endswith(".py") and Path(f).exists()
            ]
        except Exception as e:
            console.print(f"❌ Failed to get staged files: {e}")
            return
    else:
        files_to_check = list(files)

    if not files_to_check:
        console.print("⚠️  No files to check")
        return

    # Run quality gates
    all_results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking files...", total=len(files_to_check))

        for file_path in files_to_check:
            progress.update(task, description=f"Checking {file_path}")
            results = integrator.run_quality_gates(file_path)
            all_results.extend([(file_path, result) for result in results])
            progress.advance(task)

    # Display results
    if output_format == "json":
        output = {
            "files_checked": len(files_to_check),
            "total_gates": len(all_results),
            "results": [
                {
                    "file": file_path,
                    "gate": result.gate_name,
                    "passed": result.passed,
                    "score": result.score,
                    "message": result.message,
                    "recommendations": result.recommendations,
                }
                for file_path, result in all_results
            ],
        }
        console.print(json.dumps(output, indent=2))

    elif output_format == "detailed":
        for file_path, result in all_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            console.print(f"\n[bold]{file_path}[/bold] - {result.gate_name}: {status}")
            console.print(f"  Score: {result.score:.2f}")
            console.print(f"  Message: {result.message}")
            if result.recommendations:
                console.print("  Recommendations:")
                for rec in result.recommendations:
                    console.print(f"    • {rec}")

    else:  # table format
        table = Table(title="Quality Gate Results")
        table.add_column("File", style="cyan")
        table.add_column("Gate", style="magenta")
        table.add_column("Status", style="bold")
        table.add_column("Score", justify="right")
        table.add_column("Message")

        for file_path, result in all_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            status_style = "green" if result.passed else "red"

            table.add_row(
                Path(file_path).name,
                result.gate_name,
                f"[{status_style}]{status}[/{status_style}]",
                f"{result.score:.2f}",
                result.message,
            )

        console.print(table)

    # Summary
    passed_gates = sum(1 for _, result in all_results if result.passed)
    total_gates = len(all_results)
    pass_rate = passed_gates / total_gates if total_gates > 0 else 0.0

    summary_color = (
        "green" if pass_rate >= 0.8 else "yellow" if pass_rate >= 0.6 else "red"
    )
    console.print(
        f"\n[{summary_color}]Quality gates: {passed_gates}/{total_gates} passed ({pass_rate:.1%})[/{summary_color}]"
    )


@workflow_group.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "detailed"]),
    default="table",
    help="Output format",
)
def review(files: tuple[str], output_format: str) -> None:
    """Generate code review insights for changed files."""
    console.print("📋 Generating code review insights...")

    client, manager, dashboard, integrator = _initialize_workflow_systems()
    if not integrator:
        return

    files_to_review = list(files) if files else []

    # If no files specified, get changed files from git
    if not files_to_review:
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1..HEAD"],
                capture_output=True,
                text=True,
            )
            files_to_review = [
                f
                for f in result.stdout.strip().split("\n")
                if f.endswith(".py") and Path(f).exists()
            ]
        except Exception as e:
            console.print(f"❌ Failed to get changed files: {e}")
            return

    if not files_to_review:
        console.print("⚠️  No files to review")
        return

    # Generate insights
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing files...", total=None)
        insights = integrator.generate_code_review_insights(files_to_review)
        progress.update(task, description="✅ Analysis complete")

    # Display insights
    if output_format == "json":
        output = {
            "files_analyzed": len(files_to_review),
            "insights": [
                {
                    "file": insight.file_path,
                    "change_type": insight.change_type,
                    "risk_level": insight.risk_level,
                    "impact_score": insight.impact_score,
                    "suggestions": insight.suggestions,
                    "test_recommendations": insight.test_recommendations,
                    "related_files": insight.related_files,
                }
                for insight in insights
            ],
        }
        console.print(json.dumps(output, indent=2))

    elif output_format == "detailed":
        for insight in insights:
            risk_color = {
                "low": "green",
                "medium": "yellow",
                "high": "orange",
                "critical": "red",
            }.get(insight.risk_level, "white")

            console.print(f"\n[bold cyan]{insight.file_path}[/bold cyan]")
            console.print(f"  Change Type: {insight.change_type}")
            console.print(
                f"  Risk Level: [{risk_color}]{insight.risk_level}[/{risk_color}]"
            )
            console.print(f"  Impact Score: {insight.impact_score:.2f}")

            if insight.suggestions:
                console.print("  Suggestions:")
                for suggestion in insight.suggestions:
                    console.print(f"    • {suggestion}")

            if insight.test_recommendations:
                console.print("  Test Recommendations:")
                for rec in insight.test_recommendations:
                    console.print(f"    • {rec}")

            if insight.related_files:
                console.print(f"  Related Files: {len(insight.related_files)}")
                for related in insight.related_files[:3]:  # Show top 3
                    console.print(f"    • {related}")

    else:  # table format
        table = Table(title="Code Review Insights")
        table.add_column("File", style="cyan")
        table.add_column("Change", style="magenta")
        table.add_column("Risk", style="bold")
        table.add_column("Impact", justify="right")
        table.add_column("Suggestions", style="dim")

        for insight in insights:
            risk_color = {
                "low": "green",
                "medium": "yellow",
                "high": "orange",
                "critical": "red",
            }.get(insight.risk_level, "white")

            suggestions_text = "; ".join(insight.suggestions[:2])  # Show first 2
            if len(insight.suggestions) > 2:
                suggestions_text += f" (+{len(insight.suggestions) - 2} more)"

            table.add_row(
                Path(insight.file_path).name,
                insight.change_type,
                f"[{risk_color}]{insight.risk_level}[/{risk_color}]",
                f"{insight.impact_score:.2f}",
                (
                    suggestions_text[:50] + "..."
                    if len(suggestions_text) > 50
                    else suggestions_text
                ),
            )

        console.print(table)

    # Summary
    high_risk_count = sum(1 for i in insights if i.risk_level in ["high", "critical"])
    if high_risk_count > 0:
        console.print(
            f"\n[red]⚠️  {high_risk_count} high-risk files require careful review[/red]"
        )
    else:
        console.print(
            f"\n[green]✅ All {len(insights)} files are low-medium risk[/green]"
        )


@workflow_group.command()
@click.option("--complexity-threshold", type=float, help="set complexity threshold")
@click.option("--debt-threshold", type=float, help="set technical debt threshold")
@click.option("--file-size-threshold", type=int, help="set file size threshold")
@click.option("--show", is_flag=True, help="Show current configuration")
@click.option("--export", type=click.Path(), help="Export configuration to file")
@click.option(
    "--import",
    "import_path",
    type=click.Path(exists=True),
    help="Import configuration from file",
)
def config(
    complexity_threshold: float | None,
    debt_threshold: float | None,
    file_size_threshold: int | None,
    show: bool,
    export: str | None,
    import_path: str | None,
) -> None:
    """Configure workflow integration settings."""
    client, manager, dashboard, integrator = _initialize_workflow_systems()
    if not integrator:
        return

    # Import configuration
    if import_path:
        if integrator.import_workflow_config(import_path):
            console.print(f"✅ Configuration imported from {import_path}")
        else:
            console.print(f"❌ Failed to import configuration from {import_path}")
            return

    # Update configuration
    if any([complexity_threshold, debt_threshold, file_size_threshold]):
        config = integrator.config

        if complexity_threshold is not None:
            config.complexity_threshold = complexity_threshold
        if debt_threshold is not None:
            config.debt_threshold = debt_threshold
        if file_size_threshold is not None:
            config.file_size_threshold = file_size_threshold

        console.print("✅ Configuration updated")

    # Export configuration
    if export:
        if integrator.export_workflow_config(export):
            console.print(f"✅ Configuration exported to {export}")
        else:
            console.print(f"❌ Failed to export configuration to {export}")

    # Show configuration
    if show or not any(
        [complexity_threshold, debt_threshold, file_size_threshold, export, import_path]
    ):
        config = integrator.config

        config_table = Table(title="Workflow Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="bold")
        config_table.add_column("Description")

        config_table.add_row(
            "Git Hooks",
            "✅ Enabled" if config.enable_git_hooks else "❌ Disabled",
            "Automatic git hook installation",
        )
        config_table.add_row(
            "Pre-commit Checks",
            "✅ Enabled" if config.enable_pre_commit else "❌ Disabled",
            "Quality gates on commit",
        )
        config_table.add_row(
            "Quality Gates",
            "✅ Enabled" if config.enable_quality_gates else "❌ Disabled",
            "Automated quality checks",
        )
        config_table.add_row(
            "Complexity Threshold",
            str(config.complexity_threshold),
            "Maximum allowed complexity",
        )
        config_table.add_row(
            "Debt Threshold", str(config.debt_threshold), "Maximum technical debt score"
        )
        config_table.add_row(
            "File Size Threshold",
            f"{config.file_size_threshold} lines",
            "Maximum file size",
        )
        config_table.add_row(
            "Auto Analysis",
            "✅ Enabled" if config.enable_auto_analysis else "❌ Disabled",
            "Automatic post-commit analysis",
        )
        config_table.add_row(
            "Review Assistance",
            "✅ Enabled" if config.enable_review_assistance else "❌ Disabled",
            "Code review insights",
        )

        console.print(config_table)


@workflow_group.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--output", type=click.Path(), help="Save report to file")
def report(files: tuple[str], output: str | None) -> None:
    """Generate comprehensive workflow report."""
    console.print("📊 Generating workflow report...")

    client, manager, dashboard, integrator = _initialize_workflow_systems()
    if not integrator:
        return

    files_to_analyze = list(files) if files else []

    # If no files specified, get recent changes
    if not files_to_analyze:
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~5..HEAD"],
                capture_output=True,
                text=True,
            )
            files_to_analyze = [
                f
                for f in result.stdout.strip().split("\n")
                if f.endswith(".py") and Path(f).exists()
            ]
        except Exception:
            files_to_analyze = []

    if not files_to_analyze:
        console.print("⚠️  No files to analyze")
        return

    # Generate report
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating report...", total=None)
        report_data = integrator.create_workflow_report(files_to_analyze)
        progress.update(task, description="✅ Report generated")

    # Save to file if requested
    if output:
        with open(output, "w") as f:
            json.dump(report_data, f, indent=2)
        console.print(f"✅ Report saved to {output}")

    # Display summary
    console.print("\n[bold]Workflow Report Summary[/bold]")
    console.print(f"Generated: {report_data['timestamp']}")
    console.print(f"Files analyzed: {report_data['files_analyzed']}")

    if report_data.get("overall_health"):
        health = report_data["overall_health"]
        pass_rate = health["pass_rate"]
        color = "green" if pass_rate >= 0.8 else "yellow" if pass_rate >= 0.6 else "red"
        console.print(
            f"Quality gates: [{color}]{health['gates_passed']}/{health['total_gates']} passed ({pass_rate:.1%})[/{color}]"
        )

    if report_data.get("recommendations"):
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in report_data["recommendations"]:
            console.print(f"  • {rec}")

    console.print("\n[dim]Full report available in JSON format[/dim]")


# Export the command group
__all__ = ["workflow_group"]
