"""Tests for the advisories commands."""

from unittest import mock

from click.testing import CliRunner


class TestAdvisoriesCommands:
    """Test cases for advisories commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        # Import the advisories group to ensure commands are registered
        from ecosystems_cli.commands.advisories import advisories

        self.advisories_group = advisories

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_packages(self, mock_print_output, mock_api_factory):
        """Test getting packages that have advisories."""
        mock_api_factory.call.return_value = [
            {"ecosystem": "npm", "package_name": "lodash"},
            {"ecosystem": "pypi", "package_name": "django"},
        ]

        result = self.runner.invoke(self.advisories_group, ["get_advisories_packages"], obj={"timeout": 20, "format": "table"})

        assert result.exit_code == 0
        # get_client call removed - now using api_factory.call
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "getAdvisoriesPackages",
            path_params={},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories(self, mock_print_output, mock_api_factory):
        """Test searching advisories with filters."""
        mock_api_factory.call.return_value = [{"uuid": "123", "title": "Test Advisory", "severity": "high"}]

        result = self.runner.invoke(
            self.advisories_group,
            ["get_advisories", "--ecosystem", "npm", "--severity", "high", "--page", "1", "--per-page", "10"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "getAdvisories",
            path_params={},
            query_params={
                "ecosystem": "npm",
                "severity": "high",
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
    def test_get_advisory(self, mock_print_output, mock_api_factory):
        """Test getting a specific advisory by UUID."""
        mock_api_factory.call.return_value = {
            "uuid": "test-uuid-123",
            "title": "Security Advisory",
            "severity": "critical",
            "cvss_score": 9.8,
        }

        result = self.runner.invoke(
            self.advisories_group, ["get_advisory", "test-uuid-123"], obj={"timeout": 20, "format": "json"}
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "getAdvisory",
            path_params={"advisoryUUID": "test-uuid-123"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_error")
    def test_get_advisory_error(self, mock_print_error, mock_api_factory):
        """Test error handling when getting an advisory."""
        mock_api_factory.call.side_effect = Exception("Advisory not found")

        result = self.runner.invoke(self.advisories_group, ["get_advisory", "nonexistent-uuid"], obj={"timeout": 20})

        assert result.exit_code == 0
        mock_print_error.assert_called_once_with("Unexpected error: Advisory not found", console=mock.ANY)

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_lookup_advisories_by_purl(self, mock_print_output, mock_api_factory):
        """Test looking up advisories by Package URL (PURL)."""
        mock_api_factory.call.return_value = [
            {
                "uuid": "adv-123",
                "title": "Lodash Prototype Pollution",
                "severity": "high",
                "cvss_score": 7.4,
                "packages": [
                    {
                        "ecosystem": "npm",
                        "package_name": "lodash",
                        "purl": "pkg:npm/lodash",
                        "affected_versions": ["< 4.17.21"],
                        "unaffected_versions": [">= 4.17.21"],
                    }
                ],
            }
        ]

        result = self.runner.invoke(
            self.advisories_group,
            ["lookup_advisories_by_purl", "--purl", "pkg:npm/lodash@4.17.20"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "lookupAdvisoriesByPurl",
            path_params={},
            query_params={"purl": "pkg:npm/lodash@4.17.20"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_error")
    def test_lookup_advisories_by_purl_invalid(self, mock_print_error, mock_api_factory):
        """Test error handling for invalid PURL in lookup."""
        mock_api_factory.call.side_effect = Exception("Invalid PURL format")

        result = self.runner.invoke(
            self.advisories_group, ["lookup_advisories_by_purl", "--purl", "invalid-purl"], obj={"timeout": 20}
        )

        assert result.exit_code == 0
        mock_print_error.assert_called_once_with("Unexpected error: Invalid PURL format", console=mock.ANY)

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_with_purl(self, mock_print_output, mock_api_factory):
        """Test get_advisories with PURL parameter."""
        mock_api_factory.call.return_value = [{"uuid": "123", "title": "Test Advisory", "severity": "high"}]

        result = self.runner.invoke(
            self.advisories_group,
            ["get_advisories", "--purl", "pkg:npm/fsa", "--severity", "high"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "getAdvisories",
            path_params={},
            query_params={
                "ecosystem": "npm",
                "package_name": "fsa",
                "severity": "high",
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_with_scoped_purl(self, mock_print_output, mock_api_factory):
        """Test get_advisories with scoped package PURL."""
        mock_api_factory.call.return_value = [{"uuid": "456", "title": "Babel Advisory", "severity": "critical"}]

        result = self.runner.invoke(
            self.advisories_group,
            ["get_advisories", "--purl", "pkg:npm/@babel/traverse"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "getAdvisories",
            path_params={},
            query_params={
                "ecosystem": "npm",
                "package_name": "@babel/traverse",
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_purl_overrides_ecosystem_package(self, mock_print_output, mock_api_factory):
        """Test that PURL overrides ecosystem and package-name when both are provided."""
        mock_api_factory.call.return_value = [{"uuid": "789", "title": "Override Test", "severity": "low"}]

        result = self.runner.invoke(
            self.advisories_group,
            ["get_advisories", "--purl", "pkg:npm/fsa", "--ecosystem", "pypi", "--package-name", "django"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        # PURL should override the explicit ecosystem and package-name
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "getAdvisories",
            path_params={},
            query_params={
                "ecosystem": "npm",
                "package_name": "fsa",
            },
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_sources(self, mock_print_output, mock_api_factory):
        """Test listing advisory sources."""
        mock_api_factory.call.return_value = [
            {"id": 1, "name": "GitHub", "kind": "github", "advisories_count": 5000},
            {"id": 2, "name": "Erlef", "kind": "erlef", "advisories_count": 100},
        ]

        result = self.runner.invoke(
            self.advisories_group,
            ["get_sources"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "getSources",
            path_params={},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_source(self, mock_print_output, mock_api_factory):
        """Test getting a specific advisory source by kind."""
        mock_api_factory.call.return_value = {
            "id": 1,
            "name": "GitHub",
            "kind": "github",
            "url": "https://github.com/advisories",
            "advisories_count": 5000,
        }

        result = self.runner.invoke(
            self.advisories_group,
            ["get_source", "github"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "getSource",
            path_params={"sourceKind": "github"},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_get_advisories_with_source_filter(self, mock_print_output, mock_api_factory):
        """Test filtering advisories by source."""
        mock_api_factory.call.return_value = [{"uuid": "abc", "title": "Test", "severity": "medium"}]

        result = self.runner.invoke(
            self.advisories_group,
            ["get_advisories", "--source", "github"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "advisories",
            "getAdvisories",
            path_params={},
            query_params={"source": "github"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()
