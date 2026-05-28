"""Generic command generator for ecosystems CLI APIs."""

import re
from typing import List

import click

from ecosystems_cli.commands.decorators import common_options
from ecosystems_cli.helpers.click_params import build_body_decorators, build_click_decorators
from ecosystems_cli.helpers.load_api_spec import load_api_spec


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
                    description = operation.get("summary", f"Execute {operation_id}")
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

            for decorator in reversed(click_decorators):
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
