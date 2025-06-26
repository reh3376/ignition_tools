#!/usr/bin/env python3
"""
Frontend File Migration Script - Following crawl_mcp.py Methodology

This script systematically identifies and moves all remaining frontend-related
files from the backend repository to the frontend repository.
"""

import json
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import git
    from git.exc import InvalidGitRepositoryError as InvalidGitRepository
except ImportError:
    print("GitPython not installed. Install with: pip install GitPython")
    exit(1)


@dataclass
class MigrationConfig:
    """Configuration for frontend file migration."""

    source_repo_path: str
    frontend_repo_url: str
    commit_hash: str = "2789c6b"  # Pre-separation commit
    dry_run: bool = True
    create_backup: bool = True


@dataclass
class FileCategory:
    """Categorization of files for migration."""

    name: str
    description: str
    patterns: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    priority: int = 1  # 1=highest, 5=lowest


@dataclass
class MigrationResult:
    """Results of the migration process."""

    success: bool
    files_migrated: list[str] = field(default_factory=list)
    files_skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    total_files_processed: int = 0
    migration_time: float = 0.0


class FrontendFileMigrationManager:
    """Frontend File Migration Manager following crawl_mcp.py methodology."""

    def __init__(self, config: MigrationConfig):
        """Initialize migration manager with comprehensive validation."""
        self.config = config
        self.source_path = Path(config.source_repo_path)
        self.temp_frontend_path = None
        self.errors = []
        self.warnings = []

        # Define file categories for migration
        self.file_categories = self._define_file_categories()

        # Validate configuration
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        """Validate configuration following crawl_mcp.py patterns."""
        if not self.source_path.exists():
            raise ValueError(
                f"Source repository path does not exist: {self.source_path}"
            )

        if not self.source_path.is_dir():
            raise ValueError(
                f"Source repository path is not a directory: {self.source_path}"
            )

        try:
            self.source_repo = git.Repo(self.source_path)
        except InvalidGitRepository as e:
            raise ValueError(f"Invalid git repository: {e}")

    def _define_file_categories(self) -> list[FileCategory]:
        """Define categories of files that should move to frontend."""
        return [
            FileCategory(
                name="Frontend Documentation",
                description="Documentation specifically for frontend development",
                patterns=[
                    "docs/UIroadmap.md",
                    "docs/FRONTEND_*.md",
                    "docs/frontend.mdc",
                    "docs/phase_summary/FRONTEND_*.md",
                    "docs/phase_summary/*FRONTEND*.md",
                ],
                priority=1,
            ),
            FileCategory(
                name="Cursor Frontend Rules",
                description="Cursor AI rules and configuration for frontend",
                patterns=[
                    ".cursor/rules/frontend.mdc",
                    ".cursor/rules/*frontend*",
                ],
                priority=1,
            ),
            FileCategory(
                name="Frontend Development Methodology",
                description="Development methodology files for frontend",
                patterns=[
                    "docs/development/*frontend*",
                    "docs/*frontend_development*",
                ],
                priority=2,
            ),
            FileCategory(
                name="Code Intelligence Framework",
                description="Frontend code intelligence and analysis tools",
                patterns=[
                    "docs/*CODE_INTELLIGENCE*FRAMEWORK*",
                    "docs/phase_summary/*CODE_INTELLIGENCE*FRAMEWORK*",
                ],
                priority=2,
            ),
            FileCategory(
                name="Neo4j Frontend Integration",
                description="Neo4j integration documentation for frontend",
                patterns=[
                    "docs/*NEO4J*FRONTEND*",
                    "docs/phase_summary/*NEO4J*",
                ],
                priority=3,
            ),
            FileCategory(
                name="Decoupling Documentation",
                description="Frontend/backend separation documentation",
                patterns=[
                    "docs/FRONTEND_BACKEND_DECOUPLING_PLAN.md",
                    "docs/phase_summary/*DECOUPLING*",
                    "migration_plan.md",
                ],
                priority=3,
            ),
            FileCategory(
                name="Configuration Files",
                description="Configuration files for frontend development",
                patterns=[
                    "docs/configuration/*frontend*",
                    "docs/development/.cursor_rules_mcp.md",
                ],
                priority=4,
            ),
        ]

    def identify_files_to_migrate(self) -> dict[str, list[str]]:
        """Step 1: Basic - Identify all files that should move to frontend."""
        print("🔍 Step 1: Identifying files for migration...")

        categorized_files = {}

        for category in self.file_categories:
            category_files = []

            for pattern in category.patterns:
                # Handle different pattern types
                if "*" in pattern:
                    # Glob pattern matching
                    matches = list(self.source_path.glob(pattern))
                    for match in matches:
                        if match.is_file():
                            relative_path = match.relative_to(self.source_path)
                            category_files.append(str(relative_path))
                else:
                    # Exact file path
                    file_path = self.source_path / pattern
                    if file_path.exists() and file_path.is_file():
                        category_files.append(pattern)

            if category_files:
                categorized_files[category.name] = category_files
                category.files = category_files
                print(f"  📁 {category.name}: {len(category_files)} files")
                for file_path in category_files:
                    print(f"    - {file_path}")

        return categorized_files

    def migrate_files(self, files_to_migrate: dict[str, list[str]]) -> MigrationResult:
        """Step 2: Advanced - Migrate files to frontend repository."""
        print("\n🚀 Step 2: Migrating files to frontend repository...")

        start_time = datetime.now()
        result = MigrationResult(success=True)

        if self.config.dry_run:
            print("  🔄 DRY RUN MODE - No actual file operations")

        try:
            # Clone frontend repository
            with tempfile.TemporaryDirectory() as temp_dir:
                frontend_repo_path = Path(temp_dir) / "frontend_repo"

                if not self.config.dry_run:
                    print("  📥 Cloning frontend repository...")
                    git.Repo.clone_from(
                        self.config.frontend_repo_url, frontend_repo_path
                    )
                    frontend_repo = git.Repo(frontend_repo_path)
                else:
                    print(f"  [DRY RUN] Would clone: {self.config.frontend_repo_url}")

                # Migrate files by category (priority order)
                sorted_categories = sorted(
                    self.file_categories, key=lambda x: x.priority
                )

                for category in sorted_categories:
                    if category.files:
                        print(f"\n  📁 Migrating {category.name}...")

                        for file_path in category.files:
                            success = self._migrate_single_file(
                                file_path,
                                frontend_repo_path if not self.config.dry_run else None,
                            )

                            if success:
                                result.files_migrated.append(file_path)
                                print(f"    ✅ {file_path}")
                            else:
                                result.files_skipped.append(file_path)
                                print(f"    ❌ {file_path}")

                # Commit and push changes
                if not self.config.dry_run and result.files_migrated:
                    print("\n  📤 Committing and pushing changes...")
                    frontend_repo.index.add([f for f in result.files_migrated])
                    frontend_repo.index.commit(
                        f"feat: migrate {len(result.files_migrated)} frontend files from backend repo\n\n"
                        f"Migrated files:\n"
                        + "\n".join([f"- {f}" for f in result.files_migrated[:10]])
                        + (
                            f"\n... and {len(result.files_migrated) - 10} more"
                            if len(result.files_migrated) > 10
                            else ""
                        )
                    )
                    frontend_repo.remote().push()
                    print("    ✅ Changes pushed to frontend repository")
                else:
                    print(
                        f"  [DRY RUN] Would commit and push {len(result.files_migrated)} files"
                    )

        except Exception as e:
            result.success = False
            result.errors.append(f"Migration failed: {e}")
            self.errors.append(str(e))

        # Calculate timing
        end_time = datetime.now()
        result.migration_time = (end_time - start_time).total_seconds()
        result.total_files_processed = len(result.files_migrated) + len(
            result.files_skipped
        )

        return result

    def _migrate_single_file(
        self, file_path: str, frontend_repo_path: Path | None = None
    ) -> bool:
        """Migrate a single file to the frontend repository."""
        if self.config.dry_run:
            return True

        if frontend_repo_path is None:
            return False

        try:
            source_file = self.source_path / file_path
            target_file = frontend_repo_path / file_path

            # Create target directory if it doesn't exist
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy2(source_file, target_file)

            return True
        except Exception as e:
            self.errors.append(f"Failed to migrate {file_path}: {e}")
            return False

    def cleanup_source_files(self, migrated_files: list[str]) -> dict[str, Any]:
        """Step 3: Enterprise - Clean up migrated files from source repository."""
        print("\n🧹 Step 3: Cleaning up source repository...")

        cleanup_result = {
            "files_removed": [],
            "files_failed": [],
            "backup_created": False,
        }

        if self.config.dry_run:
            print("  [DRY RUN] Would remove files from source repository")
            cleanup_result["files_removed"] = migrated_files
            return cleanup_result

        # Create backup if requested
        if self.config.create_backup:
            backup_dir = (
                self.source_path
                / "migration_backup"
                / datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            backup_dir.mkdir(parents=True, exist_ok=True)

            for file_path in migrated_files:
                source_file = self.source_path / file_path
                backup_file = backup_dir / file_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, backup_file)

            cleanup_result["backup_created"] = True
            print(f"  💾 Backup created: {backup_dir}")

        # Remove files from source repository
        for file_path in migrated_files:
            try:
                source_file = self.source_path / file_path
                if source_file.exists():
                    source_file.unlink()
                    cleanup_result["files_removed"].append(file_path)
                    print(f"    🗑️  Removed: {file_path}")
            except Exception as e:
                cleanup_result["files_failed"].append(file_path)
                self.errors.append(f"Failed to remove {file_path}: {e}")

        return cleanup_result

    def execute_migration(self) -> dict[str, Any]:
        """Execute complete migration process following crawl_mcp.py methodology."""
        print("🚀 Starting Frontend File Migration (crawl_mcp.py methodology)")
        print(f"Source: {self.source_path}")
        print(f"Target: {self.config.frontend_repo_url}")
        print(f"Mode: {'DRY RUN' if self.config.dry_run else 'LIVE MIGRATION'}")
        print("=" * 70)

        try:
            # Step 1: Identify files
            files_identified = self.identify_files_to_migrate()

            # Step 2: Migrate files
            migration_result = self.migrate_files(files_identified)

            # Step 3: Cleanup (only if migration successful)
            cleanup_result = None
            if (
                migration_result.success
                and migration_result.files_migrated
                and not self.config.dry_run
            ):
                cleanup_result = self.cleanup_source_files(
                    migration_result.files_migrated
                )

            # Generate report
            report = {
                "migration_summary": {
                    "timestamp": datetime.now().isoformat(),
                    "dry_run": self.config.dry_run,
                    "success": migration_result.success,
                    "total_files_identified": sum(
                        len(files) for files in files_identified.values()
                    ),
                    "files_migrated": len(migration_result.files_migrated),
                    "files_skipped": len(migration_result.files_skipped),
                    "migration_time_seconds": migration_result.migration_time,
                },
                "file_categories": {},
                "migration_details": {
                    "migrated_files": migration_result.files_migrated,
                    "skipped_files": migration_result.files_skipped,
                    "errors": migration_result.errors,
                },
                "cleanup_results": cleanup_result or {},
            }

            # Add category details
            for category in self.file_categories:
                if category.files:
                    report["file_categories"][category.name] = {
                        "description": category.description,
                        "priority": category.priority,
                        "files_count": len(category.files),
                        "files": category.files,
                    }

            # Save report
            report_file = (
                self.source_path
                / f"frontend_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            print(f"\n📊 Migration Report: {report_file}")
            print("=" * 70)
            print(
                "✅ MIGRATION COMPLETED SUCCESSFULLY"
                if migration_result.success
                else "❌ MIGRATION FAILED"
            )

            return report

        except Exception as e:
            error_msg = f"Migration failed with error: {e}"
            print(f"\n❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
            }


def main():
    """Main function for CLI execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Frontend File Migration Tool")
    parser.add_argument(
        "--source",
        default="/Users/reh3376/repos/IGN_scripts",
        help="Source repository path",
    )
    parser.add_argument(
        "--frontend-repo",
        default="https://github.com/reh3376/ignition_tools_front.git",
        help="Frontend repository URL",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform dry run without actual changes"
    )
    parser.add_argument(
        "--no-backup", action="store_true", help="Skip creating backup of files"
    )

    args = parser.parse_args()

    config = MigrationConfig(
        source_repo_path=args.source,
        frontend_repo_url=args.frontend_repo,
        dry_run=args.dry_run,
        create_backup=not args.no_backup,
    )

    manager = FrontendFileMigrationManager(config)
    result = manager.execute_migration()

    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    exit(main())
