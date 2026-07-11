"""Tests for the docker commands."""

from unittest import mock

from click.testing import CliRunner


class TestDockerCommands:
    """Test cases for docker commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        # Import the docker group to ensure commands are registered
        from ecosystems_cli.commands.docker import docker

        self.docker_group = docker

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_packages(self, mock_print_output, mock_api_factory):
        """Test getting docker packages."""
        mock_api_factory.call.return_value = [
            {
                "name": "nginx",
                "versions_count": 100,
                "latest_release_number": "1.25.0",
            }
        ]

        result = self.runner.invoke(
            self.docker_group,
            ["get_packages", "--page", "1", "--per-page", "20"],
            obj={"timeout": 20, "format": "table"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "getPackages",
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
    def test_get_package(self, mock_print_output, mock_api_factory):
        """Test getting a specific docker package."""
        mock_api_factory.call.return_value = {
            "name": "nginx",
            "versions_count": 100,
            "latest_release_number": "1.25.0",
        }

        result = self.runner.invoke(
            self.docker_group,
            ["get_package", "nginx"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "getPackage",
            path_params={"packageName": "nginx"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_package_versions(self, mock_print_output, mock_api_factory):
        """Test getting versions for a docker package."""
        mock_api_factory.call.return_value = [
            {"number": "1.25.0", "published_at": "2024-01-01T00:00:00Z"},
            {"number": "1.24.0", "published_at": "2023-12-01T00:00:00Z"},
        ]

        result = self.runner.invoke(
            self.docker_group,
            ["get_package_versions", "nginx", "--page", "1"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "getPackageVersions",
            path_params={"packageName": "nginx"},
            query_params={"page": 1},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_package_version(self, mock_print_output, mock_api_factory):
        """Test getting a specific version of a docker package."""
        mock_api_factory.call.return_value = {
            "number": "1.25.0",
            "published_at": "2024-01-01T00:00:00Z",
            "distro": "alpine",
        }

        result = self.runner.invoke(
            self.docker_group,
            ["get_package_version", "nginx", "1.25.0"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "getPackageVersion",
            path_params={"packageName": "nginx", "versionNumber": "1.25.0"},
            query_params={},
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
            {"name": "npm", "packages_count": 1000, "total_downloads": 50000},
            {"name": "pypi", "packages_count": 500, "total_downloads": 30000},
        ]

        result = self.runner.invoke(
            self.docker_group,
            ["usage"],
            obj={"timeout": 20, "format": "table"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "usage",
            path_params={},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_usage_ecosystem(self, mock_print_output, mock_api_factory):
        """Test getting package usage for an ecosystem."""
        mock_api_factory.call.return_value = [
            {"ecosystem": "npm", "name": "react", "dependents_count": 1000},
        ]

        result = self.runner.invoke(
            self.docker_group,
            ["usage_ecosystem", "npm"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "usageEcosystem",
            path_params={"ecosystem": "npm"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_usage_package(self, mock_print_output, mock_api_factory):
        """Test getting package usage for a specific package."""
        mock_api_factory.call.return_value = {
            "ecosystem": "npm",
            "name": "react",
            "dependents_count": 1500,
        }

        result = self.runner.invoke(
            self.docker_group,
            ["usage_package", "npm", "react"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "usagePackage",
            path_params={"ecosystem": "npm", "package": "react"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_distros(self, mock_print_output, mock_api_factory):
        """Test getting Linux distributions."""
        mock_api_factory.call.return_value = [
            {
                "slug": "ubuntu-22.04",
                "name": "Ubuntu",
                "pretty_name": "Ubuntu 22.04 LTS",
                "versions_count": 10,
            },
            {
                "slug": "alpine-3.18",
                "name": "Alpine",
                "pretty_name": "Alpine Linux 3.18",
                "versions_count": 5,
            },
        ]

        result = self.runner.invoke(
            self.docker_group,
            ["get_distros", "--page", "1", "--per-page", "20"],
            obj={"timeout": 20, "format": "table"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "getDistros",
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
    def test_get_distros_with_query(self, mock_print_output, mock_api_factory):
        """Test getting Linux distributions with search query."""
        mock_api_factory.call.return_value = [
            {
                "slug": "ubuntu-22.04",
                "name": "Ubuntu",
                "pretty_name": "Ubuntu 22.04 LTS",
                "versions_count": 10,
            },
        ]

        result = self.runner.invoke(
            self.docker_group,
            ["get_distros", "--query", "ubuntu"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "getDistros",
            path_params={},
            query_params={
                "query": "ubuntu",
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_distro(self, mock_print_output, mock_api_factory):
        """Test getting a specific Linux distribution by slug."""
        mock_api_factory.call.return_value = {
            "slug": "ubuntu-22.04",
            "name": "Ubuntu",
            "pretty_name": "Ubuntu 22.04 LTS",
            "version_id": "22.04",
            "versions_count": 10,
            "home_url": "https://ubuntu.com",
        }

        result = self.runner.invoke(
            self.docker_group,
            ["get_distro", "ubuntu-22.04"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "getDistro",
            path_params={"slug": "ubuntu-22.04"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_distro_versions(self, mock_print_output, mock_api_factory):
        """Test getting versions for a Linux distribution."""
        mock_api_factory.call.return_value = [
            {"number": "22.04.1", "published_at": "2024-01-01T00:00:00Z"},
            {"number": "22.04.0", "published_at": "2023-12-01T00:00:00Z"},
        ]

        result = self.runner.invoke(
            self.docker_group,
            ["get_distro_versions", "ubuntu-22.04", "--page", "1"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "docker",
            "getDistroVersions",
            path_params={"slug": "ubuntu-22.04"},
            query_params={"page": 1},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_error")
    def test_get_distro_error(self, mock_print_error, mock_api_factory):
        """Test error handling when getting a distro."""
        mock_api_factory.call.side_effect = Exception("Distro not found")

        result = self.runner.invoke(
            self.docker_group,
            ["get_distro", "nonexistent"],
            obj={"timeout": 20},
        )

        assert result.exit_code == 1
        mock_print_error.assert_called_once_with("Unexpected error: Distro not found", console=mock.ANY)
