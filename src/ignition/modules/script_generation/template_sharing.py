"""Template Sharing and Import/Export for Script Generation Module.

This module provides functionality for sharing templates including
bundling, exporting, and importing template packages.
"""

import json
import logging
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from .template_metadata import TemplateMetadata
from .template_storage import TemplateStorage


class TemplateSharingManager:
    """Manages template sharing, import, and export operations."""

    def __init__(
        self,
        storage: TemplateStorage,
        shared_dir: str | Path = ".template_metadata/shared",
    ) -> None:
        """Initialize sharing manager.

        Args:
            storage: Template storage instance
            shared_dir: Directory for shared templates
        """
        self.storage = storage
        self.shared_dir = Path(shared_dir)
        self.shared_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def export_template(
        self,
        template_path: str,
        output_path: str | Path,
        include_metadata: bool = True,
        include_versions: bool = False,
    ) -> bool:
        """Export a template to a shareable bundle.

        Args:
            template_path: Relative path to template
            output_path: Path for output bundle
            include_metadata: Whether to include metadata
            include_versions: Whether to include version history

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)

            # Create temporary directory for bundle
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                bundle_dir = temp_path / "template_bundle"
                bundle_dir.mkdir()

                # Copy template file
                template_content = self.storage.get_template_content(template_path)
                if template_content is None:
                    self.logger.error(f"Template {template_path} not found")
                    return False

                template_file = bundle_dir / "template.jinja2"
                template_file.write_text(template_content, encoding="utf-8")

                # Include metadata if requested
                if include_metadata:
                    metadata = self.storage.load_template_metadata(template_path)
                    if metadata:
                        metadata_file = bundle_dir / "metadata.json"
                        self._save_metadata_to_file(metadata_file, metadata)

                # Create bundle info
                bundle_info = {
                    "template_path": template_path,
                    "exported_at": datetime.now().isoformat(),
                    "bundle_version": "1.0",
                    "includes_metadata": include_metadata,
                    "includes_versions": include_versions,
                }

                info_file = bundle_dir / "bundle_info.json"
                with open(info_file, "w", encoding="utf-8") as f:
                    json.dump(bundle_info, f, indent=2)

                # Create zip archive
                with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in bundle_dir.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(bundle_dir)
                            zipf.write(file_path, arcname)

            self.logger.info(f"Exported template to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export template: {e}")
            return False

    def import_template(
        self,
        bundle_path: str | Path,
        target_path: str | None = None,
        overwrite: bool = False,
    ) -> str | None:
        """Import a template from a bundle.

        Args:
            bundle_path: Path to template bundle
            target_path: Optional custom path for imported template
            overwrite: Whether to overwrite existing template

        Returns:
            Path of imported template or None if failed
        """
        try:
            bundle_path = Path(bundle_path)

            if not bundle_path.exists():
                self.logger.error(f"Bundle {bundle_path} not found")
                return None

            # Extract bundle
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract zip
                with zipfile.ZipFile(bundle_path, "r") as zipf:
                    zipf.extractall(temp_path)

                # Read bundle info
                info_file = temp_path / "bundle_info.json"
                if not info_file.exists():
                    self.logger.error("Invalid bundle: missing bundle_info.json")
                    return None

                with open(info_file, encoding="utf-8") as f:
                    bundle_info = json.load(f)

                # Determine target path
                if target_path is None:
                    target_path = bundle_info["template_path"]

                # Ensure target_path is not None
                if not target_path:
                    self.logger.error("Target path cannot be determined")
                    return None

                # Check if template exists
                if self.storage.template_exists(target_path) and not overwrite:
                    self.logger.error(f"Template {target_path} already exists")
                    return None

                # Import template content
                template_file = temp_path / "template.jinja2"
                if not template_file.exists():
                    self.logger.error("Invalid bundle: missing template file")
                    return None

                content = template_file.read_text(encoding="utf-8")
                if not self.storage.save_template_content(target_path, content):
                    return None

                # Import metadata if available
                if bundle_info.get("includes_metadata"):
                    metadata_file = temp_path / "metadata.json"
                    if metadata_file.exists():
                        metadata = self._load_metadata_from_file(metadata_file)
                        if metadata:
                            self.storage.save_template_metadata(target_path, metadata)

            self.logger.info(f"Imported template to {target_path}")
            return target_path

        except Exception as e:
            self.logger.error(f"Failed to import template: {e}")
            return None

    def create_template_package(
        self,
        template_paths: list[str],
        package_name: str,
        output_dir: str | Path = ".",
    ) -> str | None:
        """Create a package containing multiple templates.

        Args:
            template_paths: list of template paths to include
            package_name: Name for the package
            output_dir: Directory for output package

        Returns:
            Path to created package or None if failed
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create package file
            package_file = output_dir / f"{package_name}.tpkg"

            # Create temporary directory for package
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                package_dir = temp_path / "package"
                package_dir.mkdir()

                # Create package info
                package_info = {
                    "name": package_name,
                    "created_at": datetime.now().isoformat(),
                    "template_count": len(template_paths),
                    "templates": [],
                }

                # Export each template
                templates_dir = package_dir / "templates"
                templates_dir.mkdir()

                for i, template_path in enumerate(template_paths):
                    template_bundle = templates_dir / f"template_{i}.zip"
                    if self.export_template(template_path, template_bundle, include_metadata=True):
                        package_info["templates"].append(
                            {
                                "index": i,
                                "path": template_path,
                                "bundle": f"template_{i}.zip",
                            }
                        )

                # Save package info
                info_file = package_dir / "package_info.json"
                with open(info_file, "w", encoding="utf-8") as f:
                    json.dump(package_info, f, indent=2)

                # Create package archive
                with zipfile.ZipFile(package_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in package_dir.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(package_dir)
                            zipf.write(file_path, arcname)

            self.logger.info(f"Created template package: {package_file}")
            return str(package_file)

        except Exception as e:
            self.logger.error(f"Failed to create template package: {e}")
            return None

    def list_shared_templates(self) -> list[dict[str, Any]]:
        """List all shared templates.

        Returns:
            list of shared template information
        """
        shared_templates = []

        for bundle_file in self.shared_dir.glob("*.zip"):
            try:
                # Read bundle info without extracting
                with zipfile.ZipFile(bundle_file, "r") as zipf:
                    if "bundle_info.json" in zipf.namelist():
                        with zipf.open("bundle_info.json") as f:
                            bundle_info = json.load(f)
                            shared_templates.append(
                                {
                                    "file": bundle_file.name,
                                    "template_path": bundle_info["template_path"],
                                    "exported_at": bundle_info["exported_at"],
                                    "size": bundle_file.stat().st_size,
                                }
                            )
            except Exception as e:
                self.logger.warning(f"Failed to read bundle {bundle_file}: {e}")

        return shared_templates

    def _save_metadata_to_file(self, file_path: Path, metadata: TemplateMetadata) -> None:
        """Save metadata to a JSON file.

        Args:
            file_path: Path to save metadata
            metadata: Template metadata
        """
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

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_metadata_from_file(self, file_path: Path) -> TemplateMetadata | None:
        """Load metadata from a JSON file.

        Args:
            file_path: Path to metadata file

        Returns:
            Template metadata or None if failed
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Import necessary enums
            from .template_metadata import TemplateCategory, TemplateStatus

            # Convert timestamps and enums
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            data["modified_at"] = datetime.fromisoformat(data["modified_at"])
            data["category"] = TemplateCategory(data["category"])
            data["status"] = TemplateStatus(data["status"])

            return TemplateMetadata(**data)

        except Exception as e:
            self.logger.error(f"Failed to load metadata from file: {e}")
            return None
