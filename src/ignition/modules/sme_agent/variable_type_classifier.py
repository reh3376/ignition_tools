"""
Variable Type Classification & Metadata System

Following the crawl_mcp.py methodology for structured development:
- Comprehensive validation and error handling
- Environment variable configuration
- Modular testing and progressive complexity
- Resource management and cleanup
- User-friendly error messages

This module implements:
- Process Variable (PV) Management (Primary and Secondary)
- Control Variable (CV) Management
- Disturbance Variable (DV) Management
- Setpoint (SP) & Process State Management
- Automated variable classification using pattern matching
- Range validation and normalization capabilities
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from .industrial_dataset_curation import (
    DataSourceType,
    IndustrialDatasetCurator,
    VariableMetadata,
    VariableType,
    format_validation_error,
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


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
        self.classification_stats: Dict[str, Any] = {}
        self._load_default_classification_rules()

    def _load_default_classification_rules(self) -> None:
        """Load default variable classification rules."""
        self.classification_rules = {
            "primary_pv_patterns": [
                r".*temp.*", r".*temperature.*", r".*press.*", r".*pressure.*",
                r".*flow.*", r".*level.*", r".*ph.*", r".*density.*",
                r".*concentration.*", r".*conductivity.*", r".*viscosity.*"
            ],
            "secondary_pv_patterns": [
                r".*spc.*", r".*secondary.*", r".*aux.*", r".*auxiliary.*",
                r".*calc.*", r".*calculated.*", r".*derived.*"
            ],
            "control_variable_patterns": [
                r".*valve.*", r".*output.*", r".*cv.*", r".*actuator.*",
                r".*speed.*", r".*position.*", r".*signal.*", r".*command.*",
                r".*demand.*", r".*drive.*"
            ],
            "setpoint_patterns": [
                r".*sp.*", r".*setpoint.*", r".*target.*", r".*set.*",
                r".*reference.*", r".*desired.*"
            ],
            "disturbance_patterns": [
                r".*ambient.*", r".*feed.*", r".*load.*", r".*disturbance.*",
                r".*external.*", r".*weather.*", r".*inlet.*", r".*supply.*"
            ],
            "process_state_patterns": [
                r".*state.*", r".*mode.*", r".*status.*", r".*phase.*",
                r".*operation.*", r".*running.*", r".*stopped.*"
            ]
        }

    def classify_variables_from_dataset(
        self,
        dataset_name: str,
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Automatically classify variables from a dataset.

        Args:
            dataset_name: Name of dataset to classify
            confidence_threshold: Minimum confidence for automatic classification

        Returns:
            Dict with classification results
        """
        try:
            # Validate dataset exists
            if dataset_name not in self.curator.datasets:
                return {
                    "success": False,
                    "error": f"Dataset '{dataset_name}' not found",
                    "classified_variables": 0
                }

            df = self.curator.datasets[dataset_name]
            classification_results = {}

            # Classify each column
            for column in df.columns:
                classification = self._classify_single_variable(
                    column, df[column], confidence_threshold
                )
                classification_results[column] = classification

                # Auto-add high-confidence classifications
                if classification["confidence"] >= confidence_threshold:
                    metadata = VariableMetadata(
                        name=column,
                        variable_type=classification["variable_type"],
                        engineering_units=classification.get("suggested_units", "unknown"),
                        description=f"Auto-classified as {classification['variable_type'].value}",
                        data_source=DataSourceType.CSV_XLS,
                        high_limit=classification.get("suggested_high_limit"),
                        low_limit=classification.get("suggested_low_limit"),
                        normalization_factor=classification.get("normalization_factor")
                    )

                    self.curator.add_variable(metadata)

            # Update classification statistics
            self.classification_stats[dataset_name] = {
                "total_variables": len(df.columns),
                "classified_variables": len([
                    c for c in classification_results.values()
                    if c["confidence"] >= confidence_threshold
                ]),
                "classification_results": classification_results,
                "confidence_threshold": confidence_threshold,
                "timestamp": pd.Timestamp.now().isoformat()
            }

            classified_count = self.classification_stats[dataset_name]["classified_variables"]

            logger.info(
                f"Classified {classified_count}/{len(df.columns)} variables "
                f"from dataset '{dataset_name}'"
            )

            return {
                "success": True,
                "dataset_name": dataset_name,
                "total_variables": len(df.columns),
                "classified_variables": classified_count,
                "classification_results": classification_results,
                "confidence_threshold": confidence_threshold
            }

        except Exception as e:
            error_msg = format_validation_error(e, "Variable classification")
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "classified_variables": 0
            }

    def _classify_single_variable(
        self,
        variable_name: str,
        data_series: pd.Series,
        confidence_threshold: float
    ) -> Dict[str, Any]:
        """
        Classify a single variable using pattern matching and data analysis.

        Args:
            variable_name: Name of the variable
            data_series: Data series for the variable
            confidence_threshold: Minimum confidence threshold

        Returns:
            Dict with classification results
        """
        try:
            # Initialize classification result
            result = {
                "variable_name": variable_name,
                "variable_type": VariableType.PRIMARY_PV,  # Default
                "confidence": 0.0,
                "classification_reasons": [],
                "data_analysis": {}
            }

            # Pattern-based classification
            pattern_scores = self._calculate_pattern_scores(variable_name)

            # Data-based classification
            data_analysis = self._analyze_variable_data(data_series)
            result["data_analysis"] = data_analysis

            # Combine pattern and data analysis for final classification
            final_classification = self._combine_classification_methods(
                pattern_scores, data_analysis, variable_name
            )

            result.update(final_classification)

            # Add engineering unit suggestions
            if result["confidence"] >= confidence_threshold:
                result.update(self._suggest_engineering_metadata(
                    result["variable_type"], data_analysis
                ))

            return result

        except Exception as e:
            logger.error(f"Error classifying variable {variable_name}: {e}")
            return {
                "variable_name": variable_name,
                "variable_type": VariableType.PRIMARY_PV,
                "confidence": 0.0,
                "error": str(e),
                "classification_reasons": ["Classification failed"],
                "data_analysis": {}
            }

    def _calculate_pattern_scores(self, variable_name: str) -> Dict[str, float]:
        """Calculate pattern matching scores for variable name."""
        scores = {}
        variable_name_lower = variable_name.lower()

        for var_type, patterns in self.classification_rules.items():
            max_score = 0.0

            for pattern in patterns:
                if re.search(pattern, variable_name_lower):
                    # Calculate score based on pattern specificity
                    pattern_length = len(pattern.replace(".*", ""))
                    match_quality = min(pattern_length / len(variable_name_lower), 1.0)
                    score = 0.8 + (match_quality * 0.2)  # Base score + quality bonus
                    max_score = max(max_score, score)

            scores[var_type] = max_score

        return scores

    def _analyze_variable_data(self, data_series: pd.Series) -> Dict[str, Any]:
        """Analyze variable data characteristics."""
        try:
            analysis = {
                "data_type": str(data_series.dtype),
                "total_points": len(data_series),
                "missing_points": data_series.isnull().sum(),
                "missing_percentage": (data_series.isnull().sum() / len(data_series) * 100)
            }

            # Numeric data analysis
            if pd.api.types.is_numeric_dtype(data_series):
                numeric_data = data_series.dropna()
                if len(numeric_data) > 0:
                    analysis.update({
                        "is_numeric": True,
                        "min_value": float(numeric_data.min()),
                        "max_value": float(numeric_data.max()),
                        "mean_value": float(numeric_data.mean()),
                        "std_value": float(numeric_data.std()),
                        "range": float(numeric_data.max() - numeric_data.min()),
                        "unique_values": len(numeric_data.unique()),
                        "zero_values": (numeric_data == 0).sum(),
                        "negative_values": (numeric_data < 0).sum()
                    })

                    # Detect if likely boolean/state variable
                    unique_vals = numeric_data.unique()
                    if len(unique_vals) <= 10 and all(val in [0, 1] or val % 1 == 0 for val in unique_vals):
                        analysis["likely_state_variable"] = True
                    else:
                        analysis["likely_state_variable"] = False

                    # Detect if likely percentage (0-100 range)
                    if 0 <= analysis["min_value"] <= 100 and 0 <= analysis["max_value"] <= 100:
                        analysis["likely_percentage"] = True
                    else:
                        analysis["likely_percentage"] = False

                else:
                    analysis["is_numeric"] = False
            else:
                analysis["is_numeric"] = False
                # Categorical data analysis
                analysis.update({
                    "unique_values": len(data_series.dropna().unique()),
                    "most_common": data_series.value_counts().head(5).to_dict()
                })

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing variable data: {e}")
            return {"error": str(e), "is_numeric": False}

    def _combine_classification_methods(
        self,
        pattern_scores: Dict[str, float],
        data_analysis: Dict[str, Any],
        variable_name: str
    ) -> Dict[str, Any]:
        """Combine pattern matching and data analysis for final classification."""

        # Find highest pattern score
        best_pattern_type = max(pattern_scores.keys(), key=lambda k: pattern_scores[k])
        best_pattern_score = pattern_scores[best_pattern_type]

        # Adjust scores based on data analysis
        adjusted_scores = pattern_scores.copy()
        reasons = []

        if data_analysis.get("is_numeric", False):
            # Boost control variable score if range suggests actuator output
            if (data_analysis.get("min_value", 0) >= 0 and
                data_analysis.get("max_value", 100) <= 100 and
                not data_analysis.get("likely_state_variable", False)):
                adjusted_scores["control_variable_patterns"] += 0.2
                reasons.append("Numeric range suggests control output")

            # Boost state variable score for discrete values
            if data_analysis.get("likely_state_variable", False):
                adjusted_scores["process_state_patterns"] += 0.3
                reasons.append("Discrete values suggest state variable")

            # Boost setpoint score for stable values
            if data_analysis.get("std_value", float('inf')) < 0.1 * data_analysis.get("mean_value", 1):
                adjusted_scores["setpoint_patterns"] += 0.1
                reasons.append("Low variability suggests setpoint")

        else:
            # Non-numeric data likely to be state variables
            adjusted_scores["process_state_patterns"] += 0.4
            reasons.append("Non-numeric data suggests state variable")

        # Determine final classification
        final_type = max(adjusted_scores.keys(), key=lambda k: adjusted_scores[k])
        final_score = adjusted_scores[final_type]

        # Map pattern type to VariableType enum
        type_mapping = {
            "primary_pv_patterns": VariableType.PRIMARY_PV,
            "secondary_pv_patterns": VariableType.SECONDARY_PV,
            "control_variable_patterns": VariableType.CONTROL_VARIABLE,
            "setpoint_patterns": VariableType.SETPOINT,
            "disturbance_patterns": VariableType.DISTURBANCE_VARIABLE,
            "process_state_patterns": VariableType.PROCESS_STATE
        }

        variable_type = type_mapping.get(final_type, VariableType.PRIMARY_PV)

        # Add pattern-specific reasons
        if best_pattern_score > 0:
            reasons.append(f"Pattern match for {variable_type.value}")

        return {
            "variable_type": variable_type,
            "confidence": min(final_score, 1.0),
            "classification_reasons": reasons,
            "pattern_scores": pattern_scores,
            "adjusted_scores": adjusted_scores
        }

    def _suggest_engineering_metadata(
        self,
        variable_type: VariableType,
        data_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Suggest engineering units and limits based on variable type and data."""
        suggestions = {}

        if not data_analysis.get("is_numeric", False):
            return suggestions

        min_val = data_analysis.get("min_value", 0)
        max_val = data_analysis.get("max_value", 100)
        mean_val = data_analysis.get("mean_value", 50)

        # Suggest engineering units based on variable type and data range
        if variable_type == VariableType.PRIMARY_PV:
            if 0 <= min_val <= 100 and 0 <= max_val <= 100:
                suggestions["suggested_units"] = "%"
            elif min_val >= 0 and max_val <= 1000:
                suggestions["suggested_units"] = "units"
            else:
                suggestions["suggested_units"] = "engineering_units"

        elif variable_type == VariableType.CONTROL_VARIABLE:
            if 0 <= min_val <= 100 and 0 <= max_val <= 100:
                suggestions["suggested_units"] = "%"
            else:
                suggestions["suggested_units"] = "output_units"

        elif variable_type == VariableType.SETPOINT:
            suggestions["suggested_units"] = "setpoint_units"

        elif variable_type == VariableType.DISTURBANCE_VARIABLE:
            suggestions["suggested_units"] = "disturbance_units"

        elif variable_type == VariableType.PROCESS_STATE:
            suggestions["suggested_units"] = "state"

        # Suggest operational limits (with safety margins)
        if variable_type != VariableType.PROCESS_STATE:
            range_val = max_val - min_val
            safety_margin = range_val * 0.1  # 10% safety margin

            suggestions["suggested_low_limit"] = min_val - safety_margin
            suggestions["suggested_high_limit"] = max_val + safety_margin

            # Suggest normalization factor for percentage-like variables
            if max_val > 0:
                suggestions["normalization_factor"] = max_val

        return suggestions

    def validate_variable_classification(
        self,
        variable_name: str,
        proposed_type: VariableType
    ) -> Dict[str, Any]:
        """
        Validate a proposed variable classification.

        Args:
            variable_name: Name of variable to validate
            proposed_type: Proposed variable type

        Returns:
            Dict with validation results
        """
        try:
            # Check if variable exists in any dataset
            variable_found = False
            data_series = None

            for dataset_name, df in self.curator.datasets.items():
                if variable_name in df.columns:
                    variable_found = True
                    data_series = df[variable_name]
                    break

            if not variable_found:
                return {
                    "valid": False,
                    "error": f"Variable '{variable_name}' not found in any dataset",
                    "confidence": 0.0
                }

            # Perform classification analysis
            if data_series is not None:
                current_classification = self._classify_single_variable(
                    variable_name, data_series, 0.0  # No threshold for validation
                )
            else:
                return {
                    "valid": False,
                    "error": f"Data series for variable '{variable_name}' is None",
                    "confidence": 0.0
                }

            # Compare with proposed type
            matches_auto_classification = (
                current_classification["variable_type"] == proposed_type
            )

            validation_result = {
                "valid": True,
                "variable_name": variable_name,
                "proposed_type": proposed_type.value,
                "auto_classified_type": current_classification["variable_type"].value,
                "matches_auto_classification": matches_auto_classification,
                "auto_classification_confidence": current_classification["confidence"],
                "validation_reasons": [],
                "data_analysis": current_classification["data_analysis"]
            }

            # Add validation reasons
            if matches_auto_classification:
                validation_result["validation_reasons"].append(
                    "Matches automatic classification"
                )
            else:
                validation_result["validation_reasons"].append(
                    f"Differs from automatic classification ({current_classification['variable_type'].value})"
                )

            # Additional validation based on data characteristics
            if data_analysis := current_classification.get("data_analysis", {}):
                if proposed_type == VariableType.PROCESS_STATE and not data_analysis.get("is_numeric", True):
                    validation_result["validation_reasons"].append(
                        "Non-numeric data appropriate for state variable"
                    )
                elif proposed_type == VariableType.CONTROL_VARIABLE and data_analysis.get("likely_percentage", False):
                    validation_result["validation_reasons"].append(
                        "Percentage range appropriate for control variable"
                    )

            return validation_result

        except Exception as e:
            error_msg = format_validation_error(e, "Variable validation")
            logger.error(error_msg)
            return {
                "valid": False,
                "error": error_msg,
                "confidence": 0.0
            }

    def get_classification_summary(self) -> Dict[str, Any]:
        """Get summary of all classification activities."""
        try:
            total_datasets = len(self.classification_stats)
            total_variables = sum(
                stats["total_variables"]
                for stats in self.classification_stats.values()
            )
            total_classified = sum(
                stats["classified_variables"]
                for stats in self.classification_stats.values()
            )

            # Variable type distribution
            type_distribution = {}
            for variable_name, metadata in self.curator.variables.items():
                var_type = metadata.variable_type.value
                type_distribution[var_type] = type_distribution.get(var_type, 0) + 1

            return {
                "total_datasets_processed": total_datasets,
                "total_variables_analyzed": total_variables,
                "total_variables_classified": total_classified,
                "classification_rate": (total_classified / total_variables * 100) if total_variables > 0 else 0,
                "variable_type_distribution": type_distribution,
                "dataset_statistics": self.classification_stats,
                "configured_variables": len(self.curator.variables),
                "timestamp": pd.Timestamp.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating classification summary: {e}")
            return {
                "error": str(e),
                "timestamp": pd.Timestamp.now().isoformat()
            }


# Initialize module logger
logger.info("Variable Type Classifier module loaded successfully")
