# IGN Scripts - Enhanced CLI Guide

**🧠 Intelligent Ignition Script Generation with Learning System**

## 🚀 Overview

The IGN Scripts Enhanced CLI provides a beautiful, intelligent command-line interface for generating Jython scripts for Ignition SCADA systems. Powered by Rich and Textual libraries, it features smart recommendations, usage tracking, and interactive pattern exploration.

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Neo4j database (optional, for full learning features)
- Virtual environment (recommended)

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd IGN_scripts

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test the CLI
python -m src.core.enhanced_cli --help
```

### Advanced Setup (with Learning System)
```bash
# Start Neo4j database
docker-compose up -d neo4j

# Run setup command
python -m src.core.enhanced_cli setup

# Test learning system connection
python -m src.core.enhanced_cli learning stats
```

## 🎯 Command Reference

### Main Command Groups

#### 📝 Script Generation (`script`)
Generate Jython scripts from templates with smart recommendations.

#### 📋 Template Management (`template`) 
Browse, list, and get insights about available templates.

#### 🧠 Learning System (`learning`)
Explore usage patterns, get recommendations, and view analytics.

#### 🔗 Gateway Connections (`gateway`)
Manage connections to Ignition gateways for testing and deployment.

#### ⚙️ Setup (`setup`)
Configure the development environment and learning system.

## 🔗 Gateway Connection Commands

### `ign gateway list`
List all configured Ignition gateways.

```bash
# List all configured gateways
python -m src.core.enhanced_cli gateway list
```

#### Features
- **Gateway overview** with connection details
- **SSL and authentication information**
- **Tags and descriptions** for organization
- **Status indicators** for quick health assessment

#### Sample Output
```
🔗 Configured Gateways (2)

┌─ 🏢 local_dev ─────────────────────────────────────────┐
│ local_dev                                              │
│ URL: http://localhost:8088                             │
│ Auth: basic (admin)                                    │
│ SSL: ✗ | Timeout: 30s                                 │
│ Local development gateway                              │
│ Tags: local, development                               │
└────────────────────────────────────────────────────────┘

┌─ 🏢 production ────────────────────────────────────────┐
│ production                                             │
│ URL: https://prod-gateway.company.com:8043             │
│ Auth: basic (operator)                                 │
│ SSL: ✓ | Timeout: 30s                                 │
│ Production Ignition Gateway                            │
│ Tags: production, live                                 │
└────────────────────────────────────────────────────────┘
```

### `ign gateway connect`
Connect to an Ignition gateway and test the connection.

#### Basic Usage
```bash
# Connect to specific gateway
python -m src.core.enhanced_cli gateway connect --name local_dev

# Test connection only (no persistent connection)
python -m src.core.enhanced_cli gateway connect --name production --test

# Interactive selection from available gateways
python -m src.core.enhanced_cli gateway connect
```

#### Features
- **Interactive gateway selection** when no name specified
- **Connection testing** with detailed feedback
- **Gateway information retrieval** upon successful connection
- **Error diagnostics** with troubleshooting suggestions

#### Sample Output
```
🔌 Connecting to local_dev...
URL: http://localhost:8088

✓ Connection established

📊 Gateway Information:
┌─ Gateway Details ──────────────────────────────────────┐
│ • Connection Url: http://localhost:8088                │
│ • Platform: Ignition 8.1.44                           │
│ • Server: Windows Server 2022                         │
│ • Status: RUNNING                                      │
│ • Redundancy: Independent/Good                         │
└────────────────────────────────────────────────────────┘

✓ Gateway connection successful and ready for use
```

### `ign gateway health`
Check the health status of configured gateways.

#### Basic Usage
```bash
# Check specific gateway health
python -m src.core.enhanced_cli gateway health --name local_dev

# Check all gateways health
python -m src.core.enhanced_cli gateway health --all

# Interactive selection
python -m src.core.enhanced_cli gateway health
```

#### Health Checks Performed
- **Connectivity**: Basic network connection
- **Authentication**: Credential validation
- **API Access**: Gateway API availability
- **Response Time**: Performance metrics

#### Sample Output
```
🏥 Health Check - local_dev
URL: http://localhost:8088

