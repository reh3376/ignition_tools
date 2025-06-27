# Advanced Process Control - Troubleshooting Guide 🔧

**Phase 15: Advanced Process Control Suite**
**Version**: 15.0.0
**Status**: ✅ Production Ready
**Methodology**: crawl_mcp.py systematic approach

---

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [Common Issues](#common-issues)
3. [Environment Problems](#environment-problems)
4. [Tuning Failures](#tuning-failures)
5. [Integration Problems](#integration-problems)
6. [Performance Issues](#performance-issues)
7. [Debug Procedures](#debug-procedures)
8. [Recovery Procedures](#recovery-procedures)

---

## Quick Diagnosis

### System Health Check
```bash
# Step 1: Quick status check
ign advanced-process-control status

# Step 2: Environment validation
ign advanced-process-control validate-env --verbose

# Step 3: Comprehensive testing
ign advanced-process-control test --verbose
```

### Expected vs. Actual Outputs

#### ✅ Healthy System
```
📊 Advanced Process Control System Status
✅ System Status: ACTIVE
✅ Environment: VALID
```

#### ❌ Problem Indicators
```
❌ Advanced Process Control Environment: INVALID
❌ System Error: Missing dependency: numpy
❌ PID Tuning Failed: Insufficient process data
```

---

## Common Issues

### 1. Command Not Found

#### Problem
```bash
$ ign advanced-process-control status
Error: No such command 'advanced-process-control'
```

#### Root Cause
- Phase 15 module not properly installed
- CLI registration failed
- Import errors in module initialization

#### Solution
```bash
# Check module availability
python -c "from src.ignition.modules.advanced_process_control import apc_cli; print('✅ Module available')"

# Reinstall IGN Scripts
pip install -e .

# Verify CLI registration
ign --help | grep advanced-process-control
```

#### Prevention
- Always run `pip install -e .` after code updates
- Check for import errors in module files
- Verify environment activation

### 2. Module Import Errors

#### Problem
```bash
ImportError: No module named 'numpy'
ModuleNotFoundError: No module named 'scipy'
```

#### Root Cause
- Missing scientific computing dependencies
- Virtual environment not activated
- Incorrect Python environment

#### Solution
```bash
# Install all required dependencies
pip install numpy>=1.21.0 scipy>=1.7.0 pandas>=1.3.0 scikit-learn>=1.0.0 asyncua>=1.0.0

# Verify installation
python -c "import numpy, scipy, pandas, sklearn; print('✅ All dependencies available')"

# Check Python environment
which python
pip list | grep -E "numpy|scipy|pandas|scikit-learn|asyncua"
```

#### Prevention
- Use `requirements.txt` for dependency management
- Always activate virtual environment
- Document dependency versions

### 3. Environment Validation Failures

#### Problem
```bash
❌ Advanced Process Control Environment: INVALID
Error: Environment validation failed: ['Missing dependency: numpy']
```

#### Root Cause Analysis
Following crawl_mcp.py Step 1 (Environment Validation First):

1. **Dependency Issues**: Missing or incompatible versions
2. **Configuration Problems**: Invalid environment variables
3. **Resource Constraints**: Insufficient memory or disk space
4. **Permission Issues**: File access restrictions

#### Systematic Solution
```bash
# Step 1: Check dependencies
ign advanced-process-control validate-env --verbose

# Step 2: Install missing dependencies
pip install -r requirements.txt

# Step 3: Verify environment variables
cat .env | grep -E "MPC|APC"

# Step 4: Check system resources
df -h  # Disk space
free -h  # Memory
```

---

## Environment Problems

### 1. Missing Dependencies

#### Diagnosis
```bash
# Check specific dependencies
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import scipy; print(f'SciPy: {scipy.__version__}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
python -c "import sklearn; print(f'Scikit-learn: {sklearn.__version__}')"
```

#### Resolution
```bash
# Install with specific versions
pip install numpy>=1.21.0
pip install scipy>=1.7.0
pip install pandas>=1.3.0
pip install scikit-learn>=1.0.0
pip install asyncua>=1.0.0

# Verify installation
ign advanced-process-control validate-env
```

### 2. MPC Framework Integration Issues

#### Problem
```bash
⚠️ MPC Framework integration unavailable: No module named 'mpc_framework'
```

#### Root Cause
- Phase 14 (MPC Framework) not installed
- Import path issues
- Module initialization failures

#### Solution
```bash
# Check Phase 14 availability
ign mpc-framework status

# Verify MPC Framework installation
python -c "from src.ignition.modules.mpc_framework import mpc_controller; print('✅ MPC Framework available')"

# Check environment variables
grep MPC .env
```

#### Workaround
Phase 15 can operate in PID-only mode without MPC Framework:
```bash
# Disable MPC integration
export MPC_CONTROLLER_ENABLED=false

# Test PID-only functionality
ign advanced-process-control tune-pid --method ai_enhanced
```

### 3. Environment Variables

#### Problem
```bash
⚠️ Not set (using defaults)
```

#### Required Variables
```bash
# Core configuration
MPC_CONTROLLER_ENABLED=true
APC_AUTO_TUNING_ENABLED=true
APC_MULTI_LOOP_COORDINATION=true
APC_ANALYTICS_ENABLED=true

# Optional features
APC_AI_ENHANCEMENT=true
APC_REAL_TIME_OPTIMIZATION=true
APC_PERFORMANCE_MONITORING=true
```

#### Setup
```bash
# Copy example configuration
cp config/env.example .env

# Edit configuration
nano .env

# Verify configuration
ign advanced-process-control validate-env --verbose
```

---

## Tuning Failures

### 1. Insufficient Process Data

#### Problem
```bash
❌ PID Tuning Failed: Insufficient process data for tuning (minimum 10 points required)
```

#### Root Cause
- Data collection timeout
- Process communication failures
- Simulation errors

#### Solution
```bash
# Try with different method
ign advanced-process-control tune-pid --method imc --verbose

# Check with smaller setpoint
ign advanced-process-control tune-pid --setpoint 25.0

# Verify system initialization
ign advanced-process-control validate-env
```

#### Debug
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export APC_DEBUG_MODE=true

# Run with verbose output
ign advanced-process-control tune-pid --verbose
```

### 2. Invalid Parameters

#### Problem
```bash
❌ Invalid parameter: Setpoint must be between 0 and 1000
❌ Invalid PID parameters (negative values)
```

#### Root Cause Analysis
Following crawl_mcp.py Step 2 (Input Validation):

1. **Input Validation**: Setpoint outside valid range
2. **Algorithm Failure**: Tuning method produced invalid results
3. **Process Characteristics**: Unusual process behavior

#### Solution
```bash
# Use valid setpoint range
ign advanced-process-control tune-pid --setpoint 50.0

# Try conservative method
ign advanced-process-control tune-pid --method imc

# Check process simulation
ign advanced-process-control test --verbose
```

### 3. Tuning Method Failures

#### Problem
```bash
❌ Method ziegler_nichols_open not implemented, using AI-enhanced
```

#### Available Methods
```bash
# Verified working methods
ign advanced-process-control tune-pid --method ai_enhanced     # Recommended
ign advanced-process-control tune-pid --method imc            # Conservative
ign advanced-process-control tune-pid --method cohen_coon     # Dead-time processes
ign advanced-process-control tune-pid --method ziegler_nichols_open  # Simple processes
```

#### Fallback Strategy
```bash
# Start with most robust method
ign advanced-process-control tune-pid --method imc

# Progress to AI-enhanced for production
ign advanced-process-control tune-pid --method ai_enhanced
```

---

## Integration Problems

### 1. CLI Registration Failures

#### Problem
```bash
Error: No such command 'advanced-process-control'
```

#### Diagnosis
```bash
# Check CLI registration
python -c "
from src.ignition.modules.advanced_process_control.cli_commands import apc_cli
print('✅ CLI module imports successfully')
"

# Verify main CLI integration
grep -r "apc_cli" src/main.py
```

#### Solution
```bash
# Reinstall with CLI registration
pip install -e .

# Check enhanced CLI
python -c "
from src.ignition.enhanced_cli import main
print('✅ Enhanced CLI available')
"
```

### 2. Console Formatting Issues

#### Problem
```bash
# Broken formatting or missing colors
Advanced Process Control Suite
Phase 15: Automated Tuning & Multi-Loop Coordination
```

#### Root Cause
- Missing Rich library
- Terminal compatibility issues
- Console encoding problems

#### Solution
```bash
# Install Rich for console formatting
pip install rich

# Test console output
python -c "from rich.console import Console; Console().print('✅ Rich working')"

# Check terminal compatibility
echo $TERM
```

### 3. Resource Conflicts

#### Problem
```bash
❌ Resource allocation failed
❌ Async context manager error
```

#### Root Cause Analysis
Following crawl_mcp.py Step 6 (Resource Management):

1. **Memory Constraints**: Insufficient system memory
2. **Async Issues**: Event loop conflicts
3. **Resource Leaks**: Improper cleanup

#### Solution
```bash
# Check system resources
free -h
ps aux | grep python

# Restart with clean environment
pkill -f advanced-process-control
ign advanced-process-control status
```

---

## Performance Issues

### 1. Slow Tuning Performance

#### Problem
Tuning takes longer than expected (>2 minutes)

#### Diagnosis
```bash
# Time the tuning process
time ign advanced-process-control tune-pid --method ai_enhanced

# Check system load
top
htop
```

#### Optimization
```bash
# Use faster method for testing
ign advanced-process-control tune-pid --method imc

# Reduce data collection time (if configurable)
export APC_DATA_COLLECTION_TIME=30

# Check for resource conflicts
lsof | grep python
```

### 2. High Memory Usage

#### Problem
```bash
# Memory usage continuously increasing
# System becomes unresponsive
```

#### Diagnosis
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep advanced-process-control'

# Check for memory leaks
valgrind python -m src.main advanced-process-control status
```

#### Solution
```bash
# Restart system components
ign advanced-process-control test

# Check for proper cleanup
python -c "
import gc
gc.collect()
print('✅ Garbage collection completed')
"
```

### 3. System Constraints

#### Problem
```bash
❌ System resource constraints detected
```

#### Requirements
- **Memory**: Minimum 2GB RAM
- **CPU**: 2+ cores recommended
- **Disk**: 1GB free space
- **Python**: 3.12+ with scientific libraries

#### Solution
```bash
# Check system specifications
free -h
nproc
df -h
python --version
```

---

## Debug Procedures

### 1. Enable Debug Logging

#### Configuration
```bash
# Add to .env file
LOG_LEVEL=DEBUG
APC_DEBUG_MODE=true
APC_VERBOSE_LOGGING=true

# Verify logging configuration
ign advanced-process-control validate-env --verbose
```

#### Log Analysis
```bash
# Check log files
tail -f logs/ign_scripts.log

# Filter for APC messages
grep -i "advanced.*process.*control" logs/*.log

# Monitor real-time logging
ign advanced-process-control tune-pid --verbose 2>&1 | tee debug.log
```

### 2. Step-by-Step Diagnosis

#### Following crawl_mcp.py Methodology

**Step 1: Environment Validation**
```bash
ign advanced-process-control validate-env --verbose
```

**Step 2: Input Validation**
```bash
# Test with known good parameters
ign advanced-process-control tune-pid --method imc --setpoint 50.0
```

**Step 3: Error Handling**
```bash
# Test error conditions
ign advanced-process-control tune-pid --setpoint -10  # Should fail gracefully
```

**Step 4: Modular Testing**
```bash
# Test individual components
ign advanced-process-control test --verbose
```

**Step 5: Progressive Complexity**
```bash
# Start simple, add complexity
ign advanced-process-control status
ign advanced-process-control tune-pid --method imc
ign advanced-process-control tune-pid --method ai_enhanced
```

**Step 6: Resource Management**
```bash
# Verify proper cleanup
ps aux | grep advanced-process-control  # Should be minimal
```

### 3. Component Isolation

#### Test Individual Components
```bash
# Test environment validation only
python -c "
from src.ignition.modules.advanced_process_control import validate_environment
result = validate_environment()
print(f'Environment: {result}')
"

# Test tuning system initialization
python -c "
import asyncio
from src.ignition.modules.advanced_process_control.automated_tuning_system import AutomatedTuningSystem

async def test():
    system = AutomatedTuningSystem()
    result = await system.initialize()
    print(f'Initialization: {result}')

asyncio.run(test())
"
```

---

## Recovery Procedures

### 1. Soft Reset

#### Procedure
```bash
# Clear temporary files
rm -rf /tmp/ign_scripts_*

# Reset environment
source .venv/bin/activate

# Validate configuration
ign advanced-process-control validate-env --verbose
```

### 2. Hard Reset

#### Complete System Reset
```bash
# Stop all processes
pkill -f advanced-process-control

# Clear cache and logs
rm -rf cache/ logs/

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Rebuild installation
pip install -e . --force-reinstall

# Verify functionality
ign advanced-process-control test --verbose
```

### 3. Emergency Procedures

#### System Unresponsive
```bash
# Force kill processes
sudo pkill -9 -f advanced-process-control

# Check system resources
free -h
df -h

# Restart with minimal configuration
export MPC_CONTROLLER_ENABLED=false
export APC_AI_ENHANCEMENT=false
ign advanced-process-control status
```

#### Data Recovery
```bash
# Backup current configuration
cp .env .env.backup
cp -r logs/ logs.backup/

# Restore from known good state
cp config/env.example .env
ign advanced-process-control validate-env
```

---

## Prevention Strategies

### 1. Regular Health Checks
```bash
# Daily health check script
#!/bin/bash
echo "🔍 APC Health Check - $(date)"
ign advanced-process-control status
ign advanced-process-control validate-env
echo "✅ Health check completed"
```

### 2. Monitoring Setup
```bash
# Monitor system resources
watch -n 60 'ign advanced-process-control status'

# Log rotation
logrotate /etc/logrotate.d/ign_scripts
```

### 3. Backup Procedures
```bash
# Configuration backup
tar -czf apc_config_$(date +%Y%m%d).tar.gz .env config/ logs/

# System state backup
ign advanced-process-control test --verbose > system_state_$(date +%Y%m%d).log
```

---

## Contact and Support

### Debug Information Collection
When reporting issues, include:

```bash
# System information
uname -a
python --version
pip list | grep -E "numpy|scipy|pandas|scikit-learn|asyncua|rich"

# IGN Scripts version
ign --version

# Environment validation
ign advanced-process-control validate-env --verbose

# Test results
ign advanced-process-control test --verbose
```

### Common Resolution Times
- **Environment Issues**: 5-15 minutes
- **Dependency Problems**: 10-30 minutes
- **Integration Issues**: 15-45 minutes
- **Performance Problems**: 30-60 minutes

---

**Last Updated**: December 27, 2024
**Version**: 15.0.0
**Status**: ✅ Production Ready
**Methodology**: crawl_mcp.py systematic approach
