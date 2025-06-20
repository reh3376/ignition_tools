#!/usr/bin/env python3
"""Analyze Pydantic AI Repository Script.

This script analyzes the Pydantic AI repository and stores the results
in the Neo4j graph database for LLM agent context.

Usage:
    python scripts/analyze_pydantic_ai.py
    python scripts/analyze_pydantic_ai.py --clear-existing
    python scripts/analyze_pydantic_ai.py --branch main
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
from rich.progress import Progress, SpinnerColumn, TextColumn

from ignition.graph.client import IgnitionGraphClient
from ignition.code_intelligence.repository_analyzer import RepositoryAnalyzer
from ignition.code_intelligence.repository_schema import RepositorySchema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)
console = Console()

# Pydantic AI repository URL
PYDANTIC_AI_REPO = "https://github.com/pydantic/pydantic-ai.git"


def main():
    """Main function to analyze Pydantic AI repository."""
    parser = argparse.ArgumentParser(description="Analyze Pydantic AI repository")
    parser.add_argument(
        "--branch", 
        default="main", 
        help="Branch to analyze (default: main)"
    )
    parser.add_argument(
        "--clear-existing", 
        action="store_true", 
        help="Clear existing repository data first"
    )
    parser.add_argument(
        "--repo-url",
        default=PYDANTIC_AI_REPO,
        help=f"Repository URL to analyze (default: {PYDANTIC_AI_REPO})"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(
        Panel(
            f"🔍 Pydantic AI Repository Analysis\n\n"
            f"Repository: {args.repo_url}\n"
            f"Branch: {args.branch}\n"
            f"Clear existing: {args.clear_existing}",
            title="Repository Analysis",
            style="blue"
        )
    )
    
    try:
        # Initialize graph client
        client = IgnitionGraphClient()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Connect to database
            task = progress.add_task("Connecting to Neo4j database...", total=None)
            if not client.connect():
                console.print("❌ Failed to connect to Neo4j database", style="red")
                console.print("Make sure Neo4j is running: docker-compose up -d neo4j", style="yellow")
                sys.exit(1)
            progress.update(task, description="✅ Connected to Neo4j")
            
            # Clear existing data if requested
            if args.clear_existing:
                progress.update(task, description="Clearing existing repository data...")
                schema = RepositorySchema(client)
                schema.drop_repository_schema()
                console.print("🗑️  Cleared existing repository data", style="yellow")
            
            # Initialize analyzer
            progress.update(task, description="Initializing repository analyzer...")
            analyzer = RepositoryAnalyzer(client)
            console.print("🧠 Repository analyzer initialized with sentence transformers", style="green")
            
            # Analyze repository
            progress.update(task, description=f"Analyzing repository: {args.repo_url}")
            console.print(f"📥 Cloning repository: {args.repo_url}", style="blue")
            console.print(f"🔍 Analyzing branch: {args.branch}", style="blue")
            
            success = analyzer.analyze_repository(args.repo_url, args.branch)
            
            if success:
                progress.update(task, description="✅ Repository analysis completed")
                
                # Get analysis statistics
                progress.update(task, description="Getting analysis statistics...")
                stats = get_analysis_stats(client, "pydantic-ai")
                
                console.print(
                    Panel(
                        f"✅ Repository analysis completed successfully!\n\n"
                        f"📊 Analysis Statistics:\n"
                        f"   • Directories: {stats['directories']:,}\n"
                        f"   • Files: {stats['files']:,}\n"
                        f"   • Classes: {stats['classes']:,}\n"
                        f"   • Functions: {stats['functions']:,}\n"
                        f"   • Dependencies: {stats['dependencies']:,}\n"
                        f"   • Agents: {stats['agents']:,}\n"
                        f"   • Tools: {stats['tools']:,}\n\n"
                        f"🎯 Ready for LLM agent context!",
                        title="Analysis Complete",
                        style="green",
                    )
                )
                
                # Show next steps
                console.print(
                    Panel(
                        "🚀 Next Steps:\n\n"
                        "1. Query the graph database:\n"
                        "   • Use Neo4j Browser: http://localhost:7474\n"
                        "   • Credentials: neo4j / ignition-graph\n\n"
                        "2. Search components:\n"
                        "   • python scripts/analyze_pydantic_ai.py --help\n"
                        "   • Use the CLI commands for exploration\n\n"
                        "3. Use for LLM context:\n"
                        "   • Repository structure is now available\n"
                        "   • Vector embeddings enable semantic search\n"
                        "   • Agent and tool information extracted",
                        title="What's Next?",
                        style="cyan"
                    )
                )
                
            else:
                console.print("❌ Repository analysis failed", style="red")
                sys.exit(1)
                
    except KeyboardInterrupt:
        console.print("\n⚠️  Analysis interrupted by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error during repository analysis: {e}", style="red")
        logger.error(f"Repository analysis error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if client:
            client.disconnect()


def get_analysis_stats(client: IgnitionGraphClient, repo_name: str) -> dict:
    """Get analysis statistics for the repository."""
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
        if result:
            return result[0]
        else:
            return {
                "directories": 0,
                "files": 0,
                "classes": 0,
                "functions": 0,
                "dependencies": 0,
                "agents": 0,
                "tools": 0,
            }
    except Exception as e:
        logger.warning(f"Failed to get analysis stats: {e}")
        return {
            "directories": 0,
            "files": 0,
            "classes": 0,
            "functions": 0,
            "dependencies": 0,
            "agents": 0,
            "tools": 0,
        }


if __name__ == "__main__":
    main() 