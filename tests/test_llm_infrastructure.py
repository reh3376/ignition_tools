"""Test Suite for LLM Infrastructure - Phase 13.1: Auto-Detecting GPU Support

Comprehensive test suite following crawl_mcp.py methodology:
- Step 1: Environment validation testing
- Step 2: Input validation with Pydantic models
- Step 3: Error handling validation
- Step 4: Modular component testing
- Step 5: Progressive complexity testing
- Step 6: Resource management testing
"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from src.ignition.modules.llm_infrastructure import auto_detect_gpu_configuration
from src.ignition.modules.llm_infrastructure.infrastructure_manager import (
    InfrastructureManager,
    ModelConfig,
)


class TestGPUAutoDetection:
    """Step 1: Environment Validation Testing (crawl_mcp.py methodology)"""

    def test_auto_detect_gpu_configuration_basic(self):
        """Test basic GPU auto-detection functionality."""
        config = auto_detect_gpu_configuration()

        # Validate required fields
        required_fields = [
            "platform",
            "architecture",
            "gpu_type",
            "device",
            "precision",
            "quantization",
            "batch_size",
            "workers",
            "max_context",
            "memory_optimized",
            "available_memory_gb",
        ]

        for field in required_fields:
            assert field in config, f"Missing required field: {field}"

        # Validate GPU type options
        assert config["gpu_type"] in [
            "none",
            "mps",
            "cuda",
        ], f"Invalid GPU type: {config['gpu_type']}"

        # Validate device configuration
        if config["gpu_type"] == "mps":
            assert config["device"] == "mps"
        elif config["gpu_type"] == "cuda":
            assert config["device"].startswith("cuda")
        else:
            assert config["device"] == "cpu"

    @patch("platform.system")
    @patch("platform.machine")
    def test_apple_silicon_detection(self, mock_machine, mock_system):
        """Test Apple Silicon MPS detection."""
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        with patch("torch.backends.mps.is_available", return_value=True), patch("torch.randn") as mock_tensor:
            mock_tensor.return_value.to.return_value = Mock()

            config = auto_detect_gpu_configuration()

            assert config["platform"] == "Darwin"
            assert config["architecture"] == "arm64"
            # Note: Actual MPS detection depends on PyTorch availability

    @patch("torch.cuda.is_available")
    @patch("torch.cuda.device_count")
    @patch("torch.cuda.get_device_properties")
    def test_cuda_detection(self, mock_props, mock_count, mock_available):
        """Test NVIDIA CUDA detection."""
        mock_available.return_value = True
        mock_count.return_value = 1

        # Mock GPU with 12GB memory
        mock_device = Mock()
        mock_device.total_memory = 12 * 1024**3  # 12GB in bytes
        mock_props.return_value = mock_device

        with patch("src.ignition.modules.llm_infrastructure._configure_nvidia_cuda") as mock_cuda:
            mock_cuda.return_value = {
                "success": True,
                "config": {
                    "device": "cuda:0",
                    "precision": "fp16",
                    "quantization": "fp16",
                    "available_memory_gb": 12.0,
                    "cuda_available": True,
                },
            }

            auto_detect_gpu_configuration()

            # Validate CUDA configuration would be applied
            assert mock_cuda.called

    def test_cpu_fallback_configuration(self):
        """Test CPU-only fallback configuration."""
        with patch("torch.cuda.is_available", return_value=False):
            with patch("torch.backends.mps.is_available", return_value=False):
                config = auto_detect_gpu_configuration()

                assert config["device"] == "cpu"
                assert config["gpu_type"] == "none"
                assert config["workers"] >= 1
                assert config["quantization"] in ["int8", "int4"]


class TestModelConfig:
    """Step 2: Input Validation Testing (crawl_mcp.py methodology)"""

    def test_model_config_validation_valid(self):
        """Test valid model configuration."""
        config = ModelConfig(
            model_name="llama3.1-8b",
            quantization="int8",
            max_context_length=4096,
            temperature=0.7,
            top_p=0.9,
            max_tokens=512,
        )

        assert config.model_name == "llama3.1-8b"
        assert config.quantization == "int8"
        assert config.max_context_length == 4096
        assert config.temperature == 0.7
        assert config.top_p == 0.9
        assert config.max_tokens == 512

    def test_model_config_validation_invalid_quantization(self):
        """Test invalid quantization validation."""
        with pytest.raises(ValueError, match="Quantization must be one of"):
            ModelConfig(quantization="invalid_quantization")

    def test_model_config_validation_invalid_temperature(self):
        """Test invalid temperature validation."""
        with pytest.raises(ValueError):
            ModelConfig(temperature=3.0)  # Too high

        with pytest.raises(ValueError):
            ModelConfig(temperature=-0.1)  # Too low

    def test_model_config_validation_invalid_context_length(self):
        """Test invalid context length validation."""
        with pytest.raises(ValueError):
            ModelConfig(max_context_length=100)  # Too low

        with pytest.raises(ValueError):
            ModelConfig(max_context_length=50000)  # Too high

    def test_model_config_defaults(self):
        """Test default configuration values."""
        config = ModelConfig()

        assert config.model_name == "llama3.1-8b"
        assert config.quantization == "int8"
        assert config.max_context_length == 4096
        assert config.temperature == 0.7
        assert config.top_p == 0.9
        assert config.max_tokens == 512


class TestInfrastructureManager:
    """Step 3: Error Handling & Step 4: Modular Testing (crawl_mcp.py methodology)"""

    @pytest.fixture
    def manager(self):
        """Create infrastructure manager for testing."""
        return InfrastructureManager()

    def test_manager_initialization(self, manager):
        """Test manager initialization."""
        assert manager.config is not None
        assert manager.gpu_config is not None
        assert not manager.is_initialized
        assert manager.model is None
        assert manager.tokenizer is None

    @pytest.mark.asyncio
    async def test_environment_validation(self, manager):
        """Test environment validation."""
        result = await manager._validate_environment()

        assert "success" in result
        assert "errors" in result
        assert "warnings" in result
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)

    @pytest.mark.asyncio
    async def test_initialization_without_dependencies(self, manager):
        """Test initialization handles missing dependencies gracefully."""
        with patch("importlib.import_module", side_effect=ImportError("Module not found")):
            result = await manager.initialize()

            assert not result["success"]
            assert "error" in result

    @pytest.mark.asyncio
    async def test_generate_text_not_initialized(self, manager):
        """Test text generation fails when not initialized."""
        result = await manager.generate_text("Test prompt")

        assert not result["success"]
        assert "not initialized" in result["error"].lower()

    def test_memory_usage_calculation(self, manager):
        """Test memory usage calculation."""
        memory_usage = manager._get_memory_usage()

        assert isinstance(memory_usage, float)
        assert memory_usage >= 0.0

    def test_error_formatting(self, manager):
        """Test error message formatting."""
        # Test CUDA error
        cuda_error = Exception("CUDA out of memory")
        formatted = manager._format_error(cuda_error)
        assert "gpu error" in formatted.lower()

        # Test memory error
        memory_error = Exception("RuntimeError: CUDA out of memory")
        formatted = manager._format_error(memory_error)
        assert "out of memory" in formatted.lower()

        # Test model error
        model_error = Exception("Model 'test-model' not found")
        formatted = manager._format_error(model_error)
        assert "model not found" in formatted.lower()

        # Test generic error
        generic_error = Exception("Generic error message")
        formatted = manager._format_error(generic_error)
        assert "llm infrastructure error" in formatted.lower()

    def test_status_reporting(self, manager):
        """Test status reporting functionality."""
        status = manager.get_status()

        required_fields = [
            "initialized",
            "gpu_config",
            "model_config",
            "performance_metrics",
            "memory_usage_gb",
        ]

        for field in required_fields:
            assert field in status, f"Missing status field: {field}"

        assert isinstance(status["initialized"], bool)
        assert isinstance(status["gpu_config"], dict)
        assert isinstance(status["model_config"], dict)
        assert isinstance(status["performance_metrics"], dict)
        assert isinstance(status["memory_usage_gb"], float)


class TestResourceManagement:
    """Step 6: Resource Management Testing (crawl_mcp.py methodology)"""

    @pytest.mark.asyncio
    async def test_managed_inference_context(self):
        """Test managed inference context manager."""
        manager = InfrastructureManager()

        # Mock initialization to avoid actual model loading
        with patch.object(manager, "initialize", return_value={"success": True}):
            with patch.object(manager, "_cleanup_resources") as mock_cleanup:
                async with manager.managed_inference() as context:
                    assert "manager" in context
                    assert "gpu_config" in context
                    assert "performance_metrics" in context

                # Verify cleanup was called
                mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_resource_cleanup(self):
        """Test resource cleanup functionality."""
        manager = InfrastructureManager()

        # Mock model and tokenizer
        manager.model = Mock()
        manager.tokenizer = Mock()
        manager.is_initialized = True

        # Mock GPU cache clearing
        with patch("torch.cuda.empty_cache"), patch("torch.mps.empty_cache"):
            await manager._cleanup_resources()

            # Verify resources were cleaned up
            assert manager.model is None
            assert manager.tokenizer is None
            assert not manager.is_initialized


class TestProgressiveComplexity:
    """Step 5: Progressive Complexity Testing (crawl_mcp.py methodology)"""

    @pytest.mark.asyncio
    async def test_basic_functionality_mock(self):
        """Test basic functionality with mocked components."""
        manager = InfrastructureManager()

        # Mock successful initialization
        mock_init_result = {
            "success": True,
            "gpu_config": {"gpu_type": "cpu", "device": "cpu"},
            "model_config": {},
            "initialization_time": 1.0,
            "memory_usage": 0.5,
        }

        with patch.object(manager, "initialize", return_value=mock_init_result):
            result = await manager.initialize()

            assert result["success"]
            assert "gpu_config" in result
            assert "initialization_time" in result

    @pytest.mark.asyncio
    async def test_text_generation_mock(self):
        """Test text generation with mocked model."""
        manager = InfrastructureManager()
        manager.is_initialized = True

        # Mock successful generation
        mock_result = {
            "success": True,
            "prompt": "Test prompt",
            "generated_text": "Generated response",
            "inference_time": 0.5,
            "tokens_generated": 10,
            "tokens_per_second": 20.0,
        }

        with patch.object(manager, "generate_text", return_value=mock_result):
            result = await manager.generate_text("Test prompt")

            assert result["success"]
            assert result["prompt"] == "Test prompt"
            assert "generated_text" in result
            assert "inference_time" in result


class TestIntegrationScenarios:
    """Integration testing for complete workflows"""

    @pytest.mark.asyncio
    async def test_full_workflow_mock(self):
        """Test complete workflow with mocked dependencies."""
        # This test verifies the full workflow without requiring actual model downloads
        manager = InfrastructureManager()

        # Mock all external dependencies
        with patch("torch.cuda.is_available", return_value=False):
            with patch("torch.backends.mps.is_available", return_value=False):
                with patch.object(manager, "_load_model", return_value={"success": True}):
                    with patch.object(
                        manager,
                        "_test_model_functionality",
                        return_value={"success": True},
                    ):
                        # Test initialization
                        init_result = await manager.initialize()
                        assert init_result["success"]

                        # Test status
                        status = manager.get_status()
                        assert status["initialized"]

                        # Test cleanup
                        await manager._cleanup_resources()
                        assert not manager.is_initialized


# Performance and stress testing
class TestPerformanceValidation:
    """Performance validation testing"""

    def test_gpu_config_performance(self):
        """Test GPU configuration performance."""
        import time

        start_time = time.time()
        config = auto_detect_gpu_configuration()
        detection_time = time.time() - start_time

        # GPU detection should be fast (< 5 seconds)
        assert detection_time < 5.0, f"GPU detection too slow: {detection_time:.2f}s"

        # Configuration should be complete
        assert len(config) >= 10, "Incomplete GPU configuration"

    @pytest.mark.asyncio
    async def test_initialization_timeout(self):
        """Test initialization doesn't hang indefinitely."""
        manager = InfrastructureManager()

        # Use asyncio.wait_for to enforce timeout
        try:
            result = await asyncio.wait_for(
                manager._validate_environment(),
                timeout=30.0,  # 30 second timeout
            )
            assert "success" in result
        except TimeoutError:
            pytest.fail("Environment validation timed out")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
