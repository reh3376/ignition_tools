"""OPC Tag Manager for Ignition Data Integration.

This module provides comprehensive OPC tag management capabilities including
tag browsing, creation, monitoring, and batch operations.
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TagOperation(Enum):
    """Supported tag operations."""

    READ = "read"
    WRITE = "write"
    BROWSE = "browse"
    CREATE = "create"
    DELETE = "delete"
    MONITOR = "monitor"


class TagDataType(Enum):
    """Supported tag data types."""

    BOOLEAN = "Boolean"
    INTEGER = "Int4"
    FLOAT = "Float8"
    STRING = "String"
    DATETIME = "DateTime"
    DOCUMENT = "Document"


class TagQuality(Enum):
    """Tag quality codes."""

    GOOD = 192
    BAD_NOT_CONNECTED = 68
    BAD_DEVICE_FAILURE = 72
    BAD_SENSOR_FAILURE = 76
    BAD_LAST_KNOWN_VALUE = 80
    BAD_COMM_FAILURE = 84
    BAD_OUT_OF_SERVICE = 88
    UNCERTAIN = 104


@dataclass
class TagDefinition:
    """Definition for creating a new tag."""

    name: str
    tag_path: str
    data_type: TagDataType
    opc_item_path: str | None = None
    scan_class: str = "Default"
    enabled: bool = True
    description: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    units: str | None = None
    deadband: float | None = None
    scale_factor: float | None = None
    offset: float | None = None


@dataclass
class TagInfo:
    """Information about an existing tag."""

    name: str
    tag_path: str
    data_type: str
    value: Any
    quality: int
    quality_name: str
    timestamp: str | None = None
    enabled: bool = True
    description: str | None = None
    opc_item_path: str | None = None


@dataclass
class BrowseResult:
    """Result from tag browsing operation."""

    success: bool
    tags: list[TagInfo]
    folders: list[str]
    total_items: int
    error_message: str | None = None


class OPCTagManager:
    """Manager for OPC tag operations in Ignition."""

    def __init__(self, provider_name: str = "default") -> None:
        """Initialize the OPC tag manager."""
        self.provider_name = provider_name
        self.logger = logging.getLogger(f"{__name__}.{provider_name}")

    def browse_tags(
        self,
        parent_path: str = "",
        recursive: bool = False,
        filter_pattern: str | None = None,
    ) -> BrowseResult:
        """Browse tags in the specified path."""
        try:
            # In a real Ignition environment, this would use system.tag.browse()
            # For now, we'll create a mock implementation

            tags = []
            folders = []

            # Mock tag browsing - in production this would be:
            # browse_results = system.tag.browse(parent_path)

            # Simulate some common industrial tags
            if parent_path == "" or parent_path == "/":
                # Root level folders
                folders = ["PLCs", "Pumps", "Tanks", "Conveyor", "HVAC", "Alarms"]
            elif "PLCs" in parent_path:
                # PLC tags
                mock_tags = [
                    TagInfo(
                        name="PLC1_Status",
                        tag_path=f"{parent_path}/PLC1_Status",
                        data_type="Boolean",
                        value=True,
                        quality=192,
                        quality_name="GOOD",
                        description="PLC 1 Communication Status",
                    ),
                    TagInfo(
                        name="PLC1_Heartbeat",
                        tag_path=f"{parent_path}/PLC1_Heartbeat",
                        data_type="Int4",
                        value=12345,
                        quality=192,
                        quality_name="GOOD",
                        description="PLC 1 Heartbeat Counter",
                    ),
                ]
                tags.extend(mock_tags)
            elif "Pumps" in parent_path:
                # Pump tags
                for i in range(1, 4):
                    pump_tags = [
                        TagInfo(
                            name=f"Pump{i}_Running",
                            tag_path=f"{parent_path}/Pump{i}_Running",
                            data_type="Boolean",
                            value=i % 2 == 1,
                            quality=192,
                            quality_name="GOOD",
                            description=f"Pump {i} Running Status",
                        ),
                        TagInfo(
                            name=f"Pump{i}_Speed",
                            tag_path=f"{parent_path}/Pump{i}_Speed",
                            data_type="Float8",
                            value=1750.5 + i * 10,
                            quality=192,
                            quality_name="GOOD",
                            description=f"Pump {i} Speed (RPM)",
                            units="RPM",
                        ),
                        TagInfo(
                            name=f"Pump{i}_Flow",
                            tag_path=f"{parent_path}/Pump{i}_Flow",
                            data_type="Float8",
                            value=125.3 + i * 5,
                            quality=192,
                            quality_name="GOOD",
                            description=f"Pump {i} Flow Rate",
                            units="GPM",
                        ),
                    ]
                    tags.extend(pump_tags)

            # Apply filter if specified
            if filter_pattern:
                filtered_tags = []
                for tag in tags:
                    if filter_pattern.lower() in tag.name.lower():
                        filtered_tags.append(tag)
                tags = filtered_tags

            # Handle recursive browsing
            if recursive and folders:
                for folder in folders:
                    sub_path = f"{parent_path}/{folder}" if parent_path else folder
                    sub_result = self.browse_tags(sub_path, recursive=True, filter_pattern=filter_pattern)
                    if sub_result.success:
                        tags.extend(sub_result.tags)
                        folders.extend([f"{folder}/{f}" for f in sub_result.folders])

            return BrowseResult(
                success=True,
                tags=tags,
                folders=folders,
                total_items=len(tags) + len(folders),
            )

        except Exception as e:
            self.logger.error(f"Tag browsing failed: {e}")
            return BrowseResult(success=False, tags=[], folders=[], total_items=0, error_message=str(e))

    def create_tag(self, tag_def: TagDefinition) -> dict[str, Any]:
        """Create a new tag."""
        try:
            # In a real Ignition environment, this would use system.tag.configure()
            # or system.tag.addTag()

            # Validate tag definition
            if not tag_def.name or not tag_def.tag_path:
                raise ValueError("Tag name and path are required")

            # Mock tag creation
            tag_config = {
                "name": tag_def.name,
                "tagType": "OPC",
                "dataType": tag_def.data_type.value,
                "opcItemPath": tag_def.opc_item_path or f"ns=2;s={tag_def.name}",
                "scanClass": tag_def.scan_class,
                "enabled": tag_def.enabled,
                "description": tag_def.description or "",
                "deadband": tag_def.deadband or 0.0,
                "scaleMode": "Linear" if tag_def.scale_factor else "None",
            }

            if tag_def.scale_factor:
                tag_config["scaleMode"] = "Linear"
                tag_config["scaleFactor"] = tag_def.scale_factor
                tag_config["offset"] = tag_def.offset or 0.0

            if tag_def.min_value is not None:
                tag_config["minValue"] = tag_def.min_value

            if tag_def.max_value is not None:
                tag_config["maxValue"] = tag_def.max_value

            if tag_def.units:
                tag_config["units"] = tag_def.units

            self.logger.info(f"Created tag: {tag_def.tag_path}")

            return {
                "success": True,
                "tag_path": tag_def.tag_path,
                "config": tag_config,
                "message": f"Tag '{tag_def.name}' created successfully",
            }

        except Exception as e:
            self.logger.error(f"Tag creation failed: {e}")
            return {"success": False, "error": str(e), "tag_path": tag_def.tag_path}

    def create_tags_batch(self, tag_definitions: list[TagDefinition]) -> dict[str, Any]:
        """Create multiple tags in batch."""
        results = []
        successful_count = 0
        failed_count = 0

        for tag_def in tag_definitions:
            result = self.create_tag(tag_def)
            results.append(result)

            if result["success"]:
                successful_count += 1
            else:
                failed_count += 1

        return {
            "success": failed_count == 0,
            "total_tags": len(tag_definitions),
            "successful_count": successful_count,
            "failed_count": failed_count,
            "results": results,
        }

    def read_tags(self, tag_paths: list[str]) -> dict[str, Any]:
        """Read values from multiple tags."""
        try:
            # In a real Ignition environment, this would use system.tag.readBlocking()

            tag_values = []
            for tag_path in tag_paths:
                # Mock tag reading
                if "Status" in tag_path:
                    value = True
                    quality = TagQuality.GOOD.value
                elif "Speed" in tag_path or "Flow" in tag_path:
                    value = 1750.5
                    quality = TagQuality.GOOD.value
                elif "Heartbeat" in tag_path:
                    value = 12345
                    quality = TagQuality.GOOD.value
                else:
                    value = 0
                    quality = TagQuality.GOOD.value

                tag_values.append(
                    {
                        "tag_path": tag_path,
                        "value": value,
                        "quality": quality,
                        "quality_name": self._get_quality_name(quality),
                        "timestamp": "2025-01-28T12:00:00Z",
                    }
                )

            return {"success": True, "tag_count": len(tag_paths), "values": tag_values}

        except Exception as e:
            self.logger.error(f"Tag reading failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tag_count": len(tag_paths),
                "values": [],
            }

    def write_tags(self, tag_writes: list[dict[str, Any]]) -> dict[str, Any]:
        """Write values to multiple tags."""
        try:
            # In a real Ignition environment, this would use system.tag.writeBlocking()

            results = []
            successful_count = 0
            failed_count = 0

            for write_op in tag_writes:
                tag_path = write_op.get("tag_path")
                value = write_op.get("value")

                if not tag_path:
                    results.append(
                        {
                            "tag_path": "unknown",
                            "success": False,
                            "error": "Tag path is required",
                        }
                    )
                    failed_count += 1
                    continue

                # Mock tag writing
                try:
                    # Simulate validation
                    if "Boolean" in tag_path and not isinstance(value, bool):
                        raise ValueError("Boolean value expected")

                    results.append(
                        {
                            "tag_path": tag_path,
                            "value": value,
                            "success": True,
                            "quality": TagQuality.GOOD.value,
                            "quality_name": "GOOD",
                        }
                    )
                    successful_count += 1

                except Exception as e:
                    results.append({"tag_path": tag_path, "success": False, "error": str(e)})
                    failed_count += 1

            return {
                "success": failed_count == 0,
                "total_writes": len(tag_writes),
                "successful_count": successful_count,
                "failed_count": failed_count,
                "results": results,
            }

        except Exception as e:
            self.logger.error(f"Tag writing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_writes": len(tag_writes),
                "results": [],
            }

    def generate_tag_creation_script(self, tag_definitions: list[TagDefinition], script_type: str = "jython") -> str:
        """Generate Ignition script for tag creation."""
        if script_type == "jython":
            return self._generate_jython_tag_script(tag_definitions)
        elif script_type == "json":
            return self._generate_json_tag_config(tag_definitions)
        else:
            raise ValueError(f"Unsupported script type: {script_type}")

    def _generate_jython_tag_script(self, tag_definitions: list[TagDefinition]) -> str:
        """Generate Jython script for tag creation."""
        script_lines = [
            '"""',
            "Generated Tag Creation Script for Ignition",
            f"Total Tags: {len(tag_definitions)}",
            "Generated by IGN Scripts Data Integration System",
            '"""',
            "",
            "from system.tag import configure",
            "",
            "def create_tags():",
            '    """Create all defined tags."""',
            "    tag_configs = []",
            "",
        ]

        for tag_def in tag_definitions:
            script_lines.extend(
                [
                    "    # Tag: " + tag_def.name,
                    "    tag_config = {",
                    f'        "name": "{tag_def.name}",',
                    '        "tagType": "OPC",',
                    f'        "dataType": "{tag_def.data_type.value}",',
                    f'        "opcItemPath": "{tag_def.opc_item_path or f"ns=2;s={tag_def.name}"}",',
                    f'        "scanClass": "{tag_def.scan_class}",',
                    f'        "enabled": {tag_def.enabled},',
                    f'        "description": "{tag_def.description or ""}",',
                    "    }",
                    "    tag_configs.append(tag_config)",
                    "",
                ]
            )

        script_lines.extend(
            [
                "    # Configure all tags",
                "    try:",
                '        result = configure("", tag_configs, "o")',  # "o" for overwrite
                "        if result.getQuality().isGood():",
                '            print("All tags created successfully!")',
                "            return True",
                "        else:",
                '            print("Tag creation failed:", result.getQuality())',
                "            return False",
                "    except Exception as e:",
                '        print("Error creating tags:", str(e))',
                "        return False",
                "",
                "# Execute the function",
                'if __name__ == "__main__":',
                "    create_tags()",
            ]
        )

        return "\n".join(script_lines)

    def _generate_json_tag_config(self, tag_definitions: list[TagDefinition]) -> str:
        """Generate JSON configuration for tags."""
        configs = []

        for tag_def in tag_definitions:
            config = {
                "name": tag_def.name,
                "tagType": "OPC",
                "dataType": tag_def.data_type.value,
                "opcItemPath": tag_def.opc_item_path or f"ns=2;s={tag_def.name}",
                "scanClass": tag_def.scan_class,
                "enabled": tag_def.enabled,
                "description": tag_def.description or "",
            }

            if tag_def.min_value is not None:
                config["minValue"] = tag_def.min_value

            if tag_def.max_value is not None:
                config["maxValue"] = tag_def.max_value

            if tag_def.units:
                config["units"] = tag_def.units

            if tag_def.deadband:
                config["deadband"] = tag_def.deadband

            if tag_def.scale_factor:
                config["scaleMode"] = "Linear"
                config["scaleFactor"] = tag_def.scale_factor
                config["offset"] = tag_def.offset or 0.0

            configs.append(config)

        return json.dumps(configs, indent=2)

    def _get_quality_name(self, quality_code: int) -> str:
        """Get human-readable quality name."""
        quality_mapping = {
            192: "GOOD",
            68: "BAD_NOT_CONNECTED",
            72: "BAD_DEVICE_FAILURE",
            76: "BAD_SENSOR_FAILURE",
            80: "BAD_LAST_KNOWN_VALUE",
            84: "BAD_COMM_FAILURE",
            88: "BAD_OUT_OF_SERVICE",
            104: "UNCERTAIN",
        }
        return quality_mapping.get(quality_code, f"UNKNOWN_QUALITY_{quality_code}")

    def export_tag_configuration(self, tag_paths: list[str]) -> dict[str, Any]:
        """Export tag configuration for backup or migration."""
        try:
            # Browse each tag to get its configuration
            tag_configs = []

            for tag_path in tag_paths:
                # In real Ignition, this would read the tag configuration
                # For now, create a mock configuration
                config = {
                    "tagPath": tag_path,
                    "name": tag_path.split("/")[-1],
                    "tagType": "OPC",
                    "dataType": "Float8",
                    "enabled": True,
                    "scanClass": "Default",
                    "description": f"Exported tag: {tag_path}",
                }
                tag_configs.append(config)

            return {
                "success": True,
                "tag_count": len(tag_paths),
                "configurations": tag_configs,
                "export_timestamp": "2025-01-28T12:00:00Z",
            }

        except Exception as e:
            self.logger.error(f"Tag export failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tag_count": 0,
                "configurations": [],
            }
