#!/usr/bin/env python3
"""Phase 12.5: Testing & Validation - Comprehensive Test Suite

Following crawl_mcp.py methodology for systematic testing:
1. Environment validation first
2. Comprehensive input validation
3. Robust error handling testing
4. Modular testing approach
5. Progressive complexity validation
6. Proper resource management
7. Performance benchmarking
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Test configuration following crawl_mcp.py patterns
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
CLI_BASE_PATH = os.getenv("CLI_BASE_PATH", ".")
TEST_TIMEOUT = 30
PERFORMANCE_THRESHOLD_MS = 200
LOAD_TEST_CONCURRENT_USERS = 10


class TestResult(BaseModel):
    """Test result model following crawl_mcp.py patterns"""

    test_name: str
    category: str
    success: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    execution_time: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class Phase125ComprehensiveTester:
    """Comprehensive testing suite following crawl_mcp.py methodology"""

    def __init__(self):
        self.api_base = API_BASE_URL
        self.cli_base = CLI_BASE_PATH
        self.test_results: list[TestResult] = []
        self.performance_results: dict[str, float] = {}
        self.start_time = time.time()

    def log_test_result(
        self,
        test_name: str,
        category: str,
        success: bool,
        message: str,
        details: dict[str, Any] | None = None,
        execution_time: float | None = None,
    ):
        """Log test result following crawl_mcp.py logging patterns"""
        result = TestResult(
            test_name=test_name,
            category=category,
            success=success,
            message=message,
            details=details or {},
            execution_time=execution_time or 0.0,
        )
        self.test_results.append(result)

        # Console output
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}: {message}")

    # === STEP 1: ENVIRONMENT VALIDATION FIRST ===
    async def test_environment_validation(self) -> bool:
        """Test environment validation (crawl_mcp.py Step 1)"""
        print("🔍 Step 1: Environment Validation Testing")
        start_time = time.time()

        try:
            validation_results = {
                "api_server_running": False,
                "neo4j_available": False,
                "cli_commands_available": False,
                "required_packages": False,
                "environment_variables": False,
                "file_permissions": False,
            }

            # Test API server availability
            try:
                async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                    response = await client.get(f"{self.api_base}/health")
                    validation_results["api_server_running"] = (
                        response.status_code == 200
                    )
                    self.log_test_result(
                        "API Server Health Check",
                        "environment",
                        validation_results["api_server_running"],
                        f"API server status: {response.status_code}",
                        {
                            "url": f"{self.api_base}/health",
                            "status": response.status_code,
                        },
                        time.time() - start_time,
                    )
            except Exception as e:
                self.log_test_result(
                    "API Server Health Check",
                    "environment",
                    False,
                    f"API server unreachable: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Test Neo4j availability
            try:
                neo4j_env = {
                    "uri": os.getenv("NEO4J_URI"),
                    "user": os.getenv("NEO4J_USER"),
                    "password": os.getenv("NEO4J_PASSWORD"),
                }
                validation_results["neo4j_available"] = all(neo4j_env.values())
                self.log_test_result(
                    "Neo4j Environment Variables",
                    "environment",
                    validation_results["neo4j_available"],
                    f"Neo4j credentials available: {validation_results['neo4j_available']}",
                    {"env_vars": {k: bool(v) for k, v in neo4j_env.items()}},
                    time.time() - start_time,
                )
            except Exception as e:
                self.log_test_result(
                    "Neo4j Environment Variables",
                    "environment",
                    False,
                    f"Neo4j environment check failed: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Test CLI commands availability
            try:
                # Test basic CLI command
                result = subprocess.run(
                    ["python", "-m", "src.main", "--help"],
                    cwd=self.cli_base,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                validation_results["cli_commands_available"] = result.returncode == 0
                self.log_test_result(
                    "CLI Commands Availability",
                    "environment",
                    validation_results["cli_commands_available"],
                    f"CLI help command status: {result.returncode}",
                    {"output_length": len(result.stdout) if result.stdout else 0},
                    time.time() - start_time,
                )
            except Exception as e:
                self.log_test_result(
                    "CLI Commands Availability",
                    "environment",
                    False,
                    f"CLI test failed: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Test required packages
            try:
                required_packages = [
                    "fastapi",
                    "uvicorn",
                    "pydantic",
                    "httpx",
                    "neo4j",
                    "pytest",
                ]
                missing_packages = []
                for package in required_packages:
                    try:
                        __import__(package)
                    except ImportError:
                        missing_packages.append(package)

                validation_results["required_packages"] = len(missing_packages) == 0
                self.log_test_result(
                    "Required Packages",
                    "environment",
                    validation_results["required_packages"],
                    (
                        f"Missing packages: {missing_packages}"
                        if missing_packages
                        else "All packages available"
                    ),
                    {
                        "missing": missing_packages,
                        "total_required": len(required_packages),
                    },
                    time.time() - start_time,
                )
            except Exception as e:
                self.log_test_result(
                    "Required Packages",
                    "environment",
                    False,
                    f"Package check failed: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Test environment variables
            try:
                required_env_vars = [
                    "NEO4J_URI",
                    "NEO4J_USER",
                    "NEO4J_PASSWORD",
                ]
                missing_env_vars = [
                    var for var in required_env_vars if not os.getenv(var)
                ]
                validation_results["environment_variables"] = len(missing_env_vars) == 0
                self.log_test_result(
                    "Environment Variables",
                    "environment",
                    validation_results["environment_variables"],
                    (
                        f"Missing env vars: {missing_env_vars}"
                        if missing_env_vars
                        else "All env vars present"
                    ),
                    {
                        "missing": missing_env_vars,
                        "total_required": len(required_env_vars),
                    },
                    time.time() - start_time,
                )
            except Exception as e:
                self.log_test_result(
                    "Environment Variables",
                    "environment",
                    False,
                    f"Environment variable check failed: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Test file permissions
            try:
                test_dirs = ["src", "tests", "docs"]
                permission_issues = []
                for dir_name in test_dirs:
                    test_path = Path(self.cli_base) / dir_name
                    if test_path.exists():
                        if not os.access(test_path, os.R_OK):
                            permission_issues.append(f"{dir_name}: no read access")
                        if dir_name in ["tests"] and not os.access(test_path, os.W_OK):
                            permission_issues.append(f"{dir_name}: no write access")

                validation_results["file_permissions"] = len(permission_issues) == 0
                self.log_test_result(
                    "File Permissions",
                    "environment",
                    validation_results["file_permissions"],
                    (
                        f"Permission issues: {permission_issues}"
                        if permission_issues
                        else "All permissions OK"
                    ),
                    {"issues": permission_issues, "dirs_checked": test_dirs},
                    time.time() - start_time,
                )
            except Exception as e:
                self.log_test_result(
                    "File Permissions",
                    "environment",
                    False,
                    f"Permission check failed: {e}",
                    {"error": str(e)},
                    time.time() - start_time,
                )

            # Overall environment validation result
            overall_success = (
                sum(validation_results.values()) >= 4
            )  # At least 4/6 must pass
            success_rate = (
                sum(validation_results.values()) / len(validation_results) * 100
            )

            print(f"   📊 Environment Validation: {success_rate:.1f}% success rate")
            return overall_success

        except Exception as e:
            self.log_test_result(
                "Environment Validation Overall",
                "environment",
                False,
                f"Environment validation failed: {e}",
                {"error": str(e)},
                time.time() - start_time,
            )
            return False

    # === STEP 2: COMPREHENSIVE INPUT VALIDATION ===
    async def test_input_validation(self) -> bool:
        """Test input validation and sanitization (crawl_mcp.py Step 2)"""
        print("🔍 Step 2: Input Validation Testing")
        start_time = time.time()

        try:
            validation_tests = [
                # API Input Validation Tests
                {
                    "name": "Valid Knowledge Graph Query",
                    "endpoint": "/api/v1/knowledge/query",
                    "method": "POST",
                    "payload": {
                        "query": "MATCH (n) RETURN count(n) as total",
                        "parameters": {},
                        "limit": 10,
                    },
                    "expected_status": [200, 201],
                },
                {
                    "name": "Empty Query Rejection",
                    "endpoint": "/api/v1/knowledge/query",
                    "method": "POST",
                    "payload": {"query": "", "parameters": {}, "limit": 10},
                    "expected_status": [400, 422],
                },
                {
                    "name": "SQL Injection Prevention",
                    "endpoint": "/api/v1/knowledge/query",
                    "method": "POST",
                    "payload": {
                        "query": "'; DROP TABLE users; --",
                        "parameters": {},
                        "limit": 10,
                    },
                    "expected_status": [400, 422],
                },
                {
                    "name": "Limit Boundary Validation",
                    "endpoint": "/api/v1/knowledge/query",
                    "method": "POST",
                    "payload": {
                        "query": "MATCH (n) RETURN n",
                        "parameters": {},
                        "limit": 200,  # Over limit
                    },
                    "expected_status": [400, 422],
                },
                {
                    "name": "Valid Script Generation Request",
                    "endpoint": "/api/v1/scripts/generate",
                    "method": "POST",
                    "payload": {
                        "template_type": "opcua_client",
                        "parameters": {"server_url": "opc.tcp://localhost:4840"},
                        "output_format": "python",
                    },
                    "expected_status": [200, 201],
                },
                {
                    "name": "Invalid Template Type Rejection",
                    "endpoint": "/api/v1/scripts/generate",
                    "method": "POST",
                    "payload": {
                        "template_type": "invalid_template",
                        "parameters": {},
                        "output_format": "python",
                    },
                    "expected_status": [400, 422],
                },
            ]

            passed_tests = 0
            total_tests = len(validation_tests)

            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                for test in validation_tests:
                    test_start = time.time()
                    try:
                        if test["method"] == "POST":
                            response = await client.post(
                                f"{self.api_base}{test['endpoint']}",
                                json=test["payload"],
                            )
                        else:
                            response = await client.get(
                                f"{self.api_base}{test['endpoint']}"
                            )

                        success = response.status_code in test["expected_status"]
                        if success:
                            passed_tests += 1

                        self.log_test_result(
                            test["name"],
                            "input_validation",
                            success,
                            f"Status: {response.status_code}, Expected: {test['expected_status']}",
                            {
                                "status_code": response.status_code,
                                "expected": test["expected_status"],
                                "endpoint": test["endpoint"],
                            },
                            time.time() - test_start,
                        )

                    except Exception as e:
                        self.log_test_result(
                            test["name"],
                            "input_validation",
                            False,
                            f"Test failed: {e}",
                            {"error": str(e), "endpoint": test["endpoint"]},
                            time.time() - test_start,
                        )

            success_rate = passed_tests / total_tests * 100
            print(f"   📊 Input Validation: {success_rate:.1f}% success rate")
            return success_rate >= 75  # 75% success rate required

        except Exception as e:
            self.log_test_result(
                "Input Validation Overall",
                "input_validation",
                False,
                f"Input validation testing failed: {e}",
                {"error": str(e)},
                time.time() - start_time,
            )
            return False

    # === STEP 3: COMPREHENSIVE ERROR HANDLING ===
    async def test_error_handling(self) -> bool:
        """Test comprehensive error handling (crawl_mcp.py Step 3)"""
        print("🔍 Step 3: Error Handling Testing")
        start_time = time.time()

        try:
            error_tests = [
                {
                    "name": "404 Not Found Handling",
                    "endpoint": "/api/v1/nonexistent/endpoint",
                    "method": "GET",
                    "expected_status": 404,
                },
                {
                    "name": "Authentication Error Handling",
                    "endpoint": "/api/v1/auth/me",
                    "method": "GET",
                    "headers": {"Authorization": "Bearer invalid_token"},
                    "expected_status": 401,
                },
                {
                    "name": "Malformed JSON Handling",
                    "endpoint": "/api/v1/knowledge/query",
                    "method": "POST",
                    "raw_data": '{"query": "MATCH (n) RETURN n", "invalid_json": }',
                    "expected_status": 400,
                },
                {
                    "name": "Method Not Allowed Handling",
                    "endpoint": "/api/v1/knowledge/query",
                    "method": "DELETE",
                    "expected_status": 405,
                },
                {
                    "name": "Rate Limit Error Handling",
                    "endpoint": "/api/v1/auth/validate",
                    "method": "GET",
                    "repeat": 15,  # Exceed rate limit
                    "expected_status": [200, 429],
                },
            ]

            passed_tests = 0
            total_tests = len(error_tests)

            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                for test in error_tests:
                    test_start = time.time()
                    try:
                        headers = test.get("headers", {})
                        repeat_count = test.get("repeat", 1)

                        success = False
                        for i in range(repeat_count):
                            if test["method"] == "GET":
                                response = await client.get(
                                    f"{self.api_base}{test['endpoint']}",
                                    headers=headers,
                                )
                            elif test["method"] == "POST":
                                if "raw_data" in test:
                                    response = await client.post(
                                        f"{self.api_base}{test['endpoint']}",
                                        content=test["raw_data"],
                                        headers={
                                            **headers,
                                            "Content-Type": "application/json",
                                        },
                                    )
                                else:
                                    response = await client.post(
                                        f"{self.api_base}{test['endpoint']}",
                                        headers=headers,
                                    )
                            elif test["method"] == "DELETE":
                                response = await client.delete(
                                    f"{self.api_base}{test['endpoint']}",
                                    headers=headers,
                                )

                            if isinstance(test["expected_status"], list):
                                if response.status_code in test["expected_status"]:
                                    success = True
                                    break
                            else:
                                if response.status_code == test["expected_status"]:
                                    success = True
                                    break

                        if success:
                            passed_tests += 1

                        self.log_test_result(
                            test["name"],
                            "error_handling",
                            success,
                            f"Status: {response.status_code}, Expected: {test['expected_status']}",
                            {
                                "status_code": response.status_code,
                                "expected": test["expected_status"],
                                "endpoint": test["endpoint"],
                                "repeat_count": repeat_count,
                            },
                            time.time() - test_start,
                        )

                    except Exception as e:
                        self.log_test_result(
                            test["name"],
                            "error_handling",
                            False,
                            f"Error handling test failed: {e}",
                            {"error": str(e), "endpoint": test["endpoint"]},
                            time.time() - test_start,
                        )

            success_rate = passed_tests / total_tests * 100
            print(f"   📊 Error Handling: {success_rate:.1f}% success rate")
            return success_rate >= 75  # 75% success rate required

        except Exception as e:
            self.log_test_result(
                "Error Handling Overall",
                "error_handling",
                False,
                f"Error handling testing failed: {e}",
                {"error": str(e)},
                time.time() - start_time,
            )
            return False

    # === STEP 4: API FUNCTIONALITY TESTING ===
    async def test_api_functionality(self) -> bool:
        """Test API functionality following crawl_mcp.py Step 4"""
        print("🔍 Step 4: API Functionality Testing")
        start_time = time.time()

        try:
            functionality_tests = [
                # Core API endpoints
                {
                    "name": "Health Check Endpoint",
                    "endpoint": "/health",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "Environment Validation Endpoint",
                    "endpoint": "/api/v1/environment/validate",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "SME Status Endpoint",
                    "endpoint": "/api/v1/sme/status",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "Knowledge Graph Status",
                    "endpoint": "/api/v1/knowledge/status",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "Templates List Endpoint",
                    "endpoint": "/api/v1/templates/list",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "Refactoring Detection",
                    "endpoint": "/api/v1/refactor/detect",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "Modules List Endpoint",
                    "endpoint": "/api/v1/modules/list",
                    "method": "GET",
                    "expected_status": 200,
                },
                {
                    "name": "System Info Endpoint",
                    "endpoint": "/api/v1/system/info",
                    "method": "GET",
                    "expected_status": 200,
                },
            ]

            passed_tests = 0
            total_tests = len(functionality_tests)

            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                for test in functionality_tests:
                    test_start = time.time()
                    try:
                        if test["method"] == "GET":
                            response = await client.get(
                                f"{self.api_base}{test['endpoint']}"
                            )
                        elif test["method"] == "POST":
                            response = await client.post(
                                f"{self.api_base}{test['endpoint']}"
                            )

                        success = response.status_code == test["expected_status"]
                        if success:
                            passed_tests += 1
                            # Store performance data
                            self.performance_results[test["name"]] = (
                                time.time() - test_start
                            )

                        self.log_test_result(
                            test["name"],
                            "api_functionality",
                            success,
                            f"Status: {response.status_code}, Expected: {test['expected_status']}",
                            {
                                "status_code": response.status_code,
                                "expected": test["expected_status"],
                                "endpoint": test["endpoint"],
                                "response_time_ms": round(
                                    (time.time() - test_start) * 1000, 2
                                ),
                            },
                            time.time() - test_start,
                        )

                    except Exception as e:
                        self.log_test_result(
                            test["name"],
                            "api_functionality",
                            False,
                            f"API functionality test failed: {e}",
                            {"error": str(e), "endpoint": test["endpoint"]},
                            time.time() - test_start,
                        )

            success_rate = passed_tests / total_tests * 100
            print(f"   📊 API Functionality: {success_rate:.1f}% success rate")
            return success_rate >= 80  # 80% success rate required

        except Exception as e:
            self.log_test_result(
                "API Functionality Overall",
                "api_functionality",
                False,
                f"API functionality testing failed: {e}",
                {"error": str(e)},
                time.time() - start_time,
            )
            return False

    # === STEP 5: PROGRESSIVE COMPLEXITY VALIDATION ===
    async def test_progressive_complexity(self) -> bool:
        """Test progressive complexity implementation (crawl_mcp.py Step 5)"""
        print("🔍 Step 5: Progressive Complexity Testing")
        start_time = time.time()

        try:
            complexity_levels = {
                "basic": [
                    "/health",
                    "/api/v1/environment/validate",
                    "/api/v1/system/info",
                ],
                "standard": [
                    "/api/v1/sme/status",
                    "/api/v1/templates/list",
                    "/api/v1/modules/list",
                ],
                "advanced": [
                    "/api/v1/knowledge/status",
                    "/api/v1/knowledge/repositories",
                    "/api/v1/refactor/detect",
                ],
                "enterprise": [
                    "/api/v1/knowledge/query",
                    "/api/v1/knowledge/context",
                    "/api/v1/auth/validate",
                ],
            }

            level_results = {}

            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                for level, endpoints in complexity_levels.items():
                    level_start = time.time()
                    available_endpoints = 0
                    total_endpoints = len(endpoints)

                    for endpoint in endpoints:
                        try:
                            response = await client.get(f"{self.api_base}{endpoint}")
                            if response.status_code in [
                                200,
                                201,
                                401,
                                422,
                            ]:  # Valid responses
                                available_endpoints += 1
                        except Exception:
                            pass  # Endpoint not available

                    level_success_rate = available_endpoints / total_endpoints * 100
                    level_results[level] = {
                        "available": available_endpoints,
                        "total": total_endpoints,
                        "success_rate": level_success_rate,
                    }

                    self.log_test_result(
                        f"Progressive Complexity - {level.title()} Level",
                        "progressive_complexity",
                        level_success_rate >= 75,
                        f"{available_endpoints}/{total_endpoints} endpoints available ({level_success_rate:.1f}%)",
                        level_results[level],
                        time.time() - level_start,
                    )

            # Overall progressive complexity validation
            overall_success = all(
                level_data["success_rate"] >= 60
                for level_data in level_results.values()
            )
            avg_success_rate = sum(
                level_data["success_rate"] for level_data in level_results.values()
            ) / len(level_results)

            print(
                f"   📊 Progressive Complexity: {avg_success_rate:.1f}% average success rate"
            )
            return avg_success_rate >= 70  # 70% average success rate required

        except Exception as e:
            self.log_test_result(
                "Progressive Complexity Overall",
                "progressive_complexity",
                False,
                f"Progressive complexity testing failed: {e}",
                {"error": str(e)},
                time.time() - start_time,
            )
            return False

    # === STEP 6: PERFORMANCE BENCHMARKING ===
    async def test_performance_benchmarking(self) -> bool:
        """Test performance benchmarking (crawl_mcp.py Step 6)"""
        print("🔍 Step 6: Performance Benchmarking")
        start_time = time.time()

        try:
            performance_tests = [
                {
                    "name": "Health Check Response Time",
                    "endpoint": "/health",
                    "method": "GET",
                    "max_response_time_ms": 50,
                },
                {
                    "name": "Environment Validation Response Time",
                    "endpoint": "/api/v1/environment/validate",
                    "method": "GET",
                    "max_response_time_ms": 200,
                },
                {
                    "name": "Knowledge Graph Status Response Time",
                    "endpoint": "/api/v1/knowledge/status",
                    "method": "GET",
                    "max_response_time_ms": 300,
                },
                {
                    "name": "Templates List Response Time",
                    "endpoint": "/api/v1/templates/list",
                    "method": "GET",
                    "max_response_time_ms": 100,
                },
            ]

            passed_tests = 0
            total_tests = len(performance_tests)

            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                for test in performance_tests:
                    # Run multiple times for average
                    response_times = []
                    for _ in range(5):
                        test_start = time.time()
                        try:
                            response = await client.get(
                                f"{self.api_base}{test['endpoint']}"
                            )
                            response_time_ms = (time.time() - test_start) * 1000
                            if response.status_code == 200:
                                response_times.append(response_time_ms)
                        except Exception:
                            pass

                    if response_times:
                        avg_response_time = sum(response_times) / len(response_times)
                        success = avg_response_time <= test["max_response_time_ms"]
                        if success:
                            passed_tests += 1

                        self.log_test_result(
                            test["name"],
                            "performance",
                            success,
                            f"Avg response time: {avg_response_time:.1f}ms (max: {test['max_response_time_ms']}ms)",
                            {
                                "avg_response_time_ms": round(avg_response_time, 2),
                                "max_allowed_ms": test["max_response_time_ms"],
                                "all_response_times": [
                                    round(rt, 2) for rt in response_times
                                ],
                            },
                            avg_response_time / 1000,
                        )
                    else:
                        self.log_test_result(
                            test["name"],
                            "performance",
                            False,
                            "No successful responses for performance testing",
                            {"endpoint": test["endpoint"]},
                            0,
                        )

            success_rate = passed_tests / total_tests * 100
            print(f"   📊 Performance Benchmarking: {success_rate:.1f}% success rate")
            return success_rate >= 75  # 75% success rate required

        except Exception as e:
            self.log_test_result(
                "Performance Benchmarking Overall",
                "performance",
                False,
                f"Performance benchmarking failed: {e}",
                {"error": str(e)},
                time.time() - start_time,
            )
            return False

    # === STEP 7: CLI-TO-API MAPPING VALIDATION ===
    async def test_cli_api_mapping(self) -> bool:
        """Test CLI-to-API mapping validation (crawl_mcp.py Step 7)"""
        print("🔍 Step 7: CLI-to-API Mapping Validation")
        start_time = time.time()

        try:
            # Test CLI-to-API mappings
            cli_api_mappings = [
                {
                    "cli_command": [
                        "python",
                        "-m",
                        "src.main",
                        "module",
                        "sme",
                        "validate-env",
                    ],
                    "api_endpoint": "/api/v1/sme/validate-env",
                    "name": "SME Environment Validation",
                },
                {
                    "cli_command": [
                        "python",
                        "-m",
                        "src.main",
                        "module",
                        "sme",
                        "status",
                    ],
                    "api_endpoint": "/api/v1/sme/status",
                    "name": "SME Status Check",
                },
                {
                    "cli_command": ["python", "-m", "src.main", "refactor", "detect"],
                    "api_endpoint": "/api/v1/refactor/detect",
                    "name": "Refactoring Detection",
                },
                {
                    "cli_command": [
                        "python",
                        "-m",
                        "src.main",
                        "refactor",
                        "statistics",
                    ],
                    "api_endpoint": "/api/v1/refactor/statistics",
                    "name": "Refactoring Statistics",
                },
            ]

            passed_tests = 0
            total_tests = len(cli_api_mappings)

            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                for mapping in cli_api_mappings:
                    mapping_start = time.time()
                    cli_success = False
                    api_success = False

                    # Test CLI command
                    try:
                        cli_result = subprocess.run(
                            mapping["cli_command"],
                            cwd=self.cli_base,
                            capture_output=True,
                            text=True,
                            timeout=15,
                        )
                        cli_success = cli_result.returncode == 0
                    except Exception:
                        cli_success = False

                    # Test API endpoint
                    try:
                        api_response = await client.get(
                            f"{self.api_base}{mapping['api_endpoint']}"
                        )
                        api_success = api_response.status_code in [200, 201]
                    except Exception:
                        api_success = False

                    # Both should work or both should fail (consistency)
                    mapping_success = cli_success == api_success
                    if mapping_success:
                        passed_tests += 1

                    self.log_test_result(
                        mapping["name"],
                        "cli_api_mapping",
                        mapping_success,
                        f"CLI: {'✅' if cli_success else '❌'}, API: {'✅' if api_success else '❌'} (consistent: {mapping_success})",
                        {
                            "cli_success": cli_success,
                            "api_success": api_success,
                            "consistent": mapping_success,
                            "cli_command": " ".join(mapping["cli_command"]),
                            "api_endpoint": mapping["api_endpoint"],
                        },
                        time.time() - mapping_start,
                    )

            success_rate = passed_tests / total_tests * 100
            print(f"   📊 CLI-to-API Mapping: {success_rate:.1f}% success rate")
            return success_rate >= 70  # 70% success rate required

        except Exception as e:
            self.log_test_result(
                "CLI-to-API Mapping Overall",
                "cli_api_mapping",
                False,
                f"CLI-to-API mapping testing failed: {e}",
                {"error": str(e)},
                time.time() - start_time,
            )
            return False

    # === MAIN TEST EXECUTION ===
    async def run_comprehensive_test_suite(self) -> dict[str, Any]:
        """Run complete test suite following crawl_mcp.py methodology"""
        print("=" * 80)
        print("PHASE 12.5: TESTING & VALIDATION - COMPREHENSIVE TEST SUITE")
        print("Following crawl_mcp.py methodology for systematic validation")
        print("=" * 80)

        start_time = time.time()

        # Execute tests in crawl_mcp.py order
        test_results = {}

        try:
            # Step 1: Environment validation first (critical)
            test_results["environment_validation"] = (
                await self.test_environment_validation()
            )

            # Step 2: Input validation and sanitization
            test_results["input_validation"] = await self.test_input_validation()

            # Step 3: Comprehensive error handling
            test_results["error_handling"] = await self.test_error_handling()

            # Step 4: API functionality testing
            test_results["api_functionality"] = await self.test_api_functionality()

            # Step 5: Progressive complexity validation
            test_results["progressive_complexity"] = (
                await self.test_progressive_complexity()
            )

            # Step 6: Performance benchmarking
            test_results["performance_benchmarking"] = (
                await self.test_performance_benchmarking()
            )

            # Step 7: CLI-to-API mapping validation
            test_results["cli_api_mapping"] = await self.test_cli_api_mapping()

        except Exception as e:
            print(f"❌ Test suite execution failed: {e}")
            test_results["execution_error"] = str(e)

        # Calculate overall results
        passed_categories = sum(
            test_results.values() if isinstance(test_results.values(), bool) else 0
        )
        total_categories = len(
            [k for k, v in test_results.items() if isinstance(v, bool)]
        )
        overall_success_rate = (
            passed_categories / total_categories * 100 if total_categories > 0 else 0
        )
        overall_success = (
            overall_success_rate >= 75
        )  # 75% success rate for Phase 12.5 completion

        execution_time = time.time() - start_time

        # Generate comprehensive report
        report = {
            "phase": "12.5 - Testing & Validation",
            "methodology": "crawl_mcp.py systematic testing",
            "execution_time": round(execution_time, 2),
            "timestamp": datetime.now().isoformat(),
            "overall_success_rate": round(overall_success_rate, 1),
            "categories_passed": passed_categories,
            "categories_total": total_categories,
            "completion_status": (
                "COMPLETED" if overall_success else "NEEDS_IMPROVEMENT"
            ),
            "test_results": test_results,
            "detailed_results": [result.dict() for result in self.test_results],
            "performance_results": self.performance_results,
            "recommendations": self._generate_recommendations(test_results),
        }

        # Print final summary
        print("\n" + "=" * 80)
        print("PHASE 12.5 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)

        for category, result in test_results.items():
            if isinstance(result, bool):
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {category.replace('_', ' ').title()}")

        print(f"\nOverall Success Rate: {overall_success_rate:.1f}%")
        print(f"Categories Passed: {passed_categories}/{total_categories}")
        print(f"Total Execution Time: {execution_time:.2f} seconds")
        print(f"Total Individual Tests: {len(self.test_results)}")

        if overall_success:
            print("\n🎯 PHASE 12.5 COMPLETION CRITERIA MET")
            print("✅ Testing & Validation implementation successful")
            print("✅ Ready to proceed to Phase 12.6: Deployment & Infrastructure")
        else:
            print("\n⚠️  PHASE 12.5 NEEDS ADDITIONAL WORK")
            print("❌ Some test categories require attention")
            print("📋 Review recommendations for improvement areas")

        return report

    def _generate_recommendations(self, test_results: dict[str, bool]) -> list[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if not test_results.get("environment_validation", True):
            recommendations.append(
                "🔧 Fix environment setup: Ensure API server, Neo4j, and CLI commands are properly configured"
            )

        if not test_results.get("input_validation", True):
            recommendations.append(
                "🛡️ Improve input validation: Add more comprehensive Pydantic models and sanitization"
            )

        if not test_results.get("error_handling", True):
            recommendations.append(
                "🚨 Enhance error handling: Implement better error responses and user-friendly messages"
            )

        if not test_results.get("api_functionality", True):
            recommendations.append(
                "⚙️ Fix API functionality: Debug failing endpoints and ensure proper responses"
            )

        if not test_results.get("progressive_complexity", True):
            recommendations.append(
                "📈 Implement progressive complexity: Ensure all complexity levels have adequate endpoint coverage"
            )

        if not test_results.get("performance_benchmarking", True):
            recommendations.append(
                "🚀 Optimize performance: Reduce response times and improve endpoint efficiency"
            )

        if not test_results.get("cli_api_mapping", True):
            recommendations.append(
                "🔗 Fix CLI-API mapping: Ensure consistency between CLI commands and API endpoints"
            )

        if not recommendations:
            recommendations.append(
                "🎉 Excellent! All test categories passed. Ready for Phase 12.6 deployment."
            )

        return recommendations


async def main():
    """Main test execution function following crawl_mcp.py patterns"""
    print("🚀 Phase 12.5: Testing & Validation")
    print("   Comprehensive Test Suite")
    print("   Following crawl_mcp.py methodology")
    print()

    tester = Phase125ComprehensiveTester()
    results = await tester.run_comprehensive_test_suite()

    # Save results to file
    results_file = "phase_12_5_test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Detailed results saved to: {results_file}")

    # Exit with appropriate code
    exit_code = 0 if results["completion_status"] == "COMPLETED" else 1
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
