import pytest
import yaml

from ecosystems_cli.helpers.load_api_spec import load_api_spec


def test_load_api_spec_success(tmp_path):
    api_name = "testapi"
    apis_dir = tmp_path / "apis"
    apis_dir.mkdir()
    spec_content = {"openapi": "3.0.0", "info": {"title": "Test API", "version": "1.0.0"}}
    spec_path = apis_dir / f"{api_name}.openapi.yaml"
    with open(spec_path, "w") as f:
        yaml.dump(spec_content, f)
    # Patch __file__ location to tmp_path/helpers
    import ecosystems_cli.helpers.load_api_spec as las

    old_file = las.__file__
    las.__file__ = str(tmp_path / "helpers" / "load_api_spec.py")
    try:
        result = load_api_spec(api_name, base_path=apis_dir)
        assert result["openapi"] == "3.0.0"
        assert result["info"]["title"] == "Test API"
    finally:
        las.__file__ = old_file


def test_load_api_spec_not_found(tmp_path):
    api_name = "doesnotexist"
    import ecosystems_cli.helpers.load_api_spec as las

    old_file = las.__file__
    las.__file__ = str(tmp_path / "helpers" / "load_api_spec.py")
    try:
        with pytest.raises(ValueError):
            load_api_spec(api_name, base_path=tmp_path / "apis")
    finally:
        las.__file__ = old_file


def test_load_api_spec_resolves_parameter_refs(tmp_path):
    """Operations may reference shared parameters under components/parameters."""
    spec_content = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/items/{id}": {
                "get": {
                    "operationId": "getItem",
                    "parameters": [
                        {"$ref": "#/components/parameters/Id"},
                        {"name": "query", "in": "query", "schema": {"type": "string"}},
                    ],
                }
            }
        },
        "components": {
            "parameters": {
                "Id": {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
            }
        },
    }
    with open(tmp_path / "testapi.openapi.yaml", "w") as f:
        yaml.dump(spec_content, f)

    result = load_api_spec("testapi", base_path=tmp_path)

    parameters = result["paths"]["/items/{id}"]["get"]["parameters"]
    assert parameters[0] == {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
    assert parameters[1]["name"] == "query"


def test_packaged_specs_have_no_unresolved_parameter_refs():
    """Every packaged spec loads with inline parameters (each has a name and location)."""
    from pathlib import Path

    import ecosystems_cli.apis

    apis_dir = Path(ecosystems_cli.apis.__file__).parent
    for spec_file in sorted(apis_dir.glob("*.openapi.yaml")):
        api_name = spec_file.name.split(".")[0]
        spec = load_api_spec(api_name)
        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if not isinstance(operation, dict):
                    continue
                for param in operation.get("parameters", []):
                    assert "name" in param and "in" in param, f"{api_name} {method.upper()} {path}: {param}"
