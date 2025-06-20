#!/usr/bin/env python3
"""Example: New Agent Initialization.

This script demonstrates how new agents or chat sessions should initialize
to automatically discover and connect to all available knowledge bases.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))


def main():
    """Demonstrate new agent initialization process."""
    print("🤖 NEW AGENT INITIALIZATION EXAMPLE")
    print("=" * 50)

    try:
        # Method 1: Simple initialization (recommended)
        print("\n📋 Method 1: Simple Initialization")
        print("-" * 30)

        from ignition.code_intelligence import initialize_agent_knowledge

        context = initialize_agent_knowledge()

        print(f"✅ Successfully connected to {len(context['knowledge_base_status'])} knowledge bases")
        print(f"🎯 Project: {context['project_context']['project_name']}")
        print(f"📊 Current Phase: {context['project_context']['current_phase']}")
        print(f"🛠️ Available Tools: {len(context['available_tools'])}")

        # Method 2: Manual discovery (for advanced use cases)
        print("\n📋 Method 2: Manual Discovery")
        print("-" * 30)

        from ignition.code_intelligence import KnowledgeDiscoverySystem

        discovery = KnowledgeDiscoverySystem()

        print("Available Knowledge Bases:")
        for kb in discovery.knowledge_bases:
            status_emoji = "✅" if kb.status == "available" else "❌" if kb.status == "error" else "⚠️"
            print(f"  {status_emoji} {kb.name}")
            print(f"     Type: {kb.type}")
            print(f"     Status: {kb.status}")
            if kb.record_count:
                print(f"     Records: {kb.record_count:,}")
            if kb.description:
                print(f"     Description: {kb.description}")
            print()

        # Method 3: Quick start (one-liner)
        print("\n📋 Method 3: Quick Start")
        print("-" * 30)

        from ignition.code_intelligence import quick_start

        quick_context = quick_start()
        print(f"✅ Quick start complete! Found {len(quick_context.get('knowledge_base_status', []))} knowledge bases")

        # Demonstrate accessing specific knowledge bases
        print("\n🔗 Connecting to Specific Knowledge Bases")
        print("-" * 40)

        # Neo4j connection example
        try:
            from ignition.code_intelligence.manager import CodeIntelligenceManager

            manager = CodeIntelligenceManager()
            if manager.client.is_connected():
                print("✅ Neo4j Graph Database: Connected")

                # Example query
                result = manager.client.execute_query("MATCH (n) RETURN count(n) as node_count")
                node_count = result[0]["node_count"]
                print(f"   📊 Total nodes in graph: {node_count:,}")
            else:
                print("⚠️ Neo4j Graph Database: Not connected")

        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")

        # Git integration example
        try:
            from ignition.code_intelligence.git_integration import GitIntegration

            GitIntegration(Path.cwd(), graph_client=None)
            print("✅ Git History Integration: Available")

            # Example: Get recent commits
            try:
                import subprocess

                result = subprocess.run(
                    ["git", "log", "--oneline", "-5"],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd(),
                )
                if result.returncode == 0:
                    print("   📝 Recent commits:")
                    for line in result.stdout.strip().split("\n")[:3]:
                        print(f"      {line}")
            except Exception:
                pass

        except Exception as e:
            print(f"❌ Git integration failed: {e}")

        # Refactoring tracking example
        try:
            from ignition.code_intelligence.refactoring_tracker import (
                RefactoringTracker,
            )

            tracker = RefactoringTracker(Path.cwd())
            stats = tracker.get_refactoring_statistics()
            print("✅ Refactoring Tracking: Available")
            print(f"   📊 Total operations tracked: {stats['operations']['total']}")
            print(f"   📈 Success rate: {stats['operations']['success_rate']:.1f}%")

        except Exception as e:
            print(f"❌ Refactoring tracking failed: {e}")

        # Show available CLI commands
        print("\n🛠️ Available CLI Commands")
        print("-" * 25)

        cli_commands = context["project_context"]["cli_commands"]
        print("Core refactoring commands:")
        for cmd in cli_commands[:6]:  # Show first 6
            print(f"  • {cmd}")

        print("\nAdvanced commands:")
        for cmd in cli_commands[6:]:  # Show remaining
            print(f"  • {cmd}")

        # Show quick usage examples
        print("\n💡 Quick Usage Examples")
        print("-" * 23)

        print("# Detect large files needing refactoring:")
        print("python -m src.ignition.code_intelligence.cli_commands refactor detect")
        print()
        print("# Analyze a specific file:")
        print("python -m src.ignition.code_intelligence.cli_commands refactor analyze path/to/file.py")
        print()
        print("# Get refactoring statistics:")
        print("python -m src.ignition.code_intelligence.cli_commands refactor statistics")

        print("\n🎉 AGENT INITIALIZATION COMPLETE!")
        print("=" * 50)
        print("Your agent now has access to:")
        print("✅ Project context and current state")
        print("✅ All available knowledge bases")
        print("✅ Connection instructions for each system")
        print("✅ CLI tools and usage examples")
        print("✅ Recent developments and capabilities")

        return context

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("\nFallback: Limited context mode")
        print("Some features may not be available.")
        return None


def demonstrate_context_usage(context):
    """Demonstrate how to use the context information."""
    if not context:
        return

    print("\n📖 CONTEXT USAGE EXAMPLES")
    print("=" * 30)

    # Access project information
    project_info = context["project_context"]
    print(f"Project Name: {project_info['project_name']}")
    print(f"Current Phase: {project_info['current_phase']}")
    print(f"Completed Phases: {', '.join(project_info['completed_phases'])}")

    # Check knowledge base status
    print("\nKnowledge Base Status:")
    for kb_status in context["knowledge_base_status"]:
        print(f"  {kb_status['name']}: {kb_status['status']}")

    # Show connection instructions
    if context["connection_instructions"]:
        print("\nConnection Instructions Available:")
        for system, _instructions in context["connection_instructions"].items():
            print(f"  • {system.title()}: Ready")

    # Show available tools
    print("\nAvailable Tools:")
    for tool in context["available_tools"]:
        print(f"  • {tool['name']}: {tool['purpose']}")


if __name__ == "__main__":
    # Run the initialization example
    context = main()

    # Demonstrate context usage
    if context:
        demonstrate_context_usage(context)

    print(f"\n💾 Context saved to: {Path.cwd() / '.agent_context.json'}")
    print("Future agents can load this context for faster initialization.")
