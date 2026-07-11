"""Handler for resolve API operations."""

from .base import OperationHandler


class ResolveOperationHandler(OperationHandler):
    """Handler for resolve API operations.

    ``createJob`` takes ``package_name`` plus one of ``registry`` / ``ecosystem``
    and optional ``version`` / ``tree`` query parameters, and ``listRegistries``
    takes none (both handled by the default behavior); ``getJob`` maps the job id
    onto the ``jobID`` path parameter.
    """

    OPERATION_PARAMS = {
        "getJob": [("jobID", ["job_id", "jobid"])],
    }
