# Phase 14.1 MPC Framework - Comprehensive How-To Guide

## 🎛️ Overview

This comprehensive guide covers the Phase 14.1 Model Predictive Control (MPC) Framework implementation in the IGN Scripts system. Following the crawl_mcp.py methodology, this guide provides step-by-step instructions for understanding, creating, training, testing, implementing, and monitoring MPCs in production environments.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Environment Setup](#environment-setup)
3. [MPC Controller Creation](#mpc-controller-creation)
4. [Safety System Configuration](#safety-system-configuration)
5. [Training and Testing](#training-and-testing)
6. [Production Implementation](#production-implementation)
7. [Monitoring and Analytics](#monitoring-and-analytics)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Features](#advanced-features)
10. [Best Practices](#best-practices)

---

## 🎯 System Overview

### What is the MPC Framework?

The Phase 14.1 MPC Framework is a production-ready Model Predictive Control system designed for industrial automation within the Ignition platform. It provides:

- **Real-time Optimization**: Advanced control algorithms with constraint handling
- **Safety Integration**: SIL-rated safety systems with emergency procedures
- **Performance Monitoring**: Comprehensive analytics and KPI tracking
- **Alarm Management**: Multi-level alarm system with escalation
- **Production Scheduling**: Integrated production optimization

### Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    MPC Framework Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface (mpc-framework commands)                         │
├─────────────────────────────────────────────────────────────────┤
│  MPC Controller  │  Safety System  │  Alarm Manager             │
├─────────────────────────────────────────────────────────────────┤
│  Performance Monitor  │  Production Scheduler                   │
├─────────────────────────────────────────────────────────────────┤
│  Control Strategies  │  Knowledge Graph Integration             │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features

- **Mathematical Foundation**: Linear/nonlinear MPC algorithms with state-space models
- **Optimization Engine**: Real-time constraint handling and multi-objective optimization
- **Safety Systems**: Emergency procedures, fail-safe modes, and SIS integration
- **Analytics**: Real-time KPIs, trend analysis, and performance assessment

---

## 🔧 Environment Setup

### Step 1: Environment Validation

Before using the MPC Framework, validate your environment:

```bash
# Validate complete MPC environment
python -m src.main module mpc-framework validate-env
```

**Expected Output:**
```
🔍 Phase 14: MPC Framework Environment Validation

Validating MPC Controller Environment...
✅ MPC Environment: VALID

Validating Safety System Environment...
✅ Safety Environment: VALID

Overall Environment Status:
✅ READY FOR PRODUCTION
```

### Step 2: Configure Environment Variables

**IMPORTANT**: Copy the complete environment template to create your .env file:

```bash
# Copy the comprehensive environment template
cp config/env.example .env
```

The template includes all required MPC Framework and Safety System configurations:

```env
# ================================
# MPC Framework Configuration - Phase 14.1
# ================================
# MPC Controller Settings
MPC_SOLVER_TIMEOUT=30.0
MPC_MAX_ITERATIONS=100
MPC_CONVERGENCE_TOLERANCE=1e-6
MPC_TEMP_DIR=/tmp/mpc_framework

# MPC Optimization Settings
MPC_PREDICTION_HORIZON=20
MPC_CONTROL_HORIZON=5
MPC_SAMPLE_TIME=1.0
MPC_OPTIMIZATION_METHOD=SLSQP

# ================================
# Safety System Configuration - CRITICAL
# ================================
# Emergency Response Settings
SAFETY_EMERGENCY_TIMEOUT=5.0
SAFETY_WATCHDOG_INTERVAL=1.0
SAFETY_BACKUP_SYSTEMS=plc,safety_relay,manual_override
SAFETY_NOTIFICATION_ENDPOINTS=safety@company.com,operator@company.com,emergency@company.com

# Safety Hardware Configuration
EMERGENCY_STOP_GPIO_PIN=18
SAFETY_DATABASE_URL=postgresql://user:pass@localhost/safety_db
SAFETY_BACKUP_CHANNELS=ethernet,serial,radio

# Safety Integrity Levels
SAFETY_DEFAULT_SIL_LEVEL=SIL_2
SAFETY_CRITICAL_TIMEOUT=2.0
SAFETY_FAIL_SAFE_MODE=true

# ================================
# Alarm Management System
# ================================
ALARM_DATABASE_URL=postgresql://user:pass@localhost/alarms
ALARM_NOTIFICATION_ENDPOINTS=alarm@company.com,sms:+1234567890,teams:webhook_url
ALARM_ESCALATION_TIMEOUT=300
ALARM_MAX_ACTIVE_ALARMS=1000
ALARM_PRIORITY_LEVELS=LOW,MEDIUM,HIGH,CRITICAL,EMERGENCY

# ================================
# Performance Monitoring
# ================================
PERFORMANCE_DATA_RETENTION_DAYS=30
PERFORMANCE_ANALYTICS_INTERVAL=60
PERFORMANCE_KPI_CALCULATION_WINDOW=3600
PERFORMANCE_ALERT_THRESHOLDS=efficiency:0.8,availability:0.95

# ================================
# Production Scheduler
# ================================
SCHEDULER_UPDATE_INTERVAL=300
SCHEDULER_MAX_CONCURRENT_TASKS=10
SCHEDULER_TASK_TIMEOUT=3600
SCHEDULER_BACKUP_INTERVAL=1800
```

### Step 3: Install Required Dependencies

Ensure all safety system dependencies are installed:

```bash
# Install watchdog for safety system monitoring
pip install watchdog>=6.0.0

# Or install all requirements
pip install -r requirements.txt
```

### Step 4: Verify System Status

Check the overall system status:

```bash
# Show comprehensive system status
python -m src.main module mpc-framework status --show-config
```

**Expected Output:**
```
📊 MPC Framework System Status

Environment Status:
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ Component      ┃ Status   ┃ Issues ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ MPC Controller │ ✅ VALID │ 0      │
│ Safety System  │ ✅ VALID │ 0      │
└────────────────┴──────────┴────────┘
```

### Step 5: Run Comprehensive Test Suite

Validate all components are working correctly:

```bash
# Run complete MPC Framework test suite
python -m src.main module mpc-framework run-test-suite --verbose
```

**Expected Output:**
```
🧪 Running MPC Framework Test Suite

Test 1: Environment Validation
✅ Environment validation passed

Test 2: MPC Controller
✅ MPC Controller test passed (0.00s)

Test 3: Safety System
✅ Safety System test passed (0.00s)

Test Suite Summary:
Tests Passed: 3/3
Total Time: 0.01s
✅ ALL TESTS PASSED
```

---

## 🎛️ MPC Controller Creation

### Understanding MPC Controllers

Model Predictive Control (MPC) is an advanced control strategy that:
1. Uses a mathematical model to predict future process behavior
2. Optimizes control actions over a prediction horizon
3. Handles constraints on inputs and outputs
4. Recalculates at each time step (receding horizon)

### Step 1: Create MPC Configuration

Generate a basic MPC controller configuration:

```bash
# Create MPC controller configuration
python -m src.main module mpc-framework controller create-config \
  --name "Reactor_Temperature_Control" \
  --model-type "FOPDT" \
  --prediction-horizon 20 \
  --control-horizon 5 \
  --sample-time 1.0 \
  --output mpc_config.json
```

**Configuration Parameters:**

- **name**: Unique identifier for the MPC controller
- **model-type**: Process model type (FOPDT, StateSpace, ARX)
- **prediction-horizon**: Number of future steps to predict (typically 10-50)
- **control-horizon**: Number of control moves to optimize (typically 2-10)
- **sample-time**: Control loop execution interval in seconds

### Step 2: Understanding Model Types

#### FOPDT (First Order Plus Dead Time)
Best for simple processes with single input/output:
```python
# Transfer function: K * exp(-td*s) / (tau*s + 1)
# Where: K = gain, tau = time constant, td = dead time
```

#### State Space
For multi-input/multi-output systems:
```python
# x(k+1) = A*x(k) + B*u(k)
# y(k) = C*x(k) + D*u(k)
```

#### ARX (AutoRegressive with eXogenous inputs)
For data-driven models:
```python
# y(k) = a1*y(k-1) + ... + an*y(k-n) + b1*u(k-1) + ... + bm*u(k-m)
```

### Step 3: Test MPC Configuration

Test your MPC controller configuration:

```bash
# Test MPC controller with configuration
python -m src.main module mpc-framework controller test \
  --config-file mpc_config.json \
  --verbose
```

**Expected Output:**
```
🧪 Testing MPC Controller
✅ MPC Controller test passed in 0.45s

Performance Metrics:
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric               ┃ Value                ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ optimization_time    │ 0.023                │
│ constraint_violations│ 0                    │
│ setpoint_tracking    │ 0.95                 │
│ control_effort       │ 0.12                 │
└──────────────────────┴──────────────────────┘
```

---

## 🛡️ Safety System Configuration

### Understanding Safety Integration

The safety system provides:
- **Safety Integrity Levels (SIL)**: SIL-1 through SIL-4 compliance
- **Emergency Procedures**: Automated shutdown and recovery
- **Watchdog Monitoring**: Continuous system health checks using the `watchdog` package
- **Fail-safe Behavior**: Default to safe state on failures

### Step 1: Create Safety Configuration

```bash
# Create safety system configuration
python -m src.main module mpc-framework safety create-config \
  --name "Reactor_Safety_System" \
  --safety-level "SIL_2" \
  --watchdog-interval 1.0 \
  --output safety_config.json
```

### Step 2: Test Safety System

```bash
# Test safety system configuration
python -m src.main module mpc-framework safety test \
  --config-file safety_config.json \
  --verbose
```

**Expected Output:**
```
🧪 Testing Safety System
✅ Safety system test passed in 0.00s

Tests Passed:
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Test                 ┃ Status    ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ parameter_update     │ ✅ PASSED │
│ alarm_creation       │ ✅ PASSED │
│ alarm_acknowledgment │ ✅ PASSED │
└──────────────────────┴───────────┘
```

---

## 🧪 Training and Testing

### MPC Model Training Process

The MPC Framework supports automated model training and optimization:

### Step 1: Prepare Training Data

Collect historical process data with:
- Input variables (manipulated variables)
- Output variables (controlled variables)
- Disturbance variables (measured disturbances)
- Sampling time consistent with control requirements

**Data Format:**
```csv
timestamp,steam_flow,cooling_water,temperature,pressure
2024-01-01 00:00:00,45.2,12.5,98.3,102.1
2024-01-01 00:01:00,46.1,12.3,98.7,102.3
...
```

### Step 2: Model Identification

Use the training CLI to identify process models:

```bash
# Train MPC model from historical data
python -m src.main module mpc-framework controller train \
  --data-file process_data.csv \
  --input-columns "steam_flow,cooling_water" \
  --output-columns "temperature,pressure" \
  --model-type "StateSpace" \
  --validation-split 0.2 \
  --output-model trained_model.json
```

### Step 3: Model Validation

Validate the trained model:

```bash
# Validate trained model
python -m src.main module mpc-framework controller validate \
  --model-file trained_model.json \
  --test-data validation_data.csv \
  --metrics "mse,mae,r2" \
  --output validation_report.json
```

**Validation Metrics:**
- **MSE**: Mean Squared Error
- **MAE**: Mean Absolute Error
- **R²**: Coefficient of Determination
- **Fit Percentage**: Model fit quality

---

## 🚀 Production Implementation

### Step 1: Pre-deployment Checklist

Before deploying to production, verify:

```bash
# Run comprehensive test suite
python -m src.main module mpc-framework run-test-suite --verbose
```

**Required Results:**
- ✅ Environment validation passed
- ✅ MPC Controller test passed
- ✅ Safety System test passed
- ✅ Integration tests passed
- ✅ Performance benchmarks met

### Step 2: Production Deployment

#### Option A: Ignition Module Deployment

1. **Export Module**:
```bash
# Export as Ignition module
python -m src.main module mpc-framework export \
  --config-file production_config.json \
  --output MPC_Framework_v14.modl
```

2. **Install in Ignition**:
   - Open Ignition Designer
   - Go to Tools → Module Manager
   - Install MPC_Framework_v14.modl
   - Restart Ignition Gateway

3. **Configure in Ignition**:
   - Add MPC tags to tag browser
   - Configure OPC-UA connections
   - Set up historical data collection

#### Option B: Standalone Service Deployment

```bash
# Deploy as standalone service
python -m src.main module mpc-framework deploy \
  --config-file production_config.json \
  --deployment-type "service" \
  --host "0.0.0.0" \
  --port 8080
```

---

## 📊 Monitoring and Analytics

### Real-time Monitoring

#### KPI Calculations

Monitor key performance indicators:

```bash
# View current KPIs
python -m src.main module mpc-framework analytics kpis
```

**Standard KPIs:**
- **Efficiency**: Actual vs. theoretical performance
- **Availability**: Uptime percentage
- **Throughput**: Production rate
- **Quality**: Product specification compliance
- **Energy Efficiency**: Energy consumption per unit

### Analytics Commands

```bash
# Generate performance report
python -m src.main module mpc-framework analytics report \
  --start-time "2024-01-01 00:00:00" \
  --end-time "2024-01-01 23:59:59" \
  --output performance_report.pdf

# Trend analysis
python -m src.main module mpc-framework analytics trends \
  --parameter "temperature" \
  --window-hours 24 \
  --forecast-hours 4

# Alarm analysis
python -m src.main module mpc-framework analytics alarms \
  --priority "HIGH,CRITICAL" \
  --days 7 \
  --output alarm_analysis.json
```

### Predictive Analytics

The framework includes predictive capabilities:

```bash
# Predict potential issues
python -m src.main module mpc-framework predict \
  --model-file predictive_model.pkl \
  --horizon-hours 4 \
  --confidence 0.95
```

---

## 🔧 Troubleshooting

### Common Safety System Issues

#### Issue: "Watchdog timer not available"
**Solution:**
```bash
pip install watchdog>=6.0.0
```

#### Issue: "Safety environment variable not set"
**Solution:**
1. Copy the complete environment template:
   ```bash
   cp config/env.example .env
   ```
2. Update the .env file with your specific values
3. Verify with: `python -m src.main module mpc-framework validate-env`

#### Issue: "Safety database URL not configured"
**Solution:**
Add to your .env file:
```env
SAFETY_DATABASE_URL=postgresql://user:pass@localhost/safety_db
```

#### Issue: "Emergency stop GPIO pin not configured"
**Solution:**
Add to your .env file:
```env
EMERGENCY_STOP_GPIO_PIN=18
```

#### Issue: "Insufficient backup communication channels"
**Solution:**
Add to your .env file:
```env
SAFETY_BACKUP_CHANNELS=ethernet,serial,radio
```

### Environment Variable Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `SAFETY_EMERGENCY_TIMEOUT` | Emergency response timeout (seconds) | `5.0` |
| `SAFETY_WATCHDOG_INTERVAL` | Watchdog check interval (seconds) | `1.0` |
| `SAFETY_BACKUP_SYSTEMS` | Backup safety systems | `plc,safety_relay,manual_override` |
| `SAFETY_NOTIFICATION_ENDPOINTS` | Emergency notification endpoints | `safety@company.com,operator@company.com` |
| `EMERGENCY_STOP_GPIO_PIN` | Emergency stop GPIO pin number | `18` |
| `SAFETY_DATABASE_URL` | Safety database connection | `postgresql://user:pass@localhost/safety_db` |
| `SAFETY_BACKUP_CHANNELS` | Communication backup channels | `ethernet,serial,radio` |

### Validation Commands

```bash
# Basic environment validation
python -m src.main module mpc-framework validate-env

# Comprehensive system status
python -m src.main module mpc-framework status --show-config

# Test specific components
python -m src.main module mpc-framework safety test --verbose
python -m src.main module mpc-framework controller test --verbose

# Run complete test suite
python -m src.main module mpc-framework run-test-suite --verbose
```

---

## 🚀 Advanced Features

### Multi-Loop Coordination

For complex processes with multiple MPC controllers:

```bash
# Configure multi-loop coordination
python -m src.main module mpc-framework coordination create \
  --controllers "reactor_temp,reactor_pressure,distillation" \
  --strategy "hierarchical" \
  --output coordination_config.json
```

### Economic MPC

Optimize economic objectives by configuring revenue and cost terms in your MPC configuration.

### Adaptive MPC

Enable model adaptation:

```bash
# Configure adaptive MPC
python -m src.main module mpc-framework adaptive configure \
  --adaptation-method "recursive_least_squares" \
  --forgetting-factor 0.98 \
  --adaptation-threshold 0.1
```

---

## 📚 Best Practices

### Design Guidelines

#### 1. Model Selection
- **Simple processes**: Use FOPDT models
- **MIMO systems**: Use State Space models
- **Data-driven**: Use ARX/ARMAX models
- **Nonlinear**: Use neural network models

#### 2. Horizon Selection
- **Prediction horizon**: 2-3 times the process settling time
- **Control horizon**: 10-20% of prediction horizon
- **Economic MPC**: Longer horizons for economic optimization

#### 3. Constraint Design
- **Hard constraints**: Safety-critical limits
- **Soft constraints**: Operational preferences
- **Rate constraints**: Equipment limitations
- **Zone constraints**: Acceptable operating ranges

#### 4. Tuning Guidelines
- **Start conservative**: Low aggressiveness, high stability
- **Iterative tuning**: Gradual performance improvement
- **Simulation first**: Validate before production
- **Monitor performance**: Continuous optimization

### Safety Considerations

#### 1. Fail-Safe Design
- Default to safe state on failures
- Independent safety systems
- Redundant measurements
- Manual override capability

#### 2. Alarm Management
- Minimize alarm floods
- Prioritize by safety impact
- Clear escalation procedures
- Regular alarm rationalization

#### 3. Cybersecurity
- Secure communication protocols
- Access control and authentication
- Regular security updates
- Network segmentation

### Maintenance Procedures

#### 1. Regular Maintenance
```bash
# Weekly health check
python -m src.main module mpc-framework health-check --detailed

# Monthly performance review
python -m src.main module mpc-framework analytics monthly-report

# Quarterly model validation
python -m src.main module mpc-framework validate-models --all
```

#### 2. Model Updates
- Monitor model performance
- Update when performance degrades
- Validate before deployment
- Maintain model history

#### 3. Configuration Management
- Version control configurations
- Document all changes
- Test configuration changes
- Backup before updates

---

## 📞 Support and Resources

### Documentation
- [Installation Guide](installation-guide.md)
- [Security Guide](security-guide.md)
- [Troubleshooting Guide](troubleshooting-guide.md)
- [API Reference](../api/index.md)

### Command Reference
```bash
# Quick help
python -m src.main module mpc-framework --help

# Command-specific help
python -m src.main module mpc-framework controller --help
python -m src.main module mpc-framework safety --help
python -m src.main module mpc-framework analytics --help
```

### Getting Help
- GitHub Issues: [IGN Scripts Issues](https://github.com/your-org/ign-scripts/issues)
- Documentation: [Online Documentation](https://docs.ign-scripts.com)
- Community: [Discussion Forum](https://community.ign-scripts.com)

---

## 📝 Conclusion

The Phase 14.1 MPC Framework provides a comprehensive solution for advanced process control in industrial environments. By following this guide and the crawl_mcp.py methodology, you can successfully implement, train, test, and monitor MPC systems in production.

Remember to:
- Always validate your environment first
- Test thoroughly before production deployment
- Monitor performance continuously
- Follow safety best practices
- Keep documentation updated

For additional support or advanced use cases, consult the API documentation or contact the development team.

---

*This guide follows the crawl_mcp.py methodology for systematic, reliable implementation of industrial automation systems.*
