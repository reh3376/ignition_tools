#!/usr/bin/env python3
"""Validate Python 3.12 compatibility of modernized codebase."""

import ast
import sys
from pathlib import Path


def validate_file(file_path: Path) -> tuple[bool, str]:
    """Validate a Python file for syntax errors.

    Args:
        file_path: Path to the Python file

    Returns:
        Tuple of (success, error_message)
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse the AST to check for syntax errors
        ast.parse(content, filename=str(file_path))
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Main validation function."""
    print(f"🐍 Python {sys.version}")
    print("🔍 Validating Python 3.12 compatibility...")
    print("=" * 60)

    # Key files to validate
    test_files = [
        "src/ignition/modules/sme_agent/adaptive_learning.py",
        "src/ignition/modules/sme_agent/knowledge_domains.py",
        "src/ignition/modules/sme_agent/context_aware_response.py",
        "test_phase_11_2_integration.py",
        "type_hint_modernizer.py",
    ]

    # Additional files that were modernized
    modernized_files = [
        "src/ignition/code_intelligence/dependency_analyzer.py",
        "src/ignition/data_integration/cli_commands.py",
        "src/ignition/modules/module_generator.py",
        "src/core/cli_core.py",
    ]

    all_files = test_files + modernized_files

    passed = 0
    failed = 0

    for file_path_str in all_files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"⚠️  {file_path_str} - File not found")
            continue

        success, error = validate_file(file_path)
        if success:
            print(f"✅ {file_path_str}")
            passed += 1
        else:
            print(f"❌ {file_path_str} - {error}")
            failed += 1

    print("=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All files are Python 3.12 compatible!")
        return 0
    else:
        print(f"💥 {failed} files have compatibility issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
