#!/usr/bin/env python3
"""Test script for Neo4j and MCP service connectivity."""

import logging
import sys
from pathlib import Path

from ignition.graph.client import IgnitionGraphClient
from ignition.mcp.client import MCPClient

# Add src to Python path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_neo4j_connection() -> bool:
    """Test connection to Neo4j database.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        client = IgnitionGraphClient()
        # Test basic connection
        result = client.run_query("RETURN 1 as test")
        if result and result[0]["test"] == 1:
            logger.info("✅ Neo4j connection successful")
            return True
        logger.error("❌ Neo4j connection test failed")
        return False
    except Exception as e:
        logger.error(f"❌ Neo4j connection error: {e}")
        return False


def test_mcp_services() -> bool:
    """Test MCP service connectivity.

    Returns:
        bool: True if all services are accessible, False otherwise
    """
    try:
        client = MCPClient()

        # Test Neo4j Memory MCP
        memory_health = client.get_health("neo4j-memory")
        if not memory_health:
            logger.error("❌ Neo4j Memory MCP health check failed")
            return False
        logger.info("✅ Neo4j Memory MCP health check passed")

        # Test Neo4j Cypher MCP
        cypher_health = client.get_health("neo4j-cypher")
        if not cypher_health:
            logger.error("❌ Neo4j Cypher MCP health check failed")
            return False
        logger.info("✅ Neo4j Cypher MCP health check passed")

        return True
    except Exception as e:
        logger.error(f"❌ MCP service test error: {e}")
        return False


def main() -> int:
    """Run all connectivity tests.

    Returns:
        int: 0 if all tests pass, 1 otherwise
    """
    logger.info("Starting Neo4j and MCP service connectivity tests...")

    # Test Neo4j connection
    if not test_neo4j_connection():
        return 1

    # Test MCP services
    if not test_mcp_services():
        return 1

    logger.info("✅ All connectivity tests passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
