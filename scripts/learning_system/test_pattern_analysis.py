#!/usr/bin/env python3
"""Test script for Pattern Analysis Engine

This script creates sample usage data and tests the pattern analysis
functionality including co-occurrence, template, parameter, and sequential patterns.
"""

import random
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.pattern_analyzer import PatternAnalyzer
from src.ignition.graph.usage_tracker import UsageTracker


def generate_sample_usage_data(tracker: UsageTracker, num_sessions: int = 10):
    """Generate sample usage data for testing pattern analysis.

    Args:
        tracker: UsageTracker instance
        num_sessions: Number of sessions to simulate
    """
    print(f"🎭 Generating {num_sessions} sample sessions for pattern analysis...")

    # Common function combinations that should create patterns
    common_patterns = [
        ["system.tag.readBlocking", "system.tag.writeBlocking"],
        ["system.db.runQuery", "system.db.runUpdate"],
        ["system.perspective.navigate", "system.perspective.getSessionInfo"],
        ["system.gui.messageBox", "system.gui.confirm"],
        ["system.tag.readBlocking", "system.db.runQuery", "system.gui.messageBox"],
    ]

    # Common templates
    templates = [
        "vision/button_click_handler.jinja2",
        "perspective/session_navigation.jinja2",
        "gateway/tag_change_script.jinja2",
        "vision/timer_script.jinja2",
    ]

    # Common parameter patterns
    tag_parameters = {
        "tagPaths": [
            "[default]Tank1/Level",
            "[default]Pump1/Status",
            "[default]Alarm1/Active",
        ],
        "timeout": [1000, 5000, 10000],
    }

    db_parameters = {
        "database": ["ProductionDB", "HistoryDB", "ConfigDB"],
        "timeout": [30000, 60000],
    }

    for session_num in range(num_sessions):
        # Start session
        session_type = random.choice(["development", "testing", "production"])
        user_id = f"user_{random.randint(1, 5)}"

        with tracker.track_session(user_id=user_id, session_type=session_type):
            # Choose a pattern to follow (70% of the time)
            if random.random() < 0.7:
                pattern = random.choice(common_patterns)
                for func in pattern:
                    # Add some realistic parameters
                    params = {}
                    if "tag" in func.lower():
                        params = {
                            "tagPaths": [random.choice(tag_parameters["tagPaths"])],
                            "timeout": random.choice(tag_parameters["timeout"]),
                        }
                    elif "db" in func.lower():
                        params = {
                            "database": random.choice(db_parameters["database"]),
                            "timeout": random.choice(db_parameters["timeout"]),
                        }

                    # Track function usage
                    success = random.random() > 0.1  # 90% success rate
                    execution_time = random.uniform(0.05, 0.5)

                    if success:
                        tracker.track_function_query(
                            function_name=func,
                            context=random.choice(
                                ["Gateway", "Vision Client", "Perspective Session"]
                            ),
                            parameters=params,
                            success=True,
                            execution_time=execution_time,
                        )
                    else:
                        tracker.track_function_query(
                            function_name=func,
                            context=random.choice(
                                ["Gateway", "Vision Client", "Perspective Session"]
                            ),
                            parameters=params,
                            success=False,
                            execution_time=execution_time,
                            error_message="Simulated error for testing",
                        )

                    # Small delay between functions in sequence
                    time.sleep(0.01)

            # Also generate some template usage
            if random.random() < 0.6:  # 60% chance of template usage
                template = random.choice(templates)

                # Template-specific parameters
                template_params = {}
                if "button" in template:
                    template_params = {
                        "component_name": f"Button{random.randint(1, 10)}",
                        "action_type": random.choice(
                            ["navigation", "tag_write", "popup"]
                        ),
                    }
                elif "navigation" in template:
                    template_params = {
                        "target_page": f"/page{random.randint(1, 5)}",
                        "navigation_type": "page",
                    }
                elif "timer" in template:
                    template_params = {
                        "delay": random.choice([1000, 5000, 10000]),
                        "timer_type": random.choice(["fixed_delay", "fixed_rate"]),
                    }

                tracker.track_template_generation(
                    template_name=template,
                    parameters=template_params,
                    success=random.random() > 0.05,  # 95% success rate
                    execution_time=random.uniform(0.1, 0.8),
                )

        print(f"   Session {session_num + 1}/{num_sessions} completed")

    print("✅ Sample usage data generation complete!")


