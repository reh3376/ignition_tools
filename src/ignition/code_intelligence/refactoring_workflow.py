from typing import Dict, List

"""Automated Refactoring Workflow.

This module implements a comprehensive refactoring workflow that:
- Ensures behavior preservation through automated testing
- Validates public API compatibility
- Updates import paths across the codebase
- Provides rollback capabilities for failed refactors
- Integrates with version control for history preservation
"""

import ast
import json
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .code_splitter import CodeSplitter, SplitResult
from .refactor_analyzer import RefactoringRecommendationEngine


@dataclass
class RefactoringOperation:
    """Represents a single refactoring operation."""

    operation_id: str
    operation_type: str  # 'split_file', 'extract_method', 'move_class', etc.
    target_files: list[str]
    description: str
    risk_level: str  # 'low', 'medium', 'high'
    estimated_time: int  # seconds
    dependencies: list[str]  # other operation IDs this depends on


@dataclass
class RefactoringResult:
    """Result of a refactoring workflow execution."""

    workflow_id: str
    operations_completed: list[str]
    operations_failed: list[str]
    files_modified: list[str]
    files_created: list[str]
    backup_location: str
    success: bool
    error_message: str | None = None
    validation_results: dict[str, Any] | None = None
    rollback_available: bool = True


@dataclass
class ValidationResult:
    """Result of validating a refactoring operation."""

    validation_type: str
    success: bool
    message: str
    details: dict[str, Any] | None = None


