"""Enhanced wrapper for Ignition system.util functions."""

import logging
from typing import Any

from .wrapper_base import IgnitionWrapperBase, WrapperError, system, wrapper_function


class SystemUtilWrapper(IgnitionWrapperBase):
    """Enhanced wrapper for system.util functions."""

    def get_wrapped_functions(self) -> list[str]:
        """Get list of wrapped utility functions."""
        return ["get_logger", "send_message", "thread_dump"]

    @wrapper_function
    def get_logger(self, name: str) -> logging.Logger:
        """Enhanced logger retrieval with validation."""
        if self.config.validate_inputs:
            if not isinstance(name, str):
                raise WrapperError("Logger name must be a string")
            if not name.strip():
                raise WrapperError("Logger name cannot be empty")

        try:
            logger = system.util.getLogger(name)

            self._log_operation("Logger retrieved", f"Name: {name}")
            return logger

        except Exception as e:
            raise WrapperError(f"Logger retrieval failed: {e}", original_error=e) from e

    @wrapper_function
    def send_message(self, project: str, message_handler: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Enhanced message sending with validation."""
        if self.config.validate_inputs:
            if not isinstance(project, str):
                raise WrapperError("Project name must be a string")
            if not isinstance(message_handler, str):
                raise WrapperError("Message handler must be a string")
            if not isinstance(payload, dict):
                raise WrapperError("Payload must be a dictionary")

        try:
            system.util.sendMessage(project, message_handler, payload)

            result = {
                "action": "send_message",
                "project": project,
                "message_handler": message_handler,
                "payload_size": len(str(payload)),
                "success": True,
            }

            self._log_operation("Message sent", f"Project: {project}, Handler: {message_handler}")
            return result

        except Exception as e:
            raise WrapperError(f"Message sending failed: {e}", original_error=e) from e
