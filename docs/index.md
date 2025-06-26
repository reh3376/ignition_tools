# IGN Scripts Documentation

Welcome to the comprehensive documentation for IGN Scripts - a powerful toolkit for generating, testing, and managing Jython scripts for Ignition SCADA systems.

## Quick Start

- **New Users**: Start with the [Getting Started Guide](getting-started/overview.md)
- **CLI Users**: See the [CLI Usage Guide](cli_readme.md)
- **Web Interface**: Check out the [Web UI Guide](ui_readme.md)
- **Developers**: Review [Contributing Guidelines](contributing/guidelines.md)

## Documentation Structure

### 📚 User Guides
- [Getting Started](getting-started/) - New user orientation and setup
- [CLI Usage](api/cli-interface.md) - Command-line interface guide
- [Web Interface](api/ui-interface.md) - Streamlit web application guide
- [OPC-UA Integration](configuration/opcua-config.md) - OPC-UA client tools and integration

### 🛠️ Development
- [Contributing Guidelines](contributing/guidelines.md) - How to contribute to the project
- [Coding Standards](development/coding-standards.md) - Jython and Python coding standards
- [Testing Guide](development/testing-guide.md) - Testing framework and best practices
- [Architecture](development/architecture.md) - System architecture and design

### 🔧 Technical Reference
- [API Reference](api/) - Complete API documentation
- [Configuration](configuration/) - Configuration file formats and options
- [Templates](templates/) - Script template documentation
- [Knowledge Graph](api/knowledge-graph.md) - AI assistant memory system
- [Learning System](api/learning-system.md) - Usage tracking and recommendations

### 🚀 Deployment
- [Installation](deployment/installation.md) - Installation and setup instructions
- [Docker Setup](deployment/docker.md) - Container deployment guide
- [Production Deployment](deployment/production.md) - Production environment setup
- [Troubleshooting](troubleshooting/) - Common issues and solutions

### 📋 Project Management
- [Roadmap](roadmap.md) - Project roadmap and milestones
- [Release Notes](releases/) - Version history and changes
- [Security](security/) - Security considerations and token management

## Features Overview

### 🎯 Core Capabilities
- **Script Generation**: Create Jython scripts for all Ignition contexts
- **Template System**: Reusable templates for common patterns
- **Graph Database**: 400+ Ignition system functions with relationship mapping
- **OPC-UA Integration**: Live OPC-UA client with real-time monitoring
- **Gateway Connection**: Direct Ignition gateway connectivity and testing
- **Export/Import System**: Complete project lifecycle management with validation ✅ **NEW**

### 🧠 Intelligence Features
- **Context-Aware Generation**: Scripts optimized for specific Ignition contexts
- **Learning System**: Usage pattern analysis and smart recommendations
- **Function Discovery**: Explore 400+ Ignition system functions with relationships
- **Validation**: Script validation and compatibility checking
- **Import Validation**: Comprehensive pre-import validation with detailed reporting ✅ **NEW**

### 🛠️ Developer Tools
- **CLI Interface**: Powerful command-line tools for script generation
- **Web Interface**: User-friendly Streamlit application
- **Testing Framework**: Comprehensive testing with Docker environment
- **CI/CD Integration**: GitHub Actions workflows for automated testing
- **Project Import Tools**: Multiple import modes with conflict resolution ✅ **NEW**

## Getting Help

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/reh3376/ignition_tools/issues)
- **Discussions**: Join community discussions on [GitHub Discussions](https://github.com/reh3376/ignition_tools/discussions)
- **Documentation**: Browse this documentation for detailed guides
- **Examples**: Check the [examples/](../examples/) directory for sample scripts

## Project Status

- **Version**: 0.4.0
- **Phase**: 13.2 Complete - Model Fine-tuning & Specialization
- **Target Ignition Version**: 8.1+
- **Jython Version**: 2.7
- **Development Status**: Production ready with active development
- **Graph Database**: 11,608+ nodes with comprehensive code intelligence
- **CLI Commands**: 35+ commands across 9 major categories including LLM fine-tuning

## Recent Completions

### Phase 13.2: Model Fine-tuning & Specialization ✅ **COMPLETED** - 2025-06-26
- **8B Parameter LLM Infrastructure**: Production-ready fine-tuning system with auto-detecting GPU support
- **Neo4j Knowledge Graph Integration**: Extract training data from 11,608+ specialized nodes
- **Parameter-Efficient Fine-tuning**: LoRA/QLoRA configuration with comprehensive validation
- **Quality-Controlled Data Pipeline**: Successfully extracted 1,012 Method records, filtered to 46 high-quality samples
- **Data Augmentation**: Generated 92 training samples with instruction variations
- **CLI Interface**: 3 comprehensive commands (extract-data, train, status) with extensive options
- **Apple Silicon MPS Support**: Auto-detecting GPU configuration for Apple Silicon, CUDA, and CPU fallback
- [View Phase 13.2 Completion Summary](phase_summary/PHASE_13_2_MODEL_FINE_TUNING_SPECIALIZATION.md)

### Phase 11.1: SME Agent Infrastructure & Human Evaluation ✅ **COMPLETED** - 2025-01-29
- **SME Agent Foundation**: Intelligent assistant with progressive complexity deployment
- **Human Evaluation Framework**: Decision logging, batch management, and reinforcement learning
- **11 CLI Commands**: Complete SME Agent lifecycle management and human evaluation workflow
- **Progressive Complexity**: 4-tier deployment system (basic → standard → advanced → enterprise)
- **Decision Logging**: Comprehensive tracking with metadata, confidence scores, and processing time
- **Batch Management**: Human expert review workflow with JSON/CSV export and import capabilities
- [View Phase 11.1 Completion Summary](phase_summary/PHASE_11_1_COMPLETION_SUMMARY.md)

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

*Last updated: 2025-06-26*
