"""OPC-UA Address Space Browser.

Provides functionality for browsing and navigating OPC-UA server
address spaces with filtering and search capabilities.
"""

import logging
from typing import Any

from asyncua import Client, Node
from asyncua.ua import NodeClass

logger = logging.getLogger(__name__)


class AddressSpaceBrowser:
    """Browses OPC-UA server address space and provides navigation utilities."""

    def __init__(self, client: Client):
        """Initialize address space browser.

        Args:
            client: AsyncUA client instance
        """
        self.client = client

    async def browse_tree(
        self, node_id: str = "i=85", max_depth: int = 3
    ) -> dict[str, Any]:
        """Browse OPC-UA address space starting from specified node.

        Args:
            node_id: Starting node ID (default: Objects folder)
            max_depth: Maximum browsing depth

        Returns:
            Dictionary containing browsed tree structure
        """
        try:
            root_node = self.client.get_node(node_id)
            tree = await self._browse_node_recursive(root_node, max_depth, 0)
            return tree

        except Exception as e:
            logger.error("Error browsing tree from %s: %s", node_id, e)
            raise

    async def _browse_node_recursive(
        self, node: Node, max_depth: int, current_depth: int
    ) -> dict[str, Any]:
        """Recursively browse a node and its children.

        Args:
            node: Node to browse
            max_depth: Maximum recursion depth
            current_depth: Current recursion depth

        Returns:
            Dictionary containing node information and children
        """
        try:
            # Get node information
            node_info = await self.get_node_info(node)

            # Add children if within depth limit
            if current_depth < max_depth:
                children = await node.get_children()
                node_info["children"] = []

                for child in children:
                    try:
                        child_info = await self._browse_node_recursive(
                            child, max_depth, current_depth + 1
                        )
                        node_info["children"].append(child_info)
                    except Exception as e:
                        logger.warning("Error browsing child node: %s", e)
                        continue
            else:
                # Check if node has children (without browsing them)
                children = await node.get_children()
                node_info["has_children"] = len(children) > 0

            return node_info

        except Exception as e:
            logger.error("Error browsing node %s: %s", node, e)
            raise

    async def get_node_info(self, node: Node) -> dict[str, Any]:
        """Get detailed information about a specific node.

        Args:
            node: Node to inspect

        Returns:
            Dictionary with node details
        """
        try:
            # Basic node information
            node_id = node.nodeid
            info = {
                "node_id": str(node_id),
                "namespace_index": node_id.NamespaceIndex,
                "identifier": str(node_id.Identifier),
            }

            # Read attributes
            try:
                info["browse_name"] = str(await node.read_browse_name())
                info["display_name"] = str(await node.read_display_name())
                info["node_class"] = str(await node.read_node_class())
                info["description"] = str(await node.read_description())
            except Exception as e:
                logger.debug("Error reading basic attributes: %s", e)

            # Additional attributes for Variable nodes
            if await self._is_variable_node(node):
                try:
                    info["data_type"] = str(await node.read_data_type())
                    info["value"] = await node.read_value()
                    info["access_level"] = await node.read_access_level()
                except Exception as e:
                    logger.debug("Error reading variable attributes: %s", e)

            # Additional attributes for Object nodes
            elif await self._is_object_node(node):
                try:
                    info["type_definition"] = str(await node.read_type_definition())
                except Exception as e:
                    logger.debug("Error reading object attributes: %s", e)

            return info

        except Exception as e:
            logger.error("Error getting node info for %s: %s", node, e)
            return {"node_id": str(node.nodeid), "error": str(e)}

    async def _is_variable_node(self, node: Node) -> bool:
        """Check if node is a Variable node."""
        try:
            node_class = await node.read_node_class()
            return node_class == NodeClass.Variable
        except Exception:
            return False

    async def _is_object_node(self, node: Node) -> bool:
        """Check if node is an Object node."""
        try:
            node_class = await node.read_node_class()
            return node_class == NodeClass.Object
        except Exception:
            return False

    async def find_nodes_by_browse_name(
        self, browse_name: str, start_node: str = "i=85"
    ) -> list[dict[str, Any]]:
        """Find nodes by browse name starting from specified node.

        Args:
            browse_name: Browse name to search for
            start_node: Starting node ID for search

        Returns:
            List of matching nodes
        """
        matches = []

        try:
            root = self.client.get_node(start_node)
            await self._search_by_browse_name(root, browse_name, matches, max_depth=5)

        except Exception as e:
            logger.error("Error searching for browse name %s: %s", browse_name, e)

        return matches

    async def _search_by_browse_name(
        self,
        node: Node,
        target_name: str,
        matches: list[dict[str, Any]],
        current_depth: int = 0,
        max_depth: int = 5,
    ):
        """Recursively search for nodes by browse name.

        Args:
            node: Current node to search from
            target_name: Target browse name
            matches: List to collect matches
            current_depth: Current search depth
            max_depth: Maximum search depth
        """
        if current_depth >= max_depth:
            return

        try:
            # Check current node
            browse_name = str(await node.read_browse_name())
            if target_name.lower() in browse_name.lower():
                node_info = await self.get_node_info(node)
                matches.append(node_info)

            # Search children
            children = await node.get_children()
            for child in children:
                try:
                    await self._search_by_browse_name(
                        child, target_name, matches, current_depth + 1, max_depth
                    )
                except Exception as e:
                    logger.debug("Error searching child node: %s", e)
                    continue

        except Exception as e:
            logger.debug("Error in browse name search: %s", e)

    async def get_node_path(self, node_id: str) -> list[str]:
        """Get the browse path from root to specified node.

        Args:
            node_id: Target node ID

        Returns:
            List of browse names forming the path
        """
        try:
            node = self.client.get_node(node_id)
            path = []

            # Get path by walking up the hierarchy
            current = node
            while current:
                try:
                    browse_name = str(await current.read_browse_name())
                    path.insert(0, browse_name)

                    # Get parent
                    parents = await current.get_parent()
                    if parents and str(parents.nodeid) != "i=84":  # Stop at Root
                        current = parents
                    else:
                        break

                except Exception as e:
                    logger.debug("Error getting parent: %s", e)
                    break

            return path

        except Exception as e:
            logger.error("Error getting node path for %s: %s", node_id, e)
            return []

    async def get_variable_nodes(
        self, start_node: str = "i=85"
    ) -> list[dict[str, Any]]:
        """Get all variable nodes from specified starting point.

        Args:
            start_node: Starting node ID

        Returns:
            List of variable node information
        """
        variables = []

        try:
            root = self.client.get_node(start_node)
            await self._collect_variable_nodes(root, variables, max_depth=10)

        except Exception as e:
            logger.error("Error collecting variable nodes: %s", e)

        return variables

    async def _collect_variable_nodes(
        self,
        node: Node,
        variables: list[dict[str, Any]],
        current_depth: int = 0,
        max_depth: int = 10,
    ):
        """Recursively collect all variable nodes.

        Args:
            node: Current node
            variables: List to collect variables
            current_depth: Current depth
            max_depth: Maximum depth
        """
        if current_depth >= max_depth:
            return

        try:
            # Check if current node is a variable
            if await self._is_variable_node(node):
                node_info = await self.get_node_info(node)
                variables.append(node_info)

            # Process children
            children = await node.get_children()
            for child in children:
                try:
                    await self._collect_variable_nodes(
                        child, variables, current_depth + 1, max_depth
                    )
                except Exception as e:
                    logger.debug("Error processing child variable: %s", e)
                    continue

        except Exception as e:
            logger.debug("Error collecting variables: %s", e)
