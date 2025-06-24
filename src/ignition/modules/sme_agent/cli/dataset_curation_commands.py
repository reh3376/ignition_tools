"""CLI Commands for Industrial Dataset Curation & AI Model Preparation

Following the crawl_mcp.py methodology for structured development:
- Comprehensive validation and error handling
- Environment variable configuration
- Modular testing and progressive complexity
- Resource management and cleanup
- User-friendly error messages

This module provides CLI commands for Phase 11.5:
- Dataset ingestion and validation
- Variable type classification
- Control system metadata management
- Data quality assessment
"""

import asyncio
import logging

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..data_ingestion_framework import DataIngestionFramework
from ..industrial_dataset_curation import (
    DataSourceType,
    IndustrialDatasetCurator,
    VariableMetadata,
    VariableType,
    validate_environment,
)
from ..variable_type_classifier import VariableTypeClassifier

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for better CLI output
console = Console()


@click.group()
def dataset_curation():
    """Industrial Dataset Curation & AI Model Preparation commands."""
    pass


@dataset_curation.command()
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def validate_env(complexity_level: str):
    """Validate environment for dataset curation system."""
    try:
        console.print(
            "\n🔍 [bold blue]Validating Dataset Curation Environment[/bold blue]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validating environment...", total=None)

            # Validate environment
            validation_results = validate_environment()

            progress.update(task, description="Environment validation complete")

        # Display results
        table = Table(title="Environment Validation Results")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="green")

        for component, status in validation_results.items():
            status_icon = "✅" if status else "❌"
            status_text = "Valid" if status else "Invalid"
            details = "Ready for use" if status else "Requires configuration"

            table.add_row(
                component.replace("_", " ").title(),
                f"{status_icon} {status_text}",
                details,
            )

        console.print(table)

        # Summary
        passed = sum(validation_results.values())
        total = len(validation_results)

        if passed == total:
            console.print(
                f"\n✅ [bold green]All {total} components validated successfully![/bold green]"
            )
            console.print(
                f"📊 Complexity level: [bold cyan]{complexity_level}[/bold cyan]"
            )
        else:
            failed = total - passed
            console.print(
                f"\n⚠️ [bold yellow]{failed}/{total} components need attention[/bold yellow]"
            )
            console.print("💡 Check environment variables and dependencies")

    except Exception as e:
        console.print(f"\n❌ [bold red]Validation failed: {e}[/bold red]")
        raise click.ClickException(str(e))


@dataset_curation.command()
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def info(complexity_level: str):
    """Show dataset curation system information."""
    try:
        # Initialize curator to get status
        curator = IndustrialDatasetCurator(complexity_level)
        status = curator.get_validation_status()

        # Create info panel
        info_text = f"""
🎯 [bold]Phase 11.5: Industrial Dataset Curation & AI Model Preparation[/bold]

📊 [cyan]System Status:[/cyan]
• Complexity Level: {status["complexity_level"]}
• Variables Configured: {status["variables_configured"]}
• Controllers Configured: {status["controllers_configured"]}
• Datasets Loaded: {status["datasets_loaded"]}

🔧 [cyan]Capabilities:[/cyan]
• Multi-format data ingestion (CSV/XLS, OPC-UA, Database historians)
• Automated variable type classification (PV, CV, DV, SP, State)
• Control system metadata management
• Data quality assessment and validation
• Feature engineering and dataset augmentation

🌟 [cyan]Features:[/cyan]
• Comprehensive validation following crawl_mcp.py methodology
• Environment-based configuration
• Progressive complexity deployment
• Real-time data streaming support
• Automated quality scoring
        """

        console.print(
            Panel(info_text, title="Dataset Curation System", border_style="blue")
        )

        # Environment validation summary
        env_results = validate_environment()
        valid_components = sum(env_results.values())
        total_components = len(env_results)

        console.print(
            f"\n📋 Environment: {valid_components}/{total_components} components ready"
        )

    except Exception as e:
        console.print(f"\n❌ [bold red]Error getting system info: {e}[/bold red]")
        raise click.ClickException(str(e))


