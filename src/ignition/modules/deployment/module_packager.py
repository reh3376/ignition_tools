"""Module Packager for automated module packaging and distribution.

Following the crawl_mcp.py methodology for structured development:
- Comprehensive validation and error handling
- Environment variable configuration
- Structured logging and progress tracking
- Modular, extensible architecture
"""

import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

# Load environment variables
load_dotenv()

console = Console()


@dataclass
class PackagingConfig:
    """Configuration for module packaging operations."""

    # Core packaging settings
    output_directory: Path = field(default_factory=lambda: Path("dist"))
    temp_directory: Path = field(default_factory=lambda: Path(tempfile.gettempdir()) / "ignition-packaging")

    # Module metadata
    module_name: str = ""
    module_version: str = "1.0.0"
    module_description: str = ""
    module_author: str = ""
    module_license: str = "MIT"

    # Build settings
    clean_build: bool = True
    include_sources: bool = False
    include_documentation: bool = True
    compression_level: int = 6

    # Validation settings
    validate_signatures: bool = True
    validate_dependencies: bool = True
    validate_compatibility: bool = True

    # Environment variables with fallbacks
    signing_cert_path: str = field(default_factory=lambda: os.getenv("MODULE_SIGNING_CERT_PATH", ""))
    signing_key_path: str = field(default_factory=lambda: os.getenv("MODULE_SIGNING_KEY_PATH", ""))
    repository_url: str = field(default_factory=lambda: os.getenv("MODULE_REPOSITORY_URL", ""))

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.temp_directory.mkdir(parents=True, exist_ok=True)


@dataclass
class PackagingResult:
    """Result of a module packaging operation."""

    success: bool
    module_file: Path | None = None
    package_file: Path | None = None
    metadata_file: Path | None = None
    checksum: str = ""
    file_size: int = 0
    build_time: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    packaging_info: dict[str, Any] = field(default_factory=dict)


def validate_project_path(project_path: Path) -> dict[str, Any]:
    """Validate project path following crawl_mcp.py validation patterns."""
    if not project_path or not isinstance(project_path, Path):
        return {"valid": False, "error": "Project path is required"}

    if not project_path.exists():
        return {"valid": False, "error": f"Project not found: {project_path}"}

    # Check for required project files
    required_files = ["build.gradle", "gradle.properties"]
    missing_files = [f for f in required_files if not (project_path / f).exists()]

    if missing_files:
        return {
            "valid": False,
            "error": f"Missing required files: {', '.join(missing_files)}",
        }

    return {"valid": True}


def calculate_file_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


