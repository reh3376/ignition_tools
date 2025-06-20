"""Test Environment Management for Module Testing.

This module provides comprehensive test environment management,
including Docker-based testing environments and local testing setups.
Following patterns from crawl_mcp.py for robust environment handling.
"""

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class TestEnvironmentConfig:
    """Configuration for test environments."""

    ignition_version: str = "8.1.0"
    gateway_port: int = 8088
    designer_port: int = 8043
    docker_enabled: bool = False
    test_timeout: int = 300
    environment_variables: dict[str, str] = field(default_factory=dict)
    volume_mounts: list[str] = field(default_factory=list)


@dataclass
class TestEnvironmentStatus:
    """Status information for test environments."""

    name: str
    type: str  # "docker" or "local"
    status: str  # "running", "stopped", "error"
    gateway_url: str | None = None
    designer_url: str | None = None
    container_id: str | None = None
    error_message: str | None = None


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
        "DOCKER_TEST_ENABLED": "Enable Docker-based testing",
        "TEST_TIMEOUT": "Test timeout in seconds",
        "IGNITION_DOCKER_IMAGE": "Docker image for Ignition testing",
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


class TestEnvironment:
    """Base class for test environments."""

    def __init__(self, config: TestEnvironmentConfig):
        """Initialize the test environment.

        Args:
            config: Test environment configuration
        """
        self.config = config
        self.status = TestEnvironmentStatus(name="base", type="base", status="stopped")

    async def start(self) -> bool:
        """Start the test environment.

        Returns:
            True if started successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement start()")

    async def stop(self) -> bool:
        """Stop the test environment.

        Returns:
            True if stopped successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement stop()")

    async def is_ready(self) -> bool:
        """Check if the test environment is ready for testing.

        Returns:
            True if ready, False otherwise
        """
        raise NotImplementedError("Subclasses must implement is_ready()")

    def get_status(self) -> TestEnvironmentStatus:
        """Get the current status of the test environment.

        Returns:
            TestEnvironmentStatus with current status information
        """
        return self.status


