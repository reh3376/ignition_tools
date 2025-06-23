"""Repository Manager for module repository and update mechanisms.

Following the crawl_mcp.py methodology for structured development:
- Comprehensive validation and error handling
- Environment variable configuration
- Structured logging and progress tracking
- RESTful API integration for repository management
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment variables
load_dotenv()

console = Console()


@dataclass
class RepositoryConfig:
    """Configuration for repository management operations."""

    # Repository settings
    repository_url: str = field(
        default_factory=lambda: os.getenv("MODULE_REPOSITORY_URL", "")
    )
    api_token: str = field(
        default_factory=lambda: os.getenv("REPOSITORY_API_TOKEN", "")
    )
    repository_name: str = field(
        default_factory=lambda: os.getenv("REPOSITORY_NAME", "ignition-modules")
    )

    # Upload settings
    upload_timeout: int = 300  # 5 minutes
    chunk_size: int = 8192  # 8KB chunks
    retry_attempts: int = 3

    # Download settings
    download_directory: Path = field(default_factory=lambda: Path("downloads"))
    cache_directory: Path = field(default_factory=lambda: Path("cache"))
    verify_checksums: bool = True

    # Authentication
    username: str = field(default_factory=lambda: os.getenv("REPOSITORY_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("REPOSITORY_PASSWORD", ""))

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self.download_directory.mkdir(parents=True, exist_ok=True)
        self.cache_directory.mkdir(parents=True, exist_ok=True)


@dataclass
class RepositoryResult:
    """Result of a repository operation."""

    success: bool
    operation: str = ""
    module_info: dict[str, Any] = field(default_factory=dict)
    download_url: str = ""
    upload_url: str = ""
    file_path: Path | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    operation_info: dict[str, Any] = field(default_factory=dict)


def validate_repository_url(repo_url: str) -> dict[str, Any]:
    """Validate repository URL following crawl_mcp.py validation patterns."""
    if not repo_url or not isinstance(repo_url, str):
        return {"valid": False, "error": "Repository URL is required"}

    try:
        parsed_url = urlparse(repo_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {"valid": False, "error": "Invalid repository URL format"}

        if parsed_url.scheme not in ["http", "https"]:
            return {"valid": False, "error": "Repository URL must use HTTP or HTTPS"}

        return {"valid": True, "parsed_url": parsed_url}

    except Exception as e:
        return {"valid": False, "error": f"URL validation error: {e!s}"}


def validate_module_package(package_path: Path) -> dict[str, Any]:
    """Validate module package following crawl_mcp.py validation patterns."""
    if not package_path or not isinstance(package_path, Path):
        return {"valid": False, "error": "Package path is required"}

    if not package_path.exists():
        return {"valid": False, "error": f"Package not found: {package_path}"}

    if package_path.suffix.lower() not in [".zip", ".modl"]:
        return {
            "valid": False,
            "error": f"Invalid package format: {package_path.suffix}",
        }

    # Check file size (reasonable limits)
    file_size = package_path.stat().st_size
    max_size = 500 * 1024 * 1024  # 500MB
    if file_size > max_size:
        return {
            "valid": False,
            "error": f"Package too large: {file_size} bytes (max: {max_size})",
        }

    return {"valid": True, "file_size": file_size}


class RepositoryManager:
    """Comprehensive repository manager for Ignition modules."""

    def __init__(self, config: RepositoryConfig) -> None:
        """Initialize repository manager with configuration."""
        self.config = config
        self.console = console
        self.session = requests.Session()

        # Configure session with authentication
        if self.config.api_token:
            self.session.headers.update(
                {"Authorization": f"Bearer {self.config.api_token}"}
            )
        elif self.config.username and self.config.password:
            self.session.auth = (self.config.username, self.config.password)

    def validate_environment(self) -> dict[str, bool]:
        """Validate repository environment following crawl_mcp.py patterns."""
        validation_results = {
            "repository_url_valid": False,
            "authentication_configured": bool(
                self.config.api_token or (self.config.username and self.config.password)
            ),
            "download_directory_writable": self._check_directory_writable(
                self.config.download_directory
            ),
            "cache_directory_writable": self._check_directory_writable(
                self.config.cache_directory
            ),
            "repository_accessible": False,
        }

        # Validate repository URL
        if self.config.repository_url:
            url_validation = validate_repository_url(self.config.repository_url)
            validation_results["repository_url_valid"] = url_validation["valid"]

            # Test repository accessibility
            if url_validation["valid"]:
                validation_results["repository_accessible"] = (
                    self._test_repository_connection()
                )

        return validation_results

    def upload_module(
        self, package_path: Path, metadata: dict[str, Any] | None = None
    ) -> RepositoryResult:
        """Upload a module package to the repository."""
        result = RepositoryResult(success=False)

        # Validate inputs
        if not package_path.exists():
            result.errors.append(f"Package file not found: {package_path}")
            return result

        # Validate environment
        validation_results = self.validate_environment()
        missing_requirements = [
            req for req, valid in validation_results.items() if not valid
        ]

        if missing_requirements:
            result.warnings.extend(
                [f"Environment issue: {req}" for req in missing_requirements]
            )

            # Check for critical missing requirements
            critical_missing = [
                req
                for req in missing_requirements
                if req in ["repository_url_valid", "authentication_configured"]
            ]
            if critical_missing:
                result.errors.extend(
                    [f"Critical requirement missing: {req}" for req in critical_missing]
                )
                return result

        try:
            with console.status(
                f"[bold green]Uploading {package_path.name}...", spinner="dots"
            ):
                # Prepare upload data
                upload_data = {
                    "name": package_path.stem,
                    "version": (
                        metadata.get("version", "1.0.0") if metadata else "1.0.0"
                    ),
                    "description": metadata.get("description", "") if metadata else "",
                    "author": metadata.get("author", "") if metadata else "",
                    "tags": metadata.get("tags", []) if metadata else [],
                }

                # Validate package
                package_validation = validate_module_package(package_path)
                if not package_validation["valid"]:
                    result.errors.append(package_validation["error"])
                    return result

                # Upload file
                upload_url = urljoin(
                    self.config.repository_url, "api/v1/modules/upload"
                )

                with open(package_path, "rb") as f:
                    files = {"file": (package_path.name, f, "application/octet-stream")}
                    data = {"metadata": json.dumps(upload_data)}

                    response = self.session.post(
                        upload_url,
                        files=files,
                        data=data,
                        timeout=self.config.upload_timeout,
                    )

                if response.status_code == 200:
                    response_data = response.json()

                    result.success = True
                    result.module_info = response_data.get("module", {})
                    result.upload_url = upload_url
                    result.operation_info = {
                        "upload_timestamp": datetime.now().isoformat(),
                        "file_size": package_validation["file_size"],
                        "response_status": response.status_code,
                    }

                    self.console.print(
                        f"✅ Successfully uploaded module: {package_path.name}"
                    )

                else:
                    result.errors.append(
                        f"Upload failed with status {response.status_code}: {response.text}"
                    )

        except requests.exceptions.RequestException as e:
            result.errors.append(f"Upload request error: {e!s}")
        except Exception as e:
            result.errors.append(f"Upload error: {e!s}")

        return result

    def download_module(
        self, module_name: str, version: str | None = None
    ) -> RepositoryResult:
        """Download a module from the repository.

        Args:
            module_name: Name of the module to download
            version: Specific version to download (latest if None)

        Returns:
            RepositoryResult with download information
        """
        result = RepositoryResult(success=False, operation="download")

        # Validate environment
        env_validation = self.validate_environment()
        if not env_validation["repository_url_valid"]:
            result.errors.append("Invalid repository URL")
            return result

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                progress.add_task(f"Downloading {module_name}...", total=None)

                # Get module information
                module_info = self.get_module_info(module_name, version)
                if not module_info.success:
                    result.errors.extend(module_info.errors)
                    return result

                # Download file
                download_url = module_info.download_url
                if not download_url:
                    result.errors.append("No download URL available for module")
                    return result

                response = self.session.get(
                    download_url, stream=True, timeout=self.config.upload_timeout
                )

                if response.status_code == 200:
                    # Determine filename
                    filename = f"{module_name}-{version or 'latest'}.modl"
                    if "content-disposition" in response.headers:
                        import re

                        cd = response.headers["content-disposition"]
                        filename_match = re.findall("filename=(.+)", cd)
                        if filename_match:
                            filename = filename_match[0].strip('"')

                    file_path = self.config.download_directory / filename

                    # Download with progress
                    with open(file_path, "wb") as f:
                        for chunk in response.iter_content(
                            chunk_size=self.config.chunk_size
                        ):
                            if chunk:
                                f.write(chunk)

                    result.success = True
                    result.file_path = file_path
                    result.module_info = module_info.module_info
                    result.download_url = download_url
                    result.operation_info = {
                        "download_timestamp": datetime.now().isoformat(),
                        "file_size": file_path.stat().st_size,
                        "response_status": response.status_code,
                    }

                    self.console.print(
                        f"✅ Successfully downloaded module: {file_path}"
                    )

                else:
                    result.errors.append(
                        f"Download failed with status {response.status_code}: {response.text}"
                    )

        except requests.exceptions.RequestException as e:
            result.errors.append(f"Download request error: {e!s}")
        except Exception as e:
            result.errors.append(f"Download error: {e!s}")

        return result

    def get_module_info(
        self, module_name: str, version: str | None = None
    ) -> RepositoryResult:
        """Get information about a module from the repository.

        Args:
            module_name: Name of the module
            version: Specific version (latest if None)

        Returns:
            RepositoryResult with module information
        """
        result = RepositoryResult(success=False, operation="info")

        try:
            # Build API URL
            api_url = urljoin(
                self.config.repository_url, f"api/v1/modules/{module_name}"
            )
            if version:
                api_url += f"/{version}"

            response = self.session.get(api_url, timeout=30)

            if response.status_code == 200:
                module_data = response.json()

                result.success = True
                result.module_info = module_data
                result.download_url = module_data.get("download_url", "")
                result.operation_info = {
                    "query_timestamp": datetime.now().isoformat(),
                    "response_status": response.status_code,
                }

            elif response.status_code == 404:
                result.errors.append(f"Module not found: {module_name}")
            else:
                result.errors.append(
                    f"API request failed with status {response.status_code}: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            result.errors.append(f"API request error: {e!s}")
        except Exception as e:
            result.errors.append(f"Info retrieval error: {e!s}")

        return result

    def list_modules(self, search_query: str | None = None) -> RepositoryResult:
        """List available modules in the repository.

        Args:
            search_query: Optional search query to filter modules

        Returns:
            RepositoryResult with module list
        """
        result = RepositoryResult(success=False, operation="list")

        try:
            # Build API URL
            api_url = urljoin(self.config.repository_url, "api/v1/modules")
            params = {}
            if search_query:
                params["search"] = search_query

            response = self.session.get(api_url, params=params, timeout=30)

            if response.status_code == 200:
                modules_data = response.json()

                result.success = True
                result.module_info = modules_data
                result.operation_info = {
                    "query_timestamp": datetime.now().isoformat(),
                    "response_status": response.status_code,
                    "module_count": len(modules_data.get("modules", [])),
                }

            else:
                result.errors.append(
                    f"List request failed with status {response.status_code}: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            result.errors.append(f"List request error: {e!s}")
        except Exception as e:
            result.errors.append(f"List retrieval error: {e!s}")

        return result

    def delete_module(
        self, module_name: str, version: str | None = None
    ) -> RepositoryResult:
        """Delete a module from the repository.

        Args:
            module_name: Name of the module to delete
            version: Specific version to delete (all versions if None)

        Returns:
            RepositoryResult with deletion information
        """
        result = RepositoryResult(success=False, operation="delete")

        try:
            # Build API URL
            api_url = urljoin(
                self.config.repository_url, f"api/v1/modules/{module_name}"
            )
            if version:
                api_url += f"/{version}"

            response = self.session.delete(api_url, timeout=30)

            if response.status_code == 200:
                result.success = True
                result.operation_info = {
                    "deletion_timestamp": datetime.now().isoformat(),
                    "response_status": response.status_code,
                }

                self.console.print(f"✅ Successfully deleted module: {module_name}")

            elif response.status_code == 404:
                result.errors.append(f"Module not found: {module_name}")
            else:
                result.errors.append(
                    f"Delete request failed with status {response.status_code}: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            result.errors.append(f"Delete request error: {e!s}")
        except Exception as e:
            result.errors.append(f"Delete error: {e!s}")

        return result

    def _check_directory_writable(self, directory: Path) -> bool:
        """Check if directory is writable."""
        try:
            test_file = directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except Exception:
            return False

    def _test_repository_connection(self) -> bool:
        """Test connection to repository."""
        try:
            health_url = urljoin(self.config.repository_url, "api/v1/health")
            response = self.session.get(health_url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
