#!/usr/bin/env python3
"""Neo4j Database Backup Manager for IGN Scripts.

This module provides comprehensive backup and restore functionality for the Neo4j
learning system database, including automated backup creation, restoration for
new installations, and lifecycle management.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.ignition.graph.client import IgnitionGraphClient


class Neo4jBackupManager:
    """Manages Neo4j database backups for the IGN Scripts learning system."""

    def __init__(self, graph_client: IgnitionGraphClient | None = None):
        """Initialize the backup manager.

        Args:
            graph_client: Optional graph client instance. If None, creates new one.
        """
        self.client = graph_client or IgnitionGraphClient()
        self.backup_dir = Path("neo4j/fullbackup")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.max_backups = 1  # Only keep the most recent backup
        self.backup_file_pattern = "ign_scripts_db_backup_{timestamp}.json"
        self.metadata_file = "backup_metadata.json"

    def create_full_backup(self, reason: str = "Manual backup") -> tuple[bool, str]:
        """Create a full database backup.

        Args:
            reason: Reason for creating the backup (for metadata)

        Returns:
            Tuple of (success, backup_file_path or error_message)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = self.backup_file_pattern.format(timestamp=timestamp)
            backup_path = self.backup_dir / backup_filename

            print(f"Creating Neo4j backup: {backup_filename}")

            # Connect to database if not already connected
            if not self.client.is_connected and not self.client.connect():
                return False, "Failed to connect to Neo4j database"

            # Extract all data from the database
            backup_data = self._extract_database_data()

            # Create metadata
            metadata = {
                "timestamp": timestamp,
                "datetime": datetime.now().isoformat(),
                "reason": reason,
                "node_count": backup_data.get("statistics", {}).get("node_count", 0),
                "relationship_count": backup_data.get("statistics", {}).get(
                    "relationship_count", 0
                ),
                "version": "1.0.0",
                "backup_type": "full",
                "source": "IGN Scripts Learning System",
            }

            # Save backup data
            backup_content = {"metadata": metadata, "data": backup_data}

            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(backup_content, f, indent=2, default=str)

            # Update backup metadata file
            self._update_backup_metadata(backup_filename, metadata)

            # Clean up old backups (keep only the most recent)
            self._cleanup_old_backups()

            print(f"✅ Backup created successfully: {backup_path}")
            return True, str(backup_path)

        except Exception as e:
            error_msg = f"Failed to create backup: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg

    def restore_from_backup(self, backup_file: str | None = None) -> tuple[bool, str]:
        """Restore database from backup.

        Args:
            backup_file: Specific backup file to restore from. If None, uses most recent.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Determine backup file to use
            if backup_file is None:
                backup_file = self._get_latest_backup()
                if not backup_file:
                    return False, "No backup files found"

            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                return False, f"Backup file not found: {backup_file}"

            print(f"Restoring from backup: {backup_file}")

            # Load backup data
            with open(backup_path, encoding="utf-8") as f:
                backup_content = json.load(f)

            metadata = backup_content.get("metadata", {})
            data = backup_content.get("data", {})

            print(f"Backup info: {metadata.get('datetime')} - {metadata.get('reason')}")
            print(
                f"Data: {metadata.get('node_count', 0)} nodes, {metadata.get('relationship_count', 0)} relationships"
            )

            # Connect to database
            if not self.client.is_connected and not self.client.connect():
                return False, "Failed to connect to Neo4j database"

            # Clear existing data (with confirmation in production)
            self._clear_database()

            # Restore data
            success = self._restore_database_data(data)

            if success:
                print("✅ Database restored successfully")
                return True, f"Database restored from {backup_file}"
            else:
                return False, "Failed to restore database data"

        except Exception as e:
            error_msg = f"Failed to restore backup: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg

    def auto_backup_on_significant_changes(self) -> bool:
        """Check if database has significant changes and create backup if needed.

        Returns:
            True if backup was created, False otherwise
        """
        try:
            # Get current database statistics
            current_stats = self._get_database_statistics()

            # Get last backup statistics
            last_backup_stats = self._get_last_backup_statistics()

            # Determine if backup is needed
            if self._should_create_backup(current_stats, last_backup_stats):
                success, _ = self.create_full_backup(
                    "Automatic backup - significant changes detected"
                )
                return success

            return False

        except Exception as e:
            print(f"❌ Auto-backup check failed: {e}")
            return False

    def list_backups(self) -> list[dict[str, Any]]:
        """List all available backups with metadata.

        Returns:
            List of backup information dictionaries
        """
        backups = []

        # Check metadata file
        metadata_file = self.backup_dir / self.metadata_file
        if metadata_file.exists():
            try:
                with open(metadata_file, encoding="utf-8") as f:
                    metadata = json.load(f)
                    backups = metadata.get("backups", [])
            except Exception as e:
                print(f"❌ Failed to read backup metadata: {e}")

        # Also scan directory for backup files
        for backup_file in self.backup_dir.glob("ign_scripts_db_backup_*.json"):
            filename = backup_file.name
            # Check if already in metadata
            if not any(b.get("filename") == filename for b in backups):
                try:
                    with open(backup_file, encoding="utf-8") as f:
                        content = json.load(f)
                        metadata = content.get("metadata", {})
                        metadata["filename"] = filename
                        metadata["file_size"] = backup_file.stat().st_size
                        backups.append(metadata)
                except Exception:
                    pass

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return backups

    def get_backup_info(self, backup_file: str) -> dict[str, Any] | None:
        """Get detailed information about a specific backup.

        Args:
            backup_file: Name of the backup file

        Returns:
            Backup information dictionary or None if not found
        """
        try:
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                return None

            with open(backup_path, encoding="utf-8") as f:
                content = json.load(f)

            info = content.get("metadata", {})
            info["filename"] = backup_file
            info["file_size"] = backup_path.stat().st_size
            info["file_path"] = str(backup_path)

            return info

        except Exception as e:
            print(f"❌ Failed to get backup info: {e}")
            return None

    def _extract_database_data(self) -> dict[str, Any]:
        """Extract all data from the Neo4j database."""
        data = {"nodes": [], "relationships": [], "statistics": {}}

        try:
            # Extract all nodes
            node_query = """
            MATCH (n)
            RETURN n, labels(n) as labels, elementId(n) as node_id
            """
            nodes_result = self.client.execute_query(node_query)

            for record in nodes_result:
                # Extract node properties - node is already a dictionary
                node = record["n"]
                node_data = node.copy() if isinstance(node, dict) else {}
                node_data["_labels"] = record["labels"]
                node_data["_id"] = record["node_id"]
                data["nodes"].append(node_data)

            # Extract all relationships
            rel_query = """
            MATCH (a)-[r]->(b)
            RETURN r, type(r) as rel_type, elementId(r) as rel_id,
                   elementId(a) as start_id, elementId(b) as end_id
            """
            rels_result = self.client.execute_query(rel_query)

            for record in rels_result:
                # Extract relationship properties - relationship is already a dictionary
                rel = record["r"]
                rel_data = rel.copy() if isinstance(rel, dict) else {}
                rel_data["_type"] = record["rel_type"]
                rel_data["_id"] = record["rel_id"]
                rel_data["_start_id"] = record["start_id"]
                rel_data["_end_id"] = record["end_id"]
                data["relationships"].append(rel_data)

            # Get statistics
            data["statistics"] = self._get_database_statistics()

            print(
                f"Extracted {len(data['nodes'])} nodes and {len(data['relationships'])} relationships"
            )

        except Exception as e:
            print(f"❌ Failed to extract database data: {e}")
            raise

        return data

    def _restore_database_data(self, data: dict[str, Any]) -> bool:
        """Restore data to the Neo4j database."""
        try:
            # Create nodes first
            nodes = data.get("nodes", [])
            node_id_mapping = {}  # Map old IDs to new nodes

            print(f"Restoring {len(nodes)} nodes...")
            for node_data in nodes:
                old_id = node_data.pop("_id", None)
                labels = node_data.pop("_labels", [])

                # Create node with labels
                labels_str = ":".join(labels) if labels else "Node"
                create_query = (
                    f"CREATE (n:{labels_str} $props) RETURN elementId(n) as new_id"
                )

                result = self.client.execute_query(create_query, {"props": node_data})
                if result:
                    new_id = result[0]["new_id"]
                    node_id_mapping[old_id] = new_id

            # Create relationships
            relationships = data.get("relationships", [])
            print(f"Restoring {len(relationships)} relationships...")

            for rel_data in relationships:
                old_start_id = rel_data.pop("_start_id", None)
                old_end_id = rel_data.pop("_end_id", None)
                rel_type = rel_data.pop("_type", "RELATED")
                rel_data.pop("_id", None)  # Remove old relationship ID

                # Map to new node IDs
                new_start_id = node_id_mapping.get(old_start_id)
                new_end_id = node_id_mapping.get(old_end_id)

                if new_start_id is not None and new_end_id is not None:
                    create_rel_query = f"""
                    MATCH (a), (b)
                    WHERE elementId(a) = $start_id AND elementId(b) = $end_id
                    CREATE (a)-[r:{rel_type}]->(b)
                    SET r = $props
                    """

                    self.client.execute_query(
                        create_rel_query,
                        {
                            "start_id": new_start_id,
                            "end_id": new_end_id,
                            "props": rel_data,
                        },
                    )

            print("✅ Database data restored successfully")
            return True

        except Exception as e:
            print(f"❌ Failed to restore database data: {e}")
            return False

    def _clear_database(self) -> None:
        """Clear all data from the database."""
        try:
            print("Clearing existing database...")
            self.client.execute_query("MATCH (n) DETACH DELETE n")
            print("✅ Database cleared")
        except Exception as e:
            print(f"❌ Failed to clear database: {e}")
            raise

    def _get_database_statistics(self) -> dict[str, Any]:
        """Get current database statistics."""
        try:
            stats = {}

            # Node count
            node_result = self.client.execute_query(
                "MATCH (n) RETURN count(n) as count"
            )
            stats["node_count"] = node_result[0]["count"] if node_result else 0

            # Relationship count
            rel_result = self.client.execute_query(
                "MATCH ()-[r]->() RETURN count(r) as count"
            )
            stats["relationship_count"] = rel_result[0]["count"] if rel_result else 0

            # Label counts
            label_result = self.client.execute_query(
                """
                CALL db.labels() YIELD label
                CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {})
                YIELD value
                RETURN label, value.count as count
            """
            )

            if label_result:
                stats["label_counts"] = {
                    record["label"]: record["count"] for record in label_result
                }

            return stats

        except Exception as e:
            print(f"❌ Failed to get database statistics: {e}")
            return {}

    def _get_last_backup_statistics(self) -> dict[str, Any]:
        """Get statistics from the last backup."""
        latest_backup = self._get_latest_backup()
        if not latest_backup:
            return {}

        try:
            backup_path = self.backup_dir / latest_backup
            with open(backup_path, encoding="utf-8") as f:
                content = json.load(f)

            return content.get("data", {}).get("statistics", {})

        except Exception:
            return {}

    def _should_create_backup(
        self, current_stats: dict[str, Any], last_backup_stats: dict[str, Any]
    ) -> bool:
        """Determine if a backup should be created based on changes."""
        if not last_backup_stats:
            return True  # No previous backup

        # Define thresholds for significant changes
        node_threshold = 50  # More than 50 new nodes
        rel_threshold = 100  # More than 100 new relationships
        percentage_threshold = 0.1  # 10% increase

        current_nodes = current_stats.get("node_count", 0)
        current_rels = current_stats.get("relationship_count", 0)

        last_nodes = last_backup_stats.get("node_count", 0)
        last_rels = last_backup_stats.get("relationship_count", 0)

        # Check absolute changes
        node_diff = current_nodes - last_nodes
        rel_diff = current_rels - last_rels

        if node_diff >= node_threshold or rel_diff >= rel_threshold:
            return True

        # Check percentage changes
        if last_nodes > 0:
            node_change_pct = node_diff / last_nodes
            if node_change_pct >= percentage_threshold:
                return True

        if last_rels > 0:
            rel_change_pct = rel_diff / last_rels
            if rel_change_pct >= percentage_threshold:
                return True

        return False

    def _get_latest_backup(self) -> str | None:
        """Get the filename of the most recent backup."""
        backups = self.list_backups()
        return backups[0]["filename"] if backups else None

    def _update_backup_metadata(self, filename: str, metadata: dict[str, Any]) -> None:
        """Update the backup metadata file."""
        metadata_file = self.backup_dir / self.metadata_file

        # Load existing metadata
        all_metadata = {"backups": []}
        if metadata_file.exists():
            try:
                with open(metadata_file, encoding="utf-8") as f:
                    all_metadata = json.load(f)
            except Exception:
                pass

        # Add new backup metadata
        backup_info = metadata.copy()
        backup_info["filename"] = filename
        backup_info["file_size"] = (self.backup_dir / filename).stat().st_size

        all_metadata["backups"].append(backup_info)

        # Keep only the most recent backup metadata
        all_metadata["backups"] = sorted(
            all_metadata["backups"], key=lambda x: x.get("timestamp", ""), reverse=True
        )[: self.max_backups]

        # Save updated metadata
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(all_metadata, f, indent=2, default=str)

    def _cleanup_old_backups(self) -> None:
        """Remove old backup files, keeping only the most recent."""
        backups = sorted(
            self.backup_dir.glob("ign_scripts_db_backup_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        # Keep only the most recent backup
        for backup_file in backups[self.max_backups :]:
            try:
                backup_file.unlink()
                print(f"🗑️ Removed old backup: {backup_file.name}")
            except Exception as e:
                print(f"❌ Failed to remove old backup {backup_file.name}: {e}")

    def selective_restore_from_backup(
        self, backup_file: str | None = None, preserve_labels: list[str] | None = None
    ) -> tuple[bool, str]:
        """Restore database from backup while preserving specified node types.

        Args:
            backup_file: Specific backup file to restore from. If None, uses most recent.
            preserve_labels: List of node labels to preserve (not overwrite)

        Returns:
            Tuple of (success, message)
        """
        try:
            if preserve_labels is None:
                preserve_labels = []

            # Determine backup file to use
            if backup_file is None:
                backup_file = self._get_latest_backup()
                if not backup_file:
                    return False, "No backup files found"

            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                return False, f"Backup file not found: {backup_file}"

            print(f"Selective restore from backup: {backup_file}")
            print(f"Preserving existing data for labels: {preserve_labels}")

            # Load backup data
            with open(backup_path, encoding="utf-8") as f:
                backup_content = json.load(f)

            metadata = backup_content.get("metadata", {})
            data = backup_content.get("data", {})

            print(f"Backup info: {metadata.get('datetime')} - {metadata.get('reason')}")
            print(
                f"Data: {metadata.get('node_count', 0)} nodes, {metadata.get('relationship_count', 0)} relationships"
            )

            # Connect to database
            if not self.client.is_connected and not self.client.connect():
                return False, "Failed to connect to Neo4j database"

            # Get current statistics before restore
            current_stats = self._get_database_statistics()
            print(
                f"Current database: {current_stats.get('node_count', 0)} nodes, {current_stats.get('relationship_count', 0)} relationships"
            )

            # Restore data selectively
            success = self._selective_restore_database_data(data, preserve_labels)

            if success:
                # Get final statistics
                final_stats = self._get_database_statistics()
                print("✅ Selective restore completed successfully")
                print(
                    f"Final database: {final_stats.get('node_count', 0)} nodes, {final_stats.get('relationship_count', 0)} relationships"
                )
                return True, f"Database selectively restored from {backup_file}"
            else:
                return False, "Failed to restore database data"

        except Exception as e:
            error_msg = f"Failed to selective restore backup: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg

    def _selective_restore_database_data(
        self, data: dict[str, Any], preserve_labels: list[str]
    ) -> bool:
        """Restore data to the Neo4j database while preserving specified node types."""
        try:
            nodes = data.get("nodes", [])
            relationships = data.get("relationships", [])

            # Filter nodes to restore (exclude preserved labels)
            nodes_to_restore = []
            preserved_node_count = 0

            for node_data in nodes:
                node_labels = node_data.get("_labels", [])
                # Check if any of the node's labels should be preserved
                should_preserve = any(label in preserve_labels for label in node_labels)

                if not should_preserve:
                    nodes_to_restore.append(node_data)
                else:
                    preserved_node_count += 1

            print(
                f"Restoring {len(nodes_to_restore)} nodes (preserving {preserved_node_count} existing nodes)..."
            )

            # Create nodes with MERGE to avoid duplicates
            node_id_mapping = {}

            for node_data in nodes_to_restore:
                old_id = node_data.pop("_id", None)
                labels = node_data.pop("_labels", [])

                if not labels:
                    continue

                # Use MERGE with name as unique identifier if available
                name = node_data.get("name")
                if name:
                    # Create node with labels using MERGE
                    labels_str = ":".join(labels)
                    merge_query = f"""
                    MERGE (n:{labels_str} {{name: $name}})
                    SET n = $props
                    RETURN elementId(n) as new_id
                    """

                    result = self.client.execute_query(
                        merge_query, {"name": name, "props": node_data}
                    )
                else:
                    # Create node without name constraint
                    labels_str = ":".join(labels)
                    create_query = (
                        f"CREATE (n:{labels_str} $props) RETURN elementId(n) as new_id"
                    )

                    result = self.client.execute_query(
                        create_query, {"props": node_data}
                    )

                if result:
                    new_id = result[0]["new_id"]
                    node_id_mapping[old_id] = new_id

            # Create relationships for restored nodes
            print("Restoring relationships...")
            relationships_restored = 0

            for rel_data in relationships:
                old_start_id = rel_data.pop("_start_id", None)
                old_end_id = rel_data.pop("_end_id", None)
                rel_type = rel_data.pop("_type", "RELATED")
                rel_data.pop("_id", None)

                # Only restore relationships where both nodes were restored
                new_start_id = node_id_mapping.get(old_start_id)
                new_end_id = node_id_mapping.get(old_end_id)

                if new_start_id is not None and new_end_id is not None:
                    # Use MERGE to avoid duplicate relationships
                    merge_rel_query = f"""
                    MATCH (a), (b)
                    WHERE elementId(a) = $start_id AND elementId(b) = $end_id
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r = $props
                    """

                    self.client.execute_query(
                        merge_rel_query,
                        {
                            "start_id": new_start_id,
                            "end_id": new_end_id,
                            "props": rel_data,
                        },
                    )
                    relationships_restored += 1

            print(
                f"✅ Selective restore completed: {len(nodes_to_restore)} nodes, {relationships_restored} relationships"
            )
            return True

        except Exception as e:
            print(f"❌ Failed to selectively restore database data: {e}")
            return False


def create_initial_backup() -> None:
    """Create an initial backup for distribution with the application."""
    print("🚀 Creating initial backup for application distribution...")

    manager = Neo4jBackupManager()
    success, result = manager.create_full_backup(
        "Initial backup for application distribution"
    )

    if success:
        print(f"✅ Initial backup created: {result}")
        print(
            "This backup will be included with the application for new installations."
        )
    else:
        print(f"❌ Failed to create initial backup: {result}")


if __name__ == "__main__":
    # CLI interface for backup operations
    import argparse

    parser = argparse.ArgumentParser(description="Neo4j Backup Manager for IGN Scripts")
    parser.add_argument(
        "action",
        choices=["backup", "restore", "list", "info", "auto", "init"],
        help="Action to perform",
    )
    parser.add_argument("--file", "-f", help="Backup file name (for restore/info)")
    parser.add_argument(
        "--reason", "-r", default="Manual backup", help="Reason for backup"
    )

    args = parser.parse_args()

    manager = Neo4jBackupManager()

    if args.action == "backup":
        success, result = manager.create_full_backup(args.reason)
        print(
            "✅ Backup completed successfully"
            if success
            else f"❌ Backup failed: {result}"
        )

    elif args.action == "restore":
        success, result = manager.restore_from_backup(args.file)
        print(
            "✅ Restore completed successfully"
            if success
            else f"❌ Restore failed: {result}"
        )

    elif args.action == "list":
        backups = manager.list_backups()
        if backups:
            print("📋 Available backups:")
            for backup in backups:
                print(
                    f"  • {backup['filename']} - {backup.get('datetime', 'Unknown')} - {backup.get('reason', 'No reason')}"
                )
        else:
            print("📭 No backups found")

    elif args.action == "info":
        if not args.file:
            print("❌ --file parameter required for info action")
        else:
            info = manager.get_backup_info(args.file)
            if info:
                print(f"📄 Backup Info: {args.file}")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            else:
                print(f"❌ Backup file not found: {args.file}")

    elif args.action == "auto":
        if manager.auto_backup_on_significant_changes():
            print("✅ Auto-backup created due to significant changes")
        else:
            print("ℹ️ No backup needed - no significant changes detected")

    elif args.action == "init":
        create_initial_backup()
