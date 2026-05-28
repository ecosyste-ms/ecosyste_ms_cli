"""Commands for the packages API."""

from typing import Optional

import click

from ecosystems_cli.commands.decorators import common_options
from ecosystems_cli.commands.execution import execute_api_call, update_context
from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.helpers.build_kwargs import build_kwargs
from ecosystems_cli.helpers.purl_parser import apply_purl, purl_type_to_registry

packages = APICommandGenerator.create_api_group("packages")


# Attach --purl as an optional parameter to the auto-generated get_dependencies
# command. When provided, its type/name decompose into --ecosystem/--package-name,
# letting users pass a single PURL instead of multiple flags.
if "get_dependencies" in packages.commands:
    _get_dependencies_cmd = packages.commands["get_dependencies"]
    _get_dependencies_cmd.params.insert(
        0,
        click.Option(
            ["--purl"],
            type=str,
            default=None,
            help="Package URL (PURL). Example: pkg:npm/axios@1.7.9. Decomposes into --ecosystem and --package-name.",
        ),
    )
    _original_get_dependencies_callback = _get_dependencies_cmd.callback

    def _get_dependencies_with_purl(*args, **kwargs):
        # getDependencies filters by ecosystem name (e.g. "npm"), not the registry
        # name ("npmjs.org"), so the PURL type is passed through unmapped.
        parsed = apply_purl(kwargs.pop("purl", None))
        for key in ("ecosystem", "package_name"):
            if parsed.get(key) and not kwargs.get(key):
                kwargs[key] = parsed[key]
        return _original_get_dependencies_callback(*args, **kwargs)

    _get_dependencies_cmd.callback = _get_dependencies_with_purl


def _add_purl_to_registry_package_command(command_name: str) -> None:
    """Attach --purl to a command whose path args are registryName + packageName.

    Makes the positional REGISTRY_NAME and PACKAGE_NAME args optional, injects
    --purl, and wraps the callback so a PURL decomposes into those two args.
    Purl type is mapped to a registry name (e.g. 'npm' -> 'npmjs.org').
    Positional args still win over a PURL when both are passed.
    """
    if command_name not in packages.commands:
        return

    cmd = packages.commands[command_name]

    for param in cmd.params:
        if isinstance(param, click.Argument) and param.name in ("registryname", "packagename"):
            param.required = False

    cmd.params.insert(
        0,
        click.Option(
            ["--purl"],
            type=str,
            default=None,
            help="Package URL (PURL). Example: pkg:npm/lodash. Decomposes into REGISTRY_NAME and PACKAGE_NAME.",
        ),
    )
    original_callback = cmd.callback

    def wrapped_callback(*args, **kwargs):
        parsed = apply_purl(kwargs.pop("purl", None), type_mapper=purl_type_to_registry)
        kwargs["registryname"] = kwargs.get("registryname") or parsed.get("ecosystem")
        kwargs["packagename"] = kwargs.get("packagename") or parsed.get("package_name")
        if not kwargs.get("registryname") or not kwargs.get("packagename"):
            raise click.UsageError("Either --purl or both REGISTRY_NAME and PACKAGE_NAME arguments are required")
        return original_callback(*args, **kwargs)

    cmd.callback = wrapped_callback


for _op in (
    "get_registry_package_dependent_packages",
    "get_registry_package_versions",
    "get_registry_package_version_numbers",
):
    _add_purl_to_registry_package_command(_op)


# Remove auto-generated commands to replace with custom implementations
if "get_registry_package" in packages.commands:
    del packages.commands["get_registry_package"]
if "get_registry_package_version" in packages.commands:
    del packages.commands["get_registry_package_version"]


@packages.command(name="get_registry_package", help="get a package by name")
@click.option("--purl", type=str, default=None, help="Package URL (PURL). Example: pkg:npm/lodash")
@click.argument("registry_name", required=False, default=None)
@click.argument("package_name", required=False, default=None)
@click.option("--page", type=int, default=None, help="pagination page number")
@click.option("--per-page", type=int, default=None, help="Number of records to return")
@common_options
@click.pass_context
def get_registry_package(
    ctx,
    timeout: int,
    format: str,
    domain: Optional[str],
    mailto: Optional[str],
    purl: Optional[str],
    registry_name: Optional[str],
    package_name: Optional[str],
    page: Optional[int],
    per_page: Optional[int],
):
    """Get a package by name with optional PURL support.

    Args:
        ctx: Click context
        timeout: Request timeout
        format: Output format
        domain: API domain
        mailto: Email for polite pool access
        purl: Package URL (alternative to registry_name + package_name)
        registry_name: Name of the registry (e.g., npm, pypi)
        package_name: Name of the package
        page: Pagination page number
        per_page: Number of records to return
    """
    update_context(ctx, timeout, format, domain, mailto)

    # Explicit positional args win over PURL-derived values.
    parsed = apply_purl(purl, type_mapper=purl_type_to_registry)
    registry_name = registry_name or parsed.get("ecosystem")
    package_name = package_name or parsed.get("package_name")

    # Validate that we have the required parameters
    if not registry_name or not package_name:
        raise click.UsageError("Either --purl or both REGISTRY_NAME and PACKAGE_NAME arguments are required")

    # Build kwargs for the API call
    kwargs = {
        "registryName": registry_name,
        "packageName": package_name,
        **build_kwargs(page=page, per_page=per_page),
    }

    execute_api_call(ctx, "packages", operation_id="getRegistryPackage", call_args=(), call_kwargs=kwargs)


@packages.command(name="get_registry_package_version", help="get a version of a package")
@click.option("--purl", type=str, default=None, help="Package URL (PURL). Example: pkg:npm/lodash@4.17.21")
@click.argument("registry_name", required=False, default=None)
@click.argument("package_name", required=False, default=None)
@click.argument("version_number", required=False, default=None)
@click.option("--page", type=int, default=None, help="pagination page number")
@click.option("--per-page", type=int, default=None, help="Number of records to return")
@common_options
@click.pass_context
def get_registry_package_version(
    ctx,
    timeout: int,
    format: str,
    domain: Optional[str],
    mailto: Optional[str],
    purl: Optional[str],
    registry_name: Optional[str],
    package_name: Optional[str],
    version_number: Optional[str],
    page: Optional[int],
    per_page: Optional[int],
):
    """Get a version of a package with optional PURL support.

    Args:
        ctx: Click context
        timeout: Request timeout
        format: Output format
        domain: API domain
        mailto: Email for polite pool access
        purl: Package URL (alternative to registry_name + package_name + version_number)
        registry_name: Name of the registry (e.g., npm, pypi)
        package_name: Name of the package
        version_number: Version number of the package
        page: Pagination page number
        per_page: Number of records to return
    """
    update_context(ctx, timeout, format, domain, mailto)

    # Explicit positional args win over PURL-derived values.
    parsed = apply_purl(purl, with_version=True, type_mapper=purl_type_to_registry)
    registry_name = registry_name or parsed.get("ecosystem")
    package_name = package_name or parsed.get("package_name")
    version_number = version_number or parsed.get("version")

    # Validate that we have the required parameters
    if not registry_name or not package_name or not version_number:
        raise click.UsageError(
            "Either --purl (with version) or all three arguments (REGISTRY_NAME, PACKAGE_NAME, VERSION_NUMBER) are required"
        )

    # Build kwargs for the API call
    kwargs = {
        "registryName": registry_name,
        "packageName": package_name,
        "versionNumber": version_number,
        **build_kwargs(page=page, per_page=per_page),
    }

    execute_api_call(ctx, "packages", operation_id="getRegistryPackageVersion", call_args=(), call_kwargs=kwargs)