✅ Overall Status: HEALTHY
Timestamp: 2025-01-28T14:30:45.123Z

Detailed Health Checks:
  ✅ Connectivity: Network connection successful
  ✅ Authentication: Credentials validated
  ✅ API Access: Gateway API responding
  ✅ Response Time: 45ms (45ms)
```

### `ign gateway test`
Run interactive gateway connection test.

```bash
# Launch interactive connection test
python -m src.core.enhanced_cli gateway test
```

#### Features
- **Interactive configuration** for new gateways
- **Step-by-step testing** with progress feedback
- **Configuration generation** for successful connections
- **Troubleshooting guidance** for failed connections

### `ign gateway discover`
Discover available endpoints on a gateway.

```bash
# Launch endpoint discovery tool
python -m src.core.enhanced_cli gateway discover
```

#### Features
- **Endpoint scanning** for available gateway APIs
- **Compatibility testing** with different Ignition versions
- **Working endpoint identification** for client optimization

## Gateway Configuration

Configure gateways using environment variables in a `.env` file:

### Configuration Format
```bash
# Gateway list
IGN_GATEWAYS=local_dev,production

# Local development gateway
IGN_LOCAL_DEV_HOST=localhost
IGN_LOCAL_DEV_PORT=8088
IGN_LOCAL_DEV_HTTPS=false
IGN_LOCAL_DEV_USERNAME=admin
IGN_LOCAL_DEV_PASSWORD=password
IGN_LOCAL_DEV_AUTH_TYPE=basic
IGN_LOCAL_DEV_VERIFY_SSL=true
IGN_LOCAL_DEV_TIMEOUT=30
IGN_LOCAL_DEV_DESCRIPTION=Local development gateway
IGN_LOCAL_DEV_TAGS=local,development

# Production gateway
IGN_PRODUCTION_HOST=prod-gateway.company.com
IGN_PRODUCTION_PORT=8043
IGN_PRODUCTION_HTTPS=true
IGN_PRODUCTION_USERNAME=operator
IGN_PRODUCTION_PASSWORD=secure_password
IGN_PRODUCTION_AUTH_TYPE=basic
IGN_PRODUCTION_VERIFY_SSL=true
IGN_PRODUCTION_TIMEOUT=30
IGN_PRODUCTION_DESCRIPTION=Production Ignition Gateway
IGN_PRODUCTION_TAGS=production,live
```

### Security Best Practices
- ✅ **Never commit** `.env` files to version control
- ✅ **Use strong passwords** for production gateways
- ✅ **Enable SSL verification** for production environments
- ✅ **Use dedicated service accounts** with minimal permissions
- ✅ **Regularly rotate passwords** for security

### Configuration Templates
Use the CLI to generate configuration templates:

```bash
# Run setup to get configuration guidance
python -m src.core.enhanced_cli setup
```

## 📝 Script Generation Commands

### `ign script generate`
Generate Jython scripts from templates with intelligent assistance.

#### Basic Usage
```bash
# Generate from template
python -m src.core.enhanced_cli script generate --template button_click_handler

# Interactive mode with recommendations
python -m src.core.enhanced_cli script generate -i --template button_click_handler

# Generate from configuration file
python -m src.core.enhanced_cli script generate --config config.json

# Save to specific file
python -m src.core.enhanced_cli script generate --template button_click_handler --output my_script.py
```

#### Advanced Options
```bash
# Complete example with all options
python -m src.core.enhanced_cli script generate \
  --template button_click_handler.jinja2 \
  --component-name "MainMenuButton" \
  --action-type navigation \
  --output scripts/menu_handler.py \
  --interactive
