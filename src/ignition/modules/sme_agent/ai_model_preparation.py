"""AI Model Preparation for Industrial Dataset Curation

Following crawl_mcp.py methodology for enterprise-ready implementation:
- Environment validation first
- Input validation with Pydantic models
- Comprehensive error handling
- Modular testing approach
- Progressive complexity deployment
- Resource management and cleanup

This module provides AI model preparation capabilities for Phase 11.5:
- Feature engineering and dataset augmentation
- Model training data preparation
- Validation dataset creation
- Model performance evaluation
- Export capabilities for various ML frameworks
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Self

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validator

from .industrial_dataset_curation import IndustrialDatasetCurator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineeringConfig(BaseModel):
    """Configuration for feature engineering operations."""

    enable_derivatives: bool = Field(True, description="Enable derivative features")
    enable_integrals: bool = Field(True, description="Enable integral features")
    enable_moving_averages: bool = Field(
        True, description="Enable moving average features"
    )
    enable_cross_correlations: bool = Field(
        True, description="Enable cross-correlation features"
    )
    enable_frequency_features: bool = Field(
        False, description="Enable frequency domain features"
    )

    window_sizes: list[int] = Field(
        [5, 10, 30, 60], description="Window sizes for moving features"
    )
    derivative_orders: list[int] = Field(
        [1, 2], description="Derivative orders to compute"
    )
    correlation_lags: list[int] = Field(
        [1, 5, 10], description="Lag values for correlations"
    )

    @validator("window_sizes")
    def validate_window_sizes(cls, v) -> Any:
        if not all(w > 0 for w in v):
            raise ValueError("Window sizes must be positive")
        return v


class ModelPreparationConfig(BaseModel):
    """Configuration for model preparation operations."""

    train_split: float = Field(
        0.7, ge=0.1, le=0.9, description="Training data split ratio"
    )
    validation_split: float = Field(
        0.15, ge=0.05, le=0.4, description="Validation data split ratio"
    )
    test_split: float = Field(
        0.15, ge=0.05, le=0.4, description="Test data split ratio"
    )

    random_seed: int = Field(42, description="Random seed for reproducibility")
    normalize_features: bool = Field(True, description="Apply feature normalization")
    handle_missing_data: bool = Field(True, description="Handle missing data")

    target_variables: list[str] = Field(
        default_factory=list, description="Target variables for prediction"
    )
    feature_selection_method: str = Field(
        "correlation", description="Feature selection method"
    )

    @validator("train_split", "validation_split", "test_split")
    def validate_splits(cls, v, values) -> Any:
        # Check that splits sum to approximately 1.0
        if "train_split" in values and "validation_split" in values:
            total = values["train_split"] + values["validation_split"] + v
            if abs(total - 1.0) > 0.01:
                raise ValueError("Train, validation, and test splits must sum to 1.0")
        return v


class PreparedDataset(BaseModel):
    """Represents a prepared dataset for ML model training."""

    dataset_name: str = Field(..., description="Name of the dataset")
    features: list[str] = Field(..., description="List of feature column names")
    targets: list[str] = Field(..., description="List of target column names")

    train_samples: int = Field(..., description="Number of training samples")
    validation_samples: int = Field(..., description="Number of validation samples")
    test_samples: int = Field(..., description="Number of test samples")

    feature_stats: dict[str, dict[str, float]] = Field(
        ..., description="Feature statistics"
    )
    preparation_timestamp: datetime = Field(default_factory=datetime.now)

    quality_score: float = Field(
        ..., ge=0.0, le=1.0, description="Dataset quality score"
    )
    completeness_score: float = Field(
        ..., ge=0.0, le=1.0, description="Data completeness score"
    )


def validate_environment() -> dict[str, bool]:
    """Validate environment for AI model preparation following crawl_mcp.py methodology."""
    try:
        validation_results = {}

        # Check required Python packages
        try:
            import numpy
            import pandas
            import sklearn

            validation_results["numpy"] = True
            validation_results["pandas"] = True
            validation_results["scikit_learn"] = True
        except ImportError as e:
            logger.error(f"Missing required package: {e}")
            validation_results["numpy"] = False
            validation_results["pandas"] = False
            validation_results["scikit_learn"] = False

        # Check optional ML packages
        try:
            import tensorflow

            validation_results["tensorflow"] = True
        except ImportError:
            validation_results["tensorflow"] = False

        try:
            import torch

            validation_results["pytorch"] = True
        except ImportError:
            validation_results["pytorch"] = False

        # Check data directories
        data_dir = Path(os.getenv("DATA_DIRECTORY", "data"))
        models_dir = Path(os.getenv("MODELS_DIRECTORY", "models"))

        validation_results["data_directory"] = data_dir.exists()
        validation_results["models_directory"] = (
            models_dir.exists() or models_dir.parent.exists()
        )

        # Check memory availability (basic check)
        try:
            import psutil

            memory = psutil.virtual_memory()
            # Require at least 4GB available memory
            validation_results["memory_available"] = memory.available > 4 * 1024**3
        except ImportError:
            validation_results["memory_available"] = (
                True  # Assume sufficient if can't check
            )

        logger.info(
            f"Environment validation completed: {sum(validation_results.values())}/{len(validation_results)} checks passed"
        )
        return validation_results

    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return {"validation_error": False}


class AIModelPreparation:
    """AI Model Preparation for Industrial Datasets

    Following crawl_mcp.py methodology:
    - Environment validation first
    - Comprehensive error handling
    - Modular testing approach
    - Progressive complexity
    - Resource management
    """

    def __init__(
        self, curator: IndustrialDatasetCurator, complexity_level: str = "standard"
    ):
        """Initialize AI model preparation framework."""
        try:
            # Environment validation first (crawl_mcp.py pattern)
            self.env_validation = validate_environment()
            if not any(self.env_validation.values()):
                raise RuntimeError("Environment validation failed")

            self.curator = curator
            self.complexity_level = complexity_level
            self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

            # Initialize configurations
            self.feature_config = FeatureEngineeringConfig()
            self.model_config = ModelPreparationConfig()

            # Initialize storage
            self.prepared_datasets: dict[str, PreparedDataset] = {}
            self.feature_cache: dict[str, pd.DataFrame] = {}

            self.logger.info(
                f"AIModelPreparation initialized with complexity: {complexity_level}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize AIModelPreparation: {e}")
            raise

    def engineer_features(
        self, dataset_name: str, config: FeatureEngineeringConfig | None = None
    ) -> pd.DataFrame:
        """Engineer features from raw dataset following crawl_mcp.py error handling."""
        try:
            if config is None:
                config = self.feature_config

            # Input validation
            if not dataset_name:
                raise ValueError("Dataset name cannot be empty")

            # Get raw data from curator
            raw_data = self.curator.get_dataset(dataset_name)
            if raw_data is None or raw_data.empty:
                raise ValueError(f"Dataset '{dataset_name}' not found or empty")

            self.logger.info(f"Engineering features for dataset: {dataset_name}")

            # Start with original data
            engineered_data = raw_data.copy()

            # Generate derivative features
            if config.enable_derivatives:
                engineered_data = self._add_derivative_features(
                    engineered_data, config.derivative_orders
                )

            # Generate integral features
            if config.enable_integrals:
                engineered_data = self._add_integral_features(
                    engineered_data, config.window_sizes
                )

            # Generate moving averages
            if config.enable_moving_averages:
                engineered_data = self._add_moving_average_features(
                    engineered_data, config.window_sizes
                )

            # Generate cross-correlation features
            if config.enable_cross_correlations:
                engineered_data = self._add_cross_correlation_features(
                    engineered_data, config.correlation_lags
                )

            # Generate frequency domain features (advanced)
            if config.enable_frequency_features and self.complexity_level in [
                "advanced",
                "enterprise",
            ]:
                engineered_data = self._add_frequency_features(engineered_data)

            # Cache results
            self.feature_cache[dataset_name] = engineered_data

            self.logger.info(
                f"Feature engineering completed: {len(engineered_data.columns)} features generated"
            )
            return engineered_data

        except Exception as e:
            self.logger.error(f"Feature engineering failed for {dataset_name}: {e}")
            raise

    def _add_derivative_features(
        self, data: pd.DataFrame, orders: list[int]
    ) -> pd.DataFrame:
        """Add derivative features to dataset."""
        try:
            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for col in numeric_columns:
                for order in orders:
                    if order == 1:
                        data[f"{col}_derivative"] = data[col].diff()
                    elif order == 2:
                        data[f"{col}_derivative2"] = data[col].diff().diff()

            return data
        except Exception as e:
            self.logger.error(f"Failed to add derivative features: {e}")
            return data

    def _add_integral_features(
        self, data: pd.DataFrame, window_sizes: list[int]
    ) -> pd.DataFrame:
        """Add integral (cumulative sum) features to dataset."""
        try:
            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for col in numeric_columns:
                for window in window_sizes:
                    data[f"{col}_integral_{window}"] = (
                        data[col].rolling(window=window).sum()
                    )

            return data
        except Exception as e:
            self.logger.error(f"Failed to add integral features: {e}")
            return data

    def _add_moving_average_features(
        self, data: pd.DataFrame, window_sizes: list[int]
    ) -> pd.DataFrame:
        """Add moving average features to dataset."""
        try:
            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for col in numeric_columns:
                for window in window_sizes:
                    data[f"{col}_ma_{window}"] = data[col].rolling(window=window).mean()
                    data[f"{col}_std_{window}"] = data[col].rolling(window=window).std()

            return data
        except Exception as e:
            self.logger.error(f"Failed to add moving average features: {e}")
            return data

    def _add_cross_correlation_features(
        self, data: pd.DataFrame, lags: list[int]
    ) -> pd.DataFrame:
        """Add cross-correlation features between variables."""
        try:
            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for i, col1 in enumerate(numeric_columns):
                for j, col2 in enumerate(numeric_columns[i + 1 :], i + 1):
                    for lag in lags:
                        # Lagged correlation
                        corr_data = data[col1].corr(data[col2].shift(lag))
                        if not np.isnan(corr_data):
                            data[f"{col1}_{col2}_corr_lag_{lag}"] = corr_data

            return data
        except Exception as e:
            self.logger.error(f"Failed to add cross-correlation features: {e}")
            return data

    def _add_frequency_features(self: Self, data: pd.DataFrame) -> pd.DataFrame:
        """Add frequency domain features (FFT-based)."""
        try:
            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for col in numeric_columns:
                # Skip if too many NaN values
                if data[col].isna().sum() / len(data) > 0.5:
                    continue

                # Fill NaN values for FFT
                col_data = data[col].fillna(data[col].mean())

                # Compute FFT
                fft_values = np.fft.fft(col_data.values)
                frequencies = np.fft.fftfreq(len(col_data))

                # Extract key frequency features
                data[f"{col}_fft_mean"] = np.mean(np.abs(fft_values))
                data[f"{col}_fft_std"] = np.std(np.abs(fft_values))
                data[f"{col}_dominant_freq"] = frequencies[
                    np.argmax(np.abs(fft_values[1:])) + 1
                ]

            return data
        except Exception as e:
            self.logger.error(f"Failed to add frequency features: {e}")
            return data

    def prepare_training_data(
        self, dataset_name: str, config: ModelPreparationConfig | None = None
    ) -> PreparedDataset:
        """Prepare data for ML model training following crawl_mcp.py methodology."""
        try:
            if config is None:
                config = self.model_config

            # Input validation
            if not dataset_name:
                raise ValueError("Dataset name cannot be empty")

            self.logger.info(f"Preparing training data for: {dataset_name}")

            # Get engineered features
            if dataset_name in self.feature_cache:
                data = self.feature_cache[dataset_name].copy()
            else:
                data = self.engineer_features(dataset_name)

            # Handle missing data
            if config.handle_missing_data:
                data = self._handle_missing_data(data)

            # Feature selection
            if config.target_variables:
                features, targets = self._select_features(
                    data, config.target_variables, config.feature_selection_method
                )
            else:
                # Auto-select targets based on variable types
                targets = self._auto_select_targets(data)
                features = [col for col in data.columns if col not in targets]

            # Split data
            train_data, val_data, test_data = self._split_data(data, config)

            # Normalize features if requested
            if config.normalize_features:
                train_data, val_data, test_data = self._normalize_features(
                    train_data, val_data, test_data, features
                )

            # Calculate quality metrics
            quality_score = self._calculate_quality_score(data)
            completeness_score = self._calculate_completeness_score(data)

            # Calculate feature statistics
            feature_stats = self._calculate_feature_statistics(train_data, features)

            # Create prepared dataset object
            prepared_dataset = PreparedDataset(
                dataset_name=dataset_name,
                features=features,
                targets=targets,
                train_samples=len(train_data),
                validation_samples=len(val_data),
                test_samples=len(test_data),
                feature_stats=feature_stats,
                quality_score=quality_score,
                completeness_score=completeness_score,
            )

            # Store prepared dataset
            self.prepared_datasets[dataset_name] = prepared_dataset

            self.logger.info(
                f"Training data preparation completed: {len(features)} features, {len(targets)} targets"
            )
            return prepared_dataset

        except Exception as e:
            self.logger.error(
                f"Failed to prepare training data for {dataset_name}: {e}"
            )
            raise

    def _handle_missing_data(self: Self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing data with appropriate strategies."""
        try:
            # Forward fill for time series data
            data = data.fillna(method="ffill")

            # Backward fill for remaining NaN values
            data = data.fillna(method="bfill")

            # Fill remaining with column means for numeric data
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if data[col].isna().any():
                    data[col] = data[col].fillna(data[col].mean())

            return data
        except Exception as e:
            self.logger.error(f"Failed to handle missing data: {e}")
            return data

    def _select_features(
        self, data: pd.DataFrame, targets: list[str], method: str
    ) -> tuple[list[str], list[str]]:
        """Select features based on correlation or other methods."""
        try:
            all_features = [col for col in data.columns if col not in targets]

            if method == "correlation":
                # Select features with high correlation to targets
                selected_features = []
                for target in targets:
                    if target in data.columns:
                        correlations = data[all_features].corrwith(data[target]).abs()
                        # Select features with correlation > 0.1
                        high_corr_features = correlations[
                            correlations > 0.1
                        ].index.tolist()
                        selected_features.extend(high_corr_features)

                # Remove duplicates
                selected_features = list(set(selected_features))
                return selected_features, targets

            # Default: return all features
            return all_features, targets

        except Exception as e:
            self.logger.error(f"Feature selection failed: {e}")
            return list(data.columns), []

    def _auto_select_targets(self: Self, data: pd.DataFrame) -> list[str]:
        """Auto-select target variables based on variable types."""
        try:
            # Look for PV (Process Variables) as common targets
            pv_columns = [
                col
                for col in data.columns
                if any(
                    keyword in col.lower()
                    for keyword in ["pv", "process", "measurement", "sensor"]
                )
            ]

            if pv_columns:
                return pv_columns[:3]  # Limit to 3 targets

            # Fallback: select numeric columns with good variance
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            high_variance_columns = []

            for col in numeric_columns:
                if data[col].var() > data[col].mean() * 0.1:  # High relative variance
                    high_variance_columns.append(col)

            return high_variance_columns[:3]  # Limit to 3 targets

        except Exception as e:
            self.logger.error(f"Auto target selection failed: {e}")
            return []

    def _split_data(
        self, data: pd.DataFrame, config: ModelPreparationConfig
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split data into train/validation/test sets."""
        try:
            # Set random seed for reproducibility
            np.random.seed(config.random_seed)

            # Shuffle data
            shuffled_data = data.sample(
                frac=1.0, random_state=config.random_seed
            ).reset_index(drop=True)

            # Calculate split indices
            n_samples = len(shuffled_data)
            train_end = int(n_samples * config.train_split)
            val_end = int(n_samples * (config.train_split + config.validation_split))

            # Split data
            train_data = shuffled_data[:train_end]
            val_data = shuffled_data[train_end:val_end]
            test_data = shuffled_data[val_end:]

            return train_data, val_data, test_data

        except Exception as e:
            self.logger.error(f"Data splitting failed: {e}")
            # Return original data as train set if splitting fails
            return data, pd.DataFrame(), pd.DataFrame()

    def _normalize_features(
        self,
        train_data: pd.DataFrame,
        val_data: pd.DataFrame,
        test_data: pd.DataFrame,
        features: list[str],
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Normalize features using training data statistics."""
        try:
            # Calculate normalization parameters from training data only
            feature_means = train_data[features].mean()
            feature_stds = train_data[features].std()

            # Apply normalization
            train_normalized = train_data.copy()
            train_normalized[features] = (
                train_data[features] - feature_means
            ) / feature_stds

            val_normalized = val_data.copy()
            if not val_data.empty:
                val_normalized[features] = (
                    val_data[features] - feature_means
                ) / feature_stds

            test_normalized = test_data.copy()
            if not test_data.empty:
                test_normalized[features] = (
                    test_data[features] - feature_means
                ) / feature_stds

            return train_normalized, val_normalized, test_normalized

        except Exception as e:
            self.logger.error(f"Feature normalization failed: {e}")
            return train_data, val_data, test_data

    def _calculate_quality_score(self: Self, data: pd.DataFrame) -> float:
        """Calculate overall data quality score."""
        try:
            # Factors: completeness, consistency, validity
            completeness = 1.0 - (
                data.isna().sum().sum() / (len(data) * len(data.columns))
            )

            # Consistency: check for outliers (simplified)
            numeric_data = data.select_dtypes(include=[np.number])
            outlier_ratio = 0.0

            for col in numeric_data.columns:
                Q1 = numeric_data[col].quantile(0.25)
                Q3 = numeric_data[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = (
                    (numeric_data[col] < (Q1 - 1.5 * IQR))
                    | (numeric_data[col] > (Q3 + 1.5 * IQR))
                ).sum()
                outlier_ratio += outliers / len(numeric_data)

            consistency = max(0.0, 1.0 - (outlier_ratio / len(numeric_data.columns)))

            # Validity: assume 1.0 for now (would require domain-specific rules)
            validity = 1.0

            # Weighted average
            quality_score = 0.4 * completeness + 0.4 * consistency + 0.2 * validity
            return min(1.0, max(0.0, quality_score))

        except Exception as e:
            self.logger.error(f"Quality score calculation failed: {e}")
            return 0.5  # Default moderate quality

    def _calculate_completeness_score(self: Self, data: pd.DataFrame) -> float:
        """Calculate data completeness score."""
        try:
            total_cells = len(data) * len(data.columns)
            missing_cells = data.isna().sum().sum()
            completeness = 1.0 - (missing_cells / total_cells)
            return max(0.0, min(1.0, completeness))
        except Exception as e:
            self.logger.error(f"Completeness score calculation failed: {e}")
            return 0.5

    def _calculate_feature_statistics(
        self, data: pd.DataFrame, features: list[str]
    ) -> dict[str, dict[str, float]]:
        """Calculate statistics for each feature."""
        try:
            stats = {}
            for feature in features:
                if feature in data.columns:
                    feature_data = data[feature]
                    stats[feature] = {
                        "mean": (
                            float(feature_data.mean())
                            if feature_data.dtype in ["int64", "float64"]
                            else 0.0
                        ),
                        "std": (
                            float(feature_data.std())
                            if feature_data.dtype in ["int64", "float64"]
                            else 0.0
                        ),
                        "min": (
                            float(feature_data.min())
                            if feature_data.dtype in ["int64", "float64"]
                            else 0.0
                        ),
                        "max": (
                            float(feature_data.max())
                            if feature_data.dtype in ["int64", "float64"]
                            else 0.0
                        ),
                        "missing_ratio": float(
                            feature_data.isna().sum() / len(feature_data)
                        ),
                    }
            return stats
        except Exception as e:
            self.logger.error(f"Feature statistics calculation failed: {e}")
            return {}

    def export_dataset(
        self, dataset_name: str, format: str = "pandas", output_path: str | None = None
    ) -> Any:
        """Export prepared dataset in various formats."""
        try:
            if dataset_name not in self.prepared_datasets:
                raise ValueError(f"Dataset '{dataset_name}' not prepared")

            prepared_dataset = self.prepared_datasets[dataset_name]

            if format == "pandas":
                # Return cached feature data
                return self.feature_cache.get(dataset_name)

            elif format == "numpy":
                data = self.feature_cache.get(dataset_name)
                if data is not None:
                    return data.values

            elif format == "csv" and output_path:
                data = self.feature_cache.get(dataset_name)
                if data is not None:
                    data.to_csv(output_path, index=False)
                    self.logger.info(f"Dataset exported to CSV: {output_path}")
                    return output_path

            elif format == "json":
                return prepared_dataset.dict()

            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            self.logger.error(f"Dataset export failed: {e}")
            raise

    def get_preparation_status(self: Self) -> dict[str, Any]:
        """Get status of model preparation system."""
        try:
            return {
                "complexity_level": self.complexity_level,
                "environment_validation": self.env_validation,
                "prepared_datasets": len(self.prepared_datasets),
                "cached_features": len(self.feature_cache),
                "feature_config": self.feature_config.dict(),
                "model_config": self.model_config.dict(),
            }
        except Exception as e:
            self.logger.error(f"Failed to get preparation status: {e}")
            return {"error": str(e)}


# Async wrapper for compatibility
async def prepare_model_data_async(
    curator: IndustrialDatasetCurator,
    dataset_name: str,
    complexity_level: str = "standard",
) -> PreparedDataset:
    """Async wrapper for model data preparation."""
    try:
        model_prep = AIModelPreparation(curator, complexity_level)
        return model_prep.prepare_training_data(dataset_name)
    except Exception as e:
        logger.error(f"Async model preparation failed: {e}")
        raise
