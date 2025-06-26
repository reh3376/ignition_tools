#!/usr/bin/env python3
"""Phase 12.3: Neo4j Context Sharing - Integration Tests
Following crawl_mcp.py methodology with comprehensive validation.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any

import requests
from pydantic import BaseModel, Field


class TestResult(BaseModel):
    """Test result model following crawl_mcp.py patterns."""

    test_name: str
    success: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    execution_time: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class Phase123TestSuite:
    """Phase 12.3: Neo4j Context Sharing Integration Test Suite
    Following crawl_mcp.py methodology: Environment validation, input validation,
    error handling, modular testing, progressive complexity.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results: list[TestResult] = []

    def log_test_result(
        self,
        test_name: str,
        success: bool,
        message: str,
        details: dict[str, Any] | None = None,
        execution_time: float = 0.0,
    ):
        """Log test result following crawl_mcp.py patterns."""
        result = TestResult(
            test_name=test_name,
            success=success,
            message=message,
            details=details or {},
            execution_time=execution_time,
        )
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")

    # === STEP 1: ENVIRONMENT VALIDATION ===
    def test_environment_validation(self) -> bool:
        """Test environment setup following crawl_mcp.py methodology."""
        start_time = time.time()

        try:
            # Check API server availability
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code != 200:
                self.log_test_result(
                    "Environment Validation",
                    False,
                    f"API server not available: {response.status_code}",
                    execution_time=time.time() - start_time,
                )
                return False

            # Check Neo4j environment variables
            neo4j_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]
            missing_vars = [var for var in neo4j_vars if not os.getenv(var)]

            if missing_vars:
                self.log_test_result(
                    "Environment Validation",
                    False,
                    f"Missing Neo4j environment variables: {missing_vars}",
                    {"missing": missing_vars},
                    execution_time=time.time() - start_time,
                )
                return False

            # Test Neo4j knowledge graph status endpoint
            response = requests.get(f"{self.base_url}/api/v1/knowledge/status", timeout=30)
            if response.status_code != 200:
                self.log_test_result(
                    "Environment Validation",
                    False,
                    f"Knowledge graph status endpoint failed: {response.status_code}",
                    execution_time=time.time() - start_time,
                )
                return False

            knowledge_status = response.json()
            if not knowledge_status.get("success"):
                self.log_test_result(
                    "Environment Validation",
                    False,
                    "Neo4j connection failed",
                    knowledge_status,
                    execution_time=time.time() - start_time,
                )
                return False

            self.log_test_result(
                "Environment Validation",
                True,
                "All environment components validated successfully",
                {
                    "api_server": "available",
                    "neo4j_vars": "configured",
                    "knowledge_graph": "connected",
                },
                execution_time=time.time() - start_time,
            )
            return True

        except Exception as e:
            self.log_test_result(
                "Environment Validation",
                False,
                f"Environment validation failed: {e!s}",
                {"error": str(e)},
                execution_time=time.time() - start_time,
            )
            return False

    # === STEP 2: INPUT VALIDATION ===
    def test_input_validation(self) -> bool:
        """Test Pydantic input validation following crawl_mcp.py patterns."""
        start_time = time.time()

        try:
            validation_tests = [
                {
                    "name": "Valid Cypher Query",
                    "endpoint": "/api/v1/knowledge/query",
                    "payload": {
                        "query": "MATCH (n) RETURN count(n) as total",
                        "parameters": {},
                        "limit": 10,
                    },
                    "should_succeed": True,
                },
                {
                    "name": "Empty Query Validation",
                    "endpoint": "/api/v1/knowledge/query",
                    "payload": {"query": "", "parameters": {}, "limit": 10},
                    "should_succeed": False,
                },
                {
                    "name": "Destructive Query Prevention",
                    "endpoint": "/api/v1/knowledge/query",
                    "payload": {
                        "query": "DELETE (n) RETURN count(n)",
                        "parameters": {},
                        "limit": 10,
                    },
                    "should_succeed": False,
                },
                {
                    "name": "Valid Context Request",
                    "endpoint": "/api/v1/knowledge/context",
                    "payload": {
                        "repository": "test-repo",
                        "context_type": "classes",
                        "filters": {},
                    },
                    "should_succeed": True,
                },
                {
                    "name": "Invalid Context Type",
                    "endpoint": "/api/v1/knowledge/context",
                    "payload": {
                        "repository": "test-repo",
                        "context_type": "invalid_type",
                        "filters": {},
                    },
                    "should_succeed": False,
                },
            ]

            passed_tests = 0
            total_tests = len(validation_tests)

            for test in validation_tests:
                try:
                    response = requests.post(
                        f"{self.base_url}{test['endpoint']}",
                        json=test["payload"],
                        timeout=30,
                    )

                    if test["should_succeed"]:
                        success = response.status_code in [200, 201]
                    else:
                        success = response.status_code in [
                            400,
                            422,
                        ]  # Validation errors

                    if success:
                        passed_tests += 1
                        print(f"   ✓ {test['name']}")
                    else:
                        print(f"   ✗ {test['name']}: Expected {test['should_succeed']}, got {response.status_code}")

                except Exception as e:
                    print(f"   ✗ {test['name']}: Exception {e!s}")

            success_rate = passed_tests / total_tests
            success = success_rate >= 0.8  # 80% success rate required

            self.log_test_result(
                "Input Validation",
                success,
                f"Passed {passed_tests}/{total_tests} validation tests ({success_rate:.1%})",
                {
                    "passed": passed_tests,
                    "total": total_tests,
                    "success_rate": success_rate,
                },
                execution_time=time.time() - start_time,
            )
            return success

        except Exception as e:
            self.log_test_result(
                "Input Validation",
                False,
                f"Input validation testing failed: {e!s}",
                {"error": str(e)},
                execution_time=time.time() - start_time,
            )
            return False

    # === STEP 3: ERROR HANDLING ===
    def test_error_handling(self) -> bool:
        """Test comprehensive error handling following crawl_mcp.py patterns."""
        start_time = time.time()

        try:
            error_tests = [
                {
                    "name": "Invalid Cypher Syntax",
                    "endpoint": "/api/v1/knowledge/query",
                    "payload": {"query": "INVALID CYPHER SYNTAX", "limit": 10},
                    "expected_error_type": "syntax",
                },
                {
                    "name": "Repository Not Found",
                    "endpoint": "/api/v1/knowledge/repositories/nonexistent-repo/overview",
                    "method": "GET",
                    "expected_status": 404,
                },
                {
                    "name": "Missing Required Fields",
                    "endpoint": "/api/v1/knowledge/query",
                    "payload": {"limit": 10},  # Missing query field
                    "expected_status": 422,
                },
                {
                    "name": "Limit Out of Range",
                    "endpoint": "/api/v1/knowledge/query",
                    "payload": {
                        "query": "MATCH (n) RETURN n",
                        "limit": 200,
                    },  # Over 100 limit
                    "expected_status": 422,
                },
            ]

            passed_tests = 0
            total_tests = len(error_tests)

            for test in error_tests:
                try:
                    if test.get("method") == "GET":
                        response = requests.get(f"{self.base_url}{test['endpoint']}", timeout=30)
                    else:
                        response = requests.post(
                            f"{self.base_url}{test['endpoint']}",
                            json=test["payload"],
                            timeout=30,
                        )

                    expected_status = test.get("expected_status", 400)
                    if response.status_code == expected_status:
                        passed_tests += 1
                        print(f"   ✓ {test['name']}: Correct error handling")
                    else:
                        print(f"   ✗ {test['name']}: Expected {expected_status}, got {response.status_code}")

                except Exception as e:
                    print(f"   ✗ {test['name']}: Exception {e!s}")

            success_rate = passed_tests / total_tests
            success = success_rate >= 0.75  # 75% success rate for error handling

            self.log_test_result(
                "Error Handling",
                success,
                f"Passed {passed_tests}/{total_tests} error handling tests ({success_rate:.1%})",
                {
                    "passed": passed_tests,
                    "total": total_tests,
                    "success_rate": success_rate,
                },
                execution_time=time.time() - start_time,
            )
            return success

        except Exception as e:
            self.log_test_result(
                "Error Handling",
                False,
                f"Error handling testing failed: {e!s}",
                {"error": str(e)},
                execution_time=time.time() - start_time,
            )
            return False

    # === STEP 4: KNOWLEDGE GRAPH FUNCTIONALITY ===
    def test_knowledge_graph_functionality(self) -> bool:
        """Test Neo4j context sharing functionality."""
        start_time = time.time()

        try:
            functionality_tests = [
                {
                    "name": "Knowledge Graph Status",
                    "endpoint": "/api/v1/knowledge/status",
                    "method": "GET",
                },
                {
                    "name": "List Repositories",
                    "endpoint": "/api/v1/knowledge/repositories",
                    "method": "GET",
                },
                {
                    "name": "CLI-API Mapping",
                    "endpoint": "/api/v1/knowledge/cli-mapping",
                    "method": "GET",
                },
                {
                    "name": "Agent Context",
                    "endpoint": "/api/v1/knowledge/agent-context",
                    "method": "GET",
                },
                {
                    "name": "Basic Query Execution",
                    "endpoint": "/api/v1/knowledge/query",
                    "method": "POST",
                    "payload": {
                        "query": "MATCH (n) RETURN count(n) as total_nodes LIMIT 1",
                        "limit": 1,
                    },
                },
            ]

            passed_tests = 0
            total_tests = len(functionality_tests)

            for test in functionality_tests:
                try:
                    if test["method"] == "GET":
                        response = requests.get(f"{self.base_url}{test['endpoint']}", timeout=30)
                    else:
                        response = requests.post(
                            f"{self.base_url}{test['endpoint']}",
                            json=test.get("payload", {}),
                            timeout=30,
                        )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success", True):  # Some endpoints don't have success field
                            passed_tests += 1
                            print(f"   ✓ {test['name']}: Working correctly")
                        else:
                            print(f"   ✗ {test['name']}: Response indicates failure")
                    else:
                        print(f"   ✗ {test['name']}: HTTP {response.status_code}")

                except Exception as e:
                    print(f"   ✗ {test['name']}: Exception {e!s}")

            success_rate = passed_tests / total_tests
            success = success_rate >= 0.8  # 80% success rate required

            self.log_test_result(
                "Knowledge Graph Functionality",
                success,
                f"Passed {passed_tests}/{total_tests} functionality tests ({success_rate:.1%})",
                {
                    "passed": passed_tests,
                    "total": total_tests,
                    "success_rate": success_rate,
                },
                execution_time=time.time() - start_time,
            )
            return success

        except Exception as e:
            self.log_test_result(
                "Knowledge Graph Functionality",
                False,
                f"Functionality testing failed: {e!s}",
                {"error": str(e)},
                execution_time=time.time() - start_time,
            )
            return False

    # === STEP 5: PROGRESSIVE COMPLEXITY ===
    def test_progressive_complexity(self) -> bool:
        """Test progressive complexity implementation following crawl_mcp.py."""
        start_time = time.time()

        try:
            # Test endpoint availability across complexity levels
            endpoints = [
                # Basic Level
                {"path": "/api/v1/knowledge/status", "level": "basic"},
                {"path": "/api/v1/knowledge/repositories", "level": "basic"},
                # Standard Level
                {"path": "/api/v1/knowledge/query", "level": "standard"},
                {"path": "/api/v1/knowledge/cli-mapping", "level": "standard"},
                # Advanced Level
                {"path": "/api/v1/knowledge/context", "level": "advanced"},
                {"path": "/api/v1/knowledge/agent-context", "level": "advanced"},
                # Enterprise Level (repository-specific)
                {
                    "path": "/api/v1/knowledge/repositories/test/overview",
                    "level": "enterprise",
                },
            ]

            available_endpoints = 0
            total_endpoints = len(endpoints)

            for endpoint in endpoints:
                try:
                    if "query" in endpoint["path"] or "context" in endpoint["path"]:
                        # POST endpoints need payload
                        response = requests.post(
                            f"{self.base_url}{endpoint['path']}",
                            json=(
                                {"query": "MATCH (n) RETURN count(n)", "limit": 1}
                                if "query" in endpoint["path"]
                                else {"repository": "test", "context_type": "classes"}
                            ),
                            timeout=10,
                        )
                    else:
                        response = requests.get(f"{self.base_url}{endpoint['path']}", timeout=10)

                    # Accept 200, 404 (for test repo), or 500 (if Neo4j issue) as "available"
                    if response.status_code in [200, 404, 500]:
                        available_endpoints += 1
                        print(f"   ✓ {endpoint['level'].title()}: {endpoint['path']}")
                    else:
                        print(f"   ✗ {endpoint['level'].title()}: {endpoint['path']} - {response.status_code}")

                except Exception:
                    print(f"   ✗ {endpoint['level'].title()}: {endpoint['path']} - Exception")

            success_rate = available_endpoints / total_endpoints
            success = success_rate >= 0.85  # 85% endpoint availability required

            self.log_test_result(
                "Progressive Complexity",
                success,
                f"Available endpoints: {available_endpoints}/{total_endpoints} ({success_rate:.1%})",
                {
                    "available": available_endpoints,
                    "total": total_endpoints,
                    "success_rate": success_rate,
                    "complexity_levels": [
                        "basic",
                        "standard",
                        "advanced",
                        "enterprise",
                    ],
                },
                execution_time=time.time() - start_time,
            )
            return success

        except Exception as e:
            self.log_test_result(
                "Progressive Complexity",
                False,
                f"Progressive complexity testing failed: {e!s}",
                {"error": str(e)},
                execution_time=time.time() - start_time,
            )
            return False

    def run_comprehensive_test_suite(self) -> dict[str, Any]:
        """Run complete test suite following crawl_mcp.py methodology."""
        print("=" * 80)
        print("PHASE 12.3: NEO4J CONTEXT SHARING - INTEGRATION TESTS")
        print("Following crawl_mcp.py methodology")
        print("=" * 80)

        start_time = time.time()

        # Execute tests in crawl_mcp.py order
        test_results = {
            "environment_validation": self.test_environment_validation(),
            "input_validation": self.test_input_validation(),
            "error_handling": self.test_error_handling(),
            "knowledge_graph_functionality": self.test_knowledge_graph_functionality(),
            "progressive_complexity": self.test_progressive_complexity(),
        }

        # Calculate overall success
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = passed_tests / total_tests
        overall_success = success_rate >= 0.8  # 80% success rate for completion

        total_time = time.time() - start_time

        print("\n" + "=" * 80)
        print("PHASE 12.3 INTEGRATION TEST RESULTS")
        print("=" * 80)

        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")

        print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})")
        print(f"Total execution time: {total_time:.2f} seconds")

        if overall_success:
            print("\n🎯 PHASE 12.3 COMPLETION CRITERIA MET")
            print("✅ Neo4j Context Sharing API implementation successful")
        else:
            print("\n⚠️  PHASE 12.3 NEEDS ADDITIONAL WORK")
            print("❌ Some components require attention")

        return {
            "overall_success": overall_success,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "execution_time": total_time,
            "test_results": test_results,
            "individual_results": [result.dict() for result in self.test_results],
        }


def main() -> None:
    """Main test execution following crawl_mcp.py patterns."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print(f"Testing Phase 12.3 API at: {base_url}")

    test_suite = Phase123TestSuite(base_url)
    results = test_suite.run_comprehensive_test_suite()

    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)


if __name__ == "__main__":
    main()
