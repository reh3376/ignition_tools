"""Script Generation Module for Ignition.

This module provides advanced script generation capabilities within the Ignition
Designer environment, leveraging code intelligence and Neo4j graph data for
context-aware script creation.
"""

from .code_intelligence import CodeIntelligenceIntegration
from .dynamic_generator import DynamicScriptGenerator
from .template_manager import TemplateManager

__all__ = [
    "CodeIntelligenceIntegration",
    "DynamicScriptGenerator",
    "TemplateManager",
]

__version__ = "1.0.0"
