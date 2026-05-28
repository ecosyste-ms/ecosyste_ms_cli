"""Handler for docker API operations."""

from .base import OperationHandler


class DockerOperationHandler(OperationHandler):
    """Handler for docker API operations.

    ``getPackages``, ``getDistros``, and ``usage`` take only query parameters
    (handled by the default behavior); the rest map package/version/ecosystem/
    distro identifiers onto the path.
    """

    OPERATION_PARAMS = {
        "getPackage": [("packageName", ["packagename"])],
        "getPackageVersions": [("packageName", ["packagename"])],
        "getPackageVersion": [("packageName", ["packagename"]), ("versionNumber", ["versionnumber"])],
        "usageEcosystem": [("ecosystem", ["ecosystem"])],
        "usagePackage": [("ecosystem", ["ecosystem"]), ("package", ["package"])],
        "getDistro": [("slug", ["slug"])],
        "getDistroVersions": [("slug", ["slug"])],
    }
