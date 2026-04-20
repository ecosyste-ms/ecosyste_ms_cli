"""Tests for the dependabot commands."""

from unittest import mock

from click.testing import CliRunner


class TestDependabotCommands:
    """Test cases for dependabot commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        from ecosystems_cli.commands.dependabot import dependabot

        self.dependabot_group = dependabot

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_with_flags(self, mock_print_output, mock_api_factory):
        """Test get_advisories with explicit --ecosystem and --package-name flags."""
        mock_api_factory.call.return_value = []

        result = self.runner.invoke(
            self.dependabot_group,
            ["get_advisories", "--ecosystem", "npm", "--package-name", "lodash", "--severity", "HIGH"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "dependabot",
            "getAdvisories",
            path_params={},
            query_params={
                "ecosystem": "npm",
                "package_name": "lodash",
                "severity": "HIGH",
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_with_purl(self, mock_print_output, mock_api_factory):
        """Test get_advisories decomposes --purl into ecosystem and package_name."""
        mock_api_factory.call.return_value = []

        result = self.runner.invoke(
            self.dependabot_group,
            ["get_advisories", "--purl", "pkg:npm/axios@1.7.9"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "dependabot",
            "getAdvisories",
            path_params={},
            query_params={"ecosystem": "npm", "package_name": "axios"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_with_scoped_purl(self, mock_print_output, mock_api_factory):
        """Test get_advisories preserves scoped package names from PURL."""
        mock_api_factory.call.return_value = []

        result = self.runner.invoke(
            self.dependabot_group,
            ["get_advisories", "--purl", "pkg:npm/@babel/traverse"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "dependabot",
            "getAdvisories",
            path_params={},
            query_params={"ecosystem": "npm", "package_name": "@babel/traverse"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_purl_overrides_flags(self, mock_print_output, mock_api_factory):
        """Test that PURL overrides explicit --ecosystem and --package-name flags."""
        mock_api_factory.call.return_value = []

        result = self.runner.invoke(
            self.dependabot_group,
            [
                "get_advisories",
                "--purl",
                "pkg:npm/fsa",
                "--ecosystem",
                "pypi",
                "--package-name",
                "django",
            ],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "dependabot",
            "getAdvisories",
            path_params={},
            query_params={"ecosystem": "npm", "package_name": "fsa"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_invalid_purl_ignored(self, mock_print_output, mock_api_factory):
        """Test that an unparseable --purl is ignored instead of raising."""
        mock_api_factory.call.return_value = []

        result = self.runner.invoke(
            self.dependabot_group,
            ["get_advisories", "--purl", "not-a-purl"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "dependabot",
            "getAdvisories",
            path_params={},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()
