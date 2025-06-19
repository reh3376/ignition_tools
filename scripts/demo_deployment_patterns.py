#!/usr/bin/env python3
"""Demo script for Deployment Pattern Learning System.

This script populates the Neo4j database with sample deployment patterns,
environment adaptations, rollback scenarios, and metrics to demonstrate
the deployment pattern learning functionality.
"""

import random
from datetime import datetime, timedelta

from src.ignition.graph.client import IgnitionGraphClient
from src.ignition.graph.deployment_pattern_learner import DeploymentPatternLearner


def create_sample_deployment_executions(learner: DeploymentPatternLearner) -> list[str]:
    """Create sample deployment executions."""
    print("🚀 Creating sample deployment executions...")

    execution_ids = []

    # Sample deployment scenarios
    scenarios = [
        {
            "name": "Production HMI Update",
            "type": "update",
            "environment": "production",
            "gateway": "prod-gateway-01.company.com",
            "strategy": "blue_green",
            "resources": ["project", "tag_provider", "database"],
            "config": {
                "backup_enabled": True,
                "validation_timeout": 300,
                "rollback_threshold": 0.95,
                "notification_channels": ["email", "slack"],
            },
            "success_rate": 0.95,
        },
        {
            "name": "Staging Environment Sync",
            "type": "migration",
            "environment": "staging",
            "gateway": "staging-gateway-01.company.com",
            "strategy": "rolling",
            "resources": ["project", "security"],
            "config": {
                "backup_enabled": True,
                "validation_timeout": 180,
                "parallel_deployments": 2,
            },
            "success_rate": 0.88,
        },
        {
            "name": "Development Feature Deploy",
            "type": "initial",
            "environment": "development",
            "gateway": "dev-gateway-01.company.com",
            "strategy": "direct",
            "resources": ["project"],
            "config": {
                "backup_enabled": False,
                "validation_timeout": 60,
                "skip_tests": True,
            },
            "success_rate": 0.92,
        },
        {
            "name": "Emergency Hotfix",
            "type": "hotfix",
            "environment": "production",
            "gateway": "prod-gateway-01.company.com",
            "strategy": "direct",
            "resources": ["project", "script"],
            "config": {
                "backup_enabled": True,
                "validation_timeout": 120,
                "emergency_mode": True,
                "approval_bypass": True,
            },
            "success_rate": 0.78,
        },
    ]

    # Create multiple executions for each scenario
    for scenario in scenarios:
        for i in range(random.randint(5, 15)):
            # Determine if this execution should succeed
            should_succeed = random.random() < scenario["success_rate"]

            # Generate execution details
            started_at = datetime.now() - timedelta(
                days=random.randint(1, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            if should_succeed:
                duration = random.randint(60, 1800)  # 1-30 minutes
                completed_at = started_at + timedelta(seconds=duration)
                status = "completed"
                failure_reasons = None
                rollback_triggered = False
                rollback_successful = None
            else:
                duration = random.randint(30, 600)  # 30 seconds to 10 minutes
                completed_at = started_at + timedelta(seconds=duration)
                status = "failed"
                failure_reasons = random.choice(
                    [
                        ["Database connection timeout", "Validation failed"],
                        ["Resource conflict detected", "Dependency missing"],
                        ["Gateway communication error"],
                        ["Insufficient permissions", "Security validation failed"],
                        ["Resource lock timeout", "Concurrent deployment detected"],
                    ]
                )
                rollback_triggered = random.choice([True, False])
                rollback_successful = (
                    random.choice([True, False]) if rollback_triggered else None
                )

            execution_name = f"{scenario['name']} - Run {i + 1}"

            try:
                execution_id = learner.record_deployment_execution(
                    execution_name=execution_name,
                    deployment_type=scenario["type"],
                    target_environment=scenario["environment"],
                    gateway_host=scenario["gateway"],
                    deployment_strategy=scenario["strategy"],
                    resources_deployed=scenario["resources"],
                    configuration_used=scenario["config"],
                    status=status,
                    started_at=started_at,
                    completed_at=completed_at,
                    failure_reasons=failure_reasons,
                    rollback_triggered=rollback_triggered,
                    rollback_successful=rollback_successful,
                    user_id=random.choice(
                        ["engineer1", "operator1", "admin", "devops1"]
                    ),
                    automation_triggered=random.choice([True, False]),
                    performance_data=(
                        {
                            "cpu_usage": random.uniform(20, 80),
                            "memory_usage": random.uniform(30, 70),
                            "network_latency": random.uniform(10, 100),
                        }
                        if should_succeed
                        else None
                    ),
                    lessons_learned=(
                        random.choice(
                            [
                                "Database connection pool needs tuning",
                                "Validation timeout should be increased",
                                "Resource dependencies need better documentation",
                                "Rollback procedure worked well",
                                None,
                            ]
                        )
                        if not should_succeed
                        else None
                    ),
                )
                execution_ids.append(execution_id)

            except Exception as e:
                print(f"   ❌ Failed to create execution {execution_name}: {e}")

    print(f"✅ Created {len(execution_ids)} deployment executions")
    return execution_ids


def create_sample_environment_adaptations(
    learner: DeploymentPatternLearner,
) -> list[str]:
    """Create sample environment adaptations."""
    print("🔄 Creating sample environment adaptations...")

    adaptation_ids = []

    # Sample adaptations
    adaptations = [
        {
            "name": "Database Connection String Adaptation",
            "source": "development",
            "target": "production",
            "type": "configuration_change",
            "resource": "database",
            "original": {
                "host": "dev-db.company.com",
                "port": 3306,
                "ssl": False,
                "pool_size": 5,
            },
            "adapted": {
                "host": "prod-db.company.com",
                "port": 3306,
                "ssl": True,
                "pool_size": 20,
                "connection_timeout": 30,
            },
            "rules": [
                "Enable SSL for production databases",
                "Increase connection pool size for production load",
                "Add connection timeout for reliability",
            ],
            "triggers": [
                "Target environment is production",
                "Resource type is database",
                "SSL is disabled in source",
            ],
        },
        {
            "name": "Tag Provider Security collections.abc.Mapping",
            "source": "staging",
            "target": "production",
            "type": "security_adjustment",
            "resource": "tag_provider",
            "original": {
                "security_zone": "staging_zone",
                "authentication": "basic",
                "encryption": False,
            },
            "adapted": {
                "security_zone": "production_zone",
                "authentication": "certificate",
                "encryption": True,
                "audit_logging": True,
            },
            "rules": [
                "Map staging security zone to production zone",
                "Upgrade authentication to certificate-based",
                "Enable encryption and audit logging",
            ],
            "triggers": [
                "Target environment is production",
                "Resource type is tag_provider",
                "Security zone contains 'staging'",
            ],
        },
        {
            "name": "Performance Tuning for Production",
            "source": "staging",
            "target": "production",
            "type": "performance_tuning",
            "resource": "project",
            "original": {
                "scan_rate": 1000,
                "cache_size": "100MB",
                "thread_pool": 4,
            },
            "adapted": {
                "scan_rate": 500,
                "cache_size": "500MB",
                "thread_pool": 8,
                "optimization_level": "high",
            },
            "rules": [
                "Reduce scan rate for production stability",
                "Increase cache size for better performance",
                "Double thread pool for production load",
            ],
            "triggers": [
                "Target environment is production",
                "Resource type is project",
                "Performance optimization required",
            ],
        },
    ]

    for adaptation in adaptations:
        try:
            adaptation_id = learner.record_environment_adaptation(
                adaptation_name=adaptation["name"],
                source_environment=adaptation["source"],
                target_environment=adaptation["target"],
                adaptation_type=adaptation["type"],
                resource_type=adaptation["resource"],
                original_configuration=adaptation["original"],
                adapted_configuration=adaptation["adapted"],
                adaptation_rules=adaptation["rules"],
                trigger_conditions=adaptation["triggers"],
                validation_criteria=[
                    "Configuration syntax is valid",
                    "All required fields are present",
                    "Security requirements are met",
                ],
                automation_level=random.choice(
                    ["manual", "semi_automated", "fully_automated"]
                ),
            )
            adaptation_ids.append(adaptation_id)

        except Exception as e:
            print(f"   ❌ Failed to create adaptation {adaptation['name']}: {e}")

    print(f"✅ Created {len(adaptation_ids)} environment adaptations")
    return adaptation_ids


def create_sample_rollback_scenarios(learner: DeploymentPatternLearner) -> list[str]:
    """Create sample rollback scenarios."""
    print("🚨 Creating sample rollback scenarios...")

    scenario_ids = []

    # Sample rollback scenarios
    scenarios = [
        {
            "name": "Database Connection Failure Rollback",
            "type": "automatic",
            "triggers": [
                "Database connection timeout > 30 seconds",
                "Connection pool exhausted",
                "Database authentication failure",
            ],
            "patterns": [
                "Database connection timeout",
                "Connection pool exhausted",
                "Authentication failure",
            ],
            "strategy": "immediate_rollback",
            "steps": [
                "Stop current deployment",
                "Restore previous database configuration",
                "Restart database connections",
                "Validate database connectivity",
                "Resume normal operations",
            ],
            "environment": "production",
            "resources": ["database", "tag_provider"],
            "recovery_target": 300,  # 5 minutes
            "data_loss_ok": False,
        },
        {
            "name": "Project Validation Failure Rollback",
            "type": "manual",
            "triggers": [
                "Project validation failed",
                "Critical alarms triggered",
                "Performance degradation > 50%",
            ],
            "patterns": [
                "Validation failure",
                "Critical alarms",
                "Performance degradation",
            ],
            "strategy": "staged_rollback",
            "steps": [
                "Assess impact and scope",
                "Notify operations team",
                "Create rollback checkpoint",
                "Restore previous project version",
                "Validate system functionality",
                "Update incident log",
            ],
            "environment": "production",
            "resources": ["project", "script"],
            "recovery_target": 900,  # 15 minutes
            "data_loss_ok": False,
        },
        {
            "name": "Security Zone Conflict Rollback",
            "type": "semi_automatic",
            "triggers": [
                "Security zone conflict detected",
                "Permission validation failed",
                "Unauthorized access attempt",
            ],
            "patterns": [
                "Security zone conflict",
                "Permission failure",
                "Unauthorized access",
            ],
            "strategy": "security_rollback",
            "steps": [
                "Immediately isolate affected resources",
                "Restore previous security configuration",
                "Audit security logs",
                "Validate access permissions",
                "Generate security report",
            ],
            "environment": "production",
            "resources": ["security", "project"],
            "recovery_target": 180,  # 3 minutes
            "data_loss_ok": False,
        },
    ]

    for scenario in scenarios:
        try:
            scenario_id = learner.record_rollback_scenario(
                scenario_name=scenario["name"],
                rollback_type=scenario["type"],
                trigger_conditions=scenario["triggers"],
                failure_patterns=scenario["patterns"],
                rollback_strategy=scenario["strategy"],
                rollback_steps=scenario["steps"],
                environment=scenario["environment"],
                resource_types_affected=scenario["resources"],
                recovery_time_target=scenario["recovery_target"],
                data_loss_acceptable=scenario["data_loss_ok"],
                validation_steps=[
                    "Verify system functionality",
                    "Check critical alarms",
                    "Validate performance metrics",
                ],
                notification_required=True,
                escalation_criteria=[
                    "Recovery time exceeds target by 50%",
                    "Multiple rollback attempts failed",
                    "Data integrity concerns",
                ],
                automation_level=scenario["type"].replace("_", "_"),
            )
            scenario_ids.append(scenario_id)

        except Exception as e:
            print(f"   ❌ Failed to create scenario {scenario['name']}: {e}")

    print(f"✅ Created {len(scenario_ids)} rollback scenarios")
    return scenario_ids


def create_sample_deployment_metrics(learner: DeploymentPatternLearner) -> list[str]:
    """Create sample deployment metrics."""
    print("📊 Creating sample deployment metrics...")

    metric_ids = []

    # Sample metrics over the last 30 days
    environments = ["development", "staging", "production"]
    strategies = ["direct", "rolling", "blue_green"]

    metric_types = [
        {
            "name": "deployment_duration",
            "type": "duration",
            "category": "performance",
            "unit": "seconds",
            "base_value": 300,
            "variance": 200,
        },
        {
            "name": "success_rate",
            "type": "success_rate",
            "category": "reliability",
            "unit": "percentage",
            "base_value": 90,
            "variance": 10,
        },
        {
            "name": "rollback_rate",
            "type": "rollback_rate",
            "category": "reliability",
            "unit": "percentage",
            "base_value": 5,
            "variance": 5,
        },
        {
            "name": "resource_count",
            "type": "resource_count",
            "category": "efficiency",
            "unit": "count",
            "base_value": 3,
            "variance": 2,
        },
    ]

    # Generate metrics for the last 30 days
    for day in range(30):
        datetime.now() - timedelta(days=day)

        for environment in environments:
            for strategy in strategies:
                for metric_def in metric_types:
                    # Add some realistic variance
                    value = metric_def["base_value"] + random.uniform(
                        -metric_def["variance"], metric_def["variance"]
                    )

                    # Ensure reasonable bounds
                    if metric_def["unit"] == "percentage":
                        value = max(0, min(100, value))
                    elif metric_def["unit"] == "seconds":
                        value = max(30, value)
                    elif metric_def["unit"] == "count":
                        value = max(1, int(value))

                    try:
                        metric_id = learner.record_deployment_metric(
                            metric_name=metric_def["name"],
                            metric_type=metric_def["type"],
                            metric_category=metric_def["category"],
                            environment=environment,
                            metric_value=value,
                            unit=metric_def["unit"],
                            deployment_strategy=strategy,
                            context_data={
                                "measurement_day": day,
                                "environment": environment,
                                "strategy": strategy,
                            },
                            tags=[environment, strategy, metric_def["category"]],
                        )
                        metric_ids.append(metric_id)

                    except Exception as e:
                        print(
                            f"   ❌ Failed to create metric {metric_def['name']}: {e}"
                        )

    print(f"✅ Created {len(metric_ids)} deployment metrics")
    return metric_ids


def demonstrate_deployment_pattern_learning():
    """Demonstrate the deployment pattern learning system."""
    print("🎯 Deployment Pattern Learning System Demo")
    print("=" * 60)

    # Initialize components
    client = IgnitionGraphClient()
    if not client.connect():
        print("❌ Failed to connect to Neo4j database")
        return False

    learner = DeploymentPatternLearner(client)

    try:
        # Create sample data
        execution_ids = create_sample_deployment_executions(learner)
        adaptation_ids = create_sample_environment_adaptations(learner)
        scenario_ids = create_sample_rollback_scenarios(learner)
        metric_ids = create_sample_deployment_metrics(learner)

        print("\n🧠 Testing Pattern Learning Functionality...")

        # Test deployment recommendations
        print("\n1. Testing Deployment Recommendations:")
        recommendations = learner.get_deployment_recommendations(
            target_environment="production",
            resource_types=["project", "database"],
            deployment_strategy="blue_green",
            limit=3,
        )
        print(f"   Found {len(recommendations)} recommendations")
        for rec in recommendations:
            print(
                f"   • {rec['pattern_name']} (confidence: {rec['confidence_score']:.1%})"
            )

        # Test environment adaptations
        print("\n2. Testing Environment Adaptations:")
        adaptations = learner.get_environment_adaptations(
            source_environment="staging", target_environment="production", limit=3
        )
        print(f"   Found {len(adaptations)} adaptations")
        for adaptation in adaptations:
            print(
                f"   • {adaptation['adaptation_name']} (success rate: {adaptation['success_rate']:.1%})"
            )

        # Test rollback scenarios
        print("\n3. Testing Rollback Scenarios:")
        scenarios = learner.get_rollback_scenarios(
            environment="production", resource_types=["database", "project"], limit=3
        )
        print(f"   Found {len(scenarios)} rollback scenarios")
        for scenario in scenarios:
            print(
                f"   • {scenario['scenario_name']} (success rate: {scenario['success_rate']:.1%})"
            )

        # Test deployment analytics
        print("\n4. Testing Deployment Analytics:")
        analytics = learner.get_deployment_analytics(
            environment="production",
            days_back=30,
            metric_types=["duration", "success_rate"],
        )
        stats = analytics.get("deployment_statistics", {})
        print(f"   Total deployments: {stats.get('total_deployments', 0)}")
        print(f"   Success rate: {analytics.get('success_rate', 0):.1%}")
        print(f"   Rollback rate: {analytics.get('rollback_rate', 0):.1%}")

        insights = analytics.get("insights", [])
        if insights:
            print("   Insights:")
            for insight in insights:
                print(f"     • {insight}")

        print("\n🎉 Deployment Pattern Learning Demo Completed Successfully!")
        print("\n📋 Summary:")
        print(f"   • {len(execution_ids)} deployment executions created")
        print(f"   • {len(adaptation_ids)} environment adaptations created")
        print(f"   • {len(scenario_ids)} rollback scenarios created")
        print(f"   • {len(metric_ids)} deployment metrics created")
        print("\n💡 You can now use the CLI commands to explore the learned patterns:")
        print("   ign deploy recommendations -e production -r project")
        print("   ign deploy adaptations -s staging -t production")
        print("   ign deploy rollback-scenarios -e production")
        print("   ign deploy analytics -e production -d 30")

        return True

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

    finally:
        client.disconnect()


if __name__ == "__main__":
    demonstrate_deployment_pattern_learning()
