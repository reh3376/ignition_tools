# IGN Scripts - Docker Testing Environment

Quick reference guide for the comprehensive Docker-based testing environment.

## 🚀 Quick Start

```bash
# Run all tests with optimization analysis
python3 scripts/run_tests.py --all

# Monitor container logs in real-time
python3 scripts/monitor_logs.py --live
```

## 🐳 Docker Services

| Service | Purpose | Port | Command |
|---------|---------|------|---------|
| `ign-scripts-test` | Main testing container | - | `docker-compose up ign-scripts-test` |
| `ign-scripts-dev` | Development UI | 8502 | `docker-compose up ign-scripts-dev` |
| `ign-scripts-benchmark` | Performance testing | - | `docker-compose up ign-scripts-benchmark` |

## 🧪 Test Categories

| Type | Command | Purpose |
|------|---------|---------|
| **Unit** | `python3 scripts/run_tests.py --unit` | Component-level testing |
| **Integration** | `python3 scripts/run_tests.py --integration` | Workflow testing |
| **UI** | `python3 scripts/run_tests.py --ui` | Streamlit interface testing |
| **Performance** | `python3 scripts/run_tests.py --performance` | Benchmarking & profiling |

## 📊 Monitoring & Analysis

### Real-time Monitoring
```bash
# Monitor all containers with color-coded logs
python3 scripts/monitor_logs.py --live

# Monitor specific container
python3 scripts/monitor_logs.py --live --container ign_scripts_test
```

### Performance Analysis
```bash
# Analyze recent logs and get optimization recommendations
python3 scripts/monitor_logs.py --analyze --since 1h

# Generate detailed report
python3 scripts/monitor_logs.py --analyze --output analysis_report.json
```

## 📈 Reports & Coverage

### Generated Reports
- **Coverage**: `coverage-reports/index.html` (80%+ target)
- **Test Results**: `test-results/report.html`
- **Benchmarks**: `test-results/benchmark.json`
- **Log Analysis**: `test-results/log_analysis_*.json`

### Quick Commands
```bash
# Generate coverage report
python3 scripts/run_tests.py --coverage

# View reports
open coverage-reports/index.html
open test-results/report.html
```

## 🔧 Development Workflow

### 1. Pre-commit Testing
```bash
python3 scripts/run_tests.py --all && echo "✅ Ready to commit"
```

### 2. Performance Optimization Cycle
```bash
# Baseline measurement
python3 scripts/run_tests.py --performance

# After code changes
python3 scripts/run_tests.py --performance
python3 scripts/monitor_logs.py --analyze --since 1h
```

### 3. Debugging
```bash
# Drop into container for debugging
docker run -it --rm -v $(pwd):/app ign-scripts-test bash

# Run specific test with debugging
docker run --rm -v $(pwd):/app ign-scripts-test \
  python -m pytest tests/test_script_generator.py::TestIgnitionScriptGenerator::test_generate_script_with_navigation -v -s
```

## 🎯 Key Features

- **🔴 Error Detection**: Automatic error pattern recognition
- **⚡ Performance Tracking**: Real-time speed and memory monitoring
- **🟡 Warning Analysis**: Performance warnings and deprecation notices
- **🟢 Success Validation**: Test completion and success tracking
- **📊 Trend Analysis**: Historical performance and quality metrics
- **🔍 Optimization Recommendations**: AI-driven improvement suggestions

## 🚨 Common Issues & Solutions

### Docker Build Failures
```bash
docker system prune -f
docker build --no-cache -t ign-scripts-test .
```

### Permission Issues
```bash
sudo chown -R $(whoami):$(whoami) test-results coverage-reports logs
```

### Memory Issues
```bash
# Increase Docker memory limit (Docker Desktop: Settings > Resources > Memory > 4GB+)
docker stats ign_scripts_test
```

### Import Errors
```bash
# Verify Python path and imports
docker run --rm ign-scripts-test python -c "from src.ignition.generators.script_generator import IgnitionScriptGenerator; print('✅ OK')"
```

## 📚 Documentation

- **Comprehensive Guide**: [docs/testing_guide.md](docs/testing_guide.md)
- **UI Documentation**: [docs/streamlit_ui_guide.md](docs/streamlit_ui_guide.md)
- **Main README**: [README.md](README.md)

## 🏗️ Architecture

```
Testing Environment
├── Docker Containers
│   ├── ign_scripts_test     # Main testing
│   ├── ign_scripts_dev      # Development UI
│   └── ign_scripts_benchmark # Performance
├── Test Suites
│   ├── Unit Tests           # tests/test_*.py
│   ├── Integration Tests    # CLI workflows
│   ├── UI Tests            # Streamlit mocking
│   └── Performance Tests   # Benchmarking
├── Automation Scripts
│   ├── run_tests.py        # Test execution
│   └── monitor_logs.py     # Log analysis
└── Reports & Analysis
    ├── Coverage Reports    # HTML + XML
    ├── Performance Data    # JSON benchmarks
    └── Log Analysis       # Optimization insights
```

## 🎯 Quality Gates

Before merging code:
- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ Coverage ≥ 80%
- ✅ No performance regressions
- ✅ No new security issues
- ✅ UI tests pass

---

**Quick Help**: Run `python3 scripts/run_tests.py --help` or `python3 scripts/monitor_logs.py --help` for detailed options.
