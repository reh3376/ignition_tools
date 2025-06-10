#!/usr/bin/env python3
"""
Final test of the Ignition Gateway client with user configuration.
This script uses environment variables or prompts for gateway details.
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from ignition.gateway.config import GatewayConfig, GatewayConfigManager
from ignition.gateway.client import IgnitionGatewayClient

# Configure logging to see more details
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_gateway_config():
    """Get gateway configuration from environment or user input."""
    # Try to load from environment first
    manager = GatewayConfigManager()
    
    try:
        # Check if we have any configured gateways
        configs = manager.list_configs()
        if configs:
            print("🔧 Available Gateway Configurations:")
            for i, name in enumerate(configs, 1):
                config = manager.get_config(name)
                if config:
                    print(f"  {i}. {name} - {config.base_url}")
            
            choice = input(f"\nSelect gateway [1]: ").strip() or "1"
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(configs):
                    config_name = configs[idx]
                    return manager.get_config(config_name)
            except (ValueError, IndexError):
                pass
    except Exception:
        pass
    
    # If no environment configs, prompt for manual configuration
    print("🔧 Manual Gateway Configuration")
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
    
    use_https = input("Use HTTPS? (y/n) [n]: ").strip().lower() in ['y', 'yes', '1', 'true']
    username = input("Username [admin]: ").strip() or "admin"
    password = input("Password [password]: ").strip() or "password"
    
    verify_ssl = True
    if use_https:
        verify_ssl = input("Verify SSL certificates? (y/n) [y]: ").strip().lower() not in ['n', 'no', '0', 'false']
    
    return GatewayConfig(
        name="manual_test",
        host=host,
        port=port,
        use_https=use_https,
        username=username,
        password=password,
        auth_type="basic",
        verify_ssl=verify_ssl,
        timeout=30,
        description="Manually configured test gateway"
    )


def test_updated_client(config):
    """Test the updated client with working endpoints."""
    print("🧪 Final Test - Gateway Client Functionality")
    print(f"Gateway: {config.base_url}")
    print("=" * 60)
    
    print(f"Configuration:")
    print(f"  Name: {config.name}")
    print(f"  URL: {config.base_url}")
    print(f"  Auth: {config.auth_type} ({config.username})")
    print(f"  SSL Verification: {config.verify_ssl}")
    print(f"  Timeout: {config.timeout}s")
    
    try:
        print(f"\n⏳ Creating client and testing connection...")
        
        # Test connection
        with IgnitionGatewayClient(config=config) as client:
            print("✅ Connection established successfully!")
            
            # Test gateway info
            print(f"\n📊 Gateway Information:")
            info = client.get_gateway_info()
            if info:
                for key, value in info.items():
                    if key == "gateway_info_raw":
                        # Show first 100 chars of raw info
                        preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                        print(f"   {key}: {preview}")
                    else:
                        print(f"   {key}: {value}")
            else:
                print("   Could not retrieve gateway info")
                
            # Test health check
            print(f"\n🏥 Health Check:")
            health = client.health_check()
            
            print(f"   Overall Status: {health['overall_status']}")
            print(f"   Timestamp: {health['timestamp']}")
            print(f"   Gateway: {health['gateway_name']} ({health['gateway_url']})")
            
            print(f"\n   Detailed Checks:")
            for check_name, check_result in health['checks'].items():
                status = check_result['status']
                details = check_result.get('details', '')
                
                # Status icons
                if status == 'healthy':
                    icon = "✅"
                elif status == 'warning':
                    icon = "⚠️"
                else:
                    icon = "❌"
                
                print(f"   {icon} {check_name.replace('_', ' ').title()}: {status}")
                if details:
                    print(f"      Details: {details}")
                    
                # Show response time
                if check_name == 'response_time' and 'value_ms' in check_result:
                    ms = check_result['value_ms']
                    print(f"      Response Time: {ms}ms")
            
            # Test connection status
            print(f"\n🔗 Connection Status:")
            print(f"   Is Connected: {client.is_connected()}")
            print(f"   Config Name: {client.config.name}")
            print(f"   Base URL: {client.config.base_url}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during final test: {e}")
        print(f"Exception type: {type(e).__name__}")
        return False


def create_env_template(config):
    """Create a .env template file with the tested configuration."""
    env_content = f"""# IGN Scripts - Gateway Configuration Template
# Gateway tested and verified: {config.host}:{config.port}

# Enable dotenv loading
DOTENV_LOADED=true

# Gateway Configuration  
IGN_GATEWAYS=tested_gateway

