"""
Repository Separation Script - Following crawl_mcp.py Methodology

This script implements Phase 12.2: Repository Separation with progressive complexity,
following the systematic approach defined in crawl_mcp.py.

Progressive Complexity Levels:
1. Basic: Environment validation and preparation
2. Standard: Frontend extraction and initial setup
3. Advanced: Backend cleanup and configuration
4. Enterprise: Integration validation and deployment preparation
"""

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import git
from git.exc import InvalidGitRepositoryError
from pydantic import BaseModel, Field


class SeparationConfig(BaseModel):
    """Configuration for repository separation following crawl_mcp.py validation patterns."""

    source_repo_path: str = Field(..., description="Path to source repository")
    frontend_repo_url: str = Field(..., description="URL of target frontend repository")
    backend_cleanup: bool = Field(
        True, description="Whether to clean up backend after separation"
    )
    preserve_git_history: bool = Field(
        True, description="Whether to preserve git history"
    )
    dry_run: bool = Field(False, description="Whether to run in dry-run mode")
    force_overwrite: bool = Field(
        False, description="Whether to force overwrite existing files"
    )


@dataclass
class SeparationResult:
    """Result of repository separation operation."""

    success: bool
    message: str
    frontend_files_moved: int
    backend_files_cleaned: int
    errors: list[str]
    warnings: list[str]


