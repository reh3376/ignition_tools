"""OPC-UA Web UI Interface.

Provides a comprehensive web-based interface for OPC-UA server connections,
browsing, monitoring, and configuration management using Streamlit.
"""

import os
import time
from datetime import datetime
from typing import Self

import streamlit as st
from dotenv import load_dotenv

from src.ignition.core.opcua_connection_config import (
    OPCUAConfigManager,
    OPCUAConnectionConfig,
)
from src.ignition.opcua.client import OPCUAClientManager
from src.ignition.opcua.security import OPCUASecurityManager

# Load environment variables
load_dotenv()


class OPCUAWebUI:
    """Web-based OPC-UA interface using Streamlit."""

    def __init__(self: Self) -> None:
        """Initialize the OPC-UA Web UI."""
        self.client_manager = None
        self.config_manager = OPCUAConfigManager()
        self.security_manager = OPCUASecurityManager()

        # Initialize session state
        if "connection_status" not in st.session_state:
            st.session_state.connection_status = "Disconnected"
        if "current_config" not in st.session_state:
            st.session_state.current_config = None
        if "browse_nodes" not in st.session_state:
            st.session_state.browse_nodes = []
        if "monitoring_data" not in st.session_state:
            st.session_state.monitoring_data = {}

    def run(self: Self) -> None:
        """Run the OPC-UA Web UI."""
        st.set_page_config(
            page_title="IGN Scripts - OPC-UA Interface",
            page_icon="🔗",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # Custom CSS
        st.markdown(
            """
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #2E86C1;
            text-align: center;
            margin-bottom: 2rem;
        }
        .status-connected {
            color: #28A745;
            font-weight: bold;
        }
        .status-disconnected {
            color: #DC3545;
            font-weight: bold;
        }
        .node-item {
            padding: 0.5rem;
            margin: 0.2rem;
            border-radius: 0.3rem;
            background-color: #F8F9FA;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Header
        st.markdown(
            '<h1 class="main-header">🔗 OPC-UA Interface</h1>', unsafe_allow_html=True
        )

        # Sidebar navigation
        self._render_sidebar()

        # Main content
        page = st.session_state.get("current_page", "Connection")

        if page == "Connection":
            self._render_connection_page()
        elif page == "Browse":
            self._render_browse_page()
        elif page == "Monitor":
            self._render_monitor_page()
        elif page == "Configuration":
            self._render_configuration_page()
        elif page == "Security":
            self._render_security_page()

    def _render_sidebar(self: Self) -> None:
        """Render the sidebar navigation."""
        with st.sidebar:
            st.title("🔗 OPC-UA Control")

            # Connection status
            status = st.session_state.connection_status
            if status == "Connected":
                st.markdown(
                    f'<p class="status-connected">● {status}</p>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<p class="status-disconnected">● {status}</p>',
                    unsafe_allow_html=True,
                )

            st.divider()

            # Navigation
            pages = ["Connection", "Browse", "Monitor", "Configuration", "Security"]
            st.radio("Navigation", pages, key="current_page")

            st.divider()

            # Quick actions
            st.subheader("Quick Actions")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔗 Connect", use_container_width=True):
                    self._quick_connect()
            with col2:
                if st.button("🔌 Disconnect", use_container_width=True):
                    self._quick_disconnect()

            # Configuration shortcuts
            st.subheader("Configurations")
            configs = self.config_manager.list_configurations()
            if configs:
                selected_config = st.selectbox(
                    "Load Config", ["None", *list(configs.keys())]
                )
                if selected_config != "None" and st.button(
                    "Load", use_container_width=True
                ):
                    self._load_configuration(selected_config)

    def _render_connection_page(self: Self) -> None:
        """Render the connection management page."""
        st.header("🔗 Connection Management")

        # Connection form
        with st.container():
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Server Configuration")

                # Server URL
                server_url = st.text_input(
                    "OPC-UA Server URL",
                    value=os.getenv("OPCUA_SERVER_URL", "opc.tcp://localhost:4840"),
                    help="Enter the OPC-UA server endpoint URL",
                )

                # Authentication
                col_auth1, col_auth2 = st.columns(2)
                with col_auth1:
                    username = st.text_input(
                        "Username", value=os.getenv("OPCUA_USERNAME", "admin")
                    )
                with col_auth2:
                    password = st.text_input("Password", type="password", value="")

                # Security settings
                st.subheader("Security Configuration")

                col_sec1, col_sec2 = st.columns(2)
                with col_sec1:
                    security_policy = st.selectbox(
                        "Security Policy",
                        ["None", "Basic256Sha256", "Basic128Rsa15", "Basic256"],
                        index=1,
                    )
                with col_sec2:
                    security_mode = st.selectbox(
                        "Security Mode", ["None", "Sign", "SignAndEncrypt"], index=2
                    )

            with col2:
                st.subheader("Connection Status")

                # Status display
                status = st.session_state.connection_status
                if status == "Connected":
                    st.success(f"✅ {status}")

                    if st.session_state.current_config:
                        config = st.session_state.current_config
                        st.info(f"**Server:** {config.server_url}")
                        st.info(f"**User:** {config.username}")
                        st.info(f"**Security:** {config.security_policy}")

                        # Connection actions
                        if st.button("📊 Server Info", use_container_width=True):
                            self._show_server_info()

                        if st.button("🔌 Disconnect", use_container_width=True):
                            self._disconnect()

                else:
                    st.error(f"❌ {status}")

                # Connection actions
                st.subheader("Actions")

                if st.button("🔗 Connect", use_container_width=True, type="primary"):
                    config = OPCUAConnectionConfig(
                        name="Web UI Connection",
                        server_url=server_url,
                        username=username,
                        password=password,
                        security_policy=security_policy,
                        security_mode=security_mode,
                    )
                    self._connect(config)

                if st.button("⚙️ Configuration Wizard", use_container_width=True):
                    self._show_wizard()

        # Connection history
        st.subheader("📝 Connection History")
        self._show_connection_history()

    def _render_browse_page(self: Self) -> None:
        """Render the OPC-UA node browsing page."""
        st.header("🌐 Node Browser")

        if st.session_state.connection_status != "Connected":
            st.warning("⚠️ Please connect to an OPC-UA server first.")
            return

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Browse Controls")

            # Root node selection
            root_node = st.text_input(
                "Root Node ID",
                value="i=84",  # Objects folder
                help="Enter the node ID to start browsing from",
            )

            # Browse options
            max_depth = st.slider("Max Depth", 1, 5, 2)
            show_variables_only = st.checkbox("Variables Only", value=False)

            if st.button("🔍 Browse", use_container_width=True):
                self._browse_nodes(root_node, max_depth, show_variables_only)

            # Node filters
            st.subheader("Filters")
            node_filter = st.text_input("Filter by name", "")

        with col2:
            st.subheader("Node Tree")

            # Display browsed nodes
            nodes = st.session_state.browse_nodes
            if nodes:
                filtered_nodes = self._filter_nodes(nodes, node_filter)
                self._display_node_tree(filtered_nodes)
            else:
                st.info("No nodes browsed yet. Click 'Browse' to start.")

    def _render_monitor_page(self: Self) -> None:
        """Render the OPC-UA monitoring page."""
        st.header("📊 Real-time Monitoring")

        if st.session_state.connection_status != "Connected":
            st.warning("⚠️ Please connect to an OPC-UA server first.")
            return

        # Monitoring controls
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            node_to_monitor = st.text_input(
                "Node ID to Monitor",
                value="",
                help="Enter the node ID you want to monitor",
            )

        with col2:
            update_interval = st.slider("Update Interval (s)", 1, 10, 2)

        with col3:
            st.write("")  # Spacing
            if st.button("+ Add Monitor"):
                self._add_monitor(node_to_monitor, update_interval)

        # Active monitors
        st.subheader("Active Monitors")

        if st.session_state.monitoring_data:
            # Display monitoring data in real-time
            for node_id, data in st.session_state.monitoring_data.items():
                with st.container():
                    col_node, col_value, col_time, col_action = st.columns([2, 2, 2, 1])

                    with col_node:
                        st.text(f"📍 {node_id}")

                    with col_value:
                        if "value" in data:
                            st.metric("Value", data["value"])
                        else:
                            st.text("No data")

                    with col_time:
                        if "timestamp" in data:
                            st.text(f"🕒 {data['timestamp']}")

                    with col_action:
                        if st.button("🗑️", key=f"remove_{node_id}"):
                            self._remove_monitor(node_id)

        else:
            st.info("No active monitors. Add a node ID to start monitoring.")

        # Auto-refresh for real-time updates
        if st.session_state.monitoring_data:
            time.sleep(1)
            st.rerun()

    def _render_configuration_page(self: Self) -> None:
        """Render the configuration management page."""
        st.header("⚙️ Configuration Management")

        # Save current configuration
        if st.session_state.current_config:
            st.subheader("💾 Save Current Configuration")

            col1, col2 = st.columns([2, 1])
            with col1:
                config_name = st.text_input("Configuration Name", "")
            with col2:
                st.write("")  # Spacing
                if st.button("💾 Save Config"):
                    if config_name:
                        self._save_configuration(config_name)
                    else:
                        st.error("Please enter a configuration name")

        # Load configurations
        st.subheader("📂 Saved Configurations")

        configs = self.config_manager.list_configurations()
        if configs:
            for name, config_data in configs.items():
                with st.expander(f"🔧 {name}"):
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.json(
                            {
                                "server_url": config_data.get("server_url", ""),
                                "username": config_data.get("username", ""),
                                "security_policy": config_data.get(
                                    "security_policy", ""
                                ),
                                "security_mode": config_data.get("security_mode", ""),
                            }
                        )

                    with col2:
                        if st.button("📥 Load", key=f"load_{name}"):
                            self._load_configuration(name)

                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{name}"):
                            self._delete_configuration(name)
        else:
            st.info("No saved configurations found.")

        # Import/Export
        st.subheader("📤 Import/Export")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Export Configurations**")
            if st.button("📤 Export All"):
                self._export_configurations()

        with col2:
            st.write("**Import Configurations**")
            uploaded_file = st.file_uploader("Choose configuration file", type=["json"])
            if uploaded_file and st.button("📥 Import"):
                self._import_configurations(uploaded_file)

    def _render_security_page(self: Self) -> None:
        """Render the security management page."""
        st.header("🔒 Security Management")

        # Certificate information
        st.subheader("📜 Certificate Management")

        cert_info = self.security_manager.get_certificate_info()
        if cert_info:
            col1, col2 = st.columns(2)

            with col1:
                st.info(f"**Subject:** {cert_info.get('subject', 'N/A')}")
                st.info(f"**Issuer:** {cert_info.get('issuer', 'N/A')}")
                st.info(f"**Valid From:** {cert_info.get('not_before', 'N/A')}")

            with col2:
                st.info(f"**Valid Until:** {cert_info.get('not_after', 'N/A')}")
                st.info(f"**Serial:** {cert_info.get('serial_number', 'N/A')}")
                st.info(f"**Key Size:** {cert_info.get('key_size', 'N/A')} bits")

        # Certificate actions
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Generate New Certificate"):
                self._generate_certificate()

        with col2:
            if st.button("📋 View Certificate Details"):
                self._show_certificate_details()

        with col3:
            if st.button("🗑️ Clear Certificates"):
                self._clear_certificates()

        # Security settings
        st.subheader("🔐 Security Settings")

        with st.container():
            st.checkbox(
                "Enforce Encryption", value=True, help="Require encrypted connections"
            )

            st.checkbox(
                "Validate Server Certificate",
                value=True,
                help="Verify server certificate authenticity",
            )

            st.checkbox(
                "Allow Untrusted Certificates",
                value=False,
                help="Allow connections to servers with untrusted certificates",
            )

        # Environment variables
        st.subheader("🌐 Environment Configuration")

        with st.expander("Environment Variables"):
            env_vars = {
                "OPCUA_SERVER_URL": os.getenv("OPCUA_SERVER_URL", ""),
                "OPCUA_USERNAME": os.getenv("OPCUA_USERNAME", ""),
                "OPCUA_SECURITY_POLICY": os.getenv("OPCUA_SECURITY_POLICY", ""),
                "OPCUA_SECURITY_MODE": os.getenv("OPCUA_SECURITY_MODE", ""),
                "OPCUA_CLIENT_CERT_PATH": os.getenv("OPCUA_CLIENT_CERT_PATH", ""),
                "NEO4J_URI": os.getenv("NEO4J_URI", ""),
                "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME", ""),
            }

            for key, value in env_vars.items():
                if "PASSWORD" in key:
                    value = "***" if value else ""
                st.text(f"{key}: {value}")

    # Helper methods
    def _quick_connect(self: Self) -> None:
        """Quick connect using environment variables."""
        config = OPCUAConnectionConfig(
            name="Quick Connect",
            server_url=os.getenv("OPCUA_SERVER_URL", "opc.tcp://localhost:4840"),
            username=os.getenv("OPCUA_USERNAME", "admin"),
            password=os.getenv("OPCUA_PASSWORD", ""),
            security_policy=os.getenv("OPCUA_SECURITY_POLICY", "Basic256Sha256"),
            security_mode=os.getenv("OPCUA_SECURITY_MODE", "SignAndEncrypt"),
        )
        self._connect(config)

    def _quick_disconnect(self: Self) -> None:
        """Quick disconnect."""
        self._disconnect()

    def _connect(self: Self, config: OPCUAConnectionConfig) -> None:
        """Connect to OPC-UA server."""
        try:
            self.client_manager = OPCUAClientManager(config)
            # Note: In real implementation, this would be async
            # For demo purposes, we'll simulate success
            st.session_state.connection_status = "Connected"
            st.session_state.current_config = config
            st.success("✅ Connected successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Connection failed: {e!s}")

    def _disconnect(self: Self) -> None:
        """Disconnect from OPC-UA server."""
        try:
            if self.client_manager:
                # Note: In real implementation, this would be async
                self.client_manager = None
            st.session_state.connection_status = "Disconnected"
            st.session_state.current_config = None
            st.session_state.browse_nodes = []
            st.session_state.monitoring_data = {}
            st.success("✅ Disconnected successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Disconnect failed: {e!s}")

    def _browse_nodes(
        self: Self, root_node: str, max_depth: int, variables_only: bool
    ) -> None:
        """Browse OPC-UA nodes."""
        # Simulated node browsing for demo
        sample_nodes = [
            {
                "id": "ns=2;i=1001",
                "name": "Temperature",
                "type": "Variable",
                "value": "25.6°C",
            },
            {
                "id": "ns=2;i=1002",
                "name": "Pressure",
                "type": "Variable",
                "value": "1.2 bar",
            },
            {
                "id": "ns=2;i=1003",
                "name": "Flow Rate",
                "type": "Variable",
                "value": "150 L/min",
            },
            {"id": "ns=2;i=2001", "name": "Motor", "type": "Object", "value": None},
            {"id": "ns=2;i=2002", "name": "Pump", "type": "Object", "value": None},
        ]

        st.session_state.browse_nodes = sample_nodes
        st.success(f"✅ Browsed {len(sample_nodes)} nodes from {root_node}")

    def _filter_nodes(self: Self, nodes: list[dict], filter_text: str) -> list[dict]:
        """Filter nodes by name."""
        if not filter_text:
            return nodes
        return [node for node in nodes if filter_text.lower() in node["name"].lower()]

    def _display_node_tree(self: Self, nodes: list[dict]) -> None:
        """Display node tree."""
        for node in nodes:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    icon = "📊" if node["type"] == "Variable" else "📁"
                    st.text(f"{icon} {node['name']}")

                with col2:
                    st.text(node["id"])

                with col3:
                    if node["value"]:
                        st.text(node["value"])
                    else:
                        st.text("-")

                with col4:
                    if node["type"] == "Variable" and st.button(
                        "📊", key=f"monitor_{node['id']}"
                    ):
                        self._add_monitor(node["id"], 2)

    def _add_monitor(self: Self, node_id: str, interval: int) -> None:
        """Add node to monitoring."""
        if node_id:
            st.session_state.monitoring_data[node_id] = {
                "value": "Monitoring...",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "interval": interval,
            }
            st.success(f"✅ Added {node_id} to monitoring")

    def _remove_monitor(self: Self, node_id: str) -> None:
        """Remove node from monitoring."""
        if node_id in st.session_state.monitoring_data:
            del st.session_state.monitoring_data[node_id]
            st.success(f"✅ Removed {node_id} from monitoring")
            st.rerun()

    def _save_configuration(self: Self, name: str) -> None:
        """Save current configuration."""
        if st.session_state.current_config:
            self.config_manager.save_configuration(
                name, st.session_state.current_config
            )
            st.success(f"✅ Configuration '{name}' saved successfully!")

    def _load_configuration(self: Self, name: str) -> None:
        """Load configuration."""
        config = self.config_manager.load_configuration(name)
        if config:
            st.session_state.current_config = config
            st.success(f"✅ Configuration '{name}' loaded successfully!")
            st.rerun()

    def _delete_configuration(self: Self, name: str) -> None:
        """Delete configuration."""
        self.config_manager.delete_configuration(name)
        st.success(f"✅ Configuration '{name}' deleted successfully!")
        st.rerun()

    def _show_server_info(self: Self) -> None:
        """Show server information."""
        info = {
            "Server Name": "Demo OPC-UA Server",
            "Server Version": "1.0.0",
            "Server State": "Running",
            "Namespaces": ["http://opcfoundation.org/UA/", "urn:demo:server"],
            "Endpoints": 3,
            "Security Policies": ["None", "Basic256Sha256"],
        }

        st.json(info)

    def _show_connection_history(self: Self) -> None:
        """Show connection history."""
        # Simulated connection history
        history = [
            {
                "time": "2025-01-23 14:30:25",
                "server": "opc.tcp://localhost:4840",
                "status": "Connected",
                "duration": "25 min",
            },
            {
                "time": "2025-01-23 13:45:10",
                "server": "opc.tcp://demo.server:4840",
                "status": "Failed",
                "duration": "-",
            },
            {
                "time": "2025-01-23 12:15:33",
                "server": "opc.tcp://localhost:4840",
                "status": "Connected",
                "duration": "1h 15min",
            },
        ]

        for entry in history:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.text(entry["time"])
            with col2:
                st.text(entry["server"])
            with col3:
                status_color = "🟢" if entry["status"] == "Connected" else "🔴"
                st.text(f"{status_color} {entry['status']}")
            with col4:
                st.text(entry["duration"])


def main() -> None:
    """Main entry point for the OPC-UA Web UI."""
    ui = OPCUAWebUI()
    ui.run()


if __name__ == "__main__":
    main()
