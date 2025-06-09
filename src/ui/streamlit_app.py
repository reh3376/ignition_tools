"""Streamlit UI for IGN Scripts - Ignition Jython Script Generator."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

# Import our script generator
try:
    from src.ignition.generators.script_generator import IgnitionScriptGenerator
except ImportError:
    # Handle import when running from different directory
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.ignition.generators.script_generator import IgnitionScriptGenerator


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
        initial_sidebar_state="expanded"
    )
    
    st.title("⚙️ IGN Scripts")
    st.subheader("Ignition Jython Script Generator")
    st.markdown("Generate, validate, and export Jython scripts for Ignition SCADA systems")
    
    # Add version info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.info("🎯 Target: Ignition 8.1+ | Jython 2.7")
    with col2:
        st.success("✅ CLI Available")
    with col3:
        st.success("✅ Web UI Active")


def render_sidebar() -> str:
    """Render the sidebar navigation and return selected page."""
    st.sidebar.title("Navigation")
    
    pages = {
        "🏠 Home": "home",
        "📝 Script Generator": "generator", 
        "📋 Templates": "templates",
        "✅ Validation": "validation",
        "📦 Export": "export",
        "📚 Documentation": "docs"
    }
    
    selected = st.sidebar.selectbox(
        "Choose a page:",
        list(pages.keys()),
        index=0
    )
    
    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Stats")
    
    templates = st.session_state.generator.list_templates()
    st.sidebar.metric("Available Templates", len(templates))
    
    if st.session_state.generated_script:
        script_lines = len(st.session_state.generated_script.split('\n'))
        st.sidebar.metric("Last Generated Script", f"{script_lines} lines")
    
    return pages[selected]


def render_home_page() -> None:
    """Render the home page with overview and quick actions."""
    st.markdown("## 🎯 Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### What is IGN Scripts?
        
        IGN Scripts is a powerful tool for generating Jython scripts for Ignition SCADA systems. 
        It allows you to:
        
        - 📝 Generate scripts from templates
        - ⚙️ Customize scripts with configurations  
        - ✅ Validate script compatibility
        - 📦 Export for gateway deployment
        - 🔄 Version control your scripts
        """)
        
    with col2:
        st.markdown("""
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
        """)
    
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


def render_generator_page() -> None:
    """Render the script generator page."""
    st.markdown("## 📝 Script Generator")
    
    # Generation method selection
    method = st.radio(
        "Choose generation method:",
        ["From Template", "From Configuration File", "Quick Generate"],
        horizontal=True
    )
    
    if method == "From Template":
        render_template_generator()
    elif method == "From Configuration File":
        render_config_generator() 
    else:
        render_quick_generator()


def render_template_generator() -> None:
    """Render the template-based generator."""
    st.markdown("### 🎯 Generate from Template")
    
    templates = st.session_state.generator.list_templates()
    
    if not templates:
        st.warning("No templates found. Please add templates to the templates/ directory.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Template selection
        selected_template = st.selectbox("Select Template:", templates)
        
        # Basic configuration
        component_name = st.text_input("Component Name:", placeholder="e.g., MainMenuButton")
        
        if "button_click_handler" in selected_template:
            action_type = st.selectbox(
                "Action Type:",
                ["navigation", "tag_write", "popup", "database", "custom"]
            )
            
            # Action-specific options
            if action_type == "navigation":
                target_window = st.text_input("Target Window:", placeholder="e.g., MainMenu")
                window_params = st.text_area(
                    "Window Parameters (JSON):",
                    placeholder='{"param1": "value1", "param2": "value2"}'
                )
            elif action_type == "tag_write":
                target_tag = st.text_input("Target Tag:", placeholder="[default]Motor1/Speed")
                tag_value = st.text_input("Tag Value:", placeholder="100")
            elif action_type == "popup":
                popup_window = st.text_input("Popup Window:", placeholder="e.g., SettingsPopup")
                popup_params = st.text_area(
                    "Popup Parameters (JSON):",
                    placeholder='{"mode": "edit"}'
                )
            elif action_type == "database":
                sql_query = st.text_area(
                    "SQL Query:",
                    placeholder="INSERT INTO logs (message, timestamp) VALUES (?, ?)"
                )
            elif action_type == "custom":
                custom_code = st.text_area(
                    "Custom Code:",
                    placeholder="# Your custom Jython code here"
                )
        
        # Advanced options
        with st.expander("Advanced Options"):
            logging_enabled = st.checkbox("Enable Logging", value=True)
            show_error_popup = st.checkbox("Show Error Popups", value=True)
            reraise_errors = st.checkbox("Re-raise Errors", value=False)
            
            if logging_enabled:
                logger_name = st.text_input("Logger Name:", value="ScriptHandler")
    
    with col2:
        st.markdown("### 📋 Template Preview")
        
        if selected_template:
            template_path = Path("templates") / selected_template
            if template_path.exists():
                with open(template_path, "r") as f:
                    template_content = f.read()
                st.code(template_content[:500] + "..." if len(template_content) > 500 else template_content)
    
    # Generate button
    if st.button("🎯 Generate Script", type="primary"):
        if not component_name:
            st.error("Component Name is required")
            return
        
        # Build context
        context = {
            "component_name": component_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if "button_click_handler" in selected_template:
            context["action_type"] = action_type
            
            if action_type == "navigation" and target_window:
                context["target_window"] = target_window
                if window_params:
                    try:
                        context["window_params"] = json.loads(window_params)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON in window parameters")
                        return
            elif action_type == "tag_write" and target_tag:
                context["target_tag"] = target_tag
                context["tag_value"] = tag_value
            elif action_type == "popup" and popup_window:
                context["popup_window"] = popup_window
                if popup_params:
                    try:
                        context["popup_params"] = json.loads(popup_params)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON in popup parameters")
                        return
            elif action_type == "database" and sql_query:
                context["sql_query"] = sql_query
            elif action_type == "custom" and custom_code:
                context["custom_code"] = custom_code
        
        # Add advanced options
        context["logging_enabled"] = logging_enabled
        context["show_error_popup"] = show_error_popup
        context["reraise_errors"] = reraise_errors
        if logging_enabled and logger_name:
            context["logger_name"] = logger_name
        
        try:
            script_content = st.session_state.generator.generate_script(
                selected_template, context
            )
            st.session_state.generated_script = script_content
            st.session_state.last_config = context
            st.success("✅ Script generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Error generating script: {e}")
    
    # Display generated script
    if st.session_state.generated_script:
        st.markdown("---")
        st.markdown("### 📄 Generated Script")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.code(st.session_state.generated_script, language="python")
        
        with col2:
            # Download button
            st.download_button(
                label="💾 Download Script",
                data=st.session_state.generated_script,
                file_name=f"{component_name.lower().replace(' ', '_')}_handler.py",
                mime="text/plain"
            )
            
            # Copy to clipboard (via text area)
            st.text_area(
                "Copy to clipboard:",
                st.session_state.generated_script,
                height=100,
                help="Select all and copy"
            )


def render_config_generator() -> None:
    """Render the configuration file-based generator."""
    st.markdown("### 📁 Generate from Configuration File")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Configuration File",
            type=["json"],
            help="Upload a JSON configuration file"
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
                "timestamp": "{Root Container.CurrentTime.text}"
            },
            "logging_enabled": True,
            "logger_name": "NavigationHandler"
        }
        
        st.json(example_config)
        
        # Download example config
        st.download_button(
            label="💾 Download Example",
            data=json.dumps(example_config, indent=2),
            file_name="example_config.json",
            mime="application/json"
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
            "Gateway Startup Script"
        ]
    )
    
    component_name = st.text_input("Component/Script Name:")
    
    if script_type == "Vision Button - Navigation":
        target_window = st.text_input("Target Window:")
        if st.button("🎯 Generate") and component_name and target_window:
            context = {
                "component_name": component_name,
                "action_type": "navigation",
                "target_window": target_window,
                "logging_enabled": True
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
                "logging_enabled": True
            }
            generate_quick_script("vision/button_click_handler.jinja2", context)


