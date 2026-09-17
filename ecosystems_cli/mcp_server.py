"""MCP (Model Context Protocol) server for Ecosystems CLI."""

import asyncio
import json
import logging
import signal
from typing import Any, Dict, List, Optional, Tuple

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

HTTP_METHODS = ("get", "post", "put", "delete", "patch")

# Suffix of the generic passthrough tool exposed per API. Reserved: an upstream
# operationId of "call" would otherwise generate a colliding tool name.
GENERIC_TOOL_SUFFIX = "_call"

# Schema for the generic ``{api}_call`` passthrough tool. Kept as a constant so
# the advertised contract and the one enforced on dispatch cannot drift apart.
GENERIC_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "operation": {"type": "string", "description": "The operation ID to call"},
        "path_params": {"type": "object", "description": "Path parameters as a JSON object"},
        "query_params": {"type": "object", "description": "Query parameters as a JSON object"},
        "body": {"type": "object", "description": "Request body as a JSON object"},
    },
    "required": ["operation"],
}

# JSON Schema primitive types mapped to the Python types they accept.
JSON_SCHEMA_TYPES = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


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

    @staticmethod
    def _resolve_parameters(spec: Dict[str, Any], path_item: Dict[str, Any], operation: Dict[str, Any]) -> List[dict]:
        """Collect an operation's parameters, including the path-level ones.

        OpenAPI lets a path item declare ``parameters`` shared by all its
        operations; those are merged in here, with the operation's own entries
        taking precedence on a name clash. Local ``$ref``s into
        ``components/parameters`` are resolved, and anything still without a
        name is dropped rather than becoming a ``None`` key in the schema.
        """
        components = (spec or {}).get("components", {}).get("parameters", {})

        def resolve(param: dict) -> Optional[dict]:
            ref = param.get("$ref")
            if ref:
                if not ref.startswith("#/components/parameters/"):
                    logger.warning(f"Unsupported parameter $ref, skipping: {ref}")
                    return None
                param = components.get(ref.rsplit("/", 1)[-1])
                if param is None:
                    logger.warning(f"Unresolvable parameter $ref, skipping: {ref}")
                    return None
            if not param.get("name"):
                logger.warning(f"Parameter without a name, skipping: {param}")
                return None
            return param

        merged: Dict[str, dict] = {}
        for param in list((path_item or {}).get("parameters", [])) + list(operation.get("parameters", [])):
            resolved = resolve(param)
            if resolved:
                merged[resolved["name"]] = resolved
        return list(merged.values())

    @staticmethod
    def _find_operation(spec: Dict[str, Any], operation_id: str) -> Optional[Tuple[dict, dict]]:
        """Return the ``(path_item, operation)`` for ``operation_id``, or None.

        Stops at the first match. An earlier version kept scanning after a hit,
        so a duplicate operationId in another path merged its parameters into
        the same call.
        """
        if not spec or "paths" not in spec:
            return None
        for path_item in spec["paths"].values():
            for method, op_spec in (path_item or {}).items():
                if method in HTTP_METHODS and isinstance(op_spec, dict) and op_spec.get("operationId") == operation_id:
                    return path_item, op_spec
        return None

    def _list_tools(self) -> List[Tool]:
        """Build the tool list from the vendored OpenAPI specs."""
        tools = []

        for api in self.apis:
            try:
                spec = load_api_spec(api)
                if not spec or "paths" not in spec:
                    continue

                # Create a tool for each operation
                for path, path_item in spec["paths"].items():
                    for method, operation in (path_item or {}).items():
                        if method in HTTP_METHODS and isinstance(operation, dict):
                            operation_id = operation.get("operationId")
                            if not operation_id:
                                continue

                            tool_name = f"{api}_{operation_id}"
                            if tool_name.endswith(GENERIC_TOOL_SUFFIX):
                                # Would collide with the generic passthrough tool below,
                                # producing two tools with the same name.
                                logger.warning(f"Skipping {api} operation '{operation_id}': name reserved for the generic tool")
                                continue

                            # Build tool description
                            description = operation.get("summary", operation.get("description", ""))
                            if not description:
                                description = f"{method.upper()} {path} on {api} API"

                            # Build input schema
                            parameters = self._resolve_parameters(spec, path_item, operation)
                            input_schema = self._build_input_schema(operation, parameters)

                            tools.append(Tool(name=tool_name, description=description, input_schema=input_schema))

                # Add a generic call tool for each API
                tools.append(
                    Tool(
                        name=f"{api}{GENERIC_TOOL_SUFFIX}",
                        description=f"Call any operation on the {api} API directly",
                        input_schema=GENERIC_TOOL_SCHEMA,
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

    @staticmethod
    def _type_matches(expected: str, value: Any) -> bool:
        """Check ``value`` against a JSON Schema primitive type name."""
        python_type = JSON_SCHEMA_TYPES.get(expected)
        if python_type is None:
            return True
        # bool is a subclass of int, but a boolean is not an acceptable number.
        if expected in ("integer", "number") and isinstance(value, bool):
            return False
        return isinstance(value, python_type)

    @classmethod
    def _validate_arguments(cls, tool_name: str, schema: Dict[str, Any], arguments: Dict[str, Any]) -> Optional[str]:
        """Check ``arguments`` against the tool's advertised schema.

        Returns an error message, or None when the arguments are acceptable.
        Catching this here keeps a misspelled or missing argument from being
        silently dropped and turned into a different call than the one asked for.
        """
        properties = schema.get("properties", {})

        missing = sorted(name for name in schema.get("required", []) if name not in arguments)
        if missing:
            return f"Missing required argument(s) for {tool_name}: {', '.join(missing)}"

        unknown = sorted(name for name in arguments if name not in properties)
        if unknown:
            expected = ", ".join(sorted(properties)) or "none"
            return f"Unknown argument(s) for {tool_name}: {', '.join(unknown)}. Expected: {expected}"

        for name, value in arguments.items():
            expected_type = properties.get(name, {}).get("type")
            if value is not None and expected_type and not cls._type_matches(expected_type, value):
                got = type(value).__name__
                return f"Argument '{name}' for {tool_name} expects type {expected_type}, got {got}"

        return None

    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Route a tool call to the right API operation and return its result.

        Tool names are ``{api}_{operationId}`` plus a generic ``{api}_call`` per
        API. For specific tools, the operation's spec decides which arguments are
        path vs query parameters; ``body`` is forwarded when the operation has a
        request body. The generic ``_call`` tool passes path/query/body through
        as given.

        Arguments are validated against the tool's advertised schema before any
        request is made. Failures are returned as results with ``is_error`` set
        rather than raised, so the client sees the message instead of a
        transport-level error.
        """
        try:
            if name.endswith(GENERIC_TOOL_SUFFIX):
                # Generic call tool
                api = name[: -len(GENERIC_TOOL_SUFFIX)]
                if api not in self.apis:
                    return self._text_result(f"Unknown tool: {name}", is_error=True)

                error = self._validate_arguments(name, GENERIC_TOOL_SCHEMA, arguments)
                if error:
                    return self._text_result(error, is_error=True)

                operation = arguments["operation"]
                path_params = arguments.get("path_params") or {}
                query_params = arguments.get("query_params") or {}
                body = arguments.get("body") or {}
            else:
                # Specific operation tool
                api, _, operation = name.partition("_")
                if not operation or api not in self.apis:
                    return self._text_result(
                        f"Invalid tool name: {name}" if not operation else f"Unknown tool: {name}", is_error=True
                    )

                # Load spec to determine parameter types
                spec = load_api_spec(api)
                found = self._find_operation(spec, operation)
                if found is None:
                    return self._text_result(f"Unknown tool: {name}", is_error=True)
                path_item, op_spec = found

                parameters = self._resolve_parameters(spec, path_item, op_spec)
                error = self._validate_arguments(name, self._build_input_schema(op_spec, parameters), arguments)
                if error:
                    return self._text_result(error, is_error=True)

                # Split the validated arguments into path vs query parameters
                path_params = {}
                query_params = {}
                body = {}
                for param in parameters:
                    param_name = param["name"]
                    if param_name in arguments:
                        if param.get("in") == "path":
                            path_params[param_name] = arguments[param_name]
                        elif param.get("in") == "query":
                            query_params[param_name] = arguments[param_name]

                if "requestBody" in op_spec and "body" in arguments:
                    body = arguments["body"]

            # Call the API
            result = await self._call_api(api, operation, path_params, query_params, body)

            # Format the result as JSON string. Only a genuinely absent result is
            # reported as such: [], {}, 0 and false are valid answers, and saying
            # "No data returned" for them hides a real response from the client.
            result_text = "No data returned" if result is None else json.dumps(result, cls=DateTimeEncoder)

            return self._text_result(result_text)

        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            # Some exceptions carry no message; fall back to the type so the
            # client gets something more useful than a bare "Error:".
            return self._text_result(f"Error: {str(e) or type(e).__name__}", is_error=True)

    def _build_input_schema(self, operation: Dict[str, Any], parameters: Optional[List[dict]] = None) -> Dict[str, Any]:
        """Build JSON schema for tool input from OpenAPI operation.

        ``parameters`` is the resolved parameter list from
        :meth:`_resolve_parameters`; it defaults to the operation's own entries.
        """
        schema = {"type": "object", "properties": {}, "required": []}

        if parameters is None:
            parameters = [p for p in operation.get("parameters", []) if p.get("name")]

        # Add parameters, preserving the spec's own schema for each so that
        # constraints like `items`, `enum` and `format` reach the client.
        for param in parameters:
            param_name = param.get("name")
            param_schema = dict(param.get("schema") or {})
            param_schema["description"] = param.get("description", "")

            schema["properties"][param_name] = param_schema

            if param.get("required", False):
                schema["required"].append(param_name)

        # Add request body if present
        if "requestBody" in operation:
            request_body = operation["requestBody"]

            # Carry the body's own schema through, so the client knows which
            # fields to send instead of being handed an opaque object.
            content = request_body.get("content", {})
            body_schema = dict((content.get("application/json") or {}).get("schema") or {})
            body_schema.setdefault("type", "object")
            body_schema["description"] = request_body.get("description", "Request body")

            schema["properties"]["body"] = body_schema

            if request_body.get("required", False):
                schema["required"].append("body")

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
            # Re-raised as the same type, so callers can still catch it specifically.
            raise EcosystemsCLIError(f"API Error: {str(e)}") from e

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
