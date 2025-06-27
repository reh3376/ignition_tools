"""Vector Embedding Enhancement for SME Agent.

This module implements vector embedding enhancement following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Error handling and user-friendly messages
4. Progressive complexity support
5. Resource management and cleanup

Enhances existing 384D vector embeddings with domain-specific knowledge,
implements hybrid search, and builds context-aware RAG system.
"""

import os
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import torch
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from neo4j import GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

from . import SMEAgentValidationError


class EmbeddingModel(Enum):
    """Supported embedding models."""

    ALL_MINILM_L6_V2 = "sentence-transformers/all-MiniLM-L6-v2"  # 384D
    ALL_MPNET_BASE_V2 = "sentence-transformers/all-mpnet-base-v2"  # 768D
    BGE_SMALL_EN_V1_5 = "BAAI/bge-small-en-v1.5"  # 384D
    BGE_BASE_EN_V1_5 = "BAAI/bge-base-en-v1.5"  # 768D
    CUSTOM = "custom"


class SearchMode(Enum):
    """Search modes for hybrid retrieval."""

    VECTOR_ONLY = "vector_only"  # Pure vector similarity search
    GRAPH_ONLY = "graph_only"  # Pure graph traversal search
    HYBRID = "hybrid"  # Combined vector + graph search
    ADAPTIVE = "adaptive"  # Adaptive based on query type


@dataclass
class VectorConfig:
    """Configuration for vector embedding enhancement."""

    # Model configuration
    embedding_model: EmbeddingModel = EmbeddingModel.ALL_MINILM_L6_V2
    custom_model_path: str | None = None
    embedding_dimension: int = 384

    # Index configuration
    use_faiss: bool = True
    faiss_index_type: str = "IndexFlatIP"  # Inner Product for cosine similarity
    enable_gpu: bool = False

    # Neo4j integration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"

    # Search configuration
    default_search_mode: SearchMode = SearchMode.HYBRID
    vector_weight: float = 0.7  # Weight for vector similarity in hybrid search
    graph_weight: float = 0.3  # Weight for graph traversal in hybrid search
    max_results: int = 10
    similarity_threshold: float = 0.5

    # RAG configuration
    context_window: int = 2048
    max_context_chunks: int = 5
    chunk_overlap: int = 50
    enable_reranking: bool = True

    # Storage configuration
    index_directory: str = "vector_indexes"
    cache_directory: str = "embedding_cache"
    enable_persistence: bool = True

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.embedding_model == EmbeddingModel.CUSTOM and not self.custom_model_path:
            raise ValueError(
                "custom_model_path required when embedding_model is CUSTOM"
            )

        if not 0.0 <= self.vector_weight <= 1.0:
            raise ValueError("vector_weight must be between 0.0 and 1.0")

        if not 0.0 <= self.graph_weight <= 1.0:
            raise ValueError("graph_weight must be between 0.0 and 1.0")

        if abs(self.vector_weight + self.graph_weight - 1.0) > 0.01:
            raise ValueError("vector_weight + graph_weight must equal 1.0")


@dataclass
class EmbeddingResult:
    """Result from embedding operation."""

    text: str
    embedding: list[float]
    model_name: str
    dimension: int
    processing_time: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "text": self.text,
            "embedding": self.embedding,
            "model_name": self.model_name,
            "dimension": self.dimension,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
        }


@dataclass
class SearchResult:
    """Result from hybrid search operation."""

    id: str
    text: str
    score: float
    source: str  # 'vector', 'graph', or 'hybrid'
    embedding: list[float] | None = None
    graph_path: list[str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "score": self.score,
            "source": self.source,
            "embedding": self.embedding,
            "graph_path": self.graph_path,
            "metadata": self.metadata,
        }