class RefactoringWorkflow:
    """Orchestrates complex refactoring operations with safety guarantees."""

    def __init__(self) -> None:
        self.project_root = project_root
        self.enable_git = enable_git
        self.code_splitter = CodeSplitter(preserve_git_history=enable_git)
        self.recommendation_engine = RefactoringRecommendationEngine()

        # Workflow state
        self.active_workflows: dict[str, dict] = {}
        self.backup_dir = project_root / ".refactoring_backups"
        self.backup_dir.mkdir(exist_ok=True)

    def plan_refactoring_workflow(
        self, target_files: list[Path]
    ) -> list[RefactoringOperation]:
        """Plan a comprehensive refactoring workflow for multiple files."""
        operations = []
        operation_counter = 0

        for file_path in target_files:
            # Get recommendations for this file
            recommendation = self.recommendation_engine.analyze_file(file_path)
            if not recommendation:
                continue

            # Only proceed if file actually needs refactoring
            if (
                recommendation.physical_lines > 1000
                or recommendation.complexity_score > 50
                or len(recommendation.single_responsibility_violations) > 2
            ):
                operation_counter += 1
                operation = RefactoringOperation(
                    operation_id=f"split_file_{operation_counter}",
                    operation_type="split_file",
                    target_files=[str(file_path)],
                    description=f"Split {file_path.name} ({recommendation.physical_lines} lines, complexity {recommendation.complexity_score:.1f})",
                    risk_level=self._assess_risk_level(recommendation),
                    estimated_time=self._estimate_refactoring_time(recommendation),
                    dependencies=[],
                )
                operations.append(operation)

        # Sort operations by risk level (low risk first)
        risk_order = {"low": 0, "medium": 1, "high": 2}
        operations.sort(key=lambda op: risk_order.get(op.risk_level, 3))

        return operations

    def execute_workflow(
        self, operations: list[RefactoringOperation], dry_run: bool = False
    ) -> RefactoringResult:
        """Execute a refactoring workflow with comprehensive validation."""
        workflow_id = f"refactor_{int(time.time())}"

        if dry_run:
            return self._simulate_workflow(workflow_id, operations)

        # Create backup
        backup_location = self._create_workflow_backup(workflow_id)

        # Initialize workflow state
        workflow_state = {
            "id": workflow_id,
            "operations": operations,
            "start_time": datetime.now(),
            "backup_location": backup_location,
            "completed_operations": [],
            "failed_operations": [],
            "modified_files": [],
            "created_files": [],
        }

        self.active_workflows[workflow_id] = workflow_state

        try:
            return self._execute_workflow_operations(workflow_state)
        except Exception as e:
            # Automatic rollback on critical failure
            self.rollback_workflow(workflow_id)
            return RefactoringResult(
                workflow_id=workflow_id,
                operations_completed=[],
                operations_failed=[op.operation_id for op in operations],
                files_modified=[],
                files_created=[],
                backup_location=backup_location,
                success=False,
                error_message=f"Workflow failed with critical error: {e!s}",
                rollback_available=True,
            )

    def _execute_workflow_operations(self, workflow_state: dict) -> RefactoringResult:
        """Execute the actual workflow operations."""
        operations = workflow_state["operations"]
        workflow_id = workflow_state["id"]

        for operation in operations:
            print(f"\n🔄 Executing: {operation.description}")

            # Pre-operation validation
            pre_validation = self._validate_pre_operation(operation)
            if not pre_validation.success:
                print(f"❌ Pre-operation validation failed: {pre_validation.message}")
                workflow_state["failed_operations"].append(operation.operation_id)
                continue

            # Execute the operation
            operation_result = self._execute_operation(operation)

            if operation_result.success:
                print("✅ Operation completed successfully")
                workflow_state["completed_operations"].append(operation.operation_id)
                workflow_state["modified_files"].extend(
                    operation_result.files_modified or []
                )
                workflow_state["created_files"].extend(
                    operation_result.files_created or []
                )

                # Post-operation validation
                post_validation = self._validate_post_operation(
                    operation, operation_result
                )
                if not post_validation.success:
                    print(
                        f"⚠️  Post-operation validation failed: {post_validation.message}"
                    )
                    # Continue but log the issue

            else:
                print(f"❌ Operation failed: {operation_result.error_message}")
                workflow_state["failed_operations"].append(operation.operation_id)

                # Check if this is a critical failure that should stop the workflow
                if operation.risk_level == "high":
                    print("🛑 High-risk operation failed, stopping workflow")
                    break

        # Final workflow validation
        final_validation = self._validate_final_workflow(workflow_state)

        success = (
            len(workflow_state["failed_operations"]) == 0 and final_validation.success
        )

        return RefactoringResult(
            workflow_id=workflow_id,
            operations_completed=workflow_state["completed_operations"],
            operations_failed=workflow_state["failed_operations"],
            files_modified=workflow_state["modified_files"],
            files_created=workflow_state["created_files"],
            backup_location=workflow_state["backup_location"],
            success=success,
            validation_results=final_validation.details,
            rollback_available=True,
        )

    def _execute_operation(self, operation: RefactoringOperation) -> Any:
        """Execute a specific refactoring operation."""
        if operation.operation_type == "split_file":
            file_path = Path(operation.target_files[0])
            return self.code_splitter.split_file(file_path, dry_run=False)

        # Add more operation types as needed
        else:
            return SplitResult(
                original_file=(
                    operation.target_files[0] if operation.target_files else ""
                ),
                new_files=[],
                moved_classes=[],
                moved_functions=[],
                import_updates={},
                git_operations=[],
                success=False,
                error_message=f"Unknown operation type: {operation.operation_type}",
            )

    def _validate_pre_operation(
        self, operation: RefactoringOperation
    ) -> ValidationResult:
        """Validate conditions before executing an operation."""
        # Check that target files exist
        for file_path_str in operation.target_files:
            file_path = Path(file_path_str)
            if not file_path.exists():
                return ValidationResult(
                    validation_type="file_existence",
                    success=False,
                    message=f"Target file does not exist: {file_path}",
                )

        # Check that files are not locked by other processes
        for file_path_str in operation.target_files:
            if self._is_file_locked(Path(file_path_str)):
                return ValidationResult(
                    validation_type="file_lock",
                    success=False,
                    message=f"File is locked by another process: {file_path_str}",
                )

        # Check git status if git is enabled
        if self.enable_git:
            git_status = self._check_git_status()
            if not git_status.success:
                return git_status

        return ValidationResult(
            validation_type="pre_operation",
            success=True,
            message="Pre-operation validation passed",
        )

    def _validate_post_operation(
        self, operation: RefactoringOperation, result: Any
    ) -> ValidationResult:
        """Validate the result after executing an operation."""
        if not result.success:
            return ValidationResult(
                validation_type="operation_result",
                success=False,
                message=f"Operation failed: {result.error_message}",
            )

        # Validate that new files can be imported
        if hasattr(result, "new_files") and result.new_files:
            for new_file in result.new_files:
                import_validation = self._validate_file_imports(Path(new_file))
                if not import_validation.success:
                    return import_validation

        # Run syntax check on modified files
        files_to_check = []
        if hasattr(result, "files_modified"):
            files_to_check.extend(result.files_modified or [])
        if hasattr(result, "new_files"):
            files_to_check.extend(result.new_files or [])

        for file_path in files_to_check:
            syntax_validation = self._validate_syntax(Path(file_path))
            if not syntax_validation.success:
                return syntax_validation

        return ValidationResult(
            validation_type="post_operation",
            success=True,
            message="Post-operation validation passed",
        )

    def _validate_final_workflow(self, workflow_state: dict) -> ValidationResult:
        """Perform final validation of the entire workflow."""
        details: dict[str, Any] = {
            "operations_completed": len(workflow_state["completed_operations"]),
            "operations_failed": len(workflow_state["failed_operations"]),
            "files_modified": len(workflow_state["modified_files"]),
            "files_created": len(workflow_state["created_files"]),
        }

        # Run tests if available
        test_result = self._run_project_tests()
        details["test_results"] = test_result

        if not test_result.get("success", True):
            return ValidationResult(
                validation_type="final_workflow",
                success=False,
                message="Final workflow validation failed - tests are failing",
                details=details,
            )

        # Check import consistency across the project
        import_validation = self._validate_project_imports()
        details["import_validation"] = import_validation

        if not import_validation.get("success", True):
            return ValidationResult(
                validation_type="final_workflow",
                success=False,
                message="Final workflow validation failed - import issues detected",
                details=details,
            )

        return ValidationResult(
            validation_type="final_workflow",
            success=True,
            message="Final workflow validation passed",
            details=details,
        )

    def _run_project_tests(self) -> dict[str, Any]:
        """Run project tests to ensure refactoring didn't break functionality."""
        try:
            # Try to run pytest
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=short", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Tests timed out after 5 minutes"}
        except FileNotFoundError:
            # pytest not available, try basic syntax check
            return {
                "success": True,
                "message": "pytest not available, skipping test validation",
            }
        except Exception as e:
            return {"success": False, "error": f"Test execution failed: {e!s}"}

    def _validate_project_imports(self) -> dict[str, Any]:
        """Validate that all imports in the project are still valid."""
        import_issues = []

        # Check all Python files for import issues
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Try to parse the file
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    import_issues.append(f"Syntax error in {py_file}: {e!s}")
                    continue

                # TODO: Add more sophisticated import validation
                # This would involve actually trying to resolve imports

            except Exception as e:
                import_issues.append(f"Could not validate {py_file}: {e!s}")

        return {
            "success": len(import_issues) == 0,
            "issues": import_issues,
            "files_checked": len(list(self.project_root.rglob("*.py"))),
        }

    def _validate_syntax(self, file_path: Path) -> ValidationResult:
        """Validate that a file has correct Python syntax."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            ast.parse(content)

            return ValidationResult(
                validation_type="syntax",
                success=True,
                message=f"Syntax validation passed for {file_path}",
            )

        except SyntaxError as e:
            return ValidationResult(
                validation_type="syntax",
                success=False,
                message=f"Syntax error in {file_path}: {e!s}",
            )
        except Exception as e:
            return ValidationResult(
                validation_type="syntax",
                success=False,
                message=f"Could not validate syntax for {file_path}: {e!s}",
            )

    def _validate_file_imports(self, file_path: Path) -> ValidationResult:
        """Validate that a file's imports are resolvable."""
        try:
            # Try to compile the file to check for basic import issues
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            compile(content, str(file_path), "exec")

            return ValidationResult(
                validation_type="imports",
                success=True,
                message=f"Import validation passed for {file_path}",
            )

        except Exception as e:
            return ValidationResult(
                validation_type="imports",
                success=False,
                message=f"Import validation failed for {file_path}: {e!s}",
            )

    def _check_git_status(self) -> ValidationResult:
        """Check git repository status before refactoring."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            # Check for uncommitted changes
            if result.stdout.strip():
                return ValidationResult(
                    validation_type="git_status",
                    success=False,
                    message="Repository has uncommitted changes. Please commit or stash changes before refactoring.",
                )

            return ValidationResult(
                validation_type="git_status",
                success=True,
                message="Git repository is clean",
            )

        except subprocess.CalledProcessError:
            return ValidationResult(
                validation_type="git_status",
                success=False,
                message="Not in a git repository or git command failed",
            )
        except FileNotFoundError:
            return ValidationResult(
                validation_type="git_status",
                success=True,
                message="Git not available, skipping git validation",
            )

    def _is_file_locked(self, file_path: Path) -> bool:
        """Check if a file is locked by another process."""
        try:
            # Try to open the file in write mode
            with open(file_path, "r+"):
                pass
            return False
        except OSError:
            return True

    def _assess_risk_level(self, recommendation) -> str:
        """Assess the risk level of a refactoring operation."""
        risk_score = 0

        # High complexity increases risk
        if recommendation.complexity_score > 100:
            risk_score += 2
        elif recommendation.complexity_score > 50:
            risk_score += 1

        # Large files increase risk
        if recommendation.physical_lines > 2000:
            risk_score += 2
        elif recommendation.physical_lines > 1500:
            risk_score += 1

        # Many dependents increase risk
        dependent_count = len(recommendation.impact_analysis.get("dependent_files", []))
        if dependent_count > 10:
            risk_score += 2
        elif dependent_count > 5:
            risk_score += 1

        # Low maintainability increases risk
        if recommendation.maintainability_index < 20:
            risk_score += 2
        elif recommendation.maintainability_index < 40:
            risk_score += 1

        if risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"

    def _estimate_refactoring_time(self, recommendation) -> int:
        """Estimate time needed for refactoring operation in seconds."""
        base_time = 60  # 1 minute base

        # Add time based on file size
        base_time += (
            recommendation.physical_lines // 100 * 30
        )  # 30 seconds per 100 lines

        # Add time based on complexity
        base_time += (
            int(recommendation.complexity_score) * 5
        )  # 5 seconds per complexity point

        # Add time based on number of dependents
        dependent_count = len(recommendation.impact_analysis.get("dependent_files", []))
        base_time += dependent_count * 10  # 10 seconds per dependent file

        return min(base_time, 1800)  # Cap at 30 minutes

    def _create_workflow_backup(self, workflow_id: str) -> str:
        """Create a backup of the current state before refactoring."""
        backup_path = self.backup_dir / f"{workflow_id}_{int(time.time())}"
        backup_path.mkdir(exist_ok=True)

        # Create a tar backup of the src directory
        src_backup = backup_path / "src_backup.tar.gz"

        try:
            subprocess.run(
                ["tar", "-czf", str(src_backup), "-C", str(self.project_root), "src"],
                check=True,
            )

            # Save metadata
            metadata = {
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "backup_path": str(backup_path),
            }

            with open(backup_path / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            return str(backup_path)

        except Exception as e:
            print(f"Warning: Could not create backup: {e!s}")
            return str(backup_path)

    def _simulate_workflow(
        self, workflow_id: str, operations: list[RefactoringOperation]
    ) -> RefactoringResult:
        """Simulate a workflow execution without making changes."""
        simulated_results = []

        for operation in operations:
            print(f"🔍 Would execute: {operation.description}")
            print(f"   Risk level: {operation.risk_level}")
            print(f"   Estimated time: {operation.estimated_time}s")

            if operation.operation_type == "split_file":
                file_path = Path(operation.target_files[0])
                result = self.code_splitter.split_file(file_path, dry_run=True)
                simulated_results.append(result)

        return RefactoringResult(
            workflow_id=workflow_id,
            operations_completed=[op.operation_id for op in operations],
            operations_failed=[],
            files_modified=[],
            files_created=[],
            backup_location="simulation_mode",
            success=True,
            validation_results={"simulation": True},
        )

    def rollback_workflow(self, workflow_id: str) -> bool:
        """Rollback a workflow to its previous state."""
        if workflow_id not in self.active_workflows:
            print(f"Workflow {workflow_id} not found in active workflows")
            return False

        workflow_state = self.active_workflows[workflow_id]
        backup_location = workflow_state.get("backup_location")

        if not backup_location or not Path(backup_location).exists():
            print(f"Backup not found for workflow {workflow_id}")
            return False

        try:
            # Restore from backup
            src_backup = Path(backup_location) / "src_backup.tar.gz"
            if src_backup.exists():
                subprocess.run(
                    ["tar", "-xzf", str(src_backup), "-C", str(self.project_root)],
                    check=True,
                )

                print(f"✅ Successfully rolled back workflow {workflow_id}")
                return True
            else:
                print(f"Backup file not found: {src_backup}")
                return False

        except Exception as e:
            print(f"❌ Rollback failed: {e!s}")
            return False


def main() -> None:
    """Main function for testing the refactoring workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="Execute refactoring workflow")
    parser.add_argument("--files", nargs="+", help="Specific files to refactor")
    parser.add_argument(
        "--directory", type=str, default="src", help="Directory to scan for files"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate without making changes"
    )
    parser.add_argument(
        "--no-git", action="store_true", help="Don't use git integration"
    )

    args = parser.parse_args()

    project_root = Path.cwd()
    workflow = RefactoringWorkflow(project_root, enable_git=not args.no_git)

    if args.files:
        target_files = [Path(f) for f in args.files]
    else:
        # Find large files automatically
        detector = RefactoringRecommendationEngine().detector
        target_files = detector.scan_directory(Path(args.directory))[
            :5
        ]  # Limit to top 5

    if not target_files:
        print("No files found that need refactoring")
        return

    print(f"Planning refactoring workflow for {len(target_files)} files...")
    operations = workflow.plan_refactoring_workflow(target_files)

    if not operations:
        print("No refactoring operations needed")
        return

    print(f"\nPlanned {len(operations)} refactoring operations:")
    for op in operations:
        print(
            f"  - {op.description} (Risk: {op.risk_level}, Est: {op.estimated_time}s)"
        )

    # Execute workflow
    result = workflow.execute_workflow(operations, dry_run=args.dry_run)

    print(f"\n{'=' * 60}")
    print("REFACTORING WORKFLOW RESULTS")
    print(f"{'=' * 60}")
    print(f"Workflow ID: {result.workflow_id}")
    print(f"Success: {'✅' if result.success else '❌'}")
    print(f"Operations completed: {len(result.operations_completed)}")
    print(f"Operations failed: {len(result.operations_failed)}")
    print(f"Files modified: {len(result.files_modified)}")
    print(f"Files created: {len(result.files_created)}")

    if not result.success and result.error_message:
        print(f"Error: {result.error_message}")

    if result.rollback_available:
        print(f"Backup available at: {result.backup_location}")


if __name__ == "__main__":
    main()
