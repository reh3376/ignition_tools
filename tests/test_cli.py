"""Tests for the CLI functionality."""

import pytest
import json
import tempfile
from pathlib import Path
from click.testing import CliRunner

from src.core.cli import main as cli


class TestCLI:
    """Test cases for the CLI functionality."""

    @pytest.fixture
    def runner(self):
        """Fixture providing a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_output_dir(self):
        """Fixture providing a temporary output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.mark.unit
    def test_cli_help(self, runner):
        """Test that CLI help works."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'IGN Scripts' in result.output
        assert 'script' in result.output
        assert 'template' in result.output

    @pytest.mark.unit
    def test_template_list_command(self, runner):
        """Test the template list command."""
        result = runner.invoke(cli, ['template', 'list'])
        assert result.exit_code == 0
        # Should show available templates
        assert 'Available templates' in result.output or 'button_click_handler' in result.output

    @pytest.mark.unit
    def test_script_generate_help(self, runner):
        """Test script generate command help."""
        result = runner.invoke(cli, ['script', 'generate', '--help'])
        assert result.exit_code == 0
        assert 'template' in result.output
        assert 'component-name' in result.output
        assert 'output' in result.output

    @pytest.mark.integration
    def test_script_generate_from_template(self, runner, temp_output_dir):
        """Test generating a script from template via CLI."""
        output_file = temp_output_dir / "test_script.py"
        
        result = runner.invoke(cli, [
            'script', 'generate',
            '--template', 'vision/button_click_handler.jinja2',
            '--component-name', 'CLITestButton',
            '--output', str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        content = output_file.read_text()
        assert 'CLITestButton' in content
        assert 'def handle_button_click' in content

    @pytest.mark.integration
    def test_script_generate_from_config(self, runner, temp_output_dir):
        """Test generating a script from config file via CLI."""
        # Create test config file
        config = {
            "template": "vision/button_click_handler.jinja2",
            "component_name": "ConfigTestButton",
            "action_type": "navigation",
            "target_window": "TestWindow",
            "logging_enabled": True
        }
        
        config_file = temp_output_dir / "test_config.json"
        config_file.write_text(json.dumps(config, indent=2))
        
        output_file = temp_output_dir / "config_script.py"
        
        result = runner.invoke(cli, [
            'script', 'generate',
            '--config', str(config_file),
            '--output', str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        content = output_file.read_text()
        assert 'ConfigTestButton' in content
        assert 'TestWindow' in content

    @pytest.mark.unit
    def test_script_generate_missing_args(self, runner):
        """Test script generate with missing required arguments."""
        result = runner.invoke(cli, ['script', 'generate'])
        assert result.exit_code != 0
        assert 'Error' in result.output or 'Missing' in result.output

    @pytest.mark.integration
    def test_template_validate_command(self, runner, temp_output_dir):
        """Test template validation command."""
        # Create test config
        config = {
            "component_name": "ValidateTestButton",
            "action_type": "navigation",
            "target_window": "TestWindow"
        }
        
        config_file = temp_output_dir / "validate_config.json"
        config_file.write_text(json.dumps(config, indent=2))
        
        result = runner.invoke(cli, [
            'template', 'validate',
            'vision/button_click_handler.jinja2',
            str(config_file)
        ])
        
        # Should not error (validation should pass)
        assert result.exit_code == 0

    @pytest.mark.unit
    def test_invalid_template_name(self, runner, temp_output_dir):
        """Test handling of invalid template names."""
        output_file = temp_output_dir / "invalid_script.py"
        
        result = runner.invoke(cli, [
            'script', 'generate',
            '--template', 'nonexistent/template.jinja2',
            '--component-name', 'TestButton',
            '--output', str(output_file)
        ])
        
        assert result.exit_code != 0
        assert not output_file.exists()

    @pytest.mark.unit
    def test_invalid_config_file(self, runner, temp_output_dir):
        """Test handling of invalid config files."""
        # Create invalid config file
        config_file = temp_output_dir / "invalid_config.json"
        config_file.write_text("{ invalid json")
        
        output_file = temp_output_dir / "invalid_script.py"
        
        result = runner.invoke(cli, [
            'script', 'generate',
            '--config', str(config_file),
            '--output', str(output_file)
        ])
        
        assert result.exit_code != 0
        assert not output_file.exists()

    @pytest.mark.unit
    def test_output_to_stdout(self, runner):
        """Test generating script to stdout."""
        result = runner.invoke(cli, [
            'script', 'generate',
            '--template', 'vision/button_click_handler.jinja2',
            '--component-name', 'StdoutTestButton'
        ])
        
        assert result.exit_code == 0
        assert 'StdoutTestButton' in result.output
        assert 'def handle_button_click' in result.output

    @pytest.mark.performance
    def test_cli_performance(self, runner, temp_output_dir, performance_monitor):
        """Test CLI performance for script generation."""
        performance_monitor.start()
        
        output_file = temp_output_dir / "perf_test_script.py"
        
        result = runner.invoke(cli, [
            'script', 'generate',
            '--template', 'vision/button_click_handler.jinja2',
            '--component-name', 'PerformanceTestButton',
            '--output', str(output_file)
        ])
        
        performance_monitor.stop()
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        duration = performance_monitor.get_duration()
        assert duration is not None
        assert duration < 2.0  # Should complete quickly

    @pytest.mark.integration
    def test_cli_with_all_options(self, runner, temp_output_dir):
        """Test CLI with all available options."""
        output_file = temp_output_dir / "full_options_script.py"
        
        result = runner.invoke(cli, [
            'script', 'generate',
            '--template', 'vision/button_click_handler.jinja2',
            '--component-name', 'FullOptionsButton',
            '--action-type', 'navigation',
            '--target-window', 'FullOptionsWindow',
            '--logging-enabled',
            '--logger-name', 'FullOptionsLogger',
            '--output', str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        content = output_file.read_text()
        assert 'FullOptionsButton' in content
        assert 'FullOptionsWindow' in content
        assert 'FullOptionsLogger' in content

    @pytest.mark.unit
    def test_cli_verbose_output(self, runner, temp_output_dir):
        """Test CLI verbose output mode."""
        output_file = temp_output_dir / "verbose_script.py"
        
        result = runner.invoke(cli, [
            'script', 'generate',
            '--template', 'vision/button_click_handler.jinja2',
            '--component-name', 'VerboseTestButton',
            '--output', str(output_file),
            '--verbose'
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        # Verbose mode should show additional output
        assert len(result.output) > 0 