"""Fallback handler for APIs without a dedicated handler."""

from .base import OperationHandler


class DefaultOperationHandler(OperationHandler):
    """Fallback returned by ``OperationHandlerFactory`` for an unregistered API.

    It declares no ``OPERATION_PARAMS``, so it relies entirely on the base
    behavior: no path parameters, and every non-None keyword argument becomes a
    query parameter. Every shipped API has its own handler, so this only takes
    effect if a new API is added without registering one -- in which case a
    predictable "all query params" mapping is a safer default than guessing.
    """