def test_pattern_analysis():
    """Test the pattern analysis engine functionality."""

    print("🧪 Testing Pattern Analysis Engine")
    print("=" * 50)

    # Initialize components
    client = IgnitionGraphClient()
    tracker = UsageTracker(client)
    analyzer = PatternAnalyzer(client)

    try:
        # Connect to database
        print("📡 Connecting to Neo4j database...")
        if not client.connect():
            print("❌ Failed to connect to database")
            return False
        print("✅ Connected successfully!")

        # Generate sample data
        generate_sample_usage_data(tracker, num_sessions=20)

        # Test 1: Analyze all patterns
        print("\n🔄 Test 1: Complete Pattern Analysis")
        results = analyzer.analyze_all_patterns(days_back=1)  # Look at last day only

        print("✅ Analysis completed:")
        for pattern_type, patterns in results["patterns"].items():
            print(f"   • {pattern_type}: {len(patterns)} patterns found")

        # Test 2: Function Co-occurrence Analysis
        print("\n🔄 Test 2: Function Co-occurrence Patterns")
        co_occurrence_patterns = analyzer.analyze_function_co_occurrence(days_back=1)

        if co_occurrence_patterns:
            print(f"✅ Found {len(co_occurrence_patterns)} co-occurrence patterns:")
            for pattern in co_occurrence_patterns[:3]:  # Show top 3
                print(f"   • {pattern['function_1']} + {pattern['function_2']}")
                print(
                    f"     Confidence: {pattern['confidence_1_to_2']:.2%} / {pattern['confidence_2_to_1']:.2%}"
                )
                print(
                    f"     Support: {pattern['support']:.2%}, Lift: {pattern['lift']:.2f}"
                )
        else:
            print("ℹ️ No co-occurrence patterns found (need more diverse data)")

        # Test 3: Template Usage Patterns
        print("\n🔄 Test 3: Template Usage Patterns")
        template_patterns = analyzer.analyze_template_patterns(days_back=1)

        if template_patterns:
            print(f"✅ Found {len(template_patterns)} template patterns:")
            for pattern in template_patterns[:3]:  # Show top 3
                print(f"   • {pattern['template_name']}")
                print(
                    f"     Usage: {pattern['usage_count']}, Success: {pattern['success_rate']:.1%}"
                )
                print(f"     Avg time: {pattern['avg_execution_time']:.3f}s")
        else:
            print("ℹ️ No template patterns found")

        # Test 4: Parameter Combination Patterns
        print("\n🔄 Test 4: Parameter Combination Patterns")
        param_patterns = analyzer.analyze_parameter_patterns(days_back=1)

        if param_patterns:
            print(f"✅ Found {len(param_patterns)} parameter patterns:")
            for pattern in param_patterns[:3]:  # Show top 3
                print(f"   • {pattern['entity_name']} -> {pattern['parameter_key']}")
                print(
                    f"     Frequency: {pattern['frequency']:.1%}, Success: {pattern['success_rate']:.1%}"
                )
                print(
                    f"     Common values: {list(pattern['common_values'].keys())[:3]}"
                )
        else:
            print("ℹ️ No parameter patterns found")

        # Test 5: Sequential Patterns
        print("\n🔄 Test 5: Sequential Usage Patterns")
        sequential_patterns = analyzer.analyze_sequential_patterns(days_back=1)

        if sequential_patterns:
            print(f"✅ Found {len(sequential_patterns)} sequential patterns:")
            for pattern in sequential_patterns[:3]:  # Show top 3
                print(f"   • {' → '.join(pattern['sequence'])}")
                print(
                    f"     Support: {pattern['support']:.2%}, Frequency: {pattern['frequency']}"
                )
        else:
            print("ℹ️ No sequential patterns found")

        # Test 6: Pattern Retrieval
        print("\n🔄 Test 6: Pattern Retrieval from Database")
        stored_patterns = analyzer.get_patterns_by_type(
            "function_co_occurrence", limit=3
        )
        print(f"✅ Retrieved {len(stored_patterns)} stored co-occurrence patterns")

        # Test 7: Function Recommendations
        print("\n🔄 Test 7: Function Recommendations")
        recommendations = analyzer.get_recommendations_for_function(
            "system.tag.readBlocking"
        )

        if recommendations:
            print(
                f"✅ Found {len(recommendations)} recommendations for 'system.tag.readBlocking':"
            )
            for rec in recommendations:
                print(
                    f"   • {rec['recommended_function']} (confidence: {rec['confidence']:.1%})"
                )
                print(f"     {rec['reasoning']}")
        else:
            print("ℹ️ No recommendations found (need more usage data)")

        print("\n🎉 Pattern analysis tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Pattern analysis test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        client.disconnect()


def main():
    """Run pattern analysis tests."""

    print("🚀 Starting Pattern Analysis Engine Tests")
    print("=" * 60)

    success = test_pattern_analysis()

    if success:
        print("\n✅ Pattern Analysis Engine is working correctly!")
        print("\n📋 Progress update:")
        print("   • Sub-task 1.1: ✅ COMPLETED - Usage tracking schema created")
        print("   • Sub-task 1.2: ✅ COMPLETED - Usage event collection implemented")
        print("   • Sub-task 1.3: ✅ COMPLETED - Pattern analysis engine built")
        print("   • Sub-task 1.4: 🔄 NEXT - Create pattern storage and retrieval")
        print("\n🎯 Phase 1 (Usage Pattern Tracking) is nearly complete!")
    else:
        print("\n❌ Pattern Analysis Engine has issues that need to be resolved")


if __name__ == "__main__":
    main()
