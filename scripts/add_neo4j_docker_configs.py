#!/usr/bin/env python3
"""Add Neo4j Docker MCP Configurations."""

import sys
from pathlib import Path

# Add parent directory to path to import mcp_config_manager
sys.path.append(str(Path(__file__).parent))

from mcp_config_manager import MCPConfigManager


def add_neo4j_docker_configs():
    """Add the Neo4j Docker configurations as provided."""
    manager = MCPConfigManager()

    # Neo4j Cypher Docker config
    neo4j_cypher_config = {
        "mcpServers": {
            "neo4j-cypher": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "-e",
                    "NEO4J_URL",
                    "-e",
                    "NEO4J_USERNAME",
                    "-e",
                    "NEO4J_PASSWORD",
                    "mcp/neo4j-cypher",
                ],
                "env": {
                    "NEO4J_URL": "bolt://host.docker.internal:7687",
                    "NEO4J_USERNAME": "${NEO4J_USERNAME}",
                    "NEO4J_PASSWORD": "${NEO4J_PASSWORD}",
                },
            }
        }
    }

    # Neo4j Memory Docker config
    neo4j_memory_config = {
        "mcpServers": {
            "neo4j-memory": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "-e",
                    "NEO4J_URL",
                    "-e",
                    "NEO4J_USERNAME",
                    "-e",
                    "NEO4J_PASSWORD",
                    "mcp/neo4j-memory",
                ],
                "env": {
                    "NEO4J_URL": "bolt://host.docker.internal:7687",
                    "NEO4J_USERNAME": "${NEO4J_USERNAME}",
                    "NEO4J_PASSWORD": "${NEO4J_PASSWORD}",
                },
            }
        }
    }

    manager.add_config("neo4j_cypher_docker", neo4j_cypher_config)
    manager.add_config("neo4j_memory_docker", neo4j_memory_config)
    manager.show_status()
    manager.update_test_script()

    print("\n✅ Neo4j Docker configurations added successfully!")
    print("   Note: Uses host.docker.internal for Neo4j connectivity")
    return manager


if __name__ == "__main__":
    add_neo4j_docker_configs()
