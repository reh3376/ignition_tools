"""LLM Infrastructure Module - Phase 13.1: LLM Infrastructure & Model Preparation.

This module implements auto-detecting GPU support for both NVIDIA CUDA and Apple Silicon MPS,
providing optimal configuration for 8B parameter LLM deployment.

Following crawl_mcp.py methodology:
- Step 1: Environment validation with auto-detection
- Step 2: Comprehensive input validation
- Step 3: Error handling with graceful fallbacks
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup
"""

import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMInfrastructureError(Exception):
    """Custom exception for LLM Infrastructure errors."""

    pass


def auto_detect_gpu_configuration() -> dict[str, Any]:
    """Step 1: Auto-detect optimal GPU configuration (crawl_mcp.py methodology).

    Automatically detects and configures the best available GPU acceleration:
    - NVIDIA CUDA (Linux/Windows)
    - Apple Silicon MPS (macOS)
    - CPU fallback (all platforms)

    Returns:
        dict containing GPU configuration and capabilities
    """
    config = {
        "platform": platform.system(),
        "architecture": platform.machine(),
        "gpu_type": "none",
        "device": "cpu",
        "precision": "fp32",
        "quantization": "int8",
        "batch_size": 1,
        "workers": 1,
        "max_context": 4096,
        "memory_optimized": True,
        "available_memory_gb": 0,
        "cuda_available": False,
        "mps_available": False,
        "errors": [],
        "warnings": [],
    }

    logger.info(f"Auto-detecting GPU configuration on {config['platform']} {config['architecture']}")

    # Step 1.1: Check for Apple Silicon MPS
    if config["platform"] == "Darwin" and config["architecture"] in [
        "arm64",
        "aarch64",
    ]:
        mps_config = _configure_apple_silicon_mps()
        if mps_config["success"]:
            config.update(mps_config["config"])
            config["gpu_type"] = "mps"
            logger.info("Apple Silicon MPS configuration applied")
        else:
            config["warnings"].extend(mps_config["warnings"])
            logger.warning("MPS not available, falling back to CPU")

    # Step 1.2: Check for NVIDIA CUDA (all platforms)
    if config["gpu_type"] == "none":
        cuda_config = _configure_nvidia_cuda()
        if cuda_config["success"]:
            config.update(cuda_config["config"])
            config["gpu_type"] = "cuda"
            logger.info("NVIDIA CUDA configuration applied")
        else:
            config["warnings"].extend(cuda_config["warnings"])
            logger.info("CUDA not available, using CPU")

    # Step 1.3: Apply CPU optimizations if no GPU
    if config["gpu_type"] == "none":
        cpu_config = _configure_cpu_optimizations()
        config.update(cpu_config)
        logger.info("CPU-only configuration applied")

    # Step 1.4: Set environment variables
    _apply_environment_configuration(config)

    return config


def _configure_apple_silicon_mps() -> dict[str, Any]:
    """Configure Apple Silicon MPS GPU acceleration."""
    result = {"success": False, "config": {}, "warnings": []}

    try:
        import torch

        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            # Test MPS functionality
            try:
                test_tensor = torch.randn(10, 10).to("mps")
                _ = test_tensor @ test_tensor.T

                # Get system memory
                memory_gb = _get_macos_memory()

                # Configure based on available memory
                if memory_gb >= 16:
                    mps_config = {
                        "device": "mps",
                        "precision": "fp16",
                        "quantization": "fp16",
                        "batch_size": 2,
                        "workers": 2,
                        "max_context": 8192,
                        "memory_optimized": False,
                    }
                elif memory_gb >= 8:
                    mps_config = {
                        "device": "mps",
                        "precision": "fp16",
                        "quantization": "int8",
                        "batch_size": 1,
                        "workers": 1,
                        "max_context": 4096,
                        "memory_optimized": True,
                    }
                else:
                    mps_config = {
                        "device": "mps",
                        "precision": "fp16",
                        "quantization": "int4",
                        "batch_size": 1,
                        "workers": 1,
                        "max_context": 2048,
                        "memory_optimized": True,
                    }

                mps_config["available_memory_gb"] = memory_gb
                mps_config["mps_available"] = True

                result["success"] = True
                result["config"] = mps_config

            except Exception as e:
                result["warnings"].append(f"MPS test failed: {e}")

        else:
            result["warnings"].append("PyTorch MPS not available")

    except ImportError:
        result["warnings"].append("PyTorch not installed")
    except Exception as e:
        result["warnings"].append(f"Error checking MPS: {e}")

    return result


