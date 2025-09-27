"""Decorators for ecosystems CLI commands."""

from functools import wraps
from typing import Optional

import click

from ecosystems_cli.constants import (
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_TIMEOUT,
    OUTPUT_FORMATS,
)


def common_options(f):
    """Decorator to add common options to commands."""
    f = click.option(
        "--format",
        default=DEFAULT_OUTPUT_FORMAT,
        type=click.Choice(OUTPUT_FORMATS),
        help=f"Output format. Default is {DEFAULT_OUTPUT_FORMAT}.",
    )(f)
    f = click.option(
        "--timeout",
        default=DEFAULT_TIMEOUT,
        help=f"Timeout in seconds for API requests. Default is {DEFAULT_TIMEOUT} seconds.",
    )(f)
    f = click.option(
        "--domain",
        default=None,
        help="Override the API domain. Example: api.example.com",
    )(f)
    f = click.option(
        "--mailto",
        default=None,
        help="Email address for polite pool access. Example: you@example.com",
    )(f)
    return f


def api_command(api_name: str, operation_id: Optional[str] = None, method_name: Optional[str] = None):
    """Decorator that wraps commands with API execution logic.

    Args:
        api_name: Name of the API (e.g., 'repos', 'packages')
        operation_id: Optional operation ID for 'call' method
        method_name: Optional API client method name for direct calls
    """

    def decorator(func):
        @common_options
        @click.pass_context
        @wraps(func)
        def wrapper(ctx, timeout, format, domain, mailto, *args, **kwargs):
            from ecosystems_cli.commands.execution import execute_api_call, update_context

            # Update context with command-level options
            update_context(ctx, timeout, format, domain, mailto)

            # Execute API call
            if operation_id:
                execute_api_call(ctx, api_name, operation_id=operation_id, call_args=args, call_kwargs=kwargs)
            elif method_name:
                execute_api_call(ctx, api_name, method_name=method_name, call_kwargs=kwargs)
            else:
                # If neither is specified, assume the function will handle it
                func(ctx, *args, **kwargs)

        return wrapper

    return decorator


def resolve_context_value(ctx, key, current_value, default_value):
    """Helper to resolve context values with inheritance.

    Args:
        ctx: Click context
        key: Context key to resolve
        current_value: Current value from command options
        default_value: Default value for comparison

    Returns:
        Resolved value considering context inheritance
    """
    # If current value is not default, use it
    if current_value != default_value:
        return current_value

    # Check current context for existing value
    if ctx.obj and key in ctx.obj:
        return ctx.obj[key]

    # Check parent context
    if ctx.parent and ctx.parent.obj:
        parent_value = ctx.parent.obj.get(key, default_value)
        if parent_value != default_value:
            return parent_value

    # Return current value (which is the default)
    return current_value
