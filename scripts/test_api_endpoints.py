#!/usr/bin/env python3
"""
FastAPI Endpoint Testing Script
Phase 11.3: SME Agent Integration & Interfaces

This script provides comprehensive testing of all FastAPI endpoints
with detailed reporting and validation.
"""

import json
from datetime import datetime
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APITester:
    """Comprehensive API testing class for SME Agent FastAPI endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API tester.

        Args:
            base_url: Base URL of the FastAPI server
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Test results storage
        self.test_results: list[dict[str, Any]] = []
        self.session_id = None

    def log_test(self, test_name: str, success: bool, details: dict[str, Any] | None = None):
        """Log test results."""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")

        if not success and details:
            print(f"    Error: {details.get('error', 'Unknown error')}")

    def test_server_connectivity(self) -> bool:
        """Test basic server connectivity."""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200

            details = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "content_type": response.headers.get("content-type", ""),
            }

            if success:
                try:
                    data = response.json()
                    details["response_data"] = data
                except (ValueError, requests.exceptions.JSONDecodeError):
                    details["response_text"] = response.text[:200]
            else:
                details["error"] = f"HTTP {response.status_code}: {response.text[:200]}"

            self.log_test("Server Connectivity", success, details)
            return success

        except requests.exceptions.RequestException as e:
            self.log_test("Server Connectivity", False, {"error": str(e)})
            return False

    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200

            details = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }

            if success:
                try:
                    data = response.json()
                    details["health_status"] = data.get("status")
                    details["agent_status"] = data.get("agent_status", {}).get("initialized", False)
                except (ValueError, requests.exceptions.JSONDecodeError):
                    details["response_text"] = response.text[:200]
            else:
                details["error"] = f"HTTP {response.status_code}: {response.text[:200]}"

            self.log_test("Health Check Endpoint", success, details)
            return success

        except requests.exceptions.RequestException as e:
            self.log_test("Health Check Endpoint", False, {"error": str(e)})
            return False

    def test_chat_endpoint(self) -> bool:
        """Test the standard chat endpoint."""
        try:
            payload = {
                "question": "What is Ignition?",
                "complexity": "standard",
                "context": "I'm learning about industrial automation software.",
            }

            response = self.session.post(f"{self.base_url}/chat", json=payload, timeout=30)

            success = response.status_code == 200

            details = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "payload": payload,
            }

            if success:
                try:
                    data = response.json()
                    details["response_length"] = len(data.get("response", ""))
                    details["confidence"] = data.get("confidence", 0)
                    details["processing_time"] = data.get("processing_time", 0)
                    details["model_used"] = data.get("model_used", "unknown")
                    self.session_id = data.get("session_id")  # Store for later tests
                except (ValueError, requests.exceptions.JSONDecodeError):
                    details["response_text"] = response.text[:200]
            else:
                details["error"] = f"HTTP {response.status_code}: {response.text[:200]}"

            self.log_test("Chat Endpoint", success, details)
            return success

        except requests.exceptions.RequestException as e:
            self.log_test("Chat Endpoint", False, {"error": str(e)})
            return False

    def run_all_tests(self) -> dict[str, Any]:
        """Run all API tests and return results."""
        print("🧪 Starting FastAPI Endpoint Testing")
        print("=" * 50)

        # Define test sequence
        tests = [
            ("Server Connectivity", self.test_server_connectivity),
            ("Health Check", self.test_health_endpoint),
            ("Chat Endpoint", self.test_chat_endpoint),
        ]

        # Run tests
        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n📋 Testing {test_name}...")
            try:
                result = test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")

        # Generate summary
        success_rate = (passed / total) * 100

        summary = {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": success_rate,
            "server_url": self.base_url,
            "test_timestamp": datetime.now().isoformat(),
            "detailed_results": self.test_results,
        }

        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"  Total Tests: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {total - passed}")
        print(f"  Success Rate: {success_rate:.1f}%")

        if passed == total:
            print("\n🎉 All tests passed! FastAPI server is working correctly.")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed. Please check the server and try again.")

        return summary


def main():
    """Main function to run API tests."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test SME Agent FastAPI endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test local server
  python scripts/test_api_endpoints.py

  # Test custom server
  python scripts/test_api_endpoints.py --url http://localhost:8080

  # Save results to file
  python scripts/test_api_endpoints.py --output test_results.json
        """,
    )

    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="FastAPI server URL (default: http://localhost:8000)",
    )

    parser.add_argument("--output", help="Save test results to JSON file")

    args = parser.parse_args()

    # Run tests
    tester = APITester(args.url)
    results = tester.run_all_tests()

    # Save results if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Test results saved to: {args.output}")

    # Exit with appropriate code
    exit_code = 0 if results["failed_tests"] == 0 else 1
    return exit_code


if __name__ == "__main__":
    import sys

    sys.exit(main())
