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


class TestOptionValidation:
    """Bounded parameter types reject nonsense as usage errors (exit 2)."""

    def test_timeout_zero_rejected(self, runner):
        result = runner.invoke(main, ["--timeout", "0", "advisories", "get_advisories_packages"])
        assert result.exit_code == 2
        assert "Invalid value" in result.output + result.stderr

    def test_timeout_negative_rejected(self, runner):
        result = runner.invoke(main, ["advisories", "get_advisories_packages", "--timeout", "-5"])
        assert result.exit_code == 2

    def test_timeout_astronomical_rejected(self, runner):
        result = runner.invoke(main, ["--timeout", "99999999999999999999", "advisories", "get_advisories_packages"])
        assert result.exit_code == 2

    def test_polling_interval_negative_rejected(self, runner):
        result = runner.invoke(main, ["resolve", "create_job", "express", "npmjs.org", "--polling-interval", "-1"])
        assert result.exit_code == 2

    def test_max_wait_zero_rejected(self, runner):
        result = runner.invoke(main, ["resolve", "create_job", "express", "npmjs.org", "--max-wait", "0"])
        assert result.exit_code == 2


class TestFormatPrecedence:
    """Leaf-level --format beats outer levels even when it equals the default."""

    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_leaf_format_table_wins_over_root_json(self, mock_print_output, runner, mock_api_client):
        result = runner.invoke(
            main,
            ["--format", "json", "advisories", "get_advisories_packages", "--format", "table"],
        )

        assert result.exit_code == 0
        # print_output(data, format, console=...) — the leaf's explicit
        # "table" must win over the root's "json".
        assert mock_print_output.call_args[0][1] == "table"

    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_root_format_inherited_when_leaf_unset(self, mock_print_output, runner, mock_api_client):
        result = runner.invoke(main, ["--format", "json", "advisories", "get_advisories_packages"])

        assert result.exit_code == 0
        assert mock_print_output.call_args[0][1] == "json"


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


class TestVersionOption:
    """The conventional --version flag, alongside the version subcommand."""

    def test_version_flag(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output


class TestPaginationValidation:
    """page/per_page are validated client-side instead of causing server 500s."""

    def test_per_page_zero_rejected_on_generated_command(self, runner):
        result = runner.invoke(main, ["packages", "get_registries", "--per-page", "0"])
        assert result.exit_code == 2

    def test_page_negative_rejected_on_generated_command(self, runner):
        result = runner.invoke(main, ["docker", "get_packages", "--page", "-5"])
        assert result.exit_code == 2

    def test_per_page_negative_rejected_on_manual_advisories_command(self, runner):
        result = runner.invoke(main, ["advisories", "get_advisories", "--per-page", "-1"])
        assert result.exit_code == 2


class TestBrokenPipe:
    """A consumer closing the pipe (| head) is not an error."""

    @mock.patch("ecosystems_cli.commands.execution.print_output", side_effect=BrokenPipeError)
    def test_broken_pipe_exits_141_without_error_panel(self, _mock_print, runner, mock_api_client):
        result = runner.invoke(main, ["advisories", "get_advisories_packages"])

        # 141 = 128 + SIGPIPE, the conventional status for a closed pipe.
        assert result.exit_code == 141
        assert "Unexpected error" not in result.output + result.stderr
