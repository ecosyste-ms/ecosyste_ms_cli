"""Tests for awesome-specific CLI behavior."""

from unittest import mock

import pytest
from click.testing import CliRunner

from ecosystems_cli.cli import main as cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_api_factory():
    with mock.patch("ecosystems_cli.commands.execution.api_factory") as factory:
        factory.call.return_value = [{"id": 1, "name": "awesome", "url": "https://github.com/sindresorhus/awesome"}]
        factory.last_next_page = None
        yield factory


class TestIdValidation:
    """Ids the API can never resolve are rejected with a hint, before any request."""

    @pytest.mark.parametrize("command", ["get_list", "get_list_projects", "get_list_list_projects"])
    def test_list_url_points_to_lookup_list(self, runner, mock_api_factory, command):
        result = runner.invoke(cli, ["awesome", command, "https://github.com/sindresorhus/awesome"])

        assert result.exit_code == 1
        assert "lookup_list" in result.stderr
        assert "owner/name" in result.stderr
        mock_api_factory.call.assert_not_called()

    @pytest.mark.parametrize("command", ["get_project", "get_project_lists"])
    def test_project_url_points_to_lookup_project(self, runner, mock_api_factory, command):
        result = runner.invoke(cli, ["awesome", command, "https://github.com/rails/rails"])

        assert result.exit_code == 1
        assert "lookup_project" in result.stderr
        mock_api_factory.call.assert_not_called()

    def test_project_slug_without_host_explains_format(self, runner, mock_api_factory):
        result = runner.invoke(cli, ["awesome", "get_project", "rails/rails"])

        assert result.exit_code == 1
        assert "host/owner/name" in result.stderr
        assert "github.com/rails/rails" in result.stderr
        mock_api_factory.call.assert_not_called()

    @pytest.mark.parametrize(
        "command,value",
        [
            ("get_list", "sindresorhus/awesome"),
            ("get_list", "3865"),
            ("get_project", "github.com/rails/rails"),
            ("get_project", "mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg"),
            ("get_project", "13400472"),
        ],
    )
    def test_valid_ids_are_passed_through(self, runner, mock_api_factory, command, value):
        result = runner.invoke(cli, ["awesome", command, value])

        assert result.exit_code == 0, result.output
        assert mock_api_factory.call.call_args.kwargs["path_params"] == {"id": value}


class TestQueryValidation:
    def test_empty_string_option_rejected(self, runner, mock_api_factory):
        result = runner.invoke(cli, ["awesome", "get_list_list_projects", "sindresorhus/awesome", "--category", ""])

        assert result.exit_code == 2
        assert "must not be empty" in result.output
        mock_api_factory.call.assert_not_called()

    def test_page_beyond_int64_rejected(self, runner, mock_api_factory):
        """Upstream answers pages beyond int64 with a 500."""
        result = runner.invoke(cli, ["awesome", "get_lists", "--page", str(2**63)])

        assert result.exit_code == 2
        mock_api_factory.call.assert_not_called()

    def test_page_at_int64_max_accepted(self, runner, mock_api_factory):
        result = runner.invoke(cli, ["awesome", "get_lists", "--page", str(2**63 - 1)])

        assert result.exit_code == 0, result.output


class TestNextPageHint:
    def test_table_output_hints_next_page_on_stderr(self, runner, mock_api_factory):
        mock_api_factory.last_next_page = 2

        result = runner.invoke(cli, ["awesome", "get_lists", "--per-page", "1"])

        assert result.exit_code == 0
        assert "--page 2" in result.stderr
        assert "--page 2" not in result.stdout

    def test_no_hint_on_last_page(self, runner, mock_api_factory):
        result = runner.invoke(cli, ["awesome", "get_lists"])

        assert result.exit_code == 0
        assert "--page" not in result.stderr

    def test_no_hint_for_machine_formats(self, runner, mock_api_factory):
        mock_api_factory.last_next_page = 2

        result = runner.invoke(cli, ["awesome", "get_lists", "--format", "json"])

        assert result.exit_code == 0
        assert result.stderr == ""


class TestTableColumns:
    def test_projects_table_shows_url(self, runner, mock_api_factory):
        """Awesome projects share 'language' with repos; columns must come from the awesome priorities."""
        mock_api_factory.call.return_value = [{"id": 1, "url": "https://github.com/rails/rails", "language": "Ruby"}]

        result = runner.invoke(cli, ["awesome", "get_projects"])

        assert "https://github.com/rails/rails" in result.stdout


def test_lookup_help_warns_about_registration(runner):
    for command in ("lookup_list", "lookup_project"):
        result = runner.invoke(cli, ["awesome", command, "--help"])
        assert "registers" in result.output, command
