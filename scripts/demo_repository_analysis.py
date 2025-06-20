#!/usr/bin/env python3
"""Demo Repository Analysis Script.

This script demonstrates the repository analysis capabilities by analyzing
a smaller repository first, then optionally the full Pydantic AI repository.

Usage:
    python scripts/demo_repository_analysis.py
    python scripts/demo_repository_analysis.py --full-analysis
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ignition.code_intelligence.repository_analyzer import RepositoryAnalyzer
from ignition.code_intelligence.repository_schema import RepositorySchema
from ignition.graph.client import IgnitionGraphClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)
console = Console()

# Demo repositories
DEMO_REPOS = [
    {
        "name": "pydantic-core",
        "url": "https://github.com/pydantic/pydantic-core.git",
        "description": "Core validation logic for Pydantic (smaller repo for testing)",
        "branch": "main",
    },
    {
        "name": "pydantic-ai",
        "url": "https://github.com/pydantic/pydantic-ai.git",
        "description": "Full Pydantic AI framework (larger repo)",
        "branch": "main",
    },
]


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Demo repository analysis")
    parser.add_argument(
        "--full-analysis",
        action="store_true",
        help="Run full Pydantic AI analysis (large repo)",
    )
    parser.add_argument(
        "--clear-all", action="store_true", help="Clear all existing data first"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    console.print(
        Panel(
            "🚀 Repository Analysis Demo\n\n"
            "This demo showcases the repository analysis capabilities\n"
            "by analyzing Python repositories and storing the results\n"
            "in Neo4j for LLM agent context.",
            title="Demo: Repository Analysis",
            style="blue",
        )
    )

    try:
        # Initialize graph client
        client = IgnitionGraphClient()

        if not client.connect():
            console.print("❌ Failed to connect to Neo4j database", style="red")
            console.print(
                "Make sure Neo4j is running: docker-compose up -d neo4j", style="yellow"
            )
            sys.exit(1)

        console.print("✅ Connected to Neo4j database", style="green")

        # Clear existing data if requested
        if args.clear_all:
            if Confirm.ask("This will clear ALL repository data. Continue?"):
                schema = RepositorySchema(client)
                schema.drop_repository_schema()
                console.print("🗑️  Cleared all repository data", style="yellow")
            else:
                console.print("Keeping existing data", style="blue")

        # Show current database state
        show_database_stats(client)

        # Choose repositories to analyze
        repos_to_analyze = []

        if args.full_analysis:
            repos_to_analyze = DEMO_REPOS
        else:
            # Start with smaller repo
            repos_to_analyze = [DEMO_REPOS[0]]

            if Confirm.ask(
                "Would you like to analyze the full Pydantic AI repo too? (This is larger and takes longer)"
            ):
                repos_to_analyze.append(DEMO_REPOS[1])

        # Analyze repositories
        analyzer = RepositoryAnalyzer(client)

        for repo in repos_to_analyze:
            console.print(f"\n📊 Analyzing: {repo['name']}", style="cyan")
            console.print(f"URL: {repo['url']}")
            console.print(f"Description: {repo['description']}")

            success = analyzer.analyze_repository(repo["url"], repo["branch"])

            if success:
                console.print(f"✅ Successfully analyzed {repo['name']}", style="green")

                # Show statistics for this repo
                stats = get_repo_stats(client, repo["name"])
                show_repo_stats(repo["name"], stats)

            else:
                console.print(f"❌ Failed to analyze {repo['name']}", style="red")

        # Final database state
        console.print("\n" + "=" * 60)
        console.print("📊 Final Database State", style="bold cyan")
        show_database_stats(client)

        # Show demo queries
        show_demo_queries(client)

        # Show next steps
        console.print(
            Panel(
                "🎯 Demo Complete!\n\n"
                "What you can do now:\n\n"
                "1. 🌐 Browse Neo4j: http://localhost:7474\n"
                "   • Username: neo4j\n"
                "   • Password: ignition-graph\n\n"
                "2. 🔍 Try example queries:\n"
                "   • MATCH (r:Repository) RETURN r.name, r.description\n"
                "   • MATCH (a:Agent) RETURN a.name, a.agent_type\n"
                "   • MATCH (f:Function) WHERE f.is_async = true RETURN f.name\n\n"
                "3. 🧠 Use for LLM context:\n"
                "   • Repository structure is graph-indexed\n"
                "   • Vector embeddings enable semantic search\n"
                "   • Agent and tool patterns identified",
                title="Demo Results",
                style="green",
            )
        )

    except KeyboardInterrupt:
        console.print("\n⚠️  Demo interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Demo error: {e}", style="red")
        logger.error(f"Demo error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if client:
            client.disconnect()


def show_database_stats(client: IgnitionGraphClient):
    """Show current database statistics."""
    try:
        # Get node counts
        node_query = """
        MATCH (n)
        RETURN labels(n)[0] as label, count(n) as count
        ORDER BY count DESC
        """
        node_results = client.execute_query(node_query)

        # Get relationship counts
        rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        """
        rel_results = client.execute_query(rel_query)

        # Create tables
        if node_results:
            node_table = Table(title="Node Counts")
            node_table.add_column("Node Type", style="cyan")
            node_table.add_column("Count", style="white", justify="right")

            for record in node_results[:10]:  # Top 10
                node_table.add_row(record["label"], str(record["count"]))

            console.print(node_table)

        if rel_results:
            rel_table = Table(title="Relationship Counts")
            rel_table.add_column("Relationship Type", style="green")
            rel_table.add_column("Count", style="white", justify="right")

            for record in rel_results[:10]:  # Top 10
                rel_table.add_row(record["rel_type"], str(record["count"]))

            console.print(rel_table)

    except Exception as e:
        logger.warning(f"Failed to get database stats: {e}")


