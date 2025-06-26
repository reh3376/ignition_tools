"""CLI commands for Code Intelligence System."""

import logging
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)


@click.group()
def code() -> None:
    """Code Intelligence commands for analyzing and searching code."""
    pass


@code.command()
@click.option("--detailed", is_flag=True, help="Show detailed information")
def status(detailed: bool) -> None:
    """Show code intelligence system status."""
    try:
        from src.ignition.code_intelligence import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Connecting to database...", total=None)

            # Connect to database
            client = IgnitionGraphClient()
            if not client.connect():
                console.print("❌ Failed to connect to Neo4j database", style="red")
                return

            progress.update(task, description="Initializing code intelligence...")
            manager = CodeIntelligenceManager(client)

            progress.update(task, description="Gathering statistics...")
            stats = manager.get_code_statistics()
            schema_info = manager.schema.get_schema_info()

        # Display status
        console.print("\n🧠 Code Intelligence System Status", style="bold blue")
        console.print("=" * 50)

        # Basic statistics
        stats_table = Table(title="📊 Code Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Count", style="green")

        stats_table.add_row("Files", str(stats.get("files", 0)))
        stats_table.add_row("Classes", str(stats.get("classes", 0)))
        stats_table.add_row("Methods", str(stats.get("methods", 0)))
        stats_table.add_row("Imports", str(stats.get("imports", 0)))

        console.print(stats_table)

        if detailed:
            # Schema information
            console.print("\n🗄️ Database Schema", style="bold")
            console.print(f"Constraints: {len(schema_info.get('constraints', []))}")
            console.print(f"Indexes: {len(schema_info.get('indexes', []))}")
            console.print(f"Schema Version: {schema_info.get('schema_version', 'Unknown')}")

            # Node counts
            node_counts = schema_info.get("node_counts", {})
            if node_counts:
                console.print("\n📈 Node Counts by Type:")
                for node_type, count in node_counts.items():
                    console.print(f"  {node_type}: {count}")

        console.print("\n✅ Code Intelligence System is operational", style="green")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.exception("Failed to get status")


@code.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--detailed", is_flag=True, help="Show detailed analysis")
def analyze(file_path: str, detailed: bool) -> None:
    """Analyze a specific file and store results."""
    try:
        from src.ignition.code_intelligence import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        file_path_obj = Path(file_path).absolute()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Connecting to database...", total=None)

            client = IgnitionGraphClient()
            if not client.connect():
                console.print("❌ Failed to connect to Neo4j database", style="red")
                return

            progress.update(task, description="Initializing code intelligence...")
            manager = CodeIntelligenceManager(client)

            progress.update(task, description=f"Analyzing {file_path}...")
            success = manager.analyze_and_store_file(file_path_obj)

        if success:
            console.print(f"✅ Successfully analyzed: {file_path}", style="green")

            if detailed:
                # Get file context
                relative_path = str(file_path_obj.relative_to(Path.cwd()))
                context = manager.get_file_context(relative_path)

                if context:
                    console.print(f"\n📁 File Analysis: {relative_path}", style="bold")

                    file_info = context.get("file", {})
                    console.print(f"Lines: {file_info.get('lines', 'N/A')}")
                    console.print(f"Complexity: {file_info.get('complexity', 'N/A')}")
                    console.print(f"Maintainability: {file_info.get('maintainability_index', 'N/A'):.1f}")

                    classes = context.get("classes", [])
                    methods = context.get("class_methods", []) + context.get("file_methods", [])
                    imports = context.get("imports", [])

                    console.print(f"Classes: {len(classes)}")
                    console.print(f"Methods: {len(methods)}")
                    console.print(f"Imports: {len(imports)}")

                    if classes:
                        console.print("\n📦 Classes:")
                        for cls in classes[:5]:  # Show first 5
                            console.print(f"  • {cls.get('name')} (complexity: {cls.get('complexity')})")

                    if methods:
                        console.print("\n🔧 Methods:")
                        for method in methods[:5]:  # Show first 5
                            console.print(f"  • {method.get('name')} (complexity: {method.get('complexity')})")
        else:
            console.print(f"❌ Failed to analyze: {file_path}", style="red")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.exception("Failed to analyze file")


