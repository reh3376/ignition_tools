"""LLM Infrastructure Manager - Phase 13.1: Auto-Detecting GPU Support.

This module manages 8B parameter LLM deployment with auto-detection for:
- NVIDIA CUDA GPU acceleration
- Apple Silicon MPS acceleration
- CPU-only fallback with optimizations

Following crawl_mcp.py methodology for robust, production-ready implementation.
"""

import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

from . import LLMInfrastructureError, auto_detect_gpu_configuration

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ModelConfig(BaseModel):
    """Step 2: Input Validation using Pydantic models (crawl_mcp.py methodology)."""

    model_name: str = Field(default="llama3.1-8b", description="8B parameter model name")
    model_path: str | None = Field(default=None, description="Local model path")
    quantization: str = Field(default="int8", description="Model quantization")
    max_context_length: int = Field(default=4096, ge=512, le=32768, description="Maximum context length")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    top_p: float = Field(default=0.9, ge=0.1, le=1.0, description="Top-p sampling")
    max_tokens: int = Field(default=512, ge=1, le=4096, description="Maximum generated tokens")

    @validator("quantization")
    def validate_quantization(cls, v):
        valid_options = ["fp32", "fp16", "int8", "int4"]
        if v not in valid_options:
            raise ValueError(f"Quantization must be one of {valid_options}")
        return v


