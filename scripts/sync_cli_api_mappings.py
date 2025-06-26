#!/usr/bin/env python3
"""
Sync CLI to API Mappings to Neo4j Knowledge Graph

This script follows the crawl_mcp.py methodology to update the Neo4j knowledge graph
with CLI command to API endpoint mappings, enabling AI agents to understand the
relationship between CLI functionality and REST API endpoints.
"""

import json
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

# Initialize console for rich output
console = Console()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CLICommand:
    """Represents a CLI command."""

    command: str
    description: str
    category: str


@dataclass
class APIEndpoint:
    """Represents an API endpoint."""

    path: str
    method: str
    request_body: dict[str, Any] | None = None
    description: str | None = None


@dataclass
class CLIAPIMapping:
    """Represents a mapping between CLI command and API endpoint."""

    cli_command: CLICommand
    api_endpoint: APIEndpoint


class Neo4jService:
    """Service for interacting with Neo4j knowledge graph."""

    def __init__(self):
        """Initialize Neo4j connection following crawl_mcp.py patterns."""
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "ign_knowledge")
        self.driver = None

    def validate_environment(self) -> bool:
        """Validate Neo4j environment configuration."""
        if not all([self.uri, self.password]):
            console.print("[red]❌ Missing Neo4j configuration[/red]")
            console.print("Required environment variables:")
            console.print("  - NEO4J_URI")
            console.print("  - NEO4J_PASSWORD")
            return False
        return True

    def connect(self) -> bool:
        """Connect to Neo4j database."""
        try:
            if not self.uri or not self.password:
                console.print("[red]❌ Neo4j configuration not properly set[/red]")
                return False

            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            console.print(f"[green]✅ Connected to Neo4j at {self.uri}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to connect to Neo4j: {e}[/red]")
            return False

    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()

    def create_cli_api_mapping(self, mapping: CLIAPIMapping) -> bool:
        """Create or update CLI to API mapping in knowledge graph."""
        try:
            with self.driver.session(database=self.database) as session:
                query = """
                MERGE (cli:CLICommand {name: $cli_name})
                SET cli.description = $cli_description,
                    cli.category = $cli_category

                MERGE (api:APIEndpoint {path: $api_path, method: $api_method})
                SET api.description = $api_description,
                    api.request_body = $request_body

                MERGE (cli)-[r:MAPS_TO]->(api)
                SET r.updated_at = datetime()

                RETURN cli, api, r
                """

                result = session.run(
                    query,
                    {
                        "cli_name": mapping.cli_command.command,
                        "cli_description": mapping.cli_command.description,
                        "cli_category": mapping.cli_command.category,
                        "api_path": mapping.api_endpoint.path,
                        "api_method": mapping.api_endpoint.method,
                        "api_description": mapping.api_endpoint.description or "",
                        "request_body": (
                            json.dumps(mapping.api_endpoint.request_body) if mapping.api_endpoint.request_body else ""
                        ),
                    },
                )

                return result.single() is not None

        except Exception as e:
            logger.error(f"Failed to create mapping: {e}")
            return False

    def get_statistics(self) -> dict[str, int]:
        """Get statistics about CLI/API mappings."""
        try:
            with self.driver.session(database=self.database) as session:
                stats_query = """
                MATCH (cli:CLICommand)
                WITH count(cli) as cli_count
                MATCH (api:APIEndpoint)
                WITH cli_count, count(api) as api_count
                MATCH (:CLICommand)-[r:MAPS_TO]->(:APIEndpoint)
                RETURN cli_count, api_count, count(r) as mapping_count
                """

                result = session.run(stats_query).single()
                if result:
                    return {
                        "cli_commands": result["cli_count"],
                        "api_endpoints": result["api_count"],
                        "mappings": result["mapping_count"],
                    }
                return {"cli_commands": 0, "api_endpoints": 0, "mappings": 0}

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"cli_commands": 0, "api_endpoints": 0, "mappings": 0}


