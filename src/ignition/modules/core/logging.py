"""Module diagnostics and logging management for Ignition modules."""

import logging
import logging.handlers
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .abstract_module import AbstractIgnitionModule

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False


class ModuleDiagnosticsManager:
    """Manages logging and diagnostics for Ignition modules."""

    def __init__(self, module: "AbstractIgnitionModule"):
        """Initialize the diagnostics manager."""
        self._module = module
        self._log_path = module.context.log_path
        self._module_name = module.metadata.name
        self._module_id = module.metadata.id

        # Logger setup
        self._logger: logging.Logger | None = None
        self._log_level = logging.INFO

        # Log files
        self._main_log_file = self._log_path / f"{self._module_id}.log"
        self._error_log_file = self._log_path / f"{self._module_id}_errors.log"

        # Error tracking
        self._error_count = 0
        self._warning_count = 0
        self._last_error: str | None = None
        self._last_error_time: datetime | None = None

        # Health status
        self._health_status = "unknown"
        self._last_health_check: datetime | None = None

        # Initialize logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        try:
            # Ensure log directory exists
            self._log_path.mkdir(parents=True, exist_ok=True)

            # Create logger
            logger_name = f"ignition.module.{self._module_id}"
            self._logger = logging.getLogger(logger_name)
            self._logger.setLevel(self._log_level)

            # Clear existing handlers
            self._logger.handlers.clear()

            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)

            # Main log file handler with rotation
            main_handler = logging.handlers.RotatingFileHandler(
                self._main_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            main_handler.setLevel(self._log_level)
            main_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
            )
            main_handler.setFormatter(main_formatter)
            self._logger.addHandler(main_handler)

            # Error log file handler
            error_handler = logging.handlers.RotatingFileHandler(
                self._error_log_file,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3,
                encoding="utf-8",
            )
            error_handler.setLevel(logging.ERROR)
            error_formatter = logging.Formatter(main_formatter._fmt)
            error_handler.setFormatter(error_formatter)
            self._logger.addHandler(error_handler)

            # Prevent propagation to root logger
            self._logger.propagate = False

            self._logger.info(f"Logging initialized for module: {self._module_name}")

        except Exception as e:
            print(f"Failed to setup logging for {self._module_name}: {e}")
            # Fallback to basic logging
            self._logger = logging.getLogger(f"ignition.module.{self._module_id}")
            self._logger.setLevel(logging.INFO)

    # Properties

    @property
    def logger(self) -> logging.Logger:
        """Get the module logger."""
        if self._logger is None:
            self._setup_logging()
        if self._logger is None:
            raise RuntimeError("Failed to initialize logger")
        return self._logger

    @property
    def health_status(self) -> str:
        """Get current health status."""
        return self._health_status

    @property
    def error_count(self) -> int:
        """Get total error count."""
        return self._error_count

    @property
    def warning_count(self) -> int:
        """Get total warning count."""
        return self._warning_count

    # Main methods

    def get_logger(self) -> logging.Logger:
        """Get the module logger."""
        return self.logger

    def set_log_level(self, level: int | str) -> Any:
        """Set logging level."""
        if isinstance(level, str):
            level = getattr(logging, level.upper())

        self._log_level = level
        if self._logger:
            self._logger.setLevel(level)

        self._logger.info(f"Log level set to {logging.getLevelName(level)}")

    def log_error(self, error: Exception, context: str | None = None) -> Any:
        """Log error with context and tracking."""
        self._error_count += 1
        self._last_error = str(error)
        self._last_error_time = datetime.now()

        # Log the error
        if context:
            self._logger.error(f"{context}: {error}", exc_info=True)
        else:
            self._logger.error(f"Error: {error}", exc_info=True)

    def log_warning(self, message: str, **kwargs) -> Any:
        """Log warning with tracking."""
        self._warning_count += 1
        self._logger.warning(message, **kwargs)

    def check_health(self) -> dict[str, Any]:
        """Perform basic health check."""
        self._last_health_check = datetime.now()

        # Basic health determination
        if self._error_count == 0:
            self._health_status = "healthy"
        elif self._error_count < 5:
            self._health_status = "warning"
        else:
            self._health_status = "unhealthy"

        return {
            "overall_status": self._health_status,
            "check_time": self._last_health_check.isoformat(),
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "last_error": self._last_error,
            "last_error_time": (self._last_error_time.isoformat() if self._last_error_time else None),
        }

    def get_health_status(self) -> dict[str, Any]:
        """Get current health status."""
        return {
            "status": self._health_status,
            "last_check": (self._last_health_check.isoformat() if self._last_health_check else None),
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "last_error": self._last_error,
        }

    def get_status(self) -> dict[str, Any]:
        """Get diagnostics manager status."""
        return {
            "health_status": self._health_status,
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "log_level": logging.getLevelName(self._log_level),
            "main_log_file": str(self._main_log_file),
            "error_log_file": str(self._error_log_file),
            "last_health_check": (self._last_health_check.isoformat() if self._last_health_check else None),
        }

    def __str__(self) -> str:
        """String representation of the diagnostics manager."""
        return f"DiagnosticsManager({self._module_name}, {self._health_status})"

    def __repr__(self) -> str:
        """Detailed string representation of the diagnostics manager."""
        return (
            f"ModuleDiagnosticsManager(module='{self._module_name}', "
            f"health='{self._health_status}', errors={self._error_count}, "
            f"warnings={self._warning_count})"
        )
