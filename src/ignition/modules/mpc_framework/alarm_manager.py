"""Production Alarm Manager - Phase 14 Implementation.

This module implements a comprehensive alarm management system for production control
with priority-based escalation, notification management, and alarm analytics.

Following crawl_mcp.py methodology:
- Step 1: Environment validation with alarm system checks
- Step 2: Input validation using Pydantic models
- Step 3: Comprehensive error handling with fail-safe behavior
- Step 4: Modular testing with alarm scenario validation
- Step 5: Progressive complexity with scalable alarm handling
- Step 6: Resource management with efficient alarm processing

Author: IGN Scripts Development Team
Version: 14.0.0
"""

import asyncio
import logging
import os
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class AlarmState(Enum):
    """Alarm states."""

    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    CLEARED = "CLEARED"
    SUPPRESSED = "SUPPRESSED"


class AlarmPriority(Enum):
    """Alarm priority levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class NotificationMethod(Enum):
    """Notification delivery methods."""

    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    WEBHOOK = "WEBHOOK"
    VOICE = "VOICE"


# Step 1: Environment Validation (crawl_mcp.py methodology)
def validate_alarm_environment() -> dict[str, Any]:
    """Validate alarm management environment setup."""
    logger.info("🔍 Step 1: Environment Validation - Alarm Manager")

    errors = []
    warnings = []

    # Check alarm environment variables
    alarm_vars = [
        "ALARM_DATABASE_URL",
        "ALARM_NOTIFICATION_ENDPOINTS",
        "ALARM_ESCALATION_TIMEOUT",
        "ALARM_MAX_ACTIVE_ALARMS",
    ]

    for var in alarm_vars:
        if not os.getenv(var):
            warnings.append(f"Alarm environment variable {var} not set")

    # Check notification system availability
    notification_endpoints = os.getenv("ALARM_NOTIFICATION_ENDPOINTS", "").split(",")
    if len(notification_endpoints) < 1 or not notification_endpoints[0]:
        warnings.append("No notification endpoints configured")

    # Check alarm database connectivity
    alarm_db_url = os.getenv("ALARM_DATABASE_URL")
    if not alarm_db_url:
        warnings.append("Alarm database URL not configured")

    # Check system resources for alarm processing
    try:
        import psutil

        memory = psutil.virtual_memory()
        if memory.available < 128 * 1024 * 1024:  # 128MB
            warnings.append("Low available memory for alarm processing")
        logger.info(
            f"✅ System resources: {memory.available / (1024**3):.1f} GB available"
        )
    except ImportError:
        warnings.append("psutil not available for resource monitoring")

    # Check alarm storage directory
    alarm_dir = os.getenv("ALARM_STORAGE_DIR", "/tmp/alarm_data")
    try:
        os.makedirs(alarm_dir, exist_ok=True)
        test_file = os.path.join(alarm_dir, "test_alarm.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        logger.info(f"✅ Alarm storage directory accessible: {alarm_dir}")
    except Exception as e:
        errors.append(f"Cannot access alarm storage directory {alarm_dir}: {e}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "timestamp": datetime.now().isoformat(),
    }


# Step 2: Input Validation Models (crawl_mcp.py methodology)
class AlarmDefinition(BaseModel):
    """Alarm definition with validation."""

    alarm_id: str = Field(..., description="Unique alarm identifier")
    name: str = Field(..., description="Alarm name")
    description: str = Field(..., description="Alarm description")
    priority: AlarmPriority = Field(..., description="Alarm priority")
    category: str = Field(..., description="Alarm category")
    source_system: str = Field(..., description="Source system")

    # Escalation settings
    escalation_timeout_minutes: int = Field(
        default=15, ge=1, description="Escalation timeout"
    )
    auto_clear_enabled: bool = Field(
        default=False, description="Enable automatic clearing"
    )
    suppression_enabled: bool = Field(
        default=True, description="Enable alarm suppression"
    )

    @field_validator("alarm_id")
    @classmethod
    def validate_alarm_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Alarm ID cannot be empty")
        return v.strip()


class NotificationRule(BaseModel):
    """Notification rule configuration."""

    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    alarm_priorities: list[AlarmPriority] = Field(
        ..., description="Alarm priorities to match"
    )
    alarm_categories: list[str] = Field(
        default_factory=list, description="Alarm categories to match"
    )

    # Notification settings
    notification_methods: list[NotificationMethod] = Field(
        ..., description="Notification methods"
    )
    recipients: list[str] = Field(..., description="Notification recipients")
    escalation_levels: list[dict[str, Any]] = Field(
        default_factory=list, description="Escalation levels"
    )

    # Timing settings
    initial_delay_minutes: int = Field(
        default=0, ge=0, description="Initial notification delay"
    )
    repeat_interval_minutes: int = Field(
        default=0, ge=0, description="Repeat notification interval"
    )
    max_notifications: int = Field(
        default=10, ge=1, description="Maximum notifications"
    )


class AlarmConfiguration(BaseModel):
    """Alarm management system configuration."""

    system_name: str = Field(..., description="Alarm system name")
    max_active_alarms: int = Field(
        default=1000, ge=1, description="Maximum active alarms"
    )
    alarm_retention_days: int = Field(
        default=90, ge=1, description="Alarm history retention"
    )

    # Alarm definitions and rules
    alarm_definitions: list[AlarmDefinition] = Field(
        ..., description="Alarm definitions"
    )
    notification_rules: list[NotificationRule] = Field(
        ..., description="Notification rules"
    )

    # System settings
    enable_alarm_suppression: bool = Field(
        default=True, description="Enable alarm suppression"
    )
    enable_escalation: bool = Field(default=True, description="Enable alarm escalation")
    enable_analytics: bool = Field(default=True, description="Enable alarm analytics")


# Step 3: Comprehensive Error Handling (crawl_mcp.py methodology)
def format_alarm_error(error: Exception, context: str = "") -> str:
    """Format alarm management errors."""
    error_str = str(error).lower()

    if "notification" in error_str or "email" in error_str or "sms" in error_str:
        return (
            f"Notification error in {context}: Check notification service configuration"
        )
    elif "database" in error_str or "storage" in error_str:
        return f"Storage error in {context}: Check alarm database connectivity"
    elif "timeout" in error_str:
        return f"Alarm timeout in {context}: System may be overloaded"
    elif "permission" in error_str:
        return f"Permission error in {context}: Check alarm system permissions"
    elif "escalation" in error_str:
        return f"Escalation error in {context}: Check escalation rules configuration"
    else:
        return f"Alarm system error in {context}: {error!s}"


# Step 5: Progressive Complexity (crawl_mcp.py methodology)
@dataclass
class AlarmInstance:
    """Individual alarm instance."""

    alarm_id: str
    definition: AlarmDefinition
    state: AlarmState
    priority: AlarmPriority

    # Timestamps
    created_at: datetime
    last_updated: datetime
    acknowledged_at: datetime | None = None
    cleared_at: datetime | None = None

    # Context information
    source_value: float | None = None
    source_description: str = ""
    tags: dict[str, str] = field(default_factory=dict)

    # Acknowledgment information
    acknowledged_by: str | None = None
    acknowledgment_comment: str = ""

    # Escalation tracking
    escalation_level: int = 0
    notifications_sent: int = 0
    last_notification: datetime | None = None


@dataclass
class ProductionAlarmManager:
    """Production alarm management system."""

    # Configuration
    config: AlarmConfiguration

    # Runtime state
    _initialized: bool = field(default=False, init=False)
    _processing_active: bool = field(default=False, init=False)
    _processing_task: asyncio.Task | None = field(default=None, init=False)

    # Alarm storage
    _active_alarms: dict[str, AlarmInstance] = field(default_factory=dict, init=False)
    _alarm_history: list[AlarmInstance] = field(default_factory=list, init=False)
    _suppressed_alarms: set[str] = field(default_factory=set, init=False)

    # Event handlers
    _alarm_handlers: list[Callable] = field(default_factory=list, init=False)
    _notification_handlers: dict[NotificationMethod, Callable] = field(
        default_factory=dict, init=False
    )

    # Analytics
    _alarm_statistics: dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """Initialize alarm manager after creation."""
        logger.info("🚨 Initializing Production Alarm Manager")

    async def initialize(self) -> dict[str, Any]:
        """Initialize alarm management system."""
        logger.info(
            "🔧 Step 1-6: Initializing Alarm Manager (crawl_mcp.py methodology)"
        )

        # Step 1: Environment validation first
        env_validation = validate_alarm_environment()
        if not env_validation["valid"]:
            return {
                "success": False,
                "error": "Alarm management environment validation failed",
                "details": env_validation["errors"],
            }

        try:
            # Step 2: Input validation (already done via Pydantic)
            logger.info("✅ Alarm configuration validation passed")

            # Step 3: Initialize alarm definitions
            for definition in self.config.alarm_definitions:
                logger.info(f"✅ Alarm definition loaded: {definition.name}")

            # Step 4: Initialize notification handlers
            await self._initialize_notification_handlers()

            # Step 5: Start alarm processing
            await self._start_processing()

            # Step 6: Initialize analytics
            await self._initialize_analytics()

            self._initialized = True
            logger.info("✅ Production Alarm Manager initialized successfully")

            return {
                "success": True,
                "message": "Alarm manager initialized successfully",
                "configuration": {
                    "system_name": self.config.system_name,
                    "max_active_alarms": self.config.max_active_alarms,
                    "alarm_definitions": len(self.config.alarm_definitions),
                    "notification_rules": len(self.config.notification_rules),
                },
            }

        except Exception as e:
            error_msg = format_alarm_error(e, "alarm manager initialization")
            logger.error(f"❌ Alarm manager initialization failed: {error_msg}")
            return {"success": False, "error": error_msg}

    async def _initialize_notification_handlers(self) -> None:
        """Initialize notification method handlers."""
        # Initialize default notification handlers
        self._notification_handlers[NotificationMethod.EMAIL] = (
            self._send_email_notification
        )
        self._notification_handlers[NotificationMethod.SMS] = (
            self._send_sms_notification
        )
        self._notification_handlers[NotificationMethod.PUSH] = (
            self._send_push_notification
        )
        self._notification_handlers[NotificationMethod.WEBHOOK] = (
            self._send_webhook_notification
        )
        self._notification_handlers[NotificationMethod.VOICE] = (
            self._send_voice_notification
        )

        logger.info("✅ Notification handlers initialized")

    async def _start_processing(self) -> None:
        """Start alarm processing task."""
        self._processing_task = asyncio.create_task(self._processing_loop())
        self._processing_active = True
        logger.info("✅ Alarm processing started")

    async def _processing_loop(self) -> None:
        """Main alarm processing loop."""
        while self._processing_active:
            try:
                # Process escalations
                await self._process_escalations()

                # Process notifications
                await self._process_notifications()

                # Update analytics
                await self._update_analytics()

                # Cleanup old alarms
                await self._cleanup_old_alarms()

                await asyncio.sleep(10)  # Process every 10 seconds

            except asyncio.CancelledError:
                logger.info("Alarm processing loop cancelled")
                break
            except Exception as e:
                logger.error(f"Alarm processing error: {e}")
                await asyncio.sleep(10)

    async def _initialize_analytics(self) -> None:
        """Initialize alarm analytics."""
        self._alarm_statistics = {
            "total_alarms": 0,
            "active_alarms": 0,
            "acknowledged_alarms": 0,
            "cleared_alarms": 0,
            "suppressed_alarms": 0,
            "by_priority": {priority.name: 0 for priority in AlarmPriority},
            "by_category": {},
            "average_resolution_time": 0.0,
            "escalation_rate": 0.0,
        }

        logger.info("✅ Alarm analytics initialized")

    async def create_alarm(
        self,
        alarm_id: str,
        source_value: float | None = None,
        source_description: str = "",
        tags: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create new alarm instance."""
        if not self._initialized:
            return {"success": False, "error": "Alarm manager not initialized"}

        try:
            # Find alarm definition
            definition = None
            for def_item in self.config.alarm_definitions:
                if def_item.alarm_id == alarm_id:
                    definition = def_item
                    break

            if not definition:
                return {
                    "success": False,
                    "error": f"Alarm definition not found: {alarm_id}",
                }

            # Check if alarm already exists
            if alarm_id in self._active_alarms:
                return {"success": False, "error": f"Alarm already active: {alarm_id}"}

            # Check maximum active alarms
            if len(self._active_alarms) >= self.config.max_active_alarms:
                return {"success": False, "error": "Maximum active alarms reached"}

            # Create alarm instance
            current_time = datetime.now()
            alarm_instance = AlarmInstance(
                alarm_id=alarm_id,
                definition=definition,
                state=AlarmState.ACTIVE,
                priority=definition.priority,
                created_at=current_time,
                last_updated=current_time,
                source_value=source_value,
                source_description=source_description,
                tags=tags or {},
            )

            # Add to active alarms
            self._active_alarms[alarm_id] = alarm_instance

            # Trigger event handlers
            for handler in self._alarm_handlers:
                try:
                    await handler("created", alarm_instance)
                except Exception as e:
                    logger.error(f"Alarm handler error: {e}")

            # Schedule initial notification
            await self._schedule_notification(alarm_instance)

            logger.warning(
                f"🚨 Alarm created: {definition.name} ({definition.priority.name})"
            )

            return {
                "success": True,
                "alarm_id": alarm_id,
                "state": alarm_instance.state.value,
                "priority": alarm_instance.priority.name,
                "created_at": alarm_instance.created_at.isoformat(),
            }

        except Exception as e:
            error_msg = format_alarm_error(e, f"alarm creation ({alarm_id})")
            logger.error(f"❌ Alarm creation failed: {error_msg}")
            return {"success": False, "error": error_msg}

    async def acknowledge_alarm(
        self, alarm_id: str, user: str, comment: str = ""
    ) -> dict[str, Any]:
        """Acknowledge active alarm."""
        if alarm_id not in self._active_alarms:
            return {"success": False, "error": "Alarm not found or not active"}

        try:
            alarm = self._active_alarms[alarm_id]

            if alarm.state == AlarmState.ACKNOWLEDGED:
                return {"success": False, "error": "Alarm already acknowledged"}

            # Update alarm state
            alarm.state = AlarmState.ACKNOWLEDGED
            alarm.acknowledged_at = datetime.now()
            alarm.acknowledged_by = user
            alarm.acknowledgment_comment = comment
            alarm.last_updated = datetime.now()

            # Trigger event handlers
            for handler in self._alarm_handlers:
                try:
                    await handler("acknowledged", alarm)
                except Exception as e:
                    logger.error(f"Alarm handler error: {e}")

            logger.info(f"✅ Alarm acknowledged: {alarm.definition.name} by {user}")

            return {
                "success": True,
                "alarm_id": alarm_id,
                "acknowledged_by": user,
                "acknowledged_at": alarm.acknowledged_at.isoformat(),
            }

        except Exception as e:
            error_msg = format_alarm_error(e, f"alarm acknowledgment ({alarm_id})")
            return {"success": False, "error": error_msg}

    async def clear_alarm(self, alarm_id: str, user: str = "system") -> dict[str, Any]:
        """Clear active alarm."""
        if alarm_id not in self._active_alarms:
            return {"success": False, "error": "Alarm not found or not active"}

        try:
            alarm = self._active_alarms[alarm_id]

            # Update alarm state
            alarm.state = AlarmState.CLEARED
            alarm.cleared_at = datetime.now()
            alarm.last_updated = datetime.now()

            # Move to history
            self._alarm_history.append(alarm)
            del self._active_alarms[alarm_id]

            # Trigger event handlers
            for handler in self._alarm_handlers:
                try:
                    await handler("cleared", alarm)
                except Exception as e:
                    logger.error(f"Alarm handler error: {e}")

            logger.info(f"✅ Alarm cleared: {alarm.definition.name}")

            return {
                "success": True,
                "alarm_id": alarm_id,
                "cleared_at": alarm.cleared_at.isoformat(),
            }

        except Exception as e:
            error_msg = format_alarm_error(e, f"alarm clearing ({alarm_id})")
            return {"success": False, "error": error_msg}

    async def suppress_alarm(self, alarm_id: str, user: str) -> dict[str, Any]:
        """Suppress alarm notifications."""
        if alarm_id not in self._active_alarms:
            return {"success": False, "error": "Alarm not found or not active"}

        try:
            alarm = self._active_alarms[alarm_id]

            if not alarm.definition.suppression_enabled:
                return {
                    "success": False,
                    "error": "Alarm suppression not enabled for this alarm",
                }

            # Update alarm state
            alarm.state = AlarmState.SUPPRESSED
            alarm.last_updated = datetime.now()

            # Add to suppressed set
            self._suppressed_alarms.add(alarm_id)

            logger.info(f"🔇 Alarm suppressed: {alarm.definition.name} by {user}")

            return {
                "success": True,
                "alarm_id": alarm_id,
                "suppressed_by": user,
            }

        except Exception as e:
            error_msg = format_alarm_error(e, f"alarm suppression ({alarm_id})")
            return {"success": False, "error": error_msg}

    async def _schedule_notification(self, alarm: AlarmInstance) -> None:
        """Schedule notification for alarm."""
        # Find matching notification rules
        matching_rules = []
        for rule in self.config.notification_rules:
            if alarm.priority in rule.alarm_priorities:
                if (
                    not rule.alarm_categories
                    or alarm.definition.category in rule.alarm_categories
                ):
                    matching_rules.append(rule)

        # Schedule notifications for matching rules
        for rule in matching_rules:
            asyncio.create_task(self._send_notifications(alarm, rule))

    async def _send_notifications(
        self, alarm: AlarmInstance, rule: NotificationRule
    ) -> None:
        """Send notifications for alarm based on rule."""
        try:
            # Apply initial delay
            if rule.initial_delay_minutes > 0:
                await asyncio.sleep(rule.initial_delay_minutes * 60)

            # Send notifications
            for method in rule.notification_methods:
                if method in self._notification_handlers:
                    try:
                        await self._notification_handlers[method](alarm, rule)
                        alarm.notifications_sent += 1
                        alarm.last_notification = datetime.now()
                    except Exception as e:
                        logger.error(
                            f"Notification sending error ({method.value}): {e}"
                        )

        except Exception as e:
            logger.error(f"Notification scheduling error: {e}")

    async def _send_email_notification(
        self, alarm: AlarmInstance, rule: NotificationRule
    ) -> None:
        """Send email notification."""
        # In real implementation, this would send actual emails
        logger.info(f"📧 Email notification sent for alarm: {alarm.definition.name}")

    async def _send_sms_notification(
        self, alarm: AlarmInstance, rule: NotificationRule
    ) -> None:
        """Send SMS notification."""
        # In real implementation, this would send actual SMS
        logger.info(f"📱 SMS notification sent for alarm: {alarm.definition.name}")

    async def _send_push_notification(
        self, alarm: AlarmInstance, rule: NotificationRule
    ) -> None:
        """Send push notification."""
        # In real implementation, this would send actual push notifications
        logger.info(f"📲 Push notification sent for alarm: {alarm.definition.name}")

    async def _send_webhook_notification(
        self, alarm: AlarmInstance, rule: NotificationRule
    ) -> None:
        """Send webhook notification."""
        # In real implementation, this would send actual webhooks
        logger.info(f"🔗 Webhook notification sent for alarm: {alarm.definition.name}")

    async def _send_voice_notification(
        self, alarm: AlarmInstance, rule: NotificationRule
    ) -> None:
        """Send voice notification."""
        # In real implementation, this would make actual voice calls
        logger.info(f"📞 Voice notification sent for alarm: {alarm.definition.name}")

    async def _process_escalations(self) -> None:
        """Process alarm escalations."""
        if not self.config.enable_escalation:
            return

        current_time = datetime.now()

        for alarm in self._active_alarms.values():
            if alarm.state != AlarmState.ACTIVE:
                continue

            # Check escalation timeout
            time_since_created = (current_time - alarm.created_at).total_seconds() / 60
            if time_since_created >= alarm.definition.escalation_timeout_minutes:
                await self._escalate_alarm(alarm)

    async def _escalate_alarm(self, alarm: AlarmInstance) -> None:
        """Escalate alarm to higher priority or next level."""
        try:
            alarm.escalation_level += 1
            alarm.last_updated = datetime.now()

            # Find escalation rules and send additional notifications
            for rule in self.config.notification_rules:
                if alarm.priority in rule.alarm_priorities and rule.escalation_levels:
                    if alarm.escalation_level <= len(rule.escalation_levels):
                        escalation_config = rule.escalation_levels[
                            alarm.escalation_level - 1
                        ]
                        # Process escalation configuration
                        logger.warning(
                            f"⬆️ Alarm escalated: {alarm.definition.name} (Level {alarm.escalation_level})"
                        )

        except Exception as e:
            logger.error(f"Alarm escalation error: {e}")

    async def _process_notifications(self) -> None:
        """Process pending notifications."""
        # Implementation for processing notification queue
        pass

    async def _update_analytics(self) -> None:
        """Update alarm analytics."""
        try:
            # Update basic statistics
            self._alarm_statistics["total_alarms"] = len(self._active_alarms) + len(
                self._alarm_history
            )
            self._alarm_statistics["active_alarms"] = len(self._active_alarms)
            self._alarm_statistics["acknowledged_alarms"] = len(
                [
                    a
                    for a in self._active_alarms.values()
                    if a.state == AlarmState.ACKNOWLEDGED
                ]
            )
            self._alarm_statistics["suppressed_alarms"] = len(self._suppressed_alarms)

            # Update priority distribution
            for alarm in self._active_alarms.values():
                self._alarm_statistics["by_priority"][alarm.priority.name] += 1

            # Calculate average resolution time
            resolved_alarms = [a for a in self._alarm_history if a.cleared_at]
            if resolved_alarms:
                resolution_times = [
                    (a.cleared_at - a.created_at).total_seconds() / 60
                    for a in resolved_alarms
                    if a.cleared_at
                ]
                self._alarm_statistics["average_resolution_time"] = sum(
                    resolution_times
                ) / len(resolution_times)

            # Calculate escalation rate
            escalated_alarms = len(
                [a for a in self._active_alarms.values() if a.escalation_level > 0]
            )
            total_alarms = len(self._active_alarms)
            self._alarm_statistics["escalation_rate"] = (
                (escalated_alarms / total_alarms * 100) if total_alarms > 0 else 0.0
            )

        except Exception as e:
            logger.error(f"Analytics update error: {e}")

    async def _cleanup_old_alarms(self) -> None:
        """Clean up old alarm history."""
        cutoff_time = datetime.now() - timedelta(days=self.config.alarm_retention_days)

        self._alarm_history = [
            alarm
            for alarm in self._alarm_history
            if alarm.cleared_at and alarm.cleared_at > cutoff_time
        ]

    def add_alarm_handler(self, handler: Callable) -> None:
        """Add alarm event handler."""
        self._alarm_handlers.append(handler)

    def get_status(self) -> dict[str, Any]:
        """Get alarm manager status."""
        return {
            "initialized": self._initialized,
            "processing_active": self._processing_active,
            "system_name": self.config.system_name,
            "active_alarms": len(self._active_alarms),
            "suppressed_alarms": len(self._suppressed_alarms),
            "alarm_history": len(self._alarm_history),
            "statistics": self._alarm_statistics.copy(),
        }

    def get_active_alarms(self) -> list[dict[str, Any]]:
        """Get list of active alarms."""
        return [
            {
                "alarm_id": alarm.alarm_id,
                "name": alarm.definition.name,
                "priority": alarm.priority.name,
                "state": alarm.state.value,
                "created_at": alarm.created_at.isoformat(),
                "source_description": alarm.source_description,
                "acknowledged_by": alarm.acknowledged_by,
                "escalation_level": alarm.escalation_level,
            }
            for alarm in self._active_alarms.values()
        ]

    # Step 6: Resource Management (crawl_mcp.py methodology)
    @asynccontextmanager
    async def managed_alarm_session(self) -> AsyncIterator["ProductionAlarmManager"]:
        """Manage alarm management session with proper cleanup."""
        try:
            # Initialize alarm manager
            init_result = await self.initialize()
            if not init_result["success"]:
                raise RuntimeError(
                    f"Alarm manager initialization failed: {init_result['error']}"
                )

            logger.info("🚨 Alarm management session started")
            yield self

        finally:
            # Cleanup resources
            await self.cleanup()
            logger.info("🧹 Alarm management session cleanup completed")

    async def cleanup(self) -> None:
        """Clean up alarm manager resources."""
        try:
            # Stop processing
            if self._processing_task:
                self._processing_active = False
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass

            # Clear data structures
            self._active_alarms.clear()
            self._alarm_history.clear()
            self._suppressed_alarms.clear()
            self._alarm_handlers.clear()
            self._notification_handlers.clear()

            # Reset state
            self._initialized = False
            self._processing_active = False

            logger.info("✅ Alarm manager cleanup completed")

        except Exception as e:
            logger.error(f"❌ Alarm manager cleanup error: {e}")


