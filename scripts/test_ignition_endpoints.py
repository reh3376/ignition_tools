#!/usr/bin/env python3
"""
Test various Ignition Gateway endpoints to find available ones.
Configure your gateway details below or use environment variables.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import requests
from ignition.gateway.client import IgnitionGatewayClient
from ignition.gateway.config import GatewayConfig
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise
logger = logging.getLogger(__name__)


def get_gateway_config():
    """Get gateway configuration from user input."""
    print("🔧 Configure Gateway for Endpoint Testing")
    print("=" * 50)

    host = input("Gateway host: ").strip()
    if not host:
        print("Host is required!")
        return None

    port = input("Gateway port [8088]: ").strip() or "8088"
    try:
        port = int(port)
    except ValueError:
        print("Invalid port, using 8088")
        port = 8088

    use_https = input("Use HTTPS? (y/n) [n]: ").strip().lower() in [
        "y",
        "yes",
        "1",
        "true",
    ]
    username = input("Username [admin]: ").strip() or "admin"
    password = input("Password [password]: ").strip() or "password"

    verify_ssl = True
    if use_https:
        verify_ssl = input(
            "Verify SSL certificates? (y/n) [y]: "
        ).strip().lower() not in ["n", "no", "0", "false"]

    return {
        "host": host,
        "port": port,
        "use_https": use_https,
        "username": username,
        "password": password,
        "verify_ssl": verify_ssl,
    }


def test_ignition_endpoints(gateway_config):
    """Test various common Ignition endpoints."""
    host = gateway_config["host"]
    port = gateway_config["port"]
    use_https = gateway_config["use_https"]
    username = gateway_config["username"]
    password = gateway_config["password"]
    verify_ssl = gateway_config["verify_ssl"]

    base_url = f"{'https' if use_https else 'http'}://{host}:{port}"

    print("🔍 Testing Ignition Gateway Endpoints")
    print(f"Gateway: {base_url}")
    print("=" * 50)

    # Common Ignition endpoints to test
    endpoints = [
        "/",  # Root page
        "/main",  # Main gateway page
        "/data",  # Data endpoints
        "/system",  # System endpoints
        "/main/web/config",  # Configuration
        "/main/web/status",  # Status page
        "/main/system/webdev",  # WebDev module
        "/main/data/perspective/status",  # Perspective status
        "/main/data/vision/status",  # Vision status
        "/main/system/console",  # System console
        "/data/perspective/sessions",  # Perspective sessions
        "/system/gwinfo",  # Gateway info
        "/status.json",  # JSON status
        "/main/system/console/status",  # Console status
        "/main/web/status/connections",  # Connection status
    ]

    # Setup session with auth
    session = requests.Session()
    session.auth = HTTPBasicAuth(username, password)
    session.verify = verify_ssl
    session.timeout = 10

    # Disable SSL warnings if needed
    if not verify_ssl:
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    successful_endpoints = []

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"

        try:
            response = session.get(url)
            status = response.status_code

            if status == 200:
                icon = "✅"
                successful_endpoints.append(endpoint)
                content_type = response.headers.get("content-type", "unknown")
                content_length = len(response.content)
                print(
                    f"{icon} {endpoint:<30} | HTTP {status} | {content_type} | {content_length} bytes"
                )

            elif status == 401:
                icon = "🔐"
                print(f"{icon} {endpoint:<30} | HTTP {status} | Auth required")

            elif status == 403:
                icon = "🚫"
                print(f"{icon} {endpoint:<30} | HTTP {status} | Forbidden")

            elif status == 404:
                icon = "❌"
                print(f"{icon} {endpoint:<30} | HTTP {status} | Not found")

            else:
                icon = "⚠️"
                print(f"{icon} {endpoint:<30} | HTTP {status}")

        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint:<30} | Timeout")

        except requests.exceptions.ConnectionError:
            print(f"🔌 {endpoint:<30} | Connection error")

        except Exception as e:
            print(f"❓ {endpoint:<30} | Error: {type(e).__name__}")

    # Summary
    print("\n" + "=" * 50)
    print(f"✅ Found {len(successful_endpoints)} working endpoints:")
    for endpoint in successful_endpoints:
        print(f"   • {endpoint}")

    return successful_endpoints


def test_gateway_with_working_endpoint(gateway_config, working_endpoints):
    """Test our gateway client with a working endpoint."""
    if not working_endpoints:
        print("❌ No working endpoints found to test with")
        return False

    print("\n🧪 Testing Gateway Client with Working Endpoint")
    print("=" * 50)

    # Use the root endpoint for testing
    test_endpoint = "/" if "/" in working_endpoints else working_endpoints[0]

    # Update our client to use a working endpoint
    config = GatewayConfig(
        name="test_gateway",
        host=gateway_config["host"],
        port=gateway_config["port"],
        use_https=gateway_config["use_https"],
        username=gateway_config["username"],
        password=gateway_config["password"],
        auth_type="basic",
        verify_ssl=gateway_config["verify_ssl"],
        timeout=30,
        description="Test Gateway for Endpoint Discovery",
    )

    try:
        # Create a modified client that tests with working endpoint
        client = IgnitionGatewayClient(config=config)

        # Test authentication by accessing a working endpoint
        print(f"Testing endpoint: {test_endpoint}")
        response = client.session.get(f"{config.base_url}{test_endpoint}", timeout=10)

        if response.status_code == 200:
            print("✅ Gateway client connection successful!")
            print(f"   Response: HTTP {response.status_code}")
            print(f"   Content Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Content Length: {len(response.content)} bytes")

            # Test if it's an Ignition gateway by looking for common indicators
            content = response.text.lower()
            if any(
                indicator in content
                for indicator in ["ignition", "inductiveautomation", "gateway"]
            ):
                print("🎯 Confirmed: This is an Ignition Gateway!")

            client.disconnect()
            return True
        else:
            print(f"❌ Unexpected response: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Client test failed: {e}")
        return False


def save_working_config(gateway_config):
    """Save a working configuration based on our findings."""
    config_content = f"""# Working Ignition Gateway Configuration
