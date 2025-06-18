"""Enhanced wrapper for Ignition system.gui functions."""

from typing import Any

from .wrapper_base import IgnitionWrapperBase, WrapperError, system, wrapper_function


class SystemGuiWrapper(IgnitionWrapperBase):
    """Enhanced wrapper for system.gui functions."""

    def get_wrapped_functions(self) -> list[str]:
        """Get list of wrapped GUI functions."""
        return ["message_box", "error_box", "warning_box", "confirm_box", "input_box"]

    @wrapper_function
    def message_box(self, message: str, title: str = "Message") -> dict[str, Any]:
        """Enhanced message box with logging and validation."""
        if self.config.validate_inputs:
            if not isinstance(message, str):
                raise WrapperError("Message must be a string")
            if not isinstance(title, str):
                raise WrapperError("Title must be a string")

        try:
            system.gui.messageBox(message, title)

            result = {
                "type": "message",
                "message": message,
                "title": title,
                "success": True,
            }

            self._log_operation("Message box displayed", f"Title: {title}")
            return result

        except Exception as e:
            raise WrapperError(f"Message box failed: {e}", original_error=e)

    @wrapper_function
    def error_box(self, message: str, title: str = "Error") -> dict[str, Any]:
        """Enhanced error box with logging and validation."""
        if self.config.validate_inputs:
            if not isinstance(message, str):
                raise WrapperError("Message must be a string")
            if not isinstance(title, str):
                raise WrapperError("Title must be a string")

        try:
            system.gui.errorBox(message, title)

            result = {
                "type": "error",
                "message": message,
                "title": title,
                "success": True,
            }

            self._log_operation("Error box displayed", f"Title: {title}")
            return result

        except Exception as e:
            raise WrapperError(f"Error box failed: {e}", original_error=e)

    @wrapper_function
    def warning_box(self, message: str, title: str = "Warning") -> dict[str, Any]:
        """Enhanced warning box with logging and validation."""
        if self.config.validate_inputs:
            if not isinstance(message, str):
                raise WrapperError("Message must be a string")
            if not isinstance(title, str):
                raise WrapperError("Title must be a string")

        try:
            system.gui.warningBox(message, title)

            result = {
                "type": "warning",
                "message": message,
                "title": title,
                "success": True,
            }

            self._log_operation("Warning box displayed", f"Title: {title}")
            return result

        except Exception as e:
            raise WrapperError(f"Warning box failed: {e}", original_error=e)
