#!/usr/bin/env python3
"""Add Desktop Commander MCP Configuration."""

import sys
from pathlib import Path

# Add parent directory to path to import mcp_config_manager
sys.path.append(str(Path(__file__).parent))

from mcp_config_manager import MCPConfigManager


def add_desktop_commander():
    """Add the Desktop Commander configuration as provided."""
    manager = MCPConfigManager()

    desktop_commander_config = {
        "mcpServers": {
            "desktop-commander": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "mcp/desktop-commander"],
            }
        }
    }

    manager.add_config("desktop_commander", desktop_commander_config)
    manager.show_status()
    manager.update_test_script()

    print("\n✅ Desktop Commander configuration added successfully!")
    return manager


if __name__ == "__main__":
    add_desktop_commander()
