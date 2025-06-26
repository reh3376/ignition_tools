"""Neo4j Knowledge Graph Extensions for Web Intelligence.

This module extends the existing Neo4j knowledge graph with web intelligence
capabilities following Phase 11.8 requirements and crawl_mcp.py methodology.

New Node Types:
- WebSource: Represents crawled web sources
- DocumentChunk: Content chunks from crawled documents
- CodeExample: Code examples found in documentation
- ValidationRule: Rules derived from documentation

New Relationships:
- CRAWLED_FROM: WebSource -> DocumentChunk
- PROVIDES_EXAMPLE: DocumentChunk -> CodeExample
- VALIDATES_AGAINST: CodeExample -> Function
- DERIVED_FROM: ValidationRule -> DocumentChunk
"""

import os
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field

try:
    from neo4j import GraphDatabase
    from neo4j import exceptions as neo4j_exceptions

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class WebSourceNode(BaseModel):
    """Model for WebSource nodes."""

    url: str = Field(..., description="Source URL")
    domain: str = Field(..., description="Domain name")
    last_crawled: str = Field(..., description="Last crawl timestamp")
    content_type: str = Field(default="html", description="Content type")
    status: str = Field(default="active", description="Source status")
    crawl_frequency: str = Field(default="daily", description="How often to crawl")


class DocumentChunkNode(BaseModel):
    """Model for DocumentChunk nodes."""

    content: str = Field(..., description="Chunk content")
    chunk_index: int = Field(..., description="Index within document")
    source_url: str = Field(..., description="Source URL")
    embedding_hash: str | None = Field(default=None, description="Hash of embedding vector")
    chunk_type: str = Field(default="text", description="Type of chunk: text, code, example")
    language: str | None = Field(default=None, description="Programming language if code")


class CodeExampleNode(BaseModel):
    """Model for CodeExample nodes."""

    code: str = Field(..., description="Code content")
    language: str = Field(..., description="Programming language")
    context: str = Field(..., description="Context or description")
    validation_status: str = Field(default="unvalidated", description="Validation status")
    complexity_score: float | None = Field(default=None, description="Complexity score")
    ignition_specific: bool = Field(default=False, description="Whether Ignition-specific")


class ValidationRuleNode(BaseModel):
    """Model for ValidationRule nodes."""

    rule_type: str = Field(..., description="Type of validation rule")
    rule_content: str = Field(..., description="Rule content/description")
    confidence: float = Field(..., description="Confidence score")
    source_documentation: str = Field(..., description="Source documentation URL")
    applies_to: list[str] = Field(default_factory=list, description="What the rule applies to")


def validate_neo4j_environment() -> dict[str, Any]:
    """Validate Neo4j environment for web intelligence extensions."""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "neo4j_available": False,
        "connection_working": False,
    }

    try:
        if not NEO4J_AVAILABLE:
            validation_result["valid"] = False
            validation_result["errors"].append("Neo4j driver not available. Install with: pip install neo4j")
            return validation_result

        validation_result["neo4j_available"] = True

        # Check environment variables
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")

        if not neo4j_uri or not neo4j_user or not neo4j_password:
            validation_result["valid"] = False
            validation_result["errors"].append(
                "Neo4j credentials not configured. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD"
            )
            return validation_result

        # Test connection
        try:
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            validation_result["connection_working"] = True
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Neo4j connection failed: {e}")
            return validation_result

    except Exception as e:
        validation_result["valid"] = False
        validation_result["errors"].append(f"Environment validation failed: {e}")

    return validation_result


def format_neo4j_error(error: Exception) -> str:
    """Format Neo4j errors for user-friendly messages following crawl_mcp.py patterns."""
    error_str = str(error).lower()

    if "authentication" in error_str or "unauthorized" in error_str:
        return "Neo4j authentication failed. Check NEO4J_USER and NEO4J_PASSWORD."
    elif "connection" in error_str or "refused" in error_str:
        return "Cannot connect to Neo4j. Check NEO4J_URI and ensure Neo4j is running."
    elif "constraint" in error_str:
        return f"Neo4j constraint violation: {error!s}"
    elif "syntax" in error_str:
        return f"Cypher syntax error: {error!s}"
    else:
        return f"Neo4j error: {error!s}"


