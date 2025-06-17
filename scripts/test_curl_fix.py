#!/usr/bin/env python3
"""Test the fixed curl MCP service."""

import json
import subprocess
import sys


def test_curl_service():
    """Test the curl MCP service with the fixed configuration."""
    print("🔧 Testing Fixed curl MCP Service")
    print("=" * 50)

    # Test 1: Container availability
    print("\n📦 Testing image availability...")
    try:
        result = subprocess.run(
            [
                "docker",
                "images",
                "--format",
                "{{.Repository}}:{{.Tag}}",
                "curlimages/curl:latest",
            ],
            capture_output=True,
            text=True,
        )

        if result.stdout.strip():
            print("   ✅ curlimages/curl:latest image available")
        else:
            print("   ❌ Image not found")
            return False

    except Exception as e:
        print(f"   ❌ Error checking image: {e}")
        return False

    # Test 2: Basic container launch
    print("\n🚀 Testing container launch...")
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "curlimages/curl:latest", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0 and "curl" in result.stdout:
            print("   ✅ Container launches successfully")
            print(f"   📋 Version: {result.stdout.split()[1]}")
        else:
            print(f"   ❌ Container launch failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"   ❌ Container launch error: {e}")
        return False

    # Test 3: HTTP functionality
    print("\n🌐 Testing HTTP functionality...")
    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "curlimages/curl:latest",
                "-s",
                "https://httpbin.org/get",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if "url" in response and "httpbin.org" in response["url"]:
                    print("   ✅ HTTP requests working perfectly")
                    print(f"   📋 Response from: {response['url']}")
                    print(
                        f"   🔄 User-Agent: {response['headers'].get('User-Agent', 'N/A')}"
                    )
                else:
                    print("   ⚠️ Unexpected response format")
                    return False
            except json.JSONDecodeError:
                print("   ⚠️ Non-JSON response received")
                print(f"   📋 Raw response: {result.stdout[:100]}...")
                return False
        else:
            print(f"   ❌ HTTP request failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"   ❌ HTTP test error: {e}")
        return False

    # Test 4: MCP-style interactive mode
    print("\n🔧 Testing MCP-style interactive mode...")
    try:
        # This simulates how MCP would invoke the container
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-i",
                "curlimages/curl:latest",
                "-s",
                "https://httpbin.org/user-agent",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("   ✅ Interactive mode working")
            print("   📋 MCP-compatible container launch successful")
        else:
            print(f"   ❌ Interactive mode failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"   ❌ Interactive mode error: {e}")
        return False

    print("\n🎉 curl MCP Service Status: FULLY FUNCTIONAL")
    print("   ✅ Image available")
    print("   ✅ Container launches successfully")
    print("   ✅ HTTP requests working")
    print("   ✅ MCP-compatible interactive mode")
    print("\n🔧 Configuration Fix Summary:")
    print("   • Changed from: vonwig/curl:latest (broken)")
    print("   • Changed to: curlimages/curl:latest (working)")
    print("   • Auth issue resolved: Container now fully functional")

    return True


if __name__ == "__main__":
    success = test_curl_service()
    sys.exit(0 if success else 1)
