"""Module Deployment & Distribution System.

This module provides comprehensive tools for packaging, signing, and distributing
Ignition modules across different environments and repositories.

Components:
- ModulePackager: Automated module packaging with Gradle integration
- ModuleSigner: Digital signing and certificate verification
- RepositoryManager: Module repository management and distribution
- DeploymentManager: End-to-end deployment orchestration
- CLI: Rich command-line interface for all operations

Features:
- Automated packaging with validation
- Digital signing with X.509 certificates
- Repository upload/download with progress tracking
- Batch deployment capabilities
- Environment variable configuration
- Comprehensive error handling and validation
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .cli_commands import deployment_cli
from .deployment_manager import DeploymentConfig, DeploymentManager, DeploymentResult
from .module_packager import ModulePackager, PackagingConfig, PackagingResult
from .module_signer import ModuleSigner, SigningConfig, SigningResult
from .repository_manager import (
    RepositoryConfig,
    RepositoryManager,
    RepositoryResult,
)

__all__ = [
    # Core deployment components
    "DeploymentConfig",
    "DeploymentManager",
    "DeploymentResult",
    "ModulePackager",
    "ModuleSigner",
    "PackagingConfig",
    "PackagingResult",
    "RepositoryConfig",
    "RepositoryManager",
    "RepositoryResult",
    "SigningConfig",
    "SigningResult",
    "deployment_cli",
]

__version__ = "1.0.0"


# Validate deployment environment
def validate_deployment_environment() -> dict[str, bool]:
    """Validate deployment environment configuration."""
    validation_results = {
        "signing_certificate": bool(os.getenv("MODULE_SIGNING_CERT_PATH")),
        "signing_key": bool(os.getenv("MODULE_SIGNING_KEY_PATH")),
        "repository_url": bool(os.getenv("MODULE_REPOSITORY_URL")),
        "deployment_token": bool(os.getenv("DEPLOYMENT_API_TOKEN")),
        "license_server": bool(os.getenv("LICENSE_SERVER_URL")),
        "cicd_webhook": bool(os.getenv("CICD_WEBHOOK_URL")),
    }
    return validation_results


# Environment validation on import
_env_status = validate_deployment_environment()
if not any(_env_status.values()):
    print(
        "Warning: Deployment environment variables not configured. See .env.example for required variables."
    )
