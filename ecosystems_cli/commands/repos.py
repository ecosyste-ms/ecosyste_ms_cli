"""Commands for the repos API."""

from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.commands.purl_options import attach_purl_option

repos = APICommandGenerator.create_api_group("repos")

_ECOSYSTEM_PACKAGE_ERROR = "Either --purl or both ECOSYSTEM and PACKAGE arguments are required"

# These commands key off ecosystem name + package (path args), so the PURL type is
# passed through unmapped. The PURL or both positional args are required.
for _command in ("usage_package", "usage_package_dependencies", "usage_package_dependent_repositories"):
    attach_purl_option(
        repos,
        _command,
        targets=("ecosystem", "package"),
        map_types=False,
        error=_ECOSYSTEM_PACKAGE_ERROR,
        example="pkg:npm/lodash. Decomposes into ECOSYSTEM and PACKAGE.",
    )
