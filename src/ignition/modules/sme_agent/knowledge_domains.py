"""Knowledge Domain Managers - Phase 11.2 SME Agent Core Capabilities.

Following crawl_mcp.py methodology for systematic development:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class DomainKnowledgeItem:
    """Represents a single knowledge item in a domain."""

    id: str
    name: str
    description: str
    category: str
    content: dict[str, Any]
    confidence: float = 0.0
    usage_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "content": self.content,
            "confidence": self.confidence,
            "usage_count": self.usage_count,
            "last_updated": self.last_updated.isoformat(),
            "tags": self.tags,
        }


@dataclass
class DomainQueryResult:
    """Result from domain knowledge query."""

    query: str
    domain: str
    results: list[DomainKnowledgeItem]
    confidence: float
    processing_time: float
    suggestions: list[str] = field(default_factory=list)
    related_topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "query": self.query,
            "domain": self.domain,
            "results": [item.to_dict() for item in self.results],
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "suggestions": self.suggestions,
            "related_topics": self.related_topics,
        }


class BaseDomainManager(ABC):
    """Base class for domain knowledge managers.

    Following crawl_mcp.py methodology for systematic implementation.
    """

    def __init__(self, domain_name: str, data_dir: str | None = None):
        """Initialize domain manager.

        Args:
            domain_name: Name of the knowledge domain
            data_dir: Directory for domain data storage
        """
        # Step 1: Environment Validation First
        self.domain_name = domain_name
        self.logger = logging.getLogger(f"{__name__}.{domain_name}")
        self.initialized = False

        # Set up data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path("data") / "sme_agent" / "domains" / domain_name
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Knowledge storage
        self.knowledge_items: dict[str, DomainKnowledgeItem] = {}
        self.categories: dict[str, list[str]] = {}
        self.statistics: dict[str, Any] = {
            "total_items": 0,
            "total_queries": 0,
            "average_confidence": 0.0,
            "last_updated": datetime.now(),
        }

        self.logger.info(f"Initialized {domain_name} domain manager")

    def validate_input(self, query: str, context: dict[str, Any] | None = None) -> bool:
        """Step 2: Comprehensive Input Validation.

        Args:
            query: User query string
            context: Optional context information

        Returns:
            True if input is valid, False otherwise
        """
        if not query or not isinstance(query, str):
            self.logger.error("Query must be a non-empty string")
            return False

        if query.strip() == "":
            self.logger.error("Query cannot be empty or whitespace only")
            return False

        if len(query) > 1000:
            self.logger.error("Query too long (max 1000 characters)")
            return False

        if context is not None and not isinstance(context, dict):
            self.logger.error("Context must be a dictionary")
            return False

        return True

    def handle_error(self, error: Exception, context: str) -> dict[str, Any]:
        """Step 3: Error Handling with User-Friendly Messages.

        Args:
            error: Exception that occurred
            context: Context where error occurred

        Returns:
            User-friendly error response
        """
        error_message = f"Error in {self.domain_name} domain: {context}"
        self.logger.error(f"{error_message}: {error!s}")

        # Create user-friendly error response
        return {
            "success": False,
            "error": error_message,
            "suggestion": f"Please try rephrasing your question about {self.domain_name}",
            "domain": self.domain_name,
            "timestamp": datetime.now().isoformat(),
        }

    @abstractmethod
    def load_knowledge_base(self) -> bool:
        """Load domain-specific knowledge base.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def query_knowledge(
        self, query: str, context: dict[str, Any] | None = None
    ) -> DomainQueryResult:
        """Query domain knowledge.

        Args:
            query: User query
            context: Optional context information

        Returns:
            Query result with knowledge items
        """
        pass

    def get_statistics(self) -> dict[str, Any]:
        """Get domain statistics."""
        return self.statistics.copy()

    def update_statistics(self):
        """Update domain statistics."""
        total_items = len(self.knowledge_items)
        avg_confidence = sum(
            item.confidence for item in self.knowledge_items.values()
        ) / max(total_items, 1)

        self.statistics.update(
            {
                "total_items": total_items,
                "total_queries": self.statistics.get("total_queries", 0) + 1,
                "average_confidence": avg_confidence,
                "last_updated": datetime.now(),
            }
        )

    def save_knowledge_base(self) -> bool:
        """Save knowledge base to disk.

        Returns:
            True if successful, False otherwise
        """
        try:
            knowledge_file = self.data_dir / "knowledge_base.json"
            stats_file = self.data_dir / "statistics.json"

            # Save knowledge items
            knowledge_data = {
                "domain": self.domain_name,
                "items": {k: v.to_dict() for k, v in self.knowledge_items.items()},
                "categories": self.categories,
                "saved_at": datetime.now().isoformat(),
            }

            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(knowledge_data, f, indent=2, ensure_ascii=False)

            # Save statistics
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(self.statistics, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(
                f"Saved {len(self.knowledge_items)} knowledge items for {self.domain_name}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to save knowledge base: {e}")
            return False

    def load_knowledge_base_from_file(self) -> bool:
        """Load knowledge base from disk.

        Returns:
            True if successful, False otherwise
        """
        try:
            knowledge_file = self.data_dir / "knowledge_base.json"
            stats_file = self.data_dir / "statistics.json"

            if knowledge_file.exists():
                with open(knowledge_file, encoding="utf-8") as f:
                    knowledge_data = json.load(f)

                # Load knowledge items
                for item_id, item_data in knowledge_data.get("items", {}).items():
                    item_data["last_updated"] = datetime.fromisoformat(
                        item_data["last_updated"]
                    )
                    self.knowledge_items[item_id] = DomainKnowledgeItem(**item_data)

                self.categories = knowledge_data.get("categories", {})

            if stats_file.exists():
                with open(stats_file, encoding="utf-8") as f:
                    self.statistics = json.load(f)
                    if "last_updated" in self.statistics:
                        self.statistics["last_updated"] = datetime.fromisoformat(
                            self.statistics["last_updated"]
                        )

            self.logger.info(
                f"Loaded {len(self.knowledge_items)} knowledge items for {self.domain_name}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
            return False


class GatewayScriptingDomainManager(BaseDomainManager):
    """Gateway Scripting Domain Manager.

    Provides expertise in:
    - Startup scripts
    - Shutdown scripts
    - Tag event scripts
    - Timer scripts
    - Message handlers
    """

    def __init__(self, data_dir: str | None = None):
        """Initialize Gateway Scripting domain manager."""
        super().__init__("gateway_scripting", data_dir)

        # Define script patterns and templates
        self.script_patterns = {
            "startup": {
                "description": "Gateway startup script patterns",
                "patterns": [
                    "system initialization",
                    "database connections",
                    "service startup",
                    "configuration loading",
                ],
            },
            "shutdown": {
                "description": "Gateway shutdown script patterns",
                "patterns": [
                    "cleanup operations",
                    "connection closing",
                    "service shutdown",
                    "resource cleanup",
                ],
            },
            "tag_events": {
                "description": "Tag event script patterns",
                "patterns": [
                    "value change handlers",
                    "quality change handlers",
                    "alarm processing",
                    "data validation",
                ],
            },
            "timers": {
                "description": "Timer script patterns",
                "patterns": [
                    "scheduled operations",
                    "periodic data collection",
                    "maintenance tasks",
                    "report generation",
                ],
            },
        }

        # Load knowledge base
        self.load_knowledge_base()

    def load_knowledge_base(self) -> bool:
        """Load gateway scripting knowledge base."""
        try:
            # First try to load from file
            if self.load_knowledge_base_from_file():
                self.initialized = True
                return True

            # If no saved data, create initial knowledge base
            self._create_initial_knowledge_base()
            self.initialized = True
            return True

        except Exception as e:
            self.logger.error(f"Failed to load gateway scripting knowledge: {e}")
            return False

    def _create_initial_knowledge_base(self):
        """Create initial knowledge base for gateway scripting."""
        # Startup script examples
        startup_examples = [
            {
                "id": "startup_db_init",
                "name": "Database Connection Initialization",
                "description": "Initialize database connections on gateway startup",
                "category": "startup",
                "content": {
                    "code_template": """# Gateway startup script - Database initialization
import system

# Initialize database connections
try:
    # Test database connection
    result = system.db.runQuery("SELECT 1", "your_database")
    logger = system.util.getLogger("GatewayStartup")
    logger.info("Database connection verified successfully")
except Exception as e:
    logger = system.util.getLogger("GatewayStartup")
    logger.error("Database connection failed: " + str(e))""",
                    "best_practices": [
                        "Always include error handling",
                        "Use proper logging",
                        "Test connections before use",
                        "Handle connection failures gracefully",
                    ],
                    "common_issues": [
                        "Database not available at startup",
                        "Connection string errors",
                        "Authentication failures",
                    ],
                },
                "confidence": 0.9,
                "tags": ["startup", "database", "initialization"],
            },
            {
                "id": "startup_service_init",
                "name": "Service Initialization",
                "description": "Initialize external services on gateway startup",
                "category": "startup",
                "content": {
                    "code_template": """# Gateway startup script - Service initialization
import system

# Initialize external services
logger = system.util.getLogger("ServiceInit")

try:
    # Initialize OPC-UA connections
    # Configure email settings
    # Set up alarm pipelines
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error("Service initialization failed: " + str(e))""",
                    "best_practices": [
                        "Initialize services in correct order",
                        "Check service dependencies",
                        "Implement retry logic for critical services",
                    ],
                },
                "confidence": 0.85,
                "tags": ["startup", "services", "initialization"],
            },
        ]

        # Add startup examples
        for example in startup_examples:
            item = DomainKnowledgeItem(**example)
            self.knowledge_items[item.id] = item

        # Tag event script examples
        tag_event_examples = [
            {
                "id": "tag_value_change",
                "name": "Tag Value Change Handler",
                "description": "Handle tag value changes with validation and processing",
                "category": "tag_events",
                "content": {
                    "code_template": """# Tag event script - Value change handler
def valueChanged(tag, tagPath, previousValue, currentValue, initialChange, missedEvents):
    import system

    logger = system.util.getLogger("TagEvents")

    try:
        # Skip initial changes if needed
        if initialChange:
            return

        # Validate new value
        if currentValue.quality.isGood():
            # Process the value change
            logger.info("Tag %s changed from %s to %s" % (tagPath, previousValue.value, currentValue.value))

            # Add your processing logic here
            # Example: trigger alarms, update databases, etc.

        else:
            logger.warn("Tag %s has bad quality: %s" % (tagPath, currentValue.quality))

    except Exception as e:
        logger.error("Error processing tag change for %s: %s" % (tagPath, str(e)))""",
                    "best_practices": [
                        "Always check tag quality",
                        "Handle initial changes appropriately",
                        "Include comprehensive error handling",
                        "Log important events",
                        "Avoid blocking operations",
                    ],
                    "parameters": [
                        "tag - Tag reference object",
                        "tagPath - String path to the tag",
                        "previousValue - Previous qualified value",
                        "currentValue - Current qualified value",
                        "initialChange - Boolean indicating initial change",
                        "missedEvents - Number of missed events",
                    ],
                },
                "confidence": 0.95,
                "tags": ["tag_events", "value_change", "validation"],
            }
        ]

        # Add tag event examples
        for example in tag_event_examples:
            item = DomainKnowledgeItem(**example)
            self.knowledge_items[item.id] = item

        # Update categories
        self.categories = {
            "startup": [
                item.id
                for item in self.knowledge_items.values()
                if item.category == "startup"
            ],
            "tag_events": [
                item.id
                for item in self.knowledge_items.values()
                if item.category == "tag_events"
            ],
            "shutdown": [],
            "timers": [],
        }

        # Save the initial knowledge base
        self.save_knowledge_base()
        self.logger.info(
            f"Created initial knowledge base with {len(self.knowledge_items)} items"
        )

    def query_knowledge(
        self, query: str, context: dict[str, Any] | None = None
    ) -> DomainQueryResult:
        """Query gateway scripting knowledge.

        Args:
            query: User query about gateway scripting
            context: Optional context information

        Returns:
            Query result with relevant knowledge items
        """
        start_time = time.time()

        # Step 2: Comprehensive Input Validation
        if not self.validate_input(query, context):
            return DomainQueryResult(
                query=query,
                domain=self.domain_name,
                results=[],
                confidence=0.0,
                processing_time=time.time() - start_time,
                suggestions=["Please provide a valid query about gateway scripting"],
            )

        try:
            # Normalize query
            query_lower = query.lower().strip()
            results = []

            # Search through knowledge items
            for item in self.knowledge_items.values():
                score = self._calculate_relevance_score(query_lower, item)
                if score > 0.3:  # Minimum relevance threshold
                    item.usage_count += 1
                    results.append(item)

            # Sort by relevance (using confidence as proxy for now)
            results.sort(key=lambda x: x.confidence, reverse=True)

            # Calculate overall confidence
            confidence = (
                sum(item.confidence for item in results) / max(len(results), 1)
                if results
                else 0.0
            )

            # Generate suggestions and related topics
            suggestions = self._generate_suggestions(results)
            related_topics = self._get_related_topics(query_lower)

            # Update statistics
            self.update_statistics()

            processing_time = time.time() - start_time

            return DomainQueryResult(
                query=query,
                domain=self.domain_name,
                results=results[:5],  # Limit to top 5 results
                confidence=confidence,
                processing_time=processing_time,
                suggestions=suggestions,
                related_topics=related_topics,
            )

        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            return DomainQueryResult(
                query=query,
                domain=self.domain_name,
                results=[],
                confidence=0.0,
                processing_time=time.time() - start_time,
                suggestions=[
                    "An error occurred while processing your query. Please try again."
                ],
            )

    def _calculate_relevance_score(
        self, query: str, item: DomainKnowledgeItem
    ) -> float:
        """Calculate relevance score between query and knowledge item."""
        score = 0.0

        # Check name match
        if query in item.name.lower():
            score += 0.4

        # Check description match
        if query in item.description.lower():
            score += 0.3

        # Check tags match
        for tag in item.tags:
            if query in tag.lower() or tag.lower() in query:
                score += 0.2

        # Check category match
        if query in item.category.lower():
            score += 0.3

        # Check content match (basic keyword matching)
        content_str = str(item.content).lower()
        query_words = query.split()
        for word in query_words:
            if len(word) > 3 and word in content_str:
                score += 0.1

        return min(score, 1.0)  # Cap at 1.0

    def _generate_suggestions(self, results: list[DomainKnowledgeItem]) -> list[str]:
        """Generate suggestions based on query and results."""
        suggestions = []

        if not results:
            suggestions.extend(
                [
                    "Try asking about 'startup scripts' or 'tag event handlers'",
                    "Ask about 'timer scripts' or 'shutdown procedures'",
                    "Request examples for 'gateway scripting best practices'",
                ]
            )
        elif len(results) < 3:
            # Suggest related categories
            categories = {item.category for item in results}
            for category in self.script_patterns:
                if category not in categories:
                    suggestions.append(
                        f"You might also be interested in {category} scripts"
                    )

        return suggestions[:3]  # Limit to 3 suggestions

    def _get_related_topics(self, query: str) -> list[str]:
        """Get related topics based on query."""
        related = []

        # Map query keywords to related topics
        topic_mapping = {
            "startup": ["initialization", "database connections", "service startup"],
            "shutdown": ["cleanup", "resource management", "graceful shutdown"],
            "tag": ["value changes", "quality monitoring", "event handling"],
            "timer": ["scheduled tasks", "periodic operations", "maintenance"],
            "database": ["connections", "queries", "transactions"],
            "opc": ["communication", "device connections", "data acquisition"],
        }

        for keyword, topics in topic_mapping.items():
            if keyword in query:
                related.extend(topics)

        return related[:5]  # Limit to 5 related topics

    def get_script_template(self, script_type: str) -> dict[str, Any] | None:
        """Get script template for specific type.

        Args:
            script_type: Type of script (startup, shutdown, tag_events, timers)

        Returns:
            Script template information or None if not found
        """
        if script_type not in self.script_patterns:
            return None

        # Find relevant knowledge items for this script type
        relevant_items = [
            item
            for item in self.knowledge_items.values()
            if item.category == script_type
        ]

        if not relevant_items:
            return None

        # Return the highest confidence item
        best_item = max(relevant_items, key=lambda x: x.confidence)

        return {
            "script_type": script_type,
            "template": best_item.content.get("code_template", ""),
            "best_practices": best_item.content.get("best_practices", []),
            "common_issues": best_item.content.get("common_issues", []),
            "description": best_item.description,
        }

    def analyze_script_quality(self, script_content: str) -> dict[str, Any]:
        """Analyze script quality and provide recommendations.

        Args:
            script_content: Script source code to analyze

        Returns:
            Analysis results with recommendations
        """
        if not script_content or not isinstance(script_content, str):
            return {"success": False, "error": "Invalid script content provided"}

        analysis = {
            "success": True,
            "score": 0.0,
            "issues": [],
            "recommendations": [],
            "best_practices_followed": [],
            "metrics": {
                "lines_of_code": len(script_content.split("\n")),
                "has_error_handling": False,
                "has_logging": False,
                "has_comments": False,
            },
        }

        script_lower = script_content.lower()

        # Check for error handling
        if any(keyword in script_lower for keyword in ["try:", "except:", "finally:"]):
            analysis["metrics"]["has_error_handling"] = True
            analysis["best_practices_followed"].append("Includes error handling")
            analysis["score"] += 0.3
        else:
            analysis["issues"].append("Missing error handling (try/except blocks)")
            analysis["recommendations"].append(
                "Add try/except blocks for robust error handling"
            )

        # Check for logging
        if any(
            keyword in script_lower
            for keyword in ["logger", "log", "system.util.getlogger"]
        ):
            analysis["metrics"]["has_logging"] = True
            analysis["best_practices_followed"].append("Includes logging")
            analysis["score"] += 0.3
        else:
            analysis["issues"].append("Missing logging statements")
            analysis["recommendations"].append(
                "Add logging for debugging and monitoring"
            )

        # Check for comments
        if "#" in script_content:
            analysis["metrics"]["has_comments"] = True
            analysis["best_practices_followed"].append("Includes comments")
            analysis["score"] += 0.2
        else:
            analysis["issues"].append("Missing code comments")
            analysis["recommendations"].append("Add comments to explain complex logic")

        # Check for common patterns
        if "initialchange" in script_lower:
            analysis["best_practices_followed"].append("Handles initial change events")
            analysis["score"] += 0.1

        if "quality" in script_lower:
            analysis["best_practices_followed"].append("Checks tag quality")
            analysis["score"] += 0.1

        # Cap score at 1.0
        analysis["score"] = min(analysis["score"], 1.0)

        return analysis


class SystemFunctionsDomainManager(BaseDomainManager):
    """System Functions Domain Manager.

    Provides expertise in Ignition system functions with Neo4j integration.
    """

    def __init__(self, neo4j_client=None, data_dir: str | None = None):
        """Initialize System Functions domain manager.

        Args:
            neo4j_client: Neo4j client for knowledge graph access
            data_dir: Directory for domain data storage
        """
        super().__init__("system_functions", data_dir)
        self.neo4j_client = neo4j_client
        self.function_cache: dict[str, Any] = {}

        # Load knowledge base
        self.load_knowledge_base()

    def load_knowledge_base(self) -> bool:
        """Load system functions knowledge base."""
        try:
            # Load from Neo4j if available
            has_neo4j = (
                self.neo4j_client
                and hasattr(self.neo4j_client, "is_connected")
                and self.neo4j_client.is_connected()
            )

            if has_neo4j:
                self._load_from_neo4j()
            else:
                # Load from file or create initial knowledge base
                if not self.load_knowledge_base_from_file():
                    self._create_initial_knowledge_base()

            self.initialized = True
            return True

        except Exception as e:
            self.logger.error(f"Failed to load system functions knowledge: {e}")
            return False

    def _load_from_neo4j(self):
        """Load system functions from Neo4j knowledge graph."""
        try:
            # Query for all system functions
            query = """
            MATCH (f:Function)
            WHERE f.name CONTAINS 'system' OR f.module CONTAINS 'system'
            RETURN f.name as name, f.module as module, f.description as description,
                   f.parameters as parameters, f.return_type as return_type
            ORDER BY f.module, f.name
            """

            results = self.neo4j_client.execute_query(query)

            for record in results:
                function_id = (
                    f"{record.get('module', 'system')}.{record.get('name', 'unknown')}"
                )

                # Create knowledge item for this function
                item = DomainKnowledgeItem(
                    id=function_id,
                    name=record.get("name", "Unknown Function"),
                    description=record.get("description", "No description available"),
                    category=self._categorize_function(record.get("name", "")),
                    content={
                        "module": record.get("module", "system"),
                        "parameters": record.get("parameters", []),
                        "return_type": record.get("return_type", "Unknown"),
                        "usage_examples": [],
                    },
                    confidence=0.8,
                    tags=self._generate_function_tags(
                        record.get("name", ""), record.get("module", "")
                    ),
                )

                self.knowledge_items[function_id] = item

            self.logger.info(
                f"Loaded {len(self.knowledge_items)} system functions from Neo4j"
            )

        except Exception as e:
            self.logger.error(f"Failed to load from Neo4j: {e}")
            self._create_initial_knowledge_base()

    def _create_initial_knowledge_base(self):
        """Create initial knowledge base for system functions."""
        # Common Ignition system functions
        system_functions = [
            {
                "id": "system.device.listDevices",
                "name": "listDevices",
                "description": "Get list of all configured devices with status information",
                "category": "device",
                "content": {
                    "module": "system.device",
                    "parameters": [],
                    "return_type": "Dataset",
                    "usage_examples": [
                        "devices = system.device.listDevices()",
                        "for row in range(devices.rowCount):",
                        "    print devices.getValueAt(row, 'Name')",
                    ],
                },
                "confidence": 0.9,
                "tags": ["device", "list", "status"],
            },
            {
                "id": "system.opcua.browseServer",
                "name": "browseServer",
                "description": "Browse an OPC-UA server structure",
                "category": "opcua",
                "content": {
                    "module": "system.opcua",
                    "parameters": ["connectionName", "nodeId", "browseFilter"],
                    "return_type": "List[BrowseElement]",
                    "usage_examples": [
                        "nodes = system.opcua.browseServer('MyOPCConnection', '2:MyFolder')",
                        "for node in nodes:",
                        "    print node.getDisplayName()",
                    ],
                },
                "confidence": 0.85,
                "tags": ["opcua", "browse", "server"],
            },
            {
                "id": "system.file.readFileAsString",
                "name": "readFileAsString",
                "description": "Read file contents as string",
                "category": "file",
                "content": {
                    "module": "system.file",
                    "parameters": ["filepath"],
                    "return_type": "String",
                    "usage_examples": [
                        "content = system.file.readFileAsString('/path/to/file.txt')",
                        "print content",
                    ],
                },
                "confidence": 0.9,
                "tags": ["file", "read", "string"],
            },
        ]

        # Add system functions
        for func_data in system_functions:
            item = DomainKnowledgeItem(**func_data)
            self.knowledge_items[item.id] = item

        # Update categories
        self.categories = {}
        for item in self.knowledge_items.values():
            if item.category not in self.categories:
                self.categories[item.category] = []
            self.categories[item.category].append(item.id)

        # Save the initial knowledge base
        self.save_knowledge_base()
        self.logger.info(
            f"Created initial system functions knowledge base with {len(self.knowledge_items)} items"
        )

    def _categorize_function(self, function_name: str) -> str:
        """Categorize function based on name."""
        name_lower = function_name.lower()

        if any(keyword in name_lower for keyword in ["device", "driver"]):
            return "device"
        elif any(keyword in name_lower for keyword in ["opc", "opcua"]):
            return "opcua"
        elif any(keyword in name_lower for keyword in ["file", "read", "write"]):
            return "file"
        elif any(keyword in name_lower for keyword in ["nav", "window", "screen"]):
            return "navigation"
        elif any(keyword in name_lower for keyword in ["db", "database", "query"]):
            return "database"
        elif any(keyword in name_lower for keyword in ["tag", "browse"]):
            return "tag"
        else:
            return "utility"

    def _generate_function_tags(self, function_name: str, module: str) -> list[str]:
        """Generate tags for a function."""
        tags = []

        # Add module-based tags
        if module:
            tags.append(module.split(".")[-1])  # Last part of module name

        # Add function name parts as tags
        name_parts = function_name.lower().split("_")
        tags.extend(name_parts)

        # Add common operation tags
        name_lower = function_name.lower()
        if any(op in name_lower for op in ["get", "read", "fetch"]):
            tags.append("read")
        if any(op in name_lower for op in ["set", "write", "update"]):
            tags.append("write")
        if any(op in name_lower for op in ["list", "browse", "find"]):
            tags.append("query")

        return list(set(tags))  # Remove duplicates

    def query_knowledge(
        self, query: str, context: dict[str, Any] | None = None
    ) -> DomainQueryResult:
        """Query system functions knowledge.

        Args:
            query: User query about system functions
            context: Optional context information

        Returns:
            Query result with relevant system functions
        """
        start_time = time.time()

        # Step 2: Comprehensive Input Validation
        if not self.validate_input(query, context):
            return DomainQueryResult(
                query=query,
                domain=self.domain_name,
                results=[],
                confidence=0.0,
                processing_time=time.time() - start_time,
                suggestions=[
                    "Please provide a valid query about Ignition system functions"
                ],
            )

        try:
            # Normalize query
            query_lower = query.lower().strip()
            results = []

            # Search through knowledge items
            for item in self.knowledge_items.values():
                score = self._calculate_function_relevance(query_lower, item)
                if score > 0.2:  # Lower threshold for system functions
                    item.usage_count += 1
                    results.append(item)

            # Sort by relevance score (calculated dynamically)
            results.sort(
                key=lambda x: self._calculate_function_relevance(query_lower, x),
                reverse=True,
            )

            # Calculate overall confidence
            confidence = (
                sum(item.confidence for item in results) / max(len(results), 1)
                if results
                else 0.0
            )

            # Generate suggestions and related topics
            suggestions = self._generate_function_suggestions(results)
            related_topics = self._get_function_related_topics(query_lower)

            # Update statistics
            self.update_statistics()

            processing_time = time.time() - start_time

            return DomainQueryResult(
                query=query,
                domain=self.domain_name,
                results=results[:10],  # More results for system functions
                confidence=confidence,
                processing_time=processing_time,
                suggestions=suggestions,
                related_topics=related_topics,
            )

        except Exception as e:
            self.logger.error(f"System function query processing failed: {e}")
            return DomainQueryResult(
                query=query,
                domain=self.domain_name,
                results=[],
                confidence=0.0,
                processing_time=time.time() - start_time,
                suggestions=[
                    "An error occurred while searching system functions. Please try again."
                ],
            )

    def _calculate_function_relevance(
        self, query: str, item: DomainKnowledgeItem
    ) -> float:
        """Calculate relevance score for system function."""
        score = 0.0

        # Exact function name match gets highest score
        if query == item.name.lower():
            score += 0.8
        elif query in item.name.lower():
            score += 0.6

        # Module match
        module = item.content.get("module", "")
        if query in module.lower():
            score += 0.4

        # Description match
        if query in item.description.lower():
            score += 0.3

        # Tags match
        for tag in item.tags:
            if query == tag.lower():
                score += 0.5
            elif query in tag.lower() or tag.lower() in query:
                score += 0.2

        # Category match
        if query == item.category.lower():
            score += 0.4
        elif query in item.category.lower():
            score += 0.2

        return min(score, 1.0)

    def _generate_function_suggestions(
        self, results: list[DomainKnowledgeItem]
    ) -> list[str]:
        """Generate suggestions for system function queries."""
        suggestions = []

        if not results:
            suggestions.extend(
                [
                    "Try searching for 'system.device' functions for device management",
                    "Look for 'system.opcua' functions for OPC-UA operations",
                    "Search 'system.file' for file operations",
                    "Try 'system.nav' for navigation functions",
                ]
            )
        else:
            # Suggest related categories
            found_categories = {item.category for item in results}
            all_categories = set(self.categories.keys())
            missing_categories = all_categories - found_categories

            for category in list(missing_categories)[:2]:
                suggestions.append(f"Also check {category} functions")

        return suggestions[:3]

    def _get_function_related_topics(self, query: str) -> list[str]:
        """Get related topics for system function queries."""
        related = []

        # Map query keywords to related system function topics
        topic_mapping = {
            "device": ["drivers", "connections", "status", "configuration"],
            "opc": ["browsing", "reading", "writing", "subscriptions"],
            "file": ["reading", "writing", "paths", "encoding"],
            "nav": ["windows", "screens", "navigation", "client"],
            "database": ["queries", "connections", "transactions"],
            "tag": ["browsing", "reading", "writing", "history"],
            "alarm": ["acknowledgment", "shelving", "pipelines"],
            "security": ["authentication", "authorization", "users", "roles"],
        }

        for keyword, topics in topic_mapping.items():
            if keyword in query:
                related.extend(topics)

        return related[:5]

    def get_function_details(self, function_name: str) -> dict[str, Any] | None:
        """Get detailed information about a specific system function.

        Args:
            function_name: Name of the system function

        Returns:
            Function details or None if not found
        """
        # Try exact match first
        if function_name in self.knowledge_items:
            item = self.knowledge_items[function_name]
        else:
            # Try partial match
            matches = [
                item
                for item in self.knowledge_items.values()
                if function_name.lower() in item.name.lower()
                or function_name.lower() in item.id.lower()
            ]
            if not matches:
                return None
            item = matches[0]  # Take first match

        return {
            "name": item.name,
            "full_name": item.id,
            "description": item.description,
            "module": item.content.get("module", ""),
            "parameters": item.content.get("parameters", []),
            "return_type": item.content.get("return_type", "Unknown"),
            "usage_examples": item.content.get("usage_examples", []),
            "category": item.category,
            "tags": item.tags,
            "confidence": item.confidence,
            "usage_count": item.usage_count,
        }


# Export all domain managers
__all__ = [
    "BaseDomainManager",
    "DomainKnowledgeItem",
    "DomainQueryResult",
    "GatewayScriptingDomainManager",
    "SystemFunctionsDomainManager",
]
