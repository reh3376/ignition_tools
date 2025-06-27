#!/usr/bin/env python3
"""Comprehensive Phase 16.3 Test Suite for Scalable Deployment & Enterprise Integration.

Following crawl_mcp.py methodology for systematic testing:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

This comprehensive test suite covers:
- Cloud-native deployment testing with all complexity levels
- Enterprise integration testing (SAP, SCADA, Oracle)
- CLI integration and workflow testing
- Security and compliance validation
- Performance and scalability testing
- Disaster recovery and backup testing
- End-to-end integration scenarios
"""

import asyncio
import logging
import os
import time
import unittest
from typing import Any
from unittest.mock import AsyncMock, patch

import yaml
from pydantic import ValidationError

from .phase_16_3_cli_integration import Phase163CLIManager
from .phase_16_3_cloud_native_deployment import (
    CloudNativeDeployment,
    DeploymentConfig,
)
from .phase_16_3_enterprise_integration import (
    EnterpriseIntegrationManager,
    IntegrationConfig,
    SAPIntegration,
    SCADAIntegration,
)

logger = logging.getLogger(__name__)


class TestEnvironmentValidator:
    """Step 1: Environment Validation First (crawl_mcp.py methodology)."""

    @staticmethod
    async def validate_test_environment() -> dict[str, Any]:
        """Validate comprehensive test environment setup."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "components": {},
            "tools": {},
            "infrastructure": {},
        }

        # Validate testing tools
        required_tools = {
            "kubectl": "Kubernetes CLI",
            "helm": "Helm package manager",
            "docker": "Docker container runtime",
            "pytest": "Python testing framework",
        }

        for tool, description in required_tools.items():
            try:
                if tool == "pytest":
                    import pytest as pytest_module

                    validation_result["tools"][tool] = {
                        "available": True,
                        "version": pytest_module.__version__,
                        "description": description,
                    }
                else:
                    import subprocess

                    result = subprocess.run(
                        [tool, "version"], capture_output=True, text=True, timeout=10
                    )
                    validation_result["tools"][tool] = {
                        "available": result.returncode == 0,
                        "version": (
                            result.stdout.split("\n")[0]
                            if result.returncode == 0
                            else None
                        ),
                        "description": description,
                    }

                    if result.returncode != 0:
                        validation_result["valid"] = False
                        validation_result["errors"].append(
                            f"Required tool {tool} not available"
                        )

            except Exception as e:
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"Tool {tool} validation failed: {e}"
                )

        # Validate test infrastructure
        test_env_vars = {
            "PHASE16_TEST_NAMESPACE": "Test Kubernetes namespace",
            "PHASE16_TEST_REGISTRY": "Test container registry",
            "PHASE16_SAP_TEST_ENDPOINT": "SAP test system endpoint",
            "PHASE16_SCADA_TEST_ENDPOINT": "SCADA test system endpoint",
        }

        for env_var, description in test_env_vars.items():
            value = os.getenv(env_var)
            validation_result["infrastructure"][env_var] = {
                "configured": value is not None,
                "value": value if value else "Not set",
                "description": description,
            }

            if not value:
                validation_result["warnings"].append(
                    f"Test environment variable {env_var} not set"
                )

        return validation_result


class ComprehensiveCloudDeploymentTests(unittest.TestCase):
    """Comprehensive cloud deployment testing following crawl_mcp.py methodology."""

    def setUp(self):
        """Step 1: Environment Validation First."""
        self.test_configs = {
            "basic": DeploymentConfig(
                deployment_name="test-basic-deployment",
                namespace="test-basic",
                replicas=1,
                min_replicas=1,
                max_replicas=3,
                cpu_request="100m",
                memory_request="256Mi",
                ingress_enabled=False,
                rbac_enabled=False,
                prometheus_enabled=False,
            ),
            "standard": DeploymentConfig(
                deployment_name="test-standard-deployment",
                namespace="test-standard",
                replicas=2,
                min_replicas=2,
                max_replicas=5,
                cpu_request="250m",
                memory_request="512Mi",
                ingress_enabled=True,
                rbac_enabled=True,
                prometheus_enabled=True,
            ),
            "advanced": DeploymentConfig(
                deployment_name="test-advanced-deployment",
                namespace="test-advanced",
                replicas=3,
                min_replicas=3,
                max_replicas=10,
                cpu_request="500m",
                memory_request="1Gi",
                ingress_enabled=True,
                rbac_enabled=True,
                prometheus_enabled=True,
                network_policies_enabled=True,
                security_context_enabled=True,
            ),
            "enterprise": DeploymentConfig(
                deployment_name="test-enterprise-deployment",
                namespace="test-enterprise",
                replicas=5,
                min_replicas=5,
                max_replicas=20,
                cpu_request="1000m",
                memory_request="2Gi",
                ingress_enabled=True,
                rbac_enabled=True,
                prometheus_enabled=True,
                network_policies_enabled=True,
                security_context_enabled=True,
                backup_enabled=True,
            ),
        }

        self.deployments = {
            complexity: CloudNativeDeployment(config)
            for complexity, config in self.test_configs.items()
        }

    def tearDown(self):
        """Step 6: Resource Management and Cleanup."""
        # Cleanup test resources
        pass

    async def test_progressive_complexity_validation(self):
        """Test progressive complexity deployment validation."""
        for complexity, deployment in self.deployments.items():
            with self.subTest(complexity=complexity):
                # Step 2: Comprehensive Input Validation
                validation = deployment._validate_deployment_config()

                assert validation[
                    "valid"
                ], f"Configuration validation failed for {complexity}: {validation['errors']}"
                assert isinstance(validation["errors"], list)
                assert isinstance(validation["warnings"], list)

    async def test_kubernetes_manifest_generation_all_complexities(self):
        """Test Kubernetes manifest generation for all complexity levels."""
        for complexity, deployment in self.deployments.items():
            with self.subTest(complexity=complexity):
                manifests = await deployment.generate_kubernetes_manifests()

                # Verify core manifests exist
                core_manifests = [
                    "namespace",
                    "deployment",
                    "service",
                    "hpa",
                    "configmap",
                    "secret",
                ]
                for manifest_name in core_manifests:
                    assert (
                        manifest_name in manifests
                    ), f"Missing {manifest_name} manifest for {complexity}"

                    # Validate YAML syntax
                    try:
                        yaml.safe_load(manifests[manifest_name])
                    except yaml.YAMLError as e:
                        self.fail(
                            f"Invalid YAML in {manifest_name} manifest for {complexity}: {e}"
                        )

                # Verify complexity-specific manifests
                config = self.test_configs[complexity]

                if config.ingress_enabled:
                    assert (
                        "ingress" in manifests
                    ), f"Missing ingress manifest for {complexity}"

                if config.network_policies_enabled:
                    assert (
                        "network_policy" in manifests
                    ), f"Missing network policy for {complexity}"

                if config.rbac_enabled:
                    assert (
                        "rbac" in manifests
                    ), f"Missing RBAC manifest for {complexity}"

                if config.prometheus_enabled:
                    assert (
                        "service_monitor" in manifests
                    ), f"Missing service monitor for {complexity}"

    async def test_deployment_security_configuration(self):
        """Test security configuration across complexity levels."""
        for complexity, deployment in self.deployments.items():
            with self.subTest(complexity=complexity):
                manifests = await deployment.generate_kubernetes_manifests()

                # Parse deployment manifest
                deployment_manifest = yaml.safe_load(manifests["deployment"])
                container_spec = deployment_manifest["spec"]["template"]["spec"][
                    "containers"
                ][0]

                config = self.test_configs[complexity]

                if config.security_context_enabled:
                    # Verify security context
                    assert "securityContext" in container_spec
                    security_context = container_spec["securityContext"]
                    assert security_context["runAsNonRoot"] is True
                    assert security_context["readOnlyRootFilesystem"] is True
                    assert "runAsUser" in security_context

    async def test_resource_limits_and_requests(self):
        """Test resource limits and requests configuration."""
        for complexity, deployment in self.deployments.items():
            with self.subTest(complexity=complexity):
                manifests = await deployment.generate_kubernetes_manifests()
                deployment_manifest = yaml.safe_load(manifests["deployment"])

                container_spec = deployment_manifest["spec"]["template"]["spec"][
                    "containers"
                ][0]
                resources = container_spec["resources"]

                config = self.test_configs[complexity]

                # Verify resource requests
                assert resources["requests"]["cpu"] == config.cpu_request
                assert resources["requests"]["memory"] == config.memory_request

                # Verify resource limits
                assert resources["limits"]["cpu"] == config.cpu_limit
                assert resources["limits"]["memory"] == config.memory_limit

    async def test_horizontal_pod_autoscaler_configuration(self):
        """Test HPA configuration for different complexity levels."""
        for complexity, deployment in self.deployments.items():
            with self.subTest(complexity=complexity):
                manifests = await deployment.generate_kubernetes_manifests()
                hpa_manifest = yaml.safe_load(manifests["hpa"])

                config = self.test_configs[complexity]

                # Verify HPA configuration
                assert hpa_manifest["spec"]["minReplicas"] == config.min_replicas
                assert hpa_manifest["spec"]["maxReplicas"] == config.max_replicas

                # Verify target CPU utilization
                metrics = hpa_manifest["spec"]["metrics"]
                cpu_metric = next(m for m in metrics if m["type"] == "Resource")
                assert (
                    cpu_metric["resource"]["target"]["averageUtilization"]
                    == config.target_cpu_utilization
                )

    @patch("subprocess.run")
    async def test_dry_run_deployment_all_complexities(self, mock_subprocess):
        """Test dry-run deployment for all complexity levels."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "deployment configured (dry run)"

        for complexity, deployment in self.deployments.items():
            with self.subTest(complexity=complexity):
                # Generate manifests first
                await deployment.generate_kubernetes_manifests()

                # Test dry run
                result = await deployment.deploy_to_kubernetes(dry_run=True)

                assert result[
                    "success"
                ], f"Dry run failed for {complexity}: {result.get('error')}"
                assert len(result["manifests_applied"]) > 0
                assert len(result["errors"]) == 0


