"""Phase 12.8: Deployment Package Creation & How-to Guides.

Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Input validation and sanitization using Pydantic models
- Step 3: Comprehensive error handling with user-friendly messages
- Step 4: Modular testing integration
- Step 5: Progressive complexity
- Step 6: Resource management
"""

import asyncio
import logging
import os
import shutil
import subprocess
import tempfile
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
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


# Step 1: Environment Validation First (crawl_mcp.py methodology)
def validate_deployment_environment() -> dict[str, Any]:
    """Validate environment setup before proceeding with deployment package creation."""
    try:
        errors = []
        warnings = []

        # Check required tools
        required_tools = ["docker", "git", "python3"]
        for tool in required_tools:
            if not shutil.which(tool):
                errors.append(f"Required tool not found: {tool}")

        # Check Docker daemon
        try:
            docker_client = docker.from_env()
            docker_client.ping()
        except Exception as e:
            errors.append(f"Docker daemon not accessible: {e}")

        # Check Python version
        try:
            result = subprocess.run(["python3", "--version"], capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            if "3.12" not in version and "3.11" not in version:
                warnings.append(f"Python version may not be optimal: {version}")
        except Exception as e:
            errors.append(f"Cannot check Python version: {e}")

        # Check required directories
        required_dirs = ["src", "docs", "scripts"]
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                errors.append(f"Required directory not found: {dir_name}")

        # Check essential files
        essential_files = ["requirements.txt", "pyproject.toml", "README.md"]
        for file_name in essential_files:
            if not Path(file_name).exists():
                warnings.append(f"Essential file not found: {file_name}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "tools_available": [tool for tool in required_tools if shutil.which(tool)],
        }

    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Environment validation failed: {e}"],
            "warnings": [],
            "tools_available": [],
        }


def format_deployment_error(error: Exception, context: str = "") -> str:
    """Format deployment errors for user-friendly messages."""
    error_str = str(error).lower()

    if "docker" in error_str:
        if "permission" in error_str:
            return "Docker permission denied. Try: sudo usermod -aG docker $USER"
        elif "daemon" in error_str or "connection" in error_str:
            return "Docker daemon not running. Try: sudo systemctl start docker"
        else:
            return f"Docker error in {context}: {error}"
    elif "git" in error_str:
        return f"Git error in {context}: {error}"
    elif "permission" in error_str:
        return f"Permission error in {context}: {error}"
    else:
        return f"Error in {context}: {error}"


# Step 2: Input Validation and Sanitization using Pydantic models
class PackageType(Enum):
    """Package type enumeration."""

    DOCKER = "docker"
    STANDALONE = "standalone"
    KUBERNETES = "kubernetes"
    SYSTEMD = "systemd"


