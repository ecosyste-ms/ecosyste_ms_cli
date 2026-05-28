"""Handler for advisories API operations."""

from .base import OperationHandler


class AdvisoriesOperationHandler(OperationHandler):
    """Handler for advisories API operations.

    The listing/lookup operations take only query parameters (handled by the
    default behavior); ``getAdvisory`` and ``getSource`` map a single value onto
    the path.
    """

    OPERATION_PARAMS = {
        "getAdvisory": [("advisoryUUID", ["advisoryuuid"])],
        "getSource": [("sourceKind", ["sourcekind"])],
    }
