"""Commands for the advisories API."""

from typing import Optional

import click

from ecosystems_cli.commands.decorators import common_options
from ecosystems_cli.commands.execution import execute_api_call, update_context
from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.helpers.purl_parser import parse_purl

advisories = APICommandGenerator.create_api_group("advisories")


# Remove auto-generated get_advisories command to replace with custom implementation
if "get_advisories" in advisories.commands:
    del advisories.commands["get_advisories"]


@advisories.command(name="get_advisories", help="list advisories")
@click.option("--purl", type=str, default=None, help="Package URL (PURL). Example: pkg:npm/fsa")
@click.option("--ecosystem", type=str, default=None, help="Ecosystem to filter by")
@click.option("--package-name", type=str, default=None, help="Package to filter by")
@click.option("--severity", type=str, default=None, help="Severity to filter by")
@click.option("--repository-url", type=str, default=None, help="Repository URL to filter by")
@click.option("--page", type=int, default=None, help="pagination page number")
@click.option("--per-page", type=int, default=None, help="Number of records to return")
@click.option("--created-after", type=str, default=None, help="filter by created_at after given time")
@click.option("--updated-after", type=str, default=None, help="filter by updated_at after given time")
@click.option("--sort", type=str, default=None, help="field to order results by")
@click.option("--order", type=str, default=None, help="direction to order results by")
@click.option("--source", type=str, default=None, help="Source to filter by (e.g. github, erlef)")
@common_options
@click.pass_context
def get_advisories(
    ctx,
    timeout: int,
    format: str,
    domain: Optional[str],
    mailto: Optional[str],
    purl: Optional[str],
    ecosystem: Optional[str],
    package_name: Optional[str],
    severity: Optional[str],
    repository_url: Optional[str],
    page: Optional[int],
    per_page: Optional[int],
    created_after: Optional[str],
    updated_after: Optional[str],
    sort: Optional[str],
    order: Optional[str],
    source: Optional[str] = None,
):
    """List advisories with optional PURL support.

    Args:
        ctx: Click context
        timeout: Request timeout
        format: Output format
        domain: API domain
        mailto: Email for polite pool access
        purl: Package URL (alternative to ecosystem + package_name)
        ecosystem: Ecosystem to filter by
        package_name: Package name to filter by
        severity: Severity to filter by
        repository_url: Repository URL to filter by
        page: Pagination page number
        per_page: Number of records to return
        created_after: Filter by created_at after given time
        updated_after: Filter by updated_at after given time
        sort: Field to order results by
        order: Direction to order results by
    """
    update_context(ctx, timeout, format, domain, mailto)

    # If PURL is provided, parse it and override ecosystem/package_name
    if purl:
        parsed_ecosystem, parsed_package_name = parse_purl(purl)
        if parsed_ecosystem:
            ecosystem = parsed_ecosystem
        if parsed_package_name:
            package_name = parsed_package_name

    # Build kwargs for the API call
    kwargs = {}
    if ecosystem is not None:
        kwargs["ecosystem"] = ecosystem
    if package_name is not None:
        kwargs["package_name"] = package_name
    if severity is not None:
        kwargs["severity"] = severity
    if repository_url is not None:
        kwargs["repository_url"] = repository_url
    if page is not None:
        kwargs["page"] = page
    if per_page is not None:
        kwargs["per_page"] = per_page
    if created_after is not None:
        kwargs["created_after"] = created_after
    if updated_after is not None:
        kwargs["updated_after"] = updated_after
    if sort is not None:
        kwargs["sort"] = sort
    if order is not None:
        kwargs["order"] = order
    if source is not None:
        kwargs["source"] = source

    execute_api_call(ctx, "advisories", operation_id="getAdvisories", call_args=(), call_kwargs=kwargs)
