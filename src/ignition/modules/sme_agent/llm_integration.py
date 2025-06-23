"""
LLM Integration Module for SME Agent - Phase 11.1
8B Parameter LLM Infrastructure Implementation

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import threading

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    import torch
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        pipeline,
        TextStreamer
    )
    from huggingface_hub import snapshot_download
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import platform
    PLATFORM_AVAILABLE = True
except ImportError:
    PLATFORM_AVAILABLE = False


class LLMValidationError(Exception):
    """Custom exception for LLM validation errors."""
    pass


@dataclass
class SystemEnvironment:
    """System environment information for LLM optimization."""
    
    # Environment Type
    env_type: str  # "nvidia_gpu", "macos_unified", "cpu_only"
    platform: str  # "windows", "linux", "darwin"
    architecture: str  # "x86_64", "arm64", etc.
    
    # Hardware Specifications
    total_memory_gb: float
    available_memory_gb: float
    cpu_cores: int
    
    # GPU/Unified Memory Information
    has_cuda: bool = False
    cuda_version: Optional[str] = None
    gpu_count: int = 0
    gpu_memory_gb: List[float] = field(default_factory=list)
    gpu_names: List[str] = field(default_factory=list)
    
    # macOS Unified Memory
    has_unified_memory: bool = False
    unified_memory_gb: float = 0.0
    metal_available: bool = False
    
    # Optimization Recommendations
    recommended_device: str = "cpu"  # "cuda", "mps", "cpu"
    recommended_quantization: str = "int8"
    can_run_full_precision: bool = False
    optimal_batch_size: int = 1


def detect_system_environment() -> SystemEnvironment:
    """
    Step 1: Environment Validation First
    
    Detect and analyze the system environment for optimal LLM configuration.
    Supports:
    - Env01: NVIDIA GPU on Windows/Linux
    - Env02: macOS with M3+ unified memory
    """
    env = SystemEnvironment(
        env_type="cpu_only",
        platform="unknown",
        architecture="unknown",
        total_memory_gb=0.0,
        available_memory_gb=0.0,
        cpu_cores=1
    )
    
    # Detect platform and architecture
    if PLATFORM_AVAILABLE:
        env.platform = platform.system().lower()
        env.architecture = platform.machine().lower()
    
    # Get system memory information
    if PSUTIL_AVAILABLE:
        memory = psutil.virtual_memory()
        env.total_memory_gb = memory.total / (1024**3)
        env.available_memory_gb = memory.available / (1024**3)
        env.cpu_cores = psutil.cpu_count(logical=False) or 1
    
    # Detect CUDA/NVIDIA environment (Env01)
    if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
        env.has_cuda = True
        env.gpu_count = torch.cuda.device_count()
        
        try:
            env.cuda_version = str(torch.version.cuda)
        except AttributeError:
            env.cuda_version = "unknown"
        
        # Get GPU memory and names
        for i in range(env.gpu_count):
            try:
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                gpu_name = torch.cuda.get_device_name(i)
                env.gpu_memory_gb.append(gpu_memory)
                env.gpu_names.append(gpu_name)
            except Exception:
                env.gpu_memory_gb.append(0.0)
                env.gpu_names.append("Unknown GPU")
        
        # Determine if this is a capable NVIDIA environment
        if env.gpu_count > 0 and max(env.gpu_memory_gb) >= 6.0:
            env.env_type = "nvidia_gpu"
            env.recommended_device = "cuda"
            
            # Check if we can run full precision
            max_vram = max(env.gpu_memory_gb)
            if max_vram >= 16.0:
                env.can_run_full_precision = True
                env.recommended_quantization = "none"
            elif max_vram >= 12.0:
                env.recommended_quantization = "fp16"
            else:
                env.recommended_quantization = "int8"
    
    # Detect macOS unified memory environment (Env02)
    elif env.platform == "darwin" and env.architecture in ["arm64", "aarch64"]:
        # Check for Metal Performance Shaders (MPS) support
        if TRANSFORMERS_AVAILABLE and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            env.metal_available = True
            env.has_unified_memory = True
            env.unified_memory_gb = env.total_memory_gb  # Unified memory = system memory
            
            # Determine if this is M3+ with sufficient memory
            if env.unified_memory_gb >= 18.0:  # M3 Pro/Max typically have 18GB+
                env.env_type = "macos_unified"
                env.recommended_device = "mps"
                
                # macOS unified memory optimization
                if env.unified_memory_gb >= 36.0:  # M3 Max with 36GB+
                    env.can_run_full_precision = True
                    env.recommended_quantization = "none"
                elif env.unified_memory_gb >= 24.0:  # M3 Pro/Max with 24GB+
                    env.recommended_quantization = "fp16"
                else:
                    env.recommended_quantization = "int8"
                
                # Optimal batch size for unified memory
                env.optimal_batch_size = min(4, int(env.unified_memory_gb / 8))
    
    # Fallback to CPU-only environment
    if env.env_type == "cpu_only":
        env.recommended_device = "cpu"
        env.recommended_quantization = "int8" if env.total_memory_gb >= 16.0 else "int4"
    
    return env


@dataclass
class LLMModelInfo:
    """Information about available LLM models."""
    model_id: str
    display_name: str
    size_gb: float
    min_vram_gb: float
    recommended_vram_gb: float
    supports_quantization: bool
    context_length: int
    description: str


@dataclass
class LLMConfig:
    """Configuration for LLM integration with environment-specific optimizations."""
    
    # Model Configuration
    model_name: str = "llama3.1-8b"
    model_path: Optional[str] = None
    quantization: str = "auto"  # auto, none, int8, int4, fp16
    gpu_enabled: bool = True  # Enable GPU/MPS acceleration when available
    device_map: str = "auto"
    max_memory: Optional[Dict[str, str]] = None
    
    # Environment-Specific Configuration
    target_device: str = "auto"  # auto, cuda, mps, cpu
    environment_type: str = "auto"  # auto, nvidia_gpu, macos_unified, cpu_only
    force_cpu: bool = False  # Force CPU-only execution
    optimize_for_environment: bool = True  # Auto-optimize based on detected environment
    
    # Generation Parameters
    max_context: int = 8192
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    do_sample: bool = True
    
    # Performance Configuration
    torch_dtype: str = "auto"
    trust_remote_code: bool = False
    use_cache: bool = True
    low_cpu_mem_usage: bool = True
    
    # Environment-Specific Performance Settings
    nvidia_gpu_settings: Dict[str, Any] = field(default_factory=lambda: {
        "use_flash_attention": True,
        "torch_compile": False,  # Experimental
        "tensor_parallel": False,
        "gpu_memory_fraction": 0.9
    })
    
    macos_unified_settings: Dict[str, Any] = field(default_factory=lambda: {
        "use_metal_performance_shaders": True,
        "unified_memory_optimization": True,
        "batch_size_optimization": True,
        "memory_efficient_attention": True
    })
    
    # Docker Configuration
    use_docker: bool = False
    docker_image: str = "huggingface/transformers-pytorch-gpu"
    docker_port: int = 8080
    docker_memory_limit: str = "16g"
    
    # System Configuration
    cache_dir: str = "models"
    log_level: str = "INFO"
    model_download_timeout: int = 3600  # 1 hour
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate quantization
        valid_quantization = ["auto", "none", "int8", "int4", "fp16"]
        if self.quantization not in valid_quantization:
            raise LLMValidationError(f"Invalid quantization '{self.quantization}'. Must be one of: {valid_quantization}")
        
        # Validate target device
        valid_devices = ["auto", "cuda", "mps", "cpu"]
        if self.target_device not in valid_devices:
            raise LLMValidationError(f"Invalid target device '{self.target_device}'. Must be one of: {valid_devices}")
        
        # Validate environment type
        valid_env_types = ["auto", "nvidia_gpu", "macos_unified", "cpu_only"]
        if self.environment_type not in valid_env_types:
            raise LLMValidationError(f"Invalid environment type '{self.environment_type}'. Must be one of: {valid_env_types}")
        
        # Validate numeric ranges
        if not 0.0 <= self.temperature <= 2.0:
            raise LLMValidationError(f"Temperature {self.temperature} must be between 0.0 and 2.0")
        if not 0.0 <= self.top_p <= 1.0:
            raise LLMValidationError(f"Top-p {self.top_p} must be between 0.0 and 1.0")
        if self.max_context <= 0:
            raise LLMValidationError(f"Max context {self.max_context} must be positive")
        if self.max_tokens <= 0:
            raise LLMValidationError(f"Max tokens {self.max_tokens} must be positive")
    
    def optimize_for_system_environment(self, system_env: SystemEnvironment) -> 'LLMConfig':
        """
        Step 5: Progressive Complexity Support
        
        Create an optimized configuration based on the detected system environment.
        """
        if not self.optimize_for_environment:
            return self
        
        # Create a copy for optimization
        optimized_config = LLMConfig(
            model_name=self.model_name,
            model_path=self.model_path,
            quantization=self.quantization,
            gpu_enabled=self.gpu_enabled,
            device_map=self.device_map,
            max_memory=self.max_memory,
            target_device=self.target_device,
            environment_type=self.environment_type,
            force_cpu=self.force_cpu,
            optimize_for_environment=self.optimize_for_environment,
            max_context=self.max_context,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repetition_penalty=self.repetition_penalty,
            do_sample=self.do_sample,
            torch_dtype=self.torch_dtype,
            trust_remote_code=self.trust_remote_code,
            use_cache=self.use_cache,
            low_cpu_mem_usage=self.low_cpu_mem_usage,
            nvidia_gpu_settings=self.nvidia_gpu_settings.copy(),
            macos_unified_settings=self.macos_unified_settings.copy(),
            use_docker=self.use_docker,
            docker_image=self.docker_image,
            docker_port=self.docker_port,
            docker_memory_limit=self.docker_memory_limit,
            cache_dir=self.cache_dir,
            log_level=self.log_level,
            model_download_timeout=self.model_download_timeout
        )
        
        # Apply environment-specific optimizations
        if system_env.env_type == "nvidia_gpu":
            optimized_config._optimize_for_nvidia_gpu(system_env)
        elif system_env.env_type == "macos_unified":
            optimized_config._optimize_for_macos_unified(system_env)
        else:
            optimized_config._optimize_for_cpu_only(system_env)
        
        return optimized_config
    
    def _optimize_for_nvidia_gpu(self, system_env: SystemEnvironment):
        """Optimize configuration for NVIDIA GPU environment (Env01)."""
        self.environment_type = "nvidia_gpu"
        self.target_device = "cuda" if not self.force_cpu else "cpu"
        self.gpu_enabled = True and not self.force_cpu
        
        # Auto-select quantization based on VRAM
        if self.quantization == "auto":
            self.quantization = system_env.recommended_quantization
        
        # NVIDIA-specific optimizations
        max_vram = max(system_env.gpu_memory_gb) if system_env.gpu_memory_gb else 0
        
        if max_vram >= 24.0:  # High-end GPUs (RTX 4090, A100, etc.)
            self.nvidia_gpu_settings.update({
                "use_flash_attention": True,
                "torch_compile": True,
                "gpu_memory_fraction": 0.95
            })
        elif max_vram >= 16.0:  # Mid-high end GPUs (RTX 4080, RTX 3090, etc.)
            self.nvidia_gpu_settings.update({
                "use_flash_attention": True,
                "torch_compile": False,
                "gpu_memory_fraction": 0.9
            })
        else:  # Lower-end GPUs
            self.nvidia_gpu_settings.update({
                "use_flash_attention": False,
                "torch_compile": False,
                "gpu_memory_fraction": 0.85
            })
            # Force more aggressive quantization for lower VRAM
            if self.quantization in ["none", "fp16"]:
                self.quantization = "int8"
    
    def _optimize_for_macos_unified(self, system_env: SystemEnvironment):
        """Optimize configuration for macOS unified memory environment (Env02)."""
        self.environment_type = "macos_unified"
        self.target_device = "mps" if not self.force_cpu else "cpu"
        self.gpu_enabled = True and not self.force_cpu
        
        # Auto-select quantization based on unified memory
        if self.quantization == "auto":
            self.quantization = system_env.recommended_quantization
        
        # macOS-specific optimizations
        if system_env.unified_memory_gb >= 36.0:  # M3 Max with 36GB+
            self.macos_unified_settings.update({
                "unified_memory_optimization": True,
                "batch_size_optimization": True,
                "memory_efficient_attention": True
            })
            # Can handle larger context windows
            self.max_context = min(16384, self.max_context * 2)
        elif system_env.unified_memory_gb >= 24.0:  # M3 Pro/Max with 24GB+
            self.macos_unified_settings.update({
                "unified_memory_optimization": True,
                "batch_size_optimization": True,
                "memory_efficient_attention": True
            })
        else:  # M3 base with 18GB
            self.macos_unified_settings.update({
                "unified_memory_optimization": True,
                "batch_size_optimization": True,
                "memory_efficient_attention": True
            })
            # More conservative settings for base M3
            if self.quantization in ["none", "fp16"]:
                self.quantization = "int8"
    
    def _optimize_for_cpu_only(self, system_env: SystemEnvironment):
        """Optimize configuration for CPU-only environment."""
        self.environment_type = "cpu_only"
        self.target_device = "cpu"
        self.gpu_enabled = False
        
        # CPU optimizations
        if self.quantization == "auto":
            self.quantization = system_env.recommended_quantization
        
        # Adjust for CPU performance
        self.low_cpu_mem_usage = True
        self.use_cache = True
        
        # Reduce context window for CPU to improve performance
        if system_env.total_memory_gb < 16.0:
            self.max_context = min(4096, self.max_context)
            self.max_tokens = min(1024, self.max_tokens)


class LLMModelRegistry:
    """Registry of supported LLM models with their specifications."""
    
    SUPPORTED_MODELS = {
        "llama3.1-8b": LLMModelInfo(
            model_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
            display_name="Llama 3.1 8B Instruct",
            size_gb=16.0,
            min_vram_gb=8.0,
            recommended_vram_gb=16.0,
            supports_quantization=True,
            context_length=131072,
            description="Meta's Llama 3.1 8B parameter model optimized for instruction following"
        ),
        "mistral-8b": LLMModelInfo(
            model_id="mistralai/Mistral-7B-Instruct-v0.3",
            display_name="Mistral 7B Instruct v0.3",
            size_gb=14.0,
            min_vram_gb=7.0,
            recommended_vram_gb=14.0,
            supports_quantization=True,
            context_length=32768,
            description="Mistral's 7B parameter model with instruction tuning"
        ),
        "codellama-8b": LLMModelInfo(
            model_id="codellama/CodeLlama-7b-Instruct-hf",
            display_name="Code Llama 7B Instruct",
            size_gb=13.0,
            min_vram_gb=7.0,
            recommended_vram_gb=13.0,
            supports_quantization=True,
            context_length=16384,
            description="Meta's Code Llama specialized for code generation and understanding"
        )
    }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Optional[LLMModelInfo]:
        """Get model information by name."""
        return cls.SUPPORTED_MODELS.get(model_name)
    
    @classmethod
    def list_models(cls) -> List[LLMModelInfo]:
        """List all supported models."""
        return list(cls.SUPPORTED_MODELS.values())


def validate_llm_environment() -> Dict[str, Any]:
    """
    Step 1: Environment Validation First
    
    Validate LLM environment and dependencies.
    
    Returns:
        Dict containing validation results
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "components_available": {},
        "system_info": {},
        "recommendations": []
    }
    
    try:
        # Check Python version
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        validation_result["system_info"]["python_version"] = python_version
        
        if sys.version_info < (3, 8):
            validation_result["errors"].append("Python 3.8+ required for LLM integration")
            validation_result["valid"] = False
        
        # Check PyTorch availability and version
        if TRANSFORMERS_AVAILABLE:
            validation_result["components_available"]["pytorch"] = True
            validation_result["system_info"]["torch_version"] = torch.__version__
            validation_result["system_info"]["cuda_available"] = torch.cuda.is_available()
            
            if torch.cuda.is_available():
                try:
                    validation_result["system_info"]["cuda_version"] = str(torch.version.cuda)
                except AttributeError:
                    validation_result["system_info"]["cuda_version"] = "unknown"
                validation_result["system_info"]["gpu_count"] = torch.cuda.device_count()
                validation_result["system_info"]["gpu_names"] = [
                    torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())
                ]
                
                # Check VRAM
                gpu_memory = []
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    total_memory_gb = props.total_memory / (1024**3)
                    gpu_memory.append(total_memory_gb)
                validation_result["system_info"]["gpu_memory_gb"] = gpu_memory
            else:
                validation_result["warnings"].append("CUDA not available - LLM will run on CPU (slower)")
                
        else:
            validation_result["components_available"]["pytorch"] = False
            validation_result["errors"].append("PyTorch/Transformers not installed")
            validation_result["valid"] = False
        
        # Check Transformers library
        validation_result["components_available"]["transformers"] = TRANSFORMERS_AVAILABLE
        if TRANSFORMERS_AVAILABLE:
            import transformers
            validation_result["system_info"]["transformers_version"] = transformers.__version__
        else:
            validation_result["errors"].append("Transformers library not installed")
            validation_result["valid"] = False
        
        # Check BitsAndBytes for quantization
        try:
            import bitsandbytes
            validation_result["components_available"]["bitsandbytes"] = True
            validation_result["system_info"]["bitsandbytes_version"] = bitsandbytes.__version__
        except ImportError:
            validation_result["components_available"]["bitsandbytes"] = False
            validation_result["warnings"].append("BitsAndBytes not available - quantization disabled")
        
        # Check Docker availability
        validation_result["components_available"]["docker"] = DOCKER_AVAILABLE
        if DOCKER_AVAILABLE:
            try:
                client = docker.from_env()
                client.ping()
                validation_result["system_info"]["docker_version"] = client.version()["Version"]
            except Exception:
                validation_result["components_available"]["docker"] = False
                validation_result["warnings"].append("Docker daemon not running")
        else:
            validation_result["warnings"].append("Docker not available - containerized deployment disabled")
        
        # Check system resources
        if PSUTIL_AVAILABLE:
            memory_gb = psutil.virtual_memory().total / (1024**3)
            validation_result["system_info"]["system_memory_gb"] = memory_gb
            
            if memory_gb < 16:
                validation_result["warnings"].append("Less than 16GB RAM - may limit model performance")
            
            # Check disk space
            disk_usage = psutil.disk_usage('/')
            free_space_gb = disk_usage.free / (1024**3)
            validation_result["system_info"]["free_disk_space_gb"] = free_space_gb
            
            if free_space_gb < 50:
                validation_result["warnings"].append("Less than 50GB free disk space - may not accommodate large models")
        else:
            validation_result["warnings"].append("psutil not available - cannot check system resources")
        
        # Generate recommendations
        if validation_result["system_info"].get("cuda_available"):
            validation_result["recommendations"].append("GPU detected - enable GPU acceleration for better performance")
        else:
            validation_result["recommendations"].append("Consider GPU acceleration for production deployment")
        
        if validation_result["components_available"].get("bitsandbytes"):
            validation_result["recommendations"].append("Use quantization (int8/int4) to reduce memory usage")
        
        memory_gb = validation_result["system_info"].get("system_memory_gb", 0)
        if memory_gb >= 32:
            validation_result["recommendations"].append("Sufficient RAM for large models without quantization")
        elif memory_gb >= 16:
            validation_result["recommendations"].append("Use quantization for 8B parameter models")
        elif memory_gb > 0:
            validation_result["recommendations"].append("Consider smaller models or quantization")
        
    except Exception as e:
        validation_result["valid"] = False
        validation_result["errors"].append(f"Environment validation failed: {e}")
    
    return validation_result


