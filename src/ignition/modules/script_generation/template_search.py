"""Template Search Engine for Script Generation Module.

This module provides advanced search and browsing capabilities for templates
including filtering, ranking, and relevance scoring.
"""

import logging

from .template_metadata import (
    TemplateCategory,
    TemplateSearchResult,
    TemplateStatus,
)
from .template_storage import TemplateStorage


class TemplateSearchEngine:
    """Advanced search engine for templates."""

    def __init__(self, storage: TemplateStorage) -> None:
        """Initialize the search engine.

        Args:
            storage: Template storage instance
        """
        self.storage = storage
        self.logger = logging.getLogger(__name__)

    def browse_templates(
        self,
        category: TemplateCategory | None = None,
        status: TemplateStatus | None = None,
        tags: list[str] | None = None,
    ) -> list[TemplateSearchResult]:
        """Browse templates with optional filtering.

        Args:
            category: Filter by category
            status: Filter by status
            tags: Filter by tags (any match)

        Returns:
            list of matching templates
        """
        # Load template index
        template_index = self.storage.load_template_index()
        results = []

        for template_path, metadata in template_index.items():
            # Apply filters
            if category and metadata.category != category:
                continue

            if status and metadata.status != status:
                continue

            if tags and not any(tag in metadata.tags for tag in tags):
                continue

            results.append(
                TemplateSearchResult(
                    template_path=template_path,
                    metadata=metadata,
                    relevance_score=1.0,
                    matched_fields=["browse"],
                )
            )

        # Sort by name
        results.sort(key=lambda x: x.metadata.name)

        return results

    def search_templates(
        self,
        query: str,
        category: TemplateCategory | None = None,
        limit: int = 20,
    ) -> list[TemplateSearchResult]:
        """Search templates by query string.

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum results to return

        Returns:
            list of search results sorted by relevance
        """
        # Load template index
        template_index = self.storage.load_template_index()
        results = []
        query_lower = query.lower()

        for template_path, metadata in template_index.items():
            # Skip if category doesn't match
            if category and metadata.category != category:
                continue

            # Calculate relevance score
            score = 0.0
            matched_fields = []

            # Name matching (highest weight)
            if query_lower in metadata.name.lower():
                score += 10.0
                matched_fields.append("name")

            # Description matching
            if query_lower in metadata.description.lower():
                score += 5.0
                matched_fields.append("description")

            # Tag matching
            for tag in metadata.tags:
                if query_lower in tag:
                    score += 3.0
                    matched_fields.append(f"tag:{tag}")
                    break

            # Path matching
            if query_lower in template_path.lower():
                score += 2.0
                matched_fields.append("path")

            # Parameter matching
            for param_name, param_info in metadata.parameters.items():
                if query_lower in param_name.lower():
                    score += 1.0
                    matched_fields.append(f"parameter:{param_name}")
                elif isinstance(param_info, dict):
                    desc = param_info.get("description", "")
                    if query_lower in desc.lower():
                        score += 0.5
                        matched_fields.append(f"parameter_desc:{param_name}")

            if score > 0:
                results.append(
                    TemplateSearchResult(
                        template_path=template_path,
                        metadata=metadata,
                        relevance_score=score,
                        matched_fields=matched_fields,
                    )
                )

        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:limit]

    def find_similar_templates(self, template_path: str, limit: int = 10) -> list[TemplateSearchResult]:
        """Find templates similar to a given template.

        Args:
            template_path: Path to reference template
            limit: Maximum results to return

        Returns:
            list of similar templates
        """
        # Load template index
        template_index = self.storage.load_template_index()

        # Get reference template metadata
        reference_metadata = template_index.get(template_path)
        if not reference_metadata:
            return []

        results = []

        for path, metadata in template_index.items():
            if path == template_path:
                continue  # Skip self

            # Calculate similarity score
            score = 0.0
            matched_fields = []

            # Same category (high weight)
            if metadata.category == reference_metadata.category:
                score += 5.0
                matched_fields.append("category")

            # Shared tags
            shared_tags = set(metadata.tags) & set(reference_metadata.tags)
            if shared_tags:
                score += len(shared_tags) * 2.0
                matched_fields.extend([f"tag:{tag}" for tag in shared_tags])

            # Similar parameters
            shared_params = set(metadata.parameters.keys()) & set(reference_metadata.parameters.keys())
            if shared_params:
                score += len(shared_params) * 1.0
                matched_fields.append(f"params:{len(shared_params)}")

            if score > 0:
                results.append(
                    TemplateSearchResult(
                        template_path=path,
                        metadata=metadata,
                        relevance_score=score,
                        matched_fields=matched_fields,
                    )
                )

        # Sort by similarity score
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:limit]

    def get_templates_by_author(self, author: str) -> list[TemplateSearchResult]:
        """Get all templates by a specific author.

        Args:
            author: Author name

        Returns:
            list of templates by the author
        """
        template_index = self.storage.load_template_index()
        results = []

        for template_path, metadata in template_index.items():
            if metadata.author.lower() == author.lower():
                results.append(
                    TemplateSearchResult(
                        template_path=template_path,
                        metadata=metadata,
                        relevance_score=1.0,
                        matched_fields=["author"],
                    )
                )

        return results

    def get_recently_modified_templates(self, limit: int = 10) -> list[TemplateSearchResult]:
        """Get recently modified templates.

        Args:
            limit: Maximum results to return

        Returns:
            list of recently modified templates
        """
        template_index = self.storage.load_template_index()
        results = []

        for template_path, metadata in template_index.items():
            results.append(
                TemplateSearchResult(
                    template_path=template_path,
                    metadata=metadata,
                    relevance_score=metadata.modified_at.timestamp(),
                    matched_fields=["recent"],
                )
            )

        # Sort by modification time (most recent first)
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:limit]

    def get_popular_templates(self, limit: int = 10) -> list[TemplateSearchResult]:
        """Get popular templates based on usage.

        Note: This is a placeholder for future usage tracking integration.

        Args:
            limit: Maximum results to return

        Returns:
            list of popular templates
        """
        # For now, return active templates sorted by name
        # In the future, this could integrate with usage statistics
        return self.browse_templates(status=TemplateStatus.ACTIVE)[:limit]
