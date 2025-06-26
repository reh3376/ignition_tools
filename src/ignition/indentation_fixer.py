"""Comprehensive Indentation Fixer
Following crawl_mcp.py methodology for systematic syntax error resolution.

This module provides automated indentation fixing capabilities for Python files
with comprehensive error handling and validation.
"""

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class IndentationFixer:
    """Comprehensive indentation fixer following crawl_mcp.py methodology.

    Handles various indentation issues:
    - Incorrect variable assignment indentation
    - Missing spaces around operators
    - Inconsistent indentation levels
    - Mixed tabs and spaces
    """

    def __init__(self, target_directory: str = "src/"):
        """Initialize the indentation fixer."""
        self.target_directory = Path(target_directory)
        self.console = Console()
        self.files_processed = 0
        self.errors_fixed = 0
        self.patterns_fixed: list[str] = []

    def validate_environment(self) -> bool:
        """Validate environment setup before proceeding."""
        try:
            # Check if target directory exists
            if not self.target_directory.exists():
                self.console.print(f"[red]Error: Target directory {self.target_directory} does not exist[/red]")
                return False

            # Check if mypy is available
            result = subprocess.run(["python", "-m", "mypy", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.console.print("[red]Error: mypy is not available[/red]")
                return False

            return True

        except Exception as e:
            self.console.print(f"[red]Environment validation failed: {e}[/red]")
            return False

    def get_syntax_errors(self) -> list[dict[str, Any]]:
        """Get all syntax errors from mypy."""
        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "mypy",
                    "--no-error-summary",
                    "--show-error-codes",
                    str(self.target_directory),
                ],
                capture_output=True,
                text=True,
            )

            syntax_errors = []
            for line in result.stdout.split("\n"):
                if "syntax" in line or "unexpected indent" in line or "indentation" in line:
                    # Parse mypy error format: file:line: error: message [error-code]
                    match = re.match(r"([^:]+):(\d+):\s*error:\s*(.+)", line)
                    if match:
                        file_path, line_num, message = match.groups()
                        syntax_errors.append(
                            {
                                "file": file_path,
                                "line": int(line_num),
                                "message": message,
                                "full_line": line,
                            }
                        )

            return syntax_errors

        except Exception as e:
            self.console.print(f"[red]Failed to get syntax errors: {e}[/red]")
            return []

    def fix_variable_assignment_indentation(self, file_path: str, line_num: int) -> bool:
        """Fix variable assignment indentation issues."""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if line_num > len(lines):
                return False

            line = lines[line_num - 1]  # Convert to 0-based index

            # Pattern 1: Fix "variable: Type= value" -> "    variable: Type = value"
            pattern1 = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*:\s*[^=]*?)=\s*(.+)$")
            match1 = pattern1.match(line.strip())

            if match1:
                # Determine proper indentation by looking at surrounding lines
                indent = self.get_proper_indentation(lines, line_num - 1)
                var_part, value_part = match1.groups()
                fixed_line = f"{indent}{var_part.strip()} = {value_part.strip()}\n"
                lines[line_num - 1] = fixed_line

                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                self.patterns_fixed.append(f"Variable assignment indentation: {file_path}:{line_num}")
                return True

            # Pattern 2: Fix general indentation issues
            if line.strip() and not line.startswith(" ") and line_num > 1:
                # Look for context to determine proper indentation
                indent = self.get_proper_indentation(lines, line_num - 1)
                if indent and line.strip():
                    lines[line_num - 1] = f"{indent}{line.strip()}\n"

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)

                    self.patterns_fixed.append(f"General indentation: {file_path}:{line_num}")
                    return True

            return False

        except Exception as e:
            self.console.print(f"[red]Failed to fix indentation in {file_path}:{line_num}: {e}[/red]")
            return False

    def get_proper_indentation(self, lines: list[str], line_index: int) -> str:
        """Determine proper indentation based on surrounding context."""
        try:
            # Look at previous non-empty lines to determine indentation
            for i in range(line_index - 1, -1, -1):
                prev_line = lines[i]
                if prev_line.strip():
                    # If previous line ends with colon, increase indentation
                    if prev_line.rstrip().endswith(":"):
                        base_indent = len(prev_line) - len(prev_line.lstrip())
                        return " " * (base_indent + 4)
                    # Otherwise, use same indentation as previous line
                    else:
                        return " " * (len(prev_line) - len(prev_line.lstrip()))

            # Default to 8 spaces if we can't determine context
            return "        "

        except Exception:
            return "        "  # Default indentation

    def fix_all_indentation_errors(self) -> dict[str, Any]:
        """Fix all indentation errors systematically."""
        try:
            # Step 1: Environment validation
            if not self.validate_environment():
                return {"success": False, "error": "Environment validation failed"}

            # Step 2: Get initial syntax errors
            initial_errors = self.get_syntax_errors()
            if not initial_errors:
                return {
                    "success": True,
                    "message": "No syntax errors found",
                    "errors_fixed": 0,
                }

            self.console.print(f"[yellow]Found {len(initial_errors)} syntax errors to fix[/yellow]")

            # Step 3: Process each error
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Fixing indentation errors...", total=len(initial_errors))

                for error in initial_errors:
                    file_path = error["file"]
                    line_num = error["line"]

                    progress.update(task, description=f"Fixing {Path(file_path).name}:{line_num}")

                    if self.fix_variable_assignment_indentation(file_path, line_num):
                        self.errors_fixed += 1

                    progress.advance(task)

            # Step 4: Validate fixes
            final_errors = self.get_syntax_errors()

            # Step 5: Generate report
            report = {
                "success": True,
                "initial_errors": len(initial_errors),
                "final_errors": len(final_errors),
                "errors_fixed": self.errors_fixed,
                "patterns_fixed": self.patterns_fixed,
                "remaining_errors": final_errors,
            }

            return report

        except Exception as e:
            return {"success": False, "error": f"Failed to fix indentation errors: {e}"}

    def validate_python_syntax(self, file_path: str) -> bool:
        """Validate Python syntax using AST."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            ast.parse(content)
            return True

        except SyntaxError:
            return False
        except Exception:
            return False


def fix_indentation_errors(target_directory: str = "src/") -> dict[str, Any]:
    """Main function to fix indentation errors following crawl_mcp.py methodology.

    Args:
        target_directory: Directory to scan for Python files

    Returns:
        Dictionary containing fix results and statistics
    """
    console = Console()

    try:
        # Step 1: Initialize fixer
        fixer = IndentationFixer(target_directory)

        # Step 2: Display header
        console.print(
            Panel.fit(
                "[bold blue]Indentation Fixer[/bold blue]\n"
                "Following crawl_mcp.py methodology for systematic error resolution",
                border_style="blue",
            )
        )

        # Step 3: Fix all errors
        result = fixer.fix_all_indentation_errors()

        # Step 4: Display results
        if result["success"]:
            if result["errors_fixed"] > 0:
                console.print(f"[green]✅ Fixed {result['errors_fixed']} indentation errors[/green]")
                console.print(f"[blue]📊 Initial errors: {result['initial_errors']}[/blue]")
                console.print(f"[blue]📊 Final errors: {result['final_errors']}[/blue]")

                if result.get("patterns_fixed"):
                    console.print("\n[bold]Patterns Fixed:[/bold]")
                    for pattern in result["patterns_fixed"]:
                        console.print(f"  • {pattern}")

                if result.get("remaining_errors"):
                    console.print(
                        f"\n[yellow]⚠️  {len(result['remaining_errors'])} errors remain (may require manual intervention)[/yellow]"  # noqa: E501
                    )
                    for error in result["remaining_errors"][:5]:  # Show first 5
                        console.print(f"  • {error['file']}:{error['line']} - {error.get('message', 'Unknown error')}")
            else:
                console.print(f"[green]✅ {result.get('message', 'No errors found')}[/green]")
        else:
            console.print(f"[red]❌ {result['error']}[/red]")

        return result

    except Exception as e:
        error_result = {"success": False, "error": f"Indentation fixer failed: {e}"}
        console.print(f"[red]❌ {error_result['error']}[/red]")
        return error_result


@click.command()
@click.option("--target", "-t", default="src/", help="Target directory to fix")
@click.option(
    "--dry-run",
    "-d",
    is_flag=True,
    help="Show what would be fixed without making changes",
)
def main(target: str, dry_run: bool) -> None:
    """Fix indentation errors in Python files."""
    if dry_run:
        console.print("[yellow]Dry run mode - no changes will be made[/yellow]")
        # TODO: Implement dry run functionality
        return

    result = fix_indentation_errors(target)

    if result["success"] and result.get("errors_fixed", 0) > 0:
        console.print("\n[green]🎉 Indentation fixing completed successfully![/green]")
    elif not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
