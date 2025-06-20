#!/usr/bin/env python3
"""
Periodic Health Check for Enhanced Graph Database

Lightweight health monitoring script to run periodically during development.
Provides quick validation without the full test suite overhead.
"""

import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from ignition.graph.client import IgnitionGraphClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class HealthChecker:
    """Lightweight health monitoring for the graph database."""

    def __init__(self):
        self.client = IgnitionGraphClient()

    def run_health_check(self) -> bool:
        """Run quick health check and return status."""
        print("🏥 **GRAPH DATABASE HEALTH CHECK**")
        print(f"📅 **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        try:
            # Test 1: Database connectivity
            if not self.client.connect():
                print("❌ **Database Connection**: FAILED")
                return False
            print("✅ **Database Connection**: OK")

            # Test 2: Basic node counts
            stats = self.client.get_database_stats()
            total_nodes = stats["total_nodes"]
            total_relationships = stats["total_relationships"]

            if total_nodes < 100:
                print(f"⚠️ **Node Count**: {total_nodes} (Warning: Low count)")
            else:
                print(f"✅ **Node Count**: {total_nodes}")

            if total_relationships < 200:
                print(f"⚠️ **Relationship Count**: {total_relationships} (Warning: Low count)")
            else:
                print(f"✅ **Relationship Count**: {total_relationships}")

            # Test 3: Function count validation
            result = self.client.execute_query("MATCH (f:Function) RETURN count(f) as total")
            function_count = result[0]["total"]

            if function_count < 60:
                print(f"⚠️ **Function Count**: {function_count} (Warning: Expected 60+)")
            else:
                print(f"✅ **Function Count**: {function_count}")

            # Test 4: Context relationships
            result = self.client.execute_query(
                """
            MATCH (f:Function)-[:AVAILABLE_IN]->(c:Context)
            RETURN c.name as context, count(f) as functions
            ORDER BY functions DESC
            """
            )

            context_health = True
            for record in result:
                context = record["context"]
                count = record["functions"]
                if count == 0:
                    print(f"❌ **{context} Context**: No functions")
                    context_health = False
                else:
                    print(f"✅ **{context} Context**: {count} functions")

            # Test 5: Category distribution
            result = self.client.execute_query(
                """
            MATCH (f:Function)-[:BELONGS_TO]->(c:Category)
            RETURN c.name as category, count(f) as functions
            ORDER BY functions DESC
            LIMIT 3
            """
            )

            print("\n📊 **Top Categories**:")
            for record in result:
                category = record["category"]
                count = record["functions"]
                print(f"   • {category}: {count} functions")

            # Test 6: Quick performance check
            start_time = time.time()
            self.client.execute_query(
                """
            MATCH (f:Function)-[:BELONGS_TO]->(c:Category)
            RETURN count(f)
            """
            )
            query_time = time.time() - start_time

            if query_time > 1.0:
                print(f"⚠️ **Query Performance**: {query_time:.3f}s (Warning: Slow)")
            else:
                print(f"✅ **Query Performance**: {query_time:.3f}s")

            # Test 7: Task 1 validation (if completed)
            result = self.client.execute_query(
                """
            MATCH (f:Function)-[:BELONGS_TO]->(c:Category {name: "tag"})
            RETURN count(f) as tag_count
            """
            )
            tag_count = result[0]["tag_count"]

            if tag_count >= 25:
                print(f"✅ **Task 1 Status**: Complete ({tag_count} tag functions)")
            else:
                print(f"⏳ **Task 1 Status**: In Progress ({tag_count} tag functions)")

            print("\n💾 **Database File**: /var/lib/neo4j/data")
            print("🌐 **Browser Access**: http://localhost:7474")
            print("🔐 **Credentials**: neo4j / ignition-graph")

            return context_health

        except Exception as e:
            print(f"❌ **Health Check Failed**: {e!s}")
            return False


def main():
    """Main health check function."""
    checker = HealthChecker()

    if checker.run_health_check():
        print("\n🎉 **Overall Status**: HEALTHY")
        return True
    else:
        print("\n⚠️ **Overall Status**: ISSUES DETECTED")
        print("💡 **Recommendation**: Run full test suite for details")
        print("   python scripts/testing/test_graph_functions.py")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
