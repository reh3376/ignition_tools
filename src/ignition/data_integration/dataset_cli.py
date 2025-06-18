"""Dataset Management CLI Commands.

This module provides CLI commands for dataset creation, management, and
launching the interactive UI for dataset curation.
"""

import logging
import subprocess
import sys
import webbrowser
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

try:
    from .dataset_core import DataQuality, DatasetType, ProcessingStatus
    from .dataset_manager import DatasetManager
except ImportError as e:
    click.echo(f"Error importing dataset modules: {e}")
    sys.exit(1)

console = Console()
logger = logging.getLogger(__name__)


@click.group()
def dataset() -> None:
    """🧠 Dataset management for AI/ML model preparation."""
    pass


@dataset.command()
@click.option("--name", "-n", required=True, help="Dataset name")
@click.option(
    "--type",
    "-t",
    "dataset_type",
    type=click.Choice([dt.value for dt in DatasetType]),
    required=True,
    help="Dataset type",
)
@click.option("--description", "-d", help="Dataset description")
@click.option("--tags", help="Comma-separated tags")
def create(
    name: str, dataset_type: str, description: str | None, tags: str | None
) -> None:
    """Create a new dataset."""
    try:
        manager = DatasetManager()

        # Parse tags
        tag_list = (
            [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        )

        # Create dataset
        dataset = manager.create_dataset(
            name=name,
            dataset_type=DatasetType(dataset_type),
            description=description,
            tags=tag_list,
        )

        console.print(f"✅ Dataset '{name}' created successfully!", style="green")
        console.print(f"   ID: {dataset.dataset_id}")
        console.print(f"   Type: {dataset_type}")

        if description:
            console.print(f"   Description: {description}")

        if tag_list:
            console.print(f"   Tags: {', '.join(tag_list)}")

        # Suggest next steps
        console.print("\n💡 Next steps:", style="bold blue")
        console.print("   1. Add data sources: ign data dataset add-source")
        console.print("   2. Define features: ign data dataset add-feature")
        console.print(
            "   3. Launch UI for interactive curation: ign data dataset buildout"
        )

    except Exception as e:
        console.print(f"❌ Failed to create dataset: {e}", style="red")


@dataset.command()
def list() -> None:
    """List all datasets."""
    try:
        manager = DatasetManager()
        datasets = manager.list_datasets()

        if not datasets:
            console.print(
                "No datasets found. Create one with 'ign data dataset create'",
                style="yellow",
            )
            return

        # Create table
        table = Table(title="📊 Available Datasets")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="blue")
        table.add_column("Rows", justify="right", style="magenta")
        table.add_column("Quality", style="yellow")
        table.add_column("Created", style="dim")

        for ds in datasets:
            # Format status with color
            status = ds["status"]
            if status == "ready":
                status_text = Text(status, style="bold green")
            elif status == "validated":
                status_text = Text(status, style="bold blue")
            elif status == "in_progress":
                status_text = Text(status, style="bold yellow")
            else:
                status_text = Text(status, style="dim")

            # Format quality with color
            quality = ds["quality"]
            if quality == "excellent":
                quality_text = Text(quality, style="bold green")
            elif quality == "good":
                quality_text = Text(quality, style="green")
            elif quality == "fair":
                quality_text = Text(quality, style="yellow")
            elif quality == "poor":
                quality_text = Text(quality, style="red")
            else:
                quality_text = Text(quality, style="dim")

            table.add_row(
                ds["name"],
                ds["type"],
                status_text,
                f"{ds['row_count']:,}",
                quality_text,
                ds["created_at"][:10],  # Just the date
            )

        console.print(table)

        # Summary
        total_datasets = len(datasets)
        ready_datasets = sum(1 for ds in datasets if ds["status"] == "ready")
        total_rows = sum(ds["row_count"] for ds in datasets)

        console.print(
            f"\n📈 Summary: {total_datasets} datasets, {ready_datasets} ready for training, {total_rows:,} total rows"
        )

    except Exception as e:
        console.print(f"❌ Failed to list datasets: {e}", style="red")


