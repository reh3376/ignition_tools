"""AI Assistant Module for Ignition Development.

This module provides AI-powered assistance for Ignition development, including:
- Intelligent code analysis and validation
- Context-aware script suggestions
- Knowledge graph-based validation
- AST-based code parsing and analysis
"""

from .ai_assistant_module import AIAssistantModule, create_ai_assistant_module
from .code_analyzer import CodeAnalyzer
from .knowledge_validator import KnowledgeValidator

__all__ = [
    "AIAssistantModule",
    "CodeAnalyzer",
    "KnowledgeValidator",
    "create_ai_assistant_module",
]
