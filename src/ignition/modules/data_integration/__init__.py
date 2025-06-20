"""Ignition Data Integration Module.

This module provides comprehensive enterprise data connectivity capabilities
for pulling data from various sources including:
- OPC-UA servers
- MQTT brokers
- Kafka streams
- Relational databases (PostgreSQL, MySQL, SQL Server, Oracle)
- Time-series databases (InfluxDB, TimescaleDB, Prometheus)
- Document databases (MongoDB, CouchDB)
- Graph databases (Neo4j)
- REST APIs and web services
- File-based sources (CSV, XML, JSON)
- Custom protocols

Key Features:
- Real-time data streaming and batch processing
- Connection pooling and management
- Data transformation and validation
- Pipeline processing with configurable stages
- Enterprise security and authentication
- Performance monitoring and statistics
- Integration with Ignition tag system
- Configuration persistence and management

Usage:
    from ignition.modules.data_integration import (
        DataIntegrationModule,
        DataSourceConfig,
        DataIntegrationStats,
        create_data_integration_module
    )
"""

from .integration_module import (
    DataIntegrationModule,
    DataIntegrationStats,
    DataSourceConfig,
    DataSourceType,
    VariableMetadata,
    VariableType,
    create_data_integration_module,
)

__all__ = [
    "DataIntegrationModule",
    "DataIntegrationStats",
    "DataSourceConfig",
    "DataSourceType",
    "VariableMetadata",
    "VariableType",
    "create_data_integration_module",
]

__version__ = "1.0.0"
