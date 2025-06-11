# IGN Scripts - Ignition Jython Script Generator

A powerful Python application for generating, validating, and exporting Jython scripts for Ignition SCADA systems.

## 🤖 **FOR AI ASSISTANTS: PERSISTENT MEMORY AVAILABLE**

**This project includes a Neo4j graph database that serves as persistent long-term memory!**

📋 **Quick AI Assistant Persistent Memory Checklist:**
- [ ] Check if Neo4j is running: `docker-compose ps neo4j`
- [ ] Start graph database: `docker-compose up -d neo4j`
- [ ] **Connection Info**: `bolt://localhost:7687` | Username: `neo4j` | Password: `ignition-graph`
- [ ] **Web Interface**: http://localhost:7474 (Neo4j Browser)
- [ ] **Python Access**: `from src.ignition.graph.client import IgnitionGraphClient`
- [ ] Query for context-aware assistance: Contains 365/400+ Ignition functions (91.3% complete)
- [ ] **Full Documentation**: See `docs/ai_assistant_memory_system.md`

📊 **Graph Database Status:** Tasks 1-12 Complete (365 functions implemented)
- ✅ Task 1: Tag System (27 functions)
- ✅ Task 2: Database System (21 functions)
- ✅ Task 3: GUI System (26 functions)
- ✅ Task 4: Perspective System (22 functions)
- ✅ Task 5: Device Communication (37 functions)
- ✅ Task 6: Utility System (50 functions)
- ✅ Task 7: Alarm System (29 functions)
- ✅ Task 8: Print System (18 functions)
- ✅ Task 9: Security System (22 functions)
- ✅ Task 10: File & Report System (25 functions)
- ✅ Task 11: Advanced Math & Analytics Functions (30 functions)
- ✅ Task 12: Machine Learning Integration Functions (25 functions)
- 🎯 Next: Task 13 - Integration & External Systems Functions

🔧 **Quick AI Assistant Commands:**
```python
# Connect to knowledge base
from src.ignition.graph.client import IgnitionGraphClient
client = IgnitionGraphClient()
client.connect()

# Query functions by context
result = client.execute_query("MATCH (f:Function)-[:AVAILABLE_IN]->(s:Scope {name: 'Gateway'}) RETURN f.name, f.description LIMIT 10")

# Get current progress stats
result = client.execute_query("MATCH (f:Function) RETURN count(f) as total")
```

**🔗 Full documentation: [AI Assistant Memory System](docs/ai_assistant_memory_system.md)**

## 🎯 Project Overview

IGN Scripts is designed to streamline the development of Jython scripts for Ignition SCADA environments. Instead of manually writing scripts within the Ignition Designer, you can use this tool to:

- Generate Jython scripts from templates and configurations
- Validate script syntax and compatibility
- Export scripts in formats compatible with Ignition gateways
- Manage version control for Ignition projects
- Automate deployment to production environments

## 🔧 Target Environment

- **Ignition Version**: 8.1+ (primary), 8.0 (secondary)
- **Jython Version**: 2.7 (as used by Ignition)
- **Development**: Python 3.11+
- **Output**: Jython 2.7 compatible scripts

## 📋 Features (Planned)

### User Interfaces
- ✅ Command Line Interface (CLI)
- ✅ Web-based UI with Streamlit
- 🔄 Desktop GUI (future consideration)

### Script Generation
- ✅ Template-based script generation
- ✅ Vision component event handlers
- ✅ **Perspective component scripts** - Button & input handlers with validation
- 🔄 Gateway startup/shutdown scripts - Enhanced lifecycle management
- 🔄 Tag event handlers - Advanced event processing
- 🔄 Timer scripts - Scheduled operations & cron-style timing
- ✅ **Alarm pipeline scripts** - Email notification system with escalation

### Ignition System Integration
- ✅ **Gateway Connection System** - HTTP/HTTPS client with authentication
- ✅ **Multi-Gateway Management** - Connection pooling and health monitoring
- ✅ **Environment Configuration** - Secure credential management with .env
- 🔄 `system.tag.*` wrapper functions
- 🔄 `system.db.*` utilities
- 🔄 `system.gui.*` helpers
- 🔄 `system.nav.*` navigation tools
- 🔄 `system.alarm.*` management

### Resource Management
- 🔄 UDT (User Defined Type) generators
- 🔄 Tag provider configuration
- 🔄 Device connection scripts
- 🔄 User role management
- 🔄 Security configuration

### Export & Deployment
- 🔄 Gateway resource export
- 🔄 Project backup creation
- 🔄 Version control integration
- 🔄 Automated deployment

Legend: ✅ Complete | 🔄 In Progress | ⏳ Planned

## 🚀 Quick Start

### Prerequisites

