"""Gateway Configuration Management.

Handles environment-based configuration for Ignition Gateway connections
using python-dotenv for secure credential and connection management.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class GatewayConfig:
    """Configuration for a single Ignition Gateway connection."""

    name: str
    host: str
    port: int = 8088
    use_https: bool = True
    username: str | None = None
    password: str | None = None
    auth_type: str = "basic"  # basic, ntlm, sso, token
    token: str | None = None
    timeout: int = 30
    verify_ssl: bool = True
    project_name: str | None = None
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.host:
            raise ValueError("Gateway host is required")

        if self.auth_type == "basic" and (not self.username or not self.password):
            raise ValueError("Username and password required for basic authentication")

        if self.auth_type == "token" and not self.token:
            raise ValueError("Token required for token authentication")

    @property
    def base_url(self) -> str:
        """Get the base URL for the gateway."""
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}"

    @property
    def api_url(self) -> str:
        """Get the API base URL for the gateway."""
        return f"{self.base_url}/main/system/webdev"

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "use_https": self.use_https,
            "username": self.username,
            "password": "***" if self.password else None,  # Mask password
            "auth_type": self.auth_type,
            "token": "***" if self.token else None,  # Mask token
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl,
            "project_name": self.project_name,
            "description": self.description,
            "tags": self.tags,
        }


class GatewayConfigManager:
    """Manages multiple gateway configurations using environment variables."""

    def __init__(self, env_file: str | None = None):
        """Initialize the configuration manager.

        Args:
            env_file: Path to .env file. If None, searches for .env in current directory
        """
        self.env_file = env_file or ".env"
        self.configs: dict[str, GatewayConfig] = {}
        self._load_environment()
        self._load_gateway_configs()

    def _load_environment(self) -> list[Any]:
        """Load environment variables from .env file."""
        env_path = Path(self.env_file)
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment variables from {env_path}")
        else:
            logger.warning(f"Environment file {env_path} not found")

    def _load_gateway_configs(self) -> list[Any]:
        """Load gateway configurations from environment variables."""
        # Get list of configured gateways
        gateway_names = self._get_gateway_names()

        for name in gateway_names:
            try:
                config = self._load_gateway_config(name)
                self.configs[name] = config
                logger.info(f"Loaded configuration for gateway: {name}")
            except Exception as e:
                logger.error(f"Failed to load configuration for gateway {name}: {e}")

    def _get_gateway_names(self) -> list[str]:
        """Get list of configured gateway names from environment."""
        gateways_env = os.getenv("IGN_GATEWAYS", "")
        if not gateways_env:
            logger.warning("No gateways configured. Set IGN_GATEWAYS environment variable")
            return []

        return [name.strip() for name in gateways_env.split(",") if name.strip()]

    def _load_gateway_config(self, name: str) -> GatewayConfig:
        """Load configuration for a specific gateway."""
        prefix = f"IGN_{name.upper()}_"

        # Required fields
        host = os.getenv(f"{prefix}HOST")
        if not host:
            raise ValueError(f"Host not configured for gateway {name}")

        # Optional fields with defaults
        config = GatewayConfig(
            name=name,
            host=host,
            port=int(os.getenv(f"{prefix}PORT", "8088")),
            use_https=os.getenv(f"{prefix}HTTPS", "true").lower() == "true",
            username=os.getenv(f"{prefix}USERNAME"),
            password=os.getenv(f"{prefix}PASSWORD"),
            auth_type=os.getenv(f"{prefix}AUTH_TYPE", "basic"),
            token=os.getenv(f"{prefix}TOKEN"),
            timeout=int(os.getenv(f"{prefix}TIMEOUT", "30")),
            verify_ssl=os.getenv(f"{prefix}VERIFY_SSL", "true").lower() == "true",
            project_name=os.getenv(f"{prefix}PROJECT"),
            description=os.getenv(f"{prefix}DESCRIPTION", ""),
            tags=self._parse_tags(os.getenv(f"{prefix}TAGS", "")),
        )

        return config

    def _parse_tags(self, tags_str: str) -> list[str]:
        """Parse tags from comma-separated string."""
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(",") if tag.strip()]

    def get_config(self, name: str) -> GatewayConfig | None:
        """Get configuration for a specific gateway."""
        return self.configs.get(name)

    def get_all_configs(self) -> dict[str, GatewayConfig]:
        """Get all gateway configurations."""
        return self.configs.copy()

    def get_config_names(self) -> list[str]:
        """Get list of configured gateway names."""
        return list(self.configs.keys())

    def has_config(self, name: str) -> bool:
        """Check if a gateway configuration exists."""
        return name in self.configs

    def add_config(self, config: GatewayConfig) -> bool:
        """Add a new gateway configuration."""
        self.configs[config.name] = config
        logger.info(f"Added configuration for gateway: {config.name}")

    def remove_config(self, name: str) -> bool:
        """Remove a gateway configuration."""
        if name in self.configs:
            del self.configs[name]
            logger.info(f"Removed configuration for gateway: {name}")
            return True
        return False

    def validate_all_configs(self) -> dict[str, list[str]]:
        """Validate all configurations and return any errors."""
        errors = {}

        for name, config in self.configs.items():
            config_errors = []

            try:
                # Validate URL format
                parsed = urlparse(config.base_url)
                if not parsed.scheme or not parsed.netloc:
                    config_errors.append("Invalid URL format")

                # Validate authentication
                if config.auth_type == "basic":
                    if not config.username or not config.password:
                        config_errors.append("Username and password required for basic auth")
                elif config.auth_type == "token" and not config.token:
                    config_errors.append("Token required for token auth")

                # Validate port range
                if not (1 <= config.port <= 65535):
                    config_errors.append("Port must be between 1 and 65535")

                # Validate timeout
                if config.timeout <= 0:
                    config_errors.append("Timeout must be positive")

            except Exception as e:
                config_errors.append(f"Configuration error: {e}")

            if config_errors:
                errors[name] = config_errors

        return errors

    def create_sample_env_file(self, file_path: str = ".env.sample") -> bool:
        """Create a sample .env file with gateway configuration examples."""
        try:
            sample_content = self._generate_sample_env_content()

            with open(file_path, "w") as f:
                f.write(sample_content)

            logger.info(f"Created sample environment file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create sample environment file: {e}")
            return False

    def _generate_sample_env_content(self) -> str:
        """Generate sample .env file content."""
        return """# IGN Scripts - Ignition Gateway Configuration
