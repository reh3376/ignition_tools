#!/usr/bin/env python3
"""Phase 16.3 Test Framework for Scalable Deployment & Enterprise Integration.

Following crawl_mcp.py methodology for systematic testing:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

Test Categories:
- Cloud deployment testing
- Enterprise integration testing
- Kubernetes manifest validation
- Integration protocol testing
- Performance and scalability testing
- Error handling and recovery testing
"""

import asyncio
import json
import logging
import os
import time
import unittest
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import yaml

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


class TestCloudNativeDeployment(unittest.TestCase):
    """Test cloud-native deployment functionality following crawl_mcp.py methodology."""

    def setUp(self):
        """Step 1: Environment Validation First."""
        self.config = DeploymentConfig(
            deployment_name="test-sme-agents",
            namespace="test-namespace",
            replicas=2,
            min_replicas=1,
            max_replicas=5,
        )
        self.deployment = CloudNativeDeployment(self.config)

    def tearDown(self):
        """Step 6: Resource Management and Cleanup."""
        # Cleanup any resources created during testing
        pass

    async def test_environment_validation(self):
        """Test environment validation functionality."""
        # Test valid environment
        validation_result = await self.deployment.validate_environment()

        assert isinstance(validation_result, dict)
        assert "valid" in validation_result
        assert "errors" in validation_result
        assert "warnings" in validation_result
        assert "tools_available" in validation_result

        # Test validation with missing tools (mocked)
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("kubectl not found")
            validation_result = await self.deployment.validate_environment()
            assert not validation_result["valid"]
            assert len(validation_result["errors"]) > 0

    def test_deployment_config_validation(self):
        """Test deployment configuration validation."""
        # Test valid configuration
        valid_config = DeploymentConfig(
            deployment_name="valid-deployment",
            namespace="valid-namespace",
            replicas=3,
            min_replicas=2,
            max_replicas=10,
        )

        deployment = CloudNativeDeployment(valid_config)
        validation = deployment._validate_deployment_config()
        assert validation["valid"]
        assert len(validation["errors"]) == 0

        # Test invalid configuration
        invalid_config = DeploymentConfig(
            deployment_name="invalid-deployment",
            namespace="invalid-namespace",
            replicas=3,
            min_replicas=10,  # Invalid: min > max
            max_replicas=5,
            target_cpu_utilization=150,  # Invalid: > 100
        )

        deployment = CloudNativeDeployment(invalid_config)
        validation = deployment._validate_deployment_config()
        assert not validation["valid"]
        assert len(validation["errors"]) >= 2

    async def test_kubernetes_manifest_generation(self):
        """Test Kubernetes manifest generation."""
        manifests = await self.deployment.generate_kubernetes_manifests()

        # Verify all expected manifests are generated
        expected_manifests = [
            "namespace",
            "deployment",
            "service",
            "hpa",
            "configmap",
            "secret",
            "ingress",
            "network_policy",
            "rbac",
            "service_monitor",
        ]

        for manifest_name in expected_manifests:
            if manifest_name == "ingress" and not self.config.ingress_enabled:
                continue
            if (
                manifest_name == "network_policy"
                and not self.config.network_policies_enabled
            ):
                continue
            if manifest_name == "rbac" and not self.config.rbac_enabled:
                continue
            if (
                manifest_name == "service_monitor"
                and not self.config.prometheus_enabled
            ):
                continue

            assert manifest_name in manifests
            assert isinstance(manifests[manifest_name], str)

            # Validate YAML syntax
            try:
                if manifest_name == "rbac":
                    # RBAC manifest contains multiple documents
                    yaml_docs = manifests[manifest_name].split("---\n")
                    for doc in yaml_docs:
                        if doc.strip():
                            yaml.safe_load(doc)
                else:
                    yaml.safe_load(manifests[manifest_name])
            except yaml.YAMLError as e:
                self.fail(f"Invalid YAML in {manifest_name} manifest: {e}")

    def test_manifest_content_validation(self):
        """Test specific manifest content validation."""
        # Test namespace manifest
        namespace_manifest = self.deployment._generate_namespace_manifest()
        namespace_data = yaml.safe_load(namespace_manifest)

        assert namespace_data["kind"] == "Namespace"
        assert namespace_data["metadata"]["name"] == self.config.namespace
        assert "app.kubernetes.io/name" in namespace_data["metadata"]["labels"]

        # Test deployment manifest
        deployment_manifest = self.deployment._generate_deployment_manifest()
        deployment_data = yaml.safe_load(deployment_manifest)

        assert deployment_data["kind"] == "Deployment"
        assert deployment_data["spec"]["replicas"] == self.config.replicas
        assert deployment_data["metadata"]["name"] == self.config.deployment_name

        # Verify resource limits
        container = deployment_data["spec"]["template"]["spec"]["containers"][0]
        assert container["resources"]["requests"]["cpu"] == self.config.cpu_request
        assert container["resources"]["limits"]["memory"] == self.config.memory_limit

    async def test_dry_run_deployment(self):
        """Test dry run deployment functionality."""
        with patch("subprocess.run") as mock_run:
            # Mock successful kubectl dry-run
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = (
                "deployment.apps/test-sme-agents configured (dry run)"
            )

            # Generate manifests first
            await self.deployment.generate_kubernetes_manifests()

            # Test dry run deployment
            result = await self.deployment.deploy_to_kubernetes(dry_run=True)

            assert result["success"]
            assert len(result["manifests_applied"]) > 0
            assert len(result["errors"]) == 0

            # Verify kubectl was called with --dry-run=client
            mock_run.assert_called()
            call_args = mock_run.call_args[0][0]
            assert "--dry-run=client" in call_args

    async def test_deployment_status_monitoring(self):
        """Test deployment status monitoring."""
        with patch("subprocess.run") as mock_run:
            # Mock kubectl get deployment response
            mock_status = {
                "status": {
                    "replicas": 3,
                    "readyReplicas": 3,
                    "availableReplicas": 3,
                }
            }
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(mock_status)

            status = await self.deployment.get_deployment_status()

            assert status["replicas_ready"] == 3
            assert "last_health_check" in status

    async def test_cleanup_deployment(self):
        """Test deployment cleanup functionality."""
        # Set up some mock manifests
        self.deployment.k8s_templates = {
            "deployment": "apiVersion: apps/v1\nkind: Deployment\n...",
            "service": "apiVersion: v1\nkind: Service\n...",
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "deployment.apps 'test-sme-agents' deleted"

            cleanup_result = await self.deployment.cleanup_deployment()

            assert cleanup_result["success"]
            assert len(cleanup_result["resources_deleted"]) > 0
            assert len(cleanup_result["errors"]) == 0


class TestEnterpriseIntegration(unittest.TestCase):
    """Test enterprise integration functionality following crawl_mcp.py methodology."""

    def setUp(self):
        """Step 1: Environment Validation First."""
        self.integration_manager = EnterpriseIntegrationManager()

        self.sap_config = IntegrationConfig(
            integration_name="test_sap",
            system_type="SAP",
            endpoint_url="https://sap.test.com:8000",
            auth_type="basic",
            username="test_user",
            password="test_password",
        )

        self.scada_config = IntegrationConfig(
            integration_name="test_scada",
            system_type="SCADA",
            endpoint_url="https://scada.test.com:8080",
            auth_type="bearer",
            token="test_token",
        )

    def tearDown(self):
        """Step 6: Resource Management and Cleanup."""
        # Cleanup integrations
        asyncio.run(self.integration_manager.cleanup_integrations())

    async def test_environment_validation(self):
        """Test enterprise integration environment validation."""
        validation_result = await self.integration_manager.validate_environment()

        assert isinstance(validation_result, dict)
        assert "valid" in validation_result
        assert "integrations_available" in validation_result
        assert "network_connectivity" in validation_result

        # Check integration availability checks
        integrations = validation_result["integrations_available"]
        assert "SAP" in integrations
        assert "SCADA" in integrations
        assert "ORACLE" in integrations

    def test_integration_config_validation(self):
        """Test integration configuration validation."""
        # Test valid SAP configuration
        assert self.sap_config.system_type == "SAP"
        assert self.sap_config.auth_type == "basic"

        # Test invalid configuration
        with self.assertRaises(ValueError):
            IntegrationConfig(
                integration_name="invalid",
                system_type="INVALID_TYPE",
                endpoint_url="invalid-url",  # Invalid URL format
                auth_type="invalid_auth",  # Invalid auth type
            )

    async def test_sap_integration(self):
        """Test SAP integration functionality."""
        sap_integration = SAPIntegration(self.sap_config)

        # Test connection with mocked HTTP client
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"system": "SAP Test System"}
            mock_response.headers = {"X-Response-Time": "100ms"}

            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
                mock_response
            )

            # Test connection
            connection_result = await sap_integration.connect()
            assert connection_result
            assert sap_integration.connection_status == "connected"

            # Test data retrieval
            query = {
                "entity_set": "BusinessPartners",
                "filters": {"CompanyCode": "1000"},
                "select": ["BusinessPartner", "BusinessPartnerName"],
            }

            mock_response.json.return_value = {
                "d": {
                    "results": [
                        {
                            "BusinessPartner": "1000",
                            "BusinessPartnerName": "Test Partner",
                        }
                    ]
                }
            }

            result = await sap_integration.get_data(query)
            assert result["success"]
            assert result["record_count"] == 1

            # Test cleanup
            await sap_integration.disconnect()
            assert sap_integration.connection_status == "disconnected"

    async def test_scada_integration(self):
        """Test SCADA integration functionality."""
        scada_integration = SCADAIntegration(self.scada_config)

        # Test connection with mocked HTTP client
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"status": "online", "historian": "PI"}

            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
                mock_response
            )

            # Test connection
            connection_result = await scada_integration.connect()
            assert connection_result
            assert scada_integration.connection_status == "connected"

            # Test historical data retrieval
            query = {
                "tags": ["TAG001", "TAG002"],
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T01:00:00Z",
                "interval": "5m",
            }

            mock_response.json.return_value = {
                "tags": [
                    {
                        "name": "TAG001",
                        "values": [
                            {"timestamp": "2024-01-01T00:00:00Z", "value": 100.0}
                        ],
                    },
                    {
                        "name": "TAG002",
                        "values": [
                            {"timestamp": "2024-01-01T00:00:00Z", "value": 200.0}
                        ],
                    },
                ]
            }

            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
                mock_response
            )

            result = await scada_integration.get_historical_data(query)
            assert result["success"]
            assert result["tag_count"] == 2
            assert result["data_points"] == 2

            # Test real-time data
            realtime_result = await scada_integration.get_real_time_data(
                ["TAG001", "TAG002"]
            )
            assert realtime_result["success"]

            # Test cleanup
            await scada_integration.disconnect()
            assert scada_integration.connection_status == "disconnected"

    async def test_integration_manager(self):
        """Test integration manager functionality."""
        # Test registration
        with patch.object(SAPIntegration, "connect", return_value=True):
            registration_result = await self.integration_manager.register_integration(
                "test_sap", self.sap_config
            )

            assert registration_result["success"]
            assert registration_result["integration_name"] == "test_sap"
            assert "test_sap" in self.integration_manager.integrations

        # Test query execution
        with patch.object(SAPIntegration, "get_data") as mock_get_data:
            mock_get_data.return_value = {"success": True, "data": {"test": "data"}}

            query_result = await self.integration_manager.execute_integration_query(
                "test_sap", {"entity_set": "TestEntity"}
            )

            assert query_result["success"]
            assert self.integration_manager.stats["successful_operations"] == 1

        # Test status check
        status = await self.integration_manager.get_integration_status()
        assert status["success"]
        assert "test_sap" in status["integrations"]


