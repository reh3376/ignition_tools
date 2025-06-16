"""MCP (Machine Control Program) Client.

Provides a Python interface for interacting with MCP Docker services,
including the main MCP API and MCP Tools API.
"""

import logging
import os
from typing import Any, cast

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP Client for interacting with MCP Docker services."""

    def __init__(self) -> None:
        """Initialize the MCP Client."""
        self.logger = logging.getLogger(__name__)

        # MCP API Configuration
        self.mcp_api_url = os.getenv("MCP_API_URL", "http://localhost:8080")
        self.mcp_api_key = os.getenv("MCP_API_KEY", "default_key")

        # MCP Tools API Configuration
        self.mcp_tools_url = os.getenv("MCP_TOOLS_API_URL", "http://localhost:8082")
        self.mcp_tools_api_key = os.getenv("MCP_TOOLS_API_KEY", "default_tools_key")

        # Common headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        is_tools: bool = False,
    ) -> dict[str, Any]:
        """Make a request to the MCP API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data (for POST/PUT)
            is_tools: Whether to use MCP Tools API

        Returns:
            API response data
        """
        try:
            base_url = self.mcp_tools_url if is_tools else self.mcp_api_url
            api_key = self.mcp_tools_api_key if is_tools else self.mcp_api_key

            headers = {
                **self.headers,
                "X-API-Key": api_key,
            }

            url = f"{base_url}{endpoint}"

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=30,
            )

            response.raise_for_status()
            return cast("dict[str, Any]", response.json())

        except requests.exceptions.RequestException as e:
            self.logger.error(f"MCP API request failed: {e}")
            raise

    def get_health(self, is_tools: bool = False) -> dict[str, Any]:
        """Get health status of MCP service.

        Args:
            is_tools: Whether to check MCP Tools API health

        Returns:
            Health status information
        """
        return self._make_request("GET", "/health", is_tools=is_tools)

    def get_mcp_status(self) -> dict[str, Any]:
        """Get status of MCP service.

        Returns:
            MCP service status information
        """
        return self._make_request("GET", "/status")

    def get_tools_status(self) -> dict[str, Any]:
        """Get status of MCP Tools service.

        Returns:
            MCP Tools service status information
        """
        return self._make_request("GET", "/status", is_tools=True)

    def execute_mcp_command(self, command: str, parameters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute an MCP command.

        Args:
            command: Command to execute
            parameters: Command parameters

        Returns:
            Command execution result
        """
        data = {
            "command": command,
            "parameters": parameters or {},
        }
        return self._make_request("POST", "/execute", data=data)

    def get_mcp_logs(self, limit: int = 100, level: str | None = None) -> dict[str, Any]:
        """Get MCP service logs.

        Args:
            limit: Maximum number of log entries to return
            level: Log level filter (DEBUG, INFO, WARNING, ERROR)

        Returns:
            Log entries
        """
        params: dict[str, Any] = {"limit": limit}
        if level:
            params["level"] = level
        return self._make_request("GET", "/logs", data=params)

    def get_tools_logs(self, limit: int = 100, level: str | None = None) -> dict[str, Any]:
        """Get MCP Tools service logs.

        Args:
            limit: Maximum number of log entries to return
            level: Log level filter (DEBUG, INFO, WARNING, ERROR)

        Returns:
            Log entries
        """
        params: dict[str, Any] = {"limit": limit}
        if level:
            params["level"] = level
        return self._make_request("GET", "/logs", data=params, is_tools=True)
