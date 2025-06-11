"""OPC-UA Subscription Management.

Handles real-time data subscriptions, monitoring, and event handling
for OPC-UA clients.
"""

import logging
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from asyncua import Client, Node
from asyncua.common.subscription import DataChangeNotif

logger = logging.getLogger(__name__)


class DataChangeHandler:
    """Handles data change notifications for subscriptions."""

    def __init__(self, callback: Callable[[str, Any], None]):
        """Initialize data change handler.

        Args:
            callback: Function to call on data change (node_id, new_value)
        """
        self.callback = callback
        self.node_map = {}  # Maps handle to node_id

    def datachange_notification(self, node: Node, val: Any, data: DataChangeNotif):
        """Handle data change notification.

        Args:
            node: The node that changed
            val: New value
            data: Change notification data
        """
        try:
            node_id = str(node.nodeid)
            logger.debug("Data change: %s = %s", node_id, val)

            # Call user callback
            if self.callback:
                self.callback(node_id, val)

        except Exception as e:
            logger.error("Error in data change handler: %s", e)


class SubscriptionManager:
    """Manages OPC-UA subscriptions for real-time data monitoring."""

    def __init__(self, client: Client):
        """Initialize subscription manager.

        Args:
            client: AsyncUA client instance
        """
        self.client = client
        self.subscriptions = {}  # subscription_id -> subscription info
        self.active_subscriptions = {}  # subscription_id -> Subscription object

    async def create_subscription(
        self,
        node_ids: list[str],
        callback: Callable[[str, Any], None],
        interval: float = 1000.0,
    ) -> str:
        """Create a new subscription for monitoring nodes.

        Args:
            node_ids: List of node IDs to monitor
            callback: Function called on data change (node_id, new_value)
            interval: Publishing interval in milliseconds

        Returns:
            Subscription ID for management
        """
        subscription_id = str(uuid.uuid4())

        try:
            # Create OPC-UA subscription
            handler = DataChangeHandler(callback)
            subscription = await self.client.create_subscription(interval, handler)

            # Subscribe to nodes
            nodes = [self.client.get_node(node_id) for node_id in node_ids]
            monitored_items = await subscription.subscribe_data_change(nodes)

            # Store subscription info
            self.subscriptions[subscription_id] = {
                "id": subscription_id,
                "node_ids": node_ids,
                "interval": interval,
                "created_at": datetime.now(),
                "callback": callback,
                "monitored_items": len(monitored_items),
                "handler": handler,
            }

            self.active_subscriptions[subscription_id] = subscription

            logger.info(
                "Created subscription %s for %d nodes", subscription_id, len(node_ids)
            )
            return subscription_id

        except Exception as e:
            logger.error("Error creating subscription: %s", e)
            raise

    async def remove_subscription(self, subscription_id: str) -> bool:
        """Remove a subscription.

        Args:
            subscription_id: ID of subscription to remove

        Returns:
            True if successfully removed
        """
        try:
            if subscription_id in self.active_subscriptions:
                subscription = self.active_subscriptions[subscription_id]
                await subscription.delete()

                del self.active_subscriptions[subscription_id]
                del self.subscriptions[subscription_id]

                logger.info("Removed subscription %s", subscription_id)
                return True
            else:
                logger.warning("Subscription %s not found", subscription_id)
                return False

        except Exception as e:
            logger.error("Error removing subscription %s: %s", subscription_id, e)
            return False

    async def get_subscription_info(
        self, subscription_id: str
    ) -> dict[str, Any] | None:
        """Get information about a specific subscription.

        Args:
            subscription_id: Subscription ID

        Returns:
            Subscription information or None if not found
        """
        if subscription_id in self.subscriptions:
            info = self.subscriptions[subscription_id].copy()

            # Add runtime information
            if subscription_id in self.active_subscriptions:
                subscription = self.active_subscriptions[subscription_id]
                info["active"] = True
                info["subscription_id_internal"] = subscription.subscription_id
            else:
                info["active"] = False

            # Remove callback from serializable info
            info.pop("callback", None)
            info.pop("handler", None)

            return info

        return None

    async def list_subscriptions(self) -> list[dict[str, Any]]:
        """List all active subscriptions.

        Returns:
            List of subscription information
        """
        subscriptions = []

        for sub_id in self.subscriptions:
            info = await self.get_subscription_info(sub_id)
            if info:
                subscriptions.append(info)

        return subscriptions

    async def modify_subscription_interval(
        self, subscription_id: str, new_interval: float
    ) -> bool:
        """Modify the publishing interval of a subscription.

        Args:
            subscription_id: Subscription ID
            new_interval: New interval in milliseconds

        Returns:
            True if successfully modified
        """
        try:
            if subscription_id in self.active_subscriptions:
                subscription = self.active_subscriptions[subscription_id]
                await subscription.modify_subscription(new_interval)

                # Update stored info
                self.subscriptions[subscription_id]["interval"] = new_interval

                logger.info(
                    "Modified subscription %s interval to %f ms",
                    subscription_id,
                    new_interval,
                )
                return True
            else:
                logger.warning(
                    "Subscription %s not found for modification", subscription_id
                )
                return False

        except Exception as e:
            logger.error("Error modifying subscription %s: %s", subscription_id, e)
            return False

    async def add_nodes_to_subscription(
        self, subscription_id: str, node_ids: list[str]
    ) -> bool:
        """Add additional nodes to an existing subscription.

        Args:
            subscription_id: Subscription ID
            node_ids: Additional node IDs to monitor

        Returns:
            True if successfully added
        """
        try:
            if subscription_id in self.active_subscriptions:
                subscription = self.active_subscriptions[subscription_id]

                # Subscribe to additional nodes
                nodes = [self.client.get_node(node_id) for node_id in node_ids]
                monitored_items = await subscription.subscribe_data_change(nodes)

                # Update stored info
                sub_info = self.subscriptions[subscription_id]
                sub_info["node_ids"].extend(node_ids)
                sub_info["monitored_items"] += len(monitored_items)

                logger.info(
                    "Added %d nodes to subscription %s", len(node_ids), subscription_id
                )
                return True
            else:
                logger.warning(
                    "Subscription %s not found for adding nodes", subscription_id
                )
                return False

        except Exception as e:
            logger.error(
                "Error adding nodes to subscription %s: %s", subscription_id, e
            )
            return False

    async def create_event_subscription(
        self, callback: Callable[[dict[str, Any]], None], interval: float = 1000.0
    ) -> str:
        """Create subscription for OPC-UA events.

        Args:
            callback: Function called on events
            interval: Publishing interval in milliseconds

        Returns:
            Subscription ID
        """
        subscription_id = str(uuid.uuid4())

        try:
            # Create event handler
            class EventHandler:
                def __init__(self, cb):
                    self.callback = cb

                def event_notification(self, event):
                    try:
                        event_data = {
                            "event_type": str(event.EventType),
                            "source_node": str(event.SourceNode),
                            "message": str(event.Message.Text)
                            if hasattr(event, "Message")
                            else "",
                            "severity": event.Severity
                            if hasattr(event, "Severity")
                            else 0,
                            "time": event.Time
                            if hasattr(event, "Time")
                            else datetime.now(),
                        }
                        self.callback(event_data)
                    except Exception as e:
                        logger.error("Error in event handler: %s", e)

            handler = EventHandler(callback)
            subscription = await self.client.create_subscription(interval, handler)

            # Subscribe to server object events
            server_node = self.client.get_node("i=2253")  # Server object
            await subscription.subscribe_events(server_node)

            # Store subscription info
            self.subscriptions[subscription_id] = {
                "id": subscription_id,
                "type": "events",
                "interval": interval,
                "created_at": datetime.now(),
                "callback": callback,
                "handler": handler,
            }

            self.active_subscriptions[subscription_id] = subscription

            logger.info("Created event subscription %s", subscription_id)
            return subscription_id

        except Exception as e:
            logger.error("Error creating event subscription: %s", e)
            raise

    async def get_status(self) -> dict[str, Any]:
        """Get overall subscription manager status.

        Returns:
            Status information
        """
        active_count = len(self.active_subscriptions)
        total_nodes = sum(
            sub_info.get("monitored_items", 0)
            for sub_info in self.subscriptions.values()
        )

        return {
            "active_subscriptions": active_count,
            "total_subscriptions": len(self.subscriptions),
            "total_monitored_nodes": total_nodes,
            "subscription_ids": list(self.subscriptions.keys()),
        }

    async def cleanup(self) -> None:
        """Clean up all subscriptions."""
        logger.info("Cleaning up %d subscriptions", len(self.active_subscriptions))

        for subscription_id in list(self.active_subscriptions.keys()):
            try:
                await self.remove_subscription(subscription_id)
            except Exception as e:
                logger.error(
                    "Error cleaning up subscription %s: %s", subscription_id, e
                )

        self.subscriptions.clear()
        self.active_subscriptions.clear()