def validate_vector_embedding_environment() -> dict[str, Any]:
    """Validate vector embedding environment following crawl_mcp.py methodology.

    Step 1: Environment validation first - comprehensive validation of all requirements.

    Returns:
        dict containing validation results and component availability.
    """
    validation_result: dict[str, Any] = {
        "validation_score": 0,
        "total_checks": 12,
        "components": {},
        "environment_variables": {},
        "hardware": {},
        "errors": [],
        "recommendations": [],
    }

    # 1. Check Python packages
    if NUMPY_AVAILABLE:
        validation_result["components"]["numpy"] = {"available": True}
        validation_result["validation_score"] += 1
    else:
        validation_result["components"]["numpy"] = {"available": False}
        validation_result["errors"].append("numpy package not installed")

    if SENTENCE_TRANSFORMERS_AVAILABLE:
        validation_result["components"]["sentence_transformers"] = {"available": True}
        validation_result["validation_score"] += 1
    else:
        validation_result["components"]["sentence_transformers"] = {"available": False}
        validation_result["errors"].append(
            "sentence-transformers package not installed"
        )

    if FAISS_AVAILABLE:
        validation_result["components"]["faiss"] = {"available": True}
        validation_result["validation_score"] += 1
    else:
        validation_result["components"]["faiss"] = {"available": False}
        validation_result["recommendations"].append(
            "faiss-cpu not available - will use slower similarity search"
        )

    if NEO4J_AVAILABLE:
        validation_result["components"]["neo4j"] = {"available": True}
        validation_result["validation_score"] += 1
    else:
        validation_result["components"]["neo4j"] = {"available": False}
        validation_result["errors"].append("neo4j package not installed")

    # 2. Check environment variables
    env_vars = {
        "EMBEDDING_MODEL": os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        ),
        "EMBEDDING_DIMENSION": os.getenv("EMBEDDING_DIMENSION", "384"),
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USER": os.getenv("NEO4J_USER"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
        "VECTOR_SEARCH_MODE": os.getenv("VECTOR_SEARCH_MODE", "hybrid"),
        "VECTOR_SIMILARITY_THRESHOLD": os.getenv("VECTOR_SIMILARITY_THRESHOLD", "0.5"),
        "VECTOR_INDEX_DIRECTORY": os.getenv("VECTOR_INDEX_DIRECTORY", "vector_indexes"),
    }

    for var, value in env_vars.items():
        validation_result["environment_variables"][var] = {
            "set": value is not None,
            "value": value if value else "not_set",
        }
        if value:
            validation_result["validation_score"] += 0.5

    # 3. Check hardware capabilities
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        try:
            import torch

            if torch.cuda.is_available():
                validation_result["hardware"]["gpu"] = {
                    "available": True,
                    "device_count": torch.cuda.device_count(),
                    "device_names": [
                        torch.cuda.get_device_name(i)
                        for i in range(torch.cuda.device_count())
                    ],
                }
                validation_result["validation_score"] += 1
            else:
                validation_result["hardware"]["gpu"] = {"available": False}
                validation_result["recommendations"].append(
                    "GPU not available - embeddings will be slower"
                )
        except Exception:
            validation_result["hardware"]["gpu"] = {"available": False}

    # Calculate final score
    max_score = validation_result["total_checks"]
    actual_score = validation_result["validation_score"]
    validation_result["validation_percentage"] = round(
        (actual_score / max_score) * 100, 1
    )

    return validation_result


