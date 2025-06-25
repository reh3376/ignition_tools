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
from typing import Self, Any

# Mock system functions for development/testing environment
try:
    # In production Ignition environment, these will be available
    import system

    IGNITION_AVAILABLE = True
except ImportError:
    # Development/testing environment - create mock system
    class MockSystem:
        """Mock system object for development and testing."""

        def __init__(self: Self) -> None:
            self.tag = MockTag()
            self.db = MockDb()
            self.gui = MockGui()
            self.nav = MockNav()
            self.alarm = MockAlarm()
            self.util = MockUtil()

    class MockTag:
        def readBlocking(self: Self, tag_paths, timeout=45000) -> None:
            return [MockQualifiedValue(0, 192, time.time())]

        def writeBlocking(self: Self, tag_paths, values, timeout=45000) -> None:
            return [MockQualityCode(192)]

        def read(self: Self, tag_paths: Any) -> None:
            return [MockQualifiedValue(0, 192, time.time())]

        def write(self: Self, tag_paths, values) -> None:
            return [MockQualityCode(192)]

    class MockDb:
        def runQuery(self: Self, query, database="") -> None:
            return []

        def runUpdateQuery(self: Self, query, database="") -> None:
            return 0

        def runPrepQuery(self: Self, query, args, database="") -> None:
            return []

    class MockGui:
        def messageBox(self: Self, message: str, title: str = "") -> None:
            print(f"MessageBox - {title}: {message}")

        def errorBox(self: Self, message: str, title: str = "") -> None:
            print(f"ErrorBox - {title}: {message}")

        def warningBox(self: Self, message: str, title: str = "") -> None:
            print(f"WarningBox - {title}: {message}")

    class MockNav:
        def openWindow(self: Self, path: str, params: dict | None = None) -> None:
            print(f"Opening window: {path}")

        def closeWindow(self: Self, path: str) -> None:
            print(f"Closing window: {path}")

    class MockAlarm:
        def acknowledge(self: Self, alarmIds, notes="") -> None:
            return True

        def queryStatus(self: Self, priority=None, state=None) -> None:
            return []

    class MockUtil:
        def getLogger(self: Self, name: Any) -> None:
            return logging.getLogger(name)

        def getSystemFlags(self: Self) -> None:
            return 0  # Return 0 for unknown context in mock

    class MockQualifiedValue:
        def __init__(self: Self, value, quality, timestamp) -> None:
            self.value = value
            self.quality = quality
            self.timestamp = timestamp

    class MockQualityCode:
        def __init__(self: Self, code: Any) -> None:
            self.code = code

    system = MockSystem()
    IGNITION_AVAILABLE = False


class WrapperError(Exception):
    """Base exception for wrapper-related errors."""

    def __init__(self: Self, message: str, original_error: Exception | None = None) -> None:
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

    def __init__(self: Self, config: WrapperConfig | None = None) -> None:
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

    def _setup_logger(self: Self) -> logging.Logger:
        """Set up logger for the wrapper."""
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

    def _detect_context(self: Self) -> IgnitionContext:
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

    def _log_operation(self: Self, operation: str, details: str = "") -> None:
        """Log wrapper operation if logging is enabled."""
        if self.config.enable_logging:
            self.logger.info(f"{operation}: {details}")

    def _log_error(self: Self, operation: str, error: Exception) -> None:
        """Log wrapper error."""
        if self.config.enable_logging:
            self.logger.error(f"{operation} failed: {error}")

    def _record_metrics(self: Self, metrics: WrapperMetrics) -> None:
        """Record performance metrics if enabled."""
        if self.config.enable_metrics:
            self.metrics.append(metrics)

            # Keep only last 1000 metrics to prevent memory issues
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]

    def get_metrics_summary(self: Self) -> dict[str, Any]:
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

    def clear_metrics(self: Self) -> None:
        """Clear collected metrics."""
        self.metrics.clear()

    @abstractmethod
    def get_wrapped_functions(self: Self) -> list[str]:
        """Get list of wrapped function names.

        Returns:
            list of function names wrapped by this class
        """
        pass


def wrapper_function(func: Any) -> None:
    """Decorator for wrapper functions to add common functionality."""

    @wraps(func)
    def wrapper_impl(self: Self, *args, **kwargs) -> None:
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
                    ) from e

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
