#!/usr/bin/env python3
"""Specialized Domain Expertise for SME Agent
Phase 11.4: Advanced SME Agent Features.

This module provides deep technical knowledge following crawl_mcp.py methodology:
1. Environment validation first
2. Comprehensive input validation
3. Error handling and user-friendly messages
4. Modular component testing
5. Progressive complexity support
6. Resource management and cleanup

Deep Technical Knowledge Areas:
- Database integration patterns and optimization
- OPC-UA communication and troubleshooting
- Alarm management and notification strategies
- Security implementation and compliance validation
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DatabaseIntegrationPattern:
    """Database integration pattern with optimization recommendations."""

    pattern_id: str
    name: str
    description: str
    database_type: str  # MySQL, PostgreSQL, SQL Server, Oracle, etc.
    use_cases: list[str] = field(default_factory=list)
    optimization_tips: list[str] = field(default_factory=list)
    performance_metrics: dict[str, Any] = field(default_factory=dict)
    security_considerations: list[str] = field(default_factory=list)
    ignition_specific_config: dict[str, Any] = field(default_factory=dict)
    example_scripts: list[str] = field(default_factory=list)


@dataclass
class OPCUATroubleshootingCase:
    """OPC-UA troubleshooting case with diagnostic information."""

    case_id: str
    issue_category: str  # Connection, Authentication, Performance, Data Quality
    symptoms: list[str] = field(default_factory=list)
    root_causes: list[str] = field(default_factory=list)
    diagnostic_steps: list[str] = field(default_factory=list)
    solutions: list[str] = field(default_factory=list)
    prevention_measures: list[str] = field(default_factory=list)
    ignition_specific_fixes: list[str] = field(default_factory=list)
    server_compatibility: dict[str, Any] = field(default_factory=dict)


@dataclass
class AlarmManagementStrategy:
    """Alarm management strategy with notification configuration."""

    strategy_id: str
    name: str
    description: str
    alarm_types: list[str] = field(default_factory=list)
    priority_levels: dict[str, str] = field(default_factory=dict)
    notification_channels: list[str] = field(default_factory=list)
    escalation_rules: list[dict[str, Any]] = field(default_factory=list)
    suppression_logic: dict[str, Any] = field(default_factory=dict)
    performance_metrics: dict[str, Any] = field(default_factory=dict)
    compliance_requirements: list[str] = field(default_factory=list)


@dataclass
class SecurityImplementation:
    """Security implementation with compliance validation."""

    implementation_id: str
    security_domain: str  # Authentication, Authorization, Encryption, Audit
    compliance_frameworks: list[str] = field(default_factory=list)
    implementation_steps: list[str] = field(default_factory=list)
    validation_tests: list[str] = field(default_factory=list)
    risk_assessment: dict[str, Any] = field(default_factory=dict)
    mitigation_strategies: list[str] = field(default_factory=list)
    ignition_security_features: list[str] = field(default_factory=list)
    audit_requirements: list[str] = field(default_factory=list)


class SpecializedDomainExpertise:
    """Specialized Domain Expertise for SME Agent."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize specialized domain expertise."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Domain expertise storage
        self.database_patterns: list[DatabaseIntegrationPattern] = []
        self.opcua_cases: list[OPCUATroubleshootingCase] = []
        self.alarm_strategies: list[AlarmManagementStrategy] = []
        self.security_implementations: list[SecurityImplementation] = []

        # Performance tracking
        self.expertise_stats = {
            "database_patterns_loaded": 0,
            "opcua_cases_loaded": 0,
            "alarm_strategies_loaded": 0,
            "security_implementations_loaded": 0,
            "queries_processed": 0,
            "last_update": None,
        }

    async def initialize(self) -> dict[str, Any]:
        """Initialize specialized domain expertise following crawl_mcp.py methodology."""
        try:
            # Step 1: Environment validation first
            validation_result = await self._validate_environment()
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": "Environment validation failed",
                    "errors": validation_result["errors"],
                }

            # Step 2: Load domain expertise data
            await self._load_database_patterns()
            await self._load_opcua_troubleshooting_cases()
            await self._load_alarm_management_strategies()
            await self._load_security_implementations()

            # Step 3: Update statistics
            self.expertise_stats["last_update"] = datetime.now().isoformat()

            return {
                "status": "success",
                "components_initialized": [
                    "database_patterns",
                    "opcua_troubleshooting",
                    "alarm_management",
                    "security_implementations",
                ],
                "statistics": self.expertise_stats,
                "warnings": [],
            }

        except Exception as e:
            self.logger.error(f"Specialized domain expertise initialization failed: {e}")
            return {
                "status": "error",
                "message": f"Initialization failed: {e!s}",
                "errors": [str(e)],
            }

    async def get_database_integration_advice(
        self, database_type: str, use_case: str, complexity: str = "standard"
    ) -> dict[str, Any]:
        """Get database integration advice with optimization recommendations."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_database_query(database_type, use_case, complexity)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "advice": None,
                }

            # Find relevant patterns
            relevant_patterns = [
                pattern
                for pattern in self.database_patterns
                if pattern.database_type.lower() == database_type.lower()
                and any(use_case.lower() in uc.lower() for uc in pattern.use_cases)
            ]

            if not relevant_patterns:
                # Generate generic advice based on database type
                advice = await self._generate_generic_database_advice(database_type, use_case, complexity)
            else:
                # Use specific patterns
                advice = await self._compile_database_advice(relevant_patterns, complexity)

            self.expertise_stats["queries_processed"] += 1

            return {
                "status": "success",
                "advice": advice,
                "patterns_found": len(relevant_patterns),
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Database integration advice failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to get database advice: {e!s}",
                "advice": None,
            }

    async def diagnose_opcua_issue(
        self,
        symptoms: list[str],
        server_info: dict[str, Any] | None = None,
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Diagnose OPC-UA communication issues with troubleshooting steps."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_opcua_query(symptoms, complexity)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "diagnosis": None,
                }

            # Find matching troubleshooting cases
            matching_cases = []
            for case in self.opcua_cases:
                symptom_matches = sum(
                    1
                    for symptom in symptoms
                    if any(symptom.lower() in case_symptom.lower() for case_symptom in case.symptoms)
                )
                if symptom_matches > 0:
                    matching_cases.append((case, symptom_matches))

            # Sort by relevance
            matching_cases.sort(key=lambda x: x[1], reverse=True)

            if not matching_cases:
                diagnosis = await self._generate_generic_opcua_diagnosis(symptoms, complexity)
            else:
                diagnosis = await self._compile_opcua_diagnosis(matching_cases, server_info, complexity)

            self.expertise_stats["queries_processed"] += 1

            return {
                "status": "success",
                "diagnosis": diagnosis,
                "cases_found": len(matching_cases),
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"OPC-UA diagnosis failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to diagnose OPC-UA issue: {e!s}",
                "diagnosis": None,
            }

    async def design_alarm_strategy(
        self,
        system_requirements: dict[str, Any],
        compliance_needs: list[str] | None = None,
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Design alarm management strategy with notification configuration."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_alarm_query(system_requirements, complexity)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "strategy": None,
                }

            # Find relevant strategies
            relevant_strategies = []
            for strategy in self.alarm_strategies:
                if compliance_needs:
                    compliance_match = any(comp in strategy.compliance_requirements for comp in compliance_needs)
                    if compliance_match:
                        relevant_strategies.append(strategy)

            # Generate custom strategy
            strategy = await self._design_custom_alarm_strategy(
                system_requirements,
                compliance_needs or [],
                relevant_strategies,
                complexity,
            )

            self.expertise_stats["queries_processed"] += 1

            return {
                "status": "success",
                "strategy": strategy,
                "base_strategies_used": len(relevant_strategies),
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Alarm strategy design failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to design alarm strategy: {e!s}",
                "strategy": None,
            }

    async def validate_security_implementation(
        self,
        security_domain: str,
        implementation_details: dict[str, Any],
        compliance_frameworks: list[str] | None = None,
        complexity: str = "standard",
    ) -> dict[str, Any]:
        """Validate security implementation with compliance checking."""
        try:
            # Step 2: Comprehensive input validation
            validation_result = self._validate_security_query(security_domain, implementation_details, complexity)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "validation_results": None,
                }

            # Find relevant security implementations
            relevant_implementations = [
                impl
                for impl in self.security_implementations
                if impl.security_domain.lower() == security_domain.lower()
            ]

            if compliance_frameworks:
                relevant_implementations = [
                    impl
                    for impl in relevant_implementations
                    if any(framework in impl.compliance_frameworks for framework in compliance_frameworks)
                ]

            # Perform validation
            validation_results = await self._validate_security_details(
                implementation_details,
                relevant_implementations,
                compliance_frameworks or [],
                complexity,
            )

            self.expertise_stats["queries_processed"] += 1

            return {
                "status": "success",
                "validation_results": validation_results,
                "implementations_checked": len(relevant_implementations),
                "complexity_level": complexity,
            }

        except Exception as e:
            self.logger.error(f"Security validation failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to validate security implementation: {e!s}",
                "validation_results": None,
            }

    async def get_expertise_statistics(self) -> dict[str, Any]:
        """Get specialized domain expertise statistics."""
        return {
            "statistics": self.expertise_stats.copy(),
            "domain_coverage": {
                "database_patterns": len(self.database_patterns),
                "opcua_cases": len(self.opcua_cases),
                "alarm_strategies": len(self.alarm_strategies),
                "security_implementations": len(self.security_implementations),
            },
            "capabilities": [
                "database_integration_advice",
                "opcua_troubleshooting",
                "alarm_strategy_design",
                "security_validation",
            ],
        }

    # Private methods following crawl_mcp.py methodology

    async def _validate_environment(self) -> dict[str, Any]:
        """Validate environment for specialized domain expertise."""
        errors = []
        warnings = []

        # Check required directories
        cache_dir = Path("cache/domain_expertise")
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
            warnings.append("Neo4j not configured - using static expertise data")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "neo4j_available": neo4j_available,
        }

    async def _load_database_patterns(self) -> None:
        """Load database integration patterns."""
        # Sample database patterns for different types
        patterns = [
            DatabaseIntegrationPattern(
                pattern_id="mysql_historian",
                name="MySQL Historian Integration",
                description="Optimized MySQL integration for historical data storage",
                database_type="MySQL",
                use_cases=["historical data", "tag logging", "production data"],
                optimization_tips=[
                    "Use InnoDB engine for ACID compliance",
                    "Configure appropriate buffer pool size",
                    "Implement proper indexing on timestamp columns",
                    "Use partitioning for large datasets",
                ],
                performance_metrics={
                    "recommended_batch_size": 1000,
                    "optimal_connection_pool": 10,
                    "index_maintenance_interval": "weekly",
                },
                security_considerations=[
                    "Use SSL connections",
                    "Implement least privilege access",
                    "Regular security updates",
                    "Audit trail configuration",
                ],
                ignition_specific_config={
                    "driver": "com.mysql.cj.jdbc.Driver",
                    "connection_string_template": "jdbc:mysql://{host}:{port}/{database}?useSSL=true",
                    "recommended_timeout": 30000,
                },
                example_scripts=[
                    "SELECT * FROM tag_history WHERE timestamp > DATE_SUB(NOW(), INTERVAL 1 DAY)",
                    "INSERT INTO production_data (timestamp, tag_name, value) VALUES (?, ?, ?)",
                ],
            ),
            DatabaseIntegrationPattern(
                pattern_id="postgresql_analytics",
                name="PostgreSQL Analytics Integration",
                description="PostgreSQL integration optimized for analytics and reporting",
                database_type="PostgreSQL",
                use_cases=["analytics", "reporting", "data warehousing"],
                optimization_tips=[
                    "Use JSONB for flexible data storage",
                    "Implement proper vacuum scheduling",
                    "Configure work_mem for complex queries",
                    "Use materialized views for aggregations",
                ],
                performance_metrics={
                    "recommended_batch_size": 5000,
                    "optimal_connection_pool": 15,
                    "vacuum_frequency": "daily",
                },
                security_considerations=[
                    "Row-level security implementation",
                    "SSL certificate validation",
                    "Role-based access control",
                    "Connection encryption",
                ],
                ignition_specific_config={
                    "driver": "org.postgresql.Driver",
                    "connection_string_template": "jdbc:postgresql://{host}:{port}/{database}?ssl=true",
                    "recommended_timeout": 45000,
                },
                example_scripts=[
                    "SELECT tag_name, AVG(value) FROM analytics_data WHERE timestamp > NOW() - INTERVAL '7 days' GROUP BY tag_name",  # noqa: E501
                    "CREATE MATERIALIZED VIEW daily_summary AS SELECT DATE(timestamp), tag_name, AVG(value) FROM tag_data GROUP BY DATE(timestamp), tag_name",  # noqa: E501
                ],
            ),
        ]

        self.database_patterns.extend(patterns)
        self.expertise_stats["database_patterns_loaded"] = len(self.database_patterns)

    async def _load_opcua_troubleshooting_cases(self) -> None:
        """Load OPC-UA troubleshooting cases."""
        cases = [
            OPCUATroubleshootingCase(
                case_id="connection_timeout",
                issue_category="Connection",
                symptoms=[
                    "Connection timeout errors",
                    "Cannot connect to OPC-UA server",
                    "Intermittent connection drops",
                ],
                root_causes=[
                    "Network latency or packet loss",
                    "Server overload or resource constraints",
                    "Firewall blocking OPC-UA ports",
                    "Incorrect endpoint configuration",
                ],
                diagnostic_steps=[
                    "Check network connectivity with ping/telnet",
                    "Verify OPC-UA server is running and accessible",
                    "Check firewall rules for ports 4840/4841",
                    "Review server logs for error messages",
                    "Test with OPC-UA client tools",
                ],
                solutions=[
                    "Increase connection timeout values",
                    "Configure firewall exceptions",
                    "Optimize network infrastructure",
                    "Implement connection retry logic",
                ],
                prevention_measures=[
                    "Regular network monitoring",
                    "Server performance monitoring",
                    "Redundant network paths",
                    "Load balancing for multiple servers",
                ],
                ignition_specific_fixes=[
                    "Adjust OPC-UA connection timeout in device settings",
                    "Enable OPC-UA connection diagnostics",
                    "Configure subscription parameters appropriately",
                ],
                server_compatibility={
                    "tested_servers": ["Kepware", "Matrikon", "Prosys"],
                    "known_issues": {
                        "Kepware": "Requires specific security policy configuration",
                        "Matrikon": "May need custom certificate handling",
                    },
                },
            ),
            OPCUATroubleshootingCase(
                case_id="authentication_failure",
                issue_category="Authentication",
                symptoms=[
                    "Authentication failed errors",
                    "Access denied messages",
                    "Certificate validation errors",
                ],
                root_causes=[
                    "Invalid username/password credentials",
                    "Certificate trust issues",
                    "Security policy mismatch",
                    "User permissions insufficient",
                ],
                diagnostic_steps=[
                    "Verify credentials with server administrator",
                    "Check certificate validity and trust chain",
                    "Review security policy configuration",
                    "Test with different authentication methods",
                ],
                solutions=[
                    "Update credentials and certificates",
                    "Configure proper security policies",
                    "Implement certificate management",
                    "Set appropriate user permissions",
                ],
                prevention_measures=[
                    "Regular credential rotation",
                    "Certificate lifecycle management",
                    "Security policy documentation",
                    "User access reviews",
                ],
                ignition_specific_fixes=[
                    "Configure OPC-UA security settings in device configuration",
                    "Import server certificates into Ignition trust store",
                    "Set appropriate authentication mode",
                ],
                server_compatibility={
                    "security_modes": ["None", "Sign", "SignAndEncrypt"],
                    "auth_methods": ["Anonymous", "Username", "Certificate"],
                },
            ),
        ]

        self.opcua_cases.extend(cases)
        self.expertise_stats["opcua_cases_loaded"] = len(self.opcua_cases)

    async def _load_alarm_management_strategies(self) -> None:
        """Load alarm management strategies."""
        strategies = [
            AlarmManagementStrategy(
                strategy_id="critical_process_alarms",
                name="Critical Process Alarm Strategy",
                description="Comprehensive strategy for critical process alarms with rapid response",
                alarm_types=["Process", "Safety", "Equipment"],
                priority_levels={
                    "Critical": "Immediate response required",
                    "High": "Response within 15 minutes",
                    "Medium": "Response within 1 hour",
                    "Low": "Response within 4 hours",
                },
                notification_channels=["SMS", "Email", "Voice Call", "Mobile App"],
                escalation_rules=[
                    {
                        "level": 1,
                        "timeout_minutes": 5,
                        "recipients": ["primary_operator"],
                        "channels": ["SMS", "Mobile App"],
                    },
                    {
                        "level": 2,
                        "timeout_minutes": 15,
                        "recipients": ["shift_supervisor"],
                        "channels": ["Voice Call", "SMS"],
                    },
                    {
                        "level": 3,
                        "timeout_minutes": 30,
                        "recipients": ["plant_manager"],
                        "channels": ["Voice Call", "Email"],
                    },
                ],
                suppression_logic={
                    "enable_flood_suppression": True,
                    "max_alarms_per_minute": 10,
                    "suppression_duration_minutes": 5,
                    "priority_bypass": ["Critical", "Safety"],
                },
                performance_metrics={
                    "target_response_time": "2 minutes",
                    "acknowledgment_rate": "95%",
                    "false_positive_rate": "<5%",
                },
                compliance_requirements=[
                    "ISA-18.2",
                    "IEC 62682",
                    "OSHA Process Safety",
                ],
            )
        ]

        self.alarm_strategies.extend(strategies)
        self.expertise_stats["alarm_strategies_loaded"] = len(self.alarm_strategies)

    async def _load_security_implementations(self) -> None:
        """Load security implementations."""
        implementations = [
            SecurityImplementation(
                implementation_id="authentication_system",
                security_domain="Authentication",
                compliance_frameworks=["NIST", "ISO 27001", "IEC 62443"],
                implementation_steps=[
                    "Design authentication architecture",
                    "Configure identity providers",
                    "Implement multi-factor authentication",
                    "Set up session management",
                    "Configure password policies",
                ],
                validation_tests=[
                    "Test login with valid credentials",
                    "Test login with invalid credentials",
                    "Test session timeout functionality",
                    "Test MFA bypass attempts",
                    "Test password complexity enforcement",
                ],
                risk_assessment={
                    "authentication_bypass": "High",
                    "credential_theft": "Medium",
                    "session_hijacking": "Medium",
                    "brute_force_attacks": "Low",
                },
                mitigation_strategies=[
                    "Implement account lockout policies",
                    "Use strong encryption for credentials",
                    "Regular security audits",
                    "Monitor authentication failures",
                ],
                ignition_security_features=[
                    "Built-in user management",
                    "LDAP/AD integration",
                    "Role-based permissions",
                    "Session timeout configuration",
                ],
                audit_requirements=[
                    "Log all authentication attempts",
                    "Track privilege escalations",
                    "Monitor administrative actions",
                    "Regular access reviews",
                ],
            )
        ]

        self.security_implementations.extend(implementations)
        self.expertise_stats["security_implementations_loaded"] = len(self.security_implementations)

    def _validate_database_query(self, database_type: str, use_case: str, complexity: str) -> dict[str, Any]:
        """Validate database integration query parameters."""
        if not database_type or not isinstance(database_type, str):
            return {
                "valid": False,
                "error": "Database type is required and must be a string",
            }

        if not use_case or not isinstance(use_case, str):
            return {
                "valid": False,
                "error": "Use case is required and must be a string",
            }

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    def _validate_opcua_query(self, symptoms: list[str], complexity: str) -> dict[str, Any]:
        """Validate OPC-UA troubleshooting query parameters."""
        if not symptoms or not isinstance(symptoms, list):
            return {"valid": False, "error": "Symptoms must be provided as a list"}

        if len(symptoms) == 0:
            return {"valid": False, "error": "At least one symptom must be provided"}

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    def _validate_alarm_query(self, system_requirements: dict[str, Any], complexity: str) -> dict[str, Any]:
        """Validate alarm management query parameters."""
        if not system_requirements or not isinstance(system_requirements, dict):
            return {
                "valid": False,
                "error": "System requirements must be provided as a dictionary",
            }

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    def _validate_security_query(
        self,
        security_domain: str,
        implementation_details: dict[str, Any],
        complexity: str,
    ) -> dict[str, Any]:
        """Validate security implementation query parameters."""
        if not security_domain or not isinstance(security_domain, str):
            return {
                "valid": False,
                "error": "Security domain is required and must be a string",
            }

        if not implementation_details or not isinstance(implementation_details, dict):
            return {
                "valid": False,
                "error": "Implementation details must be provided as a dictionary",
            }

        valid_complexities = ["basic", "standard", "advanced", "enterprise"]
        if complexity not in valid_complexities:
            return {
                "valid": False,
                "error": f"Complexity must be one of: {valid_complexities}",
            }

        return {"valid": True}

    async def _generate_generic_database_advice(
        self, database_type: str, use_case: str, complexity: str
    ) -> dict[str, Any]:
        """Generate generic database integration advice."""
        return {
            "database_type": database_type,
            "use_case": use_case,
            "general_recommendations": [
                f"Configure {database_type} with appropriate connection pooling",
                "Implement proper error handling and retry logic",
                "Use parameterized queries to prevent SQL injection",
                "Monitor database performance metrics",
            ],
            "ignition_integration": [
                "Configure database connection in Ignition Gateway",
                "Test connection and verify connectivity",
                "Set appropriate timeout values",
                "Implement proper logging for troubleshooting",
            ],
            "complexity_specific": self._get_complexity_specific_advice(complexity),
        }

    async def _compile_database_advice(
        self, patterns: list[DatabaseIntegrationPattern], complexity: str
    ) -> dict[str, Any]:
        """Compile database advice from matching patterns."""
        combined_advice: Any = {
            "optimization_tips": [],
            "security_considerations": [],
            "ignition_configuration": {},
            "example_scripts": [],
            "performance_metrics": {},
        }

        for pattern in patterns:
            combined_advice["optimization_tips"].extend(pattern.optimization_tips)
            combined_advice["security_considerations"].extend(pattern.security_considerations)
            combined_advice["ignition_configuration"].update(pattern.ignition_specific_config)
            combined_advice["example_scripts"].extend(pattern.example_scripts)
            combined_advice["performance_metrics"].update(pattern.performance_metrics)

        # Remove duplicates
        combined_advice["optimization_tips"] = list(set(combined_advice["optimization_tips"]))
        combined_advice["security_considerations"] = list(set(combined_advice["security_considerations"]))
        combined_advice["example_scripts"] = list(set(combined_advice["example_scripts"]))

        combined_advice["complexity_specific"] = self._get_complexity_specific_advice(complexity)

        return combined_advice

    async def _generate_generic_opcua_diagnosis(self, symptoms: list[str], complexity: str) -> dict[str, Any]:
        """Generate generic OPC-UA troubleshooting diagnosis."""
        return {
            "symptoms_analyzed": symptoms,
            "general_diagnostic_steps": [
                "Check network connectivity to OPC-UA server",
                "Verify server is running and accessible",
                "Review OPC-UA security configuration",
                "Check client certificate validity",
                "Verify subscription parameters",
            ],
            "common_solutions": [
                "Restart OPC-UA server service",
                "Update client certificates",
                "Adjust security policy settings",
                "Configure firewall exceptions",
                "Optimize subscription rates",
            ],
            "ignition_specific_checks": [
                "Review OPC-UA device status in Gateway",
                "Check connection diagnostics",
                "Verify tag subscription settings",
                "Review Gateway logs for errors",
            ],
            "complexity_specific": self._get_complexity_specific_advice(complexity),
        }

    async def _compile_opcua_diagnosis(
        self,
        matching_cases: list[tuple],
        server_info: dict[str, Any] | None,
        complexity: str,
    ) -> dict[str, Any]:
        """Compile OPC-UA diagnosis from matching cases."""
        diagnosis: Any = {
            "root_causes": [],
            "diagnostic_steps": [],
            "solutions": [],
            "prevention_measures": [],
            "ignition_fixes": [],
            "server_compatibility": {},
        }

        for case, _relevance in matching_cases[:3]:  # Top 3 most relevant cases
            diagnosis["root_causes"].extend(case.root_causes)
            diagnosis["diagnostic_steps"].extend(case.diagnostic_steps)
            diagnosis["solutions"].extend(case.solutions)
            diagnosis["prevention_measures"].extend(case.prevention_measures)
            diagnosis["ignition_fixes"].extend(case.ignition_specific_fixes)
            diagnosis["server_compatibility"].update(case.server_compatibility)

        # Remove duplicates
        for key in [
            "root_causes",
            "diagnostic_steps",
            "solutions",
            "prevention_measures",
            "ignition_fixes",
        ]:
            diagnosis[key] = list(set(diagnosis[key]))

        diagnosis["cases_analyzed"] = len(matching_cases)
        diagnosis["complexity_specific"] = self._get_complexity_specific_advice(complexity)

        return diagnosis

    async def _design_custom_alarm_strategy(
        self,
        system_requirements: dict[str, Any],
        compliance_needs: list[str],
        base_strategies: list[AlarmManagementStrategy],
        complexity: str,
    ) -> dict[str, Any]:
        """Design custom alarm management strategy."""
        strategy = {
            "system_requirements": system_requirements,
            "compliance_frameworks": compliance_needs,
            "recommended_priority_levels": {
                "Critical": "Immediate response - Safety or production critical",
                "High": "Response within 15 minutes - Significant impact",
                "Medium": "Response within 1 hour - Moderate impact",
                "Low": "Response within 4 hours - Minor impact",
            },
            "notification_channels": ["Email", "SMS", "Mobile App", "HMI Display"],
            "escalation_rules": [
                {
                    "level": 1,
                    "timeout_minutes": 5,
                    "recipients": ["primary_operator"],
                    "channels": ["HMI Display", "Mobile App"],
                },
                {
                    "level": 2,
                    "timeout_minutes": 15,
                    "recipients": ["shift_supervisor"],
                    "channels": ["SMS", "Voice Call"],
                },
            ],
            "suppression_configuration": {
                "enable_flood_suppression": True,
                "max_alarms_per_minute": 20,
                "suppression_duration_minutes": 2,
                "priority_bypass": ["Critical"],
            },
            "performance_targets": {
                "response_time": "< 3 minutes for critical alarms",
                "acknowledgment_rate": "> 90%",
                "false_positive_rate": "< 10%",
            },
        }

        # Incorporate base strategies if available
        if base_strategies:
            strategy["base_strategies_referenced"] = [s.strategy_id for s in base_strategies]

        strategy["complexity_specific"] = self._get_complexity_specific_advice(complexity)

        return strategy

    async def _validate_security_details(
        self,
        implementation_details: dict[str, Any],
        relevant_implementations: list[SecurityImplementation],
        compliance_frameworks: list[str],
        complexity: str,
    ) -> dict[str, Any]:
        """Validate security implementation details."""
        validation_results = {
            "implementation_details": implementation_details,
            "compliance_check": {},
            "security_recommendations": [],
            "risk_assessment": {},
            "validation_tests": [],
            "audit_requirements": [],
        }

        # Compliance checking
        for framework in compliance_frameworks:
            validation_results["compliance_check"][framework] = {
                "status": "partial",
                "missing_requirements": [],
                "recommendations": [],
            }

        # Security recommendations from relevant implementations
        for impl in relevant_implementations:
            validation_results["security_recommendations"].extend(impl.mitigation_strategies)
            validation_results["validation_tests"].extend(impl.validation_tests)
            validation_results["audit_requirements"].extend(impl.audit_requirements)
            validation_results["risk_assessment"].update(impl.risk_assessment)

        # Remove duplicates
        validation_results["security_recommendations"] = list(set(validation_results["security_recommendations"]))
        validation_results["validation_tests"] = list(set(validation_results["validation_tests"]))
        validation_results["audit_requirements"] = list(set(validation_results["audit_requirements"]))

        validation_results["complexity_specific"] = self._get_complexity_specific_advice(complexity)
        validation_results["implementations_analyzed"] = len(relevant_implementations)

        return validation_results

    def _get_complexity_specific_advice(self, complexity: str) -> dict[str, Any]:
        """Get complexity-specific advice and recommendations."""
        complexity_advice = {
            "basic": {
                "focus": "Essential configuration and basic security",
                "recommendations": [
                    "Start with default configurations",
                    "Implement basic authentication",
                    "Use standard security policies",
                ],
            },
            "standard": {
                "focus": "Production-ready configuration with monitoring",
                "recommendations": [
                    "Implement comprehensive monitoring",
                    "Configure backup and recovery",
                    "Set up proper logging and alerting",
                ],
            },
            "advanced": {
                "focus": "Optimized performance and advanced security",
                "recommendations": [
                    "Implement advanced security measures",
                    "Optimize for high performance",
                    "Configure advanced monitoring and analytics",
                ],
            },
            "enterprise": {
                "focus": "Enterprise-grade scalability and compliance",
                "recommendations": [
                    "Implement enterprise security frameworks",
                    "Configure for high availability",
                    "Ensure full compliance and audit trails",
                ],
            },
        }

        return complexity_advice.get(complexity, complexity_advice["standard"])


# Validation functions following crawl_mcp.py methodology


async def validate_specialized_domain_environment() -> dict[str, Any]:
    """Validate environment for specialized domain expertise."""
    try:
        expertise = SpecializedDomainExpertise()
        return await expertise._validate_environment()
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Environment validation failed: {e!s}"],
            "warnings": [],
        }


def get_specialized_domain_info() -> dict[str, Any]:
    """Get specialized domain expertise information."""
    return {
        "module": "specialized_domain_expertise",
        "version": "1.0.0",
        "capabilities": [
            "database_integration_advice",
            "opcua_troubleshooting",
            "alarm_strategy_design",
            "security_validation",
        ],
        "supported_databases": ["MySQL", "PostgreSQL", "SQL Server", "Oracle"],
        "opcua_expertise": [
            "Connection",
            "Authentication",
            "Performance",
            "Data Quality",
        ],
        "alarm_management": [
            "Strategy Design",
            "Notification",
            "Escalation",
            "Suppression",
        ],
        "security_domains": ["Authentication", "Authorization", "Encryption", "Audit"],
        "complexity_levels": ["basic", "standard", "advanced", "enterprise"],
        "requirements": [
            "Python 3.11+",
            "Optional: Neo4j for enhanced knowledge retrieval",
        ],
        "features": [
            "Environment validation first",
            "Comprehensive input validation",
            "Progressive complexity support",
            "Modular component testing",
        ],
    }
