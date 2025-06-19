"""Module Builder for building and packaging Ignition modules."""

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .sdk_manager import IgnitionSDKManager

console = Console()


@dataclass
class BuildResult:
    """Result of a module build operation."""

    success: bool
    project_name: str
    project_path: Path
    module_file: Path | None
    build_time: float
    errors: list[str]
    warnings: list[str]


class ModuleBuilder:
    """Builder for Ignition modules with enhanced build capabilities."""

    def __init__(self, sdk_manager: IgnitionSDKManager | None = None) -> None:
        """Initialize the module builder.

        Args:
            sdk_manager: SDK manager for accessing projects
        """
        self.sdk_manager = sdk_manager or IgnitionSDKManager()

    def build_project(self, project_path: Path, clean: bool = True) -> BuildResult:
        """Build an Ignition module project.

        Args:
            project_path: Path to the module project
            clean: Whether to clean before building

        Returns:
            BuildResult with build information
        """
        import time

        start_time = time.time()

        result = BuildResult(
            success=False,
            project_name=project_path.name,
            project_path=project_path,
            module_file=None,
            build_time=0.0,
            errors=[],
            warnings=[],
        )

        if not project_path.exists():
            result.errors.append(f"Project path does not exist: {project_path}")
            return result

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(f"Building {project_path.name}...", total=None)

                # Use gradlew wrapper
                gradlew_cmd = (
                    "./gradlew" if project_path.name != "nt" else "gradlew.bat"
                )

                # Build command
                build_cmd = [gradlew_cmd]
                if clean:
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

                result.build_time = time.time() - start_time

                if build_result.returncode == 0:
                    result.success = True

                    # Find the generated .modl file
                    build_dir = project_path / "build"
                    modl_files = list(build_dir.glob("*.modl"))
                    if modl_files:
                        result.module_file = modl_files[0]
                        console.print(f"✅ Build successful: {result.module_file}")
                    else:
                        result.warnings.append("No .modl file found in build output")

                    # Parse warnings from output
                    if "warning" in build_result.stdout.lower():
                        result.warnings.extend(
                            self._parse_warnings(build_result.stdout)
                        )

                else:
                    result.success = False
                    result.errors.append(
                        f"Build failed with exit code {build_result.returncode}"
                    )
                    result.errors.extend(self._parse_errors(build_result.stderr))

        except subprocess.TimeoutExpired:
            result.errors.append("Build timeout (10 minutes)")
        except Exception as e:
            result.errors.append(f"Build error: {e!s}")

        return result

    def build_all_projects(self) -> list[BuildResult]:
        """Build all projects in the workspace.

        Returns:
            list of build results
        """
        projects = self.sdk_manager.list_projects()
        results = []

        console.print(f"🔨 Building {len(projects)} projects...")

        for project_path in projects:
            console.print(f"\n📦 Building {project_path.name}...")
            result = self.build_project(project_path)
            results.append(result)

            if result.success:
                console.print(f"✅ {project_path.name} built successfully")
            else:
                console.print(f"❌ {project_path.name} build failed")
                for error in result.errors:
                    console.print(f"   Error: {error}")

        return results

    def clean_project(self, project_path: Path) -> bool:
        """Clean a module project.

        Args:
            project_path: Path to the module project

        Returns:
            True if successful, False otherwise
        """
        if not project_path.exists():
            console.print(f"❌ Project not found: {project_path}")
            return False

        try:
            # Use gradlew wrapper
            gradlew_cmd = "./gradlew" if project_path.name != "nt" else "gradlew.bat"

            result = subprocess.run(
                [gradlew_cmd, "clean"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                console.print(f"🧹 Cleaned {project_path.name}")
                return True
            else:
                console.print(
                    f"❌ Failed to clean {project_path.name}: {result.stderr}"
                )
                return False

        except Exception as e:
            console.print(f"❌ Error cleaning {project_path.name}: {e}")
            return False

    def package_module(
        self, project_path: Path, output_dir: Path | None = None
    ) -> Path | None:
        """Package a module for distribution.

        Args:
            project_path: Path to the module project
            output_dir: Output directory for the packaged module

        Returns:
            Path to the packaged module if successful, None otherwise
        """
        # Build the project first
        build_result = self.build_project(project_path)
        if not build_result.success:
            console.print(f"❌ Cannot package - build failed for {project_path.name}")
            return None

        if not build_result.module_file:
            console.print(f"❌ No module file found for {project_path.name}")
            return None

        # Determine output location
        if output_dir is None:
            output_dir = Path.cwd() / "packaged-modules"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Copy the module file
        output_file = output_dir / build_result.module_file.name
        try:
            shutil.copy2(build_result.module_file, output_file)
            console.print(f"📦 Packaged module: {output_file}")
            return output_file
        except Exception as e:
            console.print(f"❌ Failed to package module: {e}")
            return None

    def validate_module(self, module_file: Path) -> dict[str, Any]:
        """Validate a module file.

        Args:
            module_file: Path to the .modl file

        Returns:
            Validation results
        """
        validation = {
            "valid": False,
            "file_exists": module_file.exists(),
            "file_size": 0,
            "is_zip": False,
            "contains_manifest": False,
            "contains_jars": False,
            "errors": [],
            "warnings": [],
        }

        if not validation["file_exists"]:
            validation["errors"].append("Module file does not exist")
            return validation

        try:
            validation["file_size"] = module_file.stat().st_size

            # Check if it's a valid ZIP file (modules are ZIP files)
            import zipfile

            with zipfile.ZipFile(module_file, "r") as zf:
                validation["is_zip"] = True

                # Check for required files
                file_list = zf.namelist()

                # Check for module.xml
                if "module.xml" in file_list:
                    validation["contains_manifest"] = True
                else:
                    validation["errors"].append("Missing module.xml manifest")

                # Check for JAR files
                jar_files = [f for f in file_list if f.endswith(".jar")]
                if jar_files:
                    validation["contains_jars"] = True
                else:
                    validation["warnings"].append("No JAR files found")

                # Overall validation
                validation["valid"] = (
                    validation["is_zip"] and validation["contains_manifest"]
                )

        except zipfile.BadZipFile:
            validation["errors"].append("File is not a valid ZIP archive")
        except Exception as e:
            validation["errors"].append(f"Validation error: {e!s}")

        return validation

    def get_build_info(self, project_path: Path) -> dict[str, Any]:
        """Get build information for a project.

        Args:
            project_path: Path to the module project

        Returns:
            Build information dictionary
        """
        info = {
            "project_name": project_path.name,
            "project_path": str(project_path),
            "has_build_file": False,
            "build_file_type": None,
            "last_build": None,
            "module_files": [],
            "build_artifacts": [],
        }

        if not project_path.exists():
            return info

        # Check for build files
        if (project_path / "build.gradle.kts").exists():
            info["has_build_file"] = True
            info["build_file_type"] = "gradle.kts"
        elif (project_path / "build.gradle").exists():
            info["has_build_file"] = True
            info["build_file_type"] = "gradle"

        # Check build directory
        build_dir = project_path / "build"
        if build_dir.exists():
            # Find module files
            modl_files = list(build_dir.glob("*.modl"))
            info["module_files"] = [str(f) for f in modl_files]

            # Find all build artifacts
            artifacts = []
            for pattern in ["*.jar", "*.modl", "*.xml"]:
                artifacts.extend(build_dir.glob(f"**/{pattern}"))
            info["build_artifacts"] = [str(f.relative_to(build_dir)) for f in artifacts]

            # Get last build time (newest file in build dir)
            try:
                newest_file = max(build_dir.rglob("*"), key=lambda f: f.stat().st_mtime)
                info["last_build"] = newest_file.stat().st_mtime
            except (ValueError, OSError):
                pass

        return info

    def display_build_summary(self, results: list[BuildResult]) -> None:
        """Display a summary of build results.

        Args:
            results: list of build results
        """
        if not results:
            console.print("No build results to display")
            return

        # Create summary table
        table = Table(title="Build Summary")
        table.add_column("Project", style="bold")
        table.add_column("Status")
        table.add_column("Time (s)")
        table.add_column("Module File")
        table.add_column("Errors/Warnings")

        successful = 0
        total_time = 0.0

        for result in results:
            status = "✅ Success" if result.success else "❌ Failed"
            time_str = f"{result.build_time:.1f}"
            module_str = result.module_file.name if result.module_file else "None"
            issues = f"{len(result.errors)}/{len(result.warnings)}"

            table.add_row(result.project_name, status, time_str, module_str, issues)

            if result.success:
                successful += 1
            total_time += result.build_time

        console.print(table)

        # Summary stats
        console.print(
            f"\n📊 Summary: {successful}/{len(results)} successful, {total_time:.1f}s total"
        )

    def _parse_errors(self, stderr: str) -> list[str]:
        """Parse errors from build output.

        Args:
            stderr: Standard error output

        Returns:
            list of error messages
        """
        errors = []
        lines = stderr.split("\n")

        for line in lines:
            line = line.strip()
            if line and ("error" in line.lower() or "failed" in line.lower()):
                errors.append(line)

        return errors

    def _parse_warnings(self, stdout: str) -> list[str]:
        """Parse warnings from build output.

        Args:
            stdout: Standard output

        Returns:
            list of warning messages
        """
        warnings = []
        lines = stdout.split("\n")

        for line in lines:
            line = line.strip()
            if line and "warning" in line.lower():
                warnings.append(line)

        return warnings
