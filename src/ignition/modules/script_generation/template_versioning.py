"""Template Version Control for Script Generation Module.

This module provides version control capabilities for templates including
version tracking, history, and restoration.
"""

import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .template_metadata import TemplateVersion
from .template_storage import TemplateStorage


class TemplateVersionManager:
    """Manages template versioning and history."""

    def __init__(
        self,
        storage: TemplateStorage,
        versions_dir: str | Path = ".template_metadata/versions",
    ) -> None:
        """Initialize version manager.

        Args:
            storage: Template storage instance
            versions_dir: Directory for version storage
        """
        self.storage = storage
        self.versions_dir = Path(versions_dir)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def create_version(
        self,
        template_path: str,
        version: str,
        author: str,
        changelog: str,
    ) -> bool:
        """Create a new version of a template.

        Args:
            template_path: Relative path to template
            version: Version string (e.g., "1.2.0")
            author: Author of the version
            changelog: Description of changes

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current template content
            content = self.storage.get_template_content(template_path)
            if content is None:
                self.logger.error(f"Template {template_path} not found")
                return False

            # Calculate file hash
            file_hash = hashlib.sha256(content.encode()).hexdigest()

            # Create version directory
            version_dir = self.versions_dir / template_path / version
            version_dir.mkdir(parents=True, exist_ok=True)

            # Save template content
            version_file = version_dir / "template.jinja2"
            version_file.write_text(content, encoding="utf-8")

            # Save version metadata
            version_info = TemplateVersion(
                version=version,
                created_at=datetime.now(),
                author=author,
                changelog=changelog,
                file_hash=file_hash,
                is_current=True,
            )

            metadata_file = version_dir / "version.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
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

            # Update current version marker
            self._update_current_version(template_path, version)

            # Update template metadata with new version
            metadata = self.storage.load_template_metadata(template_path)
            if metadata:
                metadata.version = version
                metadata.modified_at = datetime.now()
                self.storage.save_template_metadata(template_path, metadata)

            self.logger.info(f"Created version {version} for {template_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create version: {e}")
            return False

    def get_versions(self, template_path: str) -> list[TemplateVersion]:
        """Get all versions of a template.

        Args:
            template_path: Relative path to template

        Returns:
            List of template versions sorted by creation date
        """
        versions = []
        template_version_dir = self.versions_dir / template_path

        if not template_version_dir.exists():
            return versions

        current_version = self._get_current_version(template_path)

        for version_dir in template_version_dir.iterdir():
            if version_dir.is_dir():
                metadata_file = version_dir / "version.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, encoding="utf-8") as f:
                            data = json.load(f)

                        version_info = TemplateVersion(
                            version=data["version"],
                            created_at=datetime.fromisoformat(data["created_at"]),
                            author=data["author"],
                            changelog=data["changelog"],
                            file_hash=data["file_hash"],
                            is_current=data["version"] == current_version,
                        )
                        versions.append(version_info)

                    except Exception as e:
                        self.logger.warning(
                            f"Failed to load version {version_dir.name}: {e}"
                        )

        # Sort by creation date (newest first)
        versions.sort(key=lambda v: v.created_at, reverse=True)

        return versions

    def get_version_content(self, template_path: str, version: str) -> str | None:
        """Get the content of a specific template version.

        Args:
            template_path: Relative path to template
            version: Version to retrieve

        Returns:
            Template content or None if not found
        """
        version_file = self.versions_dir / template_path / version / "template.jinja2"

        if version_file.exists():
            try:
                return version_file.read_text(encoding="utf-8")
            except Exception as e:
                self.logger.error(f"Failed to read version {version}: {e}")

        return None

    def restore_version(
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
        try:
            # Get version content
            version_content = self.get_version_content(template_path, version)
            if version_content is None:
                self.logger.error(f"Version {version} not found")
                return False

            # Create backup of current version if requested
            if create_backup:
                current_content = self.storage.get_template_content(template_path)
                if current_content:
                    metadata = self.storage.load_template_metadata(template_path)
                    if metadata:
                        backup_version = f"{metadata.version}-backup-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        self.create_version(
                            template_path,
                            backup_version,
                            "System",
                            f"Backup before restoring to version {version}",
                        )

            # Restore the version
            if not self.storage.save_template_content(template_path, version_content):
                return False

            # Update current version marker
            self._update_current_version(template_path, version)

            # Update metadata
            metadata = self.storage.load_template_metadata(template_path)
            if metadata:
                metadata.version = version
                metadata.modified_at = datetime.now()
                self.storage.save_template_metadata(template_path, metadata)

            self.logger.info(f"Restored {template_path} to version {version}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to restore version: {e}")
            return False

    def compare_versions(
        self, template_path: str, version1: str, version2: str
    ) -> dict[str, Any] | None:
        """Compare two versions of a template.

        Args:
            template_path: Relative path to template
            version1: First version
            version2: Second version

        Returns:
            Comparison results or None if versions not found
        """
        content1 = self.get_version_content(template_path, version1)
        content2 = self.get_version_content(template_path, version2)

        if content1 is None or content2 is None:
            return None

        # Simple comparison - in a real implementation, you might use difflib
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()

        return {
            "version1": version1,
            "version2": version2,
            "lines_added": len(lines2) - len(lines1),
            "content_changed": content1 != content2,
            "size_difference": len(content2) - len(content1),
        }

    def cleanup_old_versions(self, template_path: str, keep_count: int = 10) -> int:
        """Clean up old versions, keeping only the most recent ones.

        Args:
            template_path: Relative path to template
            keep_count: Number of versions to keep

        Returns:
            Number of versions deleted
        """
        versions = self.get_versions(template_path)

        if len(versions) <= keep_count:
            return 0

        # Sort by date (oldest first for deletion)
        versions.sort(key=lambda v: v.created_at)

        # Delete old versions
        deleted = 0
        for version in versions[:-keep_count]:
            if not version.is_current:  # Never delete current version
                version_dir = self.versions_dir / template_path / version.version
                try:
                    shutil.rmtree(version_dir)
                    deleted += 1
                except Exception as e:
                    self.logger.error(
                        f"Failed to delete version {version.version}: {e}"
                    )

        return deleted

    def _get_current_version(self, template_path: str) -> str | None:
        """Get the current version of a template.

        Args:
            template_path: Relative path to template

        Returns:
            Current version or None
        """
        current_file = self.versions_dir / template_path / "current.txt"
        if current_file.exists():
            try:
                return current_file.read_text().strip()
            except Exception:
                pass

        # Fallback to metadata
        metadata = self.storage.load_template_metadata(template_path)
        return metadata.version if metadata else None

    def _update_current_version(self, template_path: str, version: str) -> None:
        """Update the current version marker.

        Args:
            template_path: Relative path to template
            version: New current version
        """
        current_file = self.versions_dir / template_path / "current.txt"
        current_file.parent.mkdir(parents=True, exist_ok=True)
        current_file.write_text(version)
