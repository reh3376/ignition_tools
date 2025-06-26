#!/usr/bin/env python3
"""
Frontend Recovery Script - Following crawl_mcp.py Methodology

This script recovers frontend files from git history and properly pushes them
to the remote frontend repository, following the systematic approach defined
in crawl_mcp.py.

Progressive Complexity Levels:
1. Basic: Environment validation and git history access
2. Standard: Frontend file extraction from git history
3. Advanced: Repository setup and file organization
4. Enterprise: Push to remote and validation
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


class RecoveryConfig(BaseModel):
    """Configuration for frontend recovery following crawl_mcp.py validation patterns."""

    source_repo_path: str = Field(..., description="Path to source repository")
    frontend_repo_url: str = Field(..., description="URL of target frontend repository")
    recovery_commit: str = Field(..., description="Commit hash to recover from")
    temp_dir: str = Field(default="/tmp", description="Temporary directory for operations")
    dry_run: bool = Field(False, description="Whether to run in dry-run mode")


@dataclass
class RecoveryResult:
    """Result of frontend recovery operation."""

    success: bool
    message: str
    files_recovered: int
    files_pushed: int
    errors: list[str]
    warnings: list[str]


class FrontendRecoveryManager:
    """
    Frontend Recovery Manager following crawl_mcp.py methodology.

    Implements progressive complexity:
    - Basic: Environment validation
    - Standard: File extraction from git history
    - Advanced: Repository setup
    - Enterprise: Remote push and validation
    """

    def __init__(self, config: RecoveryConfig):
        """Initialize recovery manager with comprehensive validation."""
        self.config = config
        self.source_path = Path(config.source_repo_path)
        self.temp_frontend_path = None
        self.errors = []
        self.warnings = []

        # Validate configuration
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        """Validate configuration following crawl_mcp.py patterns."""
        if not self.source_path.exists():
            raise ValueError(f"Source repository path does not exist: {self.source_path}")

        if not self.source_path.is_dir():
            raise ValueError(f"Source repository path is not a directory: {self.source_path}")

    def validate_environment(self) -> dict[str, Any]:
        """
        Step 1: Environment Validation (crawl_mcp.py methodology)
        Basic complexity level - foundational validation.
        """
        validation_result = {
            "git_available": False,
            "source_repo_valid": False,
            "recovery_commit_exists": False,
            "frontend_repo_accessible": False,
            "temp_dir_writable": False,
            "internet_connection": False,
        }

        try:
            # Git availability
            try:
                result = subprocess.run(["git", "--version"], capture_output=True, text=True)
                validation_result["git_available"] = result.returncode == 0
            except FileNotFoundError:
                self.errors.append("Git not available in PATH")

            # Source repository validation
            try:
                repo = git.Repo(self.source_path)
                validation_result["source_repo_valid"] = True

                # Check if recovery commit exists
                try:
                    repo.commit(self.config.recovery_commit)
                    validation_result["recovery_commit_exists"] = True
                except:
                    self.errors.append(f"Recovery commit {self.config.recovery_commit} not found")

            except InvalidGitRepositoryError:
                self.errors.append("Source path is not a valid Git repository")

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

            # Temp directory writable
            try:
                test_file = Path(self.config.temp_dir) / "test_write"
                test_file.write_text("test")
                test_file.unlink()
                validation_result["temp_dir_writable"] = True
            except:
                self.errors.append("Temporary directory not writable")

            # Internet connection (basic check)
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "github.com"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                validation_result["internet_connection"] = result.returncode == 0
            except:
                self.warnings.append("Internet connection check failed")

        except Exception as e:
            self.errors.append(f"Environment validation failed: {e!s}")

        return validation_result

    def extract_frontend_files(self) -> dict[str, Any]:
        """
        Step 2: Frontend File Extraction (crawl_mcp.py methodology)
        Standard complexity level - core recovery logic.
        """
        extraction_result = {
            "files_found": 0,
            "files_extracted": 0,
            "temp_dir_created": False,
            "extraction_successful": False,
        }

        try:
            # Create temporary directory for frontend files
            temp_dir = tempfile.mkdtemp(prefix="frontend_recovery_")
            self.temp_frontend_path = Path(temp_dir)
            extraction_result["temp_dir_created"] = True

            print(f"Created temporary directory: {self.temp_frontend_path}")

            # Get list of frontend files from git history
            git.Repo(self.source_path)

            # Get all frontend files from the recovery commit
            result = subprocess.run(
                ["git", "ls-tree", "-r", self.config.recovery_commit],
                cwd=self.source_path,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                self.errors.append(f"Failed to list files from commit: {result.stderr}")
                return extraction_result

            frontend_files = []
            for line in result.stdout.strip().split("\n"):
                if line and "frontend/" in line:
                    # Parse git ls-tree output: mode type hash filename
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        filename = parts[1]
                        if filename.startswith("frontend/"):
                            frontend_files.append(filename)

            extraction_result["files_found"] = len(frontend_files)
            print(f"Found {len(frontend_files)} frontend files to recover")

            # Extract each file
            for file_path in frontend_files:
                try:
                    # Get file content from git history
                    result = subprocess.run(
                        ["git", "show", f"{self.config.recovery_commit}:{file_path}"],
                        cwd=self.source_path,
                        capture_output=True,
                    )

                    if result.returncode == 0:
                        # Create directory structure
                        target_path = self.temp_frontend_path / file_path.replace("frontend/", "")
                        target_path.parent.mkdir(parents=True, exist_ok=True)

                        # Write file content
                        target_path.write_bytes(result.stdout)
                        extraction_result["files_extracted"] += 1
                        print(f"Extracted: {file_path}")
                    else:
                        self.warnings.append(f"Failed to extract {file_path}: {result.stderr.decode()}")

                except Exception as e:
                    self.warnings.append(f"Error extracting {file_path}: {e!s}")

            extraction_result["extraction_successful"] = extraction_result["files_extracted"] > 0

        except Exception as e:
            self.errors.append(f"Frontend extraction failed: {e!s}")

        return extraction_result

    def setup_frontend_repository(self) -> dict[str, Any]:
        """
        Step 3: Repository Setup (crawl_mcp.py methodology)
        Advanced complexity level - repository configuration.
        """
        setup_result = {
            "repo_cloned": False,
            "files_copied": 0,
            "git_configured": False,
            "ready_for_push": False,
        }

        try:
            if not self.temp_frontend_path:
                self.errors.append("No temporary frontend path available")
                return setup_result

            # Clone the frontend repository
            frontend_repo_path = self.temp_frontend_path.parent / "frontend_repo"

            print(f"Cloning frontend repository to: {frontend_repo_path}")
            result = subprocess.run(
                [
                    "git",
                    "clone",
                    self.config.frontend_repo_url,
                    str(frontend_repo_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                self.errors.append(f"Failed to clone frontend repository: {result.stderr}")
                return setup_result

            setup_result["repo_cloned"] = True

            # Copy extracted files to the cloned repository
            for item in self.temp_frontend_path.iterdir():
                if item.name != ".git":  # Skip any git directories
                    target = frontend_repo_path / item.name
                    if item.is_dir():
                        if target.exists():
                            shutil.rmtree(target)
                        shutil.copytree(item, target)
                    else:
                        shutil.copy2(item, target)
                    setup_result["files_copied"] += 1

            # Configure git in the frontend repository
            os.chdir(frontend_repo_path)

            # Add all files
            result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
            if result.returncode != 0:
                self.errors.append(f"Failed to add files: {result.stderr}")
                return setup_result

            # Check if there are changes to commit
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if result.stdout.strip():
                # Commit the changes
                commit_message = f"feat: Initial frontend files migration from IGN_scripts\n\n✅ Frontend Migration Complete:\n- {setup_result['files_copied']} files migrated from backend repository\n- Clean separation with independent development capability\n- Ready for UI development following UIroadmap.md\n\n🎯 Source: IGN_scripts commit {self.config.recovery_commit}\n📊 Files: {setup_result['files_copied']} TypeScript/React components"

                result = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    self.errors.append(f"Failed to commit changes: {result.stderr}")
                    return setup_result

                setup_result["git_configured"] = True
                setup_result["ready_for_push"] = True
                print("Successfully committed frontend files")
            else:
                self.warnings.append("No changes to commit - repository may already be up to date")
                setup_result["git_configured"] = True

        except Exception as e:
            self.errors.append(f"Repository setup failed: {e!s}")

        return setup_result

    def push_to_remote(self) -> dict[str, Any]:
        """
        Step 4: Push to Remote (crawl_mcp.py methodology)
        Enterprise complexity level - remote synchronization.
        """
        push_result = {
            "push_successful": False,
            "files_pushed": 0,
            "remote_updated": False,
        }

        try:
            if self.config.dry_run:
                print("DRY RUN: Would push changes to remote repository")
                push_result["push_successful"] = True
                return push_result

            # Push to remote
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                push_result["push_successful"] = True
                push_result["remote_updated"] = True
                print("Successfully pushed to remote repository")

                # Count files in the repository
                result = subprocess.run(
                    ["find", ".", "-type", "f", "!", "-path", "./.git/*"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    push_result["files_pushed"] = len(result.stdout.strip().split("\n"))

            else:
                self.errors.append(f"Failed to push to remote: {result.stderr}")

        except Exception as e:
            self.errors.append(f"Push to remote failed: {e!s}")

        return push_result

    def execute_recovery(self) -> RecoveryResult:
        """
        Execute complete frontend recovery following crawl_mcp.py methodology.
        """
        print("🔄 Starting Frontend Recovery - Following crawl_mcp.py Methodology")
        print("=" * 70)

        try:
            # Step 1: Environment Validation
            print("\n📋 Step 1: Environment Validation")
            self.validate_environment()
            if self.errors:
                return RecoveryResult(
                    success=False,
                    message=f"Environment validation failed: {'; '.join(self.errors)}",
                    files_recovered=0,
                    files_pushed=0,
                    errors=self.errors,
                    warnings=self.warnings,
                )
            print("✅ Environment validation completed")

            # Step 2: Frontend File Extraction
            print("\n📁 Step 2: Frontend File Extraction")
            extract_result = self.extract_frontend_files()
            if not extract_result["extraction_successful"]:
                return RecoveryResult(
                    success=False,
                    message="Frontend file extraction failed",
                    files_recovered=extract_result["files_extracted"],
                    files_pushed=0,
                    errors=self.errors,
                    warnings=self.warnings,
                )
            print(f"✅ Extracted {extract_result['files_extracted']} files")

            # Step 3: Repository Setup
            print("\n🔧 Step 3: Repository Setup")
            setup_result = self.setup_frontend_repository()
            if not setup_result["ready_for_push"]:
                return RecoveryResult(
                    success=False,
                    message="Repository setup failed",
                    files_recovered=extract_result["files_extracted"],
                    files_pushed=0,
                    errors=self.errors,
                    warnings=self.warnings,
                )
            print(f"✅ Repository setup completed with {setup_result['files_copied']} files")

            # Step 4: Push to Remote
            print("\n🚀 Step 4: Push to Remote")
            push_result = self.push_to_remote()
            if not push_result["push_successful"]:
                return RecoveryResult(
                    success=False,
                    message="Push to remote failed",
                    files_recovered=extract_result["files_extracted"],
                    files_pushed=0,
                    errors=self.errors,
                    warnings=self.warnings,
                )
            print(f"✅ Successfully pushed {push_result['files_pushed']} files to remote")

            return RecoveryResult(
                success=True,
                message="Frontend recovery completed successfully",
                files_recovered=extract_result["files_extracted"],
                files_pushed=push_result["files_pushed"],
                errors=self.errors,
                warnings=self.warnings,
            )

        except Exception as e:
            return RecoveryResult(
                success=False,
                message=f"Recovery failed: {e!s}",
                files_recovered=0,
                files_pushed=0,
                errors=[*self.errors, str(e)],
                warnings=self.warnings,
            )

        finally:
            # Cleanup temporary directories
            if self.temp_frontend_path and self.temp_frontend_path.exists():
                try:
                    shutil.rmtree(self.temp_frontend_path)
                    print(f"🧹 Cleaned up temporary directory: {self.temp_frontend_path}")
                except:
                    pass


def main():
    """Main execution function following crawl_mcp.py methodology."""
    print("🚀 Frontend Recovery Script - crawl_mcp.py Methodology")
    print("=" * 60)

    # Configuration
    config = RecoveryConfig(
        source_repo_path="/Users/reh3376/repos/IGN_scripts",
        frontend_repo_url="https://github.com/reh3376/ignition_tools_front.git",
        recovery_commit="2789c6b",  # Pre-separation commit
        dry_run=False,
    )

    # Execute recovery
    manager = FrontendRecoveryManager(config)
    result = manager.execute_recovery()

    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "methodology": "crawl_mcp.py",
        "config": config.model_dump(),
        "result": {
            "success": result.success,
            "message": result.message,
            "files_recovered": result.files_recovered,
            "files_pushed": result.files_pushed,
            "errors": result.errors,
            "warnings": result.warnings,
        },
    }

    # Save report
    report_path = Path("/Users/reh3376/repos/IGN_scripts/frontend_recovery_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Recovery Report saved to: {report_path}")

    if result.success:
        print(f"✅ SUCCESS: {result.message}")
        print(f"📁 Files recovered: {result.files_recovered}")
        print(f"🚀 Files pushed: {result.files_pushed}")
    else:
        print(f"❌ FAILED: {result.message}")
        if result.errors:
            print("🔥 Errors:")
            for error in result.errors:
                print(f"   - {error}")

    if result.warnings:
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   - {warning}")

    return 0 if result.success else 1


if __name__ == "__main__":
    exit(main())
