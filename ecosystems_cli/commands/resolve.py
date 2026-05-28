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
@click.argument("registry", required=True)
@click.option("--version", default=None, help="Resolve only with version within this range")
@click.option("--before", default=None, help="Resolve only with dependencies before this date")
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
    registry: str,
    version: Optional[str],
    before: Optional[str],
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
        registry: Name of the package registry
        version: Optional version range
        before: Optional date to resolve dependencies before
        polling_interval: Optional polling interval in seconds
        max_wait: Maximum seconds to poll before giving up
    """
    update_context(ctx, timeout, format, domain, mailto)
    payload = {"package_name": package_name, "registry": registry, **build_kwargs(version=version, before=before)}
    submit_and_poll(ctx, "resolve", payload, polling_interval=polling_interval, max_wait=max_wait)
