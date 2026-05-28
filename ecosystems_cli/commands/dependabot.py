"""Commands for the dependabot API."""

from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.commands.purl_options import attach_purl_option

dependabot = APICommandGenerator.create_api_group("dependabot")

# getAdvisories filters by ecosystem name and package_name (query options), so the
# PURL type is passed through unmapped and both parts stay optional filters.
attach_purl_option(
    dependabot,
    "get_advisories",
    targets=("ecosystem", "package_name"),
    map_types=False,
    example="pkg:npm/fsa. Decomposes into --ecosystem and --package-name.",
)
