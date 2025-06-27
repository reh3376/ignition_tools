# Advanced Process Control - Troubleshooting Guide 🔧

**Phase 15: Advanced Process Control Suite**
**Version**: 15.0.0
**Status**: ✅ Production Ready
**Methodology**: crawl_mcp.py systematic approach

---

## Table of Contents

1. [Common Issues](#common-issues)
2. [Environment Problems](#environment-problems)
3. [Tuning Failures](#tuning-failures)
4. [Integration Issues](#integration-issues)
5. [Performance Problems](#performance-problems)
6. [Debug Procedures](#debug-procedures)
7. [Recovery Steps](#recovery-steps)

---

## Common Issues

### Issue: Command Not Found
**Symptoms**: `ign: command not found` or `advanced-process-control: command not found`
**Root Cause**: CLI not properly installed or registered
**Solution**:
```bash
# Check if IGN Scripts is properly installed
which ign

# If not found, activate virtual environment
source .venv312/bin/activate

# Verify CLI registration
ign --help | grep advanced-process-control

# If missing, reinstall
pip install -e .
```

### Issue: Module Import Errors
**Symptoms**: `ModuleNotFoundError: No module named 'src.ignition.modules.advanced_process_control'`
**Root Cause**: Python path or module structure issues
**Solution**:
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Verify module structure
ls -la src/ignition/modules/advanced_process_control/

# Reinstall in development mode
pip install -e .
```

---

## Environment Problems

### Issue: Environment Validation Fails
**Symptoms**: `❌ Environment validation failed`
**Diagnostic Steps**:
```bash
# Run detailed validation
ign advanced-process-control validate-env --verbose

# Check specific dependencies
python -c "import numpy; print('numpy OK')"
python -c "import scipy; print('scipy OK')"
python -c "import pandas; print('pandas OK')"
python -c "import sklearn; print('sklearn OK')"
```

**Solutions**:
```bash
# Install missing dependencies
pip install numpy>=1.21.0 scipy>=1.7.0 pandas>=1.3.0 scikit-learn>=1.0.0

# For asyncua issues
pip install asyncua>=1.0.0

# Update all dependencies
pip install --upgrade -r requirements.txt
```

### Issue: MPC Framework Integration Missing
**Symptoms**: `❌ MPC Framework missing`
**Root Cause**: Phase 14 not properly installed
**Solution**:
```bash
# Check Phase 14 status
ign mpc-framework status

# If not available, install Phase 14 first
# See MPC Framework documentation

# Verify integration
python -c "from src.ignition.modules.mpc_framework import mpc_controller; print('MPC OK')"
```

### Issue: Environment Variables Not Set
**Symptoms**: Configuration warnings during validation
**Solution**:
```bash
# Check .env file exists
ls -la .env

# Copy from example if missing
cp config/env.example .env

# Edit with required values
vim .env

# Verify loading
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('MPC_CONTROLLER_ENABLED'))"
```

---

## Tuning Failures

### Issue: Insufficient Process Data
**Symptoms**: `Insufficient process data for tuning (minimum 10 points required)`
**Root Cause**: Data collection problems
**Diagnostic Steps**:
```bash
# Check if process is responsive
# Verify OPC-UA connections if using real data
# Check simulation parameters
```

**Solutions**:
```bash
# Use longer data collection period
# Ensure process is running and stable
# Check for communication issues
# Verify step input is properly applied
```

### Issue: Invalid PID Parameters
**Symptoms**: `Invalid PID parameters (negative values)`
**Root Cause**: Poor process data or inappropriate method
**Solutions**:
```bash
# Try different tuning method
ign advanced-process-control tune-pid --method imc

# Check process stability
# Verify setpoint is reasonable
# Use conservative method first

# For unstable processes, try IMC
ign advanced-process-control tune-pid --method imc --setpoint 50.0
```

### Issue: Tuning Takes Too Long
**Symptoms**: Tuning process hangs or takes excessive time
**Root Cause**: Data collection or algorithm issues
**Solutions**:
```bash
# Cancel with Ctrl+C
# Check system resources
top

# Try simpler method
ign advanced-process-control tune-pid --method ziegler_nichols_open

# Check for deadlocks in logs
tail -f logs/advanced_process_control.log
```

---

## Integration Issues

### Issue: CLI Commands Not Registered
**Symptoms**: `No such command 'advanced-process-control'`
**Root Cause**: Module not properly registered in enhanced_cli.py
**Solution**:
```bash
# Check enhanced_cli.py registration
grep -n "advanced_process_control" src/core/enhanced_cli.py

# Verify import path
python -c "from src.ignition.modules.advanced_process_control.cli_commands import apc_cli; print('Import OK')"

# Reinstall if needed
pip install -e .
```

### Issue: Rich Console Formatting Issues
**Symptoms**: Broken console output or formatting errors
**Solution**:
```bash
# Check rich installation
pip show rich

# Update if needed
pip install --upgrade rich

# Test console
python -c "from rich.console import Console; Console().print('Test', style='bold green')"
```

---

## Performance Problems

### Issue: Slow Tuning Performance
**Symptoms**: Tuning takes much longer than expected
**Diagnostic Steps**:
```bash
# Check system resources
top
free -h

# Monitor during tuning
ign advanced-process-control tune-pid --verbose &
top -p $!
```

**Solutions**:
```bash
# Close unnecessary applications
# Use faster tuning method
ign advanced-process-control tune-pid --method ziegler_nichols_open

# Check for memory issues
# Restart Python environment if needed
```

### Issue: High Memory Usage
**Symptoms**: System becomes slow during tuning
**Solutions**:
```bash
# Monitor memory usage
watch -n 1 'free -h'

# Use smaller data collection periods
# Check for memory leaks in logs
# Restart if necessary
```

---

## Debug Procedures

### Enable Debug Logging
```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Run with verbose output
ign advanced-process-control tune-pid --verbose

# Check logs
tail -f logs/advanced_process_control.log
```

### Systematic Debugging Steps

#### Step 1: Environment Validation
```bash
# Always start here
ign advanced-process-control validate-env --verbose
```

#### Step 2: Component Testing
```bash
# Test each component
ign advanced-process-control test --verbose
```

#### Step 3: Isolation Testing
```bash
# Test individual methods
ign advanced-process-control tune-pid --method imc --verbose
ign advanced-process-control tune-pid --method ai_enhanced --verbose
```

#### Step 4: Integration Testing
```bash
# Test with MPC Framework
ign mpc-framework status
ign advanced-process-control status
```

### Log Analysis

#### Common Log Patterns
```bash
# Error patterns
grep "ERROR" logs/advanced_process_control.log

# Warning patterns
grep "WARNING" logs/advanced_process_control.log

# Performance issues
grep "slow\|timeout\|hang" logs/advanced_process_control.log
```

#### Log Locations
- **Main logs**: `logs/advanced_process_control.log`
- **System logs**: `/var/log/ignition/` (if applicable)
- **Python logs**: Check console output

---

## Recovery Steps

### Complete System Reset
```bash
# Stop all processes
pkill -f "advanced-process-control"

# Clear temporary files
rm -rf /tmp/apc_*

# Reset environment
source .venv312/bin/activate

# Reinstall
pip install -e .

# Validate
ign advanced-process-control validate-env
```

### Dependency Recovery
```bash
# Backup current environment
pip freeze > requirements_backup.txt

# Reinstall clean
pip uninstall -y numpy scipy pandas scikit-learn
pip install numpy>=1.21.0 scipy>=1.7.0 pandas>=1.3.0 scikit-learn>=1.0.0

# Test
ign advanced-process-control validate-env
```

### Configuration Recovery
```bash
# Backup current config
cp .env .env.backup

# Reset to defaults
cp config/env.example .env

# Edit required values
vim .env

# Test
ign advanced-process-control validate-env
```

---

## Emergency Procedures

### System Unresponsive
```bash
# Force kill processes
sudo pkill -9 -f "advanced-process-control"

# Check system resources
df -h
free -h

# Restart if necessary
sudo reboot
```

### Data Corruption
```bash
# Check file integrity
ls -la src/ignition/modules/advanced_process_control/

# Restore from git if needed
git status
git checkout -- src/ignition/modules/advanced_process_control/

# Reinstall
pip install -e .
```

---

## Getting Help

### Self-Diagnosis Checklist
- [ ] Environment validation passes
- [ ] All dependencies installed
- [ ] MPC Framework integration working
- [ ] Configuration files present
- [ ] No error messages in logs
- [ ] System resources adequate

### Support Resources
- **Documentation**: See [Advanced Process Control Guide](advanced-process-control-guide.md)
- **Logs**: Check `logs/advanced_process_control.log`
- **GitHub Issues**: Report bugs and get community help
- **CLI Help**: `ign advanced-process-control --help`

### Information to Provide When Seeking Help
1. **Environment details**: OS, Python version, dependency versions
2. **Error messages**: Complete error output
3. **Steps to reproduce**: Exact commands and sequence
4. **Log files**: Relevant log excerpts
5. **Configuration**: Environment variables and settings (redact sensitive info)

---

**Last Updated**: December 27, 2024
**Version**: 15.0.0
**Status**: ✅ Production Ready
