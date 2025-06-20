"""CLI Commands for AI Assistant Module.

Provides command-line interface for AI-powered code analysis, validation,
and assistance features.
"""

import asyncio
import json
import logging
import os
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..ai_assistant import create_ai_assistant_module
from ..ai_assistant.ai_assistant_module import CodeAnalysisRequest

console = Console()
logger = logging.getLogger(__name__)


@click.group(name="ai")
@click.pass_context
def ai_assistant_commands(ctx):
    """AI Assistant commands for intelligent code analysis and validation."""
    ctx.ensure_object(dict)


@ai_assistant_commands.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Enable/disable knowledge graph validation",
)
@click.option(
    "--detect-hallucinations/--no-detect-hallucinations",
    default=True,
    help="Enable/disable hallucination detection",
)
@click.option("--output", "-o", type=click.Path(), help="Save analysis results to file")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "markdown", "console"]),
    default="console",
    help="Output format",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def analyze(
    file_path: str,
    validate: bool,
    detect_hallucinations: bool,
    output: str | None,
    output_format: str,
    verbose: bool,
):
    """Analyze a Python file for potential issues and AI hallucinations."""

    async def _analyze():
        # Create AI Assistant Module
        ai_module = create_ai_assistant_module()

        try:
            # Initialize module
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Initializing AI Assistant Module...", total=None)
                initialized = await ai_module.initialize()

                if not initialized:
                    console.print("[red]Failed to initialize AI Assistant Module[/red]")
                    return

                progress.update(task, description="Analyzing code...")

                # Create analysis request
                request = CodeAnalysisRequest(
                    file_path=file_path,
                    validate_against_knowledge_graph=validate,
                    detect_hallucinations=detect_hallucinations,
                )

                # Perform analysis
                response = await ai_module.analyze_code(request)

                progress.update(task, description="Analysis complete!")

            # Display results based on format
            if output_format == "console":
                _display_analysis_console(response, verbose)
            elif output_format == "json":
                _display_analysis_json(response, output)
            elif output_format == "markdown":
                _display_analysis_markdown(response, output)

        finally:
            await ai_module.shutdown()

    asyncio.run(_analyze())


@ai_assistant_commands.command()
@click.option("--code", "-c", help="Python code to analyze (as string)")
@click.option(
    "--file",
    "-f",
    "file_path",
    type=click.Path(exists=True),
    help="Python file to analyze",
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Enable/disable knowledge graph validation",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def quick_check(code: str | None, file_path: str | None, validate: bool, verbose: bool):
    """Quick code analysis for immediate feedback."""
    if not code and not file_path:
        console.print("[red]Error: Either --code or --file must be provided[/red]")
        return

    async def _quick_check():
        ai_module = create_ai_assistant_module()

        try:
            await ai_module.initialize()

            if code:
                response = await ai_module.analyze_code_string(code)
            elif file_path:
                response = await ai_module.analyze_file(file_path)
            else:
                # This should not happen due to the check above, but for type safety
                console.print("[red]Error: No code or file provided[/red]")
                return

            # Quick summary display
            _display_quick_summary(response, verbose)

        finally:
            await ai_module.shutdown()

    asyncio.run(_quick_check())


@ai_assistant_commands.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--pattern", default="*.py", help="File pattern to match")
@click.option("--output-dir", type=click.Path(), help="Directory to save analysis reports")
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Enable/disable knowledge graph validation",
)
@click.option("--summary-only", is_flag=True, help="Show only summary statistics")
def batch_analyze(
    directory: str,
    pattern: str,
    output_dir: str | None,
    validate: bool,
    summary_only: bool,
):
    """Analyze multiple Python files in a directory."""

    async def _batch_analyze():
        ai_module = create_ai_assistant_module()

        try:
            await ai_module.initialize()

            # Find Python files
            dir_path = Path(directory)
            python_files = list(dir_path.rglob(pattern))

            if not python_files:
                console.print(f"[yellow]No files matching '{pattern}' found in {directory}[/yellow]")
                return

            console.print(f"[blue]Found {len(python_files)} files to analyze[/blue]")

            results = []

            with Progress() as progress:
                task = progress.add_task("Analyzing files...", total=len(python_files))

                for file_path in python_files:
                    try:
                        response = await ai_module.analyze_file(str(file_path))
                        results.append(
                            {
                                "file": str(file_path.relative_to(dir_path)),
                                "response": response,
                            }
                        )

                        # Save individual report if output directory specified
                        if output_dir:
                            _save_individual_report(file_path, response, output_dir)

                    except Exception as e:
                        console.print(f"[red]Error analyzing {file_path}: {e}[/red]")

                    progress.advance(task)

            # Display batch summary
            _display_batch_summary(results, summary_only)

        finally:
            await ai_module.shutdown()

    asyncio.run(_batch_analyze())


