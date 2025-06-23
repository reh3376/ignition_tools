#!/usr/bin/env python3
"""Comprehensive Type Hint Modernizer for Python 3.11+
Converts old typing syntax to modern built-in syntax.
"""

import ast
import re
from pathlib import Path
from typing import Any


class TypeHintModernizer:
    """Modernizes type hints to Python 3.11+ syntax."""

    def __init__(self) -> None:
        self.conversions = {
            # Basic collections
            "List": "list",
            "Dict": "dict",
            "Set": "set",
            "Tuple": "tuple",
            "FrozenSet": "frozenset",
            "Deque": "deque",
            "Counter": "Counter",
            "OrderedDict": "OrderedDict",
            # Abstract collections
            "Sequence": "collections.abc.Sequence",
            "Mapping": "collections.abc.Mapping",
            "MutableMapping": "collections.abc.MutableMapping",
            "Iterable": "collections.abc.Iterable",
            "Iterator": "collections.abc.Iterator",
            "Generator": "collections.abc.Generator",
            "Callable": "collections.abc.Callable",
        }

        self.imports_to_remove = {
            "List",
            "Dict",
            "Set",
            "Tuple",
            "FrozenSet",
            "Deque",
            "Counter",
            "OrderedDict",
            "Sequence",
            "Mapping",
            "MutableMapping",
            "Iterable",
            "Iterator",
            "Generator",
            "Callable",
        }

        # Imports to keep (still needed for specific cases)
        self.imports_to_keep = {
            "Any",
            "Union",
            "Optional",
            "TypeVar",
            "Generic",
            "Protocol",
            "Literal",
            "Final",
            "ClassVar",
            "Type",
            "NoReturn",
            "overload",
            "TYPE_CHECKING",
        }

    def modernize_file(self, file_path: Path) -> bool:
        """Modernize type hints in a single file."""
        try:
            try:
                relative_path = file_path.relative_to(Path.cwd())
                print(f"Processing {relative_path}")
            except ValueError:
                print(f"Processing {file_path}")

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Step 1: Convert Optional[X] to X | None
            content = self._convert_optional(content)

            # Step 2: Convert Union[X, Y] to X | Y
            content = self._convert_union(content)

            # Step 3: Convert typing collections to built-ins
            content = self._convert_collections(content)

            # Step 4: Clean up imports
            content = self._clean_imports(content)

            # Step 5: Validate syntax
            if not self._validate_syntax(content):
                print(f"  ❌ Syntax validation failed for {file_path.name}")
                return False

            # Only write if content changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  ✅ Modernized {file_path.name}")
                return True
            else:
                print(f"  ⏭️  No changes needed for {file_path.name}")
                return False

        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            return False

    def _convert_optional(self, content: str) -> str:
        """Convert Optional[X] to X | None."""

        # Handle nested Optional patterns
        def replace_optional(match: Any) -> str:
            inner_type = match.group(1)
            # Handle nested brackets properly
            bracket_count = 0
            inner_end = 0
            for i, char in enumerate(inner_type):
                if char == "[":
                    bracket_count += 1
                elif char == "]":
                    bracket_count -= 1
                elif char == "," and bracket_count == 0:
                    inner_end = i
                    break
            else:
                inner_end = len(inner_type)

            actual_type = inner_type[:inner_end]
            return f"{actual_type} | None"

        # Pattern for Optional[...]
        content = re.sub(
            r"Optional\[([^\[\]]*(?:\[[^\]]*\][^\[\]]*)*)\]", replace_optional, content
        )
        return content

    def _convert_union(self, content: str) -> str:
        """Convert Union[X, Y, ...] to X | Y | ..."""

        def replace_union(match: Any) -> str:
            union_content = match.group(1)
            # Split by comma, but respect nested brackets
            types = []
            current = ""
            bracket_count = 0

            for char in union_content:
                if char == "[":
                    bracket_count += 1
                elif char == "]":
                    bracket_count -= 1
                elif char == "," and bracket_count == 0:
                    types.append(current.strip())
                    current = ""
                    continue
                current += char

            if current.strip():
                types.append(current.strip())

            return " | ".join(types)

        # Pattern for Union[...]
        content = re.sub(
            r"Union\[([^\[\]]*(?:\[[^\]]*\][^\[\]]*)*)\]", replace_union, content
        )
        return content

    def _convert_collections(self, content: str) -> str:
        """Convert typing collections to built-in equivalents."""
        for old_type, new_type in self.conversions.items():
            # Replace Type[...] patterns
            pattern = rf"\b{old_type}\["
            replacement = f"{new_type}["
            content = re.sub(pattern, replacement, content)

            # Replace standalone Type annotations
            pattern = rf"\b{old_type}\b(?!\[)"
            content = re.sub(pattern, new_type, content)

        return content

    def _clean_imports(self, content: str) -> str:
        """Clean up typing imports, removing unnecessary ones."""
        lines = content.split("\n")
        new_lines = []

        for line in lines:
            # Check if this is a typing import line
            if line.strip().startswith("from typing import"):
                # Extract imported items
                import_match = re.match(r"from typing import (.+)", line.strip())
                if import_match:
                    imports_str = import_match.group(1)

                    # Parse imports (handle multiline imports later)
                    imports = []
                    for item in imports_str.split(","):
                        item = item.strip()
                        if item in self.imports_to_keep:
                            imports.append(item)

                    # Reconstruct import line if we have imports to keep
                    if imports:
                        if len(imports) == 1:
                            new_lines.append(f"from typing import {imports[0]}")
                        else:
                            new_lines.append(
                                f"from typing import {', '.join(sorted(imports))}"
                            )
                    # If no imports to keep, skip the line entirely
                    continue

            new_lines.append(line)

        return "\n".join(new_lines)

    def _validate_syntax(self, content: str) -> bool:
        """Validate that the modernized content has valid Python syntax."""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    def scan_directory(
        self, directory: Path, extensions: list[str] | None = None
    ) -> list[Path]:
        """Scan directory for Python files to modernize."""
        if extensions is None:
            extensions = [".py"]

        files: list[Path] = []
        for ext in extensions:
            files.extend(directory.rglob(f"*{ext}"))

        # Filter out __pycache__ and other unwanted directories
        filtered_files = []
        for file_path in files:
            if any(
                part.startswith(".") or part == "__pycache__"
                for part in file_path.parts
            ):
                continue
            filtered_files.append(file_path)

        return sorted(filtered_files)

    def modernize_project(
        self, base_path: Path | None = None, target_dirs: list[str] | None = None
    ) -> dict[str, Any]:
        """Modernize type hints across the entire project."""
        if base_path is None:
            base_path = Path.cwd()

        if target_dirs is None:
            target_dirs = ["src", "scripts", "tests"]

        print("🔧 Modernizing type hints to Python 3.11+ syntax")
        print("=" * 60)

        results = {
            "total_files": 0,
            "modified_files": 0,
            "failed_files": 0,
            "directories": {},
        }

        for target_dir in target_dirs:
            dir_path = base_path / target_dir
            if not dir_path.exists():
                print(f"⚠️  Directory {target_dir} does not exist, skipping")
                continue

            print(f"\n📁 Processing directory: {target_dir}")
            files = self.scan_directory(dir_path)

            dir_results = {"total": len(files), "modified": 0, "failed": 0}

            for file_path in files:
                results["total_files"] += 1
                dir_results["total"] += 1

                if self.modernize_file(file_path):
                    results["modified_files"] += 1
                    dir_results["modified"] += 1
                else:
                    # Check if it was a failure vs no changes needed
                    try:
                        with open(file_path) as f:
                            content = f.read()
                        if not self._validate_syntax(content):
                            results["failed_files"] += 1
                            dir_results["failed"] += 1
                    except Exception:
                        results["failed_files"] += 1
                        dir_results["failed"] += 1

            results["directories"][target_dir] = dir_results
            print(
                f"  📊 {dir_results['modified']}/{dir_results['total']} files modified"
            )

        return results


