# Template System Documentation

This section provides comprehensive documentation for the IGN Scripts template system, covering available templates, usage patterns, and customization guidelines.

## 📚 Template System Overview

The IGN Scripts template system uses Jinja2 templates to generate context-aware Jython scripts for Ignition SCADA systems. Templates are organized by Ignition context (Gateway, Vision, Perspective) and provide intelligent parameter validation and pattern recognition.

## 🎯 Available Template Categories

### Gateway Templates
Server-side scripts that run on the Ignition Gateway:

- **[Startup Scripts](./gateway/startup-scripts.md)** - System initialization and configuration
- **[Timer Scripts](./gateway/timer-scripts.md)** - Periodic data collection and processing  
- **[Tag Change Scripts](./gateway/tag-change-scripts.md)** - React to tag value changes
- **[Message Handlers](./gateway/message-handlers.md)** - Process system messages and events

### Vision Client Templates
Scripts for Vision client applications:

- **[Button Click Handlers](./vision/button-click-handlers.md)** - User interaction responses
- **[Window Management](./vision/window-management.md)** - Window opening, closing, navigation
- **[Data Binding Scripts](./vision/data-binding-scripts.md)** - Dynamic component updates
- **[Custom Components](./vision/custom-components.md)** - Reusable component behaviors

### Perspective Session Templates
Scripts for Perspective web-based sessions:

- **[Session Events](./perspective/session-events.md)** - Session lifecycle management
- **[Component Actions](./perspective/component-actions.md)** - Interactive component behaviors
- **[Navigation Scripts](./perspective/navigation-scripts.md)** - Page and view navigation
- **[Data Management](./perspective/data-management.md)** - Session data handling

### Specialized Templates
Advanced and specialized use cases:

- **[OPC-UA Integration](./specialized/opcua-integration.md)** - OPC-UA client operations
- **[Database Operations](./specialized/database-operations.md)** - SQL queries and transactions
- **[Alarm Management](./specialized/alarm-management.md)** - Alarm handling and notifications
- **[Report Generation](./specialized/report-generation.md)** - Automated report creation

## 🚀 Quick Start Guide

### 1. List Available Templates
```bash
# View all available templates
python -m src.main template list

# View detailed template information
python -m src.main template list --detailed
```

### 2. Generate Script from Template
```bash
# Basic script generation
python -m src.main script generate --template button_click_handler

# Interactive mode with recommendations
python -m src.main script generate -i --template button_click_handler

# Generate with custom parameters
python -m src.main script generate \
  --template button_click_handler \
  --component-name "StartButton" \
  --action-type "navigation"
```

### 3. Use Configuration File
```bash
# Generate from JSON configuration
python -m src.main script generate --config button_config.json
```

Configuration file example:
```json
{
  "template": "vision/button_click_handler",
  "component_name": "StartButton",
  "action_type": "navigation",
  "target_window": "MainMenu",
  "window_params": {
    "mode": "production",
    "user_level": "operator"
  }
}
```

## 📋 Template Structure

### Template Organization
```
templates/
├── gateway/                 # Gateway context templates
│   ├── startup_script.jinja2
│   ├── timer_script.jinja2
│   └── tag_change_script.jinja2
├── vision/                  # Vision client templates
│   ├── button_click_handler.jinja2
│   ├── popup_window_handler.jinja2
│   └── advanced_tag_write_handler.jinja2
├── perspective/             # Perspective session templates
│   ├── session_navigation.jinja2
│   ├── component_action.jinja2
│   └── data_update_handler.jinja2
└── specialized/             # Advanced templates
    ├── opcua_client.jinja2
    ├── database_query.jinja2
    └── alarm_handler.jinja2
```

### Template Metadata
Each template includes metadata for validation and recommendations:

```python
# Template: vision/button_click_handler.jinja2
{
    "name": "Vision Button Click Handler",
    "context": "Vision",
    "script_type": "ActionPerformed",
    "required_parameters": ["component_name"],
    "optional_parameters": ["action_type", "target_window", "target_tag"],
    "uses_functions": [
        "system.gui.openWindow",
        "system.tag.writeBlocking",
        "system.gui.messageBox"
    ],
    "validation_rules": {
        "action_type": ["navigation", "tag_write", "popup", "database"],
        "component_name": "^[A-Za-z][A-Za-z0-9_]*$"
    }
}
```

## 🔧 Template Usage Patterns

### Pattern Analysis
The system tracks template usage and identifies patterns:

```bash
# View template usage patterns
python -m src.main learning patterns --type template_usage

# Get recommendations for template
python -m src.main learning recommend --template button_click_handler
```

### Common Usage Patterns

#### Navigation Pattern
```json
{
  "pattern_type": "template_usage",
  "template_name": "button_click_handler",
  "common_parameters": {
    "action_type": {
      "frequency": 0.75,
      "common_values": {
        "navigation": 45,
        "tag_write": 25,
        "popup": 15
      }
    },
    "component_name": {
      "frequency": 1.0,
      "common_values": {
        "StartButton": 12,
        "StopButton": 10,
        "MenuButton": 8
      }
    }
  },
  "success_rate": 0.92,
  "usage_count": 156
}
```

## 🎨 Template Customization

### Creating Custom Templates

