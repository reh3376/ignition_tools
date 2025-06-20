"""Vector Embeddings System for Code Intelligence.

This module implements Phase 8.2 of the roadmap: Vector Embeddings Integration.
It provides semantic search capabilities using sentence transformers and Neo4j vector indexes.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Vector embeddings dependencies
try:
    import torch
    from sentence_transformers import SentenceTransformer

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""

    text: str
    embedding: list[float]
    model_name: str
    dimensions: int
    created_at: datetime
    text_hash: str


class CodeEmbeddingGenerator:
    """Generates vector embeddings for code elements."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str | None = None) -> None:
        """Initialize the embedding generator.

        Args:
            model_name: Name of the sentence transformer model
            cache_dir: Directory to cache embeddings
        """
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".ignition" / "embeddings_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize model
        self.model = None
        self.dimensions = 384  # Default for all-MiniLM-L6-v2
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the sentence transformer model."""
        if not EMBEDDINGS_AVAILABLE:
            logger.warning("Sentence transformers not available. Install with: pip install sentence-transformers")
            return

        try:
            self.model = SentenceTransformer(self.model_name)
            self.dimensions = self.model.get_sentence_embedding_dimension()
            logger.info(f"Initialized embedding model: {self.model_name} ({self.dimensions}D)")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.model = None

    def generate_embedding(self, text: str, use_cache: bool = True) -> EmbeddingResult | None:
        """Generate embedding for text.

        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings

        Returns:
            EmbeddingResult or None if failed
        """
        if not self.model:
            logger.warning("Embedding model not available")
            return None

        # Create text hash for caching
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        # Check cache first
        if use_cache:
            cached = self._get_cached_embedding(text_hash)
            if cached:
                return cached

        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True).tolist()

            result = EmbeddingResult(
                text=text,
                embedding=embedding,
                model_name=self.model_name,
                dimensions=self.dimensions,
                created_at=datetime.now(),
                text_hash=text_hash,
            )

            # Cache the result
            if use_cache:
                self._cache_embedding(result)

            return result

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    def generate_file_embedding(self, file_content: str, file_path: str) -> EmbeddingResult | None:
        """Generate embedding for a code file.

        Preprocesses the code content for optimal embedding.
        """
        # Preprocess file content for embedding
        processed_content = self._preprocess_code_for_embedding(file_content, file_path)

        return self.generate_embedding(processed_content)

    def generate_function_embedding(
        self, function_code: str, function_name: str, docstring: str | None = None
    ) -> EmbeddingResult | None:
        """Generate embedding for a function.

        Combines function code, name, and docstring for optimal embedding.
        """
        # Combine function elements for embedding
        embedding_text = self._prepare_function_text(function_code, function_name, docstring)

        return self.generate_embedding(embedding_text)

    def generate_class_embedding(
        self,
        class_code: str,
        class_name: str,
        docstring: str | None = None,
        method_names: list[str] | None = None,
    ) -> EmbeddingResult | None:
        """Generate embedding for a class.

        Combines class code, name, docstring, and method names for optimal embedding.
        """
        # Combine class elements for embedding
        embedding_text = self._prepare_class_text(class_code, class_name, docstring, method_names)

        return self.generate_embedding(embedding_text)

    def _preprocess_code_for_embedding(self, code: str, file_path: str) -> str:
        """Preprocess code content for optimal embedding generation."""
        lines = code.split("\n")

        # Extract key information for embedding
        imports = []
        classes = []
        functions = []
        comments = []

        for line in lines:
            stripped = line.strip()

            # Collect imports
            if stripped.startswith(("import ", "from ")):
                imports.append(stripped)

            # Collect class definitions
            elif stripped.startswith("class "):
                classes.append(stripped.split("(")[0])  # Just class name

            # Collect function definitions
            elif stripped.startswith(("def ", "async def ")):
                functions.append(stripped.split("(")[0])  # Just function name

            # Collect meaningful comments
            elif stripped.startswith("#") and len(stripped) > 5:
                comments.append(stripped[1:].strip())

        # Create structured text for embedding
        file_summary = f"Python file: {Path(file_path).name}\n"

        if imports:
            file_summary += f"Imports: {', '.join(imports[:10])}\n"  # Limit imports

        if classes:
            file_summary += f"Classes: {', '.join(classes)}\n"

        if functions:
            file_summary += f"Functions: {', '.join(functions[:20])}\n"  # Limit functions

        if comments:
            file_summary += f"Key comments: {' | '.join(comments[:5])}\n"

        # Add first few meaningful lines of code (skip imports and comments)
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith(("#", "import ", "from "))]

        if code_lines:
            file_summary += f"Code excerpt: {' '.join(code_lines[:5])}"

        return file_summary

    def _prepare_function_text(self, function_code: str, function_name: str, docstring: str | None = None) -> str:
        """Prepare function text for embedding."""
        text_parts = [f"Function: {function_name}"]

        if docstring:
            text_parts.append(f"Purpose: {docstring}")

        # Extract function signature
        lines = function_code.split("\n")
        for line in lines:
            if "def " in line:
                text_parts.append(f"Signature: {line.strip()}")
                break

        # Add some key code lines (excluding docstring)
        code_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('"""')]

        if len(code_lines) > 1:
            meaningful_lines = [line for line in code_lines[1:6] if line and not line.startswith("#")]
            if meaningful_lines:
                text_parts.append(f"Implementation: {' | '.join(meaningful_lines)}")

        return "\n".join(text_parts)

    def _prepare_class_text(
        self,
        class_code: str,
        class_name: str,
        docstring: str | None = None,
        method_names: list[str] | None = None,
    ) -> str:
        """Prepare class text for embedding."""
        text_parts = [f"Class: {class_name}"]

        if docstring:
            text_parts.append(f"Purpose: {docstring}")

        if method_names:
            text_parts.append(f"Methods: {', '.join(method_names)}")

        # Extract class signature and inheritance
        lines = class_code.split("\n")
        for line in lines:
            if "class " in line:
                text_parts.append(f"Definition: {line.strip()}")
                break

        return "\n".join(text_parts)

    def _get_cached_embedding(self, text_hash: str) -> EmbeddingResult | None:
        """Get cached embedding by text hash."""
        cache_file = self.cache_dir / f"{text_hash}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                data = json.load(f)

            return EmbeddingResult(
                text=data["text"],
                embedding=data["embedding"],
                model_name=data["model_name"],
                dimensions=data["dimensions"],
                created_at=datetime.fromisoformat(data["created_at"]),
                text_hash=data["text_hash"],
            )
        except Exception as e:
            logger.debug(f"Failed to load cached embedding: {e}")
            return None

    def _cache_embedding(self, result: EmbeddingResult) -> None:
        """Cache embedding result."""
        cache_file = self.cache_dir / f"{result.text_hash}.json"

        try:
            data = {
                "text": result.text,
                "embedding": result.embedding,
                "model_name": result.model_name,
                "dimensions": result.dimensions,
                "created_at": result.created_at.isoformat(),
                "text_hash": result.text_hash,
            }

            with open(cache_file, "w") as f:
                json.dump(data, f)

        except Exception as e:
            logger.debug(f"Failed to cache embedding: {e}")

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Embedding cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get statistics about the embedding cache."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)

            return {
                "cached_embeddings": len(cache_files),
                "cache_size_mb": total_size / (1024 * 1024),
                "cache_directory": str(self.cache_dir),
                "model_name": self.model_name,
                "dimensions": self.dimensions,
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


class SemanticCodeSearch:
    """Provides semantic search capabilities for code using vector embeddings."""

    def __init__(self, graph_client, embedding_generator: CodeEmbeddingGenerator) -> None:
        """Initialize semantic search system.

        Args:
            graph_client: Neo4j graph client
            embedding_generator: Code embedding generator
        """
        self.client = graph_client
        self.embedder = embedding_generator

    def find_similar_code(self, query: str, context_type: str = "all", limit: int = 10) -> list[dict[str, Any]]:
        """Find semantically similar code using vector search.

        Args:
            query: Natural language or code query
            context_type: Type of code elements to search ('file', 'class', 'method', 'all')
            limit: Maximum number of results

        Returns:
            list of similar code elements with scores
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_embedding(query)
        if not query_embedding:
            logger.warning("Could not generate embedding for query")
            return []

        results = []

        # Search different node types based on context_type
        if context_type in ("all", "file"):
            results.extend(self._search_files(query_embedding.embedding, limit))

        if context_type in ("all", "class"):
            results.extend(self._search_classes(query_embedding.embedding, limit))

        if context_type in ("all", "method"):
            results.extend(self._search_methods(query_embedding.embedding, limit))

        # Sort by score and limit results
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:limit]

    def find_similar_to_file(self, file_path: str, limit: int = 10) -> list[dict[str, Any]]:
        """Find files similar to the given file.

        Args:
            file_path: Path to the reference file
            limit: Maximum number of results

        Returns:
            list of similar files with scores
        """
        # Get the file's embedding from the database
        cypher = """
        MATCH (f:CodeFile {path: $path})
        WHERE f.embedding IS NOT NULL
        RETURN f.embedding as embedding
        """

        result = self.client.execute_query(cypher, {"path": file_path})
        if not result:
            logger.warning(f"No embedding found for file: {file_path}")
            return []

        file_embedding = result[0]["embedding"]
        return self._search_files(file_embedding, limit, exclude_path=file_path)

    def _search_files(
        self, query_embedding: list[float], limit: int, exclude_path: str | None = None
    ) -> list[dict[str, Any]]:
        """Search for similar files using vector similarity."""
        cypher = """
        CALL db.index.vector.queryNodes('code_file_embeddings', $limit, $embedding)
        YIELD node, score
        WHERE ($exclude_path IS NULL OR node.path <> $exclude_path)
        MATCH (node)-[:CONTAINS]->(element)
        OPTIONAL MATCH (node)-[:IMPORTS]->(dep:CodeFile)
        RETURN
            'file' as type,
            node.path as path,
            node.complexity as complexity,
            node.lines as lines,
            score,
            collect(DISTINCT element.name)[0..5] as components,
            collect(DISTINCT dep.path)[0..5] as dependencies
        ORDER BY score DESC
        LIMIT $limit
        """

        params = {
            "embedding": query_embedding,
            "limit": limit,
            "exclude_path": exclude_path,
        }

        try:
            return self.client.execute_query(cypher, params)
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return []

    def _search_classes(self, query_embedding: list[float], limit: int) -> list[dict[str, Any]]:
        """Search for similar classes using vector similarity."""
        cypher = """
        CALL db.index.vector.queryNodes('class_embeddings', $limit, $embedding)
        YIELD node, score
        MATCH (f:CodeFile)-[:CONTAINS]->(node)
        OPTIONAL MATCH (node)-[:HAS_METHOD]->(m:Method)
        RETURN
            'class' as type,
            node.name as name,
            f.path as file_path,
            node.complexity as complexity,
            score,
            collect(m.name)[0..5] as methods
        ORDER BY score DESC
        LIMIT $limit
        """

        params = {"embedding": query_embedding, "limit": limit}

        try:
            return self.client.execute_query(cypher, params)
        except Exception as e:
            logger.error(f"Failed to search classes: {e}")
            return []

    def _search_methods(self, query_embedding: list[float], limit: int) -> list[dict[str, Any]]:
        """Search for similar methods using vector similarity."""
        cypher = """
        CALL db.index.vector.queryNodes('method_embeddings', $limit, $embedding)
        YIELD node, score
        MATCH (f:CodeFile)-[:CONTAINS]->(node)
        OPTIONAL MATCH (c:Class)-[:HAS_METHOD]->(node)
        RETURN
            'method' as type,
            node.name as name,
            f.path as file_path,
            c.name as class_name,
            node.complexity as complexity,
            node.parameters as parameters,
            score
        ORDER BY score DESC
        LIMIT $limit
        """

        params = {"embedding": query_embedding, "limit": limit}

        try:
            return self.client.execute_query(cypher, params)
        except Exception as e:
            logger.error(f"Failed to search methods: {e}")
            return []

    def find_code_patterns(
        self,
        pattern_description: str,
        complexity_range: tuple[float, float] | None = None,
        file_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Find code patterns matching a description.

        Args:
            pattern_description: Natural language description of the pattern
            complexity_range: Optional complexity filter (min, max)
            file_types: Optional list of file extensions to search

        Returns:
            list of matching code elements
        """
        # Generate embedding for pattern description
        pattern_embedding = self.embedder.generate_embedding(pattern_description)
        if not pattern_embedding:
            return []

        # Build dynamic query with filters
        base_cypher = """
        CALL db.index.vector.queryNodes('method_embeddings', 20, $embedding)
        YIELD node, score
        MATCH (f:CodeFile)-[:CONTAINS]->(node)
        WHERE score > 0.7
        """

        conditions = []
        params: dict[str, Any] = {"embedding": pattern_embedding.embedding}

        if complexity_range:
            conditions.append("node.complexity >= $min_complexity AND node.complexity <= $max_complexity")
            params["min_complexity"] = float(complexity_range[0])
            params["max_complexity"] = float(complexity_range[1])

        if file_types:
            file_patterns = [f"f.path ENDS WITH '.{ext}'" for ext in file_types]
            conditions.append(f"({' OR '.join(file_patterns)})")

        if conditions:
            base_cypher += " AND " + " AND ".join(conditions)

        base_cypher += """
        OPTIONAL MATCH (c:Class)-[:HAS_METHOD]->(node)
        RETURN
            node.name as method_name,
            f.path as file_path,
            c.name as class_name,
            node.complexity as complexity,
            node.docstring as docstring,
            score
        ORDER BY score DESC
        LIMIT 10
        """

        try:
            return self.client.execute_query(base_cypher, params)
        except Exception as e:
            logger.error(f"Failed to find code patterns: {e}")
            return []


def get_embedding_system(
    graph_client, model_name: str = "all-MiniLM-L6-v2"
) -> tuple[CodeEmbeddingGenerator | None, SemanticCodeSearch | None]:
    """Factory function to create embedding system components.

    Args:
        graph_client: Neo4j graph client
        model_name: Sentence transformer model name

    Returns:
        tuple of (embedding_generator, semantic_search) or (None, None) if unavailable
    """
    if not EMBEDDINGS_AVAILABLE:
        logger.error(
            "Vector embeddings not available. Install with: pip install sentence-transformers torch transformers"
        )
        return None, None

    embedding_generator = CodeEmbeddingGenerator(model_name)
    semantic_search = SemanticCodeSearch(graph_client, embedding_generator)

    return embedding_generator, semantic_search
