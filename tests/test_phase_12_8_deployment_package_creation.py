"""Tests for Phase 12.8: Deployment Package Creation & How-to Guides

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Input validation and sanitization using Pydantic models
- Step 3: Comprehensive error handling with user-friendly messages
- Step 4: Modular testing integration
- Step 5: Progressive complexity
- Step 6: Resource management
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import the Phase 12.8 implementation
from src.phase_12_8_deployment_package_creation import (
    DeploymentPackageCreator,
    DeploymentTarget,
    DockerPackageConfig,
    PackageCreationRequest,
    PackageType,
    StandalonePackageConfig,
    create_docker_package,
    create_standalone_package,
    format_deployment_error,
    generate_comprehensive_guides,
    run_phase_12_8_implementation,
    validate_deployment_environment,
)


class TestPhase128DeploymentPackageCreation:
    """Test suite for Phase 12.8 deployment package creation."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp(prefix="test_phase_12_8_")
        yield temp_dir
        # Cleanup
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_docker_client(self):
        """Mock Docker client for testing."""
        mock_client = Mock()
        mock_client.ping.return_value = True

        # Mock image build
        mock_image = Mock()
        mock_image.attrs = {"Size": 1024}
        mock_image.save.return_value = [b"mock_image_data"]

        mock_client.images.build.return_value = (
            mock_image,
            [
                {"stream": "Step 1/5 : FROM python:3.12-slim\n"},
                {"stream": "Successfully built abc123\n"},
            ],
        )

        return mock_client

    # Step 1: Environment Validation Tests
    def test_validate_deployment_environment_success(self):
        """Test successful environment validation."""
        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda tool: (f"/usr/bin/{tool}" if tool in ["docker", "git", "python3"] else None)

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(stdout="Python 3.12.0", returncode=0)

                with patch("docker.from_env") as mock_docker:
                    mock_docker.return_value.ping.return_value = True

                    result = validate_deployment_environment()

                    assert result["valid"] is True
                    assert len(result["errors"]) == 0
                    assert "docker" in result["tools_available"]
                    assert "git" in result["tools_available"]
                    assert "python3" in result["tools_available"]

    def test_validate_deployment_environment_missing_tools(self):
        """Test environment validation with missing tools."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None  # No tools found

            result = validate_deployment_environment()

            assert result["valid"] is False
            assert len(result["errors"]) > 0
            assert any("Required tool not found" in error for error in result["errors"])

    def test_validate_deployment_environment_docker_unavailable(self):
        """Test environment validation with Docker unavailable."""
        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda tool: (f"/usr/bin/{tool}" if tool in ["git", "python3"] else None)

            with patch("docker.from_env") as mock_docker:
                mock_docker.side_effect = Exception("Docker not available")

                result = validate_deployment_environment()

                assert result["valid"] is False
                assert any("Docker daemon not accessible" in error for error in result["errors"])

    # Step 2: Input Validation Tests
    def test_docker_package_config_validation(self):
        """Test Docker package configuration validation."""
        # Valid configuration
        config = DockerPackageConfig(image_name="test-app", tag="1.0.0", expose_ports=[8000, 8501])
        assert config.image_name == "test-app"
        assert config.tag == "1.0.0"
        assert config.expose_ports == [8000, 8501]

        # Invalid image name with spaces
        with pytest.raises(ValueError, match="Image name cannot contain spaces"):
            DockerPackageConfig(image_name="test app")

        # Empty image name
        with pytest.raises(ValueError, match="Image name cannot be empty"):
            DockerPackageConfig(image_name="")

    def test_standalone_package_config_validation(self):
        """Test standalone package configuration validation."""
        # Valid configuration
        config = StandalonePackageConfig(service_name="test-service", install_path="/opt/test-service")
        assert config.service_name == "test-service"
        assert config.install_path == "/opt/test-service"

        # Invalid install path (not absolute)
        with pytest.raises(ValueError, match="Install path must be absolute"):
            StandalonePackageConfig(install_path="relative/path")

    def test_package_creation_request_validation(self):
        """Test package creation request validation."""
        # Valid request
        request = PackageCreationRequest(
            package_type=PackageType.DOCKER,
            deployment_target=DeploymentTarget.PRODUCTION,
            version="1.0.0",
        )
        assert request.package_type == PackageType.DOCKER
        assert request.deployment_target == DeploymentTarget.PRODUCTION
        assert request.version == "1.0.0"

        # Invalid version format
        with pytest.raises(ValueError, match="Version must be in format X.Y.Z"):
            PackageCreationRequest(
                package_type=PackageType.DOCKER,
                deployment_target=DeploymentTarget.PRODUCTION,
                version="1.0",
            )

        # Invalid version with non-numeric parts
        with pytest.raises(ValueError, match="Version parts must be numeric"):
            PackageCreationRequest(
                package_type=PackageType.DOCKER,
                deployment_target=DeploymentTarget.PRODUCTION,
                version="1.0.beta",
            )

    # Step 3: Error Handling Tests
    def test_format_deployment_error(self):
        """Test deployment error formatting."""
        # Docker permission error
        docker_error = Exception("permission denied while trying to connect to the Docker daemon")
        formatted = format_deployment_error(docker_error, "Docker operation")
        assert "Docker permission denied" in formatted
        assert "sudo usermod -aG docker" in formatted

        # Docker daemon error
        daemon_error = Exception("Cannot connect to the Docker daemon")
        formatted = format_deployment_error(daemon_error, "Docker connection")
        assert "Docker daemon not running" in formatted
        assert "sudo systemctl start docker" in formatted

        # Git error
        git_error = Exception("fatal: not a git repository")
        formatted = format_deployment_error(git_error, "Git operation")
        assert "Git error in Git operation" in formatted

        # Generic error
        generic_error = Exception("Something went wrong")
        formatted = format_deployment_error(generic_error, "test operation")
        assert "Error in test operation: Something went wrong" in formatted

    # Step 4: Modular Testing
    @pytest.mark.asyncio
    async def test_deployment_package_creator_initialization(self):
        """Test deployment package creator initialization."""
        creator = DeploymentPackageCreator()

        with patch("src.phase_12_8_deployment_package_creation.validate_deployment_environment") as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "tools_available": ["docker", "git", "python3"],
            }

            with patch("docker.from_env") as mock_docker:
                mock_docker.return_value.ping.return_value = True

                result = await creator.initialize()

                assert result["success"] is True
                assert "Package creator initialized successfully" in result["message"]
                assert creator._is_initialized is True

    @pytest.mark.asyncio
    async def test_deployment_package_creator_initialization_failure(self):
        """Test deployment package creator initialization failure."""
        creator = DeploymentPackageCreator()

        with patch("src.phase_12_8_deployment_package_creation.validate_deployment_environment") as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "errors": ["Docker not available"],
                "warnings": [],
                "tools_available": [],
            }

            result = await creator.initialize()

            assert result["success"] is False
            assert "Environment validation failed" in result["error"]
            assert creator._is_initialized is False

    @pytest.mark.asyncio
    async def test_create_docker_package_success(self, temp_dir, mock_docker_client):
        """Test successful Docker package creation."""
        with (
            patch("docker.from_env", return_value=mock_docker_client),
            patch("src.phase_12_8_deployment_package_creation.validate_deployment_environment") as mock_validate,
        ):
            mock_validate.return_value = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "tools_available": ["docker", "git", "python3"],
            }

            # Create mock project structure
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()
            (src_dir / "__init__.py").touch()

            templates_dir = Path(temp_dir) / "templates"
            templates_dir.mkdir()

            (Path(temp_dir) / "requirements.txt").write_text("fastapi>=0.104.0\n")
            (Path(temp_dir) / "pyproject.toml").write_text("[tool.poetry]\nname = 'ign-scripts'\n")
            (Path(temp_dir) / "README.md").write_text("# IGN Scripts\n")

            # Change to temp directory for the test
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                result = await create_docker_package(
                    image_name="test-app",
                    version="1.0.0",
                    deployment_target="production",
                    output_dir=str(Path(temp_dir) / "dist"),
                )

                assert result.success is True
                assert result.package_path is not None
                assert "test-app-1.0.0-docker" in result.package_path

            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_create_standalone_package_success(self, temp_dir):
        """Test successful standalone package creation."""
        with patch("src.phase_12_8_deployment_package_creation.validate_deployment_environment") as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "tools_available": ["git", "python3"],
            }

            # Create mock project structure
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()
            (src_dir / "__init__.py").touch()

            templates_dir = Path(temp_dir) / "templates"
            templates_dir.mkdir()

            (Path(temp_dir) / "requirements.txt").write_text("fastapi>=0.104.0\n")
            (Path(temp_dir) / "pyproject.toml").write_text("[tool.poetry]\nname = 'ign-scripts'\n")
            (Path(temp_dir) / "README.md").write_text("# IGN Scripts\n")

            # Change to temp directory for the test
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                result = await create_standalone_package(
                    version="1.0.0",
                    deployment_target="production",
                    output_dir=str(Path(temp_dir) / "dist"),
                )

                assert result.success is True
                assert result.package_path is not None
                assert "ign-scripts-1.0.0-standalone" in result.package_path

            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_create_package_without_initialization(self):
        """Test package creation without initialization."""
        creator = DeploymentPackageCreator()

        request = PackageCreationRequest(
            package_type=PackageType.DOCKER,
            deployment_target=DeploymentTarget.PRODUCTION,
            version="1.0.0",
        )

        result = await creator.create_package(request)

        assert result.success is False
        assert "Package creator not initialized" in result.error_message

    # Step 5: Progressive Complexity Tests
    @pytest.mark.asyncio
    async def test_generate_comprehensive_guides(self, temp_dir):
        """Test comprehensive guides generation."""
        # Change to temp directory for the test
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            result = await generate_comprehensive_guides()

            assert result["success"] is True
            assert len(result["guides"]) == 5
            assert "installation-guide.md" in result["guides"]
            assert "deployment-guide.md" in result["guides"]
            assert "operations-guide.md" in result["guides"]
            assert "troubleshooting-guide.md" in result["guides"]
            assert "security-guide.md" in result["guides"]

            # Verify guides were actually created
            guides_dir = Path("docs/how-to")
            assert guides_dir.exists()
            assert (guides_dir / "installation-guide.md").exists()
            assert (guides_dir / "deployment-guide.md").exists()
            assert (guides_dir / "operations-guide.md").exists()
            assert (guides_dir / "troubleshooting-guide.md").exists()
            assert (guides_dir / "security-guide.md").exists()

        finally:
            os.chdir(original_cwd)

    # Step 6: Resource Management Tests
    @pytest.mark.asyncio
    async def test_managed_creation_context_manager(self):
        """Test managed creation context manager."""
        creator = DeploymentPackageCreator()

        with patch("src.phase_12_8_deployment_package_creation.validate_deployment_environment") as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "tools_available": ["docker", "git", "python3"],
            }

            with patch("docker.from_env") as mock_docker:
                mock_docker.return_value.ping.return_value = True

                async with creator.managed_creation() as managed_creator:
                    assert managed_creator._is_initialized is True

                # Verify cleanup was called
                assert len(creator._temp_dirs) == 0

    @pytest.mark.asyncio
    async def test_managed_creation_cleanup_on_exception(self):
        """Test managed creation cleanup on exception."""
        creator = DeploymentPackageCreator()

        with patch("src.phase_12_8_deployment_package_creation.validate_deployment_environment") as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "tools_available": ["docker", "git", "python3"],
            }

            with patch("docker.from_env") as mock_docker:
                mock_docker.return_value.ping.return_value = True

                try:
                    async with creator.managed_creation():
                        # Add a temp directory
                        temp_dir = tempfile.mkdtemp()
                        creator._temp_dirs.append(temp_dir)
                        raise Exception("Test exception")
                except Exception:
                    pass

                # Verify cleanup was still called
                assert len(creator._temp_dirs) == 0

    # Integration Tests
    @pytest.mark.asyncio
    async def test_run_phase_12_8_implementation_success(self, temp_dir):
        """Test full Phase 12.8 implementation."""
        with patch("src.phase_12_8_deployment_package_creation.validate_deployment_environment") as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "tools_available": ["docker", "git", "python3"],
            }

            with patch("docker.from_env") as mock_docker:
                mock_client = Mock()
                mock_client.ping.return_value = True
                mock_docker.return_value = mock_client

                # Create mock project structure
                src_dir = Path(temp_dir) / "src"
                src_dir.mkdir()
                (src_dir / "__init__.py").touch()

                templates_dir = Path(temp_dir) / "templates"
                templates_dir.mkdir()

                (Path(temp_dir) / "requirements.txt").write_text("fastapi>=0.104.0\n")
                (Path(temp_dir) / "pyproject.toml").write_text("[tool.poetry]\nname = 'ign-scripts'\n")
                (Path(temp_dir) / "README.md").write_text("# IGN Scripts\n")

                # Change to temp directory for the test
                original_cwd = os.getcwd()
                try:
                    os.chdir(temp_dir)

                    result = await run_phase_12_8_implementation()

                    assert result["success"] is True
                    assert result["phase"] == "12.8"
                    assert "Deployment Package Creation & How-to Guides" in result["title"]
                    assert len(result["documentation_generated"]) > 0

                finally:
                    os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_run_phase_12_8_implementation_environment_failure(self):
        """Test Phase 12.8 implementation with environment failure."""
        with patch("src.phase_12_8_deployment_package_creation.validate_deployment_environment") as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "errors": ["Docker not available", "Git not found"],
                "warnings": [],
                "tools_available": [],
            }

            result = await run_phase_12_8_implementation()

            assert result["success"] is False
            assert len(result["errors"]) > 0
            assert "Environment validation failed" in result["errors"]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
