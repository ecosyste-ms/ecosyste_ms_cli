"""Tests for the diff commands."""

from unittest import mock

from click.testing import CliRunner


class TestDiffCommands:
    """Test cases for diff commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        # Import the diff group to ensure commands are registered
        from ecosystems_cli.commands.diff import diff

        self.diff_group = diff

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_output")
    def test_create_job(self, mock_print_output, mock_api_factory):
        """Test creating a diff job."""
        mock_api_factory.call.return_value = {
            "id": "test-job-123",
            "status": "pending",
            "location": "https://diff.ecosyste.ms/api/v1/jobs/test-job-123",
        }

        result = self.runner.invoke(
            self.diff_group,
            ["create_job", "https://example.com/package1.tar.gz", "https://example.com/package2.tar.gz"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "diff",
            "createJob",
            path_params={},
            query_params={"url_1": "https://example.com/package1.tar.gz", "url_2": "https://example.com/package2.tar.gz"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_output")
    def test_get_job_parameter_mapping(self, mock_print_output, mock_api_factory):
        """Test that job_id parameter is correctly mapped to jobID key."""
        # We need to test the handler directly
        from ecosystems_cli.commands.handlers import OperationHandlerFactory

        handler = OperationHandlerFactory.get_handler("diff")
        path_params, query_params = handler.build_params("getJob", (), {"job_id": "test-job-456"})

        # Assert that job_id is mapped to jobID in path_params
        assert path_params == {"jobID": "test-job-456"}
        assert query_params == {}

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_output")
    @mock.patch("ecosystems_cli.helpers.job_polling.time.sleep")
    def test_create_job_with_polling(self, mock_sleep, mock_print_output, mock_api_factory):
        """Test creating a diff job with polling enabled."""
        # Mock the initial create_job response
        create_response = {
            "id": "test-job-789",
            "status": "pending",
            "location": "https://diff.ecosyste.ms/api/v1/jobs/test-job-789",
        }

        # Mock the get_job response (completed job)
        get_response = {
            "id": "test-job-789",
            "status": "completed",
            "results": {"added": [], "removed": [], "modified": []},
        }

        # Set up the mock to return different values for different calls
        mock_api_factory.call.side_effect = [create_response, get_response]

        result = self.runner.invoke(
            self.diff_group,
            [
                "create_job",
                "https://example.com/package1.tar.gz",
                "https://example.com/package2.tar.gz",
                "--polling-interval",
                "1",
            ],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0

        # Verify create_job was called first
        first_call = mock_api_factory.call.call_args_list[0]
        assert first_call[1]["path_params"] == {}
        assert first_call[1]["query_params"] == {
            "url_1": "https://example.com/package1.tar.gz",
            "url_2": "https://example.com/package2.tar.gz",
        }

        # Verify get_job was called with jobID (not job_id) in path_params
        second_call = mock_api_factory.call.call_args_list[1]
        assert second_call[0][0] == "diff"
        assert second_call[0][1] == "getJob"
        assert second_call[1]["path_params"] == {"jobID": "test-job-789"}
        assert second_call[1]["query_params"] == {}

        # Verify output was printed with the final result
        mock_print_output.assert_called_once_with(get_response, "json", console=mock.ANY)

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_output")
    @mock.patch("ecosystems_cli.helpers.job_polling.time.sleep")
    def test_create_job_with_polling_multiple_status_checks(self, mock_sleep, mock_print_output, mock_api_factory):
        """Test creating a diff job with polling that requires multiple status checks."""
        # Mock the initial create_job response
        create_response = {
            "id": "test-job-999",
            "status": "pending",
            "location": "https://diff.ecosyste.ms/api/v1/jobs/test-job-999",
        }

        # Mock the get_job responses (pending -> processing -> completed)
        get_response_1 = {"id": "test-job-999", "status": "pending", "results": None}
        get_response_2 = {"id": "test-job-999", "status": "processing", "results": None}
        get_response_3 = {
            "id": "test-job-999",
            "status": "completed",
            "results": {"added": ["file1.txt"], "removed": [], "modified": []},
        }

        # Set up the mock to return different values for different calls
        mock_api_factory.call.side_effect = [create_response, get_response_1, get_response_2, get_response_3]

        result = self.runner.invoke(
            self.diff_group,
            [
                "create_job",
                "https://example.com/package1.tar.gz",
                "https://example.com/package2.tar.gz",
                "--polling-interval",
                "0.5",
            ],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0

        # Verify create_job was called once
        assert mock_api_factory.call.call_count == 4

        # Verify sleep was called 3 times (once before each get_job call)
        assert mock_sleep.call_count == 3

        # Verify output was printed with the final result
        mock_print_output.assert_called_once_with(get_response_3, "json", console=mock.ANY)

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_error")
    def test_create_job_error(self, mock_print_error, mock_api_factory):
        """Test error handling when creating a job."""
        mock_api_factory.call.side_effect = Exception("Invalid URL")

        result = self.runner.invoke(
            self.diff_group,
            ["create_job", "invalid-url-1", "invalid-url-2"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_print_error.assert_called_once_with("Unexpected error: Invalid URL", console=mock.ANY)

    @mock.patch("ecosystems_cli.helpers.job_polling.api_factory")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_output")
    @mock.patch("ecosystems_cli.helpers.job_polling.print_error")
    def test_create_job_with_polling_no_job_id(self, mock_print_error, mock_print_output, mock_api_factory):
        """Test creating a diff job with polling when no job ID is returned."""
        # Mock a response without job ID or location
        create_response = {"status": "pending"}

        mock_api_factory.call.return_value = create_response

        result = self.runner.invoke(
            self.diff_group,
            [
                "create_job",
                "https://example.com/package1.tar.gz",
                "https://example.com/package2.tar.gz",
                "--polling-interval",
                "1",
            ],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0

        # Verify error was printed
        mock_print_error.assert_called_once_with("No job ID in response, cannot poll for completion", console=mock.ANY)

        # Verify output was still printed with the create response
        mock_print_output.assert_called_once_with(create_response, "json", console=mock.ANY)
