# Project Structure

This document outlines the organization of the IGN Scripts project after cleanup and reorganization.

## Root Directory Structure

```
IGN_scripts/
├── .github/                    # GitHub Actions workflows
│   └── workflows/
├── config/                     # Configuration files
├── docs/                       # Documentation
│   ├── ignition/              # Ignition-specific documentation
│   ├── ai_assistant_memory_system.md  # 🤖 AI Assistant Graph DB Guide
│   └── *.md                   # Project documentation
├── examples/                   # Example configurations
│   ├── gateway/               # Gateway script examples
│   ├── vision/                # Vision Client script examples
│   └── perspective/           # Perspective Session script examples
├── scripts/                    # Utility and development scripts
│   ├── testing/               # Test-related scripts
│   ├── utilities/             # Development utility scripts
│   ├── test_specific_gateway.py      # Interactive gateway testing
│   ├── test_ignition_endpoints.py    # Gateway endpoint discovery
│   └── test_final_connection.py      # Comprehensive connection validation
├── src/                        # Main source code
│   ├── api/                   # API modules
│   ├── core/                  # Core functionality
│   │   └── enhanced_cli.py    # Enhanced CLI with gateway commands
│   ├── ignition/              # Ignition-specific modules
│   │   ├── gateway/           # 🔗 Gateway connection system
│   │   │   ├── __init__.py    # Gateway module exports
│   │   │   ├── config.py      # Gateway configuration management
│   │   │   └── client.py      # Gateway client and connection pool
│   │   ├── generators/        # Script generation modules
│   │   ├── graph/            # Learning system and graph database
│   │   └── templates/        # Template processing
│   ├── models/                # Data models
│   └── ui/                    # User interface modules
│       └── streamlit_app.py   # Web UI with gateway management
├── templates/                  # Jinja2 templates for script generation
│   ├── gateway/               # Gateway scope templates
│   ├── perspective/           # Perspective Session templates
│   └── vision/                # Vision Client templates
├── tests/                      # Test suite
├── coverage-reports/           # Test coverage reports
├── logs/                       # Application logs
├── test-results/              # Test result files
├── gateway_config.env         # 🔧 Gateway configuration template
├── .env.template              # Environment configuration template
└── .env                       # Local environment (git-ignored)
```

## Key Directories

### `/src` - Main Source Code
- **`core/`**: Core functionality including enhanced CLI interface with gateway management
- **`ignition/`**: Ignition-specific modules (generators, validators, exporters, gateway connections)
  - **`gateway/`**: Gateway connection system with configuration management and HTTP/HTTPS clients
- **`api/`**: API endpoints and handlers
- **`models/`**: Data models and schemas
- **`ui/`**: User interface components including web UI with gateway management

### `/src/ignition/gateway` - Gateway Connection System
New module providing comprehensive Ignition gateway connectivity:
- **`config.py`**: Gateway configuration management with environment variable support
- **`client.py`**: HTTP/HTTPS gateway client with authentication and health monitoring
- **Connection features**: Multi-gateway support, SSL configuration, health checks, connection pooling

### `/templates` - Script Templates
Organized by Ignition context for easy navigation:
- **`gateway/`**: Server-side scripts (startup, timer, tag change)
- **`vision/`**: Client-side Vision scripts (popup handlers, tag operations)
- **`perspective/`**: Session-specific Perspective scripts (navigation, etc.)

### `/examples` - Configuration Examples
Mirrors the template structure with example JSON configurations:
- **`gateway/`**: Gateway script configuration examples
- **`vision/`**: Vision script configuration examples
- **`perspective/`**: Perspective script configuration examples

### `/scripts` - Development Scripts
Organized by purpose with new gateway testing utilities:
- **`testing/`**: Test runners and validation scripts
- **`utilities/`**: Development utilities (log monitoring, UI runners)
- **Gateway testing**: Interactive gateway connection, endpoint discovery, and validation scripts

### `/docs` - Documentation
- **`ignition/`**: Ignition-specific documentation and references
- Project documentation files (README, testing guides, CLI/UI documentation)

## Configuration Management

### Gateway Configuration
- **`gateway_config.env`**: Template for gateway environment variables
- **`.env`**: Local environment configuration (git-ignored for security)
- **Environment pattern**: `IGN_{GATEWAY_NAME}_{PROPERTY}` for multi-gateway support

### Security Features
- Environment-based credential management
- SSL verification controls for dev/prod environments
- Password masking in outputs and UI
- Git-ignored sensitive configuration files

## File Organization Principles

1. **Context-Based Organization**: Templates and examples are organized by Ignition context (Gateway, Vision, Perspective)
2. **Purpose-Based Grouping**: Scripts are grouped by their purpose (testing vs utilities)
3. **Standard Python Package Structure**: All directories include `__init__.py` files for proper package imports
4. **Clean Separation**: Source code, templates, examples, and utilities are clearly separated
5. **Security-First**: Sensitive configuration separated from code with git-ignore protection

## New Features Added (v0.5.x)

### 🔗 Gateway Connection System
1. ✅ **HTTP/HTTPS Gateway Client** with authentication support
2. ✅ **Multi-Gateway Configuration** management via environment variables  
3. ✅ **Health Monitoring** with comprehensive diagnostics
4. ✅ **Connection Pooling** for efficient multi-gateway management
5. ✅ **Enhanced CLI Commands** (`ign gateway list|connect|health|test|discover`)
6. ✅ **Web UI Integration** with gateway management interface
7. ✅ **Security Features** (SSL verification, credential masking, environment-based config)

### 🛡️ Security Enhancements
1. ✅ **Environment-based configuration** (no hardcoded credentials)
2. ✅ **SSL verification controls** for different environments
3. ✅ **Credential masking** in all outputs
4. ✅ **Git-ignored sensitive files** (.env, credential files)

## Cleanup Actions Performed

1. ✅ Removed all `.DS_Store` files
2. ✅ Removed empty template directories (`alarms/`, `tags/`)
3. ✅ Organized scripts into `testing/` and `utilities/` subdirectories
4. ✅ Organized examples by Ignition context
5. ✅ Added `__init__.py` files for proper package structure
6. ✅ Cleaned up `__pycache__` directories
7. ✅ Updated documentation references to reflect new structure
8. ✅ **Removed production gateway credentials** from all test scripts
9. ✅ **Added gateway connection system** with secure configuration management
10. ✅ **Integrated gateway functionality** into CLI and Web UI

This organization provides a clean, logical structure that scales well as the project grows and makes it easy for developers to find relevant files. The new gateway connection system adds enterprise-grade Ignition gateway management while maintaining security best practices.
