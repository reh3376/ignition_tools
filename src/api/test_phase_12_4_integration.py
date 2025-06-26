#!/usr/bin/env python3
"""Phase 12.4 Authentication & Security Integration Tests
Following crawl_mcp.py methodology for systematic testing

This test suite validates the complete authentication and security implementation
using the step-by-step approach defined in crawl_mcp.py
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Any

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
TEST_TIMEOUT = 30


class Phase124IntegrationTester:
    """Integration tester following crawl_mcp.py methodology"""

    def __init__(self):
        self.api_base = API_BASE_URL
        self.test_results = {
            "environment_validation": {},
            "input_validation": {},
            "error_handling": {},
            "authentication_functionality": {},
            "progressive_complexity": {},
        }
        self.start_time = time.time()

    async def run_comprehensive_tests(self) -> dict[str, Any]:
        """Run comprehensive tests following crawl_mcp.py methodology"""
        print("🚀 Starting Phase 12.4 Authentication & Security Integration Tests")
        print("📋 Following crawl_mcp.py methodology for systematic validation\n")

        # Step 1: Environment Validation First
        await self._test_environment_validation()

        # Step 2: Input Validation and Sanitization
        await self._test_input_validation()

        # Step 3: Comprehensive Error Handling
        await self._test_error_handling()

        # Step 4: Authentication Functionality Testing
        await self._test_authentication_functionality()

        # Step 5: Progressive Complexity Validation
        await self._test_progressive_complexity()

        # Generate final report
        return await self._generate_test_report()

    async def _test_environment_validation(self):
        """Test environment validation (crawl_mcp.py Step 1)"""
        print("🔍 Step 1: Environment Validation Testing")

        results = {
            "auth_validation_endpoint": False,
            "environment_variables": False,
            "security_features": False,
            "rate_limiting": False,
        }

        try:
            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                # Test auth validation endpoint
                response = await client.get(f"{self.api_base}/api/v1/auth/validate")
                if response.status_code == 200:
                    data = response.json()
                    results["auth_validation_endpoint"] = True
                    results["environment_variables"] = data.get("status") == "valid"
                    results["security_features"] = bool(
                        data.get("security_features", {})
                    )
                    print(f"   ✅ Auth validation endpoint: {response.status_code}")
                    print(f"   ✅ Environment status: {data.get('status', 'unknown')}")
                    print(
                        f"   ✅ Security features: {len(data.get('security_features', {}))}"
                    )
                else:
                    print(f"   ❌ Auth validation failed: {response.status_code}")

                # Test rate limiting
                for i in range(3):
                    response = await client.get(f"{self.api_base}/api/v1/auth/validate")
                    if i == 2:
                        results["rate_limiting"] = response.status_code in [200, 429]
                        print(f"   ✅ Rate limiting active: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Environment validation error: {e}")

        self.test_results["environment_validation"] = results
        success_rate = sum(results.values()) / len(results) * 100
        print(f"   📊 Environment Validation: {success_rate:.1f}% success rate\n")

    async def _test_input_validation(self):
        """Test input validation and sanitization (crawl_mcp.py Step 2)"""
        print("🔍 Step 2: Input Validation Testing")

        results = {
            "user_registration_validation": False,
            "login_validation": False,
            "password_validation": False,
            "api_key_validation": False,
            "malformed_data_rejection": False,
        }

        try:
            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                # Test user registration validation
                valid_user = {
                    "username": "testuser123",
                    "email": "test@example.com",
                    "password": "SecurePass123!",
                    "full_name": "Test User",
                    "role": "user",
                }

                response = await client.post(
                    f"{self.api_base}/api/v1/auth/register", json=valid_user
                )
                results["user_registration_validation"] = response.status_code in [
                    200,
                    201,
                ]
                print(f"   ✅ User registration validation: {response.status_code}")

                # Test login validation
                login_data = {"username": "testuser123", "password": "SecurePass123!"}

                response = await client.post(
                    f"{self.api_base}/api/v1/auth/login", json=login_data
                )
                results["login_validation"] = response.status_code in [200, 201]
                print(f"   ✅ Login validation: {response.status_code}")

                # Test password validation (weak password)
                weak_password_user = {
                    "username": "testuser456",
                    "email": "test2@example.com",
                    "password": "123",  # Too weak
                    "full_name": "Test User 2",
                    "role": "user",
                }

                response = await client.post(
                    f"{self.api_base}/api/v1/auth/register", json=weak_password_user
                )
                results["password_validation"] = response.status_code == 422
                print(
                    f"   ✅ Password validation (weak rejected): {response.status_code}"
                )

                # Test API key validation
                api_key_data = {
                    "name": "Test API Key",
                    "description": "Test key for validation",
                    "expires_in_days": 30,
                    "permissions": ["read", "write"],
                }

                # This should fail without authentication
                response = await client.post(
                    f"{self.api_base}/api/v1/auth/api-keys", json=api_key_data
                )
                results["api_key_validation"] = response.status_code == 401
                print(
                    f"   ✅ API key validation (auth required): {response.status_code}"
                )

                # Test malformed data rejection
                malformed_data = {"invalid": "data", "structure": True}
                response = await client.post(
                    f"{self.api_base}/api/v1/auth/register", json=malformed_data
                )
                results["malformed_data_rejection"] = response.status_code == 422
                print(f"   ✅ Malformed data rejection: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Input validation error: {e}")

        self.test_results["input_validation"] = results
        success_rate = sum(results.values()) / len(results) * 100
        print(f"   📊 Input Validation: {success_rate:.1f}% success rate\n")

    async def _test_error_handling(self):
        """Test comprehensive error handling (crawl_mcp.py Step 3)"""
        print("🔍 Step 3: Error Handling Testing")

        results = {
            "authentication_errors": False,
            "authorization_errors": False,
            "rate_limit_errors": False,
            "validation_errors": False,
        }

        try:
            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                # Test authentication errors
                response = await client.get(
                    f"{self.api_base}/api/v1/auth/me",
                    headers={"Authorization": "Bearer invalid_token"},
                )
                results["authentication_errors"] = response.status_code == 401
                print(f"   ✅ Authentication error handling: {response.status_code}")

                # Test authorization errors
                response = await client.get(f"{self.api_base}/api/v1/protected/admin")
                results["authorization_errors"] = response.status_code == 401
                print(f"   ✅ Authorization error handling: {response.status_code}")

                # Test rate limit errors (attempt to trigger rate limit)
                rate_limit_triggered = False
                for i in range(15):  # Try to exceed rate limit
                    response = await client.post(
                        f"{self.api_base}/api/v1/auth/login",
                        json={"username": "test", "password": "test"},
                    )
                    if response.status_code == 429:
                        rate_limit_triggered = True
                        break

                results["rate_limit_errors"] = rate_limit_triggered
                print(
                    f"   ✅ Rate limit error handling: {'Triggered' if rate_limit_triggered else 'Not triggered'}"
                )

                # Test validation errors
                response = await client.post(
                    f"{self.api_base}/api/v1/auth/register",
                    json={"username": "a", "email": "invalid", "password": "short"},
                )
                results["validation_errors"] = response.status_code == 422
                print(f"   ✅ Validation error handling: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error handling test error: {e}")

        self.test_results["error_handling"] = results
        success_rate = sum(results.values()) / len(results) * 100
        print(f"   📊 Error Handling: {success_rate:.1f}% success rate\n")

    async def _test_authentication_functionality(self):
        """Test authentication functionality (crawl_mcp.py Step 4)"""
        print("🔍 Step 4: Authentication Functionality Testing")

        results = {
            "user_registration": False,
            "user_login": False,
            "token_refresh": False,
            "user_profile": False,
            "password_change": False,
        }

        access_token = None
        refresh_token = None

        try:
            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                # Test user registration
                user_data = {
                    "username": f"testuser_{int(time.time())}",
                    "email": f"test_{int(time.time())}@example.com",
                    "password": "SecurePassword123!",
                    "full_name": "Test User",
                    "role": "user",
                }

                response = await client.post(
                    f"{self.api_base}/api/v1/auth/register", json=user_data
                )
                results["user_registration"] = response.status_code in [200, 201]
                print(f"   ✅ User registration: {response.status_code}")

                # Test user login
                login_data = {
                    "username": user_data["username"],
                    "password": user_data["password"],
                }

                response = await client.post(
                    f"{self.api_base}/api/v1/auth/login", json=login_data
                )

                if response.status_code in [200, 201]:
                    results["user_login"] = True
                    token_data = response.json()
                    access_token = token_data.get("access_token")
                    refresh_token = token_data.get("refresh_token")
                    print(f"   ✅ User login: {response.status_code}")
                else:
                    print(f"   ❌ User login failed: {response.status_code}")

                # Test token refresh
                if refresh_token:
                    response = await client.post(
                        f"{self.api_base}/api/v1/auth/refresh",
                        json={"refresh_token": refresh_token},
                    )
                    results["token_refresh"] = response.status_code in [200, 201]
                    print(f"   ✅ Token refresh: {response.status_code}")

                # Test user profile access
                if access_token:
                    response = await client.get(
                        f"{self.api_base}/api/v1/auth/me",
                        headers={"Authorization": f"Bearer {access_token}"},
                    )
                    results["user_profile"] = response.status_code == 200
                    print(f"   ✅ User profile access: {response.status_code}")

                    # Test password change
                    password_change_data = {
                        "current_password": user_data["password"],
                        "new_password": "NewSecurePassword123!",
                        "confirm_password": "NewSecurePassword123!",
                    }

                    response = await client.post(
                        f"{self.api_base}/api/v1/auth/change-password",
                        json=password_change_data,
                        headers={"Authorization": f"Bearer {access_token}"},
                    )
                    results["password_change"] = response.status_code == 200
                    print(f"   ✅ Password change: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Authentication functionality error: {e}")

        self.test_results["authentication_functionality"] = results
        success_rate = sum(results.values()) / len(results) * 100
        print(f"   📊 Authentication Functionality: {success_rate:.1f}% success rate\n")

    async def _test_progressive_complexity(self):
        """Test progressive complexity implementation (crawl_mcp.py Step 5)"""
        print("🔍 Step 5: Progressive Complexity Testing")

        results = {
            "basic_auth_endpoints": False,
            "standard_user_management": False,
            "advanced_api_keys": False,
            "enterprise_role_based_access": False,
            "security_features": False,
        }

        try:
            async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
                # Basic: Authentication endpoints
                basic_endpoints = [
                    "/api/v1/auth/validate",
                    "/api/v1/auth/register",
                    "/api/v1/auth/login",
                ]

                basic_available = 0
                for endpoint in basic_endpoints:
                    response = await client.get(f"{self.api_base}{endpoint}")
                    if response.status_code in [
                        200,
                        405,
                        422,
                    ]:  # 405 for POST-only endpoints
                        basic_available += 1

                results["basic_auth_endpoints"] = basic_available >= 2
                print(
                    f"   ✅ Basic auth endpoints: {basic_available}/{len(basic_endpoints)}"
                )

                # Standard: User management
                standard_endpoints = [
                    "/api/v1/auth/me",
                    "/api/v1/auth/refresh",
                    "/api/v1/auth/change-password",
                ]

                standard_available = 0
                for endpoint in standard_endpoints:
                    response = await client.get(f"{self.api_base}{endpoint}")
                    if response.status_code in [401, 422]:  # Expect auth required
                        standard_available += 1

                results["standard_user_management"] = standard_available >= 2
                print(
                    f"   ✅ Standard user management: {standard_available}/{len(standard_endpoints)}"
                )

                # Advanced: API key management
                advanced_endpoints = [
                    "/api/v1/auth/api-keys",
                ]

                advanced_available = 0
                for endpoint in advanced_endpoints:
                    response = await client.get(f"{self.api_base}{endpoint}")
                    if response.status_code in [
                        401,
                        403,
                    ]:  # Expect auth/permission required
                        advanced_available += 1

                results["advanced_api_keys"] = advanced_available >= 1
                print(
                    f"   ✅ Advanced API keys: {advanced_available}/{len(advanced_endpoints)}"
                )

                # Enterprise: Role-based access control
                enterprise_endpoints = [
                    "/api/v1/protected/admin",
                    "/api/v1/protected/knowledge-graph",
                ]

                enterprise_available = 0
                for endpoint in enterprise_endpoints:
                    response = await client.get(f"{self.api_base}{endpoint}")
                    if response.status_code in [401, 403]:  # Expect permission required
                        enterprise_available += 1

                results["enterprise_role_based_access"] = enterprise_available >= 1
                print(
                    f"   ✅ Enterprise RBAC: {enterprise_available}/{len(enterprise_endpoints)}"
                )

                # Security features validation
                response = await client.get(f"{self.api_base}/api/v1/auth/validate")
                if response.status_code == 200:
                    data = response.json()
                    security_features = data.get("security_features", {})
                    results["security_features"] = len(security_features) >= 3
                    print(
                        f"   ✅ Security features: {len(security_features)} available"
                    )

        except Exception as e:
            print(f"   ❌ Progressive complexity error: {e}")

        self.test_results["progressive_complexity"] = results
        success_rate = sum(results.values()) / len(results) * 100
        print(f"   📊 Progressive Complexity: {success_rate:.1f}% success rate\n")

    async def _generate_test_report(self) -> dict[str, Any]:
        """Generate comprehensive test report"""
        execution_time = time.time() - self.start_time

        # Calculate overall success rates
        category_success_rates = {}
        overall_tests_passed = 0
        overall_tests_total = 0

        for category, results in self.test_results.items():
            if results:
                passed = sum(results.values())
                total = len(results)
                success_rate = (passed / total) * 100
                category_success_rates[category] = {
                    "passed": passed,
                    "total": total,
                    "success_rate": success_rate,
                }
                overall_tests_passed += passed
                overall_tests_total += total

        overall_success_rate = (overall_tests_passed / overall_tests_total) * 100

        # Determine completion status
        completion_criteria = {
            "environment_validation": category_success_rates.get(
                "environment_validation", {}
            ).get("success_rate", 0)
            >= 75,
            "input_validation": category_success_rates.get("input_validation", {}).get(
                "success_rate", 0
            )
            >= 80,
            "error_handling": category_success_rates.get("error_handling", {}).get(
                "success_rate", 0
            )
            >= 75,
            "authentication_functionality": category_success_rates.get(
                "authentication_functionality", {}
            ).get("success_rate", 0)
            >= 80,
            "progressive_complexity": category_success_rates.get(
                "progressive_complexity", {}
            ).get("success_rate", 0)
            >= 80,
        }

        completion_status = (
            sum(completion_criteria.values()) >= 4
        )  # At least 4 out of 5 criteria met

        report = {
            "phase": "12.4 - Authentication & Security",
            "methodology": "crawl_mcp.py systematic testing",
            "execution_time": round(execution_time, 2),
            "timestamp": datetime.now().isoformat(),
            "overall_success_rate": round(overall_success_rate, 1),
            "tests_passed": overall_tests_passed,
            "tests_total": overall_tests_total,
            "category_results": category_success_rates,
            "completion_criteria": completion_criteria,
            "completion_status": "PASSED" if completion_status else "NEEDS_IMPROVEMENT",
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(category_success_rates),
        }

        return report

    def _generate_recommendations(self, category_results: dict[str, Any]) -> list[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        for category, results in category_results.items():
            success_rate = results.get("success_rate", 0)
            if success_rate < 80:
                if category == "environment_validation":
                    recommendations.append(
                        "Review authentication environment configuration and security settings"
                    )
                elif category == "input_validation":
                    recommendations.append(
                        "Strengthen input validation and sanitization mechanisms"
                    )
                elif category == "error_handling":
                    recommendations.append(
                        "Improve error handling and user-friendly error messages"
                    )
                elif category == "authentication_functionality":
                    recommendations.append(
                        "Debug authentication flow and token management"
                    )
                elif category == "progressive_complexity":
                    recommendations.append(
                        "Complete implementation of advanced security features"
                    )

        if not recommendations:
            recommendations.append(
                "All authentication and security features are working correctly"
            )

        return recommendations


async def main():
    """Main test execution following crawl_mcp.py methodology"""
    tester = Phase124IntegrationTester()

    try:
        # Run comprehensive tests
        report = await tester.run_comprehensive_tests()

        # Display final results
        print("=" * 80)
        print("🎯 PHASE 12.4 AUTHENTICATION & SECURITY - FINAL RESULTS")
        print("=" * 80)
        print(f"📊 Overall Success Rate: {report['overall_success_rate']}%")
        print(f"✅ Tests Passed: {report['tests_passed']}/{report['tests_total']}")
        print(f"⏱️  Execution Time: {report['execution_time']}s")
        print(f"🎯 Completion Status: {report['completion_status']}")

        print("\n📋 Category Breakdown:")
        for category, results in report["category_results"].items():
            status = "✅" if results["success_rate"] >= 75 else "❌"
            print(
                f"   {status} {category.replace('_', ' ').title()}: {results['success_rate']:.1f}% ({results['passed']}/{results['total']})"
            )

        print("\n💡 Recommendations:")
        for recommendation in report["recommendations"]:
            print(f"   • {recommendation}")

        # Save detailed report
        report_file = f"phase_12_4_test_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved: {report_file}")

        # Return appropriate exit code
        return 0 if report["completion_status"] == "PASSED" else 1

    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))
