"""Commands for the dependabot API."""

import click

from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.helpers.purl_parser import parse_purl

dependabot = APICommandGenerator.create_api_group("dependabot")


# Attach --purl as an optional parameter to the auto-generated get_advisories
# command. When provided, its type/name decompose into --ecosystem/--package-name,
# letting users pass a single PURL instead of two flags.
if "get_advisories" in dependabot.commands:
    _get_advisories_cmd = dependabot.commands["get_advisories"]
    _get_advisories_cmd.params.insert(
        0,
        click.Option(
            ["--purl"],
            type=str,
            default=None,
            help="Package URL (PURL). Example: pkg:npm/fsa. Decomposes into --ecosystem and --package-name.",
        ),
    )
    _original_get_advisories_callback = _get_advisories_cmd.callback

    def _get_advisories_with_purl(*args, **kwargs):
        purl = kwargs.pop("purl", None)
        if purl:
            parsed_ecosystem, parsed_package_name = parse_purl(purl)
            if parsed_ecosystem:
                kwargs["ecosystem"] = parsed_ecosystem
            if parsed_package_name:
                kwargs["package_name"] = parsed_package_name
        return _original_get_advisories_callback(*args, **kwargs)

    _get_advisories_cmd.callback = _get_advisories_with_purl