def _configure_nvidia_cuda() -> dict[str, Any]:
    """Configure NVIDIA CUDA GPU acceleration."""
    result = {"success": False, "config": {}, "warnings": []}

    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.device_count()
            device_props = torch.cuda.get_device_properties(0)
            memory_gb = device_props.total_memory / (1024**3)

            # Configure based on GPU memory
            if memory_gb >= 12:
                cuda_config = {
                    "device": "cuda:0",
                    "precision": "fp16",
                    "quantization": "fp16",
                    "batch_size": 4,
                    "workers": 2,
                    "max_context": 8192,
                    "memory_optimized": False,
                }
            elif memory_gb >= 8:
                cuda_config = {
                    "device": "cuda:0",
                    "precision": "fp16",
                    "quantization": "int8",
                    "batch_size": 2,
                    "workers": 2,
                    "max_context": 6144,
                    "memory_optimized": True,
                }
            elif memory_gb >= 6:
                cuda_config = {
                    "device": "cuda:0",
                    "precision": "fp16",
                    "quantization": "int4",
                    "batch_size": 1,
                    "workers": 1,
                    "max_context": 4096,
                    "memory_optimized": True,
                }
            else:
                result["warnings"].append(f"GPU memory ({memory_gb:.1f}GB) insufficient for 8B model")
                return result

            cuda_config["available_memory_gb"] = memory_gb
            cuda_config["cuda_available"] = True

            result["success"] = True
            result["config"] = cuda_config

        else:
            result["warnings"].append("CUDA not available")

    except ImportError:
        result["warnings"].append("PyTorch not installed")
    except Exception as e:
        result["warnings"].append(f"Error checking CUDA: {e}")

    return result


def _configure_cpu_optimizations() -> dict[str, Any]:
    """Configure CPU-only optimizations."""
    import multiprocessing

    cpu_cores = multiprocessing.cpu_count()

    # Optimize for different CPU configurations
    if cpu_cores >= 8:
        cpu_config = {
            "device": "cpu",
            "precision": "fp32",
            "quantization": "int8",
            "batch_size": 1,
            "workers": min(4, cpu_cores // 2),
            "max_context": 4096,
            "memory_optimized": True,
        }
    else:
        cpu_config = {
            "device": "cpu",
            "precision": "fp32",
            "quantization": "int4",
            "batch_size": 1,
            "workers": 1,
            "max_context": 2048,
            "memory_optimized": True,
        }

    return cpu_config


def _get_macos_memory() -> float:
    """Get macOS system memory in GB."""
    try:
        result = subprocess.run(["sysctl", "hw.memsize"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            memory_bytes = int(result.stdout.split(":")[1].strip())
            return memory_bytes / (1024**3)
    except Exception:
        pass
    return 8.0  # Default fallback


def _apply_environment_configuration(config: dict[str, Any]) -> None:
    """Apply configuration to environment variables."""
    env_mapping = {
        "SME_AGENT_GPU_ENABLED": "true" if config["gpu_type"] != "none" else "false",
        "SME_AGENT_DEVICE": config["device"],
        "SME_AGENT_PRECISION": config["precision"],
        "SME_AGENT_QUANTIZATION": config["quantization"],
        "SME_AGENT_BATCH_SIZE": str(config["batch_size"]),
        "SME_AGENT_WORKERS": str(config["workers"]),
        "SME_AGENT_MAX_CONTEXT": str(config["max_context"]),
        "SME_AGENT_MEMORY_OPTIMIZED": "true" if config["memory_optimized"] else "false",
        "SME_AGENT_GPU_TYPE": config["gpu_type"],
    }

    # Platform-specific optimizations
    if config["gpu_type"] == "mps":
        env_mapping.update(
            {
                "PYTORCH_ENABLE_MPS_FALLBACK": "1",
                "PYTORCH_MPS_HIGH_WATERMARK_RATIO": "0.0",
            }
        )
    elif config["gpu_type"] == "cuda":
        env_mapping.update(
            {
                "CUDA_VISIBLE_DEVICES": "0",
                "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512",
            }
        )
    elif config["gpu_type"] == "none":
        env_mapping.update(
            {
                "OMP_NUM_THREADS": str(config["workers"] * 2),
                "MKL_NUM_THREADS": str(config["workers"] * 2),
            }
        )

    for key, value in env_mapping.items():
        os.environ[key] = value
        logger.debug(f"Set {key}={value}")


# Initialize auto-detection on import
_gpu_config = auto_detect_gpu_configuration()

# Export main components
__all__ = ["LLMInfrastructureError", "_gpu_config", "auto_detect_gpu_configuration"]
