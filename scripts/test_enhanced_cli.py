#!/usr/bin/env python3
"""Test script for enhanced CLI functionality."""

import subprocess
import sys
from pathlib import Path


def install_dependencies():
    """Install required dependencies for enhanced CLI."""
    dependencies = ["rich>=13.7.0", "prompt_toolkit>=3.0.0", "click>=8.1.7"]

    print("🔧 Installing enhanced CLI dependencies...")

    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ Installed: {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False

    return True


def test_imports():
    """Test if all required modules can be imported."""
    print("\n🧪 Testing imports...")

    modules = [
        ("rich", "Rich formatting library"),
        ("prompt_toolkit", "Interactive prompt toolkit library"),
        ("click", "Click CLI library"),
    ]

    for module, description in modules:
        try:
            __import__(module)
            print(f"✅ {description}: OK")
        except ImportError as e:
            print(f"❌ {description}: Failed - {e}")
            return False

    return True


def test_enhanced_cli():
    """Test the enhanced CLI functionality."""
    print("\n🎯 Testing enhanced CLI...")

    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    try:
        from src.core.enhanced_cli import enhanced_cli

        print("✅ Enhanced CLI module imported successfully")

        # Test basic functionality
        if enhanced_cli.client:
            print("✅ Learning system client available")
        else:
            print("⚠️ Learning system client not available (database not connected)")

        # Test Rich formatting
        from rich.console import Console

        console = Console()
        console.print("✅ Rich formatting working!", style="bold green")

        return True

    except Exception as e:
        print(f"❌ Enhanced CLI test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Enhanced CLI Setup & Test")
    print("=" * 40)

    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        sys.exit(1)

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        sys.exit(1)

    # Test enhanced CLI
    if not test_enhanced_cli():
        print("\n❌ Enhanced CLI tests failed")
        sys.exit(1)

    print("\n🎉 All tests passed!")
    print("\n📖 Usage Examples:")
    print("  python -m src.core.enhanced_cli --help")
    print("  python -m src.core.enhanced_cli script generate --help")
    print("  python -m src.core.enhanced_cli learning patterns")
    print("  python -m src.core.enhanced_cli learning stats")
    print("\n💡 To create a global 'ign' command:")
    print("  python scripts/setup_enhanced_cli.py")


if __name__ == "__main__":
    main()
