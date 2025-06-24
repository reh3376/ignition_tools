"""SME Agent Streamlit Interface - Interactive Web UI

Phase 11.3: SME Agent Integration & Interfaces
Following crawl_mcp.py methodology:
- Step 1: Environment validation first
- Step 2: Comprehensive input validation
- Step 3: Error handling with user-friendly messages
- Step 4: Modular component testing
- Step 5: Progressive complexity support
- Step 6: Resource management and cleanup

Multi-Interface Deployment:
- Streamlit web interface with conversation history
- Real-time chat interface
- File analysis capabilities
- System status monitoring
"""

import json
import logging
import time
import uuid
from datetime import datetime

import streamlit as st

from .sme_agent_module import SMEAgentModule, SMEAgentValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="SME Agent - Ignition Expert Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }

    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        background-color: #f8f9fa;
    }

    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }

    .assistant-message {
        background-color: #f1f8e9;
        border-left-color: #4caf50;
    }

    .error-message {
        background-color: #ffebee;
        border-left-color: #f44336;
    }

    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: bold;
    }

    .status-healthy {
        background-color: #4caf50;
        color: white;
    }

    .status-degraded {
        background-color: #ff9800;
        color: white;
    }

    .status-unhealthy {
        background-color: #f44336;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initialize session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "sme_agent" not in st.session_state:
        st.session_state.sme_agent = None

    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False

    if "last_response" not in st.session_state:
        st.session_state.last_response = None

    if "complexity_level" not in st.session_state:
        st.session_state.complexity_level = "standard"


@st.cache_resource
def get_sme_agent():
    """Get or create SME Agent instance with caching."""
    try:
        # Step 1: Environment Validation First
        agent = SMEAgentModule()
        validation_result = agent.validate_environment()

        if not validation_result["valid"]:
            st.error("❌ SME Agent environment validation failed")
            st.error(f"Validation errors: {validation_result.get('errors', [])}")
            return None, validation_result

        # Initialize with standard complexity for web interface
        init_result = agent.initialize_components(complexity_level="standard")
        if not init_result["success"]:
            st.error("❌ SME Agent initialization failed")
            return None, init_result

        return agent, {
            "success": True,
            "validation": validation_result,
            "initialization": init_result,
        }

    except Exception as e:
        st.error(f"❌ Failed to initialize SME Agent: {e}")
        return None, {"success": False, "error": str(e)}


def display_header():
    """Display the main header and navigation."""
    st.markdown(
        '<div class="main-header">🤖 SME Agent - Ignition Expert Assistant</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**Phase 11.3: Multi-Interface Deployment**")

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["💬 Chat", "📄 File Analysis", "📊 Status", "⚙️ Settings"]
    )

    return tab1, tab2, tab3, tab4


def display_sidebar():
    """Display sidebar with session info and controls."""
    with st.sidebar:
        st.header("🔧 Session Control")

        # Session information
        st.subheader("Session Info")
        st.text(f"Session ID: {st.session_state.session_id[:8]}...")
        st.text(f"Messages: {len(st.session_state.conversation_history)}")

        # Complexity level selector
        st.subheader("Complexity Level")
        complexity = st.selectbox(
            "Select complexity level:",
            ["basic", "standard", "advanced", "enterprise"],
            index=["basic", "standard", "advanced", "enterprise"].index(
                st.session_state.complexity_level
            ),
            help="Higher complexity levels provide more detailed responses",
        )

        if complexity != st.session_state.complexity_level:
            st.session_state.complexity_level = complexity
            st.rerun()

        # Session controls
        st.subheader("Actions")
        if st.button("🗑️ Clear History", help="Clear conversation history"):
            st.session_state.conversation_history = []
            st.session_state.last_response = None
            st.rerun()

        if st.button("🔄 New Session", help="Start a new session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.conversation_history = []
            st.session_state.last_response = None
            st.rerun()

        # Export conversation
        if st.session_state.conversation_history:
            st.subheader("Export")
            export_data = {
                "session_id": st.session_state.session_id,
                "timestamp": datetime.now().isoformat(),
                "conversation_history": st.session_state.conversation_history,
            }

            st.download_button(
                "📥 Download Chat",
                data=json.dumps(export_data, indent=2),
                file_name=f"sme_chat_{st.session_state.session_id[:8]}.json",
                mime="application/json",
            )


def display_conversation_history():
    """Display the conversation history."""
    if not st.session_state.conversation_history:
        st.info("💡 Start a conversation by asking a question below!")
        return

    st.subheader("💬 Conversation History")

    for i, message in enumerate(st.session_state.conversation_history):
        # User message
        with st.container():
            st.markdown(
                f"""
            <div class="chat-message user-message">
                <strong>🙋 You:</strong><br>
                {message["question"]}
                {f"<br><small><strong>Context:</strong> {message['context']}</small>" if message.get("context") else ""}
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Assistant response
        with st.container():
            st.markdown(
                f"""
            <div class="chat-message assistant-message">
                <strong>🤖 SME Agent:</strong><br>
                {message["response"]}
                <br><small>
                    <strong>Confidence:</strong> {message["confidence"]:.2%} |
                    <strong>Time:</strong> {message["processing_time"]:.2f}s |
                    <strong>Model:</strong> {message["model_used"]}
                </small>
            </div>
            """,
                unsafe_allow_html=True,
            )


def chat_interface():
    """Main chat interface."""
    # Get SME Agent
    agent, agent_info = get_sme_agent()

    if not agent:
        st.error("❌ SME Agent is not available. Please check the system status.")
        return

    # Display conversation history
    display_conversation_history()

    # Chat input form
    with st.form("chat_form", clear_on_submit=True):
        st.subheader("💬 Ask a Question")

        col1, col2 = st.columns([3, 1])

        with col1:
            question = st.text_area(
                "Your question:",
                placeholder="Ask anything about Ignition development, OPC-UA, database integration, etc.",
                height=100,
                help="Enter your question for the SME Agent",
            )

        with col2:
            context = st.text_area(
                "Optional context:",
                placeholder="Additional context or background information...",
                height=100,
                help="Provide additional context to help the agent understand your question better",
            )

        submitted = st.form_submit_button("🚀 Ask SME Agent", type="primary")

        if submitted and question.strip():
            # Step 2: Comprehensive Input Validation
            if len(question) > 10000:
                st.error("❌ Question is too long (max 10,000 characters)")
                return

            if context and len(context) > 20000:
                st.error("❌ Context is too long (max 20,000 characters)")
                return

            # Process question
            with st.spinner("🤔 SME Agent is thinking..."):
                try:
                    start_time = time.time()
                    response = agent.ask_question(
                        question.strip(), context.strip() if context else None
                    )

                    # Add to conversation history
                    conversation_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "question": question.strip(),
                        "context": context.strip() if context else None,
                        "response": response.response,
                        "confidence": response.confidence,
                        "sources": response.sources,
                        "processing_time": response.processing_time,
                        "model_used": response.model_used,
                        "knowledge_sources": response.knowledge_sources,
                    }

                    st.session_state.conversation_history.append(conversation_entry)
                    st.session_state.last_response = response

                    st.rerun()

                except SMEAgentValidationError as e:
                    # Step 3: Error Handling and User-Friendly Messages
                    st.error(f"❌ Validation Error: {e}")

                except Exception as e:
                    st.error(f"❌ Error processing question: {e}")
                    logger.error(f"Chat error: {e}")

        elif submitted and not question.strip():
            st.warning("⚠️ Please enter a question before submitting.")


def file_analysis_interface():
    """File analysis interface."""
    st.subheader("📄 File Analysis")
    st.markdown("Upload a file or paste content for analysis by the SME Agent.")

    # Get SME Agent
    agent, agent_info = get_sme_agent()

    if not agent:
        st.error("❌ SME Agent is not available. Please check the system status.")
        return

    # File upload or text input
    analysis_method = st.radio(
        "Choose analysis method:", ["Upload File", "Paste Content"], horizontal=True
    )

    if analysis_method == "Upload File":
        uploaded_file = st.file_uploader(
            "Choose a file to analyze:",
            type=["py", "txt", "md", "json", "yaml", "yml", "xml", "sql"],
            help="Upload a file for analysis (max 100KB)",
        )

        if uploaded_file:
            # Check file size
            if uploaded_file.size > 100000:  # 100KB limit
                st.error("❌ File too large (max 100KB)")
                return

            try:
                content = uploaded_file.read().decode("utf-8")
                filename = uploaded_file.name
            except UnicodeDecodeError:
                st.error("❌ Could not decode file. Please ensure it's a text file.")
                return
        else:
            content = None
            filename = None

    else:  # Paste Content
        content = st.text_area(
            "Paste your content here:",
            height=200,
            placeholder="Paste the content you want to analyze...",
            help="Paste content directly for analysis (max 100,000 characters)",
        )
        filename = st.text_input("Optional filename:", placeholder="example.py")

        if content and len(content) > 100000:
            st.error("❌ Content too long (max 100,000 characters)")
            return

    # Analysis button
    if st.button("🔍 Analyze", type="primary", disabled=not content):
        if content:
            with st.spinner("🔍 Analyzing content..."):
                try:
                    # Create analysis question
                    question = "Please analyze this file and provide insights about its structure, purpose, and potential improvements."
                    context = f"Filename: {filename or 'unknown'}\nContent:\n{content[:5000]}..."  # Limit context size

                    # Process analysis
                    response = agent.ask_question(question, context)

                    # Display results
                    st.success("✅ Analysis complete!")

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.subheader("📋 Analysis Results")
                        st.markdown(response.response)

                    with col2:
                        st.subheader("📊 Metadata")
                        st.metric("Confidence", f"{response.confidence:.2%}")
                        st.metric("Processing Time", f"{response.processing_time:.2f}s")
                        st.text(f"Model: {response.model_used}")

                        if response.sources:
                            st.subheader("📚 Sources")
                            for source in response.sources:
                                st.text(f"• {source}")

                        if response.knowledge_sources:
                            st.subheader("🧠 Knowledge Sources")
                            for ks in response.knowledge_sources:
                                st.text(f"• {ks}")

                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
                    logger.error(f"Analysis error: {e}")


def status_interface():
    """System status interface."""
    st.subheader("📊 System Status")

    # Get SME Agent
    agent, agent_info = get_sme_agent()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🤖 SME Agent Status")

        if agent:
            try:
                status = agent.get_status()

                # Overall status
                if status["initialized"]:
                    st.markdown(
                        '<span class="status-badge status-healthy">✅ Operational</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<span class="status-badge status-degraded">⚠️ Degraded</span>',
                        unsafe_allow_html=True,
                    )

                # Component status
                st.subheader("🔧 Components")
                for component, status_val in status["components"].items():
                    icon = "✅" if status_val else "❌"
                    st.text(
                        f"{icon} {component.replace('_', ' ').title()}: {'Ready' if status_val else 'Not Available'}"
                    )

                # Configuration
                st.subheader("⚙️ Configuration")
                config = status["config"]
                st.text(f"Model: {config['model_name']}")
                st.text(
                    f"Knowledge Graph: {'Enabled' if config['use_knowledge_graph'] else 'Disabled'}"
                )
                st.text(
                    f"Vector Embeddings: {'Enabled' if config['use_vector_embeddings'] else 'Disabled'}"
                )

            except Exception as e:
                st.error(f"❌ Failed to get status: {e}")
        else:
            st.markdown(
                '<span class="status-badge status-unhealthy">❌ Not Available</span>',
                unsafe_allow_html=True,
            )

    with col2:
        st.subheader("💾 Session Information")
        st.text(f"Session ID: {st.session_state.session_id}")
        st.text(
            f"Conversation Length: {len(st.session_state.conversation_history)} messages"
        )
        st.text(f"Complexity Level: {st.session_state.complexity_level}")

        if agent_info and agent_info.get("success"):
            st.subheader("✅ Initialization Info")
            validation = agent_info.get("validation", {})
            if validation.get("valid"):
                st.success("Environment validation: ✅ Passed")
            else:
                st.error("Environment validation: ❌ Failed")

            initialization = agent_info.get("initialization", {})
            if initialization.get("success"):
                st.success("Component initialization: ✅ Success")
            else:
                st.error("Component initialization: ❌ Failed")

        # Performance metrics
        if st.session_state.conversation_history:
            st.subheader("📈 Performance Metrics")
            processing_times = [
                msg["processing_time"] for msg in st.session_state.conversation_history
            ]
            confidences = [
                msg["confidence"] for msg in st.session_state.conversation_history
            ]

            st.metric(
                "Avg Processing Time",
                f"{sum(processing_times) / len(processing_times):.2f}s",
            )
            st.metric("Avg Confidence", f"{sum(confidences) / len(confidences):.2%}")


def settings_interface():
    """Settings and configuration interface."""
    st.subheader("⚙️ Settings")

    # Step 5: Progressive Complexity Support
    st.subheader("🎛️ Complexity Configuration")
    st.markdown(
        """
    **Complexity Levels:**
    - **Basic**: Simple responses, faster processing
    - **Standard**: Balanced responses with good detail
    - **Advanced**: Detailed responses with comprehensive analysis
    - **Enterprise**: Maximum detail with enterprise-grade insights
    """
    )

    # Environment information
    st.subheader("🌍 Environment Information")
    agent, agent_info = get_sme_agent()

    if agent and agent_info.get("success"):
        validation = agent_info.get("validation", {})

        with st.expander("🔍 Environment Validation Details"):
            st.json(validation)

        with st.expander("🔧 Component Status Details"):
            try:
                status = agent.get_status()
                st.json(status)
            except Exception as e:
                st.error(f"Failed to get detailed status: {e}")

    # Interface information
    st.subheader("🌐 Interface Information")
    st.markdown(
        """
    **Available Interfaces:**
    - **Streamlit Web UI**: Current interface (you are here)
    - **FastAPI REST API**: Programmatic access with streaming
    - **CLI Commands**: Terminal-based interaction
    - **Future Designer Integration**: Planned for future releases
    """
    )

    # Documentation links
    st.subheader("📚 Documentation")
    st.markdown(
        """
    **Useful Links:**
    - [Phase 11.3 Roadmap](docs/roadmap.md#phase-113)
    - [SME Agent CLI Commands](docs/api/cli-interface.md)
    - [API Documentation](http://localhost:8000/docs) (when FastAPI server is running)
    """
    )


def main():
    """Main Streamlit application."""
    # Step 1: Environment Validation First (handled in get_sme_agent)
    initialize_session_state()

    # Display header and get tabs
    tab1, tab2, tab3, tab4 = display_header()

    # Display sidebar
    display_sidebar()

    # Tab content
    with tab1:
        chat_interface()

    with tab2:
        file_analysis_interface()

    with tab3:
        status_interface()

    with tab4:
        settings_interface()

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666; font-size: 0.875rem;">
        🤖 SME Agent Web Interface - Phase 11.3: Multi-Interface Deployment<br>
        Ignition Scripts Project - Code Intelligence System
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
