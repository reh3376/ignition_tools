"""LLM Infrastructure CLI Commands - Phase 13.1: Auto-Detecting GPU Support.

CLI interface for 8B parameter LLM deployment with auto-detection for:
- NVIDIA CUDA GPU acceleration
- Apple Silicon MPS acceleration
- CPU-only fallback with optimizations

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

from . import auto_detect_gpu_configuration
from .infrastructure_manager import InfrastructureManager, ModelConfig

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@click.group(name="llm-infrastructure")
@click.pass_context
def llm_infrastructure_cli(ctx):
    """LLM Infrastructure Management - Phase 13.1: Auto-Detecting GPU Support.

    Manage 8B parameter LLM deployment with automatic GPU detection and optimization.

    Features:
    - Auto-detection of NVIDIA CUDA and Apple Silicon MPS
    - Intelligent fallback to optimized CPU-only mode
    - Production-ready deployment with comprehensive monitoring
    - Integration with Neo4j knowledge graph
    """
    ctx.ensure_object(dict)


@llm_infrastructure_cli.command()
@click.option("--detailed", is_flag=True, help="Show detailed GPU information")
def detect_gpu(detailed: bool):
    """Step 1: Auto-detect available GPU acceleration (crawl_mcp.py methodology).

    Automatically detects and reports optimal GPU configuration:
    - NVIDIA CUDA (Linux/Windows)
    - Apple Silicon MPS (macOS)
    - CPU optimizations (all platforms)
    """
    click.echo("🎯 LLM Infrastructure - GPU Auto-Detection")
    click.echo("📋 Following crawl_mcp.py methodology - Environment Validation")

    try:
        # Step 1: Environment validation with auto-detection
        gpu_config = auto_detect_gpu_configuration()

        # Display results
        click.echo(f"\n🔍 Platform: {gpu_config['platform']} ({gpu_config['architecture']})")

        if gpu_config["gpu_type"] == "mps":
            click.echo("✅ Apple Silicon MPS GPU acceleration detected")
            click.echo(f"   Device: {gpu_config['device']}")
            click.echo(f"   Memory: {gpu_config['available_memory_gb']:.1f} GB")
            click.echo(f"   Precision: {gpu_config['precision']}")
            click.echo(f"   Quantization: {gpu_config['quantization']}")

        elif gpu_config["gpu_type"] == "cuda":
            click.echo("✅ NVIDIA CUDA GPU acceleration detected")
            click.echo(f"   Device: {gpu_config['device']}")
            click.echo(f"   Memory: {gpu_config['available_memory_gb']:.1f} GB")
            click.echo(f"   Precision: {gpu_config['precision']}")
            click.echo(f"   Quantization: {gpu_config['quantization']}")

        else:
            click.echo("ℹ️ CPU-only configuration (no GPU acceleration)")
            click.echo(f"   Workers: {gpu_config['workers']}")
            click.echo(f"   Quantization: {gpu_config['quantization']}")

        click.echo("\n⚙️ Optimal Configuration:")
        click.echo(f"   Batch Size: {gpu_config['batch_size']}")
        click.echo(f"   Max Context: {gpu_config['max_context']}")
        click.echo(f"   Memory Optimized: {gpu_config['memory_optimized']}")

        if gpu_config["warnings"]:
            click.echo("\n⚠️ Warnings:")
            for warning in gpu_config["warnings"]:
                click.echo(f"   - {warning}")

        if detailed:
            click.echo("\n📊 Detailed Configuration:")
            click.echo(json.dumps(gpu_config, indent=2))

    except Exception as e:
        click.echo(f"❌ GPU detection failed: {e}")
        raise click.ClickException(f"GPU detection error: {e}")


@llm_infrastructure_cli.command()
@click.option("--model-name", default="llama3.1-8b", help="8B parameter model name")
@click.option(
    "--quantization",
    type=click.Choice(["fp32", "fp16", "int8", "int4"]),
    help="Override quantization",
)
@click.option("--max-context", type=int, help="Override max context length")
@click.option("--test-prompt", default="Hello, this is a test.", help="Test prompt for validation")
def initialize(model_name: str, quantization: str | None, max_context: int | None, test_prompt: str):
    """Step 2: Initialize LLM Infrastructure with validation (crawl_mcp.py methodology).

    Initialize 8B parameter LLM with auto-detected GPU configuration and comprehensive testing.
    """
    click.echo("🚀 LLM Infrastructure - Initialization")
    click.echo("📋 Following crawl_mcp.py methodology - Progressive Complexity")

    try:
        # Step 2: Input validation using Pydantic
        config_dict = {"model_name": model_name}
        if quantization:
            config_dict["quantization"] = quantization
        if max_context:
            config_dict["max_context_length"] = max_context

        config = ModelConfig(**config_dict)

        # Step 3: Comprehensive error handling
        async def run_initialization():
            manager = InfrastructureManager(config)

            click.echo("\n🔍 Step 1: Environment validation...")
            result = await manager.initialize()

            if result["success"]:
                click.echo("✅ LLM Infrastructure initialized successfully")
                click.echo(f"   GPU Type: {result['gpu_config']['gpu_type']}")
                click.echo(f"   Device: {result['gpu_config']['device']}")
                click.echo(f"   Initialization Time: {result['initialization_time']:.2f}s")
                click.echo(f"   Memory Usage: {result['memory_usage']:.2f} GB")

                # Step 4: Modular testing
                click.echo("\n🧪 Step 2: Testing model functionality...")
                test_result = await manager.generate_text(test_prompt, max_tokens=50)

                if test_result["success"]:
                    click.echo("✅ Model functionality test passed")
                    click.echo(f"   Prompt: {test_result['prompt']}")
                    click.echo(f"   Generated: {test_result['generated_text'][:100]}...")
                    click.echo(f"   Inference Time: {test_result['inference_time']:.2f}s")
                    click.echo(f"   Tokens/Second: {test_result['tokens_per_second']:.1f}")
                else:
                    click.echo(f"❌ Model functionality test failed: {test_result['error']}")

                # Step 6: Resource cleanup
                await manager._cleanup_resources()

            else:
                click.echo(f"❌ Initialization failed: {result['error']}")

        # Run async initialization
        asyncio.run(run_initialization())

    except Exception as e:
        click.echo(f"❌ Initialization failed: {e}")
        raise click.ClickException(f"Initialization error: {e}")


@llm_infrastructure_cli.command()
@click.option("--prompt", required=True, help="Text prompt for generation")
@click.option("--max-tokens", type=int, default=512, help="Maximum tokens to generate")
@click.option("--temperature", type=float, default=0.7, help="Generation temperature")
@click.option("--top-p", type=float, default=0.9, help="Top-p sampling parameter")
@click.option("--output-file", type=click.Path(), help="Save output to file")
def generate(
    prompt: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    output_file: str | None,
):
    """Step 5: Generate text with auto-detected GPU optimization (crawl_mcp.py methodology).

    Generate text using 8B parameter LLM with optimal GPU acceleration.
    """
    click.echo("🎯 LLM Infrastructure - Text Generation")
    click.echo("📋 Following crawl_mcp.py methodology - Production Deployment")

    try:

        async def run_generation():
            # Initialize infrastructure
            manager = InfrastructureManager()

            async with manager.managed_inference() as context:
                click.echo(f"\n🔍 Using {context['gpu_config']['gpu_type']} acceleration")

                # Generate text
                result = await manager.generate_text(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                )

                if result["success"]:
                    click.echo("✅ Text generation completed")
                    click.echo(f"\n📝 Prompt: {result['prompt']}")
                    click.echo(f"🤖 Generated Text:\n{result['generated_text']}")
                    click.echo("\n📊 Performance:")
                    click.echo(f"   Inference Time: {result['inference_time']:.2f}s")
                    click.echo(f"   Tokens Generated: {result['tokens_generated']}")
                    click.echo(f"   Tokens/Second: {result['tokens_per_second']:.1f}")

                    # Save to file if requested
                    if output_file:
                        output_data = {
                            "prompt": result["prompt"],
                            "generated_text": result["generated_text"],
                            "metadata": {
                                "inference_time": result["inference_time"],
                                "tokens_generated": result["tokens_generated"],
                                "tokens_per_second": result["tokens_per_second"],
                                "gpu_config": context["gpu_config"],
                                "timestamp": time.time(),
                            },
                        }

                        Path(output_file).write_text(json.dumps(output_data, indent=2))
                        click.echo(f"💾 Output saved to: {output_file}")

                else:
                    click.echo(f"❌ Text generation failed: {result['error']}")

        # Run async generation
        asyncio.run(run_generation())

    except Exception as e:
        click.echo(f"❌ Generation failed: {e}")
        raise click.ClickException(f"Generation error: {e}")


@llm_infrastructure_cli.command()
@click.option("--duration", type=int, default=60, help="Benchmark duration in seconds")
@click.option("--concurrent-requests", type=int, default=1, help="Number of concurrent requests")
def benchmark(duration: int, concurrent_requests: int):
    """Step 4: Benchmark LLM performance with auto-detected configuration (crawl_mcp.py methodology).

    Run comprehensive performance benchmarks to validate deployment readiness.
    """
    click.echo("📊 LLM Infrastructure - Performance Benchmark")
    click.echo("📋 Following crawl_mcp.py methodology - Modular Testing")

    try:

        async def run_benchmark():
            manager = InfrastructureManager()

            # Initialize
            init_result = await manager.initialize()
            if not init_result["success"]:
                click.echo(f"❌ Initialization failed: {init_result['error']}")
                return

            click.echo(f"✅ Benchmark starting with {init_result['gpu_config']['gpu_type']} acceleration")

            # Benchmark metrics
            total_requests = 0
            total_tokens = 0
            total_time = 0.0
            errors = 0

            test_prompts = [
                "Explain the concept of machine learning in simple terms.",
                "Write a short story about a robot learning to paint.",
                "Describe the benefits of renewable energy sources.",
                "What are the key principles of good software design?",
                "How does photosynthesis work in plants?",
            ]

            start_time = time.time()

            while time.time() - start_time < duration:
                # Run concurrent requests
                tasks = []
                for _i in range(concurrent_requests):
                    prompt = test_prompts[total_requests % len(test_prompts)]
                    task = manager.generate_text(prompt, max_tokens=100)
                    tasks.append(task)

                # Execute concurrent requests
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in results:
                    total_requests += 1
                    if isinstance(result, Exception):
                        errors += 1
                    elif result.get("success"):
                        total_tokens += result.get("tokens_generated", 0)
                        total_time += result.get("inference_time", 0)
                    else:
                        errors += 1

                # Progress update
                elapsed = time.time() - start_time
                if total_requests % 10 == 0:
                    click.echo(f"   Progress: {elapsed:.1f}s / {duration}s - {total_requests} requests")

            # Calculate final metrics
            elapsed_total = time.time() - start_time
            avg_inference_time = total_time / max(total_requests - errors, 1)
            tokens_per_second = total_tokens / total_time if total_time > 0 else 0
            requests_per_second = total_requests / elapsed_total
            error_rate = errors / total_requests * 100 if total_requests > 0 else 0

            # Display results
            click.echo("\n📊 Benchmark Results:")
            click.echo(f"   Duration: {elapsed_total:.1f}s")
            click.echo(f"   Total Requests: {total_requests}")
            click.echo(f"   Successful Requests: {total_requests - errors}")
            click.echo(f"   Error Rate: {error_rate:.1f}%")
            click.echo(f"   Requests/Second: {requests_per_second:.2f}")
            click.echo(f"   Average Inference Time: {avg_inference_time:.2f}s")
            click.echo(f"   Total Tokens Generated: {total_tokens}")
            click.echo(f"   Tokens/Second: {tokens_per_second:.1f}")
            click.echo(f"   GPU Type: {init_result['gpu_config']['gpu_type']}")

            # Cleanup
            await manager._cleanup_resources()

        # Run async benchmark
        asyncio.run(run_benchmark())

    except Exception as e:
        click.echo(f"❌ Benchmark failed: {e}")
        raise click.ClickException(f"Benchmark error: {e}")


@llm_infrastructure_cli.command()
def status():
    """Get current LLM Infrastructure status and configuration."""
    click.echo("📋 LLM Infrastructure - Status Report")

    try:
        # Get GPU configuration
        gpu_config = auto_detect_gpu_configuration()

        click.echo("\n🔍 System Information:")
        click.echo(f"   Platform: {gpu_config['platform']} ({gpu_config['architecture']})")
        click.echo(f"   GPU Type: {gpu_config['gpu_type']}")
        click.echo(f"   Device: {gpu_config['device']}")

        if gpu_config["gpu_type"] != "none":
            click.echo(f"   Available Memory: {gpu_config['available_memory_gb']:.1f} GB")

        click.echo("\n⚙️ Configuration:")
        click.echo(f"   Precision: {gpu_config['precision']}")
        click.echo(f"   Quantization: {gpu_config['quantization']}")
        click.echo(f"   Batch Size: {gpu_config['batch_size']}")
        click.echo(f"   Workers: {gpu_config['workers']}")
        click.echo(f"   Max Context: {gpu_config['max_context']}")
        click.echo(f"   Memory Optimized: {gpu_config['memory_optimized']}")

        # Environment variables
        click.echo("\n🌍 Environment Variables:")
        env_vars = [
            "SME_AGENT_GPU_ENABLED",
            "SME_AGENT_DEVICE",
            "SME_AGENT_GPU_TYPE",
            "SME_AGENT_PRECISION",
            "SME_AGENT_QUANTIZATION",
        ]

        for var in env_vars:
            value = os.getenv(var, "Not set")
            click.echo(f"   {var}: {value}")

        if gpu_config["warnings"]:
            click.echo("\n⚠️ Warnings:")
            for warning in gpu_config["warnings"]:
                click.echo(f"   - {warning}")

    except Exception as e:
        click.echo(f"❌ Status check failed: {e}")
        raise click.ClickException(f"Status error: {e}")


# Export CLI group
__all__ = ["llm_infrastructure_cli"]
