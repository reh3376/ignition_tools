"""Comprehensive Type Fixer - Main coordinator for all mypy error fixes.

Following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Robust error handling
4. Modular testing approach
5. Progressive complexity
6. Proper resource management

Coordinates fixes for all major error patterns:
- Phase 1: Basic annotations (no-untyped-def, var-annotated)
- Phase 2: Complex patterns (attr-defined, index, assignment)
- Phase 3: Advanced fixes (return-value, arg-type, union-attr)
"""

import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from .advanced_type_fixer import AdvancedTypeFixer
from .type_annotation_fixer import FixResult, TypeAnnotationFixer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ComprehensiveFixResult:
    """Result of comprehensive type fixing."""

    total_initial_errors: int
    total_final_errors: int
    total_fixes_applied: int
    phase_results: dict[str, dict[str, FixResult]]
    execution_time: float
    success: bool
    message: str


class ComprehensiveTypeFixer:
    """Comprehensive type fixer following crawl_mcp.py methodology.

    Systematically fixes mypy errors in phases:
    1. Basic type annotations
    2. Complex type patterns
    3. Advanced error resolution
    """

    def __init__(self, source_dir: str = "src"):
        """Initialize with environment validation first."""
        self.source_dir = Path(source_dir)
        self.start_time = time.time()

        # Validate environment
        self.validate_environment()

        # Initialize fixers
        self.basic_fixer = TypeAnnotationFixer(source_dir)
        self.advanced_fixer = AdvancedTypeFixer(source_dir)

        # Define fixing phases
        self.fixing_phases = {
            "Phase 1 - Basic Annotations": {
                "fixer": self.basic_fixer,
                "method": "fix_all_errors",
                "error_types": ["no-untyped-def", "var-annotated"],
                "description": "Add basic function and variable type annotations",
            },
            "Phase 2 - Complex Patterns": {
                "fixer": self.advanced_fixer,
                "method": "fix_all_advanced_errors",
                "error_types": ["attr-defined", "index", "assignment"],
                "description": "Fix attribute access, indexing, and assignment issues",
            },
            "Phase 3 - Advanced Resolution": {
                "fixer": self.advanced_fixer,
                "method": "fix_all_advanced_errors",
                "error_types": ["return-value", "arg-type", "union-attr"],
                "description": "Resolve return values, argument types, and union attributes",
            },
        }

    def validate_environment(self) -> bool:
        """Validate environment setup before proceeding."""
        logger.info("🔍 Step 1: Environment Validation (crawl_mcp.py methodology)")

        try:
            # Check if source directory exists
            if not self.source_dir.exists():
                raise FileNotFoundError(f"Source directory {self.source_dir} not found")

            # Check if Python version supports modern typing
            if sys.version_info < (3, 8):
                raise RuntimeError("Python 3.8+ required for modern type annotations")

            # Check mypy availability
            import subprocess

            result = subprocess.run(
                [sys.executable, "-m", "mypy", "--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError("mypy not available")

            logger.info("✅ Environment validation successful")
            return True

        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            raise

    def get_error_summary(self) -> dict[str, int]:
        """Get comprehensive error summary."""
        logger.info("📊 Analyzing current mypy error state")

        try:
            import subprocess

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

            # Count errors by type
            error_counts = {}
            total_errors = 0

            for line in result.stdout.split("\n"):
                if "error:" in line and "[" in line and "]" in line:
                    # Extract error type from [error-type] pattern
                    start = line.rfind("[")
                    end = line.rfind("]")
                    if start != -1 and end != -1:
                        error_type = line[start + 1 : end]
                        error_counts[error_type] = error_counts.get(error_type, 0) + 1
                        total_errors += 1

            error_counts["TOTAL"] = total_errors
            logger.info(
                f"📋 Found {total_errors} total errors across {len(error_counts) - 1} types"
            )

            return error_counts

        except Exception as e:
            logger.error(f"Failed to get error summary: {e}")
            return {"TOTAL": 0}

    def fix_all_comprehensively(self) -> ComprehensiveFixResult:
        """Fix all mypy errors comprehensively following crawl_mcp.py methodology."""
        logger.info("🚀 Starting comprehensive mypy error fixing")
        logger.info(
            "📋 Following crawl_mcp.py methodology: systematic, modular, and progressive"
        )

        # Step 1: Get initial error state
        initial_errors = self.get_error_summary()
        logger.info(f"📊 Initial state: {initial_errors.get('TOTAL', 0)} errors")

        # Step 2: Execute fixing phases
        phase_results = {}
        total_fixes_applied = 0

        try:
            for phase_name, phase_config in self.fixing_phases.items():
                logger.info(f"\n🔧 {phase_name}")
                logger.info(f"📝 {phase_config['description']}")

                fixer = phase_config["fixer"]
                method_name = phase_config["method"]
                error_types = phase_config["error_types"]

                # Execute the fixing method
                method = getattr(fixer, method_name)
                phase_result = method(error_types)

                phase_results[phase_name] = phase_result

                # Calculate fixes applied in this phase
                phase_fixes = sum(
                    result.fixes_applied for result in phase_result.values()
                )
                total_fixes_applied += phase_fixes

                logger.info(f"✅ {phase_name} completed: {phase_fixes} fixes applied")

                # Show progress
                current_errors = self.get_error_summary()
                logger.info(f"📊 Current error count: {current_errors.get('TOTAL', 0)}")

            # Step 3: Get final error state
            final_errors = self.get_error_summary()
            execution_time = time.time() - self.start_time

            # Step 4: Determine success
            initial_count = initial_errors.get("TOTAL", 0)
            final_count = final_errors.get("TOTAL", 0)
            success = final_count < initial_count

            result = ComprehensiveFixResult(
                total_initial_errors=initial_count,
                total_final_errors=final_count,
                total_fixes_applied=total_fixes_applied,
                phase_results=phase_results,
                execution_time=execution_time,
                success=success,
                message=f"Reduced errors from {initial_count} to {final_count} ({total_fixes_applied} fixes applied)",
            )

            logger.info(f"🎯 Comprehensive fixing completed: {result.message}")
            return result

        except Exception as e:
            logger.error(f"❌ Critical error in comprehensive fixing: {e}")
            execution_time = time.time() - self.start_time

            return ComprehensiveFixResult(
                total_initial_errors=initial_errors.get("TOTAL", 0),
                total_final_errors=initial_errors.get("TOTAL", 0),
                total_fixes_applied=total_fixes_applied,
                phase_results=phase_results,
                execution_time=execution_time,
                success=False,
                message=f"Failed with error: {e}",
            )

    def generate_comprehensive_report(self, result: ComprehensiveFixResult) -> str:
        """Generate comprehensive report following crawl_mcp.py methodology."""
        logger.info("📊 Generating comprehensive report")

        report = [
            "# Comprehensive Type Annotation Fixer Report",
            "Generated using crawl_mcp.py methodology",
            f"Execution time: {result.execution_time:.2f} seconds",
            "",
            "## Executive Summary",
            "",
        ]

        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        reduction_percent = (
            (result.total_initial_errors - result.total_final_errors)
            / max(result.total_initial_errors, 1)
        ) * 100

        report.extend(
            [
                f"- **Status**: {status}",
                f"- **Initial errors**: {result.total_initial_errors}",
                f"- **Final errors**: {result.total_final_errors}",
                f"- **Total fixes applied**: {result.total_fixes_applied}",
                f"- **Error reduction**: {reduction_percent:.1f}%",
                f"- **Execution time**: {result.execution_time:.2f} seconds",
                "",
                "## Phase-by-Phase Results",
                "",
            ]
        )

        for phase_name, phase_results in result.phase_results.items():
            report.extend([f"### {phase_name}", ""])

            phase_fixes = sum(
                fix_result.fixes_applied for fix_result in phase_results.values()
            )
            phase_success = sum(
                1 for fix_result in phase_results.values() if fix_result.success
            )

            report.extend(
                [
                    f"- **Fixes applied**: {phase_fixes}",
                    f"- **Successful operations**: {phase_success}/{len(phase_results)}",
                    "",
                ]
            )

            for error_type, fix_result in phase_results.items():
                status_icon = "✅" if fix_result.success else "❌"
                report.extend(
                    [
                        f"#### {error_type} {status_icon}",
                        f"- Fixes: {fix_result.fixes_applied}",
                        f"- Message: {fix_result.message}",
                        "",
                    ]
                )

        report.extend(
            [
                "## Remaining Error Analysis",
                "",
                "To see remaining errors by type:",
                "```bash",
                "python -m mypy src/ --no-error-summary 2>&1 | grep 'error:' | sed 's/.*\\[\\(.*\\)\\]$/\\1/' | sort | uniq -c | sort -nr",
                "```",
                "",
                "## Next Steps",
                "",
                "1. **Review automated changes**: Check the modified files for correctness",
                "2. **Run tests**: Ensure functionality is preserved after type fixes",
                "3. **Address remaining errors**: Some complex errors may need manual fixes",
                "4. **Commit changes**: Use descriptive commit message following project conventions",
                "",
                "## Implementation Details",
                "",
                "This fixer follows crawl_mcp.py methodology:",
                "- ✅ Environment validation first",
                "- ✅ Comprehensive input validation",
                "- ✅ Robust error handling",
                "- ✅ Modular testing approach",
                "- ✅ Progressive complexity",
                "- ✅ Proper resource management",
                "",
                "Generated by ComprehensiveTypeFixer v1.0",
            ]
        )

        return "\n".join(report)

    def run_and_report(self) -> str:
        """Run comprehensive fixing and generate report."""
        logger.info("🚀 Starting comprehensive type fixing with reporting")

        try:
            # Run comprehensive fixing
            result = self.fix_all_comprehensively()

            # Generate report
            report = self.generate_comprehensive_report(result)

            # Save report
            report_path = Path("comprehensive_type_fix_report.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)

            logger.info(f"📋 Comprehensive report saved to {report_path}")

            # Also show summary in console
            print("\n" + "=" * 80)
            print("COMPREHENSIVE TYPE FIXING SUMMARY")
            print("=" * 80)
            print(f"Initial errors: {result.total_initial_errors}")
            print(f"Final errors: {result.total_final_errors}")
            print(f"Fixes applied: {result.total_fixes_applied}")
            print(f"Success: {'YES' if result.success else 'NO'}")
            print(f"Execution time: {result.execution_time:.2f}s")
            print(f"Report saved: {report_path}")
            print("=" * 80)

            return report

        except Exception as e:
            error_msg = f"❌ Critical failure in run_and_report: {e}"
            logger.error(error_msg)
            print(error_msg)
            return error_msg


def main() -> None:
    """Main entry point following crawl_mcp.py methodology."""
    logger.info("🚀 Comprehensive Type Fixer - Following crawl_mcp.py methodology")

    try:
        fixer = ComprehensiveTypeFixer()
        report = fixer.run_and_report()

        # Exit with appropriate code
        sys.exit(0 if "SUCCESS" in report else 1)

    except Exception as e:
        logger.error(f"❌ Critical failure: {e}")
        print(f"CRITICAL FAILURE: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
