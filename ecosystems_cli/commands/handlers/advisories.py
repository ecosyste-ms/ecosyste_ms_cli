"""Handler for advisories API operations."""

from typing import Any, Dict, Tuple

from .base import OperationHandler


class AdvisoriesOperationHandler(OperationHandler):
    """Handler for advisories API operations."""

    # CLI parameter names
    CLI_PARAM_ADVISORY_UUID = "advisoryuuid"
    # OpenAPI parameter names
    API_PARAM_ADVISORY_UUID = "advisoryUUID"

    def build_params(self, operation_id: str, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Build parameters for advisories API operations.

        Args:
            operation_id: The operation identifier
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Tuple of (path_params, query_params)
        """
        handlers = {
            "getAdvisory": self._handle_get_advisory,
            "getAdvisories": self._handle_query_params,
            "getAdvisoriesPackages": self._handle_no_params,
            "lookupAdvisoriesByPurl": self._handle_query_params,
            "getSources": self._handle_no_params,
            "getSource": self._handle_get_source,
        }

        handler = handlers.get(operation_id, self._handle_default)
        return handler(args, kwargs)

    def _handle_get_advisory(self, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Handle getAdvisory operation parameters."""
        path_params = {}

        advisory_uuid = args[0] if args else kwargs.pop(self.CLI_PARAM_ADVISORY_UUID, None)
        if advisory_uuid:
            path_params[self.API_PARAM_ADVISORY_UUID] = advisory_uuid

        return path_params, {}

    def _handle_query_params(self, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Handle operations that only have query parameters."""
        _ = args  # Unused but required for consistent interface
        query_params = {key: value for key, value in kwargs.items() if value is not None}
        return {}, query_params

    def _handle_no_params(self, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Handle operations with no parameters."""
        _ = args, kwargs  # Unused but required for consistent interface
        return {}, {}

    def _handle_get_source(self, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Handle getSource operation parameters."""
        path_params = {}

        source_kind = args[0] if args else kwargs.pop("sourcekind", None)
        if source_kind:
            path_params["sourceKind"] = source_kind

        return path_params, {}

    def _handle_default(self, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Default handler for unknown operations."""
        _ = args, kwargs  # Unused but required for consistent interface
        return {}, {}
