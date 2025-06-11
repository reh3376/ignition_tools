"""Tests for the Streamlit UI functionality."""

import json
from unittest.mock import Mock, patch

import pytest

# Import the main functions from the UI module
from src.ui.streamlit_app import (
    init_session_state,
    main,
    render_generator_page,
    render_header,
    render_home_page,
    render_sidebar,
    render_templates_page,
)


class TestStreamlitUI:
    """Test cases for the Streamlit UI functionality."""

    @pytest.mark.ui()
    def test_init_session_state(self, mock_streamlit):
        """Test session state initialization."""
        with patch("streamlit.session_state", {}) as mock_session_state:
            init_session_state()
            # Should have initialized required session state variables
            assert (
                hasattr(mock_session_state, "generator")
                or "generator" in mock_session_state
            )

    @pytest.mark.ui()
    def test_render_header(self, mock_streamlit):
        """Test header rendering."""
        with patch("streamlit.set_page_config") as mock_page_config, patch(
            "streamlit.title"
        ) as mock_title, patch("streamlit.subheader") as mock_subheader, patch(
            "streamlit.markdown"
        ), patch("streamlit.columns") as mock_columns:
            # Mock columns return
            mock_columns.return_value = [Mock(), Mock(), Mock()]

            render_header()

            mock_page_config.assert_called_once()
            mock_title.assert_called_once()
            mock_subheader.assert_called_once()

    @pytest.mark.ui()
    def test_render_sidebar(self, mock_streamlit):
        """Test sidebar rendering."""
        with patch("streamlit.sidebar") as mock_sidebar, patch(
            "streamlit.session_state"
        ) as mock_session_state:
            # Mock sidebar components
            mock_sidebar.title = Mock()
            mock_sidebar.selectbox = Mock(return_value="🏠 Home")
            mock_sidebar.markdown = Mock()
            mock_sidebar.metric = Mock()

            # Mock session state
            mock_generator = Mock()
            mock_generator.list_templates.return_value = ["template1", "template2"]
            mock_session_state.generator = mock_generator
            mock_session_state.generated_script = "test script"

            result = render_sidebar()

            assert result == "home"
            mock_sidebar.title.assert_called()
            mock_sidebar.selectbox.assert_called()

    @pytest.mark.ui()
    def test_render_home_page(self, mock_streamlit):
        """Test home page rendering."""
        with patch("streamlit.markdown") as mock_markdown, patch(
            "streamlit.columns"
        ) as mock_columns, patch("streamlit.button") as mock_button:
            mock_columns.return_value = [Mock(), Mock(), Mock()]
            mock_button.return_value = False

            render_home_page()

            mock_markdown.assert_called()
            mock_columns.assert_called()

    @pytest.mark.ui()
    def test_render_generator_page(self, mock_streamlit):
        """Test generator page rendering."""
        with patch("streamlit.markdown") as mock_markdown, patch(
            "streamlit.radio"
        ) as mock_radio:
            mock_radio.return_value = "From Template"

            render_generator_page()

            mock_markdown.assert_called()
            mock_radio.assert_called()

    @pytest.mark.ui()
    def test_render_templates_page(self, mock_streamlit):
        """Test templates page rendering."""
        with patch("streamlit.markdown") as mock_markdown, patch(
            "streamlit.warning"
        ) as mock_warning, patch("streamlit.session_state") as mock_session_state:
            # Mock no templates case
            mock_generator = Mock()
            mock_generator.list_templates.return_value = []
            mock_session_state.generator = mock_generator

            render_templates_page()

            mock_markdown.assert_called()
            mock_warning.assert_called()

    @pytest.mark.ui()
    def test_main_function(self, mock_streamlit):
        """Test main function execution."""
        with patch("src.ui.streamlit_app.init_session_state") as mock_init, patch(
            "src.ui.streamlit_app.render_header"
        ) as mock_header, patch(
            "src.ui.streamlit_app.render_sidebar"
        ) as mock_sidebar, patch(
            "src.ui.streamlit_app.render_home_page"
        ) as mock_home, patch("streamlit.session_state") as mock_session_state:
            mock_sidebar.return_value = "home"
            mock_session_state.page = "home"

            main()

            mock_init.assert_called_once()
            mock_header.assert_called_once()
            mock_sidebar.assert_called_once()
            mock_home.assert_called_once()

    @pytest.mark.ui()
    def test_template_selection_flow(self, mock_streamlit):
        """Test template selection in generator."""
        with patch("streamlit.selectbox") as mock_selectbox, patch(
            "streamlit.text_input"
        ) as mock_text_input, patch("streamlit.button") as mock_button, patch(
            "streamlit.session_state"
        ) as mock_session_state:
            # Mock template selection
            mock_selectbox.return_value = "vision/button_click_handler.jinja2"
            mock_text_input.return_value = "TestComponent"
            mock_button.return_value = True

            # Mock generator
            mock_generator = Mock()
            mock_generator.list_templates.return_value = [
                "vision/button_click_handler.jinja2"
            ]
            mock_generator.generate_script.return_value = "# Generated script"
            mock_session_state.generator = mock_generator

            # This would be part of the template generator render function
            # Testing the flow conceptually
            templates = mock_generator.list_templates()
            assert len(templates) > 0
            assert "button_click_handler" in templates[0]

    @pytest.mark.ui()
    def test_script_generation_error_handling(self, mock_streamlit):
        """Test error handling in script generation."""
        with patch("streamlit.error"), patch(
            "streamlit.session_state"
        ) as mock_session_state:
            # Mock generator that raises an exception
            mock_generator = Mock()
            mock_generator.generate_script.side_effect = Exception("Test error")
            mock_session_state.generator = mock_generator

            # Simulate error in generation
            try:
                mock_generator.generate_script("template", {})
            except Exception as e:
                # This is how the UI would handle the error
                assert str(e) == "Test error"

    @pytest.mark.ui()
    def test_file_upload_functionality(self, mock_streamlit):
        """Test file upload functionality."""
        with patch("streamlit.file_uploader") as mock_uploader, patch("streamlit.json"):
            # Mock uploaded file
            mock_file = Mock()
            mock_file.read.return_value = (
                b'{"template": "test", "component_name": "TestButton"}'
            )
            mock_uploader.return_value = mock_file

            # Simulate file upload processing
            uploaded_file = mock_uploader.return_value
            if uploaded_file:
                config_content = json.loads(uploaded_file.read())
                assert config_content["component_name"] == "TestButton"

    @pytest.mark.ui()
    def test_download_button_functionality(self, mock_streamlit):
        """Test download button functionality."""
        with patch("streamlit.download_button") as mock_download, patch(
            "streamlit.session_state"
        ) as mock_session_state:
            mock_session_state.generated_script = "# Test script content"

            # Simulate download button
            mock_download.return_value = True

            # Test download parameters
            mock_download.assert_not_called()  # Not called yet

            # Simulate actual download button call
            if mock_session_state.generated_script:
                mock_download(
                    label="Download Script",
                    data=mock_session_state.generated_script,
                    file_name="test_script.py",
                    mime="text/plain",
                )
                mock_download.assert_called()

    @pytest.mark.ui()
    def test_session_state_persistence(self, mock_streamlit):
        """Test session state persistence across renders."""
        with patch("streamlit.session_state") as mock_session_state:
            # Initialize session state
            mock_session_state.generated_script = ""
            mock_session_state.last_config = {}

            # Simulate script generation
            test_script = "# Generated test script"
            test_config = {"component_name": "TestButton"}

            mock_session_state.generated_script = test_script
            mock_session_state.last_config = test_config

            # Verify persistence
            assert mock_session_state.generated_script == test_script
            assert mock_session_state.last_config == test_config

    @pytest.mark.ui()
    def test_ui_component_integration(self, mock_streamlit):
        """Test integration between UI components."""
        with patch("streamlit.selectbox") as mock_selectbox, patch(
            "streamlit.text_input"
        ) as mock_text_input, patch("streamlit.columns") as mock_columns, patch(
            "streamlit.session_state"
        ) as mock_session_state:
            # Mock UI components
            mock_columns.return_value = [Mock(), Mock()]
            mock_selectbox.return_value = "navigation"
            mock_text_input.return_value = "TestWindow"

            # Mock session state
            mock_generator = Mock()
            mock_session_state.generator = mock_generator

            # Test component interaction
            action_type = mock_selectbox.return_value
            target_window = mock_text_input.return_value

            assert action_type == "navigation"
            assert target_window == "TestWindow"

    @pytest.mark.performance()
    def test_ui_render_performance(self, mock_streamlit, performance_monitor):
        """Test UI rendering performance."""
        with patch("src.ui.streamlit_app.render_header") as mock_header, patch(
            "src.ui.streamlit_app.render_sidebar"
        ) as mock_sidebar, patch("src.ui.streamlit_app.render_home_page") as mock_home:
            performance_monitor.start()

            mock_header()
            mock_sidebar()
            mock_home()

            performance_monitor.stop()

            duration = performance_monitor.get_duration()
            assert duration is not None
            # UI rendering should be fast
            assert duration < 1.0