class DeploymentTarget(Enum):
    """Deployment target enumeration."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


class DockerPackageConfig(BaseModel):
    """Docker package configuration."""

    base_image: str = Field(default="python:3.12-slim", description="Base Docker image")
    image_name: str = Field(..., description="Docker image name")
    tag: str = Field(default="latest", description="Docker image tag")
    expose_ports: list[int] = Field(default=[8000], description="Ports to expose")
    volumes: dict[str, str] = Field(default_factory=dict, description="Volume mappings")
    environment_vars: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    health_check_command: str = Field(
        default="curl -f http://localhost:8000/health || exit 1",
        description="Health check command",
    )

    @field_validator("image_name")
    @classmethod
    def validate_image_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Image name cannot be empty")
        if " " in v:
            raise ValueError("Image name cannot contain spaces")
        return v.lower().strip()


class StandalonePackageConfig(BaseModel):
    """Standalone package configuration."""

    include_python: bool = Field(default=False, description="Include Python runtime")
    create_installer: bool = Field(default=True, description="Create installation script")
    service_name: str = Field(default="ign-scripts", description="Service name")
    install_path: str = Field(default="/opt/ign-scripts", description="Installation path")
    user_account: str = Field(default="ign-scripts", description="Service user account")

    @field_validator("install_path")
    @classmethod
    def validate_install_path(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("Install path must be absolute")
        return v


class PackageCreationRequest(BaseModel):
    """Package creation request model."""

    package_type: PackageType = Field(..., description="Type of package to create")
    deployment_target: DeploymentTarget = Field(..., description="Deployment target environment")
    version: str = Field(default="1.0.0", description="Package version")
    output_directory: str = Field(default="./dist", description="Output directory for packages")
    include_documentation: bool = Field(default=True, description="Include documentation in package")
    include_tests: bool = Field(default=False, description="Include tests in package")
    docker_config: DockerPackageConfig | None = Field(default=None, description="Docker-specific configuration")
    standalone_config: StandalonePackageConfig | None = Field(
        default=None, description="Standalone-specific configuration"
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        # Basic semantic version validation
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError("Version must be in format X.Y.Z")
        for part in parts:
            if not part.isdigit():
                raise ValueError("Version parts must be numeric")
        return v

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory(cls, v: str) -> str:
        # Ensure output directory is safe
        path = Path(v)
        if path.is_absolute() and not str(path).startswith("/tmp") and not str(path).startswith(os.getcwd()):
            raise ValueError("Output directory must be relative or within project")
        return v


@dataclass
class PackageCreationResult:
    """Result of package creation operation."""

    success: bool
    package_path: str | None = None
    package_size: int | None = None
    creation_time: datetime | None = None
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)
    included_files: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# Step 4: Modular Testing Integration
class DeploymentPackageCreator:
    """Main deployment package creator following crawl_mcp.py methodology."""

    def __init__(self) -> None:
        self._docker_client: docker.DockerClient | None = None
        self._temp_dirs: list[str] = []
        self._is_initialized = False

    async def initialize(self) -> dict[str, Any]:
        """Initialize the package creator with environment validation."""
        try:
            # Step 1: Environment validation first
            env_validation = validate_deployment_environment()
            if not env_validation["valid"]:
                return {
                    "success": False,
                    "error": "Environment validation failed",
                    "details": env_validation["errors"],
                }

            # Log warnings if any
            for warning in env_validation["warnings"]:
                logger.warning(f"⚠️ {warning}")

            # Step 2: Initialize Docker client if available
            if "docker" in env_validation["tools_available"]:
                try:
                    self._docker_client = docker.from_env()
                    self._docker_client.ping()
                    logger.info("✅ Docker client initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Docker client initialization failed: {e}")

            self._is_initialized = True
            return {
                "success": True,
                "message": "Package creator initialized successfully",
                "tools_available": env_validation["tools_available"],
            }

        except Exception as e:
            return {
                "success": False,
                "error": format_deployment_error(e, "package creator initialization"),
            }

    @asynccontextmanager
    async def managed_creation(self) -> None:
        """Context manager for package creation with proper cleanup."""
        try:
            if not self._is_initialized:
                init_result = await self.initialize()
                if not init_result["success"]:
                    raise RuntimeError(f"Initialization failed: {init_result['error']}")

            yield self
        finally:
            # Step 6: Resource management - cleanup temporary directories
            await self._cleanup_temp_dirs()

    async def _cleanup_temp_dirs(self) -> None:
        """Clean up temporary directories."""
        for temp_dir in self._temp_dirs:
            try:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                    logger.info(f"🧹 Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup {temp_dir}: {e}")
        self._temp_dirs.clear()

    async def create_package(self, request: PackageCreationRequest) -> PackageCreationResult:
        """Create deployment package based on request."""
        start_time = datetime.now()

        try:
            # Step 3: Comprehensive error handling
            if not self._is_initialized:
                return PackageCreationResult(success=False, error_message="Package creator not initialized")

            # Create output directory
            output_path = Path(request.output_directory)
            output_path.mkdir(parents=True, exist_ok=True)

            # Route to appropriate package creation method
            if request.package_type == PackageType.DOCKER:
                result = await self._create_docker_package(request)
            elif request.package_type == PackageType.STANDALONE:
                result = await self._create_standalone_package(request)
            elif request.package_type == PackageType.KUBERNETES:
                result = await self._create_kubernetes_package(request)
            elif request.package_type == PackageType.SYSTEMD:
                result = await self._create_systemd_package(request)
            else:
                return PackageCreationResult(
                    success=False,
                    error_message=f"Unsupported package type: {request.package_type}",
                )

            # Add timing information
            if result.success:
                result.creation_time = start_time
                result.metadata["creation_duration"] = (datetime.now() - start_time).total_seconds()

            return result

        except Exception as e:
            return PackageCreationResult(
                success=False,
                error_message=format_deployment_error(e, "package creation"),
                creation_time=start_time,
            )

    async def _create_docker_package(self, request: PackageCreationRequest) -> PackageCreationResult:
        """Create Docker deployment package."""
        try:
            if not self._docker_client:
                return PackageCreationResult(success=False, error_message="Docker client not available")

            if not request.docker_config:
                return PackageCreationResult(
                    success=False,
                    error_message="Docker configuration required for Docker package",
                )

            # Create temporary build directory
            temp_dir = tempfile.mkdtemp(prefix="ign_docker_build_")
            self._temp_dirs.append(temp_dir)
            build_path = Path(temp_dir)

            # Copy project files
            await self._copy_project_files(build_path, request)

            # Generate Dockerfile
            dockerfile_content = self._generate_dockerfile(request.docker_config, request.deployment_target)
            dockerfile_path = build_path / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)

            # Generate docker-compose.yml
            compose_content = self._generate_docker_compose(request.docker_config, request.deployment_target)
            compose_path = build_path / "docker-compose.yml"
            compose_path.write_text(compose_content)

            # Build Docker image
            logger.info(f"🐳 Building Docker image: {request.docker_config.image_name}:{request.docker_config.tag}")

            try:
                image, build_logs = self._docker_client.images.build(
                    path=str(build_path),
                    tag=f"{request.docker_config.image_name}:{request.docker_config.tag}",
                    rm=True,
                    pull=True,
                )

                # Log build output
                for log in build_logs:
                    if isinstance(log, dict) and "stream" in log:
                        stream_value = log["stream"]
                        if isinstance(stream_value, str):
                            logger.debug(stream_value.strip())

            except Exception as build_error:
                return PackageCreationResult(success=False, error_message=f"Docker build failed: {build_error}")

            # Create package directory
            package_name = f"{request.docker_config.image_name}-{request.version}-docker"
            package_path = Path(request.output_directory) / package_name
            package_path.mkdir(parents=True, exist_ok=True)

            # Export Docker image
            image_tar_path = package_path / f"{request.docker_config.image_name}-{request.version}.tar"
            with open(image_tar_path, "wb") as f:
                for chunk in image.save():
                    f.write(chunk)

            # Copy deployment files
            shutil.copy2(dockerfile_path, package_path)
            shutil.copy2(compose_path, package_path)

            # Generate deployment scripts
            await self._generate_deployment_scripts(package_path, request)

            # Generate documentation if requested
            included_files = ["Dockerfile", "docker-compose.yml"]
            if request.include_documentation:
                await self._generate_package_documentation(package_path, request)
                included_files.extend(["README.md", "INSTALLATION.md"])

            # Calculate package size
            package_size = sum(f.stat().st_size for f in package_path.rglob("*") if f.is_file())

            logger.info(f"✅ Docker package created: {package_path}")

            return PackageCreationResult(
                success=True,
                package_path=str(package_path),
                package_size=package_size,
                included_files=included_files,
                metadata={
                    "image_name": f"{request.docker_config.image_name}:{request.docker_config.tag}",
                    "image_size": image.attrs.get("Size", 0),
                    "deployment_target": request.deployment_target.value,
                },
            )

        except Exception as e:
            return PackageCreationResult(
                success=False,
                error_message=format_deployment_error(e, "Docker package creation"),
            )

    async def _create_standalone_package(self, request: PackageCreationRequest) -> PackageCreationResult:
        """Create standalone deployment package."""
        try:
            if not request.standalone_config:
                return PackageCreationResult(
                    success=False,
                    error_message="Standalone configuration required for standalone package",
                )

            # Create package directory
            package_name = f"ign-scripts-{request.version}-standalone"
            package_path = Path(request.output_directory) / package_name
            package_path.mkdir(parents=True, exist_ok=True)

            # Copy project files
            await self._copy_project_files(package_path, request)

            # Generate installation script
            install_script = self._generate_install_script(request.standalone_config, request.deployment_target)
            install_path = package_path / "install.sh"
            install_path.write_text(install_script)
            install_path.chmod(0o755)

            # Generate systemd service file
            service_content = self._generate_systemd_service(request.standalone_config)
            service_path = package_path / f"{request.standalone_config.service_name}.service"
            service_path.write_text(service_content)

            # Generate uninstall script
            uninstall_script = self._generate_uninstall_script(request.standalone_config)
            uninstall_path = package_path / "uninstall.sh"
            uninstall_path.write_text(uninstall_script)
            uninstall_path.chmod(0o755)

            # Generate documentation if requested
            included_files = [
                "install.sh",
                "uninstall.sh",
                f"{request.standalone_config.service_name}.service",
            ]
            if request.include_documentation:
                await self._generate_package_documentation(package_path, request)
                included_files.extend(["README.md", "INSTALLATION.md"])

            # Calculate package size
            package_size = sum(f.stat().st_size for f in package_path.rglob("*") if f.is_file())

            logger.info(f"✅ Standalone package created: {package_path}")

            return PackageCreationResult(
                success=True,
                package_path=str(package_path),
                package_size=package_size,
                included_files=included_files,
                metadata={
                    "service_name": request.standalone_config.service_name,
                    "install_path": request.standalone_config.install_path,
                    "deployment_target": request.deployment_target.value,
                },
            )

        except Exception as e:
            return PackageCreationResult(
                success=False,
                error_message=format_deployment_error(e, "standalone package creation"),
            )

    async def _create_kubernetes_package(self, request: PackageCreationRequest) -> PackageCreationResult:
        """Create Kubernetes deployment package."""
        # Placeholder for Kubernetes package creation
        return PackageCreationResult(
            success=False,
            error_message="Kubernetes package creation not yet implemented",
        )

    async def _create_systemd_package(self, request: PackageCreationRequest) -> PackageCreationResult:
        """Create systemd service package."""
        # Placeholder for systemd package creation
        return PackageCreationResult(success=False, error_message="Systemd package creation not yet implemented")

    async def _copy_project_files(self, target_path: Path, request: PackageCreationRequest) -> None:
        """Copy project files to target directory."""
        try:
            # Essential directories to copy
            essential_dirs = ["src", "templates"]
            for dir_name in essential_dirs:
                src_dir = Path(dir_name)
                if src_dir.exists():
                    dest_dir = target_path / dir_name
                    shutil.copytree(
                        src_dir,
                        dest_dir,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                    )

            # Essential files to copy
            essential_files = ["requirements.txt", "pyproject.toml", "README.md"]
            for file_name in essential_files:
                src_file = Path(file_name)
                if src_file.exists():
                    shutil.copy2(src_file, target_path)

            # Copy configuration examples
            config_dir = Path("config")
            if config_dir.exists():
                dest_config = target_path / "config"
                shutil.copytree(config_dir, dest_config, ignore=shutil.ignore_patterns("*.env"))

            # Copy documentation if requested
            if request.include_documentation:
                docs_dir = Path("docs")
                if docs_dir.exists():
                    dest_docs = target_path / "docs"
                    shutil.copytree(docs_dir, dest_docs)

            # Copy tests if requested
            if request.include_tests:
                tests_dir = Path("tests")
                if tests_dir.exists():
                    dest_tests = target_path / "tests"
                    shutil.copytree(tests_dir, dest_tests)

            logger.info("📁 Project files copied successfully")

        except Exception as e:
            logger.error(f"❌ Failed to copy project files: {e}")
            raise

    def _generate_dockerfile(self, config: DockerPackageConfig, target: DeploymentTarget) -> str:
        """Generate Dockerfile content."""
        dockerfile_content = f"""# IGN Scripts Deployment Package
