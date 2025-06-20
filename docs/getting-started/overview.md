# Getting Started with IGN Scripts

Welcome to IGN Scripts! This guide will help you get up and running with our Jython script generation toolkit for Ignition SCADA systems.

## What is IGN Scripts?

IGN Scripts is a comprehensive toolkit for generating, testing, and managing Jython scripts for Ignition SCADA systems. It provides:

- **Script Generation**: Create Jython scripts for all Ignition contexts (Gateway, Vision, Perspective)
- **Template System**: Pre-built templates for common automation patterns
- **Graph Database**: 400+ Ignition system functions with intelligent relationships
- **OPC-UA Integration**: Live OPC-UA client with real-time monitoring
- **Gateway Connectivity**: Direct connection and testing with Ignition gateways
- **Learning System**: AI-powered recommendations based on usage patterns

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11 or higher** installed on your system
- **uv** (Python package installer) - for dependency management
- **Docker** (optional) - for development environment and testing
- **Ignition Gateway** (optional) - for testing generated scripts
- **Basic knowledge** of Ignition SCADA and Jython scripting

## Installation

### Option 1: Quick Setup (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/reh3376/ignition_tools.git
   cd ignition_tools
   ```

2. **Set up the environment**:
   ```bash
   # Create virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -r requirements.txt
   ```

3. **Configure environment variables** (for security):
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   nano .env  # or use your preferred editor
   ```

4. **Verify installation**:
   ```bash
   # Test CLI
   python -m src.main --help
   
   # Test web interface
   python -m src.ui.app
   ```

### Option 2: Development Setup

For contributors or advanced users who want the full development environment:

1. **Follow steps 1-3 from Quick Setup**

2. **Install development dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   pre-commit install
   ```

3. **Set up Docker environment** (optional):
   ```bash
   docker-compose up -d neo4j
   ```

4. **Run tests**:
   ```bash
   pytest tests/
   ```

## Initial Configuration

### Environment Variables

Create a `.env` file in the project root with your configuration:

```bash
# Gateway Connection (optional)
IGNITION_GATEWAY_URL=http://localhost:8088
IGNITION_USERNAME=admin
IGNITION_PASSWORD=password

# OPC-UA Configuration (optional)
OPCUA_SERVER_URL=opc.tcp://localhost:4840
OPCUA_USERNAME=opcuauser
OPCUA_PASSWORD=opcuapass

# Database Configuration (optional)
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=ignition-graph

# Security Settings
SSL_VERIFY=true
CERT_PATH=/path/to/certificates
```

### First Run Setup

1. **Initialize the graph database** (if using):
   ```bash
   # Note: Graph database initialization is handled automatically by the system
   # To check graph database status:
   python -m src.main learning stats
   ```

2. **Test gateway connection** (if configured):
   ```bash
   python -m src.main gateway test-connection
   ```

3. **Generate your first script**:
   ```bash
   python -m src.main script generate --template tag_read
   ```

## Your First Script

Let's generate a simple tag reading script to get familiar with the system.

### Using the CLI

```bash
# Generate a basic tag reading script
python -m src.main script generate \
  --template gateway/tag_change_script.jinja2 \
  --component-name "SpeedReader" \
  --output my_first_script.py
```

This creates a Jython script that reads a tag value with proper error handling.

### Using the Web Interface

1. **Start the web interface**:
   ```bash
   python -m src.ui.app
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Navigate to "Script Generator"**

4. **Fill in the form**:
   - Template: "Tag Read"
   - Context: "Gateway"
   - Tag Path: "[PLC]Production/Line1/Speed"

5. **Click "Generate Script"** and download the result

### Generated Script Example

Here's what a generated tag reading script looks like:

```python
"""
Generated Jython Script - Tag Read
Context: Gateway
Generated by: IGN Scripts v0.6.0
"""

from system.tag import readBlocking
from system.util import getLogger

# Configuration
TAG_PATH = "[PLC]Production/Line1/Speed"
DEFAULT_VALUE = 0.0

def read_tag_value():
    """Read tag value with error handling."""
    logger = getLogger("TagReader")
    
    try:
        # Read the tag
        result = readBlocking([TAG_PATH])[0]
        
        # Check quality
        if result.quality.isGood():
            logger.info("Successfully read tag %s: %s" % (TAG_PATH, result.value))
            return result.value
        else:
            logger.warn("Poor quality for tag %s: %s" % (TAG_PATH, result.quality))
            return DEFAULT_VALUE
            
    except Exception, e:
        logger.error("Failed to read tag %s: %s" % (TAG_PATH, str(e)))
        return DEFAULT_VALUE

# Execute the function
if __name__ == "__main__":
    value = read_tag_value()
    print "Tag value: %s" % value
```

## Key Features Tour

### 1. Graph Database Exploration

Explore the knowledge base of 400+ Ignition functions:

```bash
# View learning system status and function database
python -m src.main learning stats

# Explore usage patterns and function relationships
python -m src.main learning patterns

# Launch interactive pattern explorer
python -m src.main learning explore
```

