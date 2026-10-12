"""Handler for awesome API operations."""

from .base import OperationHandler


class AwesomeOperationHandler(OperationHandler):
    """Handler for awesome API operations.

    ``lookupProject``/``lookupList`` (query ``url``) and the list operations take
    only query parameters (handled by the default behavior); the rest map an
    ``id`` or ``slug`` onto the path.
    """

    OPERATION_PARAMS = {
        "getProject": [("id", ["id"])],
        "getProjectLists": [("id", ["id"])],
        "getList": [("id", ["id"])],
        "getListProjects": [("id", ["id"])],
        "getListListProjects": [("id", ["id"])],
        "getTopic": [("slug", ["slug"])],
    }