class VectorEmbeddingEnhancement:
    """Vector Embedding Enhancement following crawl_mcp.py methodology.

    Implements systematic approach:
    1. Environment validation first
    2. Comprehensive input validation
    3. Error handling and user-friendly messages
    4. Progressive complexity support
    5. Resource management and cleanup
    """

    def __init__(self, config: VectorConfig | None = None):
        """Initialize vector embedding enhancement with configuration."""
        self.config = config or VectorConfig()
        self.embedding_model = None
        self.faiss_index = None
        self.neo4j_driver = None
        self.validation_result: dict[str, Any] = None

        # Storage
        self.document_store = {}  # id -> document mapping
        self.embedding_cache = {}  # text -> embedding mapping

        # Statistics
        self.stats = {
            "embeddings_generated": 0,
            "searches_performed": 0,
            "cache_hits": 0,
            "total_processing_time": 0.0,
        }

    async def initialize(self) -> dict[str, Any]:
        """Initialize vector embedding enhancement following crawl_mcp.py methodology.

        Step 1: Environment validation first
        Step 2: Component initialization
        Step 3: Resource management setup
        """
        # Step 1: Environment validation first
        self.validation_result = validate_vector_embedding_environment()

        if self.validation_result["validation_percentage"] < 60:
            raise SMEAgentValidationError(
                f"Vector embedding validation failed: {self.validation_result['validation_percentage']}% "
                f"Errors: {', '.join(self.validation_result['errors'])}"
            )

        # Step 2: Component initialization
        init_result = {
            "status": "success",
            "components_initialized": [],
            "warnings": [],
        }

        try:
            # Initialize embedding model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                model_name = self._get_model_name()
                self.embedding_model = SentenceTransformer(model_name)
                init_result["components_initialized"].append("embedding_model")

            # Initialize FAISS index
            if FAISS_AVAILABLE and self.config.use_faiss:
                self._initialize_faiss_index()
                init_result["components_initialized"].append("faiss_index")

            # Initialize Neo4j connection
            if NEO4J_AVAILABLE:
                self.neo4j_driver = GraphDatabase.driver(
                    self.config.neo4j_uri,
                    auth=(self.config.neo4j_user, self.config.neo4j_password),
                )
                init_result["components_initialized"].append("neo4j_driver")

            # Create directories
            self._create_directories()
            init_result["components_initialized"].append("directories")

            # Load existing index if available
            if self.config.enable_persistence:
                self._load_persistent_index()
                init_result["components_initialized"].append("persistent_index")

            return init_result

        except Exception as e:
            raise SMEAgentValidationError(
                f"Vector embedding initialization failed: {e}"
            )

    def _get_model_name(self) -> str:
        """Get the model name based on configuration."""
        if self.config.embedding_model == EmbeddingModel.CUSTOM:
            if self.config.custom_model_path:
                return self.config.custom_model_path
            else:
                raise SMEAgentValidationError("Custom model path not provided")
        return self.config.embedding_model.value

    def _initialize_faiss_index(self) -> None:
        """Initialize FAISS index for vector similarity search."""
        if self.config.faiss_index_type == "IndexFlatIP":
            # Inner Product (cosine similarity for normalized vectors)
            self.faiss_index = faiss.IndexFlatIP(self.config.embedding_dimension)
        elif self.config.faiss_index_type == "IndexFlatL2":
            # L2 distance
            self.faiss_index = faiss.IndexFlatL2(self.config.embedding_dimension)
        elif self.config.faiss_index_type == "IndexIVFFlat":
            # Inverted File with Flat quantizer (faster for large datasets)
            quantizer = faiss.IndexFlatIP(self.config.embedding_dimension)
            self.faiss_index = faiss.IndexIVFFlat(
                quantizer, self.config.embedding_dimension, 100
            )
        else:
            # Default to flat inner product
            self.faiss_index = faiss.IndexFlatIP(self.config.embedding_dimension)

        # Enable GPU if available and requested
        if self.config.enable_gpu and FAISS_AVAILABLE:
            try:
                import faiss

                if faiss.get_num_gpus() > 0:
                    self.faiss_index = faiss.index_cpu_to_gpu(
                        faiss.StandardGpuResources(), 0, self.faiss_index
                    )
            except Exception:
                pass  # Fall back to CPU

    def _create_directories(self) -> None:
        """Create necessary directories."""
        Path(self.config.index_directory).mkdir(parents=True, exist_ok=True)
        Path(self.config.cache_directory).mkdir(parents=True, exist_ok=True)

    def _load_persistent_index(self) -> None:
        """Load persistent index and document store if available."""
        try:
            index_path = Path(self.config.index_directory) / "faiss_index.bin"
            docs_path = Path(self.config.index_directory) / "document_store.pkl"

            if index_path.exists() and docs_path.exists():
                # Load FAISS index
                if FAISS_AVAILABLE and self.faiss_index is not None:
                    saved_index = faiss.read_index(str(index_path))
                    # Verify dimensions match
                    if saved_index.d == self.config.embedding_dimension:
                        self.faiss_index = saved_index

                # Load document store
                with open(docs_path, "rb") as f:
                    self.document_store = pickle.load(f)

        except Exception as e:
            print(f"Warning: Could not load persistent index: {e}")

    async def generate_embedding(
        self, text: str, use_cache: bool = True
    ) -> EmbeddingResult:
        """Generate embedding for text following crawl_mcp.py methodology.

        Step 2: Comprehensive input validation
        Step 3: Error handling and user-friendly messages
        """
        # Step 2: Comprehensive input validation
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        if len(text.strip()) == 0:
            raise ValueError("Text cannot be empty or whitespace only")

        if len(text) > 10000:  # Reasonable limit
            raise ValueError("Text too long (max 10,000 characters)")

        # Check cache first
        if use_cache and text in self.embedding_cache:
            self.stats["cache_hits"] += 1
            cached_result = self.embedding_cache[text]
            return EmbeddingResult(
                text=text,
                embedding=cached_result["embedding"],
                model_name=cached_result["model_name"],
                dimension=cached_result["dimension"],
                processing_time=0.0,  # Cached
                metadata={"cached": True},
            )

        try:
            start_time = datetime.now()

            if not self.embedding_model:
                raise SMEAgentValidationError("Embedding model not initialized")

            # Generate embedding
            embedding = self.embedding_model.encode([text])[0]

            # Normalize for cosine similarity
            if NUMPY_AVAILABLE:
                embedding = embedding / np.linalg.norm(embedding)

            processing_time = (datetime.now() - start_time).total_seconds()

            # Cache result
            if use_cache:
                self.embedding_cache[text] = {
                    "embedding": embedding.tolist(),
                    "model_name": self._get_model_name(),
                    "dimension": len(embedding),
                }

            # Update statistics
            self.stats["embeddings_generated"] += 1
            self.stats["total_processing_time"] += processing_time

            return EmbeddingResult(
                text=text,
                embedding=embedding.tolist(),
                model_name=self._get_model_name(),
                dimension=len(embedding),
                processing_time=processing_time,
                metadata={"cached": False},
            )

        except Exception as e:
            # Step 3: Error handling and user-friendly messages
            error_msg = self._format_embedding_error(e)
            raise SMEAgentValidationError(f"Embedding generation failed: {error_msg}")

    async def add_documents(
        self, documents: list[dict[str, Any]], batch_size: int = 32
    ) -> dict[str, Any]:
        """Add documents to the vector index."""
        if not documents:
            raise ValueError("Documents list cannot be empty")

        added_count = 0
        embeddings_batch = []
        ids_batch = []

        try:
            for i, doc in enumerate(documents):
                # Validate document format
                if "id" not in doc or "text" not in doc:
                    continue

                doc_id = doc["id"]
                text = doc["text"]

                # Generate embedding
                result = await self.generate_embedding(text)

                # Store document
                self.document_store[doc_id] = {
                    "text": text,
                    "embedding": result.embedding,
                    "metadata": doc.get("metadata", {}),
                    "added_at": datetime.now().isoformat(),
                }

                embeddings_batch.append(result.embedding)
                ids_batch.append(doc_id)
                added_count += 1

                # Add to FAISS index in batches
                if len(embeddings_batch) >= batch_size or i == len(documents) - 1:
                    if (
                        FAISS_AVAILABLE
                        and self.faiss_index is not None
                        and embeddings_batch
                    ):
                        if NUMPY_AVAILABLE:
                            embeddings_array = np.array(
                                embeddings_batch, dtype=np.float32
                            )
                            self.faiss_index.add(embeddings_array)

                        embeddings_batch = []
                        ids_batch = []

            # Save persistent index
            if self.config.enable_persistence:
                self._save_persistent_index()

            return {
                "status": "success",
                "documents_added": added_count,
                "total_documents": len(self.document_store),
            }

        except Exception as e:
            raise SMEAgentValidationError(f"Failed to add documents: {e}")

    async def hybrid_search(
        self,
        query: str,
        search_mode: SearchMode | None = None,
        max_results: int | None = None,
    ) -> list[SearchResult]:
        """Perform hybrid search combining vector similarity and graph traversal.

        Step 2: Comprehensive input validation
        Step 3: Error handling and user-friendly messages
        """
        # Step 2: Comprehensive input validation
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        if len(query.strip()) == 0:
            raise ValueError("Query cannot be empty or whitespace only")

        search_mode = search_mode or self.config.default_search_mode
        max_results = max_results or self.config.max_results

        if max_results <= 0:
            raise ValueError("max_results must be positive")

        try:
            start_time = datetime.now()

            if search_mode == SearchMode.VECTOR_ONLY:
                results = await self._vector_search(query, max_results)
            elif search_mode == SearchMode.GRAPH_ONLY:
                results = await self._graph_search(query, max_results)
            elif search_mode == SearchMode.HYBRID:
                results = await self._hybrid_search_combined(query, max_results)
            elif search_mode == SearchMode.ADAPTIVE:
                results = await self._adaptive_search(query, max_results)
            else:
                results = await self._hybrid_search_combined(query, max_results)

            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats["searches_performed"] += 1
            self.stats["total_processing_time"] += processing_time

            return results

        except Exception as e:
            # Step 3: Error handling and user-friendly messages
            error_msg = self._format_search_error(e)
            raise SMEAgentValidationError(f"Hybrid search failed: {error_msg}")

    async def _vector_search(self, query: str, max_results: int) -> list[SearchResult]:
        """Perform pure vector similarity search."""
        if not self.faiss_index or not self.document_store:
            return []

        # Generate query embedding
        query_result = await self.generate_embedding(query)
        query_embedding = np.array([query_result.embedding], dtype=np.float32)

        # Search FAISS index
        scores, indices = self.faiss_index.search(query_embedding, max_results)

        results = []
        doc_ids = list(self.document_store.keys())

        for i, (score, idx) in enumerate(zip(scores[0], indices[0], strict=False)):
            if (
                idx >= 0
                and idx < len(doc_ids)
                and score >= self.config.similarity_threshold
            ):
                doc_id = doc_ids[idx]
                doc = self.document_store[doc_id]

                result = SearchResult(
                    id=doc_id,
                    text=doc["text"],
                    score=float(score),
                    source="vector",
                    embedding=doc["embedding"],
                    metadata=doc.get("metadata", {}),
                )
                results.append(result)

        return results

    async def _graph_search(self, query: str, max_results: int) -> list[SearchResult]:
        """Perform pure graph traversal search."""
        if not self.neo4j_driver:
            return []

        results = []

        try:
            with self.neo4j_driver.session() as session:
                # Simple text search in Neo4j
                cypher_query = """
                MATCH (n)
                WHERE any(prop in keys(n) WHERE toString(n[prop]) CONTAINS $query)
                RETURN n, id(n) as node_id
                LIMIT $max_results
                """

                result = session.run(cypher_query, query=query, max_results=max_results)

                for record in result:
                    node = record["n"]
                    node_id = str(record["node_id"])

                    # Extract text content
                    properties = dict(node)
                    text_parts = []
                    for key, value in properties.items():
                        if isinstance(value, str) and value.strip():
                            text_parts.append(f"{key}: {value}")

                    text = " | ".join(text_parts) if text_parts else str(properties)

                    search_result = SearchResult(
                        id=node_id,
                        text=text,
                        score=0.8,  # Default score for graph results
                        source="graph",
                        metadata={
                            "node_labels": list(node.labels),
                            "properties": properties,
                        },
                    )
                    results.append(search_result)

        except Exception as e:
            print(f"Warning: Graph search failed: {e}")

        return results

    async def _hybrid_search_combined(
        self, query: str, max_results: int
    ) -> list[SearchResult]:
        """Perform combined vector and graph search."""
        # Get results from both methods
        vector_results = await self._vector_search(query, max_results)
        graph_results = await self._graph_search(query, max_results)

        # Combine and rerank results
        all_results = []

        # Add vector results with weighted scores
        for result in vector_results:
            result.score = result.score * self.config.vector_weight
            result.source = "hybrid"
            all_results.append(result)

        # Add graph results with weighted scores
        for result in graph_results:
            result.score = result.score * self.config.graph_weight
            result.source = "hybrid"
            all_results.append(result)

        # Remove duplicates and sort by score
        unique_results = {}
        for result in all_results:
            if (
                result.id not in unique_results
                or result.score > unique_results[result.id].score
            ):
                unique_results[result.id] = result

        # Sort by score and return top results
        sorted_results = sorted(
            unique_results.values(), key=lambda x: x.score, reverse=True
        )
        return sorted_results[:max_results]

    async def _adaptive_search(
        self, query: str, max_results: int
    ) -> list[SearchResult]:
        """Perform adaptive search based on query characteristics."""
        # Simple heuristics for now - can be enhanced with ML
        if any(
            keyword in query.lower()
            for keyword in ["function", "method", "class", "code"]
        ):
            # Code-related queries favor vector search
            return await self._vector_search(query, max_results)
        elif any(
            keyword in query.lower()
            for keyword in ["relationship", "connected", "related"]
        ):
            # Relationship queries favor graph search
            return await self._graph_search(query, max_results)
        else:
            # Default to hybrid
            return await self._hybrid_search_combined(query, max_results)

    def _format_embedding_error(self, error: Exception) -> str:
        """Format embedding errors for user-friendly messages."""
        error_str = str(error).lower()

        if "out of memory" in error_str or "cuda out of memory" in error_str:
            return "GPU out of memory. Try reducing batch size or using CPU."
        elif "model not found" in error_str:
            return "Embedding model not found. Check model name and ensure it's downloaded."
        elif "connection" in error_str:
            return "Network connection error. Check internet connectivity."
        else:
            return str(error)

    def _format_search_error(self, error: Exception) -> str:
        """Format search errors for user-friendly messages."""
        error_str = str(error).lower()

        if "index" in error_str:
            return "Vector index error. Try rebuilding the index."
        elif "neo4j" in error_str or "connection" in error_str:
            return "Neo4j connection error. Check if Neo4j is running."
        elif "timeout" in error_str:
            return "Search timeout. Try reducing max_results or simplifying query."
        else:
            return str(error)

    def _save_persistent_index(self) -> Any:
        """Save persistent index and document store."""
        try:
            index_path = Path(self.config.index_directory) / "faiss_index.bin"
            docs_path = Path(self.config.index_directory) / "document_store.pkl"

            # Save FAISS index
            if FAISS_AVAILABLE and self.faiss_index is not None:
                faiss.write_index(self.faiss_index, str(index_path))

            # Save document store
            with open(docs_path, "wb") as f:
                pickle.dump(self.document_store, f)

        except Exception as e:
            print(f"Warning: Could not save persistent index: {e}")

    def get_enhancement_stats(self) -> dict[str, Any]:
        """Get comprehensive enhancement statistics."""
        return {
            "stats": self.stats,
            "index_info": {
                "total_documents": len(self.document_store),
                "index_size": (
                    self.faiss_index.ntotal
                    if FAISS_AVAILABLE and self.faiss_index
                    else 0
                ),
                "embedding_dimension": self.config.embedding_dimension,
            },
            "config": {
                "embedding_model": self.config.embedding_model.value,
                "search_mode": self.config.default_search_mode.value,
                "similarity_threshold": self.config.similarity_threshold,
            },
            "validation": self.validation_result,
        }

    async def cleanup(self) -> None:
        """Cleanup resources following crawl_mcp.py methodology."""
        try:
            # Save persistent state
            if self.config.enable_persistence:
                self._save_persistent_index()

            # Close Neo4j connection
            if self.neo4j_driver:
                self.neo4j_driver.close()
                self.neo4j_driver = None

            # Clear memory
            self.document_store = {}
            self.embedding_cache = {}

            # Clear GPU cache if using PyTorch
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                try:
                    import torch

                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except Exception:
                    pass

        except Exception as e:
            print(f"Warning: Error during vector embedding cleanup: {e}")

    async def __aenter__(self) -> Any:
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.cleanup()


