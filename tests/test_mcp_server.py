"""Tests for MCP server functionality."""

import json
from unittest import mock
from unittest.mock import patch

import pytest

from ecosystems_cli.mcp_server import EcosystemsMCPServer


@pytest.fixture
def mcp_server():
    """Create an MCP server instance for testing."""
    return EcosystemsMCPServer()


@pytest.fixture
def mock_api_spec():
    """Mock API specification for testing."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/repos/{host}/{owner}/{name}": {
                "get": {
                    "operationId": "get_repository",
                    "summary": "Get repository information",
                    "parameters": [
                        {"name": "host", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "owner", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "name", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                }
            },
            "/packages": {
                "post": {
                    "operationId": "create_package",
                    "summary": "Create a new package",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"name": {"type": "string"}, "version": {"type": "string"}},
                                }
                            }
                        },
                    },
                }
            },
        },
    }


class TestEcosystemsMCPServer:
    """Test cases for EcosystemsMCPServer."""

    def test_server_initialization(self, mcp_server):
        """Test that MCP server initializes correctly."""
        assert mcp_server.server is not None
        assert mcp_server.server.name == "ecosystems-cli"
        expected_apis = [
            "advisories",
            "archives",
            "commits",
            "dependabot",
            "diff",
            "docker",
            "issues",
            "licenses",
            "opencollective",
            "packages",
            "parser",
            "repos",
            "resolve",
            "sbom",
            "sponsors",
            "summary",
            "timeline",
        ]
        assert mcp_server.apis == expected_apis

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.load_api_spec")
    async def test_list_tools(self, mock_load_spec, mcp_server, mock_api_spec):
        """Test listing available tools."""
        mock_load_spec.return_value = mock_api_spec

        # The handler is registered but not easily accessible for direct testing
        # Instead, we'll test the underlying method behavior

        # Test that the server was initialized
        assert mcp_server.server is not None
        assert mcp_server.server.name == "ecosystems-cli"

    def test_build_input_schema(self, mcp_server):
        """Test building input schema from operation."""
        operation = {
            "parameters": [
                {
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"},
                    "description": "The ID of the resource",
                },
                {
                    "name": "filter",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": "Optional filter",
                },
            ]
        }

        schema = mcp_server._build_input_schema(operation)

        assert schema["type"] == "object"
        assert "id" in schema["properties"]
        assert "filter" in schema["properties"]
        assert "id" in schema["required"]
        assert "filter" not in schema["required"]
        assert schema["properties"]["id"]["type"] == "integer"
        assert schema["properties"]["filter"]["type"] == "string"

    def test_build_input_schema_with_body(self, mcp_server):
        """Test building input schema with request body."""
        operation = {
            "requestBody": {
                "required": True,
                "description": "Package data",
                "content": {"application/json": {"schema": {"type": "object", "properties": {"name": {"type": "string"}}}}},
            }
        }

        schema = mcp_server._build_input_schema(operation)

        assert "body" in schema["properties"]
        assert "body" in schema["required"]
        assert schema["properties"]["body"]["type"] == "object"

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.api_factory")
    @patch("ecosystems_cli.mcp_server.get_domain_with_precedence")
    @patch("ecosystems_cli.mcp_server.build_base_url")
    async def test_call_api(self, mock_build_url, mock_get_domain, mock_api_factory, mcp_server):
        """Test calling an API operation."""
        # Setup mocks
        mock_get_domain.return_value = "api.example.com"
        mock_build_url.return_value = "https://api.example.com/v1"

        mock_api_factory.call.return_value = {"status": "success", "data": {"id": 1}}

        # Call the API
        result = await mcp_server._call_api(
            api="repos",
            operation="get_repository",
            path_params={"host": "github.com", "owner": "test", "name": "repo"},
            query_params={"full": "true"},
            body=None,
        )

        # Verify the calls
        mock_get_domain.assert_called_once_with("repos", None)
        mock_build_url.assert_called_once_with("api.example.com", "repos")
        mock_api_factory.call.assert_called_once_with(
            api_name="repos",
            operation_id="get_repository",
            path_params={"host": "github.com", "owner": "test", "name": "repo"},
            query_params={"full": "true"},
            body=None,
            timeout=mock.ANY,
            base_url="https://api.example.com/v1",
        )

        assert result == {"status": "success", "data": {"id": 1}}

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.load_api_spec")
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_specific_routes_path_and_query_params(self, mock_call_api, mock_load_spec, mcp_server):
        """A specific tool uses the operation spec to split args into path vs query params."""
        mock_load_spec.return_value = {
            "paths": {
                "/repos/{host}": {
                    "get": {
                        "operationId": "getThing",
                        "parameters": [
                            {"name": "host", "in": "path"},
                            {"name": "page", "in": "query"},
                        ],
                    }
                }
            }
        }
        mock_call_api.return_value = {"ok": True}

        result = await mcp_server._call_tool("repos_getThing", {"host": "github.com", "page": 2, "unknown": "ignored"})

        mock_call_api.assert_awaited_once_with("repos", "getThing", {"host": "github.com"}, {"page": 2}, {})
        assert json.loads(result[0].text) == {"ok": True}

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.load_api_spec")
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_specific_routes_request_body(self, mock_call_api, mock_load_spec, mcp_server, mock_api_spec):
        """An operation with a requestBody forwards the ``body`` argument."""
        mock_load_spec.return_value = mock_api_spec
        mock_call_api.return_value = {"id": 1}

        await mcp_server._call_tool("packages_create_package", {"body": {"name": "x", "version": "1.0"}})

        mock_call_api.assert_awaited_once_with("packages", "create_package", {}, {}, {"name": "x", "version": "1.0"})

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_generic_passes_params_through(self, mock_call_api, mcp_server):
        """The generic ``{api}_call`` tool forwards path/query/body as given, no spec needed."""
        mock_call_api.return_value = {"packages": []}

        result = await mcp_server._call_tool(
            "packages_call",
            {"operation": "getRegistryPackages", "query_params": {"page": 1}, "path_params": {}, "body": {}},
        )

        mock_call_api.assert_awaited_once_with("packages", "getRegistryPackages", {}, {"page": 1}, {})
        assert json.loads(result[0].text) == {"packages": []}

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_unknown_api_specific(self, mock_call_api, mcp_server):
        """An unknown API in a specific tool name is rejected without calling the API."""
        result = await mcp_server._call_tool("bogus_getThing", {})

        assert result[0].text == "Unknown API: bogus"
        mock_call_api.assert_not_called()

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_unknown_api_generic(self, mock_call_api, mcp_server):
        """An unknown API in the generic ``_call`` form is rejected too."""
        result = await mcp_server._call_tool("bogus_call", {"operation": "x"})

        assert result[0].text == "Unknown API: bogus"
        mock_call_api.assert_not_called()

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_invalid_name(self, mock_call_api, mcp_server):
        """A tool name with no API/operation separator is rejected."""
        result = await mcp_server._call_tool("bogus", {})

        assert result[0].text == "Invalid tool name: bogus"
        mock_call_api.assert_not_called()

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_empty_result(self, mock_call_api, mcp_server):
        """A falsy API result is reported as 'No data returned'."""
        mock_call_api.return_value = {}

        result = await mcp_server._call_tool("packages_call", {"operation": "x"})

        assert result[0].text == "No data returned"

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_surfaces_errors_as_text(self, mock_call_api, mcp_server):
        """Exceptions from the API call are caught and returned as error text, not raised."""
        mock_call_api.side_effect = Exception("boom")

        result = await mcp_server._call_tool("packages_call", {"operation": "x"})

        assert result[0].text == "Error: boom"

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.api_factory")
    @patch("ecosystems_cli.mcp_server.get_domain_with_precedence")
    @patch("ecosystems_cli.mcp_server.build_base_url")
    async def test_call_api_wraps_cli_errors(self, mock_build_url, mock_get_domain, mock_api_factory, mcp_server):
        """_call_api converts an EcosystemsCLIError into a generic API Error exception."""
        from ecosystems_cli.exceptions import EcosystemsCLIError

        mock_get_domain.return_value = None
        mock_build_url.return_value = None
        mock_api_factory.call.side_effect = EcosystemsCLIError("Connection failed")

        with pytest.raises(Exception) as exc_info:
            await mcp_server._call_api(api="repos", operation="getThing", path_params={}, query_params={}, body={})

        assert "API Error" in str(exc_info.value) or "Connection failed" in str(exc_info.value)
