"""CLI commands for Script Generation Module functionality."""

import json
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from ..script_generation import (
    CodeIntelligenceIntegration,
    DynamicScriptGenerator,
    TemplateManager,
)

console = Console()


@click.group(name="script")
def script_group() -> None:
    """Script generation and template management commands."""
    pass


@script_group.command()
@click.argument(
    "context",
    type=click.Choice(["gateway", "client", "designer", "perspective", "tag", "alarm"]),
)
@click.argument("script_type")
@click.option("--template", "-t", help="Template name to use")
@click.option("--output", "-o", help="Output file path")
@click.option("--project", "-p", help="Project context for analysis")
@click.option("--ai-assist", is_flag=True, help="Enable AI-powered recommendations")
def generate(
    context: str,
    script_type: str,
    template: str | None,
    output: str | None,
    project: str | None,
    ai_assist: bool,
) -> None:
    """Generate a script for a specific Ignition context."""
    console.print(f"🚀 Generating {script_type} script for {context} context...")

    try:
        # Initialize generator
        generator = DynamicScriptGenerator()

        # Prepare context data
        context_data = {
            "context": context,
            "script_type": script_type,
            "project": project,
            "ai_assist": ai_assist,
        }

        # Generate script
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating script...", total=None)

            if template:
                script_content = generator.generate_from_template(
                    template, context_data
                )
            else:
                script_content = generator.generate_dynamic_script(context_data)

            progress.update(task, completed=True)

        # Display or save script
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(script_content)
            console.print(f"✅ Script saved to: {output_path}")
        else:
            # Display script with syntax highlighting
            syntax = Syntax(
                script_content, "python", theme="monokai", line_numbers=True
            )
            console.print(Panel(syntax, title=f"{context} {script_type} Script"))

        # Show AI recommendations if enabled
        if ai_assist:
            _show_ai_recommendations(context, script_type, script_content)

    except Exception as e:
        console.print(f"❌ Failed to generate script: {e}")


@script_group.command()
@click.option("--category", "-c", help="Filter by category")
@click.option("--context", help="Filter by Ignition context")
@click.option("--search", "-s", help="Search templates by name or description")
def templates(category: str | None, context: str | None, search: str | None) -> None:
    """List available script templates."""
    try:
        manager = TemplateManager()

        # Get templates with filters
        all_templates = manager.list_templates(
            category=category, context=context, search=search
        )

        if not all_templates:
            console.print("No templates found matching criteria.")
            return

        # Group templates by category
        by_category: dict[str, list[Any]] = {}
        for template in all_templates:
            cat = template.get("category", "Uncategorized")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(template)

        # Display templates
        for cat, templates in by_category.items():
            console.print(f"\n📁 {cat}")

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Description")
            table.add_column("Context", style="green")
            table.add_column("Version", style="yellow")

            for tmpl in templates:
                table.add_row(
                    tmpl["name"],
                    tmpl.get("description", ""),
                    tmpl.get("context", "Any"),
                    tmpl.get("version", "1.0"),
                )

            console.print(table)

    except Exception as e:
        console.print(f"❌ Failed to list templates: {e}")


@script_group.command()
@click.argument("template_name")
def template_info(template_name: str) -> None:
    """Show detailed information about a template."""
    try:
        manager = TemplateManager()
        template = manager.get_template(template_name)

        if not template:
            console.print(f"❌ Template not found: {template_name}")
            return

        # Display template info
        console.print(
            Panel(f"[bold]{template['name']}[/bold]", title="Template Information")
        )

        # Basic info
        console.print(f"📝 Description: {template.get('description', 'N/A')}")
        console.print(f"📁 Category: {template.get('category', 'Uncategorized')}")
        console.print(f"🎯 Context: {template.get('context', 'Any')}")
        console.print(f"📌 Version: {template.get('version', '1.0')}")
        console.print(f"👤 Author: {template.get('author', 'Unknown')}")

        # Parameters
        if template.get("parameters"):
            console.print("\n⚙️ Parameters:")
            for param, info in template["parameters"].items():
                required = "Required" if info.get("required", False) else "Optional"
                console.print(
                    f"  • {param} ({required}): {info.get('description', '')}"
                )

        # Code preview
        if template.get("code"):
            console.print("\n📄 Code Preview:")
            syntax = Syntax(
                (
                    template["code"][:500] + "..."
                    if len(template["code"]) > 500
                    else template["code"]
                ),
                "python",
                theme="monokai",
                line_numbers=True,
            )
            console.print(syntax)

    except Exception as e:
        console.print(f"❌ Failed to get template info: {e}")


@script_group.command()
@click.argument("name")
@click.argument(
    "category",
    type=click.Choice(
        ["gateway", "client", "designer", "perspective", "tag", "alarm", "utility"]
    ),
)
@click.option("--description", "-d", help="Template description")
@click.option("--code-file", "-f", help="Path to code file")
@click.option("--parameters", "-p", help="Parameters as JSON")
def create_template(
    name: str,
    category: str,
    description: str | None,
    code_file: str | None,
    parameters: str | None,
) -> None:
    """Create a new script template."""
    try:
        manager = TemplateManager()

        # Load code from file if provided
        code = ""
        if code_file:
            code_path = Path(code_file)
            if not code_path.exists():
                console.print(f"❌ Code file not found: {code_file}")
                return
            code = code_path.read_text()
        else:
            # Interactive code input
            console.print("Enter template code (press Ctrl+D when done):")
            lines = []
            try:
                while True:
                    lines.append(input())
            except EOFError:
                code = "\n".join(lines)

        # Parse parameters
        params = {}
        if parameters:
            try:
                params = json.loads(parameters)
            except json.JSONDecodeError:
                console.print("❌ Invalid parameters JSON")
                return

        # Create template
        template_data = {
            "name": name,
            "category": category,
            "description": description or f"Template for {category} scripts",
            "code": code,
            "parameters": params,
        }

        result = manager.create_template(template_data)

        if result:
            console.print(f"✅ Template '{name}' created successfully!")
        else:
            console.print("❌ Failed to create template")

    except Exception as e:
        console.print(f"❌ Error creating template: {e}")


