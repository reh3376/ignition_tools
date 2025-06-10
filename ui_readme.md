# IGN Scripts - Web UI Guide

**🌐 Intelligent Web Interface for Ignition Script Generation**

## 🚀 Overview

The IGN Scripts Web UI provides a modern, intuitive web interface for generating Jython scripts for Ignition SCADA systems. Built with Streamlit and integrated with the learning system, it offers smart recommendations, visual analytics, and an interactive development experience.

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Neo4j database (optional, for full learning features)
- Virtual environment (recommended)
- Modern web browser

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

# Start the web UI
streamlit run src/ui/streamlit_app.py
```

### Advanced Setup (with Learning System)
```bash
# Start Neo4j database
docker-compose up -d neo4j

# Start the web UI with learning system
streamlit run src/ui/streamlit_app.py

# Access at http://localhost:8501
```

## 🎯 Navigation Guide

### 🏠 Home Page
The landing page provides an overview of the system and quick access to key features.

#### Features:
- **System Status Dashboard**: Shows learning system connectivity and health
- **Quick Actions**: Direct links to common tasks
- **Recent Activity**: Overview of recent script generations and patterns
- **Getting Started Guide**: Interactive tutorials for new users

#### Smart Recommendations Section:
When learning system is connected, the home page displays:
- **Popular Templates**: Most frequently used templates
- **Recommended Actions**: Personalized suggestions based on usage patterns
- **Trending Patterns**: Currently popular function combinations

### 📝 Script Generator
The main script generation interface with intelligent assistance.

#### Basic Generation:
1. **Select Template**: Choose from available Jinja2 templates
2. **Configure Parameters**: Set component names, action types, and other options
3. **Preview**: See generated script before saving
4. **Download**: Save the script file locally

#### Smart Features:
- **Template Recommendations**: Suggestions based on usage patterns
- **Parameter Auto-completion**: Pre-populated common values
- **Success Rate Indicators**: Template reliability metrics
- **Context-Aware Help**: Tooltips and guidance based on selections

#### Step-by-Step Process:

##### 1. Template Selection
```
📋 Available Templates
┌─────────────────────────────────────┐
│ ✅ button_click_handler.jinja2      │ 92% success rate
│ ✅ window_opener.jinja2             │ 87% success rate
│ ✅ tag_writer.jinja2                │ 89% success rate
│ ⚠️  custom_action.jinja2            │ 65% success rate
└─────────────────────────────────────┘

💡 Recommendation: button_click_handler.jinja2 is popular for navigation tasks
```

##### 2. Parameter Configuration
Interactive form with smart defaults:
- **Component Name**: Auto-suggestions from similar projects
- **Action Type**: Dropdown with usage statistics
- **Target Parameters**: Context-sensitive options
- **Advanced Settings**: Expandable section for expert users

##### 3. Script Preview
```python
# Generated Jython Script for Ignition
# Template: button_click_handler.jinja2
# Generated: 2025-01-28 10:30:00

def action_performed(self, event):
    """Handle button click event for NavigateToMainButton"""

    try:
        # Navigate to target window
        system.nav.openWindow('MainMenu')

        # Log the action
        logger = system.util.getLogger("NavigateToMainButton")
        logger.info("Navigation to MainMenu completed successfully")

    except Exception as e:
        # Error handling
        logger.error("Navigation failed: %s" % str(e))
        system.gui.messageBox("Navigation failed. Please try again.")
```

##### 4. Download & Integration
- **Download Script**: Save as .py file
- **Copy to Clipboard**: For direct pasting
- **Gateway Export**: Export ready for Ignition gateway
- **Usage Tracking**: Automatically track generation for learning

### 📊 Learning Analytics
Comprehensive analytics dashboard for usage insights and system performance.

#### Analytics Tabs:

##### 📈 Usage Statistics
- **Script Generation Trends**: Daily/weekly/monthly generation counts
- **Template Popularity**: Usage rankings and success rates
- **User Activity**: Session statistics and engagement metrics
- **Performance Metrics**: Response times and error rates

##### 🔗 Pattern Analysis
- **Function Co-occurrence**: Interactive network graphs showing function relationships
- **Template Combinations**: Commonly used template sequences
- **Parameter Patterns**: Successful parameter combinations
- **Time-based Trends**: Usage patterns over time

##### 💡 Recommendations
- **Personal Recommendations**: Based on your usage history
- **Community Insights**: Popular choices among all users
- **Success Optimization**: Suggestions to improve script reliability
- **Workflow Improvements**: Process optimization recommendations

##### 📋 Template Insights
- **Template Performance**: Success rates and usage statistics
- **Parameter Analysis**: Common configurations for each template
- **Update Recommendations**: Suggestions for template improvements
- **Version Comparisons**: Performance across template versions

#### Interactive Visualizations:

##### Network Graph (Function Co-occurrence)
```
         system.tag.read
              |
         system.gui.messageBox ──── system.util.getLogger
              |                         |
         system.nav.openWindow ────── logger.info
