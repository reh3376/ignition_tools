"""Enhanced wrapper for Ignition system.nav functions."""

from typing import Any

from .wrapper_base import IgnitionWrapperBase, WrapperError, system, wrapper_function


class SystemNavWrapper(IgnitionWrapperBase):
    """Enhanced wrapper for system.nav functions."""

    def get_wrapped_functions(self) -> list[str]:
        """Get list of wrapped navigation functions."""
        return ["open_window", "close_window", "swap_window", "center_window"]

    @wrapper_function
    def open_window(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Enhanced window opening with validation and logging."""
        if self.config.validate_inputs:
            if not isinstance(path, str):
                raise WrapperError("Window path must be a string")
            if not path.strip():
                raise WrapperError("Window path cannot be empty")

        try:
            if params:
                system.nav.openWindow(path, params)
            else:
                system.nav.openWindow(path)

            result = {
                "action": "open_window",
                "path": path,
                "params": params,
                "success": True,
            }

            self._log_operation("Window opened", f"Path: {path}")
            return result

        except Exception as e:
            raise WrapperError(f"Window open failed: {e}", original_error=e) from e

    @wrapper_function
    def close_window(self, path: str) -> dict[str, Any]:
        """Enhanced window closing with validation and logging."""
        if self.config.validate_inputs:
            if not isinstance(path, str):
                raise WrapperError("Window path must be a string")
            if not path.strip():
                raise WrapperError("Window path cannot be empty")

        try:
            system.nav.closeWindow(path)

            result = {"action": "close_window", "path": path, "success": True}

            self._log_operation("Window closed", f"Path: {path}")
            return result

        except Exception as e:
            raise WrapperError(f"Window close failed: {e}", original_error=e) from e