class ModulePackager:
    """Comprehensive module packager for Ignition modules."""

    def __init__(self, config: PackagingConfig) -> None:
        """Initialize module packager with configuration."""
        self.config = config
        self.console = console

    def validate_environment(self) -> dict[str, bool]:
        """Validate packaging environment following crawl_mcp.py patterns."""
        validation_results = {
            "java_available": self._check_java(),
            "gradle_available": self._check_gradle(),
            "signing_cert_exists": bool(self.config.signing_cert_path and Path(self.config.signing_cert_path).exists()),
            "signing_key_exists": bool(self.config.signing_key_path and Path(self.config.signing_key_path).exists()),
            "output_directory_writable": self._check_directory_writable(self.config.output_directory),
            "temp_directory_writable": self._check_directory_writable(self.config.temp_directory),
        }
        return validation_results

    def package_module(self, project_path: Path) -> PackagingResult:
        """Package an Ignition module for distribution.

        Args:
            project_path: Path to the module project

        Returns:
            PackagingResult with packaging information
        """
        import time

        start_time = time.time()

        result = PackagingResult(success=False)

        # Validate project path
        validation = validate_project_path(project_path)
        if not validation["valid"]:
            result.errors.append(validation["error"])
            return result

        # Validate environment
        env_validation = self.validate_environment()
        missing_requirements = [k for k, v in env_validation.items() if not v]
        if missing_requirements:
            result.warnings.extend([f"Missing requirement: {req}" for req in missing_requirements])

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console,
            ) as progress:
                # Step 1: Clean and build module
                build_task = progress.add_task("Building module...", total=100)
                build_result = self._build_module(project_path)
                progress.update(build_task, advance=25)

                if not build_result["success"]:
                    result.errors.extend(build_result["errors"])
                    return result

                result.module_file = build_result["module_file"]
                progress.update(build_task, advance=25)

                # Verify module file exists before proceeding
                if not result.module_file:
                    result.errors.append("Module file not found after build")
                    return result

                # Step 2: Create package metadata
                metadata_task = progress.add_task("Creating metadata...", total=100)
                metadata = self._create_package_metadata(project_path, result.module_file)
                result.metadata_file = self._save_metadata(metadata)
                progress.update(metadata_task, advance=50)

                # Step 3: Create distribution package
                package_task = progress.add_task("Creating package...", total=100)
                package_result = self._create_distribution_package(
                    result.module_file, result.metadata_file, project_path
                )
                progress.update(package_task, advance=50)

                if not package_result["success"]:
                    result.errors.extend(package_result["errors"])
                    return result

                result.package_file = package_result["package_file"]
                progress.update(package_task, advance=50)

                # Step 4: Calculate checksums and file info
                if result.package_file:
                    result.checksum = calculate_file_checksum(result.package_file)
                    result.file_size = result.package_file.stat().st_size

                result.build_time = time.time() - start_time
                result.success = True
                result.packaging_info = {
                    "project_name": project_path.name,
                    "build_timestamp": datetime.now().isoformat(),
                    "packager_version": "1.0.0",
                    "environment": env_validation,
                }

                self.console.print(f"✅ Successfully packaged module: {result.package_file}")

        except Exception as e:
            result.errors.append(f"Packaging error: {e!s}")
            result.build_time = time.time() - start_time

        return result

    def package_multiple_modules(self, project_paths: list[Path]) -> list[PackagingResult]:
        """Package multiple modules in batch.

        Args:
            project_paths: list of project paths to package

        Returns:
            list of packaging results
        """
        results = []

        self.console.print(f"📦 Packaging {len(project_paths)} modules...")

        for project_path in project_paths:
            self.console.print(f"\n🔨 Packaging {project_path.name}...")
            result = self.package_module(project_path)
            results.append(result)

            if result.success:
                self.console.print(f"✅ {project_path.name} packaged successfully")
            else:
                self.console.print(f"❌ {project_path.name} packaging failed")
                for error in result.errors:
                    self.console.print(f"   Error: {error}")

        return results

    def _check_java(self) -> bool:
        """Check if Java is available."""
        try:
            result = subprocess.run(["java", "-version"], capture_output=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_gradle(self) -> bool:
        """Check if Gradle is available."""
        try:
            result = subprocess.run(["gradle", "--version"], capture_output=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_directory_writable(self, directory: Path) -> bool:
        """Check if directory is writable."""
        try:
            test_file = directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except Exception:
            return False

    def _build_module(self, project_path: Path) -> dict[str, Any]:
        """Build the module project."""
        try:
            # Use gradlew wrapper
            gradlew_cmd = "./gradlew" if os.name != "nt" else "gradlew.bat"

            # Build command
            build_cmd = [gradlew_cmd]
            if self.config.clean_build:
                build_cmd.append("clean")
            build_cmd.append("build")

            # Execute build
            build_result = subprocess.run(
                build_cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            if build_result.returncode == 0:
                # Find the generated .modl file
                build_dir = project_path / "build"
                modl_files = list(build_dir.glob("*.modl"))

                if modl_files:
                    return {"success": True, "module_file": modl_files[0], "errors": []}
                else:
                    return {
                        "success": False,
                        "module_file": None,
                        "errors": ["No .modl file found in build output"],
                    }
            else:
                return {
                    "success": False,
                    "module_file": None,
                    "errors": [f"Build failed: {build_result.stderr}"],
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "module_file": None,
                "errors": ["Build timeout (10 minutes)"],
            }
        except Exception as e:
            return {
                "success": False,
                "module_file": None,
                "errors": [f"Build error: {e!s}"],
            }

    def _create_package_metadata(self, project_path: Path, module_file: Path) -> dict[str, Any]:
        """Create package metadata."""
        metadata = {
            "package_info": {
                "name": self.config.module_name or project_path.name,
                "version": self.config.module_version,
                "description": self.config.module_description,
                "author": self.config.module_author,
                "license": self.config.module_license,
                "created_at": datetime.now().isoformat(),
            },
            "module_info": {
                "file_name": module_file.name,
                "file_size": module_file.stat().st_size,
                "checksum": calculate_file_checksum(module_file),
            },
            "build_info": {
                "project_path": str(project_path),
                "build_timestamp": datetime.now().isoformat(),
                "packager_version": "1.0.0",
            },
            "requirements": {
                "min_ignition_version": "8.1.0",
                "java_version": "11+",
            },
        }
        return metadata

    def _save_metadata(self, metadata: dict[str, Any]) -> Path:
        """Save package metadata to file."""
        metadata_file = self.config.output_directory / f"{metadata['package_info']['name']}-metadata.json"

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return metadata_file

    def _create_distribution_package(
        self, module_file: Path, metadata_file: Path, project_path: Path
    ) -> dict[str, Any]:
        """Create distribution package."""
        try:
            package_name = f"{self.config.module_name or project_path.name}-{self.config.module_version}.zip"
            package_file = self.config.output_directory / package_name

            with zipfile.ZipFile(
                package_file,
                "w",
                zipfile.ZIP_DEFLATED,
                compresslevel=self.config.compression_level,
            ) as zipf:
                # Add module file
                zipf.write(module_file, module_file.name)

                # Add metadata
                zipf.write(metadata_file, metadata_file.name)

                # Add documentation if requested
                if self.config.include_documentation:
                    readme_file = project_path / "README.md"
                    if readme_file.exists():
                        zipf.write(readme_file, "README.md")

                # Add sources if requested
                if self.config.include_sources:
                    src_dir = project_path / "src"
                    if src_dir.exists():
                        for src_file in src_dir.rglob("*"):
                            if src_file.is_file():
                                arcname = f"src/{src_file.relative_to(src_dir)}"
                                zipf.write(src_file, arcname)

            return {"success": True, "package_file": package_file, "errors": []}

        except Exception as e:
            return {
                "success": False,
                "package_file": None,
                "errors": [f"Package creation error: {e!s}"],
            }
