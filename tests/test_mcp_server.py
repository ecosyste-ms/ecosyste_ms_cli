"""Tests for MCP server functionality."""

import json
from unittest import mock
from unittest.mock import patch

import pytest
from mcp.types import CallToolRequestParams, ListToolsResult

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

    @patch("ecosystems_cli.mcp_server.load_api_spec")
    def test_list_tools(self, mock_load_spec, mcp_server, mock_api_spec):
        """Each spec operation becomes a tool, plus a generic {api}_call per API."""
        mock_load_spec.return_value = mock_api_spec

        tools = mcp_server._list_tools()
        names = {t.name for t in tools}

        # One tool per operation, namespaced by API.
        assert "repos_get_repository" in names
        assert "packages_create_package" in names
        # One generic passthrough tool per API, for every API.
        assert {f"{api}_call" for api in mcp_server.apis} <= names

        repo_tool = next(t for t in tools if t.name == "repos_get_repository")
        assert repo_tool.description == "Get repository information"
        assert set(repo_tool.input_schema["required"]) == {"host", "owner", "name"}

    @patch("ecosystems_cli.mcp_server.load_api_spec")
    def test_list_tools_skips_unloadable_spec(self, mock_load_spec, mcp_server):
        """A spec that fails to load is logged and skipped, not fatal to the listing."""
        mock_load_spec.side_effect = Exception("bad spec")

        assert mcp_server._list_tools() == []

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.load_api_spec")
    async def test_on_list_tools_wraps_result(self, mock_load_spec, mcp_server, mock_api_spec):
        """The tools/list handler returns a ListToolsResult carrying the tool list."""
        mock_load_spec.return_value = mock_api_spec

        result = await mcp_server._on_list_tools(None, None)

        assert isinstance(result, ListToolsResult)
        assert {t.name for t in result.tools} == {t.name for t in mcp_server._list_tools()}

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_on_call_tool_passes_name_and_arguments(self, mock_call_api, mcp_server):
        """The tools/call handler forwards the request params to the router."""
        mock_call_api.return_value = {"ok": True}

        params = CallToolRequestParams(name="packages_call", arguments={"operation": "getRegistries"})
        result = await mcp_server._on_call_tool(None, params)

        mock_call_api.assert_awaited_once_with("packages", "getRegistries", {}, {}, {})
        assert json.loads(result.content[0].text) == {"ok": True}

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_on_call_tool_tolerates_absent_arguments(self, mock_call_api, mcp_server):
        """arguments is optional in the protocol; a missing one is treated as empty."""
        result = await mcp_server._on_call_tool(None, CallToolRequestParams(name="bogus"))

        assert result.content[0].text == "Invalid tool name: bogus"
        assert result.is_error is True
        mock_call_api.assert_not_called()

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
        assert json.loads(result.content[0].text) == {"ok": True}
        assert result.is_error is False

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
        assert json.loads(result.content[0].text) == {"packages": []}
        assert result.is_error is False

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_unknown_api_specific(self, mock_call_api, mcp_server):
        """An unknown API in a specific tool name is rejected without calling the API."""
        result = await mcp_server._call_tool("bogus_getThing", {})

        assert result.content[0].text == "Unknown API: bogus"
        assert result.is_error is True
        mock_call_api.assert_not_called()

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_unknown_api_generic(self, mock_call_api, mcp_server):
        """An unknown API in the generic ``_call`` form is rejected too."""
        result = await mcp_server._call_tool("bogus_call", {"operation": "x"})

        assert result.content[0].text == "Unknown API: bogus"
        assert result.is_error is True
        mock_call_api.assert_not_called()

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_invalid_name(self, mock_call_api, mcp_server):
        """A tool name with no API/operation separator is rejected."""
        result = await mcp_server._call_tool("bogus", {})

        assert result.content[0].text == "Invalid tool name: bogus"
        assert result.is_error is True
        mock_call_api.assert_not_called()

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_empty_result(self, mock_call_api, mcp_server):
        """A falsy API result is reported as 'No data returned'."""
        mock_call_api.return_value = {}

        result = await mcp_server._call_tool("packages_call", {"operation": "x"})

        assert result.content[0].text == "No data returned"
        assert result.is_error is False

    @pytest.mark.asyncio
    @patch("ecosystems_cli.mcp_server.EcosystemsMCPServer._call_api")
    async def test_call_tool_surfaces_errors_as_text(self, mock_call_api, mcp_server):
        """Exceptions from the API call are caught and flagged as an error result, not raised."""
        mock_call_api.side_effect = Exception("boom")

        result = await mcp_server._call_tool("packages_call", {"operation": "x"})

        assert result.content[0].text == "Error: boom"
        assert result.is_error is True

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