class InfrastructureManager:
    """Step 3: Comprehensive Error Handling with Resource Management."""

    def __init__(self, config: ModelConfig | None = None):
        """Initialize LLM Infrastructure Manager with auto-detecting GPU support."""
        self.config = config or ModelConfig()
        self.gpu_config = auto_detect_gpu_configuration()
        self.model = None
        self.tokenizer = None
        self.is_initialized = False
        self.performance_metrics = {
            "initialization_time": 0.0,
            "inference_times": [],
            "memory_usage": 0.0,
            "gpu_utilization": 0.0,
        }

        logger.info(f"LLM Infrastructure Manager initialized with {self.gpu_config['gpu_type']} acceleration")

    async def initialize(self) -> dict[str, Any]:
        """Step 4: Modular initialization with comprehensive testing."""
        start_time = time.time()

        try:
            # Step 4.1: Validate environment
            validation_result = await self._validate_environment()
            if not validation_result["success"]:
                raise LLMInfrastructureError(f"Environment validation failed: {validation_result['errors']}")

            # Step 4.2: Load model with GPU auto-detection
            model_result = await self._load_model()
            if not model_result["success"]:
                raise LLMInfrastructureError(f"Model loading failed: {model_result['error']}")

            # Step 4.3: Test model functionality
            test_result = await self._test_model_functionality()
            if not test_result["success"]:
                raise LLMInfrastructureError(f"Model testing failed: {test_result['error']}")

            self.is_initialized = True
            self.performance_metrics["initialization_time"] = time.time() - start_time

            return {
                "success": True,
                "gpu_config": self.gpu_config,
                "model_config": self.config.dict(),
                "initialization_time": self.performance_metrics["initialization_time"],
                "memory_usage": self._get_memory_usage(),
            }

        except Exception as e:
            logger.error(f"LLM Infrastructure initialization failed: {e}")
            return {
                "success": False,
                "error": self._format_error(e),
                "gpu_config": self.gpu_config,
            }

    async def _validate_environment(self) -> dict[str, Any]:
        """Validate environment for LLM deployment."""
        try:
            validation_errors = []
            validation_warnings = []

            # Check PyTorch installation
            try:
                import torch

                logger.info(f"PyTorch version: {torch.__version__}")
            except ImportError:
                validation_errors.append("PyTorch not installed")

            # Check transformers library
            try:
                import transformers

                logger.info(f"Transformers version: {transformers.__version__}")
            except ImportError:
                validation_errors.append("Transformers library not installed")

            # Validate GPU configuration
            if self.gpu_config["gpu_type"] == "mps":
                try:
                    import torch

                    if not torch.backends.mps.is_available():
                        validation_warnings.append("MPS reported as available but not working")
                except Exception as e:
                    validation_warnings.append(f"MPS validation failed: {e}")

            elif self.gpu_config["gpu_type"] == "cuda":
                try:
                    import torch

                    if not torch.cuda.is_available():
                        validation_warnings.append("CUDA reported as available but not working")
                except Exception as e:
                    validation_warnings.append(f"CUDA validation failed: {e}")

            # Check available memory
            available_memory = self.gpu_config.get("available_memory_gb", 0)
            if available_memory < 4:
                validation_warnings.append(f"Low memory ({available_memory}GB) - may impact performance")

            return {
                "success": len(validation_errors) == 0,
                "errors": validation_errors,
                "warnings": validation_warnings,
            }

        except Exception as e:
            return {
                "success": False,
                "errors": [f"Environment validation error: {e}"],
                "warnings": [],
            }

    async def _load_model(self) -> dict[str, Any]:
        """Load 8B parameter model with auto-detected GPU configuration."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            # Configure device and precision based on auto-detection
            device = self.gpu_config["device"]
            precision = self.gpu_config["precision"]
            quantization = self.gpu_config["quantization"]

            logger.info(f"Loading model on {device} with {precision} precision and {quantization} quantization")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name, trust_remote_code=True, cache_dir="cache/models"
            )

            # Configure model loading parameters
            model_kwargs = {
                "trust_remote_code": True,
                "cache_dir": "cache/models",
                "low_cpu_mem_usage": True,
            }

            # Apply quantization
            if quantization == "int8":
                model_kwargs["load_in_8bit"] = True
            elif quantization == "int4":
                model_kwargs["load_in_4bit"] = True
            elif precision == "fp16":
                model_kwargs["torch_dtype"] = torch.float16

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(self.config.model_name, **model_kwargs)

            # Move to device if not already quantized
            if quantization in ["fp32", "fp16"]:
                self.model = self.model.to(device)

            # Set to evaluation mode
            self.model.eval()

            return {
                "success": True,
                "device": device,
                "precision": precision,
                "quantization": quantization,
                "memory_usage": self._get_memory_usage(),
            }

        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return {"success": False, "error": str(e)}

    async def _test_model_functionality(self) -> dict[str, Any]:
        """Test model functionality with simple inference."""
        try:
            if not self.model or not self.tokenizer:
                return {"success": False, "error": "Model or tokenizer not loaded"}

            # Simple test prompt
            test_prompt = "Hello, this is a test of the LLM infrastructure."

            # Tokenize
            inputs = self.tokenizer(test_prompt, return_tensors="pt")

            # Move inputs to device
            device = self.gpu_config["device"]
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # Generate
            start_time = time.time()
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            inference_time = time.time() - start_time

            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            return {
                "success": True,
                "test_prompt": test_prompt,
                "generated_text": generated_text,
                "inference_time": inference_time,
                "tokens_per_second": 50 / inference_time if inference_time > 0 else 0,
            }

        except Exception as e:
            logger.error(f"Model functionality test failed: {e}")
            return {"success": False, "error": str(e)}

    async def generate_text(self, prompt: str, **kwargs) -> dict[str, Any]:
        """Step 5: Progressive complexity - Generate text with error handling."""
        if not self.is_initialized:
            return {
                "success": False,
                "error": "Infrastructure not initialized. Call initialize() first.",
            }

        try:
            import torch

            # Merge generation parameters
            generation_params = {
                "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "do_sample": True,
                "pad_token_id": self.tokenizer.eos_token_id,
            }

            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            device = self.gpu_config["device"]
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # Generate text
            start_time = time.time()
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **generation_params)

            inference_time = time.time() - start_time

            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remove input prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt) :].strip()

            # Update performance metrics
            self.performance_metrics["inference_times"].append(inference_time)

            return {
                "success": True,
                "prompt": prompt,
                "generated_text": generated_text,
                "inference_time": inference_time,
                "tokens_generated": len(self.tokenizer.encode(generated_text)),
                "tokens_per_second": (
                    len(self.tokenizer.encode(generated_text)) / inference_time if inference_time > 0 else 0
                ),
            }

        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return {"success": False, "error": self._format_error(e)}

    def _get_memory_usage(self) -> float:
        """Get current memory usage in GB."""
        try:
            if self.gpu_config["gpu_type"] == "cuda":
                import torch

                return torch.cuda.memory_allocated() / (1024**3)
            elif self.gpu_config["gpu_type"] == "mps":
                import torch

                return (
                    torch.mps.current_allocated_memory() / (1024**3)
                    if hasattr(torch.mps, "current_allocated_memory")
                    else 0.0
                )
            else:
                import psutil

                return psutil.virtual_memory().used / (1024**3)
        except Exception:
            return 0.0

    def _format_error(self, error: Exception) -> str:
        """Format errors for user-friendly messages."""
        error_str = str(error).lower()

        if "cuda" in error_str or "mps" in error_str:
            return f"GPU error: {error}. Falling back to CPU mode may help."
        elif "memory" in error_str or "oom" in error_str:
            return f"Out of memory: {error}. Try reducing batch size or model size."
        elif "model" in error_str and "not found" in error_str:
            return f"Model not found: {error}. Check model name and availability."
        elif "connection" in error_str:
            return f"Connection error: {error}. Check network connectivity."
        else:
            return f"LLM Infrastructure error: {error}"

    @asynccontextmanager
    async def managed_inference(self) -> AsyncGenerator[dict[str, Any], None]:
        """Step 6: Resource management with proper cleanup."""
        try:
            if not self.is_initialized:
                await self.initialize()

            yield {
                "manager": self,
                "gpu_config": self.gpu_config,
                "performance_metrics": self.performance_metrics,
            }

        finally:
            # Cleanup resources
            await self._cleanup_resources()

    async def _cleanup_resources(self) -> None:
        """Clean up model resources."""
        try:
            if self.model:
                del self.model
                self.model = None

            if self.tokenizer:
                del self.tokenizer
                self.tokenizer = None

            # Clear GPU cache if available
            if self.gpu_config["gpu_type"] == "cuda":
                import torch

                torch.cuda.empty_cache()
            elif self.gpu_config["gpu_type"] == "mps":
                import torch

                if hasattr(torch.mps, "empty_cache"):
                    torch.mps.empty_cache()

            self.is_initialized = False
            logger.info("LLM Infrastructure resources cleaned up")

        except Exception as e:
            logger.warning(f"Resource cleanup warning: {e}")

    def get_status(self) -> dict[str, Any]:
        """Get current infrastructure status."""
        return {
            "initialized": self.is_initialized,
            "gpu_config": self.gpu_config,
            "model_config": self.config.dict(),
            "performance_metrics": self.performance_metrics,
            "memory_usage_gb": self._get_memory_usage(),
        }


# Export main components
__all__ = ["InfrastructureManager", "LLMInfrastructureError", "ModelConfig"]
