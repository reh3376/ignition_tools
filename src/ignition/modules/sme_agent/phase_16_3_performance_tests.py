#!/usr/bin/env python3
"""Phase 16.3 Performance Tests following crawl_mcp.py methodology.

This module provides comprehensive performance testing for Phase 16.3 components
including load testing, scalability testing, and resource utilization analysis.
"""

import asyncio
import logging
import time
from typing import Any

from .phase_16_3_cloud_native_deployment import CloudNativeDeployment, DeploymentConfig
from .phase_16_3_enterprise_integration import (
    EnterpriseIntegrationManager,
    IntegrationConfig,
)

logger = logging.getLogger(__name__)


class Phase163PerformanceTests:
    """Performance tests for Phase 16.3 following crawl_mcp.py methodology."""

    def __init__(self):
        """Initialize performance tests."""
        self.logger = logging.getLogger(__name__)
        self.performance_metrics = {}

    async def validate_performance_test_environment(self) -> dict[str, Any]:
        """Step 1: Environment Validation First (crawl_mcp.py methodology)."""
        self.logger.info("🔍 Validating performance test environment...")

        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "system_resources": {},
            "test_limits": {},
        }

        try:
            # Check system resources
            import psutil

            validation["system_resources"] = {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_free": psutil.disk_usage("/").free,
            }

            # Set test limits based on available resources
            available_memory_gb = psutil.virtual_memory().available / (1024**3)

            if available_memory_gb < 2:
                validation["warnings"].append(
                    "Limited memory available - reducing test scale"
                )
                validation["test_limits"]["max_concurrent_operations"] = 10
            elif available_memory_gb < 4:
                validation["test_limits"]["max_concurrent_operations"] = 25
            else:
                validation["test_limits"]["max_concurrent_operations"] = 50

        except ImportError:
            validation["warnings"].append(
                "psutil not available - using default test limits"
            )
            validation["test_limits"]["max_concurrent_operations"] = 10

        return validation

    async def test_manifest_generation_performance(self) -> dict[str, Any]:
        """Test Kubernetes manifest generation performance across different scales."""
        test_name = "Manifest Generation Performance"
        self.logger.info(f"🚀 Running performance test: {test_name}")

        test_result = {
            "test_name": test_name,
            "success": True,
            "metrics": {},
            "errors": [],
        }

        # Test different deployment scales
        test_scales = {
            "small": {"replicas": 2, "iterations": 50},
            "medium": {"replicas": 5, "iterations": 25},
            "large": {"replicas": 10, "iterations": 10},
            "xlarge": {"replicas": 20, "iterations": 5},
        }

        try:
            for scale_name, scale_config in test_scales.items():
                config = DeploymentConfig(
                    deployment_name=f"perf-test-{scale_name}",
                    replicas=scale_config["replicas"],
                    min_replicas=scale_config["replicas"],
                    max_replicas=scale_config["replicas"] * 2,
                )

                deployment = CloudNativeDeployment(config)

                # Measure manifest generation performance
                times = []
                for i in range(scale_config["iterations"]):
                    start_time = time.time()
                    manifests = await deployment.generate_kubernetes_manifests()
                    end_time = time.time()

                    generation_time = end_time - start_time
                    times.append(generation_time)

                    # Validate manifests were generated
                    if len(manifests) == 0:
                        test_result["success"] = False
                        test_result["errors"].append(
                            f"No manifests generated for {scale_name} scale"
                        )

                # Calculate performance metrics
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)

                test_result["metrics"][scale_name] = {
                    "replicas": scale_config["replicas"],
                    "iterations": scale_config["iterations"],
                    "avg_generation_time": avg_time,
                    "min_generation_time": min_time,
                    "max_generation_time": max_time,
                    "manifest_count": len(manifests),
                    "performance_rating": (
                        "excellent"
                        if avg_time < 0.1
                        else (
                            "good"
                            if avg_time < 0.5
                            else "acceptable" if avg_time < 1.0 else "slow"
                        )
                    ),
                }

                self.logger.info(
                    f"  {scale_name}: {avg_time:.3f}s avg, {len(manifests)} manifests"
                )

        except Exception as e:
            test_result["success"] = False
            test_result["errors"].append(str(e))
            self.logger.error(f"Performance test {test_name} failed: {e}")

        return test_result

    async def test_concurrent_deployment_operations(self) -> dict[str, Any]:
        """Test concurrent deployment operations performance."""
        test_name = "Concurrent Deployment Operations"
        self.logger.info(f"🚀 Running performance test: {test_name}")

        test_result = {
            "test_name": test_name,
            "success": True,
            "metrics": {},
            "errors": [],
        }

        try:
            # Test different concurrency levels
            concurrency_levels = [1, 5, 10, 20]

            for concurrency in concurrency_levels:
                # Create multiple deployment configs
                configs = []
                for i in range(concurrency):
                    config = DeploymentConfig(
                        deployment_name=f"concurrent-test-{i}",
                        namespace=f"test-concurrent-{i}",
                        replicas=2,
                    )
                    configs.append(config)

                # Measure concurrent manifest generation
                start_time = time.time()

                async def generate_manifests(config):
                    deployment = CloudNativeDeployment(config)
                    return await deployment.generate_kubernetes_manifests()

                # Run concurrent operations
                tasks = [generate_manifests(config) for config in configs]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                end_time = time.time()
                total_time = end_time - start_time

                # Analyze results
                successful_operations = 0
                failed_operations = 0
                total_manifests = 0

                for result in results:
                    if isinstance(result, Exception):
                        failed_operations += 1
                        test_result["errors"].append(
                            f"Concurrent operation failed: {result}"
                        )
                    else:
                        successful_operations += 1
                        total_manifests += len(result)

                # Calculate metrics
                operations_per_second = (
                    successful_operations / total_time if total_time > 0 else 0
                )
                avg_time_per_operation = (
                    total_time / concurrency if concurrency > 0 else 0
                )

                test_result["metrics"][f"concurrency_{concurrency}"] = {
                    "concurrency_level": concurrency,
                    "total_time": total_time,
                    "successful_operations": successful_operations,
                    "failed_operations": failed_operations,
                    "operations_per_second": operations_per_second,
                    "avg_time_per_operation": avg_time_per_operation,
                    "total_manifests_generated": total_manifests,
                    "success_rate": successful_operations / concurrency * 100,
                }

                if failed_operations > 0:
                    test_result["success"] = False

                self.logger.info(
                    f"  Concurrency {concurrency}: {operations_per_second:.2f} ops/sec, {successful_operations}/{concurrency} success"
                )

        except Exception as e:
            test_result["success"] = False
            test_result["errors"].append(str(e))
            self.logger.error(f"Performance test {test_name} failed: {e}")

        return test_result

    async def test_integration_connection_performance(self) -> dict[str, Any]:
        """Test enterprise integration connection performance."""
        test_name = "Integration Connection Performance"
        self.logger.info(f"🚀 Running performance test: {test_name}")

        test_result = {
            "test_name": test_name,
            "success": True,
            "metrics": {},
            "errors": [],
        }

        try:
            integration_manager = EnterpriseIntegrationManager()

            # Test different numbers of concurrent integrations
            integration_counts = [1, 5, 10, 20]

            for count in integration_counts:
                # Create integration configs
                configs = []
                for i in range(count):
                    config = IntegrationConfig(
                        integration_name=f"perf-test-integration-{i}",
                        system_type="SAP",
                        endpoint_url=f"https://test-{i}.example.com",
                        auth_type="basic",
                        username="test_user",
                        password="test_pass",
                        timeout=10,  # Shorter timeout for performance testing
                    )
                    configs.append(config)

                # Measure registration performance
                start_time = time.time()

                registration_tasks = []
                for config in configs:
                    task = integration_manager.register_integration(
                        config.integration_name, config
                    )
                    registration_tasks.append(task)

                registration_results = await asyncio.gather(
                    *registration_tasks, return_exceptions=True
                )

                end_time = time.time()
                registration_time = end_time - start_time

                # Analyze registration results
                successful_registrations = 0
                failed_registrations = 0

                for result in registration_results:
                    if isinstance(result, Exception):
                        failed_registrations += 1
                        test_result["errors"].append(f"Registration failed: {result}")
                    elif result.get("success"):
                        successful_registrations += 1
                    else:
                        failed_registrations += 1

                # Test status retrieval performance
                status_start_time = time.time()
                status = await integration_manager.get_integration_status()
                status_end_time = time.time()
                status_time = status_end_time - status_start_time

                # Calculate metrics
                registrations_per_second = (
                    successful_registrations / registration_time
                    if registration_time > 0
                    else 0
                )

                test_result["metrics"][f"integrations_{count}"] = {
                    "integration_count": count,
                    "registration_time": registration_time,
                    "status_retrieval_time": status_time,
                    "successful_registrations": successful_registrations,
                    "failed_registrations": failed_registrations,
                    "registrations_per_second": registrations_per_second,
                    "success_rate": successful_registrations / count * 100,
                    "total_integrations_reported": status.get("total_integrations", 0),
                }

                if failed_registrations > 0:
                    test_result["success"] = False

                self.logger.info(
                    f"  {count} integrations: {registrations_per_second:.2f} reg/sec, {successful_registrations}/{count} success"
                )

                # Cleanup for next iteration
                await integration_manager.cleanup_integrations()

        except Exception as e:
            test_result["success"] = False
            test_result["errors"].append(str(e))
            self.logger.error(f"Performance test {test_name} failed: {e}")

        return test_result

    async def test_memory_usage_patterns(self) -> dict[str, Any]:
        """Test memory usage patterns during operations."""
        test_name = "Memory Usage Patterns"
        self.logger.info(f"🚀 Running performance test: {test_name}")

        test_result = {
            "test_name": test_name,
            "success": True,
            "metrics": {},
            "errors": [],
        }

        try:
            import gc

            import psutil

            process = psutil.Process()

            # Baseline memory measurement
            gc.collect()  # Force garbage collection
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Test memory usage during large-scale operations
            test_operations = {
                "manifest_generation": {
                    "operation": "generate_many_manifests",
                    "scale": 50,
                },
                "integration_registration": {
                    "operation": "register_many_integrations",
                    "scale": 30,
                },
            }

            for operation_name, operation_config in test_operations.items():
                gc.collect()
                start_memory = process.memory_info().rss / 1024 / 1024  # MB

                if operation_config["operation"] == "generate_many_manifests":
                    # Generate many manifests
                    for i in range(operation_config["scale"]):
                        config = DeploymentConfig(
                            deployment_name=f"memory-test-{i}",
                            replicas=3,
                        )
                        deployment = CloudNativeDeployment(config)
                        manifests = await deployment.generate_kubernetes_manifests()

                        # Measure memory every 10 operations
                        if i % 10 == 0:
                            current_memory = process.memory_info().rss / 1024 / 1024
                            memory_increase = current_memory - baseline_memory
                            self.logger.debug(
                                f"    Operation {i}: {memory_increase:.2f}MB increase"
                            )

                elif operation_config["operation"] == "register_many_integrations":
                    # Register many integrations
                    integration_manager = EnterpriseIntegrationManager()

                    for i in range(operation_config["scale"]):
                        config = IntegrationConfig(
                            integration_name=f"memory-test-integration-{i}",
                            system_type="SAP",
                            endpoint_url=f"https://memory-test-{i}.example.com",
                            auth_type="basic",
                            username="test_user",
                            password="test_pass",
                        )

                        await integration_manager.register_integration(
                            config.integration_name, config
                        )

                        # Measure memory every 10 operations
                        if i % 10 == 0:
                            current_memory = process.memory_info().rss / 1024 / 1024
                            memory_increase = current_memory - baseline_memory
                            self.logger.debug(
                                f"    Operation {i}: {memory_increase:.2f}MB increase"
                            )

                    # Cleanup integrations
                    await integration_manager.cleanup_integrations()

                gc.collect()
                end_memory = process.memory_info().rss / 1024 / 1024  # MB

                # Calculate memory metrics
                peak_memory = end_memory
                memory_increase = peak_memory - baseline_memory
                memory_per_operation = memory_increase / operation_config["scale"]

                test_result["metrics"][operation_name] = {
                    "baseline_memory_mb": baseline_memory,
                    "start_memory_mb": start_memory,
                    "end_memory_mb": end_memory,
                    "peak_memory_increase_mb": memory_increase,
                    "memory_per_operation_mb": memory_per_operation,
                    "operations_count": operation_config["scale"],
                    "memory_efficiency": (
                        "excellent"
                        if memory_per_operation < 1
                        else (
                            "good"
                            if memory_per_operation < 5
                            else "acceptable" if memory_per_operation < 10 else "poor"
                        )
                    ),
                }

                self.logger.info(
                    f"  {operation_name}: {memory_increase:.2f}MB total, {memory_per_operation:.3f}MB per operation"
                )

        except ImportError:
            test_result["success"] = False
            test_result["errors"].append("psutil not available for memory testing")
        except Exception as e:
            test_result["success"] = False
            test_result["errors"].append(str(e))
            self.logger.error(f"Performance test {test_name} failed: {e}")

        return test_result

    async def run_all_performance_tests(self) -> dict[str, Any]:
        """Run all performance tests following crawl_mcp.py methodology."""
        self.logger.info("🚀 Running all Phase 16.3 performance tests...")

        # Step 1: Environment Validation First
        env_validation = await self.validate_performance_test_environment()

        # Step 4: Modular Component Testing - Run all performance tests
        performance_tests = [
            self.test_manifest_generation_performance,
            self.test_concurrent_deployment_operations,
            self.test_integration_connection_performance,
            self.test_memory_usage_patterns,
        ]

        results = {
            "success": True,
            "total_tests": len(performance_tests),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": {},
            "environment_validation": env_validation,
            "execution_time": 0,
            "performance_summary": {},
        }

        start_time = time.time()

        for test_func in performance_tests:
            test_result = await test_func()
            test_name = test_result["test_name"]

            results["test_results"][test_name] = test_result

            if test_result["success"]:
                results["passed_tests"] += 1
            else:
                results["failed_tests"] += 1
                results["success"] = False

        results["execution_time"] = time.time() - start_time

        # Generate performance summary
        results["performance_summary"] = self._generate_performance_summary(
            results["test_results"]
        )

        # Step 6: Resource Management and Cleanup
        self.logger.info("🧹 Cleaning up performance test resources...")

        return results

    def _generate_performance_summary(
        self, test_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate performance summary from test results."""
        summary = {
            "overall_performance": "good",
            "key_metrics": {},
            "recommendations": [],
        }

        # Analyze manifest generation performance
        if "Manifest Generation Performance" in test_results:
            manifest_test = test_results["Manifest Generation Performance"]
            if "metrics" in manifest_test:
                # Find average performance across scales
                avg_times = []
                for scale_metrics in manifest_test["metrics"].values():
                    avg_times.append(scale_metrics["avg_generation_time"])

                if avg_times:
                    overall_avg = sum(avg_times) / len(avg_times)
                    summary["key_metrics"]["manifest_generation_avg_time"] = overall_avg

                    if overall_avg > 1.0:
                        summary["overall_performance"] = "poor"
                        summary["recommendations"].append(
                            "Optimize manifest generation - average time exceeds 1 second"
                        )
                    elif overall_avg > 0.5:
                        summary["overall_performance"] = "acceptable"
                        summary["recommendations"].append(
                            "Consider optimizing manifest generation for better performance"
                        )

        # Analyze concurrent operations performance
        if "Concurrent Deployment Operations" in test_results:
            concurrent_test = test_results["Concurrent Deployment Operations"]
            if "metrics" in concurrent_test:
                # Find best operations per second
                best_ops_per_sec = 0
                for concurrency_metrics in concurrent_test["metrics"].values():
                    ops_per_sec = concurrency_metrics["operations_per_second"]
                    if ops_per_sec > best_ops_per_sec:
                        best_ops_per_sec = ops_per_sec

                summary["key_metrics"]["max_operations_per_second"] = best_ops_per_sec

                if best_ops_per_sec < 5:
                    summary["recommendations"].append(
                        "Low concurrent operation throughput - consider optimization"
                    )

        # Analyze memory usage
        if "Memory Usage Patterns" in test_results:
            memory_test = test_results["Memory Usage Patterns"]
            if "metrics" in memory_test:
                total_memory_per_op = 0
                operation_count = 0

                for operation_metrics in memory_test["metrics"].values():
                    total_memory_per_op += operation_metrics["memory_per_operation_mb"]
                    operation_count += 1

                if operation_count > 0:
                    avg_memory_per_op = total_memory_per_op / operation_count
                    summary["key_metrics"][
                        "avg_memory_per_operation_mb"
                    ] = avg_memory_per_op

                    if avg_memory_per_op > 10:
                        summary["overall_performance"] = "poor"
                        summary["recommendations"].append(
                            "High memory usage per operation - investigate memory leaks"
                        )
                    elif avg_memory_per_op > 5:
                        summary["recommendations"].append(
                            "Consider optimizing memory usage"
                        )

        return summary


async def main():
    """Main function to run performance tests."""
    performance_tests = Phase163PerformanceTests()

    print("🚀 Starting Phase 16.3 Performance Tests")
    print("Following crawl_mcp.py methodology for systematic performance testing")
    print("=" * 60)

    results = await performance_tests.run_all_performance_tests()

    # Display results
    print("\n" + "=" * 80)
    print("PHASE 16.3 PERFORMANCE TEST RESULTS")
    print("=" * 80)
    print(f"Overall Success: {'✅' if results['success'] else '❌'}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Execution Time: {results['execution_time']:.2f}s")

    # Display performance summary
    if "performance_summary" in results:
        summary = results["performance_summary"]
        print(f"\nOverall Performance: {summary['overall_performance'].upper()}")

        if "key_metrics" in summary:
            print("\nKey Metrics:")
            for metric, value in summary["key_metrics"].items():
                if isinstance(value, float):
                    print(f"  {metric}: {value:.3f}")
                else:
                    print(f"  {metric}: {value}")

        if summary.get("recommendations"):
            print("\nRecommendations:")
            for rec in summary["recommendations"]:
                print(f"  • {rec}")

    print("\nDetailed Test Results:")
    for test_name, test_result in results["test_results"].items():
        status = "✅" if test_result["success"] else "❌"
        print(f"  {status} {test_name}")

        if not test_result["success"] and test_result["errors"]:
            for error in test_result["errors"]:
                print(f"    ❌ {error}")

    print("=" * 80)

    return 0 if results["success"] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
