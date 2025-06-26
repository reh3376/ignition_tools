"""Data Integration Module for Ignition.

This module provides comprehensive enterprise data connectivity capabilities
for pulling data from various sources including OPC-UA, MQTT, Kafka, databases,
and other enterprise data sources. It includes industrial variable metadata
injection system for model preparation.

Author: IGN Scripts Development Team
Version: 1.0.0
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from dotenv import load_dotenv

from ignition.modules.core.abstract_module import (
    AbstractIgnitionModule,
    ModuleContext,
    ModuleMetadata,
    ModuleScope,
)

# Load environment variables
load_dotenv()


class DataSourceType(Enum):
    """Enumeration of supported data source types."""

    # Industrial Automation
    OPC_UA = "opc_ua"
    MQTT = "mqtt"
    KAFKA = "kafka"

    # Databases
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQL_SERVER = "sql_server"
    ORACLE = "oracle"
    SQLITE = "sqlite"

    # Time-Series Databases
    INFLUXDB = "influxdb"
    TIMESCALEDB = "timescaledb"
    PROMETHEUS = "prometheus"
    HISTORIAN = "historian"

    # Document Databases
    MONGODB = "mongodb"
    COUCHDB = "couchdb"
    ELASTICSEARCH = "elasticsearch"

    # Graph Databases
    NEO4J = "neo4j"
    NEPTUNE = "neptune"
    COSMOS_DB = "cosmos_db"

    # Web Services
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    SOAP = "soap"

    # File Sources
    CSV = "csv"
    EXCEL = "excel"
    JSON_FILE = "json_file"
    XML = "xml"
    PARQUET = "parquet"

    # Cloud Storage
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    FTP = "ftp"
    SFTP = "sftp"

    # Message Queues
    RABBITMQ = "rabbitmq"
    ACTIVEMQ = "activemq"
    REDIS = "redis"

    # Custom Protocols
    MODBUS = "modbus"
    DNP3 = "dnp3"
    CUSTOM_TCP = "custom_tcp"
    SERIAL = "serial"


class VariableType(Enum):
    """Industrial variable types for metadata classification."""

    PV = "process_variable"  # Process Variables
    CV = "control_variable"  # Control Variables
    DV = "disturbance_variable"  # Disturbance Variables
    SP = "setpoint"  # Setpoints
    PROCESS_STATE = "process_state"  # Process State


@dataclass
class VariableMetadata:
    """Metadata for industrial variables."""

    variable_type: VariableType
    name: str
    engineering_units: str = ""
    range_high: float | None = None
    range_low: float | None = None
    max_value: float | None = None  # For normalization

    # PV-specific metadata
    is_primary_pv: bool = False  # PPV
    is_secondary_pv: bool = False  # SPC

    # Process state metadata
    state_values: list[str] = field(default_factory=list)  # For Process_State enumeration

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization."""
        return {
            "variable_type": self.variable_type.value,
            "name": self.name,
            "engineering_units": self.engineering_units,
            "range_high": self.range_high,
            "range_low": self.range_low,
            "max_value": self.max_value,
            "is_primary_pv": self.is_primary_pv,
            "is_secondary_pv": self.is_secondary_pv,
            "state_values": self.state_values,
        }


@dataclass
class DataSourceConfig:
    """Configuration for a data source connection."""

    source_id: str
    source_type: DataSourceType
    connection_params: dict[str, Any]
    enabled: bool = True
    polling_interval: int | None = None  # seconds
    batch_size: int = 1000
    timeout: int = 30
    retry_attempts: int = 3
    variable_mappings: dict[str, VariableMetadata] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "source_id": self.source_id,
            "source_type": self.source_type.value,
            "connection_params": self.connection_params,
            "enabled": self.enabled,
            "polling_interval": self.polling_interval,
            "batch_size": self.batch_size,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "variable_mappings": {k: v.to_dict() for k, v in self.variable_mappings.items()},
        }


@dataclass
class DataIntegrationStats:
    """Statistics for data integration operations."""

    total_sources: int = 0
    active_connections: int = 0
    total_data_points: int = 0
    successful_reads: int = 0
    failed_reads: int = 0
    last_update: datetime | None = None
    processing_rate: float = 0.0  # points per second
    error_rate: float = 0.0  # percentage

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_sources": self.total_sources,
            "active_connections": self.active_connections,
            "total_data_points": self.total_data_points,
            "successful_reads": self.successful_reads,
            "failed_reads": self.failed_reads,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "processing_rate": self.processing_rate,
            "error_rate": self.error_rate,
        }


