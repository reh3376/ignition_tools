"""Ignition OPC-UA Client Wrapper.

Enhanced OPC-UA client wrapper built on asyncua for industrial automation.
Provides high-level interface for connection management, data operations,
and real-time monitoring.
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from asyncua import Client

from .browser import AddressSpaceBrowser
from .connection import ConnectionManager
from .security import SecurityManager
from .subscription import SubscriptionManager

logger = logging.getLogger(__name__)


class IgnitionOPCUAClient:
    """Enhanced OPC-UA client wrapper for Ignition tools.

    Provides high-level interface for industrial OPC-UA operations including:
    - Secure connection management with certificates
    - Address space browsing and navigation
    - Real-time data subscriptions
    - Batch read/write operations
    - Industrial alarm and event handling
    """

    def __init__(self, url: str, **kwargs):
        """Initialize OPC-UA client.

        Args:
            url: OPC-UA server URL (e.g., "opc.tcp://localhost:4840")
            **kwargs: Additional configuration options
        """
        self.url = url
        self.client = Client(url)
        self.connected = False
        self._lock = asyncio.Lock()

        # Configuration
        self.config = {
            "timeout": kwargs.get("timeout", 10.0),
            "name": kwargs.get("name", "IgnitionClient"),
            "description": kwargs.get("description", "Ignition OPC-UA Client"),
            "auto_reconnect": kwargs.get("auto_reconnect", True),
            "keep_alive": kwargs.get("keep_alive", True),
        }

        # Initialize managers
        self.connection_manager = ConnectionManager(self.client, self.config)
        self.browser = AddressSpaceBrowser(self.client)
        self.subscription_manager = SubscriptionManager(self.client)
        self.security_manager = SecurityManager(self.client)

        # State tracking
        self._connection_stats = {
            "connect_time": None,
            "last_activity": None,
            "reconnect_count": 0,
            "error_count": 0,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self, **kwargs) -> bool:
        """Connect to OPC-UA server with enhanced error handling.

        Args:
            **kwargs: Connection options (username, password, certificate, etc.)

        Returns:
            bool: True if connection successful

        Raises:
            ConnectionError: If connection fails after retries
        """
        async with self._lock:
            if self.connected:
                logger.warning("Already connected to %s", self.url)
                return True

            try:
                logger.info("Connecting to OPC-UA server: %s", self.url)

                # Configure security if provided
                if "username" in kwargs or "certificate" in kwargs:
                    await self.security_manager.configure_security(**kwargs)

                # Attempt connection
                await self.connection_manager.connect(**kwargs)
                self.connected = True

                # Update stats
                self._connection_stats["connect_time"] = datetime.now()
                self._connection_stats["last_activity"] = datetime.now()

                logger.info("Successfully connected to %s", self.url)
                return True

            except Exception as e:
                self._connection_stats["error_count"] += 1
                logger.error("Failed to connect to %s: %s", self.url, e)
                raise ConnectionError(f"Failed to connect to {self.url}: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from OPC-UA server."""
        async with self._lock:
            if not self.connected:
                return

            try:
                logger.info("Disconnecting from %s", self.url)

                # Clean up subscriptions
                await self.subscription_manager.cleanup()

                # Disconnect client
                await self.connection_manager.disconnect()
                self.connected = False

                logger.info("Disconnected from %s", self.url)

            except Exception as e:
                logger.error("Error during disconnect: %s", e)

    async def browse_tree(
        self, node_id: str = "i=85", max_depth: int = 3
    ) -> dict[str, Any]:
        """Browse OPC-UA address space tree.

        Args:
            node_id: Starting node ID (default: Objects folder)
            max_depth: Maximum browsing depth

        Returns:
            Dict containing browsed tree structure
        """
        if not self.connected:
            raise RuntimeError("Not connected to OPC-UA server")

        return await self.browser.browse_tree(node_id, max_depth)

    async def read_values(self, node_ids: str | list[str]) -> Any | list[Any]:
        """Read values from one or more OPC-UA nodes.

        Args:
            node_ids: Single node ID or list of node IDs

        Returns:
            Single value or list of values
        """
        if not self.connected:
            raise RuntimeError("Not connected to OPC-UA server")

        self._update_activity()

        if isinstance(node_ids, str):
            # Single node read
            node = self.client.get_node(node_ids)
            value = await node.read_value()
            logger.debug("Read %s = %s", node_ids, value)
            return value
        else:
            # Batch read
            nodes = [self.client.get_node(nid) for nid in node_ids]
            values = []
            for node in nodes:
                try:
                    value = await node.read_value()
                    values.append(value)
                except Exception as e:
                    logger.error("Error reading %s: %s", node, e)
                    values.append(None)

            logger.debug("Batch read %d nodes", len(values))
            return values

    async def write_values(self, node_values: dict[str, Any]) -> dict[str, bool]:
        """Write values to OPC-UA nodes.

        Args:
            node_values: Dictionary of {node_id: value}

        Returns:
            Dictionary of {node_id: success_status}
        """
        if not self.connected:
            raise RuntimeError("Not connected to OPC-UA server")

        self._update_activity()
        results = {}

        for node_id, value in node_values.items():
            try:
                node = self.client.get_node(node_id)
                await node.write_value(value)
                results[node_id] = True
                logger.debug("Wrote %s = %s", node_id, value)
            except Exception as e:
                logger.error("Error writing %s: %s", node_id, e)
                results[node_id] = False

        return results

    async def subscribe_nodes(
        self,
        node_ids: list[str],
        callback: Callable[[str, Any], None],
        interval: float = 1000.0,
    ) -> str:
        """Subscribe to data changes on multiple nodes.

        Args:
            node_ids: List of node IDs to monitor
            callback: Function called on data change (node_id, new_value)
            interval: Publishing interval in milliseconds

        Returns:
            Subscription ID for management
        """
        if not self.connected:
            raise RuntimeError("Not connected to OPC-UA server")

        return await self.subscription_manager.create_subscription(
            node_ids, callback, interval
        )

    async def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a subscription.

        Args:
            subscription_id: ID returned from subscribe_nodes

        Returns:
            True if successfully removed
        """
        return await self.subscription_manager.remove_subscription(subscription_id)

    async def execute_method(
        self, object_id: str, method_id: str, args: list[Any] | None = None
    ) -> Any:
        """Execute OPC-UA method on server.

        Args:
            object_id: Parent object node ID
            method_id: Method node ID
            args: Method arguments

        Returns:
            Method execution result
        """
        if not self.connected:
            raise RuntimeError("Not connected to OPC-UA server")

        self._update_activity()

        try:
            parent = self.client.get_node(object_id)
            method = self.client.get_node(method_id)
            result = await parent.call_method(method, *(args or []))

            logger.debug("Executed method %s on %s", method_id, object_id)
            return result

        except Exception as e:
            logger.error("Error executing method %s: %s", method_id, e)
            raise

    async def get_server_info(self) -> dict[str, Any]:
        """Get server information and endpoints.

        Returns:
            Dictionary with server details
        """
        if not self.connected:
            await self.connect()

        try:
            # Get server info
            server_info = {
                "url": self.url,
                "connected": self.connected,
                "server_time": await self.client.get_server_time(),
                "namespace_uris": await self.client.get_namespace_array(),
                "stats": self._connection_stats.copy(),
            }

            # Get endpoints if available
            try:
                endpoints = await self.client.connect_and_get_server_endpoints()
                server_info["endpoints"] = [str(ep) for ep in endpoints]
            except Exception:
                server_info["endpoints"] = []

            return server_info

        except Exception as e:
            logger.error("Error getting server info: %s", e)
            raise

    def _update_activity(self):
        """Update last activity timestamp."""
        self._connection_stats["last_activity"] = datetime.now()

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on connection.

        Returns:
            Health status dictionary
        """
        health = {
            "connected": self.connected,
            "url": self.url,
            "stats": self._connection_stats.copy(),
            "subscriptions": await self.subscription_manager.get_status(),
        }

        if self.connected:
            try:
                # Test read operation
                server_time = await self.client.get_server_time()
                health["server_time"] = server_time
                health["status"] = "healthy"
            except Exception as e:
                health["status"] = "error"
                health["error"] = str(e)
        else:
            health["status"] = "disconnected"

        return health
