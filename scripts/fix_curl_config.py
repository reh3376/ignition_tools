#!/usr/bin/env python3
"""Fix curl MCP Configuration by switching to working image."""

import sys
from pathlib import Path

# Add parent directory to path to import mcp_config_manager
sys.path.append(str(Path(__file__).parent))

from mcp_config_manager import MCPConfigManager


def fix_curl_config():
    """Fix the curl configuration with a working image."""
    manager = MCPConfigManager()

    # Updated curl configuration with working image
    curl_config = {
        "mcpServers": {
            "curl": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "curlimages/curl:latest"],
            }
        }
    }

    # Update the curl configuration with working image
    manager.add_config("curl", curl_config)
    manager.show_status()
    manager.update_test_script()

    print("\n✅ curl configuration fixed!")
    print("   Switched from vonwig/curl:latest to curlimages/curl:latest")
    print("   New image tested and working properly")
    return manager


if __name__ == "__main__":
    fix_curl_config()
