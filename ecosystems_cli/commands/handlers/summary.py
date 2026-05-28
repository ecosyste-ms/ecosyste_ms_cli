"""Handler for summary API operations."""

from .base import OperationHandler


class SummaryOperationHandler(OperationHandler):
    """Handler for summary API operations.

    ``lookupProject`` (query ``url``) and the list operations take only query
    parameters (handled by the default behavior); the rest map an ``id`` onto the
    path.
    """

    OPERATION_PARAMS = {
        "getProject": [("id", ["id"])],
        "getCollection": [("id", ["id"])],
        "getCollectionProjects": [("id", ["id"])],
    }
