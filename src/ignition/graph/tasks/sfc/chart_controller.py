"""SFC Chart Controller.

Manages Sequential Function Chart operations including start, stop, pause, resume, and reset.
Provides comprehensive chart lifecycle management for industrial automation.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class SFCChartController:
    """Sequential Function Chart Controller.

    Manages SFC chart lifecycle operations including execution control,
    status monitoring, and step management for industrial automation systems.
    """

    def __init__(self) -> bool:
        """Initialize the SFC Chart Controller."""
        self.logger = logging.getLogger(__name__)
        self.active_charts: dict[str, dict[str, Any]] = {}

    def start_chart(self, chart_path: str, initial_variables: dict[str, Any] | None = None) -> bool:
        """Start execution of an SFC chart.

        Args:
            chart_path: Path to the SFC chart
            initial_variables: Initial variable values for the chart

        Returns:
            bool: True if chart started successfully
        """
        try:
            self.logger.info(f"Starting SFC chart: {chart_path}")

            # Validate chart path
            if not self._validate_chart_path(chart_path):
                self.logger.error(f"Invalid chart path: {chart_path}")
                return False

            # Check if chart is already running
            if chart_path in self.active_charts:
                self.logger.warning(f"Chart already running: {chart_path}")
                return False

            # Initialize chart execution
            execution_id = str(uuid.uuid4())
            chart_data = {
                "execution_id": execution_id,
                "chart_path": chart_path,
                "status": "running",
                "start_time": datetime.now(),
                "current_step": "initial",
                "variables": initial_variables or {},
                "step_history": [],
            }

            self.active_charts[chart_path] = chart_data
            self.logger.info(f"SFC chart started successfully: {chart_path} (ID: {execution_id})")
            return True

        except Exception as e:
            self.logger.error(f"Error starting SFC chart {chart_path}: {e}")
            return False

    def stop_chart(self, chart_path: str, force_stop: bool = False) -> bool:
        """Stop execution of an SFC chart.

        Args:
            chart_path: Path to the SFC chart
            force_stop: Force immediate stop without cleanup

        Returns:
            bool: True if chart stopped successfully
        """
        try:
            self.logger.info(f"Stopping SFC chart: {chart_path} (force: {force_stop})")

            if chart_path not in self.active_charts:
                self.logger.warning(f"Chart not running: {chart_path}")
                return False

            chart_data = self.active_charts[chart_path]

            if force_stop:
                # Immediate stop
                chart_data["status"] = "stopped"
                chart_data["stop_time"] = datetime.now()
            else:
                # Graceful stop - complete current step
                chart_data["status"] = "stopping"
                chart_data["stop_requested"] = datetime.now()

            self.logger.info(f"SFC chart stopped: {chart_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping SFC chart {chart_path}: {e}")
            return False

    def pause_chart(self, chart_path: str, safe_pause: bool = True) -> bool:
        """Pause execution of an SFC chart.

        Args:
            chart_path: Path to the SFC chart
            safe_pause: Pause only at safe points

        Returns:
            bool: True if chart paused successfully
        """
        try:
            self.logger.info(f"Pausing SFC chart: {chart_path} (safe: {safe_pause})")

            if chart_path not in self.active_charts:
                self.logger.warning(f"Chart not running: {chart_path}")
                return False

            chart_data = self.active_charts[chart_path]

            if chart_data["status"] != "running":
                self.logger.warning(f"Chart not in running state: {chart_path}")
                return False

            chart_data["status"] = "paused"
            chart_data["pause_time"] = datetime.now()
            chart_data["safe_pause"] = safe_pause

            self.logger.info(f"SFC chart paused: {chart_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error pausing SFC chart {chart_path}: {e}")
            return False

    def resume_chart(self, chart_path: str) -> bool:
        """Resume execution of a paused SFC chart.

        Args:
            chart_path: Path to the SFC chart

        Returns:
            bool: True if chart resumed successfully
        """
        try:
            self.logger.info(f"Resuming SFC chart: {chart_path}")

            if chart_path not in self.active_charts:
                self.logger.warning(f"Chart not found: {chart_path}")
                return False

            chart_data = self.active_charts[chart_path]

            if chart_data["status"] != "paused":
                self.logger.warning(f"Chart not paused: {chart_path}")
                return False

            chart_data["status"] = "running"
            chart_data["resume_time"] = datetime.now()

            # Calculate pause duration
            if "pause_time" in chart_data:
                pause_duration = datetime.now() - chart_data["pause_time"]
                chart_data["total_pause_time"] = chart_data.get("total_pause_time", 0) + pause_duration.total_seconds()

            self.logger.info(f"SFC chart resumed: {chart_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error resuming SFC chart {chart_path}: {e}")
            return False

    def reset_chart(self, chart_path: str) -> bool:
        """Reset an SFC chart to initial state.

        Args:
            chart_path: Path to the SFC chart

        Returns:
            bool: True if chart reset successfully
        """
        try:
            self.logger.info(f"Resetting SFC chart: {chart_path}")

            if chart_path in self.active_charts:
                # Remove from active charts
                del self.active_charts[chart_path]

            self.logger.info(f"SFC chart reset: {chart_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error resetting SFC chart {chart_path}: {e}")
            return False

    def get_chart_status(self, chart_path: str) -> dict[str, Any] | None:
        """Get current status of an SFC chart.

        Args:
            chart_path: Path to the SFC chart

        Returns:
            dict containing chart status information
        """
        try:
            if chart_path not in self.active_charts:
                return None

            chart_data = self.active_charts[chart_path].copy()

            # Calculate runtime
            if "start_time" in chart_data:
                runtime = datetime.now() - chart_data["start_time"]
                chart_data["runtime_seconds"] = runtime.total_seconds()

            return chart_data

        except Exception as e:
            self.logger.error(f"Error getting chart status {chart_path}: {e}")
            return None

    def get_current_step(self, chart_path: str) -> str | None:
        """Get the currently active step of an SFC chart.

        Args:
            chart_path: Path to the SFC chart

        Returns:
            Current step name or None if not found
        """
        try:
            if chart_path in self.active_charts:
                return self.active_charts[chart_path].get("current_step")
            return None

        except Exception as e:
            self.logger.error(f"Error getting current step {chart_path}: {e}")
            return None

    def get_step_history(self, chart_path: str) -> list[dict[str, Any]]:
        """Get execution history of steps for an SFC chart.

        Args:
            chart_path: Path to the SFC chart

        Returns:
            list of step execution history
        """
        try:
            if chart_path in self.active_charts:
                return self.active_charts[chart_path].get("step_history", [])
            return []

        except Exception as e:
            self.logger.error(f"Error getting step history {chart_path}: {e}")
            return []

    def _validate_chart_path(self, chart_path: str) -> bool:
        """Validate SFC chart path.

        Args:
            chart_path: Path to validate

        Returns:
            bool: True if path is valid
        """
        if not chart_path or not isinstance(chart_path, str):
            return False

        # Basic path validation
        if len(chart_path.strip()) == 0:
            return False

        # Additional validation logic would go here
        # (e.g., check if chart exists in Ignition)

        return True
