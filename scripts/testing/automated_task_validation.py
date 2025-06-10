#!/usr/bin/env python3
"""
Automated Task Validation Script

Runs specific validation tests after each task completion to ensure
quality gates are met and no regressions are introduced.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from ignition.graph.client import IgnitionGraphClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TaskValidator:
    """Automated validation for task completion."""

    def __init__(self):
        self.client = IgnitionGraphClient()

    def validate_task_completion(self, task_id: int) -> dict[str, Any]:
        """Validate specific task completion based on task ID."""
        print(f"🔍 **TASK {task_id} VALIDATION**")
        print(f"📅 **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        if not self.client.connect():
            return {"success": False, "error": "Database connection failed"}

        # Task-specific validation
        if task_id == 1:
            return self._validate_task_1()
        elif task_id == 2:
            return self._validate_task_2()
        else:
            return {
                "success": False,
                "error": f"No validation defined for Task {task_id}",
            }

    def _validate_task_1(self) -> dict[str, Any]:
        """Validate Task 1: Tag System Expansion completion."""
        validation_results = []

        # Test 1: Minimum function count
        result = self.client.execute_query(
            """
        MATCH (f:Function)-[:BELONGS_TO]->(c:Category {name: "tag"})
        RETURN count(f) as tag_count
        """
        )
        tag_count = result[0]["tag_count"]

        if tag_count >= 25:
            validation_results.append(
                {
                    "test": "Tag Function Count",
                    "passed": True,
                    "message": f"{tag_count} functions (target: 25+)",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Tag Function Count",
                    "passed": False,
                    "message": f"Only {tag_count} functions (target: 25+)",
                }
            )

        # Test 2: Required functions exist
        required_functions = [
            "system.tag.configure",
            "system.tag.deleteConfiguration",
            "system.tag.queryTagHistory",
            "system.tag.subscribe",
            "system.tag.exportTags",
            "system.tag.browseTags",
            "system.tag.readAll",
            "system.tag.writeAll",
        ]

        missing_functions = []
        for func_name in required_functions:
            result = self.client.execute_query(
                f"""
            MATCH (f:Function {{name: "{func_name}"}})
            RETURN count(f) as exists
            """
            )

            if result[0]["exists"] == 0:
                missing_functions.append(func_name)

        if len(missing_functions) == 0:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": True,
                    "message": "All key functions present",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Required Functions",
                    "passed": False,
                    "message": f"Missing: {missing_functions}",
                }
            )

        # Test 3: Context mappings validation
        result = self.client.execute_query(
            """
        MATCH (f:Function)-[:BELONGS_TO]->(c:Category {name: "tag"})
        WHERE NOT EXISTS((f)-[:AVAILABLE_IN]->(:Context))
        RETURN count(f) as orphaned
        """
        )
        orphaned = result[0]["orphaned"]

        if orphaned == 0:
            validation_results.append(
                {
                    "test": "Context Mappings",
                    "passed": True,
                    "message": "All tag functions have context mappings",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Context Mappings",
                    "passed": False,
                    "message": f"{orphaned} functions without context",
                }
            )

        # Test 4: Gateway scope validation for configuration functions
        config_functions = [
            "system.tag.configure",
            "system.tag.deleteConfiguration",
            "system.tag.editTags",
        ]
        gateway_issues = 0

        for func_name in config_functions:
            # Check if function exists first
            exists_result = self.client.execute_query(
                f"""
            MATCH (f:Function {{name: "{func_name}"}})
            RETURN count(f) as exists
            """
            )

            if exists_result[0]["exists"] > 0:
                # If it's a gateway-only function, it should not have non-gateway contexts
                result = self.client.execute_query(
                    f"""
                MATCH (f:Function {{name: "{func_name}"}})
                WHERE f.scope = "gateway"
                WITH f
                MATCH (f)-[:AVAILABLE_IN]->(c:Context)
                WHERE c.name <> "Gateway"
                RETURN count(c) as invalid_contexts
                """
                )

                if result[0]["invalid_contexts"] > 0:
                    gateway_issues += 1

        if gateway_issues == 0:
            validation_results.append(
                {
                    "test": "Gateway Scope Validation",
                    "passed": True,
                    "message": "Configuration functions properly scoped",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Gateway Scope Validation",
                    "passed": False,
                    "message": f"{gateway_issues} scope violations",
                }
            )

        # Test 5: Performance validation
        import time

        start_time = time.time()
        self.client.execute_query(
            """
        MATCH (f:Function)-[:BELONGS_TO]->(c:Category {name: "tag"})
        RETURN f.name, f.description
        ORDER BY f.name
        """
        )
        query_time = time.time() - start_time

        if query_time < 0.5:
            validation_results.append(
                {
                    "test": "Query Performance",
                    "passed": True,
                    "message": f"Tag query: {query_time:.3f}s",
                }
            )
        else:
            validation_results.append(
                {
                    "test": "Query Performance",
                    "passed": False,
                    "message": f"Slow query: {query_time:.3f}s",
                }
            )

        # Generate summary
        passed_tests = sum(1 for r in validation_results if r["passed"])
        total_tests = len(validation_results)
        success = passed_tests == total_tests

        print("\n📋 **Task 1 Validation Results**:")
        for result in validation_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")

        if success:
            print(f"\n🎉 **Task 1 VALIDATION PASSED** ({passed_tests}/{total_tests})")
        else:
            print(
                f"\n❌ **Task 1 VALIDATION FAILED** ({passed_tests}/{total_tests} passed)"
            )

        return {
            "success": success,
            "task_id": 1,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": validation_results,
            "tag_function_count": tag_count,
        }

    def _validate_task_2(self) -> dict[str, Any]:
        """Validate Task 2: Database System Expansion completion (template for future use)."""
        # This will be implemented when Task 2 is completed
        return {
            "success": False,
            "task_id": 2,
            "error": "Task 2 validation not yet implemented - complete Task 2 first",
        }

    def generate_validation_report(self, task_id: int, results: dict[str, Any]) -> str:
        """Generate a detailed validation report."""
        report_data = {
            "validation_timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "results": results,
            "system_info": {
                "total_functions": self._get_total_function_count(),
                "completion_percentage": self._get_completion_percentage(),
            },
        }

        # Save report
        report_file = f"task_{task_id}_validation_report.json"
        report_path = Path("reports") / report_file
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        return str(report_path)

    def _get_total_function_count(self) -> int:
        """Get total function count."""
        result = self.client.execute_query(
            "MATCH (f:Function) RETURN count(f) as total"
        )
        return result[0]["total"]

    def _get_completion_percentage(self) -> float:
        """Get completion percentage."""
        total = self._get_total_function_count()
        return (total / 400) * 100


def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("Usage: python automated_task_validation.py <task_id>")
        print("Example: python automated_task_validation.py 1")
        sys.exit(1)

    try:
        task_id = int(sys.argv[1])
    except ValueError:
        print("Error: Task ID must be a number")
        sys.exit(1)

    validator = TaskValidator()
    results = validator.validate_task_completion(task_id)

    if results.get("success", False):
        print(f"\n✅ Task {task_id} validation completed successfully!")

        # Generate detailed report
        report_path = validator.generate_validation_report(task_id, results)
        print(f"📄 **Detailed Report**: {report_path}")

        return True
    else:
        print(f"\n❌ Task {task_id} validation failed!")
        if "error" in results:
            print(f"Error: {results['error']}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
