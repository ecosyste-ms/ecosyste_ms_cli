"""Tests for the sponsors commands."""

from unittest import mock

from click.testing import CliRunner


class TestSponsorsCommands:
    """Test cases for sponsors commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        # Import the sponsors group to ensure commands are registered
        from ecosystems_cli.commands.sponsors import sponsors

        self.sponsors_group = sponsors

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_list_accounts(self, mock_print_output, mock_api_factory):
        """Test listing accounts."""
        mock_api_factory.call.return_value = [
            {"login": "octocat", "has_sponsors_listing": True, "sponsors_count": 10},
            {"login": "defunkt", "has_sponsors_listing": False, "sponsors_count": 0},
        ]

        result = self.runner.invoke(
            self.sponsors_group,
            ["list_accounts", "--page", "1", "--per-page", "20"],
            obj={"timeout": 20, "format": "table"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "sponsors",
            "listAccounts",
            path_params={},
            query_params={
                "page": 1,
                "per_page": 20,
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_account(self, mock_print_output, mock_api_factory):
        """Test getting a specific account."""
        mock_api_factory.call.return_value = {
            "login": "octocat",
            "has_sponsors_listing": True,
            "sponsors_count": 10,
            "sponsorships_count": 5,
            "active_sponsorships_count": 3,
        }

        result = self.runner.invoke(
            self.sponsors_group,
            ["get_account", "octocat"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "sponsors",
            "getAccount",
            path_params={"login": "octocat"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_list_account_sponsors(self, mock_print_output, mock_api_factory):
        """Test listing sponsors for an account."""
        mock_api_factory.call.return_value = [
            {"id": 1, "status": "active", "funder": {"login": "sponsor1"}, "maintainer": {"login": "octocat"}},
            {"id": 2, "status": "active", "funder": {"login": "sponsor2"}, "maintainer": {"login": "octocat"}},
        ]

        result = self.runner.invoke(
            self.sponsors_group,
            ["list_account_sponsors", "octocat", "--page", "1"],
            obj={"timeout": 20, "format": "table"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "sponsors",
            "listAccountSponsors",
            path_params={"login": "octocat"},
            query_params={"page": 1},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_list_sponsors(self, mock_print_output, mock_api_factory):
        """Test listing all sponsors."""
        mock_api_factory.call.return_value = [
            {"login": "sponsor1", "has_sponsors_listing": False, "sponsors_count": 0},
            {"login": "sponsor2", "has_sponsors_listing": False, "sponsors_count": 0},
        ]

        result = self.runner.invoke(
            self.sponsors_group,
            ["list_sponsors"],
            obj={"timeout": 20, "format": "table"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "sponsors",
            "listSponsors",
            path_params={},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_error")
    def test_get_account_error(self, mock_print_error, mock_api_factory):
        """Test error handling when getting an account."""
        mock_api_factory.call.side_effect = Exception("Account not found")

        result = self.runner.invoke(
            self.sponsors_group,
            ["get_account", "nonexistent"],
            obj={"timeout": 20},
        )

        assert result.exit_code == 1
        mock_print_error.assert_called_once_with("Unexpected error: Account not found", console=mock.ANY)
