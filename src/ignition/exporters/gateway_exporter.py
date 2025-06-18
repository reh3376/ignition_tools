"""Gateway Resource Exporter for Ignition projects and resources.

Provides export functionality for Ignition gateway resources including
projects, tags, databases, device connections, and security configurations.
Supports multiple export formats and includes dependency analysis.
"""

import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.ignition.gateway.client import IgnitionGatewayClient
from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.schema import GraphNode, NodeType

logger = logging.getLogger(__name__)


class GatewayResourceExporter:
    """Exports Ignition gateway resources with intelligent dependency analysis."""

    def __init__(
        self,
        gateway_client: IgnitionGatewayClient,
        graph_client: IgnitionGraphClient | None = None,
    ):
        """Initialize the exporter.

        Args:
            gateway_client: Connected Ignition gateway client
            graph_client: Optional graph client for dependency tracking
        """
        self.gateway_client = gateway_client
        self.graph_client = graph_client
        self.export_id = str(uuid4())
        self.export_metadata = {
            "export_id": self.export_id,
            "created_at": datetime.now().isoformat(),
            "gateway_host": gateway_client.config.host,
            "exporter_version": "1.0.0",
        }

    def export_gateway_backup(
        self, output_path: Path, export_profile: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a full gateway backup (.gwbk equivalent).

        Args:
            output_path: Path for the backup file
            export_profile: Optional export configuration profile

        Returns:
            Export result with metadata and statistics
        """
        logger.info(f"Starting gateway backup export to {output_path}")

        try:
            # Create export profile if not provided
            if not export_profile:
                export_profile = self._create_default_backup_profile()

            # Gather all gateway resources
            resources = self._gather_gateway_resources(export_profile)

            # Analyze dependencies
            dependencies = self._analyze_dependencies(resources)

            # Create backup package
            backup_data = {
                "metadata": self.export_metadata,
                "export_profile": export_profile,
                "resources": resources,
                "dependencies": dependencies,
                "schema_version": "1.0.0",
            }

            # Save backup
            if output_path.suffix.lower() == ".gwbk":
                result = self._save_gwbk_format(backup_data, output_path)
            elif output_path.suffix.lower() == ".zip":
                result = self._save_zip_format(backup_data, output_path)
            else:
                result = self._save_json_format(backup_data, output_path)

            # Track export in graph database
            if self.graph_client:
                self._track_export_in_graph(export_profile, result)

            logger.info("Gateway backup export completed successfully")
            return result

        except Exception as e:
            logger.error(f"Gateway backup export failed: {e}")
            raise

    def export_project(
        self,
        project_name: str,
        output_path: Path,
        export_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Export a specific Ignition project (.proj equivalent).

        Args:
            project_name: Name of the project to export
            output_path: Path for the exported project
            export_options: Optional export configuration

        Returns:
            Export result with metadata and statistics
        """
        logger.info(f"Starting project export for '{project_name}' to {output_path}")

        try:
            # Create export options if not provided
            if not export_options:
                export_options = self._create_default_project_options()

            # Gather project resources
            project_resources = self._gather_project_resources(
                project_name, export_options
            )

            # Analyze project dependencies
            dependencies = self._analyze_project_dependencies(
                project_name, project_resources
            )

            # Create project package
            project_data = {
                "metadata": {
                    **self.export_metadata,
                    "project_name": project_name,
                    "export_type": "project",
                },
                "export_options": export_options,
                "project": project_resources,
                "dependencies": dependencies,
                "schema_version": "1.0.0",
            }

            # Save project export
            if output_path.suffix.lower() == ".proj":
                result = self._save_proj_format(project_data, output_path)
            elif output_path.suffix.lower() == ".zip":
                result = self._save_zip_format(project_data, output_path)
            else:
                result = self._save_json_format(project_data, output_path)

            # Track export in graph database
            if self.graph_client:
                self._track_project_export_in_graph(
                    project_name, export_options, result
                )

            logger.info("Project export completed successfully")
            return result

        except Exception as e:
            logger.error(f"Project export failed: {e}")
            raise

    def export_resources(
        self,
        resource_selection: dict[str, list[str]],
        output_path: Path,
        export_format: str = "json",
    ) -> dict[str, Any]:
        """Export specific gateway resources.

        Args:
            resource_selection: Dict mapping resource types to lists of resource names
            output_path: Path for the exported resources
            export_format: Export format ("json", "xml", "zip")

        Returns:
            Export result with metadata and statistics
        """
        logger.info(f"Starting selective resource export to {output_path}")

        try:
            # Gather selected resources
            resources = {}
            total_size = 0

            for resource_type, resource_names in resource_selection.items():
                logger.debug(f"Gathering {resource_type} resources: {resource_names}")
                type_resources = self._gather_resources_by_type(
                    resource_type, resource_names
                )
                resources[resource_type] = type_resources
                total_size += self._calculate_resources_size(type_resources)

            # Analyze cross-resource dependencies
            dependencies = self._analyze_selective_dependencies(resources)

            # Create export package
            export_data = {
                "metadata": {
                    **self.export_metadata,
                    "export_type": "selective",
                    "resource_count": sum(len(res) for res in resources.values()),
                    "total_size": total_size,
                },
                "resource_selection": resource_selection,
                "resources": resources,
                "dependencies": dependencies,
                "schema_version": "1.0.0",
            }

            # Save based on format
            if export_format.lower() == "xml":
                result = self._save_xml_format(export_data, output_path)
            elif export_format.lower() == "zip":
                result = self._save_zip_format(export_data, output_path)
            else:
                result = self._save_json_format(export_data, output_path)

            # Track export in graph database
            if self.graph_client:
                self._track_selective_export_in_graph(resource_selection, result)

            logger.info("Selective resource export completed successfully")
            return result

        except Exception as e:
            logger.error(f"Selective resource export failed: {e}")
            raise

    def create_deployment_package(
        self, package_config: dict[str, Any], output_path: Path
    ) -> dict[str, Any]:
        """Create a deployment package with scripts and configurations.

        Args:
            package_config: Package configuration with deployment settings
            output_path: Path for the deployment package

        Returns:
            Package creation result
        """
        logger.info(f"Creating deployment package at {output_path}")

        try:
            # Gather package components
            package_components = self._gather_package_components(package_config)

            # Generate deployment scripts
            deployment_scripts = self._generate_deployment_scripts(package_config)

            # Create deployment package
            package_data = {
                "metadata": {
                    **self.export_metadata,
                    "export_type": "deployment_package",
                    "package_name": package_config.get("name", "unnamed_package"),
                    "target_environment": package_config.get("environment", "unknown"),
                },
                "package_config": package_config,
                "components": package_components,
                "deployment_scripts": deployment_scripts,
                "schema_version": "1.0.0",
            }

            # Always create deployment packages as ZIP
            result = self._save_deployment_package(package_data, output_path)

            # Track package creation in graph database
            if self.graph_client:
                self._track_package_creation_in_graph(package_config, result)

            logger.info("Deployment package created successfully")
            return result

        except Exception as e:
            logger.error(f"Deployment package creation failed: {e}")
            raise

    def _create_default_backup_profile(self) -> dict[str, Any]:
        """Create default backup profile configuration."""
        return {
            "name": "full_backup",
            "description": "Complete gateway backup including all resources",
            "include_projects": True,
            "include_tags": True,
            "include_databases": True,
            "include_devices": True,
            "include_security": True,
            "include_alarms": True,
            "include_scripts": True,
            "compression": True,
            "validate_dependencies": True,
        }

    def _create_default_project_options(self) -> dict[str, Any]:
        """Create default project export options."""
        return {
            "include_global_resources": False,
            "include_dependencies": True,
            "validate_resources": True,
            "compression": True,
        }

    def _gather_gateway_resources(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Gather all gateway resources based on export profile."""
        resources = {}

        # Mock implementation - in real scenario, this would use gateway APIs
        if profile.get("include_projects", True):
            resources["projects"] = self._get_projects()

        if profile.get("include_tags", True):
            resources["tags"] = self._get_tag_providers()

        if profile.get("include_databases", True):
            resources["databases"] = self._get_database_connections()

        if profile.get("include_devices", True):
            resources["devices"] = self._get_device_connections()

        if profile.get("include_security", True):
            resources["security"] = self._get_security_configuration()

        if profile.get("include_alarms", True):
            resources["alarms"] = self._get_alarm_configuration()

        if profile.get("include_scripts", True):
            resources["scripts"] = self._get_gateway_scripts()

        return resources

    def _analyze_dependencies(self, resources: dict[str, Any]) -> dict[str, Any]:
        """Analyze dependencies between resources."""
        dependencies = {
            "strong_dependencies": [],
            "weak_dependencies": [],
            "potential_conflicts": [],
            "missing_dependencies": [],
        }

        # Mock dependency analysis - real implementation would examine resource configs
        for resource_type, resource_list in resources.items():
            if isinstance(resource_list, list):
                for resource in resource_list:
                    deps = self._analyze_resource_dependencies(resource_type, resource)
                    dependencies["strong_dependencies"].extend(deps.get("strong", []))
                    dependencies["weak_dependencies"].extend(deps.get("weak", []))

        return dependencies

    def _save_gwbk_format(
        self, data: dict[str, Any], output_path: Path
    ) -> dict[str, Any]:
        """Save data in .gwbk compatible format."""
        # In a real implementation, this would create an actual .gwbk file
        # For now, we'll save as compressed JSON
        return self._save_compressed_json(data, output_path)

    def _save_proj_format(
        self, data: dict[str, Any], output_path: Path
    ) -> dict[str, Any]:
        """Save data in .proj compatible format."""
        # In a real implementation, this would create an actual .proj file
        # For now, we'll save as compressed JSON
        return self._save_compressed_json(data, output_path)

    def _save_json_format(
        self, data: dict[str, Any], output_path: Path
    ) -> dict[str, Any]:
        """Save data in JSON format."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        file_size = output_path.stat().st_size

        return {
            "success": True,
            "output_path": str(output_path),
            "format": "json",
            "file_size": file_size,
            "compression_ratio": 1.0,
            "export_time": datetime.now().isoformat(),
        }

    def _save_zip_format(
        self, data: dict[str, Any], output_path: Path
    ) -> dict[str, Any]:
        """Save data in ZIP format with structured files."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Add metadata
            zipf.writestr(
                "metadata.json", json.dumps(data["metadata"], indent=2, default=str)
            )

            # Add main data
            zipf.writestr("export_data.json", json.dumps(data, indent=2, default=str))

            # Add individual resource files if applicable
            if "resources" in data:
                for resource_type, resource_data in data["resources"].items():
                    filename = f"resources/{resource_type}.json"
                    zipf.writestr(
                        filename, json.dumps(resource_data, indent=2, default=str)
                    )

        file_size = output_path.stat().st_size
        uncompressed_size = len(json.dumps(data, default=str).encode("utf-8"))
        compression_ratio = (
            file_size / uncompressed_size if uncompressed_size > 0 else 1.0
        )

        return {
            "success": True,
            "output_path": str(output_path),
            "format": "zip",
            "file_size": file_size,
            "compression_ratio": compression_ratio,
            "export_time": datetime.now().isoformat(),
        }

    def _save_compressed_json(
        self, data: dict[str, Any], output_path: Path
    ) -> dict[str, Any]:
        """Save data as compressed JSON."""
        import gzip

        output_path.parent.mkdir(parents=True, exist_ok=True)

        json_data = json.dumps(data, indent=2, default=str).encode("utf-8")

        with gzip.open(output_path, "wb") as f:
            f.write(json_data)

        file_size = output_path.stat().st_size
        compression_ratio = file_size / len(json_data) if len(json_data) > 0 else 1.0

        return {
            "success": True,
            "output_path": str(output_path),
            "format": "compressed_json",
            "file_size": file_size,
            "compression_ratio": compression_ratio,
            "export_time": datetime.now().isoformat(),
        }

    def _track_export_in_graph(
        self, profile: dict[str, Any], result: dict[str, Any]
    ) -> None:
        """Track export operation in the graph database."""
        if not self.graph_client or not self.graph_client.is_connected:
            return

        try:
            # Create export profile node
            export_node = GraphNode(
                node_type=NodeType.EXPORT_PROFILE,
                properties={
                    "id": self.export_id,
                    "name": profile.get("name", "unnamed_export"),
                    "description": profile.get("description", ""),
                    "export_type": "gateway_backup",
                    "format": result.get("format", "unknown"),
                    "created_date": datetime.now(),
                    "usage_count": 1,
                    "success_rate": 1.0 if result.get("success") else 0.0,
                    "average_size": result.get("file_size", 0),
                    "compression_ratio": result.get("compression_ratio", 1.0),
                    "configuration": profile,
                },
            )

            self.graph_client.create_node(export_node)
            logger.debug(
                f"Tracked export operation in graph database: {self.export_id}"
            )

        except Exception as e:
            logger.warning(f"Failed to track export in graph database: {e}")

    # Mock methods for gathering gateway resources
    # In a real implementation, these would use the gateway client APIs

    def _get_projects(self) -> list[dict[str, Any]]:
        """Get all projects from the gateway."""
        return [
            {
                "name": "ExampleProject",
                "type": "project",
                "size": 1024000,
                "status": "enabled",
            },
        ]

    def _get_tag_providers(self) -> list[dict[str, Any]]:
        """Get all tag providers from the gateway."""
        return [
            {
                "name": "default",
                "type": "tag_provider",
                "driver": "internal",
                "tag_count": 150,
            },
        ]

    def _get_database_connections(self) -> list[dict[str, Any]]:
        """Get all database connections from the gateway."""
        return [
            {
                "name": "production_db",
                "type": "database",
                "driver": "mysql",
                "status": "connected",
            },
        ]

    def _get_device_connections(self) -> list[dict[str, Any]]:
        """Get all device connections from the gateway."""
        return [
            {
                "name": "PLC_1",
                "type": "device",
                "driver": "allen_bradley",
                "status": "connected",
            },
        ]

    def _get_security_configuration(self) -> list[dict[str, Any]]:
        """Get security configuration from the gateway."""
        return [
            {
                "name": "security_config",
                "type": "security",
                "auth_profiles": 2,
                "user_sources": 1,
            },
        ]

    def _get_alarm_configuration(self) -> list[dict[str, Any]]:
        """Get alarm configuration from the gateway."""
        return [
            {"name": "alarm_config", "type": "alarms", "pipelines": 3, "journals": 1},
        ]

    def _get_gateway_scripts(self) -> list[dict[str, Any]]:
        """Get gateway scripts from the gateway."""
        return [
            {
                "name": "startup_script",
                "type": "script",
                "scope": "gateway",
                "enabled": True,
            },
        ]

    def _analyze_resource_dependencies(
        self, resource_type: str, resource: dict[str, Any]
    ) -> dict[str, list[str]]:
        """Analyze dependencies for a specific resource."""
        # Mock implementation
        return {"strong": [], "weak": []}

    def _gather_project_resources(
        self, project_name: str, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Gather resources for a specific project."""
        # Mock implementation
        return {
            "name": project_name,
            "windows": [],
            "templates": [],
            "scripts": [],
            "tags": [],
        }

    def _analyze_project_dependencies(
        self, project_name: str, resources: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze dependencies for a project."""
        # Mock implementation
        return {"dependencies": [], "conflicts": []}

    def _gather_resources_by_type(
        self, resource_type: str, resource_names: list[str]
    ) -> list[dict[str, Any]]:
        """Gather specific resources by type and names."""
        # Mock implementation
        return [{"name": name, "type": resource_type} for name in resource_names]

    def _calculate_resources_size(self, resources: list[dict[str, Any]]) -> int:
        """Calculate total size of resources."""
        # Mock implementation
        return len(resources) * 1000

    def _analyze_selective_dependencies(
        self, resources: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze dependencies for selective export."""
        # Mock implementation
        return {"dependencies": [], "conflicts": []}

    def _save_xml_format(
        self, data: dict[str, Any], output_path: Path
    ) -> dict[str, Any]:
        """Save data in XML format."""
        # Mock implementation - would use xml.etree.ElementTree or lxml
        return self._save_json_format(data, output_path.with_suffix(".json"))

    def _gather_package_components(self, config: dict[str, Any]) -> dict[str, Any]:
        """Gather components for deployment package."""
        # Mock implementation
        return {"components": []}

    def _generate_deployment_scripts(self, config: dict[str, Any]) -> dict[str, Any]:
        """Generate deployment scripts for package."""
        # Mock implementation
        return {
            "deploy.py": "# Deployment script",
            "rollback.py": "# Rollback script",
            "validate.py": "# Validation script",
        }

    def _save_deployment_package(
        self, data: dict[str, Any], output_path: Path
    ) -> dict[str, Any]:
        """Save deployment package."""
        return self._save_zip_format(data, output_path)

    def _track_project_export_in_graph(
        self, project_name: str, options: dict[str, Any], result: dict[str, Any]
    ) -> None:
        """Track project export in graph database."""
        # Similar to _track_export_in_graph but for projects
        pass

    def _track_selective_export_in_graph(
        self, selection: dict[str, list[str]], result: dict[str, Any]
    ) -> None:
        """Track selective export in graph database."""
        # Similar to _track_export_in_graph but for selective exports
        pass

    def _track_package_creation_in_graph(
        self, config: dict[str, Any], result: dict[str, Any]
    ) -> None:
        """Track package creation in graph database."""
        # Similar to _track_export_in_graph but for packages
        pass
