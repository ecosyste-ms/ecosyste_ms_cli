"""Base class for operation handlers."""

from abc import ABC
from typing import Any, Dict, List, Optional, Tuple


class OperationHandler(ABC):
    """Base class for operation handlers.

    Subclasses describe each operation's path parameters via ``OPERATION_PARAMS``
    and inherit :meth:`build_params`. The default mapping is: parameters listed in
    ``OPERATION_PARAMS`` become path parameters (matched positionally or by name);
    every remaining non-None keyword argument becomes a query parameter.

    ``OPERATION_PARAMS`` maps ``operation_id`` to an ordered list of
    ``(api_param_name, [lowercase_variants])`` tuples. ``api_param_name`` is the
    exact name used in the URL path template; the variants cover the lowercased
    form Click produces from ``click.argument`` and any underscore form passed by
    programmatic callers.
    """

    OPERATION_PARAMS: Dict[str, List[Tuple[str, List[str]]]] = {}

    def _extract_param(self, kwargs: dict, api_name: str, lowercase_variants: List[str]) -> Optional[str]:
        """Extract parameter from kwargs, trying API name first, then lowercase variants.

        Args:
            kwargs: Keyword arguments dict
            api_name: The API parameter name (exact case)
            lowercase_variants: List of lowercase parameter name variants to try

        Returns:
            Parameter value if found, None otherwise
        """
        # Try exact API name first
        if api_name in kwargs:
            return kwargs.pop(api_name)

        # Try lowercase variants
        for variant in lowercase_variants:
            if variant in kwargs:
                return kwargs.pop(variant)

        return None

    def build_params(self, operation_id: str, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Build path and query parameters for an operation.

        Path parameters come from ``OPERATION_PARAMS`` (matched against positional
        args first, then keyword args); all remaining non-None kwargs become query
        parameters.

        Args:
            operation_id: The operation ID to handle
            args: Positional arguments passed to the command
            kwargs: Keyword arguments passed to the command

        Returns:
            Tuple of (path_params, query_params)
        """
        path_params: Dict[str, Any] = {}
        query_params: Dict[str, Any] = {}

        for i, (api_name, lowercase_variants) in enumerate(self.OPERATION_PARAMS.get(operation_id, [])):
            if i < len(args):
                path_params[api_name] = args[i]
            else:
                value = self._extract_param(kwargs, api_name, lowercase_variants)
                if value is not None:
                    path_params[api_name] = value

        for key, value in kwargs.items():
            if value is not None:
                query_params[key] = value

        return path_params, query_params

    def build_click_params(self, operation: dict) -> List:
        """Build Click parameter decorators from OpenAPI operation.

        Default implementation that can be overridden by specific handlers.

        Args:
            operation: OpenAPI operation definition

        Returns:
            List of Click parameter decorators
        """
        from ecosystems_cli.helpers.click_params import build_click_decorators

        parameters = operation.get("parameters", [])
        return build_click_decorators(parameters)
