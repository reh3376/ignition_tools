"""OPC-UA data source adapter."""

import asyncio
from typing import Any

from ignition.opcua import IgnitionOPCUAClient

from .base_adapter import BaseDataAdapter


class OPCUAAdapter(BaseDataAdapter):
    """OPC-UA data source adapter.

    This adapter provides connectivity to OPC-UA servers using the existing
    IgnitionOPCUAClient implementation.
    """

    def __init__(self, config):
        """Initialize OPC-UA adapter."""
        super().__init__(config)
        self._client = None

    async def connect(self) -> bool:
        """Connect to OPC-UA server."""
        try:
            # Extract connection parameters
            url = self.config.connection_params.get("url") or self.config.connection_params.get("endpoint_url")
            if not url:
                self.logger.error("OPC-UA URL is required")
                return False

            # Create OPC-UA client with correct constructor
            self._client = IgnitionOPCUAClient(url)

            # Connect to server with authentication if provided
            connect_kwargs = {}
            if "username" in self.config.connection_params:
                connect_kwargs["username"] = self.config.connection_params["username"]
            if "password" in self.config.connection_params:
                connect_kwargs["password"] = self.config.connection_params["password"]
            if "certificate" in self.config.connection_params:
                connect_kwargs["certificate"] = self.config.connection_params["certificate"]

            success = await self._client.connect(**connect_kwargs)
            if success:
                self._connected = True
                self.logger.info(f"Connected to OPC-UA server: {url}")
                return True
            else:
                self.logger.error(f"Failed to connect to OPC-UA server: {url}")
                return False

        except Exception as e:
            self.logger.error(f"OPC-UA connection error: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from OPC-UA server."""
        try:
            if self._client:
                await self._client.disconnect()
                self._client = None
                self._connected = False
                self.logger.info("Disconnected from OPC-UA server")
            return True
        except Exception as e:
            self.logger.error(f"OPC-UA disconnection error: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test OPC-UA server connection."""
        try:
            if not self._client or not self._connected:
                return False

            # Test by getting server info
            server_info = await self._client.get_server_info()
            return server_info is not None

        except Exception as e:
            self.logger.error(f"OPC-UA connection test error: {e}")
            return False

    async def read_data(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Read data from OPC-UA server."""
        if not self._client or not self._connected:
            self.logger.error("OPC-UA client not connected")
            return []

        try:
            data = []

            if query and "node_ids" in query:
                # Read specific node IDs using the correct API
                node_ids = query["node_ids"]
                if isinstance(node_ids, str):
                    node_ids = [node_ids]

                # Use read_values method which handles both single and multiple nodes
                values = await self._client.read_values(node_ids)

                # Handle both single value and list of values
                if not isinstance(values, list):
                    values = [values]

                for i, value in enumerate(values):
                    if i < len(node_ids):
                        data.append(
                            {
                                "node_id": node_ids[i],
                                "value": value,
                                "timestamp": asyncio.get_event_loop().time(),
                                "source_type": "opcua",
                                "source_id": self.config.source_id,
                            }
                        )

            elif query and "browse_path" in query:
                # Browse address space
                browse_path = query["browse_path"]
                tree = await self._client.browse_tree(browse_path, max_depth=1)

                # Extract node information from browse results
                if "children" in tree:
                    for child in tree["children"]:
                        data.append(
                            {
                                "node_id": child.get("node_id", ""),
                                "display_name": child.get("display_name", ""),
                                "node_class": child.get("node_class", ""),
                                "source_type": "opcua",
                                "source_id": self.config.source_id,
                            }
                        )
            else:
                # Default: get server information
                server_info = await self._client.get_server_info()
                if server_info:
                    data.append(
                        {
                            "server_info": server_info,
                            "timestamp": asyncio.get_event_loop().time(),
                            "source_type": "opcua",
                            "source_id": self.config.source_id,
                        }
                    )

            return data

        except Exception as e:
            self.logger.error(f"OPC-UA read error: {e}")
            return []

    async def write_data(self, data: list[dict[str, Any]]) -> bool:
        """Write data to OPC-UA server."""
        if not self._client or not self._connected:
            self.logger.error("OPC-UA client not connected")
            return False

        try:
            success_count = 0

            # Prepare write operations
            node_values = {}
            for record in data:
                if "node_id" in record and "value" in record:
                    node_values[record["node_id"]] = record["value"]
                else:
                    self.logger.warning("Invalid write data format - missing node_id or value")

            if node_values:
                # Use write_values method
                results = await self._client.write_values(node_values)

                # Count successful writes
                for node_id, success in results.items():
                    if success:
                        success_count += 1
                    else:
                        self.logger.warning(f"Failed to write to node {node_id}")

            self.logger.info(f"Successfully wrote {success_count}/{len(data)} records")
            return success_count > 0

        except Exception as e:
            self.logger.error(f"OPC-UA write error: {e}")
            return False

    async def stream_data(self, callback: callable, query: dict[str, Any] | None = None) -> None:
        """Stream data from OPC-UA server using subscriptions."""
        if not self._client or not self._connected:
            self.logger.error("OPC-UA client not connected")
            return

        try:
            # Subscribe to nodes for real-time updates
            node_ids = query.get("node_ids", []) if query else []
            if isinstance(node_ids, str):
                node_ids = [node_ids]

            if not node_ids:
                self.logger.warning("No node IDs specified for streaming")
                return

            def data_change_callback(node_id: str, value: Any) -> None:
                """Handle data change notifications."""
                try:
                    data_record = {
                        "node_id": node_id,
                        "value": value,
                        "timestamp": asyncio.get_event_loop().time(),
                        "source_type": "opcua",
                        "source_id": self.config.source_id,
                    }
                    # Schedule the async callback
                    task = asyncio.create_task(callback(data_record))
                    # Store reference to prevent garbage collection
                    task.add_done_callback(lambda _: None)
                except Exception as e:
                    self.logger.error(f"Callback error for node {node_id}: {e}")

            # Create subscription
            interval = query.get("interval", 1000.0) if query else 1000.0
            subscription_id = await self._client.subscribe_nodes(node_ids, data_change_callback, interval)

            self.logger.info(f"Created OPC-UA subscription {subscription_id} for {len(node_ids)} nodes")

            # Keep streaming until disconnected
            while self._connected:
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"OPC-UA streaming error: {e}")

    def validate_config(self) -> bool:
        """Validate OPC-UA specific configuration."""
        if not super().validate_config():
            return False

        # Check OPC-UA specific parameters
        params = self.config.connection_params
        if "url" not in params and "endpoint_url" not in params:
            self.logger.error("OPC-UA url or endpoint_url is required")
            return False

        return True