def get_repo_stats(client: IgnitionGraphClient, repo_name: str) -> dict:
    """Get statistics for a specific repository."""
    try:
        query = """
        MATCH (r:Repository {name: $repo_name})
        OPTIONAL MATCH (r)-[:CONTAINS]->(d:Directory)
        OPTIONAL MATCH (r)-[:CONTAINS*]->(f:File)
        OPTIONAL MATCH (r)-[:CONTAINS*]->(c:Class)
        OPTIONAL MATCH (r)-[:CONTAINS*]->(fn:Function)
        OPTIONAL MATCH (r)-[:CONTAINS*]->(dep:Dependency)
        OPTIONAL MATCH (r)-[:CONTAINS*]->(a:Agent)
        OPTIONAL MATCH (r)-[:CONTAINS*]->(t:Tool)
        RETURN count(DISTINCT d) as directories,
               count(DISTINCT f) as files,
               count(DISTINCT c) as classes,
               count(DISTINCT fn) as functions,
               count(DISTINCT dep) as dependencies,
               count(DISTINCT a) as agents,
               count(DISTINCT t) as tools
        """

        result = client.execute_query(query, {"repo_name": repo_name})
        return result[0] if result else {}

    except Exception as e:
        logger.warning(f"Failed to get repo stats for {repo_name}: {e}")
        return {}


def show_repo_stats(repo_name: str, stats: dict):
    """Display repository statistics."""
    if not stats:
        return

    table = Table(title=f"Statistics: {repo_name}")
    table.add_column("Component", style="cyan")
    table.add_column("Count", style="white", justify="right")

    table.add_row("Directories", str(stats.get("directories", 0)))
    table.add_row("Files", str(stats.get("files", 0)))
    table.add_row("Classes", str(stats.get("classes", 0)))
    table.add_row("Functions", str(stats.get("functions", 0)))
    table.add_row("Dependencies", str(stats.get("dependencies", 0)))
    table.add_row("Agents", str(stats.get("agents", 0)))
    table.add_row("Tools", str(stats.get("tools", 0)))

    console.print(table)


def show_demo_queries(client: IgnitionGraphClient):
    """Show some demo queries and their results."""
    console.print("\n🔍 Demo Queries", style="bold cyan")

    queries = [
        {
            "title": "Repositories in Database",
            "query": "MATCH (r:Repository) RETURN r.name as name, r.stars as stars, r.language as language ORDER BY r.stars DESC",
            "description": "Shows all analyzed repositories with their GitHub stats",
        },
        {
            "title": "Async Functions",
            "query": "MATCH (f:Function) WHERE f.is_async = true RETURN f.name as name, f.module as module LIMIT 5",
            "description": "Shows async functions found in the codebase",
        },
        {
            "title": "Pydantic Models",
            "query": "MATCH (c:Class) WHERE c.is_pydantic_model = true RETURN c.name as name, c.module as module LIMIT 5",
            "description": "Shows Pydantic model classes",
        },
    ]

    for query_info in queries:
        try:
            console.print(f"\n📋 {query_info['title']}", style="yellow")
            console.print(f"   {query_info['description']}", style="dim")

            results = client.execute_query(query_info["query"])

            if results:
                # Create a simple table for results
                if len(results) > 0:
                    first_result = results[0]
                    headers = list(first_result.keys())

                    table = Table()
                    for header in headers:
                        table.add_column(header.title(), style="white")

                    for result in results[:5]:  # Limit to 5 results
                        row = [str(result.get(header, "")) for header in headers]
                        table.add_row(*row)

                    console.print(table)
                else:
                    console.print("   No results found", style="dim")
            else:
                console.print("   No results found", style="dim")

        except Exception as e:
            console.print(f"   Query failed: {e}", style="red")


if __name__ == "__main__":
    main()
