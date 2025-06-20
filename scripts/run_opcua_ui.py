#!/usr/bin/env python3
"""Launch script for OPC-UA Web UI Interface.

This script launches the Streamlit-based OPC-UA interface for managing
OPC-UA server connections, browsing nodes, and monitoring data.

Usage:
    python scripts/run_opcua_ui.py [options]

Environment Variables:
    OPCUA_SERVER_URL - Default OPC-UA server URL
    OPCUA_USERNAME - Default username for authentication
    OPCUA_PASSWORD - Default password for authentication
    STREAMLIT_SERVER_PORT - Port for the Streamlit server (default: 8501)
    STREAMLIT_SERVER_ADDRESS - Address for the Streamlit server (default: localhost)
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "streamlit",
        "asyncua",
        "python-dotenv",
        "cryptography",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False

    return True


def setup_environment():
    """Setup environment variables and directories."""
    # Create necessary directories
    directories = [
        ".secret_env",
        "logs",
        "config",
        os.path.expanduser("~/.ignition/opcua/certificates/trusted"),
        os.path.expanduser("~/.ignition/opcua/certificates/rejected"),
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    # set default environment variables if not present
    defaults = {
        "OPCUA_SERVER_URL": "opc.tcp://localhost:4840",
        "OPCUA_USERNAME": "admin",
        "OPCUA_APPLICATION_NAME": "IGN-Scripts",
        "OPCUA_SECURITY_POLICY": "Basic256Sha256",
        "OPCUA_SECURITY_MODE": "SignAndEncrypt",
        "STREAMLIT_SERVER_PORT": "8501",
        "STREAMLIT_SERVER_ADDRESS": "localhost",
        "LOG_LEVEL": "INFO",
        "ENVIRONMENT": "development",
    }

    env_updated = False
    for key, default_value in defaults.items():
        if not os.getenv(key):
            os.environ[key] = default_value
            env_updated = True

    if env_updated:
        print("🔧 set default environment variables")


def launch_ui():
    """Launch the OPC-UA Streamlit UI."""
    import subprocess

    # Get configuration from environment
    port = os.getenv("STREAMLIT_SERVER_PORT", "8501")
    address = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")

    # Path to the UI module
    ui_module = src_path / "ignition" / "opcua" / "gui" / "opcua_ui.py"

    if not ui_module.exists():
        print(f"❌ UI module not found at {ui_module}")
        return False

    print("🚀 Launching OPC-UA Web UI...")
    print(f"   📍 URL: http://{address}:{port}")
    print(f"   📂 Module: {ui_module}")
    print("   🔄 Starting Streamlit server...")

    try:
        # Launch Streamlit with the UI module
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ui_module),
            "--server.port",
            port,
            "--server.address",
            address,
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
            "--theme.base",
            "dark",
        ]

        subprocess.run(cmd, cwd=project_root)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down OPC-UA UI...")
        return True
    except Exception as e:
        print(f"❌ Failed to launch UI: {e}")
        return False

    return True


def main():
    """Main entry point."""
    print("🔗 IGN Scripts - OPC-UA Web Interface")
    print("=" * 50)

    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies found")

    # Setup environment
    print("🔧 Setting up environment...")
    setup_environment()
    print("✅ Environment configured")

    # Display configuration
    print("\n📋 Configuration:")
    print(f"   🌐 Server URL: {os.getenv('OPCUA_SERVER_URL')}")
    print(f"   👤 Username: {os.getenv('OPCUA_USERNAME')}")
    print(f"   🔒 Security Policy: {os.getenv('OPCUA_SECURITY_POLICY')}")
    print(f"   🔐 Security Mode: {os.getenv('OPCUA_SECURITY_MODE')}")
    print(f"   🌍 UI Address: {os.getenv('STREAMLIT_SERVER_ADDRESS')}:{os.getenv('STREAMLIT_SERVER_PORT')}")

    # Check .env file
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"   📄 Environment file: {env_file}")
    else:
        print("   ⚠️  No .env file found - using defaults and environment variables")
        print(f"   💡 Create {env_file} from .env.sample for custom configuration")

    print("\n" + "=" * 50)

    # Launch UI
    success = launch_ui()

    if success:
        print("✅ OPC-UA UI finished successfully")
    else:
        print("❌ OPC-UA UI failed to start")
        sys.exit(1)


if __name__ == "__main__":
    main()
