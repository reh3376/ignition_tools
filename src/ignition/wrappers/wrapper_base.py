"""Base wrapper class for Ignition system functions.

This module provides the foundation for all Ignition system function wrappers,
including common error handling, logging, validation, and configuration management.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any

# Mock system functions for development/testing environment
try:
    # In production Ignition environment, these will be available
    import system

    IGNITION_AVAILABLE = True
except ImportError:
    # Development/testing environment - create mock system
    class MockSystem:
        """Mock system object for development and testing."""

        def __init__(self) -> None:
            self.tag = MockTag()
            self.db = MockDb()
            self.gui = MockGui()
            self.nav = MockNav()
            self.alarm = MockAlarm()
            self.util = MockUtil()

    class MockTag:
        def readBlocking(self, tag_paths, timeout=45000):
            return [MockQualifiedValue(0, 192, time.time())]

        def writeBlocking(self, tag_paths, values, timeout=45000):
            return [MockQualityCode(192)]

        def read(self, tag_paths):
            return [MockQualifiedValue(0, 192, time.time())]

        def write(self, tag_paths, values):
            return [MockQualityCode(192)]

    class MockDb:
        def runQuery(self, query, database=""):
            return []

        def runUpdateQuery(self, query, database=""):
            return 0

        def runPrepQuery(self, query, args, database=""):
            return []

    class MockGui:
        def messageBox(self, message: str, title: str = "") -> None:
            print(f"MessageBox - {title}: {message}")

        def errorBox(self, message: str, title: str = "") -> None:
            print(f"ErrorBox - {title}: {message}")

        def warningBox(self, message: str, title: str = "") -> None:
            print(f"WarningBox - {title}: {message}")

    class MockNav:
        def openWindow(self, path: str, params: dict = None) -> None:
            print(f"Opening window: {path}")

        def closeWindow(self, path: str) -> None:
            print(f"Closing window: {path}")

    class MockAlarm:
        def acknowledge(self, alarmIds, notes=""):
            return True

        def queryStatus(self, priority=None, state=None):
            return []

    class MockUtil:
        def getLogger(self, name):
            return logging.getLogger(name)

        def getSystemFlags(self):
            return 0  # Return 0 for unknown context in mock

    class MockQualifiedValue:
        def __init__(self, value, quality, timestamp) -> None:
            self.value = value
            self.quality = quality
            self.timestamp = timestamp

    class MockQualityCode:
        def __init__(self, code) -> None:
            self.code = code

    system = MockSystem()
    IGNITION_AVAILABLE = False


class WrapperError(Exception):
    """Base exception for wrapper-related errors."""

    def __init__(self, message: str, original_error: Exception = None) -> None:
        super().__init__(message)
        self.original_error = original_error


class IgnitionContext(Enum):
    """Enumeration of Ignition execution contexts."""

    GATEWAY = "Gateway"
    DESIGNER = "Designer"
    CLIENT = "Client"
    UNKNOWN = "Unknown"


@dataclass
class WrapperConfig:
    """Configuration for wrapper behavior."""

    enable_logging: bool = True
    log_level: str = "INFO"
    enable_metrics: bool = True
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    validate_inputs: bool = True
    context: IgnitionContext = IgnitionContext.UNKNOWN
    custom_settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class WrapperMetrics:
    """Metrics collected by wrapper functions."""

    function_name: str
    execution_time_ms: float
    success: bool
    error_message: str | None = None
    retry_count: int = 0
    timestamp: float = field(default_factory=time.time)


class IgnitionWrapperBase(ABC):
    """Base class for all Ignition system function wrappers."""

    def __init__(self, config: WrapperConfig | None = None) -> None:
        """Initialize the wrapper with configuration.

        Args:
            config: Wrapper configuration, defaults to WrapperConfig()
        """
        self.config = config or WrapperConfig()
        self.logger = self._setup_logger()
        self.metrics: list[WrapperMetrics] = []

        # Detect Ignition context if not specified
        if self.config.context == IgnitionContext.UNKNOWN:
            self.config.context = self._detect_context()

    def _setup_logger(self) -> logging.Logger:
        """set up logger for the wrapper."""
        logger_name = f"ignition.wrapper.{self.__class__.__name__}"
        logger = logging.getLogger(logger_name)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        return logger

    def _detect_context(self) -> IgnitionContext:
        """Detect the current Ignition execution context."""
        try:
            # Try to detect context based on available system functions
            if hasattr(system, "util") and hasattr(system.util, "getSystemFlags"):
                flags = system.util.getSystemFlags()
                if flags & 1:  # Gateway flag
                    return IgnitionContext.GATEWAY
                elif flags & 2:  # Designer flag
                    return IgnitionContext.DESIGNER
                elif flags & 4:  # Client flag
                    return IgnitionContext.CLIENT
        except Exception:
            pass

        return IgnitionContext.UNKNOWN

    def _log_operation(self, operation: str, details: str = "") -> None:
        """Log wrapper operation if logging is enabled."""
        if self.config.enable_logging:
            self.logger.info(f"{operation}: {details}")

    def _log_error(self, operation: str, error: Exception) -> None:
        """Log wrapper error."""
        if self.config.enable_logging:
            self.logger.error(f"{operation} failed: {error}")

    def _record_metrics(self, metrics: WrapperMetrics) -> None:
        """Record performance metrics if enabled."""
        if self.config.enable_metrics:
            self.metrics.append(metrics)

            # Keep only last 1000 metrics to prevent memory issues
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics."""
        if not self.metrics:
            return {"total_calls": 0}

        successful_calls = sum(1 for m in self.metrics if m.success)
        failed_calls = len(self.metrics) - successful_calls
        avg_execution_time = sum(m.execution_time_ms for m in self.metrics) / len(
            self.metrics
        )

        return {
            "total_calls": len(self.metrics),
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / len(self.metrics),
            "average_execution_time_ms": avg_execution_time,
            "total_retries": sum(m.retry_count for m in self.metrics),
        }

    def clear_metrics(self) -> None:
        """Clear collected metrics."""
        self.metrics.clear()

    @abstractmethod
    def get_wrapped_functions(self) -> list[str]:
        """Get list of wrapped function names.

        Returns:
            list of function names wrapped by this class
        """
        pass


