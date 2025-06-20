#!/usr/bin/env python3
"""Add Memory and curl MCP Configurations."""

import sys
from pathlib import Path

# Add parent directory to path to import mcp_config_manager
sys.path.append(str(Path(__file__).parent))

from mcp_config_manager import MCPConfigManager


def add_memory_and_curl_configs():
    """Add the Memory and curl configurations as provided."""
    manager = MCPConfigManager()

    # Memory configuration
    memory_config = {"mcpServers": {"memory": {"command": "docker", "args": ["run", "-i", "--rm", "mcp/memory"]}}}

    # curl configuration - based on the provided template
    # Note: This follows a different pattern than the other configs
    curl_config = {
        "mcpServers": {
            "curl": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "vonwig/curl:latest"],
            }
        }
    }

    manager.add_config("memory", memory_config)
    manager.add_config("curl", curl_config)
    manager.show_status()
    manager.update_test_script()

    print("\n✅ Memory and curl configurations added successfully!")
    print("   Note: Memory provides persistent storage, curl enables HTTP requests")
    return manager


if __name__ == "__main__":
    add_memory_and_curl_configs()
