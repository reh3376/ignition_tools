# OPC-UA Web Interface Guide

This guide provides comprehensive instructions for using the IGN Scripts OPC-UA web interface - a powerful Streamlit-based application for industrial automation monitoring and control.

## 🚀 Quick Start

### Prerequisites

1. Python 3.11+ with virtual environment activated
2. All dependencies installed (`uv pip install -r requirements.txt`)
3. Environment variables configured (see [Environment Variables Guide](environment_variables.md))

### Launch the Interface

```bash
# Method 1: Using the launch script (recommended)
python scripts/run_opcua_ui.py

# Method 2: Direct Streamlit launch
streamlit run src/ignition/opcua/gui/opcua_ui.py --server.port 8501
```

The interface will be available at `http://localhost:8501`

## 📋 Interface Overview

The OPC-UA web interface consists of 5 main sections:

1. **🔌 Connection Management** - Server connection and authentication
2. **🔍 Node Browser** - Real-time server address space exploration
3. **📊 Real-time Monitoring** - Live data monitoring and visualization
4. **⚙️ Configuration Management** - Save/load connection configurations
5. **🔒 Security Management** - Certificate and security configuration

## 🔌 Connection Management

### Server Connection

1. **Server URL**: Enter your OPC-UA server endpoint
   - Format: `opc.tcp://hostname:port`
   - Example: `opc.tcp://localhost:4840`

2. **Authentication**: Choose authentication method
   - **Anonymous**: No credentials required
   - **Username/Password**: Basic authentication
   - **Certificate**: X.509 certificate-based authentication

3. **Security Configuration**:
   - **Security Policy**: Choose from None, Basic256Sha256, etc.
   - **Security Mode**: None, Sign, SignAndEncrypt
   - **Certificate Path**: Path to client certificate file

### Connection Process

1. Fill in server details
2. Configure security settings
3. Click **Connect to Server**
4. Monitor connection status in the sidebar

## 🔍 Node Browser

### Features

- **Real-time Browsing**: Live exploration of server address space
- **Node Information**: Detailed node attributes and properties
- **Tree Navigation**: Hierarchical view of server structure
- **Search Functionality**: Find nodes by name or identifier

### Usage

1. **Ensure Connection**: Must be connected to browse nodes
2. **Select Root Node**: Choose starting point for browsing
3. **Expand Nodes**: Click to explore child nodes
4. **View Details**: Select nodes to see detailed information

### Node Information Display

For each node, the interface shows:
- **Node ID**: Unique identifier
- **Display Name**: Human-readable name
- **Node Class**: Object, Variable, Method, etc.
- **Data Type**: For variable nodes
- **Access Level**: Read/Write permissions
- **Description**: Node description if available

## 📊 Real-time Monitoring

### Setup Monitoring

1. **Add Nodes**: Select nodes from the browser
2. **Configure Interval**: Set monitoring update frequency (100ms - 10s)
3. **Start Monitoring**: Begin real-time data collection
4. **View Data**: Monitor live values and timestamps

### Monitoring Features

- **Live Values**: Real-time data updates
- **Timestamps**: Server and source timestamps
- **Status Codes**: Quality indicators for each reading
- **Historical View**: Recent value history
- **Export Data**: Download monitoring data as CSV

### Visualization Options

- **Table View**: Tabular display of current values
- **Chart View**: Time-series graphs for numeric data
- **Status Indicators**: Quality and connection status
- **Alerts**: Notifications for value changes or errors

## ⚙️ Configuration Management

### Save Configurations

1. **Create Profile**: Set up connection parameters
2. **Name Profile**: Give it a descriptive name
3. **Save Configuration**: Store for future use
4. **Manage Profiles**: Edit or delete existing profiles

### Load Configurations

1. **Select Profile**: Choose from saved configurations
2. **Load Settings**: Apply configuration to current session
3. **Quick Connect**: One-click connection setup

### Configuration Profiles

Profiles store:
- Server connection details
- Authentication credentials
- Security settings
- Certificate paths
- Monitoring preferences

## 🔒 Security Management

### Certificate Management

1. **Generate Certificates**: Create client certificates
2. **View Certificates**: Inspect certificate details
3. **Trust Certificates**: Manage server certificate trust
4. **Certificate Status**: Monitor certificate validity

