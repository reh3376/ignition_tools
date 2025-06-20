"""Task 11: Advanced Math & Analytics Functions.

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

REFACTORED: This module has been refactored for better maintainability.
Functions are now organized in separate modules:
- task_11_math_operations.py (10 functions)
- task_11_statistical_analysis.py (10 functions)
- task_11_data_analytics.py (10 functions)
"""

from typing import Any

from .task_11_data_analytics import get_data_analytics_functions

# Import from extracted modules
from .task_11_math_operations import get_math_operations_functions
from .task_11_statistical_analysis import get_statistical_analysis_functions


def get_math_analytics_functions() -> list[dict[str, Any]]:
    """Get comprehensive math and analytics functions for Task 11.

    Returns:
        list[dict[str, Any]]: list of math and analytics function definitions
    """
    functions = []

    # Import functions from extracted modules
    functions.extend(get_math_operations_functions())
    functions.extend(get_statistical_analysis_functions())
    functions.extend(get_data_analytics_functions())

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
        "refactoring_info": {
            "refactored": True,
            "refactoring_date": "2024",
            "extracted_modules": [
                "task_11_math_operations.py",
                "task_11_statistical_analysis.py",
                "task_11_data_analytics.py",
            ],
            "functions_per_module": {
                "math_operations": 10,
                "statistical_analysis": 10,
                "data_analytics": 10,
            },
        },
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
    print(
        f"✅ Refactored into {len(metadata['refactoring_info']['extracted_modules'])} modules"
    )
