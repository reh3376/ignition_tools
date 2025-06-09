"""Tests for the CLI module."""

import pytest
from click.testing import CliRunner

from src.core.cli import main


class TestCLI:
    """Test cases for the CLI interface."""

    def test_main_command(self) -> None:
        """Test that the main command runs without error."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "IGN Scripts" in result.output

    def test_version_command(self) -> None:
        """Test that the version command works."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_dataset_subcommand(self) -> None:
        """Test that dataset subcommand exists."""
        runner = CliRunner()
        result = runner.invoke(main, ["dataset", "--help"])
        assert result.exit_code == 0
        assert "Dataset management commands" in result.output

    def test_schema_subcommand(self) -> None:
        """Test that schema subcommand exists."""
        runner = CliRunner()
        result = runner.invoke(main, ["schema", "--help"])
        assert result.exit_code == 0
        assert "Schema management commands" in result.output 