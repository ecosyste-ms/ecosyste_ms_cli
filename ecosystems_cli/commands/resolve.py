"""Commands for the resolve API."""

from typing import Optional

import click

from ecosystems_cli.commands.decorators import common_options, override_auto_command
from ecosystems_cli.commands.execution import update_context
from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.constants import DEFAULT_MAX_POLL_WAIT
from ecosystems_cli.helpers.build_kwargs import build_kwargs
from ecosystems_cli.helpers.job_polling import submit_and_poll

resolve = APICommandGenerator.create_api_group("resolve")


@override_auto_command(resolve, "create_job", help="Submit a resolve job")
@click.argument("package_name", required=True)
@click.argument("registry", required=False)
@click.option("--ecosystem", default=None, help="Ecosystem/purl type (e.g. gem, npm, cargo). Alternative to REGISTRY.")
@click.option("--version", default=None, help="Resolve only with version within this range")
@click.option("--tree", is_flag=True, default=False, help="Return the full dependency tree with PURLs instead of a flat map")
@click.option(
    "--polling-interval",
    type=float,
    default=None,
    help="Polling interval in seconds. If set, the command will poll the job status until completion.",
)
@click.option(
    "--max-wait",
    type=float,
    default=DEFAULT_MAX_POLL_WAIT,
    help=f"Maximum seconds to poll before giving up. Default is {DEFAULT_MAX_POLL_WAIT}.",
)
@common_options
@click.pass_context
def create_job(
    ctx,
    timeout: int,
    format: str,
    domain: Optional[str],
    mailto: Optional[str],
    package_name: str,
    registry: Optional[str],
    ecosystem: Optional[str],
    version: Optional[str],
    tree: bool,
    polling_interval: Optional[float],
    max_wait: float,
):
    """Submit a resolve job.

    Args:
        ctx: Click context
        timeout: Request timeout
        format: Output format
        domain: API domain
        mailto: Email for polite pool access
        package_name: Name of the package
        registry: Name of the package registry (either registry or ecosystem is required)
        ecosystem: Ecosystem/purl type, alternative to registry
        version: Optional version range
        tree: Return the full dependency tree with PURLs instead of a flat map
        polling_interval: Optional polling interval in seconds
        max_wait: Maximum seconds to poll before giving up
    """
    update_context(ctx, timeout, format, domain, mailto)

    # The API accepts either a registry or an ecosystem/purl type; require one.
    if not registry and not ecosystem:
        raise click.UsageError("Either REGISTRY argument or --ecosystem is required.")

    payload = {
        "package_name": package_name,
        **build_kwargs(
            registry=registry,
            ecosystem=ecosystem,
            version=version,
            tree="true" if tree else None,
        ),
    }
    submit_and_poll(ctx, "resolve", payload, polling_interval=polling_interval, max_wait=max_wait)