@dataset.command()
@click.argument("dataset_id")
def info(dataset_id: str) -> None:
    """Show detailed information about a dataset."""
    try:
        manager = DatasetManager()
        dataset = manager.get_dataset(dataset_id)

        if not dataset:
            console.print(f"❌ Dataset '{dataset_id}' not found", style="red")
            return

        # Basic information panel
        info_text = f"""
Name: {dataset.name}
Type: {dataset.schema.dataset_type.value}
Status: {dataset.status.value}
Created: {dataset.created_at.strftime("%Y-%m-%d %H:%M:%S")}
Updated: {dataset.updated_at.strftime("%Y-%m-%d %H:%M:%S")}
Rows: {dataset.row_count:,}
Columns: {dataset.column_count}
Size: {dataset.file_size_mb:.2f} MB
"""

        if dataset.tags:
            info_text += f"Tags: {', '.join(dataset.tags)}\n"

        if dataset.schema.description:
            info_text += f"Description: {dataset.schema.description}\n"

        console.print(
            Panel(
                info_text.strip(), title="📊 Dataset Information", border_style="blue"
            )
        )

        # Data sources
        if dataset.data_sources:
            console.print("\n🔗 Data Sources:", style="bold")
            for i, source in enumerate(dataset.data_sources):
                status_icon = "🟢" if source.active else "🔴"
                console.print(
                    f"  {i + 1}. {status_icon} {source.source_type} ({source.source_id[:8]}...)"
                )
        else:
            console.print("\n🔗 Data Sources: None configured", style="yellow")

        # Features
        if dataset.schema.features:
            console.print(
                f"\n🎯 Features ({len(dataset.schema.features)}):", style="bold"
            )
            for feature in dataset.schema.features:
                target_icon = "🎯" if feature.is_target else "📊"
                transform_text = (
                    f" ({feature.transformation})" if feature.transformation else ""
                )
                console.print(
                    f"  {target_icon} {feature.name} [{feature.data_type}]{transform_text}"
                )
        else:
            console.print("\n🎯 Features: None defined", style="yellow")

        # Quality report
        if dataset.quality_report:
            quality = dataset.quality_report.overall_quality.value
            console.print(f"\n📈 Quality: {quality}", style="bold")
            console.print(
                f"  Completeness: {dataset.quality_report.completeness_score:.1f}%"
            )
            console.print(
                f"  Consistency: {dataset.quality_report.consistency_score:.1f}%"
            )
            console.print(f"  Accuracy: {dataset.quality_report.accuracy_score:.1f}%")
        else:
            console.print("\n📈 Quality: Not assessed", style="yellow")

    except Exception as e:
        console.print(f"❌ Failed to get dataset info: {e}", style="red")


@dataset.command()
@click.argument("dataset_id")
def process(dataset_id: str) -> None:
    """Process a dataset (extract, transform, validate)."""
    try:
        manager = DatasetManager()
        dataset = manager.get_dataset(dataset_id)

        if not dataset:
            console.print(f"❌ Dataset '{dataset_id}' not found", style="red")
            return

        console.print(f"🔄 Processing dataset '{dataset.name}'...", style="blue")

        with console.status("[bold blue]Processing..."):
            processed_data = manager.process_dataset(dataset_id)

        console.print("✅ Dataset processed successfully!", style="green")
        console.print(f"   Rows: {len(processed_data):,}")
        console.print(f"   Columns: {len(processed_data.columns)}")

        # Show updated dataset info
        updated_dataset = manager.get_dataset(dataset_id)
        if updated_dataset and updated_dataset.quality_report:
            quality = updated_dataset.quality_report.overall_quality.value
            console.print(f"   Quality: {quality}")

    except Exception as e:
        console.print(f"❌ Failed to process dataset: {e}", style="red")


@dataset.command()
@click.argument("dataset_id")
@click.option(
    "--format",
    "format_type",
    type=click.Choice(["csv", "parquet", "json"]),
    default="csv",
    help="Export format",
)
@click.option(
    "--include-metadata", is_flag=True, default=True, help="Include metadata in export"
)
def export(dataset_id: str, format_type: str, include_metadata: bool) -> None:
    """Export a dataset."""
    try:
        manager = DatasetManager()
        dataset = manager.get_dataset(dataset_id)

        if not dataset:
            console.print(f"❌ Dataset '{dataset_id}' not found", style="red")
            return

        console.print(
            f"📥 Exporting dataset '{dataset.name}' as {format_type.upper()}...",
            style="blue",
        )

        with console.status("[bold blue]Exporting..."):
            export_path = manager.export_dataset(
                dataset_id, format_type=format_type, include_metadata=include_metadata
            )

        console.print("✅ Dataset exported successfully!", style="green")
        console.print(f"   Location: {export_path}")

    except Exception as e:
        console.print(f"❌ Failed to export dataset: {e}", style="red")