```

#### Parameters
- `--template, -t`: Template name to use
- `--config, -c`: Configuration file (JSON)
- `--output, -o`: Output file path
- `--component-name`: Name of the component
- `--action-type`: Type of action (navigation, tag_write, popup, database, custom)
- `--interactive, -i`: Interactive mode with recommendations

#### Interactive Mode Features
When using `--interactive` flag:
- **Smart recommendations** based on template usage patterns
- **Parameter suggestions** from successful configurations
- **Follow-up suggestions** for next steps
- **Template insights** showing success rates and common parameters

### `ign script validate`
Validate Jython scripts for Ignition compatibility.

```bash
# Validate a script file
python -m src.core.enhanced_cli script validate my_script.py
```

## 📋 Template Management Commands

### `ign template list`
List available script templates with optional usage statistics.

#### Basic Usage
```bash
# List all templates
python -m src.core.enhanced_cli template list

# Detailed view with usage statistics
python -m src.core.enhanced_cli template list --detailed
```

#### Features
- **Template categorization** (Vision, Perspective, Gateway)
- **Usage statistics** (when learning system is available)
- **Success rates** and last used dates
- **Popular template recommendations** based on community usage

#### Sample Output
```
📋 Available Templates
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Template                      ┃ Type        ┃ Usage Count ┃ Success Rate ┃ Last Used   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ button_click_handler.jinja2   │ Vision      │ 45          │ 92.3%        │ 2025-01-28  │
│ window_opener.jinja2          │ Vision      │ 23          │ 87.5%        │ 2025-01-27  │
└───────────────────────────────┴─────────────┴─────────────┴──────────────┴─────────────┘

🌟 Most Popular Templates
  1. button_click_handler.jinja2 (45 uses, 92.3% success)
  2. tag_writer.jinja2 (38 uses, 89.1% success)
  3. window_opener.jinja2 (23 uses, 87.5% success)
```

## 🧠 Learning System Commands

### `ign learning patterns`
Explore usage patterns and insights from the learning system.

#### Basic Usage
```bash
# Show all pattern types overview
python -m src.core.enhanced_cli learning patterns

# Show specific pattern type
python -m src.core.enhanced_cli learning patterns --pattern-type function_co_occurrence

# Analyze patterns from specific time range
python -m src.core.enhanced_cli learning patterns --days 7
```

#### Pattern Types
- **Function Co-occurrence**: Functions commonly used together
- **Template Usage**: Template popularity and success rates
- **Parameter Combinations**: Successful parameter patterns

#### Sample Output
```
📊 Pattern Analysis Overview

Pattern Counts by Type
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Pattern Type             ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Function Co Occurrence   │ 13    │
│ Template Usage           │ 12    │
│ Parameter Combination    │ 42    │
└──────────────────────────┴───────┘

📈 Confidence Distribution
  High Confidence: 34 ████████████████████
  Medium Confidence: 18 ████████████
  Low Confidence: 5 ███
```

### `ign learning recommend`
Get personalized command recommendations based on usage patterns.

```bash
# Get recommendations for specific command
python -m src.core.enhanced_cli learning recommend --command script.generate

# Get general recommendations
python -m src.core.enhanced_cli learning recommend
```

#### Sample Output
```
🎯 Recommendations for 'script.generate'

  1. template.list (confidence: 85.2%)
     Users often browse templates before generating scripts

  2. script.validate (confidence: 73.8%)
     Validation commonly follows script generation

  3. learning.patterns (confidence: 62.1%)
     Users explore patterns to improve their workflows
```

### `ign learning stats`
Show comprehensive learning system statistics and health.

```bash
python -m src.core.enhanced_cli learning stats
```

#### Features
- **Pattern distribution** by type and confidence
- **System health** metrics
- **Recent activity** summary
- **Performance statistics**

### `ign learning explore`
Launch interactive TUI for pattern exploration.

```bash
python -m src.core.enhanced_cli learning explore
```

#### TUI Features
- **Interactive tables** for different pattern types
- **Real-time filtering** and search
- **Pattern details** on selection
- **Export capabilities** for analysis

## ⚙️ Setup & Configuration

### `ign setup`
Set up the development environment and learning system.

```bash
python -m src.core.enhanced_cli setup
```

#### What it does:
- Tests learning system connection
- Validates database setup
- Provides setup instructions for missing components
- Configures optimal environment settings

## 🎨 CLI Features

### Beautiful Terminal UI
- **Rich formatting** with colors, panels, and tables
- **Progress indicators** for long-running operations
- **Syntax highlighting** for generated scripts
- **Interactive prompts** and confirmations

### Smart Recommendations
- **Context-aware suggestions** based on usage patterns
- **Template insights** showing success rates
- **Parameter recommendations** from successful combinations
- **Workflow optimization** suggestions

### Usage Tracking
- **Automatic tracking** of all CLI commands
- **Session management** for context preservation
- **Performance monitoring** and optimization
- **Privacy-focused** local data storage

### Learning Integration
- **Pattern analysis** from usage data
- **Recommendation engine** for improved workflows
- **Analytics dashboard** for insights
- **Continuous improvement** through machine learning

## 🔧 Troubleshooting

### Common Issues

#### Learning System Not Available
```bash
# Check database connection
python -m src.core.enhanced_cli learning stats

