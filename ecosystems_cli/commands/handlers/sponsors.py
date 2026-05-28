"""Handler for sponsors API operations."""

from .base import OperationHandler


class SponsorsOperationHandler(OperationHandler):
    """Handler for sponsors API operations."""

    OPERATION_PARAMS = {
        "getAccount": [("login", ["login"])],
        "listAccountSponsors": [("login", ["login"])],
        "listAccountSponsorships": [("login", ["login"])],
    }
