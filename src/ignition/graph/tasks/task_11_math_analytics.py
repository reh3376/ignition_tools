"""Task 11: Advanced Math & Analytics Functions

Mathematical operations, statistical analysis, and data analytics functions for Ignition SCADA systems.

This module provides comprehensive mathematical and analytical capabilities including:
- Advanced Mathematical Operations
- Statistical Analysis & Distributions  
- Data Analytics & Pattern Recognition
- Machine Learning Utilities for SCADA
- Predictive Analytics & Forecasting
- Performance Metrics & KPI Calculations

Total Functions: 30 functions
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Tag System (Task 1), Database System (Task 2), File System (Task 10)
"""

from typing import Any


def get_math_analytics_functions() -> list[dict[str, Any]]:
    """Get comprehensive math and analytics functions for Task 11.

    Returns:
        List[Dict[str, Any]]: List of math and analytics function definitions
    """
    functions = []

    # ============================================================================
    # ADVANCED MATHEMATICAL OPERATIONS (10 functions)
    # ============================================================================

    functions.extend([
        {
            "name": "system.math.calculateTrigonometric",
            "description": "Calculate trigonometric functions with precision and units",
            "parameters": [
                {
                    "name": "function", 
                    "type": "str",
                    "description": "Trig function (sin, cos, tan, asin, acos, atan)",
                    "required": True,
                },
                {
                    "name": "value",
                    "type": "float", 
                    "description": "Input value for calculation",
                    "required": True,
                },
                {
                    "name": "inputUnit",
                    "type": "str",
                    "description": "Input unit (degrees, radians)",
                    "required": False,
                    "default": "radians",
                },
                {
                    "name": "precision",
                    "type": "int",
                    "description": "Decimal places for result",
                    "required": False,
                    "default": 6,
                },
            ],
            "returns": {
                "type": "float",
                "description": "Trigonometric calculation result with metadata",
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations",
            "patterns": [
                "trigonometric_calculations",
                "engineering_math",
                "geometric_analysis",
                "scientific_computing",
            ],
        },
        {
            "name": "system.math.matrixOperations",
            "description": "Perform matrix operations for engineering calculations",
            "parameters": [
                {
                    "name": "operation",
                    "type": "str", 
                    "description": "Matrix operation (multiply, add, subtract, transpose, inverse)",
                    "required": True,
                },
                {
                    "name": "matrixA",
                    "type": "list",
                    "description": "First matrix as nested list",
                    "required": True,
                },
                {
                    "name": "matrixB", 
                    "type": "list",
                    "description": "Second matrix (if required)",
                    "required": False,
                },
                {
                    "name": "validateDimensions",
                    "type": "bool",
                    "description": "Validate matrix dimensions before operation",
                    "required": False,
                    "default": True,
                },
            ],
            "returns": {
                "type": "list",
                "description": "Result matrix with operation metadata",
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations",
            "patterns": [
                "matrix_algebra",
                "linear_transformations", 
                "engineering_calculations",
                "data_processing",
            ],
        },
        {
            "name": "system.math.convertUnits",
            "description": "Convert between engineering units with precision",
            "parameters": [
                {
                    "name": "value",
                    "type": "float",
                    "description": "Value to convert",
                    "required": True,
                },
                {
                    "name": "fromUnit",
                    "type": "str",
                    "description": "Source unit",
                    "required": True,
                },
                {
                    "name": "toUnit",
                    "type": "str", 
                    "description": "Target unit",
                    "required": True,
                },
                {
                    "name": "unitCategory",
                    "type": "str",
                    "description": "Unit category (temperature, pressure, flow, etc.)",
                    "required": False,
                },
                {
                    "name": "precision",
                    "type": "int",
                    "description": "Decimal places for result",
                    "required": False,
                    "default": 4,
                },
            ],
            "returns": {
                "type": "dict",
                "description": "Converted value with conversion metadata",
            },
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations",
            "patterns": [
                "unit_conversion",
                "engineering_units",
                "measurement_standardization",
                "industrial_calculations",
            ],
        },
        {
            "name": "system.math.calculateLogarithmic",
            "description": "Calculate logarithmic and exponential functions",
            "parameters": [
                {"name": "function", "type": "str", "description": "Function type (log, ln, log10, exp, pow)", "required": True},
                {"name": "value", "type": "float", "description": "Input value", "required": True},
                {"name": "base", "type": "float", "description": "Base for logarithm (if applicable)", "required": False, "default": 10.0},
                {"name": "power", "type": "float", "description": "Power for exponential (if applicable)", "required": False, "default": 1.0},
            ],
            "returns": {"type": "float", "description": "Logarithmic/exponential calculation result"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations", 
            "patterns": ["logarithmic_calculations", "exponential_growth", "scientific_notation", "data_scaling"],
        },
        {
            "name": "system.math.interpolateValues",
            "description": "Interpolate values using various methods",
            "parameters": [
                {"name": "xValues", "type": "list", "description": "X-axis data points", "required": True},
                {"name": "yValues", "type": "list", "description": "Y-axis data points", "required": True},
                {"name": "targetX", "type": "float", "description": "X value to interpolate", "required": True},
                {"name": "method", "type": "str", "description": "Interpolation method (linear, cubic, spline)", "required": False, "default": "linear"},
                {"name": "extrapolate", "type": "bool", "description": "Allow extrapolation beyond data range", "required": False, "default": False},
            ],
            "returns": {"type": "float", "description": "Interpolated Y value with method metadata"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations",
            "patterns": ["data_interpolation", "curve_fitting", "signal_processing", "trend_estimation"],
        },
        {
            "name": "system.math.calculateDerivative",
            "description": "Calculate numerical derivatives for trend analysis",
            "parameters": [
                {"name": "dataPoints", "type": "list", "description": "Data points as [x, y] pairs", "required": True},
                {"name": "order", "type": "int", "description": "Derivative order (1st, 2nd, etc.)", "required": False, "default": 1},
                {"name": "method", "type": "str", "description": "Calculation method (forward, backward, central)", "required": False, "default": "central"},
                {"name": "smoothing", "type": "bool", "description": "Apply smoothing to reduce noise", "required": False, "default": True},
            ],
            "returns": {"type": "list", "description": "Derivative values with calculation metadata"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations",
            "patterns": ["derivative_analysis", "rate_of_change", "trend_detection", "signal_analysis"],
        },
        {
            "name": "system.math.calculateIntegral",
            "description": "Calculate numerical integrals for area under curves",
            "parameters": [
                {"name": "dataPoints", "type": "list", "description": "Data points as [x, y] pairs", "required": True},
                {"name": "method", "type": "str", "description": "Integration method (trapezoidal, simpson, rectangle)", "required": False, "default": "trapezoidal"},
                {"name": "lowerBound", "type": "float", "description": "Lower integration bound", "required": False},
                {"name": "upperBound", "type": "float", "description": "Upper integration bound", "required": False},
            ],
            "returns": {"type": "float", "description": "Integral value with calculation metadata"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations", 
            "patterns": ["numerical_integration", "area_calculation", "cumulative_analysis", "energy_calculations"],
        },
        {
            "name": "system.math.solvePIDController",
            "description": "Calculate PID controller output for process control",
            "parameters": [
                {"name": "setpoint", "type": "float", "description": "Desired setpoint value", "required": True},
                {"name": "processValue", "type": "float", "description": "Current process value", "required": True},
                {"name": "Kp", "type": "float", "description": "Proportional gain", "required": True},
                {"name": "Ki", "type": "float", "description": "Integral gain", "required": True},
                {"name": "Kd", "type": "float", "description": "Derivative gain", "required": True},
                {"name": "dt", "type": "float", "description": "Time step (seconds)", "required": True},
                {"name": "integralSum", "type": "float", "description": "Accumulated integral term", "required": False, "default": 0.0},
                {"name": "previousError", "type": "float", "description": "Previous error value", "required": False, "default": 0.0},
            ],
            "returns": {"type": "dict", "description": "PID output with component values and updated state"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations",
            "patterns": ["pid_control", "process_control", "feedback_systems", "automation_control"],
        },
        {
            "name": "system.math.optimizeFunction",
            "description": "Optimize functions using numerical methods",
            "parameters": [
                {"name": "functionData", "type": "list", "description": "Function data points", "required": True},
                {"name": "optimizationType", "type": "str", "description": "Optimization type (minimize, maximize)", "required": True},
                {"name": "method", "type": "str", "description": "Optimization method (gradient, simplex, genetic)", "required": False, "default": "gradient"},
                {"name": "constraints", "type": "dict", "description": "Optimization constraints", "required": False, "default": "{}"},
                {"name": "tolerance", "type": "float", "description": "Convergence tolerance", "required": False, "default": 1e-6},
            ],
            "returns": {"type": "dict", "description": "Optimized parameters with convergence info"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations",
            "patterns": ["function_optimization", "parameter_tuning", "efficiency_maximization", "cost_minimization"],
        },
        {
            "name": "system.math.calculateFourierTransform",
            "description": "Perform Fourier transform for frequency analysis",
            "parameters": [
                {"name": "timeSeriesData", "type": "list", "description": "Time series data points", "required": True},
                {"name": "samplingRate", "type": "float", "description": "Data sampling rate (Hz)", "required": True},
                {"name": "transformType", "type": "str", "description": "Transform type (FFT, DFT, inverse)", "required": False, "default": "FFT"},
                {"name": "windowFunction", "type": "str", "description": "Window function (hamming, hanning, blackman)", "required": False, "default": "hamming"},
                {"name": "zeroPadding", "type": "bool", "description": "Apply zero padding for better resolution", "required": False, "default": True},
            ],
            "returns": {"type": "dict", "description": "Frequency domain data with magnitude and phase"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Mathematical Operations",
            "patterns": ["frequency_analysis", "signal_processing", "vibration_analysis", "spectral_analysis"],
        },
    ])

    # ============================================================================
    # STATISTICAL ANALYSIS & DISTRIBUTIONS (10 functions)
    # ============================================================================

    functions.extend([
        {
            "name": "system.statistics.calculateDescriptiveStats",
            "description": "Calculate comprehensive descriptive statistics",
            "parameters": [
                {"name": "dataset", "type": "list", "description": "Numeric dataset for analysis", "required": True},
                {"name": "includeOutliers", "type": "bool", "description": "Include outlier detection", "required": False, "default": True},
                {"name": "confidenceLevel", "type": "float", "description": "Confidence level for intervals", "required": False, "default": 0.95},
                {"name": "precision", "type": "int", "description": "Decimal places for results", "required": False, "default": 4},
            ],
            "returns": {"type": "dict", "description": "Complete statistical summary with all metrics"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["descriptive_statistics", "data_summarization", "quality_metrics", "process_analysis"],
        },
        {
            "name": "system.statistics.performRegressionAnalysis",
            "description": "Perform regression analysis with multiple methods",
            "parameters": [
                {"name": "xData", "type": "list", "description": "Independent variable data", "required": True},
                {"name": "yData", "type": "list", "description": "Dependent variable data", "required": True},
                {"name": "regressionType", "type": "str", "description": "Regression type (linear, polynomial, exponential)", "required": False, "default": "linear"},
                {"name": "polynomialDegree", "type": "int", "description": "Polynomial degree (if applicable)", "required": False, "default": 2},
                {"name": "includeStatistics", "type": "bool", "description": "Include statistical measures", "required": False, "default": True},
            ],
            "returns": {"type": "dict", "description": "Regression results with equation and statistics"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["regression_analysis", "trend_modeling", "predictive_modeling", "relationship_analysis"],
        },
        {
            "name": "system.statistics.detectAnomalies",
            "description": "Detect statistical anomalies in datasets",
            "parameters": [
                {"name": "dataset", "type": "list", "description": "Dataset to analyze for anomalies", "required": True},
                {"name": "method", "type": "str", "description": "Detection method (zscore, iqr, isolation_forest)", "required": False, "default": "zscore"},
                {"name": "threshold", "type": "float", "description": "Anomaly detection threshold", "required": False, "default": 3.0},
                {"name": "contextWindow", "type": "int", "description": "Context window size", "required": False, "default": 50},
            ],
            "returns": {"type": "dict", "description": "Anomaly detection results with indices and scores"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["anomaly_detection", "outlier_identification", "quality_control", "fault_detection"],
        },
        {
            "name": "system.statistics.calculateCorrelation",
            "description": "Calculate correlation between multiple variables",
            "parameters": [
                {"name": "datasets", "type": "list", "description": "List of datasets to correlate", "required": True},
                {"name": "correlationType", "type": "str", "description": "Correlation type (pearson, spearman, kendall)", "required": False, "default": "pearson"},
                {"name": "includeMatrix", "type": "bool", "description": "Include correlation matrix", "required": False, "default": True},
                {"name": "significanceTest", "type": "bool", "description": "Perform significance testing", "required": False, "default": True},
            ],
            "returns": {"type": "dict", "description": "Correlation results with matrix and significance"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["correlation_analysis", "relationship_detection", "multivariate_analysis", "variable_dependency"],
        },
        {
            "name": "system.statistics.performHypothesisTest",
            "description": "Perform statistical hypothesis tests",
            "parameters": [
                {"name": "sample1", "type": "list", "description": "First sample dataset", "required": True},
                {"name": "sample2", "type": "list", "description": "Second sample dataset (if applicable)", "required": False},
                {"name": "testType", "type": "str", "description": "Test type (ttest, anova, chisquare)", "required": True},
                {"name": "alpha", "type": "float", "description": "Significance level", "required": False, "default": 0.05},
                {"name": "alternative", "type": "str", "description": "Alternative hypothesis (two-sided, greater, less)", "required": False, "default": "two-sided"},
            ],
            "returns": {"type": "dict", "description": "Test results with statistics and p-values"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["hypothesis_testing", "statistical_inference", "quality_validation", "process_comparison"],
        },
        {
            "name": "system.statistics.generateDistribution",
            "description": "Generate and analyze statistical distributions",
            "parameters": [
                {"name": "distributionType", "type": "str", "description": "Distribution type (normal, exponential, uniform, gamma)", "required": True},
                {"name": "parameters", "type": "dict", "description": "Distribution parameters", "required": True},
                {"name": "sampleSize", "type": "int", "description": "Number of samples to generate", "required": False, "default": 1000},
                {"name": "calculateFit", "type": "bool", "description": "Calculate goodness of fit", "required": False, "default": True},
            ],
            "returns": {"type": "dict", "description": "Distribution data with samples and fit statistics"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["distribution_analysis", "probability_modeling", "random_sampling", "monte_carlo_simulation"],
        },
        {
            "name": "system.statistics.performTimeSeriesAnalysis",
            "description": "Analyze time series data for trends and seasonality",
            "parameters": [
                {"name": "timeSeriesData", "type": "list", "description": "Time series data with timestamps", "required": True},
                {"name": "analysisType", "type": "str", "description": "Analysis type (trend, seasonal, decomposition)", "required": False, "default": "decomposition"},
                {"name": "seasonalPeriod", "type": "int", "description": "Seasonal period length", "required": False, "default": 12},
                {"name": "smoothingFactor", "type": "float", "description": "Smoothing factor for trends", "required": False, "default": 0.3},
            ],
            "returns": {"type": "dict", "description": "Time series analysis with components and forecasts"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["time_series_analysis", "trend_detection", "seasonal_analysis", "forecasting"],
        },
        {
            "name": "system.statistics.calculateControlLimits",
            "description": "Calculate statistical process control limits",
            "parameters": [
                {"name": "processData", "type": "list", "description": "Process measurement data", "required": True},
                {"name": "controlType", "type": "str", "description": "Control chart type (xbar, r, p, c)", "required": True},
                {"name": "subgroupSize", "type": "int", "description": "Subgroup size for calculations", "required": False, "default": 5},
                {"name": "sigmaLevel", "type": "float", "description": "Sigma level for limits", "required": False, "default": 3.0},
            ],
            "returns": {"type": "dict", "description": "Control limits with centerline and violation points"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["statistical_process_control", "quality_control", "control_charts", "process_monitoring"],
        },
        {
            "name": "system.statistics.performSurvivalAnalysis",
            "description": "Perform survival analysis for reliability studies",
            "parameters": [
                {"name": "eventTimes", "type": "list", "description": "Event occurrence times", "required": True},
                {"name": "censoringData", "type": "list", "description": "Censoring indicators", "required": False},
                {"name": "analysisMethod", "type": "str", "description": "Analysis method (kaplan_meier, weibull, exponential)", "required": False, "default": "kaplan_meier"},
                {"name": "confidenceLevel", "type": "float", "description": "Confidence level for intervals", "required": False, "default": 0.95},
            ],
            "returns": {"type": "dict", "description": "Survival analysis with curves and statistics"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["survival_analysis", "reliability_analysis", "failure_analysis", "maintenance_planning"],
        },
        {
            "name": "system.statistics.performClusterAnalysis",
            "description": "Perform cluster analysis for data grouping",
            "parameters": [
                {"name": "dataset", "type": "list", "description": "Multi-dimensional dataset", "required": True},
                {"name": "clusteringMethod", "type": "str", "description": "Clustering method (kmeans, hierarchical, dbscan)", "required": False, "default": "kmeans"},
                {"name": "numberOfClusters", "type": "int", "description": "Number of clusters (if applicable)", "required": False, "default": 3},
                {"name": "distanceMetric", "type": "str", "description": "Distance metric (euclidean, manhattan)", "required": False, "default": "euclidean"},
            ],
            "returns": {"type": "dict", "description": "Cluster analysis with assignments and centroids"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Statistical Analysis",
            "patterns": ["cluster_analysis", "data_grouping", "pattern_recognition", "data_segmentation"],
        },
    ])

    # ============================================================================
    # DATA ANALYTICS & PATTERN RECOGNITION (10 functions)
    # ============================================================================

    functions.extend([
        {
            "name": "system.analytics.calculateKPIs",
            "description": "Calculate key performance indicators for operations",
            "parameters": [
                {"name": "kpiDefinitions", "type": "dict", "description": "KPI calculation definitions", "required": True},
                {"name": "dataSource", "type": "str", "description": "Data source identifier", "required": True},
                {"name": "timeRange", "type": "dict", "description": "Time range for calculations", "required": True},
                {"name": "aggregationLevel", "type": "str", "description": "Aggregation level (hourly, daily, weekly)", "required": False, "default": "daily"},
                {"name": "includeTargets", "type": "bool", "description": "Include target comparisons", "required": False, "default": True},
            ],
            "returns": {"type": "dict", "description": "KPI values with trends and target comparisons"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["kpi_calculation", "performance_monitoring", "operational_analytics", "dashboard_metrics"],
        },
        {
            "name": "system.analytics.performPredictiveAnalysis",
            "description": "Perform predictive analysis using machine learning",
            "parameters": [
                {"name": "historicalData", "type": "list", "description": "Historical training data", "required": True},
                {"name": "targetVariable", "type": "str", "description": "Variable to predict", "required": True},
                {"name": "predictionModel", "type": "str", "description": "Model type (linear, neural_network, random_forest)", "required": False, "default": "linear"},
                {"name": "forecastHorizon", "type": "int", "description": "Number of periods to forecast", "required": False, "default": 10},
                {"name": "includeConfidenceIntervals", "type": "bool", "description": "Include prediction intervals", "required": False, "default": True},
            ],
            "returns": {"type": "dict", "description": "Predictions with confidence intervals and model metrics"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["predictive_analytics", "forecasting", "machine_learning", "trend_prediction"],
        },
        {
            "name": "system.analytics.detectPatterns",
            "description": "Detect patterns in process data using advanced algorithms",
            "parameters": [
                {"name": "dataset", "type": "list", "description": "Dataset to analyze for patterns", "required": True},
                {"name": "patternType", "type": "str", "description": "Pattern type (sequence, frequency, association)", "required": True},
                {"name": "minSupport", "type": "float", "description": "Minimum support threshold", "required": False, "default": 0.1},
                {"name": "minConfidence", "type": "float", "description": "Minimum confidence threshold", "required": False, "default": 0.5},
                {"name": "windowSize", "type": "int", "description": "Analysis window size", "required": False, "default": 100},
            ],
            "returns": {"type": "dict", "description": "Detected patterns with support and confidence metrics"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["pattern_detection", "data_mining", "sequence_analysis", "association_rules"],
        },
        {
            "name": "system.analytics.optimizeProcess",
            "description": "Optimize process parameters using data-driven methods",
            "parameters": [
                {"name": "processData", "type": "list", "description": "Historical process data", "required": True},
                {"name": "objectiveFunction", "type": "str", "description": "Optimization objective", "required": True},
                {"name": "constraints", "type": "dict", "description": "Process constraints", "required": False, "default": "{}"},
                {"name": "optimizationMethod", "type": "str", "description": "Optimization algorithm", "required": False, "default": "genetic_algorithm"},
                {"name": "maxIterations", "type": "int", "description": "Maximum optimization iterations", "required": False, "default": 1000},
            ],
            "returns": {"type": "dict", "description": "Optimized parameters with performance improvements"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["process_optimization", "parameter_tuning", "efficiency_improvement", "performance_optimization"],
        },
        {
            "name": "system.analytics.calculateOEE",
            "description": "Calculate Overall Equipment Effectiveness metrics",
            "parameters": [
                {"name": "productionData", "type": "dict", "description": "Production data with times and quantities", "required": True},
                {"name": "timeRange", "type": "dict", "description": "Analysis time range", "required": True},
                {"name": "plannedProductionTime", "type": "float", "description": "Planned production time", "required": True},
                {"name": "idealCycleTime", "type": "float", "description": "Ideal cycle time per unit", "required": True},
                {"name": "includeBreakdown", "type": "bool", "description": "Include component breakdown", "required": False, "default": True},
            ],
            "returns": {"type": "dict", "description": "OEE metrics with availability, performance, and quality"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["oee_calculation", "equipment_effectiveness", "production_analytics", "manufacturing_kpis"],
        },
        {
            "name": "system.analytics.performRootCauseAnalysis",
            "description": "Perform automated root cause analysis on system events",
            "parameters": [
                {"name": "eventData", "type": "list", "description": "System event and alarm data", "required": True},
                {"name": "timeWindow", "type": "int", "description": "Analysis time window (minutes)", "required": False, "default": 60},
                {"name": "correlationThreshold", "type": "float", "description": "Correlation threshold for causality", "required": False, "default": 0.7},
                {"name": "includeSystemModel", "type": "bool", "description": "Use system model for analysis", "required": False, "default": True},
            ],
            "returns": {"type": "dict", "description": "Root cause analysis with ranked probable causes"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["root_cause_analysis", "fault_diagnosis", "event_correlation", "troubleshooting"],
        },
        {
            "name": "system.analytics.generateRecommendations",
            "description": "Generate operational recommendations using analytics",
            "parameters": [
                {"name": "operationalData", "type": "dict", "description": "Current operational data", "required": True},
                {"name": "historicalPerformance", "type": "list", "description": "Historical performance data", "required": True},
                {"name": "recommendationType", "type": "str", "description": "Recommendation type (efficiency, maintenance, quality)", "required": True},
                {"name": "confidenceThreshold", "type": "float", "description": "Minimum confidence for recommendations", "required": False, "default": 0.8},
            ],
            "returns": {"type": "dict", "description": "Ranked recommendations with confidence and impact"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["recommendation_engine", "decision_support", "optimization_suggestions", "intelligent_insights"],
        },
        {
            "name": "system.analytics.detectEquipmentDegradation",
            "description": "Detect equipment performance degradation trends",
            "parameters": [
                {"name": "equipmentData", "type": "list", "description": "Equipment performance time series", "required": True},
                {"name": "baselineData", "type": "list", "description": "Baseline performance data", "required": True},
                {"name": "degradationMetrics", "type": "list", "description": "Metrics to monitor for degradation", "required": True},
                {"name": "alertThreshold", "type": "float", "description": "Degradation alert threshold", "required": False, "default": 0.15},
            ],
            "returns": {"type": "dict", "description": "Degradation analysis with severity and predictions"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["condition_monitoring", "predictive_maintenance", "equipment_health", "degradation_detection"],
        },
        {
            "name": "system.analytics.calculateEnergyEfficiency",
            "description": "Calculate energy efficiency metrics and optimization opportunities",
            "parameters": [
                {"name": "energyData", "type": "dict", "description": "Energy consumption data", "required": True},
                {"name": "productionData", "type": "dict", "description": "Production output data", "required": True},
                {"name": "benchmarkData", "type": "dict", "description": "Industry benchmark data", "required": False},
                {"name": "analysisLevel", "type": "str", "description": "Analysis level (equipment, line, plant)", "required": False, "default": "equipment"},
            ],
            "returns": {"type": "dict", "description": "Energy efficiency metrics with improvement opportunities"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["energy_efficiency", "sustainability_metrics", "cost_optimization", "environmental_impact"],
        },
        {
            "name": "system.analytics.performRiskAssessment",
            "description": "Perform quantitative risk assessment using operational data",
            "parameters": [
                {"name": "riskFactors", "type": "dict", "description": "Identified risk factors and data", "required": True},
                {"name": "probabilityModel", "type": "str", "description": "Probability estimation method", "required": False, "default": "monte_carlo"},
                {"name": "impactScenarios", "type": "list", "description": "Impact scenario definitions", "required": True},
                {"name": "confidenceLevel", "type": "float", "description": "Confidence level for estimates", "required": False, "default": 0.95},
            ],
            "returns": {"type": "dict", "description": "Risk assessment with probability and impact analysis"},
            "scope": ["Gateway", "Vision Client", "Perspective Session"],
            "category": "Data Analytics",
            "patterns": ["risk_assessment", "probability_analysis", "impact_evaluation", "decision_analysis"],
        },
    ])

    return functions


def get_task_11_metadata() -> dict[str, Any]:
    """Get metadata about Task 11: Advanced Math & Analytics Functions."""
    return {
        "task_number": 11,
        "task_name": "Advanced Math & Analytics Functions", 
        "description": "Mathematical operations, statistical analysis, and data analytics for SCADA systems",
        "total_functions": 30,
        "categories": ["Mathematical Operations", "Statistical Analysis", "Data Analytics"],
        "contexts": ["Gateway", "Vision Client", "Perspective Session"],
        "dependencies": ["Task 1: Tag System", "Task 2: Database System", "Task 10: File System"],
        "priority": "MEDIUM",
        "estimated_completion": "Week 12"
    }


if __name__ == "__main__":
    functions = get_math_analytics_functions()
    metadata = get_task_11_metadata()
    print(f"Task 11: {metadata['task_name']}")
    print(f"Total Functions: {len(functions)}")
    print(f"Expected: {metadata['total_functions']}")
    
    # Verify function structure
    for func in functions:
        assert "name" in func
        assert "description" in func
        assert "parameters" in func
        assert "returns" in func
        assert "scope" in func
        assert "category" in func
        assert "patterns" in func
    
    print("✅ All function definitions are valid!") 