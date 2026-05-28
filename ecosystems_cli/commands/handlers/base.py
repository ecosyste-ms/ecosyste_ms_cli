"""Base class for operation handlers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class OperationHandler(ABC):
    """Base class for operation handlers."""

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

    @abstractmethod
    def build_params(self, operation_id: str, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Build path and query parameters for an operation.

        Args:
            operation_id: The operation ID to handle
            args: Positional arguments passed to the command
            kwargs: Keyword arguments passed to the command

        Returns:
            Tuple of (path_params, query_params)
        """
        pass

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
