#!/usr/bin/env python3
"""
Uvicorn API Testing Demo Script
Phase 11.3: SME Agent Integration & Interfaces

This script demonstrates how to use uvicorn for API testing and documentation
with the SME Agent FastAPI server.
"""

import json
import subprocess
import sys
import time

import requests


class UvicornAPIDemo:
    """Demo class for uvicorn API testing and documentation."""

    def __init__(self):
        """Initialize the demo."""
        self.server_url = "http://localhost:8000"
        self.server_process = None

    def print_section(self, title: str):
        """Print a formatted section header."""
        print("\n" + "=" * 60)
        print(f"🚀 {title}")
        print("=" * 60)

    def print_step(self, step: str):
        """Print a formatted step."""
        print(f"\n📋 {step}")
        print("-" * 40)

    def start_server(self, dev_mode: bool = True) -> bool:
        """Start the uvicorn server."""
        self.print_step("Starting Uvicorn Server")

        try:
            if dev_mode:
                cmd = [
                    sys.executable,
                    "scripts/start_api_server.py",
                    "--dev",
                    "--port",
                    "8000",
                ]
                print("Command: python scripts/start_api_server.py --dev --port 8000")
            else:
                cmd = [
                    "uvicorn",
                    "src.ignition.modules.sme_agent.web_interface:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                    "--reload",
                ]
                print(
                    "Command: uvicorn src.ignition.modules.sme_agent.web_interface:app "
                    "--host 127.0.0.1 --port 8000 --reload"
                )

            print("Starting server in background...")
            self.server_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Wait for server to start
            print("Waiting for server to initialize...")
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Server started successfully after {i + 1} seconds")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    print(f"   Waiting... ({i + 1}/30)")

            print("❌ Server failed to start within 30 seconds")
            return False

        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False

    def stop_server(self):
        """Stop the uvicorn server."""
        if self.server_process:
            self.print_step("Stopping Server")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ Server stopped")

    def demo_api_documentation(self):
        """Demonstrate API documentation features."""
        self.print_section("API Documentation with Uvicorn")

        docs_endpoints = [
            ("/docs", "Swagger UI - Interactive API documentation"),
            ("/redoc", "ReDoc - Alternative API documentation"),
            ("/openapi.json", "OpenAPI JSON - Machine-readable API schema"),
        ]

        for endpoint, description in docs_endpoints:
            self.print_step(f"Testing {description}")
            try:
                response = requests.get(f"{self.server_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {description}")
                    print(f"   URL: {self.server_url}{endpoint}")
                    if endpoint == "/openapi.json":
                        data = response.json()
                        print(
                            f"   API Title: {data.get('info', {}).get('title', 'N/A')}"
                        )
                        print(
                            f"   API Version: {data.get('info', {}).get('version', 'N/A')}"
                        )
                        print(f"   Endpoints: {len(data.get('paths', {}))}")
                else:
                    print(f"❌ Failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")

        print("\n🌐 Open these URLs in your browser:")
        for endpoint, description in docs_endpoints:
            print(f"   • {self.server_url}{endpoint} - {description}")

    def demo_basic_testing(self):
        """Demonstrate basic API testing."""
        self.print_section("Basic API Testing")

        # Health check
        self.print_step("Health Check Endpoint")
        try:
            response = requests.get(f"{self.server_url}/health", timeout=10)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed")
                print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Health check failed: {response.text}")
        except Exception as e:
            print(f"❌ Health check error: {e}")

        # Status endpoint
        self.print_step("Status Endpoint")
        try:
            response = requests.get(f"{self.server_url}/status", timeout=15)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("✅ Status check passed")
                print(f"System Status: {data.get('status', 'unknown')}")
                print(f"Initialized: {data.get('initialized', False)}")
            else:
                print(f"❌ Status check failed: {response.text}")
        except Exception as e:
            print(f"❌ Status check error: {e}")

    def demo_chat_testing(self):
        """Demonstrate chat endpoint testing."""
        self.print_section("Chat Endpoint Testing")

        # Basic chat
        self.print_step("Basic Chat Request")
        payload = {
            "question": "What is Ignition SCADA?",
            "complexity": "standard",
            "context": "Learning about industrial automation",
        }

        try:
            response = requests.post(
                f"{self.server_url}/chat", json=payload, timeout=30
            )
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("✅ Chat request successful")
                print(f"Response length: {len(data.get('response', ''))}")
                print(f"Confidence: {data.get('confidence', 'N/A')}")
                print(f"Processing time: {data.get('processing_time', 'N/A')}s")
                print(f"Session ID: {data.get('session_id', 'N/A')}")
            else:
                print(f"❌ Chat request failed: {response.text}")
        except Exception as e:
            print(f"❌ Chat request error: {e}")

    def demo_input_validation(self):
        """Demonstrate input validation testing."""
        self.print_section("Input Validation Testing")

        test_cases = [
            {
                "name": "Empty Question",
                "payload": {"question": "", "complexity": "standard"},
                "expected": 422,
            },
            {
                "name": "Invalid Complexity",
                "payload": {"question": "Test", "complexity": "invalid"},
                "expected": 422,
            },
            {
                "name": "Valid Request",
                "payload": {"question": "Test question", "complexity": "basic"},
                "expected": 200,
            },
        ]

        for test_case in test_cases:
            self.print_step(f"Testing {test_case['name']}")
            try:
                response = requests.post(
                    f"{self.server_url}/chat", json=test_case["payload"], timeout=10
                )
                expected_status = test_case["expected"]
                actual_status = response.status_code

                if actual_status == expected_status:
                    print(f"✅ Expected status {expected_status}, got {actual_status}")
                else:
                    print(f"❌ Expected status {expected_status}, got {actual_status}")

                if actual_status == 422:
                    try:
                        error_data = response.json()
                        print(
                            f"   Validation error: {error_data.get('detail', 'Unknown')}"
                        )
                    except (ValueError, requests.exceptions.JSONDecodeError):
                        print(f"   Raw error: {response.text[:100]}")

            except Exception as e:
                print(f"❌ Test error: {e}")

    def demo_automated_testing(self):
        """Demonstrate automated testing script."""
        self.print_section("Automated Testing with Test Script")

        self.print_step("Running Comprehensive Test Suite")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/test_api_endpoints.py",
                    "--url",
                    self.server_url,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print("Test output:")
                print(result.stdout)
            if result.stderr:
                print("Error output:")
                print(result.stderr)

        except subprocess.TimeoutExpired:
            print("❌ Test script timed out")
        except Exception as e:
            print(f"❌ Failed to run test script: {e}")

    def demo_curl_commands(self):
        """Demonstrate equivalent curl commands."""
        self.print_section("Equivalent curl Commands")

        curl_examples = [
            {
                "description": "Health Check",
                "command": f"curl -X GET {self.server_url}/health",
            },
            {
                "description": "Basic Chat",
                "command": f"""curl -X POST {self.server_url}/chat \\
     -H "Content-Type: application/json" \\
     -d '{{"question": "What is Ignition?", "complexity": "standard"}}'""",
            },
            {
                "description": "File Analysis",
                "command": f"""curl -X POST {self.server_url}/analyze \\
     -H "Content-Type: application/json" \\
     -d '{{"content": "def hello(): pass", "filename": "test.py"}}'""",
            },
            {
                "description": "Get API Documentation",
                "command": f"curl -X GET {self.server_url}/openapi.json",
            },
        ]

        for example in curl_examples:
            self.print_step(example["description"])
            print("Command:")
            print(f"  {example['command']}")

    def run_demo(self):
        """Run the complete uvicorn API testing demo."""
        print("🎯 Uvicorn API Testing and Documentation Demo")
        print("Phase 11.3: SME Agent Integration & Interfaces")

        try:
            # Start server
            if not self.start_server(dev_mode=True):
                print("❌ Failed to start server. Exiting demo.")
                return

            # Run demo sections
            self.demo_api_documentation()
            self.demo_basic_testing()
            self.demo_chat_testing()
            self.demo_input_validation()
            self.demo_automated_testing()
            self.demo_curl_commands()

            # Final summary
            self.print_section("Demo Complete")
            print("✅ Uvicorn API testing demo completed successfully!")
            print("\n📚 Key Takeaways:")
            print("   • Uvicorn provides excellent development server with auto-reload")
            print("   • FastAPI generates interactive documentation automatically")
            print("   • Comprehensive testing can be automated with scripts")
            print("   • Multiple testing approaches: Python requests, curl, browser")
            print("   • Production deployment supports multiple workers and SSL")

            print("\n🔗 Useful Resources:")
            print(f"   • API Documentation: {self.server_url}/docs")
            print(f"   • Alternative Docs: {self.server_url}/redoc")
            print(f"   • OpenAPI Schema: {self.server_url}/openapi.json")
            print("   • Testing Script: python scripts/test_api_endpoints.py")
            print("   • Startup Script: python scripts/start_api_server.py")

        except KeyboardInterrupt:
            print("\n⚠️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
        finally:
            self.stop_server()


def main():
    """Main function to run the demo."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Uvicorn API Testing Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This demo shows how to use uvicorn for API testing and documentation.

Examples:
  # Run full demo
  python scripts/demo_uvicorn_testing.py

  # Run demo with production server
  python scripts/demo_uvicorn_testing.py --production
        """,
    )

    parser.add_argument(
        "--production",
        action="store_true",
        help="Use production server mode instead of development",
    )

    # Parse args but don't use them in this simple demo
    parser.parse_args()

    demo = UvicornAPIDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()
