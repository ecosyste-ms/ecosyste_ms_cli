"""Command line interface for ecosystems CLI."""

import click

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
    OUTPUT_FORMATS,
)


@click.group(invoke_without_command=True)
@click.version_option(__version__, "--version", prog_name="ecosystems")
@click.option(
    "--timeout",
    default=DEFAULT_TIMEOUT,
    # Same bounds as commands/decorators.py common_options.
    type=click.IntRange(min=1, max=86400),
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


# Command registry - maps API names to their command instances
# (each value is a Click group generated from an OpenAPI spec).
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


@main.command(name="version", help="Show the ecosystems CLI version and exit.")
def version():
    """Print the installed ecosystems CLI version."""
    click.echo(__version__)
