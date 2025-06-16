#!/usr/bin/env python3
"""
Selective Restore from Neo4j Backup

This script restores missing data from a Neo4j backup while preserving
existing deployment pattern learning data.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from ignition.graph.backup_manager import Neo4jBackupManager
from ignition.graph.client import IgnitionGraphClient


def main():
    """Main function to perform selective restore."""
    print("🔄 Selective Neo4j Database Restore")
    print("=" * 50)

    # Connect to Neo4j
    client = IgnitionGraphClient()

    print("Connecting to Neo4j database...")
    if not client.connect():
        print("❌ Failed to connect to Neo4j database")
        print("💡 Make sure Neo4j is running: docker-compose up -d neo4j")
        return False

    print("✅ Connected to Neo4j successfully")

    # Create backup manager
    backup_manager = Neo4jBackupManager(client)

    # List available backups
    print("\n📋 Available backups:")
    backups = backup_manager.list_backups()

    if not backups:
        print("❌ No backup files found")
        return False

    for i, backup in enumerate(backups):
        print(f"  {i + 1}. {backup['filename']}")
        print(f"     Date: {backup.get('datetime', 'Unknown')}")
        print(f"     Reason: {backup.get('reason', 'Unknown')}")
        print(
            f"     Nodes: {backup.get('node_count', 0)}, Relationships: {backup.get('relationship_count', 0)}"
        )
        print()

    # Get current database statistics
    current_stats = client.get_database_stats()
    print(
        f"📊 Current database: {current_stats.get('total_nodes', 0)} nodes, {current_stats.get('total_relationships', 0)} relationships"
    )

    # Define labels to preserve (deployment pattern learning data)
    preserve_labels = [
        "DeploymentPattern",
        "DeploymentExecution",
        "EnvironmentAdaptation",
        "RollbackScenario",
        "DeploymentMetric",
    ]

    print(f"\n🛡️ Preserving existing data for labels: {preserve_labels}")

    # Ask user which backup to restore
    try:
        choice = input(
            f"\nSelect backup to restore (1-{len(backups)}) or 'q' to quit: "
        ).strip()

        if choice.lower() == "q":
            print("Operation cancelled")
            return True

        backup_index = int(choice) - 1
        if backup_index < 0 or backup_index >= len(backups):
            print("❌ Invalid selection")
            return False

        selected_backup = backups[backup_index]
        backup_filename = selected_backup["filename"]

        print(f"\n🔄 Starting selective restore from: {backup_filename}")

        # Perform selective restore
        success, message = backup_manager.selective_restore_from_backup(
            backup_file=backup_filename, preserve_labels=preserve_labels
        )

        if success:
            print(f"\n✅ {message}")

            # Get final statistics
            final_stats = client.get_database_stats()
            print("\n📊 Final database statistics:")
            print(f"   Total Nodes: {final_stats.get('total_nodes', 0)}")
            print(
                f"   Total Relationships: {final_stats.get('total_relationships', 0)}"
            )

            # Show node breakdown
            if "node_counts" in final_stats:
                print("\n📋 Node breakdown:")
                for node_type, count in final_stats["node_counts"].items():
                    print(f"   {node_type}: {count}")

            print("\n🌐 Neo4j Browser: http://localhost:7474")
            print("🔐 Credentials: neo4j / ignition-graph")

            return True
        else:
            print(f"\n❌ {message}")
            return False

    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        client.disconnect()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