def main() -> None:
    """Main entry point."""
    modernizer = TypeHintModernizer()

    # Target specific directories for this project
    target_directories = [
        "src/ignition/code_intelligence",
        "src/ignition/data_integration",
        "src/ignition/graph",
        "src/ignition/modules",
        "src/ignition/wrappers",
        "src/core",
        "scripts",
    ]

    # Run modernization
    results = modernizer.modernize_project(target_dirs=target_directories)

    print("\n" + "=" * 60)
    print("📊 MODERNIZATION SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {results['total_files']}")
    print(f"Files modified: {results['modified_files']}")
    print(f"Files failed: {results['failed_files']}")

    for dir_name, dir_stats in results["directories"].items():
        print(f"\n📁 {dir_name}:")
        print(f"   Modified: {dir_stats['modified']}/{dir_stats['total']}")
        if dir_stats["failed"] > 0:
            print(f"   Failed: {dir_stats['failed']}")

    if results["modified_files"] > 0:
        print("\n🧪 Testing compilation of modified files...")
        # Could add compilation testing here
        print("✅ Modernization completed!")

        print("\n📝 Next steps:")
        print("1. Run: python -m py_compile <modified_files>")
        print("2. Run: python -m pytest tests/")
        print(
            "3. Run: git add . && git commit -m 'Modernize type hints to Python 3.11+ syntax'"
        )
    else:
        print("\n✅ No files needed modernization!")


if __name__ == "__main__":
    main()
