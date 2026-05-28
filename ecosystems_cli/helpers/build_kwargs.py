"""Utility for building API call kwargs from optional command parameters."""

from typing import Any, Dict


def build_kwargs(**maybe: Any) -> Dict[str, Any]:
    """Collect keyword arguments, dropping any whose value is None.

    Replaces the repeated ``if x is not None: kwargs[...] = x`` blocks at command
    call sites. Keys whose value is ``None`` are omitted; every other value
    (including ``0``, ``False``, and ``""``) is kept.

    Callers whose API expects a key name that differs from the Python parameter
    name should merge the result, e.g.
    ``{"registryName": registry_name, **build_kwargs(page=page)}``.
    """
    return {key: value for key, value in maybe.items() if value is not None}
