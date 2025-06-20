#!/usr/bin/env python3
"""Script to systematically fix type annotation issues in the codebase.

This script helps automate the process of adding missing return type annotations
and fixing common typing issues identified by mypy.
"""

import re
import sys
from pathlib import Path


class TypeAnnotationFixer:
    """Fixes common type annotation issues in Python files."""

    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0

    def add_none_return_annotations(self, file_path: Path) -> bool:
        """Add -> None annotations to functions that don't return values."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Pattern for functions without return type annotations
            # that likely should return None (have no return statements or return without value)

            lines = content.split("\n")
            modified = False

            for i, line in enumerate(lines):
                if re.match(r"\s*def\s+\w+.*:\s*$", line) and "->" not in line:
                    # Check if this function should have -> None
                    if self._should_add_none_annotation(lines, i):
                        # Add -> None before the colon
                        lines[i] = line.replace(":", " -> None:")
                        modified = True
                        self.fixes_applied += 1

            if modified:
                file_path.write_text("\n".join(lines), encoding="utf-8")
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def _should_add_none_annotation(self, lines: list[str], func_line_idx: int) -> bool:
        """Determine if a function should have -> None annotation."""
        # Simple heuristic: if function has no return statements with values
        # or only has bare return statements, it should return None

        # Find the end of the function (next def, class, or dedent)
        indent_level = len(lines[func_line_idx]) - len(lines[func_line_idx].lstrip())
        func_end = len(lines)

        for i in range(func_line_idx + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and line.strip():
                func_end = i
                break

        # Check return statements in the function
        has_return_with_value = False
        for i in range(func_line_idx + 1, func_end):
            line = lines[i].strip()
            if line.startswith("return ") and len(line) > 7:
                has_return_with_value = True
                break

        return not has_return_with_value

    def fix_click_decorators(self, file_path: Path) -> bool:
        """Add type annotations to Click command functions."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            modified = False

            for i, line in enumerate(lines):
                # Look for Click command functions
                if "@click." in line or "@" in line:
                    # Check if next few lines have a function definition without -> None
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if re.match(r"\s*def\s+\w+.*:\s*$", lines[j]) and "->" not in lines[j]:
                            # This is likely a Click command function
                            lines[j] = lines[j].replace(":", " -> None:")
                            modified = True
                            self.fixes_applied += 1
                            break

            if modified:
                file_path.write_text("\n".join(lines), encoding="utf-8")
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def add_missing_imports(self, file_path: Path) -> bool:
        """Add missing type imports."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check if we need to add typing imports
            needs_typing = False
            needs_any = "Any" in content and "from typing import" not in content
            needs_dict = "dict[" in content or "dict[" in content
            needs_list = "list[" in content or "list[" in content
            needs_optional = "Optional[" in content

            if needs_any or needs_dict or needs_list or needs_optional:
                needs_typing = True

            if needs_typing:
                # Find the best place to add the import
                lines = content.split("\n")
                import_line_idx = 0

                # Find existing imports
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        import_line_idx = i + 1
                    elif line.strip() and not line.startswith("#"):
                        break

                # Build the typing import
                typing_imports = []
                if needs_any:
                    typing_imports.append("Any")
                if needs_dict:
                    typing_imports.append("dict")
                if needs_list:
                    typing_imports.append("list")
                if needs_optional:
                    typing_imports.append("Optional")

                if typing_imports:
                    import_statement = f"from typing import {', '.join(typing_imports)}"
                    lines.insert(import_line_idx, import_statement)
                    file_path.write_text("\n".join(lines), encoding="utf-8")
                    self.fixes_applied += 1
                    return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def process_file(self, file_path: Path) -> None:
        """Process a single Python file."""
        print(f"Processing: {file_path}")
        self.files_processed += 1

        # Apply various fixes
        self.add_none_return_annotations(file_path)
        self.fix_click_decorators(file_path)
        self.add_missing_imports(file_path)

    def process_directory(self, directory: Path) -> None:
        """Process all Python files in a directory."""
        for py_file in directory.rglob("*.py"):
            # Skip certain directories
            if any(part.startswith(".") for part in py_file.parts):
                continue
            if "venv" in py_file.parts or "__pycache__" in py_file.parts:
                continue

            self.process_file(py_file)

    def report(self) -> None:
        """Print a summary of fixes applied."""
        print("\n📊 Type Annotation Fix Summary:")
        print(f"   Files Processed: {self.files_processed}")
        print(f"   Fixes Applied: {self.fixes_applied}")


def main():
    """Main function."""
    target_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src")

    print("🔧 Starting Type Annotation Fixes...")
    print(f"   Target: {target_path}")

    fixer = TypeAnnotationFixer()

    if target_path.is_file():
        fixer.process_file(target_path)
    else:
        fixer.process_directory(target_path)

    fixer.report()
    print("✅ Type annotation fixes complete!")


if __name__ == "__main__":
    main()
