# IGN Scripts Web UI Guide

This guide covers how to use the IGN Scripts web interface built with Streamlit. The web UI provides all the functionality of the command-line interface in a user-friendly, graphical format.

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- All project dependencies installed (`pip install -r requirements.txt`)

### Launching the Web UI

#### Method 1: Using the Launch Script (Recommended)
```bash
python3 scripts/run_ui.py
```

#### Method 2: Direct Streamlit Command
```bash
streamlit run src/ui/streamlit_app.py
```

The web interface will automatically open in your default browser at `http://localhost:8501`.

## 📋 Interface Overview

The web UI is organized into six main sections accessible via the sidebar navigation:

### 🏠 Home
- **Overview**: Introduction to IGN Scripts and its capabilities
- **Quick Actions**: Direct navigation to main features
- **System Information**: Current configuration and statistics

### 📝 Script Generator
The core functionality with three generation methods:

#### From Template
- **Interactive Forms**: Guided input forms for each template type
- **Template Preview**: Live preview of the selected template
- **Advanced Options**: Configuration for logging, error handling, etc.
- **Instant Generation**: Generate scripts with real-time validation

#### From Configuration File
- **File Upload**: Drag-and-drop JSON configuration files
- **Configuration Preview**: View uploaded configuration structure
- **Batch Generation**: Generate multiple scripts from complex configurations

#### Quick Generate
- **Common Scenarios**: Pre-configured templates for frequent use cases
- **Minimal Input**: Generate scripts with just essential parameters
- **Rapid Prototyping**: Perfect for testing and development

### 📋 Templates
- **Template Browser**: View all available templates
- **Template Preview**: See template content and structure
- **Download Templates**: Export templates for modification
- **Template Information**: File size, path, and usage details

### ✅ Validation (Coming Soon)
- **Syntax Validation**: Check Jython 2.7 compatibility
- **API Validation**: Verify Ignition system function usage
- **Configuration Validation**: Validate configs against templates
- **Performance Analysis**: Identify optimization opportunities

### 📦 Export (Coming Soon)
- **Gateway Backup**: Export as .gwbk files
- **Project Archives**: Create deployment-ready packages
- **Version Control**: Prepare for git integration

### 📚 Documentation
- **Getting Started**: Setup and basic usage
- **Template System**: Understanding templates and variables
- **CLI Reference**: Command-line equivalent operations
- **Examples**: Code samples and use cases

## 🎯 Using the Script Generator

### Template-Based Generation

1. **Select Template**: Choose from available templates in the dropdown
2. **Configure Component**: Enter component name and basic settings
3. **Action-Specific Options**: 
   - **Navigation**: Target window and parameters
   - **Tag Write**: Tag path and value to write
   - **Popup**: Popup window and parameters
   - **Database**: SQL queries and parameters
   - **Custom**: Your own Jython code
4. **Advanced Options**: Configure logging, error handling, etc.
5. **Generate**: Click the generate button to create your script
6. **Download**: Save the generated script to your computer

### Configuration File Generation

1. **Prepare Configuration**: Create a JSON file with your script configuration
2. **Upload File**: Use the file uploader to select your configuration
3. **Preview**: Verify the configuration structure
4. **Generate**: Create the script from your configuration
5. **Download**: Save the generated script

#### Example Configuration File
```json
{
  "template": "vision/button_click_handler",
  "component_name": "MainMenuButton",
  "description": "Navigation button to main menu",
  "action_type": "navigation",
  "target_window": "MainMenu",
  "window_params": {
    "user_id": "{Root Container.CurrentUser.text}",
    "timestamp": "{Root Container.CurrentTime.text}"
  },
  "logging_enabled": true,
  "logger_name": "NavigationHandler"
}
```

### Quick Generation

1. **Select Script Type**: Choose from common scenarios
2. **Minimal Configuration**: Enter only essential parameters
3. **Instant Generation**: Scripts are generated with sensible defaults

## 📁 File Management

### Downloading Scripts
- Generated scripts can be downloaded directly from the interface
- Files are named automatically based on component names
- Scripts include proper Jython formatting and comments

### Configuration Files
- Upload JSON configuration files for batch processing
- Download example configurations for reference
- Validate configurations before generation

### Template Management
- Browse and preview all available templates
- Download templates for local modification
- View template structure and required variables

## 🔧 Advanced Features

### Session State
- The UI remembers your last generated script
- Configuration options persist during your session
- Quick access to recently used settings

### Real-time Validation
- Form inputs are validated as you type
- JSON configurations are validated on upload
- Clear error messages guide you to correct issues

### Responsive Design
- Works on desktop, tablet, and mobile devices
- Optimized for different screen sizes
- Accessible interface following web standards

## 🎨 Customization

### Theme
- The UI automatically adapts to your system theme
- Light and dark modes supported
- Consistent with Streamlit's design system

### Layout
- Wide layout optimizes screen space usage
- Collapsible sidebar for more workspace
- Multi-column layouts for complex forms

## ⚡ Tips and Best Practices

### Performance
- Large configuration files may take a moment to process
- Complex templates generate more comprehensive scripts
- Use Quick Generate for rapid prototyping

### Workflow
1. Start with Quick Generate to understand the basics
2. Use Template Generation for customized scripts
3. Move to Configuration Files for batch operations
4. Download and organize your generated scripts

### Organization
- Use descriptive component names for easy identification
- Group related scripts in folders
- Maintain configuration files for complex setups

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're running from the project root directory

#### Template Not Found
- Verify templates exist in the `templates/` directory
- Check template file permissions
- Ensure template syntax is valid Jinja2

#### Configuration Errors
- Validate JSON syntax in configuration files
- Check required fields are present
- Verify template-specific parameters

#### Generation Failures
- Check component names don't contain invalid characters
- Ensure all required fields are completed
- Review advanced options for conflicts

### Getting Help
- Use the built-in Documentation section
- Check the console for detailed error messages
- Review example configurations for reference

## 🔄 Updates and Maintenance

### Updating Templates
- New templates are automatically detected
- Restart the UI to refresh the template list
- Check the Templates page to verify new additions

### Configuration Changes
- Restart the application after modifying settings
- Clear browser cache if experiencing issues
- Check the console for configuration errors

## 🎓 Learning Resources

### Built-in Examples
- The UI includes comprehensive examples
- Each page has contextual help
- Download sample configurations to learn

### External Resources
- [Ignition User Manual](https://docs.inductiveautomation.com/)
- [Jython Documentation](https://jython.readthedocs.io/)
- [Ignition SDK Documentation](https://docs.inductiveautomation.com/display/SE/SDK+Documentation)

---

*This guide covers the current version of the IGN Scripts web UI. Features marked as "Coming Soon" are planned for future releases.* 