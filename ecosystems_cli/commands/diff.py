"""Commands for the diff API."""

from typing import Optional

import click

from ecosystems_cli.commands.decorators import common_options, override_auto_command
from ecosystems_cli.commands.execution import update_context
from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.constants import DEFAULT_MAX_POLL_WAIT
from ecosystems_cli.helpers.job_polling import submit_and_poll

diff = APICommandGenerator.create_api_group("diff")


@override_auto_command(diff, "create_job", help="Submit a diff job with two URLs to compare")
@click.argument("url_1", required=True)
@click.argument("url_2", required=True)
@click.option(
    "--polling-interval",
    type=click.FloatRange(min=0.1),
    default=None,
    help="Polling interval in seconds. If set, the command will poll the job status until completion.",
)
@click.option(
    "--max-wait",
    type=click.FloatRange(min=0, min_open=True),
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
    url_1: str,
    url_2: str,
    polling_interval: Optional[float],
    max_wait: float,
):
    """Submit a diff job with two URLs to compare.

    Args:
        ctx: Click context
        timeout: Request timeout
        format: Output format
        domain: API domain
        mailto: Email for polite pool access
        url_1: First URL of file or zip/tar archive
        url_2: Second URL of file or zip/tar archive
        polling_interval: Optional polling interval in seconds
        max_wait: Maximum seconds to poll before giving up
    """
    update_context(ctx, timeout, format, domain, mailto)
    submit_and_poll(ctx, "diff", {"url_1": url_1, "url_2": url_2}, polling_interval=polling_interval, max_wait=max_wait)
