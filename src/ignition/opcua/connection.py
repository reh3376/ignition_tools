"""OPC-UA Connection Management

Handles connection lifecycle, authentication, and error recovery
for OPC-UA client connections.
"""

import logging
from datetime import datetime
from typing import Any

from asyncua import Client

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages OPC-UA client connections with authentication and reconnection logic."""

    def __init__(self, client: Client, config: dict[str, Any]):
        """Initialize connection manager.

        Args:
            client: AsyncUA client instance
            config: Connection configuration
        """
        self.client = client
        self.config = config
        self.connected = False
        self.last_connect_time = None
        self.reconnect_count = 0
        self.max_reconnect_attempts = config.get("max_reconnect_attempts", 5)
        self.reconnect_delay = config.get("reconnect_delay", 5.0)

    async def connect(self, **kwargs) -> None:
        """Connect to OPC-UA server with authentication.

        Args:
            **kwargs: Connection options including:
                - username: Username for authentication
                - password: Password for authentication
                - certificate: Client certificate path
                - private_key: Private key path
                - security_policy: Security policy to use
                - security_mode: Security mode to use
        """
        try:
            # Configure authentication
            await self._configure_authentication(**kwargs)

            # Set client properties
            self.client.name = self.config.get("name", "IgnitionClient")
            self.client.description = self.config.get(
                "description", "Ignition OPC-UA Client"
            )

            # Set timeout
            timeout = kwargs.get("timeout", self.config.get("timeout", 10.0))
            self.client.secure_channel_timeout = (
                timeout * 1000
            )  # Convert to milliseconds

            # Attempt connection
            await self.client.connect()

            self.connected = True
            self.last_connect_time = datetime.now()
            self.reconnect_count = 0

            logger.info("Connected to OPC-UA server: %s", self.client.server_url)

        except Exception as e:
            logger.error("Connection failed: %s", e)
            raise ConnectionError(f"Failed to connect: {e}")

    async def disconnect(self) -> None:
        """Disconnect from OPC-UA server."""
        if self.connected:
            try:
                await self.client.disconnect()
                self.connected = False
                logger.info("Disconnected from OPC-UA server")
            except Exception as e:
                logger.error("Error during disconnect: %s", e)
                raise

    async def _configure_authentication(self, **kwargs) -> None:
        """Configure client authentication based on provided options.

        Args:
            **kwargs: Authentication options
        """
        # Username/password authentication
        username = kwargs.get("username")
        password = kwargs.get("password")

        if username and password:
            self.client.set_user(username)
            self.client.set_password(password)
            logger.debug(
                "Configured username/password authentication for user: %s", username
            )

    async def check_connection(self) -> bool:
        """Check if connection is still alive.

        Returns:
            bool: True if connection is healthy
        """
        if not self.connected:
            return False

        try:
            # Simple read operation to check connection
            await self.client.get_server_time()
            return True
        except Exception as e:
            logger.warning("Connection check failed: %s", e)
            self.connected = False
            return False
