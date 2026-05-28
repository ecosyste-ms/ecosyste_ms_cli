"""Shared submit-then-poll workflow for job-based API commands.

The diff, parser, licenses, and sbom APIs all expose the same ``createJob`` /
``getJob`` lifecycle: submit a job, then optionally poll until it reaches a
terminal status. ``submit_and_poll`` captures that single shared shape so each
command only supplies its API name and create payload.
"""

import time
from typing import Any, Dict, Optional

from rich.console import Console

from ecosystems_cli.constants import DEFAULT_OUTPUT_FORMAT, DEFAULT_TIMEOUT
from ecosystems_cli.exceptions import EcosystemsCLIError
from ecosystems_cli.helpers.get_domain import build_base_url, get_domain_with_precedence
from ecosystems_cli.helpers.print_error import print_error
from ecosystems_cli.helpers.print_output import print_output
from ecosystems_cli.openapi_client import _factory as api_factory

console = Console()

# Statuses that end a polling loop.
TERMINAL_STATUSES = ("completed", "complete", "success", "failed", "error")


def _extract_job_id(result: Dict[str, Any]) -> Optional[str]:
    """Return the job id from the create response, falling back to the trailing
    path segment of its ``location`` URL. Returns None when neither is present."""
    job_id = result.get("id")
    if job_id:
        return job_id

    location = result.get("location", "")
    if location:
        return location.rstrip("/").split("/")[-1] or None
    return None


def submit_and_poll(ctx, api_name: str, create_payload: dict, *, polling_interval: Optional[float]) -> None:
    """Submit a ``createJob`` request and, when polling is enabled, poll ``getJob``
    until the job reaches a terminal status.

    When ``polling_interval`` is None the create response is printed as-is. Otherwise
    the job id is resolved (response ``id`` or trailing segment of ``location``) and
    the job is polled every ``polling_interval`` seconds until its status is terminal.
    Progress messages are shown only in interactive (table) output mode.
    """
    from ecosystems_cli.commands.handlers import OperationHandlerFactory

    api_domain = get_domain_with_precedence(api_name, ctx.obj.get("domain"))
    base_url = build_base_url(api_domain, api_name)
    output_format = ctx.obj.get("format", DEFAULT_OUTPUT_FORMAT)

    try:
        handler = OperationHandlerFactory.get_handler(api_name)
        path_params, query_params = handler.build_params("createJob", (), create_payload)

        result = api_factory.call(
            api_name,
            "createJob",
            path_params=path_params,
            query_params=query_params,
            timeout=ctx.obj.get("timeout", DEFAULT_TIMEOUT),
            mailto=ctx.obj.get("mailto"),
            base_url=base_url,
        )

        if polling_interval is None:
            print_output(result, output_format, console=console)
            return

        job_id = _extract_job_id(result)
        if not job_id:
            print_error("No job ID in response, cannot poll for completion", console=console)
            print_output(result, output_format, console=console)
            return

        is_interactive = output_format == "table"
        if is_interactive:
            console.print(f"[yellow]Job created with ID: {job_id}[/yellow]")
            console.print(f"[yellow]Polling every {polling_interval} seconds...[/yellow]")

        while True:
            time.sleep(polling_interval)

            handler_get = OperationHandlerFactory.get_handler(api_name)
            path_params_get, query_params_get = handler_get.build_params("getJob", (), {"job_id": job_id})

            job_status = api_factory.call(
                api_name,
                "getJob",
                path_params=path_params_get,
                query_params=query_params_get,
                timeout=ctx.obj.get("timeout", DEFAULT_TIMEOUT),
                mailto=ctx.obj.get("mailto"),
                base_url=base_url,
            )

            status = job_status.get("status", "unknown")
            if is_interactive:
                console.print(f"[cyan]Job status: {status}[/cyan]")

            if status in TERMINAL_STATUSES:
                print_output(job_status, output_format, console=console)
                break

    except EcosystemsCLIError as e:
        print_error(str(e), console=console)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}", console=console)
