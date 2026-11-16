import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ecosystems_cli.constants import OPENAPI_FILE_EXTENSION

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files

PARAMETER_REF_PREFIX = "#/components/parameters/"


def _resolve_parameter_refs(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Inline ``$ref`` entries in operation parameter lists.

    Specs may declare shared parameters under ``components/parameters`` and
    reference them from operations. Command generation, handlers and the MCP
    server read each parameter's ``name``/``in`` directly, so the references
    are replaced with the definitions they point to.
    """
    if not isinstance(spec, dict):
        return spec
    shared = spec.get("components", {}).get("parameters", {})
    for path_item in spec.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict) or "parameters" not in operation:
                continue
            operation["parameters"] = [
                (
                    shared[param["$ref"][len(PARAMETER_REF_PREFIX) :]]
                    if param.get("$ref", "").startswith(PARAMETER_REF_PREFIX)
                    else param
                )
                for param in operation["parameters"]
            ]
    return spec


def load_api_spec(api_name: str, base_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load OpenAPI specification from file, with parameter references resolved."""
    if base_path is None:
        # Use importlib.resources for reliable resource access
        try:
            api_file_name = f"{api_name}{OPENAPI_FILE_EXTENSION}"
            spec_content = files("ecosystems_cli.apis").joinpath(api_file_name).read_text()
            return _resolve_parameter_refs(yaml.safe_load(spec_content))
        except (FileNotFoundError, ModuleNotFoundError):
            raise ValueError(f"API specification for '{api_name}' not found")
    else:
        # Fallback for custom base_path (mainly for testing)
        api_file = base_path / f"{api_name}{OPENAPI_FILE_EXTENSION}"
        if not api_file.exists():
            raise ValueError(f"API specification for '{api_name}' not found")
        with open(api_file, "r") as f:
            return _resolve_parameter_refs(yaml.safe_load(f))
