#!/usr/bin/env python3
"""
Populate Enhanced Ignition Graph Database

Script to populate the Neo4j graph database with comprehensive enhanced Ignition
system functions, context variables, and relationships.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

import contextlib

from ignition.graph.client import IgnitionGraphClient
from ignition.graph.enhanced_populator import EnhancedIgnitionGraphPopulator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main function to populate enhanced graph database."""
    try:
        logger.info("🚀 Starting Enhanced Ignition Graph Database Population")

        # Connect to Neo4j
        client = IgnitionGraphClient()

        logger.info("Connecting to Neo4j database...")
        if not client.connect():
            logger.error("❌ Failed to connect to Neo4j database")
            logger.info(
                "💡 Make sure Neo4j is running: python scripts/utilities/start_graph_db.py"
            )
            return False

        logger.info("✅ Connected to Neo4j successfully")

        # Check if database already has data
        stats = client.get_database_stats()
        if stats["total_nodes"] > 0:
            logger.warning(f"⚠️ Database already contains {stats['total_nodes']} nodes")

            # Prompt user for confirmation
            response = (
                input("Do you want to clear existing data and reload? (y/N): ")
                .strip()
                .lower()
            )
            clear_first = response in ["y", "yes"]
        else:
            clear_first = False

        # Create enhanced populator
        populator = EnhancedIgnitionGraphPopulator(client)

        # Populate enhanced database
        logger.info("🔄 Populating enhanced database...")
        success = populator.populate_full_enhanced_database(clear_first=clear_first)

        if success:
            # Get final statistics
            final_stats = client.get_database_stats()

            logger.info("✅ Enhanced database population completed successfully!")
            logger.info("📊 Final Statistics:")
            logger.info(f"   • Total Nodes: {final_stats['total_nodes']}")
            logger.info(
                f"   • Total Relationships: {final_stats['total_relationships']}"
            )

            # Breakdown by node type
            if "node_counts" in final_stats:
                logger.info("   • Node Breakdown:")
                for node_type, count in final_stats["node_counts"].items():
                    logger.info(f"     - {node_type}: {count}")

            logger.info("🌐 Neo4j Browser: http://localhost:7474")
            logger.info("🔐 Credentials: neo4j / ignition-graph")

            return True
        else:
            logger.error("❌ Enhanced database population failed")
            return False

    except KeyboardInterrupt:
        logger.info("\n⏹️ Population interrupted by user")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during population: {e}")
        return False
    finally:
        # Close connection
        with contextlib.suppress(Exception):
            client.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
