"""Commands for the packages API."""

from typing import Optional

import click

from ecosystems_cli.commands.decorators import common_options
from ecosystems_cli.commands.execution import execute_api_call, update_context
from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.helpers.purl_parser import parse_purl_with_version, purl_type_to_registry

packages = APICommandGenerator.create_api_group("packages")


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

    # If PURL is provided, parse it and override registry_name/package_name
    if purl:
        parsed_ecosystem, parsed_package_name, _ = parse_purl_with_version(purl)
        if parsed_ecosystem:
            # Convert purl type to registry name (e.g., 'npm' -> 'npmjs.org')
            registry_name = purl_type_to_registry(parsed_ecosystem)
        if parsed_package_name:
            package_name = parsed_package_name

    # Validate that we have the required parameters
    if not registry_name or not package_name:
        raise click.UsageError("Either --purl or both REGISTRY_NAME and PACKAGE_NAME arguments are required")

    # Build kwargs for the API call
    kwargs = {
        "registryName": registry_name,
        "packageName": package_name,
    }
    if page is not None:
        kwargs["page"] = page
    if per_page is not None:
        kwargs["per_page"] = per_page

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

    # If PURL is provided, parse it and override registry_name/package_name/version_number
    if purl:
        parsed_ecosystem, parsed_package_name, parsed_version = parse_purl_with_version(purl)
        if parsed_ecosystem:
            # Convert purl type to registry name (e.g., 'npm' -> 'npmjs.org')
            registry_name = purl_type_to_registry(parsed_ecosystem)
        if parsed_package_name:
            package_name = parsed_package_name
        if parsed_version:
            version_number = parsed_version

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
    }
    if page is not None:
        kwargs["page"] = page
    if per_page is not None:
        kwargs["per_page"] = per_page

    execute_api_call(ctx, "packages", operation_id="getRegistryPackageVersion", call_args=(), call_kwargs=kwargs)