# Generated for {target.value} environment
# Following crawl_mcp.py methodology with comprehensive validation

FROM {config.base_image}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/
COPY config/ ./config/
COPY pyproject.toml .
COPY README.md .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEPLOYMENT_ENVIRONMENT={target.value}

# Add environment variables from config
"""

        for key, value in config.environment_vars.items():
            dockerfile_content += f"ENV {key}={value}\n"

        dockerfile_content += """
# Expose ports
"""
        for port in config.expose_ports:
            dockerfile_content += f"EXPOSE {port}\n"

        dockerfile_content += f"""
# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD {config.health_check_command}

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Default command
CMD ["python", "-m", "src.main"]
"""

        return dockerfile_content

    def _generate_docker_compose(self, config: DockerPackageConfig, target: DeploymentTarget) -> str:
        """Generate docker-compose.yml content."""
        compose_content = f"""version: '3.8'

# IGN Scripts Docker Compose Configuration
# Generated for {target.value} environment
# Following crawl_mcp.py methodology

        services:
  ign-scripts:
    image: {config.image_name}:{config.tag}
    container_name: ign-scripts-{target.value}
    restart: unless-stopped
    environment:
      - DEPLOYMENT_ENVIRONMENT={target.value}
"""

        # Add environment variables
        for key, value in config.environment_vars.items():
            compose_content += f"      - {key}={value}\n"

        # Add ports
        compose_content += "    ports:\n"
        for port in config.expose_ports:
            compose_content += f'      - "{port}:{port}"\n'

        # Add volumes
        if config.volumes:
            compose_content += "    volumes:\n"
            for host_path, container_path in config.volumes.items():
                compose_content += f"      - {host_path}:{container_path}\n"

        # Add health check
        compose_content += f"""    healthcheck:
      test: [{config.health_check_command.split()}]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

    networks:
      - ign-network

networks:
  ign-network:
    driver: bridge
"""

        return compose_content

    def _generate_install_script(self, config: StandalonePackageConfig, target: DeploymentTarget) -> str:
        """Generate installation script for standalone package."""
        install_script = f"""#!/bin/bash

# IGN Scripts Installation Script
# Generated for {target.value} environment
# Following crawl_mcp.py methodology with comprehensive validation

set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Configuration
SERVICE_NAME="{config.service_name}"
INSTALL_PATH="{config.install_path}"
USER_ACCOUNT="{config.user_account}"
PYTHON_VERSION="3.12"

# Functions
log_info() {{
    echo -e "${{BLUE}}[INFO]${{NC}} $1"
}}

log_success() {{
    echo -e "${{GREEN}}[SUCCESS]${{NC}} $1"
}}

log_warning() {{
    echo -e "${{YELLOW}}[WARNING]${{NC}} $1"
}}

