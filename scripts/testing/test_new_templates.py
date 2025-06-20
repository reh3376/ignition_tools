#!/usr/bin/env python3
"""
Test script for new Ignition templates
Tests the recently created templates with sample configurations
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ignition.generators.script_generator import IgnitionScriptGenerator


def test_gateway_timer_template():
    """Test the Gateway timer script template"""
    print("=== Testing Gateway Timer Template ===")

    generator = IgnitionScriptGenerator()

    # Test configuration
    config = {
        "script_name": "TestDataCollector",
        "timer_purpose": "Test data collection every 30 seconds",
        "enable_logging": True,
        "error_handling": "continue",
        "tag_operations": [
            {
                "type": "read",
                "description": "Read test tags",
                "tag_paths": ["[default]Test/Tag1", "[default]Test/Tag2"],
                "process_code": "for i, tag_value in enumerate(tag_values):\n    print('Tag value:', tag_value.value)",
            }
        ],
        "custom_code": "# Test custom logic\nprint('Timer executed successfully')",
    }

    try:
        result = generator.generate_script("gateway/timer_script.jinja2", config)

        print(f"✅ Template generated successfully ({len(result)} characters)")
        print("\n--- First 300 characters ---")
        print(result[:300])
        print("...\n")

        # Basic validation
        if "system.util.getLogger" in result and "TestDataCollector" in result:
            print("✅ Template contains expected elements")
        else:
            print("❌ Template missing expected elements")

        return True

    except Exception as e:
        print(f"❌ Template generation failed: {e}")
        return False


def test_tag_change_template():
    """Test the Gateway tag change script template"""
    print("=== Testing Gateway Tag Change Template ===")

    generator = IgnitionScriptGenerator()

    config = {
        "script_name": "TestTagChange",
        "handle_initial_change": False,
        "enable_logging": True,
        "change_triggers": ["value"],
        "response_actions": [
            {
                "type": "tag_write",
                "description": "Write response to another tag",
                "target_paths": ["[default]Response/Tag"],
                "values": ["newValue.getValue() * 2"],
            }
        ],
    }

    try:
        result = generator.generate_script("gateway/tag_change_script.jinja2", config)

        print(f"✅ Template generated successfully ({len(result)} characters)")
        print("\n--- First 300 characters ---")
        print(result[:300])
        print("...\n")

        # Basic validation
        if "initialChange" in result and "newValue" in result:
            print("✅ Template contains tag change context variables")
        else:
            print("❌ Template missing tag change context variables")

        return True

    except Exception as e:
        print(f"❌ Template generation failed: {e}")
        return False


def test_vision_popup_template():
    """Test the Vision popup window handler template"""
    print("=== Testing Vision Popup Template ===")

    generator = IgnitionScriptGenerator()

    config = {
        "component_name": "TestPopupHandler",
        "window_path": "Windows/TestPopup",
        "enable_logging": True,
        "popup_mode": "modal",
        "window_params": {"testParam": "testValue", "timestamp": "system.date.now()"},
        "validation_checks": [
            {
                "type": "user_role",
                "required_roles": ["Operator"],
                "error_message": "Only operators can open this window",
            }
        ],
    }

    try:
        result = generator.generate_script("vision/popup_window_handler.jinja2", config)

        print(f"✅ Template generated successfully ({len(result)} characters)")
        print("\n--- First 300 characters ---")
        print(result[:300])
        print("...\n")

        # Basic validation
        if "system.nav.openWindow" in result and "system.security.getRoles" in result:
            print("✅ Template contains Vision-specific functions")
        else:
            print("❌ Template missing Vision-specific functions")

        return True

    except Exception as e:
        print(f"❌ Template generation failed: {e}")
        return False


def test_perspective_navigation_template():
    """Test the Perspective navigation template"""
    print("=== Testing Perspective Navigation Template ===")

    generator = IgnitionScriptGenerator()

    config = {
        "component_name": "TestPerspectiveNav",
        "navigation_type": "page",
        "target_page": "/test/page",
        "enable_logging": True,
        "page_params": {
            "userId": "system.security.getUsername()",
            "timestamp": "system.date.now()",
        },
    }

    try:
        result = generator.generate_script("perspective/session_navigation.jinja2", config)

        print(f"✅ Template generated successfully ({len(result)} characters)")
        print("\n--- First 300 characters ---")
        print(result[:300])
        print("...\n")

        # Basic validation
        if "system.perspective.navigate" in result:
            print("✅ Template contains Perspective-specific functions")
        else:
            print("❌ Template missing Perspective-specific functions")

        return True

    except Exception as e:
        print(f"❌ Template generation failed: {e}")
        return False


def main():
    """Run all template tests"""
    print("🚀 Starting IGN Scripts Template Tests\n")

    tests = [
        test_gateway_timer_template,
        test_tag_change_template,
        test_vision_popup_template,
        test_perspective_navigation_template,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            failed += 1
        print("-" * 50)

    print(f"\n📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! New templates are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
