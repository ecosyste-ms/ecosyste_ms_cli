"""Commands for the packages API.

Several auto-generated commands accept a ``--purl`` shortcut that decomposes a
Package URL into the registry/package/version parameters the command already
takes. ``_attach_purl_option`` is the single mechanism for wiring that up: it
makes the relevant positional arguments optional, injects ``--purl``, and wraps
the command's callback so the PURL fills in any parameter the user didn't pass
explicitly (explicit values always win).
"""

from typing import Optional, Sequence

import click

from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.helpers.purl_parser import apply_purl, purl_type_to_registry

packages = APICommandGenerator.create_api_group("packages")

# The PURL components, in the order they map onto a command's target parameters.
_PURL_COMPONENTS = ("ecosystem", "package_name", "version")


def _attach_purl_option(
    command_name: str,
    *,
    targets: Sequence[str],
    with_version: bool = False,
    map_types: bool = True,
    error: Optional[str] = None,
    example: str,
) -> None:
    """Attach an optional ``--purl`` to an auto-generated command.

    Args:
        command_name: Name of the auto-generated command to augment.
        targets: Command parameter names that the PURL decomposes into, paired
            positionally with ``_PURL_COMPONENTS`` (ecosystem, package_name,
            version). Any positional arguments among them are made optional.
        with_version: Whether to also extract the version from the PURL.
        map_types: Map the PURL type to a registry name (e.g. ``npm`` ->
            ``npmjs.org``). Disable when the command filters by ecosystem name.
        error: Message raised as a ``UsageError`` when a target is still unset
            after decomposition. When ``None`` the PURL is an optional shortcut.
        example: Example PURL shown in the option help text.
    """
    if command_name not in packages.commands:
        return

    cmd = packages.commands[command_name]

    # Let --purl stand in for the positional arguments it decomposes into.
    for param in cmd.params:
        if isinstance(param, click.Argument) and param.name in targets:
            param.required = False

    # Normalize positional order to `targets` (e.g. REGISTRY_NAME before
    # PACKAGE_NAME) so every PURL-enabled command shares one contract that
    # matches the help text, regardless of the auto-generated argument order.
    arg_slots = [i for i, p in enumerate(cmd.params) if isinstance(p, click.Argument) and p.name in targets]
    ordered_args = sorted((cmd.params[i] for i in arg_slots), key=lambda p: list(targets).index(p.name))
    for slot, arg in zip(arg_slots, ordered_args):
        cmd.params[slot] = arg

    cmd.params.insert(
        0,
        click.Option(["--purl"], type=str, default=None, help=f"Package URL (PURL). Example: {example}"),
    )

    original_callback = cmd.callback
    type_mapper = purl_type_to_registry if map_types else (lambda purl_type: purl_type)

    def wrapped_callback(*args, **kwargs):
        parsed = apply_purl(kwargs.pop("purl", None), with_version=with_version, type_mapper=type_mapper)
        for component, target in zip(_PURL_COMPONENTS, targets):
            if not kwargs.get(target):
                kwargs[target] = parsed.get(component)
        if error and any(not kwargs.get(target) for target in targets):
            raise click.UsageError(error)
        return original_callback(*args, **kwargs)

    cmd.callback = wrapped_callback


_REGISTRY_PACKAGE_ERROR = "Either --purl or both REGISTRY_NAME and PACKAGE_NAME arguments are required"
_REGISTRY_VERSION_ERROR = (
    "Either --purl (with version) or all three arguments (REGISTRY_NAME, PACKAGE_NAME, VERSION_NUMBER) are required"
)

# getDependencies filters by ecosystem name ("npm"), not registry name ("npmjs.org"),
# so the PURL type is passed through unmapped and both parts stay optional filters.
_attach_purl_option(
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
    _attach_purl_option(
        _command,
        targets=("registryname", "packagename"),
        error=_REGISTRY_PACKAGE_ERROR,
        example="pkg:npm/lodash. Decomposes into REGISTRY_NAME and PACKAGE_NAME.",
    )

# Adds a version segment on top of registry + package.
_attach_purl_option(
    "get_registry_package_version",
    targets=("registryname", "packagename", "versionnumber"),
    with_version=True,
    error=_REGISTRY_VERSION_ERROR,
    example="pkg:npm/lodash@4.17.21. Decomposes into REGISTRY_NAME, PACKAGE_NAME and VERSION_NUMBER.",
)
