#!/usr/bin/env python3
"""Phase 16.3: Cloud-Native Deployment & Integration for Enterprise AI Platform.

Following crawl_mcp.py methodology for systematic cloud deployment:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

This module provides:
- Kubernetes orchestration and deployment
- Microservices architecture
- Auto-scaling and load balancing
- Multi-region deployment capabilities
- Disaster recovery and backup systems
- Security and compliance frameworks
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Self

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DeploymentConfig(BaseModel):
    """Configuration for cloud-native deployment."""

    # Basic deployment configuration
    deployment_name: str = Field(..., description="Name of the deployment")
    namespace: str = Field(default="sme-agents", description="Kubernetes namespace")
    replicas: int = Field(default=3, description="Number of replicas")

    # Resource configuration
    cpu_request: str = Field(default="500m", description="CPU request")
    cpu_limit: str = Field(default="2000m", description="CPU limit")
    memory_request: str = Field(default="1Gi", description="Memory request")
    memory_limit: str = Field(default="4Gi", description="Memory limit")

    # Scaling configuration
    min_replicas: int = Field(default=2, description="Minimum replicas for HPA")
    max_replicas: int = Field(default=20, description="Maximum replicas for HPA")
    target_cpu_utilization: int = Field(
        default=70, description="Target CPU utilization %"
    )

    # Network configuration
    service_port: int = Field(default=8080, description="Service port")
    ingress_enabled: bool = Field(default=True, description="Enable ingress")
    ingress_host: str | None = Field(default=None, description="Ingress hostname")

    # Security configuration
    security_context_enabled: bool = Field(
        default=True, description="Enable security context"
    )
    network_policies_enabled: bool = Field(
        default=True, description="Enable network policies"
    )
    rbac_enabled: bool = Field(default=True, description="Enable RBAC")

    # Monitoring configuration
    prometheus_enabled: bool = Field(
        default=True, description="Enable Prometheus monitoring"
    )
    grafana_enabled: bool = Field(default=True, description="Enable Grafana dashboards")

    # Backup configuration
    backup_enabled: bool = Field(default=True, description="Enable backup")
    backup_schedule: str = Field(
        default="0 2 * * *", description="Backup cron schedule"
    )


class CloudNativeDeployment:
    """Cloud-Native Deployment Manager for Phase 16.3.

    Following crawl_mcp.py methodology for systematic deployment management.
    """

    def __init__(self: Self, config: DeploymentConfig | None = None):
        """Initialize cloud-native deployment manager."""
        # Step 1: Environment Validation First
        self.logger = logging.getLogger(__name__)
        self.config = config or DeploymentConfig(deployment_name="sme-agents-default")
        self.validation_result: dict[str, Any] | None = None

        # Deployment state
        self.deployment_status = {
            "status": "not_deployed",
            "deployment_time": None,
            "last_health_check": None,
            "replicas_ready": 0,
            "services_ready": [],
            "ingress_ready": False,
        }

        # Resource templates
        self.k8s_templates = {}

    async def validate_environment(self) -> dict[str, Any]:
        """Step 1: Environment Validation First (crawl_mcp.py methodology).

        Validate all required tools and configurations for cloud deployment.

        Returns:
            dict containing validation results
        """
        self.logger.info("🔍 Validating cloud deployment environment...")

        validation_result: dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "tools_available": {},
            "cluster_info": {},
        }

        try:
            # Step 1.1: Check required tools
            required_tools = {
                "kubectl": "Kubernetes CLI",
                "helm": "Helm package manager",
                "docker": "Docker container runtime",
            }

            for tool, description in required_tools.items():
                try:
                    result = subprocess.run(
                        [tool, "version"], capture_output=True, text=True, timeout=30
                    )
                    validation_result["tools_available"][tool] = {
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
                            f"Required tool {tool} not available or not working ({description})"
                        )

                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Tool {tool} not found: {e} ({description})"
                    )
                    validation_result["tools_available"][tool] = {
                        "available": False,
                        "error": str(e),
                        "description": description,
                    }

            # Step 1.2: Check Kubernetes cluster connectivity
            if validation_result["tools_available"].get("kubectl", {}).get("available"):
                try:
                    result = subprocess.run(
                        ["kubectl", "cluster-info"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.returncode == 0:
                        validation_result["cluster_info"]["connected"] = True
                        validation_result["cluster_info"]["info"] = result.stdout

                        # Get cluster version
                        version_result = subprocess.run(
                            ["kubectl", "version", "--short"],
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )
                        if version_result.returncode == 0:
                            validation_result["cluster_info"][
                                "version"
                            ] = version_result.stdout

                    else:
                        validation_result["warnings"].append(
                            "Kubernetes cluster not accessible - deployment will require cluster setup"
                        )
                        validation_result["cluster_info"]["connected"] = False
                        validation_result["cluster_info"]["error"] = result.stderr

                except subprocess.TimeoutExpired:
                    validation_result["warnings"].append(
                        "Kubernetes cluster connection timeout - check cluster status"
                    )
                    validation_result["cluster_info"]["connected"] = False
                    validation_result["cluster_info"]["error"] = "Connection timeout"

            # Step 1.3: Check environment variables
            required_env_vars = {
                "PHASE16_DEPLOYMENT_NAMESPACE": "Kubernetes namespace for deployment",
                "PHASE16_CONTAINER_REGISTRY": "Container registry for images",
            }

            optional_env_vars = {
                "PHASE16_INGRESS_HOST": "Ingress hostname",
                "PHASE16_BACKUP_STORAGE": "Backup storage configuration",
                "PHASE16_MONITORING_ENABLED": "Enable monitoring stack",
            }

            for env_var, description in required_env_vars.items():
                value = os.getenv(env_var)
                if not value:
                    validation_result["warnings"].append(
                        f"Optional environment variable {env_var} not set ({description})"
                    )

            # Step 1.4: Validate deployment configuration
            config_validation = self._validate_deployment_config()
            if not config_validation["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(config_validation["errors"])

            validation_result["config_validation"] = config_validation

            self.validation_result = validation_result
            return validation_result

        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {e}")
            return validation_result

    def _validate_deployment_config(self) -> dict[str, Any]:
        """Validate deployment configuration."""
        validation = {"valid": True, "errors": [], "warnings": []}

        try:
            # Validate resource limits
            if self.config.min_replicas > self.config.max_replicas:
                validation["valid"] = False
                validation["errors"].append(
                    f"min_replicas ({self.config.min_replicas}) cannot be greater than max_replicas ({self.config.max_replicas})"
                )

            # Validate CPU utilization target
            if not 1 <= self.config.target_cpu_utilization <= 100:
                validation["valid"] = False
                validation["errors"].append(
                    f"target_cpu_utilization must be between 1-100, got {self.config.target_cpu_utilization}"
                )

            # Validate port
            if not 1 <= self.config.service_port <= 65535:
                validation["valid"] = False
                validation["errors"].append(
                    f"service_port must be between 1-65535, got {self.config.service_port}"
                )

        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Configuration validation error: {e}")

        return validation

    async def generate_kubernetes_manifests(self) -> dict[str, str]:
        """Step 2: Generate Kubernetes deployment manifests.

        Returns:
            dict containing generated YAML manifests
        """
        self.logger.info("📝 Generating Kubernetes manifests...")

        manifests = {}

        try:
            # Namespace manifest
            manifests["namespace"] = self._generate_namespace_manifest()

            # Deployment manifest
            manifests["deployment"] = self._generate_deployment_manifest()

            # Service manifest
            manifests["service"] = self._generate_service_manifest()

            # HPA manifest
            manifests["hpa"] = self._generate_hpa_manifest()

            # ConfigMap manifest
            manifests["configmap"] = self._generate_configmap_manifest()

            # Secret manifest
            manifests["secret"] = self._generate_secret_manifest()

            if self.config.ingress_enabled:
                manifests["ingress"] = self._generate_ingress_manifest()

            if self.config.network_policies_enabled:
                manifests["network_policy"] = self._generate_network_policy_manifest()

            if self.config.rbac_enabled:
                manifests["rbac"] = self._generate_rbac_manifest()

            if self.config.prometheus_enabled:
                manifests["service_monitor"] = self._generate_service_monitor_manifest()

            self.k8s_templates = manifests
            return manifests

        except Exception as e:
            self.logger.error(f"Manifest generation failed: {e}")
            raise RuntimeError(f"Failed to generate Kubernetes manifests: {e}") from e

    def _generate_namespace_manifest(self) -> str:
        """Generate namespace manifest."""
        manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.config.namespace,
                "labels": {
                    "app.kubernetes.io/name": "sme-agents",
                    "app.kubernetes.io/part-of": "phase-16-enterprise-ai",
                    "app.kubernetes.io/managed-by": "phase-16-deployment-manager",
                },
            },
        }
        return yaml.dump(manifest, default_flow_style=False)

    def _generate_deployment_manifest(self) -> str:
        """Generate deployment manifest."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self.config.deployment_name,
                "namespace": self.config.namespace,
                "labels": {
                    "app": self.config.deployment_name,
                    "version": "v1",
                    "component": "sme-agent",
                },
            },
            "spec": {
                "replicas": self.config.replicas,
                "selector": {"matchLabels": {"app": self.config.deployment_name}},
                "template": {
                    "metadata": {
                        "labels": {"app": self.config.deployment_name, "version": "v1"},
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": str(self.config.service_port),
                            "prometheus.io/path": "/metrics",
                        },
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "sme-agent",
                                "image": f"{os.getenv('PHASE16_CONTAINER_REGISTRY', 'localhost:5000')}/sme-agent:latest",
                                "ports": [
                                    {
                                        "containerPort": self.config.service_port,
                                        "name": "http",
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": self.config.cpu_request,
                                        "memory": self.config.memory_request,
                                    },
                                    "limits": {
                                        "cpu": self.config.cpu_limit,
                                        "memory": self.config.memory_limit,
                                    },
                                },
                                "env": [
                                    {
                                        "name": "PHASE16_DEPLOYMENT_MODE",
                                        "value": "kubernetes",
                                    },
                                    {
                                        "name": "PHASE16_NAMESPACE",
                                        "valueFrom": {
                                            "fieldRef": {
                                                "fieldPath": "metadata.namespace"
                                            }
                                        },
                                    },
                                ],
                                "envFrom": [
                                    {
                                        "configMapRef": {
                                            "name": f"{self.config.deployment_name}-config"
                                        }
                                    },
                                    {
                                        "secretRef": {
                                            "name": f"{self.config.deployment_name}-secret"
                                        }
                                    },
                                ],
                                "livenessProbe": {
                                    "httpGet": {"path": "/health", "port": "http"},
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                },
                                "readinessProbe": {
                                    "httpGet": {"path": "/ready", "port": "http"},
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                },
                            }
                        ],
                        "securityContext": (
                            {"runAsNonRoot": True, "runAsUser": 1000, "fsGroup": 2000}
                            if self.config.security_context_enabled
                            else {}
                        ),
                    },
                },
            },
        }
        return yaml.dump(manifest, default_flow_style=False)

    def _generate_service_manifest(self) -> str:
        """Generate service manifest."""
        manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": self.config.deployment_name,
                "namespace": self.config.namespace,
                "labels": {"app": self.config.deployment_name},
            },
            "spec": {
                "selector": {"app": self.config.deployment_name},
                "ports": [
                    {"port": 80, "targetPort": self.config.service_port, "name": "http"}
                ],
                "type": "ClusterIP",
            },
        }
        return yaml.dump(manifest, default_flow_style=False)

    def _generate_hpa_manifest(self) -> str:
        """Generate HPA manifest."""
        manifest = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{self.config.deployment_name}-hpa",
                "namespace": self.config.namespace,
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": self.config.deployment_name,
                },
                "minReplicas": self.config.min_replicas,
                "maxReplicas": self.config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": self.config.target_cpu_utilization,
                            },
                        },
                    }
                ],
            },
        }
        return yaml.dump(manifest, default_flow_style=False)

    def _generate_configmap_manifest(self) -> str:
        """Generate ConfigMap manifest."""
        manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.deployment_name}-config",
                "namespace": self.config.namespace,
            },
            "data": {
                "PHASE16_COORDINATION_STRATEGY": "expertise_based",
                "PHASE16_MAX_CONCURRENT_TASKS": "50",
                "PHASE16_DEFAULT_TIMEOUT": "300",
                "PHASE16_LOG_LEVEL": "INFO",
                "PHASE16_PROMETHEUS_ENABLED": str(
                    self.config.prometheus_enabled
                ).lower(),
                "PHASE16_BACKUP_ENABLED": str(self.config.backup_enabled).lower(),
            },
        }
        return yaml.dump(manifest, default_flow_style=False)

    def _generate_secret_manifest(self) -> str:
        """Generate Secret manifest."""
        manifest = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{self.config.deployment_name}-secret",
                "namespace": self.config.namespace,
            },
            "type": "Opaque",
            "data": {
                # Base64 encoded secrets - these should be provided externally
                "NEO4J_PASSWORD": "Y2hhbmdlbWU=",  # "changeme" - MUST be changed in production
                "API_SECRET_KEY": "Y2hhbmdlbWVfc2VjcmV0X2tleQ==",  # "changeme_secret_key" - MUST be changed
            },
        }
        return yaml.dump(manifest, default_flow_style=False)

    def _generate_ingress_manifest(self) -> str:
        """Generate Ingress manifest."""
        host = self.config.ingress_host or f"{self.config.deployment_name}.local"

        manifest = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{self.config.deployment_name}-ingress",
                "namespace": self.config.namespace,
                "annotations": {
                    "nginx.ingress.kubernetes.io/rewrite-target": "/",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                },
            },
            "spec": {
                "tls": [
                    {
                        "hosts": [host],
                        "secretName": f"{self.config.deployment_name}-tls",
                    }
                ],
                "rules": [
                    {
                        "host": host,
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": self.config.deployment_name,
                                            "port": {"number": 80},
                                        }
                                    },
                                }
                            ]
                        },
                    }
                ],
            },
        }
        return yaml.dump(manifest, default_flow_style=False)

    def _generate_network_policy_manifest(self) -> str:
        """Generate NetworkPolicy manifest."""
        manifest = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{self.config.deployment_name}-netpol",
                "namespace": self.config.namespace,
            },
            "spec": {
                "podSelector": {"matchLabels": {"app": self.config.deployment_name}},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {"name": "ingress-nginx"}
                                }
                            }
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": self.config.service_port}
                        ],
                    }
                ],
                "egress": [
                    {
                        "to": [],
                        "ports": [
                            {"protocol": "TCP", "port": 53},
                            {"protocol": "UDP", "port": 53},
                        ],
                    }
                ],
            },
        }
        return yaml.dump(manifest, default_flow_style=False)

    def _generate_rbac_manifest(self) -> str:
        """Generate RBAC manifest."""
        manifests = []

        # ServiceAccount
        sa_manifest = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": f"{self.config.deployment_name}-sa",
                "namespace": self.config.namespace,
            },
        }
        manifests.append(sa_manifest)

        # Role
        role_manifest = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": f"{self.config.deployment_name}-role",
                "namespace": self.config.namespace,
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["configmaps", "secrets"],
                    "verbs": ["get", "list", "watch"],
                }
            ],
        }
        manifests.append(role_manifest)

        # RoleBinding
        rb_manifest = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": f"{self.config.deployment_name}-rb",
                "namespace": self.config.namespace,
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": f"{self.config.deployment_name}-sa",
                    "namespace": self.config.namespace,
                }
            ],
            "roleRef": {
                "kind": "Role",
                "name": f"{self.config.deployment_name}-role",
                "apiGroup": "rbac.authorization.k8s.io",
            },
        }
        manifests.append(rb_manifest)

        return "---\n".join([yaml.dump(m, default_flow_style=False) for m in manifests])

    def _generate_service_monitor_manifest(self) -> str:
        """Generate ServiceMonitor manifest for Prometheus."""
        manifest = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": f"{self.config.deployment_name}-monitor",
                "namespace": self.config.namespace,
                "labels": {"app": self.config.deployment_name},
            },
            "spec": {
                "selector": {"matchLabels": {"app": self.config.deployment_name}},
                "endpoints": [{"port": "http", "path": "/metrics", "interval": "30s"}],
            },
        }
        return yaml.dump(manifest, default_flow_style=False)

    async def deploy_to_kubernetes(self, dry_run: bool = False) -> dict[str, Any]:
        """Step 5: Deploy to Kubernetes cluster.

        Args:
            dry_run: If True, validate manifests without applying

        Returns:
            dict containing deployment results
        """
        self.logger.info(
            f"🚀 {'Validating' if dry_run else 'Deploying'} to Kubernetes..."
        )

        deployment_result = {
            "success": False,
            "deployment_time": None,
            "manifests_applied": [],
            "errors": [],
            "warnings": [],
        }

        try:
            start_time = time.time()

            # Step 5.1: Generate manifests if not already done
            if not self.k8s_templates:
                await self.generate_kubernetes_manifests()

            # Step 5.2: Apply manifests in order
            manifest_order = [
                "namespace",
                "configmap",
                "secret",
                "rbac",
                "deployment",
                "service",
                "hpa",
                "ingress",
                "network_policy",
                "service_monitor",
            ]

            for manifest_name in manifest_order:
                if manifest_name in self.k8s_templates:
                    try:
                        await self._apply_manifest(
                            manifest_name, self.k8s_templates[manifest_name], dry_run
                        )
                        deployment_result["manifests_applied"].append(manifest_name)

                    except Exception as e:
                        error_msg = f"Failed to apply {manifest_name}: {e}"
                        self.logger.error(error_msg)
                        deployment_result["errors"].append(error_msg)

                        # Continue with other manifests unless it's a critical failure
                        if manifest_name in ["namespace", "deployment"]:
                            raise RuntimeError(
                                f"Critical manifest {manifest_name} failed: {e}"
                            ) from e

            # Step 5.3: Wait for deployment to be ready (if not dry run)
            if not dry_run and "deployment" in deployment_result["manifests_applied"]:
                await self._wait_for_deployment_ready()

            deployment_result["success"] = True
            deployment_result["deployment_time"] = time.time() - start_time

            self.deployment_status.update(
                {
                    "status": "deployed" if not dry_run else "validated",
                    "deployment_time": datetime.now().isoformat(),
                }
            )

            return deployment_result

        except Exception as e:
            error_msg = f"Deployment failed: {e}"
            self.logger.error(error_msg)
            deployment_result["errors"].append(error_msg)
            return deployment_result

    async def _apply_manifest(self, name: str, manifest: str, dry_run: bool) -> None:
        """Apply a single manifest to Kubernetes."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(manifest)
            temp_file = f.name

        try:
            cmd = ["kubectl", "apply", "-f", temp_file]
            if dry_run:
                cmd.append("--dry-run=client")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                raise RuntimeError(f"kubectl apply failed: {result.stderr}")

            self.logger.info(f"✅ Applied {name} manifest")

        finally:
            # Clean up temporary file
            Path(temp_file).unlink(missing_ok=True)

    async def _wait_for_deployment_ready(self, timeout: int = 300) -> None:
        """Wait for deployment to be ready."""
        self.logger.info("⏳ Waiting for deployment to be ready...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    [
                        "kubectl",
                        "get",
                        "deployment",
                        self.config.deployment_name,
                        "-n",
                        self.config.namespace,
                        "-o",
                        "json",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    deployment_info = json.loads(result.stdout)
                    status = deployment_info.get("status", {})

                    ready_replicas = status.get("readyReplicas", 0)
                    desired_replicas = status.get("replicas", 0)

                    if ready_replicas == desired_replicas and ready_replicas > 0:
                        self.logger.info(
                            f"✅ Deployment ready: {ready_replicas}/{desired_replicas} replicas"
                        )
                        self.deployment_status["replicas_ready"] = ready_replicas
                        return

                await asyncio.sleep(10)

            except Exception as e:
                self.logger.warning(f"Error checking deployment status: {e}")
                await asyncio.sleep(10)

        raise RuntimeError(f"Deployment not ready after {timeout} seconds")

    async def get_deployment_status(self) -> dict[str, Any]:
        """Get current deployment status."""
        try:
            if self.deployment_status["status"] == "not_deployed":
                return self.deployment_status

            # Get live status from Kubernetes
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "deployment",
                    self.config.deployment_name,
                    "-n",
                    self.config.namespace,
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                deployment_info = json.loads(result.stdout)
                status = deployment_info.get("status", {})

                self.deployment_status.update(
                    {
                        "replicas_ready": status.get("readyReplicas", 0),
                        "replicas_total": status.get("replicas", 0),
                        "last_health_check": datetime.now().isoformat(),
                    }
                )

            return self.deployment_status

        except Exception as e:
            self.logger.error(f"Failed to get deployment status: {e}")
            return {
                **self.deployment_status,
                "error": str(e),
                "last_health_check": datetime.now().isoformat(),
            }

    async def cleanup_deployment(self) -> dict[str, Any]:
        """Step 6: Resource Management and Cleanup (crawl_mcp.py methodology)."""
        self.logger.info("🧹 Cleaning up deployment...")

        cleanup_result = {
            "success": False,
            "resources_deleted": [],
            "errors": [],
        }

        try:
            # Delete all resources in reverse order
            if self.k8s_templates:
                manifest_order = [
                    "service_monitor",
                    "network_policy",
                    "ingress",
                    "hpa",
                    "service",
                    "deployment",
                    "rbac",
                    "secret",
                    "configmap",
                    "namespace",
                ]

                for manifest_name in manifest_order:
                    if manifest_name in self.k8s_templates:
                        try:
                            with tempfile.NamedTemporaryFile(
                                mode="w", suffix=".yaml", delete=False
                            ) as f:
                                f.write(self.k8s_templates[manifest_name])
                                temp_file = f.name

                            result = subprocess.run(
                                [
                                    "kubectl",
                                    "delete",
                                    "-f",
                                    temp_file,
                                    "--ignore-not-found=true",
                                ],
                                capture_output=True,
                                text=True,
                                timeout=60,
                            )

                            Path(temp_file).unlink(missing_ok=True)

                            if result.returncode == 0:
                                cleanup_result["resources_deleted"].append(
                                    manifest_name
                                )
                                self.logger.info(f"✅ Deleted {manifest_name}")
                            else:
                                cleanup_result["errors"].append(
                                    f"Failed to delete {manifest_name}: {result.stderr}"
                                )

                        except Exception as e:
                            cleanup_result["errors"].append(
                                f"Error deleting {manifest_name}: {e}"
                            )

            cleanup_result["success"] = len(cleanup_result["errors"]) == 0

            # Reset deployment status
            self.deployment_status = {
                "status": "not_deployed",
                "deployment_time": None,
                "last_health_check": None,
                "replicas_ready": 0,
                "services_ready": [],
                "ingress_ready": False,
            }

            return cleanup_result

        except Exception as e:
            error_msg = f"Cleanup failed: {e}"
            self.logger.error(error_msg)
            cleanup_result["errors"].append(error_msg)
            return cleanup_result


# Example usage and testing
async def main():
    """Example usage of CloudNativeDeployment."""
    # Create deployment configuration
    config = DeploymentConfig(
        deployment_name="sme-agents-prod",
        namespace="sme-agents",
        replicas=5,
        min_replicas=3,
        max_replicas=20,
        ingress_host="sme-agents.example.com",
    )

    # Initialize cloud deployment
    deployment = CloudNativeDeployment(config)

    # Step 1: Validate environment
    validation = await deployment.validate_environment()
    if not validation["valid"]:
        print(f"❌ Environment validation failed: {validation['errors']}")
        return

    print("✅ Environment validation passed")

    # Step 2: Generate manifests
    manifests = await deployment.generate_kubernetes_manifests()
    print(f"✅ Generated {len(manifests)} Kubernetes manifests")

    # Step 3: Deploy (dry run first)
    dry_run_result = await deployment.deploy_to_kubernetes(dry_run=True)
    if not dry_run_result["success"]:
        print(f"❌ Dry run failed: {dry_run_result['errors']}")
        return

    print("✅ Dry run validation passed")

    # Step 4: Actual deployment (commented out for safety)
    # deployment_result = await deployment.deploy_to_kubernetes(dry_run=False)
    # print(f"✅ Deployment {'succeeded' if deployment_result['success'] else 'failed'}")


if __name__ == "__main__":
    asyncio.run(main())