```

##### Usage Heatmap
Shows activity patterns by time of day and day of week.

##### Success Rate Trends
Line charts showing template performance over time.

### 📋 Template Browser
Explore and manage available script templates.

#### Features:
- **Template Catalog**: Grid view of all available templates
- **Search & Filter**: Find templates by name, type, or functionality
- **Template Details**: View template source, parameters, and usage statistics
- **Usage Examples**: See example configurations and generated scripts
- **Template Ratings**: Community ratings and reviews

#### Template Categories:
- **Vision Components**: Traditional Ignition Vision templates
- **Perspective Components**: Modern Perspective templates
- **Gateway Scripts**: Server-side and startup scripts
- **Tag Scripts**: Value change and alarm scripts
- **Custom Templates**: User-created templates

#### Template Detail View:
```
📋 Template: button_click_handler.jinja2

📊 Statistics:
- Usage Count: 245 times
- Success Rate: 92.3%
- Average Generation Time: 0.8s
- Last Updated: 2025-01-15

⚙️ Parameters:
- component_name (required): Name of the button component
- action_type (optional): Type of action (navigation, popup, custom)
- target_window (conditional): Required when action_type=navigation
- logging_enabled (optional): Enable detailed logging (default: true)

💻 Source Preview:
def action_performed(self, event):
    """Handle button click event for {{ component_name }}"""
    try:
        {% if action_type == 'navigation' %}
        system.nav.openWindow('{{ target_window }}')
        {% endif %}

        {% if logging_enabled %}
        logger = system.util.getLogger("{{ component_name }}")
        logger.info("Action performed successfully")
        {% endif %}
    except Exception as e:
        system.gui.messageBox("Error: %s" % str(e))
```

#### Template Management Actions:
- **Preview Template**: See the template source and variables
- **Generate Example**: Create an example script with default parameters
- **Usage History**: View when and how the template was used
- **Export Template**: Download template file for external use

### 🔗 Gateway Connections
Comprehensive gateway management interface for connecting to Ignition gateways.

#### 📋 Gateway List Tab
Visual dashboard of all configured gateways.

##### Features:
- **Gateway Cards**: Visual representation of each gateway with key information
- **Status Indicators**: Real-time connection status with color-coded indicators
- **Quick Actions**: Test and health check buttons for immediate feedback
- **Configuration Overview**: SSL settings, authentication, and timeout information

##### Gateway Card Layout:
```
┌─ 🏢 Local Development ────────────────────────────┐
│ URL: http://localhost:8088                        │
│ Auth: basic (admin)                               │
│ SSL: ✗ | Timeout: 30s                           │
│ Local development gateway                         │
│ Tags: local, development                          │
│                                                   │
│ [🧪 Test]  [🏥 Health]                           │
└───────────────────────────────────────────────────┘
```

##### Setup Instructions:
For users with no configured gateways, the interface provides:
- **Quick Setup Guide**: Step-by-step configuration instructions
- **Example Configuration**: Copy-paste ready environment variables
- **Troubleshooting Links**: Common configuration issues and solutions

#### 🔌 Connection Test Tab
Interactive gateway testing with step-by-step feedback.

##### Features:
- **Gateway Selection**: Dropdown list of configured gateways
- **Progress Tracking**: Visual progress bar with status updates
- **Connection Details**: Comprehensive information about successful connections
- **Error Diagnostics**: Detailed error messages with troubleshooting suggestions

##### Test Process:
1. **Select Gateway**: Choose from configured gateways
2. **Initiate Test**: Click "Test Connection" button
3. **Progress Monitoring**: Watch real-time progress:
   ```
   ⏳ Creating client... [25%]
   ⏳ Connecting... [50%]
   ⏳ Getting gateway information... [75%]
   ✅ Connection successful! [100%]
   ```
4. **Results Display**: View connection results and gateway information

##### Success Results Display:
```
✅ Connection established successfully!

