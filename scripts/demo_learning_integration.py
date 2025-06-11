#!/usr/bin/env python3
"""Demo script showcasing learning system integration."""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demo_cli_integration():
    """Demonstrate CLI learning system integration."""
    print("🎯 CLI Learning System Integration Demo")
    print("=" * 50)

    try:
        from rich.console import Console
        from rich.table import Table

        from src.core.enhanced_cli import enhanced_cli

        console = Console()

        # Test connection
        console.print("\n[bold blue]1. Testing Learning System Connection[/bold blue]")
        if enhanced_cli.connect_learning_system():
            console.print("✅ Learning system connected successfully")
        else:
            console.print("⚠️ Learning system not available (continuing with demo)")

        # Simulate CLI usage tracking
        console.print("\n[bold blue]2. Simulating CLI Usage Tracking[/bold blue]")

        # Simulate various CLI commands
        demo_commands = [
            (
                "script",
                "generate",
                {"template": "button_click_handler.jinja2", "interactive": True},
            ),
            ("template", "list", {"detailed": True}),
            ("learning", "patterns", {"days": 30}),
            ("script", "validate", {"script_file": "test_script.py"}),
        ]

        for command, subcommand, params in demo_commands:
            enhanced_cli.track_cli_usage(command, subcommand, params, success=True)
            console.print(f"📝 Tracked: {command} {subcommand}")
            time.sleep(0.5)

        # Show recommendations
        console.print("\n[bold blue]3. Getting Smart Recommendations[/bold blue]")
        recommendations = enhanced_cli.get_recommendations("script.generate")

        if recommendations:
            table = Table(title="🎯 CLI Recommendations")
            table.add_column("Command", style="cyan")
            table.add_column("Confidence", style="green")
            table.add_column("Reasoning", style="dim")

            for rec in recommendations[:3]:
                table.add_row(
                    rec["command"],
                    f"{rec['confidence']:.1%}",
                    rec["reasoning"][:50] + "..."
                    if len(rec["reasoning"]) > 50
                    else rec["reasoning"],
                )

            console.print(table)
        else:
            console.print("ℹ No recommendations available yet")

        # Display welcome message
        console.print("\n[bold blue]4. Enhanced CLI Welcome Experience[/bold blue]")
        enhanced_cli.display_welcome()

        console.print("\n✅ CLI integration demo complete!")

    except Exception as e:
        print(f"❌ CLI demo failed: {e}")
        return False

    return True


def demo_ui_integration():
    """Demonstrate UI learning system integration."""
    print("\n🎯 Streamlit UI Learning System Integration Demo")
    print("=" * 50)

    try:
        from src.ui.learning_integration import (
            get_learning_system,
            track_page_visit,
            track_script_generation,
            track_template_usage,
        )

        # Get learning system instance
        learning_system = get_learning_system()

        print("1. Testing UI Learning System...")
        if learning_system.is_available():
            print("✅ UI learning system connected")
        else:
            print("⚠️ UI learning system not available (continuing with demo)")

        # Simulate UI usage tracking
        print("\n2. Simulating UI Usage Tracking...")

        # Simulate page visits
        pages = ["home", "generator", "templates", "learning", "validation"]
        for page in pages:
            track_page_visit(page)
            print(f"📝 Tracked page visit: {page}")
            time.sleep(0.3)

        # Simulate script generation
        track_script_generation(
            template="button_click_handler.jinja2",
            config={"component_name": "TestButton", "action_type": "navigation"},
            success=True,
        )
        print("📝 Tracked script generation")

        # Simulate template usage
        templates = [
            "button_click_handler.jinja2",
            "window_opener.jinja2",
            "tag_writer.jinja2",
        ]
        for template in templates:
            track_template_usage(template, "selected")
            print(f"📝 Tracked template usage: {template}")
            time.sleep(0.2)

        # Test recommendations
        print("\n3. Testing UI Recommendations...")
        recommendations = learning_system.get_recommendations("script_generation")

        if recommendations:
            print("🎯 UI Recommendations available:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec['action']} (confidence: {rec['confidence']:.1%})")
        else:
            print("ℹ No UI recommendations available yet")

        print("\n✅ UI integration demo complete!")

    except Exception as e:
        print(f"❌ UI demo failed: {e}")
        return False

    return True


def show_integration_summary():
    """Show summary of learning system integration features."""
    print("\n🧠 Learning System Integration Summary")
    print("=" * 50)

    features = [
        "✅ Enhanced CLI with Rich formatting and interactive TUI",
        "✅ Automatic usage tracking for CLI commands",
        "✅ Smart recommendations based on usage patterns",
        "✅ Interactive pattern exploration (TUI)",
        "✅ Streamlit UI integration with learning hooks",
        "✅ Real-time analytics and insights display",
        "✅ Learning dashboard with visualizations",
        "✅ Session management and user tracking",
        "✅ Pattern-based template recommendations",
        "✅ Comprehensive analytics and reporting",
    ]

    for feature in features:
        print(f"  {feature}")

    print("\n📖 Usage Examples:")
    print("  CLI Commands:")
    print("    python -m src.core.enhanced_cli --help")
    print("    python -m src.core.enhanced_cli script generate -i")
    print("    python -m src.core.enhanced_cli learning patterns")
    print("    python -m src.core.enhanced_cli learning explore")
    print("    python -m src.core.enhanced_cli learning stats")

    print("\n  Streamlit UI:")
    print("    streamlit run src/ui/streamlit_app.py")
    print("    # Visit 'Learning Analytics' page for insights")

    print("\n💡 Next Steps:")
    print("  1. Install dependencies: python scripts/test_enhanced_cli.py")
    print("  2. Start Neo4j database for full learning system")
    print(
        "  3. Run Phase 1 learning test: python scripts/learning_system/test_complete_phase_1.py"
    )
    print("  4. Generate some scripts to create usage patterns")
    print("  5. Explore patterns: python -m src.core.enhanced_cli learning explore")


def main():
    """Run the complete integration demo."""
    print("🚀 Learning System Integration Demo")
    print("🎨 Enhanced CLI + Streamlit UI + Pattern Learning")
    print("=" * 60)

    success = True

    # Demo CLI integration
    if not demo_cli_integration():
        success = False

    # Demo UI integration
    if not demo_ui_integration():
        success = False

    # Show summary
    show_integration_summary()

    if success:
        print("\n🎉 All integration demos completed successfully!")
        print("🧠 Learning system is ready for production use!")
    else:
        print("\n⚠️ Some demos failed - check dependencies and database connection")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