# Gateway: {gateway_config["host"]}:{gateway_config["port"]}
# Connection confirmed working

IGN_GATEWAYS=discovered_gateway

# Discovered Gateway Configuration
IGN_DISCOVERED_GATEWAY_HOST={gateway_config["host"]}
IGN_DISCOVERED_GATEWAY_PORT={gateway_config["port"]}
IGN_DISCOVERED_GATEWAY_HTTPS={'true' if gateway_config["use_https"] else 'false'}
IGN_DISCOVERED_GATEWAY_USERNAME={gateway_config["username"]}
IGN_DISCOVERED_GATEWAY_PASSWORD={gateway_config["password"]}
IGN_DISCOVERED_GATEWAY_AUTH_TYPE=basic
IGN_DISCOVERED_GATEWAY_VERIFY_SSL={'true' if gateway_config["verify_ssl"] else 'false'}
IGN_DISCOVERED_GATEWAY_TIMEOUT=30
IGN_DISCOVERED_GATEWAY_DESCRIPTION=Discovered Gateway - Working Configuration
"""

    try:
        with open(".env.discovered", "w") as f:
            f.write(config_content)
        print("\n💾 Saved working configuration to .env.discovered")
        print("   Copy this to .env to use with the system")
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")


if __name__ == "__main__":
    print("🚀 IGN Scripts - Ignition Endpoint Discovery")
    print("Discovering available endpoints on your gateway...")
    print("=" * 60)

    # Get gateway configuration
    gateway_config = get_gateway_config()

    if not gateway_config:
        print("❌ Gateway configuration required")
        exit(1)

    # Test endpoints
    working_endpoints = test_ignition_endpoints(gateway_config)

    # Test client with working endpoints
    if working_endpoints:
        success = test_gateway_with_working_endpoint(gateway_config, working_endpoints)

        if success:
            print("\n🎉 SUCCESS! Gateway connection is working!")

            save_choice = (
                input("\n💾 Save this working configuration? (y/n) [y]: ")
                .strip()
                .lower()
            )
            if save_choice != "n":
                save_working_config(gateway_config)

            print("\n✅ Endpoint Discovery Complete!")
            print("Your gateway is accessible and responding correctly")
            print("Use the saved configuration for further development")
        else:
            print("\n⚠️ Gateway responds but client needs adjustment")
    else:
        print("\n❌ No accessible endpoints found")
        print("Check:")
        print("- Gateway credentials")
        print("- Gateway web interface is enabled")
        print("- Network connectivity")
