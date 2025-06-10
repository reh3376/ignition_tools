#!/usr/bin/env python3
"""
Test script for the Ignition Gateway Configuration System.

This script demonstrates the functionality of the gateway configuration
management system with python-dotenv integration.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from ignition.gateway.config import GatewayConfig, GatewayConfigManager


def test_gateway_config():
    """Test gateway configuration functionality."""
    print("🧪 Testing IGN Scripts Gateway Configuration System")
    print("=" * 60)

    # Test 1: Create sample .env file
    print("\n1. Creating sample .env file...")
    manager = GatewayConfigManager()
    if manager.create_sample_env_file(".env.sample"):
        print("✅ Created .env.sample file successfully")
    else:
        print("❌ Failed to create .env.sample file")

    # Test 2: Manual configuration creation
    print("\n2. Testing manual configuration creation...")
    try:
        config = GatewayConfig(
            name="test_gateway",
            host="localhost",
            port=8088,
            use_https=False,
            username="admin",
            password="password",
            auth_type="basic",
            project_name="TestProject",
            description="Test gateway for development",
            tags=["test", "development"],
        )
        print("✅ Created gateway config:", config.name)
        print(f"   URL: {config.base_url}")
        print(f"   API URL: {config.api_url}")
        print(f"   Auth Type: {config.auth_type}")
        print(f"   Project: {config.project_name}")
        print(f"   Tags: {config.tags}")
    except Exception as e:
        print(f"❌ Failed to create config: {e}")

    # Test 3: Configuration validation
    print("\n3. Testing configuration validation...")
    try:
        # Test invalid config (missing username for basic auth)
        invalid_config = GatewayConfig(
            name="invalid",
            host="localhost",
            auth_type="basic",  # Missing username/password
        )
        print("❌ Should have failed validation")
    except ValueError as e:
        print(f"✅ Correctly caught validation error: {e}")

    # Test 4: Environment-based configuration
    print("\n4. Testing environment-based configuration...")

    # Create a test environment file
    test_env_content = """# Test Configuration
IGN_GATEWAYS=dev,prod

# Development Gateway
IGN_DEV_HOST=localhost
IGN_DEV_PORT=8088
IGN_DEV_HTTPS=false
IGN_DEV_USERNAME=admin
IGN_DEV_PASSWORD=password
IGN_DEV_AUTH_TYPE=basic
IGN_DEV_PROJECT=DevProject
IGN_DEV_DESCRIPTION=Development gateway
IGN_DEV_TAGS=dev,testing

# Production Gateway
IGN_PROD_HOST=prod-server.company.com
IGN_PROD_PORT=8443
IGN_PROD_HTTPS=true
IGN_PROD_USERNAME=prod_user
IGN_PROD_PASSWORD=secure_password
IGN_PROD_AUTH_TYPE=basic
IGN_PROD_PROJECT=ProdApp
IGN_PROD_DESCRIPTION=Production gateway
IGN_PROD_TAGS=prod,critical
"""

    with open("test_gateway.env", "w") as f:
        f.write(test_env_content)

    try:
        env_manager = GatewayConfigManager("test_gateway.env")
        print(f"✅ Loaded {len(env_manager.get_config_names())} gateway configs")

        for name in env_manager.get_config_names():
            config = env_manager.get_config(name)
            print(f"   {name}: {config.host}:{config.port} ({config.auth_type})")

        # Test configuration summary
        summary = env_manager.get_summary()
        print(f"✅ Gateway summary: {summary['total_gateways']} gateways configured")

    except Exception as e:
        print(f"❌ Failed to load environment configs: {e}")

    # Test 5: Configuration validation
    print("\n5. Testing configuration validation...")
    try:
        errors = env_manager.validate_all_configs()
        if errors:
            print("⚠️  Found configuration errors:")
            for name, error_list in errors.items():
                print(f"   {name}: {error_list}")
        else:
            print("✅ All configurations are valid")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

    # Test 6: Configuration management operations
    print("\n6. Testing configuration management...")
    try:
        # Add a new config
        new_config = GatewayConfig(
            name="staging",
            host="staging-gateway.local",
            port=8088,
            username="staging_user",
            password="staging_pass",
            description="Staging environment",
        )
        env_manager.add_config(new_config)
        print(
            f"✅ Added staging config. Total configs: {len(env_manager.get_config_names())}"
        )

        # Remove a config
        if env_manager.remove_config("staging"):
            print(
                f"✅ Removed staging config. Total configs: {len(env_manager.get_config_names())}"
            )
        else:
            print("❌ Failed to remove staging config")

    except Exception as e:
        print(f"❌ Configuration management failed: {e}")

    # Cleanup
    print("\n7. Cleaning up test files...")
    test_files = ["test_gateway.env"]
    for file in test_files:
        try:
            Path(file).unlink(missing_ok=True)
            print(f"✅ Cleaned up {file}")
        except Exception as e:
            print(f"⚠️  Could not clean up {file}: {e}")

    print("\n" + "=" * 60)
    print("🎉 Gateway Configuration System Test Complete!")
    print("\nNext Steps:")
    print("1. Copy .env.sample to .env and configure your gateways")
    print("2. Use GatewayConfigManager to load your configurations")
    print("3. Ready for IgnitionGatewayClient implementation!")


if __name__ == "__main__":
    test_gateway_config()