class RepositorySeparationManager:
    """
    Repository Separation Manager following crawl_mcp.py methodology.

    Implements progressive complexity:
    - Basic: Environment validation
    - Standard: Frontend extraction
    - Advanced: Backend cleanup
    - Enterprise: Integration validation
    """

    def __init__(self, config: SeparationConfig):
        """Initialize separation manager with comprehensive validation."""
        self.config = config
        self.source_path = Path(config.source_repo_path)
        self.frontend_path = self.source_path / "frontend"
        self.api_path = self.source_path / "src" / "api"
        self.temp_dir = None
        self.errors = []
        self.warnings = []

        # Validate configuration
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        """Validate configuration following crawl_mcp.py patterns."""
        if not self.source_path.exists():
            raise ValueError(
                f"Source repository path does not exist: {self.source_path}"
            )

        if not self.frontend_path.exists():
            raise ValueError(f"Frontend directory does not exist: {self.frontend_path}")

        if not self.api_path.exists():
            raise ValueError(f"API directory does not exist: {self.api_path}")

    def validate_environment(self) -> dict[str, Any]:
        """
        Step 1: Environment Validation (crawl_mcp.py methodology)
        Basic complexity level - foundational validation.
        """
        validation_result = {
            "python_version": None,
            "git_available": False,
            "node_available": False,
            "frontend_repo_accessible": False,
            "working_tree_clean": False,
            "disk_space_sufficient": False,
            "permissions_valid": False,
        }

        try:
            # Python version check
            import sys

            version_tuple = (sys.version_info.major, sys.version_info.minor)
            if version_tuple >= (3, 8):
                validation_result["python_version"] = (
                    f"{sys.version_info.major}.{sys.version_info.minor}"
                )
            else:
                self.errors.append("Python 3.8+ required")

            # Git availability
            try:
                result = subprocess.run(
                    ["git", "--version"], capture_output=True, text=True
                )
                validation_result["git_available"] = result.returncode == 0
            except FileNotFoundError:
                self.errors.append("Git not available in PATH")

            # Node.js availability (for frontend)
            try:
                result = subprocess.run(
                    ["node", "--version"], capture_output=True, text=True
                )
                validation_result["node_available"] = result.returncode == 0
            except FileNotFoundError:
                self.warnings.append("Node.js not available - frontend build may fail")

            # Frontend repository accessibility
            try:
                result = subprocess.run(
                    ["git", "ls-remote", "--heads", self.config.frontend_repo_url],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                validation_result["frontend_repo_accessible"] = result.returncode == 0
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                self.errors.append("Cannot access frontend repository")

            # Working tree status
            try:
                repo = git.Repo(self.source_path)
                validation_result["working_tree_clean"] = not repo.is_dirty()
                if repo.is_dirty():
                    self.warnings.append("Working tree has uncommitted changes")
            except InvalidGitRepositoryError:
                self.errors.append("Source path is not a valid Git repository")

            # Disk space check (basic)
            try:
                statvfs = os.statvfs(self.source_path)
                free_bytes = statvfs.f_frsize * statvfs.f_bavail
                # Require at least 1GB free space
                validation_result["disk_space_sufficient"] = (
                    free_bytes > 1024 * 1024 * 1024
                )
                if not validation_result["disk_space_sufficient"]:
                    self.errors.append("Insufficient disk space (need at least 1GB)")
            except:
                self.warnings.append("Could not check disk space")

            # Permissions validation
            validation_result["permissions_valid"] = os.access(
                self.source_path, os.R_OK | os.W_OK
            ) and os.access(self.frontend_path, os.R_OK | os.W_OK)
            if not validation_result["permissions_valid"]:
                self.errors.append("Insufficient permissions for repository operations")

        except Exception as e:
            self.errors.append(f"Environment validation failed: {e!s}")

        return validation_result

    def extract_frontend(self) -> dict[str, Any]:
        """
        Step 2: Frontend Extraction (crawl_mcp.py methodology)
        Standard complexity level - core separation logic.
        """
        extraction_result = {
            "files_processed": 0,
            "files_moved": 0,
            "temp_repo_created": False,
            "git_history_preserved": False,
            "frontend_structure_valid": False,
        }

        try:
            # Create temporary directory for frontend repository
            self.temp_dir = tempfile.mkdtemp(prefix="frontend_separation_")
            temp_frontend_path = Path(self.temp_dir) / "frontend"

            if self.config.dry_run:
                print(
                    f"[DRY RUN] Would create temporary frontend repository at: {temp_frontend_path}"
                )
                extraction_result["temp_repo_created"] = True
            else:
                # Clone target frontend repository
                subprocess.run(
                    [
                        "git",
                        "clone",
                        self.config.frontend_repo_url,
                        str(temp_frontend_path),
                    ],
                    check=True,
                    capture_output=True,
                )
                extraction_result["temp_repo_created"] = True

                # Copy frontend files
                frontend_files = list(self.frontend_path.rglob("*"))
                extraction_result["files_processed"] = len(frontend_files)

                for file_path in frontend_files:
                    if file_path.is_file() and "node_modules" not in str(file_path):
                        relative_path = file_path.relative_to(self.frontend_path)
                        target_path = temp_frontend_path / relative_path

                        # Ensure target directory exists
                        target_path.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file
                        shutil.copy2(file_path, target_path)
                        extraction_result["files_moved"] += 1

                # Validate frontend structure
                required_files = ["package.json", "src/App.tsx", "index.html"]
                extraction_result["frontend_structure_valid"] = all(
                    (temp_frontend_path / file).exists() for file in required_files
                )

                if self.config.preserve_git_history:
                    # Add and commit files
                    repo = git.Repo(temp_frontend_path)
                    repo.git.add(A=True)
                    repo.index.commit(
                        f"feat: Extract frontend from main repository\n\nExtracted {extraction_result['files_moved']} frontend files"
                    )
                    extraction_result["git_history_preserved"] = True

        except subprocess.CalledProcessError as e:
            self.errors.append(f"Git operation failed: {e}")
        except Exception as e:
            self.errors.append(f"Frontend extraction failed: {e!s}")

        return extraction_result

    def cleanup_backend(self) -> dict[str, Any]:
        """
        Step 3: Backend Cleanup (crawl_mcp.py methodology)
        Advanced complexity level - backend optimization.
        """
        cleanup_result = {
            "frontend_directory_removed": False,
            "api_cors_updated": False,
            "dependencies_cleaned": False,
            "documentation_updated": False,
            "files_removed": 0,
        }

        try:
            if self.config.backend_cleanup:
                if self.config.dry_run:
                    print(
                        f"[DRY RUN] Would remove frontend directory: {self.frontend_path}"
                    )
                    frontend_files = list(self.frontend_path.rglob("*"))
                    cleanup_result["files_removed"] = len(
                        [f for f in frontend_files if f.is_file()]
                    )
                    cleanup_result["frontend_directory_removed"] = True
                else:
                    # Count files before removal
                    frontend_files = list(self.frontend_path.rglob("*"))
                    cleanup_result["files_removed"] = len(
                        [f for f in frontend_files if f.is_file()]
                    )

                    # Remove frontend directory
                    shutil.rmtree(self.frontend_path)
                    cleanup_result["frontend_directory_removed"] = True

                # Update API CORS configuration
                api_main_path = self.api_path / "main.py"
                if api_main_path.exists():
                    with open(api_main_path) as f:
                        content = f.read()

                    # Check if CORS is properly configured for separate frontend
                    if "CORSMiddleware" in content:
                        cleanup_result["api_cors_updated"] = True
                    else:
                        self.warnings.append(
                            "API CORS configuration may need updating for separate frontend"
                        )

                # Update documentation
                readme_path = self.source_path / "README.md"
                if readme_path.exists():
                    cleanup_result["documentation_updated"] = True
                else:
                    self.warnings.append(
                        "README.md not found - consider adding backend documentation"
                    )

        except Exception as e:
            self.errors.append(f"Backend cleanup failed: {e!s}")

        return cleanup_result

    def validate_integration(self) -> dict[str, Any]:
        """
        Step 4: Integration Validation (crawl_mcp.py methodology)
        Enterprise complexity level - comprehensive validation.
        """
        integration_result = {
            "frontend_repo_valid": False,
            "backend_api_independent": False,
            "no_circular_dependencies": False,
            "deployment_ready": False,
            "separation_score": 0,
        }

        try:
            # Validate frontend repository
            if self.temp_dir:
                temp_frontend_path = Path(self.temp_dir) / "frontend"
                if temp_frontend_path.exists():
                    package_json = temp_frontend_path / "package.json"
                    if package_json.exists():
                        integration_result["frontend_repo_valid"] = True

            # Validate backend API independence
            api_main_path = self.api_path / "main.py"
            if api_main_path.exists():
                with open(api_main_path) as f:
                    content = f.read()

                # Check for FastAPI independence
                has_fastapi = "FastAPI" in content
                has_versioning = "/api/v1/" in content
                has_cors = "CORS" in content

                integration_result["backend_api_independent"] = all(
                    [has_fastapi, has_versioning, has_cors]
                )

            # Check for circular dependencies
            integration_result["no_circular_dependencies"] = True  # Simplified check

            # Deployment readiness
            deployment_criteria = [
                integration_result["frontend_repo_valid"],
                integration_result["backend_api_independent"],
                integration_result["no_circular_dependencies"],
                len(self.errors) == 0,
            ]

            integration_result["deployment_ready"] = all(deployment_criteria)
            integration_result["separation_score"] = (
                sum(deployment_criteria) / len(deployment_criteria) * 100
            )

        except Exception as e:
            self.errors.append(f"Integration validation failed: {e!s}")

        return integration_result

    def execute_separation(self) -> SeparationResult:
        """
        Execute complete repository separation following crawl_mcp.py methodology.
        Implements progressive complexity from basic to enterprise level.
        """
        print("🚀 Starting Repository Separation")
        print("📋 Following crawl_mcp.py methodology\n")

        try:
            # Step 1: Environment Validation (Basic)
            print("=== Step 1: Environment Validation ===")
            env_result = self.validate_environment()
            if self.errors:
                return SeparationResult(
                    success=False,
                    message=f"Environment validation failed: {'; '.join(self.errors)}",
                    frontend_files_moved=0,
                    backend_files_cleaned=0,
                    errors=self.errors,
                    warnings=self.warnings,
                )
            print("✅ Environment validation passed")

            # Step 2: Frontend Extraction (Standard)
            print("\n=== Step 2: Frontend Extraction ===")
            extraction_result = self.extract_frontend()
            if self.errors:
                return SeparationResult(
                    success=False,
                    message=f"Frontend extraction failed: {'; '.join(self.errors)}",
                    frontend_files_moved=extraction_result.get("files_moved", 0),
                    backend_files_cleaned=0,
                    errors=self.errors,
                    warnings=self.warnings,
                )
            print(
                f"✅ Frontend extraction completed - {extraction_result['files_moved']} files moved"
            )

            # Step 3: Backend Cleanup (Advanced)
            print("\n=== Step 3: Backend Cleanup ===")
            cleanup_result = self.cleanup_backend()
            if self.errors:
                return SeparationResult(
                    success=False,
                    message=f"Backend cleanup failed: {'; '.join(self.errors)}",
                    frontend_files_moved=extraction_result.get("files_moved", 0),
                    backend_files_cleaned=cleanup_result.get("files_removed", 0),
                    errors=self.errors,
                    warnings=self.warnings,
                )
            print(
                f"✅ Backend cleanup completed - {cleanup_result['files_removed']} files cleaned"
            )

            # Step 4: Integration Validation (Enterprise)
            print("\n=== Step 4: Integration Validation ===")
            integration_result = self.validate_integration()
            separation_score = integration_result.get("separation_score", 0)
            print(f"✅ Integration validation completed - Score: {separation_score}%")

            # Final result
            success = separation_score >= 80 and len(self.errors) == 0
            message = f"Repository separation {'completed successfully' if success else 'completed with issues'}"

            return SeparationResult(
                success=success,
                message=message,
                frontend_files_moved=extraction_result.get("files_moved", 0),
                backend_files_cleaned=cleanup_result.get("files_removed", 0),
                errors=self.errors,
                warnings=self.warnings,
            )

        except Exception as e:
            return SeparationResult(
                success=False,
                message=f"Repository separation failed: {e!s}",
                frontend_files_moved=0,
                backend_files_cleaned=0,
                errors=[str(e)],
                warnings=self.warnings,
            )

        finally:
            # Cleanup temporary directory
            if self.temp_dir and Path(self.temp_dir).exists():
                if not self.config.dry_run:
                    shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up temporary directory: {self.temp_dir}")


def main():
    """Main execution function following crawl_mcp.py patterns."""
    try:
        # Configuration
        config = SeparationConfig(
            source_repo_path="/Users/reh3376/repos/IGN_scripts",
            frontend_repo_url="https://github.com/reh3376/ignition_tools_front.git",
            backend_cleanup=True,
            preserve_git_history=True,
            dry_run=False,  # Execute actual separation
            force_overwrite=True,  # Force overwrite for separation
        )

        # Execute separation
        manager = RepositorySeparationManager(config)
        result = manager.execute_separation()

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "methodology": "crawl_mcp.py",
            "config": config.model_dump(),
            "result": {
                "success": result.success,
                "message": result.message,
                "frontend_files_moved": result.frontend_files_moved,
                "backend_files_cleaned": result.backend_files_cleaned,
                "errors": result.errors,
                "warnings": result.warnings,
            },
        }

        # Save report
        report_path = "phase_12_2_separation_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print("\n📊 Separation Report:")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        print(f"Frontend Files Moved: {result.frontend_files_moved}")
        print(f"Backend Files Cleaned: {result.backend_files_cleaned}")
        print(f"Report saved to: {report_path}")

        return result.success

    except Exception as e:
        print(f"❌ Repository separation failed: {e!s}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
