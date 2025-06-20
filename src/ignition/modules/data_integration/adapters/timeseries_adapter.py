"""Time-series database adapter (placeholder implementation)."""

from typing import Any

from .base_adapter import BaseDataAdapter


class TimeSeriesAdapter(BaseDataAdapter):
    """Time-series database adapter (InfluxDB, TimescaleDB, etc.)."""

    async def connect(self) -> bool:
        self._connected = True
        self.logger.info(f"Connected to time-series DB: {self.config.source_id}")
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
            {
                "measurement": "process_values",
                "time": "2024-01-15T10:30:00Z",
                "fields": {"temperature": 23.4, "pressure": 1013.25},
                "tags": {"location": "reactor_1", "unit": "celsius"},
                "source_type": "timeseries",
                "source_id": self.config.source_id,
            }
        ]

    async def write_data(self, data: list[dict[str, Any]]) -> bool:
        self.logger.info(f"Wrote {len(data)} time-series points")
        return True

    async def stream_data(
        self, callback: callable, query: dict[str, Any] | None = None
    ) -> None:
        pass