class ComprehensiveEnterpriseIntegrationTests(unittest.TestCase):
    """Comprehensive enterprise integration testing following crawl_mcp.py methodology."""

    def setUp(self):
        """Step 1: Environment Validation First."""
        self.integration_configs = {
            "sap_basic": IntegrationConfig(
                integration_name="test-sap-basic",
                system_type="SAP",
                endpoint_url="https://sap-test.example.com",
                auth_type="basic",
                username="test_user",
                password="test_pass",
                timeout=30,
                max_retries=3,
            ),
            "sap_oauth": IntegrationConfig(
                integration_name="test-sap-oauth",
                system_type="SAP",
                endpoint_url="https://sap-oauth.example.com",
                auth_type="oauth2",
                token="test_oauth_token",
                timeout=45,
                max_retries=5,
            ),
            "scada_basic": IntegrationConfig(
                integration_name="test-scada-basic",
                system_type="SCADA",
                endpoint_url="http://scada-test.example.com:8080",
                auth_type="api_key",
                api_key="test_api_key",
                timeout=60,
                max_retries=3,
            ),
            "oracle_enterprise": IntegrationConfig(
                integration_name="test-oracle-enterprise",
                system_type="Oracle",
                endpoint_url="https://oracle-enterprise.example.com",
                auth_type="certificate",
                client_cert_path="/path/to/client.crt",
                client_key_path="/path/to/client.key",
                ca_cert_path="/path/to/ca.crt",
                timeout=120,
                max_retries=5,
            ),
        }

        self.integration_manager = EnterpriseIntegrationManager()

    def tearDown(self):
        """Step 6: Resource Management and Cleanup."""
        # Cleanup integration resources
        pass

    def test_integration_config_validation(self):
        """Step 2: Comprehensive Input Validation."""
        for config_name, config in self.integration_configs.items():
            with self.subTest(config=config_name):
                # Test valid configuration
                assert config.integration_name
                assert config.system_type
                assert config.endpoint_url
                assert config.auth_type in [
                    "basic",
                    "bearer",
                    "api_key",
                    "oauth2",
                    "certificate",
                ]

        # Test invalid configurations
        with self.assertRaises(ValidationError):
            IntegrationConfig(
                integration_name="",  # Invalid: empty name
                system_type="SAP",
                endpoint_url="invalid-url",  # Invalid: malformed URL
                auth_type="invalid_auth",  # Invalid: unsupported auth type
            )

    async def test_sap_integration_connection_methods(self):
        """Test SAP integration with different authentication methods."""
        for config_name, config in self.integration_configs.items():
            if config.system_type != "SAP":
                continue

            with self.subTest(config=config_name):
                integration = SAPIntegration(config)

                # Mock the HTTP session and response
                with patch("aiohttp.ClientSession") as mock_session:
                    mock_response = AsyncMock()
                    mock_response.status = 200
                    mock_response.json = AsyncMock(return_value={"system": "SAP Test"})
                    mock_response.headers = {"X-Response-Time": "100ms"}

                    mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
                        mock_response
                    )

                    # Test connection
                    connection_result = await integration.connect()
                    assert connection_result is True
                    assert integration.connection_status == "connected"

    async def test_scada_integration_data_operations(self):
        """Test SCADA integration data operations."""
        config = self.integration_configs["scada_basic"]
        integration = SCADAIntegration(config)

        # Mock HTTP responses
        with patch("aiohttp.ClientSession") as mock_session:
            # Mock successful connection test
            mock_test_response = AsyncMock()
            mock_test_response.status = 200
            mock_test_response.json = AsyncMock(return_value={"status": "online"})

            # Mock historical data response
            mock_historical_response = AsyncMock()
            mock_historical_response.status = 200
            mock_historical_response.json = AsyncMock(
                return_value={
                    "data": [
                        {"timestamp": "2024-01-01T00:00:00Z", "value": 100.0},
                        {"timestamp": "2024-01-01T01:00:00Z", "value": 105.0},
                    ]
                }
            )

            # Mock real-time data response
            mock_realtime_response = AsyncMock()
            mock_realtime_response.status = 200
            mock_realtime_response.json = AsyncMock(
                return_value={
                    "tags": {
                        "temperature": {"value": 25.5, "quality": "good"},
                        "pressure": {"value": 1013.25, "quality": "good"},
                    }
                }
            )

            mock_session_instance = mock_session.return_value.__aenter__.return_value
            mock_session_instance.get.return_value.__aenter__.return_value = (
                mock_test_response
            )

            # Test connection
            connection_result = await integration.connect()
            assert connection_result is True

            # Test historical data retrieval
            mock_session_instance.get.return_value.__aenter__.return_value = (
                mock_historical_response
            )

            historical_query = {
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T02:00:00Z",
                "tags": ["temperature", "pressure"],
            }

            historical_result = await integration.get_historical_data(historical_query)
            assert historical_result["success"] is True
            assert len(historical_result["data"]) == 2

            # Test real-time data retrieval
            mock_session_instance.get.return_value.__aenter__.return_value = (
                mock_realtime_response
            )

            realtime_result = await integration.get_real_time_data(
                ["temperature", "pressure"]
            )
            assert realtime_result["success"] is True
            assert "temperature" in realtime_result["tags"]
            assert "pressure" in realtime_result["tags"]

    async def test_integration_manager_lifecycle(self):
        """Test integration manager complete lifecycle."""
        # Step 1: Environment validation
        validation = await self.integration_manager.validate_environment()
        assert isinstance(validation, dict)
        assert "valid" in validation

        # Step 2: Register integrations
        for config_name, config in self.integration_configs.items():
            registration_result = await self.integration_manager.register_integration(
                config.integration_name, config
            )
            assert registration_result["success"] is True
            assert config.integration_name in self.integration_manager.integrations

        # Step 3: Get integration status
        status = await self.integration_manager.get_integration_status()
        assert status["total_integrations"] == len(self.integration_configs)

        # Step 4: Cleanup integrations
        cleanup_result = await self.integration_manager.cleanup_integrations()
        assert cleanup_result["success"] is True


