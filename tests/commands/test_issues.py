"""Tests for the issues commands."""

from unittest import mock

from click.testing import CliRunner


class TestIssuesCommands:
    """Test cases for issues commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        # Import the issues group to ensure commands are registered
        from ecosystems_cli.commands.issues import issues

        self.issues_group = issues

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_repositories_lookup(self, mock_print_output, mock_api_factory):
        """Test repository lookup."""
        mock_api_factory.call.return_value = {
            "full_name": "octocat/hello-world",
            "html_url": "https://github.com/octocat/hello-world",
            "open_issues_count": 42,
        }

        result = self.runner.invoke(
            self.issues_group,
            ["repositories_lookup", "--url", "https://github.com/octocat/hello-world"],
            obj={"timeout": 20, "format": "table", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "repositoriesLookup",
            path_params={},
            query_params={
                "url": "https://github.com/octocat/hello-world",
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_registries(self, mock_print_output, mock_api_factory):
        """Test getting registries."""
        mock_api_factory.call.return_value = [
            {"name": "github", "url": "https://github.com"},
            {"name": "gitlab", "url": "https://gitlab.com"},
        ]

        result = self.runner.invoke(
            self.issues_group,
            ["get_registries", "--page", "1", "--per-page", "10"],
            obj={"timeout": 20, "format": "table", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "getRegistries",
            path_params={},
            query_params={
                "page": 1,
                "per_page": 10,
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_repository_labels(self, mock_print_output, mock_api_factory):
        """Test getting labels for a repository."""
        mock_api_factory.call.return_value = [
            {"label": "bug", "count": 42},
            {"label": "enhancement", "count": 15},
        ]

        result = self.runner.invoke(
            self.issues_group,
            ["get_host_repository_labels", "octocat/hello-world", "GitHub"],
            obj={"timeout": 20, "format": "json", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "getHostRepositoryLabels",
            path_params={"hostName": "GitHub", "repoName": "octocat/hello-world"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_owners(self, mock_print_output, mock_api_factory):
        """Test getting owners from a host."""
        mock_api_factory.call.return_value = [
            {"login": "octocat", "repositories_count": 10},
            {"login": "torvalds", "repositories_count": 5},
        ]

        result = self.runner.invoke(
            self.issues_group,
            ["get_host_owners", "GitHub", "--page", "1", "--per-page", "10"],
            obj={"timeout": 20, "format": "json", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "getHostOwners",
            path_params={"hostName": "GitHub"},
            query_params={"page": 1, "per_page": 10},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_owner(self, mock_print_output, mock_api_factory):
        """Test getting owner statistics from a host."""
        mock_api_factory.call.return_value = {
            "login": "octocat",
            "issues_count": 100,
            "pull_requests_count": 50,
        }

        result = self.runner.invoke(
            self.issues_group,
            ["get_host_owner", "octocat", "GitHub"],
            obj={"timeout": 20, "format": "json", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "getHostOwner",
            path_params={"hostName": "GitHub", "ownerName": "octocat"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_owner_maintainers(self, mock_print_output, mock_api_factory):
        """Test getting maintainers for an owner."""
        mock_api_factory.call.return_value = {
            "login": "octocat",
            "maintainers": [{"maintainer": "dev1", "count": 10}],
            "active_maintainers": [{"maintainer": "dev1", "count": 5}],
        }

        result = self.runner.invoke(
            self.issues_group,
            ["get_host_owner_maintainers", "octocat", "GitHub"],
            obj={"timeout": 20, "format": "json", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "getHostOwnerMaintainers",
            path_params={"hostName": "GitHub", "ownerName": "octocat"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_authors(self, mock_print_output, mock_api_factory):
        """Test getting authors from a host."""
        mock_api_factory.call.return_value = [
            {"login": "author1", "repositories_count": 8},
        ]

        result = self.runner.invoke(
            self.issues_group,
            ["get_host_authors", "GitHub", "--page", "1"],
            obj={"timeout": 20, "format": "json", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "getHostAuthors",
            path_params={"hostName": "GitHub"},
            query_params={"page": 1},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_author(self, mock_print_output, mock_api_factory):
        """Test getting author statistics from a host."""
        mock_api_factory.call.return_value = {
            "login": "author1",
            "issues_count": 200,
            "pull_requests_count": 100,
            "merged_pull_requests_count": 80,
        }

        result = self.runner.invoke(
            self.issues_group,
            ["get_host_author", "author1", "GitHub"],
            obj={"timeout": 20, "format": "json", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "getHostAuthor",
            path_params={"hostName": "GitHub", "authorName": "author1"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_host_repository_issues_with_filters(self, mock_print_output, mock_api_factory):
        """Test filtering repository issues by state and label."""
        mock_api_factory.call.return_value = [
            {"number": 1, "title": "Bug report", "state": "open"},
        ]

        result = self.runner.invoke(
            self.issues_group,
            [
                "get_host_repository_issues",
                "octocat/hello-world",
                "GitHub",
                "--state",
                "open",
                "--label",
                "bug",
            ],
            obj={"timeout": 20, "format": "json", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "getHostRepositoryIssues",
            path_params={"hostName": "GitHub", "repoName": "octocat/hello-world"},
            query_params={"state": "open", "label": "bug"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_job(self, mock_print_output, mock_api_factory):
        """Test getting a job status."""
        mock_api_factory.call.return_value = {
            "id": 42,
            "url": "https://github.com/octocat/hello-world",
            "status": "completed",
        }

        result = self.runner.invoke(
            self.issues_group,
            ["get_job", "42"],
            obj={"timeout": 20, "format": "json", "domain": None},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "issues",
            "getJob",
            path_params={"jobId": "42"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()
