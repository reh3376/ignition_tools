"""Ignition Graph Database Schema

Defines the node types, relationships, and constraints for the Ignition
knowledge graph that serves as AI Assistant persistent memory.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class NodeType(Enum):
    """Graph node types for Ignition knowledge system."""

    CONTEXT = "Context"
    FUNCTION = "Function"
    TEMPLATE = "Template"
    SCRIPT_TYPE = "ScriptType"
    PARAMETER = "Parameter"
    EXAMPLE = "Example"
    CATEGORY = "Category"


class RelationshipType(Enum):
    """Graph relationship types for Ignition knowledge system."""

    AVAILABLE_IN = "AVAILABLE_IN"
    USES = "USES"
    PROVIDES = "PROVIDES"
    COMPATIBLE_WITH = "COMPATIBLE_WITH"
    DEPENDS_ON = "DEPENDS_ON"
    OFTEN_USED_WITH = "OFTEN_USED_WITH"
    BELONGS_TO = "BELONGS_TO"
    EXAMPLE_OF = "EXAMPLE_OF"


@dataclass
class GraphNode:
    """Represents a node in the Ignition knowledge graph."""

    node_type: NodeType
    properties: dict[str, Any]

    def to_cypher_create(self) -> str:
        """Generate Cypher CREATE statement for this node."""
        props = ", ".join([f"{k}: ${k}" for k in self.properties.keys()])
        return f"CREATE (n:{self.node_type.value} {{{props}}})"

    def to_cypher_merge(self) -> str:
        """Generate Cypher MERGE statement for this node."""
        # Use 'name' as the primary identifier for merging
        name_prop = self.properties.get("name", "unknown")
        other_props = {k: v for k, v in self.properties.items() if k != "name"}

        merge_part = f"MERGE (n:{self.node_type.value} {{name: $name}})"
        if other_props:
            set_props = ", ".join([f"n.{k} = ${k}" for k in other_props.keys()])
            merge_part += f" SET {set_props}"

        return merge_part


@dataclass
class GraphRelationship:
    """Represents a relationship in the Ignition knowledge graph."""

    from_node_type: NodeType
    to_node_type: NodeType
    relationship_type: RelationshipType
    from_name: str
    to_name: str
    properties: dict[str, Any] = None

    def to_cypher_create(self) -> str:
        """Generate Cypher CREATE statement for this relationship."""
        from_label = self.from_node_type.value
        to_label = self.to_node_type.value
        rel_type = self.relationship_type.value

        if self.properties:
            props = ", ".join([f"{k}: ${k}" for k in self.properties.keys()])
            rel_props = f" {{{props}}}"
        else:
            rel_props = ""

        return f"""
        MATCH (a:{from_label} {{name: $from_name}})
        MATCH (b:{to_label} {{name: $to_name}})
        CREATE (a)-[:{rel_type}{rel_props}]->(b)
        """


class IgnitionGraphSchema:
    """Manages the Ignition knowledge graph schema."""

    @staticmethod
    def get_constraints() -> list[str]:
        """Get list of database constraints to create."""
        return [
            "CREATE CONSTRAINT context_name_unique IF NOT EXISTS FOR (c:Context) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT function_name_unique IF NOT EXISTS FOR (f:Function) REQUIRE f.name IS UNIQUE",
            "CREATE CONSTRAINT template_name_unique IF NOT EXISTS FOR (t:Template) REQUIRE t.name IS UNIQUE",
            "CREATE CONSTRAINT script_type_name_unique IF NOT EXISTS FOR (s:ScriptType) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT parameter_name_unique IF NOT EXISTS FOR (p:Parameter) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT example_name_unique IF NOT EXISTS FOR (e:Example) REQUIRE e.name IS UNIQUE",
            "CREATE CONSTRAINT category_name_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
        ]

    @staticmethod
    def get_indexes() -> list[str]:
        """Get list of database indexes to create for performance."""
        return [
            "CREATE INDEX context_name_index IF NOT EXISTS FOR (c:Context) ON (c.name)",
            "CREATE INDEX function_category_index IF NOT EXISTS FOR (f:Function) ON (f.category)",
            "CREATE INDEX function_scope_index IF NOT EXISTS FOR (f:Function) ON (f.scope)",
            "CREATE INDEX template_context_index IF NOT EXISTS FOR (t:Template) ON (t.context)",
            "CREATE INDEX script_type_context_index IF NOT EXISTS FOR (s:ScriptType) ON (s.context)",
        ]

    @staticmethod
    def create_context_nodes() -> list[GraphNode]:
        """Create Context nodes for Ignition scopes."""
        contexts = [
            {
                "name": "Gateway",
                "description": "Server-side scripts that run continuously on the Ignition Gateway",
                "scope": "gateway",
                "execution": "server",
                "persistent": True,
            },
            {
                "name": "Vision",
                "description": "Client-side scripts for Vision module applications",
                "scope": "client",
                "execution": "client",
                "persistent": False,
            },
            {
                "name": "Perspective",
                "description": "Session-specific scripts for Perspective module applications",
                "scope": "session",
                "execution": "gateway",
                "persistent": False,
            },
        ]

        return [GraphNode(NodeType.CONTEXT, context) for context in contexts]

    @staticmethod
    def create_script_type_nodes() -> list[GraphNode]:
        """Create ScriptType nodes for different event script types."""
        script_types = [
            {
                "name": "Startup",
                "description": "Gateway startup scripts executed when gateway starts",
                "context": "Gateway",
                "trigger": "gateway_startup",
                "parameters": ["logger"],
            },
            {
                "name": "Shutdown",
                "description": "Gateway shutdown scripts executed when gateway stops",
                "context": "Gateway",
                "trigger": "gateway_shutdown",
                "parameters": ["logger"],
            },
            {
                "name": "Timer",
                "description": "Scheduled scripts that execute at regular intervals",
                "context": "Gateway",
                "trigger": "scheduled",
                "parameters": ["logger"],
            },
            {
                "name": "TagChange",
                "description": "Scripts triggered when tag values change",
                "context": "Gateway",
                "trigger": "tag_change",
                "parameters": [
                    "tagPath",
                    "previousValue",
                    "currentValue",
                    "initialChange",
                    "missedEvents",
                ],
            },
            {
                "name": "ValueChanged",
                "description": "Vision component value changed scripts",
                "context": "Vision",
                "trigger": "component_event",
                "parameters": ["event", "newValue", "oldValue"],
            },
            {
                "name": "ActionPerformed",
                "description": "Vision component action performed scripts (buttons, etc)",
                "context": "Vision",
                "trigger": "component_event",
                "parameters": ["event"],
            },
            {
                "name": "MouseClicked",
                "description": "Vision component mouse click scripts",
                "context": "Vision",
                "trigger": "mouse_event",
                "parameters": ["event"],
            },
            {
                "name": "SessionStartup",
                "description": "Perspective session startup scripts",
                "context": "Perspective",
                "trigger": "session_event",
                "parameters": ["session"],
            },
            {
                "name": "SessionShutdown",
                "description": "Perspective session shutdown scripts",
                "context": "Perspective",
                "trigger": "session_event",
                "parameters": ["session"],
            },
        ]

        return [
            GraphNode(NodeType.SCRIPT_TYPE, script_type) for script_type in script_types
        ]

    @staticmethod
    def create_category_nodes() -> list[GraphNode]:
        """Create Category nodes for organizing functions."""
        categories = [
            {
                "name": "tag",
                "description": "Tag system functions for reading, writing, and browsing tags",
            },
            {
                "name": "db",
                "description": "Database functions for queries, connections, and transactions",
            },
            {
                "name": "gui",
                "description": "GUI functions for windows, popups, and user interface",
            },
            {
                "name": "util",
                "description": "Utility functions for logging, scheduling, and general operations",
            },
            {
                "name": "nav",
                "description": "Navigation functions for window and page management",
            },
            {
                "name": "alarm",
                "description": "Alarm system functions for acknowledgment, shelving, and queries",
            },
            {
                "name": "perspective",
                "description": "Perspective-specific functions for sessions and navigation",
            },
            {
                "name": "dataset",
                "description": "Dataset manipulation and analysis functions",
            },
            {"name": "date", "description": "Date and time utility functions"},
            {
                "name": "security",
                "description": "User authentication and authorization functions",
            },
            {"name": "opc", "description": "OPC server and browsing functions"},
            {"name": "net", "description": "Network communication and HTTP functions"},
            {
                "name": "file",
                "description": "File system access and manipulation functions",
            },
            {"name": "print", "description": "Report and document printing functions"},
            {
                "name": "sfc",
                "description": "Sequential Function Chart (SFC) control functions",
            },
            {
                "name": "bacnet",
                "description": "BACnet protocol communication functions",
            },
        ]

        return [GraphNode(NodeType.CATEGORY, category) for category in categories]
