# Phase 16.2: Specialized Expertise Modules - How-To Guide

## Overview

This guide provides step-by-step instructions for deploying, configuring, and using the Phase 16.2 Specialized Expertise Modules. These modules extend the Multi-Domain Architecture with industry-specific knowledge bases for Distillation (American Whiskey), Pharmaceutical Manufacturing, and Power Generation.

## Prerequisites

### System Requirements
- Python 3.12+
- Phase 16.1 Multi-Domain Architecture (must be deployed first)
- Neo4j database (optional, for knowledge graph integration)
- Minimum 4GB RAM for full deployment

### Environment Setup
```bash
# Required environment variables
export SPECIALIZED_AGENTS_ENABLED=true
export WHISKEY_DISTILLATION_ENABLED=true
export PHARMACEUTICAL_ENABLED=true
export POWER_GENERATION_ENABLED=true

# Industry-specific configuration
export TTB_COMPLIANCE_MODE=strict
export GMP_VALIDATION_LEVEL=full
export NERC_COMPLIANCE_ENABLED=true

# Knowledge base configuration
export SPECIALIZED_KNOWLEDGE_CACHE_SIZE=1000
export REGULATORY_UPDATE_INTERVAL=86400
export PROCESS_TEMPLATE_VALIDATION=enabled
```

## Installation and Deployment

### Step 1: Validate Phase 16.1 Foundation
```bash
# Validate existing Phase 16.1 components
python -m src.ignition.modules.sme_agent.phase_16_cli_integration validate-env

# Check agent coordination framework
python -m src.ignition.modules.sme_agent.phase_16_cli_integration coordination-status
```

### Step 2: Deploy Specialized Expertise Modules
```bash
# Deploy with progressive complexity
python -m src.ignition.modules.sme_agent.phase_16_cli_integration deploy standard

# Register specialized agents
python -m src.ignition.modules.sme_agent.phase_16_cli_integration register-agent distillation_whiskey
python -m src.ignition.modules.sme_agent.phase_16_cli_integration register-agent pharmaceutical
python -m src.ignition.modules.sme_agent.phase_16_cli_integration register-agent power_generation
```

### Step 3: Validate Specialized Agent Deployment
```python
# Python validation script
from src.ignition.modules.sme_agent.specialized import (
    BaseSpecializedAgent,
    DistillationWhiskeyAgent,
    PharmaceuticalAgent,
    PowerGenerationAgent
)

# Test agent creation
whiskey_agent = DistillationWhiskeyAgent()
pharma_agent = PharmaceuticalAgent()
power_agent = PowerGenerationAgent()

# Validate environment
print(f"Whiskey Agent: {await whiskey_agent.validate_environment()}")
print(f"Pharma Agent: {await pharma_agent.validate_environment()}")
print(f"Power Agent: {await power_agent.validate_environment()}")
```

## Usage Examples

### Distillation: American Whiskey Agent

#### Basic Bourbon Production Query
```python
from src.ignition.modules.sme_agent.multi_domain_architecture import AgentTask, DomainType
from src.ignition.modules.sme_agent.specialized import DistillationWhiskeyAgent

# Create whiskey agent
whiskey_agent = DistillationWhiskeyAgent()

# Query bourbon production optimization
task = AgentTask(
    query="Optimize fermentation temperature for high-corn mash bill",
    domain=DomainType.CHEMICAL_PROCESS,
    context={
        "mash_bill": {"corn": 75, "wheat": 15, "malted_barley": 10},
        "current_temp": 82,
        "target_abv": 8.5
    }
)

result = await whiskey_agent.process_task(task)
print(f"Recommendation: {result['response']}")
print(f"TTB Compliance: {result['specialized_metadata']['regulatory_considerations']}")
```

#### TTB Compliance Checking
```python
# Check TTB compliance for distillation process
compliance_task = AgentTask(
    query="Validate TTB compliance for bourbon distillation process",
    domain=DomainType.CHEMICAL_PROCESS,
    context={
        "proof_off_still": 155,
        "proof_into_barrel": 120,
        "mash_bill": {"corn": 51, "wheat": 20, "malted_barley": 29}
    }
)

compliance_result = await whiskey_agent.process_task(compliance_task)
```

### Pharmaceutical Manufacturing Agent

