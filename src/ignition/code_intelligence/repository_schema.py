"""Repository Analysis Schema for Neo4j Graph Database.

This module extends the existing code intelligence system to provide comprehensive
repository analysis for external repositories like Pydantic AI. It creates a
detailed graph representation including repository structure, dependencies,
documentation, and relationships for LLM agent context.

Based on Pydantic AI repository structure:
https://github.com/pydantic/pydantic-ai.git
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RepositoryNodeType(Enum):
    """Repository-specific node types."""
    REPOSITORY = "Repository"
    DIRECTORY = "Directory"
    FILE = "File"
    PACKAGE = "Package"
    MODULE = "Module"
    FUNCTION = "Function"
    CLASS = "Class"
    METHOD = "Method"
    VARIABLE = "Variable"
    IMPORT = "Import"
    DEPENDENCY = "Dependency"
    CONFIGURATION = "Configuration"
    DOCUMENTATION = "Documentation"
    TEST = "Test"
    EXAMPLE = "Example"
    AGENT = "Agent"
    TOOL = "Tool"
    MODEL_INTEGRATION = "ModelIntegration"


class RepositoryRelationType(Enum):
    """Repository-specific relationship types."""
    CONTAINS = "CONTAINS"
    IMPORTS = "IMPORTS"
    DEPENDS_ON = "DEPENDS_ON"
    INHERITS_FROM = "INHERITS_FROM"
    IMPLEMENTS = "IMPLEMENTS"
    CALLS = "CALLS"
    DEFINES = "DEFINES"
    USES = "USES"
    TESTS = "TESTS"
    DOCUMENTS = "DOCUMENTS"
    EXTENDS = "EXTENDS"
    CONFIGURES = "CONFIGURES"
    PROVIDES = "PROVIDES"
    REQUIRES = "REQUIRES"
    SIMILAR_TO = "SIMILAR_TO"


@dataclass
class RepositoryNode:
    """Represents a repository in the graph database."""
    name: str
    url: str
    description: str
    language: str
    stars: int
    forks: int
    size_kb: int
    created_at: datetime
    updated_at: datetime
    license: Optional[str] = None
    topics: Optional[list[str]] = None
    readme_content: Optional[str] = None
    embedding: Optional[list[float]] = None


@dataclass
class DirectoryNode:
    """Represents a directory in the repository."""
    name: str
    path: str
    repository: str
    file_count: int
    subdirectory_count: int
    total_lines: int
    purpose: Optional[str] = None
    readme_content: Optional[str] = None
    embedding: Optional[list[float]] = None


@dataclass
class FileNode:
    """Enhanced file node for repository analysis."""
    name: str
    path: str
    repository: str
    directory: str
    extension: str
    size_bytes: int
    lines: int
    language: str
    file_type: str  # source, test, config, doc, example
    complexity: Optional[float] = None
    maintainability_index: Optional[float] = None
    last_modified: Optional[datetime] = None
    content_hash: Optional[str] = None
    docstring: Optional[str] = None
    purpose: Optional[str] = None
    embedding: Optional[list[float]] = None


@dataclass
class PackageNode:
    """Represents a Python package."""
    name: str
    path: str
    repository: str
    version: Optional[str] = None
    description: Optional[str] = None
    module_count: int = 0
    init_file: Optional[str] = None
    exports: Optional[list[str]] = None
    embedding: Optional[list[float]] = None


@dataclass
class ModuleNode:
    """Represents a Python module."""
    name: str
    path: str
    repository: str
    package: Optional[str] = None
    docstring: Optional[str] = None
    function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    complexity: Optional[float] = None
    purpose: Optional[str] = None
    exports: Optional[list[str]] = None
    embedding: Optional[list[float]] = None


@dataclass
class FunctionNode:
    """Enhanced function node for repository analysis."""
    name: str
    module: str
    repository: str
    signature: str
    docstring: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    parameters: Optional[list[str]] = None
    return_type: Optional[str] = None
    complexity: Optional[float] = None
    is_async: bool = False
    is_generator: bool = False
    is_property: bool = False
    decorators: Optional[list[str]] = None
    purpose: Optional[str] = None
    embedding: Optional[list[float]] = None


@dataclass
class ClassNode:
    """Enhanced class node for repository analysis."""
    name: str
    module: str
    repository: str
    docstring: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    base_classes: Optional[list[str]] = None
    method_count: int = 0
    property_count: int = 0
    complexity: Optional[float] = None
    is_abstract: bool = False
    is_dataclass: bool = False
    is_pydantic_model: bool = False
    decorators: Optional[list[str]] = None
    purpose: Optional[str] = None
    embedding: Optional[list[float]] = None


@dataclass
class DependencyNode:
    """Represents external dependencies."""
    name: str
    repository: str
    dependency_type: str  # runtime, dev, optional
    source: str  # pyproject.toml, requirements.txt, etc.
    version: Optional[str] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None


@dataclass
class AgentNode:
    """Represents AI agents in the repository."""
    name: str
    module: str
    repository: str
    agent_type: str  # simple, structured, streaming, etc.
    model_support: list[str]  # openai, anthropic, etc.
    capabilities: list[str]
    docstring: Optional[str] = None
    example_usage: Optional[str] = None
    embedding: Optional[list[float]] = None


@dataclass
class ToolNode:
    """Represents tools/functions available to agents."""
    name: str
    module: str
    repository: str
    tool_type: str  # function, class, integration
    parameters: Optional[list[str]] = None
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    example_usage: Optional[str] = None
    embedding: Optional[list[float]] = None


class RepositorySchema:
    """Manages Neo4j schema for repository analysis."""

    def __init__(self, graph_client):
        """Initialize with graph client."""
        self.client = graph_client

    def create_repository_schema(self) -> bool:
        """Create the complete schema for repository analysis."""
        try:
            # Create constraints
            self._create_repository_constraints()

            # Create indexes
            self._create_repository_indexes()

            # Create vector indexes
            self._create_repository_vector_indexes()

            logger.info("Repository analysis schema created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create repository schema: {e}")
            return False

    def _create_repository_constraints(self) -> None:
        """Create uniqueness constraints for repository nodes."""
        constraints = [
            # Repository constraints
            "CREATE CONSTRAINT repository_url IF NOT EXISTS FOR (r:Repository) REQUIRE r.url IS UNIQUE",
            
            # Directory constraints
            "CREATE CONSTRAINT directory_path IF NOT EXISTS FOR (d:Directory) REQUIRE (d.path, d.repository) IS UNIQUE",
            
            # File constraints
            "CREATE CONSTRAINT file_path IF NOT EXISTS FOR (f:File) REQUIRE (f.path, f.repository) IS UNIQUE",
            
            # Package constraints
            "CREATE CONSTRAINT package_path IF NOT EXISTS FOR (p:Package) REQUIRE (p.path, p.repository) IS UNIQUE",
            
            # Module constraints
            "CREATE CONSTRAINT module_path IF NOT EXISTS FOR (m:Module) REQUIRE (m.path, m.repository) IS UNIQUE",
            
            # Function constraints
            "CREATE CONSTRAINT function_unique IF NOT EXISTS FOR (f:Function) REQUIRE (f.name, f.module, f.repository, f.start_line) IS UNIQUE",
            
            # Class constraints
            "CREATE CONSTRAINT class_unique IF NOT EXISTS FOR (c:Class) REQUIRE (c.name, c.module, c.repository, c.start_line) IS UNIQUE",
            
            # Dependency constraints
            "CREATE CONSTRAINT dependency_unique IF NOT EXISTS FOR (d:Dependency) REQUIRE (d.name, d.repository) IS UNIQUE",
            
            # Agent constraints
            "CREATE CONSTRAINT agent_unique IF NOT EXISTS FOR (a:Agent) REQUIRE (a.name, a.module, a.repository) IS UNIQUE",
            
            # Tool constraints
            "CREATE CONSTRAINT tool_unique IF NOT EXISTS FOR (t:Tool) REQUIRE (t.name, t.module, t.repository) IS UNIQUE",
        ]

        for constraint in constraints:
            try:
                self.client.execute_query(constraint)
                logger.debug(f"Created constraint: {constraint}")
            except Exception as e:
                logger.debug(f"Constraint may already exist: {e}")

    def _create_repository_indexes(self) -> None:
        """Create performance indexes for repository analysis."""
        indexes = [
            # Repository indexes
            "CREATE INDEX repository_language IF NOT EXISTS FOR (r:Repository) ON (r.language)",
            "CREATE INDEX repository_stars IF NOT EXISTS FOR (r:Repository) ON (r.stars)",
            "CREATE INDEX repository_updated IF NOT EXISTS FOR (r:Repository) ON (r.updated_at)",
            
            # File indexes
            "CREATE INDEX file_extension IF NOT EXISTS FOR (f:File) ON (f.extension)",
            "CREATE INDEX file_language IF NOT EXISTS FOR (f:File) ON (f.language)",
            "CREATE INDEX file_type IF NOT EXISTS FOR (f:File) ON (f.file_type)",
            "CREATE INDEX file_size IF NOT EXISTS FOR (f:File) ON (f.size_bytes)",
            "CREATE INDEX file_complexity IF NOT EXISTS FOR (f:File) ON (f.complexity)",
            
            # Module indexes
            "CREATE INDEX module_complexity IF NOT EXISTS FOR (m:Module) ON (m.complexity)",
            "CREATE INDEX module_function_count IF NOT EXISTS FOR (m:Module) ON (m.function_count)",
            "CREATE INDEX module_class_count IF NOT EXISTS FOR (m:Module) ON (m.class_count)",
            
            # Function indexes
            "CREATE INDEX function_complexity IF NOT EXISTS FOR (f:Function) ON (f.complexity)",
            "CREATE INDEX function_async IF NOT EXISTS FOR (f:Function) ON (f.is_async)",
            "CREATE INDEX function_parameters IF NOT EXISTS FOR (f:Function) ON (f.parameters)",
            
            # Class indexes
            "CREATE INDEX class_complexity IF NOT EXISTS FOR (c:Class) ON (c.complexity)",
            "CREATE INDEX class_method_count IF NOT EXISTS FOR (c:Class) ON (c.method_count)",
            "CREATE INDEX class_pydantic IF NOT EXISTS FOR (c:Class) ON (c.is_pydantic_model)",
            
            # Dependency indexes
            "CREATE INDEX dependency_type IF NOT EXISTS FOR (d:Dependency) ON (d.dependency_type)",
            "CREATE INDEX dependency_version IF NOT EXISTS FOR (d:Dependency) ON (d.version)",
            
            # Agent indexes
            "CREATE INDEX agent_type IF NOT EXISTS FOR (a:Agent) ON (a.agent_type)",
            "CREATE INDEX agent_model_support IF NOT EXISTS FOR (a:Agent) ON (a.model_support)",
            
            # Tool indexes
            "CREATE INDEX tool_type IF NOT EXISTS FOR (t:Tool) ON (t.tool_type)",
        ]

        for index in indexes:
            try:
                self.client.execute_query(index)
                logger.debug(f"Created index: {index}")
            except Exception as e:
                logger.debug(f"Index may already exist: {e}")

    def _create_repository_vector_indexes(self) -> None:
        """Create vector indexes for repository embeddings."""
        vector_indexes = [
            {
                "name": "repository_embeddings",
                "query": "CREATE VECTOR INDEX repository_embeddings IF NOT EXISTS FOR (r:Repository) ON (r.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "directory_embeddings",
                "query": "CREATE VECTOR INDEX directory_embeddings IF NOT EXISTS FOR (d:Directory) ON (d.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "file_embeddings",
                "query": "CREATE VECTOR INDEX file_embeddings IF NOT EXISTS FOR (f:File) ON (f.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "package_embeddings",
                "query": "CREATE VECTOR INDEX package_embeddings IF NOT EXISTS FOR (p:Package) ON (p.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "module_embeddings",
                "query": "CREATE VECTOR INDEX module_embeddings IF NOT EXISTS FOR (m:Module) ON (m.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "function_embeddings",
                "query": "CREATE VECTOR INDEX function_embeddings IF NOT EXISTS FOR (f:Function) ON (f.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "class_embeddings",
                "query": "CREATE VECTOR INDEX class_embeddings IF NOT EXISTS FOR (c:Class) ON (c.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "agent_embeddings",
                "query": "CREATE VECTOR INDEX agent_embeddings IF NOT EXISTS FOR (a:Agent) ON (a.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "tool_embeddings",
                "query": "CREATE VECTOR INDEX tool_embeddings IF NOT EXISTS FOR (t:Tool) ON (t.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
        ]

        for index_info in vector_indexes:
            try:
                self.client.execute_query(index_info["query"])
                logger.info(f"Created vector index: {index_info['name']}")
            except Exception as e:
                logger.debug(f"Vector index {index_info['name']} may already exist: {e}")

    def get_repository_schema_info(self) -> dict[str, Any]:
        """Get information about the repository schema."""
        try:
            # Get node counts for repository-specific nodes
            node_counts = {}
            node_types = [
                "Repository", "Directory", "File", "Package", "Module",
                "Function", "Class", "Dependency", "Agent", "Tool"
            ]
            
            for node_type in node_types:
                count_result = self.client.execute_query(
                    f"MATCH (n:{node_type}) RETURN count(n) as count"
                )
                node_counts[node_type] = count_result[0]["count"] if count_result else 0

            # Get relationship counts
            relationship_counts = {}
            relationship_types = [
                "CONTAINS", "IMPORTS", "DEPENDS_ON", "INHERITS_FROM",
                "IMPLEMENTS", "CALLS", "DEFINES", "USES", "TESTS",
                "DOCUMENTS", "EXTENDS", "CONFIGURES", "PROVIDES", "REQUIRES"
            ]
            
            for rel_type in relationship_types:
                count_result = self.client.execute_query(
                    f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count"
                )
                relationship_counts[rel_type] = count_result[0]["count"] if count_result else 0

            return {
                "node_counts": node_counts,
                "relationship_counts": relationship_counts,
                "total_nodes": sum(node_counts.values()),
                "total_relationships": sum(relationship_counts.values()),
                "schema_version": "1.0.0",
                "repository_support": True,
            }

        except Exception as e:
            logger.error(f"Failed to get repository schema info: {e}")
            return {}

    def drop_repository_schema(self) -> bool:
        """Drop the repository analysis schema (for testing/reset)."""
        try:
            # Drop all repository-specific nodes
            node_types = [
                "Repository", "Directory", "File", "Package", "Module",
                "Function", "Class", "Dependency", "Agent", "Tool"
            ]
            
            for node_type in node_types:
                self.client.execute_query(f"MATCH (n:{node_type}) DETACH DELETE n")

            logger.info("Repository analysis schema dropped")
            return True

        except Exception as e:
            logger.error(f"Failed to drop repository schema: {e}")
            return False 