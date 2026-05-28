"""Handler for archives API operations."""

from .base import OperationHandler


class ArchivesOperationHandler(OperationHandler):
    """Handler for archives API operations.

    Every archives operation (``list``, ``contents``, ``readme``, ``changelog``,
    ``repopack``) takes only query parameters -- ``url`` and, for ``contents``,
    ``path`` -- so the base "all remaining kwargs become query params" behavior
    is sufficient and no path-parameter mapping is declared.
    """
