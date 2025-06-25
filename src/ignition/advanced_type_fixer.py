"""Advanced Type Fixer - Complex mypy error resolution patterns.

Following crawl_mcp.py methodology for advanced error patterns:
- attr-defined: Object attribute access issues
- index: Index access issues
- assignment: Type assignment mismatches
- return-value: Return value type mismatches
- arg-type: Argument type issues
"""

import logging
import re
import sys
from pathlib import Path

from .type_annotation_fixer import FixResult, MypyError, TypeAnnotationFixer

logger = logging.getLogger(__name__)


class AdvancedTypeFixer(TypeAnnotationFixer):
    """Extended fixer for complex type annotation patterns."""

    def __init__(self, source_dir: str = "src"):
        """Initialize with additional patterns for complex fixes."""
        super().__init__(source_dir)

        # Common attribute patterns
        self.attribute_patterns = {
            "append": "list[Any]",
            "extend": "list[Any]",
            "keys": "dict[str, Any]",
            "values": "dict[str, Any]",
            "items": "dict[str, Any]",
            "get": "dict[str, Any]",
            "update": "dict[str, Any]",
            "add": "set[Any]",
            "remove": "set[Any]",
            "split": "str",
            "join": "str",
            "replace": "str",
            "strip": "str",
            "startswith": "str",
            "endswith": "str",
        }

        # Index access patterns
        self.index_patterns = {
            r"\[\d+\]": "list[Any] | tuple[Any, ...] | str",
            r'\[[\'"]\w+[\'"]\]': "dict[str, Any]",
            r"\[:\]": "list[Any] | str",
            r"\[\d*:\d*\]": "list[Any] | str",
        }

    def fix_attr_defined_errors(self, errors: list[MypyError]) -> FixResult:
        """Fix attr-defined errors by adding proper type annotations."""
        logger.info("🔧 Fixing attr-defined errors")

        fixes_applied = 0
        files_processed = set()

        try:
            for error in errors:
                if error.rule_code == "attr-defined":
                    if self._fix_attribute_error(error):
                        fixes_applied += 1
                        files_processed.add(error.file_path)

            return FixResult(
                success=True,
                fixes_applied=fixes_applied,
                errors_remaining=0,
                message=f"Fixed {fixes_applied} attribute access issues in {len(files_processed)} files",
            )

        except Exception as e:
            logger.error(f"Error fixing attribute errors: {e}")
            return FixResult(
                success=False,
                fixes_applied=fixes_applied,
                errors_remaining=0,
                message=f"Failed after {fixes_applied} fixes: {e}",
            )

    def _fix_attribute_error(self, error: MypyError) -> bool:
        """Fix a single attribute access error."""
        try:
            file_path = Path(error.file_path)
            if not file_path.exists():
                return False

            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            if error.line_number > len(lines):
                return False

            line = lines[error.line_number - 1]

            # Extract object and attribute from error
            obj_attr_match = re.search(
                r'"(.+?)" has no attribute "(.+?)"', error.message
            )
            if not obj_attr_match:
                return False

            obj_type = obj_attr_match.group(1)
            attr_name = obj_attr_match.group(2)

            # If it's an "object" type, we need to find the variable and annotate it
            if obj_type == "object":
                return self._fix_object_attribute(file_path, lines, error, attr_name)

            return False

        except Exception as e:
            logger.warning(
                f"Failed to fix attribute error in {error.file_path}:{error.line_number}: {e}"
            )
            return False

    def _fix_object_attribute(
        self, file_path: Path, lines: list[str], error: MypyError, attr_name: str
    ) -> bool:
        """Fix object attribute access by inferring proper type."""
        try:
            # Find the variable assignment in the function
            current_line = error.line_number - 1

            # Look backwards to find variable assignments
            for i in range(current_line, max(0, current_line - 50), -1):
                line = lines[i]

                # Look for assignments that could be the object
                if "=" in line and not line.strip().startswith("#"):
                    # Extract variable name from current error line
                    error_line = lines[current_line]
                    var_match = re.search(r"(\w+)\." + re.escape(attr_name), error_line)
                    if var_match:
                        var_name = var_match.group(1)

                        # Check if this line assigns to that variable
                        if var_name in line.split("=")[0]:
                            # Infer type from attribute name
                            if attr_name in self.attribute_patterns:
                                inferred_type = self.attribute_patterns[attr_name]

                                # Add type annotation if not present
                                if ":" not in line.split("=")[0]:
                                    assignment_pos = line.find("=")
                                    var_part = line[:assignment_pos].strip()
                                    value_part = line[assignment_pos:]

                                    new_line = (
                                        f"{var_part}: {inferred_type}{value_part}"
                                    )
                                    lines[i] = new_line

                                    # Write back to file
                                    with open(file_path, "w", encoding="utf-8") as f:
                                        f.write("\n".join(lines))
                                    return True

            return False

        except Exception as e:
            logger.warning(f"Failed to fix object attribute: {e}")
            return False

    def fix_index_errors(self, errors: list[MypyError]) -> FixResult:
        """Fix index access errors."""
        logger.info("🔧 Fixing index errors")

        fixes_applied = 0
        files_processed = set()

        try:
            for error in errors:
                if error.rule_code == "index":
                    if self._fix_index_error(error):
                        fixes_applied += 1
                        files_processed.add(error.file_path)

            return FixResult(
                success=True,
                fixes_applied=fixes_applied,
                errors_remaining=0,
                message=f"Fixed {fixes_applied} index access issues in {len(files_processed)} files",
            )

        except Exception as e:
            logger.error(f"Error fixing index errors: {e}")
            return FixResult(
                success=False,
                fixes_applied=fixes_applied,
                errors_remaining=0,
                message=f"Failed after {fixes_applied} fixes: {e}",
            )

    def _fix_index_error(self, error: MypyError) -> bool:
        """Fix a single index access error."""
        try:
            file_path = Path(error.file_path)
            if not file_path.exists():
                return False

            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if error.line_number > len(lines):
                return False

            line = lines[error.line_number - 1]

            # Find index access pattern
            for pattern, suggested_type in self.index_patterns.items():
                if re.search(pattern, line):
                    # Find the variable being indexed
                    var_match = re.search(r"(\w+)" + pattern, line)
                    if var_match:
                        var_name = var_match.group(1)

                        # Look for variable assignment to add type annotation
                        if self._add_type_annotation_to_var(
                            file_path, var_name, suggested_type
                        ):
                            return True

            return False

        except Exception as e:
            logger.warning(
                f"Failed to fix index error in {error.file_path}:{error.line_number}: {e}"
            )
            return False

    def fix_assignment_errors(self, errors: list[MypyError]) -> FixResult:
        """Fix assignment type mismatch errors."""
        logger.info("🔧 Fixing assignment errors")

        fixes_applied = 0
        files_processed = set()

        try:
            for error in errors:
                if error.rule_code == "assignment":
                    if self._fix_assignment_error(error):
                        fixes_applied += 1
                        files_processed.add(error.file_path)

            return FixResult(
                success=True,
                fixes_applied=fixes_applied,
                errors_remaining=0,
                message=f"Fixed {fixes_applied} assignment issues in {len(files_processed)} files",
            )

        except Exception as e:
            logger.error(f"Error fixing assignment errors: {e}")
            return FixResult(
                success=False,
                fixes_applied=fixes_applied,
                errors_remaining=0,
                message=f"Failed after {fixes_applied} fixes: {e}",
            )

    def _fix_assignment_error(self, error: MypyError) -> bool:
        """Fix a single assignment error."""
        try:
            file_path = Path(error.file_path)
            if not file_path.exists():
                return False

            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if error.line_number > len(lines):
                return False

            line = lines[error.line_number - 1]

            # Parse assignment mismatch message
            # Example: Incompatible types in assignment (expression has type "None", variable has type "dict[str, Any]")
            mismatch_pattern = (
                r'expression has type "([^"]+)", variable has type "([^"]+)"'
            )
            match = re.search(mismatch_pattern, error.message)

            if match:
                expr_type = match.group(1)
                var_type = match.group(2)

                # If assigning None to a typed variable, make it Optional
                if expr_type == "None" and var_type != "None":
                    # Find variable and make it Optional
                    if "=" in line:
                        var_name = line.split("=")[0].strip()
                        if ":" in var_name:
                            # Already has type annotation, make it Optional
                            type_part = var_name.split(":")[1].strip()
                            if (
                                not type_part.startswith("Optional")
                                and "|" not in type_part
                            ):
                                new_type = f"Optional[{type_part}]"
                                new_line = line.replace(
                                    f": {type_part}", f": {new_type}"
                                )
                                lines[error.line_number - 1] = new_line

                                # Add Optional import if needed
                                self._ensure_optional_import(file_path, lines)

                                # Write back to file
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.writelines(lines)
                                return True

            return False

        except Exception as e:
            logger.warning(
                f"Failed to fix assignment error in {error.file_path}:{error.line_number}: {e}"
            )
            return False

    def _add_type_annotation_to_var(
        self, file_path: Path, var_name: str, suggested_type: str
    ) -> bool:
        """Add type annotation to a variable."""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Find variable assignment
            for i, line in enumerate(lines):
                if f"{var_name} =" in line and ":" not in line.split("=")[0]:
                    assignment_pos = line.find("=")
                    var_part = line[:assignment_pos].strip()
                    value_part = line[assignment_pos:]

                    new_line = f"{var_part}: {suggested_type}{value_part}"
                    lines[i] = new_line

                    # Write back to file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)
                    return True

            return False

        except Exception as e:
            logger.warning(f"Failed to add type annotation for {var_name}: {e}")
            return False

    def _ensure_optional_import(self, file_path: Path, lines: list[str]) -> bool:
        """Ensure Optional is imported from typing."""
        try:
            # Check if Optional is already imported
            has_optional = False
            typing_import_line = -1

            for i, line in enumerate(lines):
                if "from typing import" in line and "Optional" in line:
                    has_optional = True
                    break
                elif "from typing import" in line:
                    typing_import_line = i

            if not has_optional:
                if typing_import_line >= 0:
                    # Add Optional to existing typing import
                    line = lines[typing_import_line]
                    if line.strip().endswith(")"):
                        # Multi-line import
                        lines[typing_import_line] = line.replace(")", ", Optional)")
                    else:
                        # Single line import
                        lines[typing_import_line] = line.rstrip() + ", Optional\n"
                else:
                    # Add new typing import
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.startswith("import ") or line.startswith("from "):
                            insert_pos = i + 1
                        else:
                            break

                    lines.insert(insert_pos, "from typing import Optional\n")

                return True

            return False

        except Exception as e:
            logger.warning(f"Failed to ensure Optional import: {e}")
            return False

    def fix_all_advanced_errors(
        self, error_types: list[str] | None = None
    ) -> dict[str, FixResult]:
        """Fix all advanced mypy errors systematically."""
        logger.info("🚀 Starting advanced mypy error fixing")

        if error_types is None:
            error_types = ["attr-defined", "index", "assignment", "return-value"]

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

                    if error_type == "attr-defined":
                        result = self.fix_attr_defined_errors(
                            errors_by_type[error_type]
                        )
                    elif error_type == "index":
                        result = self.fix_index_errors(errors_by_type[error_type])
                    elif error_type == "assignment":
                        result = self.fix_assignment_errors(errors_by_type[error_type])
                    else:
                        result = FixResult(
                            success=False,
                            fixes_applied=0,
                            errors_remaining=len(errors_by_type[error_type]),
                            message=f"Handler for {error_type} not implemented yet",
                        )

                    results[error_type] = result
                    logger.info(f"✅ {error_type}: {result.message}")

            return results

        except Exception as e:
            logger.error(f"❌ Critical error in fix_all_advanced_errors: {e}")
            raise


def main() -> None:
    """Main entry point for advanced type fixing."""
    logger.info("🚀 Advanced Type Fixer - Following crawl_mcp.py methodology")

    try:
        fixer = AdvancedTypeFixer()

        with fixer.error_handling_context("Advanced Type Fixing"):
            results = fixer.fix_all_advanced_errors()

            # Generate and save report
            report = fixer.generate_report(results)

            report_path = Path("advanced_type_fix_report.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)

            logger.info(f"📋 Report saved to {report_path}")
            print(report)

    except Exception as e:
        logger.error(f"❌ Critical failure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
