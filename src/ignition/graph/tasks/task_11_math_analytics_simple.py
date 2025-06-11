"""Task 11: Advanced Math & Analytics Functions (Simplified for Neo4j)

Mathematical operations, statistical analysis, and data analytics functions for Ignition SCADA systems.
This is a Neo4j-compatible version with simplified parameter and return structures.

Total Functions: 30 functions
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Tag System (Task 1), Database System (Task 2), File System (Task 10)
"""

from typing import Any


def get_math_analytics_functions() -> list[dict[str, Any]]:
    """Get simplified math and analytics functions for Task 11."""
    functions = []

    # ============================================================================
    # ADVANCED MATHEMATICAL OPERATIONS (10 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.math.calculateTrigonometric",
                "description": "Calculate trigonometric functions with precision and units",
                "parameters": "function:str:required, value:float:required, inputUnit:str:optional:radians, precision:int:optional:6",
                "returns": "float - Trigonometric calculation result with metadata",
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
                "parameters": "operation:str:required, matrixA:list:required, matrixB:list:optional, validateDimensions:bool:optional:true",
                "returns": "list - Result matrix with operation metadata",
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
                "parameters": "value:float:required, fromUnit:str:required, toUnit:str:required, unitCategory:str:optional, precision:int:optional:4",
                "returns": "dict - Converted value with conversion metadata",
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
                "parameters": "function:str:required, value:float:required, base:float:optional:10.0, power:float:optional:1.0",
                "returns": "float - Logarithmic/exponential calculation result",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "logarithmic_calculations",
                    "exponential_growth",
                    "scientific_notation",
                    "data_scaling",
                ],
            },
            {
                "name": "system.math.interpolateValues",
                "description": "Interpolate values using various methods",
                "parameters": "xValues:list:required, yValues:list:required, targetX:float:required, method:str:optional:linear, extrapolate:bool:optional:false",
                "returns": "float - Interpolated Y value with method metadata",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "data_interpolation",
                    "curve_fitting",
                    "signal_processing",
                    "trend_estimation",
                ],
            },
            {
                "name": "system.math.calculateDerivative",
                "description": "Calculate numerical derivatives for trend analysis",
                "parameters": "dataPoints:list:required, order:int:optional:1, method:str:optional:central, smoothing:bool:optional:true",
                "returns": "list - Derivative values with calculation metadata",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "derivative_analysis",
                    "rate_of_change",
                    "trend_detection",
                    "signal_analysis",
                ],
            },
            {
                "name": "system.math.calculateIntegral",
                "description": "Calculate numerical integrals for area under curves",
                "parameters": "dataPoints:list:required, method:str:optional:trapezoidal, lowerBound:float:optional, upperBound:float:optional",
                "returns": "float - Integral value with calculation metadata",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "numerical_integration",
                    "area_calculation",
                    "cumulative_analysis",
                    "energy_calculations",
                ],
            },
            {
                "name": "system.math.solvePIDController",
                "description": "Calculate PID controller output for process control",
                "parameters": "setpoint:float:required, processValue:float:required, Kp:float:required, Ki:float:required, Kd:float:required, dt:float:required, integralSum:float:optional:0.0, previousError:float:optional:0.0",
                "returns": "dict - PID output with component values and updated state",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "pid_control",
                    "process_control",
                    "feedback_systems",
                    "automation_control",
                ],
            },
            {
                "name": "system.math.optimizeFunction",
                "description": "Optimize functions using numerical methods",
                "parameters": "functionData:list:required, optimizationType:str:required, method:str:optional:gradient, constraints:dict:optional, tolerance:float:optional:1e-6",
                "returns": "dict - Optimized parameters with convergence info",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "function_optimization",
                    "parameter_tuning",
                    "efficiency_maximization",
                    "cost_minimization",
                ],
            },
            {
                "name": "system.math.calculateFourierTransform",
                "description": "Perform Fourier transform for frequency analysis",
                "parameters": "timeSeriesData:list:required, samplingRate:float:required, transformType:str:optional:FFT, windowFunction:str:optional:hamming, zeroPadding:bool:optional:true",
                "returns": "dict - Frequency domain data with magnitude and phase",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "frequency_analysis",
                    "signal_processing",
                    "vibration_analysis",
                    "spectral_analysis",
                ],
            },
        ]
    )

    # ============================================================================
    # STATISTICAL ANALYSIS & DISTRIBUTIONS (10 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.statistics.calculateDescriptiveStats",
                "description": "Calculate comprehensive descriptive statistics",
                "parameters": "dataset:list:required, includeOutliers:bool:optional:true, confidenceLevel:float:optional:0.95, precision:int:optional:4",
                "returns": "dict - Complete statistical summary with all metrics",
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
                "parameters": "xData:list:required, yData:list:required, regressionType:str:optional:linear, polynomialDegree:int:optional:2, includeStatistics:bool:optional:true",
                "returns": "dict - Regression results with equation and statistics",
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
                "parameters": "dataset:list:required, method:str:optional:zscore, threshold:float:optional:3.0, contextWindow:int:optional:50",
                "returns": "dict - Anomaly detection results with indices and scores",
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
                "parameters": "datasets:list:required, correlationType:str:optional:pearson, includeMatrix:bool:optional:true, significanceTest:bool:optional:true",
                "returns": "dict - Correlation results with matrix and significance",
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
                "parameters": "sample1:list:required, sample2:list:optional, testType:str:required, alpha:float:optional:0.05, alternative:str:optional:two-sided",
                "returns": "dict - Test results with statistics and p-values",
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
                "parameters": "distributionType:str:required, parameters:dict:required, sampleSize:int:optional:1000, calculateFit:bool:optional:true",
                "returns": "dict - Distribution data with samples and fit statistics",
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
                "parameters": "timeSeriesData:list:required, analysisType:str:optional:decomposition, seasonalPeriod:int:optional:12, smoothingFactor:float:optional:0.3",
                "returns": "dict - Time series analysis with components and forecasts",
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
                "parameters": "processData:list:required, controlType:str:required, subgroupSize:int:optional:5, sigmaLevel:float:optional:3.0",
                "returns": "dict - Control limits with centerline and violation points",
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
                "parameters": "eventTimes:list:required, censoringData:list:optional, analysisMethod:str:optional:kaplan_meier, confidenceLevel:float:optional:0.95",
                "returns": "dict - Survival analysis with curves and statistics",
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
                "parameters": "dataset:list:required, clusteringMethod:str:optional:kmeans, numberOfClusters:int:optional:3, distanceMetric:str:optional:euclidean",
                "returns": "dict - Cluster analysis with assignments and centroids",
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

    # ============================================================================
    # DATA ANALYTICS & PATTERN RECOGNITION (10 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.analytics.calculateKPIs",
                "description": "Calculate key performance indicators for operations",
                "parameters": "kpiDefinitions:dict:required, dataSource:str:required, timeRange:dict:required, aggregationLevel:str:optional:daily, includeTargets:bool:optional:true",
                "returns": "dict - KPI values with trends and target comparisons",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "kpi_calculation",
                    "performance_monitoring",
                    "operational_analytics",
                    "dashboard_metrics",
                ],
            },
            {
                "name": "system.analytics.performPredictiveAnalysis",
                "description": "Perform predictive analysis using machine learning",
                "parameters": "historicalData:list:required, targetVariable:str:required, predictionModel:str:optional:linear, forecastHorizon:int:optional:10, includeConfidenceIntervals:bool:optional:true",
                "returns": "dict - Predictions with confidence intervals and model metrics",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "predictive_analytics",
                    "forecasting",
                    "machine_learning",
                    "trend_prediction",
                ],
            },
            {
                "name": "system.analytics.detectPatterns",
                "description": "Detect patterns in process data using advanced algorithms",
                "parameters": "dataset:list:required, patternType:str:required, minSupport:float:optional:0.1, minConfidence:float:optional:0.5, windowSize:int:optional:100",
                "returns": "dict - Detected patterns with support and confidence metrics",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "pattern_detection",
                    "data_mining",
                    "sequence_analysis",
                    "association_rules",
                ],
            },
            {
                "name": "system.analytics.optimizeProcess",
                "description": "Optimize process parameters using data-driven methods",
                "parameters": "processData:list:required, objectiveFunction:str:required, constraints:dict:optional, optimizationMethod:str:optional:genetic_algorithm, maxIterations:int:optional:1000",
                "returns": "dict - Optimized parameters with performance improvements",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "process_optimization",
                    "parameter_tuning",
                    "efficiency_improvement",
                    "performance_optimization",
                ],
            },
            {
                "name": "system.analytics.calculateOEE",
                "description": "Calculate Overall Equipment Effectiveness metrics",
                "parameters": "productionData:dict:required, timeRange:dict:required, plannedProductionTime:float:required, idealCycleTime:float:required, includeBreakdown:bool:optional:true",
                "returns": "dict - OEE metrics with availability, performance, and quality",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "oee_calculation",
                    "equipment_effectiveness",
                    "production_analytics",
                    "manufacturing_kpis",
                ],
            },
            {
                "name": "system.analytics.performRootCauseAnalysis",
                "description": "Perform automated root cause analysis on system events",
                "parameters": "eventData:list:required, timeWindow:int:optional:60, correlationThreshold:float:optional:0.7, includeSystemModel:bool:optional:true",
                "returns": "dict - Root cause analysis with ranked probable causes",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "root_cause_analysis",
                    "fault_diagnosis",
                    "event_correlation",
                    "troubleshooting",
                ],
            },
            {
                "name": "system.analytics.generateRecommendations",
                "description": "Generate operational recommendations using analytics",
                "parameters": "operationalData:dict:required, historicalPerformance:list:required, recommendationType:str:required, confidenceThreshold:float:optional:0.8",
                "returns": "dict - Ranked recommendations with confidence and impact",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "recommendation_engine",
                    "decision_support",
                    "optimization_suggestions",
                    "intelligent_insights",
                ],
            },
            {
                "name": "system.analytics.detectEquipmentDegradation",
                "description": "Detect equipment performance degradation trends",
                "parameters": "equipmentData:list:required, baselineData:list:required, degradationMetrics:list:required, alertThreshold:float:optional:0.15",
                "returns": "dict - Degradation analysis with severity and predictions",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "condition_monitoring",
                    "predictive_maintenance",
                    "equipment_health",
                    "degradation_detection",
                ],
            },
            {
                "name": "system.analytics.calculateEnergyEfficiency",
                "description": "Calculate energy efficiency metrics and optimization opportunities",
                "parameters": "energyData:dict:required, productionData:dict:required, benchmarkData:dict:optional, analysisLevel:str:optional:equipment",
                "returns": "dict - Energy efficiency metrics with improvement opportunities",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "energy_efficiency",
                    "sustainability_metrics",
                    "cost_optimization",
                    "environmental_impact",
                ],
            },
            {
                "name": "system.analytics.performRiskAssessment",
                "description": "Perform quantitative risk assessment using operational data",
                "parameters": "riskFactors:dict:required, probabilityModel:str:optional:monte_carlo, impactScenarios:list:required, confidenceLevel:float:optional:0.95",
                "returns": "dict - Risk assessment with probability and impact analysis",
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Data Analytics",
                "patterns": [
                    "risk_assessment",
                    "probability_analysis",
                    "impact_evaluation",
                    "decision_analysis",
                ],
            },
        ]
    )

    return functions


def get_task_11_metadata() -> dict[str, Any]:
    """Get metadata about Task 11: Advanced Math & Analytics Functions."""
    return {
        "task_number": 11,
        "task_name": "Advanced Math & Analytics Functions",
        "description": "Mathematical operations, statistical analysis, and data analytics for SCADA systems",
        "total_functions": 30,
        "categories": [
            "Mathematical Operations",
            "Statistical Analysis",
            "Data Analytics",
        ],
        "contexts": ["Gateway", "Vision Client", "Perspective Session"],
        "dependencies": [
            "Task 1: Tag System",
            "Task 2: Database System",
            "Task 10: File System",
        ],
        "priority": "MEDIUM",
        "estimated_completion": "Week 12",
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
