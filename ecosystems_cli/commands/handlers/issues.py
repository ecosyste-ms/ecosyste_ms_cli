"""Handler for issues API operations."""

from typing import Any, Dict, Tuple

from .base import OperationHandler


class IssuesOperationHandler(OperationHandler):
    """Handler for issues API operations."""

    # Operation parameter configuration
    # Maps operation_id -> list of (api_param_name, lowercase_variants)
    OPERATION_PARAMS = {
        "getHost": [("hostName", ["hostname"])],
        "getHostRepositories": [("hostName", ["hostname"])],
        "getHostRepository": [("hostName", ["hostname"]), ("repoName", ["reponame"])],
        "getHostRepositoryIssues": [("hostName", ["hostname"]), ("repoName", ["reponame"])],
        "getHostRepositoryIssue": [
            ("hostName", ["hostname"]),
            ("repoName", ["reponame"]),
            ("issueNumber", ["issuenumber", "issue_number"]),
        ],
        "getHostRepositoryLabels": [("hostName", ["hostname"]), ("repoName", ["reponame"])],
        "getHostOwners": [("hostName", ["hostname"])],
        "getHostOwner": [("hostName", ["hostname"]), ("ownerName", ["ownername"])],
        "getHostOwnerMaintainers": [("hostName", ["hostname"]), ("ownerName", ["ownername"])],
        "getHostAuthors": [("hostName", ["hostname"])],
        "getHostAuthor": [("hostName", ["hostname"]), ("authorName", ["authorname"])],
        "getJob": [("jobId", ["jobid"])],
    }

    def build_params(self, operation_id: str, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Build parameters for issues API operations.

        Args:
            operation_id: The operation identifier
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Tuple of (path_params, query_params)
        """
        path_params = {}
        query_params = {}

        # Get parameter configuration for this operation
        param_config = self.OPERATION_PARAMS.get(operation_id, [])

        # Extract path parameters from args or kwargs
        for i, (api_name, lowercase_variants) in enumerate(param_config):
            if i < len(args):
                # Use positional argument
                path_params[api_name] = args[i]
            else:
                # Try to extract from kwargs
                value = self._extract_param(kwargs, api_name, lowercase_variants)
                if value is not None:
                    path_params[api_name] = value

        # For all operations, remaining kwargs are query parameters
        for key, value in kwargs.items():
            if value is not None:
                query_params[key] = value

        return path_params, query_params
