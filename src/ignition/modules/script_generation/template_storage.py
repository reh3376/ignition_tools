"""Template Storage Operations for Script Generation Module.

This module handles all file-based storage operations for templates including
reading, writing, and metadata management.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from .template_metadata import (
    TemplateCategory,
    TemplateMetadata,
    TemplateStatus,
)


class TemplateStorage:
    """Handles template file storage and metadata operations."""

    def __init__(
        self,
        templates_dir: str | Path = "templates",
        metadata_dir: str | Path = ".template_metadata",
    ) -> None:
        """Initialize template storage.

        Args:
            templates_dir: Path to templates directory
            metadata_dir: Path to metadata storage directory
        """
        self.templates_dir = Path(templates_dir)
        self.metadata_dir = Path(metadata_dir)
        self.logger = logging.getLogger(__name__)

        # Create directories if they don't exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        # Template index cache
        self._template_index: dict[str, TemplateMetadata] = {}
        self._index_loaded = False

    def load_template_index(self) -> dict[str, TemplateMetadata]:
        """Load template index from metadata files.

        Returns:
            Dictionary mapping template paths to metadata
        """
        if self._index_loaded:
            return self._template_index

        self._template_index.clear()

        # Load metadata for all templates
        for template_file in self.templates_dir.rglob("*.jinja2"):
            relative_path = str(template_file.relative_to(self.templates_dir))
            metadata = self.load_template_metadata(relative_path)
            if metadata:
                self._template_index[relative_path] = metadata

        self._index_loaded = True
        return self._template_index

    def load_template_metadata(self, template_path: str) -> TemplateMetadata | None:
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

    def save_template_metadata(
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

    def save_template_content(
        self, template_path: str, content: str, create_dirs: bool = True
    ) -> bool:
        """Save template content to file.

        Args:
            template_path: Relative path for template
            content: Template content
            create_dirs: Whether to create parent directories

        Returns:
            True if successful, False otherwise
        """
        full_path = self.templates_dir / template_path

        try:
            if create_dirs:
                full_path.parent.mkdir(parents=True, exist_ok=True)

            full_path.write_text(content, encoding="utf-8")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save template {template_path}: {e}")
            return False

    def delete_template(self, template_path: str, delete_metadata: bool = True) -> bool:
        """Delete a template file and optionally its metadata.

        Args:
            template_path: Relative path to template
            delete_metadata: Whether to delete metadata file

        Returns:
            True if successful, False otherwise
        """
        full_path = self.templates_dir / template_path

        try:
            if full_path.exists():
                full_path.unlink()

            if delete_metadata:
                metadata_file = self.metadata_dir / f"{template_path}.meta.json"
                if metadata_file.exists():
                    metadata_file.unlink()

            # Remove from index
            if template_path in self._template_index:
                del self._template_index[template_path]

            return True

        except Exception as e:
            self.logger.error(f"Failed to delete template {template_path}: {e}")
            return False

    def template_exists(self, template_path: str) -> bool:
        """Check if a template exists.

        Args:
            template_path: Relative path to template

        Returns:
            True if template exists, False otherwise
        """
        return (self.templates_dir / template_path).exists()

    def list_all_templates(self) -> list[str]:
        """List all template paths.

        Returns:
            list of relative template paths
        """
        templates = []
        for template_file in self.templates_dir.rglob("*.jinja2"):
            relative_path = str(template_file.relative_to(self.templates_dir))
            templates.append(relative_path)
        return sorted(templates)

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
        self.save_template_metadata(template_path, metadata)

        return metadata

    def _extract_tags_from_path(self, template_path: str) -> list[str]:
        """Extract tags from template path.

        Args:
            template_path: Template path

        Returns:
            list of extracted tags
        """
        tags = []
        parts = Path(template_path).parts

        for part in parts[:-1]:  # Exclude filename
            tags.append(part.lower())

        # Add tags from filename
        filename = Path(template_path).stem
        tags.extend(filename.lower().split("_"))

        return list(set(tags))