class WebIntelligenceGraphManager:
    """Manager for web intelligence knowledge graph extensions."""

    def __init__(self) -> None:
        """Initialize the graph manager."""
        self.driver = None
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize Neo4j connection and create schema."""
        try:
            # Validate environment
            env_validation = validate_neo4j_environment()
            if not env_validation["valid"]:
                print(f"Environment validation failed: {env_validation['errors']}")
                return False

            # Connect to Neo4j
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_user = os.getenv("NEO4J_USER")
            neo4j_password = os.getenv("NEO4J_PASSWORD")

            if neo4j_uri and neo4j_user and neo4j_password:
                self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

                # Create schema
                await self._create_web_intelligence_schema()

                self.initialized = True
                print("✓ Web intelligence graph extensions initialized")
                return True
            else:
                print("❌ Neo4j credentials not available")
                return False

        except Exception as e:
            print(f"Initialization failed: {format_neo4j_error(e)}")
            return False

    async def _create_web_intelligence_schema(self) -> None:
        """Create web intelligence schema in Neo4j."""
        schema_queries = [
            # Create constraints for unique identification
            "CREATE CONSTRAINT web_source_url IF NOT EXISTS FOR (ws:WebSource) REQUIRE ws.url IS UNIQUE",
            "CREATE CONSTRAINT document_chunk_id IF NOT EXISTS FOR (dc:DocumentChunk) REQUIRE dc.chunk_id IS UNIQUE",
            "CREATE CONSTRAINT code_example_id IF NOT EXISTS FOR (ce:CodeExample) REQUIRE ce.example_id IS UNIQUE",
            "CREATE CONSTRAINT validation_rule_id IF NOT EXISTS FOR (vr:ValidationRule) REQUIRE vr.rule_id IS UNIQUE",
            # Create indexes for performance
            "CREATE INDEX web_source_domain IF NOT EXISTS FOR (ws:WebSource) ON ws.domain",
            "CREATE INDEX document_chunk_source IF NOT EXISTS FOR (dc:DocumentChunk) ON dc.source_url",
            "CREATE INDEX code_example_language IF NOT EXISTS FOR (ce:CodeExample) ON ce.language",
            "CREATE INDEX validation_rule_type IF NOT EXISTS FOR (vr:ValidationRule) ON vr.rule_type",
        ]

        try:
            with self.driver.session() as session:
                for query in schema_queries:
                    try:
                        session.run(query)
                    except neo4j_exceptions.ClientError as e:
                        # Ignore constraint already exists errors
                        if "already exists" not in str(e).lower():
                            raise

            print("✓ Web intelligence schema created")

        except Exception as e:
            print(f"Schema creation failed: {format_neo4j_error(e)}")
            raise

    async def add_web_source(self, web_source: WebSourceNode) -> bool:
        """Add or update a web source node."""
        try:
            with self.driver.session() as session:
                query = """
                MERGE (ws:WebSource {url: $url})
                SET ws.domain = $domain,
                    ws.last_crawled = $last_crawled,
                    ws.content_type = $content_type,
                    ws.status = $status,
                    ws.crawl_frequency = $crawl_frequency,
                    ws.updated_at = datetime()
                RETURN ws
                """

                result = session.run(query, **web_source.dict())
                return result.single() is not None

        except Exception as e:
            print(f"Failed to add web source: {format_neo4j_error(e)}")
            return False

    async def add_document_chunk(self, document_chunk: DocumentChunkNode, source_url: str) -> str | None:
        """Add a document chunk and link it to its web source."""
        try:
            with self.driver.session() as session:
                # Generate unique chunk ID
                chunk_id = f"{source_url}#{document_chunk.chunk_index}"

                query = """
                MATCH (ws:WebSource {url: $source_url})
                CREATE (dc:DocumentChunk {
                    chunk_id: $chunk_id,
                    content: $content,
                    chunk_index: $chunk_index,
                    source_url: $source_url,
                    embedding_hash: $embedding_hash,
                    chunk_type: $chunk_type,
                    language: $language,
                    created_at: datetime()
                })
                CREATE (ws)-[:CONTAINS]->(dc)
                RETURN dc.chunk_id as chunk_id
                """

                params = document_chunk.dict()
                params["chunk_id"] = chunk_id
                params["source_url"] = source_url

                result = session.run(query, **params)
                record = result.single()
                return record["chunk_id"] if record else None

        except Exception as e:
            print(f"Failed to add document chunk: {format_neo4j_error(e)}")
            return None

    async def add_code_example(self, code_example: CodeExampleNode, chunk_id: str) -> str | None:
        """Add a code example and link it to its document chunk."""
        try:
            with self.driver.session() as session:
                # Generate unique example ID
                example_id = f"{chunk_id}#{hash(code_example.code) % 10000}"

                query = """
                MATCH (dc:DocumentChunk {chunk_id: $chunk_id})
                CREATE (ce:CodeExample {
                    example_id: $example_id,
                    code: $code,
                    language: $language,
                    context: $context,
                    validation_status: $validation_status,
                    complexity_score: $complexity_score,
                    ignition_specific: $ignition_specific,
                    created_at: datetime()
                })
                CREATE (dc)-[:PROVIDES_EXAMPLE]->(ce)
                RETURN ce.example_id as example_id
                """

                params = code_example.dict()
                params["example_id"] = example_id
                params["chunk_id"] = chunk_id

                result = session.run(query, **params)
                record = result.single()
                return record["example_id"] if record else None

        except Exception as e:
            print(f"Failed to add code example: {format_neo4j_error(e)}")
            return None

    async def add_validation_rule(self, validation_rule: ValidationRuleNode, chunk_id: str) -> str | None:
        """Add a validation rule derived from documentation."""
        try:
            with self.driver.session() as session:
                # Generate unique rule ID
                rule_id = f"rule_{hash(validation_rule.rule_content) % 10000}"

                query = """
                MATCH (dc:DocumentChunk {chunk_id: $chunk_id})
                CREATE (vr:ValidationRule {
                    rule_id: $rule_id,
                    rule_type: $rule_type,
                    rule_content: $rule_content,
                    confidence: $confidence,
                    source_documentation: $source_documentation,
                    applies_to: $applies_to,
                    created_at: datetime()
                })
                CREATE (vr)-[:DERIVED_FROM]->(dc)
                RETURN vr.rule_id as rule_id
                """

                params = validation_rule.dict()
                params["rule_id"] = rule_id
                params["chunk_id"] = chunk_id

                result = session.run(query, **params)
                record = result.single()
                return record["rule_id"] if record else None

        except Exception as e:
            print(f"Failed to add validation rule: {format_neo4j_error(e)}")
            return None

    async def link_example_to_function(self, example_id: str, function_name: str) -> bool:
        """Create relationship between code example and function."""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (ce:CodeExample {example_id: $example_id})
                MATCH (f:Function {name: $function_name})
                MERGE (ce)-[:VALIDATES_AGAINST]->(f)
                RETURN ce, f
                """

                result = session.run(query, example_id=example_id, function_name=function_name)
                return result.single() is not None

        except Exception as e:
            print(f"Failed to link example to function: {format_neo4j_error(e)}")
            return False

    async def find_examples_for_pattern(self, pattern: str, limit: int = 5) -> list[dict[str, Any]]:
        """Find code examples matching a pattern."""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (ce:CodeExample)
                WHERE ce.code CONTAINS $pattern
                   OR ce.context CONTAINS $pattern
                OPTIONAL MATCH (dc:DocumentChunk)-[:PROVIDES_EXAMPLE]->(ce)
                OPTIONAL MATCH (ws:WebSource)-[:CONTAINS]->(dc)
                RETURN ce.code as code,
                       ce.language as language,
                       ce.context as context,
                       ce.ignition_specific as ignition_specific,
                       ws.url as source_url,
                       ws.domain as domain
                ORDER BY ce.ignition_specific DESC, ce.created_at DESC
                LIMIT $limit
                """

                result = session.run(query, pattern=pattern, limit=limit)

                examples = []
                for record in result:
                    examples.append(
                        {
                            "code": record["code"],
                            "language": record["language"],
                            "context": record["context"],
                            "ignition_specific": record["ignition_specific"],
                            "source_url": record["source_url"],
                            "domain": record["domain"],
                        }
                    )

                return examples

        except Exception as e:
            print(f"Failed to find examples: {format_neo4j_error(e)}")
            return []

    async def get_validation_rules_for_function(self, function_name: str) -> list[dict[str, Any]]:
        """Get validation rules that apply to a specific function."""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (vr:ValidationRule)
                WHERE $function_name IN vr.applies_to
                OPTIONAL MATCH (vr)-[:DERIVED_FROM]->(dc:DocumentChunk)
                OPTIONAL MATCH (ws:WebSource)-[:CONTAINS]->(dc)
                RETURN vr.rule_type as rule_type,
                       vr.rule_content as rule_content,
                       vr.confidence as confidence,
                       ws.url as source_url
                ORDER BY vr.confidence DESC
                """

                result = session.run(query, function_name=function_name)

                rules = []
                for record in result:
                    rules.append(
                        {
                            "rule_type": record["rule_type"],
                            "rule_content": record["rule_content"],
                            "confidence": record["confidence"],
                            "source_url": record["source_url"],
                        }
                    )

                return rules

        except Exception as e:
            print(f"Failed to get validation rules: {format_neo4j_error(e)}")
            return []

    async def get_web_intelligence_stats(self) -> dict[str, Any]:
        """Get statistics about web intelligence data."""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (ws:WebSource)
                OPTIONAL MATCH (ws)-[:CONTAINS]->(dc:DocumentChunk)
                OPTIONAL MATCH (dc)-[:PROVIDES_EXAMPLE]->(ce:CodeExample)
                OPTIONAL MATCH (vr:ValidationRule)-[:DERIVED_FROM]->(dc)
                RETURN COUNT(DISTINCT ws) as web_sources,
                       COUNT(DISTINCT dc) as document_chunks,
                       COUNT(DISTINCT ce) as code_examples,
                       COUNT(DISTINCT vr) as validation_rules
                """

                result = session.run(query)
                record = result.single()

                if record:
                    return {
                        "web_sources": record["web_sources"],
                        "document_chunks": record["document_chunks"],
                        "code_examples": record["code_examples"],
                        "validation_rules": record["validation_rules"],
                    }
                else:
                    return {
                        "web_sources": 0,
                        "document_chunks": 0,
                        "code_examples": 0,
                        "validation_rules": 0,
                    }

        except Exception as e:
            print(f"Failed to get stats: {format_neo4j_error(e)}")
            return {}

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.driver:
            self.driver.close()
            self.driver = None
            self.initialized = False


# Utility functions for working with crawled content


def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return "unknown"


def create_web_source_from_crawl(url: str, content_type: str = "html") -> WebSourceNode:
    """Create a WebSource node from crawl information."""
    return WebSourceNode(
        url=url,
        domain=extract_domain_from_url(url),
        last_crawled=datetime.utcnow().isoformat(),
        content_type=content_type,
    )


def create_document_chunk_from_content(
    content: str,
    chunk_index: int,
    source_url: str,
    chunk_type: str = "text",
    language: str | None = None,
) -> DocumentChunkNode:
    """Create a DocumentChunk node from content."""
    return DocumentChunkNode(
        content=content,
        chunk_index=chunk_index,
        source_url=source_url,
        chunk_type=chunk_type,
        language=language,
    )


def create_code_example_from_chunk(
    code: str, language: str, context: str, ignition_specific: bool = False
) -> CodeExampleNode:
    """Create a CodeExample node from code content."""
    return CodeExampleNode(
        code=code,
        language=language,
        context=context,
        ignition_specific=ignition_specific,
    )


def create_validation_rule_from_documentation(
    rule_type: str,
    rule_content: str,
    confidence: float,
    source_url: str,
    applies_to: list[str] | None = None,
) -> ValidationRuleNode:
    """Create a ValidationRule node from documentation content."""
    return ValidationRuleNode(
        rule_type=rule_type,
        rule_content=rule_content,
        confidence=confidence,
        source_documentation=source_url,
        applies_to=applies_to or [],
    )


__all__ = [
    "CodeExampleNode",
    "DocumentChunkNode",
    "ValidationRuleNode",
    "WebIntelligenceGraphManager",
    "WebSourceNode",
    "create_code_example_from_chunk",
    "create_document_chunk_from_content",
    "create_validation_rule_from_documentation",
    "create_web_source_from_crawl",
    "format_neo4j_error",
    "validate_neo4j_environment",
]
