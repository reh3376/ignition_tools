#!/usr/bin/env python3
"""
Enhanced Graph Database Testing Suite

Comprehensive testing framework for validating the Ignition graph database
functions, relationships, and performance. Run after each task completion
to ensure system integrity.
"""

import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from ignition.graph.client import IgnitionGraphClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result container."""

    test_name: str
    passed: bool
    message: str
    execution_time: float
    details: dict[str, Any] = None


class GraphDatabaseTester:
    """Comprehensive testing framework for the graph database."""

    def __init__(self):
        self.client = IgnitionGraphClient()
        self.test_results: list[TestResult] = []

    def connect(self) -> bool:
        """Connect to the database."""
        return self.client.connect()

    def run_all_tests(self) -> dict[str, Any]:
        """Run all test suites and return comprehensive results."""
        logger.info("🧪 Starting Enhanced Graph Database Test Suite")
        logger.info("=" * 60)

        if not self.connect():
            logger.error("❌ Failed to connect to Neo4j database")
            return {"success": False, "error": "Database connection failed"}

        # Run test suites
        test_suites = [
            ("Database Integrity", self._test_database_integrity),
            ("Function Validation", self._test_function_validation),
            ("Context Relationships", self._test_context_relationships),
            ("Category Organization", self._test_category_organization),
            ("Performance Benchmarks", self._test_performance_benchmarks),
            ("Data Consistency", self._test_data_consistency),
            ("Task Completion Validation", self._test_task_completion),
            ("Security & Permissions", self._test_security_validation),
        ]

        for suite_name, test_function in test_suites:
            logger.info(f"\n🔍 Running {suite_name} Tests...")
            suite_results = test_function()
            self.test_results.extend(suite_results)

        # Generate summary
        return self._generate_test_summary()

    def _run_test(self, test_name: str, test_function) -> TestResult:
        """Run a single test and measure execution time."""
        start_time = time.time()
        try:
            result = test_function()
            execution_time = time.time() - start_time

            if isinstance(result, tuple):
                passed, message, details = result
            else:
                passed, message, details = result, "Test completed", {}

            return TestResult(test_name, passed, message, execution_time, details)
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(test_name, False, f"Test failed: {e!s}", execution_time)

    def _test_database_integrity(self) -> list[TestResult]:
        """Test basic database integrity and structure."""
        tests = []

        # Test 1: Database connectivity
        def test_connectivity():
            stats = self.client.get_database_stats()
            return (
                stats["is_connected"],
                f"Database connected: {stats['total_nodes']} nodes, {stats['total_relationships']} relationships",
            )

        tests.append(self._run_test("Database Connectivity", test_connectivity))

        # Test 2: Core node types exist
        def test_core_nodes():
            result = self.client.execute_query(
                """
            MATCH (n)
            RETURN labels(n)[0] as nodeType, count(n) as count
            ORDER BY nodeType
            """
            )

            node_types = {r["nodeType"]: r["count"] for r in result}
            required_types = [
                "Function",
                "Context",
                "Category",
                "ScriptType",
                "Parameter",
                "Template",
            ]
            missing = [t for t in required_types if t not in node_types]

            return (
                len(missing) == 0,
                f"Node types: {node_types}, Missing: {missing}",
                {"node_types": node_types},
            )

        tests.append(self._run_test("Core Node Types", test_core_nodes))

        # Test 3: Relationship integrity
        def test_relationships():
            result = self.client.execute_query(
                """
            MATCH ()-[r]->()
            RETURN type(r) as relType, count(r) as count
            ORDER BY count DESC
            """
            )

            rel_types = {r["relType"]: r["count"] for r in result}
            required_rels = ["BELONGS_TO", "AVAILABLE_IN", "PROVIDES"]
            missing = [r for r in required_rels if r not in rel_types]

            return (
                len(missing) == 0,
                f"Relationships: {rel_types}, Missing: {missing}",
                {"relationships": rel_types},
            )

        tests.append(self._run_test("Relationship Integrity", test_relationships))

        return tests

    def _test_function_validation(self) -> list[TestResult]:
        """Test function-specific validation."""
        tests = []

        # Test 1: Function count validation
        def test_function_count():
            result = self.client.execute_query(
                "MATCH (f:Function) RETURN count(f) as total"
            )
            total = result[0]["total"]
            expected_min = 60  # We should have at least 60 functions after Task 1

            return (
                total >= expected_min,
                f"Function count: {total} (expected >= {expected_min})",
                {"total_functions": total},
            )

        tests.append(self._run_test("Function Count", test_function_count))

        # Test 2: Tag functions validation (Task 1)
        def test_tag_functions():
            result = self.client.execute_query(
                """
            MATCH (f:Function)-[:BELONGS_TO]->(c:Category {name: "tag"})
            RETURN count(f) as tag_count
            """
            )
            tag_count = result[0]["tag_count"]
            expected_min = 25  # Task 1 should have added 25+ tag functions

            return (
                tag_count >= expected_min,
                f"Tag functions: {tag_count} (expected >= {expected_min})",
                {"tag_functions": tag_count},
            )

        tests.append(self._run_test("Tag Functions (Task 1)", test_tag_functions))

        # Test 3: Function properties validation
        def test_function_properties():
            result = self.client.execute_query(
                """
            MATCH (f:Function)
            WHERE f.name IS NULL OR f.description IS NULL OR f.category IS NULL
            RETURN count(f) as invalid_count
            """
            )
            invalid_count = result[0]["invalid_count"]

            return (
                invalid_count == 0,
                f"Invalid functions: {invalid_count} (should be 0)",
                {"invalid_functions": invalid_count},
            )

        tests.append(self._run_test("Function Properties", test_function_properties))

        # Test 4: Function naming convention
        def test_function_naming():
            result = self.client.execute_query(
                """
            MATCH (f:Function)
            WHERE NOT f.name STARTS WITH "system."
            RETURN count(f) as invalid_naming
            """
            )
            invalid_naming = result[0]["invalid_naming"]

            return (
                invalid_naming == 0,
                f"Invalid function names: {invalid_naming}",
                {"invalid_naming": invalid_naming},
            )

        tests.append(self._run_test("Function Naming Convention", test_function_naming))

        return tests

    def _test_context_relationships(self) -> list[TestResult]:
        """Test context-function relationships."""
        tests = []

        # Test 1: All functions have context relationships
        def test_context_coverage():
            result = self.client.execute_query(
                """
            MATCH (f:Function)
            WHERE NOT EXISTS((f)-[:AVAILABLE_IN]->(:Context))
            RETURN count(f) as orphaned_functions
            """
            )
            orphaned = result[0]["orphaned_functions"]

            return (
                orphaned == 0,
                f"Functions without context: {orphaned}",
                {"orphaned_functions": orphaned},
            )

        tests.append(self._run_test("Context Coverage", test_context_coverage))

        # Test 2: Context distribution validation
        def test_context_distribution():
            result = self.client.execute_query(
                """
            MATCH (f:Function)-[:AVAILABLE_IN]->(c:Context)
            RETURN c.name as context, count(f) as function_count
            ORDER BY function_count DESC
            """
            )

            distribution = {r["context"]: r["function_count"] for r in result}
            expected_contexts = ["Gateway", "Vision", "Perspective"]
            missing_contexts = [c for c in expected_contexts if c not in distribution]

            return (
                len(missing_contexts) == 0,
                f"Context distribution: {distribution}",
                {"distribution": distribution},
            )

        tests.append(self._run_test("Context Distribution", test_context_distribution))

        # Test 3: Gateway-only functions validation
        def test_gateway_only_functions():
            result = self.client.execute_query(
                """
            MATCH (f:Function)
            WHERE f.scope = "gateway"
            WITH f
            MATCH (f)-[:AVAILABLE_IN]->(c:Context)
            WHERE c.name <> "Gateway"
            RETURN count(f) as invalid_gateway
            """
            )
            invalid = result[0]["invalid_gateway"]

            return (
                invalid == 0,
                f"Invalid gateway-only mappings: {invalid}",
                {"invalid_gateway_mappings": invalid},
            )

        tests.append(
            self._run_test("Gateway-Only Functions", test_gateway_only_functions)
        )

        return tests

    def _test_category_organization(self) -> list[TestResult]:
        """Test category organization and relationships."""
        tests = []

        # Test 1: All functions have categories
        def test_category_coverage():
            result = self.client.execute_query(
                """
            MATCH (f:Function)
            WHERE NOT EXISTS((f)-[:BELONGS_TO]->(:Category))
            RETURN count(f) as uncategorized
            """
            )
            uncategorized = result[0]["uncategorized"]

            return (
                uncategorized == 0,
                f"Uncategorized functions: {uncategorized}",
                {"uncategorized": uncategorized},
            )

        tests.append(self._run_test("Category Coverage", test_category_coverage))

        # Test 2: Category distribution
        def test_category_distribution():
            result = self.client.execute_query(
                """
            MATCH (f:Function)-[:BELONGS_TO]->(c:Category)
            RETURN c.name as category, count(f) as count
            ORDER BY count DESC
            """
            )

            distribution = {r["category"]: r["count"] for r in result}
            # After Task 1, 'tag' should be the largest category
            largest_category = (
                max(distribution, key=distribution.get) if distribution else None
            )

            return (
                largest_category == "tag",
                f"Category distribution: {distribution}, Largest: {largest_category}",
                {"distribution": distribution},
            )

        tests.append(
            self._run_test("Category Distribution", test_category_distribution)
        )

        return tests

    def _test_performance_benchmarks(self) -> list[TestResult]:
        """Test system performance benchmarks."""
        tests = []

        # Test 1: Function query performance
        def test_function_query_performance():
            start_time = time.time()
            self.client.execute_query(
                """
            MATCH (f:Function)-[:BELONGS_TO]->(c:Category)
            RETURN c.name, count(f)
            ORDER BY count(f) DESC
            """
            )
            query_time = time.time() - start_time

            return (
                query_time < 1.0,
                f"Function query time: {query_time:.3f}s (target: <1.0s)",
                {"query_time": query_time},
            )

        tests.append(
            self._run_test(
                "Function Query Performance", test_function_query_performance
            )
        )

        # Test 2: Context relationship performance
        def test_context_query_performance():
            start_time = time.time()
            self.client.execute_query(
                """
            MATCH (f:Function)-[:AVAILABLE_IN]->(c:Context)
            WHERE c.name = "Gateway"
            RETURN count(f) as gateway_functions
            """
            )
            query_time = time.time() - start_time

            return (
                query_time < 0.5,
                f"Context query time: {query_time:.3f}s (target: <0.5s)",
                {"query_time": query_time},
            )

        tests.append(
            self._run_test("Context Query Performance", test_context_query_performance)
        )

        # Test 3: Complex relationship traversal
        def test_complex_traversal_performance():
            start_time = time.time()
            self.client.execute_query(
                """
            MATCH (s:ScriptType)-[:COMPATIBLE_WITH]->(c:Context)<-[:AVAILABLE_IN]-(f:Function)-[:BELONGS_TO]->(cat:Category)
            WHERE s.name = "Timer"
            RETURN cat.name, count(f) as function_count
            ORDER BY function_count DESC
            """
            )
            query_time = time.time() - start_time

            return (
                query_time < 2.0,
                f"Complex traversal time: {query_time:.3f}s (target: <2.0s)",
                {"query_time": query_time},
            )

        tests.append(
            self._run_test(
                "Complex Traversal Performance", test_complex_traversal_performance
            )
        )

        return tests

    def _test_data_consistency(self) -> list[TestResult]:
        """Test data consistency and integrity."""
        tests = []

        # Test 1: Scope consistency
        def test_scope_consistency():
            result = self.client.execute_query(
                """
            MATCH (f:Function)
            WHERE f.scope NOT IN ["gateway", "client", "session", "all"]
            RETURN count(f) as invalid_scope
            """
            )
            invalid = result[0]["invalid_scope"]

            return (
                invalid == 0,
                f"Functions with invalid scope: {invalid}",
                {"invalid_scope": invalid},
            )

        tests.append(self._run_test("Scope Consistency", test_scope_consistency))

        # Test 2: Category-function consistency
        def test_category_function_consistency():
            result = self.client.execute_query(
                """
            MATCH (f:Function)-[:BELONGS_TO]->(c:Category)
            WHERE f.category <> c.name
            RETURN count(f) as inconsistent
            """
            )
            inconsistent = result[0]["inconsistent"]

            return (
                inconsistent == 0,
                f"Category-function inconsistencies: {inconsistent}",
                {"inconsistent": inconsistent},
            )

        tests.append(
            self._run_test(
                "Category-Function Consistency", test_category_function_consistency
            )
        )

        return tests

    def _test_task_completion(self) -> list[TestResult]:
        """Test task completion validation."""
        tests = []

        # Test 1: Task 1 completion validation
        def test_task_1_completion():
            # Check if we have the expected Task 1 functions
            expected_functions = [
                "system.tag.configure",
                "system.tag.deleteConfiguration",
                "system.tag.queryTagHistory",
                "system.tag.subscribe",
                "system.tag.exportTags",
            ]

            missing = []
            for func_name in expected_functions:
                result = self.client.execute_query(
                    """
                MATCH (f:Function {name: $name})
                RETURN count(f) as exists
                """,
                    name=func_name,
                )

                if result[0]["exists"] == 0:
                    missing.append(func_name)

            return (
                len(missing) == 0,
                f"Task 1 validation - Missing functions: {missing}",
                {"missing_functions": missing},
            )

        tests.append(self._run_test("Task 1 Completion", test_task_1_completion))

        return tests

    def _test_security_validation(self) -> list[TestResult]:
        """Test security and access validation."""
        tests = []

        # Test 1: Function security properties
        def test_function_security():
            result = self.client.execute_query(
                """
            MATCH (f:Function)
            WHERE f.name CONTAINS "security" OR f.name CONTAINS "permission"
            RETURN count(f) as security_functions
            """
            )
            security_count = result[0]["security_functions"]

            return (
                security_count > 0,
                f"Security functions found: {security_count}",
                {"security_functions": security_count},
            )

        tests.append(self._run_test("Security Functions", test_function_security))

        return tests

    def _generate_test_summary(self) -> dict[str, Any]:
        """Generate comprehensive test summary."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t.passed)
        failed_tests = total_tests - passed_tests

        total_time = sum(t.execution_time for t in self.test_results)

        summary = {
            "success": failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "total_execution_time": total_time,
            "test_results": self.test_results,
        }

        # Print summary
        print("\n" + "=" * 60)
        print("🧪 **TEST SUITE SUMMARY**")
        print("=" * 60)

        if summary["success"]:
            print(f"✅ **ALL TESTS PASSED** ({passed_tests}/{total_tests})")
        else:
            print(
                f"❌ **{failed_tests} TESTS FAILED** ({passed_tests}/{total_tests} passed)"
            )

        print(f"📊 **Pass Rate**: {summary['pass_rate']:.1f}%")
        print(f"⏱️ **Total Time**: {total_time:.2f}s")

        print("\n📋 **Test Results**:")
        for result in self.test_results:
            status = "✅" if result.passed else "❌"
            print(
                f"{status} {result.test_name}: {result.message} ({result.execution_time:.3f}s)"
            )

        if failed_tests > 0:
            print("\n⚠️ **Failed Tests Details**:")
            for result in self.test_results:
                if not result.passed:
                    print(f"   ❌ {result.test_name}: {result.message}")

        return summary


def main():
    """Main testing function."""
    logger.info("🚀 Starting Enhanced Graph Database Testing")

    tester = GraphDatabaseTester()
    results = tester.run_all_tests()

    if results["success"]:
        logger.info("✅ All tests passed - database is healthy!")
        return True
    else:
        logger.error(
            f"❌ {results['failed_tests']} tests failed - please review issues"
        )
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
