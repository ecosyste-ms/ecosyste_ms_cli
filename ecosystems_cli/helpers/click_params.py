"""Shared utilities for building Click parameter decorators from OpenAPI parameters."""

from typing import List, Tuple

import click


def build_body_decorators(request_body: dict) -> Tuple[List, List[str]]:
    """Build click option decorators for an operation's JSON request body.

    Auto-generated commands map path/query parameters from ``parameters``; this
    covers the other input channel -- a ``requestBody`` -- by turning each
    top-level property of its ``application/json`` schema into a ``--option``.
    Array properties become repeatable (``multiple=True``) options.

    Returns the decorators plus the list of body property names, so the caller
    can separate body fields from path/query kwargs when invoking the API
    (otherwise they would be misclassified as query parameters).

    Bodies described only by a ``$ref`` (no inline ``properties``) yield no
    options; such operations simply expose no body fields.
    """
    schema = request_body.get("content", {}).get("application/json", {}).get("schema", {})
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    decorators = []
    body_params = []
    for prop_name, prop_schema in properties.items():
        body_params.append(prop_name)
        option_name = prop_name.replace("_", "-")
        prop_type = prop_schema.get("type", "string")
        description = prop_schema.get("description", "")

        if prop_type == "array":
            decorators.append(click.option(f"--{option_name}", prop_name, multiple=True, help=description))
        else:
            click_type = None
            if prop_type == "integer":
                click_type = int
            elif prop_type == "boolean":
                click_type = bool
            decorators.append(
                click.option(
                    f"--{option_name}",
                    prop_name,
                    type=click_type,
                    help=description,
                    required=prop_name in required,
                )
            )

    return decorators, body_params


def build_click_decorators(parameters: List[dict]) -> List:
    """Build click decorators from OpenAPI parameters.

    This utility function converts OpenAPI parameter definitions into Click
    decorators for command-line arguments and options.

    Args:
        parameters: List of OpenAPI parameter definitions

    Returns:
        List of Click parameter decorators
    """
    click_decorators = []
    for param in parameters:
        param_name = param.get("name")
        param_in = param.get("in")
        param_description = param.get("description", "")
        param_required = param.get("required", False)
        param_schema = param.get("schema", {})
        param_type = param_schema.get("type", "string")

        python_param_name = param_name.replace("_", "-")

        if param_in == "path":
            click_decorators.append(click.argument(param_name))
        elif param_in == "query":
            click_type = None
            if param_type == "integer":
                # Pagination values are forwarded to the API verbatim, where
                # zero/negative values produce opaque 500s; validate them
                # client-side as positive integers.
                if param_name in ("page", "per_page"):
                    click_type = click.IntRange(min=1)
                else:
                    click_type = int
            elif param_type == "boolean":
                click_type = bool

            option_decorator = click.option(
                f"--{python_param_name}",
                param_name.replace("-", "_"),
                type=click_type,
                help=param_description,
                required=param_required,
            )
            click_decorators.append(option_decorator)

    return click_decorators
