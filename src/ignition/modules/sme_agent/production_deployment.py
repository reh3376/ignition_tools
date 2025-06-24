"""Phase 11.7: Production Deployment & PLC Integration Module

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Input validation and sanitization
- Step 3: Comprehensive error handling
- Step 4: Modular testing integration
- Step 5: Progressive complexity
- Step 6: Resource management
"""

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import docker
from pydantic import BaseModel, Field, field_validator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


class DeploymentMode(Enum):
    """Deployment mode enumeration."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


class PLCConnectionStatus(Enum):
    """PLC connection status enumeration."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNAUTHORIZED = "unauthorized"


class DeploymentStatus(Enum):
    """Deployment status enumeration."""

    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    UPDATING = "updating"


# Pydantic Models for Input Validation


class DockerConfig(BaseModel):
    """Docker deployment configuration with validation."""

    image_name: str = Field(..., description="Docker image name")
    tag: str = Field(default="latest", description="Docker image tag")
    container_name: str = Field(..., description="Container name")
    ports: dict[int, int] = Field(default_factory=dict, description="Port mappings")
    environment: dict[str, str] = Field(
        default_factory=dict, description="Environment variables"
    )
    volumes: dict[str, str] = Field(default_factory=dict, description="Volume mappings")
    network_mode: str = Field(default="bridge", description="Docker network mode")
    restart_policy: str = Field(
        default="unless-stopped", description="Container restart policy"
    )
    memory_limit: str = Field(default="2g", description="Memory limit")
    cpu_limit: float = Field(default=2.0, ge=0.1, le=32.0, description="CPU limit")

    @field_validator("image_name")
    @classmethod
    def validate_image_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Image name cannot be empty")
        if (
            not v.replace("-", "")
            .replace("_", "")
            .replace("/", "")
            .replace(":", "")
            .replace(".", "")
            .isalnum()
        ):
            raise ValueError("Invalid Docker image name format")
        return v.strip()

    @field_validator("ports")
    @classmethod
    def validate_ports(cls, v: dict[int, int]) -> dict[int, int]:
        for host_port, container_port in v.items():
            if not (1 <= host_port <= 65535) or not (1 <= container_port <= 65535):
                raise ValueError(f"Invalid port mapping: {host_port}:{container_port}")
        return v


class PLCConfig(BaseModel):
    """PLC configuration with validation."""

    name: str = Field(..., description="PLC name/identifier")
    server_url: str = Field(..., description="OPC-UA server URL")
    username: str | None = Field(None, description="Authentication username")
    password: str | None = Field(None, description="Authentication password")
    security_policy: str = Field(default="None", description="Security policy")
    timeout: float = Field(default=30.0, gt=0, le=300, description="Connection timeout")
    polling_interval: float = Field(
        default=1.0, gt=0.1, le=60.0, description="Data polling interval"
    )
    tag_list: list[str] = Field(
        default_factory=list, description="OPC-UA tags to monitor"
    )

    @field_validator("server_url")
    @classmethod
    def validate_server_url(cls, v: str) -> str:
        if not v.startswith(("opc.tcp://", "http://", "https://")):
            raise ValueError("Invalid OPC-UA server URL format")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("PLC name cannot be empty")
        return v.strip()


class ProductionConfig(BaseModel):
    """Production deployment configuration."""

    deployment_mode: DeploymentMode = Field(
        default=DeploymentMode.PRODUCTION, description="Deployment mode"
    )
    docker_config: DockerConfig = Field(..., description="Docker configuration")
    plc_configs: list[PLCConfig] = Field(
        default_factory=list, description="PLC configurations"
    )
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")
    auto_restart: bool = Field(default=True, description="Enable auto-restart")
    health_check_interval: float = Field(
        default=30.0, gt=0, description="Health check interval"
    )
    log_level: str = Field(default="INFO", description="Logging level")
    backup_enabled: bool = Field(default=True, description="Enable automated backups")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()


