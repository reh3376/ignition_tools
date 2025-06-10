# IGN Scripts Documentation Index

Welcome to the IGN Scripts documentation! This directory contains comprehensive guides for using and contributing to the project.

## 📚 Documentation Overview

### Getting Started
- **[Main README](../README.md)**: Project overview, installation, and basic usage
- **[Quick Testing Guide](../TESTING.md)**: Fast reference for Docker testing environment

### User Guides
- **[Streamlit UI Guide](streamlit_ui_guide.md)**: Complete web interface documentation
  - Interactive script generation
  - Template browser and configuration upload
  - Built-in documentation and examples

### Developer Guides
- **[Testing Environment Guide](testing_guide.md)**: Comprehensive Docker testing documentation
  - Docker container setup and configuration
  - Test categories (unit, integration, UI, performance)
  - Real-time monitoring and log analysis
  - Performance benchmarking and optimization
  - Troubleshooting and best practices

- **[Test Suite Documentation](../tests/README.md)**: Detailed test structure and usage
  - Test categories and fixtures
  - Running and debugging tests
  - Performance standards and quality gates

### Project Information
- **[Roadmap](../roadmap.md)**: Development progress and future plans
- **[Configuration](../pyproject.toml)**: Project metadata and dependencies

## 🎯 Quick Navigation

### For Users
1. **First Time**: Start with [Main README](../README.md) → [Streamlit UI Guide](streamlit_ui_guide.md)
2. **Web Interface**: [Streamlit UI Guide](streamlit_ui_guide.md)
3. **Command Line**: [Main README](../README.md) CLI section

### For Developers
1. **Setup**: [Main README](../README.md) development section
2. **Testing**: [TESTING.md](../TESTING.md) → [Testing Guide](testing_guide.md)
3. **Contributing**: [Test Suite Documentation](../tests/README.md)

### For DevOps/CI
1. **Docker Testing**: [TESTING.md](../TESTING.md)
2. **Monitoring**: [Testing Guide](testing_guide.md) monitoring section
3. **Performance**: [Testing Guide](testing_guide.md) optimization workflows

## 🔧 Testing & Quality Assurance

IGN Scripts includes a comprehensive testing environment:

| Component | Purpose | Documentation |
|-----------|---------|---------------|
| **Docker Environment** | Isolated, reproducible testing | [TESTING.md](../TESTING.md) |
| **Test Suite** | Unit, integration, UI, performance tests | [tests/README.md](../tests/README.md) |
| **Monitoring** | Real-time log analysis and optimization | [Testing Guide](testing_guide.md) |
| **Coverage Reports** | Code coverage tracking (80%+ target) | [Testing Guide](testing_guide.md) |

## 🌐 User Interfaces

IGN Scripts provides multiple interfaces:

| Interface | Purpose | Documentation |
|-----------|---------|---------------|
| **Web UI (Streamlit)** | User-friendly graphical interface | [Streamlit UI Guide](streamlit_ui_guide.md) |
| **Command Line** | Scripting and automation | [Main README](../README.md) |
| **Docker Environment** | Testing and development | [TESTING.md](../TESTING.md) |

## 📊 Features & Capabilities

### Script Generation
- ✅ Template-based Jython script generation
- ✅ Vision component event handlers
- ✅ Custom script templates
- 🔄 Gateway and Perspective scripts (planned)

### Testing & Quality
- ✅ Comprehensive Docker testing environment
- ✅ Real-time performance monitoring
- ✅ Automated optimization recommendations
- ✅ Code coverage and quality gates

### User Experience
- ✅ Web-based UI with Streamlit
- ✅ CLI for automation and scripting
- ✅ Interactive documentation and examples
- ✅ File upload and download capabilities

## 🚀 Quick Start Commands

### Web Interface
```bash
streamlit run src/ui/streamlit_app.py
# or
python3 scripts/run_ui.py
```

### Testing
```bash
# Run all tests
python3 scripts/run_tests.py --all

# Monitor logs
python3 scripts/monitor_logs.py --live

# Performance analysis
python3 scripts/monitor_logs.py --analyze
```

### CLI Usage
```bash
# Generate script
python -m src.core.cli script generate --template vision/button_click_handler.jinja2 --component-name MyButton

# List templates
python -m src.core.cli template list
```

## 📞 Getting Help

- **Issues**: Check existing documentation or create an issue
- **Questions**: Review the comprehensive guides in this directory
- **Contributing**: See testing documentation for development setup

---

**Last Updated**: January 2025
**Version**: 0.1.0
**Documentation Coverage**: Complete
