#!/usr/bin/env python3
"""
Test script for connecting to user-configured Ignition Gateway.

This script helps test connections to Ignition gateways using user-provided configuration.
Update the gateway details below or use environment variables.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from ignition.gateway.client import IgnitionGatewayClient
from ignition.gateway.config import GatewayConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_user_gateway_config():
    """Get gateway configuration from user input or environment variables."""
    print("🔧 Configure Your Ignition Gateway Connection")
    print("=" * 55)

    # Get connection details from user
    host = input("Gateway host [localhost]: ").strip() or "localhost"
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

    # Authentication
    print("\nAuthentication:")
    username = input("Username [admin]: ").strip() or "admin"
    password = input("Password [password]: ").strip() or "password"

    # SSL verification (only for HTTPS)
    verify_ssl = True
    if use_https:
        verify_ssl = input(
            "Verify SSL certificates? (y/n) [y]: "
        ).strip().lower() not in ["n", "no", "0", "false"]

    # Create configuration
    config = GatewayConfig(
        name="user_test_gateway",
        host=host,
        port=port,
        use_https=use_https,
        username=username,
        password=password,
        auth_type="basic",
        verify_ssl=verify_ssl,
        timeout=30,
        description="User-configured test gateway",
    )

    return config


def test_gateway_connection(config: GatewayConfig):
    """Test connection to the gateway with detailed output."""
    print(f"\n🔗 Testing Connection to {config.name}")
    print("=" * 50)
    print(f"Gateway URL: {config.base_url}")
    print(f"Authentication: {config.auth_type} ({config.username})")
    print(f"SSL Verification: {config.verify_ssl}")
    print(f"Timeout: {config.timeout}s")

    try:
        # Create and test client
        print("\n⏳ Creating client and connecting...")
        client = IgnitionGatewayClient(config=config)

        success = client.connect()

        if success:
            print("✅ Connection successful!")

            # Get gateway info
            print("\n📊 Gateway Information:")
            info = client.get_gateway_info()
            if info:
                for key, value in info.items():
                    if key == "gateway_info_raw":
                        # Show first 100 chars of raw info
                        preview = (
                            str(value)[:100] + "..."
                            if len(str(value)) > 100
                            else str(value)
                        )
                        print(f"   {key}: {preview}")
                    else:
                        print(f"   {key}: {value}")
            else:
                print("   Could not retrieve gateway info")

            # Perform health check
            print("\n🏥 Health Check:")
            health = client.health_check()
            print(f"   Overall Status: {health['overall_status']}")

            for check_name, check_result in health["checks"].items():
                status = check_result["status"]
                details = check_result.get("details", "")

                if status == "healthy":
                    icon = "✅"
                elif status == "warning":
                    icon = "⚠️"
                else:
                    icon = "❌"

                print(f"   {icon} {check_name.replace('_', ' ').title()}: {status}")
                if details:
                    print(f"      {details}")

                if check_name == "response_time":
                    ms = check_result.get("value_ms", 0)
                    print(f"      Response time: {ms}ms")

            # Clean up
            client.disconnect()

        else:
            print("❌ Connection failed!")
            return False

    except Exception as e:
        print(f"❌ Error during connection test: {e}")
        print(f"Exception type: {type(e).__name__}")

        if "SSL" in str(e):
            print("\n💡 SSL Error - Try with verify_ssl=False")
        elif "Connection refused" in str(e):
            print("\n💡 Connection refused - Check if gateway is running")
        elif "timeout" in str(e).lower():
            print("\n💡 Timeout - Gateway may be slow or unreachable")

        return False

    return True


def save_config_to_env(config: GatewayConfig):
    """Save working config to .env template file."""
    env_content = f"""# Working Gateway Configuration for {config.host}:{config.port}
# Generated by test_specific_gateway.py

IGN_GATEWAYS=user_gateway

# User Gateway Configuration
IGN_USER_GATEWAY_HOST={config.host}
IGN_USER_GATEWAY_PORT={config.port}
IGN_USER_GATEWAY_HTTPS={'true' if config.use_https else 'false'}
IGN_USER_GATEWAY_USERNAME={config.username}
IGN_USER_GATEWAY_PASSWORD={config.password}
IGN_USER_GATEWAY_AUTH_TYPE={config.auth_type}
IGN_USER_GATEWAY_VERIFY_SSL={'true' if config.verify_ssl else 'false'}
IGN_USER_GATEWAY_TIMEOUT={config.timeout}
IGN_USER_GATEWAY_DESCRIPTION={config.description}

# Copy this content to your .env file to use with the system
"""

    try:
        with open(".env.test", "w") as f:
            f.write(env_content)
        print("\n💾 Saved working configuration to .env.test")
        print("   You can copy this content to your .env file")
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")


if __name__ == "__main__":
    print("🧪 IGN Scripts - Gateway Connection Test")
    print("Configure and test your Ignition Gateway connection")
    print("=" * 60)

    # Get user configuration
    config = get_user_gateway_config()

    # Test the connection
    success = test_gateway_connection(config)

    # Save config if successful
    if success:
        save_choice = (
            input("\n💾 Save this working configuration? (y/n) [y]: ").strip().lower()
        )
        if save_choice != "n":
            save_config_to_env(config)

    print(f"\n🎯 Test completed: {'SUCCESS' if success else 'FAILED'}")

    if success:
        print("\n🎉 Your gateway connection is working!")
        print("Next steps:")
        print("- Copy the configuration to your .env file")
        print("- Use the enhanced CLI: python -m src.core.enhanced_cli")
        print("- Build applications using the gateway client")
    else:
        print("\n🔧 Connection failed. Check:")
        print("- Gateway is running and accessible")
        print("- Correct host and port")
        print("- Valid username and password")
        print("- Network connectivity")
