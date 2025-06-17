#!/usr/bin/env python3
"""Add GitHub Official MCP Configuration."""

import sys
from pathlib import Path

# Add parent directory to path to import mcp_config_manager
sys.path.append(str(Path(__file__).parent))

from mcp_config_manager import MCPConfigManager


def add_github_official():
    """Add the GitHub Official configuration as provided."""
    manager = MCPConfigManager()

    github_official_config = {
        "mcpServers": {
            "github-official": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "-e",
                    "GITHUB_PERSONAL_ACCESS_TOKEN",
                    "mcp/github-mcp-server",
                ],
                "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"},
            }
        }
    }

    manager.add_config("github_official", github_official_config)
    manager.show_status()
    manager.update_test_script()

    print("\n✅ GitHub Official configuration added successfully!")
    print("   Note: Requires GITHUB_TOKEN environment variable")
    return manager


if __name__ == "__main__":
    add_github_official()
