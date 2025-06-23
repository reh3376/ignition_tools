"""Neo4j Knowledge Graph Fine-Tuning Pipeline for SME Agent.

This module implements the knowledge graph fine-tuning pipeline following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Error handling and user-friendly messages
4. Progressive complexity support
5. Resource management and cleanup

Extracts structured knowledge from Neo4j nodes, creates fine-tuning datasets,
and implements automated knowledge graph expansion pipeline.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from neo4j import GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from . import SMEAgentValidationError


class KnowledgeExtractionType(Enum):
    """Types of knowledge extraction from Neo4j."""

    FUNCTIONS = "functions"  # System functions and their relationships
    COMPONENTS = "components"  # Ignition components and configurations
    PATTERNS = "patterns"  # Code patterns and best practices
    TROUBLESHOOTING = "troubleshooting"  # Problem-solution relationships
    WORKFLOWS = "workflows"  # Process workflows and procedures
    ALL = "all"  # Extract all types


class DatasetFormat(Enum):
    """Output formats for fine-tuning datasets."""

    JSONL = "jsonl"  # JSON Lines format
    CSV = "csv"  # Comma-separated values
    PARQUET = "parquet"  # Apache Parquet format
    HUGGINGFACE = "huggingface"  # HuggingFace datasets format


@dataclass
class KnowledgeGraphConfig:
    """Configuration for knowledge graph fine-tuning pipeline."""

    # Neo4j connection
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"

    # Extraction configuration
    extraction_types: list[KnowledgeExtractionType] = field(
        default_factory=lambda: [KnowledgeExtractionType.ALL]
    )
    max_nodes_per_query: int = 1000
    include_relationships: bool = True
    include_properties: bool = True

    # Dataset configuration
    output_format: DatasetFormat = DatasetFormat.JSONL
    output_directory: str = "datasets"
    dataset_name: str = "ignition_knowledge"

    # Fine-tuning configuration
    context_window: int = 2048
    min_text_length: int = 50
    max_text_length: int = 4000
    include_code_examples: bool = True

    # Embedding configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    similarity_threshold: float = 0.8

    # Pipeline configuration
    batch_size: int = 100
    enable_caching: bool = True
    cache_directory: str = "cache"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.neo4j_uri or not self.neo4j_user or not self.neo4j_password:
            raise ValueError("Neo4j connection parameters required")

        if self.context_window < 512 or self.context_window > 8192:
            raise ValueError("context_window must be between 512 and 8192")

        if not 0.1 <= self.similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0.1 and 1.0")


@dataclass
class KnowledgeRecord:
    """Individual knowledge record extracted from Neo4j."""

    id: str
    type: str
    title: str
    content: str
    context: str
    relationships: list[dict[str, Any]] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "context": self.context,
            "relationships": self.relationships,
            "properties": self.properties,
            "embedding": self.embedding,
            "metadata": self.metadata,
        }

    def to_training_example(self) -> dict[str, str]:
        """Convert to training example format."""
        return {
            "instruction": f"Explain {self.title} in Ignition development context",
            "input": self.context,
            "output": self.content,
        }


def validate_knowledge_graph_environment() -> dict[str, Any]:
    """Validate knowledge graph pipeline environment following crawl_mcp.py methodology.

    Step 1: Environment validation first - comprehensive validation of all requirements.

    Returns:
        dict containing validation results and component availability.
    """
    validation_result = {
        "validation_score": 0,
        "total_checks": 10,
        "components": {},
        "environment_variables": {},
        "neo4j_connection": {},
        "errors": [],
        "recommendations": [],
    }

    # 1. Check Python packages
    if NEO4J_AVAILABLE:
        validation_result["components"]["neo4j"] = {"available": True}
        validation_result["validation_score"] += 1
    else:
        validation_result["components"]["neo4j"] = {"available": False}
        validation_result["errors"].append("neo4j package not installed")

    if PANDAS_AVAILABLE:
        validation_result["components"]["pandas"] = {"available": True}
        validation_result["validation_score"] += 1
    else:
        validation_result["components"]["pandas"] = {"available": False}
        validation_result["errors"].append("pandas package not installed")

    if SENTENCE_TRANSFORMERS_AVAILABLE:
        validation_result["components"]["sentence_transformers"] = {"available": True}
        validation_result["validation_score"] += 1
    else:
        validation_result["components"]["sentence_transformers"] = {"available": False}
        validation_result["errors"].append(
            "sentence-transformers package not installed"
        )

    # 2. Check environment variables
    env_vars = {
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USER": os.getenv("NEO4J_USER"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
        "NEO4J_DATABASE": os.getenv("NEO4J_DATABASE", "neo4j"),
        "KNOWLEDGE_EXTRACTION_TYPES": os.getenv("KNOWLEDGE_EXTRACTION_TYPES", "all"),
        "KNOWLEDGE_OUTPUT_FORMAT": os.getenv("KNOWLEDGE_OUTPUT_FORMAT", "jsonl"),
        "KNOWLEDGE_CONTEXT_WINDOW": os.getenv("KNOWLEDGE_CONTEXT_WINDOW", "2048"),
        "KNOWLEDGE_EMBEDDING_MODEL": os.getenv(
            "KNOWLEDGE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        ),
    }

    for var, value in env_vars.items():
        validation_result["environment_variables"][var] = {
            "set": value is not None,
            "value": value if value else "not_set",
        }
        if value:
            validation_result["validation_score"] += 0.5

    # 3. Test Neo4j connection
    if (
        NEO4J_AVAILABLE
        and env_vars["NEO4J_URI"]
        and env_vars["NEO4J_USER"]
        and env_vars["NEO4J_PASSWORD"]
    ):
        try:
            driver = GraphDatabase.driver(
                env_vars["NEO4J_URI"],
                auth=(env_vars["NEO4J_USER"], env_vars["NEO4J_PASSWORD"]),
            )
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                if result.single()["test"] == 1:
                    validation_result["neo4j_connection"] = {
                        "available": True,
                        "uri": env_vars["NEO4J_URI"],
                        "database": env_vars["NEO4J_DATABASE"],
                    }
                    validation_result["validation_score"] += 2
            driver.close()
        except Exception as e:
            validation_result["neo4j_connection"] = {
                "available": False,
                "error": str(e),
            }
            validation_result["errors"].append(f"Neo4j connection failed: {e}")
    else:
        validation_result["neo4j_connection"] = {"available": False}
        validation_result["recommendations"].append(
            "Neo4j connection parameters not configured"
        )

    # Calculate final score
    max_score = validation_result["total_checks"]
    actual_score = validation_result["validation_score"]
    validation_result["validation_percentage"] = round(
        (actual_score / max_score) * 100, 1
    )

    return validation_result


class KnowledgeGraphPipeline:
    """Neo4j Knowledge Graph Fine-Tuning Pipeline following crawl_mcp.py methodology.

    Implements systematic approach:
    1. Environment validation first
    2. Comprehensive input validation
    3. Error handling and user-friendly messages
    4. Progressive complexity support
    5. Resource management and cleanup
    """

    def __init__(self, config: KnowledgeGraphConfig | None = None):
        """Initialize knowledge graph pipeline with configuration."""
        self.config = config or KnowledgeGraphConfig()
        self.driver = None
        self.embedding_model = None
        self.validation_result = None

        # Extraction state
        self.extracted_records = []
        self.knowledge_cache = {}

        # Statistics
        self.extraction_stats = {
            "total_nodes": 0,
            "total_relationships": 0,
            "extracted_records": 0,
            "processing_time": 0.0,
        }

    async def initialize(self) -> dict[str, Any]:
        """Initialize knowledge graph pipeline following crawl_mcp.py methodology.

        Step 1: Environment validation first
        Step 2: Component initialization
        Step 3: Resource management setup
        """
        # Step 1: Environment validation first
        self.validation_result = validate_knowledge_graph_environment()

        if self.validation_result["validation_percentage"] < 70:
            raise SMEAgentValidationError(
                f"Knowledge graph pipeline validation failed: {self.validation_result['validation_percentage']}% "
                f"Errors: {', '.join(self.validation_result['errors'])}"
            )

        # Step 2: Component initialization
        init_result = {
            "status": "success",
            "components_initialized": [],
            "warnings": [],
        }

        try:
            # Initialize Neo4j connection
            if NEO4J_AVAILABLE:
                self.driver = GraphDatabase.driver(
                    self.config.neo4j_uri,
                    auth=(self.config.neo4j_user, self.config.neo4j_password),
                )
                init_result["components_initialized"].append("neo4j_driver")

            # Initialize embedding model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer(self.config.embedding_model)
                init_result["components_initialized"].append("embedding_model")

            # Create output directories
            self._create_directories()
            init_result["components_initialized"].append("directories")

            return init_result

        except Exception as e:
            raise SMEAgentValidationError(
                f"Knowledge graph pipeline initialization failed: {e}"
            )

    def _create_directories(self):
        """Create necessary directories."""
        Path(self.config.output_directory).mkdir(parents=True, exist_ok=True)
        if self.config.enable_caching:
            Path(self.config.cache_directory).mkdir(parents=True, exist_ok=True)

    async def extract_knowledge(
        self,
        extraction_types: list[KnowledgeExtractionType] | None = None,
        max_records: int | None = None,
    ) -> list[KnowledgeRecord]:
        """Extract knowledge from Neo4j following crawl_mcp.py methodology.

        Step 2: Comprehensive input validation
        Step 3: Error handling and user-friendly messages
        """
        # Step 2: Comprehensive input validation
        if not self.driver:
            raise SMEAgentValidationError("Neo4j driver not initialized")

        extraction_types = extraction_types or self.config.extraction_types
        if not extraction_types:
            raise ValueError("extraction_types cannot be empty")

        if max_records is not None and max_records <= 0:
            raise ValueError("max_records must be positive")

        try:
            start_time = datetime.now()
            self.extracted_records = []

            # Extract knowledge by type
            for extraction_type in extraction_types:
                if extraction_type == KnowledgeExtractionType.ALL:
                    # Extract all types
                    for single_type in [
                        KnowledgeExtractionType.FUNCTIONS,
                        KnowledgeExtractionType.COMPONENTS,
                        KnowledgeExtractionType.PATTERNS,
                        KnowledgeExtractionType.TROUBLESHOOTING,
                        KnowledgeExtractionType.WORKFLOWS,
                    ]:
                        records = await self._extract_by_type(single_type, max_records)
                        self.extracted_records.extend(records)
                else:
                    records = await self._extract_by_type(extraction_type, max_records)
                    self.extracted_records.extend(records)

            # Generate embeddings if model available
            if self.embedding_model:
                await self._generate_embeddings()

            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.extraction_stats.update(
                {
                    "extracted_records": len(self.extracted_records),
                    "processing_time": processing_time,
                }
            )

            return self.extracted_records

        except Exception as e:
            # Step 3: Error handling and user-friendly messages
            error_msg = self._format_extraction_error(e)
            raise SMEAgentValidationError(f"Knowledge extraction failed: {error_msg}")

    async def _extract_by_type(
        self, extraction_type: KnowledgeExtractionType, max_records: int | None
    ) -> list[KnowledgeRecord]:
        """Extract knowledge records by type."""
        queries = self._get_extraction_queries(extraction_type)
        records = []

        with self.driver.session() as session:
            for query_name, query in queries.items():
                try:
                    # Add limit if specified
                    if max_records:
                        query += f" LIMIT {max_records}"

                    result = session.run(query)

                    for record in result:
                        knowledge_record = self._create_knowledge_record(
                            record, extraction_type, query_name
                        )
                        records.append(knowledge_record)

                except Exception as e:
                    print(f"Warning: Query {query_name} failed: {e}")
                    continue

        return records

    def _get_extraction_queries(
        self, extraction_type: KnowledgeExtractionType
    ) -> dict[str, str]:
        """Get Neo4j queries for different extraction types."""
        queries = {}

        if extraction_type == KnowledgeExtractionType.FUNCTIONS:
            queries[
                "system_functions"
            ] = """
            MATCH (f:Function)
            OPTIONAL MATCH (f)-[r]-(related)
            RETURN f, collect(distinct {type: type(r), node: related}) as relationships
            """

        elif extraction_type == KnowledgeExtractionType.COMPONENTS:
            queries[
                "ignition_components"
            ] = """
            MATCH (c:Component)
            OPTIONAL MATCH (c)-[r]-(related)
            RETURN c, collect(distinct {type: type(r), node: related}) as relationships
            """

        elif extraction_type == KnowledgeExtractionType.PATTERNS:
            queries[
                "code_patterns"
            ] = """
            MATCH (p:Pattern)
            OPTIONAL MATCH (p)-[r]-(related)
            RETURN p, collect(distinct {type: type(r), node: related}) as relationships
            """

        elif extraction_type == KnowledgeExtractionType.TROUBLESHOOTING:
            queries[
                "troubleshooting"
            ] = """
            MATCH (t:Troubleshooting)
            OPTIONAL MATCH (t)-[r]-(related)
            RETURN t, collect(distinct {type: type(r), node: related}) as relationships
            """

        elif extraction_type == KnowledgeExtractionType.WORKFLOWS:
            queries[
                "workflows"
            ] = """
            MATCH (w:Workflow)
            OPTIONAL MATCH (w)-[r]-(related)
            RETURN w, collect(distinct {type: type(r), node: related}) as relationships
            """

        # Fallback to general node extraction
        if not queries:
            queries[
                "general_nodes"
            ] = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]-(related)
            RETURN n, collect(distinct {type: type(r), node: related}) as relationships
            """

        return queries

    def _create_knowledge_record(
        self,
        neo4j_record: Any,
        extraction_type: KnowledgeExtractionType,
        query_name: str,
    ) -> KnowledgeRecord:
        """Create knowledge record from Neo4j result."""
        node = (
            neo4j_record["n"]
            if "n" in neo4j_record
            else neo4j_record[list(neo4j_record.keys())[0]]
        )
        relationships = neo4j_record.get("relationships", [])

        # Extract node properties
        properties = dict(node)
        node_id = str(node.id)
        node_type = list(node.labels)[0] if node.labels else "Unknown"

        # Generate title and content
        title = properties.get(
            "name", properties.get("title", f"{node_type}_{node_id}")
        )
        content = self._generate_content_from_node(node, relationships)
        context = self._generate_context_from_relationships(relationships)

        return KnowledgeRecord(
            id=node_id,
            type=extraction_type.value,
            title=title,
            content=content,
            context=context,
            relationships=[self._format_relationship(r) for r in relationships],
            properties=properties,
            metadata={
                "query_name": query_name,
                "node_labels": list(node.labels),
                "extracted_at": datetime.now().isoformat(),
            },
        )

    def _generate_content_from_node(self, node: Any, relationships: list[Any]) -> str:
        """Generate descriptive content from node and relationships."""
        properties = dict(node)
        labels = list(node.labels)

        content_parts = []

        # Add description from properties
        if "description" in properties:
            content_parts.append(properties["description"])
        elif "summary" in properties:
            content_parts.append(properties["summary"])

        # Add type information
        if labels:
            content_parts.append(
                f"This is a {', '.join(labels)} in the Ignition system."
            )

        # Add key properties
        key_props = ["function", "purpose", "usage", "parameters", "returns"]
        for prop in key_props:
            if properties.get(prop):
                content_parts.append(f"{prop.capitalize()}: {properties[prop]}")

        # Add relationship context
        if relationships:
            rel_summary = self._summarize_relationships(relationships)
            if rel_summary:
                content_parts.append(f"Related to: {rel_summary}")

        return (
            " ".join(content_parts)
            if content_parts
            else f"Node of type {', '.join(labels) if labels else 'Unknown'}"
        )

    def _generate_context_from_relationships(self, relationships: list[Any]) -> str:
        """Generate context information from relationships."""
        if not relationships:
            return "No specific context available."

        context_parts = []

        # Group relationships by type
        rel_groups = {}
        for rel in relationships:
            rel_type = rel.get("type", "UNKNOWN")
            if rel_type not in rel_groups:
                rel_groups[rel_type] = []
            rel_groups[rel_type].append(rel)

        # Describe relationship groups
        for rel_type, rels in rel_groups.items():
            if len(rels) == 1:
                context_parts.append(f"Has {rel_type.lower()} relationship")
            else:
                context_parts.append(
                    f"Has {len(rels)} {rel_type.lower()} relationships"
                )

        return (
            "Context: " + ", ".join(context_parts)
            if context_parts
            else "No specific context available."
        )

    def _summarize_relationships(self, relationships: list[Any]) -> str:
        """Create a summary of relationships."""
        if not relationships:
            return ""

        rel_types = set()
        for rel in relationships:
            if "type" in rel:
                rel_types.add(rel["type"])

        if len(rel_types) <= 3:
            return ", ".join(rel_types)
        else:
            return f"{len(rel_types)} different relationship types"

    def _format_relationship(self, relationship: Any) -> dict[str, Any]:
        """Format relationship for storage."""
        return {
            "type": relationship.get("type", "UNKNOWN"),
            "node_id": (
                str(relationship.get("node", {}).get("id", "unknown"))
                if relationship.get("node")
                else "unknown"
            ),
            "properties": (
                dict(relationship.get("node", {})) if relationship.get("node") else {}
            ),
        }

    async def _generate_embeddings(self):
        """Generate embeddings for extracted records."""
        if not self.embedding_model:
            return

        texts = [
            f"{record.title} {record.content}" for record in self.extracted_records
        ]

        # Generate embeddings in batches
        batch_size = self.config.batch_size
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_embeddings = self.embedding_model.encode(batch_texts)

            for j, embedding in enumerate(batch_embeddings):
                record_idx = i + j
                if record_idx < len(self.extracted_records):
                    self.extracted_records[record_idx].embedding = embedding.tolist()

    def _format_extraction_error(self, error: Exception) -> str:
        """Format extraction errors for user-friendly messages."""
        error_str = str(error).lower()

        if "connection" in error_str or "refused" in error_str:
            return "Neo4j connection failed. Check if Neo4j is running and connection parameters are correct."
        elif "authentication" in error_str or "unauthorized" in error_str:
            return "Neo4j authentication failed. Check username and password."
        elif "database" in error_str:
            return "Neo4j database error. Check if database exists and is accessible."
        elif "timeout" in error_str:
            return "Query timeout. Try reducing batch size or adding query limits."
        else:
            return str(error)

    async def create_fine_tuning_dataset(
        self, output_path: str | None = None, format_type: DatasetFormat | None = None
    ) -> str:
        """Create fine-tuning dataset from extracted knowledge."""
        if not self.extracted_records:
            raise SMEAgentValidationError(
                "No knowledge records available. Run extract_knowledge first."
            )

        output_path = output_path or os.path.join(
            self.config.output_directory,
            f"{self.config.dataset_name}.{(format_type or self.config.output_format).value}",
        )

        format_type = format_type or self.config.output_format

        # Convert records to training examples
        training_examples = []
        for record in self.extracted_records:
            example = record.to_training_example()
            training_examples.append(example)

        # Save in specified format
        if format_type == DatasetFormat.JSONL:
            self._save_as_jsonl(training_examples, output_path)
        elif format_type == DatasetFormat.CSV and PANDAS_AVAILABLE:
            self._save_as_csv(training_examples, output_path)
        elif format_type == DatasetFormat.PARQUET and PANDAS_AVAILABLE:
            self._save_as_parquet(training_examples, output_path)
        else:
            # Fallback to JSONL
            self._save_as_jsonl(training_examples, output_path)

        return output_path

    def _save_as_jsonl(self, examples: list[dict[str, str]], output_path: str):
        """Save examples as JSONL format."""
        with open(output_path, "w", encoding="utf-8") as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")

    def _save_as_csv(self, examples: list[dict[str, str]], output_path: str):
        """Save examples as CSV format."""
        df = pd.DataFrame(examples)
        df.to_csv(output_path, index=False, encoding="utf-8")

    def _save_as_parquet(self, examples: list[dict[str, str]], output_path: str):
        """Save examples as Parquet format."""
        df = pd.DataFrame(examples)
        df.to_parquet(output_path, index=False)

    def get_pipeline_stats(self) -> dict[str, Any]:
        """Get comprehensive pipeline statistics."""
        return {
            "extraction_stats": self.extraction_stats,
            "records_by_type": self._get_records_by_type(),
            "validation": self.validation_result,
            "config": {
                "extraction_types": [t.value for t in self.config.extraction_types],
                "output_format": self.config.output_format.value,
                "context_window": self.config.context_window,
            },
        }

    def _get_records_by_type(self) -> dict[str, int]:
        """Get count of records by type."""
        type_counts = {}
        for record in self.extracted_records:
            type_counts[record.type] = type_counts.get(record.type, 0) + 1
        return type_counts

    async def cleanup(self):
        """Cleanup resources following crawl_mcp.py methodology."""
        try:
            if self.driver:
                self.driver.close()
                self.driver = None

            # Clear memory
            self.extracted_records = []
            self.knowledge_cache = {}

        except Exception as e:
            print(f"Warning: Error during knowledge graph pipeline cleanup: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


# Convenience functions for easy usage
async def create_knowledge_dataset(
    extraction_types: list[str] | None = None,
    output_format: str = "jsonl",
    max_records: int | None = None,
    **kwargs,
) -> str:
    """Create knowledge dataset with simplified interface.

    Args:
        extraction_types: list of extraction types (functions, components, patterns, etc.)
        output_format: Output format (jsonl, csv, parquet)
        max_records: Maximum number of records to extract
        **kwargs: Additional configuration options

    Returns:
        Path to created dataset file
    """
    # Map string inputs to enums
    type_map = {
        "functions": KnowledgeExtractionType.FUNCTIONS,
        "components": KnowledgeExtractionType.COMPONENTS,
        "patterns": KnowledgeExtractionType.PATTERNS,
        "troubleshooting": KnowledgeExtractionType.TROUBLESHOOTING,
        "workflows": KnowledgeExtractionType.WORKFLOWS,
        "all": KnowledgeExtractionType.ALL,
    }

    format_map = {
        "jsonl": DatasetFormat.JSONL,
        "csv": DatasetFormat.CSV,
        "parquet": DatasetFormat.PARQUET,
        "huggingface": DatasetFormat.HUGGINGFACE,
    }

    # Convert extraction types
    if extraction_types:
        extraction_enum_types = [
            type_map.get(t, KnowledgeExtractionType.ALL) for t in extraction_types
        ]
    else:
        extraction_enum_types = [KnowledgeExtractionType.ALL]

    config = KnowledgeGraphConfig(
        extraction_types=extraction_enum_types,
        output_format=format_map.get(output_format, DatasetFormat.JSONL),
        **kwargs,
    )

    async with KnowledgeGraphPipeline(config) as pipeline:
        await pipeline.extract_knowledge(max_records=max_records)
        return await pipeline.create_fine_tuning_dataset()


def get_extraction_info() -> dict[str, Any]:
    """Get information about available extraction types and formats."""
    return {
        "extraction_types": {
            "functions": "System functions and their relationships",
            "components": "Ignition components and configurations",
            "patterns": "Code patterns and best practices",
            "troubleshooting": "Problem-solution relationships",
            "workflows": "Process workflows and procedures",
            "all": "Extract all available types",
        },
        "output_formats": {
            "jsonl": "JSON Lines format (recommended for training)",
            "csv": "Comma-separated values",
            "parquet": "Apache Parquet format",
            "huggingface": "HuggingFace datasets format",
        },
        "requirements": {
            "neo4j": "Neo4j database with knowledge graph",
            "pandas": "For CSV and Parquet output formats",
            "sentence_transformers": "For embedding generation",
        },
    }
