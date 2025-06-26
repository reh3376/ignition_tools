"""Automated Syntax Fixer for Python Code.

This module provides comprehensive automated fixing of Python syntax issues
following the crawl_mcp.py methodology for systematic code repair.
"""

import ast
import re
from pathlib import Path
from typing import Any


class AutomatedSyntaxFixer:
    """Automated syntax fixer following crawl_mcp.py methodology."""

    def __init__(self):
        """Initialize the syntax fixer."""
        self.fixes_applied = []
        self.errors_found = []

    def fix_file(self, file_path: str | Path) -> dict[str, Any]:
        """Fix syntax issues in a single file.

        Args:
            file_path: Path to the Python file to fix

        Returns:
            Dictionary with fix results
        """
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File not found: {path}"}

        try:
            with open(path) as f:
                original_content = f.read()

            # Apply fixes in order
            fixed_content = original_content
            fixes_applied = []

            # 1. Fix indentation issues
            fixed_content, indent_fixes = self._fix_indentation_issues(fixed_content)
            fixes_applied.extend(indent_fixes)

            # 2. Fix incomplete try/except blocks
            fixed_content, try_fixes = self._fix_incomplete_try_blocks(fixed_content)
            fixes_applied.extend(try_fixes)

            # 3. Fix hanging parentheses and brackets
            fixed_content, paren_fixes = self._fix_hanging_parentheses(fixed_content)
            fixes_applied.extend(paren_fixes)

            # 4. Fix variable assignment syntax
            fixed_content, assign_fixes = self._fix_variable_assignments(fixed_content)
            fixes_applied.extend(assign_fixes)

            # 5. Fix incomplete function definitions
            fixed_content, func_fixes = self._fix_incomplete_functions(fixed_content)
            fixes_applied.extend(func_fixes)

            # Test if the fixed content is valid Python
            try:
                ast.parse(fixed_content)

                # Write back the fixed content
                with open(path, "w") as f:
                    f.write(fixed_content)

                return {
                    "success": True,
                    "file": str(path),
                    "fixes_applied": fixes_applied,
                    "lines_changed": len(fixes_applied),
                }

            except SyntaxError as e:
                return {
                    "success": False,
                    "file": str(path),
                    "error": f"Syntax error after fixes: {e.msg} at line {e.lineno}",
                    "fixes_attempted": fixes_applied,
                }

        except Exception as e:
            return {"success": False, "file": str(path), "error": f"Error processing file: {e}"}

    def _fix_indentation_issues(self, content: str) -> tuple[str, list[str]]:
        """Fix indentation issues in Python code."""
        lines = content.split("\n")
        fixed_lines = []
        fixes = []

        for i, line in enumerate(lines):
            line_num = i + 1

            # Check for variable assignments at wrong indentation
            if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*: dict\[str, Any\] = \{", line.strip()):
                # Find the proper indentation level
                proper_indent = self._find_proper_indentation(lines, i)
                if proper_indent != len(line) - len(line.lstrip()):
                    fixed_line = " " * proper_indent + line.strip()
                    fixed_lines.append(fixed_line)
                    fixes.append(f"Line {line_num}: Fixed indentation for variable assignment")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines), fixes

    def _fix_incomplete_try_blocks(self, content: str) -> tuple[str, list[str]]:
        """Fix incomplete try/except blocks."""
        lines = content.split("\n")
        fixed_lines = []
        fixes = []

        i = 0
        while i < len(lines):
            line = lines[i]
            line_num = i + 1

            # Check for try block without proper except/finally
            if line.strip() == "try:":
                # Look ahead to see if there's a proper except/finally
                has_except_or_finally = False
                try_indent = len(line) - len(line.lstrip())

                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if next_line.strip() == "":
                        j += 1
                        continue

                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= try_indent:
                        # Same or less indentation, check if it's except/finally
                        if next_line.strip().startswith(("except", "finally")):
                            has_except_or_finally = True
                        break
                    j += 1

                if not has_except_or_finally:
                    # Add a basic except block
                    fixed_lines.append(line)
                    fixed_lines.append(" " * (try_indent + 4) + "pass  # TODO: Add try block content")
                    fixed_lines.append(" " * try_indent + "except Exception as e:")
                    fixed_lines.append(" " * (try_indent + 4) + "pass  # TODO: Handle exception")
                    fixes.append(f"Line {line_num}: Added except block for incomplete try")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        return "\n".join(fixed_lines), fixes

    def _fix_hanging_parentheses(self, content: str) -> tuple[str, list[str]]:
        """Fix hanging parentheses and brackets."""
        lines = content.split("\n")
        fixed_lines = []
        fixes = []

        for i, line in enumerate(lines):
            line_num = i + 1

            # Check for lines ending with opening parentheses/brackets without proper closure
            if line.strip().endswith(("(", "[", "{")):
                # Count opening vs closing brackets in subsequent lines
                open_count = line.count("(") + line.count("[") + line.count("{")
                close_count = line.count(")") + line.count("]") + line.count("}")

                if open_count > close_count:
                    # Look ahead to see if it's properly closed
                    balance = open_count - close_count
                    j = i + 1
                    while j < len(lines) and balance > 0:
                        next_line = lines[j]
                        balance += next_line.count("(") + next_line.count("[") + next_line.count("{")
                        balance -= next_line.count(")") + next_line.count("]") + next_line.count("}")
                        j += 1

                    if balance > 0:
                        # Add closing brackets
                        closing_chars = ")" * line.count("(") + "]" * line.count("[") + "}" * line.count("{")
                        fixed_lines.append(line + closing_chars)
                        fixes.append(f"Line {line_num}: Added missing closing brackets")
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines), fixes

    def _fix_variable_assignments(self, content: str) -> tuple[str, list[str]]:
        """Fix malformed variable assignments."""
        lines = content.split("\n")
        fixed_lines = []
        fixes = []

        for i, line in enumerate(lines):
            line_num = i + 1

            # Fix malformed type annotations with assignments
            if re.search(r": dict\[str, Any\]= ", line):
                fixed_line = re.sub(r": dict\[str, Any\]= ", ": dict[str, Any] = ", line)
                fixed_lines.append(fixed_line)
                fixes.append(f"Line {line_num}: Fixed spacing in type annotation assignment")
            elif re.search(r": list\[Any\] \| str= ", line):
                fixed_line = re.sub(r": list\[Any\] \| str= ", ": list[Any] | str = ", line)
                fixed_lines.append(fixed_line)
                fixes.append(f"Line {line_num}: Fixed spacing in union type assignment")
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines), fixes

    def _fix_incomplete_functions(self, content: str) -> tuple[str, list[str]]:
        """Fix incomplete function definitions."""
        lines = content.split("\n")
        fixed_lines = []
        fixes = []

        for i, line in enumerate(lines):
            line_num = i + 1

            # Check for function definitions without body
            if re.match(r"^\s*(def|async def)\s+\w+\([^)]*\)\s*->\s*[^:]*:\s*$", line):
                # Check if next line has content
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if not next_line.strip() or not next_line.startswith(" "):
                        # Add pass statement
                        func_indent = len(line) - len(line.lstrip())
                        fixed_lines.append(line)
                        fixed_lines.append(" " * (func_indent + 4) + "pass  # TODO: Implement function")
                        fixes.append(f"Line {line_num}: Added pass statement for empty function")
                    else:
                        fixed_lines.append(line)
                else:
                    # End of file, add pass
                    func_indent = len(line) - len(line.lstrip())
                    fixed_lines.append(line)
                    fixed_lines.append(" " * (func_indent + 4) + "pass  # TODO: Implement function")
                    fixes.append(f"Line {line_num}: Added pass statement for empty function at EOF")
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines), fixes

    def _find_proper_indentation(self, lines: list[str], current_line: int) -> int:
        """Find the proper indentation level for a line based on context."""
        # Look backwards to find the containing scope
        for i in range(current_line - 1, max(0, current_line - 20), -1):
            line = lines[i].strip()
            if line.endswith(":") and (
                "def " in line
                or "class " in line
                or "if " in line
                or "for " in line
                or "while " in line
                or "try:" in line
                or "except" in line
                or "finally:" in line
            ):
                # Found a scope-defining line, indent 4 spaces from it
                base_indent = len(lines[i]) - len(lines[i].lstrip())
                return base_indent + 4

        # Default to no indentation if no scope found
        return 0

    def fix_directory(self, directory: str | Path, pattern: str = "*.py") -> dict[str, Any]:
        """Fix all Python files in a directory.

        Args:
            directory: Directory to process
            pattern: File pattern to match

        Returns:
            Summary of fixes applied
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {dir_path}"}

        python_files = list(dir_path.rglob(pattern))
        results = []

        for file_path in python_files:
            result = self.fix_file(file_path)
            results.append(result)

        successful_fixes = [r for r in results if r["success"]]
        failed_fixes = [r for r in results if not r["success"]]

        return {
            "success": True,
            "directory": str(dir_path),
            "files_processed": len(results),
            "files_fixed": len(successful_fixes),
            "files_failed": len(failed_fixes),
            "total_fixes": sum(len(r.get("fixes_applied", [])) for r in successful_fixes),
            "successful_files": [r["file"] for r in successful_fixes],
            "failed_files": [{"file": r["file"], "error": r["error"]} for r in failed_fixes],
        }


def main():
    """Main function for command-line usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python automated_syntax_fixer.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]
    fixer = AutomatedSyntaxFixer()

    target_path = Path(target)
    if target_path.is_file():
        result = fixer.fix_file(target_path)
        print(f"Fixed {target}: {result}")
    elif target_path.is_dir():
        result = fixer.fix_directory(target_path)
        print(f"Fixed directory {target}: {result}")
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
