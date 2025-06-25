"""Neo4j Schema Definitions for Code Intelligence System."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Self

logger = logging.getLogger(__name__)


@dataclass
class CodeFileNode:
    """Represents a code file in the graph database."""

    path: str
    lines: int
    complexity: float
    maintainability_index: float
    last_modified: datetime
    content_hash: str
    language: str = "python"
    size_bytes: int = 0
    embedding: list[float] | None = None


@dataclass
class ClassNode:
    """Represents a class in the graph database."""

    name: str
    file_path: str
    start_line: int
    end_line: int
    methods_count: int
    complexity: float
    docstring: str | None = None
    inheritance: list[str] | None = None
    embedding: list[float] | None = None


@dataclass
class MethodNode:
    """Represents a method/function in the graph database."""

    name: str
    class_name: str | None
    file_path: str
    start_line: int
    end_line: int
    parameters: list[str]
    complexity: float
    return_type: str | None = None
    docstring: str | None = None
    is_async: bool = False
    embedding: list[float] | None = None


@dataclass
class ImportNode:
    """Represents an import statement in the graph database."""

    module: str
    alias: str | None
    from_module: str | None
    file_path: str
    line_number: int
    is_local: bool = False


class CodeSchema:
    """Manages Neo4j schema for code intelligence."""

    def __init__(self: Self, graph_client: Any) -> None:
        """Initialize with graph client."""
        self.client = graph_client

    def create_schema(self: Self) -> bool:
        """Create the complete schema for code intelligence."""
        try:
            # Create constraints
            self._create_constraints()

            # Create indexes
            self._create_indexes()

            # Create vector indexes
            self._create_vector_indexes()

            logger.info("Code intelligence schema created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False

    def _create_constraints(self: Self) -> None:
        """Create uniqueness constraints."""
        constraints = [
            "CREATE CONSTRAINT code_file_path IF NOT EXISTS FOR (f:CodeFile) REQUIRE f.path IS UNIQUE",
            "CREATE CONSTRAINT class_unique IF NOT EXISTS FOR (c:Class) REQUIRE (c.name, c.file_path) IS UNIQUE",
            "CREATE CONSTRAINT method_unique IF NOT EXISTS FOR (m:Method) REQUIRE (m.name, m.file_path, m.start_line) IS UNIQUE",
            "CREATE CONSTRAINT import_unique IF NOT EXISTS FOR (i:Import) REQUIRE (i.module, i.file_path, i.line_number) IS UNIQUE",
        ]

        for constraint in constraints:
            try:
                self.client.execute_query(constraint)
                logger.debug(f"Created constraint: {constraint}")
            except Exception as e:
                logger.debug(f"Constraint may already exist: {e}")

    def _create_indexes(self: Self) -> None:
        """Create performance indexes."""
        indexes = [
            "CREATE INDEX code_file_modified IF NOT EXISTS FOR (f:CodeFile) ON (f.last_modified)",
            "CREATE INDEX code_file_complexity IF NOT EXISTS FOR (f:CodeFile) ON (f.complexity)",
            "CREATE INDEX class_complexity IF NOT EXISTS FOR (c:Class) ON (c.complexity)",
            "CREATE INDEX method_complexity IF NOT EXISTS FOR (m:Method) ON (m.complexity)",
            "CREATE INDEX import_module IF NOT EXISTS FOR (i:Import) ON (i.module)",
        ]

        for index in indexes:
            try:
                self.client.execute_query(index)
                logger.debug(f"Created index: {index}")
            except Exception as e:
                logger.debug(f"Index may already exist: {e}")

    def _create_vector_indexes(self: Self) -> None:
        """Create vector indexes for embeddings."""
        vector_indexes = [
            {
                "name": "code_file_embeddings",
                "query": "CREATE VECTOR INDEX code_file_embeddings IF NOT EXISTS FOR (f:CodeFile) ON (f.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "class_embeddings",
                "query": "CREATE VECTOR INDEX class_embeddings IF NOT EXISTS FOR (c:Class) ON (c.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
            {
                "name": "method_embeddings",
                "query": "CREATE VECTOR INDEX method_embeddings IF NOT EXISTS FOR (m:Method) ON (m.embedding) OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}",
            },
        ]

        for index_info in vector_indexes:
            try:
                self.client.execute_query(index_info["query"])
                logger.info(f"Created vector index: {index_info['name']}")
            except Exception as e:
                logger.debug(
                    f"Vector index {index_info['name']} may already exist: {e}"
                )

    def get_schema_info(self: Self) -> dict[str, Any]:
        """Get information about the current schema."""
        try:
            # Get constraints
            constraints_result = self.client.execute_query("SHOW CONSTRAINTS")
            constraints = [r["name"] for r in constraints_result]

            # Get indexes
            indexes_result = self.client.execute_query("SHOW INDEXES")
            indexes = [r["name"] for r in indexes_result]

            # Get node counts
            node_counts = {}
            for node_type in ["CodeFile", "Class", "Method", "Import"]:
                count_result = self.client.execute_query(
                    f"MATCH (n:{node_type}) RETURN count(n) as count"
                )
                node_counts[node_type] = count_result[0]["count"] if count_result else 0

            return {
                "constraints": constraints,
                "indexes": indexes,
                "node_counts": node_counts,
                "schema_version": "1.0.0",
            }

        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            return {}

    def drop_schema(self: Self) -> bool:
        """Drop the code intelligence schema (for testing/reset)."""
        try:
            # Drop all code intelligence nodes
            node_types = ["CodeFile", "Class", "Method", "Import"]
            for node_type in node_types:
                self.client.execute_query(f"MATCH (n:{node_type}) DETACH DELETE n")

            logger.info("Code intelligence schema dropped")
            return True

        except Exception as e:
            logger.error(f"Failed to drop schema: {e}")
            return False