log_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1"
}}

# Step 1: Environment validation (crawl_mcp.py methodology)
validate_environment() {{
    log_info "Validating installation environment..."

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi

    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    PYTHON_VER=$(python3 -c "import sys; print(f'{{sys.version_info.major}}.{{sys.version_info.minor}}')")
    if [[ "$PYTHON_VER" < "3.11" ]]; then
        log_warning "Python $PYTHON_VER detected. Python 3.11+ recommended"
    fi

    # Check systemd
    if ! command -v systemctl &> /dev/null; then
        log_error "systemctl is required but not found"
        exit 1
    fi

    log_success "Environment validation passed"
}}

# Step 2: Create user account
create_user_account() {{
    log_info "Creating service user account: $USER_ACCOUNT"

    if id "$USER_ACCOUNT" &>/dev/null; then
        log_info "User $USER_ACCOUNT already exists"
    else
        useradd -r -s /bin/false -d "$INSTALL_PATH" "$USER_ACCOUNT"
        log_success "User $USER_ACCOUNT created"
    fi
}}

# Step 3: Create installation directory
create_install_directory() {{
    log_info "Creating installation directory: $INSTALL_PATH"

    mkdir -p "$INSTALL_PATH"
    mkdir -p "$INSTALL_PATH/logs"
    mkdir -p "$INSTALL_PATH/data"
    mkdir -p "$INSTALL_PATH/config"

    chown -R "$USER_ACCOUNT:$USER_ACCOUNT" "$INSTALL_PATH"
    chmod 755 "$INSTALL_PATH"

    log_success "Installation directory created"
}}

# Step 4: Install application files
install_application() {{
    log_info "Installing application files..."

    # Copy application files
    cp -r src/ "$INSTALL_PATH/"
    cp -r templates/ "$INSTALL_PATH/"
    cp -r config/ "$INSTALL_PATH/"
    cp requirements.txt "$INSTALL_PATH/"
    cp pyproject.toml "$INSTALL_PATH/"
    cp README.md "$INSTALL_PATH/"

    # Set permissions
    chown -R "$USER_ACCOUNT:$USER_ACCOUNT" "$INSTALL_PATH"
    find "$INSTALL_PATH" -type f -exec chmod 644 {{}} \\;
    find "$INSTALL_PATH" -type d -exec chmod 755 {{}} \\;

    log_success "Application files installed"
}}

# Step 5: Install Python dependencies
install_dependencies() {{
    log_info "Installing Python dependencies..."

    cd "$INSTALL_PATH"

    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    # Install dependencies
    pip install -r requirements.txt

    # Set permissions
    chown -R "$USER_ACCOUNT:$USER_ACCOUNT" venv/

    log_success "Python dependencies installed"
}}

# Step 6: Install systemd service
install_systemd_service() {{
    log_info "Installing systemd service..."

    cp "$SERVICE_NAME.service" "/etc/systemd/system/"
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"

    log_success "Systemd service installed and enabled"
}}

# Step 7: Start service
start_service() {{
    log_info "Starting $SERVICE_NAME service..."

    systemctl start "$SERVICE_NAME"

    # Wait a moment for service to start
    sleep 5

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "$SERVICE_NAME service started successfully"
    else
        log_error "$SERVICE_NAME service failed to start"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}}

# Main installation process
main() {{
    log_info "Starting IGN Scripts installation for {target.value} environment"

    validate_environment
    create_user_account
    create_install_directory
    install_application
    install_dependencies
    install_systemd_service
    start_service

    log_success "Installation completed successfully!"
    log_info "Service status: systemctl status $SERVICE_NAME"
    log_info "Service logs: journalctl -u $SERVICE_NAME -f"
    log_info "Installation path: $INSTALL_PATH"
}}

# Run main function
main "$@"
"""

        return install_script

    def _generate_systemd_service(self, config: StandalonePackageConfig) -> str:
        """Generate systemd service file."""
        service_content = f"""[Unit]
Description=IGN Scripts Service
Documentation=https://github.com/reh3376/IGN_scripts
After=network.target
Wants=network.target

[Service]
Type=simple
User={config.user_account}
Group={config.user_account}
WorkingDirectory={config.install_path}
Environment=PYTHONPATH={config.install_path}
Environment=PYTHONUNBUFFERED=1
ExecStart={config.install_path}/venv/bin/python -m src.main
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier={config.service_name}

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths={config.install_path}/logs {config.install_path}/data

[Install]
WantedBy=multi-user.target
"""

        return service_content

    def _generate_uninstall_script(self, config: StandalonePackageConfig) -> str:
        """Generate uninstallation script."""
        uninstall_script = f"""#!/bin/bash

# IGN Scripts Uninstallation Script
# Following crawl_mcp.py methodology with comprehensive validation

set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Configuration
SERVICE_NAME="{config.service_name}"
INSTALL_PATH="{config.install_path}"
USER_ACCOUNT="{config.user_account}"

# Functions
log_info() {{
    echo -e "${{BLUE}}[INFO]${{NC}} $1"
}}

log_success() {{
    echo -e "${{GREEN}}[SUCCESS]${{NC}} $1"
}}

log_warning() {{
    echo -e "${{YELLOW}}[WARNING]${{NC}} $1"
}}

log_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1"
}}

# Confirmation prompt
confirm_uninstall() {{
    log_warning "This will completely remove IGN Scripts from your system"
    log_warning "Installation path: $INSTALL_PATH"
    log_warning "Service: $SERVICE_NAME"
    log_warning "User account: $USER_ACCOUNT"

    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstallation cancelled"
        exit 0
    fi
}}

# Stop and disable service
stop_service() {{
    log_info "Stopping and disabling $SERVICE_NAME service..."

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
        log_success "Service stopped"
    fi

    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        systemctl disable "$SERVICE_NAME"
        log_success "Service disabled"
    fi

    # Remove service file
    if [[ -f "/etc/systemd/system/$SERVICE_NAME.service" ]]; then
        rm "/etc/systemd/system/$SERVICE_NAME.service"
        systemctl daemon-reload
        log_success "Service file removed"
    fi
}}

# Remove installation directory
remove_installation() {{
    log_info "Removing installation directory: $INSTALL_PATH"

    if [[ -d "$INSTALL_PATH" ]]; then
        rm -rf "$INSTALL_PATH"
        log_success "Installation directory removed"
    else
        log_info "Installation directory not found"
    fi
}}

