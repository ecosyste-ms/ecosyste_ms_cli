"""Tests for the commits commands."""

from unittest import mock

from click.testing import CliRunner


class TestCommitsCommands:
    """Test cases for commits commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        from ecosystems_cli.commands.commits import commits

        self.commits_group = commits

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_committer(self, mock_print_output, mock_api_factory):
        """Test getting a committer from a host."""
        mock_api_factory.call.return_value = {
            "id": 1,
            "login": "octocat",
            "emails": ["octocat@github.com"],
            "commits_count": 150,
            "repositories_count": 10,
        }

        result = self.runner.invoke(
            self.commits_group,
            ["get_host_committer", "octocat", "GitHub"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "commits",
            "getHostCommitter",
            path_params={"hostName": "GitHub", "login": "octocat"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()
