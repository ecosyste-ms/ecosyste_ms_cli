"""Commands for the licenses API."""

from typing import Optional

import click

from ecosystems_cli.commands.decorators import common_options
from ecosystems_cli.commands.execution import update_context
from ecosystems_cli.commands.generator import APICommandGenerator
from ecosystems_cli.helpers.job_polling import submit_and_poll

licenses = APICommandGenerator.create_api_group("licenses")


# Remove auto-generated create_job command to replace with custom implementation
if "create_job" in licenses.commands:
    del licenses.commands["create_job"]


@licenses.command(name="create_job", help="Submit a dependency parsing job")
@click.argument("url", required=True)
@click.option(
    "--polling-interval",
    type=float,
    default=None,
    help="Polling interval in seconds. If set, the command will poll the job status until completion.",
)
@common_options
@click.pass_context
def create_job(
    ctx, timeout: int, format: str, domain: Optional[str], mailto: Optional[str], url: str, polling_interval: Optional[float]
):
    """Submit a dependency parsing job.

    Args:
        ctx: Click context
        timeout: Request timeout
        format: Output format
        domain: API domain
        mailto: Email for polite pool access
        url: URL of file or zip/tar archive
        polling_interval: Optional polling interval in seconds
    """
    update_context(ctx, timeout, format, domain, mailto)
    submit_and_poll(ctx, "licenses", {"url": url}, polling_interval=polling_interval)