# Step 4: Modular Testing (crawl_mcp.py methodology)
async def test_alarm_manager() -> dict[str, Any]:
    """Test alarm management functionality."""
    start_time = datetime.now()

    try:
        # Create test configuration
        test_config = AlarmConfiguration(
            system_name="Test Alarm Manager",
            alarm_definitions=[
                AlarmDefinition(
                    alarm_id="test_alarm_1",
                    name="Test High Temperature",
                    description="Temperature exceeds safe limits",
                    priority=AlarmPriority.HIGH,
                    category="temperature",
                    source_system="test_system",
                ),
                AlarmDefinition(
                    alarm_id="test_alarm_2",
                    name="Test Critical Pressure",
                    description="Pressure in critical range",
                    priority=AlarmPriority.CRITICAL,
                    category="pressure",
                    source_system="test_system",
                ),
            ],
            notification_rules=[
                NotificationRule(
                    rule_id="test_rule_1",
                    name="High Priority Notifications",
                    alarm_priorities=[AlarmPriority.HIGH, AlarmPriority.CRITICAL],
                    notification_methods=[NotificationMethod.EMAIL],
                    recipients=["test@example.com"],
                ),
            ],
        )

        # Test alarm manager
        manager = ProductionAlarmManager(config=test_config)

        async with manager.managed_alarm_session():
            # Test alarm creation
            result1 = await manager.create_alarm(
                "test_alarm_1",
                source_value=95.0,
                source_description="High temperature detected",
            )
            if not result1["success"]:
                raise RuntimeError(f"Alarm creation failed: {result1['error']}")

            # Test alarm acknowledgment
            result2 = await manager.acknowledge_alarm(
                "test_alarm_1", "test_user", "Investigating high temperature"
            )
            if not result2["success"]:
                raise RuntimeError(f"Alarm acknowledgment failed: {result2['error']}")

            # Test alarm clearing
            result3 = await manager.clear_alarm("test_alarm_1", "test_user")
            if not result3["success"]:
                raise RuntimeError(f"Alarm clearing failed: {result3['error']}")

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "success": True,
            "execution_time": execution_time,
            "tests_passed": [
                "alarm_creation",
                "alarm_acknowledgment",
                "alarm_clearing",
            ],
        }

    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        return {
            "success": False,
            "execution_time": execution_time,
            "error": str(e),
        }


# Main execution for testing
if __name__ == "__main__":

    async def main():
        logger.info("🧪 Testing Production Alarm Manager")
        test_result = await test_alarm_manager()

        if test_result["success"]:
            logger.info(f"✅ Test passed in {test_result['execution_time']:.2f}s")
        else:
            logger.error(f"❌ Test failed: {test_result['error']}")

    asyncio.run(main())
