"""Generic command generator for ecosystems CLI APIs."""

import re
from typing import List

import click

from ecosystems_cli.commands.decorators import common_options
from ecosystems_cli.helpers.click_params import build_body_decorators, build_click_decorators
from ecosystems_cli.helpers.load_api_spec import load_api_spec

# Help-text overrides for auto-generated commands, keyed by
# (api_name, operation_id). The OpenAPI specs are vendored verbatim from
# upstream (and checksummed), so spec typos and missing summaries are
# corrected here instead of editing the spec files.
HELP_OVERRIDES = {
    ("advisories", "getAdvisory"): "get an advisory by uuid",
    ("commits", "getRegistries"): "list registries",
    ("dependabot", "getRegistries"): "list registries",
    ("issues", "getRegistries"): "list registries",
    ("packages", "getRegistries"): "list registries",
    ("repos", "getRegistries"): "list registries",
    # The opencollective spec has no summary fields at all, so these commands
    # would otherwise fall back to "Execute <operationId>" placeholders.
    ("opencollective", "getCollectives"): "list open collective collectives",
    ("opencollective", "getCollective"): "get a collective by id",
    ("opencollective", "getCollectiveProjects"): "list projects of a collective",
    ("opencollective", "getProjects"): "list open source projects with collectives",
    ("opencollective", "getProject"): "get a project by id",
    ("opencollective", "getProjectPackages"): "list packages of a project",
    ("opencollective", "lookupProject"): "lookup a project by repository or package URL",
}


class APICommandGenerator:
    """Generate CLI commands from OpenAPI specifications."""

    @staticmethod
    def operation_id_to_command_name(operation_id: str) -> str:
        """Convert operationId to command name.

        Examples:
        - getTopics -> get_topics
        - getTopic -> get_topic
        - repositoriesLookup -> repositories_lookup
        """
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", operation_id)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def _build_click_decorators(parameters: List[dict]) -> List:
        """Build click decorators from OpenAPI parameters."""
        return build_click_decorators(parameters)

    @staticmethod
    def _create_group_command(api_name: str) -> click.Group:
        """Create the main group command for an API."""

        @click.group(help=f"Commands for the {api_name} API.")
        @common_options
        @click.pass_context
        def api_group(ctx, timeout, format, domain, mailto):
            f"""Commands for the {api_name} API."""
            from ecosystems_cli.commands.execution import update_context

            # Same merge rule as leaf commands: a value set at this level wins;
            # otherwise the value inherited from the parent context is kept.
            update_context(ctx, timeout, format, domain, mailto)

        api_group.name = api_name
        return api_group

    @staticmethod
    def _register_commands(api_group: click.Group, api_name: str):
        """Register all commands for an API dynamically from OpenAPI spec."""
        spec = load_api_spec(api_name)

        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    operation_id = operation.get("operationId")
                    if not operation_id:
                        continue

                    command_name = APICommandGenerator.operation_id_to_command_name(operation_id)
                    description = HELP_OVERRIDES.get((api_name, operation_id)) or operation.get(
                        "summary", f"Execute {operation_id}"
                    )
                    parameters = operation.get("parameters", [])
                    request_body = operation.get("requestBody")

                    if not parameters and not request_body:
                        APICommandGenerator._create_simple_command(api_group, command_name, description, api_name, operation_id)
                    else:
                        APICommandGenerator._create_parameterized_command(
                            api_group, command_name, description, api_name, operation_id, parameters, request_body
                        )

    @staticmethod
    def _create_simple_command(api_group: click.Group, command_name: str, description: str, api_name: str, operation_id: str):
        """Create a command without parameters."""
        from ecosystems_cli.commands.decorators import api_command

        @api_group.command(name=command_name, help=description)
        @api_command(api_name, operation_id=operation_id)
        def command_impl():
            pass

    @staticmethod
    def _create_parameterized_command(
        api_group: click.Group,
        command_name: str,
        description: str,
        api_name: str,
        operation_id: str,
        parameters: List[dict],
        request_body: dict = None,
    ):
        """Create a command with parameters and/or a JSON request body."""
        click_decorators = APICommandGenerator._build_click_decorators(parameters)
        body_params: List[str] = []
        if request_body:
            body_decorators, body_params = build_body_decorators(request_body)
            click_decorators = click_decorators + body_decorators

        def make_command(op_id, body_keys):
            @api_group.command(name=command_name, help=description)
            @common_options
            @click.pass_context
            def command_impl(ctx, timeout, format, domain, mailto, *args, **kwargs):
                from ecosystems_cli.commands.execution import execute_api_call, update_context

                update_context(ctx, timeout, format, domain, mailto)
                execute_api_call(ctx, api_name, operation_id=op_id, call_args=args, call_kwargs=kwargs, body_keys=body_keys)

            # command_impl is already a click.Command here, so each decorator
            # APPENDS its parameter to command.params in application order.
            # Iterating forward therefore preserves the OpenAPI spec order —
            # positional arguments must match the URL path order
            # (/hosts/{host}/... => HOSTNAME first). reversed() here produced
            # REPOSITORYNAME HOSTNAME usage, inverted from the API path.
            for decorator in click_decorators:
                command_impl = decorator(command_impl)

            return command_impl

        make_command(operation_id, body_params)

    @staticmethod
    def create_api_group(api_name: str) -> click.Group:
        """Create a complete API command group from OpenAPI spec.

        Args:
            api_name: Name of the API (e.g., 'repos', 'packages')

        Returns:
            Configured Click group with all commands registered
        """
        api_group = APICommandGenerator._create_group_command(api_name)
        APICommandGenerator._register_commands(api_group, api_name)
        return api_group
