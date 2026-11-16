"""Handler for awesome API operations."""

import re
from typing import Any, Dict, Tuple

from ecosystems_cli.exceptions import InvalidParameterError

from .base import OperationHandler

_URL = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)
_LIST_OPERATIONS = {"getList", "getListProjects", "getListListProjects"}
_PROJECT_OPERATIONS = {"getProject", "getProjectLists"}


class AwesomeOperationHandler(OperationHandler):
    """Handler for awesome API operations.

    ``lookupProject``/``lookupList`` (query ``url``) and the list operations take
    only query parameters (handled by the default behavior); the rest map an
    ``id`` or ``slug`` onto the path.

    List ids are a numeric id or ``owner/name``; project ids a numeric id or
    ``host/owner/name``. Values that can never resolve (URLs, project slugs
    without a host) are rejected with a hint instead of a bare 404.
    """

    OPERATION_PARAMS = {
        "getProject": [("id", ["id"])],
        "getProjectLists": [("id", ["id"])],
        "getList": [("id", ["id"])],
        "getListProjects": [("id", ["id"])],
        "getListListProjects": [("id", ["id"])],
        "getTopic": [("slug", ["slug"])],
    }

    def build_params(self, operation_id: str, args: tuple, kwargs: dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        path_params, query_params = super().build_params(operation_id, args, kwargs)
        value = str(path_params.get("id", ""))

        if operation_id in _LIST_OPERATIONS and _URL.match(value):
            raise InvalidParameterError(
                "id",
                "Pass the list as owner/name (e.g. sindresorhus/awesome), "
                f"or find it by URL with: ecosystems awesome lookup_list --url {value}",
            )
        if operation_id in _PROJECT_OPERATIONS and _URL.match(value):
            raise InvalidParameterError(
                "id",
                "Pass the project as host/owner/name (e.g. github.com/rails/rails), "
                f"or find it by URL with: ecosystems awesome lookup_project --url {value}",
            )
        if operation_id in _PROJECT_OPERATIONS and not value.isdigit() and "." not in value.split("/")[0]:
            raise InvalidParameterError(
                "id",
                (
                    f"Project ids are host/owner/name, e.g. github.com/{value}"
                    if "/" in value
                    else "Project ids are a numeric id or host/owner/name, e.g. github.com/rails/rails"
                ),
            )

        return path_params, query_params