### 2. Template Browser

Browse available templates through the web interface:

1. Open the web app (`python -m src.ui.app`)
2. Go to "Template Browser"
3. Filter by context (Gateway, Vision, Perspective)
4. Preview template code and parameters

### 3. OPC-UA Integration

Connect to live OPC-UA servers:

```bash
# Test OPC-UA connection
python -m src.main opcua connect --url "opc.tcp://localhost:4840"

# Browse server nodes
python -m src.main opcua browse --node "i=85"

# Monitor real-time data
python -m src.main opcua monitor "ns=2;i=1001" "ns=2;i=1002"
```

### 4. Gateway Integration

Test connectivity with Ignition gateways:

```bash
# Test gateway connection
python -m src.main gateway test-connection

# Get gateway info
python -m src.main gateway info

# Discover gateway endpoints
python -m src.main gateway discover
```

## Common Use Cases

### Use Case 1: Tag Event Scripts

Generate scripts that respond to tag value changes:

```bash
python -m src.main script generate \
  --template gateway/tag_change_script.jinja2 \
  --component-name "HighTemperatureAlarm" \
  --action-type "alarm"
```

### Use Case 2: Vision Button Handlers

Create button event handlers for Vision clients:

```bash
python -m src.main script generate \
  --template vision/button_click_handler.jinja2 \
  --component-name "StartProductionButton" \
  --action-type "tag_write"
```

### Use Case 3: Perspective View Scripts

Generate scripts for Perspective web interfaces:

```bash
python -m src.main script generate \
  --template perspective/components/button_handler.jinja2 \
  --component-name "DashboardNavigation" \
  --action-type "navigation"
```

### Use Case 4: Gateway Startup Scripts

Create initialization scripts for gateway startup:

```bash
python -m src.main script generate \
  --template gateway/startup_script.jinja2 \
  --component-name "SystemInitializer" \
  --action-type "startup"
```

## Learning and Improvement

The system learns from your usage patterns and provides intelligent recommendations:

### Usage Analytics

View your usage patterns:

1. **Web Interface**: Go to "Learning Analytics" page
2. **CLI**: `python -m src.main learning patterns`

### Smart Recommendations

Get recommendations based on your usage:

- **Function suggestions**: Based on what you've used before
- **Template recommendations**: Tailored to your common patterns
- **Parameter suggestions**: Smart defaults from similar scripts

## Best Practices

### 1. Start with Templates

- Always start with existing templates when possible
- Customize templates rather than writing from scratch
- Contribute new templates back to the community

### 2. Use Environment Variables

- Never hardcode credentials or sensitive information
- Use the `.env` file for configuration
- Follow the security guidelines in our documentation

### 3. Test Your Scripts

- Use the built-in testing framework
- Test scripts in development environment first
- Validate Jython syntax before deploying

### 4. Follow Coding Standards

- Review our [Coding Standards](../development/coding-standards.md)
- Use proper error handling and logging
- Document your scripts thoroughly

## Getting Help

### Documentation

- **Complete documentation**: Browse the `docs/` folder
- **API Reference**: See `docs/api/` for detailed API docs
- **Examples**: Check `examples/` for sample scripts

### Community Support

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Contributing**: See our [Contributing Guidelines](../contributing/guidelines.md)

### Common Issues

#### Installation Problems

**Problem**: `uv` command not found  
**Solution**: Install uv with `pip install uv`

**Problem**: Permission denied on virtual environment  
**Solution**: Use `sudo` or check file permissions

#### Configuration Issues

**Problem**: Gateway connection fails  
**Solution**: Check network connectivity and credentials in `.env`

**Problem**: OPC-UA connection timeout  
**Solution**: Verify server URL and firewall settings

#### Script Generation Issues

**Problem**: Template not found  
**Solution**: Check available templates with `python -m src.main template list`

**Problem**: Invalid Jython syntax  
**Solution**: Review generated script and check template parameters

## Next Steps

Now that you're set up, here are some suggested next steps:

1. **Explore Templates**: Browse all available templates in the web interface
2. **Generate Test Scripts**: Create a few scripts for your Ignition environment
3. **Connect to Your Gateway**: Configure and test your Ignition gateway connection
4. **Learn the Graph Database**: Explore the relationship between Ignition functions
5. **Try OPC-UA Integration**: Connect to an OPC-UA server and monitor real-time data
6. **Customize Templates**: Modify existing templates for your specific needs
7. **Contribute**: Share your templates and improvements with the community

## Advanced Topics

Once you're comfortable with the basics, explore these advanced features:

- **Custom Template Creation**: Build your own script templates
- **Graph Database Queries**: Write complex queries for function discovery
- **Performance Optimization**: Optimize script generation for large projects
- **Integration APIs**: Use IGN Scripts as a library in your own applications
- **Module Development**: Create custom Ignition modules using our SDK integration

---

**Congratulations!** You're now ready to start generating powerful Jython scripts for your Ignition SCADA systems. Happy scripting!

---

*Last updated: 2025-01-28* 