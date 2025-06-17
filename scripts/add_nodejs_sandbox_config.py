#!/usr/bin/env python3
"""Add Node.js Code Sandbox MCP Configuration."""

import sys
from pathlib import Path

# Add parent directory to path to import mcp_config_manager
sys.path.append(str(Path(__file__).parent))

from mcp_config_manager import MCPConfigManager


def add_nodejs_sandbox():
    """Add the Node.js Code Sandbox configuration as provided."""
    manager = MCPConfigManager()

    nodejs_sandbox_config = {
        "mcpServers": {
            "node-code-sandbox": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "mcp/node-code-sandbox"],
            }
        }
    }

    manager.add_config("nodejs_sandbox", nodejs_sandbox_config)
    manager.show_status()
    manager.update_test_script()

    print("\n✅ Node.js Code Sandbox configuration added successfully!")
    return manager


if __name__ == "__main__":
    add_nodejs_sandbox()
