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


def override_auto_command(group: click.Group, name: str, **command_kwargs):
    """Register a custom command in place of an auto-generated one.

    Drops any command already registered on ``group`` under ``name`` (the
    auto-generated version), then registers the decorated function via
    ``group.command(name=name, **command_kwargs)``. Use this as the outermost
    decorator instead of a bare ``del group.commands[name]`` followed by
    ``@group.command(name=name, ...)``.
    """

    def decorator(func):
        group.commands.pop(name, None)
        return group.command(name=name, **command_kwargs)(func)

    return decorator


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
