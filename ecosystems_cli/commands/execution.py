"""API execution helpers for ecosystems CLI commands."""

import sys
from typing import Optional

from rich.console import Console

from ecosystems_cli.commands.handlers import OperationHandlerFactory
from ecosystems_cli.constants import DEFAULT_OUTPUT_FORMAT, DEFAULT_TIMEOUT
from ecosystems_cli.exceptions import EcosystemsCLIError
from ecosystems_cli.helpers.get_domain import build_base_url, get_domain_with_precedence
from ecosystems_cli.helpers.print_error import print_error
from ecosystems_cli.helpers.print_output import print_output
from ecosystems_cli.openapi_client import _factory as api_factory

console = Console()
# Diagnostics go to stderr so stdout stays machine-parseable: piping
# `--format json` output must never receive an error panel as data.
err_console = Console(stderr=True)


def update_context(ctx, timeout: int, format: str, domain: Optional[str], mailto: Optional[str] = None):
    """Merge command-level options into ``ctx.obj``.

    The single context-precedence mechanism, used by both the API group callback
    and every leaf command. An option is written only when it differs from its
    default (i.e. was explicitly set at this level); otherwise the value already
    in ``ctx.obj`` -- inherited from the parent context -- is left untouched.
    The net precedence is therefore: leaf option > group option > root option >
    default.

    Args:
        ctx: Click context
        timeout: Timeout value from command options
        format: Format value from command options
        domain: Domain value from command options
        mailto: Email address for polite pool access
    """
    ctx.ensure_object(dict)
    if timeout != DEFAULT_TIMEOUT:
        ctx.obj["timeout"] = timeout
    if format != DEFAULT_OUTPUT_FORMAT:
        ctx.obj["format"] = format
    if domain is not None:
        ctx.obj["domain"] = domain
    if mailto is not None:
        ctx.obj["mailto"] = mailto


def _extract_body(call_kwargs: dict, body_keys: Optional[list]) -> dict:
    """Pull request-body fields out of ``call_kwargs`` into a JSON body dict.

    Removes each ``body_keys`` entry from ``call_kwargs`` (mutating it) so the
    remaining kwargs map cleanly to path/query parameters. Unset values are
    dropped; Click's repeatable options arrive as tuples and are normalized to
    lists so they serialize as JSON arrays.
    """
    body: dict = {}
    for key in body_keys or []:
        value = call_kwargs.pop(key, None)
        if value is None or value == ():
            continue
        body[key] = list(value) if isinstance(value, tuple) else value
    return body


def execute_api_call(
    ctx,
    api_name: str,
    operation_id: str,
    call_args: tuple = (),
    call_kwargs: Optional[dict] = None,
    body_keys: Optional[list] = None,
):
    """Execute an API call with proper error handling.

    Args:
        ctx: Click context
        api_name: Name of the API (e.g., 'repos', 'packages')
        operation_id: Operation ID to call
        call_args: Positional arguments for the API call
        call_kwargs: Keyword arguments for the API call
        body_keys: Names of kwargs that belong in the JSON request body rather
            than the path/query parameters
    """
    if call_kwargs is None:
        call_kwargs = {}

    # Separate request-body fields before path/query mapping.
    body = _extract_body(call_kwargs, body_keys)

    # Get domain with proper precedence
    domain = get_domain_with_precedence(api_name, ctx.obj.get("domain"))
    base_url = build_base_url(domain, api_name)

    try:
        handler = OperationHandlerFactory.get_handler(api_name)
        path_params, query_params = handler.build_params(operation_id, call_args, call_kwargs)

        call_params = {
            "path_params": path_params,
            "query_params": query_params,
            "timeout": ctx.obj.get("timeout", DEFAULT_TIMEOUT),
            "mailto": ctx.obj.get("mailto"),
            "base_url": base_url,
        }
        # Only send a body when there is one, so body-less calls keep their
        # existing call signature.
        if body:
            call_params["body"] = body

        result = api_factory.call(api_name, operation_id, **call_params)

        print_output(result, ctx.obj.get("format", DEFAULT_OUTPUT_FORMAT), console=console)
    except EcosystemsCLIError as e:
        print_error(str(e), console=err_console)
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}", console=err_console)
        sys.exit(1)