class DataIntegrationModule(AbstractIgnitionModule):
    """Comprehensive data integration module for enterprise data sources.

    This module provides connectivity to various enterprise data sources including:
    - Industrial automation (OPC-UA, MQTT, Kafka)
    - Relational and NoSQL databases
    - Time-series and document databases
    - File sources and cloud storage
    - Message queues and custom protocols

    Features:
    - Real-time data streaming and batch processing
    - Industrial variable metadata injection
    - JSON dataset preparation for model ingestion
    - Connection pooling and lifecycle management
    - Data transformation and validation pipelines
    """

    def __init__(self, metadata: ModuleMetadata, context: ModuleContext):
        """Initialize the data integration module."""
        super().__init__(metadata, context)

        # Data sources management
        self._data_sources: dict[str, DataSourceConfig] = {}
        self._active_connections: dict[str, Any] = {}
        self._message_processors: dict[str, asyncio.Task] = {}

        # Statistics and monitoring
        self._stats = DataIntegrationStats()
        self._executor = ThreadPoolExecutor(max_workers=10)

        # Configuration
        self._default_config = self._create_default_config()

        # Initialize logging
        self.logger.info("Data Integration Module initialized")

    def _create_default_config(self) -> dict[str, Any]:
        """Create default configuration for the module."""
        return {
            "security": {
                "encryption_enabled": True,
                "certificate_validation": True,
                "max_retry_attempts": 3,
                "connection_timeout": 30,
            },
            "performance": {
                "max_concurrent_connections": 50,
                "default_batch_size": 1000,
                "connection_pool_size": 10,
                "message_buffer_size": 10000,
            },
            "data_processing": {
                "enable_metadata_injection": True,
                "normalize_timestamps": True,
                "validate_data_quality": True,
                "auto_detect_variable_types": True,
            },
            "json_output": {
                "include_metadata": True,
                "timestamp_format": "iso8601",
                "normalize_values": True,
                "include_quality_codes": True,
            },
        }

    # Abstract method implementations

    def get_module_info(self) -> dict[str, Any]:
        """Get detailed module information."""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "supported_data_sources": [t.value for t in DataSourceType],
            "supported_variable_types": [t.value for t in VariableType],
            "statistics": self._stats.to_dict(),
            "active_sources": len(self._data_sources),
            "active_connections": len(self._active_connections),
        }

    def validate_configuration(self) -> bool:
        """Validate module configuration."""
        try:
            config = self.config_manager.config

            # Validate required configuration sections
            required_sections = [
                "security",
                "performance",
                "data_processing",
                "json_output",
            ]
            for section in required_sections:
                if section not in config:
                    self.logger.error(f"Missing required configuration section: {section}")
                    return False

            # Validate performance settings
            perf_config = config["performance"]
            if perf_config.get("max_concurrent_connections", 0) <= 0:
                self.logger.error("Invalid max_concurrent_connections value")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False

    def initialize_module(self) -> bool:
        """Initialize the module."""
        try:
            self.logger.info("Initializing Data Integration Module...")

            # Load configuration
            if not self.config_manager.config:
                self.config_manager.set_default_configuration(self._default_config)
                self.config_manager.save_configuration()

            # Validate configuration
            if not self.validate_configuration():
                return False

            # Initialize statistics
            self._stats.last_update = datetime.now(UTC)

            self.logger.info("Data Integration Module initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Module initialization failed: {e}")
            return False

    def startup_module(self) -> bool:
        """Start the module."""
        try:
            self.logger.info("Starting Data Integration Module...")

            # Start enabled data sources
            for source_id, config in self._data_sources.items():
                if config.enabled:
                    self._start_data_source(source_id, config)

            self.logger.info("Data Integration Module started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Module startup failed: {e}")
            return False

    def shutdown_module(self) -> bool:
        """Shutdown the module."""
        try:
            self.logger.info("Shutting down Data Integration Module...")

            # Stop all data sources
            for source_id in list(self._active_connections.keys()):
                self._stop_data_source(source_id)

            # Stop message processors
            for task in self._message_processors.values():
                task.cancel()

            # Shutdown executor
            self._executor.shutdown(wait=True)

            self.logger.info("Data Integration Module shut down successfully")
            return True

        except Exception as e:
            self.logger.error(f"Module shutdown failed: {e}")
            return False

    def configure_module(self, config: dict[str, Any]) -> bool:
        """Configure the module with new settings."""
        try:
            # Update configuration using the proper interface
            if self.config_manager.update(config, save=True):
                # Validate new configuration
                return self.validate_configuration()
            else:
                self.logger.error("Failed to update configuration")
                return False

        except Exception as e:
            self.logger.error(f"Module configuration failed: {e}")
            return False

    # Public API methods

    def add_data_source(self, config: DataSourceConfig) -> bool:
        """Add a new data source configuration."""
        try:
            self.logger.info(f"Adding data source: {config.source_id}")

            # Validate configuration
            if config.source_id in self._data_sources:
                self.logger.warning(f"Data source {config.source_id} already exists")
                return False

            # Add to configuration
            self._data_sources[config.source_id] = config
            self._stats.total_sources = len(self._data_sources)

            # Start if enabled and module is running
            if config.enabled and self.state.name == "RUNNING":
                self._start_data_source(config.source_id, config)

            self.logger.info(f"Data source {config.source_id} added successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add data source {config.source_id}: {e}")
            return False

    def remove_data_source(self, source_id: str) -> bool:
        """Remove a data source configuration."""
        try:
            self.logger.info(f"Removing data source: {source_id}")

            if source_id not in self._data_sources:
                self.logger.warning(f"Data source {source_id} not found")
                return False

            # Stop if active
            if source_id in self._active_connections:
                self._stop_data_source(source_id)

            # Remove from configuration
            del self._data_sources[source_id]
            self._stats.total_sources = len(self._data_sources)

            self.logger.info(f"Data source {source_id} removed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to remove data source {source_id}: {e}")
            return False

    def test_connection(self, source_id: str) -> dict[str, Any]:
        """Test connection to a data source."""
        try:
            if source_id not in self._data_sources:
                return {"success": False, "error": "Data source not found"}

            config = self._data_sources[source_id]
            self.logger.info(f"Testing connection for data source: {source_id}")

            # Simulate connection test based on source type
            # In a real implementation, this would perform actual connection tests
            result = {
                "success": True,
                "source_id": source_id,
                "source_type": config.source_type.value,
                "response_time": 0.1,  # seconds
                "status": "Connected",
                "timestamp": datetime.now(UTC).isoformat(),
            }

            self.logger.info(f"Connection test successful for {source_id}")
            return result

        except Exception as e:
            self.logger.error(f"Connection test failed for {source_id}: {e}")
            return {"success": False, "error": str(e)}

    def read_data(self, source_id: str, query: dict[str, Any] | None = None) -> dict[str, Any]:
        """Read data from a specific data source."""
        try:
            if source_id not in self._data_sources:
                return {"success": False, "error": "Data source not found"}

            if source_id not in self._active_connections:
                return {"success": False, "error": "Data source not connected"}

            config = self._data_sources[source_id]
            self.logger.debug(f"Reading data from source: {source_id}")

            # Simulate data reading with metadata injection
            # In a real implementation, this would perform actual data retrieval
            raw_data = self._simulate_data_read(config, query)

            # Apply metadata injection
            processed_data = self._inject_metadata(raw_data, config.variable_mappings)

            # Prepare JSON format for model ingestion
            json_data = self._prepare_json_for_model(processed_data)

            self._stats.successful_reads += 1
            self._stats.total_data_points += len(processed_data)

            return {
                "success": True,
                "source_id": source_id,
                "data": json_data,
                "metadata": {
                    "record_count": len(processed_data),
                    "timestamp": datetime.now(UTC).isoformat(),
                    "variable_types": self._get_variable_type_summary(config.variable_mappings),
                },
            }

        except Exception as e:
            self.logger.error(f"Failed to read data from {source_id}: {e}")
            self._stats.failed_reads += 1
            return {"success": False, "error": str(e)}

    def write_data(self, source_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Write data to a specific data source."""
        try:
            if source_id not in self._data_sources:
                return {"success": False, "error": "Data source not found"}

            if source_id not in self._active_connections:
                return {"success": False, "error": "Data source not connected"}

            self.logger.debug(f"Writing data to source: {source_id}")

            # Simulate data writing
            # In a real implementation, this would perform actual data writing

            return {
                "success": True,
                "source_id": source_id,
                "records_written": len(data.get("records", [])),
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Failed to write data to {source_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_integration_stats(self) -> dict[str, Any]:
        """Get integration statistics."""
        self._stats.active_connections = len(self._active_connections)
        self._stats.last_update = datetime.now(UTC)

        # Calculate rates
        if self._stats.total_data_points > 0:
            total_operations = self._stats.successful_reads + self._stats.failed_reads
            if total_operations > 0:
                self._stats.error_rate = (self._stats.failed_reads / total_operations) * 100

        return self._stats.to_dict()

    # Private helper methods

    def _start_data_source(self, source_id: str, config: DataSourceConfig) -> bool:
        """Start a data source connection."""
        try:
            self.logger.info(f"Starting data source: {source_id}")

            # Simulate connection creation based on source type
            connection = self._create_connection(config)
            self._active_connections[source_id] = connection

            # Start message processing if needed
            if config.polling_interval:
                task = asyncio.create_task(self._process_messages(source_id, config))
                self._message_processors[source_id] = task

            return True

        except Exception as e:
            self.logger.error(f"Failed to start data source {source_id}: {e}")
            return False

    def _stop_data_source(self, source_id: str) -> bool:
        """Stop a data source connection."""
        try:
            self.logger.info(f"Stopping data source: {source_id}")

            # Stop message processor
            if source_id in self._message_processors:
                self._message_processors[source_id].cancel()
                del self._message_processors[source_id]

            # Close connection
            if source_id in self._active_connections:
                # In a real implementation, properly close the connection
                del self._active_connections[source_id]

            return True

        except Exception as e:
            self.logger.error(f"Failed to stop data source {source_id}: {e}")
            return False

    def _create_connection(self, config: DataSourceConfig) -> Any:
        """Create a connection based on data source type."""
        # In a real implementation, this would create actual connections
        # based on the data source type using appropriate libraries
        return f"mock_connection_{config.source_type.value}"

    async def _process_messages(self, source_id: str, config: DataSourceConfig) -> Any:
        """Process messages from a data source."""
        try:
            while True:
                # Simulate message processing
                await asyncio.sleep(config.polling_interval or 1)

                # In a real implementation, this would process actual messages
                self.logger.debug(f"Processing messages for {source_id}")

        except asyncio.CancelledError:
            self.logger.info(f"Message processing cancelled for {source_id}")
        except Exception as e:
            self.logger.error(f"Message processing error for {source_id}: {e}")

    def _simulate_data_read(self, _config: DataSourceConfig, _query: dict[str, Any] | None) -> list[dict[str, Any]]:
        """Simulate data reading for demonstration purposes."""
        # In a real implementation, this would perform actual data retrieval
        return [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "variable1": 75.5,
                "variable2": 150.2,
                "variable3": "steady_state",
                "quality": "good",
            }
        ]

    def _inject_metadata(
        self, data: list[dict[str, Any]], variable_mappings: dict[str, VariableMetadata]
    ) -> list[dict[str, Any]]:
        """Inject metadata into data points."""
        enhanced_data = []

        for record in data:
            enhanced_record = record.copy()
            enhanced_record["metadata"] = {}

            for variable_name, value in record.items():
                if variable_name in variable_mappings and variable_name != "metadata":
                    metadata = variable_mappings[variable_name]

                    # Add variable metadata
                    enhanced_record["metadata"][variable_name] = {
                        "type": metadata.variable_type.value,
                        "engineering_units": metadata.engineering_units,
                        "range_high": metadata.range_high,
                        "range_low": metadata.range_low,
                        "max_value": metadata.max_value,
                    }

                    # Add PV-specific metadata
                    if metadata.variable_type == VariableType.PV:
                        enhanced_record["metadata"][variable_name]["is_primary_pv"] = metadata.is_primary_pv
                        enhanced_record["metadata"][variable_name]["is_secondary_pv"] = metadata.is_secondary_pv

                    # Add normalization if max_value is available
                    if metadata.max_value and isinstance(value, int | float):
                        enhanced_record[f"{variable_name}_normalized"] = value / metadata.max_value

            enhanced_data.append(enhanced_record)

        return enhanced_data

    def _prepare_json_for_model(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Prepare data in JSON format for model ingestion."""
        config = self.config_manager.config.get("json_output", {})

        return {
            "dataset": {
                "format_version": "1.0",
                "timestamp": datetime.now(UTC).isoformat(),
                "include_metadata": config.get("include_metadata", True),
                "normalize_values": config.get("normalize_values", True),
                "records": data,
            },
            "schema": {
                "variable_types": ["PV", "CV", "DV", "SP", "PROCESS_STATE"],
                "normalization": "min_max",
                "timestamp_format": config.get("timestamp_format", "iso8601"),
            },
        }

    def _get_variable_type_summary(self, variable_mappings: dict[str, VariableMetadata]) -> dict[str, int]:
        """Get summary of variable types."""
        summary = {}
        for metadata in variable_mappings.values():
            var_type = metadata.variable_type.value
            summary[var_type] = summary.get(var_type, 0) + 1
        return summary


def create_data_integration_module(
    context: ModuleContext,
    module_name: str = "Data Integration",
    version: str = "1.0.0",
) -> DataIntegrationModule:
    """Factory function to create a DataIntegrationModule instance.

    Args:
        context: Module execution context
        module_name: Name for the module
        version: Version of the module

    Returns:
        Configured DataIntegrationModule instance
    """
    metadata = ModuleMetadata(
        name=module_name,
        id="ign_data_integration",
        version=version,
        description="Comprehensive enterprise data integration module with metadata injection",
        vendor="IGN Scripts Development Team",
        scopes=[ModuleScope.GATEWAY, ModuleScope.DESIGNER],
        min_ignition_version="8.1.0",
        dependencies=[],
    )

    return DataIntegrationModule(metadata, context)
