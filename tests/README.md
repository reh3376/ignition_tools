# IGN Scripts Test Suite

Comprehensive test suite for IGN Scripts with Docker-based isolation and performance monitoring.

## 📁 Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_script_generator.py # Script generation functionality tests
├── test_cli.py              # Command-line interface tests
├── test_ui.py               # Streamlit UI tests
└── test_performance.py      # Performance and benchmark tests
```

## 🧪 Test Categories

### Unit Tests (`@pytest.mark.unit`)
**Files**: `test_script_generator.py`, `test_cli.py`
**Purpose**: Test individual components in isolation
**Coverage**: Core functionality, error handling, edge cases

**Example Test**:
```python
@pytest.mark.unit
def test_script_generation(script_generator, sample_config):
    result = script_generator.generate_script(
        sample_config["template"],
        sample_config
    )
    assert result is not None
    assert "TestButton" in result
```

### Integration Tests (`@pytest.mark.integration`)
**Files**: `test_cli.py`, `test_script_generator.py`
**Purpose**: Test component interactions and complete workflows
**Coverage**: CLI-to-generator integration, file I/O, template processing

**Example Test**:
```python
@pytest.mark.integration
def test_cli_script_generation(runner, temp_dir):
    result = runner.invoke(cli, [
        'script', 'generate',
        '--template', 'vision/button_click_handler.jinja2',
        '--component-name', 'TestButton',
        '--output', str(output_file)
    ])
    assert result.exit_code == 0
    assert output_file.exists()
```

### UI Tests (`@pytest.mark.ui`)
**Files**: `test_ui.py`
**Purpose**: Test Streamlit interface functionality
**Coverage**: UI components, user interactions, session state

**Example Test**:
```python
@pytest.mark.ui
def test_template_selection_flow(mock_streamlit):
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = "vision/button_click_handler.jinja2"
        # Test UI flow...
```

### Performance Tests (`@pytest.mark.performance`)
**Files**: `test_performance.py`
**Purpose**: Benchmark performance and identify bottlenecks
**Coverage**: Generation speed, memory usage, concurrency, stress testing

**Example Test**:
```python
@pytest.mark.performance
def test_generation_speed(script_generator, benchmark):
    def generate():
        return script_generator.generate_script(template, config)

    result = benchmark(generate)
    assert result is not None
```

## 🔧 Fixtures Overview

### Core Fixtures (`conftest.py`)

| Fixture | Purpose | Scope |
|---------|---------|-------|
| `script_generator` | Configured IgnitionScriptGenerator | Function |
| `sample_button_config` | Test button configuration | Function |
| `temp_dir` | Temporary directory for test files | Function |
| `mock_ignition_system` | Mock Ignition system functions | Function |
| `captured_logs` | Capture and analyze log messages | Function |
| `performance_monitor` | Monitor timing and memory usage | Function |
| `mock_streamlit` | Mock Streamlit components for UI tests | Function |

### Configuration Fixtures

| Fixture | Purpose | Configuration Type |
|---------|---------|-------------------|
| `sample_button_config` | Navigation button | Navigation action |
| `sample_tag_write_config` | Tag write button | Tag write action |
| `sample_custom_config` | Custom code button | Custom action |

## 🚀 Running Tests

### Quick Commands
```bash
# Run all tests
python3 scripts/run_tests.py --all

# Run specific categories
python3 scripts/run_tests.py --unit
python3 scripts/run_tests.py --integration
python3 scripts/run_tests.py --ui
python3 scripts/run_tests.py --performance

# Run with coverage
python3 scripts/run_tests.py --coverage
```

### Direct pytest Commands
```bash
# Run unit tests only
pytest -m unit -v

# Run specific test file
pytest tests/test_script_generator.py -v

# Run specific test method
pytest tests/test_script_generator.py::TestIgnitionScriptGenerator::test_generate_script_with_navigation -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Docker Commands
```bash
# Run tests in Docker container
docker run --rm -v $(pwd):/app ign-scripts-test python -m pytest tests/ -v

# Run specific test category in Docker
docker run --rm -v $(pwd):/app ign-scripts-test python -m pytest tests/ -v -m unit

# Interactive debugging in container
docker run -it --rm -v $(pwd):/app ign-scripts-test bash
```

## 📊 Test Metrics & Standards

### Coverage Targets
- **Overall Coverage**: 80% minimum, 90% target
- **Critical Components**: 95%+ (script generator, CLI core)
- **UI Components**: 70%+ (mocked interactions)

### Performance Standards
- **Script Generation**: < 100ms per script average
- **Template Loading**: < 50ms per template
- **Memory Usage**: < 50MB growth over 100 iterations
- **Concurrent Operations**: Support 4+ parallel generations

### Quality Gates
- All unit tests must pass
- Integration tests must pass
- Coverage ≥ 80%
- No performance regressions
- No security vulnerabilities
- Code quality checks pass

## 🎯 Test Data & Examples

### Sample Configurations
Located in fixture definitions and `examples/` directory:
- `button_config_example.json`: Complete button configuration
- Sample navigation, tag write, popup, and custom configurations
- Mock Ignition system responses
- Performance test datasets

### Mock Objects
- **Ignition System**: Complete mock of `system.*` functions
- **Streamlit Components**: Mock UI components for testing
- **File System**: Temporary directories and files
- **Network**: Mock HTTP responses for external services

## 🐛 Debugging Tests

### Common Debugging Patterns
```bash
# Run with verbose output and no capture
pytest tests/test_script_generator.py -v -s

# Run with pdb debugger
pytest tests/test_script_generator.py --pdb

# Run with detailed tracebacks
pytest tests/test_script_generator.py --tb=long

# Run specific test with maximum verbosity
pytest tests/test_script_generator.py::TestIgnitionScriptGenerator::test_generate_script_with_navigation -v -s --tb=short
```

### Test Environment Variables
- `TESTING_MODE=true`: Enable testing-specific behavior
- `LOG_LEVEL=DEBUG`: Detailed logging for analysis
- `PYTHONPATH=/app`: Ensure proper module imports

### Fixture Debugging
```python
# Use captured_logs fixture to analyze log messages
def test_with_logging(script_generator, captured_logs):
    with captured_logs as logs:
        result = script_generator.generate_script(template, config)

    log_messages = logs.get_messages()
    assert any("Generating script" in msg for msg in log_messages)
```

## 📈 Performance Analysis

### Benchmarking
The test suite includes comprehensive benchmarking using `pytest-benchmark`:
- Script generation speed
- Template parsing performance
- Memory usage patterns
- Concurrent operation efficiency

### Memory Monitoring
Using `psutil` and custom fixtures:
- Memory growth detection
- Leak identification
- Resource utilization tracking
- Optimization opportunity identification

### Stress Testing
High-volume testing scenarios:
- 500+ script generations
- Concurrent multi-user simulation
- Large configuration handling
- Template caching effectiveness

---

**Next Steps**: Run `python3 scripts/run_tests.py --help` for detailed execution options or see [docs/testing_guide.md](../docs/testing_guide.md) for comprehensive documentation.