@ai_assistant_commands.command()
def info():
    """Display AI Assistant Module information and capabilities."""

    async def _info():
        ai_module = create_ai_assistant_module()

        try:
            await ai_module.initialize()

            info_data = ai_module.get_module_info()
            stats = await ai_module.get_statistics()

            # Create information display
            console.print(
                Panel.fit(
                    f"[bold blue]{info_data['module_name']} v{info_data['version']}[/bold blue]\n"
                    f"{info_data['description']}\n\n"
                    f"[bold]Status:[/bold] {info_data['status']}\n"
                    f"[bold]Neo4j Enabled:[/bold] {info_data['configuration']['neo4j_enabled']}"
                )
            )

            # Features table
            features_table = Table(title="Features & Capabilities")
            features_table.add_column("Feature", style="cyan")
            features_table.add_column("Description", style="white")

            feature_descriptions = {
                "AST-based code analysis": "Parse Python code using Abstract Syntax Trees",
                "Knowledge graph validation": "Validate code against Neo4j knowledge graph",
                "Hallucination detection": "Detect AI-generated code issues",
                "Import validation": "Check import statements against known modules",
                "Method signature checking": "Verify method calls and parameters",
                "Parameter validation": "Validate function/method parameters",
                "Confidence scoring": "Provide confidence scores for validations",
                "Intelligent suggestions": "Generate smart suggestions for improvements",
            }

            for feature in info_data["features"]:
                description = feature_descriptions.get(feature, "Advanced code analysis feature")
                features_table.add_row(feature, description)

            console.print(features_table)

            # Configuration table
            config_table = Table(title="Configuration")
            config_table.add_column("Setting", style="yellow")
            config_table.add_column("Value", style="white")

            for key, value in info_data["configuration"].items():
                config_table.add_row(key.replace("_", " ").title(), str(value))

            console.print(config_table)

            # Statistics
            if stats:
                stats_table = Table(title="Statistics")
                stats_table.add_column("Metric", style="green")
                stats_table.add_column("Value", style="white")

                for key, value in stats.items():
                    stats_table.add_row(key.replace("_", " ").title(), str(value))

                console.print(stats_table)

        finally:
            await ai_module.shutdown()

    asyncio.run(_info())


@ai_assistant_commands.command()
@click.option("--neo4j-uri", help="Neo4j URI")
@click.option("--neo4j-user", help="Neo4j username")
@click.option("--neo4j-password", help="Neo4j password")
def test_connection(neo4j_uri: str | None, neo4j_user: str | None, neo4j_password: str | None):
    """Test Neo4j knowledge graph connection."""

    async def _test_connection():
        from dotenv import load_dotenv

        load_dotenv()

        # Use provided values or fall back to environment/defaults
        uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        password = neo4j_password or os.getenv("NEO4J_PASSWORD", "password")

        console.print(f"[blue]Testing connection to Neo4j at {uri}...[/blue]")

        try:
            from ..ai_assistant.knowledge_validator import KnowledgeValidator

            validator = KnowledgeValidator(uri, user, password)
            await validator.initialize()

            # Test basic query
            await validator._find_modules("test")

            console.print("[green]✓ Connection successful![/green]")
            console.print("[blue]Knowledge graph appears to be accessible[/blue]")

            await validator.close()

        except Exception as e:
            console.print(f"[red]✗ Connection failed: {e}[/red]")
            console.print("[yellow]Make sure Neo4j is running and credentials are correct[/yellow]")

    asyncio.run(_test_connection())


