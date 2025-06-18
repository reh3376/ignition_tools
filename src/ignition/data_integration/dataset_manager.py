"""Dataset Management System for AI/ML Model Preparation

This module provides comprehensive dataset creation, curation, and management
capabilities for preparing industrial data for AI supervised learning models.
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatasetType(Enum):
    """Types of datasets for different ML use cases."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    TIME_SERIES = "time_series"
    ANOMALY_DETECTION = "anomaly_detection"
    CLUSTERING = "clustering"
    FORECASTING = "forecasting"


class DataQuality(Enum):
    """Data quality assessment levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class ProcessingStatus(Enum):
    """Dataset processing status."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    VALIDATED = "validated"
    READY = "ready"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


@dataclass
class DataSource:
    """Configuration for a data source."""

    source_id: str
    source_type: str  # database, file, api, historian, opc
    connection_config: dict[str, Any]
    query_config: dict[str, Any] | None = None
    refresh_interval: int | None = None  # minutes
    last_updated: datetime | None = None
    active: bool = True


@dataclass
class FeatureDefinition:
    """Definition of a feature in the dataset."""

    name: str
    data_type: str  # numeric, categorical, datetime, text, boolean
    source_column: str
    transformation: str | None = None  # scaling, encoding, etc.
    is_target: bool = False
    is_feature: bool = True
    missing_value_strategy: str = (
        "drop"  # drop, fill_mean, fill_median, fill_mode, custom
    )
    custom_fill_value: Any | None = None
    validation_rules: list[dict[str, Any]] = field(default_factory=list)
    description: str | None = None


@dataclass
class DatasetSchema:
    """Schema definition for a dataset."""

    schema_id: str
    name: str
    version: str
    dataset_type: DatasetType
    features: list[FeatureDefinition]
    target_variable: str | None = None
    time_column: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    description: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class DataQualityReport:
    """Data quality assessment report."""

    report_id: str
    dataset_id: str
    overall_quality: DataQuality
    completeness_score: float  # 0-100
    consistency_score: float  # 0-100
    accuracy_score: float  # 0-100
    uniqueness_score: float  # 0-100
    timeliness_score: float  # 0-100
    issues: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Dataset:
    """Complete dataset definition and metadata."""

    dataset_id: str
    name: str
    schema: DatasetSchema
    data_sources: list[DataSource]
    status: ProcessingStatus
    quality_report: DataQualityReport | None = None
    row_count: int = 0
    column_count: int = 0
    file_size_mb: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    export_formats: list[str] = field(
        default_factory=lambda: ["csv", "parquet", "json"]
    )