@dataset.command()
@click.argument("dataset_id")
@click.confirmation_option(prompt="Are you sure you want to delete this dataset?")
def delete(dataset_id: str) -> None:
    """Delete a dataset."""
    try:
        manager = DatasetManager()
        dataset = manager.get_dataset(dataset_id)

        if not dataset:
            console.print(f"❌ Dataset '{dataset_id}' not found", style="red")
            return

        dataset_name = dataset.name

        if manager.delete_dataset(dataset_id):
            console.print(
                f"✅ Dataset '{dataset_name}' deleted successfully!", style="green"
            )
        else:
            console.print(f"❌ Failed to delete dataset '{dataset_name}'", style="red")

    except Exception as e:
        console.print(f"❌ Failed to delete dataset: {e}", style="red")


@dataset.command()
@click.option("--port", "-p", default=8501, help="Port for the UI server")
@click.option("--host", "-h", default="localhost", help="Host for the UI server")
@click.option(
    "--open-browser", is_flag=True, default=True, help="Open browser automatically"
)
def buildout(port: int, host: str, open_browser: bool) -> None:
    """🚀 Launch interactive dataset buildout UI."""
    try:
        # Check if streamlit is available
        try:
            import streamlit
        except ImportError:
            console.print(
                "❌ Streamlit not installed. Install with: pip install streamlit",
                style="red",
            )
            return

        # Find the UI script
        ui_script = Path(__file__).parent / "dataset_ui.py"

        if not ui_script.exists():
            console.print(f"❌ UI script not found at: {ui_script}", style="red")
            return

        console.print("🚀 Launching Dataset Curation Studio...", style="blue")
        console.print(f"   Host: {host}")
        console.print(f"   Port: {port}")
        console.print(f"   URL: http://{host}:{port}")

        # Launch streamlit
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ui_script),
            "--server.port",
            str(port),
            "--server.address",
            host,
            "--server.headless",
            "true" if not open_browser else "false",
        ]

        if open_browser:
            console.print("\n🌐 Opening browser...", style="green")
            # Give streamlit a moment to start
            import threading
            import time

            def open_browser_delayed() -> None:
                time.sleep(2)
                webbrowser.open(f"http://{host}:{port}")

            threading.Thread(target=open_browser_delayed).start()

        console.print("\n💡 Tip: Use Ctrl+C to stop the server", style="dim")
        console.print("=" * 50)

        # Run streamlit
        subprocess.run(cmd)

    except KeyboardInterrupt:
        console.print("\n👋 Dataset Curation Studio stopped.", style="blue")
    except Exception as e:
        console.print(f"❌ Failed to launch UI: {e}", style="red")


@dataset.command()
@click.option("--dataset-id", help="Specific dataset ID to check")
def status(dataset_id: str | None) -> None:
    """Show dataset system status."""
    try:
        manager = DatasetManager()

        if dataset_id:
            # Show specific dataset status
            dataset = manager.get_dataset(dataset_id)
            if not dataset:
                console.print(f"❌ Dataset '{dataset_id}' not found", style="red")
                return

            console.print(f"📊 Dataset Status: {dataset.name}", style="bold blue")
            console.print(f"   Status: {dataset.status.value}")
            console.print(f"   Rows: {dataset.row_count:,}")
            console.print(f"   Columns: {dataset.column_count}")

            if dataset.quality_report:
                console.print(
                    f"   Quality: {dataset.quality_report.overall_quality.value}"
                )
        else:
            # Show system overview
            datasets = manager.list_datasets()

            console.print("🧠 Dataset Management System Status", style="bold blue")
            console.print("=" * 40)

            # Summary metrics
            total_datasets = len(datasets)
            ready_datasets = sum(1 for ds in datasets if ds["status"] == "ready")
            total_rows = sum(ds["row_count"] for ds in datasets)

            console.print(f"📊 Total Datasets: {total_datasets}")
            console.print(f"✅ Ready for Training: {ready_datasets}")
            console.print(f"📈 Total Records: {total_rows:,}")

            # Status breakdown
            if datasets:
                status_counts = {}
                for ds in datasets:
                    status = ds["status"]
                    status_counts[status] = status_counts.get(status, 0) + 1

                console.print("\n📋 Status Breakdown:")
                for status, count in status_counts.items():
                    console.print(f"   {status}: {count}")

            # Storage info
            storage_path = manager.storage_path
            console.print(f"\n💾 Storage Location: {storage_path}")

            # Check if UI dependencies are available
            try:
                import plotly
                import streamlit

                console.print("🌐 UI Dependencies: ✅ Available")
            except ImportError:
                console.print(
                    "🌐 UI Dependencies: ❌ Missing (install streamlit and plotly)"
                )

    except Exception as e:
        console.print(f"❌ Failed to get status: {e}", style="red")