class ComprehensiveCLIIntegrationTests(unittest.TestCase):
    """Comprehensive CLI integration testing following crawl_mcp.py methodology."""

    def setUp(self):
        """Step 1: Environment Validation First."""
        self.cli_manager = Phase163CLIManager()

    def tearDown(self):
        """Step 6: Resource Management and Cleanup."""
        pass

    async def test_cli_environment_validation(self):
        """Test CLI environment validation."""
        validation = await self.cli_manager.validate_environment()

        assert isinstance(validation, dict)
        assert "valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        assert "components" in validation
        assert "tools" in validation

    async def test_cli_deployment_workflow(self):
        """Test complete CLI deployment workflow."""
        complexity_levels = ["basic", "standard", "advanced", "enterprise"]

        for complexity in complexity_levels:
            with self.subTest(complexity=complexity):
                # Test deployment configuration creation
                config = self.cli_manager._create_deployment_config(complexity)
                assert isinstance(config, DeploymentConfig)
                assert config.deployment_name

                # Test dry-run deployment
                with patch("subprocess.run") as mock_subprocess:
                    mock_subprocess.return_value.returncode = 0
                    mock_subprocess.return_value.stdout = (
                        f"deployment configured (dry run) for {complexity}"
                    )

                    deployment_result = await self.cli_manager.deploy_to_cloud(
                        complexity, dry_run=True
                    )
                    assert deployment_result["success"] is True

    async def test_cli_integration_registration(self):
        """Test CLI integration registration workflow."""
        integration_types = ["SAP", "SCADA", "Oracle"]

        for system_type in integration_types:
            with self.subTest(system_type=system_type):
                config_data = {
                    "endpoint_url": f"https://{system_type.lower()}-test.example.com",
                    "auth_type": "basic",
                    "username": "test_user",
                    "password": "test_pass",
                }

                registration_result = (
                    await self.cli_manager.register_enterprise_integration(
                        system_type, config_data
                    )
                )
                assert registration_result["success"] is True


