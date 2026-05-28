"""Handler for commits API operations."""

from .base import OperationHandler


class CommitsOperationHandler(OperationHandler):
    """Handler for commits API operations."""

    OPERATION_PARAMS = {
        "getHost": [("hostName", ["hostname"])],
        "getHostRepositories": [("hostName", ["hostname"])],
        "getHostRepository": [("hostName", ["hostname"]), ("repoName", ["reponame"])],
        "getRepositoryCommits": [("hostName", ["hostname"]), ("repoName", ["reponame"])],
        "getHostCommitter": [("hostName", ["hostname"]), ("login", ["login"])],
    }
