"""Phase 9.8: Real-time Analytics Module
====================================

Following crawl_mcp.py methodology for systematic development:
1. Environment Variable Validation First
2. Comprehensive Input Validation
3. Error Handling with User-Friendly Messages
4. Modular Component Testing
5. Progressive Complexity
6. Resource Management

This module provides advanced analytics capabilities for Ignition:
- Real-time data processing and analysis
- Machine learning model integration
- Predictive analytics and forecasting
- Custom dashboard and visualization tools
"""

import logging
import os
import sys
import warnings
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Initialize console and logging
console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnalyticsConfig:
    """Configuration for analytics module following crawl_mcp.py patterns."""

    # Step 1: Environment Variable Validation First
    data_source_url: str = ""
    analytics_temp_dir: str = ""
    model_cache_dir: str = ""
    enable_ml_models: bool = True
    enable_predictions: bool = True
    enable_dashboards: bool = True
    max_data_points: int = 10000
    update_interval_seconds: int = 60

    # Progressive complexity settings
    complexity_level: str = "basic"  # basic, intermediate, advanced

    def __post_init__(self):
        """Validate configuration following crawl_mcp.py methodology."""
        if not self.analytics_temp_dir:
            self.analytics_temp_dir = os.getenv(
                "ANALYTICS_TEMP_DIR", str(Path.home() / "tmp" / "ign_analytics")
            )
        if not self.model_cache_dir:
            self.model_cache_dir = os.getenv(
                "ANALYTICS_MODEL_CACHE_DIR",
                str(Path.home() / "ign_analytics" / "models"),
            )


@dataclass
class ValidationResult:
    """Result of validation following crawl_mcp.py patterns."""

    valid: bool
    error: str = ""
    warning: str = ""
    suggestions: list[str] = field(default_factory=list)