# Copy this file to .env and configure your gateway connections

# =============================================================================
# GATEWAY CONFIGURATION
# =============================================================================

# List of gateway names (comma-separated)
IGN_GATEWAYS=development,production,staging

# =============================================================================
# DEVELOPMENT GATEWAY
# =============================================================================
IGN_DEVELOPMENT_HOST=localhost
IGN_DEVELOPMENT_PORT=8088
IGN_DEVELOPMENT_HTTPS=false
IGN_DEVELOPMENT_USERNAME=admin
IGN_DEVELOPMENT_PASSWORD=password
IGN_DEVELOPMENT_AUTH_TYPE=basic
IGN_DEVELOPMENT_PROJECT=MyProject
IGN_DEVELOPMENT_DESCRIPTION=Development gateway for testing
IGN_DEVELOPMENT_TAGS=dev,testing,local
IGN_DEVELOPMENT_TIMEOUT=30
IGN_DEVELOPMENT_VERIFY_SSL=false

# =============================================================================
# PRODUCTION GATEWAY
# =============================================================================
IGN_PRODUCTION_HOST=prod-gateway.company.com
IGN_PRODUCTION_PORT=8443
IGN_PRODUCTION_HTTPS=true
IGN_PRODUCTION_USERNAME=prod_user
IGN_PRODUCTION_PASSWORD=secure_production_password
IGN_PRODUCTION_AUTH_TYPE=basic
IGN_PRODUCTION_PROJECT=ProductionApp
IGN_PRODUCTION_DESCRIPTION=Production Ignition Gateway
IGN_PRODUCTION_TAGS=prod,critical,monitored
IGN_PRODUCTION_TIMEOUT=60
IGN_PRODUCTION_VERIFY_SSL=true

# =============================================================================
# STAGING GATEWAY (with token authentication)
# =============================================================================
IGN_STAGING_HOST=staging-gateway.company.com
IGN_STAGING_PORT=8088
IGN_STAGING_HTTPS=true
IGN_STAGING_AUTH_TYPE=token
IGN_STAGING_TOKEN=your_api_token_here
IGN_STAGING_PROJECT=StagingApp
IGN_STAGING_DESCRIPTION=Staging environment for testing
IGN_STAGING_TAGS=staging,test,pre-prod
IGN_STAGING_TIMEOUT=45
IGN_STAGING_VERIFY_SSL=true

# =============================================================================
# GLOBAL SETTINGS
# =============================================================================

# Default timeout for all connections (can be overridden per gateway)
IGN_DEFAULT_TIMEOUT=30

# Enable debug logging
IGN_DEBUG=false

# Log file location
IGN_LOG_FILE=logs/ignition_gateway.log
"""

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all configured gateways."""
        summary: dict[str, Any] = {
            "total_gateways": len(self.configs),
            "gateway_names": list(self.configs.keys()),
            "gateways": {},
        }

        for name, config in self.configs.items():
            summary["gateways"][name] = {
                "host": config.host,
                "port": config.port,
                "https": config.use_https,
                "auth_type": config.auth_type,
                "project": config.project_name,
                "tags": config.tags,
                "description": config.description,
            }

        return summary
