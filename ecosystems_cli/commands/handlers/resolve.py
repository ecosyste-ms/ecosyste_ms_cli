"""Handler for resolve API operations."""

from typing import Any, Dict, Tuple

from .base import OperationHandler


class ResolveOperationHandler(OperationHandler):
    """Handler for resolve API operations."""

    def build_params(self, operation_id: str, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Build parameters for resolve API operations.

        Args:
            operation_id: The operation identifier
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Tuple of (path_params, query_params)
        """
        handlers = {
            "createJob": self._handle_create_job,
            "getJob": self._handle_get_job,
            "listRegistries": self._handle_default,
        }

        handler = handlers.get(operation_id, self._handle_default)
        return handler(args, kwargs)

    def _handle_create_job(self, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Handle createJob operation parameters."""
        query_params = {}

        # Handle required parameters
        if len(args) >= 2:
            query_params["package_name"] = args[0]
            query_params["registry"] = args[1]
        else:
            if "package_name" in kwargs:
                query_params["package_name"] = kwargs["package_name"]
            if "registry" in kwargs:
                query_params["registry"] = kwargs["registry"]

        # Handle optional parameters
        if len(args) >= 3:
            query_params["version"] = args[2]
        elif "version" in kwargs:
            query_params["version"] = kwargs["version"]

        if "before" in kwargs:
            query_params["before"] = kwargs["before"]

        return {}, query_params

    def _handle_get_job(self, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Handle getJob operation parameters."""
        path_params = {}

        job_id = args[0] if args else kwargs.get("job_id")
        if job_id:
            path_params["jobID"] = job_id

        return path_params, {}

    def _handle_default(self, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Default handler for unknown operations."""
        return {}, {}