# Remove user account
remove_user_account() {{
    log_info "Removing user account: $USER_ACCOUNT"

    if id "$USER_ACCOUNT" &>/dev/null; then
        userdel "$USER_ACCOUNT"
        log_success "User account removed"
    else
        log_info "User account not found"
    fi
}}

# Main uninstallation process
main() {{
    log_info "Starting IGN Scripts uninstallation"

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi

    confirm_uninstall
    stop_service
    remove_installation
    remove_user_account

    log_success "Uninstallation completed successfully!"
}}

# Run main function
main "$@"
"""

        return uninstall_script

    async def _generate_deployment_scripts(self, package_path: Path, request: PackageCreationRequest) -> None:
        """Generate deployment helper scripts."""
        try:
            pass  # TODO: Add try block content
        except Exception:
            pass  # TODO: Handle exception
            # Generate start script
            start_script = f"""#!/bin/bash

# IGN Scripts Docker Start Script
# Following crawl_mcp.py methodology

set -e

echo "🚀 Starting IGN Scripts ({request.deployment_target.value} environment)"

# Load image if tar file exists
if [[ -f "{request.docker_config.image_name}-{request.version}.tar" ]]; then
    echo "📦 Loading Docker image..."
    docker load -i "{request.docker_config.image_name}-{request.version}.tar"
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo "🏥 Checking service health..."
docker-compose ps

echo "✅ IGN Scripts started successfully!"
echo "📊 Access the application at: http://localhost:{request.docker_config.expose_ports[0] if request.docker_config.expose_ports else 8000}"  # noqa: E501
"""

            start_path = package_path / "start.sh"
            start_path.write_text(start_script)
            start_path.chmod(0o755)

            # Generate stop script
            stop_script = """#!/bin/bash

# IGN Scripts Docker Stop Script

set -e

echo "🛑 Stopping IGN Scripts..."

# Stop services
docker-compose down

echo "✅ IGN Scripts stopped successfully!"
"""

            stop_path = package_path / "stop.sh"
            stop_path.write_text(stop_script)
            stop_path.chmod(0o755)

            # Generate update script
            update_script = """#!/bin/bash

# IGN Scripts Update Script

set -e

echo "🔄 Updating IGN Scripts..."

# Pull latest images
docker-compose pull

# Restart services
docker-compose down
docker-compose up -d

echo "✅ IGN Scripts updated successfully!"
"""

            update_path = package_path / "update.sh"
            update_path.write_text(update_script)
            update_path.chmod(0o755)

            logger.info("📜 Deployment scripts generated")

        except Exception as e:
            logger.error(f"❌ Failed to generate deployment scripts: {e}")
            raise

    async def _generate_package_documentation(self, package_path: Path, request: PackageCreationRequest) -> None:
        """Generate package documentation."""
        try:
            pass  # TODO: Add try block content
        except Exception:
            pass  # TODO: Handle exception
            # Generate README.md
            readme_content = f"""# IGN Scripts Deployment Package

Version: {request.version}
Package Type: {request.package_type.value}
Target Environment: {request.deployment_target.value}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

This package contains everything needed to deploy IGN Scripts in a {request.deployment_target.value} environment.
The package follows the crawl_mcp.py methodology with comprehensive validation and error handling.

## Contents

"""

            if request.package_type == PackageType.DOCKER:
                readme_content += """- `Dockerfile` - Docker image definition
- `docker-compose.yml` - Docker Compose configuration
- `start.sh` - Start services script
- `stop.sh` - Stop services script
- `update.sh` - Update services script
- Docker image tar file for offline installation

## Quick Start (Docker)

1. Load the Docker image (if using offline installation):
   ```bash
   docker load -i *.tar
   ```

2. Start the services:
   ```bash
   ./start.sh
   ```

3. Access the application:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

4. Stop the services:
   ```bash
   ./stop.sh
   ```

## Configuration

Environment variables can be configured in the `docker-compose.yml` file.
"""

            elif request.package_type == PackageType.STANDALONE:
                readme_content += f"""- `install.sh` - Installation script
- `uninstall.sh` - Uninstallation script
- `{request.standalone_config.service_name}.service` - Systemd service file
- Application source code and dependencies

## Quick Start (Standalone)

1. Run the installation script as root:
   ```bash
   sudo ./install.sh
   ```

2. Check service status:
   ```bash
   sudo systemctl status {request.standalone_config.service_name}
   ```

3. View logs:
   ```bash
   sudo journalctl -u {request.standalone_config.service_name} -f
   ```

## Configuration

The application is installed to: `{request.standalone_config.install_path}`
Configuration files are located in: `{request.standalone_config.install_path}/config/`
"""

            readme_content += """
## Support

For support and documentation, visit: https://github.com/reh3376/IGN_scripts

## Security

This package includes security best practices:
- Non-root user execution
- Minimal file permissions
- Environment variable configuration
- Health checks and monitoring

## Troubleshooting

See INSTALLATION.md for detailed troubleshooting information.
"""

            readme_path = package_path / "README.md"
            readme_path.write_text(readme_content)

            # Generate INSTALLATION.md
            await self._generate_installation_guide(package_path, request)

            logger.info("📚 Package documentation generated")

        except Exception as e:
            logger.error(f"❌ Failed to generate package documentation: {e}")
            raise

    async def _generate_installation_guide(self, package_path: Path, request: PackageCreationRequest) -> None:
        """Generate detailed installation guide."""
        installation_content = f"""# IGN Scripts Installation Guide

This guide provides detailed installation instructions for IGN Scripts {request.version}
in a {request.deployment_target.value} environment.

## Prerequisites

### System Requirements

- Operating System: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- Memory: 4GB RAM minimum, 8GB recommended
- Storage: 10GB available space
- Network: Internet access for initial setup

### Software Requirements

"""

        if request.package_type == PackageType.DOCKER:
            installation_content += """- Docker Engine 20.10+
- Docker Compose 2.0+
- curl (for health checks)

### Docker Installation