@dataclass
class PLCConnectionInfo:
    """PLC connection information."""

    name: str
    server_url: str
    status: PLCConnectionStatus
    last_connected: datetime | None = None
    error_message: str | None = None
    tag_count: int = 0
    data_quality: float = 0.0  # 0.0 to 1.0


@dataclass
class DeploymentInfo:
    """Deployment information."""

    container_name: str
    status: DeploymentStatus
    image: str
    created: datetime
    ports: dict[int, int]
    memory_usage: str = "N/A"
    cpu_usage: str = "N/A"
    uptime: str = "N/A"


# Environment Validation Functions (Step 1: crawl_mcp.py methodology)


def validate_production_environment() -> dict[str, Any]:
    """Validate production deployment environment."""
    logger.info("🔍 Validating production deployment environment...")

    validation_results = {"valid": True, "errors": [], "warnings": [], "components": {}}

    try:
        # Validate Docker environment
        docker_validation = validate_docker_environment()
        validation_results["components"]["docker"] = docker_validation
        if not docker_validation["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(docker_validation["errors"])

        # Validate required packages
        packages_validation = validate_production_packages()
        validation_results["components"]["packages"] = packages_validation
        if not packages_validation["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(packages_validation["errors"])

        # Validate environment variables
        env_validation = validate_production_env_vars()
        validation_results["components"]["environment"] = env_validation
        if not env_validation["valid"]:
            validation_results["warnings"].extend(env_validation["warnings"])

        # Validate network connectivity
        network_validation = validate_network_connectivity()
        validation_results["components"]["network"] = network_validation
        if not network_validation["valid"]:
            validation_results["warnings"].extend(network_validation["warnings"])

        return validation_results

    except Exception as e:
        logger.error(f"❌ Environment validation failed: {e}")
        return {
            "valid": False,
            "errors": [f"Environment validation error: {e!s}"],
            "components": {},
        }


def validate_docker_environment() -> dict[str, Any]:
    """Validate Docker environment."""
    try:
        # Check if Docker is installed and running
        client = docker.from_env()
        client.ping()

        # Get Docker version info
        version_info = client.version()

        # Check available resources
        info = client.info()

        return {
            "valid": True,
            "version": version_info.get("Version", "unknown"),
            "api_version": version_info.get("ApiVersion", "unknown"),
            "containers_running": info.get("ContainersRunning", 0),
            "containers_total": info.get("Containers", 0),
            "images_count": info.get("Images", 0),
            "memory_total": info.get("MemTotal", 0),
            "cpus": info.get("NCPU", 0),
        }

    except Exception as e:
        return {"valid": False, "errors": [f"Docker validation error: {e!s}"]}


def validate_production_packages() -> dict[str, Any]:
    """Validate required packages for production deployment."""
    required_packages = [
        ("docker", "docker"),
        ("asyncua", "asyncua"),
        ("pydantic", "pydantic"),
        ("rich", "rich"),
        ("psutil", "psutil"),
    ]

    missing_packages = []
    available_packages = {}

    for package_name, import_name in required_packages:
        try:
            module = __import__(import_name)
            available_packages[package_name] = getattr(module, "__version__", "unknown")
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        return {
            "valid": False,
            "errors": [f"Missing packages: {', '.join(missing_packages)}"],
            "available": available_packages,
        }

    return {"valid": True, "available": available_packages}


def validate_production_env_vars() -> dict[str, Any]:
    """Validate production environment variables."""
    required_vars = ["DOCKER_REGISTRY", "DEPLOYMENT_MODE", "LOG_LEVEL"]

    optional_vars = [
        "NEO4J_URI",
        "NEO4J_USER",
        "NEO4J_PASSWORD",
        "OPCUA_SERVER_URL",
        "OPCUA_USERNAME",
        "OPCUA_PASSWORD",
    ]

    missing_vars = []
    warnings = []
    configured_vars = {}

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            configured_vars[var] = value

    for var in optional_vars:
        value = os.getenv(var)
        if not value:
            warnings.append(f"Optional environment variable {var} not configured")
        else:
            configured_vars[var] = "***" if "password" in var.lower() else value

    return {
        "valid": len(missing_vars) == 0,
        "warnings": warnings,
        "configured": configured_vars,
        "missing": missing_vars,
    }


def validate_network_connectivity() -> dict[str, Any]:
    """Validate network connectivity for production deployment."""
    connectivity_checks = []

    # Check Docker daemon connectivity
    try:
        client = docker.from_env()
        client.ping()
        connectivity_checks.append({"service": "Docker Daemon", "status": "connected"})
    except Exception as e:
        connectivity_checks.append(
            {"service": "Docker Daemon", "status": "failed", "error": str(e)}
        )

    # Check OPC-UA server connectivity if configured
    opcua_url = os.getenv("OPCUA_SERVER_URL")
    if opcua_url:
        try:
            # Basic URL validation
            if opcua_url.startswith("opc.tcp://"):
                connectivity_checks.append(
                    {"service": f"OPC-UA ({opcua_url})", "status": "configured"}
                )
            else:
                connectivity_checks.append(
                    {"service": f"OPC-UA ({opcua_url})", "status": "invalid_url"}
                )
        except Exception as e:
            connectivity_checks.append(
                {"service": "OPC-UA", "status": "failed", "error": str(e)}
            )

    # Check Neo4j connectivity if configured
    neo4j_uri = os.getenv("NEO4J_URI")
    if neo4j_uri:
        connectivity_checks.append(
            {"service": f"Neo4j ({neo4j_uri})", "status": "configured"}
        )

    failed_checks = [
        check
        for check in connectivity_checks
        if check["status"] in ["failed", "invalid_url"]
    ]

    return {
        "valid": len(failed_checks) == 0,
        "checks": connectivity_checks,
        "warnings": [
            f"Connectivity issue: {check['service']}" for check in failed_checks
        ],
    }


# Error Handling Functions (Step 3: crawl_mcp.py methodology)


def format_deployment_error(error: Exception, context: str = "") -> str:
    """Format deployment errors for user-friendly messages."""
    error_str = str(error).lower()

    if "docker" in error_str and "connection" in error_str:
        return (
            f"Docker connection error in {context}: Check if Docker daemon is running"
        )
    elif "permission" in error_str or "denied" in error_str:
        return (
            f"Permission error in {context}: Check Docker permissions or run with sudo"
        )
    elif "not found" in error_str or "no such" in error_str:
        return f"Resource not found in {context}: Check image/container names"
    elif "port" in error_str and "bind" in error_str:
        return f"Port binding error in {context}: Check if ports are already in use"
    elif "timeout" in error_str:
        return f"Timeout error in {context}: Check network connectivity and timeouts"
    else:
        return f"Deployment error in {context}: {error!s}"


# Core Production Deployment Class


@dataclass
class ProductionDeploymentManager:
    """Production Deployment Manager for Phase 11.7.

    Manages Docker-based production deployments with PLC integration,
    monitoring, and automated management capabilities.
    """

    config: ProductionConfig
    _docker_client: docker.DockerClient | None = field(default=None, init=False)
    _plc_connections: dict[str, PLCConnectionInfo] = field(
        default_factory=dict, init=False
    )
    _deployment_info: DeploymentInfo | None = field(default=None, init=False)
    _monitoring_task: asyncio.Task | None = field(default=None, init=False)
    _is_initialized: bool = field(default=False, init=False)

    async def initialize(self) -> dict[str, Any]:
        """Initialize the production deployment manager."""
        logger.info("🚀 Initializing Production Deployment Manager...")

        # Step 1: Environment validation first (crawl_mcp.py methodology)
        env_validation = validate_production_environment()
        if not env_validation["valid"]:
            return {
                "success": False,
                "error": "Environment validation failed",
                "details": env_validation["errors"],
            }

        try:
            # Step 2: Initialize Docker client
            docker_result = await self._initialize_docker()
            if not docker_result["success"]:
                return docker_result

            # Step 3: Initialize PLC connections
            plc_result = await self._initialize_plc_connections()
            if not plc_result["success"]:
                logger.warning(f"PLC initialization failed: {plc_result['error']}")
                # Continue without PLC - not critical for basic deployment

            # Step 4: Start monitoring if enabled
            if self.config.monitoring_enabled:
                monitoring_result = await self._start_monitoring()
                if not monitoring_result["success"]:
                    logger.warning(
                        f"Monitoring initialization failed: {monitoring_result['error']}"
                    )

            self._is_initialized = True
            logger.info("✅ Production Deployment Manager initialized successfully")

            return {
                "success": True,
                "message": "Production Deployment Manager initialized successfully",
                "components": {
                    "docker": docker_result,
                    "plc": plc_result,
                    "monitoring": self.config.monitoring_enabled,
                },
            }

        except Exception as e:
            error_msg = format_deployment_error(e, "initialization")
            logger.error(f"❌ Initialization failed: {error_msg}")
            return {"success": False, "error": error_msg}

    async def _initialize_docker(self) -> dict[str, Any]:
        """Initialize Docker client."""
        try:
            self._docker_client = docker.from_env()
            self._docker_client.ping()

            logger.info("✅ Docker client initialized")
            return {"success": True, "message": "Docker client connected"}

        except Exception as e:
            error_msg = format_deployment_error(e, "Docker initialization")
            return {"success": False, "error": error_msg}

    async def _initialize_plc_connections(self) -> dict[str, Any]:
        """Initialize PLC connections."""
        if not self.config.plc_configs:
            return {"success": True, "message": "No PLC configurations provided"}

        try:
            for plc_config in self.config.plc_configs:
                connection_info = PLCConnectionInfo(
                    name=plc_config.name,
                    server_url=plc_config.server_url,
                    status=PLCConnectionStatus.DISCONNECTED,
                    tag_count=len(plc_config.tag_list),
                )

                # Test connection
                connection_result = await self._test_plc_connection(plc_config)
                if connection_result["success"]:
                    connection_info.status = PLCConnectionStatus.CONNECTED
                    connection_info.last_connected = datetime.now()
                    connection_info.data_quality = 1.0
                else:
                    connection_info.status = PLCConnectionStatus.ERROR
                    connection_info.error_message = connection_result["error"]

                self._plc_connections[plc_config.name] = connection_info

            connected_count = sum(
                1
                for conn in self._plc_connections.values()
                if conn.status == PLCConnectionStatus.CONNECTED
            )

            logger.info(
                f"✅ PLC connections initialized: {connected_count}/{len(self.config.plc_configs)} connected"
            )

            return {
                "success": True,
                "message": f"PLC connections initialized: {connected_count}/{len(self.config.plc_configs)} connected",
                "connections": {
                    name: conn.status.value
                    for name, conn in self._plc_connections.items()
                },
            }

        except Exception as e:
            error_msg = format_deployment_error(e, "PLC initialization")
            return {"success": False, "error": error_msg}

    async def _test_plc_connection(self, plc_config: PLCConfig) -> dict[str, Any]:
        """Test PLC connection."""
        try:
            from asyncua import Client

            client = Client(url=plc_config.server_url)

            if plc_config.username and plc_config.password:
                client.set_user(plc_config.username)
                client.set_password(plc_config.password)

            # Test connection with timeout
            await asyncio.wait_for(client.connect(), timeout=plc_config.timeout)
            await client.disconnect()

            return {
                "success": True,
                "message": f"PLC {plc_config.name} connection successful",
            }

        except TimeoutError:
            return {
                "success": False,
                "error": f"Connection timeout for PLC {plc_config.name}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"PLC {plc_config.name} connection failed: {e!s}",
            }

    async def _start_monitoring(self) -> dict[str, Any]:
        """Start monitoring tasks."""
        try:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("✅ Monitoring started")
            return {"success": True, "message": "Monitoring started"}

        except Exception as e:
            error_msg = format_deployment_error(e, "monitoring startup")
            return {"success": False, "error": error_msg}

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self._is_initialized:
            try:
                # Monitor deployment status
                await self._update_deployment_status()

                # Monitor PLC connections
                await self._monitor_plc_connections()

                # Health checks
                await self._perform_health_checks()

                # Wait for next monitoring cycle
                await asyncio.sleep(self.config.health_check_interval)

            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.config.health_check_interval)

    async def _update_deployment_status(self) -> None:
        """Update deployment status information."""
        if not self._docker_client or not self._deployment_info:
            return

        try:
            container = self._docker_client.containers.get(
                self._deployment_info.container_name
            )

            # Update status
            if container.status == "running":
                self._deployment_info.status = DeploymentStatus.RUNNING
            elif container.status == "exited":
                self._deployment_info.status = DeploymentStatus.STOPPED
            else:
                self._deployment_info.status = DeploymentStatus.FAILED

            # Update resource usage
            stats = container.stats(stream=False)
            if stats:
                # Calculate memory usage
                memory_usage = stats.get("memory_stats", {}).get("usage", 0)
                memory_limit = stats.get("memory_stats", {}).get("limit", 0)
                if memory_limit > 0:
                    memory_percent = (memory_usage / memory_limit) * 100
                    self._deployment_info.memory_usage = f"{memory_percent:.1f}%"

                # Calculate CPU usage
                cpu_stats = stats.get("cpu_stats", {})
                precpu_stats = stats.get("precpu_stats", {})
                if cpu_stats and precpu_stats:
                    cpu_delta = cpu_stats.get("cpu_usage", {}).get(
                        "total_usage", 0
                    ) - precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
                    system_delta = cpu_stats.get(
                        "system_cpu_usage", 0
                    ) - precpu_stats.get("system_cpu_usage", 0)
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * 100
                        self._deployment_info.cpu_usage = f"{cpu_percent:.1f}%"

            # Update uptime
            created_time = datetime.fromisoformat(
                container.attrs["Created"].replace("Z", "+00:00")
            )
            uptime = datetime.now() - created_time.replace(tzinfo=None)
            self._deployment_info.uptime = str(uptime).split(".")[
                0
            ]  # Remove microseconds

        except Exception as e:
            logger.error(f"Error updating deployment status: {e}")

    async def _monitor_plc_connections(self) -> None:
        """Monitor PLC connection health."""
        for name, connection_info in self._plc_connections.items():
            try:
                plc_config = next(
                    (cfg for cfg in self.config.plc_configs if cfg.name == name), None
                )
                if not plc_config:
                    continue

                # Test connection
                test_result = await self._test_plc_connection(plc_config)

                if test_result["success"]:
                    if connection_info.status != PLCConnectionStatus.CONNECTED:
                        logger.info(f"PLC {name} reconnected")
                    connection_info.status = PLCConnectionStatus.CONNECTED
                    connection_info.last_connected = datetime.now()
                    connection_info.error_message = None
                else:
                    if connection_info.status == PLCConnectionStatus.CONNECTED:
                        logger.warning(
                            f"PLC {name} disconnected: {test_result['error']}"
                        )
                    connection_info.status = PLCConnectionStatus.ERROR
                    connection_info.error_message = test_result["error"]

            except Exception as e:
                logger.error(f"Error monitoring PLC {name}: {e}")
                connection_info.status = PLCConnectionStatus.ERROR
                connection_info.error_message = str(e)

    async def _perform_health_checks(self) -> None:
        """Perform system health checks."""
        try:
            # Check system resources
            import psutil

            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage("/")

            # Log warnings for high resource usage
            if memory.percent > 90:
                logger.warning(f"High memory usage: {memory.percent:.1f}%")

            if cpu_percent > 90:
                logger.warning(f"High CPU usage: {cpu_percent:.1f}%")

            if disk.percent > 90:
                logger.warning(f"High disk usage: {disk.percent:.1f}%")

        except Exception as e:
            logger.error(f"Health check error: {e}")

    # Resource Management (Step 6: crawl_mcp.py methodology)

    @asynccontextmanager
    async def managed_deployment(self) -> AsyncIterator["ProductionDeploymentManager"]:
        """Manage production deployment with proper cleanup."""
        try:
            initialization_result = await self.initialize()
            if not initialization_result["success"]:
                raise RuntimeError(
                    f"Initialization failed: {initialization_result['error']}"
                )

            yield self

        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Clean up all resources properly."""
        logger.info("🧹 Cleaning up Production Deployment Manager resources...")

        # Stop monitoring
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ Monitoring stopped")

        # Close Docker client
        if self._docker_client:
            try:
                self._docker_client.close()
                logger.info("✅ Docker client closed")
            except Exception as e:
                logger.error(f"Error closing Docker client: {e}")

        self._is_initialized = False
        logger.info("✅ Cleanup completed")

    # Deployment Operations

    async def deploy_container(self) -> dict[str, Any]:
        """Deploy production container."""
        if not self._is_initialized:
            return {"success": False, "error": "Manager not initialized"}

        if not self._docker_client:
            return {"success": False, "error": "Docker client not available"}

        try:
            docker_config = self.config.docker_config

            # Check if container already exists
            try:
                existing_container = self._docker_client.containers.get(
                    docker_config.container_name
                )
                if existing_container.status == "running":
                    return {
                        "success": False,
                        "error": f"Container {docker_config.container_name} already running",
                    }
                else:
                    # Remove stopped container
                    existing_container.remove()
                    logger.info(
                        f"Removed existing container: {docker_config.container_name}"
                    )
            except docker.errors.NotFound:
                pass  # Container doesn't exist, which is fine

            # Pull image if needed
            try:
                image_name = f"{docker_config.image_name}:{docker_config.tag}"
                logger.info(f"Pulling image: {image_name}")
                self._docker_client.images.pull(
                    docker_config.image_name, tag=docker_config.tag
                )
            except Exception as e:
                logger.warning(f"Could not pull image: {e}")

            # Create and start container
            logger.info(f"Creating container: {docker_config.container_name}")

            # Convert port mappings to Docker API format
            port_bindings = {
                f"{container_port}/tcp": host_port
                for host_port, container_port in docker_config.ports.items()
            }

            # Convert volumes to Docker API format (if any)
            volume_bindings = None
            if docker_config.volumes:
                volume_bindings = [
                    f"{host_path}:{container_path}"
                    for host_path, container_path in docker_config.volumes.items()
                ]

            container = self._docker_client.containers.run(
                image=f"{docker_config.image_name}:{docker_config.tag}",
                name=docker_config.container_name,
                ports=port_bindings,
                environment=docker_config.environment,
                volumes=volume_bindings,
                network_mode=docker_config.network_mode,
                restart_policy={"Name": docker_config.restart_policy},
                mem_limit=docker_config.memory_limit,
                nano_cpus=int(docker_config.cpu_limit * 1e9),
                detach=True,
            )

            # Update deployment info
            self._deployment_info = DeploymentInfo(
                container_name=docker_config.container_name,
                status=DeploymentStatus.RUNNING,
                image=f"{docker_config.image_name}:{docker_config.tag}",
                created=datetime.now(),
                ports=docker_config.ports,
            )

            logger.info(
                f"✅ Container deployed successfully: {docker_config.container_name}"
            )

            return {
                "success": True,
                "message": f"Container {docker_config.container_name} deployed successfully",
                "container_id": container.id,
                "status": container.status,
                "ports": docker_config.ports,
            }

        except Exception as e:
            error_msg = format_deployment_error(e, "container deployment")
            logger.error(f"❌ Container deployment failed: {error_msg}")
            return {"success": False, "error": error_msg}

    async def stop_container(self) -> dict[str, Any]:
        """Stop production container."""
        if not self._docker_client or not self._deployment_info:
            return {"success": False, "error": "No active deployment"}

        try:
            container = self._docker_client.containers.get(
                self._deployment_info.container_name
            )
            container.stop(timeout=30)

            self._deployment_info.status = DeploymentStatus.STOPPED

            logger.info(f"✅ Container stopped: {self._deployment_info.container_name}")

            return {
                "success": True,
                "message": f"Container {self._deployment_info.container_name} stopped successfully",
            }

        except Exception as e:
            error_msg = format_deployment_error(e, "container stop")
            return {"success": False, "error": error_msg}

    async def restart_container(self) -> dict[str, Any]:
        """Restart production container."""
        if not self._docker_client or not self._deployment_info:
            return {"success": False, "error": "No active deployment"}

        try:
            container = self._docker_client.containers.get(
                self._deployment_info.container_name
            )
            container.restart(timeout=30)

            self._deployment_info.status = DeploymentStatus.RUNNING

            logger.info(
                f"✅ Container restarted: {self._deployment_info.container_name}"
            )

            return {
                "success": True,
                "message": f"Container {self._deployment_info.container_name} restarted successfully",
            }

        except Exception as e:
            error_msg = format_deployment_error(e, "container restart")
            return {"success": False, "error": error_msg}

    def get_deployment_status(self) -> dict[str, Any]:
        """Get current deployment status."""
        if not self._deployment_info:
            return {"deployed": False, "message": "No active deployment"}

        plc_status = {
            name: {
                "status": conn.status.value,
                "last_connected": (
                    conn.last_connected.isoformat() if conn.last_connected else None
                ),
                "error": conn.error_message,
                "tag_count": conn.tag_count,
                "data_quality": conn.data_quality,
            }
            for name, conn in self._plc_connections.items()
        }

        return {
            "deployed": True,
            "container": {
                "name": self._deployment_info.container_name,
                "status": self._deployment_info.status.value,
                "image": self._deployment_info.image,
                "created": self._deployment_info.created.isoformat(),
                "ports": self._deployment_info.ports,
                "memory_usage": self._deployment_info.memory_usage,
                "cpu_usage": self._deployment_info.cpu_usage,
                "uptime": self._deployment_info.uptime,
            },
            "plc_connections": plc_status,
            "monitoring_enabled": self.config.monitoring_enabled,
            "deployment_mode": self.config.deployment_mode.value,
        }

    def display_status(self) -> None:
        """Display deployment status in a formatted table."""
        status = self.get_deployment_status()

        if not status["deployed"]:
            console.print("[yellow]No active deployment[/yellow]")
            return

        # Container status table
        container_table = Table(
            title="🐳 Container Status", show_header=True, header_style="bold blue"
        )
        container_table.add_column("Property", style="cyan")
        container_table.add_column("Value", style="white")

        container = status["container"]
        container_table.add_row("Name", container["name"])
        container_table.add_row("Status", container["status"])
        container_table.add_row("Image", container["image"])
        container_table.add_row("Created", container["created"])
        container_table.add_row("Uptime", container["uptime"])
        container_table.add_row("Memory Usage", container["memory_usage"])
        container_table.add_row("CPU Usage", container["cpu_usage"])
        container_table.add_row("Ports", str(container["ports"]))

        console.print(container_table)

        # PLC connections table
        if status["plc_connections"]:
            plc_table = Table(
                title="🏭 PLC Connections", show_header=True, header_style="bold green"
            )
            plc_table.add_column("Name", style="cyan")
            plc_table.add_column("Status", style="white")
            plc_table.add_column("Last Connected", style="white")
            plc_table.add_column("Tags", style="white")
            plc_table.add_column("Quality", style="white")
            plc_table.add_column("Error", style="red")

            for name, conn in status["plc_connections"].items():
                status_color = "green" if conn["status"] == "connected" else "red"
                quality_str = (
                    f"{conn['data_quality']:.1%}" if conn["data_quality"] > 0 else "N/A"
                )

                plc_table.add_row(
                    name,
                    f"[{status_color}]{conn['status']}[/{status_color}]",
                    conn["last_connected"] or "Never",
                    str(conn["tag_count"]),
                    quality_str,
                    conn["error"] or "",
                )

            console.print(plc_table)

        # System info
        system_panel = Panel(
            f"[bold]Deployment Mode:[/bold] {status['deployment_mode']}\n"
            f"[bold]Monitoring:[/bold] {'Enabled' if status['monitoring_enabled'] else 'Disabled'}",
            title="🔧 System Configuration",
            border_style="blue",
        )
        console.print(system_panel)


# Testing Functions (Step 4: crawl_mcp.py methodology)


async def test_production_deployment() -> dict[str, Any]:
    """Test production deployment functionality."""
    logger.info("🧪 Testing production deployment functionality...")

    try:
        # Create test configuration
        test_docker_config = DockerConfig(
            image_name="nginx",
            tag="alpine",
            container_name="ign-scripts-test-deployment",
            ports={8080: 80},
            environment={"TEST_MODE": "true"},
            memory_limit="512m",
            cpu_limit=1.0,
        )

        test_config = ProductionConfig(
            deployment_mode=DeploymentMode.DEVELOPMENT,
            docker_config=test_docker_config,
            monitoring_enabled=False,  # Disable for testing
            health_check_interval=60.0,
        )

        # Test deployment manager
        async with ProductionDeploymentManager(
            test_config
        ).managed_deployment() as manager:
            # Test deployment
            deploy_result = await manager.deploy_container()
            if not deploy_result["success"]:
                return {
                    "success": False,
                    "error": f"Deployment test failed: {deploy_result['error']}",
                }

            # Test status
            status = manager.get_deployment_status()
            if not status["deployed"]:
                return {
                    "success": False,
                    "error": "Status test failed: Container not deployed",
                }

            # Test stop
            stop_result = await manager.stop_container()
            if not stop_result["success"]:
                return {
                    "success": False,
                    "error": f"Stop test failed: {stop_result['error']}",
                }

        logger.info("✅ Production deployment test completed successfully")
        return {"success": True, "message": "All production deployment tests passed"}

    except Exception as e:
        error_msg = format_deployment_error(e, "testing")
        logger.error(f"❌ Production deployment test failed: {error_msg}")
        return {"success": False, "error": error_msg}


# Factory Functions


async def create_production_deployment_manager(
    deployment_mode: str = "production",
    docker_image: str = "ign-scripts",
    docker_tag: str = "latest",
    container_name: str = "ign-scripts-production",
    ports: dict[int, int] | None = None,
    plc_configs: list[dict[str, Any]] | None = None,
) -> ProductionDeploymentManager:
    """Create a production deployment manager with default configuration."""
    if ports is None:
        ports = {8000: 8000, 8501: 8501}  # Default ports for API and Streamlit

    docker_config = DockerConfig(
        image_name=docker_image,
        tag=docker_tag,
        container_name=container_name,
        ports=ports,
        environment={
            "PYTHONPATH": "/app",
            "PYTHONUNBUFFERED": "1",
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "DEPLOYMENT_MODE": deployment_mode,
        },
        volumes={"./logs": "/app/logs", "./data": "/app/data"},
    )

    plc_config_list = []
    if plc_configs:
        for plc_data in plc_configs:
            plc_config_list.append(PLCConfig(**plc_data))

    config = ProductionConfig(
        deployment_mode=DeploymentMode(deployment_mode),
        docker_config=docker_config,
        plc_configs=plc_config_list,
    )

    return ProductionDeploymentManager(config)


# Main execution for testing
if __name__ == "__main__":

    async def main() -> None:
        console.print(
            "[bold blue]🏭 Phase 11.7: Production Deployment & PLC Integration[/bold blue]"
        )
        console.print("Testing production deployment functionality...\n")

        # Test environment validation
        env_result = validate_production_environment()
        console.print(
            f"Environment Validation: {'✅ Valid' if env_result['valid'] else '❌ Invalid'}"
        )

        if env_result["errors"]:
            for error in env_result["errors"]:
                console.print(f"  [red]Error:[/red] {error}")

        if env_result["warnings"]:
            for warning in env_result["warnings"]:
                console.print(f"  [yellow]Warning:[/yellow] {warning}")

        # Test deployment functionality
        test_result = await test_production_deployment()
        console.print(
            f"\nDeployment Test: {'✅ Passed' if test_result['success'] else '❌ Failed'}"
        )

        if not test_result["success"]:
            console.print(f"  [red]Error:[/red] {test_result['error']}")
        else:
            console.print(f"  [green]Success:[/green] {test_result['message']}")

    asyncio.run(main())
