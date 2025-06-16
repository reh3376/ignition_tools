# IGN Scripts Testing Environment Guide

This guide covers the comprehensive Docker-based testing environment for IGN Scripts, including setup, execution, monitoring, and optimization through log analysis.

## 🐳 Docker Testing Environment

### Overview

The testing environment provides:
- **Isolated Testing**: Clean, reproducible environment for all tests
- **Comprehensive Coverage**: Unit, integration, UI, and performance tests
- **Real-time Monitoring**: Live log analysis and performance tracking
- **Automated Reports**: Coverage reports, performance benchmarks, and optimization recommendations

### Architecture

```
IGN Scripts Testing Environment
├── Docker Containers
│   ├── ign_scripts_test     # Main testing container
│   ├── ign_scripts_dev      # Development/UI container  
│   └── ign_scripts_benchmark # Performance testing
├── Test Suites
│   ├── Unit Tests           # Component-level testing
│   ├── Integration Tests    # Cross-component testing
│   ├── UI Tests            # Streamlit interface testing
│   └── Performance Tests   # Benchmarking and profiling
└── Monitoring & Analysis
    ├── Real-time Log Monitoring
    ├── Performance Analysis
    └── Optimization Recommendations
```

## 🚀 Quick Start

### Prerequisites

- Docker installed and running
- Python 3.11+ (for local script execution)
- 4GB+ available RAM for performance tests

### Basic Test Execution

```bash
# Run the complete test suite
python3 scripts/run_tests.py --all

# Run specific test categories
python3 scripts/run_tests.py --unit          # Unit tests only
python3 scripts/run_tests.py --integration   # Integration tests only
python3 scripts/run_tests.py --ui            # UI tests only
python3 scripts/run_tests.py --performance   # Performance tests only

# Generate coverage report
python3 scripts/run_tests.py --coverage
```

### Using Docker Compose

```bash
# Run all test containers
docker-compose up

# Run specific services
docker-compose up ign-scripts-test          # Testing
docker-compose up ign-scripts-dev           # Development UI
docker-compose up ign-scripts-benchmark     # Performance testing

# View logs
docker-compose logs -f ign-scripts-test
```

## 📋 Test Categories

### Unit Tests (`tests/test_*.py`)

**Purpose**: Test individual components in isolation
**Markers**: `@pytest.mark.unit`
**Coverage**: Script generator, CLI, utilities

```bash
# Run unit tests
python3 scripts/run_tests.py --unit

# Or directly with pytest
docker run --rm -v $(pwd):/app ign-scripts-test \
  python -m pytest tests/ -v -m unit
```

**Example Test**:
```python
@pytest.mark.unit
def test_script_generation(script_generator, sample_config):
    """Test basic script generation functionality."""
    result = script_generator.generate_script(
        sample_config["template"], 
        sample_config
    )
    assert result is not None
    assert "TestButton" in result
```

### Integration Tests

**Purpose**: Test component interactions and workflows
**Markers**: `@pytest.mark.integration`
**Coverage**: CLI-to-generator integration, file I/O, template processing

```bash
# Run integration tests
python3 scripts/run_tests.py --integration
```

**Example Test**:
```python
@pytest.mark.integration
def test_cli_script_generation(runner, temp_dir):
    """Test complete CLI workflow."""
    output_file = temp_dir / "test_script.py"
    result = runner.invoke(cli, [
        'script', 'generate',
        '--template', 'vision/button_click_handler.jinja2',
        '--component-name', 'TestButton',
        '--output', str(output_file)
    ])
    assert result.exit_code == 0
    assert output_file.exists()
```

### UI Tests

**Purpose**: Test Streamlit interface functionality
**Markers**: `@pytest.mark.ui`
**Coverage**: UI components, user interactions, session state

```bash
# Run UI tests
python3 scripts/run_tests.py --ui
```

**Example Test**:
```python
@pytest.mark.ui
def test_template_selection_flow(mock_streamlit):
    """Test template selection in UI."""
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = "vision/button_click_handler.jinja2"
        # Test UI flow...
```

### Performance Tests

**Purpose**: Benchmark performance and identify bottlenecks
**Markers**: `@pytest.mark.performance`
**Coverage**: Generation speed, memory usage, concurrency

```bash
# Run performance tests
python3 scripts/run_tests.py --performance

# View benchmark results
cat test-results/benchmark.json
```

**Example Test**:
```python
@pytest.mark.performance
def test_generation_speed(script_generator, benchmark):
    """Benchmark script generation performance."""
    def generate():
        return script_generator.generate_script(template, config)
    
    result = benchmark(generate)
    assert result is not None
```

## 📊 Monitoring and Analysis

### Real-time Log Monitoring

Monitor container logs in real-time with intelligent highlighting:

```bash
# Monitor all containers
python3 scripts/monitor_logs.py --live

# Monitor specific container
python3 scripts/monitor_logs.py --live --container ign_scripts_test
```

**Log Highlighting**:
- 🔴 **Errors**: Failed tests, exceptions, critical issues
- 🟡 **Warnings**: Performance warnings, deprecations
- ⚡ **Performance**: Timing and memory metrics
- 🟢 **Success**: Passed tests, completions

### Log Analysis and Optimization

Analyze historical logs for optimization insights:

```bash
# Analyze recent logs (last hour)
python3 scripts/monitor_logs.py --analyze --since 1h

# Analyze specific container
python3 scripts/monitor_logs.py --analyze --container ign_scripts_test

# Generate detailed report
python3 scripts/monitor_logs.py --analyze --output analysis_report.json
```

**Analysis Features**:
- Error pattern detection
- Performance trend analysis  
- Memory usage tracking
- Test failure analysis
- Optimization recommendations

### Performance Metrics

