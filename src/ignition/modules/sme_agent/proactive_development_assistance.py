#!/usr/bin/env python3
"""Proactive Development Assistance for SME Agent
Phase 11.4: Advanced SME Agent Features

This module provides intelligent recommendations following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Error handling and user-friendly messages
4. Modular component testing
5. Progressive complexity support
6. Resource management and cleanup

Intelligent Recommendations:
- Architecture pattern suggestions based on project requirements
- Component selection and configuration optimization
- Performance bottleneck identification and resolution
- Maintenance and monitoring strategy development
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ArchitecturePattern:
    """Architecture pattern with implementation recommendations."""

    pattern_id: str
    name: str
    description: str
    pattern_type: str  # MVC, MVP, MVVM, Microservices, etc.
    use_cases: list[str] = field(default_factory=list)
    advantages: list[str] = field(default_factory=list)
    disadvantages: list[str] = field(default_factory=list)
    implementation_steps: list[str] = field(default_factory=list)
    ignition_specific_considerations: list[str] = field(default_factory=list)
    component_recommendations: dict[str, Any] = field(default_factory=dict)
    performance_characteristics: dict[str, Any] = field(default_factory=dict)
    scalability_factors: list[str] = field(default_factory=list)


@dataclass
class ComponentRecommendation:
    """Component selection and configuration recommendation."""

    recommendation_id: str
    component_type: str  # Gateway, Designer, Vision, Perspective, etc.
    component_name: str
    recommended_configuration: dict[str, Any] = field(default_factory=dict)
    optimization_tips: list[str] = field(default_factory=list)
    performance_impact: str = ""  # High, Medium, Low
    resource_requirements: dict[str, Any] = field(default_factory=dict)
    compatibility_notes: list[str] = field(default_factory=list)
    best_practices: list[str] = field(default_factory=list)
    common_pitfalls: list[str] = field(default_factory=list)


@dataclass
class PerformanceBottleneck:
    """Performance bottleneck identification and resolution."""

    bottleneck_id: str
    category: str  # Database, Network, Memory, CPU, etc.
    symptoms: list[str] = field(default_factory=list)
    root_causes: list[str] = field(default_factory=list)
    detection_methods: list[str] = field(default_factory=list)
    resolution_steps: list[str] = field(default_factory=list)
    prevention_measures: list[str] = field(default_factory=list)
    monitoring_recommendations: list[str] = field(default_factory=list)
    performance_metrics: dict[str, Any] = field(default_factory=dict)
    ignition_specific_tools: list[str] = field(default_factory=list)


@dataclass
class MaintenanceStrategy:
    """Maintenance and monitoring strategy."""

    strategy_id: str
    name: str
    description: str
    maintenance_type: str  # Preventive, Predictive, Reactive
    monitoring_components: list[str] = field(default_factory=list)
    maintenance_tasks: list[dict[str, Any]] = field(default_factory=list)
    monitoring_metrics: list[str] = field(default_factory=list)
    alert_thresholds: dict[str, Any] = field(default_factory=dict)
    automation_opportunities: list[str] = field(default_factory=list)
    resource_requirements: dict[str, Any] = field(default_factory=dict)
    compliance_considerations: list[str] = field(default_factory=list)


class ProactiveDevelopmentAssistance:
    """Proactive Development Assistance for SME Agent."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize proactive development assistance."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Recommendation storage
        self.architecture_patterns: list[ArchitecturePattern] = []
        self.component_recommendations: list[ComponentRecommendation] = []
        self.performance_bottlenecks: list[PerformanceBottleneck] = []
        self.maintenance_strategies: list[MaintenanceStrategy] = []

        # Performance tracking
        self.assistance_stats = {
            "architecture_patterns_loaded": 0,
            "component_recommendations_loaded": 0,
            "performance_bottlenecks_loaded": 0,
            "maintenance_strategies_loaded": 0,
            "recommendations_generated": 0,
            "last_update": None,
        }

    async def initialize(self) -> dict[str, Any]:
        """Initialize proactive development assistance following crawl_mcp.py methodology."""
        try:
            # Step 1: Environment validation first
            validation_result = await self._validate_environment()
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": "Environment validation failed",
                    "errors": validation_result["errors"],
                }

            # Step 2: Load assistance data
            await self._load_architecture_patterns()
            await self._load_component_recommendations()
            await self._load_performance_bottlenecks()
            await self._load_maintenance_strategies()

            # Step 3: Update statistics
            self.assistance_stats["last_update"] = datetime.now().isoformat()

            return {
                "status": "success",
                "components_initialized": [
                    "architecture_patterns",
                    "component_recommendations",
                    "performance_bottlenecks",
                    "maintenance_strategies",
                ],
                "statistics": self.assistance_stats,
                "warnings": [],
            }

        except Exception as e:
            self.logger.error(
                f"Proactive development assistance initialization failed: {e}"
            )
            return {
                "status": "error",
                "message": f"Initialization failed: {e!s}",
                "errors": [str(e)],
            }

    async def suggest_architecture_pattern(
        self,
        project_requirements: dict[str, Any],
        constraints: dict[str, Any] | None = None,
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Suggest architecture patterns based on project requirements."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_architecture_query(
                project_requirements, complexity
            )
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "suggestions": None,
                }

            # Find relevant patterns
            relevant_patterns = await self._find_relevant_architecture_patterns(
                project_requirements, constraints or {}
            )

            # Generate suggestions
            suggestions = await self._generate_architecture_suggestions(
                relevant_patterns, project_requirements, constraints or {}, complexity
            )

            self.assistance_stats["recommendations_generated"] += 1

            return {
                "status": "success",
                "suggestions": suggestions,
                "patterns_analyzed": len(relevant_patterns),
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Architecture pattern suggestion failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to suggest architecture pattern: {e!s}",
                "suggestions": None,
            }

    async def optimize_component_selection(
        self,
        system_components: list[str],
        performance_requirements: dict[str, Any],
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Optimize component selection and configuration."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_component_query(
                system_components, complexity
            )
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "optimizations": None,
                }

            # Find relevant recommendations
            relevant_recommendations = [
                rec
                for rec in self.component_recommendations
                if rec.component_type.lower()
                in [comp.lower() for comp in system_components]
            ]

            # Generate optimizations
            optimizations = await self._generate_component_optimizations(
                relevant_recommendations, performance_requirements, complexity
            )

            self.assistance_stats["recommendations_generated"] += 1

            return {
                "status": "success",
                "optimizations": optimizations,
                "recommendations_found": len(relevant_recommendations),
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Component optimization failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to optimize component selection: {e!s}",
                "optimizations": None,
            }

    async def identify_performance_bottlenecks(
        self,
        performance_metrics: dict[str, Any],
        system_symptoms: list[str] | None = None,
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Identify and resolve performance bottlenecks."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_performance_query(
                performance_metrics, complexity
            )
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "analysis": None,
                }

            # Find matching bottlenecks
            matching_bottlenecks = []
            for bottleneck in self.performance_bottlenecks:
                if system_symptoms:
                    symptom_matches = sum(
                        1
                        for symptom in system_symptoms
                        if any(
                            symptom.lower() in bottleneck_symptom.lower()
                            for bottleneck_symptom in bottleneck.symptoms
                        )
                    )
                    if symptom_matches > 0:
                        matching_bottlenecks.append((bottleneck, symptom_matches))

            # Sort by relevance
            matching_bottlenecks.sort(key=lambda x: x[1], reverse=True)

            # Generate analysis
            analysis = await self._generate_performance_analysis(
                matching_bottlenecks,
                performance_metrics,
                system_symptoms or [],
                complexity,
            )

            self.assistance_stats["recommendations_generated"] += 1

            return {
                "status": "success",
                "analysis": analysis,
                "bottlenecks_identified": len(matching_bottlenecks),
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Performance bottleneck identification failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to identify performance bottlenecks: {e!s}",
                "analysis": None,
            }

    async def develop_maintenance_strategy(
        self,
        system_components: list[str],
        maintenance_requirements: dict[str, Any],
        compliance_needs: list[str] | None = None,
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Develop maintenance and monitoring strategy."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_maintenance_query(
                system_components, complexity
            )
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "strategy": None,
                }

            # Find relevant strategies
            relevant_strategies = []
            for strategy in self.maintenance_strategies:
                component_match = any(
                    comp in strategy.monitoring_components for comp in system_components
                )
                if component_match:
                    relevant_strategies.append(strategy)

            # Generate custom strategy
            strategy = await self._generate_maintenance_strategy(
                system_components,
                maintenance_requirements,
                compliance_needs or [],
                relevant_strategies,
                complexity,
            )

            self.assistance_stats["recommendations_generated"] += 1

            return {
                "status": "success",
                "strategy": strategy,
                "base_strategies_used": len(relevant_strategies),
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Maintenance strategy development failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to develop maintenance strategy: {e!s}",
                "strategy": None,
            }

    async def get_assistance_statistics(self) -> dict[str, Any]:
        """Get proactive development assistance statistics."""
        return {
            "statistics": self.assistance_stats.copy(),
            "knowledge_coverage": {
                "architecture_patterns": len(self.architecture_patterns),
                "component_recommendations": len(self.component_recommendations),
                "performance_bottlenecks": len(self.performance_bottlenecks),
                "maintenance_strategies": len(self.maintenance_strategies),
            },
            "capabilities": [
                "architecture_pattern_suggestion",
                "component_optimization",
                "performance_bottleneck_identification",
                "maintenance_strategy_development",
            ],
        }

    # Private methods following crawl_mcp.py methodology

    async def _validate_environment(self) -> dict[str, Any]:
        """Validate environment for proactive development assistance."""
        errors = []
        warnings = []

        # Check required directories
        cache_dir = Path("cache/development_assistance")
        if not cache_dir.exists():
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create cache directory: {e}")

        # Check optional Neo4j connection
        neo4j_available = all(
            [
                os.getenv("NEO4J_URI"),
                os.getenv("NEO4J_USER"),
                os.getenv("NEO4J_PASSWORD"),
            ]
        )

        if not neo4j_available:
            warnings.append("Neo4j not configured - using static assistance data")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "neo4j_available": neo4j_available,
        }

    async def _load_architecture_patterns(self) -> None:
        """Load architecture patterns."""
        patterns = [
            ArchitecturePattern(
                pattern_id="ignition_mvc",
                name="Ignition MVC Pattern",
                description="Model-View-Controller pattern optimized for Ignition applications",
                pattern_type="MVC",
                use_cases=[
                    "Large-scale HMI applications",
                    "Complex data visualization",
                    "Multi-user systems",
                    "Maintainable code architecture",
                ],
                advantages=[
                    "Clear separation of concerns",
                    "Improved maintainability",
                    "Better testability",
                    "Reusable components",
                ],
                disadvantages=[
                    "Initial complexity overhead",
                    "Requires disciplined development",
                    "May be overkill for simple applications",
                ],
                implementation_steps=[
                    "Define data models using UDTs and database structures",
                    "Create view components using Vision or Perspective",
                    "Implement controllers using Gateway scripting",
                    "Establish communication patterns between layers",
                    "Implement error handling and logging",
                ],
                ignition_specific_considerations=[
                    "Use UDTs for model definitions",
                    "Leverage tag change scripts for controller logic",
                    "Implement proper session management",
                    "Use message handlers for inter-component communication",
                ],
                component_recommendations={
                    "gateway": "Centralized business logic and data processing",
                    "designer": "View layer implementation with templates",
                    "database": "Model persistence and data storage",
                },
                performance_characteristics={
                    "scalability": "High - supports large applications",
                    "maintainability": "High - clear structure",
                    "performance": "Medium - some overhead from abstraction",
                },
                scalability_factors=[
                    "Component separation enables horizontal scaling",
                    "Database optimization critical for performance",
                    "Gateway resource management important",
                ],
            ),
            ArchitecturePattern(
                pattern_id="microservices_ignition",
                name="Microservices for Ignition",
                description="Microservices architecture adapted for Ignition environments",
                pattern_type="Microservices",
                use_cases=[
                    "Enterprise-scale deployments",
                    "Multi-site implementations",
                    "Service-oriented architecture",
                    "Independent component scaling",
                ],
                advantages=[
                    "Independent deployment and scaling",
                    "Technology diversity support",
                    "Fault isolation",
                    "Team autonomy",
                ],
                disadvantages=[
                    "Increased complexity",
                    "Network communication overhead",
                    "Distributed system challenges",
                ],
                implementation_steps=[
                    "Identify service boundaries based on business domains",
                    "Implement services using Ignition modules or external APIs",
                    "Establish communication protocols (REST, OPC-UA, messaging)",
                    "Implement service discovery and configuration management",
                    "Set up monitoring and logging across services",
                ],
                ignition_specific_considerations=[
                    "Use Ignition modules for service boundaries",
                    "Leverage OPC-UA for service communication",
                    "Implement proper security between services",
                    "Use Gateway clustering for high availability",
                ],
                component_recommendations={
                    "gateway_cluster": "Multiple Gateway instances for different services",
                    "message_broker": "For asynchronous communication",
                    "api_gateway": "For external service access",
                },
                performance_characteristics={
                    "scalability": "Very High - independent scaling",
                    "maintainability": "Medium - distributed complexity",
                    "performance": "Variable - depends on network and service design",
                },
                scalability_factors=[
                    "Independent service scaling",
                    "Load balancing across service instances",
                    "Database per service pattern",
                ],
            ),
        ]

        self.architecture_patterns.extend(patterns)
        self.assistance_stats["architecture_patterns_loaded"] = len(
            self.architecture_patterns
        )

    async def _load_component_recommendations(self) -> None:
        """Load component recommendations."""
        recommendations = [
            ComponentRecommendation(
                recommendation_id="gateway_optimization",
                component_type="Gateway",
                component_name="Ignition Gateway",
                recommended_configuration={
                    "memory_settings": {
                        "heap_size": "4GB minimum for production",
                        "garbage_collection": "G1GC for low latency",
                    },
                    "database_connections": {
                        "connection_pool_size": "10-20 connections",
                        "timeout_settings": "30 seconds",
                    },
                    "security_settings": {
                        "ssl_enabled": True,
                        "session_timeout": "30 minutes",
                    },
                },
                optimization_tips=[
                    "Monitor memory usage and adjust heap size accordingly",
                    "Use connection pooling for database operations",
                    "Enable SSL for secure communications",
                    "Configure appropriate logging levels",
                    "Implement proper backup strategies",
                ],
                performance_impact="High",
                resource_requirements={
                    "cpu": "4+ cores recommended",
                    "memory": "8GB+ RAM",
                    "storage": "SSD for database and logs",
                    "network": "Gigabit Ethernet minimum",
                },
                compatibility_notes=[
                    "Compatible with Windows Server and Linux",
                    "Requires Java 11 or higher",
                    "Database compatibility varies by version",
                ],
                best_practices=[
                    "Regular backup and disaster recovery testing",
                    "Monitor system performance metrics",
                    "Keep software updated with latest patches",
                    "Implement proper security measures",
                ],
                common_pitfalls=[
                    "Insufficient memory allocation",
                    "Poor database connection management",
                    "Inadequate security configuration",
                    "Lack of monitoring and alerting",
                ],
            ),
            ComponentRecommendation(
                recommendation_id="perspective_optimization",
                component_type="Perspective",
                component_name="Perspective Module",
                recommended_configuration={
                    "session_management": {
                        "max_concurrent_sessions": "100-500 depending on hardware",
                        "session_timeout": "15 minutes idle",
                    },
                    "resource_optimization": {
                        "image_compression": "Enable for better performance",
                        "caching_strategy": "Aggressive caching for static content",
                    },
                    "security_settings": {
                        "authentication_required": True,
                        "role_based_access": True,
                    },
                },
                optimization_tips=[
                    "Optimize view hierarchies for performance",
                    "Use efficient binding strategies",
                    "Implement proper error handling",
                    "Minimize unnecessary data updates",
                ],
                performance_impact="Medium",
                resource_requirements={
                    "browser": "Modern browser with WebGL support",
                    "network": "Stable internet connection",
                    "client_device": "Tablet or desktop with adequate processing power",
                },
                compatibility_notes=[
                    "Works on modern web browsers",
                    "Mobile device compatibility varies",
                    "Performance depends on client hardware",
                ],
                best_practices=[
                    "Design responsive layouts for different screen sizes",
                    "Implement proper error handling and user feedback",
                    "Use consistent UI/UX patterns",
                    "Test on target devices and browsers",
                ],
                common_pitfalls=[
                    "Overloading views with too many components",
                    "Poor binding performance",
                    "Inadequate error handling",
                    "Inconsistent user experience",
                ],
            ),
        ]

        self.component_recommendations.extend(recommendations)
        self.assistance_stats["component_recommendations_loaded"] = len(
            self.component_recommendations
        )

    async def _load_performance_bottlenecks(self) -> None:
        """Load performance bottlenecks."""
        bottlenecks = [
            PerformanceBottleneck(
                bottleneck_id="database_performance",
                category="Database",
                symptoms=[
                    "Slow query execution",
                    "High database CPU usage",
                    "Connection timeouts",
                    "Long response times",
                ],
                root_causes=[
                    "Inefficient queries",
                    "Missing or poor indexes",
                    "Insufficient database resources",
                    "Poor connection management",
                ],
                detection_methods=[
                    "Query execution plan analysis",
                    "Database performance monitoring",
                    "Connection pool monitoring",
                    "Application response time tracking",
                ],
                resolution_steps=[
                    "Optimize slow queries",
                    "Add appropriate indexes",
                    "Increase database resources",
                    "Implement connection pooling",
                    "Consider query caching",
                ],
                prevention_measures=[
                    "Regular query performance reviews",
                    "Proactive index maintenance",
                    "Capacity planning and monitoring",
                    "Database health checks",
                ],
                monitoring_recommendations=[
                    "Track query execution times",
                    "Monitor database resource utilization",
                    "Alert on connection pool exhaustion",
                    "Regular performance baseline updates",
                ],
                performance_metrics={
                    "query_execution_time": "< 100ms for simple queries",
                    "connection_pool_utilization": "< 80%",
                    "database_cpu": "< 70% average",
                },
                ignition_specific_tools=[
                    "Gateway performance monitoring",
                    "Database connection diagnostics",
                    "Query execution logging",
                ],
            ),
            PerformanceBottleneck(
                bottleneck_id="network_latency",
                category="Network",
                symptoms=[
                    "High response times",
                    "Intermittent connectivity issues",
                    "Data update delays",
                    "Timeout errors",
                ],
                root_causes=[
                    "Network congestion",
                    "Poor network infrastructure",
                    "Inefficient data protocols",
                    "Geographic distance",
                ],
                detection_methods=[
                    "Network latency monitoring",
                    "Bandwidth utilization tracking",
                    "Packet loss analysis",
                    "End-to-end response time measurement",
                ],
                resolution_steps=[
                    "Optimize network infrastructure",
                    "Implement data compression",
                    "Use efficient protocols",
                    "Consider edge computing",
                    "Implement local caching",
                ],
                prevention_measures=[
                    "Regular network performance monitoring",
                    "Capacity planning for network growth",
                    "Redundant network paths",
                    "Quality of Service (QoS) implementation",
                ],
                monitoring_recommendations=[
                    "Continuous latency monitoring",
                    "Bandwidth utilization alerts",
                    "Network health dashboards",
                    "SLA monitoring and reporting",
                ],
                performance_metrics={
                    "network_latency": "< 50ms for local networks",
                    "bandwidth_utilization": "< 70%",
                    "packet_loss": "< 0.1%",
                },
                ignition_specific_tools=[
                    "OPC-UA connection diagnostics",
                    "Gateway network monitoring",
                    "Client-server communication analysis",
                ],
            ),
        ]

        self.performance_bottlenecks.extend(bottlenecks)
        self.assistance_stats["performance_bottlenecks_loaded"] = len(
            self.performance_bottlenecks
        )

    async def _load_maintenance_strategies(self) -> None:
        """Load maintenance strategies."""
        strategies = [
            MaintenanceStrategy(
                strategy_id="preventive_maintenance",
                name="Preventive Maintenance Strategy",
                description="Scheduled maintenance to prevent system failures",
                maintenance_type="Preventive",
                monitoring_components=["Gateway", "Database", "Network", "Storage"],
                maintenance_tasks=[
                    {
                        "task": "System backup verification",
                        "frequency": "Daily",
                        "duration": "30 minutes",
                        "automation_level": "Fully automated",
                    },
                    {
                        "task": "Database maintenance",
                        "frequency": "Weekly",
                        "duration": "2 hours",
                        "automation_level": "Semi-automated",
                    },
                    {
                        "task": "Security updates",
                        "frequency": "Monthly",
                        "duration": "4 hours",
                        "automation_level": "Manual with automation",
                    },
                ],
                monitoring_metrics=[
                    "System uptime",
                    "Performance metrics",
                    "Error rates",
                    "Resource utilization",
                ],
                alert_thresholds={
                    "cpu_usage": "80%",
                    "memory_usage": "85%",
                    "disk_space": "90%",
                    "error_rate": "5%",
                },
                automation_opportunities=[
                    "Automated backup verification",
                    "Automated health checks",
                    "Automated report generation",
                    "Automated alert escalation",
                ],
                resource_requirements={
                    "maintenance_window": "4 hours monthly",
                    "staff_hours": "8 hours monthly",
                    "tools_required": ["Monitoring software", "Backup tools"],
                },
                compliance_considerations=[
                    "Change management procedures",
                    "Documentation requirements",
                    "Audit trail maintenance",
                ],
            )
        ]

        self.maintenance_strategies.extend(strategies)
        self.assistance_stats["maintenance_strategies_loaded"] = len(
            self.maintenance_strategies
        )

    def _validate_architecture_query(
        self, project_requirements: dict[str, Any], complexity: str
    ) -> dict[str, Any]:
        """Validate architecture pattern query parameters."""
        if not project_requirements or not isinstance(project_requirements, dict):
            return {
                "valid": False,
                "error": "Project requirements must be provided as a dictionary",
            }

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    def _validate_component_query(
        self, system_components: list[str], complexity: str
    ) -> dict[str, Any]:
        """Validate component optimization query parameters."""
        if not system_components or not isinstance(system_components, list):
            return {
                "valid": False,
                "error": "System components must be provided as a list",
            }

        if len(system_components) == 0:
            return {
                "valid": False,
                "error": "At least one system component must be provided",
            }

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    def _validate_performance_query(
        self, performance_metrics: dict[str, Any], complexity: str
    ) -> dict[str, Any]:
        """Validate performance analysis query parameters."""
        if not performance_metrics or not isinstance(performance_metrics, dict):
            return {
                "valid": False,
                "error": "Performance metrics must be provided as a dictionary",
            }

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    def _validate_maintenance_query(
        self, system_components: list[str], complexity: str
    ) -> dict[str, Any]:
        """Validate maintenance strategy query parameters."""
        if not system_components or not isinstance(system_components, list):
            return {
                "valid": False,
                "error": "System components must be provided as a list",
            }

        if len(system_components) == 0:
            return {
                "valid": False,
                "error": "At least one system component must be provided",
            }

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    async def _find_relevant_architecture_patterns(
        self, project_requirements: dict[str, Any], constraints: dict[str, Any]
    ) -> list[ArchitecturePattern]:
        """Find relevant architecture patterns based on requirements."""
        relevant_patterns = []

        for pattern in self.architecture_patterns:
            # Check if pattern matches requirements
            requirement_match = False
            for req_key, req_value in project_requirements.items():
                if isinstance(req_value, str):
                    if any(
                        req_value.lower() in use_case.lower()
                        for use_case in pattern.use_cases
                    ):
                        requirement_match = True
                        break

            if requirement_match:
                relevant_patterns.append(pattern)

        return relevant_patterns

    async def _generate_architecture_suggestions(
        self,
        relevant_patterns: list[ArchitecturePattern],
        project_requirements: dict[str, Any],
        constraints: dict[str, Any],
        complexity: str,
    ) -> dict[str, Any]:
        """Generate architecture pattern suggestions."""
        suggestions = {
            "recommended_patterns": [],
            "implementation_guidance": {},
            "trade_offs": {},
            "next_steps": [],
        }

        for pattern in relevant_patterns[:3]:  # Top 3 patterns
            pattern_suggestion = {
                "pattern_id": pattern.pattern_id,
                "name": pattern.name,
                "description": pattern.description,
                "advantages": pattern.advantages,
                "disadvantages": pattern.disadvantages,
                "implementation_steps": pattern.implementation_steps,
                "ignition_considerations": pattern.ignition_specific_considerations,
                "fit_score": self._calculate_pattern_fit_score(
                    pattern, project_requirements
                ),
            }
            suggestions["recommended_patterns"].append(pattern_suggestion)

        suggestions["implementation_guidance"] = self._get_implementation_guidance(
            complexity
        )
        suggestions["next_steps"] = [
            "Review recommended patterns and select the best fit",
            "Create detailed implementation plan",
            "Set up development environment",
            "Begin with proof-of-concept implementation",
        ]

        return suggestions

    async def _generate_component_optimizations(
        self,
        relevant_recommendations: list[ComponentRecommendation],
        performance_requirements: dict[str, Any],
        complexity: str,
    ) -> dict[str, Any]:
        """Generate component optimization recommendations."""
        optimizations = {
            "component_recommendations": [],
            "configuration_optimizations": {},
            "performance_improvements": [],
            "implementation_priority": [],
        }

        for rec in relevant_recommendations:
            optimization = {
                "component_type": rec.component_type,
                "component_name": rec.component_name,
                "recommended_configuration": rec.recommended_configuration,
                "optimization_tips": rec.optimization_tips,
                "performance_impact": rec.performance_impact,
                "best_practices": rec.best_practices,
                "common_pitfalls": rec.common_pitfalls,
            }
            optimizations["component_recommendations"].append(optimization)

        optimizations["implementation_priority"] = [
            "High-impact, low-effort optimizations first",
            "Critical performance bottlenecks",
            "Security and compliance requirements",
            "Long-term maintainability improvements",
        ]

        return optimizations

    async def _generate_performance_analysis(
        self,
        matching_bottlenecks: list[tuple],
        performance_metrics: dict[str, Any],
        system_symptoms: list[str],
        complexity: str,
    ) -> dict[str, Any]:
        """Generate performance bottleneck analysis."""
        analysis = {
            "identified_bottlenecks": [],
            "root_cause_analysis": [],
            "resolution_recommendations": [],
            "monitoring_setup": [],
            "prevention_strategy": [],
        }

        for bottleneck, relevance in matching_bottlenecks[:3]:  # Top 3 bottlenecks
            bottleneck_analysis = {
                "category": bottleneck.category,
                "symptoms": bottleneck.symptoms,
                "root_causes": bottleneck.root_causes,
                "resolution_steps": bottleneck.resolution_steps,
                "monitoring_recommendations": bottleneck.monitoring_recommendations,
                "ignition_tools": bottleneck.ignition_specific_tools,
                "relevance_score": relevance,
            }
            analysis["identified_bottlenecks"].append(bottleneck_analysis)

        analysis["prevention_strategy"] = [
            "Implement proactive monitoring",
            "Regular performance reviews",
            "Capacity planning and forecasting",
            "Automated alerting and response",
        ]

        return analysis

    async def _generate_maintenance_strategy(
        self,
        system_components: list[str],
        maintenance_requirements: dict[str, Any],
        compliance_needs: list[str],
        base_strategies: list[MaintenanceStrategy],
        complexity: str,
    ) -> dict[str, Any]:
        """Generate custom maintenance strategy."""
        strategy = {
            "system_components": system_components,
            "maintenance_requirements": maintenance_requirements,
            "compliance_frameworks": compliance_needs,
            "maintenance_schedule": {},
            "monitoring_setup": {},
            "automation_opportunities": [],
            "resource_planning": {},
        }

        # Generate maintenance schedule
        strategy["maintenance_schedule"] = {
            "daily_tasks": [
                "System health checks",
                "Backup verification",
                "Performance monitoring review",
            ],
            "weekly_tasks": [
                "Database maintenance",
                "Log file cleanup",
                "Security scan",
            ],
            "monthly_tasks": [
                "Full system backup test",
                "Security updates",
                "Performance optimization review",
            ],
        }

        # Monitoring setup
        strategy["monitoring_setup"] = {
            "key_metrics": [
                "System uptime",
                "Response times",
                "Error rates",
                "Resource utilization",
            ],
            "alert_thresholds": {
                "cpu_usage": "80%",
                "memory_usage": "85%",
                "disk_space": "90%",
            },
        }

        # Automation opportunities
        strategy["automation_opportunities"] = [
            "Automated backup verification",
            "Automated health checks",
            "Automated report generation",
            "Automated patch management",
        ]

        return strategy

    def _calculate_pattern_fit_score(
        self, pattern: ArchitecturePattern, project_requirements: dict[str, Any]
    ) -> float:
        """Calculate how well a pattern fits the project requirements."""
        # Simple scoring based on use case matches
        matches = 0
        total_requirements = len(project_requirements)

        for req_key, req_value in project_requirements.items():
            if isinstance(req_value, str):
                if any(
                    req_value.lower() in use_case.lower()
                    for use_case in pattern.use_cases
                ):
                    matches += 1

        return (matches / max(total_requirements, 1)) * 100

    def _get_implementation_guidance(self, complexity: str) -> dict[str, Any]:
        """Get implementation guidance based on complexity level."""
        guidance = {
            "basic": {
                "focus": "Simple, straightforward implementation",
                "recommendations": [
                    "Start with proven patterns",
                    "Minimize complexity",
                    "Focus on core functionality",
                ],
            },
            "standard": {
                "focus": "Balanced approach with good practices",
                "recommendations": [
                    "Follow established patterns",
                    "Implement proper error handling",
                    "Plan for scalability",
                ],
            },
            "advanced": {
                "focus": "Optimized implementation with advanced features",
                "recommendations": [
                    "Implement advanced patterns",
                    "Optimize for performance",
                    "Include comprehensive monitoring",
                ],
            },
            "enterprise": {
                "focus": "Enterprise-grade implementation",
                "recommendations": [
                    "Full enterprise patterns",
                    "Comprehensive security",
                    "High availability and disaster recovery",
                ],
            },
        }

        return guidance.get(complexity, guidance["standard"])


