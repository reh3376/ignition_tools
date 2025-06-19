"""Enhanced Ignition Graph Database Populator.

Loads comprehensive Ignition system functions, context variables, best practices,
and detailed relationships from our documentation into the Neo4j graph database.
"""

import logging
from typing import Any

from .client import IgnitionGraphClient
from .schema import (
    GraphNode,
    GraphRelationship,
    NodeType,
    RelationshipType,
)
from .tasks.task_1_tag_system import get_tag_system_extended

logger = logging.getLogger(__name__)


class EnhancedIgnitionGraphPopulator:
    """Enhanced populator for comprehensive Ignition knowledge graph."""

    def __init__(self, client: IgnitionGraphClient):
        """Initialize the enhanced populator with a graph client."""
        self.client = client

    def populate_full_enhanced_database(self, clear_first: bool = False) -> bool:
        """Populate the database with comprehensive enhanced Ignition knowledge."""
        try:
            if clear_first:
                logger.warning("Clearing existing database...")
                if not self.client.clear_database():
                    return False

            logger.info("Starting enhanced database population...")

            # Step 1: Basic schema (reuse from regular populator)
            from .populator import IgnitionGraphPopulator

            basic_populator = IgnitionGraphPopulator(self.client)

            if not basic_populator.populate_initial_schema():
                logger.error("Failed to populate initial schema")
                return False

            # Step 2: Load comprehensive functions
            if not self._load_comprehensive_functions():
                logger.error("Failed to load comprehensive functions")
                return False

            # Step 3: Load advanced features
            if not self._load_advanced_features():
                logger.error("Failed to load advanced features")
                return False

            # Step 4: Templates (reuse from regular populator)
            if not basic_populator.populate_templates():
                logger.error("Failed to populate templates")
                return False

            # Get final stats
            stats = self.client.get_database_stats()
            logger.info("Enhanced database population completed successfully!")
            logger.info(f"Final stats: {stats}")

            return True

        except Exception as e:
            logger.error(f"Enhanced database population failed: {e}")
            return False

    def _load_comprehensive_functions(self) -> bool:
        """Load all comprehensive Ignition system functions."""
        try:
            logger.info("Loading comprehensive Ignition system functions...")

            # Load device functions
            device_functions = self._get_device_functions()
            for func_data in device_functions:
                self._create_function_with_relationships(func_data)

            # Load navigation functions
            nav_functions = self._get_navigation_functions()
            for func_data in nav_functions:
                self._create_function_with_relationships(func_data)

            # Load file functions
            file_functions = self._get_file_functions()
            for func_data in file_functions:
                self._create_function_with_relationships(func_data)

            # Load security functions
            security_functions = self._get_security_functions()
            for func_data in security_functions:
                self._create_function_with_relationships(func_data)

            # Load math functions
            math_functions = self._get_math_functions()
            for func_data in math_functions:
                self._create_function_with_relationships(func_data)

            # Load network functions
            net_functions = self._get_network_functions()
            for func_data in net_functions:
                self._create_function_with_relationships(func_data)

            # Load dataset functions
            dataset_functions = self._get_dataset_functions()
            for func_data in dataset_functions:
                self._create_function_with_relationships(func_data)

            # Load Task 1: Extended tag system functions
            task_1_functions = get_tag_system_extended()
            for func_data in task_1_functions:
                self._create_function_with_relationships(func_data)

            logger.info(
                "Successfully loaded comprehensive Ignition functions including Task 1"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to load comprehensive functions: {e}")
            return False

    def _create_function_with_relationships(self, func_data: dict[str, Any]) -> bool:
        """Helper to create function node and its relationships."""
        try:
            # Create function node
            node = GraphNode(NodeType.FUNCTION, func_data)
            if not self.client.create_node(node):
                logger.warning(
                    f"Failed to create function node: {func_data.get('name', 'unknown')}"
                )
                return False

            # Create function-context relationships
            func_name = func_data["name"]
            for context in func_data.get("contexts", []):
                relationship = GraphRelationship(
                    from_node_type=NodeType.FUNCTION,
                    to_node_type=NodeType.CONTEXT,
                    relationship_type=RelationshipType.AVAILABLE_IN,
                    from_name=func_name,
                    to_name=context,
                )
                self.client.create_relationship(relationship)

            # Create function-category relationships
            category = func_data.get("category", "util")
            relationship = GraphRelationship(
                from_node_type=NodeType.FUNCTION,
                to_node_type=NodeType.CATEGORY,
                relationship_type=RelationshipType.BELONGS_TO,
                from_name=func_name,
                to_name=category,
            )
            self.client.create_relationship(relationship)

            return True

        except Exception as e:
            logger.error(f"Failed to create function with relationships: {e}")
            return False

    def _get_device_functions(self) -> list[dict[str, Any]]:
        """Get device and OPC functions."""
        return [
            {
                "name": "system.device.listDevices",
                "description": "list all configured device connections",
                "category": "device",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": [],
                "returns": "String[]",
            },
            {
                "name": "system.device.refreshBrowse",
                "description": "Refresh device browse cache",
                "category": "device",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["deviceName"],
                "returns": "None",
            },
            {
                "name": "system.opc.browseServer",
                "description": "Browse an OPC server structure",
                "category": "device",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["opcServer", "nodeId"],
                "returns": "BrowseElement[]",
            },
            {
                "name": "system.opc.getServers",
                "description": "Get list of available OPC servers",
                "category": "device",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["host"],
                "returns": "String[]",
            },
            {
                "name": "system.opcua.browseServer",
                "description": "Browse an OPC-UA server structure",
                "category": "device",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["connectionSettings", "nodeId"],
                "returns": "BrowseElement[]",
            },
            {
                "name": "system.opcua.callMethod",
                "description": "Call a method on an OPC-UA server",
                "category": "device",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["connectionSettings", "objectId", "methodId", "inputs"],
                "returns": "Object[]",
            },
            {
                "name": "system.dnp3.sendDataSet",
                "description": "Send a dataset via DNP3",
                "category": "device",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["deviceName", "dataset"],
                "returns": "None",
            },
        ]

    def _get_navigation_functions(self) -> list[dict[str, Any]]:
        """Get Vision navigation functions."""
        return [
            {
                "name": "system.nav.openWindow",
                "description": "Open a new window in Vision client",
                "category": "nav",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["path", "params"],
                "returns": "FPMIWindow",
            },
            {
                "name": "system.nav.openWindowInstance",
                "description": "Open a specific window instance",
                "category": "nav",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["path", "params", "instanceId"],
                "returns": "FPMIWindow",
            },
            {
                "name": "system.nav.closeWindow",
                "description": "Close a window",
                "category": "nav",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["window"],
                "returns": "None",
            },
            {
                "name": "system.nav.closeParentWindow",
                "description": "Close the parent window",
                "category": "nav",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["event"],
                "returns": "None",
            },
            {
                "name": "system.nav.swapWindow",
                "description": "Replace current window with another",
                "category": "nav",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["event", "path", "params"],
                "returns": "FPMIWindow",
            },
            {
                "name": "system.nav.centerWindow",
                "description": "Center a window on screen",
                "category": "nav",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["window"],
                "returns": "None",
            },
            {
                "name": "system.nav.getCurrentWindow",
                "description": "Get reference to current window",
                "category": "nav",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": [],
                "returns": "FPMIWindow",
            },
            {
                "name": "system.nav.getWindowNames",
                "description": "Get list of open window names",
                "category": "nav",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": [],
                "returns": "String[]",
            },
        ]

    def _get_file_functions(self) -> list[dict[str, Any]]:
        """Get file system functions."""
        return [
            {
                "name": "system.file.readFileAsString",
                "description": "Read file contents as string",
                "category": "file",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["filepath", "encoding"],
                "returns": "String",
            },
            {
                "name": "system.file.writeFile",
                "description": "Write data to a file",
                "category": "file",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["filepath", "data"],
                "returns": "None",
            },
            {
                "name": "system.file.openFile",
                "description": "Open file dialog and return contents",
                "category": "file",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["extension", "extensionDesc"],
                "returns": "String",
            },
            {
                "name": "system.file.saveFile",
                "description": "Save file dialog and write contents",
                "category": "file",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["filename", "extension", "data"],
                "returns": "String",
            },
            {
                "name": "system.file.getTempFile",
                "description": "Get temporary file path",
                "category": "file",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["extension"],
                "returns": "String",
            },
        ]

    def _get_security_functions(self) -> list[dict[str, Any]]:
        """Get security functions."""
        return [
            {
                "name": "system.security.getUsername",
                "description": "Get current username",
                "category": "security",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": [],
                "returns": "String",
            },
            {
                "name": "system.security.getRoles",
                "description": "Get user roles",
                "category": "security",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["username"],
                "returns": "String[]",
            },
            {
                "name": "system.security.isScreenLocked",
                "description": "Check if screen is locked",
                "category": "security",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": [],
                "returns": "boolean",
            },
            {
                "name": "system.security.lockScreen",
                "description": "Lock the screen",
                "category": "security",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": [],
                "returns": "None",
            },
            {
                "name": "system.security.unlockScreen",
                "description": "Unlock the screen",
                "category": "security",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": [],
                "returns": "None",
            },
            {
                "name": "system.security.validateUser",
                "description": "Validate user credentials",
                "category": "security",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": ["username", "password", "authProfile"],
                "returns": "User",
            },
        ]

    def _get_math_functions(self) -> list[dict[str, Any]]:
        """Get mathematical functions."""
        return [
            {
                "name": "system.math.mean",
                "description": "Calculate arithmetic mean",
                "category": "math",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["values"],
                "returns": "double",
            },
            {
                "name": "system.math.stdDev",
                "description": "Calculate standard deviation",
                "category": "math",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["values"],
                "returns": "double",
            },
            {
                "name": "system.math.scale",
                "description": "Scale a value between ranges",
                "category": "math",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["value", "rawLow", "rawHigh", "scaledLow", "scaledHigh"],
                "returns": "double",
            },
        ]

    def _get_network_functions(self) -> list[dict[str, Any]]:
        """Get network functions."""
        return [
            {
                "name": "system.net.httpGet",
                "description": "Execute HTTP GET request",
                "category": "network",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": [
                    "url",
                    "connectTimeout",
                    "readTimeout",
                    "username",
                    "password",
                ],
                "returns": "String",
            },
            {
                "name": "system.net.httpPost",
                "description": "Execute HTTP POST request",
                "category": "network",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": [
                    "url",
                    "contentType",
                    "postData",
                    "connectTimeout",
                    "readTimeout",
                    "username",
                    "password",
                ],
                "returns": "String",
            },
            {
                "name": "system.net.sendEmail",
                "description": "Send email message",
                "category": "network",
                "contexts": ["Gateway"],
                "scope": "gateway",
                "parameters": [
                    "smtp",
                    "fromAddr",
                    "subject",
                    "body",
                    "html",
                    "to",
                    "attachmentNames",
                    "attachmentData",
                ],
                "returns": "None",
            },
            {
                "name": "system.net.openURL",
                "description": "Open URL in default browser",
                "category": "network",
                "contexts": ["Vision"],
                "scope": "client",
                "parameters": ["url"],
                "returns": "None",
            },
        ]

    def _get_dataset_functions(self) -> list[dict[str, Any]]:
        """Get dataset manipulation functions."""
        return [
            {
                "name": "system.dataset.addColumn",
                "description": "Add column to dataset",
                "category": "dataset",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["dataset", "colIndex", "colName", "colType", "colData"],
                "returns": "Dataset",
            },
            {
                "name": "system.dataset.addRow",
                "description": "Add row to dataset",
                "category": "dataset",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["dataset", "rowIndex", "rowData"],
                "returns": "Dataset",
            },
            {
                "name": "system.dataset.deleteRow",
                "description": "Delete row from dataset",
                "category": "dataset",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["dataset", "rowIndex"],
                "returns": "Dataset",
            },
            {
                "name": "system.dataset.filterColumns",
                "description": "Filter dataset columns",
                "category": "dataset",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["dataset", "columns"],
                "returns": "Dataset",
            },
            {
                "name": "system.dataset.sort",
                "description": "Sort dataset by column",
                "category": "dataset",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["dataset", "keyColumn", "ascending"],
                "returns": "Dataset",
            },
            {
                "name": "system.dataset.toPyDataSet",
                "description": "Convert dataset to PyDataSet",
                "category": "dataset",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["dataset"],
                "returns": "PyDataSet",
            },
            {
                "name": "system.dataset.toDataSet",
                "description": "Convert PyDataSet to dataset",
                "category": "dataset",
                "contexts": ["Gateway", "Vision", "Perspective"],
                "scope": "all",
                "parameters": ["pyDataset"],
                "returns": "Dataset",
            },
        ]

    def _load_advanced_features(self) -> bool:
        """Load advanced features like context variables and best practices."""
        try:
            logger.info("Loading advanced features...")

            # Load context variables
            context_variables = self._get_context_variables()
            for var_data in context_variables:
                node = GraphNode(NodeType.PARAMETER, var_data)
                if not self.client.create_node(node):
                    continue

                # Create script type -> parameter relationships
                var_name = var_data["name"]
                for script_type in var_data.get("available_in", []):
                    relationship = GraphRelationship(
                        from_node_type=NodeType.SCRIPT_TYPE,
                        to_node_type=NodeType.PARAMETER,
                        relationship_type=RelationshipType.PROVIDES,
                        from_name=script_type,
                        to_name=var_name,
                    )
                    self.client.create_relationship(relationship)

            logger.info("Successfully loaded advanced features")
            return True

        except Exception as e:
            logger.error(f"Failed to load advanced features: {e}")
            return False

    def _get_context_variables(self) -> list[dict[str, Any]]:
        """Get context variables available in different script types."""
        return [
            {
                "name": "initialChange",
                "description": "Boolean indicating if this is the first tag change event after subscription",
                "type": "boolean",
                "available_in": ["TagChange"],
                "usage_notes": "Use to skip processing on initial subscription",
            },
            {
                "name": "newValue",
                "description": "The new qualified value of the tag",
                "type": "QualifiedValue",
                "available_in": ["TagChange"],
                "usage_notes": "Contains value, quality, and timestamp",
            },
            {
                "name": "previousValue",
                "description": "The previous qualified value of the tag",
                "type": "QualifiedValue",
                "available_in": ["TagChange"],
                "usage_notes": "Contains value, quality, and timestamp",
            },
            {
                "name": "event",
                "description": "Complete tag change event object",
                "type": "TagChangeEvent",
                "available_in": ["TagChange"],
                "usage_notes": "Contains all event details and metadata",
            },
            {
                "name": "tagPath",
                "description": "The path of the tag that changed",
                "type": "String",
                "available_in": ["TagChange"],
                "usage_notes": "Full tag path including provider",
            },
            {
                "name": "payload",
                "description": "Message payload data",
                "type": "PyDictionary",
                "available_in": ["MessageHandler"],
                "usage_notes": "Contains data sent with the message",
            },
            {
                "name": "logger",
                "description": "Pre-configured logger instance",
                "type": "Logger",
                "available_in": ["Startup", "Shutdown", "Timer"],
                "usage_notes": "Use for logging instead of print statements",
            },
            {
                "name": "event",
                "description": "Component event object",
                "type": "ComponentEvent",
                "available_in": ["ActionPerformed", "ValueChanged", "MouseClicked"],
                "usage_notes": "Contains event details and source component",
            },
            {
                "name": "newValue",
                "description": "New component value",
                "type": "Object",
                "available_in": ["ValueChanged"],
                "usage_notes": "Type depends on component property",
            },
            {
                "name": "session",
                "description": "Perspective session object",
                "type": "Session",
                "available_in": ["SessionStartup", "SessionShutdown"],
                "usage_notes": "Contains session state and properties",
            },
        ]