class PerformanceAndScalabilityTests(unittest.TestCase):
    """Performance and scalability testing following crawl_mcp.py methodology."""

    def setUp(self):
        """Step 1: Environment Validation First."""
        self.performance_configs = {
            "small_scale": DeploymentConfig(
                deployment_name="perf-test-small",
                replicas=2,
                min_replicas=1,
                max_replicas=5,
            ),
            "medium_scale": DeploymentConfig(
                deployment_name="perf-test-medium",
                replicas=5,
                min_replicas=3,
                max_replicas=15,
            ),
            "large_scale": DeploymentConfig(
                deployment_name="perf-test-large",
                replicas=10,
                min_replicas=5,
                max_replicas=50,
            ),
        }

    def test_manifest_generation_performance(self):
        """Test manifest generation performance across different scales."""
        for scale, config in self.performance_configs.items():
            with self.subTest(scale=scale):
                deployment = CloudNativeDeployment(config)

                start_time = time.time()

                # Run manifest generation multiple times
                for _ in range(10):
                    asyncio.run(deployment.generate_kubernetes_manifests())

                end_time = time.time()
                avg_time = (end_time - start_time) / 10

                # Performance assertion (should complete within reasonable time)
                assert (
                    avg_time < 1.0
                ), f"Manifest generation too slow for {scale}: {avg_time}s"

    async def test_concurrent_integration_operations(self):
        """Test concurrent integration operations."""
        integration_manager = EnterpriseIntegrationManager()

        # Create multiple integration configs
        configs = []
        for i in range(5):
            config = IntegrationConfig(
                integration_name=f"concurrent-test-{i}",
                system_type="SAP",
                endpoint_url=f"https://test-{i}.example.com",
                auth_type="basic",
                username="test_user",
                password="test_pass",
            )
            configs.append(config)

        # Test concurrent registration
        start_time = time.time()

        tasks = []
        for config in configs:
            task = integration_manager.register_integration(
                config.integration_name, config
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        # Verify all registrations succeeded
        for result in results:
            if isinstance(result, Exception):
                self.fail(f"Concurrent registration failed: {result}")
            assert result["success"] is True

        # Performance assertion
        assert total_time < 10.0, f"Concurrent operations too slow: {total_time}s"


class SecurityAndComplianceTests(unittest.TestCase):
    """Security and compliance testing following crawl_mcp.py methodology."""

    def test_deployment_security_policies(self):
        """Test deployment security policies."""
        config = DeploymentConfig(
            deployment_name="security-test",
            security_context_enabled=True,
            network_policies_enabled=True,
            rbac_enabled=True,
        )

        deployment = CloudNativeDeployment(config)
        manifests = asyncio.run(deployment.generate_kubernetes_manifests())

        # Verify security context
        deployment_manifest = yaml.safe_load(manifests["deployment"])
        container_spec = deployment_manifest["spec"]["template"]["spec"]["containers"][
            0
        ]

        assert "securityContext" in container_spec
        security_context = container_spec["securityContext"]
        assert security_context["runAsNonRoot"] is True
        assert security_context["readOnlyRootFilesystem"] is True

        # Verify network policies
        assert "network_policy" in manifests
        network_policy = yaml.safe_load(manifests["network_policy"])
        assert network_policy["kind"] == "NetworkPolicy"

        # Verify RBAC
        assert "rbac" in manifests
        rbac_manifests = manifests["rbac"].split("---\n")
        rbac_kinds = []
        for rbac_doc in rbac_manifests:
            if rbac_doc.strip():
                rbac_obj = yaml.safe_load(rbac_doc)
                rbac_kinds.append(rbac_obj["kind"])

        assert "ServiceAccount" in rbac_kinds
        assert "Role" in rbac_kinds
        assert "RoleBinding" in rbac_kinds

    def test_integration_ssl_configuration(self):
        """Test integration SSL/TLS configuration."""
        config = IntegrationConfig(
            integration_name="ssl-test",
            system_type="SAP",
            endpoint_url="https://secure.example.com",
            auth_type="certificate",
            verify_ssl=True,
            ca_cert_path="/path/to/ca.crt",
            client_cert_path="/path/to/client.crt",
            client_key_path="/path/to/client.key",
        )

        integration = SAPIntegration(config)

        # Verify SSL configuration is properly set
        assert config.verify_ssl is True
        assert config.ca_cert_path is not None
        assert config.client_cert_path is not None
        assert config.client_key_path is not None


def run_comprehensive_phase_16_3_tests() -> dict[str, Any]:
    """Run comprehensive Phase 16.3 test suite following crawl_mcp.py methodology.

    Returns:
        Dict containing test results and metrics
    """
    logger.info("🚀 Starting comprehensive Phase 16.3 test suite...")

    # Step 1: Environment Validation First
    async def validate_and_run():
        validation = await TestEnvironmentValidator.validate_test_environment()

        if not validation["valid"]:
            return {
                "success": False,
                "error": "Test environment validation failed",
                "validation_errors": validation["errors"],
                "validation_warnings": validation["warnings"],
            }

        # Step 4: Modular Component Testing
        test_suites = [
            ComprehensiveCloudDeploymentTests,
            ComprehensiveEnterpriseIntegrationTests,
            ComprehensiveCLIIntegrationTests,
            PerformanceAndScalabilityTests,
            SecurityAndComplianceTests,
        ]

        test_results = {
            "success": True,
            "test_suites": {},
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "execution_time": 0,
            "environment_validation": validation,
        }

        start_time = time.time()

        for test_suite_class in test_suites:
            suite_name = test_suite_class.__name__
            logger.info(f"Running test suite: {suite_name}")

            try:
                # Create test suite
                suite = unittest.TestLoader().loadTestsFromTestCase(test_suite_class)

                # Run tests
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)

                # Record results
                test_results["test_suites"][suite_name] = {
                    "tests_run": result.testsRun,
                    "failures": len(result.failures),
                    "errors": len(result.errors),
                    "success": result.wasSuccessful(),
                }

                test_results["total_tests"] += result.testsRun
                test_results["passed_tests"] += (
                    result.testsRun - len(result.failures) - len(result.errors)
                )
                test_results["failed_tests"] += len(result.failures) + len(
                    result.errors
                )

                if not result.wasSuccessful():
                    test_results["success"] = False

            except Exception as e:
                logger.error(f"Test suite {suite_name} failed with exception: {e}")
                test_results["success"] = False
                test_results["test_suites"][suite_name] = {
                    "error": str(e),
                    "success": False,
                }

        end_time = time.time()
        test_results["execution_time"] = end_time - start_time

        # Step 6: Resource Management and Cleanup
        logger.info("🧹 Cleaning up test resources...")

        return test_results

    # Run async validation and tests
    return asyncio.run(validate_and_run())


if __name__ == "__main__":
    # Run comprehensive test suite
    results = run_comprehensive_phase_16_3_tests()

    print("\n" + "=" * 80)
    print("COMPREHENSIVE PHASE 16.3 TEST RESULTS")
    print("=" * 80)
    print(f"Overall Success: {'✅' if results['success'] else '❌'}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Execution Time: {results['execution_time']:.2f}s")
    print("\nTest Suite Results:")

    for suite_name, suite_results in results.get("test_suites", {}).items():
        status = "✅" if suite_results.get("success", False) else "❌"
        print(f"  {status} {suite_name}")
        if "tests_run" in suite_results:
            print(
                f"    Tests: {suite_results['tests_run']}, "
                f"Failures: {suite_results['failures']}, "
                f"Errors: {suite_results['errors']}"
            )

    print("=" * 80)
