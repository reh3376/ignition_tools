# Phase 16 Enterprise AI Platform - How-to Guide

## 🎯 Overview

This guide provides step-by-step instructions for deploying and using the Phase 16 Enterprise AI Platform, following the methodology established in `crawl_mcp.py`. The platform provides multi-domain SME agents with progressive complexity deployment.

## 📋 Prerequisites

### Environment Requirements
- Python 3.12+
- Neo4j database (for knowledge graph functionality)
- Virtual environment setup
- Required environment variables configured

### Required Environment Variables
```bash
# Neo4j Knowledge Graph
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Phase 16 Configuration
PHASE16_COORDINATION_STRATEGY=expertise_based
PHASE16_MAX_TASK_QUEUE_SIZE=100
PHASE16_AGENT_TIMEOUT=30
PHASE16_ENABLE_PERFORMANCE_MONITORING=true
```

## 🚀 Quick Start

### Step 1: Environment Validation
Following crawl_mcp.py methodology, always validate environment first:

```bash
# Validate SME agent environment
python -m src.main module sme phase16 validate-env
```

Expected output:
```
✅ Environment validation: VALID
✅ Neo4j connection: ACTIVE
✅ Phase 16 configuration: READY
```

### Step 2: Deploy with Progressive Complexity

Choose your deployment complexity level:

```bash
# Basic deployment (1 agent, 3 concurrent tasks)
python -m src.main module sme phase16 deploy basic

# Standard deployment (3 agents, 10 concurrent tasks)
python -m src.main module sme phase16 deploy standard

# Advanced deployment (10 agents, 50 concurrent tasks)
python -m src.main module sme phase16 deploy advanced

# Enterprise deployment (unlimited agents and tasks)
python -m src.main module sme phase16 deploy enterprise
```

### Step 3: Verify Deployment Status

```bash
# Check overall system status
python -m src.main module sme phase16 status

# Get detailed coordination status
python -m src.main module sme phase16 coordination-status
```

## 🔧 Core Usage Patterns

### Working with Electrical Engineering Agent

The electrical engineering agent provides specialized expertise in:
- Power systems analysis
- Motor control design
- PLC programming
- Electrical safety compliance
- Arc flash analysis
- Instrumentation design

#### Submit Electrical Engineering Tasks

```bash
# Analyze motor control system
python -m src.main module sme phase16 submit-task electrical "Analyze 480V motor control system with VFD"

# Design PLC ladder logic
python -m src.main module sme phase16 submit-task electrical "Design PLC ladder logic for conveyor system"

# Calculate arc flash hazard
python -m src.main module sme phase16 submit-task electrical "Calculate arc flash hazard for 480V MCC"

# Power system analysis
python -m src.main module sme phase16 submit-task electrical "Design power distribution for manufacturing facility"
```

#### Expected Response Format
```json
{
  "success": true,
  "task_id": "task_12345",
  "domain": "electrical",
  "agent_assigned": "electrical_engineering_agent",
  "estimated_completion": "2025-06-27T12:30:00Z",
  "status": "queued"
}
```

### Multi-Domain Task Coordination

The coordination framework intelligently routes tasks to appropriate domain agents:

```bash
# Submit tasks to different domains
python -m src.main module sme phase16 submit-task electrical "Motor starter design"
python -m src.main module sme phase16 submit-task mechanical "Pump sizing calculation"
python -m src.main module sme phase16 submit-task chemical "Distillation column optimization"
```

## 📊 Monitoring and Performance

### Performance Metrics

```bash
# Get comprehensive performance metrics
python -m src.main module sme phase16 performance-metrics
```

Expected output:
```json
{
  "system_performance": {
    "active_agents": 2,
    "completed_tasks": 15,
    "active_tasks": 3,
    "average_response_time": 1.2,
    "success_rate": 0.95
  },
  "agent_performance": {
    "electrical_engineering_agent": {
      "tasks_completed": 12,
      "average_time": 0.8,
      "success_rate": 0.98
    }
  }
}
```

### Task Queue Management

```bash
# Check coordination status
python -m src.main module sme phase16 coordination-status
```

Monitor key metrics:
- **Queue Size**: Number of pending tasks
- **Active Agents**: Currently processing agents
- **Coordination Strategy**: Current routing strategy
- **Load Distribution**: Task distribution across agents

## 🧪 Testing and Validation

### Run Comprehensive Test Suite

```bash
# Execute full test framework
python -m src.main module sme phase16 test-framework
```