def _display_analysis_console(response, verbose: bool):
    """Display analysis results in console format."""
    # Header
    console.print(
        Panel.fit(
            f"[bold blue]Code Analysis Results[/bold blue]\n"
            f"File: {response.analysis_result.file_path}\n"
            f"Confidence: {response.confidence_score:.1%}"
        )
    )

    # Analysis summary
    analysis = response.analysis_result
    summary_table = Table(title="Analysis Summary")
    summary_table.add_column("Component", style="cyan")
    summary_table.add_column("Count", style="white")

    summary_table.add_row("Imports", str(len(analysis.imports)))
    summary_table.add_row("Class Instantiations", str(len(analysis.class_instantiations)))
    summary_table.add_row("Method Calls", str(len(analysis.method_calls)))
    summary_table.add_row("Function Calls", str(len(analysis.function_calls)))
    summary_table.add_row("Attribute Accesses", str(len(analysis.attribute_accesses)))

    console.print(summary_table)

    # Validation results
    if response.validation_result:
        validation = response.validation_result

        validation_table = Table(title="Validation Results")
        validation_table.add_column("Type", style="yellow")
        validation_table.add_column("Total", style="white")
        validation_table.add_column("Valid", style="green")
        validation_table.add_column("Invalid/Not Found", style="red")

        validation_table.add_row(
            "Imports",
            str(len(validation.import_validations)),
            str(sum(1 for v in validation.import_validations if v.validation.status.value == "VALID")),
            str(sum(1 for v in validation.import_validations if v.validation.status.value != "VALID")),
        )

        validation_table.add_row(
            "Classes",
            str(len(validation.class_validations)),
            str(sum(1 for v in validation.class_validations if v.validation.status.value == "VALID")),
            str(sum(1 for v in validation.class_validations if v.validation.status.value != "VALID")),
        )

        validation_table.add_row(
            "Methods",
            str(len(validation.method_validations)),
            str(sum(1 for v in validation.method_validations if v.validation.status.value == "VALID")),
            str(sum(1 for v in validation.method_validations if v.validation.status.value != "VALID")),
        )

        console.print(validation_table)

    # Suggestions
    if response.suggestions:
        console.print("\n[bold yellow]Suggestions:[/bold yellow]")
        for i, suggestion in enumerate(response.suggestions, 1):
            console.print(f"  {i}. {suggestion}")

    # Hallucinations
    if response.hallucinations_detected:
        console.print(f"\n[bold red]Potential Issues Detected ({len(response.hallucinations_detected)}):[/bold red]")
        for hallucination in response.hallucinations_detected:
            console.print(f"  • {hallucination.get('description', 'Unknown issue')}")
            if verbose and "message" in hallucination:
                console.print(f"    {hallucination['message']}")

    # Errors
    if response.errors:
        console.print(f"\n[bold red]Errors ({len(response.errors)}):[/bold red]")
        for error in response.errors:
            console.print(f"  • {error}")


def _display_quick_summary(response, verbose: bool):
    """Display quick analysis summary."""
    status_color = (
        "green" if response.confidence_score > 0.7 else "yellow" if response.confidence_score > 0.4 else "red"
    )
    status_icon = "✓" if response.confidence_score > 0.7 else "⚠" if response.confidence_score > 0.4 else "✗"

    console.print(f"[{status_color}]{status_icon} Confidence: {response.confidence_score:.1%}[/{status_color}]")

    if response.suggestions:
        console.print(f"[blue]📝 {len(response.suggestions)} suggestions available[/blue]")

    if response.hallucinations_detected:
        console.print(f"[red]⚠ {len(response.hallucinations_detected)} potential issues detected[/red]")

    if response.errors:
        console.print(f"[red]❌ {len(response.errors)} errors found[/red]")

    if verbose:
        _display_analysis_console(response, verbose)


def _display_analysis_json(response, output_file: str | None):
    """Display analysis results in JSON format."""
    # Convert response to JSON-serializable format
    result = {
        "file_path": response.analysis_result.file_path,
        "confidence_score": response.confidence_score,
        "analysis": {
            "imports": len(response.analysis_result.imports),
            "class_instantiations": len(response.analysis_result.class_instantiations),
            "method_calls": len(response.analysis_result.method_calls),
            "function_calls": len(response.analysis_result.function_calls),
            "attribute_accesses": len(response.analysis_result.attribute_accesses),
        },
        "suggestions": response.suggestions,
        "hallucinations_detected": response.hallucinations_detected,
        "errors": response.errors,
    }

    json_output = json.dumps(result, indent=2)

    if output_file:
        with open(output_file, "w") as f:
            f.write(json_output)
        console.print(f"[green]Analysis results saved to {output_file}[/green]")
    else:
        console.print(json_output)


