#!/usr/bin/env python3
"""
Task 16 Implementation Runner

Executes the Task 16 SFC & Recipe Management system implementation
and populates the Neo4j graph database with all functions.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.tasks.task_16_sfc_recipe_system import create_task_16_functions


def main():
    """Main execution function."""
    client = None
    try:
        # Connect to Neo4j
        client = IgnitionGraphClient()
        client.connect()
        print("✅ Connected to Neo4j successfully")

        # Create Task 16 functions
        print("\n🚀 Starting Task 16 implementation...")
        result = create_task_16_functions(client)

        # Display results
        print("\n=== Task 16: SFC & Recipe Management - Implementation Results ===")
        print(
            f'Total functions created: {result["task_16_summary"]["total_functions"]}'
        )
        print(f'Target met: {result["task_16_summary"]["target_met"]}')
        print("\nFunction categories:")
        for category, count in result["task_16_summary"]["categories"].items():
            print(f"  - {category}: {count} functions")

        # List created functions
        print("\n📋 Created Functions:")
        for func_key, func_data in result["functions"].items():
            print(f'  ✓ {func_data.get("name", func_key)}')

        print("\n🎉 Task 16 implementation completed successfully!")
        print("📊 Graph database updated with SFC & Recipe Management functions")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        if client:
            client.disconnect()
            print("🔐 Neo4j connection closed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
