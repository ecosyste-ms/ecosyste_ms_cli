"""Handler for repos API operations."""

from .base import OperationHandler


class ReposOperationHandler(OperationHandler):
    """Handler for repos API operations."""

    OPERATION_PARAMS = {
        "topic": [("topic", ["topic"])],
        "getHost": [("hostName", ["hostname"])],
        "getHostOwners": [("hostName", ["hostname"])],
        # Capital "HostName" is intentional: this op's spec path is
        # /hosts/{HostName}/owners/lookup, unlike the lowercase {hostName} elsewhere.
        "lookupHostOwner": [("HostName", ["hostname"])],
        "getHostOwner": [("hostName", ["hostname"]), ("ownerLogin", ["ownerlogin"])],
        "getHostOwnerRepositories": [("hostName", ["hostname"]), ("ownerLogin", ["ownerlogin"])],
        "getHostRepositories": [("hostName", ["hostname"])],
        "getHostRepositoryNames": [("hostName", ["hostname"])],
        "getHostOwnerNames": [("hostName", ["hostname"])],
        "getHostRepository": [("hostName", ["hostname"]), ("repositoryName", ["repositoryname"])],
        "getHostRepositoryManifests": [("hostName", ["hostname"]), ("repositoryName", ["repositoryname"])],
        "getHostRepositoryTags": [("hostName", ["hostname"]), ("repositoryName", ["repositoryname"])],
        "getHostRepositoryTag": [("hostName", ["hostname"]), ("repositoryName", ["repositoryname"]), ("tag", ["tag"])],
        "getHostRepositoryTagManifests": [("hostName", ["hostname"]), ("repositoryName", ["repositoryname"]), ("tag", ["tag"])],
        "getHostRepositoryReleases": [("hostName", ["hostname"]), ("repositoryName", ["repositoryname"])],
        "getHostRepositorySbom": [("hostName", ["hostname"]), ("repositoryName", ["repositoryname"])],
        "getHostRepositoryRelease": [
            ("hostName", ["hostname"]),
            ("repositoryName", ["repositoryname"]),
            ("release", ["release"]),
        ],
        "usageEcosystem": [("ecosystem", ["ecosystem"])],
        "usagePackage": [("ecosystem", ["ecosystem"]), ("package", ["package"])],
        "usagePackageDependencies": [("ecosystem", ["ecosystem"]), ("package", ["package"])],
        "usagePackageDependentRepositories": [("ecosystem", ["ecosystem"]), ("package", ["package"])],
        "getHostOwnerSponsorsLogins": [("hostName", ["hostname"])],
    }
