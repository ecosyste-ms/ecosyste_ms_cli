"""Handler for issues API operations."""

from .base import OperationHandler


class IssuesOperationHandler(OperationHandler):
    """Handler for issues API operations."""

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
