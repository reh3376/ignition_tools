# IGN Scripts - Comprehensive Ignition SCADA Development Platform

**Version**: 0.2.1 | **Phase**: 9.2 Complete - Core Module Infrastructure | **Status**: Production Ready

IGN Scripts is an intelligent, AI-enhanced development platform for Ignition SCADA systems that combines script generation, code intelligence, module development, and industrial automation capabilities into a unified ecosystem. With the

## 🏭 **Core Services & Capabilities**

### **1. 🤖 AI-Enhanced Code Intelligence System** ✅ **Phase 8 Complete**
- **Neo4j Graph Database**: 10,389+ nodes with comprehensive Ignition function knowledge
- **Vector Embeddings**: 384-dimensional semantic search and code analysis
- **Automated Refactoring**: Intelligent code splitting and AST-based analysis
- **AI Assistant Enhancement**: Context-aware development assistance

### **2. 🔧 Ignition Module Development Framework** ✅ **Phase 9.2 Complete**
- **Core Module Infrastructure**: AbstractIgnitionModule base class with lifecycle management
- **Configuration Management**: JSON-based persistence with validation and backup
- **Diagnostics Framework**: Multi-handler logging with health monitoring
- **Module SDK Integration**: Complete development environment for custom Ignition modules

### **3. 📝 Intelligent Script Generation Engine** ✅ **Phase 3 Complete**
- **424+ Ignition Functions**: Complete function library (106% of target - MILESTONE EXCEEDED!)
- **Template System**: Jinja2-based templates for all Ignition contexts
- **Multi-Context Support**: Gateway, Vision, Perspective, Tag, and Alarm scripts
- **Validation Framework**: Syntax and compatibility checking

### **4. 🏭 Industrial OPC-UA Integration** ✅ **Phase 7 Complete**
- **Live OPC-UA Client**: Real-time industrial device connectivity
- **Security Framework**: Certificate-based authentication
- **Monitoring Dashboard**: Comprehensive Streamlit-based industrial UI
- **Data Operations**: Read/write with subscription and historical data access

### **5. 📊 Advanced Analytics & Workflow Integration** ✅ **Phase 8 Complete**
- **Technical Debt Analysis**: Comprehensive code quality assessment
- **Performance Insights**: Automated optimization recommendations
- **Git Integration**: Intelligent version control with evolution tracking
- **Workflow Automation**: Pre-commit hooks and quality gates

## 🚀 **Quick Start**

### Prerequisites
- **Python**: 3.11+ (development) / Jython 2.7 (output compatibility)
- **Docker**: For Neo4j database and testing environments
- **Git**: Version control and project management
- **uv**: Modern Python package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/reh3376/IGN_scripts.git
cd IGN_scripts

# Set up Python environment with uv
uv venv && source .venv/bin/activate  # Unix/macOS
# or .venv\Scripts\activate           # Windows

# Install dependencies
uv pip install -r requirements.txt
```

4. Set up GitHub repositories:
   ```bash
   # Set required environment variables
   export DOCKER_TOKEN="your_docker_token"
   export CODECOV_TOKEN="your_codecov_token"

   # Run the setup script
   ./scripts/setup_github_repo.sh
   ```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m e2e
```

### Building Docker Images

```bash
# Build MCP service
cd mcp
docker build -t ghcr.io/reh3376/mcp:latest .

# Build MCP Tools service
cd ../mcp-tools
docker build -t ghcr.io/reh3376/mcp-tools:latest .
```

### Documentation

Documentation for each service is available in their respective `docs` directories and is also published to GitHub Pages:

