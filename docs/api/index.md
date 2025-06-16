# API Reference

This section provides comprehensive API documentation for the IGN Scripts project, covering all major components and their public interfaces.

## 📚 API Documentation Overview

The IGN Scripts API is organized into several key modules:

### Core APIs
- **[Script Generator](./script-generator.md)** - Generate Jython scripts from templates
- **[CLI Interface](./cli-interface.md)** - Command-line interface for all operations
- **[UI Interface](./ui-interface.md)** - Streamlit web application interface
- **[Template System](./template-system.md)** - Template management and pattern system

### Ignition Integration APIs
- **[OPC-UA Client](./opcua-client.md)** - OPC-UA server communication and data access
- **[Gateway Management](./gateway-management.md)** - Ignition Gateway connection and configuration
- **[System Functions](./system-functions.md)** - Available Ignition system functions

### Graph Database APIs
- **[Knowledge Graph](./knowledge-graph.md)** - AI assistant memory and pattern analysis
- **[Learning System](./learning-system.md)** - Usage tracking and recommendations
- **[Pattern Analysis](./pattern-analysis.md)** - Usage pattern detection and insights
- **[Streamlit Guide](./streamlit-guide.md)** - Streamlit UI components and integration

### Utility APIs
- **[Configuration Management](./configuration.md)** - Environment and connection configuration
- **[Security Management](./security.md)** - Certificate and authentication handling
- **[MCP Integration](./mcp-integration.md)** - Machine Control Program interfaces

## 🚀 Quick Start Examples

### Basic Script Generation
```python
from src.ignition.generators.script_generator import IgnitionScriptGenerator

# Initialize generator
generator = IgnitionScriptGenerator()

# Generate script from template
script = generator.generate_script(
    "vision/button_click_handler.jinja2",
    {
        "component_name": "StartButton",
        "action_type": "navigation",
        "target_window": "MainMenu"
    }
)
```

### OPC-UA Client Usage
```python
from src.ignition.opcua.client import OPCUAClientManager

# Initialize client with configuration
client = OPCUAClientManager()

# Connect to server
await client.connect("opc.tcp://localhost:4840")

# Browse nodes
nodes = await client.browse_nodes("Root/Objects")

# Read values
values = await client.read_values(["ns=2;i=2", "ns=2;i=3"])
```

### Graph Database Operations
```python
from src.ignition.graph.client import IgnitionGraphClient

# Initialize graph client
client = IgnitionGraphClient()

# Get function information
functions = client.get_functions_by_context("Gateway")

# Analyze usage patterns
patterns = client.get_usage_patterns("template_usage")
```

## 📖 API Conventions

### Return Types
- **Success responses**: Return data directly or wrapped in result objects
- **Error handling**: Raise specific exceptions with descriptive messages
- **Async operations**: Use `async`/`await` for I/O-bound operations

### Configuration
- All APIs use environment variables for configuration
- See [Configuration Guide](../configuration/index.md) for setup details
- Use `.env` files for sensitive credentials

### Authentication
- OPC-UA: Username/password or certificate-based
- Gateway: Basic auth or token-based
- Graph Database: Username/password authentication

## 📋 API Status

| Component | Status | Version | Documentation |
|-----------|--------|---------|---------------|
| Script Generator | ✅ Stable | 1.0 | Complete |
| OPC-UA Client | ✅ Stable | 1.0 | Complete |
| CLI Interface | ✅ Stable | 1.0 | Complete |
| Graph Database | ✅ Stable | 1.0 | Complete |
| Gateway Management | ✅ Stable | 1.0 | Complete |
| Template System | ✅ Stable | 1.0 | Complete |
| Learning System | ✅ Stable | 1.0 | Complete |
| MCP Integration | 🔄 Beta | 0.9 | In Progress |

## 🔗 Related Documentation

- [Getting Started Guide](../getting-started/overview.md)
- [Configuration Guide](../configuration/index.md)
- [Template Documentation](../templates/index.md)
- [Development Guidelines](../development/index.md)

## 📝 API Versioning

The IGN Scripts API follows semantic versioning:
- **Major version**: Breaking changes to public APIs
- **Minor version**: New features with backward compatibility
- **Patch version**: Bug fixes and improvements

Current API version: **1.0.x**

For version-specific documentation and migration guides, see the [Changelog](../development/changelog.md). 