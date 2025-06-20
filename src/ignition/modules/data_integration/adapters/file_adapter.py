"""File data source adapter (placeholder implementation)."""

from typing import Any

from .base_adapter import BaseDataAdapter


class FileAdapter(BaseDataAdapter):
    """File data source adapter (CSV, JSON, XML, etc.)."""

    async def connect(self) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        return True

    async def test_connection(self) -> bool:
        return self._connected

    async def read_data(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return [{"filename": "data.csv", "row": 1, "data": {"col1": "value1"}, "source_type": "file"}]

    async def write_data(self, data: list[dict[str, Any]]) -> bool:
        return True

    async def stream_data(self, callback: callable, query: dict[str, Any] | None = None) -> None:
        pass
