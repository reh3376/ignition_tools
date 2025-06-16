#!/usr/bin/env python3
"""Startup script for IGN Scripts.

This script ensures proper initialization of Neo4j and MCP clients
when starting a new Cursor session or chat.
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from ignition.graph.client import IgnitionGraphClient
from ignition.mcp.client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def initialize_neo4j() -> IgnitionGraphClient | None:
    """Initialize Neo4j client and verify connection.

    Returns:
        IgnitionGraphClient if successful, None otherwise
    """
    try:
        logger.info("Initializing Neo4j client...")
        client = IgnitionGraphClient()
        
        if not client.connect():
            logger.error("Failed to connect to Neo4j database")
            return None
            
        # Test connection with simple query
        result = client.run_query("RETURN 1 as test")
        if not result or result[0]["test"] != 1:
            logger.error("Neo4j connection test failed")
            return None
            
        logger.info("✅ Neo4j client initialized successfully")
        return client
        
    except Exception as e:
        logger.error(f"Error initializing Neo4j client: {e}")
        return None


def initialize_mcp() -> MCPClient | None:
    """Initialize MCP client and verify connection.

    Returns:
        MCPClient if successful, None otherwise
    """
    try:
        logger.info("Initializing MCP client...")
        client = MCPClient()
        
        # Test MCP API health
        mcp_health = client.get_health()
        if not mcp_health:
            logger.error("MCP API health check failed")
            return None
            
        # Test MCP Tools API health
        tools_health = client.get_health(is_tools=True)
        if not tools_health:
            logger.error("MCP Tools API health check failed")
            return None
            
        logger.info("✅ MCP client initialized successfully")
        return client
        
    except Exception as e:
        logger.error(f"Error initializing MCP client: {e}")
        return None


def main() -> bool:
    """Initialize all required clients.

    Returns:
        bool: True if all clients initialized successfully
    """
    logger.info("Starting IGN Scripts initialization...")
    
    # Initialize Neo4j
    neo4j_client = initialize_neo4j()
    if not neo4j_client:
        logger.error("❌ Neo4j initialization failed")
        return False
        
    # Initialize MCP
    mcp_client = initialize_mcp()
    if not mcp_client:
        logger.error("❌ MCP initialization failed")
        return False
        
    logger.info("✅ All clients initialized successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 