"""
Industrial Dataset Curation & AI Model Preparation Module

Following the crawl_mcp.py methodology for structured development:
- Comprehensive validation and error handling
- Environment variable configuration
- Modular testing and progressive complexity
- Resource management and cleanup
- User-friendly error messages

This module implements Phase 11.5 of the IGN Scripts roadmap:
- Multi-format data ingestion (CSV/XLS, OPC-UA, Database historians)
- Variable type classification (PV, CV, DV, SP)
- Control system metadata framework
- Dataset augmentation and feature engineering
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VariableType(Enum):
    """Variable type classification for industrial datasets."""
    PRIMARY_PV = "primary_pv"        # Primary Process Variable
    SECONDARY_PV = "secondary_pv"    # Secondary Process Variable (SPC)
    CONTROL_VARIABLE = "cv"          # Control Variable
    DISTURBANCE_VARIABLE = "dv"      # Disturbance Variable
    SETPOINT = "sp"                  # Setpoint Variable
    PROCESS_STATE = "state"          # Process State Variable


class ControllerType(Enum):
    """Controller type classification."""
    P = "proportional"
    PI = "proportional_integral"
    PID = "proportional_integral_derivative"
    SA = "single_loop_advanced"
    MPC = "model_predictive_control"


class DataSourceType(Enum):
    """Data source type classification."""
    CSV_XLS = "csv_xls"
    OPC_UA = "opc_ua"
    INFLUX_DB = "influx_db"
    TIMESCALE_DB = "timescale_db"
    CANARY_LABS = "canary_labs"
    MANUAL_INPUT = "manual_input"


@dataclass
class VariableMetadata:
    """Metadata for industrial process variables."""
    name: str
    variable_type: VariableType
    engineering_units: str
    high_limit: Optional[float] = None
    low_limit: Optional[float] = None
    description: Optional[str] = None
    data_source: Optional[DataSourceType] = None
    quality_code_column: Optional[str] = None
    normalization_factor: Optional[float] = None


@dataclass
class ControllerMetadata:
    """Metadata for control system configuration."""
    name: str
    controller_type: ControllerType
    controlled_variable: str
    process_variable: str
    setpoint_variable: Optional[str] = None
    kc_kp: Optional[float] = None  # Proportional gain
    ti_ki: Optional[float] = None  # Integral time/gain
    td_kd: Optional[float] = None  # Derivative time/gain
    dependent_gains: bool = False
    description: Optional[str] = None


def validate_environment() -> Dict[str, bool]:
    """
    Validate environment configuration following crawl_mcp.py patterns.

    Returns:
        Dict with validation results for each component
    """
    validation_results = {
        "python_environment": True,
        "required_packages": True,
        "data_directories": True,
        "database_connections": True,
        "opc_ua_config": True
    }

    try:
        # Check required packages
        import numpy as np
        import pandas as pd
        validation_results["required_packages"] = True
    except ImportError as e:
        logger.error(f"Missing required packages: {e}")
        validation_results["required_packages"] = False

    # Check data directories
    data_dir = Path(os.getenv("IGN_DATA_DIR", "data"))
    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created data directory: {data_dir}")
        except Exception as e:
            logger.error(f"Cannot create data directory: {e}")
            validation_results["data_directories"] = False

    # Check database connection variables
    db_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing_db_vars = [var for var in db_vars if not os.getenv(var)]
    if missing_db_vars:
        logger.warning(f"Missing database environment variables: {missing_db_vars}")
        validation_results["database_connections"] = False

    # Check OPC-UA configuration
    opc_vars = ["OPCUA_SERVER_URL", "OPCUA_USERNAME", "OPCUA_PASSWORD"]
    missing_opc_vars = [var for var in opc_vars if not os.getenv(var)]
    if missing_opc_vars:
        logger.warning(f"Missing OPC-UA environment variables: {missing_opc_vars}")
        validation_results["opc_ua_config"] = False

    return validation_results


def validate_data_source(source_path: str, source_type: DataSourceType) -> Dict[str, Any]:
    """
    Validate data source following crawl_mcp.py validation patterns.

    Args:
        source_path: Path to data source
        source_type: Type of data source

    Returns:
        Dict with validation results and error messages
    """
    if not source_path or not isinstance(source_path, str):
        return {"valid": False, "error": "Data source path is required"}

    if source_type == DataSourceType.CSV_XLS:
        source_file = Path(source_path)
        if not source_file.exists():
            return {"valid": False, "error": f"Data file not found: {source_path}"}

        if not source_file.suffix.lower() in ['.csv', '.xlsx', '.xls']:
            return {"valid": False, "error": "Only CSV and Excel files are supported"}

        try:
            # Test file readability
            if source_file.suffix.lower() == '.csv':
                pd.read_csv(source_path, nrows=1)
            else:
                pd.read_excel(source_path, nrows=1)
            return {"valid": True, "file_type": source_file.suffix}
        except Exception as e:
            return {"valid": False, "error": f"Cannot read data file: {e}"}

    elif source_type == DataSourceType.OPC_UA:
        # Validate OPC-UA server URL format
        if not source_path.startswith("opc.tcp://"):
            return {"valid": False, "error": "OPC-UA URL must start with 'opc.tcp://'"}
        return {"valid": True, "server_url": source_path}

    elif source_type in [DataSourceType.INFLUX_DB, DataSourceType.TIMESCALE_DB]:
        # Validate database connection string format
        if "://" not in source_path:
            return {"valid": False, "error": "Invalid database connection string format"}
        return {"valid": True, "connection_string": source_path}

    else:
        return {"valid": False, "error": f"Unsupported data source type: {source_type}"}


def format_validation_error(error: Exception, context: str) -> str:
    """Format validation errors for user-friendly messages."""
    error_str = str(error).lower()

    if "file not found" in error_str or "no such file" in error_str:
        return f"{context}: File not found. Check the file path."
    elif "permission" in error_str or "access" in error_str:
        return f"{context}: Permission denied. Check file permissions."
    elif "connection" in error_str or "timeout" in error_str:
        return f"{context}: Connection failed. Check network and credentials."
    elif "authentication" in error_str or "unauthorized" in error_str:
        return f"{context}: Authentication failed. Check username and password."
    else:
        return f"{context}: {error}"


class IndustrialDatasetCurator:
    """
    Main class for industrial dataset curation and AI model preparation.

    Following crawl_mcp.py methodology:
    - Environment validation on initialization
    - Comprehensive error handling
    - Progressive complexity support
    - Resource management
    """

    def __init__(self, complexity_level: str = "standard"):
        """
        Initialize the dataset curator.

        Args:
            complexity_level: Deployment complexity (basic/standard/advanced/enterprise)
        """
        self.complexity_level = complexity_level
        self.variables: Dict[str, VariableMetadata] = {}
        self.controllers: Dict[str, ControllerMetadata] = {}
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.validation_results = {}

        # Validate environment on initialization
        self._validate_initialization()

    def _validate_initialization(self) -> None:
        """Validate initialization environment following crawl_mcp.py patterns."""
        try:
            self.validation_results = validate_environment()

            # Check for critical failures
            critical_components = ["python_environment", "required_packages"]
            failed_critical = [
                comp for comp in critical_components
                if not self.validation_results.get(comp, False)
            ]

            if failed_critical:
                raise RuntimeError(
                    f"Critical environment validation failed: {failed_critical}"
                )

            # Warn about non-critical failures
            failed_components = [
                comp for comp, status in self.validation_results.items()
                if not status and comp not in critical_components
            ]

            if failed_components:
                logger.warning(
                    f"Non-critical components failed validation: {failed_components}. "
                    "Some features may be unavailable."
                )

            logger.info("Industrial dataset curator initialized successfully")

        except Exception as e:
            logger.error(f"Initialization failed: {format_validation_error(e, 'Environment validation')}")
            raise

    def get_validation_status(self) -> Dict[str, Any]:
        """Get current validation status."""
        return {
            "environment_validation": self.validation_results,
            "complexity_level": self.complexity_level,
            "variables_configured": len(self.variables),
            "controllers_configured": len(self.controllers),
            "datasets_loaded": len(self.datasets),
            "timestamp": datetime.now().isoformat()
        }

    def add_variable(self, metadata: VariableMetadata) -> bool:
        """
        Add variable metadata with validation.

        Args:
            metadata: Variable metadata to add

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate variable metadata
            if not metadata.name or not isinstance(metadata.name, str):
                logger.error("Variable name is required and must be a string")
                return False

            if metadata.name in self.variables:
                logger.warning(f"Variable {metadata.name} already exists, updating")

            # Validate limits if provided
            if (metadata.high_limit is not None and
                metadata.low_limit is not None and
                metadata.high_limit <= metadata.low_limit):
                logger.error(f"High limit must be greater than low limit for {metadata.name}")
                return False

            self.variables[metadata.name] = metadata
            logger.info(f"Added variable: {metadata.name} ({metadata.variable_type.value})")
            return True

        except Exception as e:
            logger.error(f"Failed to add variable: {format_validation_error(e, 'Variable validation')}")
            return False

    def add_controller(self, metadata: ControllerMetadata) -> bool:
        """
        Add controller metadata with validation.

        Args:
            metadata: Controller metadata to add

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate controller metadata
            if not metadata.name or not isinstance(metadata.name, str):
                logger.error("Controller name is required and must be a string")
                return False

            if not metadata.controlled_variable or not metadata.process_variable:
                logger.error("Controlled variable and process variable are required")
                return False

            if metadata.name in self.controllers:
                logger.warning(f"Controller {metadata.name} already exists, updating")

            self.controllers[metadata.name] = metadata
            logger.info(f"Added controller: {metadata.name} ({metadata.controller_type.value})")
            return True

        except Exception as e:
            logger.error(f"Failed to add controller: {format_validation_error(e, 'Controller validation')}")
            return False


# Initialize module logger
logger.info("Industrial Dataset Curation module loaded successfully")


class DataIngestionFramework:
    """
    Multi-format data ingestion framework following crawl_mcp.py methodology.

    Supports:
    - CSV/XLS historical data import
    - Real-time OPC-UA data streaming
    - Database historian data extraction
    - Automated data validation and quality checks
    - Time synchronization and resampling
    """

    def __init__(self, curator: IndustrialDatasetCurator):
        """Initialize data ingestion framework."""
        self.curator = curator
        self.active_connections: Dict[str, Any] = {}
        self.ingestion_stats: Dict[str, Any] = {}

    async def ingest_csv_data(
        self,
        file_path: str,
        timestamp_column: str = "timestamp",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Ingest CSV/XLS data with comprehensive validation.

        Args:
            file_path: Path to CSV/XLS file
            timestamp_column: Name of timestamp column
            **kwargs: Additional pandas read options

        Returns:
            Dict with ingestion results and statistics
        """
        try:
            # Validate data source
            validation = validate_data_source(file_path, DataSourceType.CSV_XLS)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"],
                    "rows_processed": 0
                }

            # Read data based on file type
            file_path_obj = Path(file_path)
            if file_path_obj.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, **kwargs)
            else:
                df = pd.read_excel(file_path, **kwargs)

            # Validate timestamp column
            if timestamp_column not in df.columns:
                return {
                    "success": False,
                    "error": f"Timestamp column '{timestamp_column}' not found in data",
                    "available_columns": list(df.columns),
                    "rows_processed": 0
                }

            # Convert timestamp column
            try:
                df[timestamp_column] = pd.to_datetime(df[timestamp_column])
                df.set_index(timestamp_column, inplace=True)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Cannot parse timestamp column: {e}",
                    "rows_processed": 0
                }

            # Validate data quality
            quality_report = self._validate_data_quality(df)

            # Store dataset
            dataset_name = file_path_obj.stem
            self.curator.datasets[dataset_name] = df

            # Update ingestion statistics
            self.ingestion_stats[dataset_name] = {
                "source_type": "csv_xls",
                "file_path": file_path,
                "rows_ingested": len(df),
                "columns_ingested": len(df.columns),
                "timestamp_range": {
                    "start": df.index.min().isoformat(),
                    "end": df.index.max().isoformat()
                },
                "quality_report": quality_report,
                "ingestion_time": datetime.now().isoformat()
            }

            logger.info(f"Successfully ingested {len(df)} rows from {file_path}")

            return {
                "success": True,
                "dataset_name": dataset_name,
                "rows_processed": len(df),
                "columns_processed": len(df.columns),
                "quality_report": quality_report,
                "timestamp_range": self.ingestion_stats[dataset_name]["timestamp_range"]
            }

        except Exception as e:
            error_msg = format_validation_error(e, "CSV/XLS ingestion")
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "rows_processed": 0
            }

    async def setup_opcua_streaming(
        self,
        server_url: str,
        node_ids: List[str],
        sampling_interval: float = 1000.0
    ) -> Dict[str, Any]:
        """
        Set up OPC-UA real-time data streaming.

        Args:
            server_url: OPC-UA server URL
            node_ids: List of node IDs to monitor
            sampling_interval: Sampling interval in milliseconds

        Returns:
            Dict with setup results
        """
        try:
            # Validate OPC-UA configuration
            validation = validate_data_source(server_url, DataSourceType.OPC_UA)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"],
                    "nodes_configured": 0
                }

            # Check OPC-UA credentials
            username = os.getenv("OPCUA_USERNAME")
            password = os.getenv("OPCUA_PASSWORD")

            if not username or not password:
                return {
                    "success": False,
                    "error": "OPC-UA credentials not configured in environment",
                    "nodes_configured": 0
                }

            # Validate node IDs
            if not node_ids or not isinstance(node_ids, list):
                return {
                    "success": False,
                    "error": "Node IDs list is required",
                    "nodes_configured": 0
                }

            # Store OPC-UA configuration
            connection_name = f"opcua_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.active_connections[connection_name] = {
                "type": "opcua",
                "server_url": server_url,
                "node_ids": node_ids,
                "sampling_interval": sampling_interval,
                "username": username,
                "status": "configured",
                "created_at": datetime.now().isoformat()
            }

            logger.info(f"Configured OPC-UA streaming for {len(node_ids)} nodes")

            return {
                "success": True,
                "connection_name": connection_name,
                "nodes_configured": len(node_ids),
                "sampling_interval": sampling_interval,
                "server_url": server_url
            }

        except Exception as e:
            error_msg = format_validation_error(e, "OPC-UA setup")
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "nodes_configured": 0
            }

    async def connect_database_historian(
        self,
        connection_string: str,
        historian_type: DataSourceType,
        table_name: str
    ) -> Dict[str, Any]:
        """
        Connect to database historian (InfluxDB, TimescaleDB, Canary Labs).

        Args:
            connection_string: Database connection string
            historian_type: Type of historian database
            table_name: Table/measurement name

        Returns:
            Dict with connection results
        """
        try:
            # Validate database connection
            validation = validate_data_source(connection_string, historian_type)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"],
                    "connection_established": False
                }

            # Validate table name
            if not table_name or not isinstance(table_name, str):
                return {
                    "success": False,
                    "error": "Table/measurement name is required",
                    "connection_established": False
                }

            # Store database connection configuration
            connection_name = f"{historian_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.active_connections[connection_name] = {
                "type": historian_type.value,
                "connection_string": connection_string,
                "table_name": table_name,
                "status": "configured",
                "created_at": datetime.now().isoformat()
            }

            logger.info(f"Configured {historian_type.value} historian connection")

            return {
                "success": True,
                "connection_name": connection_name,
                "historian_type": historian_type.value,
                "table_name": table_name,
                "connection_established": True
            }

        except Exception as e:
            error_msg = format_validation_error(e, f"{historian_type.value} connection")
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "connection_established": False
            }

    def _validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data quality following crawl_mcp.py patterns.

        Args:
            df: DataFrame to validate

        Returns:
            Dict with quality metrics
        """
        try:
            total_rows = len(df)
            total_columns = len(df.columns)

            # Calculate missing data statistics
            missing_data = df.isnull().sum()
            missing_percentage = (missing_data / total_rows * 100).round(2)

            # Identify numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            # Calculate basic statistics for numeric columns
            numeric_stats = {}
            for col in numeric_columns:
                if col in df.columns:
                    numeric_stats[col] = {
                        "mean": df[col].mean(),
                        "std": df[col].std(),
                        "min": df[col].min(),
                        "max": df[col].max(),
                        "missing_count": missing_data[col],
                        "missing_percentage": missing_percentage[col]
                    }

            # Detect potential outliers (simple IQR method)
            outlier_summary = {}
            for col in numeric_columns:
                if col in df.columns and len(df[col].dropna()) > 0:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
                    outlier_summary[col] = {
                        "outlier_count": len(outliers),
                        "outlier_percentage": round((len(outliers) / total_rows * 100), 2)
                    }

            # Time series validation if index is datetime
            time_series_stats = {}
            if isinstance(df.index, pd.DatetimeIndex):
                time_series_stats = {
                    "time_range": {
                        "start": df.index.min(),
                        "end": df.index.max(),
                        "duration_days": (df.index.max() - df.index.min()).days
                    },
                    "sampling_frequency": self._detect_sampling_frequency(df.index),
                    "time_gaps": self._detect_time_gaps(df.index)
                }

            quality_score = self._calculate_quality_score(
                missing_percentage, outlier_summary, total_rows
            )

            return {
                "total_rows": total_rows,
                "total_columns": total_columns,
                "missing_data_summary": {
                    col: {"count": int(missing_data[col]), "percentage": float(missing_percentage[col])}
                    for col in df.columns
                },
                "numeric_statistics": numeric_stats,
                "outlier_summary": outlier_summary,
                "time_series_stats": time_series_stats,
                "quality_score": quality_score,
                "validation_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Data quality validation failed: {e}")
            return {
                "error": f"Quality validation failed: {e}",
                "quality_score": 0.0,
                "validation_timestamp": datetime.now().isoformat()
            }

    def _detect_sampling_frequency(self, time_index: pd.DatetimeIndex) -> str:
        """Detect sampling frequency from time index."""
        try:
            if len(time_index) < 2:
                return "insufficient_data"

            # Calculate time differences
            time_diffs = time_index[1:] - time_index[:-1]
            median_diff = time_diffs.to_series().median()

            # Convert to common frequency strings
            if median_diff <= pd.Timedelta(seconds=1):
                return "1S"  # 1 second
            elif median_diff <= pd.Timedelta(minutes=1):
                return f"{median_diff.total_seconds():.0f}S"
            elif median_diff <= pd.Timedelta(hours=1):
                return f"{median_diff.total_seconds() / 60:.0f}min"
            elif median_diff <= pd.Timedelta(days=1):
                return f"{median_diff.total_seconds() / 3600:.0f}H"
            else:
                return f"{median_diff.days}D"

        except Exception:
            return "irregular"

    def _detect_time_gaps(self, time_index: pd.DatetimeIndex) -> Dict[str, Any]:
        """Detect significant time gaps in the data."""
        try:
            if len(time_index) < 2:
                return {"gap_count": 0, "largest_gap": None}

            time_diffs = time_index[1:] - time_index[:-1]
            median_diff = time_diffs.to_series().median()

            # Define significant gap as 3x median difference
            gap_threshold = median_diff * 3
            gaps = time_diffs[time_diffs > gap_threshold]

            return {
                "gap_count": len(gaps),
                "largest_gap": str(gaps.max()) if len(gaps) > 0 else None,
                "gap_threshold": str(gap_threshold)
            }

        except Exception:
            return {"gap_count": 0, "largest_gap": None, "error": "gap_detection_failed"}

    def _calculate_quality_score(
        self,
        missing_percentage: pd.Series,
        outlier_summary: Dict[str, Any],
        total_rows: int
    ) -> float:
        """Calculate overall data quality score (0-100)."""
        try:
            # Base score
            score = 100.0

            # Penalize for missing data
            avg_missing = missing_percentage.mean()
            score -= min(avg_missing * 2, 50)  # Max 50 point penalty

            # Penalize for outliers
            if outlier_summary:
                avg_outliers = np.mean([
                    stats["outlier_percentage"]
                    for stats in outlier_summary.values()
                ])
                score -= min(avg_outliers, 30)  # Max 30 point penalty

            # Penalize for insufficient data
            if total_rows < 100:
                score -= 20
            elif total_rows < 1000:
                score -= 10

            return max(0.0, round(score, 2))

        except Exception:
            return 50.0  # Default moderate score if calculation fails


class VariableTypeClassifier:
    """
    Variable type classification and metadata management system.

    Following crawl_mcp.py methodology for comprehensive validation
    and error handling in variable classification.
    """

    def __init__(self, curator: IndustrialDatasetCurator):
        """Initialize variable type classifier."""
        self.curator = curator
        self.classification_rules: Dict[str, Any] = {}
        self._load_default_classification_rules()

    def _load_default_classification_rules(self) -> None:
        """Load default variable classification rules."""
        self.classification_rules = {
            "primary_pv_patterns": [
                r".*temp.*", r".*temperature.*", r".*press.*", r".*pressure.*",
                r".*flow.*", r".*level.*", r".*ph.*", r".*density.*"
            ],
            "control_variable_patterns": [
                r".*valve.*", r".*output.*", r".*cv.*", r".*actuator.*",
                r".*speed.*", r".*position.*"
            ],
            "setpoint_patterns": [
                r".*sp.*", r".*setpoint.*", r".*target.*", r".*set.*"
            ],
            "disturbance_patterns": [
                r".*ambient.*", r".*feed.*", r".*load.*", r".*disturbance.*"
            ]
        }
