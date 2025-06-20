"""CLI Commands for AI Assistant Enhancement - Phase 8.3.

Provides command-line interface for context-aware development and change impact analysis.
"""

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.group()
def ai() -> None:
    """AI Assistant Enhancement commands for context-aware development."""
    pass


@ai.command()
@click.argument("file_path")
def context(file_path: str) -> None:
    """Get smart context for a file."""
    try:
        from src.ignition.graph.client import IgnitionGraphClient

        from .ai_assistant_enhancement import AIAssistantEnhancement
        from .manager import CodeIntelligenceManager

        client = IgnitionGraphClient()
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j", style="red")
            return

        manager = CodeIntelligenceManager(client)
        ai_enhancement = AIAssistantEnhancement(manager)

        context_data = ai_enhancement.get_smart_context(file_path)

        console.print(f"\n🧠 Smart Context: {file_path}", style="bold blue")

        if context_data.file_metrics:
            metrics = context_data.file_metrics
            console.print(
                Panel(
                    f"Lines: {metrics.get('lines', 'N/A')}\n"
                    f"Complexity: {metrics.get('complexity', 'N/A'):.1f}\n"
                    f"Maintainability: {metrics.get('maintainability_index', 'N/A'):.1f}",
                    title="📊 Metrics",
                )
            )

        if context_data.refactoring_suggestions:
            console.print("\n💡 Suggestions:")
            for suggestion in context_data.refactoring_suggestions:
                console.print(f"  • {suggestion.get('description', 'No description')}")

    except Exception as e:
        console.print(f"❌ Error: {e!s}", style="red")


@ai.command()
@click.argument("file_path")
@click.argument("query")
def snippets(file_path: str, query: str) -> None:
    """Get relevant code snippets."""
    try:
        from src.ignition.graph.client import IgnitionGraphClient

        from .ai_assistant_enhancement import AIAssistantEnhancement
        from .manager import CodeIntelligenceManager

        client = IgnitionGraphClient()
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j", style="red")
            return

        manager = CodeIntelligenceManager(client)
        ai_enhancement = AIAssistantEnhancement(manager)

        snippets_data = ai_enhancement.get_relevant_snippets(file_path, query)

        if not snippets_data:
            console.print("No relevant snippets found", style="yellow")
            return

        console.print(f"\n🔍 Snippets for: '{query}'", style="bold blue")

        for i, snippet in enumerate(snippets_data, 1):
            console.print(f"\n{i}. {snippet['type'].title()}: {snippet['name']}")
            console.print(f"   Relevance: {snippet['relevance_score']:.2f}")

    except Exception as e:
        console.print(f"❌ Error: {e!s}", style="red")


@ai.command()
@click.argument("file_path")
def impact(file_path: str) -> None:
    """Analyze change impact."""
    try:
        from src.ignition.graph.client import IgnitionGraphClient

        from .ai_assistant_enhancement import AIAssistantEnhancement
        from .manager import CodeIntelligenceManager

        client = IgnitionGraphClient()
        if not client.connect():
            console.print("❌ Failed to connect to Neo4j", style="red")
            return

        manager = CodeIntelligenceManager(client)
        ai_enhancement = AIAssistantEnhancement(manager)

        impact_analysis = ai_enhancement.analyze_change_impact(file_path)

        console.print(f"\n🎯 Impact Analysis: {file_path}", style="bold blue")

        risk_color = {
            "critical": "red",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }.get(impact_analysis.risk_level, "white")
        console.print(f"Risk Level: [{risk_color}]{impact_analysis.risk_level.upper()}[/{risk_color}]")

        if impact_analysis.affected_files:
            console.print(f"\n📁 Affected Files ({len(impact_analysis.affected_files)}):")
            for file in impact_analysis.affected_files[:5]:
                console.print(f"  • {file}")

    except Exception as e:
        console.print(f"❌ Error: {e!s}", style="red")


if __name__ == "__main__":
    ai()
