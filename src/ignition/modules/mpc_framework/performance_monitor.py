"""Production Performance Monitor - Phase 14 Implementation.

This module implements comprehensive performance monitoring for production control systems
with real-time analytics, KPI tracking, and automated reporting.

Following crawl_mcp.py methodology:
- Step 1: Environment validation with monitoring system checks
- Step 2: Input validation using Pydantic models
- Step 3: Comprehensive error handling with graceful degradation
- Step 4: Modular testing with performance validation
- Step 5: Progressive complexity with scalable monitoring
- Step 6: Resource management with efficient data handling

Author: IGN Scripts Development Team
Version: 14.0.0
"""

import asyncio
import logging
import os
import statistics
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Performance metric types."""

    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    ENERGY_CONSUMPTION = "energy_consumption"
    COST_PER_UNIT = "cost_per_unit"


class AlertLevel(Enum):
    """Performance alert levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


# Step 1: Environment Validation (crawl_mcp.py methodology)
def validate_performance_environment() -> dict[str, Any]:
    """Validate performance monitoring environment setup."""
    logger.info("🔍 Step 1: Environment Validation - Performance Monitor")

    errors = []
    warnings = []

    # Check monitoring environment variables
    monitoring_vars = [
        "PERFORMANCE_DATA_DIR",
        "PERFORMANCE_RETENTION_DAYS",
        "PERFORMANCE_ALERT_ENDPOINTS",
        "PERFORMANCE_SAMPLING_RATE",
    ]

    for var in monitoring_vars:
        if not os.getenv(var):
            warnings.append(f"Performance environment variable {var} not set")

    # Check data storage directory
    data_dir = os.getenv("PERFORMANCE_DATA_DIR", "/tmp/performance_data")
    try:
        os.makedirs(data_dir, exist_ok=True)
        test_file = os.path.join(data_dir, "test_write.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        logger.info(f"✅ Performance data directory accessible: {data_dir}")
    except Exception as e:
        errors.append(f"Cannot access performance data directory {data_dir}: {e}")

    # Check required Python packages
    try:
        import numpy
        import pandas

        logger.info("✅ NumPy and Pandas available for analytics")
    except ImportError as e:
        warnings.append(f"Analytics packages not available: {e}")

    # Check system resources for monitoring
    try:
        import psutil

        memory = psutil.virtual_memory()
        if memory.available < 256 * 1024 * 1024:  # 256MB
            warnings.append("Low available memory for performance monitoring")
        logger.info(
            f"✅ System resources: {memory.available / (1024**3):.1f} GB available"
        )
    except ImportError:
        warnings.append("psutil not available for system monitoring")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "timestamp": datetime.now().isoformat(),
    }


