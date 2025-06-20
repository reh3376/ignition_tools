"""Enhanced wrapper for Ignition system.alarm functions."""

from typing import Any

from .wrapper_base import IgnitionWrapperBase, WrapperError, system, wrapper_function


class SystemAlarmWrapper(IgnitionWrapperBase):
    """Enhanced wrapper for system.alarm functions."""

    def get_wrapped_functions(self) -> list[str]:
        """Get list of wrapped alarm functions."""
        return ["acknowledge", "query_status", "shelve", "unshelve"]

    @wrapper_function
    def acknowledge(self, alarm_ids: str | list[str], notes: str = "") -> dict[str, Any]:
        """Enhanced alarm acknowledgment with validation and logging."""
        if self.config.validate_inputs:
            if isinstance(alarm_ids, str):
                alarm_ids = [alarm_ids]
            if not isinstance(alarm_ids, list):
                raise WrapperError("Alarm IDs must be a string or list of strings")
            if not isinstance(notes, str):
                raise WrapperError("Notes must be a string")

        try:
            success = system.alarm.acknowledge(alarm_ids, notes)

            result = {
                "action": "acknowledge",
                "alarm_ids": alarm_ids,
                "notes": notes,
                "success": success,
            }

            self._log_operation(
                "Alarms acknowledged",
                f"Count: {len(alarm_ids)}, Notes: {notes[:50]}...",
            )
            return result

        except Exception as e:
            raise WrapperError(f"Alarm acknowledgment failed: {e}", original_error=e) from e

    @wrapper_function
    def query_status(self, priority: int | None = None, state: str | None = None) -> dict[str, Any]:
        """Enhanced alarm status query with filtering."""
        try:
            alarms = system.alarm.queryStatus(priority=priority, state=state)

            result = {
                "action": "query_status",
                "filters": {"priority": priority, "state": state},
                "alarm_count": len(alarms) if alarms else 0,
                "alarms": alarms,
                "success": True,
            }

            self._log_operation("Alarm status queried", f"Found {len(alarms) if alarms else 0} alarms")
            return result

        except Exception as e:
            raise WrapperError(f"Alarm status query failed: {e}", original_error=e) from e
