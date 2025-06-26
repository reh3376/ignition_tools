"""Change Tracker for monitoring and analyzing changes in Ignition resources."""

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of changes that can be detected."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"
    MOVED = "moved"


class ResourceType(Enum):
    """Types of Ignition resources."""

    VISION_WINDOW = "vision_window"
    PERSPECTIVE_VIEW = "perspective_view"
    GATEWAY_SCRIPT = "gateway_script"
    TAG_CONFIGURATION = "tag_configuration"
    DATABASE_CONNECTION = "database_connection"
    DEVICE_CONNECTION = "device_connection"
    SECURITY_CONFIG = "security_config"
    ALARM_CONFIG = "alarm_config"
    UDT_DEFINITION = "udt_definition"
    NAMED_QUERY = "named_query"
    REPORT_TEMPLATE = "report_template"
    UNKNOWN = "unknown"


@dataclass
class ChangeRecord:
    """Record of a detected change."""

    id: str
    file_path: str
    resource_type: ResourceType
    change_type: ChangeType
    timestamp: datetime
    file_size: int
    content_hash: str
    previous_hash: str | None = None
    lines_added: int = 0
    lines_deleted: int = 0
    complexity_delta: float = 0.0
    risk_level: str = "low"
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class ChangeTracker:
    """Tracks and analyzes changes in Ignition resources."""

    def __init__(
        self,
        repository_path: Path,
        graph_client: Any | None = None,
        watch_patterns: list[str] | None = None,
    ):
        """Initialize the Change Tracker."""
        self.repository_path = repository_path
        self.graph_client = graph_client

        # Default patterns for Ignition resources
        self.watch_patterns = watch_patterns or [
            "*.proj",  # Project files
            "*.json",  # Configuration files
            "*.xml",  # Resource exports
            "*.py",  # Python scripts
            "*.sql",  # SQL queries
            "*.gwbk",  # Gateway backups
        ]

        # Change tracking state
        self._file_hashes = {}
        self._change_history = []
        self._monitoring_active = False

        logger.info(f"ChangeTracker initialized for repository: {repository_path}")

    def scan_for_changes(self) -> list[ChangeRecord]:
        """Scan the repository for changes since last scan."""
        try:
            changes = []

            # Scan all files matching watch patterns
            for pattern in self.watch_patterns:
                for file_path in self.repository_path.rglob(pattern):
                    if file_path.is_file():
                        change = self._check_file_for_changes(file_path)
                        if change:
                            changes.append(change)

            # Update change history
            self._change_history.extend(changes)

            logger.info(f"Detected {len(changes)} changes in repository scan")
            return changes

        except Exception as e:
            logger.error(f"Failed to scan for changes: {e}")
            return []

    def get_recent_changes(self, limit: int = 50) -> list[ChangeRecord]:
        """Get recent changes across all files."""
        try:
            recent_changes = sorted(self._change_history, key=lambda x: x.timestamp, reverse=True)
            return recent_changes[:limit]
        except Exception as e:
            logger.error(f"Failed to get recent changes: {e}")
            return []

    def _check_file_for_changes(self, file_path: Path) -> ChangeRecord | None:
        """Check a specific file for changes."""
        try:
            relative_path = str(file_path.relative_to(self.repository_path))
            current_hash = self._calculate_file_hash(file_path)
            current_size = file_path.stat().st_size

            # Check if file is new or modified
            if relative_path not in self._file_hashes:
                # New file
                change = self._create_change_record(
                    file_path=relative_path,
                    change_type=ChangeType.CREATED,
                    current_hash=current_hash,
                    file_size=current_size,
                )

                # Update tracking
                self._file_hashes[relative_path] = {
                    "hash": current_hash,
                    "size": current_size,
                    "modified": datetime.now(),
                }

                return change

            else:
                # Check for modifications
                previous_info = self._file_hashes[relative_path]
                if current_hash != previous_info["hash"]:
                    # File modified
                    change = self._create_change_record(
                        file_path=relative_path,
                        change_type=ChangeType.MODIFIED,
                        current_hash=current_hash,
                        previous_hash=previous_info["hash"],
                        file_size=current_size,
                    )

                    # Update tracking
                    self._file_hashes[relative_path] = {
                        "hash": current_hash,
                        "size": current_size,
                        "modified": datetime.now(),
                    }

                    return change

            return None

        except Exception as e:
            logger.error(f"Failed to check file for changes: {e}")
            return None

    def _create_change_record(
        self,
        file_path: str,
        change_type: ChangeType,
        current_hash: str,
        file_size: int,
        previous_hash: str | None = None,
    ) -> ChangeRecord:
        """Create a change record for a detected change."""
        try:
            # Generate unique ID for the change
            change_id = hashlib.md5(
                f"{file_path}_{change_type.value}_{datetime.now().isoformat()}".encode()
            ).hexdigest()

            # Determine resource type
            resource_type = self._determine_resource_type(file_path)

            # Calculate risk level
            risk_level = self._calculate_risk_level(file_path, change_type, resource_type)

            # Create change record
            change = ChangeRecord(
                id=change_id,
                file_path=file_path,
                resource_type=resource_type,
                change_type=change_type,
                timestamp=datetime.now(),
                file_size=file_size,
                content_hash=current_hash,
                previous_hash=previous_hash,
                risk_level=risk_level,
                metadata={
                    "repository_path": str(self.repository_path),
                    "detected_by": "ChangeTracker",
                },
            )

            return change

        except Exception as e:
            logger.error(f"Failed to create change record: {e}")
            raise

    def _determine_resource_type(self, file_path: str) -> ResourceType:
        """Determine the resource type based on file path and extension."""
        try:
            path_lower = file_path.lower()

            # Check file extension and path patterns
            if path_lower.endswith(".proj"):
                return ResourceType.VISION_WINDOW
            elif "perspective" in path_lower and path_lower.endswith(".json"):
                return ResourceType.PERSPECTIVE_VIEW
            elif "gateway" in path_lower and path_lower.endswith(".py"):
                return ResourceType.GATEWAY_SCRIPT
            elif "tag" in path_lower:
                return ResourceType.TAG_CONFIGURATION
            elif "database" in path_lower or "db" in path_lower:
                return ResourceType.DATABASE_CONNECTION
            elif "device" in path_lower:
                return ResourceType.DEVICE_CONNECTION
            elif "security" in path_lower:
                return ResourceType.SECURITY_CONFIG
            elif "alarm" in path_lower:
                return ResourceType.ALARM_CONFIG
            elif "udt" in path_lower:
                return ResourceType.UDT_DEFINITION
            elif path_lower.endswith(".sql"):
                return ResourceType.NAMED_QUERY
            elif "report" in path_lower:
                return ResourceType.REPORT_TEMPLATE
            else:
                return ResourceType.UNKNOWN

        except Exception as e:
            logger.error(f"Failed to determine resource type: {e}")
            return ResourceType.UNKNOWN

    def _calculate_risk_level(self, file_path: str, change_type: ChangeType, resource_type: ResourceType) -> str:
        """Calculate risk level for a change."""
        try:
            risk_score = 0.0

            # Base risk by change type
            if change_type == ChangeType.CREATED:
                risk_score += 0.2
            elif change_type == ChangeType.MODIFIED:
                risk_score += 0.4
            elif change_type == ChangeType.DELETED:
                risk_score += 0.6
            elif change_type in [ChangeType.RENAMED, ChangeType.MOVED]:
                risk_score += 0.3

            # Risk by resource type
            high_risk_resources = [
                ResourceType.GATEWAY_SCRIPT,
                ResourceType.SECURITY_CONFIG,
                ResourceType.DATABASE_CONNECTION,
            ]
            medium_risk_resources = [
                ResourceType.TAG_CONFIGURATION,
                ResourceType.ALARM_CONFIG,
                ResourceType.DEVICE_CONNECTION,
            ]

            if resource_type in high_risk_resources:
                risk_score += 0.4
            elif resource_type in medium_risk_resources:
                risk_score += 0.2
            else:
                risk_score += 0.1

            # Risk by file location
            if "production" in file_path.lower() or "prod" in file_path.lower():
                risk_score += 0.3
            elif "critical" in file_path.lower():
                risk_score += 0.4

            # Convert to risk level
            if risk_score >= 0.8:
                return "critical"
            elif risk_score >= 0.6:
                return "high"
            elif risk_score >= 0.4:
                return "medium"
            else:
                return "low"

        except Exception as e:
            logger.error(f"Failed to calculate risk level: {e}")
            return "medium"

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            return ""