#### GMP Compliance Validation
```python
from src.ignition.modules.sme_agent.specialized import PharmaceuticalAgent

# Create pharmaceutical agent
pharma_agent = PharmaceuticalAgent()

# Query GMP compliance for tablet production
gmp_task = AgentTask(
    query="Validate GMP compliance for direct compression tablet process",
    domain=DomainType.CHEMICAL_PROCESS,
    context={
        "product": "immediate_release_tablet",
        "api_content": 10,  # mg
        "batch_size": 100000,  # tablets
        "compression_force": 8  # kN
    }
)

gmp_result = await pharma_agent.process_task(gmp_task)
print(f"GMP Status: {gmp_result['specialized_metadata']['regulatory_compliance']}")
```

#### Validation Protocol Generation
```python
# Generate IQ/OQ/PQ validation protocol
validation_task = AgentTask(
    query="Generate validation protocol for tablet compression equipment",
    domain=DomainType.CHEMICAL_PROCESS,
    context={
        "equipment": "rotary_tablet_press",
        "validation_type": "OQ",
        "product_family": "immediate_release"
    }
)

validation_result = await pharma_agent.process_task(validation_task)
```

### Power Generation Agent

#### Thermal Plant Optimization
```python
from src.ignition.modules.sme_agent.specialized import PowerGenerationAgent

# Create power generation agent
power_agent = PowerGenerationAgent()

# Query thermal plant efficiency optimization
efficiency_task = AgentTask(
    query="Improve heat rate for natural gas combined cycle plant",
    domain=DomainType.ELECTRICAL,
    context={
        "plant_type": "combined_cycle",
        "fuel": "natural_gas",
        "current_heat_rate": 7200,  # BTU/kWh
        "target_efficiency": 58  # %
    }
)

efficiency_result = await power_agent.process_task(efficiency_task)
print(f"Optimization: {efficiency_result['response']}")
print(f"NERC Compliance: {efficiency_result['specialized_metadata']['regulatory_considerations']}")
```

#### Grid Integration Analysis
```python
# Analyze grid integration requirements
grid_task = AgentTask(
    query="Analyze grid integration requirements for wind farm",
    domain=DomainType.ELECTRICAL,
    context={
        "capacity": 100,  # MW
        "technology": "wind_turbine",
        "grid_voltage": 138,  # kV
        "location": "midwest_iso"
    }
)

grid_result = await power_agent.process_task(grid_task)
```

## Advanced Configuration

### Progressive Complexity Deployment

#### Basic Level Configuration
```python
# Basic level: Single specialized agent
DEPLOYMENT_CONFIG = {
    "complexity_level": "basic",
    "max_agents": 1,
    "max_concurrent_tasks": 3,
    "enabled_agents": ["distillation_whiskey"]  # User choice
}
```

#### Standard Level Configuration
```python
# Standard level: All specialized agents
DEPLOYMENT_CONFIG = {
    "complexity_level": "standard",
    "max_agents": 3,
    "max_concurrent_tasks": 10,
    "enabled_agents": ["distillation_whiskey", "pharmaceutical", "power_generation"],
    "performance_monitoring": True
}
```

#### Advanced Level Configuration
```python
# Advanced level: Full knowledge integration
DEPLOYMENT_CONFIG = {
    "complexity_level": "advanced",
    "max_agents": 10,
    "max_concurrent_tasks": 50,
    "enabled_agents": ["all"],
    "knowledge_integration": True,
    "cross_domain_correlation": True,
    "regulatory_monitoring": True
}
```

#### Enterprise Level Configuration
```python
# Enterprise level: Full platform capabilities
DEPLOYMENT_CONFIG = {
    "complexity_level": "enterprise",
    "max_agents": "unlimited",
    "max_concurrent_tasks": "unlimited",
    "enabled_agents": ["all"],
    "cloud_integration": True,
    "real_time_updates": True,
    "multi_site_deployment": True,
    "advanced_analytics": True
}
```

### Custom Knowledge Base Integration

