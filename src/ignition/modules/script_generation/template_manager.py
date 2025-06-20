"""Template Management System for Ignition Script Generation Module.

This module provides comprehensive template management including browsing,
categorization, search, sharing, and version control capabilities.
"""

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ...graph.client import IgnitionGraphClient


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


class TemplateManager:
    """Comprehensive template management system."""

    def __init__(
        self,
        templates_dir: str | Path = "templates",
        metadata_dir: str | Path = ".template_metadata",
        graph_client: IgnitionGraphClient | None = None,
        enable_versioning: bool = True,
        enable_sharing: bool = True,
    ) -> None:
        """Initialize the template manager.

        Args:
            templates_dir: Path to templates directory
            metadata_dir: Path to metadata storage directory
            graph_client: Optional Neo4j graph client
            enable_versioning: Whether to enable version control
            enable_sharing: Whether to enable template sharing
        """
        self.templates_dir = Path(templates_dir)
        self.metadata_dir = Path(metadata_dir)
        self.graph_client = graph_client
        self.enable_versioning = enable_versioning
        self.enable_sharing = enable_sharing

        # Create directories if they don't exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        # Version control directory
        if enable_versioning:
            self.versions_dir = self.metadata_dir / "versions"
            self.versions_dir.mkdir(exist_ok=True)

        # Shared templates directory
        if enable_sharing:
            self.shared_dir = self.metadata_dir / "shared"
            self.shared_dir.mkdir(exist_ok=True)

        # Template index cache
        self._template_index: dict[str, TemplateMetadata] = {}
        self._index_loaded = False

        # Logger
        self.logger = logging.getLogger(__name__)

    def _load_template_index(self) -> None:
        """Load template index from metadata files."""
        if self._index_loaded:
            return

        self._template_index.clear()

        # Load metadata for all templates
        for template_file in self.templates_dir.rglob("*.jinja2"):
            relative_path = str(template_file.relative_to(self.templates_dir))
            metadata = self._load_template_metadata(relative_path)
            if metadata:
                self._template_index[relative_path] = metadata

        self._index_loaded = True

    def _load_template_metadata(self, template_path: str) -> TemplateMetadata | None:
        """Load metadata for a specific template.

        Args:
            template_path: Relative path to template

        Returns:
            Template metadata or None if not found
        """
        metadata_file = self.metadata_dir / f"{template_path}.meta.json"

        if metadata_file.exists():
            try:
                with open(metadata_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Convert timestamps
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                data["modified_at"] = datetime.fromisoformat(data["modified_at"])

                # Convert enums
                data["category"] = TemplateCategory(data["category"])
                data["status"] = TemplateStatus(data["status"])

                return TemplateMetadata(**data)

            except Exception as e:
                self.logger.warning(f"Failed to load metadata for {template_path}: {e}")

        # Create default metadata if none exists
        return self._create_default_metadata(template_path)

    def _create_default_metadata(self, template_path: str) -> TemplateMetadata:
        """Create default metadata for a template.

        Args:
            template_path: Relative path to template

        Returns:
            Default template metadata
        """
        # Infer category from path
        category = TemplateCategory.CUSTOM
        for cat in TemplateCategory:
            if cat.value in template_path.lower():
                category = cat
                break

        # Extract name from filename
        name = Path(template_path).stem.replace("_", " ").title()

        metadata = TemplateMetadata(
            name=name,
            category=category,
            description=f"Template for {name}",
            tags=self._extract_tags_from_path(template_path),
        )

        # Save metadata
        self._save_template_metadata(template_path, metadata)

        return metadata

    def _save_template_metadata(
        self, template_path: str, metadata: TemplateMetadata
    ) -> None:
        """Save template metadata to file.

        Args:
            template_path: Relative path to template
            metadata: Template metadata to save
        """
        metadata_file = self.metadata_dir / f"{template_path}.meta.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict for serialization
        data = {
            "name": metadata.name,
            "category": metadata.category.value,
            "description": metadata.description,
            "version": metadata.version,
            "author": metadata.author,
            "created_at": metadata.created_at.isoformat(),
            "modified_at": metadata.modified_at.isoformat(),
            "status": metadata.status.value,
            "tags": metadata.tags,
            "parameters": metadata.parameters,
            "examples": metadata.examples,
            "dependencies": metadata.dependencies,
            "compatible_versions": metadata.compatible_versions,
        }

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _extract_tags_from_path(self, template_path: str) -> list[str]:
        """Extract tags from template path.

        Args:
            template_path: Template path

        Returns:
            List of extracted tags
        """
        tags = []
        parts = Path(template_path).parts

        for part in parts[:-1]:  # Exclude filename
            tags.append(part.lower())

        # Add tags from filename
        filename = Path(template_path).stem
        tags.extend(filename.lower().split("_"))

        return list(set(tags))

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
        self._load_template_index()
        results = []

        for template_path, metadata in self._template_index.items():
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
            List of search results sorted by relevance
        """
        self._load_template_index()
        results = []
        query_lower = query.lower()

        for template_path, metadata in self._template_index.items():
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

    def get_template_content(self, template_path: str) -> str | None:
        """Get the content of a template.

        Args:
            template_path: Relative path to template

        Returns:
            Template content or None if not found
        """
        full_path = self.templates_dir / template_path

        if full_path.exists():
            try:
                return full_path.read_text(encoding="utf-8")
            except Exception as e:
                self.logger.error(f"Failed to read template {template_path}: {e}")

        return None

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
        full_path = self.templates_dir / template_path

        # Check if exists
        if full_path.exists() and not overwrite:
            self.logger.error(f"Template {template_path} already exists")
            return False

        try:
            # Create directories
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Save template content
            full_path.write_text(content, encoding="utf-8")

            # Save metadata
            self._save_template_metadata(template_path, metadata)

            # Update index
            self._template_index[template_path] = metadata

            # Create initial version if versioning enabled
            if self.enable_versioning:
                self._create_template_version(
                    template_path,
                    metadata.version,
                    metadata.author,
                    "Initial version",
                )

            # Update graph if available
            if self.graph_client:
                self._update_graph_template(template_path, metadata)

            return True

        except Exception as e:
            self.logger.error(f"Failed to create template {template_path}: {e}")
            return False

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
        full_path = self.templates_dir / template_path

        if not full_path.exists():
            self.logger.error(f"Template {template_path} not found")
            return False

        try:
            # Load current metadata
            metadata = self._load_template_metadata(template_path)
            if not metadata:
                return False

            # Update content if provided
            if content is not None:
                full_path.write_text(content, encoding="utf-8")

            # Update metadata if provided
            if metadata_updates:
                for key, value in metadata_updates.items():
                    if hasattr(metadata, key):
                        setattr(metadata, key, value)

                # Update modification time
                metadata.modified_at = datetime.now()

                # Increment version if content changed
                if content is not None:
                    version_parts = metadata.version.split(".")
                    version_parts[-1] = str(int(version_parts[-1]) + 1)
                    metadata.version = ".".join(version_parts)

            # Save updated metadata
            self._save_template_metadata(template_path, metadata)

            # Update index
            self._template_index[template_path] = metadata

            # Create version if versioning enabled and content changed
            if self.enable_versioning and content is not None:
                self._create_template_version(
                    template_path,
                    metadata.version,
                    metadata.author,
                    changelog,
                )

            # Update graph if available
            if self.graph_client:
                self._update_graph_template(template_path, metadata)

            return True

        except Exception as e:
            self.logger.error(f"Failed to update template {template_path}: {e}")
            return False

    def delete_template(self, template_path: str, archive: bool = True) -> bool:
        """Delete or archive a template.

        Args:
            template_path: Relative path to template
            archive: Whether to archive instead of delete

        Returns:
            True if successful, False otherwise
        """
        full_path = self.templates_dir / template_path

        if not full_path.exists():
            self.logger.error(f"Template {template_path} not found")
            return False

        try:
            if archive:
                # Archive by updating status
                metadata = self._load_template_metadata(template_path)
                if metadata:
                    metadata.status = TemplateStatus.ARCHIVED
                    metadata.modified_at = datetime.now()
                    self._save_template_metadata(template_path, metadata)
                    self._template_index[template_path] = metadata
            else:
                # Actually delete the template
                full_path.unlink()

                # Delete metadata
                metadata_file = self.metadata_dir / f"{template_path}.meta.json"
                if metadata_file.exists():
                    metadata_file.unlink()

                # Remove from index
                self._template_index.pop(template_path, None)

                # Delete versions if versioning enabled
                if self.enable_versioning:
                    version_dir = self.versions_dir / template_path
                    if version_dir.exists():
                        shutil.rmtree(version_dir)

            return True

        except Exception as e:
            self.logger.error(f"Failed to delete template {template_path}: {e}")
            return False

    def share_template(
        self,
        template_path: str,
        share_name: str | None = None,
        include_metadata: bool = True,
    ) -> str | None:
        """Share a template for export.

        Args:
            template_path: Relative path to template
            share_name: Optional custom name for shared template
            include_metadata: Whether to include metadata

        Returns:
            Path to shared template bundle or None if failed
        """
        if not self.enable_sharing:
            self.logger.error("Template sharing is not enabled")
            return None

        full_path = self.templates_dir / template_path

        if not full_path.exists():
            self.logger.error(f"Template {template_path} not found")
            return None

        try:
            # Create share bundle name
            if not share_name:
                share_name = Path(template_path).stem

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bundle_name = f"{share_name}_{timestamp}.bundle"
            bundle_path = self.shared_dir / bundle_name

            # Create bundle directory
            bundle_path.mkdir(parents=True)

            # Copy template
            template_dest = bundle_path / "template.jinja2"
            shutil.copy2(full_path, template_dest)

            # Copy metadata if requested
            if include_metadata:
                metadata = self._load_template_metadata(template_path)
                if metadata:
                    metadata_dest = bundle_path / "metadata.json"
                    self._save_template_metadata("metadata.json", metadata)
                    shutil.move(
                        self.metadata_dir / "metadata.json.meta.json",
                        metadata_dest,
                    )

            # Create bundle info
            bundle_info = {
                "template_path": template_path,
                "share_name": share_name,
                "created_at": datetime.now().isoformat(),
                "includes_metadata": include_metadata,
            }

            with open(bundle_path / "bundle_info.json", "w", encoding="utf-8") as f:
                json.dump(bundle_info, f, indent=2)

            return str(bundle_path)

        except Exception as e:
            self.logger.error(f"Failed to share template {template_path}: {e}")
            return None

    def import_shared_template(
        self,
        bundle_path: str | Path,
        target_path: str | None = None,
        overwrite: bool = False,
    ) -> bool:
        """Import a shared template bundle.

        Args:
            bundle_path: Path to template bundle
            target_path: Optional custom target path
            overwrite: Whether to overwrite existing template

        Returns:
            True if successful, False otherwise
        """
        bundle_path = Path(bundle_path)

        if not bundle_path.exists():
            self.logger.error(f"Bundle {bundle_path} not found")
            return False

        try:
            # Load bundle info
            bundle_info_file = bundle_path / "bundle_info.json"
            if bundle_info_file.exists():
                with open(bundle_info_file, encoding="utf-8") as f:
                    bundle_info = json.load(f)
            else:
                bundle_info = {}

            # Determine target path
            if not target_path:
                target_path = bundle_info.get(
                    "template_path", "imported/template.jinja2"
                )

            # Load template content
            template_file = bundle_path / "template.jinja2"
            if not template_file.exists():
                self.logger.error("Template file not found in bundle")
                return False

            content = template_file.read_text(encoding="utf-8")

            # Load metadata if available
            metadata_file = bundle_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, encoding="utf-8") as f:
                    metadata_data = json.load(f)

                # Convert to TemplateMetadata
                metadata_data["created_at"] = datetime.fromisoformat(
                    metadata_data["created_at"]
                )
                metadata_data["modified_at"] = datetime.fromisoformat(
                    metadata_data["modified_at"]
                )
                metadata_data["category"] = TemplateCategory(metadata_data["category"])
                metadata_data["status"] = TemplateStatus(metadata_data["status"])

                metadata = TemplateMetadata(**metadata_data)
            else:
                # Create default metadata
                metadata = self._create_default_metadata(target_path)

            # Import template
            return self.create_template(target_path, content, metadata, overwrite)

        except Exception as e:
            self.logger.error(f"Failed to import template bundle {bundle_path}: {e}")
            return False

    def _create_template_version(
        self,
        template_path: str,
        version: str,
        author: str,
        changelog: str,
    ) -> None:
        """Create a version snapshot of a template.

        Args:
            template_path: Relative path to template
            version: Version string
            author: Version author
            changelog: Version changelog
        """
        if not self.enable_versioning:
            return

        try:
            # Create version directory
            version_dir = self.versions_dir / template_path
            version_dir.mkdir(parents=True, exist_ok=True)

            # Copy template to version
            source_path = self.templates_dir / template_path
            version_file = version_dir / f"v{version}.jinja2"
            shutil.copy2(source_path, version_file)

            # Calculate file hash
            import hashlib

            file_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()

            # Create version info
            version_info = TemplateVersion(
                version=version,
                created_at=datetime.now(),
                author=author,
                changelog=changelog,
                file_hash=file_hash,
                is_current=True,
            )

            # Save version info
            version_info_file = version_dir / f"v{version}.info.json"
            with open(version_info_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "version": version_info.version,
                        "created_at": version_info.created_at.isoformat(),
                        "author": version_info.author,
                        "changelog": version_info.changelog,
                        "file_hash": version_info.file_hash,
                        "is_current": version_info.is_current,
                    },
                    f,
                    indent=2,
                )

            # Update previous versions to not be current
            for info_file in version_dir.glob("*.info.json"):
                if info_file != version_info_file:
                    with open(info_file, encoding="utf-8") as f:
                        info = json.load(f)
                    info["is_current"] = False
                    with open(info_file, "w", encoding="utf-8") as f:
                        json.dump(info, f, indent=2)

        except Exception as e:
            self.logger.warning(f"Failed to create version for {template_path}: {e}")

    def get_template_versions(self, template_path: str) -> list[TemplateVersion]:
        """Get all versions of a template.

        Args:
            template_path: Relative path to template

        Returns:
            List of template versions sorted by creation date
        """
        versions = []

        if not self.enable_versioning:
            return versions

        version_dir = self.versions_dir / template_path

        if not version_dir.exists():
            return versions

        try:
            for info_file in version_dir.glob("*.info.json"):
                with open(info_file, encoding="utf-8") as f:
                    info_data = json.load(f)

                versions.append(
                    TemplateVersion(
                        version=info_data["version"],
                        created_at=datetime.fromisoformat(info_data["created_at"]),
                        author=info_data["author"],
                        changelog=info_data["changelog"],
                        file_hash=info_data["file_hash"],
                        is_current=info_data["is_current"],
                    )
                )

            # Sort by creation date
            versions.sort(key=lambda v: v.created_at, reverse=True)

        except Exception as e:
            self.logger.warning(f"Failed to get versions for {template_path}: {e}")

        return versions

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
        if not self.enable_versioning:
            self.logger.error("Template versioning is not enabled")
            return False

        version_file = self.versions_dir / template_path / f"v{version}.jinja2"

        if not version_file.exists():
            self.logger.error(f"Version {version} not found for {template_path}")
            return False

        try:
            # Create backup of current version if requested
            if create_backup:
                metadata = self._load_template_metadata(template_path)
                if metadata:
                    self._create_template_version(
                        template_path,
                        metadata.version + ".backup",
                        metadata.author,
                        f"Backup before restoring to v{version}",
                    )

            # Restore version
            target_path = self.templates_dir / template_path
            shutil.copy2(version_file, target_path)

            # Update metadata
            metadata = self._load_template_metadata(template_path)
            if metadata:
                metadata.version = version
                metadata.modified_at = datetime.now()
                self._save_template_metadata(template_path, metadata)
                self._template_index[template_path] = metadata

            return True

        except Exception as e:
            self.logger.error(
                f"Failed to restore version {version} of {template_path}: {e}"
            )
            return False

    def _update_graph_template(
        self, template_path: str, metadata: TemplateMetadata
    ) -> None:
        """Update template information in Neo4j graph.

        Args:
            template_path: Template path
            metadata: Template metadata
        """
        if not self.graph_client:
            return

        try:
            query = """
            MERGE (t:Template {path: $path})
            SET t.name = $name,
                t.category = $category,
                t.description = $description,
                t.version = $version,
                t.author = $author,
                t.status = $status,
                t.tags = $tags,
                t.modified_at = datetime($modified_at)
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
            self.logger.warning(
                f"Failed to update graph for template {template_path}: {e}"
            )

    def get_template_statistics(self) -> dict[str, Any]:
        """Get statistics about templates.

        Returns:
            Dictionary with template statistics
        """
        self._load_template_index()

        stats = {
            "total_templates": len(self._template_index),
            "by_category": {},
            "by_status": {},
            "most_used_tags": {},
            "authors": set(),
            "average_parameters": 0,
        }

        tag_counts = {}
        total_params = 0

        for metadata in self._template_index.values():
            # Count by category
            cat = metadata.category.value
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

            # Count by status
            status = metadata.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Count tags
            for tag in metadata.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Collect authors
            stats["authors"].add(metadata.author)

            # Count parameters
            total_params += len(metadata.parameters)

        # Calculate averages
        if stats["total_templates"] > 0:
            stats["average_parameters"] = total_params / stats["total_templates"]

        # Get top tags
        stats["most_used_tags"] = dict(
            sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )

        # Convert set to list for JSON serialization
        stats["authors"] = list(stats["authors"])

        return stats
