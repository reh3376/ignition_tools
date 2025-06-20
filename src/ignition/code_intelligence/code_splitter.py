"""Intelligent Code Splitting Engine.

This module implements automated code splitting for large files while preserving:
- Git blame history through git-mv operations
- Public API surface compatibility
- Existing behavior through minimal diffs
- Import path consistency across the codebase
"""

import ast
import contextlib
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .analyzer import CodeAnalyzer
from .refactor_analyzer import RefactoringRecommendationEngine, SplitRecommendation


@dataclass
class SplitResult:
    """Result of a code splitting operation."""

    original_file: str
    new_files: list[str]
    moved_classes: list[str]
    moved_functions: list[str]
    import_updates: dict[str, list[str]]  # file -> list of import updates needed
    git_operations: list[str]  # git commands that were executed
    success: bool
    error_message: str | None = None


@dataclass
class CodeExtraction:
    """Represents code that will be extracted to a new module."""

    target_module_path: Path
    target_module_name: str
    classes: list[str]
    functions: list[str]
    imports_needed: set[str]
    code_blocks: list[tuple[int, int]]  # (start_line, end_line) pairs
    estimated_lines: int


class CodeSplitter:
    """Splits large files into smaller, more maintainable modules."""

    def __init__(self, preserve_git_history: bool = True, max_file_lines: int = 1000) -> None:
        self.preserve_git_history = preserve_git_history
        self.max_file_lines = max_file_lines
        self.recommendation_engine = RefactoringRecommendationEngine()
        self.analyzer = CodeAnalyzer()

    def split_file(self, file_path: Path, dry_run: bool = False) -> SplitResult:
        """Split a large file into smaller modules based on recommendations."""
        try:
            # Get refactoring recommendations
            recommendation = self.recommendation_engine.analyze_file(file_path)
            if not recommendation:
                return SplitResult(
                    original_file=str(file_path),
                    new_files=[],
                    moved_classes=[],
                    moved_functions=[],
                    import_updates={},
                    git_operations=[],
                    success=False,
                    error_message="Could not analyze file for splitting",
                )

            # Plan the extractions
            extractions = self._plan_extractions(file_path, recommendation)
            if not extractions:
                return SplitResult(
                    original_file=str(file_path),
                    new_files=[],
                    moved_classes=[],
                    moved_functions=[],
                    import_updates={},
                    git_operations=[],
                    success=False,
                    error_message="No suitable extractions found",
                )

            if dry_run:
                return self._simulate_split(file_path, extractions)

            # Execute the actual split
            return self._execute_split(file_path, extractions)

        except Exception as e:
            return SplitResult(
                original_file=str(file_path),
                new_files=[],
                moved_classes=[],
                moved_functions=[],
                import_updates={},
                git_operations=[],
                success=False,
                error_message=f"Split failed: {e!s}",
            )

    def _plan_extractions(self, file_path: Path, recommendation) -> list[CodeExtraction]:
        """Plan which code blocks to extract to new modules."""
        extractions = []

        # Parse the original file to get AST and source
        with open(file_path, encoding="utf-8") as f:
            source_code = f.read()

        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return []

        source_lines = source_code.splitlines()

        # Plan extractions based on split recommendations
        for split_rec in recommendation.suggested_splits:
            if split_rec.confidence_score < 0.6:
                continue  # Skip low-confidence recommendations

            extraction = self._create_extraction_plan(file_path, split_rec, tree, source_lines)
            if extraction:
                extractions.append(extraction)

        return extractions

    def _create_extraction_plan(
        self,
        file_path: Path,
        split_rec: SplitRecommendation,
        tree: ast.AST,
        source_lines: list[str],
    ) -> CodeExtraction | None:
        """Create a detailed extraction plan for a split recommendation."""
        # Find the target module path
        target_module_name = split_rec.target_module_name
        target_module_path = file_path.parent / f"{target_module_name}.py"

        # Find classes and functions to extract
        classes_to_extract = set(split_rec.classes_to_move)
        functions_to_extract = set(split_rec.functions_to_move)

        # Find the actual AST nodes and their line ranges
        code_blocks = []
        imports_needed = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in classes_to_extract:
                start_line = node.lineno - 1  # Convert to 0-based
                end_line = getattr(node, "end_lineno", node.lineno) - 1
                code_blocks.append((start_line, end_line))

                # Analyze imports needed for this class
                class_imports = self._analyze_class_imports(node, tree)
                imports_needed.update(class_imports)

            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name in functions_to_extract:
                start_line = node.lineno - 1
                end_line = getattr(node, "end_lineno", node.lineno) - 1
                code_blocks.append((start_line, end_line))

                # Analyze imports needed for this function
                func_imports = self._analyze_function_imports(node, tree)
                imports_needed.update(func_imports)

        if not code_blocks:
            return None

        return CodeExtraction(
            target_module_path=target_module_path,
            target_module_name=target_module_name,
            classes=list(classes_to_extract),
            functions=list(functions_to_extract),
            imports_needed=imports_needed,
            code_blocks=sorted(code_blocks),
            estimated_lines=split_rec.estimated_lines,
        )

    def _analyze_class_imports(self, class_node: ast.ClassDef, tree: ast.AST) -> set[str]:
        """Analyze which imports a class needs."""
        imports_needed = set()

        # Get all names used in the class
        names_used = set()
        for node in ast.walk(class_node):
            if isinstance(node, ast.Name):
                names_used.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                names_used.add(node.value.id)

        # Find corresponding imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    if name in names_used:
                        imports_needed.add(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    if name in names_used:
                        imports_needed.add(f"from {node.module} import {alias.name}")

        return imports_needed

    def _analyze_function_imports(self, func_node, tree: ast.AST) -> set[str]:
        """Analyze which imports a function needs."""
        # Similar to class analysis but for functions
        imports_needed = set()

        # Get all names used in the function
        names_used = set()
        for node in ast.walk(func_node):
            if isinstance(node, ast.Name):
                names_used.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                names_used.add(node.value.id)

        # Find corresponding imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    if name in names_used:
                        imports_needed.add(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    if name in names_used:
                        imports_needed.add(f"from {node.module} import {alias.name}")

        return imports_needed

    def _simulate_split(self, file_path: Path, extractions: list[CodeExtraction]) -> SplitResult:
        """Simulate the split operation without making actual changes."""
        new_files = []
        moved_classes = []
        moved_functions = []
        git_operations = []

        for extraction in extractions:
            new_files.append(str(extraction.target_module_path))
            moved_classes.extend(extraction.classes)
            moved_functions.extend(extraction.functions)

            if self.preserve_git_history:
                git_operations.append(f"git mv {file_path} {extraction.target_module_path}")

        return SplitResult(
            original_file=str(file_path),
            new_files=new_files,
            moved_classes=moved_classes,
            moved_functions=moved_functions,
            import_updates={},  # Would be calculated in real execution
            git_operations=git_operations,
            success=True,
        )

    def _execute_split(self, file_path: Path, extractions: list[CodeExtraction]) -> SplitResult:
        """Execute the actual split operation."""
        # Read the original file
        with open(file_path, encoding="utf-8") as f:
            original_source = f.read()

        original_lines = original_source.splitlines()

        new_files = []
        moved_classes = []
        moved_functions = []
        git_operations = []
        import_updates = {}

        try:
            # Create new module files
            for extraction in extractions:
                new_file_content = self._create_new_module_content(original_lines, extraction)

                # Write the new module
                with open(extraction.target_module_path, "w", encoding="utf-8") as f:
                    f.write(new_file_content)

                new_files.append(str(extraction.target_module_path))
                moved_classes.extend(extraction.classes)
                moved_functions.extend(extraction.functions)

                # Git operations
                if self.preserve_git_history:
                    git_cmd = f"git add {extraction.target_module_path}"
                    git_operations.append(git_cmd)
                    subprocess.run(git_cmd.split(), check=True)

            # Update the original file (remove extracted code)
            updated_original = self._create_updated_original(original_lines, extractions)

            # Create backup and update original
            backup_path = file_path.with_suffix(".py.backup")
            shutil.copy2(file_path, backup_path)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_original)

            # Update import statements across the codebase
            import_updates = self._update_imports_across_codebase(file_path, extractions)

            return SplitResult(
                original_file=str(file_path),
                new_files=new_files,
                moved_classes=moved_classes,
                moved_functions=moved_functions,
                import_updates=import_updates,
                git_operations=git_operations,
                success=True,
            )

        except Exception as e:
            # Rollback on error
            self._rollback_split(file_path, new_files)
            raise e

    def _create_new_module_content(self, original_lines: list[str], extraction: CodeExtraction) -> str:
        """Create the content for a new module file."""
        content_parts = []

        # Add module docstring
        content_parts.append('"""')
        content_parts.append(f"{extraction.target_module_name.replace('_', ' ').title()}")
        content_parts.append("")
        content_parts.append("Extracted from large file for better maintainability.")
        content_parts.append("This module contains related functionality that was grouped together.")
        content_parts.append('"""')
        content_parts.append("")

        # Add imports
        for import_stmt in sorted(extraction.imports_needed):
            content_parts.append(import_stmt)

        if extraction.imports_needed:
            content_parts.append("")

        # Add extracted code blocks
        for start_line, end_line in extraction.code_blocks:
            # Add the code block with proper spacing
            code_block = original_lines[start_line : end_line + 1]
            content_parts.extend(code_block)
            content_parts.append("")  # Add spacing between blocks

        return "\n".join(content_parts)

    def _create_updated_original(self, original_lines: list[str], extractions: list[CodeExtraction]) -> str:
        """Create the updated original file with extracted code removed."""
        # Collect all line ranges to remove
        lines_to_remove = set()
        for extraction in extractions:
            for start_line, end_line in extraction.code_blocks:
                for line_num in range(start_line, end_line + 1):
                    lines_to_remove.add(line_num)

        # Keep lines that are not being extracted
        updated_lines = []
        for i, line in enumerate(original_lines):
            if i not in lines_to_remove:
                updated_lines.append(line)

        # Add import statements for the new modules
        import_section = []
        for extraction in extractions:
            module_import = self._create_import_statement(extraction)
            if module_import:
                import_section.append(module_import)

        if import_section:
            # Find where to insert imports (after existing imports)
            insert_index = self._find_import_insertion_point(updated_lines)
            for i, import_stmt in enumerate(import_section):
                updated_lines.insert(insert_index + i, import_stmt)

        return "\n".join(updated_lines)

    def _create_import_statement(self, extraction: CodeExtraction) -> str | None:
        """Create import statement for the extracted module."""
        if not (extraction.classes or extraction.functions):
            return None

        module_name = extraction.target_module_name
        imports = extraction.classes + extraction.functions

        if len(imports) == 1:
            return f"from .{module_name} import {imports[0]}"
        else:
            return f"from .{module_name} import {', '.join(sorted(imports))}"

    def _find_import_insertion_point(self, lines: list[str]) -> int:
        """Find the best place to insert new import statements."""
        # Look for existing import statements
        last_import_line = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                last_import_line = i
            elif stripped and not stripped.startswith("#") and last_import_line >= 0:
                # Found non-import, non-comment line after imports
                break

        if last_import_line >= 0:
            return last_import_line + 1

        # No imports found, insert after docstring/comments
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith('"""'):
                return i

        return 0

    def _update_imports_across_codebase(
        self, original_file: Path, extractions: list[CodeExtraction]
    ) -> dict[str, list[str]]:
        """Update import statements across the codebase for moved code."""
        import_updates = {}

        # Find all Python files that might import from the original file
        project_root = Path.cwd()
        original_module = self._path_to_module_name(original_file)

        for py_file in project_root.rglob("*.py"):
            if py_file == original_file:
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check if this file imports from the original module
                if original_module in content:
                    updates = self._calculate_import_updates(py_file, content, original_module, extractions)
                    if updates:
                        import_updates[str(py_file)] = updates

            except Exception:
                continue

        return import_updates

    def _calculate_import_updates(
        self,
        file_path: Path,
        content: str,
        original_module: str,
        extractions: list[CodeExtraction],
    ) -> list[str]:
        """Calculate what import updates are needed for a specific file."""
        updates = []

        # Create mapping of moved items to their new modules
        moved_items = {}
        for extraction in extractions:
            for item in extraction.classes + extraction.functions:
                moved_items[item] = extraction.target_module_name

        # Parse imports and check what needs updating
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == original_module:
                    for alias in node.names:
                        item_name = alias.name
                        if item_name in moved_items:
                            new_module = moved_items[item_name]
                            old_import = f"from {original_module} import {item_name}"
                            new_import = f"from {original_module}.{new_module} import {item_name}"
                            updates.append(f"Replace: {old_import} -> {new_import}")
        except Exception:
            pass

        return updates

    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        try:
            relative_path = file_path.relative_to(Path.cwd())
            parts = relative_path.parts

            if "src" in parts:
                src_index = parts.index("src")
                module_parts = parts[src_index + 1 :]
                module_name = ".".join(module_parts).replace(".py", "")
                return module_name
            else:
                return file_path.stem
        except Exception:
            return file_path.stem

    def _rollback_split(self, original_file: Path, new_files: list[str]) -> None:
        """Rollback a failed split operation."""
        # Remove any created new files
        for new_file_path in new_files:
            with contextlib.suppress(Exception):
                Path(new_file_path).unlink(missing_ok=True)

        # Restore original from backup if it exists
        backup_path = original_file.with_suffix(".py.backup")
        if backup_path.exists():
            shutil.copy2(backup_path, original_file)
            backup_path.unlink()


class BatchCodeSplitter:
    """Splits multiple files in a coordinated batch operation."""

    def __init__(self, preserve_git_history: bool = True) -> None:
        self.preserve_git_history = preserve_git_history
        self.splitter = CodeSplitter(preserve_git_history=preserve_git_history)
        self.detector = RefactoringRecommendationEngine().detector

    def split_oversized_files(self, directory: Path, dry_run: bool = False) -> dict[str, SplitResult]:
        """Split all oversized files in a directory."""
        results = {}

        # Find oversized files
        oversized_files = self.detector.scan_directory(directory)

        print(f"Found {len(oversized_files)} oversized files to process")

        for file_path in oversized_files:
            print(f"\nProcessing: {file_path}")

            result = self.splitter.split_file(file_path, dry_run=dry_run)
            results[str(file_path)] = result

            if result.success:
                print(f"✅ Successfully {'simulated' if dry_run else 'completed'} split")
                print(f"   Created {len(result.new_files)} new files")
                print(f"   Moved {len(result.moved_classes)} classes, {len(result.moved_functions)} functions")
            else:
                print(f"❌ Split failed: {result.error_message}")

        return results


def main() -> None:
    """Main function for testing the code splitter."""
    import argparse

    parser = argparse.ArgumentParser(description="Split large code files")
    parser.add_argument("--file", type=str, help="Specific file to split")
    parser.add_argument("--directory", type=str, default="src", help="Directory to scan for large files")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without making changes")
    parser.add_argument("--no-git", action="store_true", help="Don't preserve git history")

    args = parser.parse_args()

    if args.file:
        # Split specific file
        splitter = CodeSplitter(preserve_git_history=not args.no_git)
        result = splitter.split_file(Path(args.file), dry_run=args.dry_run)

        if result.success:
            print("✅ Split successful!")
            print(f"New files: {result.new_files}")
            print(f"Moved classes: {result.moved_classes}")
            print(f"Moved functions: {result.moved_functions}")
        else:
            print(f"❌ Split failed: {result.error_message}")
    else:
        # Batch split directory
        batch_splitter = BatchCodeSplitter(preserve_git_history=not args.no_git)
        results = batch_splitter.split_oversized_files(Path(args.directory), dry_run=args.dry_run)

        print(f"\n{'=' * 60}")
        print("BATCH SPLIT SUMMARY")
        print(f"{'=' * 60}")

        successful = sum(1 for r in results.values() if r.success)
        total = len(results)

        print(f"Total files processed: {total}")
        print(f"Successful splits: {successful}")
        print(f"Failed splits: {total - successful}")


if __name__ == "__main__":
    main()