# Validation functions following crawl_mcp.py methodology


async def validate_proactive_development_environment() -> dict[str, Any]:
    """Validate environment for proactive development assistance."""
    try:
        assistance = ProactiveDevelopmentAssistance()
        return await assistance._validate_environment()
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Environment validation failed: {e!s}"],
            "warnings": [],
        }


def get_proactive_development_info() -> dict[str, Any]:
    """Get proactive development assistance information."""
    return {
        "module": "proactive_development_assistance",
        "version": "1.0.0",
        "capabilities": [
            "architecture_pattern_suggestion",
            "component_optimization",
            "performance_bottleneck_identification",
            "maintenance_strategy_development",
        ],
        "architecture_patterns": ["MVC", "Microservices", "Layered", "Event-Driven"],
        "component_types": ["Gateway", "Designer", "Vision", "Perspective", "Database"],
        "performance_categories": ["Database", "Network", "Memory", "CPU", "Storage"],
        "maintenance_types": ["Preventive", "Predictive", "Reactive"],
        "complexity_levels": ["basic", "standard", "advanced", "enterprise"],
        "requirements": [
            "Python 3.11+",
            "Optional: Neo4j for enhanced recommendations",
        ],
        "features": [
            "Environment validation first",
            "Comprehensive input validation",
            "Progressive complexity support",
            "Intelligent pattern matching",
        ],
    }
