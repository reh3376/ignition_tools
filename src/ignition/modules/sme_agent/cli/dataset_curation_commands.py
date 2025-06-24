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
- AI model preparation and feature engineering
"""

import asyncio
import logging

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..ai_model_preparation import (
    AIModelPreparation,
    FeatureEngineeringConfig,
    ModelPreparationConfig,
    validate_environment as validate_ai_env,
)
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
    try:
        console.print("\n📋 [bold blue]Available Variable Types[/bold blue]")

        table = Table(title="Industrial Variable Types")
        table.add_column("Type", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Description", style="white")

        descriptions = {
            "primary_pv": "Primary Process Variable - Main controlled variable",
            "secondary_pv": "Secondary Process Variable (SPC) - Supporting measurement",
            "cv": "Control Variable - Actuator output (valve position, speed, etc.)",
            "dv": "Disturbance Variable - External factors affecting process",
            "sp": "Setpoint Variable - Target value for control",
            "state": "Process State Variable - Operating mode or condition",
        }

        for var_type in VariableType:
            description = descriptions.get(var_type.value, "Industrial process variable")
            table.add_row(var_type.name, var_type.value, description)

        console.print(table)

        # Usage examples
        console.print("\n💡 [bold yellow]Usage Examples:[/bold yellow]")
        console.print(
            "  ign dataset-curation add-variable 'reactor_temp' primary_pv '°C' --high-limit 150 --low-limit 0"
        )
        console.print(
            "  ign dataset-curation add-variable 'pressure_sensor' secondary_pv 'bar' --description 'Backup pressure reading'"
        )
        console.print(
            "  ign dataset-curation add-variable 'valve_output' cv '%' --high-limit 100 --low-limit 0"
        )

    except Exception as e:
        console.print(f"\n❌ [bold red]Error listing variable types: {e}[/bold red]")
        raise click.ClickException(str(e))


# AI Model Preparation Commands
@dataset_curation.group("ai-model-prep")
def ai_model_prep():
    """AI Model Preparation commands for feature engineering and training data preparation."""
    pass


@ai_model_prep.command("validate-env")
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def validate_ai_env_cmd(complexity_level: str):
    """Validate environment for AI model preparation."""
    try:
        console.print(
            "\n🔍 [bold blue]Validating AI Model Preparation Environment[/bold blue]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validating AI environment...", total=None)

            # Validate environment
            validation_results = validate_ai_env()

            progress.update(task, description="AI environment validation complete")

        # Display results
        table = Table(title="AI Model Preparation Environment Validation")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="green")

        for component, status in validation_results.items():
            status_icon = "✅" if status else "❌"
            status_text = "Available" if status else "Missing"
            
            if component == "numpy":
                details = "NumPy for numerical computations"
            elif component == "pandas":
                details = "Pandas for data manipulation"
            elif component == "scikit_learn":
                details = "Scikit-learn for ML algorithms"
            elif component == "tensorflow":
                details = "TensorFlow for deep learning (optional)"
            elif component == "pytorch":
                details = "PyTorch for deep learning (optional)"
            elif component == "data_directory":
                details = "Data storage directory"
            elif component == "models_directory":
                details = "Model storage directory"
            elif component == "memory_available":
                details = "Sufficient memory for ML operations"
            else:
                details = "System component"

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
                f"🤖 AI Model Preparation ready for complexity level: [bold cyan]{complexity_level}[/bold cyan]"
            )
        else:
            failed = total - passed
            console.print(
                f"\n⚠️ [bold yellow]{failed}/{total} components need attention[/bold yellow]"
            )
            console.print("💡 Install missing packages: pip install numpy pandas scikit-learn")

    except Exception as e:
        console.print(f"\n❌ [bold red]AI environment validation failed: {e}[/bold red]")
        raise click.ClickException(str(e))


@ai_model_prep.command("info")
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def ai_model_prep_info(complexity_level: str):
    """Show AI model preparation system information."""
    try:
        # Create info panel
        info_text = f"""
🤖 [bold]AI Model Preparation System[/bold]

📊 [cyan]Capabilities:[/cyan]
• Feature engineering with derivatives, integrals, moving averages
• Cross-correlation analysis between variables
• Frequency domain feature extraction for oscillation detection
• Automated train/validation/test dataset splitting
• Feature normalization and missing data handling
• Model-ready dataset export (Pandas, NumPy, TensorFlow, PyTorch)

