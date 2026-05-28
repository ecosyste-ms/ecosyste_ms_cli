"""Handler for opencollective API operations."""

from .base import OperationHandler


class OpenCollectiveOperationHandler(OperationHandler):
    """Handler for opencollective API operations.

    ``lookupProject`` (query ``url``), ``getProjectPackages``, and the list
    operations take only query parameters (handled by the default behavior); the
    rest map an ``id`` or ``slug`` onto the path.
    """

    OPERATION_PARAMS = {
        "getProject": [("id", ["id"])],
        "getCollective": [("id", ["id"])],
        "getCollectiveProjects": [("slug", ["slug"])],
    }
