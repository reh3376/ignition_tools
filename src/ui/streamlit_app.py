"""Streamlit UI for IGN Scripts - Ignition Jython Script Generator."""

import json
from pathlib import Path
from typing import Any

import streamlit as st

# Import our script generator
try:
    from src.ignition.generators.script_generator import IgnitionScriptGenerator
    from src.ui.learning_integration import (
        show_learning_dashboard,
        show_learning_status,
        show_smart_recommendations,
        show_usage_insights,
        track_page_visit,
        track_script_generation,
        track_template_usage,
    )
except ImportError:
    # Handle import when running from different directory
    import sys

    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.ignition.generators.script_generator import IgnitionScriptGenerator

    # Learning system not available
    def track_page_visit(page_name: str) -> bool:
        pass

    def track_script_generation(template: str, config: dict[str, Any], success: bool) -> bool:
        pass

    def track_template_usage(template: str, action: str) -> bool:
        pass

    def show_smart_recommendations(current_action: str, container=None) -> bool:
        pass

    def show_learning_status() -> bool:
        return False

    def show_usage_insights() -> None:
        pass

    def show_learning_dashboard() -> None:
        pass


def init_session_state() -> None:
    """Initialize session state variables."""
    if "generator" not in st.session_state:
        st.session_state.generator = IgnitionScriptGenerator()
    if "generated_script" not in st.session_state:
        st.session_state.generated_script = ""
    if "last_config" not in st.session_state:
        st.session_state.last_config = {}