@dataset_curation.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--timestamp-column", default="timestamp", help="Name of timestamp column"
)
@click.option("--dataset-name", help="Custom name for dataset (defaults to filename)")
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def ingest_csv(
    file_path: str,
    timestamp_column: str,
    dataset_name: str | None,
    complexity_level: str,
):
    """Ingest CSV/XLS data with validation and quality assessment."""
    try:
        console.print(f"\n📊 [bold blue]Ingesting Data from {file_path}[/bold blue]")

        # Initialize components
        curator = IndustrialDatasetCurator(complexity_level)
        ingestion_framework = DataIngestionFramework(curator)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Ingesting data...", total=None)

            # Ingest data
            result = asyncio.run(
                ingestion_framework.ingest_csv_data(
                    file_path=file_path, timestamp_column=timestamp_column
                )
            )

            progress.update(task, description="Data ingestion complete")

        if result["success"]:
            console.print("\n✅ [bold green]Successfully ingested data![/bold green]")

            # Display ingestion results
            table = Table(title="Ingestion Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Dataset Name", result["dataset_name"])
            table.add_row("Rows Processed", str(result["rows_processed"]))
            table.add_row("Columns Processed", str(result["columns_processed"]))
            table.add_row(
                "Quality Score", f"{result['quality_report']['quality_score']:.1f}/100"
            )
            table.add_row(
                "Time Range",
                f"{result['timestamp_range']['start']} to {result['timestamp_range']['end']}",
            )

            console.print(table)

            # Quality report summary
            quality_report = result["quality_report"]
            if quality_report["quality_score"] >= 80:
                console.print(
                    "\n🌟 [bold green]High quality dataset - ready for analysis![/bold green]"
                )
            elif quality_report["quality_score"] >= 60:
                console.print(
                    "\n⚠️ [bold yellow]Moderate quality dataset - review recommended[/bold yellow]"
                )
            else:
                console.print(
                    "\n❌ [bold red]Low quality dataset - data cleaning required[/bold red]"
                )
        else:
            console.print(
                f"\n❌ [bold red]Ingestion failed: {result['error']}[/bold red]"
            )
            raise click.ClickException(result["error"])

    except Exception as e:
        console.print(f"\n❌ [bold red]Error ingesting data: {e}[/bold red]")
        raise click.ClickException(str(e))


@dataset_curation.command()
@click.argument("dataset_name")
@click.option(
    "--confidence-threshold",
    default=0.7,
    type=float,
    help="Minimum confidence for auto-classification",
)
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def classify_variables(
    dataset_name: str, confidence_threshold: float, complexity_level: str
):
    """Automatically classify variables in a dataset."""
    try:
        console.print(
            f"\n🔍 [bold blue]Classifying Variables in {dataset_name}[/bold blue]"
        )

        # Initialize components
        curator = IndustrialDatasetCurator(complexity_level)
        classifier = VariableTypeClassifier(curator)

        # Load existing datasets if any
        # Note: In a real implementation, you'd load from persistent storage

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Classifying variables...", total=None)

            # Classify variables
            result = classifier.classify_variables_from_dataset(
                dataset_name=dataset_name, confidence_threshold=confidence_threshold
            )

            progress.update(task, description="Variable classification complete")

        if result["success"]:
            console.print("\n✅ [bold green]Classification complete![/bold green]")

            # Display classification results
            table = Table(title="Classification Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Total Variables", str(result["total_variables"]))
            table.add_row("Classified Variables", str(result["classified_variables"]))
            table.add_row(
                "Classification Rate",
                f"{(result['classified_variables'] / result['total_variables'] * 100):.1f}%",
            )
            table.add_row("Confidence Threshold", f"{confidence_threshold:.1f}")

            console.print(table)

            # Variable type distribution
            type_counts = {}
            for var_result in result["classification_results"].values():
                if var_result["confidence"] >= confidence_threshold:
                    var_type = var_result["variable_type"].value
                    type_counts[var_type] = type_counts.get(var_type, 0) + 1

            if type_counts:
                console.print("\n📊 [bold cyan]Variable Type Distribution:[/bold cyan]")
                for var_type, count in type_counts.items():
                    console.print(f"  • {var_type.replace('_', ' ').title()}: {count}")
        else:
            console.print(
                f"\n❌ [bold red]Classification failed: {result['error']}[/bold red]"
            )
            raise click.ClickException(result["error"])

    except Exception as e:
        console.print(f"\n❌ [bold red]Error classifying variables: {e}[/bold red]")
        raise click.ClickException(str(e))


