"""Enhanced CLI Commands for Code Intelligence & Validation.

This module provides command-line interface for AI-powered code validation
and analysis following crawl_mcp.py methodology as specified in Phase 11.8.

Commands:
- ign code validate <script>              # Validate against knowledge graph (local models)
- ign code check-hallucinations <script>  # Detect AI hallucinations (CodeLlama)
- ign code analyze-ast <script>           # Comprehensive AST analysis
- ign code validate-imports <script>      # Validate imports against real modules
- ign code suggest-improvements <script>  # AI-powered improvement suggestions
- ign code find-examples <pattern>        # Find real-world examples from crawled data
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .enhanced_validator import EnhancedCodeValidator
from .enhanced_validator import validate_environment as validate_validator_environment
from .script_analyzer import AIScriptAnalyzer

console = Console()


def format_cli_error(error: Exception) -> str:
    """Format CLI errors for user-friendly messages following crawl_mcp.py patterns."""
    error_str = str(error).lower()

    if "validation" in error_str:
        return f"Input validation failed: {error!s}"
    elif "environment" in error_str:
        return f"Environment setup issue: {error!s}"
    elif "permission" in error_str:
        return f"Permission denied: {error!s}"
    elif "file not found" in error_str:
        return f"Script file not found: {error!s}"
    elif "syntax" in error_str:
        return f"Python syntax error: {error!s}"
    else:
        return f"Command error: {error!s}"


def validate_script_path(script_path: str) -> dict[str, Any]:
    """Validate script path following crawl_mcp.py methodology."""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "sanitized_path": script_path,
    }

    try:
        # Check if path is provided
        if not script_path or not script_path.strip():
            validation_result["valid"] = False
            validation_result["errors"].append("Script path is required")
            return validation_result

        # Normalize path
        script_path = script_path.strip()
        path_obj = Path(script_path)

        # Check if file exists
        if not path_obj.exists():
            validation_result["valid"] = False
            validation_result["errors"].append(f"Script file not found: {script_path}")
            return validation_result

        # Check if it's a file
        if not path_obj.is_file():
            validation_result["valid"] = False
            validation_result["errors"].append(f"Path is not a file: {script_path}")
            return validation_result

        # Check if it's a Python file
        if not script_path.endswith(".py"):
            validation_result["warnings"].append("File does not have .py extension - proceeding anyway")

        # Check if file is readable
        try:
            with open(script_path, encoding="utf-8") as f:
                f.read(1)  # Read first character to test
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Cannot read script file: {e}")
            return validation_result

        validation_result["sanitized_path"] = str(path_obj.resolve())

    except Exception as e:
        validation_result["valid"] = False
        validation_result["errors"].append(f"Path validation error: {e}")

    return validation_result


@click.group()
def code() -> None:
    """Enhanced Code Intelligence & Validation commands."""
    pass


@code.command()
@click.argument("script_path")
@click.option(
    "--validation-type",
    default="comprehensive",
    help="Type of validation: ast, imports, hallucination, comprehensive",
)
@click.option(
    "--use-knowledge-graph/--no-knowledge-graph",
    default=True,
    help="Use Neo4j knowledge graph for validation",
)
@click.option(
    "--model-preference",
    default="codellama",
    help="Preferred model: codellama, qwen, auto",
)
@click.option(
    "--confidence-threshold",
    default=0.7,
    type=float,
    help="Confidence threshold for issues (0.0-1.0)",
)
@click.option("--output", help="Output file for results (JSON format)")
def validate(
    script_path: str,
    validation_type: str,
    use_knowledge_graph: bool,
    model_preference: str,
    confidence_threshold: float,
    output: str | None,
):
    """Validate Python script against knowledge graph using local models.

    Examples:
        ign code validate my_script.py
        ign code validate script.py --validation-type hallucination
        ign code validate script.py --model-preference qwen --output results.json
    """
    console.print("\n[bold blue]🔍 Enhanced Code Validator[/bold blue]")
    console.print("Following crawl_mcp.py methodology for systematic validation...\n")

    # Step 1: Input validation and sanitization
    path_validation = validate_script_path(script_path)
    if not path_validation["valid"]:
        console.print("[bold red]❌ Input validation failed:[/bold red]")
        for error in path_validation["errors"]:
            console.print(f"  • {error}")
        return

    if path_validation["warnings"]:
        console.print("[yellow]⚠️  Warnings:[/yellow]")
        for warning in path_validation["warnings"]:
            console.print(f"  • {warning}")
        console.print()

    sanitized_path = path_validation["sanitized_path"]

    # Step 2: Environment validation
    console.print("[bold yellow]📋 Validating Environment...[/bold yellow]")
    env_validation = validate_validator_environment()

    if not env_validation["valid"]:
        console.print("[bold red]❌ Environment validation failed:[/bold red]")
        for error in env_validation["errors"]:
            console.print(f"  • {error}")
        return

    if env_validation["warnings"]:
        console.print("[yellow]⚠️  Environment warnings:[/yellow]")
        for warning in env_validation["warnings"]:
            console.print(f"  • {warning}")
        console.print()

    # Step 3: Execute validation with comprehensive error handling
    async def run_validation() -> Any:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Initializing validator...", total=None)

                validator = EnhancedCodeValidator()
                await validator.initialize()

                progress.update(task, description="Validating script...")

                result = await validator.validate_script(
                    script_path=sanitized_path,
                    validation_type=validation_type,
                    use_knowledge_graph=use_knowledge_graph,
                    model_preference=model_preference,
                    confidence_threshold=confidence_threshold,
                )

                progress.update(task, description="Processing results...")
                await validator.cleanup()
                return result

        except Exception as e:
            console.print(f"[bold red]❌ Validation failed: {format_cli_error(e)}[/bold red]")
            return None

    # Run the async validation
    result = asyncio.run(run_validation())

    if result is None:
        return

    # Step 4: Display results
    if result.success:
        console.print("\n[bold green]✅ Validation completed successfully![/bold green]")

        # Create results table
        table = Table(title="Validation Results")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="green")

        table.add_row(
            "AST Parsing",
            "✅ Valid" if result.ast_valid else "❌ Invalid",
            f"{len(result.ast_errors)} errors" if result.ast_errors else "No issues",
        )
        table.add_row(
            "Import Validation",
            "✅ Valid" if result.imports_valid else "❌ Invalid",
            (f"{len(result.missing_imports)} missing" if result.missing_imports else "All available"),
        )
        table.add_row(
            "Knowledge Graph",
            "✅ Validated" if result.kg_validated else "⚠️  Skipped",
            f"{len(result.kg_issues)} issues" if result.kg_issues else "No issues",
        )
        table.add_row(
            "Hallucination Check",
            "✅ Clean" if not result.hallucination_detected else "⚠️  Issues",
            (f"{len(result.hallucination_issues)} found" if result.hallucination_issues else "None detected"),
        )

        console.print(table)

        # Display processing info
        console.print(f"\n[bold]Processing Time:[/bold] {result.processing_time:.2f}s")
        if result.models_used:
            console.print(f"[bold]Models Used:[/bold] {', '.join(result.models_used)}")

        # Display suggestions if any
        if result.suggestions:
            console.print("\n[bold yellow]💡 Improvement Suggestions:[/bold yellow]")
            for i, suggestion in enumerate(result.suggestions, 1):
                console.print(f"  {i}. [{suggestion['type'].upper()}] {suggestion['suggestion']}")

        # Save to output file if requested
        if output:
            try:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(result.dict(), f, indent=2, default=str)
                console.print(f"\n[green]📄 Results saved to: {output}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to save results: {e}[/red]")
    else:
        console.print("\n[bold red]❌ Validation failed![/bold red]")
        if result.ast_errors:
            console.print("[red]Errors:[/red]")
            for error in result.ast_errors:
                console.print(f"  • {error}")


@code.command()
@click.argument("script_path")
@click.option(
    "--model-preference",
    default="codellama",
    help="Preferred model: codellama, qwen, auto",
)
@click.option(
    "--confidence-threshold",
    default=0.7,
    type=float,
    help="Confidence threshold for hallucinations (0.0-1.0)",
)
@click.option("--output", help="Output file for results (JSON format)")
def check_hallucinations(
    script_path: str,
    model_preference: str,
    confidence_threshold: float,
    output: str | None,
):
    """Detect AI hallucinations in Python scripts using local models.

    Examples:
        ign code check-hallucinations my_script.py
        ign code check-hallucinations script.py --model-preference qwen
        ign code check-hallucinations script.py --confidence-threshold 0.8
    """
    console.print("\n[bold blue]🧠 AI Hallucination Detector[/bold blue]")
    console.print("Using local models for hallucination detection...\n")

    # Input validation
    path_validation = validate_script_path(script_path)
    if not path_validation["valid"]:
        console.print("[bold red]❌ Input validation failed:[/bold red]")
        for error in path_validation["errors"]:
            console.print(f"  • {error}")
        return

    sanitized_path = path_validation["sanitized_path"]

    # Run validation with hallucination focus
    async def run_hallucination_check() -> Any:
        try:
            validator = EnhancedCodeValidator()
            await validator.initialize()

            result = await validator.validate_script(
                script_path=sanitized_path,
                validation_type="hallucination",
                use_knowledge_graph=False,
                model_preference=model_preference,
                confidence_threshold=confidence_threshold,
            )

            await validator.cleanup()
            return result
        except Exception as e:
            console.print(f"[bold red]❌ Hallucination check failed: {format_cli_error(e)}[/bold red]")
            return None

    result = asyncio.run(run_hallucination_check())

    if result and result.success:
        if result.hallucination_detected:
            console.print("[bold red]⚠️  Potential AI hallucinations detected![/bold red]")

            for i, issue in enumerate(result.hallucination_issues, 1):
                console.print(f"\n{i}. [bold]Type:[/bold] {issue.get('type', 'Unknown')}")
                console.print(f"   [bold]Description:[/bold] {issue.get('description', 'No description')}")
                console.print(f"   [bold]Confidence:[/bold] {issue.get('confidence', 0.0):.2f}")
                if "line" in issue:
                    console.print(f"   [bold]Line:[/bold] {issue['line']}")
        else:
            console.print("[bold green]✅ No hallucinations detected![/bold green]")

        if output:
            try:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(result.dict(), f, indent=2, default=str)
                console.print(f"\n[green]📄 Results saved to: {output}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to save results: {e}[/red]")


@code.command()
@click.argument("script_path")
@click.option(
    "--analysis-type",
    default="comprehensive",
    help="Analysis type: pattern, context, structure, comprehensive",
)
@click.option("--model-preference", default="qwen", help="Preferred model: qwen, codellama, auto")
@click.option(
    "--include-suggestions/--no-suggestions",
    default=True,
    help="Include improvement suggestions",
)
@click.option("--output", help="Output file for results (JSON format)")
def analyze_ast(
    script_path: str,
    analysis_type: str,
    model_preference: str,
    include_suggestions: bool,
    output: str | None,
):
    """Comprehensive AST analysis with AI-powered insights.

    Examples:
        ign code analyze-ast my_script.py
        ign code analyze-ast script.py --analysis-type pattern
        ign code analyze-ast script.py --model-preference qwen --output analysis.json
    """
    console.print("\n[bold blue]🔬 AST Analysis & AI Insights[/bold blue]")
    console.print("Analyzing code structure and patterns...\n")

    # Input validation
    path_validation = validate_script_path(script_path)
    if not path_validation["valid"]:
        console.print("[bold red]❌ Input validation failed:[/bold red]")
        for error in path_validation["errors"]:
            console.print(f"  • {error}")
        return

    sanitized_path = path_validation["sanitized_path"]

    # Run analysis
    async def run_analysis() -> Any:
        try:
            analyzer = AIScriptAnalyzer()
            await analyzer.initialize()

            result = await analyzer.analyze_script(
                script_path=sanitized_path,
                analysis_type=analysis_type,
                model_preference=model_preference,
                include_suggestions=include_suggestions,
            )

            return result
        except Exception as e:
            console.print(f"[bold red]❌ Analysis failed: {format_cli_error(e)}[/bold red]")
            return None

    result = asyncio.run(run_analysis())

    if result and result.success:
        console.print("[bold green]✅ Analysis completed successfully![/bold green]")

        # Structure information
        structure_table = Table(title="Code Structure")
        structure_table.add_column("Metric", style="cyan")
        structure_table.add_column("Value", style="magenta")

        structure_table.add_row("Total Lines", str(result.total_lines))
        structure_table.add_row("Functions", str(result.total_functions))
        structure_table.add_row("Classes", str(result.total_classes))
        structure_table.add_row("Complexity Score", f"{result.complexity_score:.1f}/10")
        if result.code_quality_score > 0:
            structure_table.add_row("Quality Score", f"{result.code_quality_score:.1f}/10")
        if result.maintainability_score > 0:
            structure_table.add_row("Maintainability", f"{result.maintainability_score:.1f}/10")

        console.print(structure_table)

        # Pattern detection results
        if result.patterns_detected or result.antipatterns_detected:
            console.print("\n[bold yellow]🔍 Pattern Detection Results:[/bold yellow]")

            if result.patterns_detected:
                console.print(f"[green]✅ Patterns found: {len(result.patterns_detected)}[/green]")
                for pattern in result.patterns_detected[:5]:  # Show first 5
                    console.print(
                        f"  • {pattern.pattern_name} (line {pattern.line_number}, confidence: {pattern.confidence:.2f})"
                    )

            if result.antipatterns_detected:
                console.print(f"[red]⚠️  Antipatterns found: {len(result.antipatterns_detected)}[/red]")
                for antipattern in result.antipatterns_detected[:5]:  # Show first 5
                    console.print(f"  • {antipattern.pattern_name} (line {antipattern.line_number})")

        # AI insights
        if result.context_understanding:
            console.print("\n[bold blue]🧠 AI Insights:[/bold blue]")
            understanding = result.context_understanding

            if "purpose" in understanding:
                console.print(f"[bold]Purpose:[/bold] {understanding['purpose']}")

            if understanding.get("patterns"):
                console.print(f"[bold]Patterns:[/bold] {', '.join(understanding['patterns'])}")

            if understanding.get("ignition_patterns"):
                console.print(f"[bold]Ignition Patterns:[/bold] {', '.join(understanding['ignition_patterns'])}")

        # Suggestions
        if result.suggestions:
            console.print("\n[bold yellow]💡 Improvement Suggestions:[/bold yellow]")
            for i, suggestion in enumerate(result.suggestions, 1):
                console.print(f"  {i}. [{suggestion['type'].upper()}] {suggestion['suggestion']}")

        # Processing info
        console.print(f"\n[bold]Processing Time:[/bold] {result.processing_time:.2f}s")
        if result.models_used:
            console.print(f"[bold]Models Used:[/bold] {', '.join(result.models_used)}")

        # Save to output file if requested
        if output:
            try:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(result.dict(), f, indent=2, default=str)
                console.print(f"\n[green]📄 Results saved to: {output}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to save results: {e}[/red]")


@code.command()
@click.argument("script_path")
@click.option(
    "--show-available/--hide-available",
    default=False,
    help="Show all available modules in environment",
)
@click.option(
    "--suggest-fixes/--no-suggestions",
    default=True,
    help="Suggest fixes for missing imports",
)
def validate_imports(script_path: str, show_available: bool, suggest_fixes: bool) -> Any:
    """Validate imports against available modules in the environment.

    Examples:
        ign code validate-imports my_script.py
        ign code validate-imports script.py --show-available
    """
    console.print("\n[bold blue]📦 Import Validator[/bold blue]")
    console.print("Checking imports against available modules...\n")

    # Input validation
    path_validation = validate_script_path(script_path)
    if not path_validation["valid"]:
        console.print("[bold red]❌ Input validation failed:[/bold red]")
        for error in path_validation["errors"]:
            console.print(f"  • {error}")
        return

    sanitized_path = path_validation["sanitized_path"]

    # Run import validation
    async def run_import_validation() -> Any:
        try:
            validator = EnhancedCodeValidator()
            await validator.initialize()

            result = await validator.validate_script(
                script_path=sanitized_path,
                validation_type="imports",
                use_knowledge_graph=False,
            )

            await validator.cleanup()
            return result
        except Exception as e:
            console.print(f"[bold red]❌ Import validation failed: {format_cli_error(e)}[/bold red]")
            return None

    result = asyncio.run(run_import_validation())

    if result and result.success:
        if result.imports_valid:
            console.print("[bold green]✅ All imports are valid![/bold green]")
        else:
            console.print("[bold red]❌ Missing or invalid imports found![/bold red]")

            for missing in result.missing_imports:
                console.print(f"  • {missing}")

            if suggest_fixes and result.suggested_imports:
                console.print("\n[bold yellow]💡 Suggested fixes:[/bold yellow]")
                for suggestion in result.suggested_imports:
                    console.print(f"  • {suggestion}")


@code.command()
@click.argument("script_path")
@click.option("--model-preference", default="qwen", help="Preferred model: qwen, codellama, auto")
@click.option(
    "--focus",
    multiple=True,
    help="Focus areas: structure, quality, maintainability, patterns",
)
def suggest_improvements(script_path: str, model_preference: str, focus: tuple) -> Any:
    """AI-powered improvement suggestions for Python scripts.

    Examples:
        ign code suggest-improvements my_script.py
        ign code suggest-improvements script.py --focus structure --focus quality
    """
    console.print("\n[bold blue]💡 AI Improvement Suggestions[/bold blue]")
    console.print("Analyzing code for improvement opportunities...\n")

    # Input validation
    path_validation = validate_script_path(script_path)
    if not path_validation["valid"]:
        console.print("[bold red]❌ Input validation failed:[/bold red]")
        for error in path_validation["errors"]:
            console.print(f"  • {error}")
        return

    sanitized_path = path_validation["sanitized_path"]

    # Run comprehensive analysis for suggestions
    async def run_suggestion_analysis() -> Any:
        try:
            analyzer = AIScriptAnalyzer()
            await analyzer.initialize()

            result = await analyzer.analyze_script(
                script_path=sanitized_path,
                analysis_type="comprehensive",
                model_preference=model_preference,
                include_suggestions=True,
            )

            return result
        except Exception as e:
            console.print(f"[bold red]❌ Analysis failed: {format_cli_error(e)}[/bold red]")
            return None

    result = asyncio.run(run_suggestion_analysis())

    if result and result.success:
        console.print("[bold green]✅ Analysis completed![/bold green]")

        if result.suggestions:
            # Filter by focus areas if specified
            filtered_suggestions = result.suggestions
            if focus:
                filtered_suggestions = [s for s in result.suggestions if s.get("type", "").lower() in focus]

            if filtered_suggestions:
                console.print("\n[bold yellow]💡 Improvement Suggestions:[/bold yellow]")
                for i, suggestion in enumerate(filtered_suggestions, 1):
                    suggestion_type = suggestion.get("type", "general").upper()
                    suggestion_text = suggestion.get("suggestion", "No suggestion available")
                    console.print(f"\n{i}. [bold][{suggestion_type}][/bold]")
                    console.print(f"   {suggestion_text}")
            else:
                console.print("[green]✅ No specific improvements needed in the selected focus areas![/green]")
        else:
            console.print("[green]✅ No improvements suggested - code looks good![/green]")


@code.command()
@click.argument("pattern")
@click.option("--source", help="Filter by source (e.g., github, documentation)")
@click.option("--limit", default=5, type=int, help="Maximum number of examples (1-20)")
def find_examples(pattern: str, source: str | None, limit: int) -> None:
    """Find real-world code examples from crawled data.

    Examples:
        ign code find-examples "tag read"
        ign code find-examples "system.opc" --source github
    """
    console.print("\n[bold blue]🔍 Code Example Finder[/bold blue]")
    console.print(f"Searching for examples of: [cyan]{pattern}[/cyan]\n")

    # This would integrate with the web intelligence system to search crawled data
    # For now, show placeholder implementation
    console.print("[yellow]⚠️  Example finder requires web intelligence data.[/yellow]")
    console.print("Run [cyan]ign web update[/cyan] to crawl documentation sources first.")

    # TODO: Integrate with web intelligence crawler results
    # - Search through crawled code examples
    # - Filter by source if specified
    # - Return relevant examples with context


# Register the command group
__all__ = ["code"]
