"""Module lifecycle management for Ignition modules."""

from collections.abc import Callable
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .abstract_module import AbstractIgnitionModule


class ModuleState(Enum):
    """Enumeration of module lifecycle states."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class LifecycleEvent:
    """Represents a module lifecycle event."""

    def __init__(
        self,
        event_type: str,
        timestamp: datetime,
        old_state: ModuleState,
        new_state: ModuleState,
        data: dict[str, Any] | None = None,
    ):
        """Initialize lifecycle event.

        Args:
            event_type: Type of lifecycle event
            timestamp: When the event occurred
            old_state: Previous module state
            new_state: New module state
            data: Additional event data
        """
        self.event_type = event_type
        self.timestamp = timestamp
        self.old_state = old_state
        self.new_state = new_state
        self.data = data or {}

    def __str__(self) -> str:
        """String representation of the event."""
        return f"{self.timestamp}: {self.event_type} ({self.old_state.value} -> {self.new_state.value})"


class ModuleLifecycleManager:
    """Manages the lifecycle of an Ignition module.

    This class provides comprehensive lifecycle management including state tracking,
    event handling, health monitoring, and automatic recovery capabilities.
    """

    def __init__(self, module: "AbstractIgnitionModule"):
        """Initialize the lifecycle manager.

        Args:
            module: The module instance to manage
        """
        self._module = module
        self._start_time: datetime | None = None
        self._uptime: timedelta = timedelta()
        self._restart_count = 0
        self._error_count = 0
        self._last_error: str | None = None
        self._last_error_time: datetime | None = None

        # Event tracking
        self._events: list[LifecycleEvent] = []
        self._max_events = 1000  # Keep last 1000 events

        # State change callbacks
        self._state_change_callbacks: list[
            Callable[[ModuleState, ModuleState], None]
        ] = []

        # Health monitoring
        self._health_check_interval = 60  # seconds
        self._last_health_check: datetime | None = None
        self._health_status = "unknown"

        # Auto-recovery settings
        self._auto_recovery_enabled = True
        self._max_restart_attempts = 3
        self._restart_delay = 5  # seconds

        # Performance metrics
        self._performance_metrics: dict[str, Any] = {
            "startup_time": None,
            "shutdown_time": None,
            "average_startup_time": None,
            "memory_usage": None,
            "cpu_usage": None,
        }

    # Properties

    @property
    def start_time(self) -> datetime | None:
        """Get module start time."""
        return self._start_time

    @property
    def uptime(self) -> timedelta:
        """Get module uptime."""
        if self._start_time and self._module.state == ModuleState.RUNNING:
            return datetime.now() - self._start_time + self._uptime
        return self._uptime

    @property
    def restart_count(self) -> int:
        """Get number of restarts."""
        return self._restart_count

    @property
    def error_count(self) -> int:
        """Get number of errors."""
        return self._error_count

    @property
    def last_error(self) -> str | None:
        """Get last error message."""
        return self._last_error

    @property
    def health_status(self) -> str:
        """Get current health status."""
        return self._health_status

    @property
    def events(self) -> list[LifecycleEvent]:
        """Get lifecycle events."""
        return self._events.copy()

    @property
    def performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        return self._performance_metrics.copy()

    # State change handling

    def on_state_changed(self, old_state: ModuleState, new_state: ModuleState):
        """Handle module state change.

        Args:
            old_state: Previous state
            new_state: New state
        """
        # Record event
        event = LifecycleEvent(
            event_type="state_change",
            timestamp=datetime.now(),
            old_state=old_state,
            new_state=new_state,
        )
        self._add_event(event)

        # Update lifecycle tracking
        self._update_lifecycle_tracking(old_state, new_state)

        # Notify callbacks
        for callback in self._state_change_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                self._module.logger.exception(f"State change callback failed: {e}")

        # Handle specific state transitions
        if new_state == ModuleState.RUNNING:
            self._on_module_started()
        elif new_state == ModuleState.STOPPED:
            self._on_module_stopped()
        elif new_state == ModuleState.ERROR:
            self._on_module_error()

    def add_state_change_callback(
        self, callback: Callable[[ModuleState, ModuleState], None]
    ):
        """Add a state change callback.

        Args:
            callback: Function to call on state changes
        """
        self._state_change_callbacks.append(callback)

    def remove_state_change_callback(
        self, callback: Callable[[ModuleState, ModuleState], None]
    ):
        """Remove a state change callback.

        Args:
            callback: Function to remove
        """
        if callback in self._state_change_callbacks:
            self._state_change_callbacks.remove(callback)

    # Event management

    def _add_event(self, event: LifecycleEvent):
        """Add an event to the history.

        Args:
            event: Event to add
        """
        self._events.append(event)

        # Trim events if we exceed the maximum
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events :]

    def get_events_since(self, since: datetime) -> list[LifecycleEvent]:
        """Get events since a specific time.

        Args:
            since: Get events after this time

        Returns:
            List of events since the specified time
        """
        return [event for event in self._events if event.timestamp >= since]

    def get_events_by_type(self, event_type: str) -> list[LifecycleEvent]:
        """Get events of a specific type.

        Args:
            event_type: Type of events to retrieve

        Returns:
            List of events of the specified type
        """
        return [event for event in self._events if event.event_type == event_type]

    # Lifecycle tracking

    def _update_lifecycle_tracking(
        self, old_state: ModuleState, new_state: ModuleState
    ):
        """Update lifecycle tracking metrics.

        Args:
            old_state: Previous state
            new_state: New state
        """
        now = datetime.now()

        if new_state == ModuleState.RUNNING and old_state in [
            ModuleState.STARTING,
            ModuleState.INITIALIZING,
        ]:
            self._start_time = now

            # Calculate startup time
            startup_events = [
                e for e in self._events if e.new_state == ModuleState.INITIALIZING
            ]
            if startup_events:
                startup_time = (now - startup_events[-1].timestamp).total_seconds()
                self._performance_metrics["startup_time"] = startup_time

                # Update average startup time
                if self._performance_metrics["average_startup_time"] is None:
                    self._performance_metrics["average_startup_time"] = startup_time
                else:
                    current_avg = self._performance_metrics["average_startup_time"]
                    self._performance_metrics["average_startup_time"] = (
                        current_avg + startup_time
                    ) / 2

        elif new_state == ModuleState.STOPPED and old_state == ModuleState.STOPPING:
            if self._start_time:
                self._uptime += now - self._start_time
                self._start_time = None

            # Calculate shutdown time
            shutdown_events = [
                e for e in self._events if e.new_state == ModuleState.STOPPING
            ]
            if shutdown_events:
                shutdown_time = (now - shutdown_events[-1].timestamp).total_seconds()
                self._performance_metrics["shutdown_time"] = shutdown_time

        elif new_state == ModuleState.ERROR:
            self._error_count += 1
            self._last_error = self._module.error_state
            self._last_error_time = now

    def _on_module_started(self):
        """Handle module started event."""
        self._module.logger.info("Module lifecycle: Started successfully")
        self._health_status = "healthy"
        self._last_health_check = datetime.now()

    def _on_module_stopped(self):
        """Handle module stopped event."""
        self._module.logger.info("Module lifecycle: Stopped successfully")
        self._health_status = "stopped"

    def _on_module_error(self):
        """Handle module error event."""
        self._module.logger.error(
            f"Module lifecycle: Error occurred - {self._last_error}"
        )
        self._health_status = "error"

        # Attempt auto-recovery if enabled
        if (
            self._auto_recovery_enabled
            and self._restart_count < self._max_restart_attempts
        ):
            self._schedule_auto_recovery()

    # Health monitoring

    def check_health(self) -> dict[str, Any]:
        """Perform health check on the module.

        Returns:
            Dictionary containing health status information
        """
        now = datetime.now()
        self._last_health_check = now

        health_data = {
            "status": self._health_status,
            "state": self._module.state.value,
            "uptime": self.uptime.total_seconds(),
            "restart_count": self._restart_count,
            "error_count": self._error_count,
            "last_error": self._last_error,
            "last_error_time": (
                self._last_error_time.isoformat() if self._last_error_time else None
            ),
            "check_time": now.isoformat(),
        }

        # Determine overall health status
        if self._module.state == ModuleState.RUNNING:
            if self._error_count == 0:
                self._health_status = "healthy"
            elif self._error_count < 5:
                self._health_status = "warning"
            else:
                self._health_status = "unhealthy"
        elif self._module.state == ModuleState.ERROR:
            self._health_status = "error"
        elif self._module.state == ModuleState.STOPPED:
            self._health_status = "stopped"
        else:
            self._health_status = "transitioning"

        health_data["status"] = self._health_status
        return health_data

    def is_healthy(self) -> bool:
        """Check if the module is healthy.

        Returns:
            True if module is healthy, False otherwise
        """
        return self._health_status in ["healthy", "warning"]

    # Auto-recovery

    def _schedule_auto_recovery(self):
        """Schedule automatic recovery attempt."""
        if self._restart_count >= self._max_restart_attempts:
            self._module.logger.error(
                f"Maximum restart attempts ({self._max_restart_attempts}) reached. Auto-recovery disabled."
            )
            self._auto_recovery_enabled = False
            return

        self._module.logger.info(
            f"Scheduling auto-recovery attempt {self._restart_count + 1} in {self._restart_delay} seconds"
        )

        # In a real implementation, this would use a timer or scheduler
        # For now, we'll just log the intent
        self._restart_count += 1

    def enable_auto_recovery(self, max_attempts: int = 3, delay: int = 5):
        """Enable automatic recovery.

        Args:
            max_attempts: Maximum number of restart attempts
            delay: Delay between restart attempts in seconds
        """
        self._auto_recovery_enabled = True
        self._max_restart_attempts = max_attempts
        self._restart_delay = delay
        self._restart_count = 0  # Reset count when re-enabling

        self._module.logger.info(
            f"Auto-recovery enabled: max_attempts={max_attempts}, delay={delay}s"
        )

    def disable_auto_recovery(self):
        """Disable automatic recovery."""
        self._auto_recovery_enabled = False
        self._module.logger.info("Auto-recovery disabled")

    # Statistics and reporting

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive lifecycle statistics.

        Returns:
            Dictionary containing lifecycle statistics
        """
        return {
            "module_name": self._module.metadata.name,
            "module_version": self._module.metadata.version,
            "current_state": self._module.state.value,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "uptime_seconds": self.uptime.total_seconds(),
            "uptime_formatted": str(self.uptime),
            "restart_count": self._restart_count,
            "error_count": self._error_count,
            "last_error": self._last_error,
            "last_error_time": (
                self._last_error_time.isoformat() if self._last_error_time else None
            ),
            "health_status": self._health_status,
            "last_health_check": (
                self._last_health_check.isoformat() if self._last_health_check else None
            ),
            "auto_recovery_enabled": self._auto_recovery_enabled,
            "max_restart_attempts": self._max_restart_attempts,
            "event_count": len(self._events),
            "performance_metrics": self._performance_metrics,
        }

    def get_uptime_report(self) -> dict[str, Any]:
        """Get detailed uptime report.

        Returns:
            Dictionary containing uptime analysis
        """
        total_uptime = self.uptime.total_seconds()

        # Calculate availability percentage (assuming 24/7 operation)
        now = datetime.now()
        first_event = self._events[0] if self._events else None
        if first_event:
            total_time = (now - first_event.timestamp).total_seconds()
            availability = (total_uptime / total_time) * 100 if total_time > 0 else 0
        else:
            availability = 0

        return {
            "total_uptime_seconds": total_uptime,
            "total_uptime_formatted": str(self.uptime),
            "availability_percentage": round(availability, 2),
            "restart_count": self._restart_count,
            "error_count": self._error_count,
            "mean_time_between_failures": (
                total_uptime / self._error_count if self._error_count > 0 else None
            ),
            "average_startup_time": self._performance_metrics.get(
                "average_startup_time"
            ),
            "last_startup_time": self._performance_metrics.get("startup_time"),
            "last_shutdown_time": self._performance_metrics.get("shutdown_time"),
        }

    def reset_statistics(self):
        """Reset all lifecycle statistics."""
        self._restart_count = 0
        self._error_count = 0
        self._last_error = None
        self._last_error_time = None
        self._events.clear()
        self._performance_metrics = {
            "startup_time": None,
            "shutdown_time": None,
            "average_startup_time": None,
            "memory_usage": None,
            "cpu_usage": None,
        }

        self._module.logger.info("Lifecycle statistics reset")

    def __str__(self) -> str:
        """String representation of the lifecycle manager."""
        return f"LifecycleManager({self._module.metadata.name}, {self._module.state.value})"

    def __repr__(self) -> str:
        """Detailed string representation of the lifecycle manager."""
        return (
            f"ModuleLifecycleManager(module='{self._module.metadata.name}', "
            f"state='{self._module.state.value}', uptime={self.uptime}, "
            f"restarts={self._restart_count}, errors={self._error_count})"
        )
