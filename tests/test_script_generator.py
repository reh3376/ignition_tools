"""Tests for the IgnitionScriptGenerator class."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, Mock

from src.ignition.generators.script_generator import IgnitionScriptGenerator


class TestIgnitionScriptGenerator:
    """Test cases for the IgnitionScriptGenerator class."""

    @pytest.mark.unit
    def test_generator_initialization(self, script_generator):
        """Test that generator initializes correctly."""
        assert script_generator is not None
        assert hasattr(script_generator, 'env')
        assert hasattr(script_generator, 'templates_dir')

    @pytest.mark.unit
    def test_list_templates(self, script_generator):
        """Test listing available templates."""
        templates = script_generator.list_templates()
        assert isinstance(templates, list)
        # Should find at least our existing template
        assert any("button_click_handler" in template for template in templates)

    @pytest.mark.unit
    def test_generate_script_with_navigation(self, script_generator, sample_button_config, captured_logs):
        """Test generating a navigation script."""
        with captured_logs as logs:
            result = script_generator.generate_script(
                sample_button_config["template"], 
                sample_button_config
            )
        
        assert result is not None
        assert isinstance(result, str)
        assert "TestButton" in result
        assert "TestWindow" in result
        assert "system.nav.openWindow" in result
        assert "logger" in result
        
        # Check that logging happened
        log_messages = logs.get_messages()
        assert any("Generating script" in msg for msg in log_messages)

    @pytest.mark.unit
    def test_generate_script_with_tag_write(self, script_generator, sample_tag_write_config):
        """Test generating a tag write script."""
        result = script_generator.generate_script(
            sample_tag_write_config["template"],
            sample_tag_write_config
        )
        
        assert result is not None
        assert "TagWriteButton" in result
        assert "system.tag.write" in result
        assert "[default]TestTag" in result
        assert "test_value" in result

    @pytest.mark.unit
    def test_generate_script_with_custom_code(self, script_generator, sample_custom_config):
        """Test generating a script with custom code."""
        result = script_generator.generate_script(
            sample_custom_config["template"],
            sample_custom_config
        )
        
        assert result is not None
        assert "CustomButton" in result
        assert "Hello from custom code" in result
        # Should not have logging since it's disabled
        assert "logger" not in result.lower()

    @pytest.mark.unit
    def test_generate_from_config(self, script_generator, sample_button_config):
        """Test generating script from configuration dict."""
        result = script_generator.generate_from_config(sample_button_config)
        
        assert result is not None
        assert "TestButton" in result
        assert "TestWindow" in result

    @pytest.mark.unit
    def test_invalid_template_handling(self, script_generator):
        """Test handling of invalid template names."""
        with pytest.raises(Exception):
            script_generator.generate_script("nonexistent/template.jinja2", {})

    @pytest.mark.unit
    def test_missing_required_fields(self, script_generator):
        """Test handling of missing required fields."""
        incomplete_config = {
            "template": "vision/button_click_handler.jinja2",
            # Missing component_name
        }
        
        # Should still work but might produce incomplete script
        result = script_generator.generate_script(
            incomplete_config["template"],
            incomplete_config
        )
        assert result is not None

    @pytest.mark.unit
    def test_jython_json_filter(self, script_generator):
        """Test the custom Jython JSON filter."""
        test_data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        # Test the filter directly
        jython_filter = script_generator.env.filters['jython_json']
        result = jython_filter(test_data)
        
        assert isinstance(result, str)
        assert "True" in result  # Python True -> Jython True
        assert "None" in result  # Python None -> Jython None

    @pytest.mark.performance
    def test_generation_performance(self, script_generator, sample_button_config, performance_monitor):
        """Test script generation performance."""
        performance_monitor.start()
        
        # Generate multiple scripts
        for _ in range(10):
            script_generator.generate_script(
                sample_button_config["template"],
                sample_button_config
            )
        
        performance_monitor.stop()
        
        duration = performance_monitor.get_duration()
        assert duration is not None
        assert duration < 5.0  # Should complete in under 5 seconds

    @pytest.mark.integration
    def test_real_template_generation(self, script_generator):
        """Integration test with real template files."""
        config = {
            "component_name": "IntegrationTestButton",
            "action_type": "navigation",
            "target_window": "IntegrationWindow",
            "logging_enabled": True
        }
        
        templates = script_generator.list_templates()
        button_template = next(
            (t for t in templates if "button_click_handler" in t), 
            None
        )
        
        if button_template:
            result = script_generator.generate_script(button_template, config)
            assert result is not None
            assert "IntegrationTestButton" in result

    @pytest.mark.unit
    def test_template_context_variables(self, script_generator):
        """Test that all expected template variables are available."""
        import datetime
        
        config = {
            "component_name": "ContextTestButton",
            "description": "Test description",
            "action_type": "navigation",
            "target_window": "TestWindow",
            "logging_enabled": True,
            "logger_name": "TestLogger",
            "show_error_popup": True,
            "reraise_errors": False
        }
        
        templates = script_generator.list_templates()
        button_template = next(
            (t for t in templates if "button_click_handler" in t), 
            None
        )
        
        if button_template:
            result = script_generator.generate_script(button_template, config)
            
            # Check that variables were substituted
            assert "ContextTestButton" in result
            assert "Test description" in result
            assert "TestWindow" in result
            assert "TestLogger" in result

    @pytest.mark.unit
    def test_error_handling_options(self, script_generator):
        """Test different error handling configurations."""
        configs = [
            {"show_error_popup": True, "reraise_errors": False},
            {"show_error_popup": False, "reraise_errors": True},
            {"show_error_popup": True, "reraise_errors": True},
            {"show_error_popup": False, "reraise_errors": False}
        ]
        
        base_config = {
            "component_name": "ErrorTestButton",
            "action_type": "navigation",
            "target_window": "TestWindow"
        }
        
        templates = script_generator.list_templates()
        button_template = next(
            (t for t in templates if "button_click_handler" in t), 
            None
        )
        
        if button_template:
            for error_config in configs:
                config = {**base_config, **error_config}
                result = script_generator.generate_script(button_template, config)
                assert result is not None
                
                if error_config["show_error_popup"]:
                    assert "system.gui.errorBox" in result
                if error_config["reraise_errors"]:
                    assert "raise" in result

    @pytest.mark.unit
    def test_logging_configuration(self, script_generator):
        """Test different logging configurations."""
        configs = [
            {"logging_enabled": True, "logger_name": "CustomLogger"},
            {"logging_enabled": True},  # Default logger name
            {"logging_enabled": False}  # No logging
        ]
        
        base_config = {
            "component_name": "LoggingTestButton",
            "action_type": "navigation",
            "target_window": "TestWindow"
        }
        
        templates = script_generator.list_templates()
        button_template = next(
            (t for t in templates if "button_click_handler" in t), 
            None
        )
        
        if button_template:
            for log_config in configs:
                config = {**base_config, **log_config}
                result = script_generator.generate_script(button_template, config)
                assert result is not None
                
                if log_config["logging_enabled"]:
                    assert "logger" in result
                    assert "system.util.getLogger" in result
                    if "logger_name" in log_config:
                        assert log_config["logger_name"] in result
                else:
                    assert "logger" not in result.lower() 