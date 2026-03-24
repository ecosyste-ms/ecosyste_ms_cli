"""Tests for the repos commands."""

from unittest import mock

from click.testing import CliRunner


class TestReposCommands:
    """Test cases for repos commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        # Import the repos group to ensure commands are registered
        from ecosystems_cli.commands.repos import repos

        self.repos_group = repos

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_topics(self, mock_print_output, mock_api_factory):
        """Test getting topics."""
        mock_api_factory.call.return_value = [
            {"name": "python", "repository_count": 1500},
            {"name": "javascript", "repository_count": 2000},
        ]

        result = self.runner.invoke(
            self.repos_group,
            ["topics", "--page", "1", "--per-page", "20"],
            obj={"timeout": 20, "format": "table"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "topics",
            path_params={},
            query_params={
                "page": 1,
                "per_page": 20,
            },
            timeout=20,
            mailto=None,
            base_url=None,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_topic(self, mock_print_output, mock_api_factory):
        """Test getting a specific topic."""
        mock_api_factory.call.return_value = {
            "name": "machine-learning",
            "repository_count": 500,
            "repositories": [
                {"name": "tensorflow/tensorflow", "stars": 180000},
                {"name": "pytorch/pytorch", "stars": 70000},
            ],
        }

        result = self.runner.invoke(
            self.repos_group,
            ["topic", "machine-learning"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "topic",
            path_params={"topic": "machine-learning"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_repositories_lookup(self, mock_print_output, mock_api_factory):
        """Test looking up a repository by URL."""
        mock_api_factory.call.return_value = {
            "name": "django/django",
            "host": "github.com",
            "language": "Python",
            "stars": 75000,
            "forks": 30000,
        }

        result = self.runner.invoke(
            self.repos_group,
            ["repositories_lookup", "--url", "https://github.com/django/django"],
            obj={"timeout": 20, "format": "table"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "repositoriesLookup",
            path_params={},
            query_params={
                "url": "https://github.com/django/django",
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_repositories_lookup_by_purl(self, mock_print_output, mock_api_factory):
        """Test looking up a repository by purl."""
        mock_api_factory.call.return_value = {
            "name": "facebook/react",
            "host": "github.com",
            "language": "JavaScript",
            "stars": 210000,
            "forks": 44000,
        }

        result = self.runner.invoke(
            self.repos_group,
            ["repositories_lookup", "--purl", "pkg:github/facebook/react"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "repositoriesLookup",
            path_params={},
            query_params={
                "purl": "pkg:github/facebook/react",
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_usage(self, mock_print_output, mock_api_factory):
        """Test getting package usage ecosystems."""
        mock_api_factory.call.return_value = [
            {"ecosystem": "npm", "packages_count": 2500000},
            {"ecosystem": "pypi", "packages_count": 450000},
        ]

        result = self.runner.invoke(
            self.repos_group,
            ["usage"],
            obj={"timeout": 20, "format": "table"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "usage",
            path_params={},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_error")
    def test_topic_error(self, mock_print_error, mock_api_factory):
        """Test error handling when getting a topic."""
        mock_api_factory.call.side_effect = Exception("Topic not found")

        result = self.runner.invoke(
            self.repos_group,
            ["topic", "nonexistent"],
            obj={"timeout": 20},
        )

        assert result.exit_code == 0
        mock_print_error.assert_called_once_with("Unexpected error: Topic not found", console=mock.ANY)

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_usage_package_dependent_repositories(self, mock_print_output, mock_api_factory):
        """Test getting dependent repositories for a package."""
        mock_api_factory.call.return_value = [
            {"name": "my-app", "host": "github.com", "stars": 50},
            {"name": "another-app", "host": "github.com", "stars": 10},
        ]

        result = self.runner.invoke(
            self.repos_group,
            [
                "usage_package_dependent_repositories",
                "express",
                "npm",
                "--page",
                "1",
                "--per-page",
                "10",
                "--sort",
                "stargazers_count",
                "--order",
                "desc",
            ],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "usagePackageDependentRepositories",
            path_params={"ecosystem": "npm", "package": "express"},
            query_params={"page": 1, "per_page": 10, "sort": "stargazers_count", "order": "desc"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_usage_package_dependent_repositories_with_filters(self, mock_print_output, mock_api_factory):
        """Test dependent repositories with min_stars filter."""
        mock_api_factory.call.return_value = []

        result = self.runner.invoke(
            self.repos_group,
            [
                "usage_package_dependent_repositories",
                "express",
                "npm",
                "--min-stars",
                "100",
            ],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "usagePackageDependentRepositories",
            path_params={"ecosystem": "npm", "package": "express"},
            query_params={"min_stars": 100},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_owner_sponsors_logins(self, mock_print_output, mock_api_factory):
        """Test getting owner logins with sponsors listings."""
        mock_api_factory.call.return_value = ["octocat", "torvalds", "gvanrossum"]

        result = self.runner.invoke(
            self.repos_group,
            ["get_host_owner_sponsors_logins", "GitHub"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "getHostOwnerSponsorsLogins",
            path_params={"hostName": "GitHub"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_owners_with_kind_filter(self, mock_print_output, mock_api_factory):
        """Test getting host owners filtered by kind."""
        mock_api_factory.call.return_value = [
            {"login": "my-org", "repositories_count": 50},
        ]

        result = self.runner.invoke(
            self.repos_group,
            ["get_host_owners", "GitHub", "--kind", "organization"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "getHostOwners",
            path_params={"hostName": "GitHub"},
            query_params={"kind": "organization"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_usage_package_dependencies_with_pagination(self, mock_print_output, mock_api_factory):
        """Test usage package dependencies with new pagination params."""
        mock_api_factory.call.return_value = [
            {"name": "body-parser", "version": "1.20.1"},
        ]

        result = self.runner.invoke(
            self.repos_group,
            ["usage_package_dependencies", "express", "npm", "--page", "1", "--per-page", "10"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "repos",
            "usagePackageDependencies",
            path_params={"ecosystem": "npm", "package": "express"},
            query_params={"page": 1, "per_page": 10},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()
