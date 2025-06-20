"""REST API adapter (placeholder implementation)."""

from typing import Any

from .base_adapter import BaseDataAdapter


class RESTAdapter(BaseDataAdapter):
    """REST API data source adapter."""

    async def connect(self) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        return True

    async def test_connection(self) -> bool:
        return self._connected

    async def read_data(
        self, query: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        return [
            {"endpoint": "/api/data", "response": {"value": 42}, "source_type": "rest"}
        ]

    async def write_data(self, data: list[dict[str, Any]]) -> bool:
        return True

    async def stream_data(
        self, callback: callable, query: dict[str, Any] | None = None
    ) -> None:
        pass