def get_cli_api_mappings() -> list[CLIAPIMapping]:
    """Get all CLI to API mappings from the decoupling plan."""
    mappings = []

    # Script Generation Commands
    script_mappings = [
        CLIAPIMapping(
            CLICommand(
                "ign script generate <type>",
                "Generate scripts from templates",
                "Script Generation",
            ),
            APIEndpoint(
                "/api/v1/scripts/generate",
                "POST",
                {"template_type": "string", "parameters": "object"},
            ),
        ),
        CLIAPIMapping(
            CLICommand("ign script list", "List available scripts", "Script Generation"),
            APIEndpoint("/api/v1/scripts", "GET"),
        ),
        CLIAPIMapping(
            CLICommand("ign script analyze <file>", "Analyze script file", "Script Generation"),
            APIEndpoint("/api/v1/scripts/analyze", "POST", {"file_path": "string"}),
        ),
        CLIAPIMapping(
            CLICommand(
                "ign script validate <file>",
                "Validate script content",
                "Script Generation",
            ),
            APIEndpoint("/api/v1/scripts/validate", "POST", {"script_content": "string"}),
        ),
    ]
    mappings.extend(script_mappings)

    # Template Management Commands
    template_mappings = [
        CLIAPIMapping(
            CLICommand("ign template list", "List available templates", "Template Management"),
            APIEndpoint("/api/v1/templates", "GET"),
        ),
        CLIAPIMapping(
            CLICommand("ign template get <name>", "Get template by name", "Template Management"),
            APIEndpoint("/api/v1/templates/{name}", "GET"),
        ),
        CLIAPIMapping(
            CLICommand("ign template create", "Create new template", "Template Management"),
            APIEndpoint(
                "/api/v1/templates",
                "POST",
                {"name": "string", "content": "string", "parameters": "object"},
            ),
        ),
    ]
    mappings.extend(template_mappings)

    # SME Agent Commands
    sme_mappings = [
        CLIAPIMapping(
            CLICommand("ign module sme validate-env", "Validate SME environment", "SME Agent"),
            APIEndpoint("/api/v1/sme/validate-env", "GET"),
        ),
        CLIAPIMapping(
            CLICommand("ign module sme status", "Get SME agent status", "SME Agent"),
            APIEndpoint("/api/v1/sme/status", "GET"),
        ),
        CLIAPIMapping(
            CLICommand(
                'ign module sme ask "<question>"',
                "Ask SME agent a question",
                "SME Agent",
            ),
            APIEndpoint("/api/v1/sme/ask", "POST", {"question": "string", "context": "object"}),
        ),
    ]
    mappings.extend(sme_mappings)

    # Refactoring Commands
    refactor_mappings = [
        CLIAPIMapping(
            CLICommand("refactor detect", "Detect files needing refactoring", "Refactoring"),
            APIEndpoint("/api/v1/refactor/detect", "GET"),
        ),
        CLIAPIMapping(
            CLICommand("refactor analyze <file>", "Analyze file for refactoring", "Refactoring"),
            APIEndpoint("/api/v1/refactor/analyze", "POST", {"file_path": "string"}),
        ),
        CLIAPIMapping(
            CLICommand("refactor split <file>", "Split large file", "Refactoring"),
            APIEndpoint(
                "/api/v1/refactor/split",
                "POST",
                {"file_path": "string", "strategy": "string"},
            ),
        ),
    ]
    mappings.extend(refactor_mappings)

    # Add more mappings as needed...

    return mappings


def main():
    """Main function following crawl_mcp.py methodology."""
    console.print("[bold blue]IGN Scripts CLI to API Mapping Sync[/bold blue]")
    console.print("Following crawl_mcp.py methodology for systematic updates\n")

    # Step 1: Environment Validation
    console.print("[yellow]Step 1: Validating Environment[/yellow]")
    neo4j_service = Neo4jService()

    if not neo4j_service.validate_environment():
        console.print("[red]Environment validation failed. Exiting.[/red]")
        return 1

    # Step 2: Connect to Neo4j
    console.print("\n[yellow]Step 2: Connecting to Neo4j[/yellow]")
    if not neo4j_service.connect():
        console.print("[red]Failed to connect to Neo4j. Exiting.[/red]")
        return 1

    try:
        # Step 3: Get current statistics
        console.print("\n[yellow]Step 3: Current Knowledge Graph Statistics[/yellow]")
        stats_before = neo4j_service.get_statistics()

        table = Table(title="Before Sync")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        table.add_row("CLI Commands", str(stats_before["cli_commands"]))
        table.add_row("API Endpoints", str(stats_before["api_endpoints"]))
        table.add_row("Mappings", str(stats_before["mappings"]))
        console.print(table)

        # Step 4: Load mappings
        console.print("\n[yellow]Step 4: Loading CLI to API Mappings[/yellow]")
        mappings = get_cli_api_mappings()
        console.print(f"Found {len(mappings)} mappings to sync")

        # Step 5: Sync mappings
        console.print("\n[yellow]Step 5: Syncing Mappings to Neo4j[/yellow]")
        success_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Syncing mappings...", total=len(mappings))

            for mapping in mappings:
                if neo4j_service.create_cli_api_mapping(mapping):
                    success_count += 1
                progress.update(task, advance=1)

        console.print(f"\n[green]✅ Successfully synced {success_count}/{len(mappings)} mappings[/green]")

        # Step 6: Show updated statistics
        console.print("\n[yellow]Step 6: Updated Knowledge Graph Statistics[/yellow]")
        stats_after = neo4j_service.get_statistics()

        table = Table(title="After Sync")
        table.add_column("Metric", style="cyan")
        table.add_column("Before", style="yellow")
        table.add_column("After", style="green")
        table.add_column("Change", style="blue")

        for metric in ["cli_commands", "api_endpoints", "mappings"]:
            before = stats_before[metric]
            after = stats_after[metric]
            change = after - before
            change_str = f"+{change}" if change > 0 else str(change)

            table.add_row(metric.replace("_", " ").title(), str(before), str(after), change_str)

        console.print(table)

        console.print("\n[green]✅ CLI to API mapping sync completed successfully![/green]")

    except Exception as e:
        console.print(f"\n[red]❌ Error during sync: {e}[/red]")
        logger.exception("Sync failed")
        return 1

    finally:
        neo4j_service.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