@script_group.command()
@click.argument("script_file")
@click.option("--context", help="Script context (gateway, client, etc.)")
@click.option("--fix", is_flag=True, help="Apply suggested fixes")
def analyze(script_file: str, context: str | None, fix: bool) -> None:
    """Analyze a script using code intelligence."""
    try:
        # Load script
        script_path = Path(script_file)
        if not script_path.exists():
            console.print(f"❌ Script file not found: {script_file}")
            return

        script_content = script_path.read_text()

        # Initialize code intelligence
        intelligence = CodeIntelligenceIntegration()

        console.print(f"🔍 Analyzing script: {script_file}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running analysis...", total=None)

            # Perform analysis
            analysis_result = intelligence.analyze_script(
                script_content, context=context, include_suggestions=True
            )

            progress.update(task, completed=True)

        # Display results
        _display_analysis_results(analysis_result)

        # Apply fixes if requested
        if fix and analysis_result.get("suggestions"):
            console.print("\n🔧 Applying suggested fixes...")
            fixed_content = intelligence.apply_suggestions(
                script_content, analysis_result["suggestions"]
            )

            # Save fixed script
            backup_path = script_path.with_suffix(script_path.suffix + ".bak")
            script_path.rename(backup_path)
            script_path.write_text(fixed_content)

            console.print(f"✅ Fixes applied. Original backed up to: {backup_path}")

    except Exception as e:
        console.print(f"❌ Analysis failed: {e}")


@script_group.command()
@click.argument("query")
@click.option("--limit", "-l", default=10, help="Maximum results to return")
@click.option("--context", help="Filter by context")
def search(query: str, limit: int, context: str | None) -> None:
    """Search for scripts using AI-powered semantic search."""
    try:
        intelligence = CodeIntelligenceIntegration()

        console.print(f"🔍 Searching for: {query}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching...", total=None)

            results = intelligence.semantic_search(
                query, limit=limit, context_filter=context
            )

            progress.update(task, completed=True)

        if not results:
            console.print("No results found.")
            return

        # Display results
        console.print(f"\n📋 Found {len(results)} results:")

        for i, result in enumerate(results, 1):
            score = result.get("score", 0.0)
            console.print(f"\n{i}. [bold]{result['name']}[/bold] (Score: {score:.2f})")
            console.print(f"   Context: {result.get('context', 'Unknown')}")
            console.print(f"   Description: {result.get('description', 'N/A')}")

            # Show code snippet
            if result.get("snippet"):
                syntax = Syntax(
                    result["snippet"], "python", theme="monokai", line_numbers=False
                )
                console.print(Panel(syntax, title="Code Snippet"))

    except Exception as e:
        console.print(f"❌ Search failed: {e}")


def _show_ai_recommendations(
    context: str, script_type: str, script_content: str
) -> None:
    """Display AI-powered recommendations for the generated script."""
    try:
        intelligence = CodeIntelligenceIntegration()
        recommendations = intelligence.get_recommendations(
            script_content, context=context, script_type=script_type
        )

        if recommendations:
            console.print("\n🤖 AI Recommendations:")
            for rec in recommendations:
                console.print(f"  • {rec['type']}: {rec['message']}")
                if rec.get("code_suggestion"):
                    syntax = Syntax(
                        rec["code_suggestion"],
                        "python",
                        theme="monokai",
                        line_numbers=False,
                    )
                    console.print(Panel(syntax, title="Suggested Code"))

    except Exception as e:
        console.print(f"⚠️ Could not generate AI recommendations: {e}")


def _display_analysis_results(results: dict[str, Any]) -> None:
    """Display code analysis results in a formatted way."""
    # Quality score
    score = results.get("quality_score", 0)
    score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
    console.print(f"\n📊 Quality Score: [{score_color}]{score}/100[/{score_color}]")

    # Issues
    issues = results.get("issues", [])
    if issues:
        console.print("\n⚠️ Issues Found:")
        for issue in issues:
            severity_color = {"error": "red", "warning": "yellow", "info": "blue"}.get(
                issue.get("severity", "info"), "white"
            )

            console.print(
                f"  [{severity_color}]{issue['severity'].upper()}[/{severity_color}] "
                f"Line {issue.get('line', '?')}: {issue['message']}"
            )

    # Suggestions
    suggestions = results.get("suggestions", [])
    if suggestions:
        console.print("\n💡 Suggestions:")
        for suggestion in suggestions:
            console.print(f"  • {suggestion['message']}")

    # Best practices
    best_practices = results.get("best_practices", {})
    if best_practices:
        console.print("\n📋 Best Practices Check:")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Practice", style="cyan")
        table.add_column("Status", style="green")

        for practice, status in best_practices.items():
            status_icon = "✅" if status else "❌"
            table.add_row(practice, status_icon)

        console.print(table)


# Export the command group
__all__ = ["script_group"]