class TestPhase163CLI(unittest.TestCase):
    """Test Phase 16.3 CLI functionality following crawl_mcp.py methodology."""

    def setUp(self):
        """Step 1: Environment Validation First."""
        self.cli_manager = Phase163CLIManager()

    def tearDown(self):
        """Step 6: Resource Management and Cleanup."""
        # Cleanup any resources created during testing
        pass

    async def test_environment_validation(self):
        """Test CLI environment validation."""
        with (
            patch.object(
                self.cli_manager.cloud_deployment, "validate_environment"
            ) as mock_cloud_val,
            patch.object(
                self.cli_manager.integration_manager, "validate_environment"
            ) as mock_int_val,
            patch("subprocess.run") as mock_subprocess,
        ):
            # Mock successful validation
            mock_cloud_val.return_value = {"valid": True, "errors": [], "warnings": []}
            mock_int_val.return_value = {"valid": True, "errors": [], "warnings": []}
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "kubectl version v1.28.0"

            validation_result = await self.cli_manager.validate_environment()

            assert validation_result["valid"]
            assert "components" in validation_result
            assert "tools" in validation_result

    async def test_cloud_deployment_workflow(self):
        """Test complete cloud deployment workflow."""
        with (
            patch.object(
                self.cli_manager.cloud_deployment, "generate_kubernetes_manifests"
            ) as mock_gen,
            patch.object(
                self.cli_manager.cloud_deployment, "deploy_to_kubernetes"
            ) as mock_deploy,
        ):
            # Mock successful manifest generation
            mock_gen.return_value = {
                "namespace": "mock_namespace_manifest",
                "deployment": "mock_deployment_manifest",
                "service": "mock_service_manifest",
            }

            # Mock successful deployment
            mock_deploy.return_value = {
                "success": True,
                "deployment_time": 30.5,
                "manifests_applied": ["namespace", "deployment", "service"],
                "errors": [],
                "warnings": [],
            }

            # Test deployment
            result = await self.cli_manager.deploy_to_cloud("standard", dry_run=True)

            assert result["success"]
            assert result["deployment_time"] == 30.5
            assert len(result["manifests_applied"]) == 3

            # Verify configuration was created correctly
            mock_gen.assert_called_once()
            mock_deploy.assert_called_once_with(dry_run=True)

    def test_deployment_config_creation(self):
        """Test deployment configuration creation for different complexity levels."""
        # Test basic complexity
        basic_config = self.cli_manager._create_deployment_config("basic")
        assert basic_config.replicas == 2
        assert basic_config.min_replicas == 1
        assert basic_config.max_replicas == 5
        assert basic_config.cpu_request == "250m"
        assert basic_config.memory_limit == "2Gi"

        # Test enterprise complexity
        enterprise_config = self.cli_manager._create_deployment_config("enterprise")
        assert enterprise_config.replicas == 10
        assert enterprise_config.min_replicas == 5
        assert enterprise_config.max_replicas == 50
        assert enterprise_config.cpu_request == "2000m"
        assert enterprise_config.memory_limit == "16Gi"

    async def test_enterprise_integration_workflow(self):
        """Test enterprise integration workflow."""
        with patch.object(
            self.cli_manager.integration_manager, "register_integration"
        ) as mock_register:
            mock_register.return_value = {
                "success": True,
                "integration_name": "test_sap",
                "system_type": "SAP",
                "status": "active",
            }

            config_data = {
                "endpoint_url": "https://sap.test.com:8000",
                "username": "test_user",
                "password": "test_password",
            }

            result = await self.cli_manager.register_enterprise_integration(
                "SAP", config_data
            )

            assert result["success"]
            assert result["integration_name"] == "test_sap"
            mock_register.assert_called_once()


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios following crawl_mcp.py methodology."""

    async def test_end_to_end_deployment_scenario(self):
        """Test complete end-to-end deployment scenario."""
        # Step 1: Environment validation
        cli_manager = Phase163CLIManager()

        with (
            patch.multiple(
                "subprocess.run",
                return_value=MagicMock(returncode=0, stdout="version info"),
            ),
            patch.object(
                cli_manager.cloud_deployment,
                "validate_environment",
                return_value={"valid": True, "errors": [], "warnings": []},
            ),
            patch.object(
                cli_manager.integration_manager,
                "validate_environment",
                return_value={"valid": True, "errors": [], "warnings": []},
            ),
        ):
            validation = await cli_manager.validate_environment()
            assert validation["valid"]

        # Step 2: Cloud deployment
        with (
            patch.object(
                cli_manager.cloud_deployment,
                "generate_kubernetes_manifests",
                return_value={"deployment": "mock_manifest"},
            ),
            patch.object(
                cli_manager.cloud_deployment,
                "deploy_to_kubernetes",
                return_value={"success": True, "manifests_applied": ["deployment"]},
            ),
        ):
            deployment_result = await cli_manager.deploy_to_cloud(
                "standard", dry_run=True
            )
            assert deployment_result["success"]

        # Step 3: Enterprise integration
        with patch.object(
            cli_manager.integration_manager,
            "register_integration",
            return_value={"success": True, "integration_name": "test_integration"},
        ):
            integration_result = await cli_manager.register_enterprise_integration(
                "SAP", {"endpoint_url": "https://test.com"}
            )
            assert integration_result["success"]

        # Step 4: Status monitoring
        with patch.object(
            cli_manager.cloud_deployment,
            "get_deployment_status",
            return_value={"status": "deployed", "replicas_ready": 3},
        ):
            status_result = await cli_manager.get_kubernetes_status()
            assert status_result["success"]

        # Step 5: Cleanup
        with (
            patch.object(
                cli_manager.cloud_deployment,
                "cleanup_deployment",
                return_value={"success": True, "resources_deleted": ["deployment"]},
            ),
            patch.object(
                cli_manager.integration_manager,
                "cleanup_integrations",
                return_value={
                    "success": True,
                    "integrations_cleaned": ["test_integration"],
                },
            ),
        ):
            cleanup_result = await cli_manager.cleanup_resources()
            assert cleanup_result["success"]


class TestPerformanceAndScalability(unittest.TestCase):
    """Test performance and scalability following crawl_mcp.py methodology."""

    def test_deployment_config_scaling(self):
        """Test deployment configuration scaling across complexity levels."""
        complexities = ["basic", "standard", "advanced", "enterprise"]
        cli_manager = Phase163CLIManager()

        previous_replicas = 0
        for complexity in complexities:
            config = cli_manager._create_deployment_config(complexity)

            # Verify scaling progression
            assert config.replicas > previous_replicas
            assert config.max_replicas >= config.min_replicas
            assert config.min_replicas <= config.replicas <= config.max_replicas

            previous_replicas = config.replicas

    async def test_concurrent_integration_operations(self):
        """Test concurrent enterprise integration operations."""
        integration_manager = EnterpriseIntegrationManager()

        # Mock multiple concurrent integrations
        configs = [
            IntegrationConfig(
                integration_name=f"test_integration_{i}",
                system_type="SAP",
                endpoint_url=f"https://sap{i}.test.com",
                auth_type="basic",
                username="test_user",
                password="test_password",
            )
            for i in range(5)
        ]

        with patch.object(SAPIntegration, "connect", return_value=True):
            # Register integrations concurrently
            tasks = [
                integration_manager.register_integration(
                    config.integration_name, config
                )
                for config in configs
            ]

            results = await asyncio.gather(*tasks)

            # Verify all registrations succeeded
            for result in results:
                assert result["success"]

            # Verify statistics
            assert integration_manager.stats["total_integrations"] == 5
            assert integration_manager.stats["active_connections"] == 5


def run_phase_16_3_tests() -> dict[str, Any]:
    """Run comprehensive Phase 16.3 test suite following crawl_mcp.py methodology."""
    print("🧪 Running Phase 16.3 Test Suite...")

    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_categories": {},
        "execution_time": 0,
        "success_rate": 0.0,
    }

    start_time = time.time()

    try:
        # Test categories to run
        test_categories = [
            ("Cloud Deployment", TestCloudNativeDeployment),
            ("Enterprise Integration", TestEnterpriseIntegration),
            ("CLI Functionality", TestPhase163CLI),
            ("Integration Scenarios", TestIntegrationScenarios),
            ("Performance & Scalability", TestPerformanceAndScalability),
        ]

        for category_name, test_class in test_categories:
            print(f"  🔍 Testing {category_name}...")

            # Create test suite
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)

            # Run tests
            runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
            result = runner.run(suite)

            # Record results
            category_results = {
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "success_rate": (
                    (result.testsRun - len(result.failures) - len(result.errors))
                    / result.testsRun
                    if result.testsRun > 0
                    else 0
                ),
            }

            test_results["test_categories"][category_name] = category_results
            test_results["total_tests"] += result.testsRun
            test_results["passed_tests"] += (
                result.testsRun - len(result.failures) - len(result.errors)
            )
            test_results["failed_tests"] += len(result.failures) + len(result.errors)

            print(
                f"    ✅ {category_results['tests_run'] - category_results['failures'] - category_results['errors']}/{category_results['tests_run']} passed"
            )

        # Calculate overall metrics
        test_results["execution_time"] = time.time() - start_time
        test_results["success_rate"] = (
            test_results["passed_tests"] / test_results["total_tests"]
            if test_results["total_tests"] > 0
            else 0
        )

        # Display summary
        print("\n📊 PHASE 16.3 TEST REPORT")
        print("📈 Overall Results:")
        print(f"   Total Tests: {test_results['total_tests']}")
        print(f"   Passed: {test_results['passed_tests']}")
        print(f"   Failed: {test_results['failed_tests']}")
        print(f"   Success Rate: {test_results['success_rate']:.1%}")
        print(f"   Execution Time: {test_results['execution_time']:.2f} seconds")

        print("\n📋 Category Breakdown:")
        for category, results in test_results["test_categories"].items():
            status = (
                "✅"
                if results["success_rate"] == 1.0
                else "⚠️" if results["success_rate"] > 0.5 else "❌"
            )
            print(
                f"   {status} {category}: {results['tests_run'] - results['failures'] - results['errors']}/{results['tests_run']}"
            )

        return test_results

    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        test_results["execution_time"] = time.time() - start_time
        test_results["error"] = str(e)
        return test_results


# Example usage
if __name__ == "__main__":
    # Run async tests
    async def run_async_tests():
        test_cloud = TestCloudNativeDeployment()
        test_cloud.setUp()

        await test_cloud.test_environment_validation()
        await test_cloud.test_kubernetes_manifest_generation()

        print("✅ Async tests completed")

    # Run the test suite
    asyncio.run(run_async_tests())

    # Run complete test suite
    results = run_phase_16_3_tests()
    print(
        f"\n🎯 Phase 16.3 testing completed with {results['success_rate']:.1%} success rate"
    )