def generate_quick_script(template: str, context: Dict[str, Any]) -> None:
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
        with cols[idx % 2]:
            with st.expander(f"📄 {template}"):
                template_path = Path("templates") / template
                if template_path.exists():
                    with open(template_path, "r") as f:
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
                        key=f"download_{idx}"
                    )


def render_validation_page() -> None:
    """Render the validation page."""
    st.markdown("## ✅ Script Validation")
    
    st.info("🚧 Script validation features are coming soon!")
    
    # Placeholder for validation features
    st.markdown("""
    ### Planned Validation Features:
    
    - **Jython Syntax Validation** - Check for Jython 2.7 compatibility
    - **Ignition API Validation** - Verify system function usage
    - **Template Configuration Validation** - Validate config against template requirements
    - **Script Performance Analysis** - Check for common performance issues
    - **Security Scanning** - Identify potential security concerns
    """)


def render_export_page() -> None:
    """Render the export page."""
    st.markdown("## 📦 Project Export")
    
    st.info("🚧 Project export features are coming soon!")
    
    st.markdown("""
    ### Planned Export Features:
    
    - **Gateway Backup Format** - Export as .gwbk files
    - **Project Archive** - Create Ignition project zips
    - **Resource Export** - Export individual resources
    - **Version Control Preparation** - Structure for git integration
    - **Deployment Packages** - Ready-to-deploy script packages
    """)


def render_docs_page() -> None:
    """Render the documentation page."""
    st.markdown("## 📚 Documentation")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Getting Started", "Templates", "CLI Usage", "Examples"])
    
    with tab1:
        st.markdown("""
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
        """)
    
    with tab2:
        st.markdown("""
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
        """)
    
    with tab3:
        st.markdown("""
        ### 💻 CLI Usage
        
        The CLI provides the same functionality as this web interface:
        
        ```bash
        # List available templates
        python -m src.core.cli template list
        
        # Generate script from template
        python -m src.core.cli script generate \\
          --template vision/button_click_handler \\
          --component-name "MainButton" \\
          --output my_script.py
        
        # Generate from configuration file
        python -m src.core.cli script generate \\
          --config config.json \\
          --output script.py
        
        # Validate configuration
        python -m src.core.cli template validate \\
          template_name config.json
        ```
        """)
    
    with tab4:
        st.markdown("""
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
        """)


def main() -> None:
    """Main application entry point."""
    init_session_state()
    render_header()
    
    # Get selected page from sidebar
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    current_page = render_sidebar()
    if current_page != st.session_state.page:
        st.session_state.page = current_page
    
    # Render the selected page
    if st.session_state.page == "home":
        render_home_page()
    elif st.session_state.page == "generator":
        render_generator_page()
    elif st.session_state.page == "templates":
        render_templates_page()
    elif st.session_state.page == "validation":
        render_validation_page()
    elif st.session_state.page == "export":
        render_export_page()
    elif st.session_state.page == "docs":
        render_docs_page()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "IGN Scripts v0.1.0 | Built for Ignition SCADA | "
        "<a href='https://github.com/your-repo/ign-scripts'>GitHub</a>"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main() 