📊 Gateway Information
┌─────────────────┬──────────────────────────────────┐
│ Connection URL  │ http://localhost:8088            │
│ Platform        │ Ignition 8.1.44                 │
│ Server          │ Windows Server 2022              │
│ Status          │ RUNNING                          │
│ Redundancy      │ Independent/Good                 │
└─────────────────┴──────────────────────────────────┘

Raw Gateway Data:
{
  "ContextStatus": "RUNNING",
  "AddressInfo": "localhost:8088:8043",
  "RequireSsl": true,
  "Platform": "Ignition 8.1.44"
}
```

##### Error Handling:
When connections fail, the interface provides:
- **Error Classification**: Connection refused, SSL errors, authentication failures
- **Troubleshooting Tips**: Contextual suggestions based on error type
- **Next Steps**: Actionable recommendations for resolution

#### 🏥 Health Check Tab
Comprehensive health monitoring for single or multiple gateways.

##### Features:
- **Single Gateway Check**: Detailed health analysis for specific gateway
- **Multi-Gateway Check**: Batch health monitoring for all configured gateways
- **Health Metrics**: Connectivity, authentication, API access, and response time
- **Detailed Diagnostics**: Expandable sections with comprehensive check results

##### Health Check Options:
```
☐ Check all gateways
    OR
Select specific gateway: [Local Development ▼]

[🏥 Check Health]
```

##### Individual Health Results:
```
✅ Overall Status: HEALTHY
🕐 Timestamp: 2025-01-28T14:30:45.123Z

Detailed Health Checks:
✅ Connectivity
   Network connection successful

✅ Authentication
   Credentials validated

✅ API Access
   Gateway API responding

✅ Response Time (45ms)
   Excellent response time
```

##### Multi-Gateway Health Results:
```
✅ Local Development - Healthy
   • Connectivity: healthy
   • Authentication: healthy
   • API Access: healthy
   • Response Time: healthy 45ms

⚠️ Production Gateway - Warning
   • Connectivity: healthy
   • Authentication: healthy
   • API Access: warning High response time
   • Response Time: warning 2340ms

❌ Test Gateway - Unhealthy
   • Connectivity: failed Connection refused
   • Authentication: not_tested
   • API Access: not_tested
   • Response Time: not_tested
```

#### ⚙️ Configuration Tab
Interactive gateway configuration generator and validator.

##### Configuration Generator:
Interactive form for creating gateway configurations:
- **Gateway Details**: Name, host, port, and protocol settings
- **Authentication**: Username, password, and authentication type
- **Security Settings**: SSL verification and timeout configuration
- **Metadata**: Description and organizational tags
- **Generated Output**: Copy-paste ready environment variables

##### Form Layout:
```
Gateway Configuration Generator

Left Column:                Right Column:
┌─────────────────────┐    ┌─────────────────────┐
│ Gateway Name        │    │ Password            │
│ [my_gateway]        │    │ [••••••••]         │
│                     │    │                     │
│ Host                │    │ ☐ Use HTTPS         │
│ [localhost]         │    │                     │
│                     │    │ ☑ Verify SSL        │
│ Port                │    │                     │
│ [8088]              │    │ Timeout (seconds)   │
│                     │    │ [30]                │
│ Username            │    │                     │
│ [admin]             │    │                     │
└─────────────────────┘    └─────────────────────┘

Description (optional):
[Local development gateway for testing]

Tags (comma-separated):
[local, development, testing]

[📋 Generate Configuration]
```

##### Generated Configuration:
After form submission, displays:
```
✅ Configuration generated!

Copy this to your .env file:

# Gateway Configuration: my_gateway
IGN_GATEWAYS=my_gateway

# My Gateway Gateway Configuration
IGN_MY_GATEWAY_HOST=localhost
IGN_MY_GATEWAY_PORT=8088
IGN_MY_GATEWAY_HTTPS=false
IGN_MY_GATEWAY_USERNAME=admin
IGN_MY_GATEWAY_PASSWORD=password
IGN_MY_GATEWAY_AUTH_TYPE=basic
IGN_MY_GATEWAY_VERIFY_SSL=true
IGN_MY_GATEWAY_TIMEOUT=30
IGN_MY_GATEWAY_DESCRIPTION=Local development gateway for testing
IGN_MY_GATEWAY_TAGS=local,development,testing