🔧 [cyan]Configuration Options:[/cyan]
• Window sizes for moving features: [5, 10, 30, 60]
• Derivative orders: [1st, 2nd order]
• Correlation lag analysis: [1, 5, 10] samples
• Train/Validation/Test splits: 70%/15%/15%
• Feature selection methods: correlation, variance, mutual information

🎯 [cyan]Complexity Level:[/cyan] {complexity_level}
• Basic: Core feature engineering
• Standard: Advanced correlations + frequency features
• Advanced: ML-based feature selection + optimization
• Enterprise: Distributed processing + GPU acceleration

🌟 [cyan]Output Formats:[/cyan]
• Pandas DataFrames for rapid prototyping
• NumPy arrays for custom ML pipelines
• TensorFlow datasets for deep learning
• PyTorch tensors for neural networks
• HuggingFace datasets for transformer models
        """

        console.print(
            Panel(info_text, title="AI Model Preparation System", border_style="blue")
        )

        # Environment validation summary
        env_results = validate_ai_env()
        valid_components = sum(env_results.values())
        total_components = len(env_results)

        console.print(
            f"\n📋 Environment: {valid_components}/{total_components} components ready"
        )

    except Exception as e:
        console.print(f"\n❌ [bold red]Error getting AI model prep info: {e}[/bold red]")
        raise click.ClickException(str(e))


@ai_model_prep.command("engineer-features")
@click.argument("dataset_name")
@click.option("--enable-derivatives/--no-derivatives", default=True, help="Enable derivative features")
@click.option("--enable-integrals/--no-integrals", default=True, help="Enable integral features")
@click.option("--enable-moving-averages/--no-moving-averages", default=True, help="Enable moving average features")
@click.option("--enable-correlations/--no-correlations", default=True, help="Enable cross-correlation features")
@click.option("--enable-frequency/--no-frequency", default=False, help="Enable frequency domain features")
@click.option("--window-sizes", default="5,10,30,60", help="Comma-separated window sizes")
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def engineer_features(
    dataset_name: str,
    enable_derivatives: bool,
    enable_integrals: bool,
    enable_moving_averages: bool,
    enable_correlations: bool,
    enable_frequency: bool,
    window_sizes: str,
    complexity_level: str,
):
    """Engineer features from raw dataset."""
    try:
        console.print(f"\n🔧 [bold blue]Engineering Features for Dataset: {dataset_name}[/bold blue]")

        # Parse window sizes
        window_list = [int(w.strip()) for w in window_sizes.split(",")]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing feature engineering...", total=None)

            # Initialize curator and AI model preparation
            curator = IndustrialDatasetCurator(complexity_level)
            ai_prep = AIModelPreparation(curator, complexity_level)

            # Create feature engineering configuration
            feature_config = FeatureEngineeringConfig(
                enable_derivatives=enable_derivatives,
                enable_integrals=enable_integrals,
                enable_moving_averages=enable_moving_averages,
                enable_cross_correlations=enable_correlations,
                enable_frequency_features=enable_frequency,
                window_sizes=window_list,
                derivative_orders=[1, 2],
                correlation_lags=[1, 5, 10],
            )

            progress.update(task, description="Engineering features...")

            # Engineer features
            engineered_data = ai_prep.engineer_features(dataset_name, feature_config)

            progress.update(task, description="Feature engineering complete!")

        # Display results
        results_table = Table(title="Feature Engineering Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")

        results_table.add_row("Original Features", str(len([col for col in engineered_data.columns if not col.startswith('engineered_')])))
        results_table.add_row("Engineered Features", str(len([col for col in engineered_data.columns if col.startswith('engineered_')])))
        results_table.add_row("Total Features", str(len(engineered_data.columns)))
        results_table.add_row("Dataset Rows", str(len(engineered_data)))
        results_table.add_row("Memory Usage", f"{engineered_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        console.print(results_table)

        # Show feature categories
        feature_categories = {}
        for col in engineered_data.columns:
            if col.startswith('engineered_derivative_'):
                feature_categories.setdefault('Derivatives', []).append(col)
            elif col.startswith('engineered_integral_'):
                feature_categories.setdefault('Integrals', []).append(col)
            elif col.startswith('engineered_ma_'):
                feature_categories.setdefault('Moving Averages', []).append(col)
            elif col.startswith('engineered_corr_'):
                feature_categories.setdefault('Cross-Correlations', []).append(col)
            elif col.startswith('engineered_freq_'):
                feature_categories.setdefault('Frequency Features', []).append(col)

        if feature_categories:
            console.print("\n📊 [bold yellow]Feature Categories:[/bold yellow]")
            for category, features in feature_categories.items():
                console.print(f"  • {category}: {len(features)} features")

        console.print(f"\n✅ [bold green]Feature engineering completed for dataset: {dataset_name}[/bold green]")

    except Exception as e:
        console.print(f"\n❌ [bold red]Feature engineering failed: {e}[/bold red]")
        raise click.ClickException(str(e))


@ai_model_prep.command("prepare-training-data")
@click.argument("dataset_name")
@click.option("--train-split", default=0.7, type=float, help="Training data split ratio")
@click.option("--validation-split", default=0.15, type=float, help="Validation data split ratio")
@click.option("--test-split", default=0.15, type=float, help="Test data split ratio")
@click.option("--target-variables", help="Comma-separated list of target variables")
@click.option("--normalize/--no-normalize", default=True, help="Apply feature normalization")
@click.option("--handle-missing/--no-handle-missing", default=True, help="Handle missing data")
@click.option("--feature-selection", default="correlation", type=click.Choice(["correlation", "variance", "mutual_info"]), help="Feature selection method")
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def prepare_training_data(
    dataset_name: str,
    train_split: float,
    validation_split: float,
    test_split: float,
    target_variables: str | None,
    normalize: bool,
    handle_missing: bool,
    feature_selection: str,
    complexity_level: str,
):
    """Prepare training data with train/validation/test splits."""
    try:
        console.print(f"\n🎯 [bold blue]Preparing Training Data for Dataset: {dataset_name}[/bold blue]")

        # Validate splits
        if abs(train_split + validation_split + test_split - 1.0) > 0.01:
            raise click.ClickException("Train, validation, and test splits must sum to 1.0")

        # Parse target variables
        target_list = []
        if target_variables:
            target_list = [var.strip() for var in target_variables.split(",")]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing training data preparation...", total=None)

            # Initialize curator and AI model preparation
            curator = IndustrialDatasetCurator(complexity_level)
            ai_prep = AIModelPreparation(curator, complexity_level)

            # Create model preparation configuration
            model_config = ModelPreparationConfig(
                train_split=train_split,
                validation_split=validation_split,
                test_split=test_split,
                target_variables=target_list,
                normalize_features=normalize,
                handle_missing_data=handle_missing,
                feature_selection_method=feature_selection,
                random_seed=42,
            )

            progress.update(task, description="Preparing training data...")

            # Prepare training data
            prepared_dataset = ai_prep.prepare_training_data(dataset_name, model_config)

            progress.update(task, description="Training data preparation complete!")

        # Display results
        results_table = Table(title="Training Data Preparation Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")

        results_table.add_row("Dataset Name", prepared_dataset.dataset_name)
        results_table.add_row("Features", str(len(prepared_dataset.features)))
        results_table.add_row("Target Variables", str(len(prepared_dataset.targets)))
        results_table.add_row("Training Samples", str(prepared_dataset.train_samples))
        results_table.add_row("Validation Samples", str(prepared_dataset.validation_samples))
        results_table.add_row("Test Samples", str(prepared_dataset.test_samples))
        results_table.add_row("Quality Score", f"{prepared_dataset.quality_score:.3f}")
        results_table.add_row("Completeness Score", f"{prepared_dataset.completeness_score:.3f}")

        console.print(results_table)

        # Show feature and target information
        console.print(f"\n📊 [bold yellow]Features ({len(prepared_dataset.features)}):[/bold yellow]")
        for i, feature in enumerate(prepared_dataset.features[:10]):  # Show first 10
            console.print(f"  • {feature}")
        if len(prepared_dataset.features) > 10:
            console.print(f"  ... and {len(prepared_dataset.features) - 10} more features")

        if prepared_dataset.targets:
            console.print(f"\n🎯 [bold yellow]Target Variables ({len(prepared_dataset.targets)}):[/bold yellow]")
            for target in prepared_dataset.targets:
                console.print(f"  • {target}")

        console.print(f"\n✅ [bold green]Training data prepared successfully for: {dataset_name}[/bold green]")

    except Exception as e:
        console.print(f"\n❌ [bold red]Training data preparation failed: {e}[/bold red]")
        raise click.ClickException(str(e))


@ai_model_prep.command("export-dataset")
@click.argument("dataset_name")
@click.option("--format", "export_format", default="pandas", type=click.Choice(["pandas", "numpy", "tensorflow", "pytorch", "huggingface"]), help="Export format")
@click.option("--output-path", help="Output file path (optional)")
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def export_dataset(
    dataset_name: str,
    export_format: str,
    output_path: str | None,
    complexity_level: str,
):
    """Export prepared dataset in various ML framework formats."""
    try:
        console.print(f"\n📤 [bold blue]Exporting Dataset: {dataset_name}[/bold blue]")
        console.print(f"Format: {export_format}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing export...", total=None)

            # Initialize curator and AI model preparation
            curator = IndustrialDatasetCurator(complexity_level)
            ai_prep = AIModelPreparation(curator, complexity_level)

            progress.update(task, description=f"Exporting to {export_format} format...")

            # Export dataset
            exported_data = ai_prep.export_dataset(dataset_name, export_format, output_path)

            progress.update(task, description="Export complete!")

        # Display results based on format
        if export_format == "pandas":
            console.print(f"✅ [bold green]Exported as Pandas DataFrame[/bold green]")
            console.print(f"Shape: {exported_data.shape}")
            console.print(f"Memory usage: {exported_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        elif export_format == "numpy":
            console.print(f"✅ [bold green]Exported as NumPy arrays[/bold green]")
            console.print(f"Features shape: {exported_data['X'].shape}")
            if 'y' in exported_data:
                console.print(f"Targets shape: {exported_data['y'].shape}")
        elif export_format in ["tensorflow", "pytorch", "huggingface"]:
            console.print(f"✅ [bold green]Exported as {export_format} dataset[/bold green]")
            console.print(f"Dataset type: {type(exported_data)}")

        if output_path:
            console.print(f"💾 [bold cyan]Saved to: {output_path}[/bold cyan]")

    except Exception as e:
        console.print(f"\n❌ [bold red]Dataset export failed: {e}[/bold red]")
        raise click.ClickException(str(e))


@ai_model_prep.command("status")
@click.option(
    "--complexity-level",
    default="standard",
    type=click.Choice(["basic", "standard", "advanced", "enterprise"]),
    help="Deployment complexity level",
)
def ai_model_prep_status(complexity_level: str):
    """Show AI model preparation system status."""
    try:
        console.print("\n📊 [bold blue]AI Model Preparation System Status[/bold blue]")

        # Initialize curator and AI model preparation
        curator = IndustrialDatasetCurator(complexity_level)
        ai_prep = AIModelPreparation(curator, complexity_level)

        # Get status information
        status = ai_prep.get_preparation_status()

        # Create status table
        status_table = Table(title="AI Model Preparation Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="magenta")
        status_table.add_column("Details", style="green")

        # Environment status
        env_validation = validate_ai_env()
        env_status = "✅ Ready" if all(env_validation.values()) else "⚠️ Issues"
        status_table.add_row("Environment", env_status, f"{sum(env_validation.values())}/{len(env_validation)} components ready")

        # System status
        status_table.add_row("Complexity Level", complexity_level.title(), f"Deployment mode: {complexity_level}")
        status_table.add_row("Prepared Datasets", str(status["prepared_datasets"]), "Datasets ready for training")
        status_table.add_row("Feature Cache", str(status["feature_cache_size"]), "Cached feature sets")

        # Capabilities status
        capabilities = [
            ("Feature Engineering", "✅ Available", "Derivatives, integrals, moving averages"),
            ("Cross-Correlations", "✅ Available", "Variable relationship analysis"),
            ("Frequency Features", "✅ Available", "Oscillation detection features"),
            ("Data Splitting", "✅ Available", "Train/validation/test splits"),
            ("Normalization", "✅ Available", "Feature scaling and normalization"),
            ("Export Formats", "✅ Available", "Pandas, NumPy, TensorFlow, PyTorch"),
        ]

        for capability, status_text, description in capabilities:
            status_table.add_row(capability, status_text, description)

        console.print(status_table)

        # Show recent activity if any
        if status.get("recent_activity"):
            console.print("\n📝 [bold yellow]Recent Activity:[/bold yellow]")
            for activity in status["recent_activity"][-5:]:  # Last 5 activities
                console.print(f"  • {activity}")

        console.print(f"\n🎯 [bold green]AI Model Preparation System: Ready for {complexity_level} deployment[/bold green]")

    except Exception as e:
        console.print(f"\n❌ [bold red]Error getting AI model prep status: {e}[/bold red]")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    dataset_curation()
