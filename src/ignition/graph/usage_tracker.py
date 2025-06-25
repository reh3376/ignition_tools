"""Usage Tracking System for Learning Enhancement.

This module implements usage pattern tracking for the Ignition Graph Database
learning system. It collects, stores, and analyzes usage patterns to improve
recommendations and user experience.
"""

import logging
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from .client import IgnitionGraphClient

logger = logging.getLogger(__name__)


class UsageTracker:
    """Tracks user interactions and usage patterns for machine learning."""

    def __init__(self, client: IgnitionGraphClient):
        """Initialize usage tracker with graph client.

        Args:
            client: IgnitionGraphClient instance for database operations
        """
        self.client = client
        self.current_session_id: str | None = None
        self.session_start_time: datetime | None = None
        self.session_events: list[dict[str, Any]] = []

    def start_session(
        self, user_id: str | None = None, session_type: str = "exploration"
    ) -> str:
        """Start a new usage tracking session.

        Args:
            user_id: Optional user identifier
            session_type: Type of session (exploration, development, debugging)

        Returns:
            Session ID for the started session
        """
        session_id = str(uuid.uuid4())
        self.current_session_id = session_id
        self.session_start_time = datetime.now()
        self.session_events = []

        # Create session node in database
        session_query = """
        CREATE (s:UserSession {
            id: $session_id,
            user_id: $user_id,
            start_time: datetime($start_time),
            session_type: $session_type,
            event_count: 0,
            unique_functions: 0,
            unique_templates: 0
        })
        """

        self.client.execute_write_query(
            session_query,
            {
                "session_id": session_id,
                "user_id": user_id,
                "start_time": self.session_start_time.isoformat(),
                "session_type": session_type,
            },
        )

        logger.info(f"Started usage tracking session: {session_id}")
        return session_id

    def end_session(self) -> dict[str, Any] | None:
        """End the current usage tracking session.

        Returns:
            Session summary dictionary or None if no active session
        """
        if not self.current_session_id or not self.session_start_time:
            logger.warning("No active session to end")
            return None

        end_time = datetime.now()
        duration = int((end_time - self.session_start_time).total_seconds())

        # Calculate session statistics
        unique_functions = len(
            {
                event.get("function_name")
                for event in self.session_events
                if event.get("function_name")
            }
        )

        unique_templates = len(
            {
                event.get("template_name")
                for event in self.session_events
                if event.get("template_name")
            }
        )

        success_events = sum(
            1 for event in self.session_events if event.get("success", True)
        )
        success_rate = (
            success_events / len(self.session_events) if self.session_events else 1.0
        )

        # Update session node with final statistics
        update_query = """
        MATCH (s:UserSession {id: $session_id})
        SET s.end_time = datetime($end_time),
            s.duration = $duration,
            s.event_count = $event_count,
            s.success_rate = $success_rate,
            s.unique_functions = $unique_functions,
            s.unique_templates = $unique_templates
        """

        self.client.execute_write_query(
            update_query,
            {
                "session_id": self.current_session_id,
                "end_time": end_time.isoformat(),
                "duration": duration,
                "event_count": len(self.session_events),
                "success_rate": success_rate,
                "unique_functions": unique_functions,
                "unique_templates": unique_templates,
            },
        )

        session_summary = {
            "session_id": self.current_session_id,
            "duration": duration,
            "event_count": len(self.session_events),
            "success_rate": success_rate,
            "unique_functions": unique_functions,
            "unique_templates": unique_templates,
        }

        logger.info(f"Ended session {self.current_session_id}: {session_summary}")

        # Reset session state
        self.current_session_id = None
        self.session_start_time = None
        self.session_events = []

        return session_summary

    @contextmanager
    def track_session(
        self, user_id: str | None = None, session_type: str = "exploration"
    ) -> None:
        """Context manager for automatic session tracking.

        Args:
            user_id: Optional user identifier
            session_type: Type of session

        Yields:
            Session ID for the tracking session
        """
        session_id = self.start_session(user_id, session_type)
        try:
            yield session_id
        finally:
            self.end_session()

    def track_function_query(
        self,
        function_name: str,
        context: str | None = None,
        parameters: dict[str, Any] | None = None,
        success: bool = True,
        execution_time: float | None = None,
        error_message: str | None = None,
    ) -> str:
        """Track a function query event.

        Args:
            function_name: Name of the queried function
            context: Execution context (Gateway, Vision, Perspective)
            parameters: Query parameters used
            success: Whether the query was successful
            execution_time: Query execution time in seconds
            error_message: Error message if query failed

        Returns:
            Event ID for the tracked event
        """
        return self._track_event(
            event_type="function_query",
            function_name=function_name,
            context=context,
            parameters=parameters,
            success=success,
            execution_time=execution_time,
            error_message=error_message,
        )

    def track_template_generation(
        self,
        template_name: str,
        parameters: dict[str, Any] | None = None,
        success: bool = True,
        execution_time: float | None = None,
        error_message: str | None = None,
    ) -> str:
        """Track a template generation event.

        Args:
            template_name: Name of the generated template
            parameters: Template generation parameters
            success: Whether generation was successful
            execution_time: Generation time in seconds
            error_message: Error message if generation failed

        Returns:
            Event ID for the tracked event
        """
        return self._track_event(
            event_type="template_generation",
            template_name=template_name,
            parameters=parameters,
            success=success,
            execution_time=execution_time,
            error_message=error_message,
        )

    def track_parameter_usage(
        self,
        function_name: str | None = None,
        template_name: str | None = None,
        parameters: dict[str, Any] | None = None,
        context: str | None = None,
        success: bool = True,
    ) -> str:
        """Track parameter usage patterns.

        Args:
            function_name: Associated function name
            template_name: Associated template name
            parameters: Parameters used
            context: Usage context
            success: Whether usage was successful

        Returns:
            Event ID for the tracked event
        """
        return self._track_event(
            event_type="parameter_usage",
            function_name=function_name,
            template_name=template_name,
            parameters=parameters,
            context=context,
            success=success,
        )

    def _track_event(
        self,
        event_type: str,
        function_name: str | None = None,
        template_name: str | None = None,
        parameters: dict[str, Any] | None = None,
        context: str | None = None,
        success: bool = True,
        execution_time: float | None = None,
        error_message: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Internal method to track usage events.

        Args:
            event_type: Type of event being tracked
            function_name: Associated function name
            template_name: Associated template name
            parameters: Event parameters
            context: Execution context
            success: Event success status
            execution_time: Event execution time
            error_message: Error message if failed
            user_id: User identifier

        Returns:
            Event ID for the tracked event
        """
        if not self.current_session_id:
            # Auto-start session if none exists
            self.start_session()

        event_id = str(uuid.uuid4())
        timestamp = datetime.now()

        event_data = {
            "id": event_id,
            "event_type": event_type,
            "timestamp": timestamp.isoformat(),
            "session_id": self.current_session_id,
            "user_id": user_id,
            "context": context,
            "function_name": function_name,
            "template_name": template_name,
            "success": success,
            "execution_time": execution_time,
            "error_message": error_message,
        }

        # Store parameters as JSON string if provided
        if parameters:
            import json

            event_data["parameters"] = json.dumps(parameters)
        else:
            event_data["parameters"] = None

        # Store event in session memory
        self.session_events.append(event_data)

        # Create event node in database
        event_query = """
        CREATE (e:UsageEvent {
            id: $id,
            event_type: $event_type,
            timestamp: datetime($timestamp),
            session_id: $session_id,
            user_id: $user_id,
            context: $context,
            function_name: $function_name,
            template_name: $template_name,
            parameters: $parameters,
            success: $success,
            execution_time: $execution_time,
            error_message: $error_message
        })
        """

        # Create relationship to session
        session_rel_query = """
        MATCH (s:UserSession {id: $session_id}), (e:UsageEvent {id: $event_id})
        CREATE (e)-[:OCCURRED_IN_SESSION]->(s)
        """

        try:
            self.client.execute_write_query(event_query, event_data)
            self.client.execute_write_query(
                session_rel_query,
                {"session_id": self.current_session_id, "event_id": event_id},
            )

            # Create relationships to functions/templates if they exist
            if function_name:
                self._create_event_function_relationship(event_id, function_name)

            if template_name:
                self._create_event_template_relationship(event_id, template_name)

        except Exception as e:
            logger.error(f"Failed to store usage event {event_id}: {e}")

        logger.debug(f"Tracked {event_type} event: {event_id}")
        return event_id

    def _create_event_function_relationship(
        self, event_id: str, function_name: str
    ) -> dict[str, Any]:
        """Create relationship between event and function."""
        rel_query = """
        MATCH (e:UsageEvent {id: $event_id}), (f:Function {name: $function_name})
        MERGE (e)-[:USES]->(f)
        """

        try:
            self.client.execute_write_query(
                rel_query, {"event_id": event_id, "function_name": function_name}
            )
        except Exception as e:
            logger.debug(f"Could not create event-function relationship: {e}")

    def _create_event_template_relationship(
        self, event_id: str, template_name: str
    ) -> dict[str, Any]:
        """Create relationship between event and template."""
        rel_query = """
        MATCH (e:UsageEvent {id: $event_id}), (t:Template {name: $template_name})
        MERGE (e)-[:USES]->(t)
        """

        try:
            self.client.execute_write_query(
                rel_query, {"event_id": event_id, "template_name": template_name}
            )
        except Exception as e:
            logger.debug(f"Could not create event-template relationship: {e}")

    def get_session_stats(self, session_id: str | None = None) -> dict[str, Any]:
        """Get statistics for a session.

        Args:
            session_id: Session ID, defaults to current session

        Returns:
            Dictionary containing session statistics
        """
        if not session_id:
            session_id = self.current_session_id

        if not session_id:
            return {}

        query = """
        MATCH (s:UserSession {id: $session_id})
        OPTIONAL MATCH (e:UsageEvent)-[:OCCURRED_IN_SESSION]->(s)
        RETURN s, count(e) as event_count
        """

        result = self.client.execute_query(query, {"session_id": session_id})

        if not result:
            return {}

        session_data = result[0]["s"]
        event_count = result[0]["event_count"]

        return {
            "session_id": session_id,
            "start_time": session_data.get("start_time"),
            "end_time": session_data.get("end_time"),
            "duration": session_data.get("duration"),
            "event_count": event_count,
            "success_rate": session_data.get("success_rate"),
            "unique_functions": session_data.get("unique_functions"),
            "unique_templates": session_data.get("unique_templates"),
            "session_type": session_data.get("session_type"),
        }

    def get_recent_events(
        self, limit: int = 10, event_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Get recent usage events.

        Args:
            limit: Maximum number of events to return
            event_type: Filter by event type

        Returns:
            list of recent usage events
        """
        query = """
        MATCH (e:UsageEvent)
        """

        if event_type:
            query += " WHERE e.event_type = $event_type"

        query += """
        RETURN e
        ORDER BY e.timestamp DESC
        LIMIT $limit
        """

        params = {"limit": limit}
        if event_type:
            params["event_type"] = event_type

        result = self.client.execute_query(query, params)

        return [record["e"] for record in result]
