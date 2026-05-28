"""Commands for the packages API.

Several auto-generated commands accept a ``--purl`` shortcut that decomposes a
Package URL into the registry/package/version parameters the command already
takes. The shared :func:`attach_purl_option` helper wires that up.
"""

from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.commands.purl_options import attach_purl_option

packages = APICommandGenerator.create_api_group("packages")

_REGISTRY_PACKAGE_ERROR = "Either --purl or both REGISTRY_NAME and PACKAGE_NAME arguments are required"
_REGISTRY_VERSION_ERROR = (
    "Either --purl (with version) or all three arguments (REGISTRY_NAME, PACKAGE_NAME, VERSION_NUMBER) are required"
)

# getDependencies filters by ecosystem name ("npm"), not registry name ("npmjs.org"),
# so the PURL type is passed through unmapped and both parts stay optional filters.
attach_purl_option(
    packages,
    "get_dependencies",
    targets=("ecosystem", "package_name"),
    map_types=False,
    example="pkg:npm/axios@1.7.9. Decomposes into --ecosystem and --package-name.",
)

# Commands keyed by registry name + package name (PURL type mapped to a registry).
for _command in (
    "get_registry_package",
    "get_registry_package_dependent_packages",
    "get_registry_package_versions",
    "get_registry_package_version_numbers",
):
    attach_purl_option(
        packages,
        _command,
        targets=("registryname", "packagename"),
        error=_REGISTRY_PACKAGE_ERROR,
        example="pkg:npm/lodash. Decomposes into REGISTRY_NAME and PACKAGE_NAME.",
    )

# Adds a version segment on top of registry + package.
attach_purl_option(
    packages,
    "get_registry_package_version",
    targets=("registryname", "packagename", "versionnumber"),
    with_version=True,
    error=_REGISTRY_VERSION_ERROR,
    example="pkg:npm/lodash@4.17.21. Decomposes into REGISTRY_NAME, PACKAGE_NAME and VERSION_NUMBER.",
)