Key metrics tracked:
- **Script Generation Time**: Average and peak generation times
- **Memory Usage**: Peak memory consumption during operations
- **Test Execution Time**: Time for different test categories
- **Error Rates**: Frequency and patterns of failures
- **Resource Utilization**: CPU and memory efficiency

## 🔧 Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
minversion = 7.0
addopts = 
    --strict-markers
    --cov=src
    --cov-report=html:coverage-reports/htmlcov
    --cov-fail-under=80
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests  
    performance: Performance tests
    ui: UI tests
    slow: Slow tests
```

### Docker Configuration

**Main Testing Container** (`Dockerfile`):
- Python 3.11 slim base image
- All dependencies pre-installed
- Non-root user for security
- Optimized for testing workloads

**Docker Compose Services**:
- `ign-scripts-test`: Main testing container
- `ign-scripts-dev`: Development UI container (port 8502)
- `ign-scripts-benchmark`: Performance testing container

### Environment Variables

- `PYTHONPATH=/app`: Ensure proper module imports
- `PYTHONUNBUFFERED=1`: Real-time log output
- `LOG_LEVEL=DEBUG`: Detailed logging for analysis
- `TESTING_MODE=true`: Enable testing-specific behavior

## 📈 Reports and Coverage

### Coverage Reports

Generated automatically with each test run:

```bash
# Generate coverage report
python3 scripts/run_tests.py --coverage

# View HTML report
open coverage-reports/index.html

# View XML report (for CI/CD)
cat coverage-reports/coverage.xml
```

**Coverage Targets**:
- **Minimum Coverage**: 80%
- **Target Coverage**: 90%+
- **Critical Paths**: 100% (script generation, CLI core)

### Test Reports

HTML test reports with detailed results:

```bash
# View test report
open test-results/report.html
```

**Report Includes**:
- Test execution summary
- Failed test details with stack traces
- Performance benchmarks
- Coverage metrics
- Historical trends

### Benchmark Reports

Performance benchmark data in JSON format:

```json
{
  "benchmarks": [
    {
      "name": "test_script_generation_speed",
      "min": 0.001234,
      "max": 0.005678,
      "mean": 0.002456,
      "stats": {...}
    }
  ]
}
```

## 🐛 Troubleshooting

### Common Issues

#### Docker Build Failures

```bash
# Clean Docker cache
docker system prune -f

# Rebuild without cache
docker build --no-cache -t ign-scripts-test .
```

#### Permission Issues

```bash
# Fix file permissions
sudo chown -R $(whoami):$(whoami) test-results coverage-reports logs
```

#### Memory Issues

```bash
# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory > 4GB+

# Monitor memory usage
docker stats ign_scripts_test
```

#### Import Errors

```bash
# Verify Python path
docker run --rm ign-scripts-test python -c "import sys; print(sys.path)"

# Check module imports
docker run --rm ign-scripts-test python -c "from src.ignition.generators.script_generator import IgnitionScriptGenerator; print('OK')"
```

### Debugging Tests

```bash
# Run tests with verbose output
python3 scripts/run_tests.py --unit --verbose

# Drop into container for debugging
docker run -it --rm -v $(pwd):/app ign-scripts-test bash

# Run specific test with debugging
docker run --rm -v $(pwd):/app ign-scripts-test \
  python -m pytest tests/test_script_generator.py::TestIgnitionScriptGenerator::test_generate_script_with_navigation -v -s
```

### Log Analysis Issues

```bash
# Check container logs directly
docker logs ign_scripts_test

# Monitor resource usage
docker stats --no-stream

# Check disk space
df -h
```

## 🔄 Optimization Workflows

### Performance Optimization Cycle

1. **Baseline Measurement**
   ```bash
   python3 scripts/run_tests.py --performance
   ```

2. **Code Changes**
   - Implement optimizations
   - Update tests as needed

3. **Performance Validation**
   ```bash
   python3 scripts/run_tests.py --performance
   python3 scripts/monitor_logs.py --analyze --since 1h
   ```

4. **Compare Results**
   - Review benchmark reports
   - Check optimization recommendations
   - Validate memory usage trends

### Continuous Monitoring

```bash
# Set up continuous monitoring
while true; do
  python3 scripts/monitor_logs.py --analyze --report-only --output "test-results/hourly_$(date +%Y%m%d_%H).json"
  sleep 3600  # Run every hour
done
```

### Quality Gates

Before code commits:
1. All unit tests pass
2. Integration tests pass  
3. Coverage ≥ 80%
4. No performance regressions
5. No new security issues

```bash
# Pre-commit check
python3 scripts/run_tests.py --all && echo "✅ Ready to commit"
```

## 📚 Best Practices

### Test Development

1. **Write Tests First**: Use TDD approach for new features
2. **Test Isolation**: Each test should be independent
3. **Clear Naming**: Test names should describe the scenario
4. **Arrange-Act-Assert**: Structure tests clearly
5. **Mock External Dependencies**: Use fixtures for external services

### Performance Testing

1. **Establish Baselines**: Record initial performance metrics
2. **Test Realistic Scenarios**: Use representative data sizes
3. **Monitor Trends**: Track performance over time
4. **Profile Bottlenecks**: Use detailed profiling for optimization
5. **Document Changes**: Record impact of optimizations

### Monitoring

1. **Regular Analysis**: Run log analysis daily
2. **Act on Recommendations**: Implement suggested optimizations
3. **Track Metrics**: Monitor key performance indicators
4. **Alert on Anomalies**: Set up notifications for issues
5. **Document Findings**: Record optimization discoveries

---

This testing environment provides comprehensive validation and optimization capabilities for IGN Scripts. The combination of Docker isolation, comprehensive test coverage, and intelligent log analysis ensures high code quality and optimal performance. 