@dataset.command()
def sample() -> None:
    """Create a sample dataset for testing."""
    try:
        from .dataset_manager import create_sample_dataset

        console.print("🔬 Creating sample dataset...", style="blue")

        dataset_id = create_sample_dataset()

        console.print("✅ Sample dataset created successfully!", style="green")
        console.print(f"   Dataset ID: {dataset_id}")
        console.print("\n💡 Try these commands:")
        console.print(f"   ign data dataset info {dataset_id}")
        console.print(f"   ign data dataset process {dataset_id}")
        console.print("   ign data dataset buildout")

    except Exception as e:
        console.print(f"❌ Failed to create sample dataset: {e}", style="red")


# Additional helper commands for feature and source management
@dataset.group()
def source() -> None:
    """Manage dataset data sources."""
    pass


@source.command()
@click.argument("dataset_id")
@click.option(
    "--type",
    "source_type",
    required=True,
    type=click.Choice(["database", "file", "historian", "opc", "api"]),
    help="Type of data source",
)
@click.option("--config", help="JSON configuration for the source")
def add(dataset_id: str, source_type: str, config: str) -> None:
    """Add a data source to a dataset."""
    try:
        import json

        manager = DatasetManager()
        dataset = manager.get_dataset(dataset_id)

        if not dataset:
            console.print(f"❌ Dataset '{dataset_id}' not found", style="red")
            return

        # Parse configuration
        try:
            connection_config = json.loads(config) if config else {}
        except json.JSONDecodeError:
            console.print("❌ Invalid JSON configuration", style="red")
            return

        source_id = manager.add_data_source(
            dataset_id, source_type=source_type, connection_config=connection_config
        )

        console.print("✅ Data source added successfully!", style="green")
        console.print(f"   Source ID: {source_id}")
        console.print(f"   Type: {source_type}")

    except Exception as e:
        console.print(f"❌ Failed to add data source: {e}", style="red")


@dataset.group()
def feature() -> None:
    """Manage dataset features."""
    pass


@feature.command()
@click.argument("dataset_id")
@click.option("--name", required=True, help="Feature name")
@click.option(
    "--type",
    "data_type",
    required=True,
    type=click.Choice(["numeric", "categorical", "datetime", "text", "boolean"]),
    help="Data type",
)
@click.option("--source", "source_column", required=True, help="Source column name")
@click.option("--target", is_flag=True, help="Mark as target variable")
@click.option("--transform", help="Transformation to apply")
@click.option("--description", help="Feature description")
def add(
    dataset_id: str,
    name: str,
    data_type: str,
    source_column: str,
    target: bool,
    transform: str | None,
    description: str | None,
):
    """Add a feature to a dataset."""
    try:
        manager = DatasetManager()
        dataset = manager.get_dataset(dataset_id)

        if not dataset:
            console.print(f"❌ Dataset '{dataset_id}' not found", style="red")
            return

        manager.define_feature(
            dataset_id,
            name=name,
            data_type=data_type,
            source_column=source_column,
            is_target=target,
            transformation=transform,
            description=description,
        )

        console.print(f"✅ Feature '{name}' added successfully!", style="green")
        console.print(f"   Type: {data_type}")
        console.print(f"   Source: {source_column}")

        if target:
            console.print("   🎯 Marked as target variable")

        if transform:
            console.print(f"   Transform: {transform}")

    except Exception as e:
        console.print(f"❌ Failed to add feature: {e}", style="red")


# Export the main command group
__all__ = ["dataset"]
