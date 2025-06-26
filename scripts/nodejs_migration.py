#!/usr/bin/env python3
"""
Node.js Dependencies Migration Script - Following crawl_mcp.py Methodology

This script migrates Node.js dependencies (package.json, node_modules) from
the backend repository to the frontend repository, following the systematic
approach defined in crawl_mcp.py.
"""

import json
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    import git
    from git.exc import InvalidGitRepositoryError as InvalidGitRepository
except ImportError:
    print("GitPython not installed. Install with: pip install GitPython")
    exit(1)


@dataclass
class NodeJSMigrationConfig:
    """Configuration for Node.js dependencies migration."""
    
    source_repo_path: str
    frontend_repo_url: str
    dry_run: bool = False
    create_backup: bool = True


class NodeJSMigrator:
    """Migrate Node.js dependencies following crawl_mcp.py methodology."""
    
    def __init__(self, config: NodeJSMigrationConfig):
        self.config = config
        self.source_path = Path(config.source_repo_path)
        
        # Validate environment
        if not self._validate_environment():
            raise ValueError("Environment validation failed")
    
    def _validate_environment(self) -> bool:
        """Step 1: Environment validation (crawl_mcp.py methodology)."""
        print("🔍 Step 1: Environment Validation...")
        
        try:
            # Validate source repository
            if not self.source_path.exists():
                print(f"❌ Source path does not exist: {self.source_path}")
                return False
            
            # Validate git repository
            try:
                git.Repo(self.source_path)
                print("✅ Source repository validation passed")
            except InvalidGitRepository as e:
                print(f"❌ Invalid git repository: {e}")
                return False
            
            # Check for Node.js files
            package_json = self.source_path / "package.json"
            node_modules = self.source_path / "node_modules"
            
            if not package_json.exists():
                print("❌ package.json not found in source repository")
                return False
            
            if not node_modules.exists():
                print("❌ node_modules directory not found in source repository")
                return False
            
            print("✅ Node.js dependencies found and ready for migration")
            return True
            
        except Exception as e:
            print(f"❌ Environment validation failed: {e}")
            return False
    
    def migrate_nodejs_dependencies(self) -> dict:
        """Step 2: Migrate Node.js dependencies to frontend repository."""
        print("\n🚀 Step 2: Migrating Node.js dependencies...")
        
        result = {
            "success": False,
            "files_migrated": [],
            "errors": [],
            "migration_time": 0.0
        }
        
        start_time = datetime.now()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                frontend_repo_path = Path(temp_dir) / "frontend"
                
                if not self.config.dry_run:
                    print("  📥 Cloning frontend repository...")
                    git.Repo.clone_from(self.config.frontend_repo_url, frontend_repo_path)
                    frontend_repo = git.Repo(frontend_repo_path)
                else:
                    print(f"  [DRY RUN] Would clone: {self.config.frontend_repo_url}")
                
                # Files to migrate
                files_to_migrate = [
                    ("package.json", self.source_path / "package.json"),
                    ("node_modules", self.source_path / "node_modules")
                ]
                
                # Migrate each file/directory
                for name, source_path in files_to_migrate:
                    if not source_path.exists():
                        result["errors"].append(f"Source {name} not found: {source_path}")
                        continue
                    
                    if not self.config.dry_run:
                        target_path = frontend_repo_path / name
                        
                        try:
                            if source_path.is_dir():
                                print(f"  📁 Copying directory: {name}")
                                shutil.copytree(source_path, target_path)
                            else:
                                print(f"  📄 Copying file: {name}")
                                shutil.copy2(source_path, target_path)
                            
                            result["files_migrated"].append(name)
                            print(f"    ✅ {name} migrated successfully")
                            
                        except Exception as e:
                            error_msg = f"Failed to migrate {name}: {e}"
                            result["errors"].append(error_msg)
                            print(f"    ❌ {error_msg}")
                    else:
                        result["files_migrated"].append(name)
                        print(f"  [DRY RUN] Would migrate: {name}")
                
                # Commit and push changes
                if not self.config.dry_run and result["files_migrated"] and not result["errors"]:
                    print("\n  📤 Committing and pushing changes...")
                    frontend_repo.index.add(result["files_migrated"])
                    frontend_repo.index.commit(
                        f"feat: add Node.js dependencies for frontend development\n\n"
                        f"Migrated from backend repository:\n"
                        f"- package.json: Tailwind CSS dependencies\n"
                        f"- node_modules/: Frontend build tools and dependencies\n\n"
                        f"This enables proper frontend development environment."
                    )
                    frontend_repo.remote().push()
                    print("    ✅ Changes pushed to frontend repository")
                    result["success"] = True
                elif self.config.dry_run:
                    print("  [DRY RUN] Would commit and push changes")
                    result["success"] = True
                
        except Exception as e:
            error_msg = f"Migration failed: {e}"
            result["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        end_time = datetime.now()
        result["migration_time"] = (end_time - start_time).total_seconds()
        
        return result
    
    def cleanup_source_files(self, migrated_files: list[str]) -> dict:
        """Step 3: Clean up migrated files from source repository."""
        print("\n🧹 Step 3: Cleaning up source repository...")
        
        cleanup_result = {
            "files_removed": [],
            "files_failed": [],
            "backup_created": False
        }
        
        if self.config.dry_run:
            print("  [DRY RUN] Would remove migrated files from source repository")
            return cleanup_result
        
        try:
            # Create backup if requested
            if self.config.create_backup:
                backup_dir = (
                    self.source_path
                    / "migration_backup"
                    / datetime.now().strftime("%Y%m%d_%H%M%S")
                    / "nodejs_migration"
                )
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                for file_name in migrated_files:
                    source_file = self.source_path / file_name
                    if source_file.exists():
                        backup_file = backup_dir / file_name
                        if source_file.is_dir():
                            shutil.copytree(source_file, backup_file)
                        else:
                            shutil.copy2(source_file, backup_file)
                
                cleanup_result["backup_created"] = True
                print(f"  📦 Backup created: {backup_dir}")
            
            # Remove files from source
            for file_name in migrated_files:
                source_file = self.source_path / file_name
                if source_file.exists():
                    try:
                        if source_file.is_dir():
                            shutil.rmtree(source_file)
                        else:
                            source_file.unlink()
                        
                        cleanup_result["files_removed"].append(file_name)
                        print(f"  🗑️  Removed: {file_name}")
                        
                    except Exception as e:
                        error_msg = f"Failed to remove {file_name}: {e}"
                        cleanup_result["files_failed"].append(error_msg)
                        print(f"  ❌ {error_msg}")
        
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
        
        return cleanup_result
    
    def execute_migration(self) -> dict:
        """Execute complete Node.js migration following crawl_mcp.py methodology."""
        print("🚀 Starting Node.js Dependencies Migration (crawl_mcp.py methodology)")
        print("=" * 70)
        
        try:
            # Step 2: Migration
            migration_result = self.migrate_nodejs_dependencies()
            
            # Step 3: Cleanup (only if migration successful)
            cleanup_result = None
            if (
                migration_result["success"]
                and migration_result["files_migrated"]
                and not self.config.dry_run
            ):
                cleanup_result = self.cleanup_source_files(
                    migration_result["files_migrated"]
                )
            
            # Generate report
            report = {
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "source_repo": str(self.source_path),
                    "frontend_repo": self.config.frontend_repo_url,
                    "dry_run": self.config.dry_run,
                },
                "migration_results": {
                    "success": migration_result["success"],
                    "files_migrated": migration_result["files_migrated"],
                    "migration_time": migration_result["migration_time"],
                    "errors": migration_result["errors"],
                },
                "cleanup_results": cleanup_result or {},
            }
            
            # Save report
            report_file = (
                self.source_path
                / f"nodejs_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            
            print(f"\n📊 Migration Report: {report_file}")
            print("=" * 70)
            print(
                "✅ NODEJS MIGRATION COMPLETED SUCCESSFULLY"
                if migration_result["success"]
                else "❌ NODEJS MIGRATION FAILED"
            )
            
            return report
            
        except Exception as e:
            error_msg = f"Migration execution failed: {e}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
            }


def main():
    """Main function for Node.js dependencies migration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Node.js Dependencies Migration Tool")
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
    
    config = NodeJSMigrationConfig(
        source_repo_path=args.source,
        frontend_repo_url=args.frontend_repo,
        dry_run=args.dry_run,
        create_backup=not args.no_backup,
    )
    
    migrator = NodeJSMigrator(config)
    result = migrator.execute_migration()
    
    exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main() 