def _display_analysis_markdown(response, output_file: str | None):
    """Display analysis results in Markdown format."""
    from datetime import datetime

    md_content = f"""# Code Analysis Report

**File:** `{response.analysis_result.file_path}`
**Confidence Score:** {response.confidence_score:.1%}
**Analysis Date:** {datetime.now()!s}

## Summary

| Component | Count |
|-----------|-------|
| Imports | {len(response.analysis_result.imports)} |
| Class Instantiations | {len(response.analysis_result.class_instantiations)} |
| Method Calls | {len(response.analysis_result.method_calls)} |
| Function Calls | {len(response.analysis_result.function_calls)} |
| Attribute Accesses | {len(response.analysis_result.attribute_accesses)} |

## Suggestions

"""

    if response.suggestions:
        for i, suggestion in enumerate(response.suggestions, 1):
            md_content += f"{i}. {suggestion}\n"
    else:
        md_content += "No suggestions available.\n"

    md_content += "\n## Potential Issues\n\n"

    if response.hallucinations_detected:
        for issue in response.hallucinations_detected:
            md_content += f"- **{issue.get('type', 'Unknown')}:** {issue.get('description', 'No description')}\n"
    else:
        md_content += "No issues detected.\n"

    if response.errors:
        md_content += "\n## Errors\n\n"
        for error in response.errors:
            md_content += f"- {error}\n"

    if output_file:
        with open(output_file, "w") as f:
            f.write(md_content)
        console.print(f"[green]Analysis report saved to {output_file}[/green]")
    else:
        console.print(md_content)


def _display_batch_summary(results, summary_only: bool):
    """Display batch analysis summary."""
    total_files = len(results)
    total_confidence = sum(r["response"].confidence_score for r in results)
    avg_confidence = total_confidence / total_files if total_files > 0 else 0

    high_confidence = sum(1 for r in results if r["response"].confidence_score > 0.7)
    medium_confidence = sum(1 for r in results if 0.4 <= r["response"].confidence_score <= 0.7)
    low_confidence = sum(1 for r in results if r["response"].confidence_score < 0.4)

    # Summary table
    summary_table = Table(title="Batch Analysis Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="white")

    summary_table.add_row("Total Files Analyzed", str(total_files))
    summary_table.add_row("Average Confidence", f"{avg_confidence:.1%}")
    summary_table.add_row(
        "High Confidence (>70%)",
        f"{high_confidence} ({high_confidence / total_files * 100:.1f}%)",
    )
    summary_table.add_row(
        "Medium Confidence (40-70%)",
        f"{medium_confidence} ({medium_confidence / total_files * 100:.1f}%)",
    )
    summary_table.add_row(
        "Low Confidence (<40%)",
        f"{low_confidence} ({low_confidence / total_files * 100:.1f}%)",
    )

    console.print(summary_table)

    if not summary_only:
        # Detailed results
        results_table = Table(title="Individual File Results")
        results_table.add_column("File", style="blue")
        results_table.add_column("Confidence", style="white")
        results_table.add_column("Issues", style="red")
        results_table.add_column("Suggestions", style="yellow")

        for result in results:
            file_name = result["file"]
            response = result["response"]
            confidence = f"{response.confidence_score:.1%}"
            issues = str(len(response.hallucinations_detected))
            suggestions = str(len(response.suggestions))

            results_table.add_row(file_name, confidence, issues, suggestions)

        console.print(results_table)


def _save_individual_report(file_path: Path, response, output_dir: str):
    """Save individual analysis report."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_name = f"{file_path.stem}_analysis.json"
    report_path = output_path / report_name

    # Create report data
    report_data = {
        "file_path": str(file_path),
        "confidence_score": response.confidence_score,
        "suggestions": response.suggestions,
        "hallucinations_detected": response.hallucinations_detected,
        "errors": response.errors,
        "analysis_summary": {
            "imports": len(response.analysis_result.imports),
            "class_instantiations": len(response.analysis_result.class_instantiations),
            "method_calls": len(response.analysis_result.method_calls),
            "function_calls": len(response.analysis_result.function_calls),
            "attribute_accesses": len(response.analysis_result.attribute_accesses),
        },
    }

    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
