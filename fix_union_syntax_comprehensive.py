#!/usr/bin/env python3
"""Comprehensive union syntax fixer for Python 3.8+ compatibility."""

import re
import sys
from pathlib import Path


def get_existing_imports(content: str) -> set[str]:
    """Extract existing typing imports from file content."""
    imports = set()

    # Match from typing import ...
    typing_import_pattern = r"from typing import (.+?)(?:\n|$)"
    matches = re.findall(typing_import_pattern, content, re.MULTILINE)

    for match in matches:
        # Split by comma and clean up
        import_items = [item.strip() for item in match.split(",")]
        imports.update(import_items)

    return imports


def add_typing_imports(content: str, needed_imports: set[str]) -> str:
    """Add missing typing imports to the file content."""
    existing_imports = get_existing_imports(content)
    missing_imports = needed_imports - existing_imports

    if not missing_imports:
        return content

    # Find the existing typing import line
    typing_import_pattern = r"from typing import (.+?)(?:\n|$)"
    match = re.search(typing_import_pattern, content, re.MULTILINE)

    if match:
        # Update existing import
        existing = match.group(1)
        all_imports = existing + ", " + ", ".join(sorted(missing_imports))
        new_import = f"from typing import {all_imports}"
        content = re.sub(typing_import_pattern, new_import + "\n", content, count=1)
    else:
        # Add new import after other imports
        import_section_end = 0
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_section_end = i + 1
            elif line.strip() == "" and i > 0:
                continue
            elif not line.startswith("#") and line.strip():
                break

        new_import = f"from typing import {', '.join(sorted(missing_imports))}"
        lines.insert(import_section_end, new_import)
        content = "\n".join(lines)

    return content


def fix_union_syntax_in_content(content: str) -> tuple[str, set[str]]:
    """Fix union syntax in content and return content and needed imports."""
    needed_imports = set()

    # Fix X | None -> Optional[X]
    def replace_optional(match):
        type_part = match.group(1)
        needed_imports.add("Optional")
        return f"Optional[{type_part}]"

    content = re.sub(r"(\w+(?:\[[^\]]+\])?)\s*\|\s*None", replace_optional, content)

    # Fix more complex union syntax like str | int | None
    def replace_complex_optional(match):
        types_part = match.group(1)
        needed_imports.add("Optional")
        needed_imports.add("Union")
        return f"Optional[Union[{types_part}]]"

    content = re.sub(
        r"(\w+(?:\[[^\]]+\])?\s*\|\s*\w+(?:\[[^\]]+\])?)\s*\|\s*None",
        replace_complex_optional,
        content,
    )

    # Fix dict[K, V] -> Dict[K, V]
    def replace_dict(match):
        key_value = match.group(1)
        needed_imports.add("Dict")
        return f"Dict[{key_value}]"

    content = re.sub(r"dict\[([^\]]+)\]", replace_dict, content)

    # Fix list[T] -> List[T]
    def replace_list(match):
        element_type = match.group(1)
        needed_imports.add("List")
        return f"List[{element_type}]"

    content = re.sub(r"list\[([^\]]+)\]", replace_list, content)

    return content, needed_imports


def fix_file(file_path: Path) -> bool:
    """Fix union syntax in a single file."""
    try:
        print(f"Processing {file_path.relative_to(Path.cwd())}")

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Fix union syntax
        fixed_content, needed_imports = fix_union_syntax_in_content(content)

        # Add missing imports
        if needed_imports:
            fixed_content = add_typing_imports(fixed_content, needed_imports)

        # Only write if content changed
        if fixed_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            print(f"  ✅ Fixed {file_path.name}")
            return True
        else:
            print(f"  ⏭️  No changes needed for {file_path.name}")
            return False

    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def main():
    """Fix union syntax in all Python files in the code intelligence module."""
    base_path = Path("src/ignition/code_intelligence")

    if not base_path.exists():
        print(f"❌ Path {base_path} does not exist")
        sys.exit(1)

    print("🔧 Fixing union syntax for Python 3.8+ compatibility")
    print("=" * 60)

    # Find all Python files
    python_files = list(base_path.glob("*.py"))

    fixed_count = 0
    total_count = len(python_files)

    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1

    print("=" * 60)
    print(f"✅ Completed: {fixed_count}/{total_count} files modified")

    if fixed_count > 0:
        print("🧪 Testing compilation...")

        # Test a few key files
        test_files = [
            "schema.py",
            "analyzer.py",
            "knowledge_discovery.py",
            "refactor_analyzer.py",
        ]

        import subprocess

        for test_file in test_files:
            test_path = base_path / test_file
            if test_path.exists():
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(test_path)],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode == 0:
                        print(f"  ✅ {test_file} compiles successfully")
                    else:
                        print(f"  ❌ {test_file} compilation failed:")
                        print(f"     {result.stderr}")
                except Exception as e:
                    print(f"  ❌ Error testing {test_file}: {e}")


if __name__ == "__main__":
    main()
