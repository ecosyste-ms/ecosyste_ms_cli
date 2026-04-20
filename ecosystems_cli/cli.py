"""Command line interface for ecosystems CLI."""

import json
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel

from ecosystems_cli import __version__
from ecosystems_cli.commands.advisories import advisories
from ecosystems_cli.commands.archives import archives
from ecosystems_cli.commands.commits import commits
from ecosystems_cli.commands.dependabot import dependabot
from ecosystems_cli.commands.diff import diff
from ecosystems_cli.commands.docker import docker
from ecosystems_cli.commands.issues import issues
from ecosystems_cli.commands.licenses import licenses
from ecosystems_cli.commands.mcp import mcp
from ecosystems_cli.commands.opencollective import opencollective
from ecosystems_cli.commands.packages import packages
from ecosystems_cli.commands.parser import parser
from ecosystems_cli.commands.repos import repos
from ecosystems_cli.commands.resolve import resolve
from ecosystems_cli.commands.sbom import sbom
from ecosystems_cli.commands.sponsors import sponsors
from ecosystems_cli.commands.summary import summary
from ecosystems_cli.commands.timeline import timeline
from ecosystems_cli.constants import (
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_TIMEOUT,
    ERROR_PANEL_STYLE,
    ERROR_PREFIX,
    OUTPUT_FORMATS,
)
from ecosystems_cli.exceptions import EcosystemsCLIError, JSONParseError
from ecosystems_cli.helpers.format_value import format_value
from ecosystems_cli.helpers.get_domain import build_base_url, get_domain_with_precedence
from ecosystems_cli.helpers.print_operations import print_operations
from ecosystems_cli.helpers.print_output import print_output
from ecosystems_cli.openapi_client import _factory as api_factory

console = Console()


@click.group(invoke_without_command=True)
@click.option(
    "--timeout",
    default=DEFAULT_TIMEOUT,
    help=f"Timeout in seconds for API requests. Default is {DEFAULT_TIMEOUT} seconds.",
)
@click.option(
    "--format",
    default=DEFAULT_OUTPUT_FORMAT,
    type=click.Choice(OUTPUT_FORMATS),
    help=f"Output format. Default is {DEFAULT_OUTPUT_FORMAT}.",
)
@click.option(
    "--domain",
    default=None,
    help="Override the API domain. Example: api.example.com",
)
@click.option(
    "--mailto",
    default=None,
    help="Email address for polite pool access. Example: you@example.com",
)
@click.option(
    "--install-completion",
    is_flag=True,
    help="Show instructions for installing shell completion.",
)
@click.pass_context
def main(ctx, timeout, format, domain, mailto, install_completion):
    """Ecosystems CLI for interacting with ecosyste.ms APIs."""
    # Handle completion installation instructions
    if install_completion:
        click.echo("Shell completion installation instructions:\n")
        click.echo("For bash, add to ~/.bashrc:")
        click.echo('  eval "$(_ECOSYSTEMS_COMPLETE=bash_source ecosystems)"')
        click.echo("\nFor zsh, add to ~/.zshrc:")
        click.echo('  eval "$(_ECOSYSTEMS_COMPLETE=zsh_source ecosystems)"')
        click.echo("\nFor fish, add to ~/.config/fish/config.fish:")
        click.echo("  _ECOSYSTEMS_COMPLETE=fish_source ecosystems | source")
        click.echo("\nThen restart your shell or source the configuration file.")
        ctx.exit()

    # If no command is provided and not handling completion, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()

    ctx.ensure_object(dict)
    ctx.obj["timeout"] = timeout
    ctx.obj["format"] = format
    ctx.obj["domain"] = domain
    ctx.obj["mailto"] = mailto


# Command Registration Strategy:
# We use a hybrid approach for command registration to balance usability and flexibility:
#
# 1. High-level API commands (e.g., 'ecosystems repos', 'ecosystems packages')
#    - Registered via COMMAND_REGISTRY below
#    - Provide user-friendly commands with custom logic and convenience methods
#    - Each command is a BaseCommand subclass with tailored functionality
#
# 2. Low-level operation commands (e.g., 'ecosystems op repos get_topic')
#    - Registered dynamically in register_op_commands()
#    - Provide direct access to all API operations
#    - Auto-generated from OpenAPI specifications

# Command registry - maps API names to their command instances
COMMAND_REGISTRY = {
    "advisories": advisories,
    "archives": archives,
    "commits": commits,
    "dependabot": dependabot,
    "diff": diff,
    "docker": docker,
    "issues": issues,
    "licenses": licenses,
    "opencollective": opencollective,
    "packages": packages,
    "parser": parser,
    "repos": repos,
    "resolve": resolve,
    "sbom": sbom,
    "sponsors": sponsors,
    "summary": summary,
    "timeline": timeline,
}

# Register all high-level commands dynamically from the registry
for api_name, command in COMMAND_REGISTRY.items():
    main.add_command(command)

# Register MCP server command
main.add_command(mcp)
# Dynamic op commands have been removed


@main.command(name="version", help="Show the ecosystems CLI version and exit.")
def version():
    """Print the installed ecosystems CLI version."""
    click.echo(__version__)


def _parse_json_param(param: Optional[str]) -> Optional[Dict]:
    """Parse JSON parameter if provided."""
    if not param:
        return None
    try:
        return json.loads(param)
    except json.JSONDecodeError as e:
        raise JSONParseError(f"Invalid JSON: {param}. Error: {str(e)}")


def _call_operation(api: str, operation: str, path_params: str, query_params: str, body: str, context=None):
    """Call an operation on the specified API."""
    # Get timeout, format, and domain from context if available
    if context and hasattr(context, "obj"):
        timeout = context.obj.get("timeout", DEFAULT_TIMEOUT)
        format_type = context.obj.get("format", DEFAULT_OUTPUT_FORMAT)
        domain = context.obj.get("domain")
    else:
        timeout = DEFAULT_TIMEOUT
        format_type = DEFAULT_OUTPUT_FORMAT
        domain = None

    # Get domain with proper precedence
    final_domain = get_domain_with_precedence(api, domain)
    base_url = build_base_url(final_domain, api)

    try:
        # Parse parameters
        path_params_dict = _parse_json_param(path_params)
        query_params_dict = _parse_json_param(query_params)
        body_dict = _parse_json_param(body)

        result = api_factory.call(
            api_name=api,
            operation_id=operation,
            path_params=path_params_dict,
            query_params=query_params_dict,
            body=body_dict,
            timeout=timeout,
            base_url=base_url,
        )
        _print_output(result, format_type)
    except JSONParseError as e:
        _print_error(str(e))
    except EcosystemsCLIError as e:
        _print_error(str(e))
    except Exception as e:
        _print_error(f"Unexpected error: {str(e)}")


def _print_output(data: Any, format_type: str = "table"):
    """Print data in the specified format."""
    print_output(data, format_type, console=console)


def _format_value(value: Any) -> str:
    """Deprecated: use format_value from helpers.format_value instead."""
    return format_value(value)


def _print_json(data: Any):
    """Print JSON data in a nicely formatted way."""
    _print_output(data, "json")


def _print_error(error_msg: str):
    """Print error message in a nicely formatted way."""
    console.print(Panel(f"{ERROR_PREFIX} {error_msg}", border_style=ERROR_PANEL_STYLE))


def _print_operations(operations: List[Dict]):
    print_operations(operations, console=console)
