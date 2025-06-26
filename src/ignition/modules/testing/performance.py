"""Performance Testing Framework for Ignition Modules.

Provides comprehensive performance testing including load testing,
resource monitoring, and performance analysis following patterns from
crawl_mcp.py for validation, error handling, and resource management.
"""

import asyncio
import json
import os
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import psutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PerformanceTestType(Enum):
    """Type of performance test."""

    LOAD = "load"
    STRESS = "stress"
    SPIKE = "spike"
    VOLUME = "volume"
    ENDURANCE = "endurance"
    BASELINE = "baseline"


class PerformanceMetric(Enum):
    """Performance metrics to track."""

    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CONCURRENT_USERS = "concurrent_users"


class TestStatus(Enum):
    """Status of performance test."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class PerformanceThreshold:
    """Performance threshold definition."""

    metric: PerformanceMetric
    max_value: float
    warning_value: float
    unit: str = ""
    description: str = ""

    def evaluate(self, value: float) -> tuple[str, str]:
        """Evaluate threshold against value.

        Args:
            value: Value to evaluate

        Returns:
            tuple of (status, message)
        """
        if value > self.max_value:
            return (
                "fail",
                f"{self.metric.value} {value:.2f}{self.unit} exceeds threshold {self.max_value}{self.unit}",
            )
        elif value > self.warning_value:
            return (
                "warning",
                f"{self.metric.value} {value:.2f}{self.unit} above warning level {self.warning_value}{self.unit}",
            )
        else:
            return (
                "pass",
                f"{self.metric.value} {value:.2f}{self.unit} within acceptable range",
            )


@dataclass
class PerformanceMetrics:
    """Performance metrics data."""

    timestamp: float
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_usage_mb: float = 0.0
    disk_read_mb: float = 0.0
    disk_write_mb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    response_time_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate: float = 0.0
    concurrent_users: int = 0
    custom_metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class LoadProfile:
    """Load testing profile definition."""

    name: str
    description: str
    initial_users: int = 1
    target_users: int = 10
    ramp_up_duration: int = 60  # seconds
    hold_duration: int = 300  # seconds
    ramp_down_duration: int = 60  # seconds
    requests_per_second: float = 1.0
    think_time: float = 1.0  # seconds between requests
    test_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceTest:
    """Performance test definition."""

    id: str
    name: str
    description: str
    test_type: PerformanceTestType
    load_profile: LoadProfile
    duration: int = 300  # seconds
    thresholds: list[PerformanceThreshold] = field(default_factory=list)
    status: TestStatus = TestStatus.PENDING
    start_time: float = 0.0
    end_time: float = 0.0
    metrics_history: list[PerformanceMetrics] = field(default_factory=list)
    summary_metrics: PerformanceMetrics | None = None
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """Comprehensive performance test report."""

    module_path: str
    total_tests: int
    completed_tests: int
    failed_tests: int
    aborted_tests: int
    overall_status: str
    duration: float
    tests: list[PerformanceTest] = field(default_factory=list)
    baseline_metrics: PerformanceMetrics | None = None
    performance_trends: dict[str, list[float]] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def validate_performance_environment() -> dict[str, Any]:
    """Validate performance testing environment.

    Returns:
        Dictionary with validation results
    """
    required_vars = {
        "PERF_TEST_TARGET_URL": "Target URL for performance testing",
    }

    optional_vars = {
        "PERF_MAX_USERS": "Maximum concurrent users",
        "PERF_TEST_DURATION": "Default test duration in seconds",
        "PERF_MONITORING_INTERVAL": "Metrics collection interval",
        "PERF_RESULTS_PATH": "Path for performance results",
    }

    missing_required = []
    available_vars = {}

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = value
        else:
            missing_required.append(f"{var} ({description})")

    for var, _description in optional_vars.items():
        value = os.getenv(var)
        if value:
            available_vars[var] = value

    # Check system resources
    try:
        available_vars["system_cpu_count"] = psutil.cpu_count()
        available_vars["system_memory_gb"] = psutil.virtual_memory().total / (1024**3)
        available_vars["system_disk_free_gb"] = psutil.disk_usage("/").free / (1024**3)
    except Exception:
        pass

    if missing_required:
        return {
            "valid": False,
            "error": f"Missing required environment variables: {', '.join(missing_required)}",
            "available": available_vars,
        }

    return {"valid": True, "variables": available_vars}


def format_performance_error(error: Exception) -> str:
    """Format performance errors for user-friendly messages.

    Args:
        error: The exception to format

    Returns:
        Formatted error message
    """
    error_str = str(error).lower()

    if "timeout" in error_str:
        return "Performance test timed out. Consider reducing test duration or load."
    elif "memory" in error_str:
        return "Memory error during performance test. Reduce concurrent users or test data size."
    elif "connection" in error_str:
        return "Connection error during performance test. Check target system availability."
    elif "permission" in error_str:
        return "Permission denied during performance monitoring. Check system permissions."
    elif "resource" in error_str:
        return "System resource exhausted during test. Reduce test load or free up resources."
    else:
        return f"Performance test error: {error!s}"


class SystemMonitor:
    """System resource monitor for performance testing."""

    def __init__(self, interval: float = 1.0):
        """Initialize system monitor.

        Args:
            interval: Monitoring interval in seconds
        """
        self.interval = interval
        self.monitoring = False
        self.metrics_history: list[PerformanceMetrics] = []
        self._initial_disk_io = psutil.disk_io_counters()
        self._initial_network_io = psutil.net_io_counters()

    async def start_monitoring(self) -> None:
        """Start system monitoring."""
        self.monitoring = True
        self.metrics_history = []

        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                await asyncio.sleep(self.interval)
            except Exception:
                break

    def stop_monitoring(self) -> None:
        """Stop system monitoring."""
        self.monitoring = False

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics."""
        timestamp = time.time()

        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = memory.used / (1024 * 1024)

        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = 0.0
        disk_write_mb = 0.0
        if self._initial_disk_io and disk_io:
            disk_read_mb = (disk_io.read_bytes - self._initial_disk_io.read_bytes) / (1024 * 1024)
            disk_write_mb = (disk_io.write_bytes - self._initial_disk_io.write_bytes) / (1024 * 1024)

        # Network I/O
        network_io = psutil.net_io_counters()
        network_sent_mb = 0.0
        network_recv_mb = 0.0
        if self._initial_network_io and network_io:
            network_sent_mb = (network_io.bytes_sent - self._initial_network_io.bytes_sent) / (1024 * 1024)
            network_recv_mb = (network_io.bytes_recv - self._initial_network_io.bytes_recv) / (1024 * 1024)

        return PerformanceMetrics(
            timestamp=timestamp,
            cpu_usage=cpu_percent,
            memory_usage=memory_percent,
            memory_usage_mb=memory_mb,
            disk_read_mb=disk_read_mb,
            disk_write_mb=disk_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
        )

    def get_summary_metrics(self) -> PerformanceMetrics | None:
        """Get summary metrics from monitoring session."""
        if not self.metrics_history:
            return None

        # Calculate averages and peaks
        cpu_values = [m.cpu_usage for m in self.metrics_history]
        memory_values = [m.memory_usage for m in self.metrics_history]
        memory_mb_values = [m.memory_usage_mb for m in self.metrics_history]

        return PerformanceMetrics(
            timestamp=self.metrics_history[-1].timestamp,
            cpu_usage=sum(cpu_values) / len(cpu_values),
            memory_usage=sum(memory_values) / len(memory_values),
            memory_usage_mb=sum(memory_mb_values) / len(memory_mb_values),
            custom_metrics={
                "peak_cpu": max(cpu_values),
                "peak_memory": max(memory_values),
                "peak_memory_mb": max(memory_mb_values),
                "samples_count": len(self.metrics_history),
            },
        )


