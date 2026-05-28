"""Handler for packages API operations."""

from .base import OperationHandler


class PackagesOperationHandler(OperationHandler):
    """Handler for packages API operations."""

    OPERATION_PARAMS = {
        "getKeyword": [("keywordName", ["keywordname"])],
        "getRegistry": [("registryName", ["registryname"])],
        "lookupRegistryPackage": [("registryName", ["registryname"])],
        "getRegistryMaintainers": [("registryName", ["registryname"])],
        "getRegistryMaintainer": [("registryName", ["registryname"]), ("MaintainerLoginOrUUID", ["maintainerloginoruuid"])],
        "getRegistryMaintainerPackages": [
            ("registryName", ["registryname"]),
            ("MaintainerLoginOrUUID", ["maintainerloginoruuid"]),
        ],
        "getRegistryNamespaces": [("registryName", ["registryname"])],
        "getRegistryNamespace": [("registryName", ["registryname"]), ("namespaceName", ["namespacename"])],
        "getRegistryNamespacePackages": [("registryName", ["registryname"]), ("namespaceName", ["namespacename"])],
        "getRegistryPackages": [("registryName", ["registryname"])],
        "getRegistryPackageNames": [("registryName", ["registryname"])],
        "getRegistryRecentVersions": [("registryName", ["registryname"])],
        "getRegistryPackage": [("registryName", ["registryname"]), ("packageName", ["packagename"])],
        "getRegistryPackageDependentPackages": [("registryName", ["registryname"]), ("packageName", ["packagename"])],
        "getRegistryPackageCodeMeta": [("registryName", ["registryname"]), ("packageName", ["packagename"])],
        "getRegistryPackageDependentPackageKinds": [("registryName", ["registryname"]), ("packageName", ["packagename"])],
        "getRegistryPackageRelatedPackages": [("registryName", ["registryname"]), ("packageName", ["packagename"])],
        "getRegistryPackageVersionNumbers": [("registryName", ["registryname"]), ("packageName", ["packagename"])],
        "getRegistryPackageVersions": [("registryName", ["registryname"]), ("packageName", ["packagename"])],
        "getRegistryPackageVersion": [
            ("registryName", ["registryname"]),
            ("packageName", ["packagename"]),
            ("versionNumber", ["versionnumber"]),
        ],
        "getRegistryPackageVersionCodeMeta": [
            ("registryName", ["registryname"]),
            ("packageName", ["packagename"]),
            ("versionNumber", ["versionnumber"]),
        ],
    }