### Security Features

- **Certificate Generation**: Automated client certificate creation
- **Trust Store Management**: Handle server certificate validation
- **Security Policy Selection**: Choose appropriate security levels
- **Encrypted Communication**: Secure data transmission

## 🛠️ Advanced Features

### Configuration Wizard

Interactive setup assistant for first-time users:

1. **Server Discovery**: Automatic server endpoint detection
2. **Security Setup**: Guided certificate configuration
3. **Test Connection**: Verify settings before saving
4. **Profile Creation**: Save configuration for reuse

### Monitoring Dashboard

Real-time industrial dashboard with:

- **Multiple Node Monitoring**: Track multiple values simultaneously
- **Customizable Intervals**: From 100ms to 10 seconds
- **Data Logging**: Automatic data collection and storage
- **Export Functions**: CSV and JSON data export

### Error Handling

Comprehensive error management:

- **Connection Errors**: Clear error messages and resolution steps
- **Certificate Issues**: Automated certificate validation and repair
- **Server Errors**: Detailed error codes and descriptions
- **Recovery Options**: Automatic reconnection and retry logic

## 📱 User Experience Features

### Responsive Design

- **Desktop Optimized**: Full-featured desktop experience
- **Tablet Compatible**: Touch-friendly interface
- **Mobile Responsive**: Essential features on mobile devices

### Accessibility

- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Compatible with assistive technologies
- **High Contrast Mode**: Improved visibility options
- **Font Scaling**: Adjustable text sizes

## 🔧 Troubleshooting

### Common Issues

1. **Connection Failures**
   - Verify server URL and port
   - Check network connectivity
   - Validate credentials
   - Review security settings

2. **Certificate Errors**
   - Generate new client certificates
   - Trust server certificates
   - Check certificate paths
   - Verify certificate validity

3. **Performance Issues**
   - Reduce monitoring interval
   - Limit number of monitored nodes
   - Check network bandwidth
   - Monitor system resources

### Debug Features

- **Connection Logs**: Detailed connection attempt logs
- **Error Messages**: Clear error descriptions with solutions
- **Status Indicators**: Visual connection and security status
- **Debug Mode**: Enhanced logging for troubleshooting

## 📊 Monitoring Best Practices

### Performance Optimization

1. **Appropriate Intervals**: Don't monitor faster than necessary
2. **Selective Monitoring**: Monitor only required nodes
3. **Batch Operations**: Group related nodes together
4. **Resource Management**: Monitor system resources

### Security Best Practices

1. **Use Encryption**: Always use SignAndEncrypt in production
2. **Certificate Validation**: Validate all server certificates
3. **Credential Management**: Use strong passwords and rotate regularly
4. **Network Security**: Use VPNs for remote connections

## 🎯 Use Cases

### Industrial Monitoring

- **Process Variables**: Monitor temperature, pressure, flow rates
- **Equipment Status**: Track machine states and alarms
- **Production Metrics**: Monitor cycle times and throughput
- **Quality Data**: Track product quality measurements

### System Integration

- **SCADA Integration**: Connect to Ignition Gateway servers
- **PLC Communication**: Direct PLC data access
- **Historian Integration**: Historical data collection
- **Dashboard Creation**: Real-time operational dashboards

### Development and Testing

- **Server Testing**: Validate OPC-UA server implementations
- **Client Development**: Test OPC-UA client applications
- **Security Testing**: Verify security configuration
- **Performance Testing**: Monitor connection performance

## 🔄 Updates and Maintenance

### Regular Maintenance

1. **Certificate Renewal**: Monitor certificate expiration
2. **Software Updates**: Keep dependencies current
3. **Security Reviews**: Regular security audits
4. **Performance Monitoring**: Track system performance

### Configuration Backup

- **Export Profiles**: Regular backup of configuration profiles
- **Version Control**: Track configuration changes
- **Documentation**: Maintain configuration documentation
- **Recovery Plans**: Document recovery procedures

This guide provides comprehensive coverage of the OPC-UA web interface. For additional support or advanced configuration, refer to the [OPC-UA Integration Plan](TASK_15_OPC_UA_INTEGRATION_PLAN.md) or the [Environment Variables Guide](environment_variables.md).