[💾 Download .env Template]
```

##### Configuration Validator:
Tool to validate current environment configuration:
- **Environment Scanning**: Reads current .env file
- **Configuration Validation**: Checks for required variables
- **Gateway Detection**: Lists found gateway configurations
- **Error Reporting**: Identifies configuration issues

##### Validation Results:
```
[🔍 Check Environment Configuration]

✅ Found 2 configured gateway(s)

local_dev: http://localhost:8088
production: https://prod-gateway.company.com:8043

Configuration is valid and ready for use.
```

##### Configuration Security:
The interface emphasizes security best practices:
- **Password Masking**: Sensitive fields are properly masked
- **Security Warnings**: Alerts about SSL and credential management
- **Best Practice Tips**: Guidance on secure configuration
- **Environment Safety**: Reminders about .env file handling

### Gateway Integration Benefits

#### For Script Generation:
- **Target Gateway Selection**: Choose which gateway to optimize scripts for
- **Version Compatibility**: Generate scripts compatible with specific Ignition versions
- **Testing Integration**: Test generated scripts directly on connected gateways

#### For Template Development:
- **Real Gateway Testing**: Validate templates against actual Ignition environments
- **API Compatibility**: Ensure generated scripts work with gateway APIs
- **Performance Optimization**: Optimize scripts based on gateway performance characteristics

#### For Deployment:
- **Gateway Export**: Prepare scripts for direct gateway deployment
- **Environment Targeting**: Generate environment-specific configurations
- **Production Readiness**: Validate scripts meet production gateway requirements

## 🎨 UI Features

### Responsive Design
- **Mobile-Friendly**: Optimized for tablets and smartphones
- **Adaptive Layout**: Adjusts to different screen sizes
- **Touch Support**: Touch-friendly controls and navigation
- **Accessibility**: WCAG compliant with screen reader support

### Interactive Elements
- **Real-time Updates**: Live data refresh and notifications
- **Progressive Loading**: Efficient loading of large datasets
- **Contextual Help**: Inline help and tutorials
- **Keyboard Shortcuts**: Power user keyboard navigation

### Visual Feedback
- **Progress Indicators**: Clear feedback for long operations
- **Status Badges**: Visual indicators for system health
- **Color Coding**: Intuitive color schemes for different states
- **Animations**: Smooth transitions and micro-interactions

## 🔧 Advanced Features

### API Integration
The web UI connects to multiple backend services:

#### Learning System API
- **Pattern Analysis**: Real-time pattern discovery
- **Recommendation Engine**: Personalized suggestions
- **Usage Tracking**: Automatic behavior tracking
- **Analytics Queries**: Complex data analysis

#### Script Generator API
- **Template Rendering**: Jinja2 template processing
- **Validation Services**: Script syntax checking
- **Export Functions**: Multi-format script export
- **Batch Processing**: Bulk script generation

### Customization Options

#### Custom Templates
Create and manage your own templates:

1. **Template Editor**: Built-in editor with syntax highlighting
2. **Parameter Definition**: Define template parameters and validation
3. **Testing Environment**: Test templates before deployment
4. **Version Control**: Track template changes and versions

#### Dashboard Customization
Personalize your analytics dashboard:

1. **Widget Selection**: Choose relevant metrics and charts
2. **Layout Configuration**: Arrange widgets in preferred order
3. **Data Filtering**: Set default filters and time ranges
4. **Export Options**: Save dashboard configurations

### Integration Capabilities

#### Ignition Gateway Integration
- **Direct Export**: Push scripts directly to Ignition gateway
- **Project Integration**: Organize scripts by Ignition project
- **Resource Management**: Manage images, datasets, and other resources
- **Deployment Automation**: Automated deployment pipelines

#### Version Control Integration
- **Git Integration**: Connect to Git repositories
- **Change Tracking**: Track script modifications
- **Collaboration**: Team-based script development
- **Release Management**: Tag and release script versions

## 🚀 Getting Started

### First-Time Setup

#### 1. Launch the Application
```bash
streamlit run src/ui/streamlit_app.py
```

#### 2. System Check
- Verify learning system connection (green indicator)
- Check template availability (should show available templates)
- Test script generation (generate a simple script)

#### 3. Initial Configuration
- Set up user preferences in Settings
- Configure learning system if available
- Import any custom templates

### Quick Start Tutorial

#### Generate Your First Script
1. **Navigate to Script Generator** from the sidebar
2. **Select Template**: Choose "button_click_handler.jinja2"
3. **Set Parameters**:
   - Component Name: "MyTestButton"
   - Action Type: "navigation"
   - Target Window: "MainWindow"
4. **Generate**: Click "Generate Script" button
5. **Review**: Check the generated script in the preview
6. **Download**: Save the script file

#### Explore Analytics
1. **Go to Learning Analytics** page
2. **View Usage Statistics** to see system activity
3. **Check Pattern Analysis** for function relationships
4. **Get Recommendations** for your workflow

## 🔧 Troubleshooting

### Common Issues

#### Learning System Connection Failed
**Symptoms**: Red indicator, no recommendations, limited analytics
**Solutions**:
```bash
# Check Neo4j status
docker-compose ps neo4j

