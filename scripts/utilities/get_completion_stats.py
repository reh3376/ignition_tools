#!/usr/bin/env python3
"""
Get Enhanced Graph Database Completion Statistics

Script to track progress of implementing all 400+ Ignition system functions
in the Neo4j graph database.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from ignition.graph.client import IgnitionGraphClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Main function to get completion statistics."""
    try:
        logger.info("📊 Getting Enhanced Graph Database Statistics...")

        # Connect to Neo4j
        client = IgnitionGraphClient()

        if not client.connect():
            logger.error("❌ Failed to connect to Neo4j database")
            logger.info(
                "💡 Make sure Neo4j is running: python scripts/utilities/start_graph_db.py"
            )
            return False

        # Get total function count first
        total_result = client.execute_query(
            "MATCH (f:Function) RETURN count(f) as total"
        )
        total_functions = total_result[0]["total"]

        # Get function count by category
        result = client.execute_query(
            """
        MATCH (f:Function)-[:BELONGS_TO]->(c:Category)
        RETURN c.name as category, count(f) as function_count
        ORDER BY function_count DESC
        """
        )

        print("\n🔍 **Function Count by Category**:")
        for record in result:
            category = record["category"]
            count = record["function_count"]
            print(f"   • {category}: {count} functions")

        # Get overall statistics
        stats = client.get_database_stats()
        print("\n📈 **Overall Statistics**:")
        print(f"   • Total Functions: {total_functions}")
        print(f"   • Total Nodes: {stats['total_nodes']}")
        print(f"   • Total Relationships: {stats['total_relationships']}")

        # Calculate completion percentage
        target_functions = 400
        completion_percentage = (total_functions / target_functions) * 100
        print(
            f"   • Completion: {completion_percentage:.1f}% ({total_functions}/{target_functions})"
        )

        # Remaining functions
        remaining = target_functions - total_functions
        print(f"   • Remaining: {remaining} functions")

        # Get context distribution
        result = client.execute_query(
            """
        MATCH (f:Function)-[:AVAILABLE_IN]->(ctx:Context)
        RETURN ctx.name as context, count(f) as function_count
        ORDER BY function_count DESC
        """
        )

        print("\n🎯 **Function Distribution by Context**:")
        for record in result:
            context = record["context"]
            count = record["function_count"]
            print(f"   • {context}: {count} functions")

        # Progress bar
        bar_length = 50
        filled_length = int(bar_length * completion_percentage / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"\n📊 **Progress**: [{bar}] {completion_percentage:.1f}%")

        # Next recommendations
        print("\n🚀 **Next Steps**:")
        if completion_percentage < 25:
            if completion_percentage > 15:
                print("   • Task 1: Tag System Expansion ✅ COMPLETED!")
                print("   • Begin Task 2: Database System Expansion (30+ functions)")
            else:
                print("   • Focus on high-priority tasks (Tag System, Database System)")
                print("   • Complete Task 1: Tag System Expansion (25+ functions)")
        elif completion_percentage < 50:
            print("   • Continue with core systems (Device Communication)")
            print("   • Maintain quality standards and context validation")
        elif completion_percentage < 75:
            print("   • Add medium-priority systems (GUI, Perspective)")
            print("   • Focus on comprehensive coverage")
        else:
            print("   • Complete remaining low-priority systems")
            print("   • Focus on optimization and performance")

        print("\n🌐 **Neo4j Browser**: http://localhost:7474")
        print("🔐 **Credentials**: neo4j / ignition-graph")

        return True

    except Exception as e:
        logger.error(f"❌ Error getting statistics: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