@code.command()
@click.argument("directory_path", type=click.Path(exists=True))
@click.option("--recursive/--no-recursive", default=True, help="Analyze subdirectories")
def scan(directory_path: str, recursive: bool) -> None:
    """Scan and analyze all Python files in a directory."""
    try:
        from src.ignition.code_intelligence import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        dir_path = Path(directory_path).absolute()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Connecting to database...", total=None)

            client = IgnitionGraphClient()
            if not client.connect():
                console.print("❌ Failed to connect to Neo4j database", style="red")
                return

            progress.update(task, description="Initializing code intelligence...")
            manager = CodeIntelligenceManager(client)

            progress.update(task, description=f"Scanning {directory_path}...")
            results = manager.analyze_and_store_directory(dir_path, recursive)

        console.print(f"\n📂 Directory Scan Results: {directory_path}", style="bold blue")
        console.print(f"Files processed: {results['files_processed']}")
        console.print(f"Files successful: {results['files_successful']}", style="green")
        console.print(
            f"Files failed: {results['files_failed']}",
            style="red" if results["files_failed"] > 0 else "white",
        )

        if results["errors"]:
            console.print("\n❌ Errors encountered:")
            for error in results["errors"][:5]:  # Show first 5 errors
                console.print(f"  • {error}")

        if results["files_successful"] > 0:
            console.print("\n✅ Directory scan completed successfully", style="green")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.exception("Failed to scan directory")


@code.command()
@click.argument("query")
@click.option(
    "--type",
    "search_type",
    type=click.Choice(["all", "files", "classes", "methods"]),
    default="all",
    help="Type of code elements to search",
)
@click.option("--limit", default=10, help="Maximum number of results")
def search(query: str, search_type: str, limit: int) -> None:
    """Search for code elements by name or content."""
    try:
        from src.ignition.code_intelligence import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Searching...", total=None)

            client = IgnitionGraphClient()
            if not client.connect():
                console.print("❌ Failed to connect to Neo4j database", style="red")
                return

            manager = CodeIntelligenceManager(client)
            results = manager.search_code(query, search_type)

        if not results:
            console.print(f"No results found for '{query}'", style="yellow")
            return

        console.print(f"\n🔍 Search Results for '{query}' ({search_type})", style="bold blue")
        console.print(f"Found {len(results)} results (showing first {min(limit, len(results))})")

        # Create results table
        table = Table()
        table.add_column("Type", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("File", style="blue")
        table.add_column("Complexity", style="yellow")
        table.add_column("Line", style="white")

        for result in results[:limit]:
            table.add_row(
                result.get("type", "N/A"),
                result.get("name", "N/A"),
                result.get("file_path", "N/A"),
                str(result.get("complexity", "N/A")),
                str(result.get("start_line", "N/A")),
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.exception("Failed to search code")


@code.command()
@click.argument("file_path")
def context(file_path: str) -> None:
    """Get comprehensive context for a file."""
    try:
        from src.ignition.code_intelligence import CodeIntelligenceManager
        from src.ignition.graph.client import IgnitionGraphClient

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Getting context...", total=None)

            client = IgnitionGraphClient()
            if not client.connect():
                console.print("❌ Failed to connect to Neo4j database", style="red")
                return

            manager = CodeIntelligenceManager(client)
            context_data = manager.get_file_context(file_path)

        if not context_data or not context_data.get("file"):
            console.print(f"No context found for '{file_path}'", style="yellow")
            console.print("Make sure the file has been analyzed first using 'ign code analyze'")
            return

        console.print(f"\n📁 File Context: {file_path}", style="bold blue")

        file_info = context_data["file"]
        console.print(
            Panel(
                f"Lines: {file_info.get('lines', 'N/A')}\n"
                f"Complexity: {file_info.get('complexity', 'N/A')}\n"
                f"Maintainability: {file_info.get('maintainability_index', 'N/A'):.1f}\n"
                f"Language: {file_info.get('language', 'N/A')}\n"
                f"Size: {file_info.get('size_bytes', 'N/A')} bytes",
                title="📊 File Metrics",
            )
        )

        # Classes
        classes = context_data.get("classes", [])
        if classes:
            console.print(f"\n📦 Classes ({len(classes)}):")
            for cls in classes:
                console.print(
                    f"  • {cls.get('name')} (lines {cls.get('start_line')}-{cls.get('end_line')}, complexity: {cls.get('complexity')})"  # noqa: E501
                )

        # Methods
        class_methods = context_data.get("class_methods", [])
        file_methods = context_data.get("file_methods", [])
        all_methods = class_methods + file_methods

        if all_methods:
            console.print(f"\n🔧 Methods ({len(all_methods)}):")
            for method in all_methods:
                class_info = f" [{method.get('class_name')}]" if method.get("class_name") else ""
                console.print(
                    f"  • {method.get('name')}{class_info} (line {method.get('start_line')}, complexity: {method.get('complexity')})"  # noqa: E501
                )

        # Imports
        imports = context_data.get("imports", [])
        if imports:
            console.print(f"\n📥 Imports ({len(imports)}):")
            for imp in imports[:10]:  # Show first 10
                module = imp.get("from_module", imp.get("module", "N/A"))
                console.print(f"  • {module}")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        logger.exception("Failed to get context")
