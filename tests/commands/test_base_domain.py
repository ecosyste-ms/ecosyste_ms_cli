"""Test base command domain functionality."""

from unittest import mock

from click.testing import CliRunner

from ecosystems_cli.commands.base import BaseCommand


class TestBaseCommandDomain:
    """Test domain configuration in base command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.base_cmd = BaseCommand("test_api", "Test API commands")

    @mock.patch("ecosystems_cli.commands.base.get_client")
    @mock.patch("ecosystems_cli.commands.base.print_operations")
    def test_list_operations_with_domain(self, mock_print_operations, mock_get_client):
        """Test list operations with domain parameter."""
        mock_client = mock.MagicMock()
        mock_client.list_operations.return_value = []
        mock_get_client.return_value = mock_client

        # Create the list command
        self.base_cmd.list_operations()

        # Test with domain parameter
        result = self.runner.invoke(self.base_cmd.group, ["list", "--domain", "custom.api.com"], obj={})

        assert result.exit_code == 0
        # Should be called with base_url built from domain
        mock_get_client.assert_called_once_with("test_api", base_url="https://custom.api.com/api/v1", timeout=20)

    @mock.patch("ecosystems_cli.commands.base.get_client")
    @mock.patch("ecosystems_cli.commands.base.print_operations")
    @mock.patch.dict("os.environ", {"ECOSYSTEMS_TEST_API_DOMAIN": "env.api.com"})
    def test_list_operations_with_env_var(self, mock_print_operations, mock_get_client):
        """Test list operations with environment variable."""
        mock_client = mock.MagicMock()
        mock_client.list_operations.return_value = []
        mock_get_client.return_value = mock_client

        # Create the list command
        self.base_cmd.list_operations()

        # Test without domain parameter (should use env var)
        result = self.runner.invoke(self.base_cmd.group, ["list"], obj={})

        assert result.exit_code == 0
        # Should be called with base_url from env var
        mock_get_client.assert_called_once_with("test_api", base_url="https://env.api.com/api/v1", timeout=20)

    @mock.patch("ecosystems_cli.commands.base.get_client")
    @mock.patch("ecosystems_cli.commands.base.print_output")
    def test_simple_command_with_domain(self, mock_print_output, mock_get_client):
        """Test simple command with domain parameter."""
        mock_client = mock.MagicMock()
        mock_client.test_method.return_value = {"result": "test"}
        mock_get_client.return_value = mock_client

        # Create a simple command
        self.base_cmd.create_simple_command("test", "test_method", "Test command")

        # Test with domain parameter
        result = self.runner.invoke(self.base_cmd.group, ["test", "--domain", "test.api.com"], obj={})

        assert result.exit_code == 0
        mock_get_client.assert_called_once_with("test_api", base_url="https://test.api.com/api/v1", timeout=20)

    @mock.patch("ecosystems_cli.commands.base.get_client")
    @mock.patch("ecosystems_cli.commands.base.print_output")
    @mock.patch.dict("os.environ", {"ECOSYSTEMS_DOMAIN": "general.api.com", "ECOSYSTEMS_TEST_API_DOMAIN": "specific.api.com"})
    def test_domain_precedence(self, mock_print_output, mock_get_client):
        """Test domain precedence: API env > general env > param."""
        mock_client = mock.MagicMock()
        mock_client.test_method.return_value = {"result": "test"}
        mock_get_client.return_value = mock_client

        # Create a simple command
        self.base_cmd.create_simple_command("test", "test_method", "Test command")

        # Test with all sources present
        result = self.runner.invoke(self.base_cmd.group, ["test", "--domain", "param.api.com"], obj={})

        assert result.exit_code == 0
        # Should use API-specific env var (highest precedence)
        mock_get_client.assert_called_once_with("test_api", base_url="https://specific.api.com/api/v1", timeout=20)

    @mock.patch("ecosystems_cli.commands.base.get_client")
    @mock.patch("ecosystems_cli.commands.base.print_output")
    def test_domain_with_full_url(self, mock_print_output, mock_get_client):
        """Test domain with full URL including protocol."""
        mock_client = mock.MagicMock()
        mock_client.test_method.return_value = {"result": "test"}
        mock_get_client.return_value = mock_client

        # Create a simple command
        self.base_cmd.create_simple_command("test", "test_method", "Test command")

        # Test with full URL
        result = self.runner.invoke(self.base_cmd.group, ["test", "--domain", "http://localhost:8080/custom/path"], obj={})

        assert result.exit_code == 0
        # Should preserve the full URL
        mock_get_client.assert_called_once_with("test_api", base_url="http://localhost:8080/custom/path", timeout=20)