#### Adding Custom Process Templates
```python
# Extend whiskey agent with custom distillery process
custom_process = {
    "custom_bourbon": {
        "mash_bills": {
            "corn_percentage": {"min": 60, "typical": 75},
            "rye_percentage": {"max": 35},
            "malted_barley": {"typical": 12}
        },
        "fermentation": {
            "temperature_range": {"min": 78, "max": 88, "unit": "F"},
            "duration": {"min": 96, "max": 120, "unit": "hours"},
            "yeast_strain": "proprietary_blend"
        }
    }
}

# Register custom process template
whiskey_agent.register_custom_process_template("custom_bourbon", custom_process)
```

#### Adding Custom Regulatory Frameworks
```python
# Add state-specific regulations
state_regulations = {
    "kentucky_bourbon_regulations": {
        "description": "Kentucky-specific bourbon production requirements",
        "requirements": [
            "Minimum 51% corn in mash bill",
            "Aged in new charred oak containers",
            "Distilled to no more than 80% ABV",
            "Entered into barrel at no more than 62.5% ABV"
        ]
    }
}

# Register custom regulatory framework
whiskey_agent.register_custom_regulatory_framework("kentucky_bourbon", state_regulations)
```

## Monitoring and Maintenance

### Performance Monitoring
```python
# Monitor specialized agent performance
from src.ignition.modules.sme_agent.phase_16_cli_integration import get_performance_metrics

# Get overall performance metrics
metrics = get_performance_metrics()
print(f"Specialized Agent Response Time: {metrics['specialized_avg_response_time']}")
print(f"Knowledge Cache Hit Rate: {metrics['knowledge_cache_hit_rate']}")
print(f"Regulatory Compliance Rate: {metrics['regulatory_compliance_rate']}")

# Get agent-specific metrics
whiskey_metrics = whiskey_agent.get_performance_metrics()
pharma_metrics = pharma_agent.get_performance_metrics()
power_metrics = power_agent.get_performance_metrics()
```

### Health Checks
```bash
# System health check
python -m src.ignition.modules.sme_agent.phase_16_cli_integration status

# Agent-specific health checks
python -c "
from src.ignition.modules.sme_agent.specialized import *
import asyncio

async def health_check():
    agents = [DistillationWhiskeyAgent(), PharmaceuticalAgent(), PowerGenerationAgent()]
    for agent in agents:
        health = await agent.health_check()
        print(f'{agent.agent_id}: {health}')

asyncio.run(health_check())
"
```

### Knowledge Base Updates
```python
# Update regulatory frameworks
await whiskey_agent.update_regulatory_frameworks()
await pharma_agent.update_regulatory_frameworks()
await power_agent.update_regulatory_frameworks()

# Refresh process templates
await whiskey_agent.refresh_process_templates()
await pharma_agent.refresh_process_templates()
await power_agent.refresh_process_templates()
```

## Troubleshooting

### Common Issues and Solutions

#### Agent Creation Failures
```python
# Issue: Agent fails to initialize
# Solution: Check environment variables and dependencies

try:
    agent = DistillationWhiskeyAgent()
except Exception as e:
    print(f"Agent creation failed: {e}")
    
    # Check environment
    import os
    required_vars = ['SPECIALIZED_AGENTS_ENABLED', 'WHISKEY_DISTILLATION_ENABLED']
    for var in required_vars:
        if not os.getenv(var):
            print(f"Missing environment variable: {var}")
```

#### Task Compatibility Issues
```python
# Issue: Task not routed to specialized agent
# Solution: Check domain and keywords

task = AgentTask(
    query="bourbon production optimization",  # Include industry keywords
    domain=DomainType.CHEMICAL_PROCESS,      # Correct domain
    context={"industry": "whiskey_distillation"}  # Explicit industry context
)

# Verify task compatibility
is_compatible = whiskey_agent.is_task_compatible(task)
print(f"Task compatible: {is_compatible}")
```

#### Regulatory Compliance Failures
```python
# Issue: Regulatory validation fails
# Solution: Update regulatory frameworks and check compliance mode

# Check current regulatory frameworks
frameworks = whiskey_agent.get_regulatory_frameworks()
print(f"Available frameworks: {frameworks}")

# Update regulatory data
await whiskey_agent.update_regulatory_frameworks()

# Check compliance mode
compliance_mode = os.getenv('TTB_COMPLIANCE_MODE', 'standard')
print(f"Compliance mode: {compliance_mode}")
```

### Performance Optimization

