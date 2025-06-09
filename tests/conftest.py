"""Pytest configuration and fixtures for IGN Scripts testing."""

import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock

import pytest
from unittest.mock import patch

from src.ignition.generators.script_generator import IgnitionScriptGenerator


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def sample_templates_dir():
    """Fixture providing path to sample templates."""
    return Path(__file__).parent.parent / "templates"


@pytest.fixture
def temp_dir():
    """Fixture providing a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def script_generator():
    """Fixture providing a configured IgnitionScriptGenerator instance."""
    generator = IgnitionScriptGenerator()
    return generator


@pytest.fixture
def sample_button_config():
    """Fixture providing a sample button configuration."""
    return {
        "template": "vision/button_click_handler.jinja2",
        "component_name": "TestButton",
        "description": "Test button for automated testing",
        "action_type": "navigation",
        "target_window": "TestWindow",
        "window_params": {
            "test_param": "test_value"
        },
        "logging_enabled": True,
        "logger_name": "TestHandler",
        "show_error_popup": True,
        "reraise_errors": False
    }


@pytest.fixture
def sample_tag_write_config():
    """Fixture providing a sample tag write configuration."""
    return {
        "template": "vision/button_click_handler.jinja2",
        "component_name": "TagWriteButton",
        "description": "Test tag write button",
        "action_type": "tag_write",
        "target_tag": "[default]TestTag",
        "tag_value": "test_value",
        "logging_enabled": True,
        "logger_name": "TagWriteHandler"
    }


@pytest.fixture
def sample_custom_config():
    """Fixture providing a sample custom code configuration."""
    return {
        "template": "vision/button_click_handler.jinja2",
        "component_name": "CustomButton",
        "description": "Test custom code button",
        "action_type": "custom",
        "custom_code": "print('Hello from custom code')",
        "logging_enabled": False
    }


@pytest.fixture
def mock_template_files(temp_dir):
    """Fixture creating mock template files for testing."""
    templates_dir = temp_dir / "templates" / "vision"
    templates_dir.mkdir(parents=True)
    
    # Create a simple test template
    test_template = templates_dir / "test_template.jinja2"
    test_template.write_text("""
# Test Template - {{ component_name }}
# Generated: {{ timestamp }}

def test_function():
    {% if logging_enabled %}
    logger = system.util.getLogger("{{ logger_name or 'TestLogger' }}")
    logger.info("Test function called")
    {% endif %}
    
    {% if action_type == "test" %}
    print("Test action executed")
    {% endif %}
    
    return "Test completed"
""".strip())
    
    return templates_dir


@pytest.fixture
def mock_ignition_system():
    """Fixture providing mock Ignition system functions."""
    mock_system = Mock()
    
    # Mock navigation
    mock_system.nav.openWindow = Mock()
    mock_system.nav.openWindowInstance = Mock()
    mock_system.nav.swapWindow = Mock()
    
    # Mock tag operations
    mock_system.tag.write = Mock()
    mock_system.tag.read = Mock()
    mock_system.tag.writeBlocking = Mock()
    
    # Mock logging
    mock_logger = Mock()
    mock_system.util.getLogger = Mock(return_value=mock_logger)
    
    # Mock GUI
    mock_system.gui.errorBox = Mock()
    mock_system.gui.warningBox = Mock()
    mock_system.gui.messageBox = Mock()
    
    # Mock database
    mock_system.db.runQuery = Mock(return_value=[])
    mock_system.db.runUpdateQuery = Mock(return_value=1)
    
    return mock_system


@pytest.fixture
def captured_logs():
    """Fixture for capturing log messages during tests."""
    class LogCapture:
        def __init__(self):
            self.records = []
            self.handler = None
            
        def __enter__(self):
            self.handler = logging.Handler()
            self.handler.emit = lambda record: self.records.append(record)
            
            # Get the root logger and add our handler
            logger = logging.getLogger()
            logger.addHandler(self.handler)
            logger.setLevel(logging.DEBUG)
            
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.handler:
                logging.getLogger().removeHandler(self.handler)
                
        def get_messages(self, level=None):
            """Get captured log messages, optionally filtered by level."""
            if level is None:
                return [record.getMessage() for record in self.records]
            return [record.getMessage() for record in self.records 
                   if record.levelno >= level]
    
    return LogCapture()


@pytest.fixture
def performance_monitor():
    """Fixture for monitoring performance during tests."""
    import time
    import psutil
    import os
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.process = psutil.Process(os.getpid())
            self.start_memory = None
            self.end_memory = None
            
        def start(self):
            self.start_time = time.time()
            self.start_memory = self.process.memory_info().rss
            
        def stop(self):
            self.end_time = time.time()
            self.end_memory = self.process.memory_info().rss
            
        def get_duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
            
        def get_memory_usage(self):
            if self.start_memory and self.end_memory:
                return self.end_memory - self.start_memory
            return None
    
    return PerformanceMonitor()


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Automatically configure logging for all tests."""
    import logging
    
    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/test.log'),
            logging.StreamHandler()
        ]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    yield
    
    # Clean up handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


@pytest.fixture
def mock_streamlit():
    """Fixture for mocking Streamlit components in UI tests."""
    with patch('streamlit.title'), \
         patch('streamlit.header'), \
         patch('streamlit.subheader'), \
         patch('streamlit.text'), \
         patch('streamlit.markdown'), \
         patch('streamlit.button'), \
         patch('streamlit.selectbox'), \
         patch('streamlit.text_input'), \
         patch('streamlit.text_area'), \
         patch('streamlit.checkbox'), \
         patch('streamlit.radio'), \
         patch('streamlit.columns'), \
         patch('streamlit.sidebar'), \
         patch('streamlit.expander'):
        yield


@pytest.fixture
def environment_variables():
    """Fixture for setting test environment variables."""
    import os
    
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ['TESTING_MODE'] = 'true'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    os.environ['PYTHONPATH'] = str(Path(__file__).parent.parent)
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env) 