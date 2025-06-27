# Advanced Process Control - Quick Reference 📋

**Phase 15: Advanced Process Control Suite**
**Version**: 15.0.0
**Status**: ✅ Production Ready

---

## Essential Commands

### Environment & Status
```bash
# Validate environment
ign advanced-process-control validate-env --verbose

# Check system status
ign advanced-process-control status

# Run comprehensive tests
ign advanced-process-control test --verbose
```

### PID Tuning
```bash
# AI-enhanced tuning (recommended)
ign advanced-process-control tune-pid --method ai_enhanced --setpoint 75.0 --verbose

# Conservative tuning (safe)
ign advanced-process-control tune-pid --method imc --setpoint 50.0

# Quick tuning (fast)
ign advanced-process-control tune-pid --method ziegler_nichols_open

# Custom setpoint
ign advanced-process-control tune-pid --setpoint 100.0
```

---

## Tuning Methods Quick Guide

| Method | Speed | Robustness | Best For |
|--------|-------|------------|----------|
| `ai_enhanced` | Medium | High | Production systems |
| `imc` | Fast | Very High | Uncertain processes |
| `cohen_coon` | Fast | Medium | Dead-time processes |
| `ziegler_nichols_open` | Very Fast | Low | Simple processes |

---

## Common Parameters

### Typical Setpoints by Industry
- **Temperature Control**: 20-100°C
- **Pressure Control**: 1-10 bar
- **Flow Control**: 10-1000 L/min
- **Level Control**: 10-90%

### Expected Tuning Results
- **Kp**: 0.1 - 10.0 (typical range)
- **Ki**: 0.01 - 1.0 (typical range)
- **Kd**: 0.0 - 0.1 (often zero or small)

---

## Troubleshooting Quick Fixes

### Environment Issues
```bash
# Install missing dependencies
pip install numpy scipy pandas scikit-learn asyncua

# Reset environment
cp config/env.example .env
ign advanced-process-control validate-env
```

### Tuning Failures
```bash
# Try conservative method
ign advanced-process-control tune-pid --method imc

# Check with smaller setpoint
ign advanced-process-control tune-pid --setpoint 25.0
```

### Integration Problems
```bash
# Check MPC Framework
ign mpc-framework status

# Reinstall if needed
pip install -e .
```

---

## Environment Variables

### Required (.env file)
```bash
MPC_CONTROLLER_ENABLED=true
APC_AUTO_TUNING_ENABLED=true
APC_MULTI_LOOP_COORDINATION=true
APC_ANALYTICS_ENABLED=true
```

### Optional Features
```bash
APC_AI_ENHANCEMENT=true
APC_REAL_TIME_OPTIMIZATION=true
APC_PERFORMANCE_MONITORING=true
```

---

## Integration with MPC Framework

### Combined Workflow
```bash
# 1. Initialize MPC
ign mpc-framework validate-env
ign mpc-framework start-controller

# 2. Tune controllers
ign advanced-process-control tune-pid --method ai_enhanced

# 3. Monitor performance
ign mpc-framework monitor-performance
ign advanced-process-control status
```

---

## CLI Help

### Get Help
```bash
# General help
ign advanced-process-control --help

# Command-specific help
ign advanced-process-control tune-pid --help
ign advanced-process-control validate-env --help
```

### Command Options
```bash
# tune-pid options
--method, -m    # Tuning method
--setpoint, -s  # Target setpoint
--verbose, -v   # Detailed output

# validate-env options
--verbose, -v   # Detailed validation

# test options
--verbose, -v   # Detailed test output
```

---

## Expected Outputs

### Successful Validation
```
✅ Advanced Process Control Environment: VALID
Overall Environment Status:
✅ READY FOR PRODUCTION
```

### Successful Tuning
```
✅ PID Tuning Completed Successfully
Kp: 3.6667
Ki: 0.4333
Kd: 0.0000
Data Points: 60
```

### Successful Testing
```
✅ All tests passed (2/2)
```

---

## Performance Benchmarks

### Typical Execution Times
- **Environment validation**: < 5 seconds
- **PID tuning**: 60-90 seconds
- **System status**: < 2 seconds
- **Comprehensive testing**: < 30 seconds

### Resource Usage
- **Memory**: < 500 MB during tuning
- **CPU**: Moderate usage during optimization
- **Storage**: < 10 MB for logs and cache

---

## Quick Diagnostics

### Check Installation
```bash
which ign
ign --version
ign advanced-process-control status
```

### Check Dependencies
```bash
python -c "import numpy, scipy, pandas, sklearn; print('Dependencies OK')"
```

### Check Integration
```bash
python -c "from src.ignition.modules.advanced_process_control import AutomatedTuningSystem; print('Module OK')"
```

---

## Emergency Commands

### Reset System
```bash
# Stop all processes
pkill -f "advanced-process-control"

# Reinstall
pip install -e .

# Validate
ign advanced-process-control validate-env
```

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
ign advanced-process-control tune-pid --verbose
```

---

**Last Updated**: December 27, 2024
**Version**: 15.0.0
**Status**: ✅ Production Ready
