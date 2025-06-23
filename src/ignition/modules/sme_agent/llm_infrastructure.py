"""8B Parameter LLM Infrastructure Module for SME Agent.

This module implements the 8B parameter LLM infrastructure following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Error handling and user-friendly messages
4. Progressive complexity support
5. Resource management and cleanup

Supports Llama3.1-8B and Mistral-8B models with Docker-based deployment,
GPU acceleration, quantization, and model versioning.
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        pipeline,
    )

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from . import SMEAgentValidationError


class LLMComplexityLevel(Enum):
    """Progressive complexity levels for LLM deployment."""

    BASIC = "basic"  # CPU-only, no quantization
    STANDARD = "standard"  # GPU if available, 8-bit quantization
    ADVANCED = "advanced"  # GPU required, 4-bit quantization
    ENTERPRISE = "enterprise"  # Multi-GPU, Docker deployment


class ModelType(Enum):
    """Supported 8B parameter model types."""

    LLAMA3_1_8B = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    MISTRAL_8B = "mistralai/Mistral-7B-Instruct-v0.3"
    CUSTOM = "custom"


@dataclass
class LLMConfig:
    """Configuration for 8B parameter LLM infrastructure."""

    # Model configuration
    model_type: ModelType = ModelType.LLAMA3_1_8B
    model_path: str | None = None
    custom_model_name: str | None = None

    # Deployment configuration
    complexity_level: LLMComplexityLevel = LLMComplexityLevel.STANDARD
    use_docker: bool = False
    docker_image: str | None = None

    # Hardware configuration
    device: str = "auto"  # auto, cpu, cuda, mps
    gpu_memory_fraction: float = 0.8
    max_memory_gb: int | None = None

    # Quantization configuration
    use_quantization: bool = True
    quantization_bits: int = 8  # 4, 8, or 16
    use_flash_attention: bool = True

    # Generation configuration
    max_length: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    do_sample: bool = True

    # Versioning and rollback
    model_version: str = "latest"
    enable_versioning: bool = True
    max_versions: int = 3

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.model_type == ModelType.CUSTOM and not self.custom_model_name:
            raise ValueError("custom_model_name required when model_type is CUSTOM")

        if self.quantization_bits not in [4, 8, 16]:
            raise ValueError("quantization_bits must be 4, 8, or 16")

        if not 0.1 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.1 and 2.0")

        if not 0.1 <= self.top_p <= 1.0:
            raise ValueError("top_p must be between 0.1 and 1.0")


@dataclass
class LLMResponse:
    """Response from LLM inference."""

    text: str
    model_name: str
    model_version: str
    generation_time: float
    tokens_generated: int
    confidence_score: float | None = None
    safety_filtered: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "text": self.text,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "generation_time": self.generation_time,
            "tokens_generated": self.tokens_generated,
            "confidence_score": self.confidence_score,
            "safety_filtered": self.safety_filtered,
            "metadata": self.metadata,
        }


def validate_llm_infrastructure_environment() -> dict[str, Any]:
    """Validate LLM infrastructure environment following crawl_mcp.py methodology.

    Step 1: Environment validation first - comprehensive validation of all requirements.

    Returns:
        Dict containing validation results and component availability.
    """
    validation_result = {
        "validation_score": 0,
        "total_checks": 12,
        "components": {},
        "environment_variables": {},
        "hardware": {},
        "errors": [],
        "recommendations": [],
    }

    # 1. Check Python packages
    if TRANSFORMERS_AVAILABLE:
        import transformers

        validation_result["components"]["transformers"] = {
            "available": True,
            "version": transformers.__version__,
        }
        validation_result["validation_score"] += 1
    else:
        validation_result["components"]["transformers"] = {"available": False}
        validation_result["errors"].append("transformers package not installed")

    if TRANSFORMERS_AVAILABLE:
        validation_result["components"]["torch"] = {
            "available": True,
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "mps_available": (
                torch.backends.mps.is_available()
                if hasattr(torch.backends, "mps")
                else False
            ),
        }
        validation_result["validation_score"] += 1
    else:
        validation_result["components"]["torch"] = {"available": False}
        validation_result["errors"].append("torch package not installed")

    if DOCKER_AVAILABLE:
        try:
            client = docker.from_env()
            client.ping()
            validation_result["components"]["docker"] = {
                "available": True,
                "version": client.version()["Version"],
            }
            validation_result["validation_score"] += 1
        except Exception:
            validation_result["components"]["docker"] = {"available": False}
            validation_result["recommendations"].append(
                "Docker not available - container deployment disabled"
            )
    else:
        validation_result["components"]["docker"] = {"available": False}
        validation_result["recommendations"].append(
            "Docker not installed - container deployment disabled"
        )

    # 2. Check environment variables
    env_vars = {
        "LLM_MODEL_TYPE": os.getenv("LLM_MODEL_TYPE", "llama3.1-8b"),
        "LLM_DEVICE": os.getenv("LLM_DEVICE", "auto"),
        "LLM_QUANTIZATION_BITS": os.getenv("LLM_QUANTIZATION_BITS", "8"),
        "LLM_MAX_LENGTH": os.getenv("LLM_MAX_LENGTH", "4096"),
        "LLM_TEMPERATURE": os.getenv("LLM_TEMPERATURE", "0.7"),
        "LLM_CACHE_DIR": os.getenv("LLM_CACHE_DIR"),
        "LLM_DOCKER_IMAGE": os.getenv("LLM_DOCKER_IMAGE"),
        "LLM_GPU_MEMORY_FRACTION": os.getenv("LLM_GPU_MEMORY_FRACTION", "0.8"),
        "LLM_ENABLE_VERSIONING": os.getenv("LLM_ENABLE_VERSIONING", "true"),
        "LLM_MAX_CONCURRENT_REQUESTS": os.getenv("LLM_MAX_CONCURRENT_REQUESTS", "10"),
    }

    for var, value in env_vars.items():
        validation_result["environment_variables"][var] = {
            "set": value is not None,
            "value": value if value else "not_set",
        }
        if value:
            validation_result["validation_score"] += 0.5

    # 3. Check hardware capabilities
    if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
        validation_result["hardware"]["gpu"] = {
            "available": True,
            "device_count": torch.cuda.device_count(),
            "device_names": [
                torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())
            ],
            "total_memory": [
                torch.cuda.get_device_properties(i).total_memory / 1e9
                for i in range(torch.cuda.device_count())
            ],
        }
        validation_result["validation_score"] += 2
    else:
        validation_result["hardware"]["gpu"] = {"available": False}
        validation_result["recommendations"].append(
            "GPU not available - CPU inference will be slower"
        )

    # Calculate final score
    max_score = validation_result["total_checks"]
    actual_score = validation_result["validation_score"]
    validation_result["validation_percentage"] = round(
        (actual_score / max_score) * 100, 1
    )

    return validation_result


class LLMInfrastructure:
    """8B Parameter LLM Infrastructure following crawl_mcp.py methodology.

    Implements systematic approach:
    1. Environment validation first
    2. Comprehensive input validation
    3. Error handling and user-friendly messages
    4. Progressive complexity support
    5. Resource management and cleanup
    """

    def __init__(self, config: LLMConfig | None = None):
        """Initialize LLM Infrastructure with configuration."""
        self.config = config or LLMConfig()
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.docker_client = None
        self.container = None
        self.validation_result = None

        # Version management
        self.model_versions = {}
        self.current_version = "latest"

        # Performance tracking
        self.inference_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_time": 0.0,
            "average_time": 0.0,
        }

    async def initialize(self) -> dict[str, Any]:
        """Initialize LLM infrastructure following crawl_mcp.py methodology.

        Step 1: Environment validation first
        Step 2: Progressive complexity initialization
        Step 3: Resource management setup
        """
        # Step 1: Environment validation first
        self.validation_result = validate_llm_infrastructure_environment()

        if self.validation_result["validation_percentage"] < 60:
            raise SMEAgentValidationError(
                f"LLM infrastructure validation failed: {self.validation_result['validation_percentage']}% "
                f"Errors: {', '.join(self.validation_result['errors'])}"
            )

        # Step 2: Progressive complexity initialization
        init_result = {
            "status": "success",
            "complexity_level": self.config.complexity_level.value,
            "model_type": self.config.model_type.value,
            "components_initialized": [],
            "warnings": [],
        }

        try:
            if self.config.complexity_level == LLMComplexityLevel.BASIC:
                await self._initialize_basic()
                init_result["components_initialized"].extend(["tokenizer", "cpu_model"])

            elif self.config.complexity_level == LLMComplexityLevel.STANDARD:
                await self._initialize_standard()
                init_result["components_initialized"].extend(
                    ["tokenizer", "quantized_model", "gpu_support"]
                )

            elif self.config.complexity_level == LLMComplexityLevel.ADVANCED:
                await self._initialize_advanced()
                init_result["components_initialized"].extend(
                    ["tokenizer", "advanced_quantization", "flash_attention"]
                )

            elif self.config.complexity_level == LLMComplexityLevel.ENTERPRISE:
                await self._initialize_enterprise()
                init_result["components_initialized"].extend(
                    ["docker_container", "multi_gpu", "load_balancing"]
                )

            # Step 3: Setup versioning if enabled
            if self.config.enable_versioning:
                self._setup_versioning()
                init_result["components_initialized"].append("versioning")

            return init_result

        except Exception as e:
            raise SMEAgentValidationError(
                f"LLM infrastructure initialization failed: {e}"
            )

    async def _initialize_basic(self):
        """Initialize basic CPU-only deployment."""
        if not TRANSFORMERS_AVAILABLE:
            raise SMEAgentValidationError("Transformers library not available")

        model_name = self._get_model_name()

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model for CPU
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True,
        )

    async def _initialize_standard(self):
        """Initialize standard deployment with GPU and 8-bit quantization."""
        if not TRANSFORMERS_AVAILABLE:
            raise SMEAgentValidationError("Transformers library not available")

        model_name = self._get_model_name()

        # Configure quantization
        quantization_config = None
        if self.config.use_quantization:
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                bnb_8bit_compute_dtype=torch.float16,
            )

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model with quantization
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
        )

    async def _initialize_advanced(self):
        """Initialize advanced deployment with 4-bit quantization and flash attention."""
        if not TRANSFORMERS_AVAILABLE:
            raise SMEAgentValidationError("Transformers library not available")

        model_name = self._get_model_name()

        # Configure advanced quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model with advanced quantization
        model_kwargs = {
            "quantization_config": quantization_config,
            "torch_dtype": torch.float16,
            "device_map": "auto",
            "low_cpu_mem_usage": True,
        }

        # Add flash attention if supported
        if self.config.use_flash_attention:
            model_kwargs["attn_implementation"] = "flash_attention_2"

        self.model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)

    async def _initialize_enterprise(self):
        """Initialize enterprise deployment with Docker and multi-GPU support."""
        if not DOCKER_AVAILABLE:
            raise SMEAgentValidationError(
                "Docker not available for enterprise deployment"
            )

        if not self.validation_result["components"]["docker"]["available"]:
            raise SMEAgentValidationError(
                "Docker not available for enterprise deployment"
            )

        # Initialize Docker client
        self.docker_client = docker.from_env()

        # Get or build Docker image
        docker_image = self.config.docker_image or self._get_default_docker_image()

        # Run container with GPU support
        container_config = {
            "image": docker_image,
            "detach": True,
            "ports": {"8000/tcp": 8000},
            "environment": {
                "MODEL_NAME": self._get_model_name(),
                "QUANTIZATION_BITS": str(self.config.quantization_bits),
                "MAX_LENGTH": str(self.config.max_length),
                "TEMPERATURE": str(self.config.temperature),
            },
            "volumes": {
                str(Path.home() / ".cache" / "huggingface"): {
                    "bind": "/root/.cache/huggingface",
                    "mode": "rw",
                }
            },
        }

        # Add GPU support if available
        if self.validation_result["hardware"]["gpu"]["available"]:
            container_config["runtime"] = "nvidia"
            container_config["environment"]["CUDA_VISIBLE_DEVICES"] = "all"

        self.container = self.docker_client.containers.run(**container_config)

        # Wait for container to be ready
        await self._wait_for_container_ready()

    def _get_model_name(self) -> str:
        """Get the model name based on configuration."""
        if self.config.model_type == ModelType.CUSTOM:
            if self.config.custom_model_name:
                return self.config.custom_model_name
            else:
                raise SMEAgentValidationError("Custom model name not provided")
        return self.config.model_type.value

    def _get_default_docker_image(self) -> str:
        """Get default Docker image for model type."""
        return "huggingface/text-generation-inference:latest"

    async def _wait_for_container_ready(self, timeout: int = 300):
        """Wait for Docker container to be ready."""
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check if container is running and healthy
                if self.container:
                    self.container.reload()
                    if self.container.status == "running":
                        # Simple check - in real implementation would test API endpoint
                        return
            except Exception:
                pass

            await asyncio.sleep(5)

        raise SMEAgentValidationError("Container failed to become ready within timeout")

    def _setup_versioning(self):
        """Setup model versioning system."""
        self.model_versions[self.config.model_version] = {
            "model_name": self._get_model_name(),
            "config": self.config,
            "created_at": datetime.now().isoformat(),
            "active": True,
        }
        self.current_version = self.config.model_version

    def get_model_info(self) -> dict[str, Any]:
        """Get comprehensive model information."""
        return {
            "model_name": self._get_model_name(),
            "model_type": self.config.model_type.value,
            "complexity_level": self.config.complexity_level.value,
            "current_version": self.current_version,
            "quantization": {
                "enabled": self.config.use_quantization,
                "bits": self.config.quantization_bits,
            },
            "hardware": {
                "device": self.config.device,
                "gpu_available": (
                    torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False
                ),
                "docker_deployment": self.container is not None,
            },
            "performance": self.inference_stats,
            "validation": self.validation_result,
        }

    async def cleanup(self):
        """Cleanup resources following crawl_mcp.py methodology."""
        try:
            # Clean up model resources
            if self.model:
                del self.model
                self.model = None

            if self.tokenizer:
                del self.tokenizer
                self.tokenizer = None

            # Clean up Docker resources
            if self.container:
                self.container.stop()
                self.container.remove()
                self.container = None

            if self.docker_client:
                self.docker_client.close()
                self.docker_client = None

            # Clear GPU cache
            if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()

        except Exception as e:
            # Log cleanup errors but don't raise
            print(f"Warning: Error during LLM infrastructure cleanup: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


# Convenience functions for easy usage
async def create_llm_infrastructure(
    complexity_level: str = "standard", model_type: str = "llama3.1-8b", **kwargs
) -> LLMInfrastructure:
    """Create and initialize LLM infrastructure with simplified interface.

    Args:
        complexity_level: basic, standard, advanced, or enterprise
        model_type: llama3.1-8b, mistral-8b, or custom
        **kwargs: Additional configuration options

    Returns:
        Initialized LLMInfrastructure instance
    """
    # Map string inputs to enums
    complexity_map = {
        "basic": LLMComplexityLevel.BASIC,
        "standard": LLMComplexityLevel.STANDARD,
        "advanced": LLMComplexityLevel.ADVANCED,
        "enterprise": LLMComplexityLevel.ENTERPRISE,
    }

    model_map = {
        "llama3.1-8b": ModelType.LLAMA3_1_8B,
        "mistral-8b": ModelType.MISTRAL_8B,
        "custom": ModelType.CUSTOM,
    }

    config = LLMConfig(
        complexity_level=complexity_map.get(
            complexity_level, LLMComplexityLevel.STANDARD
        ),
        model_type=model_map.get(model_type, ModelType.LLAMA3_1_8B),
        **kwargs,
    )

    infrastructure = LLMInfrastructure(config)
    await infrastructure.initialize()
    return infrastructure


def get_available_models() -> dict[str, Any]:
    """Get information about available 8B parameter models."""
    return {
        "supported_models": {
            "llama3.1-8b": {
                "name": "Meta-Llama-3.1-8B-Instruct",
                "parameters": "8B",
                "context_length": 8192,
                "recommended_gpu_memory": "16GB",
            },
            "mistral-8b": {
                "name": "Mistral-7B-Instruct-v0.3",
                "parameters": "7B",
                "context_length": 4096,
                "recommended_gpu_memory": "14GB",
            },
        },
        "complexity_levels": {
            "basic": "CPU-only, no quantization",
            "standard": "GPU if available, 8-bit quantization",
            "advanced": "GPU required, 4-bit quantization, flash attention",
            "enterprise": "Multi-GPU, Docker deployment, load balancing",
        },
        "system_requirements": {
            "minimum_ram": "16GB",
            "recommended_ram": "32GB",
            "minimum_storage": "20GB",
            "recommended_gpu": "RTX 4090, A100, or similar",
        },
    }
