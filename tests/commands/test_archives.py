"""Tests for the archives commands."""

from unittest import mock

from click.testing import CliRunner


class TestArchivesCommands:
    """Archives operations are all query-param based (no path params)."""

    def setup_method(self):
        self.runner = CliRunner()
        from ecosystems_cli.commands.archives import archives

        self.archives_group = archives

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_list_passes_url_as_query_param(self, mock_print_output, mock_api_factory):
        mock_api_factory.call.return_value = [{"name": "package.json"}]

        result = self.runner.invoke(
            self.archives_group,
            ["list", "--url", "https://example.com/pkg.tgz"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "archives",
            "list",
            path_params={},
            query_params={"url": "https://example.com/pkg.tgz"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_contents_passes_url_and_path_as_query_params(self, mock_print_output, mock_api_factory):
        mock_api_factory.call.return_value = {"name": "package.json"}

        result = self.runner.invoke(
            self.archives_group,
            ["contents", "--url", "https://example.com/pkg.tgz", "--path", "package.json"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "archives",
            "contents",
            path_params={},
            query_params={"url": "https://example.com/pkg.tgz", "path": "package.json"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    def test_contents_requires_path(self):
        """path is required:true in the spec, so Click rejects a call without it."""
        result = self.runner.invoke(
            self.archives_group,
            ["contents", "--url", "https://example.com/pkg.tgz"],
            obj={"timeout": 20, "format": "json"},
        )
        assert result.exit_code != 0
