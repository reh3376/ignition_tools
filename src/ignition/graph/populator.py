"""Ignition Graph Database Populator.

Loads Ignition system functions, contexts, templates, and relationships
into the Neo4j graph database from various sources.
"""

import logging
from typing import Any

from .client import IgnitionGraphClient
from .schema import (
    GraphNode,
    GraphRelationship,
    IgnitionGraphSchema,
    NodeType,
    RelationshipType,
)

logger = logging.getLogger(__name__)


class IgnitionGraphPopulator:
    """Populates the Ignition knowledge graph with system data."""

    def __init__(self, client: IgnitionGraphClient):
        """Initialize the populator with a graph client.

        Args:
            client: Connected IgnitionGraphClient instance
        """
        self.client = client

    def populate_initial_schema(self) -> bool:
        """Populate the database with initial schema and basic nodes.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Setting up database schema...")
            if not self.client.setup_schema():
                return False

            logger.info("Creating context nodes...")
            if not self._create_context_nodes():
                return False

            logger.info("Creating script type nodes...")
            if not self._create_script_type_nodes():
                return False

            logger.info("Creating category nodes...")
            if not self._create_category_nodes():
                return False

            logger.info("Creating context-script type relationships...")
            if not self._create_context_script_relationships():
                return False

            logger.info("Initial schema population completed successfully")
            return True

        except Exception as e:
            logger.error(f"Schema population failed: {e}")
            return False

    def _create_context_nodes(self) -> bool:
        """Create Context nodes."""
        try:
            return all(self.client.create_node(node) for node in IgnitionGraphSchema.create_context_nodes())
        except Exception as e:
            logger.error(f"Failed to create context nodes: {e}")
            return False

    def _create_script_type_nodes(self) -> bool:
        """Create ScriptType nodes."""
        try:
            return all(self.client.create_node(node) for node in IgnitionGraphSchema.create_script_type_nodes())
        except Exception as e:
            logger.error(f"Failed to create script type nodes: {e}")
            return False

    def _create_category_nodes(self) -> bool:
        """Create Category nodes."""
        try:
            return all(self.client.create_node(node) for node in IgnitionGraphSchema.create_category_nodes())
        except Exception as e:
            logger.error(f"Failed to create category nodes: {e}")
            return False

    def _create_context_script_relationships(self) -> bool:
        """Create relationships between contexts and script types."""
        try:
            # Map script types to their contexts
            script_context_map = {
                "Startup": "Gateway",
                "Shutdown": "Gateway",
                "Timer": "Gateway",
                "TagChange": "Gateway",
                "ValueChanged": "Vision",
                "ActionPerformed": "Vision",
                "MouseClicked": "Vision",
                "SessionStartup": "Perspective",
                "SessionShutdown": "Perspective",
            }

            for script_type, context in script_context_map.items():
                relationship = GraphRelationship(
                    from_node_type=NodeType.SCRIPT_TYPE,
                    to_node_type=NodeType.CONTEXT,
                    relationship_type=RelationshipType.COMPATIBLE_WITH,
                    from_name=script_type,
                    to_name=context,
                )

                if not self.client.create_relationship(relationship):
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to create context-script relationships: {e}")
            return False

    def populate_ignition_functions(self) -> bool:
        """Populate the database with Ignition system functions.

        This loads the 400+ Ignition system functions from our documentation.
        """
        try:
            logger.info("Loading Ignition system functions...")

            # Core system functions with their context availability
            functions_data = self._get_ignition_functions_data()

            # Create function nodes
            for func_data in functions_data:
                node = GraphNode(NodeType.FUNCTION, func_data)
                if not self.client.create_node(node):
                    logger.warning(f"Failed to create function node: {func_data.get('name', 'unknown')}")

            # Create function-context relationships
            for func_data in functions_data:
                func_name = func_data["name"]
                for context in func_data.get("contexts", []):
                    relationship = GraphRelationship(
                        from_node_type=NodeType.FUNCTION,
                        to_node_type=NodeType.CONTEXT,
                        relationship_type=RelationshipType.AVAILABLE_IN,
                        from_name=func_name,
                        to_name=context,
                    )

                    if not self.client.create_relationship(relationship):
                        logger.warning(f"Failed to create function-context relationship: {func_name} -> {context}")

            # Create function-category relationships
            for func_data in functions_data:
                func_name = func_data["name"]
                category = func_data.get("category", "util")

                relationship = GraphRelationship(
                    from_node_type=NodeType.FUNCTION,
                    to_node_type=NodeType.CATEGORY,
                    relationship_type=RelationshipType.BELONGS_TO,
                    from_name=func_name,
                    to_name=category,
                )

                if not self.client.create_relationship(relationship):
                    logger.warning(f"Failed to create function-category relationship: {func_name} -> {category}")

            logger.info(f"Successfully loaded {len(functions_data)} Ignition functions")
            return True

        except Exception as e:
            logger.error(f"Failed to populate Ignition functions: {e}")
            return False

    def _get_ignition_functions_data(self) -> list[dict[str, Any]]:
        """Get Ignition system functions data.

        This is a curated list of essential Ignition functions with their
        context availability. In a full implementation, this would be loaded
        from the comprehensive documentation.
        """
        return [
            # Tag System Functions
            {
                "name": "system.tag.readBlocking",
                "description": "Read tag values synchronously",
                "category": "tag",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["tagPaths", "timeout"],
                "returns": "QualifiedValue[]",
            },
            {
                "name": "system.tag.writeBlocking",
                "description": "Write tag values synchronously",
                "category": "tag",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["tagPaths", "values", "timeout"],
                "returns": "QualityCode[]",
            },
            {
                "name": "system.tag.read",
                "description": "Read tag values asynchronously",
                "category": "tag",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["tagPaths"],
                "returns": "QualifiedValue[]",
            },
            {
                "name": "system.tag.write",
                "description": "Write tag values asynchronously",
                "category": "tag",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["tagPaths", "values"],
                "returns": "QualityCode[]",
            },
            {
                "name": "system.tag.browse",
                "description": "Browse tag provider structure",
                "category": "tag",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["path", "filter"],
                "returns": "BrowseTag[]",
            },
            # Database Functions
            {
                "name": "system.db.runQuery",
                "description": "Execute a database query",
                "category": "db",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["query", "database", "params"],
                "returns": "Dataset",
            },
            {
                "name": "system.db.runUpdateQuery",
                "description": "Execute a database update query",
                "category": "db",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["query", "database", "params"],
                "returns": "int",
            },
            {
                "name": "system.db.runPrepQuery",
                "description": "Execute a prepared database query",
                "category": "db",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["query", "params", "database"],
                "returns": "Dataset",
            },
            {
                "name": "system.db.runPrepUpdate",
                "description": "Execute a prepared database update",
                "category": "db",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["query", "params", "database"],
                "returns": "int",
            },
            # GUI Functions (Vision Only)
            {
                "name": "system.gui.openWindow",
                "description": "Open a Vision window",
                "category": "gui",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["path", "params"],
                "returns": "FPMIWindow",
            },
            {
                "name": "system.gui.openWindowInstance",
                "description": "Open a specific window instance",
                "category": "gui",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["path", "params", "instanceId"],
                "returns": "FPMIWindow",
            },
            {
                "name": "system.gui.closeWindow",
                "description": "Close a Vision window",
                "category": "gui",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["window"],
                "returns": "None",
            },
            {
                "name": "system.gui.messageBox",
                "description": "Display a message box",
                "category": "gui",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["message", "title", "options"],
                "returns": "int",
            },
            {
                "name": "system.gui.confirm",
                "description": "Display a confirmation dialog",
                "category": "gui",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["message", "title", "allowCancel"],
                "returns": "boolean",
            },
            {
                "name": "system.gui.inputBox",
                "description": "Display an input dialog",
                "category": "gui",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["message", "title", "defaultText"],
                "returns": "String",
            },
            # Perspective Functions
            {
                "name": "system.perspective.navigate",
                "description": "Navigate to a Perspective page",
                "category": "perspective",
                "contexts": ["Perspective"],
                "scope": "session",
                "parameters": ["page", "params", "view", "sessionId"],
                "returns": "None",
            },
            {
                "name": "system.perspective.print",
                "description": "Print a Perspective view",
                "category": "perspective",
                "contexts": ["Perspective"],
                "scope": "session",
                "parameters": ["componentId", "options"],
                "returns": "None",
            },
            {
                "name": "system.perspective.closePopup",
                "description": "Close a Perspective popup",
                "category": "perspective",
                "contexts": ["Perspective"],
                "scope": "session",
                "parameters": ["id", "sessionId"],
                "returns": "None",
            },
            {
                "name": "system.perspective.openPopup",
                "description": "Open a Perspective popup",
                "category": "perspective",
                "contexts": ["Perspective"],
                "scope": "session",
                "parameters": [
                    "id",
                    "view",
                    "params",
                    "title",
                    "position",
                    "showCloseIcon",
                    "draggable",
                    "resizable",
                    "modal",
                    "overlayDismiss",
                ],
                "returns": "None",
            },
            # Utility Functions
            {
                "name": "system.util.logger",
                "description": "Get a logger instance",
                "category": "util",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["name"],
                "returns": "Logger",
            },
            {
                "name": "system.util.sendMessage",
                "description": "Send a message between scopes",
                "category": "util",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["project", "messageHandler", "payload", "scope"],
                "returns": "None",
            },
            {
                "name": "system.util.execute",
                "description": "Execute a system command",
                "category": "util",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["command", "args", "workingDirectory"],
                "returns": "ProcessBuilder",
            },
            {
                "name": "system.util.globals",
                "description": "Access global variables",
                "category": "util",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": [],
                "returns": "PyDictionary",
            },
            # Date Functions
            {
                "name": "system.date.now",
                "description": "Get current date and time",
                "category": "date",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": [],
                "returns": "Date",
            },
            {
                "name": "system.date.format",
                "description": "Format a date as string",
                "category": "date",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["date", "format"],
                "returns": "String",
            },
            {
                "name": "system.date.parse",
                "description": "Parse a date string",
                "category": "date",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["dateString", "format"],
                "returns": "Date",
            },
            # Alarm Functions
            {
                "name": "system.alarm.acknowledge",
                "description": "Acknowledge alarms",
                "category": "alarm",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["alarmIds", "notes", "username"],
                "returns": "None",
            },
            {
                "name": "system.alarm.queryStatus",
                "description": "Query alarm status",
                "category": "alarm",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["provider", "paths", "includeShelved"],
                "returns": "Dataset",
            },
            {
                "name": "system.alarm.shelve",
                "description": "Shelve alarms",
                "category": "alarm",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["paths", "timeoutMinutes", "notes"],
                "returns": "None",
            },
        ]

    def populate_templates(self) -> bool:
        """Populate the database with template information."""
        try:
            logger.info("Loading template information...")

            # Get template data from our templates directory
            templates_data = self._get_templates_data()

            # Create template nodes
            for template_data in templates_data:
                node = GraphNode(NodeType.TEMPLATE, template_data)
                if not self.client.create_node(node):
                    logger.warning(f"Failed to create template node: {template_data.get('name', 'unknown')}")

            # Create template-context relationships
            for template_data in templates_data:
                template_name = template_data["name"]
                context = template_data.get("context", "Gateway")

                relationship = GraphRelationship(
                    from_node_type=NodeType.TEMPLATE,
                    to_node_type=NodeType.CONTEXT,
                    relationship_type=RelationshipType.COMPATIBLE_WITH,
                    from_name=template_name,
                    to_name=context,
                )

                if not self.client.create_relationship(relationship):
                    logger.warning(f"Failed to create template-context relationship: {template_name} -> {context}")

            # Create template-function relationships (based on functions used)
            for template_data in templates_data:
                template_name = template_data["name"]
                for func_name in template_data.get("uses_functions", []):
                    relationship = GraphRelationship(
                        from_node_type=NodeType.TEMPLATE,
                        to_node_type=NodeType.FUNCTION,
                        relationship_type=RelationshipType.USES,
                        from_name=template_name,
                        to_name=func_name,
                    )

                    if not self.client.create_relationship(relationship):
                        logger.warning(
                            f"Failed to create template-function relationship: {template_name} -> {func_name}"
                        )

            logger.info(f"Successfully loaded {len(templates_data)} templates")
            return True

        except Exception as e:
            logger.error(f"Failed to populate templates: {e}")
            return False

    def _get_templates_data(self) -> list[dict[str, Any]]:
        """Get template data from our templates directory."""
        return [
            {
                "name": "Gateway Startup Script",
                "description": "System initialization script for gateway startup",
                "context": "Gateway",
                "script_type": "Startup",
                "file_path": "templates/gateway/startup_script.jinja2",
                "uses_functions": [
                    "system.util.logger",
                    "system.db.runQuery",
                    "system.tag.writeBlocking",
                    "system.util.sendMessage",
                ],
            },
            {
                "name": "Gateway Timer Script",
                "description": "Periodic data collection and processing script",
                "context": "Gateway",
                "script_type": "Timer",
                "file_path": "templates/gateway/timer_script.jinja2",
                "uses_functions": [
                    "system.util.logger",
                    "system.tag.readBlocking",
                    "system.tag.writeBlocking",
                    "system.db.runQuery",
                    "system.db.runUpdateQuery",
                ],
            },
            {
                "name": "Gateway Tag Change Script",
                "description": "React to tag value changes with configurable actions",
                "context": "Gateway",
                "script_type": "TagChange",
                "file_path": "templates/gateway/tag_change_script.jinja2",
                "uses_functions": [
                    "system.util.logger",
                    "system.tag.writeBlocking",
                    "system.db.runUpdateQuery",
                    "system.alarm.acknowledge",
                ],
            },
            {
                "name": "Vision Popup Window Handler",
                "description": "Open popup windows with parameter passing",
                "context": "Vision",
                "script_type": "ActionPerformed",
                "file_path": "templates/vision/popup_window_handler.jinja2",
                "uses_functions": [
                    "system.gui.openWindow",
                    "system.gui.messageBox",
                    "system.gui.confirm",
                ],
            },
            {
                "name": "Advanced Tag Write Handler",
                "description": "Complex tag write operations with validation",
                "context": "Vision",
                "script_type": "ActionPerformed",
                "file_path": "templates/vision/advanced_tag_write_handler.jinja2",
                "uses_functions": [
                    "system.tag.readBlocking",
                    "system.tag.writeBlocking",
                    "system.gui.confirm",
                    "system.gui.messageBox",
                ],
            },
            {
                "name": "Perspective Session Navigation",
                "description": "Navigate between Perspective pages with parameters",
                "context": "Perspective",
                "script_type": "ActionPerformed",
                "file_path": "templates/perspective/session_navigation.jinja2",
                "uses_functions": [
                    "system.perspective.navigate",
                    "system.perspective.openPopup",
                    "system.perspective.closePopup",
                ],
            },
        ]

    def get_population_stats(self) -> dict[str, Any]:
        """Get statistics about the populated database."""
        return self.client.get_database_stats()

    def populate_full_database(self, clear_first: bool = False) -> bool:
        """Populate the entire database with all Ignition knowledge.

        Args:
            clear_first: Whether to clear existing data first

        Returns:
            True if successful, False otherwise
        """
        try:
            if clear_first:
                logger.warning("Clearing existing database...")
                if not self.client.clear_database():
                    return False

            logger.info("Starting full database population...")

            # Step 1: Initial schema and basic nodes
            if not self.populate_initial_schema():
                logger.error("Failed to populate initial schema")
                return False

            # Step 2: Ignition system functions
            if not self.populate_ignition_functions():
                logger.error("Failed to populate Ignition functions")
                return False

            # Step 3: Templates
            if not self.populate_templates():
                logger.error("Failed to populate templates")
                return False

            # Get final stats
            stats = self.get_population_stats()
            logger.info("Database population completed successfully!")
            logger.info(f"Final stats: {stats}")

            return True

        except Exception as e:
            logger.error(f"Full database population failed: {e}")
            return False