1. **Create Template File**
```jinja2
{# templates/custom/my_template.jinja2 #}
# {{ component_name }} - Custom Script
# Generated: {{ generation_timestamp }}
# Description: {{ description | default("Custom component script") }}

def {{ component_name | lower }}_action():
    """{{ description | default("Custom action implementation") }}"""
    
    {% if logging_enabled | default(true) %}
    logger = system.util.getLogger("{{ component_name }}")
    logger.info("Executing {{ component_name }} action")
    {% endif %}
    
    try:
        {% block main_logic %}
        # Custom logic here
        {{ custom_code | default("pass") }}
        {% endblock %}
        
        {% if success_message %}
        system.gui.messageBox("{{ success_message }}")
        {% endif %}
        
    except Exception as e:
        {% if error_handling | default(true) %}
        logger.error("Error in {{ component_name }}: %s" % str(e))
        system.gui.messageBox("Error: %s" % str(e), "Error")
        {% endif %}
```

2. **Add Template Metadata**
```python
# In template configuration
{
    "name": "Custom Template",
    "description": "Custom script template for specific use cases",
    "context": "Vision",
    "script_type": "ActionPerformed",
    "required_parameters": ["component_name"],
    "optional_parameters": ["description", "custom_code", "success_message"],
    "validation_rules": {
        "component_name": "^[A-Za-z][A-Za-z0-9_]*$"
    }
}
```

### Template Validation
```python
from src.ignition.generators.script_generator import IgnitionScriptGenerator

generator = IgnitionScriptGenerator()

# Validate template configuration
config = {
    "component_name": "MyButton",
    "action_type": "navigation",
    "target_window": "MainMenu"
}

errors = generator.validate_config(config, "button_click_handler.jinja2")
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

## 📊 Template Analytics

### Usage Statistics
Track and analyze template usage:

```bash
# View template usage statistics
python -m src.main template stats

# View specific template analytics
python -m src.main template stats --template button_click_handler

# Export usage data
python -m src.main template export --format json --output template_usage.json
```

### Performance Metrics
Monitor template performance:

| Template | Usage Count | Success Rate | Avg Generation Time | Last Used |
|----------|-------------|--------------|-------------------|-----------|
| button_click_handler | 156 | 92.3% | 0.15s | 2025-01-28 |
| tag_change_script | 89 | 96.6% | 0.12s | 2025-01-27 |
| popup_window_handler | 67 | 88.1% | 0.18s | 2025-01-28 |
| timer_script | 45 | 97.8% | 0.10s | 2025-01-26 |

## 🛠️ Advanced Features

### Template Inheritance
```jinja2
{# Base template: templates/base/component_base.jinja2 #}
{% extends "base/component_base.jinja2" %}

{% block imports %}
{{ super() }}
from com.inductiveautomation.ignition.common.util import LogUtil
{% endblock %}

{% block main_logic %}
# Specific implementation
{% endblock %}
```

### Conditional Logic
```jinja2
{# Context-aware template generation #}
{% if context == "Gateway" %}
# Gateway-specific imports
import system.util
{% elif context == "Vision" %}
# Vision-specific imports
import system.gui
{% elif context == "Perspective" %}
# Perspective-specific imports
import system.perspective
{% endif %}
```

### Dynamic Parameters
```jinja2
{# Dynamic parameter handling #}
{% for param_name, param_value in dynamic_params.items() %}
{{ param_name }} = {{ param_value | tojson }}
{% endfor %}
```

## 📖 Best Practices

### Template Design Guidelines
1. **Use descriptive names** for templates and parameters
2. **Include comprehensive documentation** in template comments
3. **Provide sensible defaults** for optional parameters
4. **Implement proper error handling** in generated scripts
5. **Follow Ignition coding standards** for consistency

### Parameter Validation
1. **Validate required parameters** before generation
2. **Use regular expressions** for format validation
3. **Provide clear error messages** for validation failures
4. **Document parameter requirements** in template metadata

### Performance Optimization
1. **Minimize template complexity** for faster generation
2. **Cache frequently used templates** for better performance
3. **Use template inheritance** to reduce duplication
4. **Profile template generation** to identify bottlenecks

## 🔗 Related Documentation

- [Script Generator API](../api/script-generator.md)
- [CLI Interface Documentation](../api/cli-interface.md)
- [Pattern Analysis Guide](../api/pattern-analysis.md)
- [Development Guidelines](../development/index.md)
- [Configuration Guide](../configuration/index.md)

## 🚨 Common Issues

### Template Not Found
```bash
# Error: Template not found
FileNotFoundError: Template 'my_template.jinja2' not found

# Solution: Check template name and location
python -m src.main template list | grep my_template
```

### Parameter Validation Failed
```bash
# Error: Required parameter missing
ValueError: 'component_name' is required

# Solution: Provide required parameters
python -m src.main script generate --template button_click_handler --component-name "MyButton"
```

### Generation Failed
```bash
# Error: Template generation failed
TemplateError: undefined variable 'action_type'

# Solution: Check template requirements
python -m src.main template info --template button_click_handler
```

## 📞 Support

For template assistance:
1. Check [Common Issues](#-common-issues) above
2. Use `python -m src.main template list --detailed` for template information
3. Review [Template Analytics](#-template-analytics) for usage patterns
4. Refer to specific template documentation for detailed guidance 