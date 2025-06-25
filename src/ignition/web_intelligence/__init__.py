"""IGN Scripts Web Intelligence & Validation System - Phase 11.8

This module provides advanced web crawling, knowledge graph validation, and AI-powered
code analysis capabilities using best-in-class open source models instead of proprietary APIs.

Key Design Principle: Complete independence from OpenAI and other proprietary model APIs
through strategic use of open source alternatives hosted locally or via Hugging Face.

Following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Robust error handling
4. Modular testing approach
5. Progressive complexity
6. Proper resource management
"""

import os
from typing import Any

from pydantic import BaseModel, Field


class WebIntelligenceConfig(BaseModel):
    """Configuration for Web Intelligence system following crawl_mcp.py patterns."""

    web_intelligence_enabled: bool = Field(
        default=False, description="Enable web intelligence features"
    )
    use_local_models: bool = Field(
        default=True, description="Force local models, no external APIs"
    )
    ollama_host: str = Field(
        default="http://localhost:11434", description="Local Ollama server"
    )
    hf_cache_dir: str = Field(
        default="/tmp/hf_cache", description="Hugging Face model cache"
    )

    # Model Selection Configuration (following Phase 11.8 spec)
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model"
    )
    code_analysis_model: str = Field(
        default="codellama:13b-instruct", description="Code analysis model"
    )
    documentation_model: str = Field(
        default="mistral:7b-instruct", description="Documentation model"
    )
    validation_model: str = Field(
        default="llama3.1:8b-instruct", description="Validation model"
    )
    coder_model: str = Field(default="qwen2.5-coder:7b", description="Coder model")

    # Crawling Configuration
    crawl_update_interval: str = Field(
        default="daily", description="Crawl update interval"
    )
    documentation_sources: str = Field(
        default="ignition_docs,community_forums,github_ignition",
        description="Documentation sources",
    )
    max_concurrent_crawls: int = Field(default=5, description="Max concurrent crawls")
    chunk_size: int = Field(
        default=1000, description="Optimized for local model context windows"
    )


def validate_environment() -> bool:
    """Validate environment setup before proceeding (crawl_mcp.py methodology).

    Returns:
        bool: True if environment is ready, False otherwise
    """
    validation_results = []

    # 1. Check web intelligence settings
    web_intelligence_enabled = (
        os.getenv("WEB_INTELLIGENCE_ENABLED", "false").lower() == "true"
    )
    validation_results.append(("Web Intelligence Enabled", web_intelligence_enabled))

    if not web_intelligence_enabled:
        print("Web Intelligence disabled - set WEB_INTELLIGENCE_ENABLED=true to enable")
        return False

    # 2. Check local models preference
    use_local_models = os.getenv("USE_LOCAL_MODELS", "true").lower() == "true"
    validation_results.append(("Use Local Models", use_local_models))

    # 3. Check Ollama availability
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        import requests

        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        ollama_available = response.status_code == 200
    except Exception:
        ollama_available = False
    validation_results.append(("Ollama Available", ollama_available))

    # 4. Check Hugging Face cache directory
    hf_cache_dir = os.getenv("HF_CACHE_DIR", "/tmp/hf_cache")
    try:
        os.makedirs(hf_cache_dir, exist_ok=True)
        hf_cache_writable = os.access(hf_cache_dir, os.W_OK)
    except Exception:
        hf_cache_writable = False
    validation_results.append(("HF Cache Writable", hf_cache_writable))

    # 5. Check Neo4j availability (following crawl_mcp.py patterns)
    neo4j_available = validate_neo4j_connection()
    validation_results.append(("Neo4j Available", neo4j_available))

    # 6. Check crawling configuration
    crawl_sources = os.getenv("DOCUMENTATION_SOURCES", "").strip()
    crawl_configured = bool(crawl_sources)
    validation_results.append(("Crawl Sources Configured", crawl_configured))

    # Print validation results
    print("Web Intelligence Environment Validation:")
    for check, result in validation_results:
        status = "✓" if result else "✗"
        print(f"  {status} {check}: {result}")

    # All critical components must be available
    critical_checks = [use_local_models, hf_cache_writable, neo4j_available]

    return all(critical_checks)


def validate_neo4j_connection() -> bool:
    """Check if Neo4j environment variables are configured (from crawl_mcp.py)."""
    return all(
        [os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")]
    )


def format_neo4j_error(error: Exception) -> str:
    """Format Neo4j connection errors for user-friendly messages (from crawl_mcp.py)."""
    error_str = str(error).lower()
    if "authentication" in error_str or "unauthorized" in error_str:
        return "Neo4j authentication failed. Check NEO4J_USER and NEO4J_PASSWORD."
    elif "connection" in error_str or "refused" in error_str or "timeout" in error_str:
        return "Cannot connect to Neo4j. Check NEO4J_URI and ensure Neo4j is running."
    elif "database" in error_str:
        return "Neo4j database error. Check if the database exists and is accessible."
    else:
        return f"Neo4j error: {error!s}"


__all__ = [
    "WebIntelligenceConfig",
    "format_neo4j_error",
    "validate_environment",
    "validate_neo4j_connection",
]
