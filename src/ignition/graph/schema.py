"""Ignition Graph Database Schema.

Defines the node types, relationships, and constraints for the Ignition
knowledge graph that serves as AI Assistant persistent memory.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class NodeType(Enum):
    """Enumeration of all node types in the graph."""

    FUNCTION = "Function"
    CONTEXT = "Context"
    SCOPE = "Scope"
    PARAMETER = "Parameter"
    TEMPLATE = "Template"
    SCRIPT_TYPE = "ScriptType"
    PATTERN = "Pattern"
    TASK = "Task"
    # Learning System Node Types
    USAGE_EVENT = "UsageEvent"
    USER_SESSION = "UserSession"
    PATTERN_ANALYSIS = "PatternAnalysis"
    RECOMMENDATION = "Recommendation"
    PERFORMANCE_METRIC = "PerformanceMetric"
    # Export/Import Intelligence Node Types
    EXPORT_PROFILE = "ExportProfile"
    IMPORT_JOB = "ImportJob"
    RESOURCE_DEPENDENCY = "ResourceDependency"
    DEPLOYMENT_CONFIG = "DeploymentConfig"
    VERSION_TAG = "VersionTag"
    GATEWAY_RESOURCE = "GatewayResource"


class RelationshipType(Enum):
    """Enumeration of all relationship types in the graph."""

    HAS_PARAMETER = "HAS_PARAMETER"
    AVAILABLE_IN = "AVAILABLE_IN"
    REQUIRES = "REQUIRES"
    USES = "USES"
    PROVIDES = "PROVIDES"
    COMPATIBLE_WITH = "COMPATIBLE_WITH"
    DEPENDS_ON = "DEPENDS_ON"
    IMPLEMENTS = "IMPLEMENTS"
    BELONGS_TO_TASK = "BELONGS_TO_TASK"
    MATCHES_PATTERN = "MATCHES_PATTERN"
    # Learning System Relationship Types
    USED_TOGETHER = "USED_TOGETHER"
    OCCURRED_IN_SESSION = "OCCURRED_IN_SESSION"
    GENERATED_RECOMMENDATION = "GENERATED_RECOMMENDATION"
    HAS_PERFORMANCE_DATA = "HAS_PERFORMANCE_DATA"
    FOLLOWS_PATTERN = "FOLLOWS_PATTERN"
    PRECEDES = "PRECEDES"
    CO_OCCURS_WITH = "CO_OCCURS_WITH"
    # Export/Import Intelligence Relationship Types
    EXPORTS_TO = "EXPORTS_TO"
    IMPORTS_FROM = "IMPORTS_FROM"
    DEPLOYED_AS = "DEPLOYED_AS"
    REPLACES = "REPLACES"
    REFERENCES = "REFERENCES"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    VERSIONED_AS = "VERSIONED_AS"


@dataclass
class GraphNode:
    """Represents a node in the Ignition knowledge graph."""

    node_type: NodeType
    properties: dict[str, Any]

    def to_cypher_create(self) -> str:
        """Generate Cypher CREATE statement for this node."""
        props = ", ".join([f"{k}: ${k}" for k in self.properties])
        return f"CREATE (n:{self.node_type.value} {{{props}}})"

    def to_cypher_merge(self) -> str:
        """Generate Cypher MERGE statement for this node."""
        # Use 'name' as the primary identifier for merging
        self.properties.get("name", "unknown")
        other_props = {k: v for k, v in self.properties.items() if k != "name"}

        merge_part = f"MERGE (n:{self.node_type.value} {{name: $name}})"
        if other_props:
            set_props = ", ".join([f"n.{k} = ${k}" for k in other_props])
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
            props = ", ".join([f"{k}: ${k}" for k in self.properties])
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

    @staticmethod
    def get_node_schemas() -> dict[str, dict[str, Any]]:
        """Return schema definitions for all node types."""
        return {
            # ... existing schemas ...
            # Learning System Schemas
            "UsageEvent": {
                "description": "Tracks individual usage events for learning patterns",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "event_type": {
                        "type": "string",
                        "required": True,
                    },  # "function_query", "template_generation", "parameter_usage"
                    "timestamp": {"type": "datetime", "required": True},
                    "user_id": {"type": "string", "required": False},
                    "session_id": {"type": "string", "required": True},
                    "context": {
                        "type": "string",
                        "required": False,
                    },  # "Gateway", "Vision", "Perspective"
                    "function_name": {"type": "string", "required": False},
                    "template_name": {"type": "string", "required": False},
                    "parameters": {"type": "map", "required": False},
                    "success": {"type": "boolean", "required": False},
                    "execution_time": {"type": "float", "required": False},
                    "error_message": {"type": "string", "required": False},
                },
                "indexes": [
                    "timestamp",
                    "event_type",
                    "session_id",
                    "function_name",
                    "template_name",
                ],
            },
            "UserSession": {
                "description": "Represents a user interaction session for pattern analysis",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "user_id": {"type": "string", "required": False},
                    "start_time": {"type": "datetime", "required": True},
                    "end_time": {"type": "datetime", "required": False},
                    "duration": {"type": "integer", "required": False},  # seconds
                    "event_count": {"type": "integer", "required": False},
                    "success_rate": {"type": "float", "required": False},
                    "primary_context": {"type": "string", "required": False},
                    "unique_functions": {"type": "integer", "required": False},
                    "unique_templates": {"type": "integer", "required": False},
                    "session_type": {
                        "type": "string",
                        "required": False,
                    },  # "exploration", "development", "debugging"
                },
                "indexes": ["start_time", "user_id", "session_type"],
            },
            "PatternAnalysis": {
                "description": "Stores analyzed patterns from usage data",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "pattern_type": {
                        "type": "string",
                        "required": True,
                    },  # "co_occurrence", "sequence", "parameter_combo"
                    "confidence": {"type": "float", "required": True},
                    "support": {
                        "type": "float",
                        "required": True,
                    },  # frequency in dataset
                    "lift": {
                        "type": "float",
                        "required": False,
                    },  # association strength
                    "pattern_data": {"type": "map", "required": True},
                    "created_date": {"type": "datetime", "required": True},
                    "last_updated": {"type": "datetime", "required": True},
                    "usage_count": {"type": "integer", "required": True},
                    "success_rate": {"type": "float", "required": False},
                    "context_specific": {"type": "boolean", "required": False},
                    "relevance_score": {"type": "float", "required": False},
                },
                "indexes": [
                    "pattern_type",
                    "confidence",
                    "created_date",
                    "usage_count",
                ],
            },
            "Recommendation": {
                "description": "Stores generated recommendations for users",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "recommendation_type": {
                        "type": "string",
                        "required": True,
                    },  # "function", "template", "parameter"
                    "source_item": {"type": "string", "required": True},
                    "recommended_item": {"type": "string", "required": True},
                    "confidence_score": {"type": "float", "required": True},
                    "reasoning": {"type": "string", "required": False},
                    "context": {"type": "string", "required": False},
                    "created_date": {"type": "datetime", "required": True},
                    "usage_count": {"type": "integer", "required": False, "default": 0},
                    "success_count": {
                        "type": "integer",
                        "required": False,
                        "default": 0,
                    },
                    "feedback_score": {"type": "float", "required": False},
                    "is_active": {"type": "boolean", "required": True, "default": True},
                },
                "indexes": [
                    "recommendation_type",
                    "confidence_score",
                    "created_date",
                    "is_active",
                ],
            },
            "PerformanceMetric": {
                "description": "Stores performance metrics for templates and functions",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "metric_type": {
                        "type": "string",
                        "required": True,
                    },  # "generation_time", "success_rate", "usage_frequency"
                    "value": {"type": "float", "required": True},
                    "context": {"type": "string", "required": False},
                    "created_date": {"type": "datetime", "required": True},
                    "time_period": {"type": "string", "required": False},
                    "sample_size": {"type": "integer", "required": False},
                },
                "indexes": [
                    "metric_type",
                    "created_date",
                    "value",
                ],
            },
            # Export/Import Intelligence Node Definitions
            "ExportProfile": {
                "description": "Stores export configuration profiles and patterns",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "name": {"type": "string", "required": True},
                    "description": {"type": "string", "required": False},
                    "export_type": {
                        "type": "string", 
                        "required": True,
                    },  # "gateway_backup", "project_export", "resource_export", "custom"
                    "format": {
                        "type": "string",
                        "required": True,
                    },  # "gwbk", "proj", "json", "xml", "zip"
                    "include_patterns": {"type": "list", "required": False},
                    "exclude_patterns": {"type": "list", "required": False},
                    "configuration": {"type": "map", "required": False},
                    "created_date": {"type": "datetime", "required": True},
                    "last_used": {"type": "datetime", "required": False},
                    "usage_count": {"type": "integer", "required": True, "default": 0},
                    "success_rate": {"type": "float", "required": False},
                    "average_size": {"type": "integer", "required": False},
                    "compression_ratio": {"type": "float", "required": False},
                },
                "indexes": [
                    "export_type",
                    "format",
                    "created_date",
                    "usage_count",
                ],
            },
            "ImportJob": {
                "description": "Tracks import/deployment jobs and their outcomes",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "name": {"type": "string", "required": True},
                    "import_type": {
                        "type": "string",
                        "required": True,
                    },  # "project_import", "resource_merge", "full_restore", "selective_import"
                    "source_format": {"type": "string", "required": True},
                    "target_gateway": {"type": "string", "required": True},
                    "import_mode": {
                        "type": "string",
                        "required": True,
                    },  # "merge", "overwrite", "skip_conflicts", "selective"
                    "status": {
                        "type": "string",
                        "required": True,
                    },  # "pending", "running", "completed", "failed", "rolled_back"
                    "started_at": {"type": "datetime", "required": True},
                    "completed_at": {"type": "datetime", "required": False},
                    "duration": {"type": "integer", "required": False},
                    "error_message": {"type": "string", "required": False},
                    "resources_imported": {"type": "integer", "required": False},
                    "conflicts_resolved": {"type": "integer", "required": False},
                    "configuration": {"type": "map", "required": False},
                    "rollback_available": {"type": "boolean", "required": True, "default": False},
                    "rollback_id": {"type": "string", "required": False},
                },
                "indexes": [
                    "import_type",
                    "target_gateway",
                    "status",
                    "started_at",
                ],
            },
            "ResourceDependency": {
                "description": "Models dependencies between Ignition resources",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "source_resource": {"type": "string", "required": True},
                    "target_resource": {"type": "string", "required": True},
                    "dependency_type": {
                        "type": "string",
                        "required": True,
                    },  # "requires", "references", "optional", "conflict"
                    "resource_type": {
                        "type": "string",
                        "required": True,
                    },  # "tag_provider", "database", "security_zone", "device", "project"
                    "strength": {
                        "type": "string",
                        "required": True,
                    },  # "strong", "weak", "optional"
                    "validation_rule": {"type": "string", "required": False},
                    "error_impact": {
                        "type": "string",
                        "required": False,
                    },  # "critical", "warning", "info"
                    "discovered_date": {"type": "datetime", "required": True},
                    "last_validated": {"type": "datetime", "required": False},
                    "is_active": {"type": "boolean", "required": True, "default": True},
                },
                "indexes": [
                    "source_resource",
                    "target_resource",
                    "dependency_type",
                    "resource_type",
                ],
            },
            "DeploymentConfig": {
                "description": "Stores deployment configuration patterns and environments",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "name": {"type": "string", "required": True},
                    "environment": {
                        "type": "string",
                        "required": True,
                    },  # "development", "staging", "production", "test"
                    "gateway_host": {"type": "string", "required": True},
                    "deployment_strategy": {
                        "type": "string",
                        "required": True,
                    },  # "blue_green", "rolling", "direct", "canary"
                    "pre_deployment_checks": {"type": "list", "required": False},
                    "post_deployment_tests": {"type": "list", "required": False},
                    "rollback_strategy": {"type": "string", "required": False},
                    "notification_settings": {"type": "map", "required": False},
                    "maintenance_window": {"type": "map", "required": False},
                    "configuration": {"type": "map", "required": False},
                    "created_date": {"type": "datetime", "required": True},
                    "last_used": {"type": "datetime", "required": False},
                    "success_count": {"type": "integer", "required": True, "default": 0},
                    "failure_count": {"type": "integer", "required": True, "default": 0},
                    "is_active": {"type": "boolean", "required": True, "default": True},
                },
                "indexes": [
                    "environment",
                    "gateway_host",
                    "deployment_strategy",
                    "created_date",
                ],
            },
            "VersionTag": {
                "description": "Tracks version information for exported resources",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "version": {"type": "string", "required": True},
                    "tag_name": {"type": "string", "required": True},
                    "commit_hash": {"type": "string", "required": False},
                    "branch_name": {"type": "string", "required": False},
                    "created_date": {"type": "datetime", "required": True},
                    "author": {"type": "string", "required": False},
                    "release_notes": {"type": "string", "required": False},
                    "is_release": {"type": "boolean", "required": True, "default": False},
                    "is_prerelease": {"type": "boolean", "required": True, "default": False},
                    "compatibility_info": {"type": "map", "required": False},
                    "file_checksums": {"type": "map", "required": False},
                },
                "indexes": [
                    "version",
                    "tag_name", 
                    "created_date",
                    "is_release",
                ],
            },
            "GatewayResource": {
                "description": "Represents individual Ignition gateway resources",
                "properties": {
                    "id": {"type": "string", "required": True, "unique": True},
                    "name": {"type": "string", "required": True},
                    "resource_type": {
                        "type": "string",
                        "required": True,
                    },  # "project", "tag_provider", "database", "device", "security", "script"
                    "resource_path": {"type": "string", "required": True},
                    "gateway_host": {"type": "string", "required": True},
                    "configuration": {"type": "map", "required": False},
                    "checksum": {"type": "string", "required": False},
                    "size": {"type": "integer", "required": False},
                    "created_date": {"type": "datetime", "required": True},
                    "modified_date": {"type": "datetime", "required": False},
                    "exported_count": {"type": "integer", "required": True, "default": 0},
                    "last_exported": {"type": "datetime", "required": False},
                    "status": {
                        "type": "string",
                        "required": True,
                        "default": "active",
                    },  # "active", "disabled", "error", "removed"
                    "metadata": {"type": "map", "required": False},
                },
                "indexes": [
                    "resource_type",
                    "gateway_host",
                    "resource_path",
                    "status",
                ],
            },
        }
