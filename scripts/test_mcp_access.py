#!/usr/bin/env python3
"""Test MCP Access Script.

This script verifies access to MCP Docker services and tests basic functionality.
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from src.ignition.mcp.client import MCPClient  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_mcp_access() -> bool:
    """Test access to MCP services."""
    try:
        # Initialize MCP client
        client = MCPClient()
        logger.info("MCP Client initialized")

        # Test MCP API health
        mcp_health = client.get_health()
        logger.info(f"MCP API Health: {mcp_health}")

        # Test MCP Tools API health
        tools_health = client.get_health(is_tools=True)
        logger.info(f"MCP Tools API Health: {tools_health}")

        # Get MCP status
        mcp_status = client.get_mcp_status()
        logger.info(f"MCP Status: {mcp_status}")

        # Get MCP Tools status
        tools_status = client.get_tools_status()
        logger.info(f"MCP Tools Status: {tools_status}")

        # Test MCP command execution
        result = client.execute_mcp_command("test", {"test_param": "test_value"})
        logger.info(f"Test Command Result: {result}")

        # Get recent logs
        mcp_logs = client.get_mcp_logs(limit=5)
        logger.info(f"Recent MCP Logs: {mcp_logs}")

        tools_logs = client.get_tools_logs(limit=5)
        logger.info(f"Recent MCP Tools Logs: {tools_logs}")

        logger.info("✅ MCP access tests completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ MCP access test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_mcp_access()
    sys.exit(0 if success else 1)
