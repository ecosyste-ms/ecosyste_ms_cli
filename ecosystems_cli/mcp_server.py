"""MCP (Model Context Protocol) server for Ecosystems CLI."""

import asyncio
import json
import logging
import signal
from typing import Any, Dict, List, Optional

from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolRequestParams, CallToolResult, ListToolsResult, PaginatedRequestParams, TextContent, Tool

from ecosystems_cli import __version__
from ecosystems_cli.constants import DEFAULT_TIMEOUT
from ecosystems_cli.exceptions import EcosystemsCLIError
from ecosystems_cli.helpers.get_domain import build_base_url, get_domain_with_precedence
from ecosystems_cli.helpers.load_api_spec import load_api_spec
from ecosystems_cli.helpers.print_output import DateTimeEncoder
from ecosystems_cli.openapi_client import _factory as api_factory

logger = logging.getLogger(__name__)


class EcosystemsMCPServer:
    """MCP server providing Ecosystems CLI functionality as tools."""

    def __init__(self):
        # Must mirror the CLI command set (cli.COMMAND_REGISTRY); keep in sync.
        self.apis = [
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
        # mcp 2.x removed the @server.list_tools()/@server.call_tool() decorators;
        # protocol handlers are supplied as constructor callbacks instead. The
        # callbacks stay thin so the tool-building and routing logic below can be
        # exercised without going through the protocol layer.
        self.server = Server(
            "ecosystems-cli",
            version=__version__,
            on_list_tools=self._on_list_tools,
            on_call_tool=self._on_call_tool,
        )

    async def _on_list_tools(self, ctx: Any, params: Optional[PaginatedRequestParams]) -> ListToolsResult:
        """Protocol handler for ``tools/list``. All tools are returned in a single page."""
        return ListToolsResult(tools=self._list_tools())

    async def _on_call_tool(self, ctx: Any, params: CallToolRequestParams) -> CallToolResult:
        """Protocol handler for ``tools/call``."""
        return await self._call_tool(params.name, params.arguments or {})

    def _list_tools(self) -> List[Tool]:
        """Build the tool list from the vendored OpenAPI specs."""
        tools = []

        for api in self.apis:
            try:
                spec = load_api_spec(api)
                if not spec or "paths" not in spec:
                    continue

                # Create a tool for each operation
                for path, methods in spec["paths"].items():
                    for method, operation in methods.items():
                        if method in ["get", "post", "put", "delete", "patch"]:
                            operation_id = operation.get("operationId")
                            if not operation_id:
                                continue

                            # Build tool description
                            description = operation.get("summary", operation.get("description", ""))
                            if not description:
                                description = f"{method.upper()} {path} on {api} API"

                            # Build input schema
                            input_schema = self._build_input_schema(operation)

                            tools.append(Tool(name=f"{api}_{operation_id}", description=description, input_schema=input_schema))

                # Add a generic call tool for each API
                tools.append(
                    Tool(
                        name=f"{api}_call",
                        description=f"Call any operation on the {api} API directly",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "operation": {"type": "string", "description": "The operation ID to call"},
                                "path_params": {"type": "object", "description": "Path parameters as a JSON object"},
                                "query_params": {"type": "object", "description": "Query parameters as a JSON object"},
                                "body": {"type": "object", "description": "Request body as a JSON object"},
                            },
                            "required": ["operation"],
                        },
                    )
                )

            except Exception as e:
                logger.error(f"Error loading spec for {api}: {e}")
                continue

        return tools

    @staticmethod
    def _text_result(text: str, *, is_error: bool = False) -> CallToolResult:
        """Wrap ``text`` as a tool result, flagging failures so clients can tell them apart."""
        return CallToolResult(content=[TextContent(type="text", text=text)], is_error=is_error)

    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Route a tool call to the right API operation and return its result.

        Tool names are ``{api}_{operationId}`` plus a generic ``{api}_call`` per
        API. For specific tools, the operation's spec decides which arguments are
        path vs query parameters; ``body`` is forwarded when the operation has a
        request body. The generic ``_call`` tool passes path/query/body through
        as given.

        Failures are returned as results with ``is_error`` set rather than raised,
        so the client sees the message instead of a transport-level error.
        """
        try:
            # Parse the tool name to get API and operation
            if name.endswith("_call"):
                # Generic call tool
                api = name[:-5]  # Remove '_call' suffix
                if api not in self.apis:
                    return self._text_result(f"Unknown API: {api}", is_error=True)
                operation = arguments.get("operation")
                path_params = arguments.get("path_params", {})
                query_params = arguments.get("query_params", {})
                body = arguments.get("body", {})
            else:
                # Specific operation tool
                parts = name.split("_", 1)
                if len(parts) != 2:
                    return self._text_result(f"Invalid tool name: {name}", is_error=True)

                api, operation = parts
                if api not in self.apis:
                    return self._text_result(f"Unknown API: {api}", is_error=True)

                # Extract parameters from arguments
                path_params = {}
                query_params = {}
                body = {}

                # Load spec to determine parameter types
                spec = load_api_spec(api)
                if spec and "paths" in spec:
                    for path, methods in spec["paths"].items():
                        for method, op_spec in methods.items():
                            if op_spec.get("operationId") == operation:
                                # Extract parameters based on spec
                                for param in op_spec.get("parameters", []):
                                    param_name = param.get("name")
                                    param_in = param.get("in")

                                    if param_name in arguments:
                                        if param_in == "path":
                                            path_params[param_name] = arguments[param_name]
                                        elif param_in == "query":
                                            query_params[param_name] = arguments[param_name]

                                # Check for request body
                                if "requestBody" in op_spec and "body" in arguments:
                                    body = arguments["body"]

                                break

            # Call the API
            result = await self._call_api(api, operation, path_params, query_params, body)

            # Format the result as JSON string
            result_text = json.dumps(result, cls=DateTimeEncoder) if result else "No data returned"

            return self._text_result(result_text)

        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return self._text_result(f"Error: {str(e)}", is_error=True)

    def _build_input_schema(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Build JSON schema for tool input from OpenAPI operation."""
        schema = {"type": "object", "properties": {}, "required": []}

        # Add parameters
        for param in operation.get("parameters", []):
            param_name = param.get("name")
            param_schema = param.get("schema", {})
            param_required = param.get("required", False)

            schema["properties"][param_name] = {
                "type": param_schema.get("type", "string"),
                "description": param.get("description", ""),
            }

            if param_required:
                schema["required"].append(param_name)

        # Add request body if present
        if "requestBody" in operation:
            request_body = operation["requestBody"]
            if request_body.get("required", False):
                schema["required"].append("body")

            # Try to get schema from content
            content = request_body.get("content", {})
            if "application/json" in content:
                schema["properties"]["body"] = {
                    "type": "object",
                    "description": request_body.get("description", "Request body"),
                }

        return schema

    async def _call_api(
        self, api: str, operation: str, path_params: Dict[str, Any], query_params: Dict[str, Any], body: Dict[str, Any]
    ) -> Any:
        """Call an API operation and return the result."""
        # Get domain and build URL
        domain = get_domain_with_precedence(api, None)
        base_url = build_base_url(domain, api)

        # api_factory.call() does blocking network I/O; run it in a worker thread
        # so a slow request can't stall the asyncio event loop (and block other
        # tool calls, cancellation, or heartbeats).
        try:
            return await asyncio.to_thread(
                api_factory.call,
                api_name=api,
                operation_id=operation,
                path_params=path_params if path_params else None,
                query_params=query_params if query_params else None,
                body=body if body else None,
                timeout=DEFAULT_TIMEOUT,
                base_url=base_url,
            )
        except EcosystemsCLIError as e:
            raise Exception(f"API Error: {str(e)}")

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            # Capabilities and server identity are derived from the Server itself,
            # so the advertised version tracks the package instead of a literal.
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


def run_mcp_server():
    """Entry point for running the MCP server."""
    server = EcosystemsMCPServer()

    # Set up signal handlers for graceful shutdown
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {sig}, initiating graceful shutdown...")
        loop.call_soon_threadsafe(shutdown_event.set)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        loop.run_until_complete(server.run())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down gracefully...")
    finally:
        loop.close()


if __name__ == "__main__":
    run_mcp_server()
