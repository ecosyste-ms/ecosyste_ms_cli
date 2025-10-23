"""MCP (Model Context Protocol) server for Ecosystems CLI."""

import asyncio
import json
import logging
import signal
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ServerCapabilities, TextContent, Tool

from ecosystems_cli.constants import DEFAULT_TIMEOUT
from ecosystems_cli.exceptions import EcosystemsCLIError
from ecosystems_cli.helpers.get_domain import build_base_url, get_domain_with_precedence
from ecosystems_cli.helpers.load_api_spec import load_api_spec
from ecosystems_cli.openapi_client import _factory as api_factory

logger = logging.getLogger(__name__)


class EcosystemsMCPServer:
    """MCP server providing Ecosystems CLI functionality as tools."""

    def __init__(self):
        self.server = Server("ecosystems-cli")
        self.apis = [
            "advisories",
            "archives",
            "dependabot",
            "diff",
            "repos",
            "packages",
            "issues",
            "licenses",
            "sponsors",
            "timeline",
            "docker",
            "opencollective",
            "parser",
            "resolve",
            "sbom",
        ]
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools from the Ecosystems APIs."""
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

                                tools.append(
                                    Tool(name=f"{api}_{operation_id}", description=description, inputSchema=input_schema)
                                )

                    # Add a generic call tool for each API
                    tools.append(
                        Tool(
                            name=f"{api}_call",
                            description=f"Call any operation on the {api} API directly",
                            inputSchema={
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

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a tool call."""
            try:
                # Parse the tool name to get API and operation
                if name.endswith("_call"):
                    # Generic call tool
                    api = name[:-5]  # Remove '_call' suffix
                    operation = arguments.get("operation")
                    path_params = arguments.get("path_params", {})
                    query_params = arguments.get("query_params", {})
                    body = arguments.get("body", {})
                else:
                    # Specific operation tool
                    parts = name.split("_", 1)
                    if len(parts) != 2:
                        return [TextContent(type="text", text=f"Invalid tool name: {name}")]

                    api, operation = parts

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
                result_text = json.dumps(result) if result else "No data returned"

                return [TextContent(type="text", text=result_text)]

            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

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

        # Call the operation using API factory
        try:
            result = api_factory.call(
                api_name=api,
                operation_id=operation,
                path_params=path_params if path_params else None,
                query_params=query_params if query_params else None,
                body=body if body else None,
                timeout=DEFAULT_TIMEOUT,
                base_url=base_url,
            )
            return result
        except EcosystemsCLIError as e:
            raise Exception(f"API Error: {str(e)}")

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ecosystems-cli", server_version="1.0.0", capabilities=ServerCapabilities(tools={})
                ),
            )


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
