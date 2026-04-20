"""Commands for the repos API."""

import click

from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.helpers.purl_parser import parse_purl

repos = APICommandGenerator.create_api_group("repos")


def _add_purl_to_ecosystem_package_command(command_name: str) -> None:
    """Attach --purl to a command whose first two path args are ecosystem + package.

    Makes the positional ECOSYSTEM and PACKAGE args optional, injects --purl, and
    wraps the callback so a PURL decomposes into those two args when provided.
    Positional args still win over a PURL when both are passed.
    """
    if command_name not in repos.commands:
        return

    cmd = repos.commands[command_name]

    for param in cmd.params:
        if isinstance(param, click.Argument) and param.name in ("ecosystem", "package"):
            param.required = False

    cmd.params.insert(
        0,
        click.Option(
            ["--purl"],
            type=str,
            default=None,
            help="Package URL (PURL). Example: pkg:npm/lodash. Decomposes into ECOSYSTEM and PACKAGE.",
        ),
    )
    original_callback = cmd.callback

    def wrapped_callback(*args, **kwargs):
        purl = kwargs.pop("purl", None)
        if purl:
            parsed_ecosystem, parsed_package = parse_purl(purl)
            if parsed_ecosystem and not kwargs.get("ecosystem"):
                kwargs["ecosystem"] = parsed_ecosystem
            if parsed_package and not kwargs.get("package"):
                kwargs["package"] = parsed_package
        if not kwargs.get("ecosystem") or not kwargs.get("package"):
            raise click.UsageError("Either --purl or both ECOSYSTEM and PACKAGE arguments are required")
        return original_callback(*args, **kwargs)

    cmd.callback = wrapped_callback


for _op in ("usage_package", "usage_package_dependencies", "usage_package_dependent_repositories"):
    _add_purl_to_ecosystem_package_command(_op)
