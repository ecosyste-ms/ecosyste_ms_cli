"""Tests for the parser commands."""

from unittest import mock

from click.testing import CliRunner


class TestParserCommands:
    """Test cases for parser commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        # Import the parser group to ensure commands are registered
        from ecosystems_cli.commands.parser import parser

        self.parser_group = parser

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_output")
    def test_create_job(self, mock_print_output, mock_api_factory):
        """Test creating a parsing job."""
        mock_api_factory.call.return_value = {
            "id": "test-job-123",
            "status": "pending",
            "location": "https://parser.ecosyste.ms/api/v1/jobs/test-job-123",
        }

        result = self.runner.invoke(
            self.parser_group, ["create_job", "https://example.com/package.tar.gz"], obj={"timeout": 20, "format": "json"}
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "parser",
            "createJob",
            path_params={},
            query_params={"url": "https://example.com/package.tar.gz"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_output")
    def test_get_job_parameter_mapping(self, mock_print_output, mock_api_factory):
        """Test that job_id parameter is correctly mapped to jobID key."""
        # Mock the create_job response first
        mock_api_factory.call.return_value = {
            "id": "test-job-456",
            "status": "completed",
            "results": {"dependencies": []},
        }

        # We need to test the handler directly since create_job with polling calls get_job internally
        from ecosystems_cli.commands.handlers import OperationHandlerFactory

        handler = OperationHandlerFactory.get_handler("parser")
        path_params, query_params = handler.build_params("getJob", (), {"job_id": "test-job-456"})

        # Assert that job_id is mapped to jobID in path_params
        assert path_params == {"jobID": "test-job-456"}
        assert query_params == {}

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_output")
    @mock.patch("ecosystems_cli.helpers.job_polling.time.sleep")
    def test_create_job_with_polling(self, mock_sleep, mock_print_output, mock_api_factory):
        """Test creating a parsing job with polling enabled."""
        # Mock the initial create_job response
        create_response = {
            "id": "test-job-789",
            "status": "pending",
            "location": "https://parser.ecosyste.ms/api/v1/jobs/test-job-789",
        }

        # Mock the get_job response (completed job)
        get_response = {"id": "test-job-789", "status": "completed", "results": {"dependencies": []}}

        # Set up the mock to return different values for different calls
        mock_api_factory.call.side_effect = [create_response, get_response]

        result = self.runner.invoke(
            self.parser_group,
            ["create_job", "https://example.com/package.tar.gz", "--polling-interval", "1"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0

        # Verify create_job was called first
        first_call = mock_api_factory.call.call_args_list[0]
        assert first_call[1]["path_params"] == {}
        assert first_call[1]["query_params"] == {"url": "https://example.com/package.tar.gz"}

        # Verify get_job was called with jobID (not job_id) in path_params
        second_call = mock_api_factory.call.call_args_list[1]
        assert second_call[0][0] == "parser"
        assert second_call[0][1] == "getJob"
        assert second_call[1]["path_params"] == {"jobID": "test-job-789"}
        assert second_call[1]["query_params"] == {}

        # Verify output was printed with the final result
        mock_print_output.assert_called_once_with(get_response, "json", console=mock.ANY)

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_error")
    def test_create_job_error(self, mock_print_error, mock_api_factory):
        """Test error handling when creating a job."""
        mock_api_factory.call.side_effect = Exception("Invalid URL")

        result = self.runner.invoke(self.parser_group, ["create_job", "invalid-url"], obj={"timeout": 20, "format": "json"})

        assert result.exit_code == 0
        mock_print_error.assert_called_once_with("Unexpected error: Invalid URL", console=mock.ANY)