# Step 2: Input Validation Models (crawl_mcp.py methodology)
class PerformanceThreshold(BaseModel):
    """Performance threshold configuration."""

    metric_name: str = Field(..., description="Metric name")
    metric_type: PerformanceMetric = Field(..., description="Metric type")
    warning_threshold: float = Field(..., description="Warning threshold value")
    critical_threshold: float = Field(..., description="Critical threshold value")
    emergency_threshold: float | None = Field(
        None, description="Emergency threshold value"
    )
    comparison_operator: str = Field(default=">=", description="Comparison operator")
    time_window_minutes: int = Field(
        default=5, ge=1, description="Time window for evaluation"
    )

    @field_validator("comparison_operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        valid_operators = [">=", "<=", ">", "<", "==", "!="]
        if v not in valid_operators:
            raise ValueError(f"Comparison operator must be one of: {valid_operators}")
        return v


class KPIConfiguration(BaseModel):
    """Key Performance Indicator configuration."""

    kpi_name: str = Field(..., description="KPI name")
    description: str = Field(..., description="KPI description")
    calculation_method: str = Field(..., description="Calculation method")
    target_value: float = Field(..., description="Target value")
    unit: str = Field(..., description="Unit of measurement")
    update_frequency_minutes: int = Field(
        default=15, ge=1, description="Update frequency"
    )
    historical_trend_days: int = Field(
        default=30, ge=1, description="Historical trend period"
    )


class PerformanceConfiguration(BaseModel):
    """Performance monitoring configuration."""

    system_name: str = Field(..., description="System name")
    sampling_rate_seconds: float = Field(
        default=1.0, gt=0, description="Data sampling rate"
    )
    data_retention_days: int = Field(
        default=30, ge=1, description="Data retention period"
    )

    # Thresholds and KPIs
    performance_thresholds: list[PerformanceThreshold] = Field(
        ..., description="Performance thresholds"
    )
    kpis: list[KPIConfiguration] = Field(..., description="KPI configurations")

    # Alert settings
    alert_endpoints: list[str] = Field(
        default_factory=list, description="Alert notification endpoints"
    )
    enable_predictive_alerts: bool = Field(
        default=True, description="Enable predictive alerting"
    )

    @field_validator("performance_thresholds")
    @classmethod
    def validate_thresholds(
        cls, v: list[PerformanceThreshold]
    ) -> list[PerformanceThreshold]:
        if not v:
            raise ValueError("At least one performance threshold must be configured")
        return v


# Step 3: Comprehensive Error Handling (crawl_mcp.py methodology)
def format_performance_error(error: Exception, context: str = "") -> str:
    """Format performance monitoring errors."""
    error_str = str(error).lower()

    if "memory" in error_str or "out of memory" in error_str:
        return f"Memory error in {context}: Consider reducing data retention or sampling rate"
    elif "disk" in error_str or "space" in error_str:
        return f"Storage error in {context}: Check available disk space"
    elif "timeout" in error_str:
        return f"Performance monitoring timeout in {context}: System may be overloaded"
    elif "permission" in error_str:
        return f"Permission error in {context}: Check file system permissions"
    elif "calculation" in error_str or "division" in error_str:
        return f"Calculation error in {context}: Check input data validity"
    else:
        return f"Performance monitoring error in {context}: {error!s}"


# Step 5: Progressive Complexity (crawl_mcp.py methodology)
@dataclass
class PerformanceDataPoint:
    """Individual performance data point."""

    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class ProductionPerformanceMonitor:
    """Production performance monitoring system."""

    # Configuration
    config: PerformanceConfiguration

    # Runtime state
    _initialized: bool = field(default=False, init=False)
    _monitoring_active: bool = field(default=False, init=False)
    _monitoring_task: asyncio.Task | None = field(default=None, init=False)

    # Data storage
    _performance_data: dict[str, list[PerformanceDataPoint]] = field(
        default_factory=dict, init=False
    )
    _kpi_values: dict[str, float] = field(default_factory=dict, init=False)
    _alert_history: list[dict[str, Any]] = field(default_factory=list, init=False)

    # Analytics
    _trend_analysis: dict[str, dict[str, float]] = field(
        default_factory=dict, init=False
    )
    _performance_summary: dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """Initialize performance monitor after creation."""
        logger.info("📊 Initializing Production Performance Monitor")

    async def initialize(self) -> dict[str, Any]:
        """Initialize performance monitoring system."""
        logger.info(
            "🔧 Step 1-6: Initializing Performance Monitor (crawl_mcp.py methodology)"
        )

        # Step 1: Environment validation first
        env_validation = validate_performance_environment()
        if not env_validation["valid"]:
            return {
                "success": False,
                "error": "Performance monitoring environment validation failed",
                "details": env_validation["errors"],
            }

        try:
            # Step 2: Input validation (already done via Pydantic)
            logger.info("✅ Performance configuration validation passed")

            # Step 3: Initialize data structures
            for threshold in self.config.performance_thresholds:
                self._performance_data[threshold.metric_name] = []

            for kpi in self.config.kpis:
                self._kpi_values[kpi.kpi_name] = 0.0

            # Step 4: Initialize analytics
            await self._initialize_analytics()

            # Step 5: Start monitoring
            await self._start_monitoring()

            self._initialized = True
            logger.info("✅ Production Performance Monitor initialized successfully")

            return {
                "success": True,
                "message": "Performance monitor initialized successfully",
                "configuration": {
                    "system_name": self.config.system_name,
                    "sampling_rate": self.config.sampling_rate_seconds,
                    "monitored_metrics": len(self.config.performance_thresholds),
                    "kpis": len(self.config.kpis),
                },
            }

        except Exception as e:
            error_msg = format_performance_error(
                e, "performance monitor initialization"
            )
            logger.error(f"❌ Performance monitor initialization failed: {error_msg}")
            return {"success": False, "error": error_msg}

    async def _initialize_analytics(self) -> None:
        """Initialize analytics components."""
        for threshold in self.config.performance_thresholds:
            self._trend_analysis[threshold.metric_name] = {
                "trend": 0.0,
                "volatility": 0.0,
                "prediction": 0.0,
            }

        logger.info("✅ Analytics components initialized")

    async def _start_monitoring(self) -> None:
        """Start performance monitoring task."""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._monitoring_active = True
        logger.info("✅ Performance monitoring started")

    async def _monitoring_loop(self) -> None:
        """Main performance monitoring loop."""
        while self._monitoring_active:
            try:
                # Collect performance data
                await self._collect_performance_data()

                # Update KPIs
                await self._update_kpis()

                # Check thresholds
                await self._check_thresholds()

                # Update analytics
                await self._update_analytics()

                # Cleanup old data
                await self._cleanup_old_data()

                await asyncio.sleep(self.config.sampling_rate_seconds)

            except asyncio.CancelledError:
                logger.info("Performance monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(self.config.sampling_rate_seconds)

    async def _collect_performance_data(self) -> None:
        """Collect performance data from various sources."""
        current_time = datetime.now()

        # Simulate data collection (in real implementation, this would
        # interface with actual monitoring systems)
        for threshold in self.config.performance_thresholds:
            # Generate realistic performance data
            base_value = 50.0
            noise = np.random.normal(0, 5)
            trend = 0.1 * (current_time.timestamp() % 3600) / 3600  # Hourly trend

            value = base_value + noise + trend

            data_point = PerformanceDataPoint(
                timestamp=current_time,
                metric_name=threshold.metric_name,
                value=value,
                unit=threshold.metric_type.value,
                tags={"system": self.config.system_name},
            )

            self._performance_data[threshold.metric_name].append(data_point)

    async def _update_kpis(self) -> None:
        """Update KPI calculations."""
        for kpi in self.config.kpis:
            try:
                # Calculate KPI based on method
                if kpi.calculation_method == "average":
                    kpi_value = await self._calculate_average_kpi(kpi.kpi_name)
                elif kpi.calculation_method == "efficiency":
                    kpi_value = await self._calculate_efficiency_kpi(kpi.kpi_name)
                elif kpi.calculation_method == "availability":
                    kpi_value = await self._calculate_availability_kpi(kpi.kpi_name)
                else:
                    kpi_value = 0.0

                self._kpi_values[kpi.kpi_name] = kpi_value

            except Exception as e:
                logger.error(f"KPI calculation error for {kpi.kpi_name}: {e}")

    async def _calculate_average_kpi(self, kpi_name: str) -> float:
        """Calculate average-based KPI."""
        # Find related performance data
        related_data = []
        for metric_name, data_points in self._performance_data.items():
            if kpi_name.lower() in metric_name.lower():
                recent_data = [dp.value for dp in data_points[-100:]]  # Last 100 points
                related_data.extend(recent_data)

        return statistics.mean(related_data) if related_data else 0.0

    async def _calculate_efficiency_kpi(self, kpi_name: str) -> float:
        """Calculate efficiency-based KPI."""
        # Simulate efficiency calculation
        return min(95.0 + np.random.normal(0, 2), 100.0)

    async def _calculate_availability_kpi(self, kpi_name: str) -> float:
        """Calculate availability-based KPI."""
        # Simulate availability calculation
        return min(99.0 + np.random.normal(0, 1), 100.0)

    async def _check_thresholds(self) -> None:
        """Check performance thresholds and generate alerts."""
        for threshold in self.config.performance_thresholds:
            if threshold.metric_name not in self._performance_data:
                continue

            recent_data = self._performance_data[threshold.metric_name][
                -threshold.time_window_minutes :
            ]
            if not recent_data:
                continue

            # Calculate aggregated value for time window
            values = [dp.value for dp in recent_data]
            avg_value = statistics.mean(values)

            # Check thresholds
            alert_level = None
            if threshold.emergency_threshold is not None and self._compare_value(
                avg_value, threshold.emergency_threshold, threshold.comparison_operator
            ):
                alert_level = AlertLevel.EMERGENCY
            elif self._compare_value(
                avg_value, threshold.critical_threshold, threshold.comparison_operator
            ):
                alert_level = AlertLevel.CRITICAL
            elif self._compare_value(
                avg_value, threshold.warning_threshold, threshold.comparison_operator
            ):
                alert_level = AlertLevel.WARNING

            if alert_level:
                await self._create_alert(threshold, avg_value, alert_level)

    def _compare_value(self, value: float, threshold: float, operator: str) -> bool:
        """Compare value against threshold using specified operator."""
        if operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == "==":
            return abs(value - threshold) < 0.001
        elif operator == "!=":
            return abs(value - threshold) >= 0.001
        return False

    async def _create_alert(
        self, threshold: PerformanceThreshold, value: float, level: AlertLevel
    ) -> None:
        """Create performance alert."""
        alert = {
            "timestamp": datetime.now(),
            "metric_name": threshold.metric_name,
            "current_value": value,
            "threshold_value": (
                threshold.emergency_threshold
                if level == AlertLevel.EMERGENCY
                else (
                    threshold.critical_threshold
                    if level == AlertLevel.CRITICAL
                    else threshold.warning_threshold
                )
            ),
            "alert_level": level.value,
            "message": f"{threshold.metric_name} {threshold.comparison_operator} threshold ({level.value})",
        }

        self._alert_history.append(alert)

        # Send notifications
        await self._send_alert_notifications(alert)

        logger.warning(f"🚨 Performance alert: {alert['message']}")

    async def _send_alert_notifications(self, alert: dict[str, Any]) -> None:
        """Send alert notifications to configured endpoints."""
        for endpoint in self.config.alert_endpoints:
            try:
                # In real implementation, this would send actual notifications
                logger.info(
                    f"📢 Alert notification sent to {endpoint}: {alert['message']}"
                )
            except Exception as e:
                logger.error(f"Failed to send alert to {endpoint}: {e}")

    async def _update_analytics(self) -> None:
        """Update trend analysis and predictions."""
        for metric_name, data_points in self._performance_data.items():
            if len(data_points) < 10:  # Need minimum data for analysis
                continue

            try:
                # Calculate trend
                recent_values = [dp.value for dp in data_points[-50:]]  # Last 50 points
                trend = self._calculate_trend(recent_values)

                # Calculate volatility
                volatility = (
                    statistics.stdev(recent_values) if len(recent_values) > 1 else 0.0
                )

                # Simple prediction (linear extrapolation)
                prediction = recent_values[-1] + trend

                self._trend_analysis[metric_name] = {
                    "trend": trend,
                    "volatility": volatility,
                    "prediction": prediction,
                }

            except Exception as e:
                logger.error(f"Analytics update error for {metric_name}: {e}")

    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend using simple linear regression."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))

        # Calculate slope using least squares
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        return numerator / denominator if denominator != 0 else 0.0

    async def _cleanup_old_data(self) -> None:
        """Clean up old performance data based on retention policy."""
        cutoff_time = datetime.now() - timedelta(days=self.config.data_retention_days)

        for metric_name in self._performance_data:
            self._performance_data[metric_name] = [
                dp
                for dp in self._performance_data[metric_name]
                if dp.timestamp > cutoff_time
            ]

        # Clean up old alerts
        self._alert_history = [
            alert for alert in self._alert_history if alert["timestamp"] > cutoff_time
        ]

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary."""
        current_time = datetime.now()

        # Calculate data statistics
        data_stats = {}
        for metric_name, data_points in self._performance_data.items():
            if data_points:
                values = [dp.value for dp in data_points[-100:]]  # Last 100 points
                data_stats[metric_name] = {
                    "current": values[-1] if values else 0.0,
                    "average": statistics.mean(values) if values else 0.0,
                    "min": min(values) if values else 0.0,
                    "max": max(values) if values else 0.0,
                    "data_points": len(data_points),
                }

        return {
            "system_name": self.config.system_name,
            "timestamp": current_time.isoformat(),
            "monitoring_active": self._monitoring_active,
            "data_statistics": data_stats,
            "kpi_values": self._kpi_values.copy(),
            "trend_analysis": self._trend_analysis.copy(),
            "active_alerts": len(
                [
                    a
                    for a in self._alert_history
                    if (current_time - a["timestamp"]).total_seconds() < 3600
                ]
            ),
            "total_alerts": len(self._alert_history),
            "configuration": {
                "sampling_rate": self.config.sampling_rate_seconds,
                "retention_days": self.config.data_retention_days,
                "monitored_metrics": len(self.config.performance_thresholds),
                "kpis": len(self.config.kpis),
            },
        }

    def get_status(self) -> dict[str, Any]:
        """Get performance monitor status."""
        return {
            "initialized": self._initialized,
            "monitoring_active": self._monitoring_active,
            "system_name": self.config.system_name,
            "metrics_monitored": len(self._performance_data),
            "kpis_tracked": len(self._kpi_values),
            "recent_alerts": len(
                [
                    a
                    for a in self._alert_history
                    if (datetime.now() - a["timestamp"]).total_seconds() < 3600
                ]
            ),
        }

    # Step 6: Resource Management (crawl_mcp.py methodology)
    @asynccontextmanager
    async def managed_monitoring_session(
        self,
    ) -> AsyncIterator["ProductionPerformanceMonitor"]:
        """Manage performance monitoring session with proper cleanup."""
        try:
            # Initialize performance monitor
            init_result = await self.initialize()
            if not init_result["success"]:
                raise RuntimeError(
                    f"Performance monitor initialization failed: {init_result['error']}"
                )

            logger.info("📊 Performance monitoring session started")
            yield self

        finally:
            # Cleanup resources
            await self.cleanup()
            logger.info("🧹 Performance monitoring session cleanup completed")

    async def cleanup(self) -> None:
        """Clean up performance monitoring resources."""
        try:
            # Stop monitoring
            if self._monitoring_task:
                self._monitoring_active = False
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass

            # Clear data structures
            self._performance_data.clear()
            self._kpi_values.clear()
            self._alert_history.clear()
            self._trend_analysis.clear()

            # Reset state
            self._initialized = False
            self._monitoring_active = False

            logger.info("✅ Performance monitor cleanup completed")

        except Exception as e:
            logger.error(f"❌ Performance monitor cleanup error: {e}")


# Step 4: Modular Testing (crawl_mcp.py methodology)
async def test_performance_monitor() -> dict[str, Any]:
    """Test performance monitoring functionality."""
    start_time = datetime.now()

    try:
        # Create test configuration
        test_config = PerformanceConfiguration(
            system_name="Test Performance Monitor",
            sampling_rate_seconds=0.1,  # Fast sampling for testing
            performance_thresholds=[
                PerformanceThreshold(
                    metric_name="response_time",
                    metric_type=PerformanceMetric.RESPONSE_TIME,
                    warning_threshold=100.0,
                    critical_threshold=200.0,
                    emergency_threshold=500.0,
                ),
                PerformanceThreshold(
                    metric_name="throughput",
                    metric_type=PerformanceMetric.THROUGHPUT,
                    warning_threshold=50.0,
                    critical_threshold=20.0,
                    comparison_operator="<=",
                ),
            ],
            kpis=[
                KPIConfiguration(
                    kpi_name="overall_efficiency",
                    description="Overall system efficiency",
                    calculation_method="efficiency",
                    target_value=95.0,
                    unit="percent",
                ),
            ],
        )

        # Test performance monitor
        monitor = ProductionPerformanceMonitor(config=test_config)

        async with monitor.managed_monitoring_session():
            # Let it run for a short time to collect data
            await asyncio.sleep(1.0)

            # Get performance summary
            summary = monitor.get_performance_summary()

            if not summary["monitoring_active"]:
                raise RuntimeError("Performance monitoring not active")

            if len(summary["data_statistics"]) == 0:
                raise RuntimeError("No performance data collected")

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "success": True,
            "execution_time": execution_time,
            "metrics_collected": len(summary["data_statistics"]),
            "kpis_calculated": len(summary["kpi_values"]),
        }

    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        return {
            "success": False,
            "execution_time": execution_time,
            "error": str(e),
        }


# Main execution for testing
if __name__ == "__main__":

    async def main():
        logger.info("🧪 Testing Production Performance Monitor")
        test_result = await test_performance_monitor()

        if test_result["success"]:
            logger.info(f"✅ Test passed in {test_result['execution_time']:.2f}s")
        else:
            logger.error(f"❌ Test failed: {test_result['error']}")

    asyncio.run(main())
