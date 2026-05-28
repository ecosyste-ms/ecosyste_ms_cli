"""Handler for licenses API operations."""

from .base import OperationHandler


class LicensesOperationHandler(OperationHandler):
    """Handler for licenses API operations.

    ``createJob`` takes only a ``url`` query parameter (handled by the default
    "remaining kwargs become query params" behavior); ``getJob`` maps the job id
    onto the ``jobID`` path parameter.
    """

    OPERATION_PARAMS = {
        "getJob": [("jobID", ["job_id", "jobid"])],
    }
