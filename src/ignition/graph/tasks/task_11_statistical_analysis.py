"""Task 11: Statistical Analysis Module.

Statistical analysis and distributions for Ignition SCADA systems.
Extracted from task_11_math_analytics.py for better modularity.

This module provides:
- Descriptive statistics calculations
- Regression analysis with multiple methods
- Anomaly detection algorithms
- Correlation analysis
- Hypothesis testing
- Distribution generation and analysis
- Time series analysis
- Statistical process control
- Survival analysis
- Cluster analysis

Total Functions: 10 functions
"""

from typing import Any


def get_statistical_analysis_functions() -> list[dict[str, Any]]:
    """Get statistical analysis functions for Task 11.

    Returns:
        list[dict[str, Any]]: list of statistical analysis function definitions
    """
    functions = []

    # Statistical Analysis Section
    functions.extend(
        [
            {
                "name": "system.statistics.calculateDescriptiveStats",
                "description": "Calculate comprehensive descriptive statistics",
                "parameters": [
                    {
                        "name": "dataset",
                        "type": "list",
                        "description": "Numeric dataset for analysis",
                        "required": True,
                    },
                    {
                        "name": "includeOutliers",
                        "type": "bool",
                        "description": "Include outlier detection",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "confidenceLevel",
                        "type": "float",
                        "description": "Confidence level for intervals",
                        "required": False,
                        "default": 0.95,
                    },
                    {
                        "name": "precision",
                        "type": "int",
                        "description": "Decimal places for results",
                        "required": False,
                        "default": 4,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Complete statistical summary with all metrics",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "descriptive_statistics",
                    "data_summarization",
                    "quality_metrics",
                    "process_analysis",
                ],
            },
            {
                "name": "system.statistics.performRegressionAnalysis",
                "description": "Perform regression analysis with multiple methods",
                "parameters": [
                    {
                        "name": "xData",
                        "type": "list",
                        "description": "Independent variable data",
                        "required": True,
                    },
                    {
                        "name": "yData",
                        "type": "list",
                        "description": "Dependent variable data",
                        "required": True,
                    },
                    {
                        "name": "regressionType",
                        "type": "str",
                        "description": "Regression type (linear, polynomial, exponential)",
                        "required": False,
                        "default": "linear",
                    },
                    {
                        "name": "polynomialDegree",
                        "type": "int",
                        "description": "Polynomial degree (if applicable)",
                        "required": False,
                        "default": 2,
                    },
                    {
                        "name": "includeStatistics",
                        "type": "bool",
                        "description": "Include statistical measures",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Regression results with equation and statistics",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "regression_analysis",
                    "trend_modeling",
                    "predictive_modeling",
                    "relationship_analysis",
                ],
            },
            {
                "name": "system.statistics.detectAnomalies",
                "description": "Detect statistical anomalies in datasets",
                "parameters": [
                    {
                        "name": "dataset",
                        "type": "list",
                        "description": "Dataset to analyze for anomalies",
                        "required": True,
                    },
                    {
                        "name": "method",
                        "type": "str",
                        "description": "Detection method (zscore, iqr, isolation_forest)",
                        "required": False,
                        "default": "zscore",
                    },
                    {
                        "name": "threshold",
                        "type": "float",
                        "description": "Anomaly detection threshold",
                        "required": False,
                        "default": 3.0,
                    },
                    {
                        "name": "contextWindow",
                        "type": "int",
                        "description": "Context window size",
                        "required": False,
                        "default": 50,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Anomaly detection results with indices and scores",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "anomaly_detection",
                    "outlier_identification",
                    "quality_control",
                    "fault_detection",
                ],
            },
            {
                "name": "system.statistics.calculateCorrelation",
                "description": "Calculate correlation between multiple variables",
                "parameters": [
                    {
                        "name": "datasets",
                        "type": "list",
                        "description": "list of datasets to correlate",
                        "required": True,
                    },
                    {
                        "name": "correlationType",
                        "type": "str",
                        "description": "Correlation type (pearson, spearman, kendall)",
                        "required": False,
                        "default": "pearson",
                    },
                    {
                        "name": "includeMatrix",
                        "type": "bool",
                        "description": "Include correlation matrix",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "significanceTest",
                        "type": "bool",
                        "description": "Perform significance testing",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Correlation results with matrix and significance",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "correlation_analysis",
                    "relationship_detection",
                    "multivariate_analysis",
                    "variable_dependency",
                ],
            },
            {
                "name": "system.statistics.performHypothesisTest",
                "description": "Perform statistical hypothesis tests",
                "parameters": [
                    {
                        "name": "sample1",
                        "type": "list",
                        "description": "First sample dataset",
                        "required": True,
                    },
                    {
                        "name": "sample2",
                        "type": "list",
                        "description": "Second sample dataset (if applicable)",
                        "required": False,
                    },
                    {
                        "name": "testType",
                        "type": "str",
                        "description": "Test type (ttest, anova, chisquare)",
                        "required": True,
                    },
                    {
                        "name": "alpha",
                        "type": "float",
                        "description": "Significance level",
                        "required": False,
                        "default": 0.05,
                    },
                    {
                        "name": "alternative",
                        "type": "str",
                        "description": "Alternative hypothesis (two-sided, greater, less)",
                        "required": False,
                        "default": "two-sided",
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Test results with statistics and p-values",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "hypothesis_testing",
                    "statistical_inference",
                    "quality_validation",
                    "process_comparison",
                ],
            },
            {
                "name": "system.statistics.generateDistribution",
                "description": "Generate and analyze statistical distributions",
                "parameters": [
                    {
                        "name": "distributionType",
                        "type": "str",
                        "description": "Distribution type (normal, exponential, uniform, gamma)",
                        "required": True,
                    },
                    {
                        "name": "parameters",
                        "type": "dict",
                        "description": "Distribution parameters",
                        "required": True,
                    },
                    {
                        "name": "sampleSize",
                        "type": "int",
                        "description": "Number of samples to generate",
                        "required": False,
                        "default": 1000,
                    },
                    {
                        "name": "calculateFit",
                        "type": "bool",
                        "description": "Calculate goodness of fit",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Distribution data with samples and fit statistics",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "distribution_analysis",
                    "probability_modeling",
                    "random_sampling",
                    "monte_carlo_simulation",
                ],
            },
            {
                "name": "system.statistics.performTimeSeriesAnalysis",
                "description": "Analyze time series data for trends and seasonality",
                "parameters": [
                    {
                        "name": "timeSeriesData",
                        "type": "list",
                        "description": "Time series data with timestamps",
                        "required": True,
                    },
                    {
                        "name": "analysisType",
                        "type": "str",
                        "description": "Analysis type (trend, seasonal, decomposition)",
                        "required": False,
                        "default": "decomposition",
                    },
                    {
                        "name": "seasonalPeriod",
                        "type": "int",
                        "description": "Seasonal period length",
                        "required": False,
                        "default": 12,
                    },
                    {
                        "name": "smoothingFactor",
                        "type": "float",
                        "description": "Smoothing factor for trends",
                        "required": False,
                        "default": 0.3,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Time series analysis with components and forecasts",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "time_series_analysis",
                    "trend_detection",
                    "seasonal_analysis",
                    "forecasting",
                ],
            },
            {
                "name": "system.statistics.calculateControlLimits",
                "description": "Calculate statistical process control limits",
                "parameters": [
                    {
                        "name": "processData",
                        "type": "list",
                        "description": "Process measurement data",
                        "required": True,
                    },
                    {
                        "name": "controlType",
                        "type": "str",
                        "description": "Control chart type (xbar, r, p, c)",
                        "required": True,
                    },
                    {
                        "name": "subgroupSize",
                        "type": "int",
                        "description": "Subgroup size for calculations",
                        "required": False,
                        "default": 5,
                    },
                    {
                        "name": "sigmaLevel",
                        "type": "float",
                        "description": "Sigma level for limits",
                        "required": False,
                        "default": 3.0,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Control limits with centerline and violation points",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "statistical_process_control",
                    "quality_control",
                    "control_charts",
                    "process_monitoring",
                ],
            },
            {
                "name": "system.statistics.performSurvivalAnalysis",
                "description": "Perform survival analysis for reliability studies",
                "parameters": [
                    {
                        "name": "eventTimes",
                        "type": "list",
                        "description": "Event occurrence times",
                        "required": True,
                    },
                    {
                        "name": "censoringData",
                        "type": "list",
                        "description": "Censoring indicators",
                        "required": False,
                    },
                    {
                        "name": "analysisMethod",
                        "type": "str",
                        "description": "Analysis method (kaplan_meier, weibull, exponential)",
                        "required": False,
                        "default": "kaplan_meier",
                    },
                    {
                        "name": "confidenceLevel",
                        "type": "float",
                        "description": "Confidence level for intervals",
                        "required": False,
                        "default": 0.95,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Survival analysis with curves and statistics",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "survival_analysis",
                    "reliability_analysis",
                    "failure_analysis",
                    "maintenance_planning",
                ],
            },
            {
                "name": "system.statistics.performClusterAnalysis",
                "description": "Perform cluster analysis for data grouping",
                "parameters": [
                    {
                        "name": "dataset",
                        "type": "list",
                        "description": "Multi-dimensional dataset",
                        "required": True,
                    },
                    {
                        "name": "clusteringMethod",
                        "type": "str",
                        "description": "Clustering method (kmeans, hierarchical, dbscan)",
                        "required": False,
                        "default": "kmeans",
                    },
                    {
                        "name": "numberOfClusters",
                        "type": "int",
                        "description": "Number of clusters (if applicable)",
                        "required": False,
                        "default": 3,
                    },
                    {
                        "name": "distanceMetric",
                        "type": "str",
                        "description": "Distance metric (euclidean, manhattan)",
                        "required": False,
                        "default": "euclidean",
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Cluster analysis with assignments and centroids",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Statistical Analysis",
                "patterns": [
                    "cluster_analysis",
                    "data_grouping",
                    "pattern_recognition",
                    "data_segmentation",
                ],
            },
        ]
    )

    return functions


if __name__ == "__main__":
    functions = get_statistical_analysis_functions()
    print(f"Statistical Analysis Functions: {len(functions)}")

    # Verify function structure
    for func in functions:
        assert "name" in func
        assert "description" in func
        assert "parameters" in func
        assert "returns" in func
        assert "scope" in func
        assert "category" in func
        assert "patterns" in func

    print("✅ All statistical analysis function definitions are valid!")
