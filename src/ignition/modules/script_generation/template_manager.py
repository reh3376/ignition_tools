"""Template Management System for Ignition Script Generation Module.

This module provides comprehensive template management using a composition
pattern to delegate responsibilities to specialized components.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ...graph.client import IgnitionGraphClient
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


class TemplateManager:
    """Comprehensive template management system using composition pattern.

    This class delegates responsibilities to specialized components:
    - TemplateStorage: File operations and metadata persistence
    - TemplateSearchEngine: Search and browsing functionality
    - TemplateVersionManager: Version control operations
    - TemplateSharingManager: Import/export functionality
    """

    def __init__(
        self,
        templates_dir: str | Path = "templates",
        metadata_dir: str | Path = ".template_metadata",
        graph_client: IgnitionGraphClient | None = None,
        enable_versioning: bool = True,
        enable_sharing: bool = True,
    ) -> None:
        """Initialize the template manager with specialized components.

        Args:
            templates_dir: Path to templates directory
            metadata_dir: Path to metadata storage directory
            graph_client: Optional Neo4j graph client
            enable_versioning: Whether to enable version control
            enable_sharing: Whether to enable template sharing
        """
        self.graph_client = graph_client
        self.logger = logging.getLogger(__name__)

        # Initialize core storage component
        self.storage = TemplateStorage(templates_dir, metadata_dir)

        # Initialize search engine
        self.search_engine = TemplateSearchEngine(self.storage)

        # Initialize version manager if enabled
        self.version_manager = None
        if enable_versioning:
            self.version_manager = TemplateVersionManager(
                self.storage, Path(metadata_dir) / "versions"
            )

        # Initialize sharing manager if enabled
        self.sharing_manager = None
        if enable_sharing:
            self.sharing_manager = TemplateSharingManager(
                self.storage, Path(metadata_dir) / "shared"
            )

    # Storage delegation methods
    def get_template_content(self, template_path: str) -> str | None:
        """Get the content of a template.

        Args:
            template_path: Relative path to template

        Returns:
            Template content or None if not found
        """
        return self.storage.get_template_content(template_path)

    def create_template(
        self,
        template_path: str,
        content: str,
        metadata: TemplateMetadata,
        overwrite: bool = False,
    ) -> bool:
        """Create a new template.

        Args:
            template_path: Relative path for template
            content: Template content
            metadata: Template metadata
            overwrite: Whether to overwrite existing template

        Returns:
            True if successful, False otherwise
        """
        # Check if exists
        if self.storage.template_exists(template_path) and not overwrite:
            self.logger.error(f"Template {template_path} already exists")
            return False

        # Save template and metadata
        if not self.storage.save_template_content(template_path, content):
            return False

        self.storage.save_template_metadata(template_path, metadata)

        # Create initial version if versioning enabled
        if self.version_manager:
            self.version_manager.create_version(
                template_path,
                metadata.version,
                metadata.author,
                "Initial version",
            )

        # Update graph if available
        if self.graph_client:
            self._update_graph_template(template_path, metadata)

        return True

    def update_template(
        self,
        template_path: str,
        content: str | None = None,
        metadata_updates: dict[str, Any] | None = None,
        changelog: str = "Updated template",
    ) -> bool:
        """Update an existing template.

        Args:
            template_path: Relative path to template
            content: New template content (optional)
            metadata_updates: Metadata fields to update (optional)
            changelog: Version changelog message

        Returns:
            True if successful, False otherwise
        """
        if not self.storage.template_exists(template_path):
            self.logger.error(f"Template {template_path} not found")
            return False

        # Load current metadata
        metadata = self.storage.load_template_metadata(template_path)
        if not metadata:
            return False

        # Update content if provided
        if content is not None:
            if not self.storage.save_template_content(template_path, content):
                return False

        # Update metadata if provided
        if metadata_updates:
            for key, value in metadata_updates.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)

            # Update modification time
            metadata.modified_at = datetime.now()

            # Increment version if needed
            if "version" not in metadata_updates and content is not None:
                # Simple version increment (you might want more sophisticated logic)
                parts = metadata.version.split(".")
                parts[-1] = str(int(parts[-1]) + 1)
                metadata.version = ".".join(parts)

            self.storage.save_template_metadata(template_path, metadata)

        # Create version if versioning enabled and content changed
        if self.version_manager and content is not None:
            self.version_manager.create_version(
                template_path,
                metadata.version,
                (
                    metadata_updates.get("author", "Unknown")
                    if metadata_updates
                    else "Unknown"
                ),
                changelog,
            )

        # Update graph if available
        if self.graph_client:
            self._update_graph_template(template_path, metadata)

        return True

    def delete_template(self, template_path: str, archive: bool = True) -> bool:
        """Delete or archive a template.

        Args:
            template_path: Relative path to template
            archive: Whether to archive instead of delete

        Returns:
            True if successful, False otherwise
        """
        if archive:
            # Archive by changing status
            metadata = self.storage.load_template_metadata(template_path)
            if metadata:
                metadata.status = TemplateStatus.ARCHIVED
                metadata.modified_at = datetime.now()
                self.storage.save_template_metadata(template_path, metadata)
                return True
            return False
        else:
            # Actually delete the template
            return self.storage.delete_template(template_path)

    # Search delegation methods
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
            List of matching templates
        """
        return self.search_engine.browse_templates(category, status, tags)

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
            List of search results sorted by relevance
        """
        return self.search_engine.search_templates(query, category, limit)

    # Version control delegation methods
    def get_template_versions(self, template_path: str) -> list[TemplateVersion]:
        """Get all versions of a template.

        Args:
            template_path: Relative path to template

        Returns:
            List of template versions
        """
        if self.version_manager:
            return self.version_manager.get_versions(template_path)
        return []

    def restore_template_version(
        self,
        template_path: str,
        version: str,
        create_backup: bool = True,
    ) -> bool:
        """Restore a template to a specific version.

        Args:
            template_path: Relative path to template
            version: Version to restore
            create_backup: Whether to backup current version

        Returns:
            True if successful, False otherwise
        """
        if self.version_manager:
            return self.version_manager.restore_version(
                template_path, version, create_backup
            )
        return False

    # Sharing delegation methods
    def share_template(
        self,
        template_path: str,
        output_path: str | Path,
        include_metadata: bool = True,
    ) -> bool:
        """Export a template for sharing.

        Args:
            template_path: Relative path to template
            output_path: Path for output bundle
            include_metadata: Whether to include metadata

        Returns:
            True if successful, False otherwise
        """
        if self.sharing_manager:
            return self.sharing_manager.export_template(
                template_path, output_path, include_metadata
            )
        return False

    def import_shared_template(
        self,
        bundle_path: str | Path,
        target_path: str | None = None,
        overwrite: bool = False,
    ) -> str | None:
        """Import a shared template bundle.

        Args:
            bundle_path: Path to template bundle
            target_path: Optional custom path for imported template
            overwrite: Whether to overwrite existing template

        Returns:
            Path of imported template or None if failed
        """
        if self.sharing_manager:
            return self.sharing_manager.import_template(
                bundle_path, target_path, overwrite
            )
        return None

    # Statistics and reporting
    def get_template_statistics(self) -> dict[str, Any]:
        """Get comprehensive template statistics.

        Returns:
            Dictionary containing template statistics
        """
        template_index = self.storage.load_template_index()

        # Basic counts
        total_templates = len(template_index)

        # Count by category
        category_counts = {}
        for metadata in template_index.values():
            category = metadata.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        # Count by status
        status_counts = {}
        for metadata in template_index.values():
            status = metadata.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Author statistics
        author_counts = {}
        for metadata in template_index.values():
            author = metadata.author
            author_counts[author] = author_counts.get(author, 0) + 1

        # Recent activity
        recent_templates = sorted(
            template_index.items(), key=lambda x: x[1].modified_at, reverse=True
        )[:10]

        return {
            "total_templates": total_templates,
            "category_distribution": category_counts,
            "status_distribution": status_counts,
            "author_distribution": author_counts,
            "recent_activity": [
                {
                    "path": path,
                    "name": metadata.name,
                    "modified": metadata.modified_at.isoformat(),
                }
                for path, metadata in recent_templates
            ],
            "versioning_enabled": self.version_manager is not None,
            "sharing_enabled": self.sharing_manager is not None,
        }

    def _update_graph_template(
        self, template_path: str, metadata: TemplateMetadata
    ) -> None:
        """Update template information in Neo4j graph.

        Args:
            template_path: Relative path to template
            metadata: Template metadata
        """
        if not self.graph_client or not self.graph_client.is_connected():
            return

        try:
            # Create or update template node
            query = """
            MERGE (t:Template {path: $path})
            SET t.name = $name,
                t.category = $category,
                t.description = $description,
                t.version = $version,
                t.author = $author,
                t.status = $status,
                t.tags = $tags,
                t.modified_at = $modified_at
            RETURN t
            """

            self.graph_client.execute_query(
                query,
                {
                    "path": template_path,
                    "name": metadata.name,
                    "category": metadata.category.value,
                    "description": metadata.description,
                    "version": metadata.version,
                    "author": metadata.author,
                    "status": metadata.status.value,
                    "tags": metadata.tags,
                    "modified_at": metadata.modified_at.isoformat(),
                },
            )

        except Exception as e:
            self.logger.warning(f"Failed to update graph for {template_path}: {e}")

    # Convenience methods
    def list_all_templates(self) -> list[str]:
        """List all template paths.

        Returns:
            List of relative template paths
        """
        return self.storage.list_all_templates()

    def get_template_metadata(self, template_path: str) -> TemplateMetadata | None:
        """Get metadata for a specific template.

        Args:
            template_path: Relative path to template

        Returns:
            Template metadata or None if not found
        """
        return self.storage.load_template_metadata(template_path)
