#!/usr/bin/env python3
"""Phase 11.3 Implementation Test Script.

This script tests the multi-interface deployment implementation
following the crawl_mcp.py methodology.
"""

import subprocess
import sys
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing module imports...")

    try:
        # Test SME Agent module
        from src.ignition.modules.sme_agent.sme_agent_module import SMEAgentModule

        print("✅ SME Agent module imported successfully")

        # Test web interface
        from src.ignition.modules.sme_agent.web_interface import app

        print("✅ FastAPI web interface imported successfully")

        # Test Streamlit interface
        streamlit_path = Path("src/ignition/modules/sme_agent/streamlit_interface.py")
        if streamlit_path.exists():
            print("✅ Streamlit interface file exists")
        else:
            print("❌ Streamlit interface file not found")
            return False

        # Test CLI commands
        from src.ignition.modules.sme_agent.cli.infrastructure_commands import (
            infrastructure_commands,
        )

        print("✅ Infrastructure CLI commands imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_sme_agent_basic():
    """Test basic SME Agent functionality."""
    print("\n🧪 Testing SME Agent basic functionality...")

    try:
        from src.ignition.modules.sme_agent.sme_agent_module import SMEAgentModule

        # Test environment validation
        agent = SMEAgentModule()
        validation_result = agent.validate_environment()

        if validation_result.get("valid"):
            print("✅ SME Agent environment validation passed")
        else:
            print(f"⚠️ SME Agent environment validation issues: {validation_result.get('errors', [])}")

        # Test status check
        status = agent.get_status()
        if status.get("initialized"):
            print("✅ SME Agent status check passed")
        else:
            print("⚠️ SME Agent not fully initialized")

        return True

    except Exception as e:
        print(f"❌ SME Agent test failed: {e}")
        return False


def test_fastapi_endpoints():
    """Test FastAPI endpoint definitions."""
    print("\n🧪 Testing FastAPI endpoint definitions...")

    try:
        from src.ignition.modules.sme_agent.web_interface import app

        # Get all routes
        routes = [route.path for route in app.routes if hasattr(route, "path")]

        expected_endpoints = [
            "/",
            "/health",
            "/chat",
            "/chat/stream",
            "/analyze",
            "/status",
        ]

        for endpoint in expected_endpoints:
            if endpoint in routes:
                print(f"✅ Endpoint {endpoint} defined")
            else:
                print(f"❌ Endpoint {endpoint} missing")
                return False

        print("✅ All expected FastAPI endpoints are defined")
        return True

    except Exception as e:
        print(f"❌ FastAPI endpoint test failed: {e}")
        return False


def test_cli_commands():
    """Test CLI command availability."""
    print("\n🧪 Testing CLI command availability...")

    try:
        # Test if ign command is available
        result = subprocess.run(
            ["python", "-m", "src.ignition.cli", "module", "sme", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ SME CLI commands available")

            # Check for infrastructure commands
            if "infrastructure" in result.stdout:
                print("✅ Infrastructure commands available")
            else:
                print("⚠️ Infrastructure commands may not be available")

            return True
        else:
            print(f"❌ CLI command test failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️ CLI command test timed out")
        return False
    except Exception as e:
        print(f"❌ CLI command test failed: {e}")
        return False


def test_dependencies():
    """Test that required dependencies are available."""
    print("\n🧪 Testing required dependencies...")

    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("streamlit", "Streamlit"),
        ("pydantic", "Pydantic"),
        ("click", "Click"),
        ("rich", "Rich"),
    ]

    all_available = True

    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {display_name} available")
        except ImportError:
            print(f"❌ {display_name} not available")
            all_available = False

    return all_available


def main():
    """Run all tests."""
    print("🚀 Phase 11.3 Implementation Test Suite")
    print("=" * 50)

    tests = [
        ("Dependencies", test_dependencies),
        ("Module Imports", test_imports),
        ("SME Agent Basic", test_sme_agent_basic),
        ("FastAPI Endpoints", test_fastapi_endpoints),
        ("CLI Commands", test_cli_commands),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Phase 11.3 implementation is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