# Tested Gateway Configuration
IGN_TESTED_GATEWAY_HOST={config.host}
IGN_TESTED_GATEWAY_PORT={config.port}
IGN_TESTED_GATEWAY_HTTPS={'true' if config.use_https else 'false'}
IGN_TESTED_GATEWAY_USERNAME={config.username}
IGN_TESTED_GATEWAY_PASSWORD={config.password}
IGN_TESTED_GATEWAY_AUTH_TYPE={config.auth_type}
IGN_TESTED_GATEWAY_VERIFY_SSL={'true' if config.verify_ssl else 'false'}
IGN_TESTED_GATEWAY_TIMEOUT={config.timeout}
IGN_TESTED_GATEWAY_DESCRIPTION={config.description}
IGN_TESTED_GATEWAY_TAGS=tested,working

# Optional: Add more gateways as needed
# IGN_GATEWAYS=tested_gateway,production_gateway
#
# IGN_PRODUCTION_GATEWAY_HOST=your-prod-gateway.com
# IGN_PRODUCTION_GATEWAY_PORT=8043
# IGN_PRODUCTION_GATEWAY_HTTPS=true
# IGN_PRODUCTION_GATEWAY_USERNAME=your_username
# IGN_PRODUCTION_GATEWAY_PASSWORD=your_password
# IGN_PRODUCTION_GATEWAY_AUTH_TYPE=basic
# IGN_PRODUCTION_GATEWAY_VERIFY_SSL=true
# IGN_PRODUCTION_GATEWAY_TIMEOUT=30
# IGN_PRODUCTION_GATEWAY_DESCRIPTION=Production Ignition Gateway
"""
    
    try:
        with open(".env.template", "w") as f:
            f.write(env_content)
        print(f"\n💾 Created .env.template with tested configuration")
        print("   ✅ Copy to .env to use with IGN Scripts system")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env template: {e}")
        return False


def show_usage_examples():
    """Show examples of how to use the gateway client."""
    print(f"\n📋 Usage Examples:")
    print("=" * 40)
    
    examples = [
        ("Basic Connection", """
from ignition.gateway import IgnitionGatewayClient

# Using config name from .env
client = IgnitionGatewayClient(config_name="tested_gateway")
if client.connect():
    info = client.get_gateway_info()
    print(f"Connected to: {info['connection_url']}")
    client.disconnect()
"""),
        
        ("Context Manager", """
from ignition.gateway import IgnitionGatewayClient

# Automatic connection/disconnection
with IgnitionGatewayClient(config_name="tested_gateway") as client:
    health = client.health_check()
    print(f"Gateway status: {health['overall_status']}")
"""),
        
        ("Connection Pool", """
from ignition.gateway import GatewayConnectionPool

# Manage multiple gateways
pool = GatewayConnectionPool()
pool.add_client("tested_gateway")

# Connect all and check health
results = pool.connect_all()
health_results = pool.health_check_all()

for name, health in health_results.items():
    print(f"{name}: {health['overall_status']}")
"""),
        
        ("Environment Loading", """
from ignition.gateway.config import GatewayConfigManager

# Load from .env file
manager = GatewayConfigManager()
config = manager.get_config("tested_gateway")
print(f"Gateway: {config.base_url}")

# List all configured gateways
configs = manager.list_configs()
for name in configs:
    print(f"Available: {name}")
""")
    ]
    
    for title, code in examples:
        print(f"\n🔧 {title}:")
        print(code.strip())


if __name__ == "__main__":
    print("🚀 IGN Scripts - Gateway Connection System Test")
    print("Testing gateway client with your configuration")
    print("=" * 70)
    
    # Get gateway configuration
    config = get_gateway_config()
    
    if not config:
        print("❌ Gateway configuration required")
        exit(1)
    
    # Run the test
    success = test_updated_client(config)
    
    if success:
        print(f"\n🎉 SUCCESS! Gateway client is fully functional!")
        
        # Create template file
        template_created = create_env_template(config)
        
        if template_created:
            print(f"\n✅ Setup Complete!")
            print("Your Ignition Gateway connection system is ready:")
            print("• Gateway client tested and working")  
            print("• Configuration template created")
            print("• Ready for integration with CLI and UI")
            
            # Show usage examples
            show_usage_examples()
            
            print(f"\n🚀 Next Steps:")
            print("1. Copy .env.template to .env and customize as needed")
            print("2. Use the enhanced CLI: python -m src.core.enhanced_cli")
            print("3. Import gateway classes in your scripts")
            print("4. Build applications using the gateway client")
        
    else:
        print(f"\n❌ Test failed. Check the error messages above.")
        print("Verify your gateway details and network connectivity.")
    
    print(f"\n🎯 Test Result: {'SUCCESS' if success else 'FAILED'}") 