def render_header() -> None:
    """Render the application header."""
    st.set_page_config(
        page_title="IGN Scripts",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("⚙️ IGN Scripts")
    st.subheader("Ignition Jython Script Generator")
    st.markdown("Generate, validate, and export Jython scripts for Ignition SCADA systems")

    # Add version info with learning system status
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.info("🎯 Target: Ignition 8.1+ | Jython 2.7")
    with col2:
        st.success("✅ CLI Available")
    with col3:
        st.success("✅ Web UI Active")
    with col4:
        show_learning_status()


def render_sidebar() -> str:
    """Render the sidebar navigation and return selected page."""
    st.sidebar.title("Navigation")

    pages = {
        "🏠 Home": "home",
        "📝 Script Generator": "generator",
        "📋 Templates": "templates",
        "✅ Validation": "validation",
        "📦 Export/Import": "export",
        "🔗 Gateway Connections": "gateways",
        "🧠 Learning Analytics": "learning",
        "📚 Documentation": "docs",
    }

    selected = st.sidebar.selectbox("Choose a page:", list(pages.keys()), index=0)

    # Track page visits
    if selected in pages:
        track_page_visit(pages[selected])

    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Stats")

    templates = st.session_state.generator.list_templates()
    st.sidebar.metric("Available Templates", len(templates))

    if st.session_state.generated_script:
        script_lines = len(st.session_state.generated_script.split("\n"))
        st.sidebar.metric("Last Generated Script", f"{script_lines} lines")

    return pages[selected]


def render_home_page() -> None:
    """Render the home page with overview and quick actions."""
    # Show smart recommendations for home page
    recommendations_container = st.container()

    st.markdown("## 🎯 Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        ### What is IGN Scripts?

        IGN Scripts is a powerful tool for generating Jython scripts for Ignition SCADA systems.
        It allows you to:

        - 📝 Generate scripts from templates
        - ⚙️ Customize scripts with configurations
        - ✅ Validate script compatibility
        - 📦 Export for gateway deployment
        - 🔄 Version control your scripts
        - 🧠 Learn from usage patterns
        """
        )

    with col2:
        st.markdown(
            """
        ### Supported Ignition Contexts

        - **Vision Client Scripts**
          - Component event handlers
          - Window events
          - Custom methods

        - **Perspective Session Scripts**
          - View scripts
          - Component events
          - Session handlers

        - **Gateway Scripts**
          - Startup/shutdown scripts
          - Timer scripts
          - Message handlers

        - **Tag Scripts**
          - Value change scripts
          - Alarm scripts
          - UDT parameters
        """
        )

    st.markdown("---")

    # Quick actions
    st.markdown("## 🚀 Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎯 Generate Script", use_container_width=True):
            st.session_state.page = "generator"
            st.rerun()

    with col2:
        if st.button("📋 Browse Templates", use_container_width=True):
            st.session_state.page = "templates"
            st.rerun()

    with col3:
        if st.button("📦 Export Project", use_container_width=True):
            st.session_state.page = "export"
            st.rerun()

    # Show smart recommendations at the bottom
    with recommendations_container:
        show_smart_recommendations("home_page")

    # Show usage insights if learning system is available
    with st.expander("📊 Usage Insights", expanded=False):
        show_usage_insights()


def render_generator_page() -> None:
    """Render the script generator page."""
    st.markdown("## 📝 Script Generator")

    # Show recommendations for script generation
    recommendations_container = st.container()

    # Generation method selection
    method = st.radio(
        "Choose generation method:",
        ["From Template", "From Configuration File", "Quick Generate"],
        horizontal=True,
    )

    if method == "From Template":
        render_template_generator()
    elif method == "From Configuration File":
        render_config_generator()
    else:
        render_quick_generator()

    # Show smart recommendations
    with recommendations_container:
        show_smart_recommendations("script_generation")


def render_template_generator() -> None:
    """Render the template-based generator."""
    st.markdown("### 🎯 Generate from Template")

    templates = st.session_state.generator.list_templates()

    if not templates:
        st.warning("No templates found. Please add templates to the templates/ directory.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        # Template selection (use pre-selected if available)
        default_template = 0
        if hasattr(st.session_state, "selected_template") and st.session_state.selected_template in templates:
            default_template = templates.index(st.session_state.selected_template)

        selected_template = st.selectbox("Select Template:", templates, index=default_template)

        # Track template selection
        if selected_template:
            track_template_usage(selected_template, "selected")

        # Basic configuration
        component_name = st.text_input("Component Name:", placeholder="e.g., MainMenuButton")

        if "button_click_handler" in selected_template:
            action_type = st.selectbox(
                "Action Type:",
                ["navigation", "tag_write", "popup", "database", "custom"],
            )

            # Action-specific options
            if action_type == "navigation":
                st.text_input("Target Window:", placeholder="e.g., MainMenu")
                st.text_area(
                    "Window Parameters (JSON):",
                    placeholder='{"param1": "value1", "param2": "value2"}',
                )
            elif action_type == "tag_write":
                st.text_input("Target Tag:", placeholder="[default]Motor1/Speed")
                st.text_input("Tag Value:", placeholder="100")
            elif action_type == "popup":
                st.text_input("Popup Window:", placeholder="e.g., SettingsPopup")
                st.text_area("Popup Parameters (JSON):", placeholder='{"mode": "edit"}')
            elif action_type == "database":
                st.text_area(
                    "SQL Query:",
                    placeholder="INSERT INTO logs (message, timestamp) VALUES (?, ?)",
                )

        # Generate button
        if st.button("🚀 Generate Script", type="primary", use_container_width=True):
            generate_template_script(
                selected_template,
                {
                    "component_name": component_name,
                    "action_type": (action_type if "button_click_handler" in selected_template else None),
                },
            )

    with col2:
        # Show template-specific recommendations
        if selected_template:
            st.markdown("### 💡 Template Insights")
            show_smart_recommendations(f"template_{selected_template.replace('.jinja2', '')}")


def generate_template_script(template: str, context: dict[str, Any]) -> Any:
    """Generate script from template with tracking."""
    try:
        with st.spinner("Generating script..."):
            script_content = st.session_state.generator.generate_script(template, context)
            st.session_state.generated_script = script_content

            # Track successful generation
            track_script_generation(template, context, success=True)
            track_template_usage(template, "generated")

            st.success(f"✅ Script generated successfully from template: {template}")

            # Display the generated script
            st.markdown("### 📄 Generated Script")
            st.code(script_content, language="python")

            # Download button
            st.download_button(
                label="💾 Download Script",
                data=script_content,
                file_name=f"{context.get('component_name', 'script')}.py",
                mime="text/x-python",
            )

    except Exception as e:
        # Track failed generation
        track_script_generation(template, context, success=False)
        st.error(f"❌ Error generating script: {e!s}")


def render_config_generator() -> None:
    """Render the configuration file-based generator."""
    st.markdown("### 📁 Generate from Configuration File")

    col1, col2 = st.columns(2)

    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Configuration File",
            type=["json"],
            help="Upload a JSON configuration file",
        )

        if uploaded_file is not None:
            try:
                config_content = json.loads(uploaded_file.read())
                st.json(config_content)

                if st.button("🎯 Generate from Config", type="primary"):
                    script_content = st.session_state.generator.generate_from_config(config_content)
                    st.session_state.generated_script = script_content
                    st.success("✅ Script generated from configuration!")

            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON file: {e}")
            except Exception as e:
                st.error(f"❌ Error generating script: {e}")

    with col2:
        st.markdown("### 📋 Example Configuration")
        st.markdown("Here's an example configuration file structure:")

        example_config = {
            "template": "vision/button_click_handler",
            "component_name": "MainMenuButton",
            "description": "Navigation button to main menu",
            "action_type": "navigation",
            "target_window": "MainMenu",
            "window_params": {
                "user_id": "{Root Container.CurrentUser.text}",
                "timestamp": "{Root Container.CurrentTime.text}",
            },
            "logging_enabled": True,
            "logger_name": "NavigationHandler",
        }

        st.json(example_config)

        # Download example config
        st.download_button(
            label="💾 Download Example",
            data=json.dumps(example_config, indent=2),
            file_name="example_config.json",
            mime="application/json",
        )


def render_quick_generator() -> None:
    """Render the quick generator for common scenarios."""
    st.markdown("### ⚡ Quick Generate")
    st.markdown("Generate common script types with minimal configuration")

    script_type = st.selectbox(
        "Script Type:",
        [
            "Vision Button - Navigation",
            "Vision Button - Tag Write",
            "Vision Button - Show Popup",
            "Tag Change Handler",
            "Gateway Startup Script",
        ],
    )

    component_name = st.text_input("Component/Script Name:")

    if script_type == "Vision Button - Navigation":
        target_window = st.text_input("Target Window:")
        if st.button("🎯 Generate") and component_name and target_window:
            context = {
                "component_name": component_name,
                "action_type": "navigation",
                "target_window": target_window,
                "logging_enabled": True,
            }
            generate_quick_script("vision/button_click_handler.jinja2", context)

    elif script_type == "Vision Button - Tag Write":
        target_tag = st.text_input("Target Tag Path:")
        tag_value = st.text_input("Value to Write:")
        if st.button("🎯 Generate") and component_name and target_tag:
            context = {
                "component_name": component_name,
                "action_type": "tag_write",
                "target_tag": target_tag,
                "tag_value": tag_value,
                "logging_enabled": True,
            }
            generate_quick_script("vision/button_click_handler.jinja2", context)


def generate_quick_script(template: str, context: dict[str, Any]) -> None:
    """Generate a script quickly with minimal configuration."""
    try:
        script_content = st.session_state.generator.generate_script(template, context)
        st.session_state.generated_script = script_content
        st.success("✅ Script generated successfully!")
    except Exception as e:
        st.error(f"❌ Error generating script: {e}")


def render_templates_page() -> None:
    """Render the templates page."""
    st.markdown("## 📋 Available Templates")

    templates = st.session_state.generator.list_templates()

    if not templates:
        st.warning("No templates found. Please add templates to the templates/ directory.")
        return

    # Template grid
    cols = st.columns(2)
    for idx, template in enumerate(templates):
        with cols[idx % 2], st.expander(f"📄 {template}"):
            template_path = Path("templates") / template
            if template_path.exists():
                with open(template_path) as f:
                    content = f.read()

                st.markdown(f"**Path:** `{template}`")
                st.markdown(f"**Size:** {len(content)} characters")

                # Show preview
                preview = content[:300] + "..." if len(content) > 300 else content
                st.code(preview, language="python")

                # Download button
                st.download_button(
                    "💾 Download Template",
                    data=content,
                    file_name=template.split("/")[-1],
                    mime="text/plain",
                    key=f"download_{idx}",
                )


def render_validation_page() -> None:
    """Render the validation page."""
    st.markdown("## ✅ Script Validation")

    st.info("🚧 Script validation features are coming soon!")

    # Placeholder for validation features
    st.markdown(
        """
    ### Planned Validation Features:

    - **Jython Syntax Validation** - Check for Jython 2.7 compatibility
    - **Ignition API Validation** - Verify system function usage
    - **Template Configuration Validation** - Validate config against template requirements
    - **Script Performance Analysis** - Check for common performance issues
    - **Security Scanning** - Identify potential security concerns
    """
    )


def render_export_page() -> None:
    """Render the export page."""
    try:
        from src.ui.pages.export_import import show_export_import_page

        show_export_import_page()
    except ImportError as e:
        st.error(f"❌ Export/Import System not available: {e}")
        st.markdown("## 📦 Project Export")
        st.info("🚧 Export/Import System is being developed!")

        st.markdown(
            """
        ### Available Export Features:

        - **Gateway Backup Format** - Export as .gwbk files
        - **Project Archive** - Create Ignition project zips
        - **Resource Export** - Export individual resources
        - **Version Control Preparation** - Structure for git integration
        - **Deployment Packages** - Ready-to-deploy script packages
        - **CLI Integration** - Full CLI support for exports and imports
        """
        )


def render_gateways_page() -> None:
    """Render the gateway connections management page."""
    st.markdown("## 🔗 Gateway Connections")
    st.markdown("Manage connections to Ignition gateways for testing and deployment.")

    try:
        from src.ignition.gateway.client import IgnitionGatewayClient
        from src.ignition.gateway.config import GatewayConfigManager

        manager = GatewayConfigManager()

        # Tabs for different gateway operations
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📋 Gateway List",
                "🔌 Connection Test",
                "🏥 Health Check",
                "⚙️ Configuration",
            ]
        )

        with tab1:
            st.subheader("Configured Gateways")

            try:
                configs = manager.list_configs()  # type: ignore[attr-defined]

                if not configs:
                    st.info(
                        "🔧 No gateways configured. Add gateways using the "
                        "Configuration tab or by setting up your .env file."
                    )

                    with st.expander("Quick Setup Instructions"):
                        st.markdown(
                            """
                        **To configure gateways:**
                        1. Copy `gateway_config.env` to `.env`
                        2. Edit with your gateway details:
                        ```
                        IGN_GATEWAYS=local_dev
                        IGN_LOCAL_DEV_HOST=localhost
                        IGN_LOCAL_DEV_PORT=8088
                        IGN_LOCAL_DEV_USERNAME=admin
                        IGN_LOCAL_DEV_PASSWORD=password
                        ```
                        3. Restart the application
                        """
                        )
                else:
                    # Display gateway cards
                    for config_name in configs:
                        config = manager.get_config(config_name)
                        if config:
                            with st.container():
                                col1, col2, col3 = st.columns([3, 1, 1])

                                with col1:
                                    st.markdown(f"**🏢 {config.name}**")
                                    st.text(f"URL: {config.base_url}")
                                    st.text(f"Auth: {config.auth_type} ({config.username})")
                                    st.text(f"SSL: {'✓' if config.verify_ssl else '✗'} | Timeout: {config.timeout}s")

                                    if config.description:
                                        st.caption(config.description)

                                    if config.tags:
                                        tags_display = " ".join([f"`{tag}`" for tag in config.tags])
                                        st.markdown(f"Tags: {tags_display}")

                                with col2:
                                    test_key = f"test_{config_name}"
                                    if st.button("🧪 Test", key=test_key):
                                        with st.spinner(f"Testing connection to {config.name}..."):
                                            try:
                                                client = IgnitionGatewayClient(config=config)  # type: ignore[arg-type]
                                                if client.connect():
                                                    st.success(f"✅ Connection to {config.name} successful!")
                                                    client.disconnect()
                                                else:
                                                    st.error(f"❌ Connection to {config.name} failed")
                                            except Exception as e:
                                                st.error(f"❌ Error: {e!s}")

                                with col3:
                                    health_key = f"health_{config_name}"
                                    if st.button("🏥 Health", key=health_key):
                                        with st.spinner(f"Checking health of {config.name}..."):
                                            try:
                                                with IgnitionGatewayClient(
                                                    config=config  # type: ignore[arg-type]
                                                ) as client:  # type: ignore[attr-defined]
                                                    health_data = client.health_check()

                                                    status = health_data.get("overall_status", "unknown")
                                                    if status == "healthy":
                                                        st.success(f"✅ {config.name} is healthy")
                                                    elif status == "warning":
                                                        st.warning(f"⚠️ {config.name} has warnings")
                                                    else:
                                                        st.error(f"❌ {config.name} is unhealthy")

                                                    # Show detailed health info
                                                    with st.expander("Health Details"):
                                                        checks = health_data.get("checks", {})
                                                        for (
                                                            check_name,
                                                            check_result,
                                                        ) in checks.items():
                                                            check_status = check_result.get("status", "unknown")
                                                            details = check_result.get("details", "")

                                                            if check_status == "healthy":
                                                                st.success(
                                                                    f"✅ {check_name.replace('_', ' ').title()}: "
                                                                    f"{details}"
                                                                )
                                                            elif check_status == "warning":
                                                                st.warning(
                                                                    f"⚠️ {check_name.replace('_', ' ').title()}: "
                                                                    f"{details}"
                                                                )
                                                            else:
                                                                st.error(
                                                                    f"❌ {check_name.replace('_', ' ').title()}: "
                                                                    f"{details}"
                                                                )
                                            except Exception as e:
                                                st.error(f"❌ Health check failed: {e!s}")

                                st.divider()

            except Exception as e:
                st.error("❌ Gateway system not available")
                st.error(f"Import error: {e!s}")
                st.info("Make sure the gateway modules are properly installed and accessible.")

        with tab2:
            st.subheader("Connection Test")

            try:
                configs = manager.list_configs()  # type: ignore[attr-defined]
                if not configs:
                    st.info("No gateways configured. Please set up gateways first.")
                else:

                    def _format_gateway_option(x) -> Any:
                        config = manager.get_config(x)
                        return f"{x} ({config.base_url if config else 'Error'})"

                    selected_gateway = st.selectbox(
                        "Select gateway to test:",
                        options=configs,
                        format_func=_format_gateway_option,
                    )

                    if st.button("🔌 Test Connection", use_container_width=True):
                        config = manager.get_config(selected_gateway)
                        if config:
                            with st.spinner(f"Testing connection to {config.name}..."):
                                try:
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()

                                    status_text.text("Creating client...")
                                    progress_bar.progress(25)

                                    client = IgnitionGatewayClient(config=config)  # type: ignore[arg-type]

                                    status_text.text("Connecting...")
                                    progress_bar.progress(50)

                                    if client.connect():
                                        status_text.text("Getting gateway information...")
                                        progress_bar.progress(75)

                                        info = client.get_gateway_info()

                                        progress_bar.progress(100)
                                        status_text.text("Connection successful!")

                                        st.success("✅ Connection established successfully!")

                                        if info:
                                            st.subheader("Gateway Information")

                                            # Display gateway info in columns
                                            col1, col2 = st.columns(2)

                                            with col1:
                                                for key, value in info.items():
                                                    if key != "gateway_info_raw" and isinstance(
                                                        value,
                                                        str | int | float | bool,
                                                    ):
                                                        st.metric(
                                                            key.replace("_", " ").title(),
                                                            str(value),
                                                        )

                                            with col2:
                                                if "gateway_info_raw" in info:
                                                    st.text_area(
                                                        "Raw Gateway Data",
                                                        str(info["gateway_info_raw"])[:500] + "...",
                                                    )

                                        client.disconnect()
                                    else:
                                        progress_bar.progress(100)
                                        status_text.text("Connection failed!")
                                        st.error("❌ Connection failed")

                                except Exception as e:
                                    st.error(f"❌ Connection error: {e!s}")

                                    # Provide troubleshooting tips
                                    with st.expander("🔧 Troubleshooting Tips"):
                                        st.markdown(
                                            """
                                        **Common issues:**
                                        - **Connection refused**: Gateway may not be running or accessible
                                        - **SSL/TLS errors**: Try disabling SSL verification for development
                                        - **Authentication failed**: Check username and password
                                        - **Timeout**: Gateway may be slow or network issues

                                        **Next steps:**
                                        1. Verify gateway is running and accessible
                                        2. Check network connectivity
                                        3. Validate credentials
                                        4. Try the CLI: `ign gateway test`
                                        """
                                        )

            except Exception as e:
                st.error("❌ Gateway system not available")
                st.error(f"Import error: {e!s}")
                st.info("Make sure the gateway modules are properly installed and accessible.")

        with tab3:
            st.subheader("Health Check")

            try:
                configs = manager.list_configs()  # type: ignore[attr-defined]
                if not configs:
                    st.info("No gateways configured. Please set up gateways first.")
                else:
                    # Option to check all gateways or specific one
                    check_all = st.checkbox("Check all gateways", value=False)

                    if check_all:
                        if st.button("🏥 Check All Gateways Health", use_container_width=True):
                            with st.spinner("Checking health of all gateways..."):
                                try:
                                    from src.ignition.gateway.client import (
                                        GatewayConnectionPool,  # type: ignore[import]
                                    )

                                    pool = GatewayConnectionPool()
                                    for config_name in configs:
                                        pool.add_client(config_name)

                                    health_results = pool.health_check_all()

                                    # Display results
                                    for (
                                        gateway_name,
                                        health_data,
                                    ) in health_results.items():
                                        status = health_data.get("overall_status", "unknown")

                                        if status == "healthy":
                                            st.success(f"✅ **{gateway_name}** - Healthy")
                                        elif status == "warning":
                                            st.warning(f"⚠️ **{gateway_name}** - Warning")
                                        else:
                                            st.error(f"❌ **{gateway_name}** - Unhealthy")

                                        # Show detailed checks
                                        with st.expander(f"Details for {gateway_name}"):
                                            checks = health_data.get("checks", {})
                                            for (
                                                check_name,
                                                check_result,
                                            ) in checks.items():
                                                check_status = check_result.get("status", "unknown")
                                                details = check_result.get("details", "")
                                                value_ms = check_result.get("value_ms", None)

                                                check_display = f"{check_name.replace('_', ' ').title()}"
                                                if value_ms:
                                                    check_display += f" ({value_ms}ms)"
                                                if details:
                                                    check_display += f": {details}"

                                                if check_status == "healthy":
                                                    st.success(f"✅ {check_display}")
                                                elif check_status == "warning":
                                                    st.warning(f"⚠️ {check_display}")
                                                else:
                                                    st.error(f"❌ {check_display}")
                                except Exception as e:
                                    st.error(f"❌ Health check failed: {e!s}")
                    else:

                        def _format_health_gateway_option(x) -> Any:
                            config = manager.get_config(x)
                            return f"{x} ({config.base_url if config else 'Error'})"

                        selected_gateway = st.selectbox(
                            "Select gateway for health check:",
                            options=configs,
                            format_func=_format_health_gateway_option,
                        )

                        if st.button("🏥 Check Health", use_container_width=True):
                            config = manager.get_config(selected_gateway)
                            if config:
                                with st.spinner(f"Checking health of {config.name}..."):
                                    try:
                                        with IgnitionGatewayClient(config=config) as client:  # type: ignore[arg-type,attr-defined]
                                            health_data = client.health_check()

                                            # Overall status
                                            status = health_data.get("overall_status", "unknown")
                                            timestamp = health_data.get("timestamp", "unknown")

                                            if status == "healthy":
                                                st.success("✅ **Overall Status: HEALTHY**")
                                            elif status == "warning":
                                                st.warning("⚠️ **Overall Status: WARNING**")
                                            else:
                                                st.error("❌ **Overall Status: UNHEALTHY**")

                                            st.info(f"🕐 Timestamp: {timestamp}")

                                            # Detailed health checks
                                            st.subheader("Detailed Health Checks")

                                            checks = health_data.get("checks", {})
                                            for (
                                                check_name,
                                                check_result,
                                            ) in checks.items():
                                                check_status = check_result.get("status", "unknown")
                                                details = check_result.get("details", "")
                                                value_ms = check_result.get("value_ms", None)

                                                with st.container():
                                                    col1, col2 = st.columns([1, 3])

                                                    with col1:
                                                        if check_status == "healthy":
                                                            st.success("✅")
                                                        elif check_status == "warning":
                                                            st.warning("⚠️")
                                                        else:
                                                            st.error("❌")

                                                    with col2:
                                                        check_display = check_name.replace("_", " ").title()
                                                        if value_ms:
                                                            check_display += f" ({value_ms}ms)"

                                                        st.write(f"**{check_display}**")
                                                        if details:
                                                            st.caption(details)
                                    except Exception as e:
                                        st.error(f"❌ Health check failed: {e!s}")

            except Exception as e:
                st.error("❌ Gateway system not available")
                st.error(f"Import error: {e!s}")
                st.info("Make sure the gateway modules are properly installed and accessible.")

        with tab4:
            st.subheader("Gateway Configuration")

            st.markdown(
                """
            Configure gateways using environment variables in your `.env` file.
            """
            )

            # Configuration template generator
            st.markdown("### 📝 Generate Configuration Template")

            with st.form("gateway_config_form"):
                col1, col2 = st.columns(2)

                with col1:
                    gateway_name = st.text_input(
                        "Gateway Name",
                        value="my_gateway",
                        help="Unique name for this gateway",
                    )
                    host = st.text_input("Host", value="localhost", help="Gateway hostname or IP address")
                    port = st.number_input(
                        "Port",
                        value=8088,
                        min_value=1,
                        max_value=65535,
                        help="Gateway port",
                    )
                    username = st.text_input("Username", value="admin", help="Gateway username")

                with col2:
                    password = st.text_input(
                        "Password",
                        value="password",
                        type="password",
                        help="Gateway password",
                    )
                    use_https = st.checkbox("Use HTTPS", value=False, help="Use HTTPS connection")
                    verify_ssl = st.checkbox("Verify SSL", value=True, help="Verify SSL certificates")
                    timeout = st.number_input(
                        "Timeout (seconds)",
                        value=30,
                        min_value=5,
                        max_value=300,
                        help="Connection timeout",
                    )

                description = st.text_area(
                    "Description",
                    value="",
                    help="Optional description for this gateway",
                )
                tags = st.text_input(
                    "Tags (comma-separated)",
                    value="",
                    help="Optional tags for organization",
                )

                if st.form_submit_button("📋 Generate Configuration", use_container_width=True):
                    # Generate configuration
                    config_lines = [
                        f"# Gateway Configuration: {gateway_name}",
                        f"IGN_GATEWAYS={gateway_name}",
                        "",
                        f"# {gateway_name.title()} Gateway Configuration",
                        f"IGN_{gateway_name.upper()}_HOST={host}",
                        f"IGN_{gateway_name.upper()}_PORT={port}",
                        f"IGN_{gateway_name.upper()}_HTTPS={'true' if use_https else 'false'}",
                        f"IGN_{gateway_name.upper()}_USERNAME={username}",
                        f"IGN_{gateway_name.upper()}_PASSWORD={password}",
                        f"IGN_{gateway_name.upper()}_AUTH_TYPE=basic",
                        f"IGN_{gateway_name.upper()}_VERIFY_SSL={'true' if verify_ssl else 'false'}",
                        f"IGN_{gateway_name.upper()}_TIMEOUT={timeout}",
                    ]

                    if description:
                        config_lines.append(f"IGN_{gateway_name.upper()}_DESCRIPTION={description}")

                    if tags:
                        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                        if tag_list:
                            config_lines.append(f"IGN_{gateway_name.upper()}_TAGS={','.join(tag_list)}")

                    config_text = "\n".join(config_lines)

                    st.success("✅ Configuration generated!")
                    st.markdown("**Copy this to your `.env` file:**")
                    st.code(config_text, language="bash")

                    # Provide download button
                    st.download_button(
                        label="💾 Download .env Template",
                        data=config_text,
                        file_name=f"{gateway_name}_gateway.env",
                        mime="text/plain",
                    )

            st.markdown("---")

            # Configuration validation
            st.markdown("### ✅ Validate Current Configuration")

            if st.button("🔍 Check Environment Configuration", use_container_width=True):
                try:
                    configs = manager.list_configs()  # type: ignore[attr-defined]

                    if configs:
                        st.success(f"✅ Found {len(configs)} configured gateway(s)")

                        for config_name in configs:
                            config = manager.get_config(config_name)
                            if config:
                                st.info(f"**{config_name}**: {config.base_url}")
                    else:
                        st.warning("⚠️ No gateways found in environment configuration")
                        st.info("Add gateways to your .env file using the template generator above")

                except Exception as e:
                    st.error(f"❌ Configuration validation failed: {e!s}")

    except ImportError as e:
        st.error("❌ Gateway system not available")
        st.error(f"Import error: {e!s}")
        st.info("Make sure the gateway modules are properly installed and accessible.")


def render_learning_page() -> None:
    """Render the learning analytics page."""
    st.markdown("## 🧠 Learning Analytics Dashboard")

    show_learning_dashboard()


def render_docs_page() -> None:
    """Render the documentation page."""
    st.markdown("## 📚 Documentation")

    tab1, tab2, tab3, tab4 = st.tabs(["Getting Started", "Templates", "CLI Usage", "Examples"])

    with tab1:
        st.markdown(
            """
        ### 🚀 Getting Started

        #### Prerequisites
        - Python 3.11 or higher
        - Access to Ignition 8.1+ environment

        #### Installation
        ```bash
        # Clone the repository
        git clone <repository-url>
        cd IGN_scripts

        # Set up virtual environment
        uv venv
        source .venv/bin/activate  # Unix

        # Install dependencies
        uv pip install -r requirements.txt
        ```

        #### Running the Web UI
        ```bash
        streamlit run src/ui/streamlit_app.py
        ```
        """
        )

    with tab2:
        st.markdown(
            """
        ### 📝 Template System

        Templates use Jinja2 syntax and are stored in the `templates/` directory.

        #### Template Structure
        ```
        templates/
        ├── vision/          # Vision client scripts
        ├── perspective/     # Perspective scripts
        ├── gateway/         # Gateway scripts
        ├── tags/           # Tag-related scripts
        └── alarms/         # Alarm system scripts
        ```

        #### Template Variables
        Common variables available in all templates:
        - `component_name` - Name of the component
        - `timestamp` - Generation timestamp
        - `description` - Script description
        - `logging_enabled` - Whether to include logging
        """
        )

    with tab3:
        st.markdown(
            """
        ### 💻 CLI Usage

        The CLI provides the same functionality as this web interface:

        ```bash
        # List available templates
                    python -m src.core.enhanced_cli template list

        # Generate script from template
        python -m src.core.enhanced_cli script generate \\
          --template vision/button_click_handler \\
          --component-name "MainButton" \\
          --output my_script.py

        # Generate from configuration file
        python -m src.core.enhanced_cli script generate \\
          --config config.json \\
          --output script.py

        # Validate configuration
        python -m src.core.enhanced_cli template validate \\
          template_name config.json
        ```
        """
        )

    with tab4:
        st.markdown(
            """
        ### 🎓 Examples

        #### Basic Button Handler
        ```python
        # Generated Jython script
        def handle_button_click(event):
            try:
                system.nav.openWindow("MainMenu")
                logger = system.util.getLogger("ButtonHandler")
                logger.info("Button clicked: MainMenuButton")
            except Exception as e:
                system.gui.errorBox("Error: %s" % str(e))
        ```

        #### Tag Write Handler
        ```python
        def handle_button_click(event):
            try:
                system.tag.write("[default]Motor1/Speed", 100)
                logger = system.util.getLogger("TagHandler")
                logger.info("Tag updated successfully")
            except Exception as e:
                logger.error("Tag write failed: %s", str(e))
        ```
        """
        )


def main() -> None:
    """Main Streamlit application."""
    init_session_state()
    render_header()

    # Get the selected page
    page = render_sidebar()

    # Route to the appropriate page
    if page == "home":
        render_home_page()
    elif page == "generator":
        render_generator_page()
    elif page == "templates":
        render_templates_page()
    elif page == "validation":
        render_validation_page()
    elif page == "export":
        render_export_page()
    elif page == "gateways":
        render_gateways_page()
    elif page == "learning":
        render_learning_page()
    elif page == "docs":
        render_docs_page()
    else:
        render_home_page()


if __name__ == "__main__":
    main()
