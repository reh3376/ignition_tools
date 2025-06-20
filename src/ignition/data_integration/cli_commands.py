"""CLI Commands for Data Integration System."""

import json
from datetime import datetime, timedelta

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
def data_integration() -> None:
    """🔗 Data Integration commands for databases, historians, and OPC tags."""
    pass


# Database Commands
@data_integration.group()
def database() -> None:
    """🗄️ Database connection and query commands."""
    pass


@database.command()
@click.option(
    "--config-name", default="neo4j_default", help="Database configuration name"
)
def test_connection(config_name: str) -> None:
    """Test database connection."""
    try:
        from .database_connections import DatabaseConnectionManager

        with console.status(f"[bold blue]Testing connection to {config_name}..."):
            manager = DatabaseConnectionManager()
            result = manager.test_connection(config_name)

        if result["success"]:
            console.print(
                f"✅ Connection successful to {result['db_type']}", style="green"
            )
            console.print(f"   Host: {result['host']}")
            console.print(f"   Database: {result['database']}")
            console.print(f"   Connection time: {result['connection_time_ms']:.2f}ms")
        else:
            console.print(f"❌ Connection failed: {result['error']}", style="red")

    except ImportError:
        console.print("❌ Database connection manager not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@database.command()
def list_configs() -> None:
    """List available database configurations."""
    try:
        from .database_connections import DatabaseConnectionManager

        manager = DatabaseConnectionManager()
        configs = manager.list_configurations()

        if not configs:
            console.print("No database configurations found", style="yellow")
            return

        table = Table(title="Available Database Configurations")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Host", style="blue")
        table.add_column("Database", style="magenta")

        for config_name in configs:
            config_info = manager.get_config_info(config_name)
            if config_info:
                table.add_row(
                    config_name,
                    config_info["db_type"],
                    f"{config_info['host']}:{config_info['port']}",
                    config_info["database"],
                )

        console.print(table)

    except ImportError:
        console.print("❌ Database connection manager not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@database.command()
@click.option("--config-name", required=True, help="Database configuration name")
@click.option("--query", required=True, help="SQL query to execute")
@click.option("--limit", default=10, help="Limit number of results")
def query(config_name: str, query: str, limit: int) -> None:
    """Execute a database query."""
    try:
        from .database_connections import DatabaseConnectionManager

        manager = DatabaseConnectionManager()

        with console.status("[bold blue]Executing query..."):
            with manager.get_connection(config_name) as connection_id:
                results = manager.execute_query(connection_id, query)

        if not results:
            console.print("Query returned no results", style="yellow")
            return

        # Display results in table format
        if isinstance(results[0], dict):
            table = Table(
                title=f"Query Results (showing first {min(limit, len(results))} rows)"
            )

            # Add columns from first result
            for key in results[0]:
                table.add_column(str(key), style="cyan")

            # Add rows
            for row in results[:limit]:
                table.add_row(*[str(value) for value in row.values()])

            console.print(table)
            console.print(f"Total results: {len(results)}")
        else:
            console.print(f"Query executed successfully. Results: {results}")

    except ImportError:
        console.print("❌ Database connection manager not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


# Historian Commands
@data_integration.group()
def historian() -> None:
    """📈 Historian and time series database commands."""
    pass


@historian.command()
@click.option(
    "--historian-type",
    type=click.Choice(["influxdb", "timescaledb", "ignition_historian"]),
    default="influxdb",
    help="Type of historian database",
)
@click.option("--tags", required=True, help="Comma-separated list of tag names")
@click.option("--hours", default=24, help="Number of hours of data to query")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format",
)
def query_raw(historian_type: str, tags: str, hours: int, output_format: str) -> None:
    """Query raw historical data."""
    try:
        from .historian_queries import HistorianQueryGenerator, HistorianType, TagFilter

        # Parse historian type
        hist_type = HistorianType(historian_type)
        generator = HistorianQueryGenerator(hist_type)

        # Parse tags
        tag_list = [TagFilter(tag_name=tag.strip()) for tag in tags.split(",")]

        # Create time range
        time_range = generator.create_time_range_from_duration(hours)

        # Generate query
        query = generator.generate_raw_data_query(tag_list, time_range, limit=100)

        console.print(Panel(query, title=f"Generated {historian_type.upper()} Query"))

        if output_format == "json":
            query_info = {
                "historian_type": historian_type,
                "query": query,
                "tags": tags.split(","),
                "time_range": {
                    "start": time_range.start_time.isoformat(),
                    "end": time_range.end_time.isoformat(),
                },
            }
            console.print(json.dumps(query_info, indent=2))

    except ImportError:
        console.print("❌ Historian query generator not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@historian.command()
@click.option(
    "--historian-type",
    type=click.Choice(["influxdb", "timescaledb", "ignition_historian"]),
    default="influxdb",
    help="Type of historian database",
)
@click.option("--tags", required=True, help="Comma-separated list of tag names")
@click.option(
    "--aggregation",
    type=click.Choice(["avg", "min", "max", "sum", "count"]),
    default="avg",
    help="Aggregation function",
)
@click.option("--interval", default="1", help="Aggregation interval")
@click.option(
    "--unit",
    type=click.Choice(["s", "m", "h", "d"]),
    default="h",
    help="Time unit for aggregation",
)
@click.option("--hours", default=24, help="Number of hours of data to query")
def query_aggregated(
    historian_type: str,
    tags: str,
    aggregation: str,
    interval: str,
    unit: str,
    hours: int,
):
    """Query aggregated historical data."""
    try:
        from .historian_queries import (
            AggregationType,
            HistorianQueryGenerator,
            HistorianType,
            TagFilter,
            TimeUnit,
        )

        # Parse parameters
        hist_type = HistorianType(historian_type)
        agg_type = AggregationType(aggregation)
        time_unit = TimeUnit(unit)

        generator = HistorianQueryGenerator(hist_type)
        tag_list = [TagFilter(tag_name=tag.strip()) for tag in tags.split(",")]
        time_range = generator.create_time_range_from_duration(hours)

        # Generate aggregated query
        query = generator.generate_aggregated_query(
            tag_list, time_range, agg_type, interval, time_unit, limit=100
        )

        console.print(
            Panel(query, title=f"Generated {historian_type.upper()} Aggregated Query")
        )

        # Show query details
        details = Table(title="Query Details")
        details.add_column("Parameter", style="cyan")
        details.add_column("Value", style="green")

        details.add_row("Historian Type", historian_type)
        details.add_row("Tags", tags)
        details.add_row("Aggregation", f"{aggregation} every {interval}{unit}")
        details.add_row("Time Range", f"Last {hours} hours")
        details.add_row(
            "Start Time", time_range.start_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        details.add_row("End Time", time_range.end_time.strftime("%Y-%m-%d %H:%M:%S"))

        console.print(details)

    except ImportError:
        console.print("❌ Historian query generator not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


# OPC Tag Commands
@data_integration.group()
def tags() -> None:
    """🏷️ OPC tag management commands."""
    pass


@tags.command()
@click.option("--path", default="", help="Tag path to browse (default: root)")
@click.option("--provider", default="default", help="Tag provider name")
def browse(path: str, provider: str) -> None:
    """Browse OPC tags."""
    try:
        from .opc_tag_manager import OPCTagManager

        manager = OPCTagManager(provider)

        with console.status(f"[bold blue]Browsing tags at {path or 'root'}..."):
            result = manager.browse_tags(path)

        if not result["success"]:
            console.print(f"❌ Browse failed: {result['error']}", style="red")
            return

        # Display folders
        if result["folders"]:
            console.print(f"\n📁 Folders in {path or 'root'}:", style="bold blue")
            for folder in result["folders"]:
                console.print(f"  📁 {folder}")

        # Display tags
        if result["tags"]:
            table = Table(title=f"Tags in {path or 'root'}")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Value", style="yellow")
            table.add_column("Quality", style="blue")
            table.add_column("Description", style="magenta")

            for tag in result["tags"]:
                table.add_row(
                    tag["name"],
                    tag["data_type"],
                    str(tag["value"]),
                    tag["quality_name"],
                    tag.get("description", "")[:50],
                )

            console.print(table)

        console.print(f"\nTotal items: {result['total_items']}")

    except ImportError:
        console.print("❌ OPC tag manager not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@tags.command()
@click.option(
    "--tag-paths", required=True, help="Comma-separated list of tag paths to read"
)
@click.option("--provider", default="default", help="Tag provider name")
def read(tag_paths: str, provider: str) -> None:
    """Read OPC tag values."""
    try:
        from .opc_tag_manager import OPCTagManager

        manager = OPCTagManager(provider)
        paths = [path.strip() for path in tag_paths.split(",")]

        with console.status("[bold blue]Reading tag values..."):
            result = manager.read_tags(paths)

        if not result["success"]:
            console.print(f"❌ Read failed: {result['error']}", style="red")
            return

        table = Table(title="Tag Values")
        table.add_column("Tag Path", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Quality", style="blue")

        for tag_value in result["values"]:
            table.add_row(
                tag_value["tag_path"],
                str(tag_value["value"]),
                tag_value["quality_name"],
            )

        console.print(table)

    except ImportError:
        console.print("❌ OPC tag manager not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@tags.command()
@click.option("--name", required=True, help="Tag name")
@click.option("--path", required=True, help="Tag path")
@click.option(
    "--data-type",
    type=click.Choice(["Boolean", "Int4", "Float8", "String"]),
    default="Float8",
    help="Tag data type",
)
@click.option("--opc-path", help="OPC item path")
@click.option("--description", help="Tag description")
@click.option("--provider", default="default", help="Tag provider name")
def create(
    name: str,
    path: str,
    data_type: str,
    opc_path: str | None,
    description: str | None,
    provider: str,
):
    """Create a new OPC tag."""
    try:
        from .opc_tag_manager import OPCTagManager, TagDataType, TagDefinition

        manager = OPCTagManager(provider)

        # Create tag definition
        tag_def = TagDefinition(
            name=name,
            tag_path=path,
            data_type=TagDataType(data_type),
            opc_item_path=opc_path,
            description=description,
        )

        with console.status(f"[bold blue]Creating tag {name}..."):
            result = manager.create_tag(tag_def)

        if result["success"]:
            console.print(
                f"✅ Tag created successfully: {result['tag_path']}", style="green"
            )
            console.print(f"   Message: {result['message']}")
        else:
            console.print(f"❌ Tag creation failed: {result['error']}", style="red")

    except ImportError:
        console.print("❌ OPC tag manager not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


# Report Commands
@data_integration.group()
def reports() -> None:
    """📊 Report generation commands."""
    pass


@reports.command()
@click.option("--hours", default=24, help="Number of hours for production report")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["csv", "json", "html"]),
    default="csv",
    help="Report output format",
)
@click.option("--output", help="Output file path")
def production(hours: int, output_format: str, output: str | None) -> None:
    """Generate production report."""
    try:
        from .report_generator import ReportFormat, ReportGenerator

        generator = ReportGenerator()

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        # Mock tags for production report
        tags = ["Line_A_Production", "Line_B_Production", "Line_C_Production"]

        with console.status("[bold blue]Generating production report..."):
            result = generator.generate_production_report(
                start_time, end_time, tags, ReportFormat(output_format)
            )

        if result["success"]:
            console.print("✅ Production report generated successfully", style="green")
            console.print(f"   Format: {output_format.upper()}")
            console.print(f"   Records: {result.get('row_count', 'N/A')}")

            if output:
                with open(output, "w") as f:
                    f.write(result["content"])
                console.print(f"   Saved to: {output}")
            else:
                console.print("\n📄 Report Content:")
                console.print(
                    result["content"][:500] + "..."
                    if len(result["content"]) > 500
                    else result["content"]
                )
        else:
            console.print(
                f"❌ Report generation failed: {result['error']}", style="red"
            )

    except ImportError:
        console.print("❌ Report generator not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@reports.command()
@click.option("--hours", default=24, help="Number of hours for alarm report")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["csv", "json", "html"]),
    default="csv",
    help="Report output format",
)
@click.option("--output", help="Output file path")
def alarms(hours: int, output_format: str, output: str | None) -> None:
    """Generate alarm report."""
    try:
        from .report_generator import ReportFormat, ReportGenerator

        generator = ReportGenerator()

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        with console.status("[bold blue]Generating alarm report..."):
            result = generator.generate_alarm_report(
                start_time, end_time, format_type=ReportFormat(output_format)
            )

        if result["success"]:
            console.print("✅ Alarm report generated successfully", style="green")
            console.print(f"   Format: {output_format.upper()}")
            console.print(f"   Records: {result.get('row_count', 'N/A')}")

            if output:
                with open(output, "w") as f:
                    f.write(result["content"])
                console.print(f"   Saved to: {output}")
            else:
                console.print("\n📄 Report Content:")
                console.print(
                    result["content"][:500] + "..."
                    if len(result["content"]) > 500
                    else result["content"]
                )
        else:
            console.print(
                f"❌ Report generation failed: {result['error']}", style="red"
            )

    except ImportError:
        console.print("❌ Report generator not available", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@data_integration.command()
def status() -> None:
    """Show data integration system status."""
    console.print("🔗 Data Integration System Status", style="bold blue")
    console.print("=" * 50)

    # Check database connections
    try:
        from .database_connections import DatabaseConnectionManager

        manager = DatabaseConnectionManager()
        configs = manager.list_configurations()
        console.print(f"📊 Database Configurations: {len(configs)}")
        for config in configs:
            console.print(f"   • {config}")
    except ImportError:
        console.print("📊 Database Connections: Not available", style="yellow")

    # Check historian capabilities
    try:
        from .historian_queries import HistorianType

        console.print(f"📈 Historian Types: {len(HistorianType)}")
        for hist_type in HistorianType:
            console.print(f"   • {hist_type.value}")
    except ImportError:
        console.print("📈 Historian Queries: Not available", style="yellow")

    # Check OPC tag management
    try:
        from .opc_tag_manager import OPCTagManager

        console.print("🏷️ OPC Tag Management: Available", style="green")
    except ImportError:
        console.print("🏷️ OPC Tag Management: Not available", style="yellow")

    # Check report generation
    try:
        from .report_generator import ReportFormat, ReportGenerator

        console.print(f"📊 Report Formats: {len(ReportFormat)}")
        for format_type in ReportFormat:
            console.print(f"   • {format_type.value}")
    except ImportError:
        console.print("📊 Report Generation: Not available", style="yellow")

    console.print("\n✅ Data Integration System operational", style="green")