def wrapper_function(func):
    """Decorator for wrapper functions to add common functionality."""

    @wraps(func)
    def wrapper_impl(*args, **kwargs):
        start_time = time.time()
        function_name = f"{self.__class__.__name__}.{func.__name__}"
        retry_count = 0

        # Log operation start
        self._log_operation(
            f"Starting {function_name}", f"args={args}, kwargs={kwargs}"
        )

        for attempt in range(self.config.retry_attempts):
            try:
                # Execute the wrapped function
                result = func(self, *args, **kwargs)

                # Record successful metrics
                execution_time = (time.time() - start_time) * 1000
                metrics = WrapperMetrics(
                    function_name=function_name,
                    execution_time_ms=execution_time,
                    success=True,
                    retry_count=retry_count,
                )
                self._record_metrics(metrics)

                # Log successful completion
                self._log_operation(
                    f"Completed {function_name}",
                    f"execution_time={execution_time:.2f}ms",
                )

                return result

            except Exception as e:
                retry_count += 1
                execution_time = (time.time() - start_time) * 1000

                # Log error
                self._log_error(f"Attempt {attempt + 1} of {function_name}", e)

                # If this is the last attempt, record failure and re-raise
                if attempt == self.config.retry_attempts - 1:
                    metrics = WrapperMetrics(
                        function_name=function_name,
                        execution_time_ms=execution_time,
                        success=False,
                        error_message=str(e),
                        retry_count=retry_count,
                    )
                    self._record_metrics(metrics)

                    # Wrap the exception with additional context
                    raise WrapperError(
                        f"Function {function_name} failed after {self.config.retry_attempts} attempts: {e}",
                        original_error=e,
                    )

                # Wait before retry
                if self.config.retry_delay_seconds > 0:
                    time.sleep(self.config.retry_delay_seconds)

    return wrapper_impl


def validate_tag_paths(tag_paths: str | list[str]) -> list[str]:
    """Validate and normalize tag paths.

    Args:
        tag_paths: Single tag path or list of tag paths

    Returns:
        list of validated tag paths

    Raises:
        WrapperError: If tag paths are invalid
    """
    if isinstance(tag_paths, str):
        tag_paths = [tag_paths]

    if not isinstance(tag_paths, list):
        raise WrapperError("Tag paths must be a string or list of strings")

    if not tag_paths:
        raise WrapperError("Tag paths cannot be empty")

    for path in tag_paths:
        if not isinstance(path, str):
            raise WrapperError(f"Tag path must be string, got {type(path)}")
        if not path.strip():
            raise WrapperError("Tag path cannot be empty or whitespace")

    return tag_paths


def validate_database_name(database: str) -> str:
    """Validate database name.

    Args:
        database: Database name to validate

    Returns:
        Validated database name

    Raises:
        WrapperError: If database name is invalid
    """
    if not isinstance(database, str):
        raise WrapperError(f"Database name must be string, got {type(database)}")

    # Empty string is valid (uses default database)
    return database.strip()


def format_sql_query(query: str) -> str:
    """Format and validate SQL query.

    Args:
        query: SQL query to format

    Returns:
        Formatted SQL query

    Raises:
        WrapperError: If query is invalid
    """
    if not isinstance(query, str):
        raise WrapperError(f"SQL query must be string, got {type(query)}")

    query = query.strip()
    if not query:
        raise WrapperError("SQL query cannot be empty")

    return query