class LLMModelManager:
    """
    LLM Model Manager - Handles model loading, quantization, and management.
    
    Following crawl_mcp.py methodology for progressive complexity and resource management.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize LLM Model Manager with environment optimization.
        
        Args:
            config: LLM configuration
        """
        # Detect system environment first
        self.system_environment = detect_system_environment()
        
        # Optimize configuration for the detected environment
        self.config = config.optimize_for_system_environment(self.system_environment)
        
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.model_info = None
        self.device = None
        self.is_loaded = False
        
        # Setup logging
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(level=log_level)
        
        # Log environment detection results
        self.logger.info(f"Detected environment: {self.system_environment.env_type}")
        self.logger.info(f"Platform: {self.system_environment.platform} ({self.system_environment.architecture})")
        self.logger.info(f"Optimized device: {self.config.target_device}")
        self.logger.info(f"Optimized quantization: {self.config.quantization}")
        
        # Create cache directory
        self.cache_dir = Path(self.config.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Validate environment
        self.validation_result = validate_llm_environment()
        if not self.validation_result["valid"]:
            raise LLMValidationError(f"Environment validation failed: {self.validation_result['errors']}")
    
    def get_model_info(self) -> Optional[LLMModelInfo]:
        """Get information about the configured model."""
        return LLMModelRegistry.get_model_info(self.config.model_name)
    
    def check_system_requirements(self) -> Dict[str, Any]:
        """
        Step 4: Modular Component Testing
        
        Check if system meets requirements for the configured model.
        """
        model_info = self.get_model_info()
        if not model_info:
            return {
                "meets_requirements": False,
                "error": f"Unknown model: {self.config.model_name}"
            }
        
        system_info = self.validation_result["system_info"]
        
        # Check memory requirements
        available_memory_gb = system_info.get("system_memory_gb", 0)
        gpu_memory_gb = system_info.get("gpu_memory_gb", [])
        cuda_available = system_info.get("cuda_available", False)
        
        requirements_check = {
            "meets_requirements": True,
            "model_info": model_info,
            "checks": {},
            "recommendations": []
        }
        
        # Memory check
        if self.config.gpu_enabled and cuda_available and gpu_memory_gb:
            max_gpu_memory = max(gpu_memory_gb)
            if max_gpu_memory >= model_info.recommended_vram_gb:
                requirements_check["checks"]["gpu_memory"] = "✅ Excellent"
            elif max_gpu_memory >= model_info.min_vram_gb:
                requirements_check["checks"]["gpu_memory"] = "⚠️ Minimum (consider quantization)"
                requirements_check["recommendations"].append("Use quantization to reduce VRAM usage")
            else:
                requirements_check["checks"]["gpu_memory"] = "❌ Insufficient"
                requirements_check["meets_requirements"] = False
        else:
            # CPU memory check
            required_memory = model_info.size_gb * 1.5  # Buffer for processing
            if available_memory_gb >= required_memory:
                requirements_check["checks"]["system_memory"] = "✅ Sufficient for CPU"
            else:
                requirements_check["checks"]["system_memory"] = "❌ Insufficient"
                requirements_check["meets_requirements"] = False
        
        # Quantization support
        if model_info.supports_quantization and self.config.quantization != "none":
            requirements_check["checks"]["quantization"] = f"✅ {self.config.quantization.upper()}"
        elif self.config.quantization != "none":
            requirements_check["checks"]["quantization"] = "⚠️ Not supported"
            requirements_check["recommendations"].append("Quantization not supported for this model")
        
        return requirements_check
    
    def generate_response(self, prompt: str, **generation_kwargs) -> Dict[str, Any]:
        """
        Step 2: Comprehensive Input Validation
        Step 3: Error Handling and User-Friendly Messages
        
        Generate response from the loaded model.
        """
        if not TRANSFORMERS_AVAILABLE:
            return {
                "success": False,
                "error": "Transformers library not available - using placeholder response",
                "response": f"[PLACEHOLDER] This is a simulated response to: {prompt[:100]}...",
                "processing_time": 0.1,
                "model_used": self.config.model_name
            }
        
        if not self.is_loaded:
            return {
                "success": False,
                "error": "Model not loaded - using placeholder response",
                "response": f"[PLACEHOLDER] This is a simulated response to: {prompt[:100]}...",
                "processing_time": 0.1,
                "model_used": self.config.model_name
            }
        
        # Input validation
        if not prompt or not prompt.strip():
            raise LLMValidationError("Prompt cannot be empty")
        
        if len(prompt) > self.config.max_context * 4:  # Rough token estimate
            raise LLMValidationError(f"Prompt too long (estimated tokens exceed {self.config.max_context})")
        
        start_time = time.time()
        
        try:
            # Merge generation parameters
            generation_params = {
                "max_new_tokens": generation_kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": generation_kwargs.get("temperature", self.config.temperature),
                "top_p": generation_kwargs.get("top_p", self.config.top_p),
                "top_k": generation_kwargs.get("top_k", self.config.top_k),
                "repetition_penalty": generation_kwargs.get("repetition_penalty", self.config.repetition_penalty),
                "do_sample": generation_kwargs.get("do_sample", self.config.do_sample),
                "pad_token_id": self.tokenizer.eos_token_id if self.tokenizer else None,
                "return_full_text": False
            }
            
            # Generate response
            if self.pipeline:
                outputs = self.pipeline(prompt, **generation_params)
            else:
                outputs = []
            
            # Extract generated text
            if outputs and len(outputs) > 0:
                generated_text = outputs[0]["generated_text"]
            else:
                generated_text = ""
            
            processing_time = time.time() - start_time
            
            # Calculate approximate token counts
            if self.tokenizer:
                input_tokens = len(self.tokenizer.encode(prompt))
                output_tokens = len(self.tokenizer.encode(generated_text))
            else:
                input_tokens = len(prompt.split())  # Rough estimate
                output_tokens = len(generated_text.split())  # Rough estimate
            
            return {
                "success": True,
                "response": generated_text,
                "processing_time": processing_time,
                "token_counts": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "generation_params": generation_params,
                "model_used": self.config.model_name
            }
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "response": f"[ERROR] Generation failed: {str(e)[:100]}...",
                "model_used": self.config.model_name
            }
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and information."""
        status = {
            "loaded": self.is_loaded,
            "model_name": self.config.model_name,
            "device": self.device,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "configuration": {
                "quantization": self.config.quantization,
                "gpu_enabled": self.config.gpu_enabled,
                "max_context": self.config.max_context,
                "max_tokens": self.config.max_tokens
            }
        }
        
        if self.model_info:
            status["model_info"] = {
                "display_name": self.model_info.display_name,
                "size_gb": self.model_info.size_gb,
                "context_length": self.model_info.context_length,
                "description": self.model_info.description
            }
        
        if self.is_loaded and self.device == "cuda" and TRANSFORMERS_AVAILABLE:
            status["memory_usage"] = {
                "gpu_allocated_gb": torch.cuda.memory_allocated() / (1024**3),
                "gpu_reserved_gb": torch.cuda.memory_reserved() / (1024**3)
            }
        
        return status
    
    def unload_model(self):
        """
        Step 6: Resource Management and Cleanup
        
        Unload model and free resources.
        """
        if self.is_loaded:
            self.logger.info("Unloading model...")
            
            # Clear model and pipeline
            self.model = None
            self.tokenizer = None
            self.pipeline = None
            
            # Clear CUDA cache if using GPU
            if self.device == "cuda" and TRANSFORMERS_AVAILABLE:
                torch.cuda.empty_cache()
            
            self.is_loaded = False
            self.device = None
            self.logger.info("Model unloaded successfully")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.unload_model() 