# Convenience functions for easy usage
async def create_enhanced_vector_search(
    documents: list[dict[str, Any]],
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    search_mode: str = "hybrid",
    **kwargs,
) -> VectorEmbeddingEnhancement:
    """Create enhanced vector search with simplified interface.

    Args:
        documents: list of documents to index
        embedding_model: Embedding model to use
        search_mode: Search mode (vector_only, graph_only, hybrid, adaptive)
        **kwargs: Additional configuration options

    Returns:
        Initialized VectorEmbeddingEnhancement instance
    """
    # Map string inputs to enums
    model_map = {
        "sentence-transformers/all-MiniLM-L6-v2": EmbeddingModel.ALL_MINILM_L6_V2,
        "sentence-transformers/all-mpnet-base-v2": EmbeddingModel.ALL_MPNET_BASE_V2,
        "BAAI/bge-small-en-v1.5": EmbeddingModel.BGE_SMALL_EN_V1_5,
        "BAAI/bge-base-en-v1.5": EmbeddingModel.BGE_BASE_EN_V1_5,
        "custom": EmbeddingModel.CUSTOM,
    }

    search_map = {
        "vector_only": SearchMode.VECTOR_ONLY,
        "graph_only": SearchMode.GRAPH_ONLY,
        "hybrid": SearchMode.HYBRID,
        "adaptive": SearchMode.ADAPTIVE,
    }

    config = VectorConfig(
        embedding_model=model_map.get(embedding_model, EmbeddingModel.ALL_MINILM_L6_V2),
        default_search_mode=search_map.get(search_mode, SearchMode.HYBRID),
        **kwargs,
    )

    enhancement = VectorEmbeddingEnhancement(config)
    await enhancement.initialize()

    # Add documents to index
    if documents:
        await enhancement.add_documents(documents)

    return enhancement


def get_enhancement_info() -> dict[str, Any]:
    """Get information about vector embedding enhancement capabilities."""
    return {
        "embedding_models": {
            "all-MiniLM-L6-v2": "384D, fast and efficient",
            "all-mpnet-base-v2": "768D, higher quality",
            "bge-small-en-v1.5": "384D, optimized for retrieval",
            "bge-base-en-v1.5": "768D, optimized for retrieval",
            "custom": "Custom model path",
        },
        "search_modes": {
            "vector_only": "Pure vector similarity search",
            "graph_only": "Pure graph traversal search",
            "hybrid": "Combined vector + graph search",
            "adaptive": "Adaptive based on query type",
        },
        "features": {
            "faiss_indexing": "Fast approximate nearest neighbor search",
            "gpu_acceleration": "GPU support for embeddings and indexing",
            "persistent_storage": "Save and load indexes automatically",
            "hybrid_retrieval": "Combine vector and graph search",
            "context_aware_rag": "Retrieval augmented generation",
        },
        "requirements": {
            "sentence_transformers": "For embedding generation",
            "faiss": "For fast vector similarity search",
            "neo4j": "For graph traversal search",
            "numpy": "For numerical operations",
        },
    }
