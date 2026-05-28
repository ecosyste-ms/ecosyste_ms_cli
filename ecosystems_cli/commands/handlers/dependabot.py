"""Handler for dependabot API operations."""

from .base import OperationHandler


class DependabotOperationHandler(OperationHandler):
    """Handler for dependabot API operations.

    ``repositoriesLookup`` (query ``url``), the listing operations, and
    ``getPackageEcosystems`` take only query parameters (handled by the default
    behavior); the rest map hierarchical path parameters such as
    ``/hosts/{hostName}/repositories/{repoName}/issues/{issueNumber}``.
    """

    OPERATION_PARAMS = {
        "getEcosystemPackages": [("ecosystem", ["ecosystem"])],
        "getPackage": [("ecosystem", ["ecosystem"]), ("name", ["name"])],
        "getIssuePackages": [("issueId", ["issueid"])],
        "getHost": [("hostName", ["hostname"])],
        "getHostRepositories": [("hostName", ["hostname"])],
        "getHostRepository": [("hostName", ["hostname"]), ("repoName", ["reponame"])],
        "getHostRepositoryIssues": [("hostName", ["hostname"]), ("repoName", ["reponame"])],
        "getHostRepositoryIssue": [
            ("hostName", ["hostname"]),
            ("repoName", ["reponame"]),
            ("issueNumber", ["issuenumber"]),
        ],
        "getAdvisory": [("advisoryId", ["advisoryid"])],
    }
