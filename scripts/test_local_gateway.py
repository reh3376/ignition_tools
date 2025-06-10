#!/usr/bin/env python3
"""
Test script for connecting to a local Ignition Gateway.

This script helps configure and test the connection to your local Ignition gateway.
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


def create_local_gateway_config():
    """Create a sample configuration for local gateway testing."""
    # Common local gateway settings
    configs = [
        {
            "name": "local_dev",
            "host": "localhost",
            "port": 8088,
            "https": False,
            "username": "admin",
            "password": "password",
            "description": "Local development gateway",
        },
        {
            "name": "local_https",
            "host": "localhost",
            "port": 8043,
            "https": True,
            "username": "admin",
            "password": "password",
            "verify_ssl": False,
            "description": "Local development gateway with HTTPS",
        },
    ]

    print("🔧 Sample Local Gateway Configurations:")
    print("=" * 50)

    for i, config in enumerate(configs, 1):
        print(f"\n{i}. {config['name']}:")
        print(
            f"   URL: {'https' if config['https'] else 'http'}://{config['host']}:{config['port']}"
        )
        print(f"   Auth: {config['username']}/{'*' * len(config['password'])}")
        print(f"   Description: {config['description']}")

    return configs


def get_user_gateway_config():
    """Get gateway configuration from user input."""
    print("\n🚀 Configure Your Local Ignition Gateway")
    print("=" * 50)

    # Get basic connection info
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
        verify_ssl = input("Verify SSL certificates? (y/n) [n]: ").strip().lower() in [
            "y",
            "yes",
            "1",
            "true",
        ]

    # Create configuration
    config = GatewayConfig(
        name="local_test",
        host=host,
        port=port,
        use_https=use_https,
        username=username,
        password=password,
        auth_type="basic",
        verify_ssl=verify_ssl,
        timeout=30,
        description="User-configured local gateway",
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
        # Create client
        client = IgnitionGatewayClient(config=config)

        # Test connection
        print("\n⏳ Attempting to connect...")
        success = client.connect()

        if success:
            print("✅ Connection successful!")

            # Get gateway info
            print("\n📊 Gateway Information:")
            info = client.get_gateway_info()
            if info:
                for key, value in info.items():
                    print(f"   {key}: {value}")

            # Perform health check
            print("\n🏥 Health Check:")
            health = client.health_check()
            print(f"   Overall Status: {health['overall_status']}")
            print(
                f"   Response Time: {health['checks']['response_time']['value_ms']}ms"
            )

            for check_name, check_result in health["checks"].items():
                status_icon = (
                    "✅"
                    if check_result["status"] == "healthy"
                    else "⚠️"
                    if check_result["status"] == "warning"
                    else "❌"
                )
                print(
                    f"   {status_icon} {check_name.title()}: {check_result['status']} - {check_result.get('details', '')}"
                )

            # Clean up
            client.disconnect()

        else:
            print("❌ Connection failed!")
            return False

    except Exception as e:
        print(f"❌ Error during connection test: {e}")
        return False

    return True


def save_working_config(config: GatewayConfig):
    """Save a working configuration to a .env file."""
    env_content = f"""# Working Local Gateway Configuration
# Generated by test_local_gateway.py

IGN_GATEWAYS=local_test

# Local Test Gateway
IGN_LOCAL_TEST_HOST={config.host}
IGN_LOCAL_TEST_PORT={config.port}
IGN_LOCAL_TEST_HTTPS={'true' if config.use_https else 'false'}
IGN_LOCAL_TEST_USERNAME={config.username}
IGN_LOCAL_TEST_PASSWORD={config.password}
IGN_LOCAL_TEST_AUTH_TYPE={config.auth_type}
IGN_LOCAL_TEST_VERIFY_SSL={'true' if config.verify_ssl else 'false'}
IGN_LOCAL_TEST_TIMEOUT={config.timeout}
IGN_LOCAL_TEST_DESCRIPTION={config.description}
"""

    try:
        with open(".env.local", "w") as f:
            f.write(env_content)
        print("\n💾 Saved working configuration to .env.local")
        print("   You can copy this to .env to use with the full system")
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")


def main():
    """Main test function."""
    print("🧪 IGN Scripts - Local Gateway Connection Test")
    print("=" * 60)

    # Show sample configurations
    sample_configs = create_local_gateway_config()

    # Choice menu
    print("\n📋 Options:")
    print("1. Test with sample configuration (localhost:8088)")
    print("2. Test with sample HTTPS configuration (localhost:8043)")
    print("3. Configure custom gateway settings")
    print("0. Exit")

    choice = input("\nSelect option [1]: ").strip()

    if choice == "0":
        print("👋 Goodbye!")
        return
    elif choice == "2":
        # Use HTTPS sample
        config_data = sample_configs[1]
        config = GatewayConfig(
            name=config_data["name"],
            host=config_data["host"],
            port=config_data["port"],
            use_https=config_data["https"],
            username=config_data["username"],
            password=config_data["password"],
            verify_ssl=config_data["verify_ssl"],
            description=config_data["description"],
        )
    elif choice == "3":
        # Custom configuration
        config = get_user_gateway_config()
    else:
        # Default to HTTP sample
        config_data = sample_configs[0]
        config = GatewayConfig(
            name=config_data["name"],
            host=config_data["host"],
            port=config_data["port"],
            use_https=config_data["https"],
            username=config_data["username"],
            password=config_data["password"],
            description=config_data["description"],
        )

    # Test the connection
    success = test_gateway_connection(config)

    # Save config if successful
    if success:
        save_choice = (
            input("\n💾 Save this working configuration? (y/n) [y]: ").strip().lower()
        )
        if save_choice != "n":
            save_working_config(config)

    print(f"\n🎯 Test completed: {'SUCCESS' if success else 'FAILED'}")

    if success:
        print("\n🎉 Your gateway connection is working!")
        print("Next steps:")
        print("- Copy .env.local to .env to use this configuration")
        print("- Try the CLI commands: python -m src.core.enhanced_cli gateway list")
        print("- Use the web UI for gateway management")
    else:
        print("\n🔧 Connection failed. Check:")
        print("- Gateway is running and accessible")
        print("- Correct host and port")
        print("- Valid username and password")
        print("- Network connectivity")


if __name__ == "__main__":
    main()