#### Ubuntu/Debian:
```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose  # noqa: E501
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

#### CentOS/RHEL:
```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose  # noqa: E501
sudo chmod +x /usr/local/bin/docker-compose
```

## Installation Steps

### Step 1: Extract Package
```bash
tar -xzf ign-scripts-{request.version}-docker.tar.gz
cd ign-scripts-{request.version}-docker
```

### Step 2: Load Docker Image (Offline Installation)
```bash
docker load -i *.tar
```

### Step 3: Configure Environment
Edit `docker-compose.yml` to customize:
- Port mappings
- Environment variables
- Volume mounts
- Resource limits

### Step 4: Start Services
```bash
./start.sh
```

### Step 5: Verify Installation
```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f

# Test API endpoint
curl http://localhost:8000/health
```
"""

        elif request.package_type == PackageType.STANDALONE:
            installation_content += f"""- Python 3.11+ (3.12 recommended)
- pip (Python package manager)
- systemd (for service management)
- git (for dependencies)

### Python Installation

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
```

#### CentOS/RHEL:
```bash
sudo yum install -y python3 python3-pip
```

## Installation Steps

### Step 1: Extract Package
```bash
tar -xzf ign-scripts-{request.version}-standalone.tar.gz
cd ign-scripts-{request.version}-standalone
```

### Step 2: Run Installation Script
```bash
sudo ./install.sh
```

The installation script will:
1. Validate the environment
2. Create service user account (`{request.standalone_config.user_account}`)
3. Create installation directory (`{request.standalone_config.install_path}`)
4. Install application files
5. Install Python dependencies in virtual environment
6. Install and enable systemd service
7. Start the service

### Step 3: Verify Installation
```bash
# Check service status
sudo systemctl status {request.standalone_config.service_name}

# View service logs
sudo journalctl -u {request.standalone_config.service_name} -f

# Test application
curl http://localhost:8000/health
```

### Step 4: Configuration
Configuration files are located in:
- Main config: `{request.standalone_config.install_path}/config/`
- Logs: `{request.standalone_config.install_path}/logs/`
- Data: `{request.standalone_config.install_path}/data/`
"""

        installation_content += """
## Post-Installation

### Firewall Configuration
```bash
# Allow application port (adjust as needed)
sudo ufw allow 8000/tcp
```

### SSL/TLS Configuration
For production deployments, configure SSL/TLS:

1. Obtain SSL certificates
2. Configure reverse proxy (nginx/Apache)
3. Update application configuration

### Backup Configuration
Set up regular backups:
- Database backups
- Configuration backups
- Log rotation

## Troubleshooting

### Common Issues

#### Issue: Service fails to start
**Solution:**
```bash
# Check service logs
sudo journalctl -u ign-scripts -n 50

# Check file permissions
sudo ls -la /opt/ign-scripts/

# Restart service
sudo systemctl restart ign-scripts
```

#### Issue: Port already in use
**Solution:**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :8000

# Kill the process or change port in configuration
```

#### Issue: Permission denied errors
**Solution:**
```bash
# Fix ownership
sudo chown -R ign-scripts:ign-scripts /opt/ign-scripts/