- MCP Documentation: https://reh3376.github.io/mcp/
- MCP Tools Documentation: https://reh3376.github.io/mcp-tools/

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue in the respective repository:
- [MCP Issues](https://github.com/reh3376/mcp/issues)
- [MCP Tools Issues](https://github.com/reh3376/mcp-tools/issues)

# IGN Scripts - Ignition Jython Script Generator

A powerful Python application for generating, validating, and exporting Jython scripts for Ignition SCADA systems.

## 🤖 **FOR AI ASSISTANTS: PERSISTENT MEMORY AVAILABLE**

**This project includes a Neo4j graph database that serves as persistent long-term memory!**

📋 **Quick AI Assistant Persistent Memory Checklist:**
- [ ] Check if Neo4j is running: `docker-compose ps neo4j`
- [ ] Start graph database: `docker-compose up -d neo4j`
- [ ] **Connection Info**: `bolt://localhost:7687` | Username: `neo4j` | Password: `ignition-graph`
- [ ] **Web Interface**: http://localhost:7474 (Neo4j Browser)
- [ ] **Setup Environment**: Copy `docs/env_template.txt` to `.env` with your credentials
- [ ] **Python Access**: `from src.ignition.graph.client import IgnitionGraphClient`
- [ ] Query for context-aware assistance: Contains 408/400+ Ignition functions (102.0% complete - MILESTONE EXCEEDED!)
- [ ] **Full Documentation**: See `docs/ai_assistant_memory_system.md`

🎊 **Graph Database Status:** Tasks 1-16 Complete (424 functions - 400+ MAJOR MILESTONE EXCEEDED!)
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
- ✅ Task 13: Integration & External Systems Functions (30 functions)
- ✅ Task 14: OPC-UA Client Integration Functions (14 functions)
- ✅ Task 15: OPC-UA Live Client Integration (CLI/UI Enhancement) 🏭 **PRODUCTION READY!**
- ✅ Task 16: Sequential Function Charts & Recipe Management (16 functions) 🏭 **NEW!**
- 🚀 Next Phase: Task 17 (System Administration & Project Management)

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
- **Import/Export Ignition projects with validation** ✅ **NEW**

## 🏭 **NEW: Industrial OPC-UA Integration**

**Task 14 Complete**: Added comprehensive OPC-UA client capabilities for real industrial automation:

### OPC-UA Function Library (14 Functions)
- ✅ **Connection Management**: Secure OPC-UA server connections with certificate handling
- ✅ **Address Space Navigation**: Browse server nodes and discover device structures
- ✅ **Data Operations**: Read/write OPC-UA node values with type validation
- ✅ **Real-time Monitoring**: Subscribe to data changes and alarm events
- ✅ **Historical Data**: Access time-series data for analysis and reporting

### **✅ Task 15 Phase 2 Complete: Live OPC-UA Client Integration**
Transform from script generator to full industrial automation platform:
- **✅ CLI Integration**: Complete 7-command CLI with `ignition opcua connect/browse/read/monitor/status/info/disconnect`
- **✅ Live UI Dashboard**: Comprehensive Streamlit-based industrial monitoring with real-time data
- **✅ Security Framework**: Certificate-based authentication with comprehensive security management
- **✅ Configuration Management**: Wizard-driven setup with save/load functionality
- **✅ Industrial Connectivity**: Production-ready OPC-UA client for PLC and SCADA systems

📋 **Detailed Documentation**: [Task 15 Phase 2 Summary](docs/TASK_15_PHASE_2_COMPLETION_SUMMARY.md) | [OPC-UA UI Guide](docs/opcua_ui_guide.md)

## 🏭 **Phase 2 Complete: Export/Import System** ✅ **NEW**

**Complete project lifecycle management for Ignition systems:**

### Import System Features
- **✅ Multiple Import Modes**: MERGE, OVERWRITE, SKIP_CONFLICTS deployment strategies
- **✅ Comprehensive Validation**: File format, size, and type validation with detailed reporting
- **✅ Rich CLI Experience**: Beautiful terminal output with colored panels and progress indicators
- **✅ Dry Run Capability**: Test imports without making changes
- **✅ Error Handling**: Graceful failure handling with actionable error messages

### Supported Import Formats
- **`.proj`** - Project export files from Ignition Designer
- **`.gwbk`** - Gateway backup files for full system imports
- **`.json`** - JSON export files with project data
- **`.zip`** - Compressed export files

### CLI Commands
```bash
# Import project with validation
python -m src.core.enhanced_cli import-project project.proj MyProject

# Validate import file before importing
python -m src.core.enhanced_cli validate-import backup.gwbk

# Import with specific mode
python -m src.core.enhanced_cli import-project export.json Project --mode overwrite --dry-run
```

📋 **Detailed Documentation**: [Phase 2 Completion Summary](docs/PHASE_2_IMPORT_SYSTEM_COMPLETION_SUMMARY.md)

## 🛡️ **Phase 3 Complete: System Function Wrappers** ✅ **NEW**

**Enhanced Ignition system functions with comprehensive error handling and monitoring:**

### System Function Wrappers Features
- **✅ 6 Major System Modules**: Tag, Database, GUI, Navigation, Alarm, and Utility wrappers
- **✅ 24 Enhanced Functions**: All major Ignition system functions with error handling
- **✅ Quality Code Translation**: Human-readable quality names (GOOD, BAD_NOT_CONNECTED, etc.)
- **✅ Performance Monitoring**: Execution time tracking and success rate analytics
- **✅ Retry Logic**: Configurable retry attempts with intelligent backoff
- **✅ Input Validation**: Type checking and parameter validation for all functions
- **✅ Mock Support**: Full development environment support without Ignition

### Enhanced System Modules
- **SystemTagWrapper**: Enhanced tag operations with quality validation and batch support
- **SystemDbWrapper**: Database operations with query validation and performance metrics
- **SystemGuiWrapper**: GUI operations with input validation and comprehensive logging
- **SystemNavWrapper**: Window navigation with parameter validation and error recovery
- **SystemAlarmWrapper**: Alarm operations with batch support and filtering capabilities
- **SystemUtilWrapper**: Utility operations with enhanced logging and validation

### CLI Commands
```bash
# Test all system function wrappers
python -m src.core.enhanced_cli wrappers test-all

# Test individual wrappers
python -m src.core.enhanced_cli wrappers test-tag --tag-path "[default]MyTag"
python -m src.core.enhanced_cli wrappers test-db --query "SELECT COUNT(*) FROM MyTable"

# Show wrapper information and capabilities
python -m src.core.enhanced_cli wrappers info
```

### Wrapper Benefits
- **Reliability**: Retry logic and graceful error handling for production environments
- **Observability**: Comprehensive logging and metrics collection for debugging
- **Validation**: Input validation prevents common scripting errors
- **Context Awareness**: Automatic adaptation to Ignition execution environment

📋 **Detailed Documentation**: [Phase 3 Completion Summary](docs/completion-summaries/PHASE_3_SYSTEM_WRAPPERS_COMPLETION_SUMMARY.md)

## 🔗 **Phase 3 Complete: Data Integration Scripts** ✅ **NEW**

**Comprehensive data integration framework for industrial automation systems:**

### Data Integration Features
- **✅ Multi-Database Support**: 7 database types (Neo4j, PostgreSQL/Supabase, InfluxDB, SQL Server, MySQL, SQLite)
- **✅ Historian Query Generation**: Optimized queries for time series databases (InfluxDB, TimescaleDB, Ignition Historian)
- **✅ OPC Tag Management**: Complete tag lifecycle with browsing, creation, and operations
- **✅ Report Generation**: Industrial reports in multiple formats (CSV, JSON, HTML)
- **✅ Environment Security**: All credentials externalized to .env files
- **✅ CLI Integration**: Rich terminal interface with 15+ commands across 4 command groups

### Database Connection Manager
- **Connection Pooling**: Efficient resource management with configurable pool sizes
- **SSL/TLS Support**: Secure connections for production environments
- **Auto-Discovery**: Automatic configuration loading from environment variables
- **Multi-Database**: Unified interface for different database types
- **Health Monitoring**: Connection testing and diagnostics

### Historian Query Generator
- **Time Series Optimization**: Performance-optimized queries for large industrial datasets
- **Flexible Time Ranges**: Duration-based and absolute time range specifications
- **Aggregation Functions**: Average, min, max, sum, count with configurable intervals
- **Tag Filtering**: Advanced filtering and grouping capabilities
- **Multi-Historian**: Support for InfluxDB, TimescaleDB, and Ignition Historian

### OPC Tag Manager
- **Tag Browsing**: Hierarchical folder structure with industrial mock data
- **Batch Operations**: Efficient bulk tag creation and management
- **Quality Management**: Comprehensive quality code translation (GOOD, BAD_NOT_CONNECTED, etc.)
- **Script Generation**: Production-ready Jython scripts for Ignition deployment
- **Tag Operations**: Create, read, write, and browse with validation

### Report Generator
- **Industrial Reports**: Production, alarm, trend, and summary reports
- **Multiple Formats**: CSV, JSON, HTML with extensible architecture
- **Time-Based Analysis**: Configurable time ranges and data aggregation
- **Ignition Integration**: Compatible script generation for Ignition report system
- **Custom Templates**: Flexible report templates for different use cases

### CLI Commands
```bash
# Database operations
python -m src.core.enhanced_cli data database test-connection --config-name neo4j_default
python -m src.core.enhanced_cli data database list-configs

# Tag management
python -m src.core.enhanced_cli data tags browse --path PLCs
python -m src.core.enhanced_cli data tags read --tag-paths "PLC1/Status,PLC1/Heartbeat"

# Report generation
python -m src.core.enhanced_cli data reports production --hours 24 --format csv
python -m src.core.enhanced_cli data reports alarms --hours 8 --format json

# System status and health
python -m src.core.enhanced_cli data status
```

### Environment Configuration
```bash
# Database Configurations
NEO4J_HOST=localhost
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

POSTGRES_HOST=localhost
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=your-password

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

INFLUXDB_HOST=localhost
INFLUXDB_TOKEN=your-token
```

### Integration Benefits
- **Production Ready**: Comprehensive error handling and retry logic
- **Security First**: No hardcoded credentials, SSL/TLS support throughout
- **Performance Optimized**: Connection pooling and query optimization
- **Development Friendly**: Mock data and testing capabilities
- **Ignition Compatible**: Generated scripts work seamlessly in Ignition environment

📋 **Detailed Documentation**: [Phase 3 Data Integration Summary](docs/completion-summaries/PHASE_3_DATA_INTEGRATION_COMPLETION_SUMMARY.md)

## 🧠 **NEW: Dataset Curation for AI/ML** ✅ **Phase 3 Extension**

**Interactive dataset building and curation for AI/ML model preparation:**

### Dataset Curation Features
- **✅ Interactive Web UI**: Streamlit-based dataset curation studio with `ign data dataset buildout`
- **✅ Multi-Source Integration**: Databases, historians, OPC tags, files, and APIs
- **✅ Feature Engineering**: Visual feature definition with transformations and validation
- **✅ Data Quality Assessment**: Automated quality scoring with detailed reports and recommendations
- **✅ ML-Ready Exports**: CSV, Parquet, JSON formats with metadata and train/test splitting
- **✅ Real-time Processing**: Live feedback during dataset processing and validation

### Dataset Types Supported
- **Classification**: Binary and multi-class classification problems
- **Regression**: Continuous value prediction
- **Time Series**: Sequential data analysis and forecasting
- **Anomaly Detection**: Outlier and anomaly identification
- **Clustering**: Unsupervised grouping analysis
- **Forecasting**: Future value prediction

### Interactive UI Features
- **Dataset Overview Dashboard**: Summary statistics, status distribution, quality visualization
- **Dataset Creation Wizard**: Step-by-step setup with data source configuration
- **Feature Engineering Interface**: Visual feature definition and transformation tools
- **Data Quality Assessment**: Interactive quality reports with radar charts and recommendations
- **Export & Deployment**: Multiple format support with ML platform integration options

### CLI Commands
```bash
# Create sample dataset for testing
python -m src.core.enhanced_cli data dataset sample

# Launch interactive dataset curation UI
python -m src.core.enhanced_cli data dataset buildout

# Create new dataset from command line
python -m src.core.enhanced_cli data dataset create --name "Production_Data" --type regression

# List all datasets with status
python -m src.core.enhanced_cli data dataset list
```

### Data Quality Metrics
- **Completeness**: Missing value assessment (0-100%)
- **Consistency**: Data format and range validation (0-100%)
- **Accuracy**: Data correctness evaluation (0-100%)
- **Uniqueness**: Duplicate detection and scoring (0-100%)
- **Timeliness**: Data freshness assessment (0-100%)
- **Overall Quality**: Excellent, Good, Fair, Poor, Critical ratings

### Quick Start
1. **Install Dependencies**: `pip install streamlit plotly pandas scikit-learn`
2. **Create Sample Dataset**: `ign data dataset sample`
3. **Launch UI**: `ign data dataset buildout`
4. **Build Your Dataset**: Use the interactive interface to add sources, define features, and export

📋 **Detailed Documentation**: [Dataset Curation Guide](docs/completion-summaries/PHASE_3_DATASET_CURATION_COMPLETION_SUMMARY.md)

## 🔄 **NEW: Version Control Intelligence**

**✅ Complete**: Advanced version control intelligence for Ignition projects with intelligent change analysis and deployment planning:

### Version Control Intelligence Features
- ✅ **Change Tracking**: SHA-256 file monitoring with resource type classification
- ✅ **Risk Assessment**: Multi-factor risk scoring based on change type, resource type, and location
- ✅ **Impact Analysis**: Intelligent analysis of commit and file change impacts
- ✅ **Conflict Prediction**: Merge conflict prediction between branches
- ✅ **Release Planning**: Intelligent release planning with multiple strategies
- ✅ **Git Integration**: Automatic repository detection and status monitoring

### CLI Commands
```bash
# Check version control intelligence status
python -m src.core.enhanced_cli version status --detailed

# Analyze impact of changes
python -m src.core.enhanced_cli version analyze-commit --files="src/core/enhanced_cli.py"

# Predict merge conflicts
python -m src.core.enhanced_cli version predict-conflicts --source-branch="feature/new-feature" --target-branch="main"

# Plan releases with intelligent recommendations
python -m src.core.enhanced_cli version plan-release --version="v1.1.0" --strategy="incremental"
```

### Supported Resource Types
- Vision Windows (*.proj)
- Perspective Views (*.json)
- Gateway Scripts (*.py)
- Tag Configurations
- Database Connections
- Device Connections
- Security Configurations
- Alarm Configurations
- UDT Definitions
- Named Queries (*.sql)
- Report Templates

📋 **Detailed Documentation**: [Version Control Intelligence Plan](docs/VERSION_CONTROL_INTELLIGENCE_PLAN.md) | [Implementation Summary](docs/VERSION_CONTROL_INTELLIGENCE_SUMMARY.md)

## 🧠 **NEW: Code Intelligence System**

**✅ Phase 8.1 Complete**: Advanced code intelligence system using Neo4j for structural relationships and vector embeddings for semantic search. Addresses growing codebase complexity (2,300+ line files) with persistent, context-aware memory for AI assistants.

### Code Intelligence Features
- ✅ **AST-based Analysis**: Python file parsing with complexity metrics and maintainability index
- ✅ **Graph Database Schema**: 4 node types (CodeFile, Class, Method, Import) with comprehensive relationships
- ✅ **Vector Support**: 3 vector indexes for 384-dimensional embeddings with cosine similarity
- ✅ **Context Retrieval**: Intelligent file context, cross-file relationships, and impact analysis
- ✅ **CLI Integration**: Rich terminal UI with progress indicators and detailed analysis

### Database Statistics
- **Live Data**: 4 files analyzed, 8 classes, 36 imports stored in Neo4j
- **Schema**: 11 constraints, 25 indexes including 3 vector indexes
- **Relationships**: CONTAINS, HAS_METHOD, IMPORTS for code structure mapping

### CLI Commands
```bash
# Check code intelligence system status
python -m src.core.enhanced_cli code-status --detailed

# Analyze specific files with complexity metrics
python -m src.core.enhanced_cli analyze-file src/ignition/code_intelligence/analyzer.py --detailed

# Search code elements by name or content
python -m src.core.enhanced_cli search-code "CodeAnalyzer" --type class --limit 5
```

### Implementation Files
- `src/ignition/code_intelligence/schema.py` - Neo4j schema management and vector indexes
- `src/ignition/code_intelligence/analyzer.py` - AST-based Python code analysis engine
- `src/ignition/code_intelligence/manager.py` - Central coordinator for code intelligence operations

📋 **Detailed Documentation**: [Code Intelligence Phase 8.1 Summary](docs/CODE_INTELLIGENCE_PHASE_8_1_SUMMARY.md)

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
- ✅ **Version control integration** - Complete intelligence system with change tracking and risk assessment
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

# Create environment configuration (REQUIRED for security)
cp docs/env_template.txt .env
# The template already includes correct Neo4j credentials:
# NEO4J_USERNAME=neo4j and NEO4J_PASSWORD=ignition-graph
```

### 🔒 Security Configuration

**CRITICAL**: All sensitive information (credentials, IPs, certificates) must be stored in environment variables:

```bash
# Required environment variables in .env file
# Neo4j Graph Database (AI Assistant Memory)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=ignition-graph

# OPC-UA Configuration
OPCUA_SERVER_URL=opc.tcp://localhost:4840
OPCUA_USERNAME=admin
OPCUA_PASSWORD=your_password
```

🔐 **Never hardcode sensitive information in scripts - use environment variables with python-dotenv**

### Basic Usage

#### Web UI (Recommended for beginners)

```bash
# Launch the web interface
streamlit run src/ui/streamlit_app.py
```

Then open your browser to `http://localhost:8501` for a user-friendly interface.

📚 **For detailed UI usage instructions, see [docs/ui_readme.md](docs/ui_readme.md)**

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

# Version Control Intelligence
python -m src.core.enhanced_cli version status --detailed
python -m src.core.enhanced_cli version analyze-commit --files="src/core/enhanced_cli.py"
python -m src.core.enhanced_cli version predict-conflicts --source-branch="feature/new-feature"
python -m src.core.enhanced_cli version plan-release --version="v1.1.0" --strategy="incremental"

# Code Intelligence System
python -m src.core.enhanced_cli code-status --detailed
python -m src.core.enhanced_cli analyze-file src/ignition/code_intelligence/analyzer.py --detailed
python -m src.core.enhanced_cli search-code "CodeAnalyzer" --type class --limit 5
```

#### 🏭 OPC-UA Client Commands

```bash
# Launch OPC-UA web interface
python scripts/run_opcua_ui.py

# CLI OPC-UA commands
python -m src.core.opcua_cli connect --wizard  # Interactive setup
python -m src.core.opcua_cli connect --url opc.tcp://localhost:4840
python -m src.core.opcua_cli browse --node-id ns=2;s=MyDevice
python -m src.core.opcua_cli read --node-id ns=2;s=Temperature
python -m src.core.opcua_cli monitor --node-id ns=2;s=Temperature --interval 1000
python -m src.core.opcua_cli status  # Connection status
python -m src.core.opcua_cli info    # Server information
python -m src.core.opcua_cli disconnect
```

📚 **For comprehensive CLI usage instructions, see [docs/cli_readme.md](docs/cli_readme.md)**

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
├── src/                    # Core application source code
│   ├── ignition/          # Ignition SCADA integration modules
│   │   ├── code_intelligence/    # AI-enhanced code analysis (Phase 8)
│   │   │   ├── ai_assistant_enhancement.py  # AI assistant with context loading
│   │   │   ├── automated_refactoring.py     # Intelligent code refactoring
│   │   │   ├── vector_embeddings.py         # 384D semantic search
│   │   │   └── workflow/                    # Workflow integration
│   │   ├── modules/           # Ignition Module Development (Phase 9)
│   │   │   ├── core/         # Core module infrastructure (Phase 9.2)
│   │   │   │   ├── abstract_module.py       # AbstractIgnitionModule base class
│   │   │   │   ├── lifecycle.py             # Module lifecycle management
│   │   │   │   ├── config.py                # Configuration persistence
│   │   │   │   └── logging.py               # Diagnostics framework
│   │   │   ├── examples/     # Working module examples
│   │   │   ├── cli/          # Module CLI commands (19+ commands)
│   │   │   └── sdk_manager.py               # Module SDK integration
│   │   ├── graph/            # Neo4j Graph Database (10,389+ nodes)
│   │   │   ├── client.py     # Graph database client
│   │   │   ├── analytics/    # Advanced analytics engine
│   │   │   └── tasks/        # Function population tasks (424+ functions)
│   │   ├── opcua/            # Industrial OPC-UA Integration
│   │   │   ├── client.py     # Live OPC-UA client
│   │   │   ├── browser.py    # Address space navigation
│   │   │   └── gui/          # Industrial monitoring UI
│   │   ├── data_integration/ # Multi-database integration (7+ DB types)
│   │   ├── generators/       # Script generation engine
│   │   ├── exporters/        # Gateway export tools
│   │   ├── importers/        # Project import system
│   │   ├── validators/       # Script validation framework
│   │   ├── version_control/  # Git intelligence system
│   │   └── wrappers/         # System integration wrappers
│   ├── core/              # Core application logic
│   │   ├── cli/           # Enhanced CLI system (19+ commands)
│   │   └── backup_cli.py  # Database backup management
│   ├── ui/                # User interfaces
│   │   ├── app.py         # Streamlit web application
│   │   └── pages/         # Multi-page UI components
│   ├── api/               # External API integrations
│   └── models/            # Data models and schemas
├── templates/             # Jinja2 script templates
│   ├── gateway/          # Gateway script templates
│   ├── vision/           # Vision component templates
│   ├── perspective/      # Perspective script templates
│   ├── data_integration/ # Database integration templates
│   └── alarms/           # Alarm system templates
├── tests/                 # Comprehensive test suite
│   ├── test_cli.py       # CLI testing
│   ├── test_ui.py        # UI testing
│   └── test_performance.py # Performance benchmarks
├── scripts/               # Utility scripts and automation
│   ├── testing/          # Automated testing utilities
│   ├── utilities/        # Development utilities
│   └── setup_*.py        # Environment setup scripts
├── examples/              # Example configurations and demos
│   ├── gateway/          # Gateway script examples
│   ├── perspective/      # Perspective examples
│   └── new_agent_initialization.py # AI agent setup
├── docs/                  # Comprehensive documentation
│   ├── completion-summaries/     # Phase completion documentation
│   ├── api/              # API documentation
│   ├── development/      # Development guides
│   ├── deployment/       # Deployment patterns
│   ├── security/         # Security guidelines
│   └── roadmap.md        # Project roadmap and progress
├── neo4j/                 # Neo4j database configuration
├── mcp/                   # MCP server integration
├── config/                # Configuration files and examples
└── docker-compose.yml     # Development environment setup
```

## 📚 Documentation

### User Guides
- **[CLI Usage Guide](docs/cli_readme.md)** - Comprehensive guide to the enhanced CLI with learning system
- **[Web UI Guide](docs/ui_readme.md)** - Complete instructions for the Streamlit web interface
- **[OPC-UA Web Interface Guide](docs/opcua_ui_guide.md)** - Industrial OPC-UA monitoring and control interface
- **[Quick Start Tutorial](docs/streamlit_ui_guide.md)** - Getting started with the web interface

### Security & Configuration
- **[Environment Variables Guide](docs/environment_variables.md)** - Comprehensive security configuration with .env files
- **[Security Best Practices](docs/environment_variables.md#security-best-practices)** - Production security guidelines

### Technical Documentation
- **[AI Assistant Memory System](docs/ai_assistant_memory_system.md)** - Neo4j graph database integration
- **[Deployment Pattern Learning](docs/deployment/pattern-learning.md)** - ✅ AI-powered deployment intelligence system
- **[Version Control Intelligence](docs/VERSION_CONTROL_INTELLIGENCE_PLAN.md)** - ✅ Complete version control intelligence system
- **[Testing Framework](docs/testing_guide.md)** - Comprehensive testing approach and utilities
- **[Project Structure](docs/project_structure.md)** - Detailed codebase organization
- **[Enhanced Graph Functions](docs/enhanced_graph_functions_README.md)** - Ignition function database

### Development Resources
- **[Deployment Pattern Learning Completion](docs/DEPLOYMENT_PATTERN_LEARNING_COMPLETION.md)** - ✅ Latest major feature completion
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

### AI-Powered Deployment Intelligence

```bash
# Get deployment recommendations based on learned patterns
python -m src.core.enhanced_cli deploy recommendations -e production

# Get environment-specific adaptations
python -m src.core.enhanced_cli deploy adaptations -s staging -t production

# Get rollback scenarios for emergency situations
python -m src.core.enhanced_cli deploy rollback-scenarios -e production

# Analyze deployment performance and trends
python -m src.core.enhanced_cli deploy analytics -e production -d 30
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

## Neo4j MCP Integration

This project now includes robust support for Neo4j-backed Machine Control Programs (MCPs) for persistent memory and Cypher query assistance.

### Key MCP Services
- **neo4j-memory**: Provides persistent memory storage and retrieval using Neo4j.
- **neo4j-cypher**: Assists with Cypher query formatting, validation, and execution.

### Setup & Testing

1. **Setup**
   - Run the setup script to check Docker, Neo4j, environment variables, and install dependencies:
     ```bash
     python scripts/setup_neo4j_mcp.py
     ```
2. **Test**
   - Run the test script to verify Neo4j and MCP service connectivity:
     ```bash
     python scripts/test_neo4j_mcp_setup.py
     ```

### MCP Server Management
For details on starting, stopping, and configuring MCP servers, see [.cursor/README.md](.cursor/README.md).

### Security
- All sensitive credentials are managed via environment variables in your `.env` file (see `docs/env_template.txt`).
- Never commit `.env` to version control.