@dataset_curation.command()
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def status(complexity_level: str):
    """Show current status of dataset curation system."""
    try:
        console.print("\n📊 [bold blue]Dataset Curation System Status[/bold blue]")

        # Initialize components
        curator = IndustrialDatasetCurator(complexity_level)
        classifier = VariableTypeClassifier(curator)

        # Get status information
        curator_status = curator.get_validation_status()
        classification_summary = classifier.get_classification_summary()

        # System status table
        status_table = Table(title="System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="magenta")
        status_table.add_column("Details", style="green")

        # Environment validation
        env_results = validate_environment()
        valid_env = sum(env_results.values())
        total_env = len(env_results)
        env_status = (
            "✅ Ready"
            if valid_env == total_env
            else f"⚠️ {total_env - valid_env} issues"
        )

        status_table.add_row(
            "Environment", env_status, f"{valid_env}/{total_env} components valid"
        )
        status_table.add_row(
            "Complexity Level", f"📊 {complexity_level}", "Deployment configuration"
        )
        status_table.add_row(
            "Variables",
            f"🔧 {curator_status['variables_configured']}",
            "Configured variables",
        )
        status_table.add_row(
            "Controllers",
            f"⚙️ {curator_status['controllers_configured']}",
            "Configured controllers",
        )
        status_table.add_row(
            "Datasets", f"💾 {curator_status['datasets_loaded']}", "Loaded datasets"
        )

        console.print(status_table)

        # Classification summary
        if not classification_summary.get("error"):
            console.print("\n📈 [bold cyan]Classification Summary:[/bold cyan]")
            console.print(
                f"  • Datasets Processed: {classification_summary['total_datasets_processed']}"
            )
            console.print(
                f"  • Variables Analyzed: {classification_summary['total_variables_analyzed']}"
            )
            console.print(
                f"  • Variables Classified: {classification_summary['total_variables_classified']}"
            )

            if classification_summary["total_variables_analyzed"] > 0:
                rate = classification_summary["classification_rate"]
                console.print(f"  • Classification Rate: {rate:.1f}%")

            # Variable type distribution
            if classification_summary.get("variable_type_distribution"):
                console.print("\n🏷️ [bold cyan]Variable Types:[/bold cyan]")
                for var_type, count in classification_summary[
                    "variable_type_distribution"
                ].items():
                    console.print(f"  • {var_type.replace('_', ' ').title()}: {count}")

        console.print(f"\n⏰ Last updated: {curator_status['timestamp']}")

    except Exception as e:
        console.print(f"\n❌ [bold red]Error getting status: {e}[/bold red]")
        raise click.ClickException(str(e))


@dataset_curation.command()
@click.argument("variable_name")
@click.argument("variable_type", type=click.Choice([vt.value for vt in VariableType]))
@click.argument("engineering_units")
@click.option("--high-limit", type=float, help="High operational limit")
@click.option("--low-limit", type=float, help="Low operational limit")
@click.option("--description", help="Variable description")
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def add_variable(
    variable_name: str,
    variable_type: str,
    engineering_units: str,
    high_limit: float | None,
    low_limit: float | None,
    description: str | None,
    complexity_level: str,
):
    """Add a variable with metadata to the curation system."""
    try:
        console.print(f"\n➕ [bold blue]Adding Variable: {variable_name}[/bold blue]")

        # Initialize curator
        curator = IndustrialDatasetCurator(complexity_level)

        # Create variable metadata
        var_type_enum = VariableType(variable_type)
        metadata = VariableMetadata(
            name=variable_name,
            variable_type=var_type_enum,
            engineering_units=engineering_units,
            high_limit=high_limit,
            low_limit=low_limit,
            description=description or f"Manually added {var_type_enum.value}",
            data_source=DataSourceType.MANUAL_INPUT,
        )

        # Add variable
        success = curator.add_variable(metadata)

        if success:
            console.print(
                f"✅ [bold green]Successfully added variable '{variable_name}'[/bold green]"
            )

            # Display variable details
            details_table = Table(title="Variable Details")
            details_table.add_column("Property", style="cyan")
            details_table.add_column("Value", style="magenta")

            details_table.add_row("Name", variable_name)
            details_table.add_row("Type", var_type_enum.value.replace("_", " ").title())
            details_table.add_row("Engineering Units", engineering_units)

            if high_limit is not None:
                details_table.add_row("High Limit", str(high_limit))
            if low_limit is not None:
                details_table.add_row("Low Limit", str(low_limit))
            if description:
                details_table.add_row("Description", description)

            console.print(details_table)
        else:
            console.print(
                f"❌ [bold red]Failed to add variable '{variable_name}'[/bold red]"
            )
            raise click.ClickException("Variable addition failed")

    except Exception as e:
        console.print(f"\n❌ [bold red]Error adding variable: {e}[/bold red]")
        raise click.ClickException(str(e))


@dataset_curation.command()
def list_variable_types():
    """List available variable types for classification."""
    console.print("\n🏷️ [bold blue]Available Variable Types[/bold blue]")

    type_table = Table(title="Variable Type Classifications")
    type_table.add_column("Type", style="cyan")
    type_table.add_column("Code", style="magenta")
    type_table.add_column("Description", style="green")

    descriptions = {
        VariableType.PRIMARY_PV: "Primary process variables (temperature, pressure, flow, level)",
        VariableType.SECONDARY_PV: "Secondary/calculated process variables (SPC variables)",
        VariableType.CONTROL_VARIABLE: "Control outputs (valve positions, actuator signals)",
        VariableType.DISTURBANCE_VARIABLE: "Disturbance inputs (ambient conditions, feed variations)",
        VariableType.SETPOINT: "Setpoint variables (target values, references)",
        VariableType.PROCESS_STATE: "Process state variables (modes, status indicators)",
    }

    for var_type in VariableType:
        type_table.add_row(
            var_type.value.replace("_", " ").title(),
            var_type.value,
            descriptions.get(var_type, "Process variable"),
        )

    console.print(type_table)

    console.print("\n💡 [bold cyan]Usage Examples:[/bold cyan]")
    console.print(
        "  ign dataset-curation add-variable 'reactor_temp' primary_pv '°C' --high-limit 150 --low-limit 0"
    )
    console.print(
        "  ign dataset-curation add-variable 'valve_output' cv '%' --high-limit 100 --low-limit 0"
    )


if __name__ == "__main__":
    dataset_curation()
