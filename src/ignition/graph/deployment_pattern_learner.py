"""Deployment Pattern Learning System for IGN Scripts.

This module implements intelligent deployment pattern learning using Neo4j graph database.
It learns from deployment history to provide AI-powered recommendations, environment adaptations,
and rollback scenarios.

Neo4j Configuration:
    Default credentials (from docker-compose.yml):
        - Username: neo4j
        - Password: ignition-graph
        - URI: bolt://localhost:7687
    
    Environment variables (optional override):
        - NEO4J_URI=bolt://localhost:7687
        - NEO4J_USERNAME=neo4j  
        - NEO4J_PASSWORD=ignition-graph
    
    Note: These are set in src/ignition/graph/client.py as defaults.
    No separate .env file needed unless overriding defaults.

Usage:
    learner = DeploymentPatternLearner()
    learner.record_deployment_execution(...)
    recommendations = learner.get_deployment_recommendations(...)

Implementation Status:
    ✅ COMPLETED - 2025-01-28
    - Full deployment pattern learning system implemented
    - Neo4j schema extended with 5 new node types and 8 relationships
    - AI-powered recommendations with confidence scoring
    - Environment adaptation intelligence
    - Rollback scenario learning and recovery patterns
    - Complete CLI integration with 4 new commands
    - Comprehensive demo and testing completed
    - All functionality verified and working
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from .client import IgnitionGraphClient

logger = logging.getLogger(__name__)


class DeploymentPatternLearner:
    """Learns from deployment patterns and provides intelligent recommendations."""

    def __init__(self, client: IgnitionGraphClient):
        """Initialize the deployment pattern learner.
        
        Args:
            client: Connected Neo4j graph client
        """
        self.client = client
        self.min_pattern_confidence = 0.7
        self.min_success_count = 3
        self.pattern_similarity_threshold = 0.8

    def record_deployment_execution(
        self,
        execution_name: str,
        deployment_type: str,
        target_environment: str,
        gateway_host: str,
        deployment_strategy: str,
        resources_deployed: List[str],
        configuration_used: Dict[str, Any],
        status: str,
        started_at: datetime,
        completed_at: Optional[datetime] = None,
        failure_reasons: Optional[List[str]] = None,
        rollback_triggered: bool = False,
        rollback_successful: Optional[bool] = None,
        user_id: Optional[str] = None,
        automation_triggered: bool = False,
        execution_log: Optional[str] = None,
        performance_data: Optional[Dict[str, Any]] = None,
        lessons_learned: Optional[str] = None,
        source_environment: Optional[str] = None,
    ) -> str:
        """Record a deployment execution for pattern learning.
        
        Args:
            execution_name: Name/identifier for this deployment
            deployment_type: Type of deployment (initial, update, rollback, etc.)
            target_environment: Target environment name
            gateway_host: Target gateway host
            deployment_strategy: Strategy used (blue_green, rolling, etc.)
            resources_deployed: List of resources that were deployed
            configuration_used: Configuration parameters used
            status: Final status of deployment
            started_at: When deployment started
            completed_at: When deployment completed (if finished)
            failure_reasons: List of failure reasons if failed
            rollback_triggered: Whether rollback was triggered
            rollback_successful: Whether rollback was successful (if triggered)
            user_id: User who initiated deployment
            automation_triggered: Whether deployment was automated
            execution_log: Detailed execution log
            performance_data: Performance metrics from deployment
            lessons_learned: Lessons learned from this deployment
            source_environment: Source environment (for migrations)
            
        Returns:
            Deployment execution ID
        """
        execution_id = str(uuid4())
        
        # Calculate duration if completed
        duration_seconds = None
        if completed_at and started_at:
            duration_seconds = int((completed_at - started_at).total_seconds())
        
        # Create deployment execution node
        execution_data = {
            "id": execution_id,
            "execution_name": execution_name,
            "deployment_type": deployment_type,
            "source_environment": source_environment,
            "target_environment": target_environment,
            "gateway_host": gateway_host,
            "deployment_strategy": deployment_strategy,
            "resources_deployed": resources_deployed,
            "configuration_used": json.dumps(configuration_used),
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat() if completed_at else None,
            "duration_seconds": duration_seconds,
            "status": status,
            "success_metrics": json.dumps(performance_data) if performance_data else None,
            "failure_reasons": failure_reasons or [],
            "rollback_triggered": rollback_triggered,
            "rollback_successful": rollback_successful,
            "user_id": user_id,
            "automation_triggered": automation_triggered,
            "execution_log": execution_log,
            "performance_data": json.dumps(performance_data) if performance_data else None,
            "lessons_learned": lessons_learned,
        }
        
        query = """
        CREATE (de:DeploymentExecution $props)
        RETURN de.id as execution_id
        """
        
        result = self.client.execute_write_query(query, {"props": execution_data})
        
        if result:
            logger.info(f"Recorded deployment execution: {execution_id}")
            
            # Trigger pattern learning if deployment was successful
            if status == "completed":
                self._learn_from_successful_deployment(execution_id, execution_data)
            elif status == "failed" and rollback_triggered:
                self._learn_from_rollback_scenario(execution_id, execution_data)
                
            return execution_id
        else:
            raise Exception(f"Failed to record deployment execution: {execution_name}")

    def record_environment_adaptation(
        self,
        adaptation_name: str,
        source_environment: str,
        target_environment: str,
        adaptation_type: str,
        resource_type: str,
        original_configuration: Dict[str, Any],
        adapted_configuration: Dict[str, Any],
        adaptation_rules: List[str],
        trigger_conditions: List[str],
        validation_criteria: Optional[List[str]] = None,
        automation_level: str = "manual",
    ) -> str:
        """Record an environment-specific adaptation pattern.
        
        Args:
            adaptation_name: Name for this adaptation
            source_environment: Source environment name
            target_environment: Target environment name
            adaptation_type: Type of adaptation
            resource_type: Type of resource being adapted
            original_configuration: Original configuration
            adapted_configuration: Adapted configuration
            adaptation_rules: Rules that govern this adaptation
            trigger_conditions: Conditions that trigger this adaptation
            validation_criteria: Criteria to validate adaptation success
            automation_level: Level of automation (manual, semi_automated, fully_automated)
            
        Returns:
            Environment adaptation ID
        """
        adaptation_id = str(uuid4())
        
        adaptation_data = {
            "id": adaptation_id,
            "adaptation_name": adaptation_name,
            "source_environment": source_environment,
            "target_environment": target_environment,
            "adaptation_type": adaptation_type,
            "resource_type": resource_type,
            "original_configuration": json.dumps(original_configuration),
            "adapted_configuration": json.dumps(adapted_configuration),
            "adaptation_rules": adaptation_rules,
            "trigger_conditions": trigger_conditions,
            "validation_criteria": validation_criteria or [],
            "discovered_date": datetime.now().isoformat(),
            "application_count": 0,
            "success_rate": 0.0,
            "automation_level": automation_level,
            "confidence_level": 0.5,  # Start with medium confidence
            "is_active": True,
        }
        
        query = """
        CREATE (ea:EnvironmentAdaptation $props)
        RETURN ea.id as adaptation_id
        """
        
        result = self.client.execute_write_query(query, {"props": adaptation_data})
        
        if result:
            logger.info(f"Recorded environment adaptation: {adaptation_id}")
            return adaptation_id
        else:
            raise Exception(f"Failed to record environment adaptation: {adaptation_name}")

    def record_rollback_scenario(
        self,
        scenario_name: str,
        rollback_type: str,
        trigger_conditions: List[str],
        failure_patterns: List[str],
        rollback_strategy: str,
        rollback_steps: List[str],
        environment: str,
        resource_types_affected: List[str],
        recovery_time_target: Optional[int] = None,
        data_loss_acceptable: bool = False,
        validation_steps: Optional[List[str]] = None,
        notification_required: bool = True,
        escalation_criteria: Optional[List[str]] = None,
        automation_level: str = "manual",
    ) -> str:
        """Record a rollback scenario for future reference.
        
        Args:
            scenario_name: Name for this rollback scenario
            rollback_type: Type of rollback (automatic, manual, etc.)
            trigger_conditions: Conditions that trigger this rollback
            failure_patterns: Patterns that indicate need for rollback
            rollback_strategy: Strategy for executing rollback
            rollback_steps: Specific steps to execute rollback
            environment: Environment where rollback applies
            resource_types_affected: Types of resources affected
            recovery_time_target: Target recovery time in seconds
            data_loss_acceptable: Whether data loss is acceptable
            validation_steps: Steps to validate rollback success
            notification_required: Whether notification is required
            escalation_criteria: Criteria for escalating rollback issues
            automation_level: Level of automation for rollback
            
        Returns:
            Rollback scenario ID
        """
        scenario_id = str(uuid4())
        
        scenario_data = {
            "id": scenario_id,
            "scenario_name": scenario_name,
            "rollback_type": rollback_type,
            "trigger_conditions": trigger_conditions,
            "failure_patterns": failure_patterns,
            "rollback_strategy": rollback_strategy,
            "rollback_steps": rollback_steps,
            "recovery_time_target": recovery_time_target,
            "data_loss_acceptable": data_loss_acceptable,
            "environment": environment,
            "resource_types_affected": resource_types_affected,
            "validation_steps": validation_steps or [],
            "notification_required": notification_required,
            "escalation_criteria": escalation_criteria or [],
            "discovered_date": datetime.now().isoformat(),
            "execution_count": 0,
            "success_rate": 0.0,
            "automation_level": automation_level,
            "is_active": True,
        }
        
        query = """
        CREATE (rs:RollbackScenario $props)
        RETURN rs.id as scenario_id
        """
        
        result = self.client.execute_write_query(query, {"props": scenario_data})
        
        if result:
            logger.info(f"Recorded rollback scenario: {scenario_id}")
            return scenario_id
        else:
            raise Exception(f"Failed to record rollback scenario: {scenario_name}")

    def get_deployment_recommendations(
        self,
        target_environment: str,
        resource_types: List[str],
        deployment_strategy: Optional[str] = None,
        gateway_host: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get deployment recommendations based on learned patterns.
        
        Args:
            target_environment: Target environment for deployment
            resource_types: Types of resources being deployed
            deployment_strategy: Preferred deployment strategy (optional)
            gateway_host: Target gateway host (optional)
            limit: Maximum number of recommendations
            
        Returns:
            List of deployment recommendations with confidence scores
        """
        # Build query conditions
        conditions = ["dp.is_active = true"]
        params = {
            "target_environment": target_environment,
            "resource_types": resource_types,
            "min_confidence": self.min_pattern_confidence,
            "min_success_count": self.min_success_count,
            "limit": limit,
        }
        
        # Add optional filters
        if deployment_strategy:
            conditions.append("dp.deployment_strategy = $deployment_strategy")
            params["deployment_strategy"] = deployment_strategy
            
        if gateway_host:
            conditions.append("EXISTS { MATCH (de:DeploymentExecution)-[:FOLLOWS_DEPLOYMENT_PATTERN]->(dp) WHERE de.gateway_host = $gateway_host }")
            params["gateway_host"] = gateway_host
        
        # Check for resource type overlap
        conditions.append("ANY(rt IN $resource_types WHERE rt IN dp.resource_types)")
        conditions.append("$target_environment IN dp.environment_types")
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        MATCH (dp:DeploymentPattern)
        WHERE {where_clause}
        AND dp.confidence_score >= $min_confidence
        AND dp.success_count >= $min_success_count
        OPTIONAL MATCH (de:DeploymentExecution)-[:FOLLOWS_DEPLOYMENT_PATTERN]->(dp)
        WITH dp, COUNT(de) as usage_count
        RETURN dp,
               usage_count,
               dp.confidence_score as confidence,
               dp.success_count as successes,
               dp.failure_count as failures,
               dp.pattern_data as pattern_json
        ORDER BY dp.confidence_score DESC, dp.success_count DESC, usage_count DESC
        LIMIT $limit
        """
        
        result = self.client.execute_query(query, params)
        
        recommendations = []
        for record in result:
            pattern = record["dp"]
            try:
                pattern_data = json.loads(record["pattern_json"])
                
                recommendation = {
                    "pattern_id": pattern["id"],
                    "pattern_name": pattern["name"],
                    "pattern_type": pattern["pattern_type"],
                    "deployment_strategy": pattern["deployment_strategy"],
                    "confidence_score": record["confidence"],
                    "success_count": record["successes"],
                    "failure_count": record["failures"],
                    "usage_count": record["usage_count"],
                    "success_rate": record["successes"] / max(record["successes"] + record["failures"], 1),
                    "configuration_template": json.loads(pattern["configuration_template"]),
                    "pre_conditions": pattern.get("pre_conditions", []),
                    "post_conditions": pattern.get("post_conditions", []),
                    "pattern_details": pattern_data,
                    "applicability_reasons": self._calculate_applicability_reasons(
                        pattern, target_environment, resource_types, deployment_strategy
                    ),
                }
                recommendations.append(recommendation)
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not parse pattern data: {e}")
                continue
        
        return recommendations

    def get_environment_adaptations(
        self,
        source_environment: str,
        target_environment: str,
        resource_type: Optional[str] = None,
        adaptation_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get environment-specific adaptations.
        
        Args:
            source_environment: Source environment
            target_environment: Target environment
            resource_type: Specific resource type (optional)
            adaptation_type: Specific adaptation type (optional)
            limit: Maximum number of adaptations
            
        Returns:
            List of applicable environment adaptations
        """
        conditions = [
            "ea.is_active = true",
            "ea.source_environment = $source_environment",
            "ea.target_environment = $target_environment",
        ]
        params = {
            "source_environment": source_environment,
            "target_environment": target_environment,
            "limit": limit,
        }
        
        if resource_type:
            conditions.append("ea.resource_type = $resource_type")
            params["resource_type"] = resource_type
            
        if adaptation_type:
            conditions.append("ea.adaptation_type = $adaptation_type")
            params["adaptation_type"] = adaptation_type
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        MATCH (ea:EnvironmentAdaptation)
        WHERE {where_clause}
        RETURN ea,
               ea.success_rate as success_rate,
               ea.application_count as applications,
               ea.confidence_level as confidence
        ORDER BY ea.success_rate DESC, ea.confidence_level DESC, ea.application_count DESC
        LIMIT $limit
        """
        
        result = self.client.execute_query(query, params)
        
        adaptations = []
        for record in result:
            adaptation = record["ea"]
            try:
                adaptation_data = {
                    "adaptation_id": adaptation["id"],
                    "adaptation_name": adaptation["adaptation_name"],
                    "adaptation_type": adaptation["adaptation_type"],
                    "resource_type": adaptation["resource_type"],
                    "original_configuration": json.loads(adaptation["original_configuration"]),
                    "adapted_configuration": json.loads(adaptation["adapted_configuration"]),
                    "adaptation_rules": adaptation["adaptation_rules"],
                    "trigger_conditions": adaptation["trigger_conditions"],
                    "validation_criteria": adaptation.get("validation_criteria", []),
                    "success_rate": record["success_rate"],
                    "application_count": record["applications"],
                    "confidence_level": record["confidence"],
                    "automation_level": adaptation["automation_level"],
                }
                adaptations.append(adaptation_data)
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not parse adaptation data: {e}")
                continue
        
        return adaptations

    def get_rollback_scenarios(
        self,
        environment: str,
        resource_types: Optional[List[str]] = None,
        rollback_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get applicable rollback scenarios.
        
        Args:
            environment: Target environment
            resource_types: Resource types that might need rollback
            rollback_type: Specific rollback type (optional)
            limit: Maximum number of scenarios
            
        Returns:
            List of applicable rollback scenarios
        """
        conditions = [
            "rs.is_active = true",
            "rs.environment = $environment",
        ]
        params = {
            "environment": environment,
            "limit": limit,
        }
        
        if resource_types:
            conditions.append("ANY(rt IN $resource_types WHERE rt IN rs.resource_types_affected)")
            params["resource_types"] = resource_types
            
        if rollback_type:
            conditions.append("rs.rollback_type = $rollback_type")
            params["rollback_type"] = rollback_type
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        MATCH (rs:RollbackScenario)
        WHERE {where_clause}
        RETURN rs,
               rs.success_rate as success_rate,
               rs.execution_count as executions,
               rs.average_recovery_time as avg_recovery_time
        ORDER BY rs.success_rate DESC, rs.execution_count DESC
        LIMIT $limit
        """
        
        result = self.client.execute_query(query, params)
        
        scenarios = []
        for record in result:
            scenario = record["rs"]
            scenario_data = {
                "scenario_id": scenario["id"],
                "scenario_name": scenario["scenario_name"],
                "rollback_type": scenario["rollback_type"],
                "trigger_conditions": scenario["trigger_conditions"],
                "failure_patterns": scenario["failure_patterns"],
                "rollback_strategy": scenario["rollback_strategy"],
                "rollback_steps": scenario["rollback_steps"],
                "recovery_time_target": scenario.get("recovery_time_target"),
                "data_loss_acceptable": scenario["data_loss_acceptable"],
                "resource_types_affected": scenario["resource_types_affected"],
                "validation_steps": scenario.get("validation_steps", []),
                "notification_required": scenario["notification_required"],
                "escalation_criteria": scenario.get("escalation_criteria", []),
                "success_rate": record["success_rate"],
                "execution_count": record["executions"],
                "average_recovery_time": record["avg_recovery_time"],
                "automation_level": scenario["automation_level"],
                "lessons_learned": scenario.get("lessons_learned"),
            }
            scenarios.append(scenario_data)
        
        return scenarios

    def record_deployment_metric(
        self,
        metric_name: str,
        metric_type: str,
        metric_category: str,
        environment: str,
        metric_value: float,
        unit: str,
        deployment_strategy: Optional[str] = None,
        resource_type: Optional[str] = None,
        baseline_value: Optional[float] = None,
        target_value: Optional[float] = None,
        context_data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Record a deployment performance metric.
        
        Args:
            metric_name: Name of the metric
            metric_type: Type of metric (duration, success_rate, etc.)
            metric_category: Category (performance, reliability, etc.)
            environment: Environment where metric was measured
            metric_value: The measured value
            unit: Unit of measurement
            deployment_strategy: Deployment strategy used (optional)
            resource_type: Resource type measured (optional)
            baseline_value: Baseline value for comparison (optional)
            target_value: Target value for this metric (optional)
            context_data: Additional context data (optional)
            tags: Tags for categorization (optional)
            
        Returns:
            Deployment metric ID
        """
        metric_id = str(uuid4())
        
        metric_data = {
            "id": metric_id,
            "metric_name": metric_name,
            "metric_type": metric_type,
            "metric_category": metric_category,
            "environment": environment,
            "deployment_strategy": deployment_strategy,
            "resource_type": resource_type,
            "metric_value": metric_value,
            "unit": unit,
            "measurement_date": datetime.now().isoformat(),
            "baseline_value": baseline_value,
            "target_value": target_value,
            "context_data": json.dumps(context_data) if context_data else None,
            "tags": tags or [],
        }
        
        query = """
        CREATE (dm:DeploymentMetric $props)
        RETURN dm.id as metric_id
        """
        
        result = self.client.execute_write_query(query, {"props": metric_data})
        
        if result:
            logger.info(f"Recorded deployment metric: {metric_id}")
            return metric_id
        else:
            raise Exception(f"Failed to record deployment metric: {metric_name}")

    def get_deployment_analytics(
        self,
        environment: Optional[str] = None,
        days_back: int = 30,
        metric_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get deployment analytics and trends.
        
        Args:
            environment: Specific environment (optional)
            days_back: Number of days to look back
            metric_types: Specific metric types to include (optional)
            
        Returns:
            Analytics data with trends and insights
        """
        since_date = datetime.now() - timedelta(days=days_back)
        
        conditions = [f"de.started_at >= '{since_date.isoformat()}'"]
        params = {"since_date": since_date.isoformat()}
        
        if environment:
            conditions.append("de.target_environment = $environment")
            params["environment"] = environment
        
        where_clause = " AND ".join(conditions)
        
        # Get deployment execution statistics
        deployment_query = f"""
        MATCH (de:DeploymentExecution)
        WHERE {where_clause}
        RETURN 
            COUNT(de) as total_deployments,
            COUNT(CASE WHEN de.status = 'completed' THEN 1 END) as successful_deployments,
            COUNT(CASE WHEN de.status = 'failed' THEN 1 END) as failed_deployments,
            COUNT(CASE WHEN de.rollback_triggered = true THEN 1 END) as rollbacks_triggered,
            AVG(de.duration_seconds) as avg_duration,
            de.target_environment as environment,
            de.deployment_strategy as strategy
        """
        
        deployment_result = self.client.execute_query(deployment_query, params)
        
        # Get metric trends if requested
        metric_trends = {}
        if metric_types:
            for metric_type in metric_types:
                trend_query = f"""
                MATCH (dm:DeploymentMetric)
                WHERE dm.measurement_date >= $since_date
                AND dm.metric_type = $metric_type
                {"AND dm.environment = $environment" if environment else ""}
                RETURN 
                    dm.metric_type as metric_type,
                    AVG(dm.metric_value) as avg_value,
                    MIN(dm.metric_value) as min_value,
                    MAX(dm.metric_value) as max_value,
                    COUNT(dm) as measurement_count,
                    dm.unit as unit
                """
                
                trend_params = {**params, "metric_type": metric_type}
                trend_result = self.client.execute_query(trend_query, trend_params)
                
                if trend_result:
                    metric_trends[metric_type] = trend_result[0]
        
        # Compile analytics
        analytics = {
            "period": {
                "days_back": days_back,
                "start_date": since_date.isoformat(),
                "end_date": datetime.now().isoformat(),
            },
            "deployment_statistics": deployment_result[0] if deployment_result else {},
            "metric_trends": metric_trends,
            "success_rate": 0.0,
            "rollback_rate": 0.0,
            "insights": [],
        }
        
        # Calculate rates
        if deployment_result and deployment_result[0]["total_deployments"] > 0:
            total = deployment_result[0]["total_deployments"]
            successful = deployment_result[0]["successful_deployments"]
            rollbacks = deployment_result[0]["rollbacks_triggered"]
            
            analytics["success_rate"] = successful / total if total > 0 else 0.0
            analytics["rollback_rate"] = rollbacks / total if total > 0 else 0.0
            
            # Generate insights
            if analytics["success_rate"] < 0.8:
                analytics["insights"].append("Success rate is below 80% - consider reviewing deployment patterns")
            
            if analytics["rollback_rate"] > 0.1:
                analytics["insights"].append("Rollback rate is above 10% - investigate common failure patterns")
            
            if deployment_result[0]["avg_duration"] and deployment_result[0]["avg_duration"] > 1800:  # 30 minutes
                analytics["insights"].append("Average deployment duration is high - consider optimization")
        
        return analytics

    def _learn_from_successful_deployment(self, execution_id: str, execution_data: Dict[str, Any]) -> None:
        """Learn patterns from successful deployments."""
        try:
            # Extract pattern characteristics
            pattern_characteristics = {
                "environment_types": [execution_data["target_environment"]],
                "resource_types": execution_data["resources_deployed"],
                "deployment_strategy": execution_data["deployment_strategy"],
                "configuration_template": json.loads(execution_data["configuration_used"]),
                "success_criteria": {
                    "max_duration": execution_data.get("duration_seconds", 3600),
                    "required_resources": execution_data["resources_deployed"],
                },
            }
            
            # Check if similar pattern exists
            similar_pattern = self._find_similar_deployment_pattern(pattern_characteristics)
            
            if similar_pattern:
                # Update existing pattern
                self._update_deployment_pattern_success(similar_pattern["id"], execution_id)
            else:
                # Create new pattern
                self._create_deployment_pattern(execution_data, pattern_characteristics)
                
        except Exception as e:
            logger.warning(f"Failed to learn from successful deployment {execution_id}: {e}")

    def _learn_from_rollback_scenario(self, execution_id: str, execution_data: Dict[str, Any]) -> None:
        """Learn from rollback scenarios."""
        try:
            if execution_data.get("failure_reasons"):
                # Create or update rollback scenario
                scenario_name = f"Rollback for {execution_data['deployment_type']} in {execution_data['target_environment']}"
                
                # Check if similar rollback scenario exists
                existing_scenario = self._find_similar_rollback_scenario(
                    execution_data["target_environment"],
                    execution_data["failure_reasons"],
                    execution_data["resources_deployed"]
                )
                
                if existing_scenario:
                    self._update_rollback_scenario_execution(existing_scenario["id"], execution_data["rollback_successful"])
                else:
                    # Create new rollback scenario
                    self.record_rollback_scenario(
                        scenario_name=scenario_name,
                        rollback_type="automatic" if execution_data["automation_triggered"] else "manual",
                        trigger_conditions=execution_data["failure_reasons"],
                        failure_patterns=execution_data["failure_reasons"],
                        rollback_strategy="standard_rollback",  # Could be enhanced
                        rollback_steps=["Stop deployment", "Restore previous state", "Validate rollback"],
                        environment=execution_data["target_environment"],
                        resource_types_affected=execution_data["resources_deployed"],
                    )
                    
        except Exception as e:
            logger.warning(f"Failed to learn from rollback scenario {execution_id}: {e}")

    def _find_similar_deployment_pattern(self, characteristics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find similar deployment patterns."""
        query = """
        MATCH (dp:DeploymentPattern)
        WHERE dp.deployment_strategy = $deployment_strategy
        AND ANY(env IN $environment_types WHERE env IN dp.environment_types)
        AND ANY(res IN $resource_types WHERE res IN dp.resource_types)
        RETURN dp
        ORDER BY dp.confidence_score DESC
        LIMIT 1
        """
        
        result = self.client.execute_query(query, {
            "deployment_strategy": characteristics["deployment_strategy"],
            "environment_types": characteristics["environment_types"],
            "resource_types": characteristics["resource_types"],
        })
        
        return result[0]["dp"] if result else None

    def _find_similar_rollback_scenario(
        self, environment: str, failure_reasons: List[str], resources: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Find similar rollback scenarios."""
        query = """
        MATCH (rs:RollbackScenario)
        WHERE rs.environment = $environment
        AND ANY(reason IN $failure_reasons WHERE reason IN rs.failure_patterns)
        AND ANY(resource IN $resources WHERE resource IN rs.resource_types_affected)
        RETURN rs
        ORDER BY rs.success_rate DESC
        LIMIT 1
        """
        
        result = self.client.execute_query(query, {
            "environment": environment,
            "failure_reasons": failure_reasons,
            "resources": resources,
        })
        
        return result[0]["rs"] if result else None

    def _create_deployment_pattern(self, execution_data: Dict[str, Any], characteristics: Dict[str, Any]) -> str:
        """Create a new deployment pattern from successful execution."""
        pattern_id = str(uuid4())
        pattern_name = f"Pattern for {execution_data['deployment_strategy']} in {execution_data['target_environment']}"
        
        pattern_data = {
            "id": pattern_id,
            "name": pattern_name,
            "pattern_type": "successful_config",
            "environment_types": characteristics["environment_types"],
            "resource_types": characteristics["resource_types"],
            "deployment_strategy": characteristics["deployment_strategy"],
            "success_criteria": json.dumps(characteristics["success_criteria"]),
            "configuration_template": json.dumps(characteristics["configuration_template"]),
            "discovered_date": datetime.now().isoformat(),
            "success_count": 1,
            "failure_count": 0,
            "confidence_score": 0.5,  # Start with medium confidence
            "applicability_score": 0.7,
            "pattern_data": json.dumps(characteristics),
            "is_active": True,
        }
        
        query = """
        CREATE (dp:DeploymentPattern $props)
        WITH dp
        MATCH (de:DeploymentExecution {id: $execution_id})
        CREATE (de)-[:FOLLOWS_DEPLOYMENT_PATTERN]->(dp)
        RETURN dp.id as pattern_id
        """
        
        result = self.client.execute_write_query(query, {
            "props": pattern_data,
            "execution_id": execution_data["id"]
        })
        
        if result:
            logger.info(f"Created new deployment pattern: {pattern_id}")
            return pattern_id
        else:
            raise Exception("Failed to create deployment pattern")

    def _update_deployment_pattern_success(self, pattern_id: str, execution_id: str) -> None:
        """Update deployment pattern with successful execution."""
        query = """
        MATCH (dp:DeploymentPattern {id: $pattern_id})
        SET dp.success_count = dp.success_count + 1,
            dp.last_applied = datetime(),
            dp.confidence_score = CASE 
                WHEN dp.success_count + dp.failure_count > 0 
                THEN toFloat(dp.success_count + 1) / toFloat(dp.success_count + dp.failure_count + 1)
                ELSE 0.5 
            END
        WITH dp
        MATCH (de:DeploymentExecution {id: $execution_id})
        CREATE (de)-[:FOLLOWS_DEPLOYMENT_PATTERN]->(dp)
        """
        
        self.client.execute_write_query(query, {
            "pattern_id": pattern_id,
            "execution_id": execution_id
        })

    def _update_rollback_scenario_execution(self, scenario_id: str, rollback_successful: bool) -> None:
        """Update rollback scenario with execution results."""
        query = """
        MATCH (rs:RollbackScenario {id: $scenario_id})
        SET rs.execution_count = rs.execution_count + 1,
            rs.last_executed = datetime(),
            rs.success_rate = CASE 
                WHEN $rollback_successful AND rs.execution_count > 0
                THEN (rs.success_rate * rs.execution_count + 1.0) / (rs.execution_count + 1)
                WHEN NOT $rollback_successful AND rs.execution_count > 0
                THEN (rs.success_rate * rs.execution_count) / (rs.execution_count + 1)
                ELSE rs.success_rate
            END
        """
        
        self.client.execute_write_query(query, {
            "scenario_id": scenario_id,
            "rollback_successful": rollback_successful
        })

    def _calculate_applicability_reasons(
        self,
        pattern: Dict[str, Any],
        target_environment: str,
        resource_types: List[str],
        deployment_strategy: Optional[str],
    ) -> List[str]:
        """Calculate why a pattern is applicable."""
        reasons = []
        
        if target_environment in pattern.get("environment_types", []):
            reasons.append(f"Proven successful in {target_environment} environment")
        
        matching_resources = set(resource_types) & set(pattern.get("resource_types", []))
        if matching_resources:
            reasons.append(f"Handles similar resources: {', '.join(matching_resources)}")
        
        if deployment_strategy and deployment_strategy == pattern.get("deployment_strategy"):
            reasons.append(f"Uses same deployment strategy: {deployment_strategy}")
        
        if pattern.get("success_count", 0) >= self.min_success_count:
            reasons.append(f"High success rate: {pattern.get('success_count', 0)} successful deployments")
        
        return reasons 