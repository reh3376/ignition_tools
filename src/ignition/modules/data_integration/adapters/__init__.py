"""Data source adapters for the Data Integration Module.

This package provides connection adapters for various enterprise data sources
including industrial automation systems, databases, and other data sources.
"""

from .base_adapter import BaseDataAdapter
from .database_adapter import DatabaseAdapter
from .document_adapter import DocumentAdapter
from .file_adapter import FileAdapter
from .graph_adapter import GraphAdapter
from .kafka_adapter import KafkaAdapter
from .mqtt_adapter import MQTTAdapter
from .opcua_adapter import OPCUAAdapter
from .rest_adapter import RESTAdapter
from .timeseries_adapter import TimeSeriesAdapter

__all__ = [
    "BaseDataAdapter",
    "DatabaseAdapter",
    "DocumentAdapter",
    "FileAdapter",
    "GraphAdapter",
    "KafkaAdapter",
    "MQTTAdapter",
    "OPCUAAdapter",
    "RESTAdapter",
    "TimeSeriesAdapter",
]