#### Memory Optimization
```python
# Optimize knowledge cache size
import os
os.environ['SPECIALIZED_KNOWLEDGE_CACHE_SIZE'] = '2000'  # Increase cache

# Enable memory profiling
os.environ['MEMORY_PROFILING_ENABLED'] = 'true'
```

#### Response Time Optimization
```python
# Enable async processing
import asyncio

async def batch_processing():
    tasks = [
        whiskey_agent.process_task(task1),
        pharma_agent.process_task(task2),
        power_agent.process_task(task3)
    ]
    results = await asyncio.gather(*tasks)
    return results

# Use batch processing for multiple queries
results = await batch_processing()
```

## Integration with Existing Systems

### Integration with Phase 16.1 Agents
```python
# Coordinate between domain and specialized agents
from src.ignition.modules.sme_agent.agent_coordination_framework import AgentCoordinationFramework

# Register specialized agents with coordination framework
coordinator = AgentCoordinationFramework()
await coordinator.register_agent(whiskey_agent)
await coordinator.register_agent(pharma_agent)
await coordinator.register_agent(power_agent)

# Submit tasks through coordinator
task = AgentTask(
    query="Optimize distillation column efficiency",
    domain=DomainType.CHEMICAL_PROCESS
)
result = await coordinator.submit_task(task)
```

### Integration with External Systems
```python
# Integration with plant historians
historian_config = {
    "historian_type": "osisoft_pi",
    "server_url": os.getenv('PI_SERVER_URL'),
    "username": os.getenv('PI_USERNAME'),
    "password": os.getenv('PI_PASSWORD')
}

# Configure historian integration
whiskey_agent.configure_historian_integration(historian_config)

# Query real-time data
real_time_data = await whiskey_agent.get_real_time_data([
    'FERMENTATION_TANK_01.TEMPERATURE',
    'FERMENTATION_TANK_01.PH',
    'FERMENTATION_TANK_01.SPECIFIC_GRAVITY'
])
```

## Security and Compliance

### Security Configuration
```bash
# Enable security features
export SPECIALIZED_AGENT_SECURITY_ENABLED=true
export ENCRYPTION_KEY_PATH="/path/to/encryption.key"
export AUDIT_LOGGING_ENABLED=true
export RBAC_ENABLED=true
```

### Compliance Auditing
```python
# Generate compliance audit report
audit_report = await whiskey_agent.generate_compliance_audit()
print(f"TTB Compliance Status: {audit_report['ttb_compliance']}")
print(f"Safety Protocol Adherence: {audit_report['safety_compliance']}")
print(f"Process Template Validation: {audit_report['process_validation']}")
```

## Best Practices

### Development Best Practices
1. **Always validate environment first** before deploying specialized agents
2. **Use progressive complexity** - start with basic level and scale up
3. **Implement comprehensive error handling** for industry-specific failures
4. **Regular regulatory updates** to maintain compliance
5. **Monitor performance metrics** continuously
6. **Test with real-world scenarios** from each industry

### Operational Best Practices
1. **Regular health checks** for all specialized agents
2. **Backup knowledge bases** before major updates
3. **Monitor regulatory compliance** in real-time
4. **Implement proper logging** for audit trails
5. **Use batch processing** for multiple queries
6. **Keep documentation updated** with process changes

### Security Best Practices
1. **Never hardcode sensitive information** in configuration
2. **Use environment variables** for all credentials
3. **Enable audit logging** for compliance tracking
4. **Implement role-based access control** for agent operations
5. **Regular security updates** for all dependencies
6. **Encrypt sensitive data** in transit and at rest

## Support and Resources

### Documentation Links
- [Phase 16.2 Architecture Documentation](../PHASE_16_2_SPECIALIZED_EXPERTISE_MODULES.md)
- [Implementation Summary](../phase_summary/PHASE_16_2_SPECIALIZED_EXPERTISE_MODULES_SUMMARY.md)
- [Phase 16.1 Foundation Guide](phase16-enterprise-ai-guide.md)

### Community and Support
- GitHub Issues: Report bugs and feature requests
- Documentation Wiki: Community-contributed guides
- Industry Forums: Domain-specific discussions

### Training and Certification
- Specialized Agent Development Course
- Industry-Specific Implementation Training
- Regulatory Compliance Certification
- Advanced Integration Workshops 