1. Python 3.11 or higher
2. uv package manager
3. Access to Ignition 8.1+ environment

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd IGN_scripts

# Set up virtual environment with uv
uv venv
source .venv/bin/activate  # On Unix-like systems
# or
.venv\Scripts\activate     # On Windows

# Install dependencies
uv pip install -r requirements.txt
```

### Basic Usage

#### Web UI (Recommended for beginners)

```bash
# Launch the web interface
streamlit run src/ui/streamlit_app.py
```

Then open your browser to `http://localhost:8501` for a user-friendly interface.

📚 **For detailed UI usage instructions, see [ui_readme.md](ui_readme.md)**

#### Enhanced CLI with Learning System

```bash
# View available commands with beautiful terminal UI
python -m src.core.enhanced_cli --help

# Interactive script generation with recommendations
python -m src.core.enhanced_cli script generate -i

# List templates with usage statistics
python -m src.core.enhanced_cli template list --detailed

# Explore usage patterns and analytics
python -m src.core.enhanced_cli learning patterns

# Launch interactive pattern explorer
python -m src.core.enhanced_cli learning explore

# Gateway connection management
python -m src.core.enhanced_cli gateway list
python -m src.core.enhanced_cli gateway connect --name local_dev
python -m src.core.enhanced_cli gateway health --all
```

📚 **For comprehensive CLI usage instructions, see [cli_readme.md](cli_readme.md)**

### Gateway Configuration

The system supports connecting to multiple Ignition gateways for testing, development, and production use:

```bash
# Test gateway connection interactively
python scripts/test_specific_gateway.py

# Discover available endpoints on a gateway
python scripts/test_ignition_endpoints.py

# Run comprehensive connection tests
python scripts/test_final_connection.py
```

Configure gateways using environment variables in a `.env` file:

```bash
# Copy the template and customize
cp gateway_config.env .env

# Edit with your gateway details
IGN_GATEWAYS=local_dev,production

IGN_LOCAL_DEV_HOST=localhost
IGN_LOCAL_DEV_PORT=8088
IGN_LOCAL_DEV_HTTPS=false
IGN_LOCAL_DEV_USERNAME=admin
IGN_LOCAL_DEV_PASSWORD=password
```

🔒 **Security Note**: Never commit `.env` files to version control. They contain sensitive credentials.

## 📁 Project Structure

```
IGN_scripts/
├── src/
│   ├── core/           # Core application logic
│   ├── ui/             # User interfaces
│   │   └── streamlit_app.py  # Web UI with Streamlit
│   ├── ignition/       # Ignition-specific modules
│   │   ├── templates/  # Jython script templates
│   │   ├── generators/ # Script generation utilities
│   │   ├── exporters/  # Gateway export tools
│   │   └── validators/ # Script validation
│   ├── api/           # External integrations
│   └── models/        # Data models
├── templates/         # Script templates
│   ├── gateway/       # Gateway script templates
│   ├── vision/        # Vision component templates
│   ├── perspective/   # Perspective script templates
│   ├── tags/          # Tag-related templates
│   └── alarms/        # Alarm system templates
├── tests/             # Test suite
├── scripts/           # Standalone utilities
│   └── run_ui.py      # Launch script for web UI
├── examples/          # Example configurations
├── docs/              # Documentation
└── config/            # Configuration files
```

## 📚 Documentation

### User Guides
- **[CLI Usage Guide](cli_readme.md)** - Comprehensive guide to the enhanced CLI with learning system
- **[Web UI Guide](ui_readme.md)** - Complete instructions for the Streamlit web interface
- **[Quick Start Tutorial](docs/streamlit_ui_guide.md)** - Getting started with the web interface

### Technical Documentation
- **[AI Assistant Memory System](docs/ai_assistant_memory_system.md)** - Neo4j graph database integration
- **[Testing Framework](docs/testing_guide.md)** - Comprehensive testing approach and utilities
- **[Project Structure](docs/project_structure.md)** - Detailed codebase organization
- **[Enhanced Graph Functions](docs/enhanced_graph_functions_README.md)** - Ignition function database

### Development Resources
- **[Testing Summary](docs/TESTING_SUMMARY.md)** - Testing implementation summary
- **[Learning System Integration](docs/LEARNING_SYSTEM_INTEGRATION_SUMMARY.md)** - Phase 1 learning system details
- **[Stage 1 Completion](docs/stage1_completion_summary.md)** - Initial development milestone
- **[Task 5 Summary](docs/TASK_5_COMPLETION_SUMMARY.md)** - Recent development progress

### Configuration Examples
- **[Templates Directory](templates/)** - Available Jinja2 script templates
- **[Example Configurations](examples/)** - Sample JSON configuration files
- **[Docker Configuration](docker-compose.yml)** - Neo4j database setup