The test framework includes:
- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-agent coordination testing
- **Performance Tests**: Load and scalability testing
- **Error Handling Tests**: Failure scenario validation

### Validate Specific Components

```python
# Python API usage example
from ignition.modules.sme_agent.phase_16_cli_integration import cli_manager

# Validate environment programmatically
result = cli_manager.validate_environment()
if result['valid']:
    print("✅ Environment ready for deployment")
else:
    print(f"❌ Environment issues: {result['issues']}")
```

## 🔄 Progressive Complexity Deployment

### Understanding Complexity Levels

| Level | Max Agents | Max Tasks | Use Case |
|-------|------------|-----------|----------|
| **Basic** | 1 | 3 | Development and testing |
| **Standard** | 3 | 10 | Small to medium operations |
| **Advanced** | 10 | 50 | Large industrial facilities |
| **Enterprise** | Unlimited | Unlimited | Multi-site enterprise deployment |

### Upgrading Complexity

```bash
# Start with basic
python -m src.main module sme phase16 deploy basic

# Upgrade to standard when ready
python -m src.main module sme phase16 deploy standard

# Scale to advanced for production
python -m src.main module sme phase16 deploy advanced
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### Environment Validation Failures

**Issue**: `NEO4J_USER environment variable missing`
```bash
# Solution: Add to .env file
echo "NEO4J_USER=neo4j" >> .env
```

**Issue**: `Neo4j connection failed`
```bash
# Check Neo4j service status
docker ps | grep neo4j

# Restart Neo4j if needed
docker restart neo4j-container
```

#### Agent Registration Issues

**Issue**: `Agent registration failed`
```bash
# Check agent status
python -m src.main module sme phase16 status

# Re-register specific agent
python -m src.main module sme phase16 register-agent electrical
```

#### Performance Issues

**Issue**: High response times
```bash
# Check performance metrics
python -m src.main module sme phase16 performance-metrics

# Consider upgrading complexity level
python -m src.main module sme phase16 deploy advanced
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set debug environment variables
export PHASE16_DEBUG=true
export PHASE16_LOG_LEVEL=DEBUG

# Run commands with verbose output
python -m src.main module sme phase16 status --verbose
```

## 📚 Advanced Usage

### Custom Agent Registration

```python
# Register custom domain agent
from ignition.modules.sme_agent.multi_domain_architecture import DomainType

# Register mechanical engineering agent (when available)
await cli_manager.register_agent_for_domain("mechanical")
```

### Batch Task Processing

```python
# Submit multiple tasks programmatically
tasks = [
    ("electrical", "Analyze motor control system"),
    ("electrical", "Design PLC ladder logic"),
    ("electrical", "Calculate arc flash hazard")
]

for domain, query in tasks:
    result = await cli_manager.submit_task_to_domain(domain, query)
    print(f"Task submitted: {result['task_id']}")
```

### Performance Optimization

```bash
# Monitor system resources
python -m src.main module sme phase16 performance-metrics

# Adjust coordination strategy if needed
export PHASE16_COORDINATION_STRATEGY=load_balanced

# Increase task queue size for high throughput
export PHASE16_MAX_TASK_QUEUE_SIZE=200
```

## 🔐 Security Considerations

### Environment Variable Security
- Store sensitive credentials in `.env` file
- Never commit `.env` file to version control
- Use secure password for Neo4j database
- Rotate credentials regularly

### Network Security
- Use secure Neo4j connection (bolt+s://)
- Implement firewall rules for database access
- Monitor access logs for suspicious activity

## 📖 Additional Resources

- **[Phase 16 Architecture Guide](../PHASE_16_ENTERPRISE_AI_PLATFORM.md)** - Complete technical documentation
- **[Phase 16 Completion Summary](../PHASE_16_COMPLETION_SUMMARY.md)** - Implementation results and metrics
- **[crawl_mcp.py](../crawl%20test/crawl_mcp.py)** - Development methodology reference

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the comprehensive test framework output
3. Consult the Phase 16 architecture documentation
4. Validate environment configuration

## 🎯 Next Steps

After successful Phase 16 deployment:
1. **Expand Domain Agents**: Add mechanical and chemical engineering agents
2. **Phase 16.2**: Implement specialized expertise modules
3. **Phase 16.3**: Deploy cloud-native architecture
4. **Integration**: Connect with existing workflow systems

---
*This guide follows the crawl_mcp.py methodology with comprehensive validation, testing, and progressive complexity deployment.*
