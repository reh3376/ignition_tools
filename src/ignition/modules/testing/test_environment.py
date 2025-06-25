"""Test Environment Management for Ignition Module Testing.

Provides Docker-based and local test environments following patterns from
crawl_mcp.py for validation, error handling, and resource management.
"""

import asyncio
import os
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import docker
import docker.errors
import docker.models.containers
import docker.models.networks
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TestEnvironmentStatus(Enum):
    """Status of test environment."""

    NOT_INITIALIZED = "not_initialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class TestEnvironmentConfig:
    """Configuration for test environment."""

    ignition_version: str
    gateway_url: str
    docker_image: str = "inductiveautomation/ignition:latest"
    gateway_port: int = 8088
    designer_port: int = 8043
    mqtt_port: int = 1883
    opc_port: int = 62541
    memory_limit: str = "2g"
    cpu_limit: str = "2.0"
    timeout: int = 300
    environment_vars: dict[str, str] = field(default_factory=dict)
    volumes: dict[str, str] = field(default_factory=dict)
    network_name: str | None = None


def validate_test_environment_config() -> dict[str, Any]:
    """Validate test environment configuration.

    Following patterns from crawl_mcp.py for environment validation.

    Returns:
        Dictionary with validation results
    """
    required_vars = {
        "IGNITION_TEST_VERSION": "Ignition version for testing",
        "TEST_GATEWAY_URL": "Test Gateway URL",
    }

    optional_vars = {
        "DOCKER_TEST_IMAGE": "Docker image for testing",
        "TEST_GATEWAY_PORT": "Gateway port",
        "TEST_DESIGNER_PORT": "Designer port",
        "TEST_TIMEOUT": "Test timeout in seconds",
        "TEST_CONTAINER_MEMORY": "Container memory limit",
        "TEST_CONTAINER_CPU": "Container CPU limit",
    }

    missing_required = []
    available_vars = {}

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = value
        else:
            missing_required.append(f"{var} ({description})")

    for var, _description in optional_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = value

    if missing_required:
        return {
            "valid": False,
            "error": f"Missing required environment variables: {', '.join(missing_required)}",
            "available": available_vars,
        }

    return {"valid": True, "variables": available_vars}


def format_docker_error(error: Exception) -> str:
    """Format Docker errors for user-friendly messages.

    Following patterns from crawl_mcp.py for error formatting.

    Args:
        error: The exception to format

    Returns:
        Formatted error message
    """
    error_str = str(error).lower()

    if "permission denied" in error_str:
        return "Docker permission denied. Add user to docker group or run with sudo."
    elif "connection refused" in error_str or "daemon" in error_str:
        return "Docker daemon not running. Start Docker service and try again."
    elif "no such image" in error_str:
        return "Docker image not found. Check image name and availability."
    elif "port" in error_str and "already" in error_str:
        return (
            "Port already in use. Stop other containers or change port configuration."
        )
    elif "memory" in error_str or "resources" in error_str:
        return "Insufficient system resources. Free up memory and try again."
    else:
        return f"Docker error: {error!s}"


class TestEnvironment:
    """Base class for test environments.

    Following patterns from crawl_mcp.py for context management
    and resource cleanup.
    """

    def __init__(self, config: TestEnvironmentConfig):
        """Initialize test environment.

        Args:
            config: Test environment configuration
        """
        self.config = config
        self.status = TestEnvironmentStatus.NOT_INITIALIZED
        self.temp_dir: Path | None = None

    @asynccontextmanager
    async def environment_context(self) -> AsyncIterator["TestEnvironment"]:
        """Create environment context with resource management.

        Yields:
            TestEnvironment instance
        """
        try:
            await self.initialize()
            yield self
        finally:
            await self.cleanup()

    async def initialize(self) -> None:
        """Initialize the test environment."""
        self.status = TestEnvironmentStatus.INITIALIZING

        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ignition_test_"))

        self.status = TestEnvironmentStatus.READY

    async def start(self) -> None:
        """Start the test environment."""
        if self.status != TestEnvironmentStatus.READY:
            raise RuntimeError(f"Environment not ready, status: {self.status}")

        self.status = TestEnvironmentStatus.RUNNING

    async def stop(self) -> None:
        """Stop the test environment."""
        self.status = TestEnvironmentStatus.STOPPING
        self.status = TestEnvironmentStatus.STOPPED

    async def cleanup(self) -> None:
        """Clean up test environment resources."""
        await self.stop()

        # Clean up temporary directory
        if self.temp_dir and self.temp_dir.exists():
            import shutil

            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

    def get_status(self) -> TestEnvironmentStatus:
        """Get current environment status."""
        return self.status

    def is_ready(self) -> bool:
        """Check if environment is ready for testing."""
        return self.status == TestEnvironmentStatus.RUNNING


