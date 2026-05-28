"""Handler for diff API operations."""

from .base import OperationHandler


class DiffOperationHandler(OperationHandler):
    """Handler for diff API operations.

    ``createJob`` takes two URLs to compare as query parameters (``url_1`` and
    ``url_2``, handled by the default "remaining kwargs become query params"
    behavior); ``getJob`` maps the job id onto the ``jobID`` path parameter.
    """

    OPERATION_PARAMS = {
        "getJob": [("jobID", ["job_id", "jobid"])],
    }
