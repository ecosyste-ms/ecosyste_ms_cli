"""Handler for timeline API operations."""

from .base import OperationHandler


class TimelineOperationHandler(OperationHandler):
    """Handler for timeline API operations.

    ``getEvents`` takes only pagination query parameters (handled by the default
    behavior); ``getEvent`` maps the repository name onto the ``repoName`` path
    parameter and forwards pagination as query parameters.
    """

    OPERATION_PARAMS = {
        "getEvent": [("repoName", ["reponame"])],
    }
