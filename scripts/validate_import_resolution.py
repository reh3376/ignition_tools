#!/usr/bin/env python3
"""
Import Resolution Validation Script

This script validates that the MCP and MCP Tools modules are properly
configured for import resolution and testing.
"""

import importlib.util
import sys
from pathlib import Path


def test_module_discovery(module_name: str, module_path: str) -> bool:
    """Test if a module can be discovered and imported."""
    try:
        # Add module path to sys.path
        sys.path.insert(0, module_path)

        # Try to find the main module
        spec = importlib.util.find_spec("main")
        if spec is None:
            print(f"❌ {module_name}: main module not found")
            return False

        print(f"✅ {module_name}: main module discovered")

        # Try to import the module (this will fail if dependencies missing, which is expected)
        try:
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            print(f"✅ {module_name}: main module imported successfully")
        except ImportError as e:
            if "fastapi" in str(e).lower() or "uvicorn" in str(e).lower():
                print(
                    f"⚠️  {module_name}: FastAPI dependencies not available (expected)"
                )
            else:
                print(f"❌ {module_name}: unexpected import error: {e}")
                return False

        return True

    except Exception as e:
        print(f"❌ {module_name}: discovery failed: {e}")
        return False
    finally:
        # Clean up sys.path
        if module_path in sys.path:
            sys.path.remove(module_path)


def test_package_structure(module_name: str, module_dir: str) -> bool:
    """Test if the package structure is correct."""
    module_path = Path(module_dir)

    required_files = [
        "__init__.py",
        "src/__init__.py",
        "src/main.py",
        "tests/__init__.py",
        "requirements.txt",
        "pytest.ini",
    ]

    missing_files = []
    for file_path in required_files:
        if not (module_path / file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ {module_name}: missing files: {missing_files}")
        return False

    print(f"✅ {module_name}: package structure complete")
    return True


def test_pytest_configuration(module_name: str, module_dir: str) -> bool:
    """Test if pytest configuration is working."""
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            cwd=module_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print(f"✅ {module_name}: pytest configuration working")
            return True
        else:
            print(f"❌ {module_name}: pytest configuration issues")
            print(f"   Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ {module_name}: pytest test failed: {e}")
        return False


def main():
    """Main validation function."""
    print("🔍 Validating Import Resolution Setup")
    print("=" * 50)

    modules = [("MCP", "mcp", "mcp/src"), ("MCP Tools", "mcp-tools", "mcp-tools/src")]

    all_passed = True

    for module_name, module_dir, src_path in modules:
        print(f"\n📦 Testing {module_name} Module:")

        # Test package structure
        structure_ok = test_package_structure(module_name, module_dir)

        # Test module discovery
        discovery_ok = test_module_discovery(module_name, src_path)

        # Test pytest configuration
        pytest_ok = test_pytest_configuration(module_name, module_dir)

        module_ok = structure_ok and discovery_ok and pytest_ok
        all_passed = all_passed and module_ok

        if module_ok:
            print(f"✅ {module_name}: All tests passed")
        else:
            print(f"❌ {module_name}: Some tests failed")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validation tests passed!")
        print("✅ Import resolution setup is working correctly")
        print(
            "⚠️  Pylance warnings for FastAPI imports are expected when dependencies not installed"
        )
    else:
        print("❌ Some validation tests failed")
        print("🔧 Please check the issues above and fix them")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
