"""Base adapter class for data source connections."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from ignition.modules.data_integration.integration_module import DataSourceConfig


class BaseDataAdapter(ABC):
    """Base class for all data source adapters.

    This class defines the interface that all data source adapters must implement
    to provide consistent connectivity patterns across different data sources.
    """

    def __init__(self, config: DataSourceConfig):
        """Initialize the adapter with configuration.

        Args:
            config: Data source configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._connected = False
        self._connection = None

    @property
    def is_connected(self) -> bool:
        """Check if the adapter is connected to the data source."""
        return self._connected

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the data source.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the data source.

        Returns:
            True if disconnection successful, False otherwise
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the connection to the data source.

        Returns:
            True if connection is healthy, False otherwise
        """
        pass

    @abstractmethod
    async def read_data(
        self, query: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Read data from the data source.

        Args:
            query: Optional query parameters specific to the data source

        Returns:
            list of data records
        """
        pass

    @abstractmethod
    async def write_data(self, data: list[dict[str, Any]]) -> bool:
        """Write data to the data source.

        Args:
            data: list of data records to write

        Returns:
            True if write successful, False otherwise
        """
        pass

    @abstractmethod
    async def stream_data(
        self, callback: callable, query: dict[str, Any] | None = None
    ) -> None:
        """Stream data from the data source.

        Args:
            callback: Function to call for each data record
            query: Optional query parameters for streaming
        """
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    def validate_config(self) -> bool:
        """Validate the adapter configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.config.source_id:
            self.logger.error("Source ID is required")
            return False

        if not self.config.source_type:
            self.logger.error("Source type is required")
            return False

        if not self.config.connection_params:
            self.logger.error("Connection parameters are required")
            return False

        return True

    def get_connection_info(self) -> dict[str, Any]:
        """Get connection information for monitoring.

        Returns:
            Dictionary containing connection details
        """
        return {
            "source_id": self.config.source_id,
            "source_type": self.config.source_type,
            "connected": self._connected,
            "connection_params": {
                k: v
                for k, v in self.config.connection_params.items()
                if k
                not in [
                    "password",
                    "api_key",
                    "secret",
                    "token",
                ]  # Exclude sensitive info
            },
        }
