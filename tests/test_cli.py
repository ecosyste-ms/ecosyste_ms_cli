"""Tests for the CLI."""

import re
from unittest import mock

import pytest
from click.testing import CliRunner

from ecosystems_cli import __version__
from ecosystems_cli.cli import main


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_api_client():
    """Create a mock API client for advisories API."""
    with mock.patch("ecosystems_cli.commands.execution.api_factory") as mock_factory:
        # Mock the call method to return success
        mock_factory.call.return_value = {"result": "success"}
        yield mock_factory


class TestVersionCommand:
    """Test the version subcommand."""

    def test_version_prints_package_version(self, runner):
        """Version output must match __version__ so semantic-release stays the source of truth."""
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert result.output.strip() == __version__


class TestAdvisoriesCommands:
    """Test the advisories commands."""

    def test_advisories_get_advisories_command(self, runner, mock_api_client):
        """Test the get_advisories command for advisories."""
        # Act
        result = runner.invoke(main, ["advisories", "get_advisories"])

        # Assert
        assert result.exit_code == 0


class TestErrorHandling:
    """Test error handling in the CLI."""

    def test_api_error_handling(self, runner, mock_api_client):
        """Test handling API errors."""
        # Arrange
        mock_api_client.call.side_effect = Exception("API error")

        # Act
        result = runner.invoke(main, ["advisories", "search"])

        # Assert
        def strip_ansi(text):
            ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
            return ansi_escape.sub("", text)

        clean_output = strip_ansi(result.output)
        assert "API error" in clean_output or "Error" in clean_output

    def test_invalid_json_params(self, runner, mock_api_client):
        """Test handling invalid JSON parameters."""
        # Act
        result = runner.invoke(main, ["advisories", "call", "test_op", "-p", "{invalid json}"])

        # Assert
        assert result.exit_code != 0