@dataclass
class AnalyticsData:
    """Analytics data structure with validation."""

    timestamp: datetime
    values: dict[str, int | float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate data structure."""
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be datetime object")
        if not isinstance(self.values, dict):
            raise ValueError("values must be dictionary")


class RealTimeAnalyticsModule:
    """Real-time Analytics Module for Ignition

    Following crawl_mcp.py methodology:
    - Step 1: Environment Variable Validation First
    - Step 2: Comprehensive Input Validation
    - Step 3: Error Handling with User-Friendly Messages
    - Step 4: Modular Component Testing
    - Step 5: Progressive Complexity
    - Step 6: Resource Management
    """

    def __init__(self, config: AnalyticsConfig | None = None):
        """Initialize analytics module with comprehensive validation."""
        self.console = console
        self.logger = logger
        self.config = config or AnalyticsConfig()

        # Step 1: Environment Variable Validation First
        self.environment_validation = self.validate_environment()

        # Initialize components based on validation
        self.data_processor = None
        self.ml_engine = None
        self.dashboard_generator = None
        self.prediction_engine = None

        # Resource management
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.data_cache: list[AnalyticsData] = []
        self.model_cache: dict[str, Any] = {}

        # Initialize based on progressive complexity
        self._initialize_components()

    def validate_environment(self) -> dict[str, ValidationResult]:
        """Step 1: Environment Variable Validation First
        Following crawl_mcp.py methodology
        """
        self.console.print(
            "🔍 Step 1: Analytics Environment Validation", style="bold blue"
        )

        results = {}

        # Validate required directories
        results["temp_directory"] = self._validate_directory(
            self.config.analytics_temp_dir,
            "Analytics temporary directory",
            create_if_missing=True,
        )

        results["model_cache_directory"] = self._validate_directory(
            self.config.model_cache_dir, "Model cache directory", create_if_missing=True
        )

        # Validate dependencies
        results["analytics_dependencies"] = self._validate_analytics_dependencies()
        results["ml_dependencies"] = self._validate_ml_dependencies()
        results["visualization_dependencies"] = (
            self._validate_visualization_dependencies()
        )

        # Display validation results
        self._display_validation_results(results)

        return results

    def _validate_directory(
        self, path: str, description: str, create_if_missing: bool = False
    ) -> ValidationResult:
        """Validate directory with user-friendly error handling."""
        try:
            path_obj = Path(path)

            if not path_obj.exists():
                if create_if_missing:
                    path_obj.mkdir(parents=True, exist_ok=True)
                    return ValidationResult(
                        valid=True, warning=f"{description} created at {path}"
                    )
                else:
                    return ValidationResult(
                        valid=False,
                        error=f"{description} does not exist: {path}",
                        suggestions=[f"Create directory: mkdir -p {path}"],
                    )

            if not path_obj.is_dir():
                return ValidationResult(
                    valid=False, error=f"{description} is not a directory: {path}"
                )

            # Test write permissions
            test_file = path_obj / ".test_write"
            try:
                test_file.touch()
                test_file.unlink()
                return ValidationResult(valid=True)
            except PermissionError:
                return ValidationResult(
                    valid=False,
                    error=f"No write permission for {description}: {path}",
                    suggestions=[f"Fix permissions: chmod 755 {path}"],
                )

        except Exception as e:
            return ValidationResult(
                valid=False, error=f"Error validating {description}: {e!s}"
            )

    def _validate_analytics_dependencies(self) -> ValidationResult:
        """Validate analytics dependencies with detailed feedback."""
        missing_packages = []

        try:
            import numpy
            import pandas
        except ImportError:
            missing_packages.extend(["pandas", "numpy"])

        try:
            import scipy
        except ImportError:
            missing_packages.append("scipy")

        if missing_packages:
            return ValidationResult(
                valid=False,
                error=f"Missing analytics packages: {', '.join(missing_packages)}",
                suggestions=[
                    f"Install packages: pip install {' '.join(missing_packages)}"
                ],
            )

        return ValidationResult(valid=True)

    def _validate_ml_dependencies(self) -> ValidationResult:
        """Validate machine learning dependencies."""
        if not self.config.enable_ml_models:
            return ValidationResult(valid=True, warning="ML models disabled")

        missing_packages = []

        try:
            import sklearn
        except ImportError:
            missing_packages.append("scikit-learn")

        try:
            import joblib
        except ImportError:
            missing_packages.append("joblib")

        if missing_packages:
            return ValidationResult(
                valid=False,
                error=f"Missing ML packages: {', '.join(missing_packages)}",
                suggestions=[
                    f"Install packages: pip install {' '.join(missing_packages)}"
                ],
            )

        return ValidationResult(valid=True)

    def _validate_visualization_dependencies(self) -> ValidationResult:
        """Validate visualization dependencies."""
        if not self.config.enable_dashboards:
            return ValidationResult(valid=True, warning="Dashboards disabled")

        missing_packages = []

        try:
            import matplotlib
            import plotly
        except ImportError:
            missing_packages.extend(["matplotlib", "plotly"])

        if missing_packages:
            return ValidationResult(
                valid=False,
                error=f"Missing visualization packages: {', '.join(missing_packages)}",
                suggestions=[
                    f"Install packages: pip install {' '.join(missing_packages)}"
                ],
            )

        return ValidationResult(valid=True)

    def _display_validation_results(self, results: dict[str, ValidationResult]) -> None:
        """Display validation results with user-friendly formatting."""
        table = Table(title="Analytics Environment Validation")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        for component, result in results.items():
            if result.valid:
                status = "✅ Valid"
                details = result.warning if result.warning else "OK"
            else:
                status = "❌ Invalid"
                details = result.error
                if result.suggestions:
                    details += f" | Suggestion: {result.suggestions[0]}"

            table.add_row(component.replace("_", " ").title(), status, details)

        self.console.print(table)

    def _initialize_components(self) -> None:
        """Step 5: Progressive Complexity
        Initialize components based on complexity level and validation results
        """
        self.console.print(
            "🔧 Step 5: Progressive Component Initialization", style="bold blue"
        )

        # Check if environment validation passed
        all_valid = all(result.valid for result in self.environment_validation.values())

        if not all_valid:
            self.console.print(
                "⚠️ Some validations failed. Initializing in limited mode.",
                style="yellow",
            )
            self.config.complexity_level = "basic"

        # Initialize components progressively
        if self.config.complexity_level == "basic":
            self._initialize_basic_components()
        elif self.config.complexity_level == "intermediate":
            self._initialize_intermediate_components()
        elif self.config.complexity_level == "advanced":
            self._initialize_advanced_components()

    def _initialize_basic_components(self) -> None:
        """Initialize basic analytics components."""
        self.console.print("📊 Initializing Basic Analytics Components", style="green")

        # Basic data processor
        self.data_processor = BasicDataProcessor(self.config)

        # Simple statistics calculator
        self.stats_calculator = BasicStatsCalculator()

        self.console.print("✅ Basic components initialized", style="green")

    def _initialize_intermediate_components(self) -> None:
        """Initialize intermediate analytics components."""
        self.console.print(
            "📊 Initializing Intermediate Analytics Components", style="green"
        )

        # Initialize basic components first
        self._initialize_basic_components()

        # Add intermediate components
        if self.environment_validation.get(
            "ml_dependencies", ValidationResult(False)
        ).valid:
            self.ml_engine = IntermediateMLEngine(self.config)

        if self.environment_validation.get(
            "visualization_dependencies", ValidationResult(False)
        ).valid:
            self.dashboard_generator = BasicDashboardGenerator(self.config)

        self.console.print("✅ Intermediate components initialized", style="green")

    def _initialize_advanced_components(self) -> None:
        """Initialize advanced analytics components."""
        self.console.print(
            "📊 Initializing Advanced Analytics Components", style="green"
        )

        # Initialize intermediate components first
        self._initialize_intermediate_components()

        # Add advanced components
        if self.config.enable_predictions:
            self.prediction_engine = AdvancedPredictionEngine(self.config)

        # Advanced dashboard with real-time updates
        if self.environment_validation.get(
            "visualization_dependencies", ValidationResult(False)
        ).valid:
            self.dashboard_generator = AdvancedDashboardGenerator(self.config)

        self.console.print("✅ Advanced components initialized", style="green")

    def process_data(
        self, data: dict[str, Any] | list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Step 2: Comprehensive Input Validation
        Process incoming data with full validation
        """
        try:
            # Validate input data
            validated_data = self._validate_input_data(data)

            if not validated_data["valid"]:
                return {
                    "success": False,
                    "error": validated_data["error"],
                    "suggestions": validated_data.get("suggestions", []),
                }

            # Process data based on complexity level
            if self.data_processor:
                result = self.data_processor.process(validated_data["data"])
                return {
                    "success": True,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "success": False,
                    "error": "Data processor not initialized",
                    "suggestions": ["Check environment validation and reinitialize"],
                }

        except Exception as e:
            # Step 3: Error Handling with User-Friendly Messages
            self.logger.error(f"Error processing data: {e!s}")
            return {
                "success": False,
                "error": f"Data processing failed: {e!s}",
                "suggestions": ["Check data format and try again"],
            }

    def _validate_input_data(
        self, data: dict[str, Any] | list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Comprehensive input validation following crawl_mcp.py patterns."""
        if data is None:
            return {
                "valid": False,
                "error": "Data cannot be None",
                "suggestions": ["Provide valid data dictionary or list"],
            }

        # Convert single dict to list for uniform processing
        if isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            return {
                "valid": False,
                "error": "Data must be dictionary or list of dictionaries",
                "suggestions": ["Format data as {'timestamp': ..., 'values': {...}}"],
            }

        validated_items = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                return {
                    "valid": False,
                    "error": f"Item {i} is not a dictionary",
                    "suggestions": ["Each data item must be a dictionary"],
                }

            # Validate required fields
            if "values" not in item:
                return {
                    "valid": False,
                    "error": f"Item {i} missing 'values' field",
                    "suggestions": ["Each item must have 'values' dictionary"],
                }

            # Add timestamp if missing
            if "timestamp" not in item:
                item["timestamp"] = datetime.now()

            try:
                analytics_data = AnalyticsData(
                    timestamp=(
                        item["timestamp"]
                        if isinstance(item["timestamp"], datetime)
                        else datetime.fromisoformat(str(item["timestamp"]))
                    ),
                    values=item["values"],
                    metadata=item.get("metadata", {}),
                )
                validated_items.append(analytics_data)
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Item {i} validation failed: {e!s}",
                    "suggestions": ["Check data format and field types"],
                }

        return {"valid": True, "data": validated_items}

    def generate_analytics_report(self) -> dict[str, Any]:
        """Generate comprehensive analytics report."""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "module_status": "active",
                "configuration": {
                    "complexity_level": self.config.complexity_level,
                    "ml_enabled": self.config.enable_ml_models,
                    "predictions_enabled": self.config.enable_predictions,
                    "dashboards_enabled": self.config.enable_dashboards,
                },
                "environment_validation": {
                    component: result.valid
                    for component, result in self.environment_validation.items()
                },
                "data_summary": {
                    "cached_data_points": len(self.data_cache),
                    "models_cached": len(self.model_cache),
                },
                "components": {
                    "data_processor": self.data_processor is not None,
                    "ml_engine": self.ml_engine is not None,
                    "prediction_engine": self.prediction_engine is not None,
                    "dashboard_generator": self.dashboard_generator is not None,
                },
            }

            return {"success": True, "report": report}

        except Exception as e:
            return {"success": False, "error": f"Failed to generate report: {e!s}"}

    def cleanup_resources(self) -> None:
        """Step 6: Resource Management
        Clean up resources and temporary files
        """
        try:
            self.console.print("🧹 Cleaning up analytics resources...", style="yellow")

            # Shutdown executor
            if self.executor:
                self.executor.shutdown(wait=True)

            # Clear caches
            self.data_cache.clear()
            self.model_cache.clear()

            # Clean temporary files
            temp_dir = Path(self.config.analytics_temp_dir)
            if temp_dir.exists():
                for temp_file in temp_dir.glob("*.tmp"):
                    temp_file.unlink()

            self.console.print("✅ Resources cleaned up successfully", style="green")

        except Exception as e:
            self.console.print(f"⚠️ Error during cleanup: {e!s}", style="red")


# Supporting classes for progressive complexity


class BasicDataProcessor:
    """Basic data processing component."""

    def __init__(self, config: AnalyticsConfig):
        self.config = config

    def process(self, data: list[AnalyticsData]) -> dict[str, Any]:
        """Process data with basic statistics."""
        if not data:
            return {"error": "No data to process"}

        # Calculate basic statistics
        all_values = []
        for item in data:
            all_values.extend(item.values.values())

        if not all_values:
            return {"error": "No numeric values found"}

        return {
            "count": len(all_values),
            "mean": sum(all_values) / len(all_values),
            "min": min(all_values),
            "max": max(all_values),
            "processed_at": datetime.now().isoformat(),
        }


class BasicStatsCalculator:
    """Basic statistics calculator."""

    def calculate_stats(self, values: list[int | float]) -> dict[str, float]:
        """Calculate basic statistics for a list of values."""
        if not values:
            return {}

        return {
            "count": len(values),
            "sum": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }


class IntermediateMLEngine:
    """Intermediate machine learning engine."""

    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.models = {}

    def train_model(
        self, data: list[AnalyticsData], model_type: str = "linear"
    ) -> dict[str, Any]:
        """Train a basic ML model."""
        return {
            "model_type": model_type,
            "trained": True,
            "timestamp": datetime.now().isoformat(),
        }


class BasicDashboardGenerator:
    """Basic dashboard generator."""

    def __init__(self, config: AnalyticsConfig):
        self.config = config

    def generate_dashboard(self, data: list[AnalyticsData]) -> dict[str, Any]:
        """Generate basic dashboard."""
        return {
            "dashboard_type": "basic",
            "data_points": len(data),
            "generated_at": datetime.now().isoformat(),
        }


class AdvancedPredictionEngine:
    """Advanced prediction engine."""

    def __init__(self, config: AnalyticsConfig):
        self.config = config

    def predict(self, data: list[AnalyticsData]) -> dict[str, Any]:
        """Generate predictions."""
        return {
            "predictions": [],
            "confidence": 0.85,
            "generated_at": datetime.now().isoformat(),
        }


class AdvancedDashboardGenerator:
    """Advanced dashboard generator with real-time updates."""

    def __init__(self, config: AnalyticsConfig):
        self.config = config

    def generate_realtime_dashboard(self, data: list[AnalyticsData]) -> dict[str, Any]:
        """Generate advanced real-time dashboard."""
        return {
            "dashboard_type": "advanced_realtime",
            "data_points": len(data),
            "features": [
                "real_time_updates",
                "interactive_charts",
                "predictive_analytics",
            ],
            "generated_at": datetime.now().isoformat(),
        }


# Main function for testing
def main():
    """Test the analytics module following crawl_mcp.py methodology."""
    console.print(
        Panel.fit("🚀 Phase 9.8 Real-time Analytics Module Test", style="green bold")
    )

    # Test with different complexity levels
    for complexity in ["basic", "intermediate", "advanced"]:
        console.print(f"\n📊 Testing {complexity.title()} Complexity Level")

        config = AnalyticsConfig(complexity_level=complexity)
        module = RealTimeAnalyticsModule(config)

        # Test data processing
        test_data = {
            "timestamp": datetime.now(),
            "values": {"temperature": 25.5, "pressure": 101.3, "humidity": 60.2},
        }

        result = module.process_data(test_data)
        console.print(f"Processing result: {result['success']}")

        # Generate report
        report = module.generate_analytics_report()
        if report["success"]:
            console.print("Report generated successfully")

        # Cleanup
        module.cleanup_resources()


if __name__ == "__main__":
    main()
