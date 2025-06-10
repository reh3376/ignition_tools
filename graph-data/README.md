# Graph Database Data Directory

This directory contains the persistent storage for the Neo4j graph database that serves as the AI Assistant's long-term memory system.

## Directory Structure

- `data/`: Neo4j database files (persistent storage)
- `logs/`: Neo4j system logs
- `import/`: Files for importing data into the graph
- `plugins/`: Neo4j plugins (APOC, etc.)

## Purpose

The graph database stores:
- 400+ Ignition system functions with context availability
- Script templates and their relationships
- Context mappings (Gateway, Vision, Perspective)
- Parameter availability by script type
- Configuration patterns and examples
- Function compatibility matrices

## Usage

This directory is automatically managed by Docker Compose. The data persists between container restarts, ensuring AI assistants maintain knowledge across conversations.

## Backup

The entire `graph-data/` directory should be backed up regularly to preserve the knowledge base.

## Access

- Neo4j Browser: http://localhost:7474
- Credentials: neo4j/ignition-graph
- Bolt Protocol: bolt://localhost:7687
