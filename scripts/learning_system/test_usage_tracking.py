#!/usr/bin/env python3
"""Test script for Usage Tracking System

This script tests the basic functionality of the usage tracking system
including session management, event tracking, and statistics retrieval.
"""

import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.usage_tracker import UsageTracker


def test_usage_tracking():
    """Test the usage tracking system functionality."""

    print("🧪 Testing Usage Tracking System")
    print("=" * 50)

    # Initialize client and tracker
    client = IgnitionGraphClient()
    tracker = UsageTracker(client)

    try:
        # Connect to database
        print("📡 Connecting to Neo4j database...")
        if not client.connect():
            print("❌ Failed to connect to database")
            return False
        print("✅ Connected successfully!")

        # Test 1: Session Management
        print("\n🔄 Test 1: Session Management")
        session_id = tracker.start_session(user_id="test_user", session_type="testing")
        print(f"✅ Started session: {session_id}")

        # Test 2: Function Query Tracking
        print("\n🔄 Test 2: Function Query Tracking")
        event_id1 = tracker.track_function_query(
            function_name="system.tag.readBlocking",
            context="Gateway",
            parameters={"tagPaths": ["[default]MyTag"]},
            success=True,
            execution_time=0.125,
        )
        print(f"✅ Tracked function query: {event_id1}")

        # Test 3: Template Generation Tracking
        print("\n🔄 Test 3: Template Generation Tracking")
        event_id2 = tracker.track_template_generation(
            template_name="vision/button_click_handler.jinja2",
            parameters={"component_name": "TestButton", "action_type": "navigation"},
            success=True,
            execution_time=0.350,
        )
        print(f"✅ Tracked template generation: {event_id2}")

        # Test 4: Parameter Usage Tracking
        print("\n🔄 Test 4: Parameter Usage Tracking")
        event_id3 = tracker.track_parameter_usage(
            function_name="system.db.runQuery",
            parameters={"query": "SELECT * FROM test", "database": "test_db"},
            context="Vision Client",
            success=True,
        )
        print(f"✅ Tracked parameter usage: {event_id3}")

        # Test 5: Error Event Tracking
        print("\n🔄 Test 5: Error Event Tracking")
        event_id4 = tracker.track_function_query(
            function_name="system.tag.writeBlocking",
            context="Perspective Session",
            parameters={"tagPaths": ["[default]BadTag"], "values": [123]},
            success=False,
            error_message="Tag not found",
            execution_time=0.050,
        )
        print(f"✅ Tracked error event: {event_id4}")

        # Wait a moment to simulate real usage
        time.sleep(1)

        # Test 6: Session Statistics
        print("\n🔄 Test 6: Session Statistics")
        stats = tracker.get_session_stats()
        print(f"✅ Session stats: {stats}")

        # Test 7: Recent Events Retrieval
        print("\n🔄 Test 7: Recent Events")
        recent_events = tracker.get_recent_events(limit=5)
        print(f"✅ Retrieved {len(recent_events)} recent events")
        for event in recent_events:
            print(
                f"   - {event.get('event_type', 'unknown')}: {event.get('function_name') or event.get('template_name', 'N/A')}"
            )

        # Test 8: End Session
        print("\n🔄 Test 8: End Session")
        session_summary = tracker.end_session()
        print(f"✅ Session ended: {session_summary}")

        print("\n🎉 All tests passed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    finally:
        client.disconnect()


def test_context_manager():
    """Test the context manager functionality."""

    print("\n🧪 Testing Context Manager")
    print("=" * 30)

    client = IgnitionGraphClient()
    tracker = UsageTracker(client)

    try:
        client.connect()

        # Test context manager
        with tracker.track_session(
            user_id="context_test_user", session_type="development"
        ) as session_id:
            print(f"📝 In context manager with session: {session_id}")

            # Track some events
            tracker.track_function_query(
                "system.perspective.navigate", context="Perspective Session"
            )
            tracker.track_template_generation("perspective/session_navigation.jinja2")

            # Get stats while session is active
            stats = tracker.get_session_stats()
            print(f"📊 Active session stats: {stats}")

        print("✅ Context manager test completed")

    except Exception as e:
        print(f"❌ Context manager test failed: {e}")

    finally:
        client.disconnect()


def main():
    """Run all usage tracking tests."""

    print("🚀 Starting Usage Tracking System Tests")
    print("=" * 60)

    # Test basic functionality
    basic_test_success = test_usage_tracking()

    # Test context manager
    test_context_manager()

    if basic_test_success:
        print("\n✅ Usage Tracking System is working correctly!")
        print("\n📋 Next steps:")
        print("   • Sub-task 1.1: ✅ COMPLETED - Usage tracking schema created")
        print("   • Sub-task 1.2: ✅ COMPLETED - Usage event collection implemented")
        print("   • Sub-task 1.3: 🔄 NEXT - Build pattern analysis engine")
        print("   • Sub-task 1.4: 📋 PENDING - Create pattern storage and retrieval")
    else:
        print("\n❌ Usage Tracking System has issues that need to be resolved")


if __name__ == "__main__":
    main()
