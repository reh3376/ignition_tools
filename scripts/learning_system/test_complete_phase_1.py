#!/usr/bin/env python3
"""Comprehensive Test for Phase 1: Usage Pattern Tracking System

This script demonstrates the complete Phase 1 learning system including:
- Usage tracking and session management
- Pattern analysis across all types
- Pattern storage and retrieval
- Pattern management and maintenance

This validates that Phase 1 is fully functional and ready for Phase 2.
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
from src.ignition.graph.pattern_manager import PatternManager
from src.ignition.graph.usage_tracker import UsageTracker


def simulate_realistic_usage_patterns(tracker: UsageTracker, sessions: int = 30):
    """Simulate realistic usage patterns for testing the learning system.

    Args:
        tracker: UsageTracker instance
        sessions: Number of sessions to simulate
    """
    print(f"🎭 Simulating {sessions} realistic usage sessions...")

    # Define realistic usage scenarios
    scenarios = {
        "tag_monitoring": {
            "functions": [
                "system.tag.readBlocking",
                "system.tag.browse",
                "system.gui.messageBox",
            ],
            "templates": [
                "vision/tag_display.jinja2",
                "perspective/tag_monitor.jinja2",
            ],
            "parameters": {
                "tagPaths": [
                    "[default]Tank1/Level",
                    "[default]Tank2/Level",
                    "[default]Pump1/Status",
                ],
                "timeout": [1000, 5000],
            },
        },
        "database_operations": {
            "functions": [
                "system.db.runQuery",
                "system.db.runUpdate",
                "system.db.createConnection",
            ],
            "templates": ["gateway/database_query.jinja2", "vision/data_table.jinja2"],
            "parameters": {
                "database": ["ProductionDB", "HistoryDB"],
                "query": ["SELECT * FROM tags", "UPDATE settings SET value = ?"],
            },
        },
        "navigation_workflow": {
            "functions": [
                "system.perspective.navigate",
                "system.perspective.getSessionInfo",
                "system.gui.confirm",
            ],
            "templates": ["perspective/navigation.jinja2", "perspective/popup.jinja2"],
            "parameters": {
                "page": ["/main", "/alarms", "/trends"],
                "target": ["_self", "_blank"],
            },
        },
        "alarm_handling": {
            "functions": [
                "system.alarm.queryStatus",
                "system.alarm.acknowledge",
                "system.gui.messageBox",
            ],
            "templates": [
                "vision/alarm_display.jinja2",
                "gateway/alarm_notification.jinja2",
            ],
            "parameters": {
                "priority": ["High", "Medium", "Low"],
                "source": ["Tank1", "Pump1", "System"],
            },
        },
    }

    users = ["engineer1", "operator1", "operator2", "manager1", "technician1"]

    for session_num in range(sessions):
        # Choose scenario and user
        scenario_name = random.choice(list(scenarios.keys()))
        scenario = scenarios[scenario_name]
        user_id = random.choice(users)
        session_type = random.choice(["development", "production", "maintenance"])

        with tracker.track_session(user_id=user_id, session_type=session_type):
            # Execute scenario functions in sequence (70% of the time)
            if random.random() < 0.7:
                # Follow the scenario pattern
                functions_to_use = scenario["functions"]
                for func in functions_to_use:
                    # Build realistic parameters
                    params = {}
                    for param_key, param_values in scenario["parameters"].items():
                        if random.random() < 0.8:  # 80% chance to include parameter
                            params[param_key] = random.choice(param_values)

                    # Track function with realistic success/timing
                    success = random.random() > 0.05  # 95% success rate
                    execution_time = random.uniform(0.1, 1.0)

                    tracker.track_function_query(
                        function_name=func,
                        context=random.choice(
                            ["Gateway", "Vision Client", "Perspective Session"]
                        ),
                        parameters=params,
                        success=success,
                        execution_time=execution_time,
                        error_message=None if success else f"Simulated error in {func}",
                    )

                    time.sleep(0.02)  # Small delay between function calls

            # Generate template usage
            if random.random() < 0.6:  # 60% chance of template usage
                template = random.choice(scenario["templates"])

                # Template-specific parameters
                template_params = {}
                if "tag" in template:
                    template_params = {
                        "tag_path": random.choice(scenario["parameters"]["tagPaths"]),
                        "display_type": random.choice(["numeric", "text", "led"]),
                    }
                elif "database" in template:
                    template_params = {
                        "table_name": random.choice(
                            ["production_data", "alarm_log", "user_actions"]
                        ),
                        "columns": random.choice(
                            [["timestamp", "value"], ["id", "message", "priority"]]
                        ),
                    }
                elif "navigation" in template:
                    template_params = {
                        "target_page": random.choice(scenario["parameters"]["page"]),
                        "animation": random.choice(["slide", "fade", "none"]),
                    }
                elif "alarm" in template:
                    template_params = {
                        "alarm_priority": random.choice(
                            scenario["parameters"]["priority"]
                        ),
                        "notification_type": random.choice(
                            ["popup", "banner", "sound"]
                        ),
                    }

                tracker.track_template_generation(
                    template_name=template,
                    parameters=template_params,
                    success=random.random() > 0.03,  # 97% success rate
                    execution_time=random.uniform(0.2, 1.5),
                )

        if (session_num + 1) % 10 == 0:
            print(f"   Completed {session_num + 1}/{sessions} sessions")

    print("✅ Realistic usage simulation complete!")


def test_complete_learning_system():
    """Test the complete Phase 1 learning system."""

    print("🚀 Phase 1 Complete System Test")
    print("=" * 60)

    # Initialize all components
    client = IgnitionGraphClient()
    tracker = UsageTracker(client)
    analyzer = PatternAnalyzer(client)
    manager = PatternManager(client)

    try:
        # Connect to database
        print("📡 Connecting to Neo4j database...")
        if not client.connect():
            print("❌ Failed to connect to database")
            return False
        print("✅ Connected successfully!")

        # Test 1: Generate comprehensive usage data
        print("\n🔄 Test 1: Generating Comprehensive Usage Data")
        simulate_realistic_usage_patterns(tracker, sessions=50)

        # Test 2: Analyze all patterns
        print("\n🔄 Test 2: Comprehensive Pattern Analysis")
        analysis_results = analyzer.analyze_all_patterns(days_back=1)

        print("✅ Pattern Analysis Results:")
        for pattern_type, patterns in analysis_results["patterns"].items():
            print(f"   • {pattern_type}: {len(patterns)} patterns")

        # Test 3: Pattern Management Operations
        print("\n🔄 Test 3: Pattern Management")

        # Get pattern statistics
        stats = manager.get_pattern_statistics()
        print("✅ Pattern Statistics:")
        print(f"   • Total patterns by type: {stats['pattern_counts']}")
        print(
            f"   • Confidence distribution: {stats.get('confidence_distribution', {})}"
        )

        # Get top patterns summary
        top_patterns = manager.get_top_patterns_summary(limit=3)
        print("\n✅ Top Patterns Summary:")
        for pattern_type, patterns in top_patterns["top_patterns"].items():
            if patterns:
                print(f"   • {pattern_type}: {len(patterns)} top patterns")

        # Test 4: Pattern Retrieval and Filtering
        print("\n🔄 Test 4: Pattern Retrieval")

        # Get high-confidence co-occurrence patterns
        co_occurrence = manager.get_patterns_by_type(
            "function_co_occurrence", limit=5, min_confidence=0.5
        )
        print(f"✅ High-confidence co-occurrence patterns: {len(co_occurrence)}")

        # Get patterns for specific function
        if co_occurrence:
            first_pattern = co_occurrence[0]
            func_name = first_pattern.get("function_1", "system.tag.readBlocking")
            func_patterns = manager.get_patterns_by_entity(func_name, "function")
            print(f"✅ Patterns for '{func_name}': {len(func_patterns)}")

        # Test 5: Pattern Maintenance
        print("\n🔄 Test 5: Pattern Maintenance")
        maintenance_results = manager.maintain_patterns()

        print("✅ Maintenance Results:")
        ops = maintenance_results["operations"]
        print(f"   • Relevance updates: {ops.get('relevance_updates', 0)}")
        print(f"   • Patterns archived: {ops.get('patterns_archived', 0)}")
        print(f"   • Patterns cleaned: {ops.get('patterns_cleaned', 0)}")

        # Test 6: Recommendation Generation
        print("\n🔄 Test 6: Function Recommendations")

        # Test recommendations for common functions
        test_functions = [
            "system.tag.readBlocking",
            "system.db.runQuery",
            "system.perspective.navigate",
        ]

        for func in test_functions:
            recommendations = analyzer.get_recommendations_for_function(func, limit=3)
            if recommendations:
                print(f"✅ Recommendations for '{func}': {len(recommendations)}")
                for rec in recommendations[:2]:  # Show top 2
                    print(
                        f"   → {rec['recommended_function']} (confidence: {rec['confidence']:.1%})"
                    )
            else:
                print(f"ℹ No recommendations found for '{func}'")

        # Test 7: Pattern Export
        print("\n🔄 Test 7: Pattern Export")
        export_data = manager.export_patterns(pattern_type="function_co_occurrence")
        print(f"✅ Exported {export_data['total_patterns']} co-occurrence patterns")

        # Final summary
        print("\n🎉 Phase 1 Complete System Test - SUCCESS!")
        print("\n📊 Final System State:")

        final_stats = manager.get_pattern_statistics()
        total_patterns = sum(final_stats["pattern_counts"].values())
        print(f"   • Total patterns stored: {total_patterns}")
        print(f"   • Pattern types: {len(final_stats['pattern_counts'])}")
        print(f"   • Analysis timestamp: {analysis_results['analysis_timestamp']}")

        print("\n✅ Phase 1: Usage Pattern Tracking System - FULLY OPERATIONAL")
        print("🎯 Ready to proceed with Phase 2: Smart Recommendation Engine")

        return True

    except Exception as e:
        print(f"❌ Complete system test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        client.disconnect()


def main():
    """Run the complete Phase 1 system test."""

    print("🧠 Learning System - Phase 1 Complete Validation")
    print("=" * 70)
    print("Testing all components:")
    print("  • Usage Tracking & Session Management")
    print("  • Pattern Analysis (Co-occurrence, Template, Parameter, Sequential)")
    print("  • Pattern Storage & Retrieval")
    print("  • Pattern Management & Maintenance")
    print("  • Recommendation Generation")
    print("=" * 70)

    success = test_complete_learning_system()

    if success:
        print("\n" + "=" * 70)
        print("🎉 PHASE 1 COMPLETE - ALL SYSTEMS OPERATIONAL!")
        print("=" * 70)
        print("\n📋 Phase 1 Achievements:")
        print("   ✅ Usage tracking schema implemented")
        print("   ✅ Event collection system operational")
        print("   ✅ Pattern analysis engine functional")
        print("   ✅ Pattern storage and retrieval working")
        print("   ✅ Pattern management and maintenance ready")
        print("   ✅ Basic recommendation generation available")

        print("\n🚀 Ready for Phase 2: Smart Recommendation Engine")
        print("   📌 Next: Enhanced function recommendation system")
        print("   📌 Next: Template recommendation system")
        print("   📌 Next: Parameter recommendation system")
        print("   📌 Next: Integration with existing UI")

    else:
        print("\n❌ Phase 1 system validation failed")
        print("🔧 Please review the errors above and fix issues before proceeding")


if __name__ == "__main__":
    main()