class DockerTestEnvironment(TestEnvironment):
    """Docker-based test environment for comprehensive module testing.

    Following patterns from crawl_mcp.py for Docker integration and management.
    """

    def __init__(self, config: TestEnvironmentConfig):
        """Initialize the Docker test environment.

        Args:
            config: Test environment configuration
        """
        super().__init__(config)
        self.status.name = "docker-ignition"
        self.status.type = "docker"

        # Docker configuration
        self.docker_image = os.getenv(
            "IGNITION_DOCKER_IMAGE", "inductiveautomation/ignition:latest"
        )
        self.container_name = f"ignition-test-{self.config.ignition_version}"

    async def start(self) -> bool:
        """Start the Docker test environment.

        Following patterns from crawl_mcp.py for robust Docker management.

        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Check if Docker is available
            if not await self._check_docker_available():
                self.status.status = "error"
                self.status.error_message = "Docker is not available"
                return False

            # Stop existing container if running
            await self._stop_existing_container()

            # Start new container
            docker_cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                self.container_name,
                "-p",
                f"{self.config.gateway_port}:8088",
                "-p",
                f"{self.config.designer_port}:8043",
            ]

            # Add environment variables
            for key, value in self.config.environment_variables.items():
                docker_cmd.extend(["-e", f"{key}={value}"])

            # Add volume mounts
            for mount in self.config.volume_mounts:
                docker_cmd.extend(["-v", mount])

            docker_cmd.append(self.docker_image)

            result = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                self.status.container_id = stdout.decode().strip()
                self.status.status = "running"
                self.status.gateway_url = f"http://localhost:{self.config.gateway_port}"
                self.status.designer_url = (
                    f"http://localhost:{self.config.designer_port}"
                )

                # Wait for container to be ready
                if await self._wait_for_ready():
                    return True
                else:
                    self.status.status = "error"
                    self.status.error_message = "Container failed to become ready"
                    return False
            else:
                self.status.status = "error"
                self.status.error_message = stderr.decode()
                return False

        except Exception as e:
            self.status.status = "error"
            self.status.error_message = str(e)
            return False

    async def stop(self) -> bool:
        """Stop the Docker test environment.

        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            if self.status.container_id:
                # Stop container
                result = await asyncio.create_subprocess_exec(
                    "docker",
                    "stop",
                    self.status.container_id,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await result.communicate()

                # Remove container
                result = await asyncio.create_subprocess_exec(
                    "docker",
                    "rm",
                    self.status.container_id,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await result.communicate()

            self.status.status = "stopped"
            self.status.container_id = None
            return True

        except Exception as e:
            self.status.error_message = str(e)
            return False

    async def is_ready(self) -> bool:
        """Check if the Docker environment is ready for testing.

        Returns:
            True if ready, False otherwise
        """
        if self.status.status != "running" or not self.status.gateway_url:
            return False

        try:
            # Simple health check - try to connect to gateway
            result = await asyncio.create_subprocess_exec(
                "curl",
                "-f",
                "-s",
                f"{self.status.gateway_url}/main/web/status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.communicate()
            return result.returncode == 0

        except Exception:
            return False

    async def _check_docker_available(self) -> bool:
        """Check if Docker is available.

        Following patterns from crawl_mcp.py for environment checking.

        Returns:
            True if Docker is available, False otherwise
        """
        try:
            result = await asyncio.create_subprocess_exec(
                "docker",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.communicate()
            return result.returncode == 0
        except Exception:
            return False

    async def _stop_existing_container(self) -> None:
        """Stop any existing container with the same name."""
        try:
            # Check if container exists
            result = await asyncio.create_subprocess_exec(
                "docker",
                "ps",
                "-a",
                "-q",
                "-f",
                f"name={self.container_name}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await result.communicate()

            if stdout.strip():
                # Stop and remove existing container
                await asyncio.create_subprocess_exec(
                    "docker",
                    "stop",
                    self.container_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await asyncio.create_subprocess_exec(
                    "docker",
                    "rm",
                    self.container_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
        except Exception:
            pass  # Ignore errors when cleaning up

    async def _wait_for_ready(self, max_wait: int = 60) -> bool:
        """Wait for the container to be ready.

        Args:
            max_wait: Maximum time to wait in seconds

        Returns:
            True if ready within timeout, False otherwise
        """
        for _ in range(max_wait):
            if await self.is_ready():
                return True
            await asyncio.sleep(1)
        return False


class LocalTestEnvironment(TestEnvironment):
    """Local test environment using existing Ignition installation."""

    def __init__(self, config: TestEnvironmentConfig):
        """Initialize the local test environment.

        Args:
            config: Test environment configuration
        """
        super().__init__(config)
        self.status.name = "local-ignition"
        self.status.type = "local"

        # Use configured gateway URL or default
        self.gateway_url = os.getenv(
            "TEST_GATEWAY_URL", f"http://localhost:{config.gateway_port}"
        )

    async def start(self) -> bool:
        """Start the local test environment.

        For local environments, this mainly validates connectivity.

        Returns:
            True if environment is accessible, False otherwise
        """
        try:
            self.status.gateway_url = self.gateway_url
            self.status.designer_url = self.gateway_url.replace(
                str(self.config.gateway_port), str(self.config.designer_port)
            )

            if await self.is_ready():
                self.status.status = "running"
                return True
            else:
                self.status.status = "error"
                self.status.error_message = "Cannot connect to local Ignition gateway"
                return False

        except Exception as e:
            self.status.status = "error"
            self.status.error_message = str(e)
            return False

    async def stop(self) -> bool:
        """Stop the local test environment.

        For local environments, this is a no-op.

        Returns:
            True always (local environment is managed externally)
        """
        self.status.status = "stopped"
        return True

    async def is_ready(self) -> bool:
        """Check if the local environment is ready for testing.

        Returns:
            True if ready, False otherwise
        """
        try:
            # Simple connectivity check
            result = await asyncio.create_subprocess_exec(
                "curl",
                "-f",
                "-s",
                "--connect-timeout",
                "5",
                f"{self.gateway_url}/main/web/status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.communicate()
            return result.returncode == 0

        except Exception:
            return False


class TestEnvironmentManager:
    """Manager for test environments with context management.

    Following patterns from crawl_mcp.py for resource management and cleanup.
    """

    def __init__(self):
        """Initialize the test environment manager."""
        self.environments: dict[str, TestEnvironment] = {}
        self.active_environment: TestEnvironment | None = None

    @asynccontextmanager
    async def test_environment(
        self, config: TestEnvironmentConfig
    ) -> AsyncIterator[TestEnvironment]:
        """Create and manage a test environment with automatic cleanup.

        Following patterns from crawl_mcp.py for context management.

        Args:
            config: Test environment configuration

        Yields:
            TestEnvironment instance ready for testing
        """
        # Create appropriate environment type
        if config.docker_enabled:
            env = DockerTestEnvironment(config)
        else:
            env = LocalTestEnvironment(config)

        try:
            # Start the environment
            if await env.start():
                self.active_environment = env
                self.environments[env.status.name] = env
                yield env
            else:
                raise RuntimeError(
                    f"Failed to start test environment: {env.status.error_message}"
                )

        finally:
            # Cleanup
            if env in self.environments.values():
                await env.stop()
                if env.status.name in self.environments:
                    del self.environments[env.status.name]
            if self.active_environment == env:
                self.active_environment = None

    async def get_environment_status(self) -> dict[str, Any]:
        """Get status of all managed environments.

        Returns:
            Dictionary with environment status information
        """
        status = {
            "total_environments": len(self.environments),
            "active_environment": (
                self.active_environment.status.name if self.active_environment else None
            ),
            "environments": [],
        }

        for env in self.environments.values():
            status["environments"].append(
                {
                    "name": env.status.name,
                    "type": env.status.type,
                    "status": env.status.status,
                    "gateway_url": env.status.gateway_url,
                    "designer_url": env.status.designer_url,
                    "error": env.status.error_message,
                }
            )

        return status

    async def cleanup_all(self) -> None:
        """Clean up all managed environments."""
        for env in list(self.environments.values()):
            await env.stop()
        self.environments.clear()
        self.active_environment = None
