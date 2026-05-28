"""Handler for parser API operations."""

from .base import OperationHandler


class ParserOperationHandler(OperationHandler):
    """Handler for parser API operations.

    ``createJob`` takes only a ``url`` query parameter and ``jobFormats`` takes no
    parameters (both handled by the default behavior); ``getJob`` maps the job id
    onto the ``jobID`` path parameter.
    """

    OPERATION_PARAMS = {
        "getJob": [("jobID", ["job_id", "jobid"])],
    }
