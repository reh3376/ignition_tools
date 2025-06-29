"""Script Generation Module for Ignition.

This module provides advanced script generation capabilities within the Ignition
Designer environment, leveraging code intelligence and Neo4j graph data for
context-aware script creation.
"""

from .code_intelligence import CodeIntelligenceIntegration
from .dynamic_generator import DynamicScriptGenerator
from .template_manager import TemplateManager
from .template_metadata import (
    TemplateCategory,
    TemplateMetadata,
    TemplateSearchResult,
    TemplateStatus,
    TemplateVersion,
)
from .template_search import TemplateSearchEngine
from .template_sharing import TemplateSharingManager
from .template_storage import TemplateStorage
from .template_versioning import TemplateVersionManager

__all__ = [
    "CodeIntelligenceIntegration",
    # Main classes
    "DynamicScriptGenerator",
    # Data classes
    "TemplateCategory",
    "TemplateManager",
    "TemplateMetadata",
    "TemplateSearchEngine",
    "TemplateSearchResult",
    "TemplateSharingManager",
    "TemplateStatus",
    # Template components
    "TemplateStorage",
    "TemplateVersion",
    "TemplateVersionManager",
]

__version__ = "1.0.0"
