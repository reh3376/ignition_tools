# Task 15: OPC-UA Client Integration Plan

## Overview
With Task 14's OPC-UA function definitions complete (14 system.opcua.* functions), we need to integrate **actual working OPC-UA client functionality** into our CLI and UI interfaces. This will transform our application from a script generator with OPC-UA schemas to a fully functional OPC-UA client for industrial automation.

## FreeOpcUa Libraries Analysis

### 1. opcua-asyncio (Primary Library)
- **Repository**: https://github.com/FreeOpcUa/opcua-asyncio
- **Package**: `asyncua` (pip install asyncua)
- **Status**: Actively maintained, latest v1.1.6 (Apr 2025)
- **Features**:
  - Async/await based OPC-UA client and server
  - Python 3.9+ support
  - Synchronous wrapper available
  - Extensive testing with industrial OPC-UA stacks
  - Command-line tools included
  - 95%+ test coverage
  - Industrial-grade reliability

### 2. opcua-client-gui (GUI Components)
- **Repository**: https://github.com/FreeOpcUa/opcua-client-gui
- **Package**: `opcua-client` (pip install opcua-client)
- **Features**:
  - PyQt5-based GUI client
  - Connection management with history
  - Node browsing with icons
  - Real-time data subscription
  - Event monitoring
  - Method calling
  - Certificate/encryption support
  - Value plotting capabilities

### 3. opcua-modeler (Model Creation)
- **Repository**: https://github.com/FreeOpcUa/opcua-modeler
- **Package**: `opcua-modeler` (pip install opcua-modeler)
- **Status**: Deprecated but functional
- **Note**: Author recommends code-based model creation with latest asyncua

## Integration Strategy

### Phase 1: Core OPC-UA Client Integration

#### 1.1 Add Dependencies
```txt
# OPC-UA Client Libraries
asyncua>=1.1.6
opcua-client>=0.8.4
```

#### 1.2 Create OPC-UA Module Structure
```
src/ignition/opcua/
├── __init__.py
├── client.py          # Main OPC-UA client wrapper
├── connection.py      # Connection management
├── subscription.py    # Data monitoring/subscriptions
├── browser.py         # Address space browsing
├── security.py        # Certificate/encryption handling
├── gui/
│   ├── __init__.py
│   ├── connection_dialog.py
│   ├── browser_widget.py
│   ├── monitor_widget.py
│   └── plot_widget.py
└── cli/
    ├── __init__.py
    ├── connect.py
    ├── browse.py
    ├── read.py
    ├── write.py
    ├── subscribe.py
    └── monitor.py
```

#### 1.3 CLI Integration
- **New CLI Commands**:
  ```bash
  ignition opcua connect --url opc.tcp://server:4840
  ignition opcua browse --path "0:Objects/2:DeviceSet"
  ignition opcua read --node "ns=2;i=1001"
  ignition opcua write --node "ns=2;i=1001" --value 42.5
  ignition opcua subscribe --node "ns=2;i=1001" --interval 1000
  ignition opcua monitor --config monitor_config.json
  ```

#### 1.4 UI Integration
- **New Streamlit Pages**:
  - OPC-UA Connection Manager
  - Live Data Browser
  - Real-time Monitoring Dashboard
  - Historical Data Viewer
  - Server Explorer

### Phase 2: Advanced Integration Features

#### 2.1 Integration with Existing Script Generation
- **Enhanced Script Templates**: Include actual OPC-UA client code
- **Live Data Binding**: Generate scripts that connect to real OPC-UA servers
- **Template Testing**: Test generated scripts against live OPC-UA servers

#### 2.2 Industrial Dashboard Creation
- **Real-time HMI**: Build Streamlit-based industrial dashboards
- **Alarm Management**: Handle OPC-UA alarms and events
- **Historical Trending**: Plot historical OPC-UA data
- **Multi-Server Support**: Connect to multiple OPC-UA servers

#### 2.3 Configuration Management
- **Connection Profiles**: Save/load OPC-UA server configurations
- **Security Certificates**: Manage OPC-UA certificates
- **Subscription Templates**: Reusable monitoring configurations

### Phase 3: Integration with Graph Database

#### 3.1 OPC-UA Server Discovery
- Store discovered OPC-UA servers in Neo4j
- Map server address spaces to graph database
- Track server availability and performance

#### 3.2 Live Data Integration
- Stream OPC-UA data to graph database
- Create relationships between OPC-UA nodes and Ignition functions
- Historical data analysis and pattern recognition

## Implementation Plan

### Task 15A: Core Dependencies and Structure
1. **Add OPC-UA Dependencies**
   - Update requirements.txt
   - Create opcua module structure
   - Basic client wrapper

2. **Basic CLI Commands**
   - Connection management
   - Simple read/write operations
   - Node browsing

3. **Connection Testing**
   - Test against demo OPC-UA servers
   - Error handling and connection management
   - Certificate support

### Task 15B: Advanced CLI Features
1. **Subscription Management**
   - Real-time data monitoring
   - Event subscription
   - Data logging