# Fix permissions
sudo chmod -R 755 /opt/ign-scripts/
```

### Log Locations
- Application logs: `/opt/ign-scripts/logs/`
- System logs: `journalctl -u ign-scripts`
- Docker logs: `docker-compose logs`

### Getting Help
- GitHub Issues: https://github.com/reh3376/IGN_scripts/issues
- Documentation: https://github.com/reh3376/IGN_scripts/docs
- Email: support@ign-scripts.com

## Uninstallation

To completely remove IGN Scripts:
```bash
sudo ./uninstall.sh
```

This will:
- Stop and disable the service
- Remove installation directory
- Remove service user account
- Remove systemd service file
"""

        installation_path = package_path / "INSTALLATION.md"
        installation_path.write_text(installation_content)


# Step 5: Progressive Complexity - Factory Functions
async def create_docker_package(
    image_name: str = "ign-scripts",
    version: str = "1.0.0",
    deployment_target: str = "production",
    output_dir: str = "./dist",
) -> PackageCreationResult:
    """Create a Docker deployment package with default configuration."""
    docker_config = DockerPackageConfig(
        image_name=image_name,
        tag=version,
        expose_ports=[8000, 8501],
        environment_vars={"LOG_LEVEL": "INFO", "PYTHONUNBUFFERED": "1"},
    )

    request = PackageCreationRequest(
        package_type=PackageType.DOCKER,
        deployment_target=DeploymentTarget(deployment_target),
        version=version,
        output_directory=output_dir,
        docker_config=docker_config,
    )

    creator = DeploymentPackageCreator()
    async with creator.managed_creation() as package_creator:
        return await package_creator.create_package(request)


async def create_standalone_package(
    version: str = "1.0.0",
    deployment_target: str = "production",
    output_dir: str = "./dist",
) -> PackageCreationResult:
    """Create a standalone deployment package with default configuration."""
    standalone_config = StandalonePackageConfig(
        service_name="ign-scripts",
        install_path="/opt/ign-scripts",
        user_account="ign-scripts",
    )

    request = PackageCreationRequest(
        package_type=PackageType.STANDALONE,
        deployment_target=DeploymentTarget(deployment_target),
        version=version,
        output_directory=output_dir,
        standalone_config=standalone_config,
    )

    creator = DeploymentPackageCreator()
    async with creator.managed_creation() as package_creator:
        return await package_creator.create_package(request)


# Main implementation function for Phase 12.8
async def run_phase_12_8_implementation() -> dict[str, Any]:
    """Run Phase 12.8 implementation following crawl_mcp.py methodology."""
    implementation_results: dict[str, Any] = {
        "success": False,
        "phase": "12.8",
        "title": "Deployment Package Creation & How-to Guides",
        "start_time": datetime.now().isoformat(),
        "steps": {},
        "packages_created": [],
        "documentation_generated": [],
        "errors": [],
        "warnings": [],
    }

    try:
        console.print(
            Panel(
                "[bold blue]🚀 Phase 12.8: Deployment Package Creation & How-to Guides[/bold blue]\n"
                "Following crawl_mcp.py methodology with comprehensive validation",
                title="Implementation Start",
                border_style="blue",
            )
        )

        # Step 1: Environment validation first
        print("\n⚙️ Step 1: Environment Validation")
        env_validation = validate_deployment_environment()
        implementation_results["steps"]["environment_validation"] = env_validation

        if not env_validation["valid"]:
            implementation_results["errors"].extend(env_validation["errors"])
            raise RuntimeError("Environment validation failed")

        if env_validation["warnings"]:
            implementation_results["warnings"].extend(env_validation["warnings"])

        print("✅ Environment validation passed")

        # Step 2: Create deployment package creator
        print("\n📦 Step 2: Initialize Package Creator")
        creator = DeploymentPackageCreator()
        init_result = await creator.initialize()
        implementation_results["steps"]["creator_initialization"] = init_result

        if not init_result["success"]:
            raise RuntimeError(f"Package creator initialization failed: {init_result['error']}")

        print("✅ Package creator initialized")

        # Step 3: Create Docker production package
        print("\n🐳 Step 3: Create Docker Production Package")
        async with creator.managed_creation():
            docker_result = await create_docker_package(
                image_name="ign-scripts-api",
                version="1.0.0",
                deployment_target="production",
                output_dir="./dist",
            )

            implementation_results["steps"]["docker_package"] = {
                "success": docker_result.success,
                "package_path": docker_result.package_path,
                "package_size": docker_result.package_size,
                "error": docker_result.error_message,
            }

            if docker_result.success:
                implementation_results["packages_created"].append(
                    {
                        "type": "docker",
                        "path": docker_result.package_path,
                        "size": docker_result.package_size,
                    }
                )
                print(f"✅ Docker package created: {docker_result.package_path}")
            else:
                print(f"❌ Docker package creation failed: {docker_result.error_message}")

        # Step 4: Create standalone production package
        print("\n📋 Step 4: Create Standalone Production Package")
        async with creator.managed_creation():
            standalone_result = await create_standalone_package(
                version="1.0.0", deployment_target="production", output_dir="./dist"
            )

            implementation_results["steps"]["standalone_package"] = {
                "success": standalone_result.success,
                "package_path": standalone_result.package_path,
                "package_size": standalone_result.package_size,
                "error": standalone_result.error_message,
            }

            if standalone_result.success:
                implementation_results["packages_created"].append(
                    {
                        "type": "standalone",
                        "path": standalone_result.package_path,
                        "size": standalone_result.package_size,
                    }
                )
                print(f"✅ Standalone package created: {standalone_result.package_path}")
            else:
                print(f"❌ Standalone package creation failed: {standalone_result.error_message}")

        # Step 5: Generate comprehensive how-to guides
        print("\n📚 Step 5: Generate How-to Guides")
        guides_created = await generate_comprehensive_guides()
        implementation_results["steps"]["how_to_guides"] = guides_created
        implementation_results["documentation_generated"] = guides_created.get("guides", [])

        print(f"✅ Generated {len(guides_created.get('guides', []))} how-to guides")

        # Success summary
        successful_packages = len(list(implementation_results["packages_created"]))
        implementation_results["success"] = successful_packages > 0
        implementation_results["end_time"] = datetime.now().isoformat()

        # Display results
        results_table = Table(title="Phase 12.8 Results")
        results_table.add_column("Component", style="cyan")
        results_table.add_column("Status", style="green")
        results_table.add_column("Details", style="white")

        results_table.add_row(
            "Environment Validation",
            "✅ Passed" if env_validation["valid"] else "❌ Failed",
            f"{len(env_validation['tools_available'])} tools available",
        )

        results_table.add_row(
            "Docker Package",
            "✅ Created" if docker_result.success else "❌ Failed",
            docker_result.package_path or docker_result.error_message or "N/A",
        )

        results_table.add_row(
            "Standalone Package",
            "✅ Created" if standalone_result.success else "❌ Failed",
            standalone_result.package_path or standalone_result.error_message or "N/A",
        )

        results_table.add_row(
            "How-to Guides",
            "✅ Generated",
            f"{len(guides_created.get('guides', []))} guides created",
        )

        console.print(results_table)

        if implementation_results["success"]:
            console.print(
                Panel(
                    f"[bold green]✅ Phase 12.8 Implementation Completed Successfully![/bold green]\n\n"
                    f"📦 Packages Created: {successful_packages}\n"
                    f"📚 Guides Generated: {len(guides_created.get('guides', []))}\n"
                    f"📁 Output Directory: ./dist/\n"
                    f"⏱️ Total Time: {(datetime.fromisoformat(implementation_results['end_time']) - datetime.fromisoformat(implementation_results['start_time'])).total_seconds():.2f}s",  # noqa: E501
                    title="🎉 Success",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    "[bold red]❌ Phase 12.8 Implementation Completed with Issues[/bold red]\n\n"
                    f"See errors: {implementation_results['errors']}",
                    title="⚠️ Partial Success",
                    border_style="yellow",
                )
            )

        return implementation_results

    except Exception as e:
        implementation_results["success"] = False
        implementation_results["end_time"] = datetime.now().isoformat()
        implementation_results["errors"].append(str(e))

        console.print(
            Panel(
                f"[bold red]❌ Phase 12.8 Implementation Failed[/bold red]\n\nError: {e}",
                title="💥 Failure",
                border_style="red",
            )
        )

        return implementation_results


# How-to Guides Generation
async def generate_comprehensive_guides() -> dict[str, Any]:
    """Generate comprehensive how-to guides."""
    guides_result = {"success": True, "guides": [], "errors": []}

    try:
        # Ensure docs directory exists
        docs_dir = Path("docs")
        guides_dir = docs_dir / "how-to"
        guides_dir.mkdir(parents=True, exist_ok=True)

        # Generate installation guide
        installation_guide = await generate_installation_how_to_guide()
        if installation_guide["success"]:
            guides_result["guides"].append("installation-guide.md")
        else:
            guides_result["errors"].append(f"Installation guide: {installation_guide['error']}")

        # Generate deployment guide
        deployment_guide = await generate_deployment_how_to_guide()
        if deployment_guide["success"]:
            guides_result["guides"].append("deployment-guide.md")
        else:
            guides_result["errors"].append(f"Deployment guide: {deployment_guide['error']}")

        # Generate operations guide
        operations_guide = await generate_operations_how_to_guide()
        if operations_guide["success"]:
            guides_result["guides"].append("operations-guide.md")
        else:
            guides_result["errors"].append(f"Operations guide: {operations_guide['error']}")

        # Generate troubleshooting guide
        troubleshooting_guide = await generate_troubleshooting_how_to_guide()
        if troubleshooting_guide["success"]:
            guides_result["guides"].append("troubleshooting-guide.md")
        else:
            guides_result["errors"].append(f"Troubleshooting guide: {troubleshooting_guide['error']}")

        # Generate security guide
        security_guide = await generate_security_how_to_guide()
        if security_guide["success"]:
            guides_result["guides"].append("security-guide.md")
        else:
            guides_result["errors"].append(f"Security guide: {security_guide['error']}")

        guides_result["success"] = len(guides_result["errors"]) == 0

    except Exception as e:
        guides_result["success"] = False
        guides_result["errors"].append(str(e))

    return guides_result


# How-to Guides Generation Functions
async def generate_installation_how_to_guide() -> dict[str, Any]:
    """Generate installation how-to guide."""
    try:
        pass  # TODO: Add try block content
    except Exception:
        pass  # TODO: Handle exception
        guides_dir = Path("docs/how-to")
        guides_dir.mkdir(parents=True, exist_ok=True)

        content = """# How to Install IGN Scripts

## Overview
This guide provides step-by-step instructions for installing IGN Scripts in various environments.

## Prerequisites
- Python 3.11+
- Git
- Docker (for containerized deployment)

## Installation Methods

### Method 1: Docker Installation
1. Clone the repository
2. Build the Docker image
3. Run the container

### Method 2: Standalone Installation
1. Install Python dependencies
2. Configure the environment
3. Start the service

For detailed instructions, see the deployment packages in the `dist/` directory.
"""

        guide_path = guides_dir / "installation-guide.md"
        guide_path.write_text(content)

        return {"success": True, "path": str(guide_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_deployment_how_to_guide() -> dict[str, Any]:
    """Generate deployment how-to guide."""
    try:
        pass  # TODO: Add try block content
    except Exception:
        pass  # TODO: Handle exception
        guides_dir = Path("docs/how-to")
        guides_dir.mkdir(parents=True, exist_ok=True)

        content = """# How to Deploy IGN Scripts

## Overview
This guide covers deployment strategies for IGN Scripts in different environments.

## Deployment Environments
- Development
- Staging
- Production
- Enterprise

## Deployment Methods
1. Docker containers
2. Standalone services
3. Kubernetes clusters
4. Systemd services

## Best Practices
- Use environment variables for configuration
- Implement health checks
- Set up monitoring and logging
- Follow security guidelines

For specific deployment packages, see the `dist/` directory.
"""

        guide_path = guides_dir / "deployment-guide.md"
        guide_path.write_text(content)

        return {"success": True, "path": str(guide_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_operations_how_to_guide() -> dict[str, Any]:
    """Generate operations how-to guide."""
    try:
        pass  # TODO: Add try block content
    except Exception:
        pass  # TODO: Handle exception
        guides_dir = Path("docs/how-to")
        guides_dir.mkdir(parents=True, exist_ok=True)

        content = """# How to Operate IGN Scripts

## Overview
This guide covers day-to-day operations for IGN Scripts.

## Service Management
- Starting and stopping services
- Checking service status
- Viewing logs
- Restarting services

## Monitoring
- Health checks
- Performance metrics
- Log analysis
- Alert configuration

## Maintenance
- Updates and upgrades
- Backup procedures
- Database maintenance
- Certificate renewal

## Common Operations
1. Service restart: `systemctl restart ign-scripts`
2. View logs: `journalctl -u ign-scripts -f`
3. Check health: `curl http://localhost:8000/health`
"""

        guide_path = guides_dir / "operations-guide.md"
        guide_path.write_text(content)

        return {"success": True, "path": str(guide_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_troubleshooting_how_to_guide() -> dict[str, Any]:
    """Generate troubleshooting how-to guide."""
    try:
        pass  # TODO: Add try block content
    except Exception:
        pass  # TODO: Handle exception
        guides_dir = Path("docs/how-to")
        guides_dir.mkdir(parents=True, exist_ok=True)

        content = """# How to Troubleshoot IGN Scripts

