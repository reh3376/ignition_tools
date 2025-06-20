"""Task 11: Mathematical Operations Module.

Advanced mathematical operations for Ignition SCADA systems.
Extracted from task_11_math_analytics.py for better modularity.

This module provides:
- Trigonometric calculations with precision
- Matrix operations for engineering
- Unit conversions with validation
- Logarithmic and exponential functions
- Value interpolation methods
- Complex number operations
- Polynomial calculations
- Numerical integration/differentiation
- Root finding algorithms
- Advanced curve fitting

Total Functions: 10 functions
"""

from typing import Any


def get_math_operations_functions() -> list[dict[str, Any]]:
    """Get mathematical operations functions for Task 11.

    Returns:
        list[dict[str, Any]]: List of mathematical operation function definitions
    """
    functions = []

    # Mathematical Operations Section
    functions.extend(
        [
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
                    {
                        "name": "function",
                        "type": "str",
                        "description": "Function type (log, ln, log10, exp, pow)",
                        "required": True,
                    },
                    {
                        "name": "value",
                        "type": "float",
                        "description": "Input value",
                        "required": True,
                    },
                    {
                        "name": "base",
                        "type": "float",
                        "description": "Base for logarithm (if applicable)",
                        "required": False,
                        "default": 10.0,
                    },
                    {
                        "name": "power",
                        "type": "float",
                        "description": "Power for exponential (if applicable)",
                        "required": False,
                        "default": 1.0,
                    },
                ],
                "returns": {
                    "type": "float",
                    "description": "Logarithmic/exponential calculation result",
                },
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
                "parameters": [
                    {
                        "name": "xValues",
                        "type": "list",
                        "description": "X-axis data points",
                        "required": True,
                    },
                    {
                        "name": "yValues",
                        "type": "list",
                        "description": "Y-axis data points",
                        "required": True,
                    },
                    {
                        "name": "targetX",
                        "type": "float",
                        "description": "X value to interpolate",
                        "required": True,
                    },
                    {
                        "name": "method",
                        "type": "str",
                        "description": "Interpolation method (linear, cubic, spline)",
                        "required": False,
                        "default": "linear",
                    },
                    {
                        "name": "extrapolate",
                        "type": "bool",
                        "description": "Allow extrapolation beyond data range",
                        "required": False,
                        "default": False,
                    },
                ],
                "returns": {
                    "type": "float",
                    "description": "Interpolated value with method metadata",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "data_interpolation",
                    "curve_fitting",
                    "signal_processing",
                    "data_smoothing",
                ],
            },
            {
                "name": "system.math.performComplexOperations",
                "description": "Perform operations with complex numbers",
                "parameters": [
                    {
                        "name": "operation",
                        "type": "str",
                        "description": "Complex operation (add, multiply, magnitude, phase, conjugate)",
                        "required": True,
                    },
                    {
                        "name": "complexA",
                        "type": "dict",
                        "description": "First complex number {real, imaginary}",
                        "required": True,
                    },
                    {
                        "name": "complexB",
                        "type": "dict",
                        "description": "Second complex number (if required)",
                        "required": False,
                    },
                    {
                        "name": "outputFormat",
                        "type": "str",
                        "description": "Output format (rectangular, polar)",
                        "required": False,
                        "default": "rectangular",
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Complex number result with metadata",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "complex_arithmetic",
                    "signal_analysis",
                    "frequency_domain",
                    "electrical_calculations",
                ],
            },
            {
                "name": "system.math.solvePolynomial",
                "description": "Solve polynomial equations and evaluate polynomials",
                "parameters": [
                    {
                        "name": "coefficients",
                        "type": "list",
                        "description": "Polynomial coefficients (highest to lowest degree)",
                        "required": True,
                    },
                    {
                        "name": "operation",
                        "type": "str",
                        "description": "Operation (evaluate, solve, derivative, integral)",
                        "required": True,
                    },
                    {
                        "name": "xValue",
                        "type": "float",
                        "description": "X value for evaluation (if applicable)",
                        "required": False,
                    },
                    {
                        "name": "integrationBounds",
                        "type": "list",
                        "description": "Integration bounds [lower, upper]",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Polynomial operation result with metadata",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "polynomial_math",
                    "equation_solving",
                    "calculus_operations",
                    "curve_analysis",
                ],
            },
            {
                "name": "system.math.numericalIntegration",
                "description": "Perform numerical integration using various methods",
                "parameters": [
                    {
                        "name": "dataPoints",
                        "type": "list",
                        "description": "Data points for integration",
                        "required": True,
                    },
                    {
                        "name": "method",
                        "type": "str",
                        "description": "Integration method (trapezoidal, simpson, gaussian)",
                        "required": False,
                        "default": "trapezoidal",
                    },
                    {
                        "name": "bounds",
                        "type": "list",
                        "description": "Integration bounds [lower, upper]",
                        "required": True,
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
                    "type": "dict",
                    "description": "Integration result with error estimation",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "numerical_integration",
                    "area_calculation",
                    "signal_processing",
                    "data_analysis",
                ],
            },
            {
                "name": "system.math.findRoots",
                "description": "Find roots of equations using numerical methods",
                "parameters": [
                    {
                        "name": "equation",
                        "type": "str",
                        "description": "Equation string or coefficients",
                        "required": True,
                    },
                    {
                        "name": "method",
                        "type": "str",
                        "description": "Root finding method (bisection, newton, secant)",
                        "required": False,
                        "default": "newton",
                    },
                    {
                        "name": "initialGuess",
                        "type": "float",
                        "description": "Initial guess for root",
                        "required": False,
                        "default": 0.0,
                    },
                    {
                        "name": "tolerance",
                        "type": "float",
                        "description": "Convergence tolerance",
                        "required": False,
                        "default": 1e-6,
                    },
                    {
                        "name": "maxIterations",
                        "type": "int",
                        "description": "Maximum iterations",
                        "required": False,
                        "default": 100,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Root finding results with convergence info",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "root_finding",
                    "equation_solving",
                    "optimization",
                    "numerical_methods",
                ],
            },
            {
                "name": "system.math.curveFitting",
                "description": "Fit curves to data using various mathematical models",
                "parameters": [
                    {
                        "name": "xData",
                        "type": "list",
                        "description": "X-axis data points",
                        "required": True,
                    },
                    {
                        "name": "yData",
                        "type": "list",
                        "description": "Y-axis data points",
                        "required": True,
                    },
                    {
                        "name": "curveType",
                        "type": "str",
                        "description": "Curve type (polynomial, exponential, logarithmic, power)",
                        "required": True,
                    },
                    {
                        "name": "degree",
                        "type": "int",
                        "description": "Polynomial degree (if applicable)",
                        "required": False,
                        "default": 2,
                    },
                    {
                        "name": "includeStatistics",
                        "type": "bool",
                        "description": "Include fit statistics",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Curve fitting results with parameters and statistics",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Mathematical Operations",
                "patterns": [
                    "curve_fitting",
                    "data_modeling",
                    "trend_analysis",
                    "parameter_estimation",
                ],
            },
        ]
    )

    return functions


if __name__ == "__main__":
    functions = get_math_operations_functions()
    print(f"Mathematical Operations Functions: {len(functions)}")

    # Verify function structure
    for func in functions:
        assert "name" in func
        assert "description" in func
        assert "parameters" in func
        assert "returns" in func
        assert "scope" in func
        assert "category" in func
        assert "patterns" in func

    print("✅ All mathematical operations function definitions are valid!")