class DockerTestEnvironment(TestEnvironment):
    """Docker-based test environment for Ignition modules.

    Following patterns from crawl_mcp.py for Docker integration
    and error handling.
    """

    def __init__(self, config: TestEnvironmentConfig):
        """Initialize Docker test environment.

        Args:
            config: Test environment configuration
        """
        super().__init__(config)
        self.docker_client: docker.DockerClient | None = None
        self.container: docker.models.containers.Container | None = None
        self.network: docker.models.networks.Network | None = None

    def _check_docker_available(self) -> bool:
        """Check if Docker is available.

        Following patterns from crawl_mcp.py for availability checks.

        Returns:
            True if Docker is available
        """
        try:
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False

    async def initialize(self) -> None:
        """Initialize Docker test environment."""
        await super().initialize()

        if not self._check_docker_available():
            self.status = TestEnvironmentStatus.ERROR
            raise RuntimeError("Docker is not available")

        try:
            self.docker_client = docker.from_env()

            # Create network if specified
            if self.config.network_name:
                try:
                    self.network = self.docker_client.networks.get(
                        self.config.network_name
                    )
                except docker.errors.NotFound:
                    self.network = self.docker_client.networks.create(
                        self.config.network_name
                    )

        except Exception as e:
            self.status = TestEnvironmentStatus.ERROR
            raise RuntimeError(format_docker_error(e)) from e

    async def start(self) -> None:
        """Start Docker container."""
        await super().start()

        if not self.docker_client:
            raise RuntimeError("Docker client not initialized")

        try:
            # Pull image if not available
            try:
                self.docker_client.images.get(self.config.docker_image)
            except docker.errors.ImageNotFound:
                print(f"Pulling Docker image: {self.config.docker_image}")
                self.docker_client.images.pull(self.config.docker_image)

            # Prepare container configuration
            container_config = {
                "image": self.config.docker_image,
                "ports": {
                    f"{self.config.gateway_port}/tcp": self.config.gateway_port,
                    f"{self.config.designer_port}/tcp": self.config.designer_port,
                    f"{self.config.mqtt_port}/tcp": self.config.mqtt_port,
                    f"{self.config.opc_port}/tcp": self.config.opc_port,
                },
                "environment": self.config.environment_vars,
                "volumes": self.config.volumes,
                "mem_limit": self.config.memory_limit,
                "cpu_period": 100000,
                "cpu_quota": int(float(self.config.cpu_limit) * 100000),
                "detach": True,
                "remove": True,
            }

            if self.network:
                container_config["network"] = self.network.name

            # Start container
            self.container = self.docker_client.containers.run(**container_config)

            # Wait for container to be ready
            await self._wait_for_container_ready()

        except Exception as e:
            self.status = TestEnvironmentStatus.ERROR
            raise RuntimeError(format_docker_error(e)) from e

    async def _wait_for_container_ready(self) -> None:
        """Wait for container to be ready."""
        if not self.container:
            return

        max_wait = self.config.timeout
        wait_interval = 5
        waited = 0

        while waited < max_wait:
            try:
                self.container.reload()
                if self.container.status == "running":
                    # Additional check for Ignition Gateway availability
                    import aiohttp

                    async with aiohttp.ClientSession() as session:
                        try:
                            async with session.get(
                                f"{self.config.gateway_url}/StatusPing",
                                timeout=aiohttp.ClientTimeout(total=10),
                            ) as response:
                                if response.status == 200:
                                    return
                        except (aiohttp.ClientError, TimeoutError):
                            pass

                await asyncio.sleep(wait_interval)
                waited += wait_interval

            except Exception:
                await asyncio.sleep(wait_interval)
                waited += wait_interval

        raise RuntimeError(f"Container not ready after {max_wait} seconds")

    async def stop(self) -> None:
        """Stop Docker container."""
        await super().stop()

        if self.container:
            try:
                self.container.stop(timeout=30)
                self.container = None
            except Exception as e:
                print(f"Warning: Error stopping container: {e}")

    async def cleanup(self) -> None:
        """Clean up Docker resources."""
        await super().cleanup()

        # Clean up network if created
        if self.network and self.config.network_name:
            try:
                self.network.remove()
                self.network = None
            except Exception as e:
                print(f"Warning: Error removing network: {e}")

        if self.docker_client:
            self.docker_client.close()
            self.docker_client = None

    def get_container_logs(self) -> str:
        """Get container logs."""
        if not self.container:
            return "No container available"

        try:
            logs = self.container.logs(tail=100)
            return cast("str", logs.decode("utf-8"))
        except Exception as e:
            return f"Error getting logs: {e}"

    def execute_command(self, command: str) -> tuple[int, str]:
        """Execute command in container.

        Args:
            command: Command to execute

        Returns:
            tuple of (exit_code, output)
        """
        if not self.container:
            return 1, "No container available"

        try:
            result = self.container.exec_run(command)
            return result.exit_code, result.output.decode("utf-8")
        except Exception as e:
            return 1, f"Error executing command: {e}"