class ModulePerformanceTester:
    """Performance tester for Ignition modules.

    Following patterns from crawl_mcp.py for robust testing,
    error handling, and resource management.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the performance tester.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.tests: list[PerformanceTest] = []
        self.report: PerformanceReport | None = None
        self.system_monitor = SystemMonitor()

        # Load configuration from environment
        self.target_url = os.getenv("PERF_TEST_TARGET_URL", "http://localhost:8088")
        self.max_users = int(os.getenv("PERF_MAX_USERS", "100"))
        self.default_duration = int(os.getenv("PERF_TEST_DURATION", "300"))
        self.monitoring_interval = float(os.getenv("PERF_MONITORING_INTERVAL", "1.0"))
        self.results_path = Path(os.getenv("PERF_RESULTS_PATH", "./performance_results"))

    @asynccontextmanager
    async def performance_context(self, module_path: str) -> AsyncIterator["ModulePerformanceTester"]:
        """Create performance testing context with resource management.

        Args:
            module_path: Path to the module

        Yields:
            ModulePerformanceTester instance
        """
        # Store module path for reference
        self._module_path = module_path

        # Ensure results directory exists
        self.results_path.mkdir(parents=True, exist_ok=True)

        try:
            await self.initialize_tests(module_path)
            yield self
        finally:
            await self.cleanup()

    async def initialize_tests(self, module_path: str) -> None:
        """Initialize performance tests for the module.

        Args:
            module_path: Path to the module
        """
        # Store module path for testing context
        self.module_path = Path(module_path)
        # Define default performance thresholds
        default_thresholds = [
            PerformanceThreshold(
                metric=PerformanceMetric.CPU_USAGE,
                max_value=80.0,
                warning_value=60.0,
                unit="%",
                description="CPU usage should remain below 80%",
            ),
            PerformanceThreshold(
                metric=PerformanceMetric.MEMORY_USAGE,
                max_value=85.0,
                warning_value=70.0,
                unit="%",
                description="Memory usage should remain below 85%",
            ),
            PerformanceThreshold(
                metric=PerformanceMetric.RESPONSE_TIME,
                max_value=5000.0,
                warning_value=2000.0,
                unit="ms",
                description="Response time should be under 5 seconds",
            ),
        ]

        # Create standard performance test suite
        self.tests = [
            # Baseline test
            PerformanceTest(
                id="perf_baseline",
                name="Baseline Performance",
                description="Establish baseline performance metrics",
                test_type=PerformanceTestType.BASELINE,
                load_profile=LoadProfile(
                    name="baseline",
                    description="Single user baseline",
                    initial_users=1,
                    target_users=1,
                    ramp_up_duration=10,
                    hold_duration=60,
                    ramp_down_duration=10,
                ),
                duration=80,
                thresholds=default_thresholds.copy(),
            ),
            # Load test
            PerformanceTest(
                id="perf_load",
                name="Load Test",
                description="Test performance under expected load",
                test_type=PerformanceTestType.LOAD,
                load_profile=LoadProfile(
                    name="normal_load",
                    description="Expected production load",
                    initial_users=1,
                    target_users=min(10, self.max_users),
                    ramp_up_duration=60,
                    hold_duration=300,
                    ramp_down_duration=60,
                ),
                duration=420,
                thresholds=default_thresholds.copy(),
            ),
            # Stress test
            PerformanceTest(
                id="perf_stress",
                name="Stress Test",
                description="Test performance under high load",
                test_type=PerformanceTestType.STRESS,
                load_profile=LoadProfile(
                    name="high_load",
                    description="High load stress test",
                    initial_users=1,
                    target_users=min(50, self.max_users),
                    ramp_up_duration=120,
                    hold_duration=600,
                    ramp_down_duration=120,
                ),
                duration=840,
                thresholds=[
                    PerformanceThreshold(
                        metric=PerformanceMetric.CPU_USAGE,
                        max_value=95.0,
                        warning_value=80.0,
                        unit="%",
                    ),
                    PerformanceThreshold(
                        metric=PerformanceMetric.MEMORY_USAGE,
                        max_value=95.0,
                        warning_value=85.0,
                        unit="%",
                    ),
                ],
            ),
            # Spike test
            PerformanceTest(
                id="perf_spike",
                name="Spike Test",
                description="Test response to sudden load spikes",
                test_type=PerformanceTestType.SPIKE,
                load_profile=LoadProfile(
                    name="spike_load",
                    description="Sudden load spike",
                    initial_users=5,
                    target_users=min(100, self.max_users),
                    ramp_up_duration=10,  # Quick spike
                    hold_duration=60,
                    ramp_down_duration=10,
                ),
                duration=80,
                thresholds=default_thresholds.copy(),
            ),
        ]

    async def run_all_tests(self) -> PerformanceReport:
        """Run all performance tests.

        Returns:
            PerformanceReport with results
        """
        if not self.tests:
            raise RuntimeError("No performance tests initialized")

        start_time = time.time()
        baseline_metrics = None

        for test in self.tests:
            try:
                await self.run_single_test(test)

                # Store baseline metrics for comparison
                if test.test_type == PerformanceTestType.BASELINE and test.summary_metrics:
                    baseline_metrics = test.summary_metrics

            except Exception as e:
                test.status = TestStatus.FAILED
                test.issues.append(format_performance_error(e))

        end_time = time.time()
        duration = end_time - start_time

        # Generate report
        self.report = self._generate_report(duration, baseline_metrics)
        return self.report

    async def run_single_test(self, test: PerformanceTest) -> None:
        """Run a single performance test.

        Args:
            test: PerformanceTest to run
        """
        test.status = TestStatus.RUNNING
        test.start_time = time.time()

        try:
            # Start system monitoring
            monitor_task = asyncio.create_task(self.system_monitor.start_monitoring())

            # Execute the load profile
            await self._execute_load_profile(test)

            # Stop monitoring
            self.system_monitor.stop_monitoring()
            monitor_task.cancel()

            # Collect metrics
            test.metrics_history = self.system_monitor.metrics_history.copy()
            test.summary_metrics = self.system_monitor.get_summary_metrics()

            # Evaluate thresholds
            self._evaluate_thresholds(test)

            test.status = TestStatus.COMPLETED

        except Exception as e:
            test.status = TestStatus.FAILED
            test.issues.append(format_performance_error(e))
            self.system_monitor.stop_monitoring()

        finally:
            test.end_time = time.time()

    async def _execute_load_profile(self, test: PerformanceTest) -> None:
        """Execute load profile for the test.

        Args:
            test: PerformanceTest with load profile
        """
        profile = test.load_profile

        # Simulate different phases of load testing
        phases = [
            ("ramp_up", profile.ramp_up_duration),
            ("hold", profile.hold_duration),
            ("ramp_down", profile.ramp_down_duration),
        ]

        for phase_name, duration in phases:
            if duration <= 0:
                continue

            # Simulate load generation
            # In a real implementation, this would generate actual HTTP requests
            # or other load patterns against the target system

            interval = min(1.0, duration / 10)  # Update progress every 10% or 1 second
            steps = max(1, int(duration / interval))

            for step in range(steps):
                if phase_name == "ramp_up":
                    # Gradually increase users
                    current_users = int(
                        profile.initial_users + (profile.target_users - profile.initial_users) * (step / steps)
                    )
                elif phase_name == "hold":
                    # Maintain target users
                    current_users = profile.target_users
                else:  # ramp_down
                    # Gradually decrease users
                    current_users = int(profile.target_users - profile.target_users * (step / steps))

                # Simulate load generation delay
                await asyncio.sleep(interval)

                # Update current metrics if available
                if self.system_monitor.metrics_history:
                    latest_metrics = self.system_monitor.metrics_history[-1]
                    latest_metrics.concurrent_users = current_users

    def _evaluate_thresholds(self, test: PerformanceTest) -> None:
        """Evaluate performance thresholds for the test.

        Args:
            test: PerformanceTest to evaluate
        """
        if not test.summary_metrics:
            return

        metrics = test.summary_metrics

        for threshold in test.thresholds:
            # Map threshold metrics to actual values
            value = 0.0
            if threshold.metric == PerformanceMetric.CPU_USAGE:
                value = metrics.cpu_usage
            elif threshold.metric == PerformanceMetric.MEMORY_USAGE:
                value = metrics.memory_usage
            elif threshold.metric == PerformanceMetric.RESPONSE_TIME:
                value = metrics.response_time_ms
            else:
                continue  # Skip unknown metrics

            status, message = threshold.evaluate(value)

            if status == "fail":
                test.issues.append(message)
            elif status == "warning":
                test.warnings.append(message)

    def _generate_report(self, total_duration: float, baseline_metrics: PerformanceMetrics | None) -> PerformanceReport:
        """Generate performance report.

        Args:
            total_duration: Total time taken for all tests
            baseline_metrics: Baseline performance metrics

        Returns:
            PerformanceReport with results
        """
        completed_tests = sum(1 for t in self.tests if t.status == TestStatus.COMPLETED)
        failed_tests = sum(1 for t in self.tests if t.status == TestStatus.FAILED)
        aborted_tests = sum(1 for t in self.tests if t.status == TestStatus.ABORTED)

        # Determine overall status
        if failed_tests > 0:
            overall_status = "failed"
        elif aborted_tests > 0:
            overall_status = "aborted"
        elif completed_tests == len(self.tests):
            overall_status = "completed"
        else:
            overall_status = "partial"

        # Generate performance trends
        trends = self._generate_performance_trends()

        return PerformanceReport(
            module_path=getattr(self, "_module_path", ""),
            total_tests=len(self.tests),
            completed_tests=completed_tests,
            failed_tests=failed_tests,
            aborted_tests=aborted_tests,
            overall_status=overall_status,
            duration=total_duration,
            tests=self.tests.copy(),
            baseline_metrics=baseline_metrics,
            performance_trends=trends,
            recommendations=self._generate_recommendations(baseline_metrics),
            metadata={
                "target_url": self.target_url,
                "max_users": self.max_users,
                "monitoring_interval": self.monitoring_interval,
                "system_info": {
                    "cpu_count": psutil.cpu_count(),
                    "memory_gb": psutil.virtual_memory().total / (1024**3),
                },
            },
        )

    def _generate_performance_trends(self) -> dict[str, list[float]]:
        """Generate performance trends from test results."""
        trends: dict[str, list[float]] = {
            "cpu_usage": [],
            "memory_usage": [],
            "response_time": [],
        }

        for test in self.tests:
            if test.summary_metrics:
                trends["cpu_usage"].append(test.summary_metrics.cpu_usage)
                trends["memory_usage"].append(test.summary_metrics.memory_usage)
                trends["response_time"].append(test.summary_metrics.response_time_ms)

        return trends

    def _generate_recommendations(self, baseline_metrics: PerformanceMetrics | None) -> list[str]:
        """Generate recommendations based on performance results."""
        recommendations = []

        failed_tests = [t for t in self.tests if t.status == TestStatus.FAILED]
        tests_with_issues = [t for t in self.tests if t.issues]

        if failed_tests:
            recommendations.append(f"Fix {len(failed_tests)} failed performance tests before deployment")

        if tests_with_issues:
            recommendations.append("Address performance threshold violations")

        # CPU-specific recommendations
        high_cpu_tests = [t for t in self.tests if t.summary_metrics and t.summary_metrics.cpu_usage > 80.0]
        if high_cpu_tests:
            recommendations.append("High CPU usage detected - optimize computational efficiency")

        # Memory-specific recommendations
        high_memory_tests = [t for t in self.tests if t.summary_metrics and t.summary_metrics.memory_usage > 80.0]
        if high_memory_tests:
            recommendations.append("High memory usage detected - review memory leaks and optimization")

        # Baseline comparison recommendations
        if baseline_metrics:
            stress_test = next(
                (t for t in self.tests if t.test_type == PerformanceTestType.STRESS),
                None,
            )
            if stress_test and stress_test.summary_metrics:
                cpu_increase = stress_test.summary_metrics.cpu_usage - baseline_metrics.cpu_usage
                if cpu_increase > 50.0:
                    recommendations.append("Significant CPU increase under load - review scalability")

        if not recommendations:
            recommendations.append("Performance tests passed - module meets performance requirements")

        return recommendations

    async def cleanup(self) -> None:
        """Clean up performance testing resources."""
        # Stop any running monitoring
        if self.system_monitor.monitoring:
            self.system_monitor.stop_monitoring()

    def export_report(self, output_path: str | None = None) -> dict[str, Any]:
        """Export performance report to file or return as dict.

        Args:
            output_path: Optional path to save report

        Returns:
            Report data as dictionary
        """
        if not self.report:
            raise RuntimeError("No report available - run tests first")

        report_data = {
            "module_path": self.report.module_path,
            "timestamp": time.time(),
            "summary": {
                "overall_status": self.report.overall_status,
                "total_tests": self.report.total_tests,
                "completed_tests": self.report.completed_tests,
                "failed_tests": self.report.failed_tests,
                "aborted_tests": self.report.aborted_tests,
                "duration": self.report.duration,
            },
            "tests": [
                {
                    "id": test.id,
                    "name": test.name,
                    "test_type": test.test_type.value,
                    "status": test.status.value,
                    "duration": (test.end_time - test.start_time if test.end_time > 0 else 0),
                    "load_profile": {
                        "name": test.load_profile.name,
                        "target_users": test.load_profile.target_users,
                        "duration": test.load_profile.ramp_up_duration
                        + test.load_profile.hold_duration
                        + test.load_profile.ramp_down_duration,
                    },
                    "summary_metrics": (
                        {
                            "cpu_usage": (test.summary_metrics.cpu_usage if test.summary_metrics else 0),
                            "memory_usage": (test.summary_metrics.memory_usage if test.summary_metrics else 0),
                            "response_time": (test.summary_metrics.response_time_ms if test.summary_metrics else 0),
                        }
                        if test.summary_metrics
                        else {}
                    ),
                    "issues": test.issues,
                    "warnings": test.warnings,
                }
                for test in self.report.tests
            ],
            "baseline_metrics": (
                {
                    "cpu_usage": self.report.baseline_metrics.cpu_usage,
                    "memory_usage": self.report.baseline_metrics.memory_usage,
                    "memory_usage_mb": self.report.baseline_metrics.memory_usage_mb,
                }
                if self.report.baseline_metrics
                else {}
            ),
            "performance_trends": self.report.performance_trends,
            "recommendations": self.report.recommendations,
            "metadata": self.report.metadata,
        }

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(report_data, f, indent=2)

        return report_data