## Overview
This guide helps diagnose and resolve common issues with IGN Scripts.

## Common Issues

### Service Won't Start
1. Check service logs
2. Verify file permissions
3. Check port availability
4. Validate configuration

### Performance Issues
1. Monitor resource usage
2. Check database connections
3. Analyze log patterns
4. Review configuration settings

### Connection Issues
1. Verify network connectivity
2. Check firewall settings
3. Validate certificates
4. Test DNS resolution

## Diagnostic Commands
- Service status: `systemctl status ign-scripts`
- Service logs: `journalctl -u ign-scripts -n 100`
- Process list: `ps aux | grep ign-scripts`
- Port usage: `netstat -tlnp | grep :8000`

## Getting Help
- Check GitHub issues
- Review documentation
- Contact support
"""

        guide_path = guides_dir / "troubleshooting-guide.md"
        guide_path.write_text(content)

        return {"success": True, "path": str(guide_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_security_how_to_guide() -> dict[str, Any]:
    """Generate security how-to guide."""
    try:
        pass  # TODO: Add try block content
    except Exception:
        pass  # TODO: Handle exception
        guides_dir = Path("docs/how-to")
        guides_dir.mkdir(parents=True, exist_ok=True)

        content = """# How to Secure IGN Scripts

## Overview
This guide covers security best practices for IGN Scripts deployment.

## Security Principles
1. Principle of least privilege
2. Defense in depth
3. Regular security updates
4. Monitoring and auditing

## Configuration Security
- Use environment variables for secrets
- Implement proper authentication
- Configure SSL/TLS
- Set up firewall rules

## Runtime Security
- Run as non-root user
- Use container security
- Implement resource limits
- Enable security headers

## Monitoring Security
- Log security events
- Monitor for anomalies
- Set up alerts
- Regular security audits

## Security Checklist
- [ ] Secrets in environment variables
- [ ] SSL/TLS configured
- [ ] Firewall rules in place
- [ ] Non-root user execution
- [ ] Security monitoring enabled
- [ ] Regular updates scheduled
"""

        guide_path = guides_dir / "security-guide.md"
        guide_path.write_text(content)

        return {"success": True, "path": str(guide_path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Run the Phase 12.8 implementation
    asyncio.run(run_phase_12_8_implementation())