class TestEnvironmentManager:
    """Manager for test environments.

    Following patterns from crawl_mcp.py for resource management
    and configuration.
    """

    def __init__(self) -> Any:
        """Initialize test environment manager."""
        self.environments: dict[str, TestEnvironment] = {}
        self.config = self._load_config()

    def _load_config(self) -> TestEnvironmentConfig:
        """Load configuration from environment variables."""
        return TestEnvironmentConfig(
            ignition_version=os.getenv("IGNITION_TEST_VERSION", "8.1.0"),
            gateway_url=os.getenv("TEST_GATEWAY_URL", "http://localhost:8088"),
            docker_image=os.getenv(
                "DOCKER_TEST_IMAGE", "inductiveautomation/ignition:latest"
            ),
            gateway_port=int(os.getenv("TEST_GATEWAY_PORT", "8088")),
            designer_port=int(os.getenv("TEST_DESIGNER_PORT", "8043")),
            mqtt_port=int(os.getenv("TEST_MQTT_PORT", "1883")),
            opc_port=int(os.getenv("TEST_OPC_PORT", "62541")),
            memory_limit=os.getenv("TEST_CONTAINER_MEMORY", "2g"),
            cpu_limit=os.getenv("TEST_CONTAINER_CPU", "2.0"),
            timeout=int(os.getenv("TEST_TIMEOUT", "300")),
        )

    async def create_environment(
        self,
        name: str,
        environment_type: str = "docker",
        config_override: dict[str, Any] | None = None,
    ) -> TestEnvironment:
        """Create a test environment.

        Args:
            name: Name for the environment
            environment_type: Type of environment ("docker" or "local")
            config_override: Configuration overrides

        Returns:
            TestEnvironment instance
        """
        # Apply config overrides
        config = self.config
        if config_override:
            for key, value in config_override.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        environment = (
            DockerTestEnvironment(config)
            if environment_type == "docker"
            else TestEnvironment(config)
        )

        self.environments[name] = environment
        return environment

    async def get_environment(self, name: str) -> TestEnvironment | None:
        """Get existing test environment.

        Args:
            name: Name of the environment

        Returns:
            TestEnvironment instance or None
        """
        return self.environments.get(name)

    async def cleanup_all(self) -> None:
        """Clean up all test environments."""
        for environment in self.environments.values():
            await environment.cleanup()
        self.environments.clear()

    def list_environments(self) -> dict[str, TestEnvironmentStatus]:
        """List all environments and their status.

        Returns:
            Dictionary mapping environment names to status
        """
        return {name: env.get_status() for name, env in self.environments.items()}
