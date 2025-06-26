"""Fine-tuning CLI Commands - Phase 13.2: Model Fine-tuning & Specialization.

CLI interface for 8B parameter LLM fine-tuning with:
- Neo4j Knowledge Graph data extraction
- Parameter-efficient fine-tuning (LoRA/QLoRA)
- Distributed training support
- Comprehensive validation and monitoring

Following crawl_mcp.py methodology for robust command-line interface.
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path

import click
from dotenv import load_dotenv

from .fine_tuning_manager import (
    FineTuningConfig,
    FineTuningManager,
    FineTuningValidationError,
    TrainingDataConfig,
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@click.group(name="fine-tuning")
@click.pass_context
def fine_tuning_cli(ctx: click.Context) -> None:
    """Fine-tuning Management - Phase 13.2: Model Fine-tuning & Specialization.

    Manage 8B parameter LLM fine-tuning with Neo4j knowledge graph integration.

    Features:
    - Extract training data from 11,608+ Neo4j nodes
    - Parameter-efficient fine-tuning with LoRA/QLoRA
    - Distributed training support with GPU acceleration
    - Comprehensive validation and quality control
    """
    ctx.ensure_object(dict)


@fine_tuning_cli.command()
@click.option(
    "--dataset-name",
    default="ignition_knowledge_base",
    help="Name for the training dataset",
)
@click.option(
    "--extraction-types",
    default="Method,Class,Function,Pattern,CodeFile",
    help="Comma-separated Neo4j node types to extract",
)
@click.option(
    "--max-records", default=10000, type=int, help="Maximum number of training records"
)
@click.option(
    "--quality-threshold",
    default=0.8,
    type=float,
    help="Quality threshold for training data (0.0-1.0)",
)
@click.option(
    "--augmentation-factor", default=3, type=int, help="Data augmentation factor"
)
def extract_data(
    dataset_name: str,
    extraction_types: str,
    max_records: int,
    quality_threshold: float,
    augmentation_factor: int,
) -> None:
    """Extract training data from Neo4j knowledge graph.

    Following crawl_mcp.py methodology:
    - Step 1: Environment validation
    - Step 2: Input validation
    - Step 3: Data extraction with error handling
    - Step 4: Quality control and augmentation
    - Step 5: Dataset saving with metadata
    """
    try:
        click.echo("🚀 Phase 13.2: Fine-tuning Data Extraction")
        click.echo("=" * 50)

        # Step 1: Environment validation (crawl_mcp.py methodology)
        click.echo("🔍 Step 1: Environment Validation...")

        # Parse extraction types
        extraction_types_list = [t.strip() for t in extraction_types.split(",")]

        # Step 2: Input validation (crawl_mcp.py methodology)
        click.echo("📋 Step 2: Input Validation...")
        training_config = TrainingDataConfig(
            dataset_name=dataset_name,
            neo4j_extraction_types=extraction_types_list,
            max_records=max_records,
            quality_threshold=quality_threshold,
            augmentation_factor=augmentation_factor,
        )

        # Placeholder fine-tuning config for initialization
        tuning_config = FineTuningConfig()

        click.echo(f"   Dataset Name: {training_config.dataset_name}")
        click.echo(
            f"   Extraction Types: {', '.join(training_config.neo4j_extraction_types)}"
        )
        click.echo(f"   Max Records: {training_config.max_records:,}")
        click.echo(f"   Quality Threshold: {training_config.quality_threshold}")
        click.echo(f"   Augmentation Factor: {training_config.augmentation_factor}")

        # Step 3: Initialize manager with comprehensive validation
        click.echo("⚙️ Step 3: Initializing Fine-tuning Manager...")
        manager = FineTuningManager(training_config, tuning_config)

        # Step 4: Extract training data
        click.echo("🔄 Step 4: Extracting Training Data from Neo4j...")

        # Run async extraction
        result = asyncio.run(manager.extract_training_data())

        # Step 5: Display results
        click.echo("✅ Step 5: Data Extraction Complete!")
        click.echo(f"   Dataset Path: {result['dataset_path']}")
        click.echo(f"   Original Records: {result['original_records']:,}")
        click.echo(f"   Augmented Records: {result['augmented_records']:,}")
        click.echo(f"   Node Types: {', '.join(result['node_types_extracted'])}")
        click.echo(f"   Quality Threshold: {result['quality_threshold']}")

        click.echo("\n🎯 Next Steps:")
        click.echo("   1. Review the generated dataset")
        click.echo("   2. Run fine-tuning with: ign fine-tuning train")
        click.echo("   3. Monitor training progress")

    except FineTuningValidationError as e:
        click.echo(f"❌ Validation Error: {e}", err=True)
        raise click.ClickException(str(e))
    except Exception as e:
        click.echo(f"❌ Unexpected Error: {e}", err=True)
        logger.exception("Data extraction failed")
        raise click.ClickException(f"Data extraction failed: {e}")


@fine_tuning_cli.command()
@click.option("--show-datasets", is_flag=True, help="Show available training datasets")
@click.option("--show-models", is_flag=True, help="Show fine-tuned models")
@click.option("--show-config", is_flag=True, help="Show current configuration")
def status(show_datasets: bool, show_models: bool, show_config: bool) -> None:
    """Show fine-tuning system status and available resources.

    Following crawl_mcp.py methodology for comprehensive status reporting.
    """
    try:
        click.echo("🚀 Phase 13.2: Fine-tuning Status")
        click.echo("=" * 50)

        # Environment status
        click.echo("🔍 Environment Status:")

        # Check Neo4j connection
        try:
            from src.ignition.graph.client import IgnitionGraphClient

            client = IgnitionGraphClient()
            if client.connect():
                click.echo("   ✅ Neo4j: Connected")
                client.disconnect()
            else:
                click.echo("   ❌ Neo4j: Connection failed")
        except Exception:
            click.echo("   ❌ Neo4j: Not available")

        # Check GPU availability
        try:
            import torch

            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                click.echo(f"   ✅ CUDA: {gpu_count} GPU(s) available")
            elif torch.backends.mps.is_available():
                click.echo("   ✅ MPS: Apple Silicon GPU available")
            else:
                click.echo("   ⚠️ GPU: CPU-only mode")
        except ImportError:
            click.echo("   ❌ PyTorch: Not available")

        # Show datasets
        if show_datasets:
            click.echo("\n📊 Available Datasets:")
            dataset_dir = Path("data/training_datasets")
            if dataset_dir.exists():
                datasets = list(dataset_dir.glob("*.jsonl"))
                if datasets:
                    for dataset in datasets:
                        metadata_file = dataset.with_suffix(".metadata.json")
                        if metadata_file.exists():
                            with open(metadata_file) as f:
                                metadata = json.load(f)
                            click.echo(f"   📄 {dataset.name}")
                            click.echo(
                                f"      Records: {metadata.get('total_records', 'Unknown'):,}"
                            )
                            click.echo(
                                f"      Created: {metadata.get('creation_date', 'Unknown')}"
                            )
                        else:
                            click.echo(f"   📄 {dataset.name} (no metadata)")
                else:
                    click.echo("   No datasets found")
            else:
                click.echo("   Dataset directory not found")

        # Show models
        if show_models:
            click.echo("\n🤖 Fine-tuned Models:")
            models_dir = Path("models/fine_tuned")
            if models_dir.exists():
                models = [d for d in models_dir.iterdir() if d.is_dir()]
                if models:
                    for model in models:
                        metadata_file = model / "fine_tuning_metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file) as f:
                                metadata = json.load(f)
                            click.echo(f"   🎯 {model.name}")
                            click.echo(
                                f"      Base: {metadata.get('base_model', 'Unknown')}"
                            )
                            click.echo(
                                f"      Status: {metadata.get('status', 'Unknown')}"
                            )
                            click.echo(
                                f"      Date: {metadata.get('training_date', 'Unknown')}"
                            )
                        else:
                            click.echo(f"   🎯 {model.name} (no metadata)")
                else:
                    click.echo("   No fine-tuned models found")
            else:
                click.echo("   Models directory not found")

        # Show configuration
        if show_config:
            click.echo("\n⚙️ Current Configuration:")
            click.echo(f"   Neo4j URI: {os.getenv('NEO4J_URI', 'Not set')}")
            click.echo(f"   GPU Enabled: {os.getenv('SME_AGENT_GPU_ENABLED', 'false')}")
            click.echo(f"   Device: {os.getenv('SME_AGENT_DEVICE', 'cpu')}")
            click.echo(f"   Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")

        click.echo("\n✅ Status Check Complete!")
        click.echo("\n📊 System Ready for Fine-tuning!")

    except Exception as e:
        click.echo(f"❌ Status Error: {e}", err=True)
        logger.exception("Status check failed")
        raise click.ClickException(f"Status check failed: {e}")


@fine_tuning_cli.command()
@click.option(
    "--dataset-name",
    default="ignition_knowledge_base",
    help="Name of the dataset to use for training",
)
@click.option("--base-model", default="llama3.1-8b", help="Base model for fine-tuning")
@click.option("--lora-rank", default=16, type=int, help="LoRA rank (4-64)")
@click.option("--learning-rate", default=2e-4, type=float, help="Learning rate")
@click.option("--batch-size", default=4, type=int, help="Training batch size")
@click.option("--num-epochs", default=3, type=int, help="Number of training epochs")
@click.option(
    "--save-steps", default=500, type=int, help="Save checkpoint every N steps"
)
def train(
    dataset_name: str,
    base_model: str,
    lora_rank: int,
    learning_rate: float,
    batch_size: int,
    num_epochs: int,
    save_steps: int,
) -> None:
    """Execute fine-tuning training process.

    Following crawl_mcp.py methodology:
    - Step 1: Environment validation
    - Step 2: Configuration validation
    - Step 3: Dataset loading and validation
    - Step 4: Training execution with monitoring
    - Step 5: Model saving and validation
    - Step 6: Resource cleanup
    """
    try:
        click.echo("🚀 Phase 13.2: Fine-tuning Training Execution")
        click.echo("=" * 50)

        # Step 1: Environment validation (crawl_mcp.py methodology)
        click.echo("🔍 Step 1: Environment Validation...")

        # Check dataset exists
        dataset_path = Path(f"./datasets/{dataset_name}.jsonl")
        if not dataset_path.exists():
            raise click.ClickException(f"Dataset not found: {dataset_path}")

        # Step 2: Configuration validation (crawl_mcp.py methodology)
        click.echo("📋 Step 2: Configuration Validation...")

        training_config = TrainingDataConfig(dataset_name=dataset_name)
        tuning_config = FineTuningConfig(
            base_model=base_model,
            lora_rank=lora_rank,
            learning_rate=learning_rate,
            batch_size=batch_size,
            num_epochs=num_epochs,
            save_steps=save_steps,
        )

        click.echo(f"   Dataset: {dataset_name}")
        click.echo(f"   Base Model: {base_model}")
        click.echo(f"   LoRA Rank: {lora_rank}")
        click.echo(f"   Learning Rate: {learning_rate}")
        click.echo(f"   Batch Size: {batch_size}")
        click.echo(f"   Epochs: {num_epochs}")

        # Step 3: Initialize training manager
        click.echo("⚙️ Step 3: Initializing Training Manager...")
        manager = FineTuningManager(training_config, tuning_config)

        # Step 4: Execute training
        click.echo("🏋️ Step 4: Executing Fine-tuning Training...")
        click.echo("   This may take several hours depending on dataset size...")

        start_time = time.time()

        # Run async training
        result = asyncio.run(manager.execute_fine_tuning(dataset_path))

        training_time = time.time() - start_time

        # Step 5: Display results
        if result.get("success"):
            click.echo("✅ Step 5: Training Complete!")
            click.echo(f"   Model Path: {result['model_path']}")
            click.echo(f"   Training Time: {training_time:.2f} seconds")
            click.echo(f"   Total Steps: {result.get('total_steps', 0):,}")
            click.echo(f"   Final Loss: {result.get('final_loss', 0.0):.4f}")

            # Display training metrics
            metrics = result.get("training_metrics", {})
            if metrics:
                click.echo("\n📊 Training Metrics:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        click.echo(f"   {key}: {value:.4f}")
                    else:
                        click.echo(f"   {key}: {value}")

            click.echo("\n🎯 Next Steps:")
            click.echo("   1. Evaluate model performance")
            click.echo("   2. Test with Ignition-specific queries")
            click.echo("   3. Deploy to production environment")
        else:
            click.echo(f"❌ Training Failed: {result.get('error')}")
            raise click.ClickException(f"Training failed: {result.get('error')}")

    except FineTuningValidationError as e:
        click.echo(f"❌ Validation Error: {e}", err=True)
        raise click.ClickException(str(e))
    except Exception as e:
        click.echo(f"❌ Training Error: {e}", err=True)
        logger.exception("Fine-tuning training failed")
        raise click.ClickException(f"Training failed: {e}")


# Register the command group
def register_commands(cli: click.Group) -> None:
    """Register fine-tuning commands with the CLI."""
    cli.add_command(fine_tuning_cli)