2. **Batch Operations**
   - Bulk read/write operations
   - Configuration-based monitoring
   - Export data to files

3. **Integration with Existing CLI**
   - Enhance script generation with OPC-UA
   - Live testing of generated scripts

### Task 15C: UI Integration
1. **Streamlit OPC-UA Pages**
   - Connection manager
   - Live data browser
   - Monitoring dashboard

2. **Data Visualization**
   - Real-time plots
   - Historical trends
   - Alarm displays

3. **Configuration Management**
   - Server profiles
   - Subscription templates
   - Export/import settings

### Task 15D: Advanced Features
1. **Industrial Dashboard**
   - Multi-server monitoring
   - Custom widget creation
   - Alarm management

2. **Graph Database Integration**
   - OPC-UA server mapping
   - Live data streaming
   - Pattern analysis

3. **Security and Certificates**
   - Certificate management
   - Encrypted connections
   - User authentication

## Technical Implementation Details

### Core OPC-UA Client Wrapper
```python
from asyncua import Client
import asyncio
from typing import Dict, List, Optional, Any

class IgnitionOPCUAClient:
    """Enhanced OPC-UA client wrapper for Ignition tools"""

    def __init__(self, url: str):
        self.url = url
        self.client = Client(url)
        self.connected = False

    async def connect(self, **kwargs):
        """Connect with enhanced error handling"""

    async def browse_tree(self, node_id: str = "i=85"):
        """Browse OPC-UA address space"""

    async def read_values(self, node_ids: List[str]):
        """Batch read multiple nodes"""

    async def subscribe_nodes(self, node_ids: List[str], callback):
        """Subscribe to multiple nodes with callback"""

    async def execute_method(self, object_id: str, method_id: str, args: List):
        """Execute OPC-UA method"""
```

### CLI Command Structure
```python
@click.group()
def opcua():
    """OPC-UA client commands"""
    pass

@opcua.command()
@click.option('--url', required=True, help='OPC-UA server URL')
@click.option('--username', help='Username for authentication')
@click.option('--password', help='Password for authentication')
@click.option('--certificate', help='Client certificate path')
def connect(url: str, username: str, password: str, certificate: str):
    """Connect to OPC-UA server"""

@opcua.command()
@click.option('--node', required=True, help='Node ID to read')
@click.option('--format', default='json', help='Output format')
def read(node: str, format: str):
    """Read OPC-UA node value"""
```

### Streamlit UI Components
```python
import streamlit as st
from src.ignition.opcua.client import IgnitionOPCUAClient

def opcua_connection_page():
    """OPC-UA connection management page"""
    st.title("OPC-UA Server Connection")

    # Connection form
    with st.form("connection_form"):
        url = st.text_input("Server URL", value="opc.tcp://localhost:4840")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.form_submit_button("Connect"):
            # Connection logic
            pass

def opcua_browser_page():
    """OPC-UA address space browser"""
    st.title("OPC-UA Address Space Browser")

    # Tree browser with real-time data
    if 'opcua_client' in st.session_state:
        # Display browseable tree
        pass

def opcua_monitor_page():
    """Real-time OPC-UA data monitoring"""
    st.title("OPC-UA Data Monitor")

    # Real-time charts and data tables
    if 'subscriptions' in st.session_state:
        # Display live data
        pass
```

## Benefits of Integration

### For Users
1. **Complete Industrial Solution**: Full OPC-UA client capabilities
2. **Real-time Monitoring**: Live data from industrial systems
3. **Script Validation**: Test generated scripts against real servers
4. **Industrial Dashboard**: Create HMIs and monitoring systems

### For Development
1. **Enhanced Script Generation**: Include working OPC-UA client code
2. **Live Testing**: Validate function definitions against real systems
3. **Industrial Use Cases**: Support real manufacturing scenarios
4. **Market Expansion**: Target industrial automation sector

### For Industrial Users
1. **PLC Integration**: Connect to Siemens, Rockwell, Schneider PLCs
2. **SCADA Connectivity**: Interface with industrial SCADA systems
3. **Data Historian**: Historical data analysis and trending
4. **Alarm Management**: Handle industrial alarms and events

## Success Metrics

1. **Successful Connections**: Connect to major OPC-UA servers (demo and industrial)
2. **Real-time Performance**: < 100ms response times for read operations
3. **Subscription Efficiency**: Handle 1000+ tag subscriptions
4. **Industrial Compatibility**: Test with major PLC brands
5. **User Adoption**: Positive feedback from industrial users

## Timeline

- **Week 1-2**: Task 15A - Core integration and basic CLI
- **Week 3-4**: Task 15B - Advanced CLI features and subscriptions
- **Week 5-6**: Task 15C - Streamlit UI integration
- **Week 7-8**: Task 15D - Advanced features and graph integration

## Conclusion

This integration will transform our Ignition script generation tool into a comprehensive industrial automation platform, providing real OPC-UA client capabilities that complement our existing script generation and AI-assisted memory system. The combination of script generation, live OPC-UA connectivity, and graph database intelligence will create a unique and powerful tool for industrial automation professionals.
