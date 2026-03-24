"""Tests for the resolve commands."""

from unittest import mock

from click.testing import CliRunner


class TestResolveCommands:
    """Test cases for resolve commands."""

    def setup_method(self):
        """Set up test dependencies."""
        self.runner = CliRunner()
        # Import the resolve group to ensure commands are registered
        from ecosystems_cli.commands.resolve import resolve

        self.resolve_group = resolve

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_output")
    def test_create_job_basic(self, mock_print_output, mock_api_factory):
        """Test creating a resolve job without polling."""
        mock_api_factory.call.return_value = {
            "id": "test-resolve-123",
            "status": "pending",
            "location": "https://resolve.ecosyste.ms/api/v1/jobs/test-resolve-123",
        }

        result = self.runner.invoke(self.resolve_group, ["create_job", "express", "npm"], obj={"timeout": 20, "format": "json"})

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "resolve",
            "createJob",
            path_params={},
            query_params={"package_name": "express", "registry": "npm"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_output")
    def test_create_job_with_optional_params(self, mock_print_output, mock_api_factory):
        """Test creating a resolve job with version and before parameters."""
        mock_api_factory.call.return_value = {
            "id": "test-resolve-456",
            "status": "pending",
            "location": "https://resolve.ecosyste.ms/api/v1/jobs/test-resolve-456",
        }

        result = self.runner.invoke(
            self.resolve_group,
            ["create_job", "express", "npm", "--version", "^4.18.0", "--before", "2023-01-01"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "resolve",
            "createJob",
            path_params={},
            query_params={"package_name": "express", "registry": "npm", "version": "^4.18.0", "before": "2023-01-01"},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_output")
    def test_get_job_parameter_mapping(self, mock_print_output, mock_api_factory):
        """Test that job_id parameter is correctly mapped to jobID key."""
        from ecosystems_cli.commands.handlers import OperationHandlerFactory

        handler = OperationHandlerFactory.get_handler("resolve")
        path_params, query_params = handler.build_params("getJob", (), {"job_id": "test-resolve-789"})

        # Assert that job_id is mapped to jobID in path_params
        assert path_params == {"jobID": "test-resolve-789"}
        assert query_params == {}

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_output")
    @mock.patch("ecosystems_cli.commands.resolve.time.sleep")
    def test_create_job_with_polling_immediate_completion(self, mock_sleep, mock_print_output, mock_api_factory):
        """Test creating a resolve job with polling when job completes immediately."""
        # Mock the initial create_job response
        create_response = {
            "id": "test-resolve-101",
            "status": "pending",
            "location": "https://resolve.ecosyste.ms/api/v1/jobs/test-resolve-101",
        }

        # Mock the get_job response (completed job)
        get_response = {
            "id": "test-resolve-101",
            "status": "completed",
            "results": {"dependencies": [{"name": "body-parser", "version": "1.20.1"}]},
        }

        # Set up the mock to return different values for different calls
        mock_api_factory.call.side_effect = [create_response, get_response]

        result = self.runner.invoke(
            self.resolve_group,
            ["create_job", "express", "npm", "--polling-interval", "1"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0

        # Verify create_job was called first
        first_call = mock_api_factory.call.call_args_list[0]
        assert first_call[0][0] == "resolve"
        assert first_call[0][1] == "createJob"
        assert first_call[1]["query_params"]["package_name"] == "express"
        assert first_call[1]["query_params"]["registry"] == "npm"

        # Verify get_job was called with jobID in path_params
        second_call = mock_api_factory.call.call_args_list[1]
        assert second_call[0][0] == "resolve"
        assert second_call[0][1] == "getJob"
        assert second_call[1]["path_params"] == {"jobID": "test-resolve-101"}
        assert second_call[1]["query_params"] == {}

        # Verify output was printed with the final result
        mock_print_output.assert_called_once_with(get_response, "json", console=mock.ANY)

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_output")
    @mock.patch("ecosystems_cli.commands.resolve.time.sleep")
    def test_create_job_with_polling_multiple_iterations(self, mock_sleep, mock_print_output, mock_api_factory):
        """Test creating a resolve job with polling through multiple status checks."""
        # Mock the initial create_job response
        create_response = {
            "id": "test-resolve-202",
            "status": "pending",
            "location": "https://resolve.ecosyste.ms/api/v1/jobs/test-resolve-202",
        }

        # Mock the get_job responses (pending -> processing -> completed)
        pending_response = {"id": "test-resolve-202", "status": "pending"}
        processing_response = {"id": "test-resolve-202", "status": "processing"}
        completed_response = {
            "id": "test-resolve-202",
            "status": "completed",
            "results": {"dependencies": [{"name": "body-parser", "version": "1.20.1"}]},
        }

        # Set up the mock to return different values for different calls
        mock_api_factory.call.side_effect = [create_response, pending_response, processing_response, completed_response]

        result = self.runner.invoke(
            self.resolve_group,
            ["create_job", "express", "npm", "--polling-interval", "0.5"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0

        # Verify we made 4 API calls total (1 create + 3 status checks)
        assert mock_api_factory.call.call_count == 4

        # Verify sleep was called 3 times (once before each status check)
        assert mock_sleep.call_count == 3
        mock_sleep.assert_called_with(0.5)

        # Verify output was printed with the final result
        mock_print_output.assert_called_once_with(completed_response, "json", console=mock.ANY)

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_output")
    @mock.patch("ecosystems_cli.commands.resolve.time.sleep")
    def test_create_job_polling_with_location_job_id(self, mock_sleep, mock_print_output, mock_api_factory):
        """Test that job ID is correctly extracted from location URL when not in response."""
        # Mock response without direct 'id' field, only location
        create_response = {
            "status": "pending",
            "location": "https://resolve.ecosyste.ms/api/v1/jobs/extracted-job-303",
        }

        completed_response = {
            "id": "extracted-job-303",
            "status": "completed",
            "results": {"dependencies": []},
        }

        mock_api_factory.call.side_effect = [create_response, completed_response]

        result = self.runner.invoke(
            self.resolve_group,
            ["create_job", "express", "npm", "--polling-interval", "1"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0

        # Verify get_job was called with the extracted job ID
        second_call = mock_api_factory.call.call_args_list[1]
        assert second_call[1]["path_params"] == {"jobID": "extracted-job-303"}

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_error")
    @mock.patch("ecosystems_cli.commands.resolve.print_output")
    def test_create_job_polling_no_job_id(self, mock_print_output, mock_print_error, mock_api_factory):
        """Test error handling when polling is requested but no job ID is available."""
        # Mock response with no 'id' and no 'location'
        create_response = {"status": "pending"}

        mock_api_factory.call.return_value = create_response

        result = self.runner.invoke(
            self.resolve_group,
            ["create_job", "express", "npm", "--polling-interval", "1"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0

        # Verify error was printed
        mock_print_error.assert_called_once_with("No job ID in response, cannot poll for completion", console=mock.ANY)
        # Verify the response was still printed
        mock_print_output.assert_called_once_with(create_response, "json", console=mock.ANY)

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_output")
    @mock.patch("ecosystems_cli.commands.resolve.time.sleep")
    def test_create_job_polling_with_failed_status(self, mock_sleep, mock_print_output, mock_api_factory):
        """Test that polling stops when job status is 'failed'."""
        create_response = {
            "id": "test-resolve-404",
            "status": "pending",
        }

        failed_response = {"id": "test-resolve-404", "status": "failed", "error": "Package not found"}

        mock_api_factory.call.side_effect = [create_response, failed_response]

        result = self.runner.invoke(
            self.resolve_group,
            ["create_job", "nonexistent-package", "npm", "--polling-interval", "1"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0

        # Verify polling stopped after detecting 'failed' status
        assert mock_api_factory.call.call_count == 2
        mock_print_output.assert_called_once_with(failed_response, "json", console=mock.ANY)

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_error")
    def test_create_job_error_handling(self, mock_print_error, mock_api_factory):
        """Test error handling when creating a job fails."""
        mock_api_factory.call.side_effect = Exception("Network error")

        result = self.runner.invoke(self.resolve_group, ["create_job", "express", "npm"], obj={"timeout": 20, "format": "json"})

        assert result.exit_code == 0
        mock_print_error.assert_called_once_with("Unexpected error: Network error", console=mock.ANY)

    @mock.patch("ecosystems_cli.commands.resolve.api_factory")
    @mock.patch("ecosystems_cli.commands.resolve.print_error")
    def test_create_job_ecosystems_error(self, mock_print_error, mock_api_factory):
        """Test error handling for EcosystemsCLIError."""
        from ecosystems_cli.exceptions import EcosystemsCLIError

        mock_api_factory.call.side_effect = EcosystemsCLIError("Invalid registry")

        result = self.runner.invoke(
            self.resolve_group, ["create_job", "express", "invalid-registry"], obj={"timeout": 20, "format": "json"}
        )

        assert result.exit_code == 0
        mock_print_error.assert_called_once_with("Invalid registry", console=mock.ANY)

    @mock.patch("ecosystems_cli.commands.execution.api_factory")
    @mock.patch("ecosystems_cli.commands.execution.print_output")
    def test_list_registries(self, mock_print_output, mock_api_factory):
        """Test listing available registries."""
        mock_api_factory.call.return_value = [
            {"name": "npmjs.org", "url": "https://www.npmjs.com", "ecosystem": "npm", "packages_count": 2000000},
            {"name": "pypi.org", "url": "https://pypi.org", "ecosystem": "pypi", "packages_count": 400000},
        ]

        result = self.runner.invoke(
            self.resolve_group,
            ["list_registries"],
            obj={"timeout": 20, "format": "json"},
        )

        assert result.exit_code == 0
        mock_api_factory.call.assert_called_once_with(
            "resolve",
            "listRegistries",
            path_params={},
            query_params={},
            timeout=mock.ANY,
            mailto=mock.ANY,
            base_url=mock.ANY,
        )
        mock_print_output.assert_called_once()
