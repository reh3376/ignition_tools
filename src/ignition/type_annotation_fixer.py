"""Type Annotation Fixer - Automated mypy error resolution system.

Following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Robust error handling
4. Modular testing approach
5. Progressive complexity
6. Proper resource management
"""

import ast
import logging
import re
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MypyError:
    """Represents a single mypy error."""

    file_path: str
    line_number: int
    column: int | None
    error_type: str
    message: str
    rule_code: str


@dataclass
class FixResult:
    """Result of applying a fix."""

    success: bool
    fixes_applied: int
    errors_remaining: int
    message: str


class TypeAnnotationFixer:
    """Automated type annotation fixer following crawl_mcp.py methodology.

    Systematically fixes mypy errors with pattern-based solutions:
    - no-untyped-def: Add function return type annotations
    - var-annotated: Add variable type annotations
    - attr-defined: Fix attribute access issues
    - assignment: Fix type assignment mismatches
    - return-value: Fix return value type issues
    """

    def __init__(self, source_dir: str = "src"):
        """Initialize with environment validation first."""
        self.source_dir = Path(source_dir)
        self.validate_environment()

        # Common type mappings for intelligent inference
        self.type_mappings = {
            "None": "None",
            "True": "bool",
            "False": "bool",
            "[]": "list[Any]",
            "{}": "dict[str, Any]",
            '""': "str",
            "''": "str",
            'f""': "str",
            "f''": "str",
        }

        # Function return type patterns
        self.return_patterns = {
            r"return None": "None",
            r"return True|return False": "bool",
            r"return \[\]": "list[Any]",
            r"return \{\}": "dict[str, Any]",
            r'return ""': "str",
            r"return \d+": "int",
            r"return \d+\.\d+": "float",
        }

    def validate_environment(self) -> bool:
        """Validate environment setup before proceeding."""
        logger.info("🔍 Step 1: Environment Validation (crawl_mcp.py methodology)")

        try:
            # Check if source directory exists
            if not self.source_dir.exists():
                raise FileNotFoundError(f"Source directory {self.source_dir} not found")

            # Check if mypy is available
            result = subprocess.run(
                [sys.executable, "-m", "mypy", "--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError("mypy not available")

            # Check if ast module works
            ast.parse("def test(): pass")

            logger.info("✅ Environment validation successful")
            return True

        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            raise

    def validate_inputs(self, file_paths: list[str]) -> list[str]:
        """Validate and sanitize input file paths."""
        logger.info("🔍 Step 2: Input Validation (crawl_mcp.py methodology)")

        validated_paths = []
        for path_str in file_paths:
            try:
                path = Path(path_str)
                if not path.exists():
                    logger.warning(f"File not found: {path}")
                    continue
                if not path.suffix == ".py":
                    logger.warning(f"Not a Python file: {path}")
                    continue
                validated_paths.append(str(path))
            except Exception as e:
                logger.warning(f"Invalid path {path_str}: {e}")

        logger.info(f"✅ Validated {len(validated_paths)} files")
        return validated_paths

    def get_mypy_errors(self) -> list[MypyError]:
        """Get all mypy errors for the source directory."""
        logger.info("🔍 Step 3: Comprehensive Error Analysis")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mypy",
                    str(self.source_dir),
                    "--no-error-summary",
                ],
                capture_output=True,
                text=True,
            )

            errors = []
            for line in result.stdout.split("\n"):
                if "error:" in line:
                    error = self._parse_mypy_error(line)
                    if error:
                        errors.append(error)

            logger.info(f"📊 Found {len(errors)} mypy errors")
            return errors

        except Exception as e:
            logger.error(f"Failed to get mypy errors: {e}")
            return []

    def _parse_mypy_error(self, error_line: str) -> MypyError | None:
        """Parse a single mypy error line."""
        pattern = r"^(.+?):(\d+):(?:(\d+):)?\s*error:\s*(.+?)\s*\[(.+?)\]$"
        match = re.match(pattern, error_line)

        if match:
            return MypyError(
                file_path=match.group(1),
                line_number=int(match.group(2)),
                column=int(match.group(3)) if match.group(3) else None,
                message=match.group(4),
                rule_code=match.group(5),
                error_type=match.group(5),
            )
        return None

    def fix_no_untyped_def_errors(self, errors: list[MypyError]) -> FixResult:
        """Fix no-untyped-def errors by adding function type annotations."""
        logger.info("🔧 Fixing no-untyped-def errors")

        fixes_applied = 0
        files_processed = set()

        try:
            for error in errors:
                if error.rule_code == "no-untyped-def":
                    if self._fix_function_annotation(error):
                        fixes_applied += 1
                        files_processed.add(error.file_path)

            return FixResult(
                success=True,
                fixes_applied=fixes_applied,
                errors_remaining=0,  # Will be recalculated
                message=f"Fixed {fixes_applied} function annotations in {len(files_processed)} files",
            )

        except Exception as e:
            logger.error(f"Error fixing function annotations: {e}")
            return FixResult(
                success=False,
                fixes_applied=fixes_applied,
                errors_remaining=0,
                message=f"Failed after {fixes_applied} fixes: {e}",
            )

    def _fix_function_annotation(self, error: MypyError) -> bool:
        """Fix a single function annotation error."""
        try:
            file_path = Path(error.file_path)
            if not file_path.exists():
                return False

            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if error.line_number > len(lines):
                return False

            line = lines[error.line_number - 1]

            # Detect function definition pattern
            if "def " in line and ":" in line:
                # Add return type annotation
                if "->" not in line:
                    # Infer return type from function body
                    return_type = self._infer_return_type(lines, error.line_number)

                    # Insert return type annotation
                    colon_pos = line.rfind(":")
                    if colon_pos != -1:
                        new_line = (
                            line[:colon_pos] + f" -> {return_type}" + line[colon_pos:]
                        )
                        lines[error.line_number - 1] = new_line

                        # Write back to file
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.writelines(lines)
                        return True

            return False

        except Exception as e:
            logger.warning(
                f"Failed to fix function annotation in {error.file_path}:{error.line_number}: {e}"
            )
            return False

    def _infer_return_type(self, lines: list[str], func_line: int) -> str:
        """Infer return type from function body."""
        # Find function body
        indent_level = len(lines[func_line - 1]) - len(lines[func_line - 1].lstrip())

        for i in range(func_line, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith("#"):
                continue

            current_indent = len(lines[i]) - len(lines[i].lstrip())
            if current_indent <= indent_level and line and not line.startswith("def "):
                break

            # Check return statements
            if line.startswith("return "):
                return_value = line[7:].strip()

                # Pattern matching for return type inference
                for pattern, return_type in self.return_patterns.items():
                    if re.search(pattern, return_value):
                        return return_type

                # Simple value-based inference
                if return_value in self.type_mappings:
                    return self.type_mappings[return_value]

                # Default to Any for complex expressions
                return "Any"

        # No return statement found - likely returns None
        return "None"

    def fix_var_annotated_errors(self, errors: list[MypyError]) -> FixResult:
        """Fix var-annotated errors by adding variable type annotations."""
        logger.info("🔧 Fixing var-annotated errors")

        fixes_applied = 0
        files_processed = set()

        try:
            for error in errors:
                if error.rule_code == "var-annotated":
                    if self._fix_variable_annotation(error):
                        fixes_applied += 1
                        files_processed.add(error.file_path)

            return FixResult(
                success=True,
                fixes_applied=fixes_applied,
                errors_remaining=0,
                message=f"Fixed {fixes_applied} variable annotations in {len(files_processed)} files",
            )

        except Exception as e:
            logger.error(f"Error fixing variable annotations: {e}")
            return FixResult(
                success=False,
                fixes_applied=fixes_applied,
                errors_remaining=0,
                message=f"Failed after {fixes_applied} fixes: {e}",
            )

    def _fix_variable_annotation(self, error: MypyError) -> bool:
        """Fix a single variable annotation error."""
        try:
            file_path = Path(error.file_path)
            if not file_path.exists():
                return False

            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if error.line_number > len(lines):
                return False

            line = lines[error.line_number - 1]

            # Extract variable name from error message
            var_match = re.search(r'Need type annotation for "([^"]+)"', error.message)
            if not var_match:
                return False

            var_name = var_match.group(1)

            # Find assignment and infer type
            if "=" in line:
                var_type = self._infer_variable_type(line, var_name)

                # Add type annotation
                if ":" not in line.split("=")[0]:  # No existing annotation
                    assignment_pos = line.find("=")
                    var_part = line[:assignment_pos].strip()
                    value_part = line[assignment_pos:]

                    new_line = f"{var_part}: {var_type}{value_part}"
                    lines[error.line_number - 1] = new_line

                    # Write back to file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    return True

            return False

        except Exception as e:
            logger.warning(
                f"Failed to fix variable annotation in {error.file_path}:{error.line_number}: {e}"
            )
            return False

    def _infer_variable_type(self, line: str, var_name: str) -> str:
        """Infer variable type from assignment."""
        if "=" not in line:
            return "Any"

        value_part = line.split("=", 1)[1].strip()

        # Direct mappings
        if value_part in self.type_mappings:
            return self.type_mappings[value_part]

        # Pattern-based inference
        if value_part.startswith("[") and value_part.endswith("]"):
            return "list[Any]"
        elif value_part.startswith("{") and value_part.endswith("}"):
            if ":" in value_part:
                return "dict[str, Any]"
            else:
                return "set[Any]"
        elif value_part.startswith("(") and value_part.endswith(")"):
            return "tuple[Any, ...]"
        elif value_part.isdigit():
            return "int"
        elif re.match(r"\d+\.\d+", value_part):
            return "float"
        elif value_part.startswith('"') or value_part.startswith("'"):
            return "str"

        return "Any"

    def fix_all_errors(
        self, error_types: list[str] | None = None
    ) -> dict[str, FixResult]:
        """Fix all mypy errors systematically."""
        logger.info("🚀 Starting comprehensive mypy error fixing")

        if error_types is None:
            error_types = ["no-untyped-def", "var-annotated"]

        results = {}

        try:
            # Get initial errors
            errors = self.get_mypy_errors()
            logger.info(f"📊 Initial error count: {len(errors)}")

            # Group errors by type
            errors_by_type = {}
            for error in errors:
                if error.rule_code not in errors_by_type:
                    errors_by_type[error.rule_code] = []
                errors_by_type[error.rule_code].append(error)

            # Fix each error type
            for error_type in error_types:
                if error_type in errors_by_type:
                    logger.info(
                        f"🔧 Processing {error_type} errors ({len(errors_by_type[error_type])} found)"
                    )

                    if error_type == "no-untyped-def":
                        result = self.fix_no_untyped_def_errors(
                            errors_by_type[error_type]
                        )
                    elif error_type == "var-annotated":
                        result = self.fix_var_annotated_errors(
                            errors_by_type[error_type]
                        )
                    else:
                        result = FixResult(
                            success=False,
                            fixes_applied=0,
                            errors_remaining=len(errors_by_type[error_type]),
                            message=f"Handler for {error_type} not implemented yet",
                        )

                    results[error_type] = result
                    logger.info(f"✅ {error_type}: {result.message}")

            # Get final error count
            final_errors = self.get_mypy_errors()
            logger.info(f"📊 Final error count: {len(final_errors)}")

            return results

        except Exception as e:
            logger.error(f"❌ Critical error in fix_all_errors: {e}")
            raise

    @contextmanager
    def error_handling_context(self, operation_name: str) -> Any:
        """Context manager for comprehensive error handling."""
        logger.info(f"🔍 Starting {operation_name}")
        try:
            yield
            logger.info(f"✅ {operation_name} completed successfully")
        except Exception as e:
            logger.error(f"❌ {operation_name} failed: {e}")
            raise

    def generate_report(self, results: dict[str, FixResult]) -> str:
        """Generate comprehensive report following crawl_mcp.py methodology."""
        logger.info("📊 Generating comprehensive report")

        report = [
            "# Type Annotation Fixer Report",
            "Generated using crawl_mcp.py methodology",
            "",
            "## Summary",
            "",
        ]

        total_fixes = sum(result.fixes_applied for result in results.values())
        successful_operations = sum(1 for result in results.values() if result.success)

        report.extend(
            [
                f"- **Total fixes applied**: {total_fixes}",
                f"- **Successful operations**: {successful_operations}/{len(results)}",
                f"- **Source directory**: {self.source_dir}",
                "",
                "## Detailed Results",
                "",
            ]
        )

        for error_type, result in results.items():
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            report.extend(
                [
                    f"### {error_type} - {status}",
                    f"- Fixes applied: {result.fixes_applied}",
                    f"- Message: {result.message}",
                    "",
                ]
            )

        report.extend(
            [
                "## Next Steps",
                "",
                "1. Run `python -m mypy src/` to verify remaining errors",
                "2. Review automated changes for correctness",
                "3. Run tests to ensure functionality preserved",
                "4. Commit changes with descriptive message",
                "",
            ]
        )

        return "\n".join(report)


def main() -> None:
    """Main entry point following crawl_mcp.py methodology."""
    logger.info("🚀 Type Annotation Fixer - Following crawl_mcp.py methodology")

    try:
        fixer = TypeAnnotationFixer()

        with fixer.error_handling_context("Comprehensive Type Fixing"):
            results = fixer.fix_all_errors(["no-untyped-def", "var-annotated"])

            # Generate and save report
            report = fixer.generate_report(results)

            report_path = Path("type_annotation_fix_report.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)

            logger.info(f"📋 Report saved to {report_path}")
            print(report)

    except Exception as e:
        logger.error(f"❌ Critical failure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
