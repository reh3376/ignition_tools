"""Template Metadata Classes and Enums for Script Generation Module.

This module contains all data structures used for template management including
metadata, search results, and enumerations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TemplateCategory(str, Enum):
    """Template categories for organization."""

    GATEWAY = "gateway"
    VISION = "vision"
    PERSPECTIVE = "perspective"
    TAG = "tag"
    ALARM = "alarm"
    DATABASE = "database"
    REPORT = "report"
    UTILITY = "utility"
    CUSTOM = "custom"


class TemplateStatus(str, Enum):
    """Template status for lifecycle management."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class TemplateMetadata:
    """Metadata for a template."""

    name: str
    category: TemplateCategory
    description: str
    version: str = "1.0.0"
    author: str = "Unknown"
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    status: TemplateStatus = TemplateStatus.ACTIVE
    tags: list[str] = field(default_factory=list)
    parameters: dict[str, dict[str, Any]] = field(default_factory=dict)
    examples: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    compatible_versions: list[str] = field(default_factory=lambda: ["8.1+"])


@dataclass
class TemplateSearchResult:
    """Search result for template queries."""

    template_path: str
    metadata: TemplateMetadata
    relevance_score: float = 1.0
    matched_fields: list[str] = field(default_factory=list)


@dataclass
class TemplateVersion:
    """Version information for a template."""

    version: str
    created_at: datetime
    author: str
    changelog: str
    file_hash: str
    is_current: bool = False
