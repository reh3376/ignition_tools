"""Dataset Manager Models

Extracted from large file for better maintainability.
This module contains related functionality that was grouped together.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ProcessingStatus(Enum):
    """Dataset processing status."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    VALIDATED = "validated"
    READY = "ready"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


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