# Start Neo4j if needed
docker-compose up -d neo4j

# Run setup
python -m src.core.enhanced_cli setup
```

#### Template Not Found
```bash
# List available templates
python -m src.core.enhanced_cli template list

# Check template directory
ls templates/
```

#### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### Debug Mode
Add `--verbose` flag to any command for detailed output:
```bash
python -m src.core.enhanced_cli --verbose script generate --template button_click_handler
```

## 📖 Examples

### Complete Workflow Examples

#### Example 1: Generate Navigation Button
```bash
# Interactive generation with recommendations
python -m src.core.enhanced_cli script generate -i \
  --template button_click_handler \
  --component-name "NavigateToMainButton" \
  --action-type navigation

# Follow the interactive prompts
# Save the generated script
# Validate the result
python -m src.core.enhanced_cli script validate generated_script.py
```

#### Example 2: Explore Usage Patterns
```bash
# View learning system status
python -m src.core.enhanced_cli learning stats

# Explore co-occurrence patterns
python -m src.core.enhanced_cli learning patterns --pattern-type function_co_occurrence

# Get recommendations for next steps
python -m src.core.enhanced_cli learning recommend
```

#### Example 3: Template Discovery
```bash
# List templates with details
python -m src.core.enhanced_cli template list --detailed

# Get recommendations based on popular choices
python -m src.core.enhanced_cli learning recommend --command template.list
```

## 🚀 Advanced Usage

### Automation & Scripting
The CLI can be used in scripts and automation pipelines:

```bash
#!/bin/bash
# Automated script generation pipeline

# Generate multiple scripts
for component in "Button1" "Button2" "Button3"; do
  python -m src.core.enhanced_cli script generate \
    --template button_click_handler \
    --component-name "$component" \
    --action-type navigation \
    --output "scripts/${component,,}_handler.py"
done

# Validate all generated scripts
for script in scripts/*.py; do
  python -m src.core.enhanced_cli script validate "$script"
done
```

### Configuration Files
Use JSON configuration files for complex script generation:

```json
{
  "template": "button_click_handler.jinja2",
  "context": {
    "component_name": "MainMenuButton",
    "action_type": "navigation",
    "target_window": "MainMenu",
    "logging_enabled": true,
    "show_error_popup": true
  }
}
```

### Integration with IDEs
The CLI can be integrated with popular IDEs:

#### VS Code Tasks
Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate IGN Script",
      "type": "shell",
      "command": "python",
      "args": ["-m", "src.core.enhanced_cli", "script", "generate", "-i"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
```

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup development environment
git clone <repository-url>
cd IGN_scripts
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
pytest

# Run linting
ruff check src/
```

### Adding New Commands
1. Add command function to `src/core/enhanced_cli.py`
2. Include usage tracking with `enhanced_cli.track_cli_usage()`
3. Add recommendations if applicable
4. Update this documentation
5. Add tests

### Learning System Extensions
The learning system can be extended with new pattern types and recommendation algorithms. See `src/ignition/graph/` for implementation details.

---

**📞 Support**: For issues and questions, please check the troubleshooting section or create an issue in the repository.

**🔄 Updates**: The CLI automatically tracks usage to improve recommendations. Run `ign learning stats` to see system health and updates. 