class DatasetManager:
    """Manager for dataset creation, curation, and preparation."""

    def __init__(self, storage_path: str = "./data/datasets"):
        """Initialize the dataset manager."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.storage_path / "raw").mkdir(exist_ok=True)
        (self.storage_path / "processed").mkdir(exist_ok=True)
        (self.storage_path / "schemas").mkdir(exist_ok=True)
        (self.storage_path / "exports").mkdir(exist_ok=True)
        (self.storage_path / "metadata").mkdir(exist_ok=True)

        self.logger = logging.getLogger(f"{__name__}.DatasetManager")

        # Load existing datasets
        self.datasets: dict[str, Dataset] = {}
        self._load_existing_datasets()

    def _load_existing_datasets(self) -> None:
        """Load existing datasets from storage."""
        metadata_path = self.storage_path / "metadata"
        for metadata_file in metadata_path.glob("*.json"):
            try:
                with open(metadata_file) as f:
                    data = json.load(f)
                    dataset = self._dict_to_dataset(data)
                    self.datasets[dataset.dataset_id] = dataset
                    self.logger.info(f"Loaded dataset: {dataset.name}")
            except Exception as e:
                self.logger.error(f"Failed to load dataset from {metadata_file}: {e}")

    def create_dataset(
        self,
        name: str,
        dataset_type: DatasetType,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> Dataset:
        """Create a new dataset."""
        dataset_id = str(uuid.uuid4())
        schema_id = str(uuid.uuid4())

        # Create schema
        schema = DatasetSchema(
            schema_id=schema_id,
            name=f"{name}_schema",
            version="1.0.0",
            dataset_type=dataset_type,
            features=[],
            description=description,
        )

        # Create dataset
        dataset = Dataset(
            dataset_id=dataset_id,
            name=name,
            schema=schema,
            data_sources=[],
            status=ProcessingStatus.DRAFT,
            tags=tags or [],
            metadata={"created_via": "dataset_manager"},
        )

        # Store dataset
        self.datasets[dataset_id] = dataset
        self._save_dataset_metadata(dataset)

        self.logger.info(f"Created new dataset: {name} ({dataset_id})")
        return dataset

    def add_data_source(
        self,
        dataset_id: str,
        source_type: str,
        connection_config: dict[str, Any],
        query_config: dict[str, Any] | None = None,
        refresh_interval: int | None = None,
    ) -> str:
        """Add a data source to a dataset."""
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset {dataset_id} not found")

        source_id = str(uuid.uuid4())
        data_source = DataSource(
            source_id=source_id,
            source_type=source_type,
            connection_config=connection_config,
            query_config=query_config,
            refresh_interval=refresh_interval,
            last_updated=datetime.now(),
        )

        self.datasets[dataset_id].data_sources.append(data_source)
        self.datasets[dataset_id].updated_at = datetime.now()
        self._save_dataset_metadata(self.datasets[dataset_id])

        self.logger.info(f"Added data source {source_id} to dataset {dataset_id}")
        return source_id

    def define_feature(
        self,
        dataset_id: str,
        name: str,
        data_type: str,
        source_column: str,
        is_target: bool = False,
        transformation: str | None = None,
        validation_rules: list[dict[str, Any]] | None = None,
        description: str | None = None,
    ) -> None:
        """Define a feature in the dataset schema."""
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset {dataset_id} not found")

        feature = FeatureDefinition(
            name=name,
            data_type=data_type,
            source_column=source_column,
            transformation=transformation,
            is_target=is_target,
            is_feature=not is_target,
            validation_rules=validation_rules or [],
            description=description,
        )

        dataset = self.datasets[dataset_id]
        dataset.schema.features.append(feature)

        if is_target:
            dataset.schema.target_variable = name

        dataset.updated_at = datetime.now()
        dataset.schema.updated_at = datetime.now()
        self._save_dataset_metadata(dataset)

        self.logger.info(f"Added feature {name} to dataset {dataset_id}")

    def extract_data(self, dataset_id: str) -> pd.DataFrame:
        """Extract data from configured sources."""
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset {dataset_id} not found")

        dataset = self.datasets[dataset_id]
        all_data = []

        for source in dataset.data_sources:
            try:
                data = self._extract_from_source(source)
                if data is not None and not data.empty:
                    all_data.append(data)
                    self.logger.info(
                        f"Extracted {len(data)} rows from source {source.source_id}"
                    )
            except Exception as e:
                self.logger.error(
                    f"Failed to extract from source {source.source_id}: {e}"
                )

        if not all_data:
            return pd.DataFrame()

        # Combine all data sources
        combined_data = pd.concat(all_data, ignore_index=True)

        # Save raw data
        raw_file = self.storage_path / "raw" / f"{dataset_id}_raw.parquet"
        combined_data.to_parquet(raw_file, index=False)

        return combined_data

    def _extract_from_source(self, source: DataSource) -> pd.DataFrame | None:
        """Extract data from a specific source."""
        try:
            if source.source_type == "database":
                return self._extract_from_database(source)
            elif source.source_type == "file":
                return self._extract_from_file(source)
            elif source.source_type == "historian":
                return self._extract_from_historian(source)
            elif source.source_type == "opc":
                return self._extract_from_opc(source)
            else:
                self.logger.warning(f"Unsupported source type: {source.source_type}")
                return None
        except Exception as e:
            self.logger.error(f"Error extracting from {source.source_type}: {e}")
            return None

    def _extract_from_database(self, source: DataSource) -> pd.DataFrame | None:
        """Extract data from database source."""
        from .database_connections import DatabaseConnectionManager

        try:
            manager = DatabaseConnectionManager()
            config_name = source.connection_config.get("config_name")
            query = (
                source.query_config.get("query")
                if source.query_config
                else "SELECT * FROM data LIMIT 1000"
            )

            with manager.get_connection(config_name) as conn_id:
                results = manager.execute_query(conn_id, query)
                if results:
                    return pd.DataFrame(results)
                return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Database extraction failed: {e}")
            return None

    def _extract_from_file(self, source: DataSource) -> pd.DataFrame | None:
        """Extract data from file source."""
        file_path = source.connection_config.get("file_path")
        file_type = source.connection_config.get("file_type", "csv")

        try:
            if file_type.lower() == "csv":
                return pd.read_csv(file_path)
            elif file_type.lower() == "parquet":
                return pd.read_parquet(file_path)
            elif file_type.lower() == "json":
                return pd.read_json(file_path)
            elif file_type.lower() in ["xlsx", "xls"]:
                return pd.read_excel(file_path)
            else:
                self.logger.warning(f"Unsupported file type: {file_type}")
                return None
        except Exception as e:
            self.logger.error(f"File extraction failed: {e}")
            return None

    def _extract_from_historian(self, source: DataSource) -> pd.DataFrame | None:
        """Extract data from historian source."""
        from .historian_queries import HistorianQueryGenerator, HistorianType

        try:
            historian_type = HistorianType(
                source.connection_config.get("historian_type", "influxdb")
            )
            generator = HistorianQueryGenerator(historian_type)

            # Generate sample data for now
            # In production, this would execute actual historian queries
            data = {
                "timestamp": pd.date_range(start="2024-01-01", periods=1000, freq="1H"),
                "tag_name": ["Temperature"] * 1000,
                "value": np.random.normal(75, 10, 1000),
                "quality": ["GOOD"] * 1000,
            }
            return pd.DataFrame(data)
        except Exception as e:
            self.logger.error(f"Historian extraction failed: {e}")
            return None

    def _extract_from_opc(self, source: DataSource) -> pd.DataFrame | None:
        """Extract data from OPC source."""
        from .opc_tag_manager import OPCTagManager

        try:
            manager = OPCTagManager()
            tag_paths = (
                source.query_config.get("tag_paths", []) if source.query_config else []
            )

            # Generate sample data for now
            # In production, this would read actual OPC tags
            data = {
                "timestamp": [datetime.now()] * len(tag_paths),
                "tag_path": tag_paths,
                "value": np.random.random(len(tag_paths)),
                "quality": ["GOOD"] * len(tag_paths),
            }
            return pd.DataFrame(data)
        except Exception as e:
            self.logger.error(f"OPC extraction failed: {e}")
            return None

    def process_dataset(self, dataset_id: str) -> pd.DataFrame:
        """Process dataset according to schema definitions."""
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset {dataset_id} not found")

        dataset = self.datasets[dataset_id]

        # Extract raw data
        raw_data = self.extract_data(dataset_id)
        if raw_data.empty:
            raise ValueError("No data extracted from sources")

        # Apply feature transformations
        processed_data = self._apply_feature_transformations(raw_data, dataset.schema)

        # Update dataset statistics
        dataset.row_count = len(processed_data)
        dataset.column_count = len(processed_data.columns)
        dataset.file_size_mb = processed_data.memory_usage(deep=True).sum() / (
            1024 * 1024
        )
        dataset.status = ProcessingStatus.IN_PROGRESS
        dataset.updated_at = datetime.now()

        # Save processed data
        processed_file = (
            self.storage_path / "processed" / f"{dataset_id}_processed.parquet"
        )
        processed_data.to_parquet(processed_file, index=False)

        # Generate quality report
        quality_report = self._generate_quality_report(dataset_id, processed_data)
        dataset.quality_report = quality_report

        # Update status based on quality
        if quality_report.overall_quality in [DataQuality.EXCELLENT, DataQuality.GOOD]:
            dataset.status = ProcessingStatus.VALIDATED

        self._save_dataset_metadata(dataset)

        self.logger.info(
            f"Processed dataset {dataset_id}: {dataset.row_count} rows, {dataset.column_count} columns"
        )
        return processed_data

    def _apply_feature_transformations(
        self, data: pd.DataFrame, schema: DatasetSchema
    ) -> pd.DataFrame:
        """Apply feature transformations according to schema."""
        processed_data = data.copy()

        for feature in schema.features:
            if feature.source_column not in processed_data.columns:
                self.logger.warning(
                    f"Source column {feature.source_column} not found in data"
                )
                continue

            # Handle missing values
            if feature.missing_value_strategy == "drop":
                processed_data = processed_data.dropna(subset=[feature.source_column])
            elif feature.missing_value_strategy == "fill_mean":
                processed_data[feature.source_column].fillna(
                    processed_data[feature.source_column].mean(), inplace=True
                )
            elif feature.missing_value_strategy == "fill_median":
                processed_data[feature.source_column].fillna(
                    processed_data[feature.source_column].median(), inplace=True
                )
            elif feature.missing_value_strategy == "fill_mode":
                processed_data[feature.source_column].fillna(
                    processed_data[feature.source_column].mode()[0], inplace=True
                )
            elif (
                feature.missing_value_strategy == "custom"
                and feature.custom_fill_value is not None
            ):
                processed_data[feature.source_column].fillna(
                    feature.custom_fill_value, inplace=True
                )

            # Apply transformations
            if feature.transformation:
                processed_data = self._apply_transformation(processed_data, feature)

            # Rename column if needed
            if feature.name != feature.source_column:
                processed_data.rename(
                    columns={feature.source_column: feature.name}, inplace=True
                )

        return processed_data

    def _apply_transformation(
        self, data: pd.DataFrame, feature: FeatureDefinition
    ) -> pd.DataFrame:
        """Apply specific transformation to a feature."""
        column = feature.source_column

        if feature.transformation == "standard_scaling":
            from sklearn.preprocessing import StandardScaler

            scaler = StandardScaler()
            data[column] = scaler.fit_transform(data[[column]])
        elif feature.transformation == "min_max_scaling":
            from sklearn.preprocessing import MinMaxScaler

            scaler = MinMaxScaler()
            data[column] = scaler.fit_transform(data[[column]])
        elif feature.transformation == "log_transform":
            data[column] = np.log1p(data[column])
        elif feature.transformation == "one_hot_encoding":
            encoded = pd.get_dummies(data[column], prefix=feature.name)
            data = pd.concat([data, encoded], axis=1)
            data.drop(column, axis=1, inplace=True)

        return data

    def _generate_quality_report(
        self, dataset_id: str, data: pd.DataFrame
    ) -> DataQualityReport:
        """Generate data quality assessment report."""
        report_id = str(uuid.uuid4())

        # Calculate quality scores
        completeness = (
            1 - data.isnull().sum().sum() / (len(data) * len(data.columns))
        ) * 100
        consistency = self._calculate_consistency_score(data)
        accuracy = self._calculate_accuracy_score(data)
        uniqueness = self._calculate_uniqueness_score(data)
        timeliness = 100.0  # Assume fresh data for now

        # Overall quality assessment
        avg_score = (
            completeness + consistency + accuracy + uniqueness + timeliness
        ) / 5
        if avg_score >= 90:
            overall_quality = DataQuality.EXCELLENT
        elif avg_score >= 80:
            overall_quality = DataQuality.GOOD
        elif avg_score >= 70:
            overall_quality = DataQuality.FAIR
        elif avg_score >= 60:
            overall_quality = DataQuality.POOR
        else:
            overall_quality = DataQuality.CRITICAL

        # Generate issues and recommendations
        issues = []
        recommendations = []

        if completeness < 95:
            issues.append(
                {
                    "type": "completeness",
                    "severity": "medium",
                    "description": f"Data completeness is {completeness:.1f}%",
                }
            )
            recommendations.append("Consider imputation strategies for missing values")

        if consistency < 90:
            issues.append(
                {
                    "type": "consistency",
                    "severity": "medium",
                    "description": f"Data consistency is {consistency:.1f}%",
                }
            )
            recommendations.append("Review data validation rules and source quality")

        return DataQualityReport(
            report_id=report_id,
            dataset_id=dataset_id,
            overall_quality=overall_quality,
            completeness_score=completeness,
            consistency_score=consistency,
            accuracy_score=accuracy,
            uniqueness_score=uniqueness,
            timeliness_score=timeliness,
            issues=issues,
            recommendations=recommendations,
        )

    def _calculate_consistency_score(self, data: pd.DataFrame) -> float:
        """Calculate data consistency score."""
        # Simple consistency check - could be enhanced
        total_checks = 0
        passed_checks = 0

        for column in data.columns:
            if data[column].dtype in ["int64", "float64"]:
                # Check for reasonable ranges (no extreme outliers)
                q1, q3 = data[column].quantile([0.25, 0.75])
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                outliers = (
                    (data[column] < lower_bound) | (data[column] > upper_bound)
                ).sum()
                consistency = 1 - (outliers / len(data))

                total_checks += 1
                passed_checks += consistency

        return (passed_checks / total_checks * 100) if total_checks > 0 else 100.0

    def _calculate_accuracy_score(self, data: pd.DataFrame) -> float:
        """Calculate data accuracy score."""
        # Simple accuracy assessment - could be enhanced with business rules
        total_score = 0
        column_count = 0

        for column in data.columns:
            if data[column].dtype == "object":
                # Check for valid string formats
                valid_strings = data[column].str.len() > 0
                accuracy = valid_strings.sum() / len(data) * 100
            elif data[column].dtype in ["int64", "float64"]:
                # Check for valid numeric ranges
                valid_numbers = ~(data[column].isinf() | data[column].isna())
                accuracy = valid_numbers.sum() / len(data) * 100
            else:
                accuracy = 100.0

            total_score += accuracy
            column_count += 1

        return total_score / column_count if column_count > 0 else 100.0

    def _calculate_uniqueness_score(self, data: pd.DataFrame) -> float:
        """Calculate data uniqueness score."""
        if len(data) == 0:
            return 100.0

        duplicate_rows = data.duplicated().sum()
        uniqueness = (1 - duplicate_rows / len(data)) * 100
        return uniqueness

    def export_dataset(
        self, dataset_id: str, format_type: str = "csv", include_metadata: bool = True
    ) -> str:
        """Export dataset in specified format."""
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset {dataset_id} not found")

        dataset = self.datasets[dataset_id]
        processed_file = (
            self.storage_path / "processed" / f"{dataset_id}_processed.parquet"
        )

        if not processed_file.exists():
            raise ValueError("Processed data not found. Run process_dataset() first.")

        data = pd.read_parquet(processed_file)

        # Export data
        export_path = self.storage_path / "exports" / f"{dataset.name}_{dataset_id[:8]}"
        export_path.mkdir(exist_ok=True)

        if format_type == "csv":
            data_file = export_path / f"{dataset.name}.csv"
            data.to_csv(data_file, index=False)
        elif format_type == "parquet":
            data_file = export_path / f"{dataset.name}.parquet"
            data.to_parquet(data_file, index=False)
        elif format_type == "json":
            data_file = export_path / f"{dataset.name}.json"
            data.to_json(data_file, orient="records", indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

        # Export metadata if requested
        if include_metadata:
            metadata_file = export_path / f"{dataset.name}_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(self._dataset_to_dict(dataset), f, indent=2, default=str)

        self.logger.info(f"Exported dataset {dataset_id} to {export_path}")
        return str(export_path)

    def list_datasets(self) -> list[dict[str, Any]]:
        """List all datasets with summary information."""
        datasets_info = []
        for dataset in self.datasets.values():
            info = {
                "dataset_id": dataset.dataset_id,
                "name": dataset.name,
                "type": dataset.schema.dataset_type.value,
                "status": dataset.status.value,
                "row_count": dataset.row_count,
                "column_count": dataset.column_count,
                "quality": (
                    dataset.quality_report.overall_quality.value
                    if dataset.quality_report
                    else "unknown"
                ),
                "created_at": dataset.created_at.isoformat(),
                "updated_at": dataset.updated_at.isoformat(),
                "tags": dataset.tags,
            }
            datasets_info.append(info)

        return datasets_info

    def get_dataset(self, dataset_id: str) -> Dataset | None:
        """Get dataset by ID."""
        return self.datasets.get(dataset_id)

    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset and its associated files."""
        if dataset_id not in self.datasets:
            return False

        dataset = self.datasets[dataset_id]

        # Delete files
        files_to_delete = [
            self.storage_path / "raw" / f"{dataset_id}_raw.parquet",
            self.storage_path / "processed" / f"{dataset_id}_processed.parquet",
            self.storage_path / "metadata" / f"{dataset_id}.json",
        ]

        for file_path in files_to_delete:
            if file_path.exists():
                file_path.unlink()

        # Remove from memory
        del self.datasets[dataset_id]

        self.logger.info(f"Deleted dataset {dataset_id}")
        return True

    def _save_dataset_metadata(self, dataset: Dataset) -> None:
        """Save dataset metadata to file."""
        metadata_file = self.storage_path / "metadata" / f"{dataset.dataset_id}.json"
        with open(metadata_file, "w") as f:
            json.dump(self._dataset_to_dict(dataset), f, indent=2, default=str)

    def _dataset_to_dict(self, dataset: Dataset) -> dict[str, Any]:
        """Convert dataset to dictionary for serialization."""
        return {
            "dataset_id": dataset.dataset_id,
            "name": dataset.name,
            "schema": asdict(dataset.schema),
            "data_sources": [asdict(source) for source in dataset.data_sources],
            "status": dataset.status.value,
            "quality_report": (
                asdict(dataset.quality_report) if dataset.quality_report else None
            ),
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "file_size_mb": dataset.file_size_mb,
            "created_at": dataset.created_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat(),
            "created_by": dataset.created_by,
            "tags": dataset.tags,
            "metadata": dataset.metadata,
            "export_formats": dataset.export_formats,
        }

    def _dict_to_dataset(self, data: dict[str, Any]) -> Dataset:
        """Convert dictionary to dataset object."""
        # Convert schema
        schema_data = data["schema"]
        schema_data["dataset_type"] = DatasetType(schema_data["dataset_type"])
        schema_data["created_at"] = datetime.fromisoformat(schema_data["created_at"])
        schema_data["updated_at"] = datetime.fromisoformat(schema_data["updated_at"])

        features = []
        for feature_data in schema_data["features"]:
            features.append(FeatureDefinition(**feature_data))
        schema_data["features"] = features

        schema = DatasetSchema(**schema_data)

        # Convert data sources
        data_sources = []
        for source_data in data["data_sources"]:
            if source_data.get("last_updated"):
                source_data["last_updated"] = datetime.fromisoformat(
                    source_data["last_updated"]
                )
            data_sources.append(DataSource(**source_data))

        # Convert quality report
        quality_report = None
        if data.get("quality_report"):
            qr_data = data["quality_report"]
            qr_data["overall_quality"] = DataQuality(qr_data["overall_quality"])
            qr_data["generated_at"] = datetime.fromisoformat(qr_data["generated_at"])
            quality_report = DataQualityReport(**qr_data)

        # Create dataset
        return Dataset(
            dataset_id=data["dataset_id"],
            name=data["name"],
            schema=schema,
            data_sources=data_sources,
            status=ProcessingStatus(data["status"]),
            quality_report=quality_report,
            row_count=data.get("row_count", 0),
            column_count=data.get("column_count", 0),
            file_size_mb=data.get("file_size_mb", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            created_by=data.get("created_by", "system"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            export_formats=data.get("export_formats", ["csv", "parquet", "json"]),
        )


# Example usage and testing functions
def create_sample_dataset() -> str:
    """Create a sample dataset for testing."""
    manager = DatasetManager()

    # Create dataset
    dataset = manager.create_dataset(
        name="Industrial_Process_Data",
        dataset_type=DatasetType.REGRESSION,
        description="Sample industrial process data for predictive modeling",
        tags=["industrial", "process", "temperature", "pressure"],
    )

    # Add data source
    manager.add_data_source(
        dataset.dataset_id,
        source_type="historian",
        connection_config={
            "historian_type": "influxdb",
            "host": "localhost",
            "port": 8086,
        },
        query_config={
            "tags": ["temperature", "pressure", "flow_rate"],
            "time_range": "24h",
        },
    )

    # Define features
    manager.define_feature(
        dataset.dataset_id,
        name="temperature",
        data_type="numeric",
        source_column="value",
        transformation="standard_scaling",
        description="Process temperature in Celsius",
    )

    manager.define_feature(
        dataset.dataset_id,
        name="pressure",
        data_type="numeric",
        source_column="value",
        transformation="min_max_scaling",
        description="Process pressure in PSI",
    )

    manager.define_feature(
        dataset.dataset_id,
        name="quality_score",
        data_type="numeric",
        source_column="quality",
        is_target=True,
        description="Product quality score (target variable)",
    )

    return dataset.dataset_id


if __name__ == "__main__":
    # Test the dataset manager
    dataset_id = create_sample_dataset()
    print(f"Created sample dataset: {dataset_id}")

    manager = DatasetManager()
    datasets = manager.list_datasets()
    print(f"Total datasets: {len(datasets)}")
    for ds in datasets:
        print(f"  - {ds['name']} ({ds['status']}) - {ds['row_count']} rows")