## 🔨 Development

### Environment Setup

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
ruff check --fix .

# Run type checking
mypy .
```

### Development Guidelines

1. **Python for Development**: Use modern Python 3.11+ features for the development environment
2. **Jython for Output**: Generated scripts must be compatible with Jython 2.7
3. **Ignition Compatibility**: All generated code must work within Ignition's scripting environment
4. **Version Control**: Use git for source control, design for Ignition project versioning

## 🧪 Testing

IGN Scripts includes a comprehensive Docker-based testing environment with real-time monitoring and optimization capabilities.

### Quick Testing

```bash
# Run all tests
python3 scripts/run_tests.py --all

# Run specific test types
python3 scripts/run_tests.py --unit
python3 scripts/run_tests.py --integration
python3 scripts/run_tests.py --ui
python3 scripts/run_tests.py --performance

# Monitor logs in real-time
python3 scripts/monitor_logs.py --live

# Analyze performance and get optimization recommendations
python3 scripts/monitor_logs.py --analyze
```

### Test Categories

- **Unit Tests**: Component-level testing with mocked dependencies
- **Integration Tests**: End-to-end workflow testing
- **UI Tests**: Streamlit interface testing with mocked components
- **Performance Tests**: Benchmarking and profiling with optimization insights

### Coverage & Reports

- **Code Coverage**: 80%+ target with HTML reports
- **Performance Benchmarks**: JSON reports with timing and memory metrics
- **Log Analysis**: Automated optimization recommendations

📚 **For detailed testing instructions, see [docs/testing_guide.md](docs/testing_guide.md)**
🚀 **For quick testing reference, see [TESTING.md](TESTING.md)**

## 📚 Ignition Script Contexts

This tool supports script generation for various Ignition contexts:

### Gateway Scripts
- Startup scripts
- Shutdown scripts
- Timer scripts (fixed delay, fixed rate)
- Message handlers
- Database connection scripts

### Vision Client Scripts
- Component event handlers (actionPerformed, mouseClicked, etc.)
- Window event handlers (internalFrameOpened, etc.)
- Property change scripts
- Custom methods

### Perspective Session Scripts
- Component event handlers
- View scripts (onStartup, onShutdown)
- Session event scripts
- Custom properties

### Tag Scripts
- Value change scripts
- Quality change scripts
- Alarm scripts
- UDT parameter scripts

## 🌐 Web Interface

IGN Scripts includes a comprehensive web-based interface built with Streamlit, perfect for users who prefer graphical interfaces over command-line tools.

### Features
- **📝 Script Generator**: Interactive form-based script generation
- **📋 Template Browser**: Browse and preview available templates
- **📁 File Upload**: Upload configuration files for batch generation
- **💾 Download Scripts**: Download generated scripts directly
- **📚 Built-in Documentation**: Comprehensive help and examples
- **🎯 Quick Actions**: One-click generation for common scenarios

### Pages Available
- **Home**: Overview and quick actions
- **Script Generator**: Full-featured script generation with three modes:
  - From Template (guided form interface)
  - From Configuration File (upload JSON configs)
  - Quick Generate (common scenarios with minimal input)
- **Templates**: Browse, preview, and download templates
- **Validation**: Script and configuration validation (coming soon)
- **Export**: Project export utilities (coming soon)
- **Documentation**: Complete usage guide and examples

## 🎓 Examples

### Generate a Basic Button Click Handler

```bash
python -m src.core.enhanced_cli script generate \
  --type vision-button \
  --template basic-navigation \
  --config '{"target_window": "MainMenu", "params": {}}'
```

### Create UDT Definition Scripts

```bash
python -m src.core.enhanced_cli udt generate \
  --name "MotorControl" \
  --type "Industrial" \
  --parameters speed,temperature,status
```

### Export Project for Gateway

```bash
python -m src.core.enhanced_cli export project \
  --source ./my_ignition_project \
  --output ./exports/production_v1.2.0.zip \
  --format gateway-import
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Resources

- [Ignition Documentation](https://docs.inductiveautomation.com/)
- [Ignition SDK](https://github.com/inductiveautomation/ignition-sdk-examples)
- [Jython Documentation](https://jython.readthedocs.io/)
- [Ignition Community Forum](https://forum.inductiveautomation.com/)

## ⚠️ Disclaimer

This is an independent project and is not affiliated with or endorsed by Inductive Automation. Ignition is a trademark of Inductive Automation.

## 📞 Support

- Check the [Issues](https://github.com/your-repo/issues) page for common problems
- Review the [Wiki](https://github.com/your-repo/wiki) for detailed documentation
- Join discussions in our [Community Forum](https://github.com/your-repo/discussions)