# Restart Neo4j
docker-compose restart neo4j

# Verify connection in settings page
```

#### Templates Not Loading
**Symptoms**: Empty template list, generation errors
**Solutions**:
```bash
# Check templates directory
ls templates/

# Verify template format
python -c "from jinja2 import Template; Template(open('templates/button_click_handler.jinja2').read())"

# Restart application
```

#### Slow Performance
**Symptoms**: Long loading times, UI freezes
**Solutions**:
- Clear browser cache
- Reduce analytics time range
- Restart the application
- Check system resources

#### Script Generation Errors
**Symptoms**: Generation fails, invalid scripts produced
**Solutions**:
- Verify all required parameters
- Check template syntax
- Review error messages in the log
- Try a different template

### Debug Mode
Enable debug mode for detailed logging:

```bash
# Set debug environment variable
export STREAMLIT_DEBUG=true

# Run with verbose logging
streamlit run src/ui/streamlit_app.py --logger.level=debug
```

### Performance Optimization

#### For Large Datasets
- Use date range filters in analytics
- Enable pagination for large tables
- Clear old cache data regularly
- Optimize database queries

#### For Slow Networks
- Enable offline mode where possible
- Use data compression
- Reduce real-time update frequency
- Cache frequently accessed data

## 📖 Usage Examples

### Example 1: Team Workflow
**Scenario**: Development team using shared templates

1. **Team Lead**: Creates custom templates, configures shared settings
2. **Developers**: Generate scripts using team templates
3. **Quality Assurance**: Reviews generated scripts and analytics
4. **Deployment**: Exports scripts to Ignition gateway

### Example 2: Learning Organization
**Scenario**: Improving development practices through analytics

1. **Baseline**: Review current usage patterns and success rates
2. **Analysis**: Identify common error patterns and inefficiencies
3. **Optimization**: Update templates based on insights
4. **Monitoring**: Track improvement in success rates and efficiency

### Example 3: Rapid Prototyping
**Scenario**: Quick script development for testing

1. **Template Selection**: Choose appropriate template for test case
2. **Quick Generation**: Use default parameters for rapid creation
3. **Testing**: Deploy to test environment
4. **Refinement**: Adjust parameters based on test results

## 🔄 Updates & Maintenance

### Automatic Updates
The system includes automatic update capabilities:

- **Template Updates**: New templates downloaded automatically
- **Pattern Updates**: Learning system patterns updated regularly
- **UI Improvements**: Interface enhancements deployed seamlessly
- **Security Patches**: Critical updates applied automatically

### Manual Maintenance
Regular maintenance tasks:

- **Cache Cleanup**: Clear old cached data monthly
- **Template Review**: Review and update custom templates quarterly
- **Usage Analysis**: Analyze usage patterns for optimization
- **Backup Creation**: Create system backups regularly

### Version Information
Check current version and updates:
- View version in Settings page
- Check for updates automatically
- Review changelog for new features
- Report issues through integrated feedback system

---

**🌐 Access**: The web UI is typically available at `http://localhost:8501`

**📞 Support**: For issues and questions, check the troubleshooting section or submit feedback through the UI

**🔄 Updates**: The system automatically tracks usage to improve recommendations and user experience
