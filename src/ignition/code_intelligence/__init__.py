"""Code Intelligence System for IGN Scripts.

This module provides intelligent code analysis, semantic search, and AI assistant
enhancement capabilities using Neo4j graph database and vector embeddings.
"""

from .manager import CodeIntelligenceManager
from .analyzer import CodeAnalyzer
from .schema import CodeSchema

__all__ = [
    "CodeIntelligenceManager",
    "CodeAnalyzer", 
    "CodeSchema",
]

__version__ = "1.0.0" 