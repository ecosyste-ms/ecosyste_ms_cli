"""Tests for PURL parser."""

import pytest

from ecosystems_cli.exceptions import InvalidParameterError
from ecosystems_cli.helpers.purl_parser import (
    PASS_THROUGH_PURL_FIELDS,
    normalize_purl,
    normalize_purl_fields,
    parse_purl,
    parse_purl_with_version,
    purl_type_to_registry,
)


def test_parse_purl_simple():
    """Test parsing a simple PURL."""
    ecosystem, package_name = parse_purl("pkg:npm/fsa")
    assert ecosystem == "npm"
    assert package_name == "fsa"


def test_parse_purl_scoped():
    """Test parsing a scoped package PURL."""
    ecosystem, package_name = parse_purl("pkg:npm/@babel/traverse")
    assert ecosystem == "npm"
    assert package_name == "@babel/traverse"


def test_parse_purl_with_version():
    """Test parsing a PURL with version."""
    ecosystem, package_name = parse_purl("pkg:pypi/django@4.2.0")
    assert ecosystem == "pypi"
    assert package_name == "django"


def test_parse_purl_with_namespace():
    """Test parsing a PURL with namespace (Maven style uses ':' separator)."""
    ecosystem, package_name = parse_purl("pkg:maven/org.apache.commons/commons-lang3")
    assert ecosystem == "maven"
    assert package_name == "org.apache.commons:commons-lang3"


def test_parse_purl_golang_namespace_keeps_slash():
    """Test that non-maven namespaces keep the '/' separator."""
    ecosystem, package_name = parse_purl("pkg:golang/github.com/gorilla/mux")
    assert ecosystem == "golang"
    assert package_name == "github.com/gorilla/mux"


def test_parse_purl_with_qualifiers():
    """Test parsing a PURL with qualifiers."""
    ecosystem, package_name = parse_purl("pkg:npm/fsa@1.0.0?arch=x86_64")
    assert ecosystem == "npm"
    assert package_name == "fsa"


def test_parse_purl_with_subpath():
    """Test parsing a PURL with subpath."""
    ecosystem, package_name = parse_purl("pkg:npm/fsa@1.0.0#some/subpath")
    assert ecosystem == "npm"
    assert package_name == "fsa"


def test_parse_purl_empty():
    """Test parsing an empty PURL."""
    ecosystem, package_name = parse_purl("")
    assert ecosystem is None
    assert package_name is None


def test_parse_purl_none():
    """Test parsing None."""
    ecosystem, package_name = parse_purl(None)
    assert ecosystem is None
    assert package_name is None


def test_parse_purl_invalid():
    """Test parsing an invalid PURL."""
    ecosystem, package_name = parse_purl("not-a-purl")
    assert ecosystem is None
    assert package_name is None


def test_parse_purl_missing_package():
    """Test parsing a PURL without package name."""
    ecosystem, package_name = parse_purl("pkg:npm/")
    assert ecosystem is None
    assert package_name is None


# Tests for parse_purl_with_version


def test_parse_purl_with_version_simple():
    """Test parsing a simple PURL without version."""
    ecosystem, package_name, version = parse_purl_with_version("pkg:npm/fsa")
    assert ecosystem == "npm"
    assert package_name == "fsa"
    assert version is None


def test_parse_purl_with_version_and_version():
    """Test parsing a PURL with version."""
    ecosystem, package_name, version = parse_purl_with_version("pkg:npm/lodash@4.17.21")
    assert ecosystem == "npm"
    assert package_name == "lodash"
    assert version == "4.17.21"


def test_parse_purl_with_version_scoped():
    """Test parsing a scoped package PURL without version."""
    ecosystem, package_name, version = parse_purl_with_version("pkg:npm/@babel/traverse")
    assert ecosystem == "npm"
    assert package_name == "@babel/traverse"
    assert version is None


def test_parse_purl_with_version_scoped_and_version():
    """Test parsing a scoped package PURL with version."""
    ecosystem, package_name, version = parse_purl_with_version("pkg:npm/@babel/core@7.22.0")
    assert ecosystem == "npm"
    assert package_name == "@babel/core"
    assert version == "7.22.0"


def test_parse_purl_with_version_pypi():
    """Test parsing a PyPI PURL with version."""
    ecosystem, package_name, version = parse_purl_with_version("pkg:pypi/django@4.2.0")
    assert ecosystem == "pypi"
    assert package_name == "django"
    assert version == "4.2.0"


def test_parse_purl_with_version_maven():
    """Test parsing a Maven PURL with version (group:artifact naming)."""
    ecosystem, package_name, version = parse_purl_with_version("pkg:maven/org.apache.commons/commons-lang3@3.12.0")
    assert ecosystem == "maven"
    assert package_name == "org.apache.commons:commons-lang3"
    assert version == "3.12.0"


def test_parse_purl_with_version_and_qualifiers():
    """Test parsing a PURL with version and qualifiers."""
    ecosystem, package_name, version = parse_purl_with_version("pkg:npm/lodash@4.17.21?arch=x86_64")
    assert ecosystem == "npm"
    assert package_name == "lodash"
    assert version == "4.17.21"


def test_parse_purl_with_version_and_subpath():
    """Test parsing a PURL with version and subpath."""
    ecosystem, package_name, version = parse_purl_with_version("pkg:npm/lodash@4.17.21#some/subpath")
    assert ecosystem == "npm"
    assert package_name == "lodash"
    assert version == "4.17.21"


def test_parse_purl_with_version_empty():
    """Test parsing an empty PURL."""
    ecosystem, package_name, version = parse_purl_with_version("")
    assert ecosystem is None
    assert package_name is None
    assert version is None


def test_parse_purl_with_version_none():
    """Test parsing None."""
    ecosystem, package_name, version = parse_purl_with_version(None)
    assert ecosystem is None
    assert package_name is None
    assert version is None


def test_parse_purl_with_version_invalid():
    """Test parsing an invalid PURL."""
    ecosystem, package_name, version = parse_purl_with_version("not-a-purl")
    assert ecosystem is None
    assert package_name is None
    assert version is None


# Tests for purl_type_to_registry


def test_purl_type_to_registry_npm():
    """Test converting npm to registry name."""
    assert purl_type_to_registry("npm") == "npmjs.org"


def test_purl_type_to_registry_pypi():
    """Test converting pypi to registry name."""
    assert purl_type_to_registry("pypi") == "pypi.org"


def test_purl_type_to_registry_maven():
    """Test converting maven to registry name."""
    # Maven has multiple registries; the canonical one (Maven Central) wins
    # over the alphabetical first-match (artifacts.alfresco.com).
    assert purl_type_to_registry("maven") == "repo1.maven.org"


def test_purl_type_to_registry_gem():
    """Test converting gem to registry name."""
    # gem has multiple registries; canonical rubygems.org wins over gem.coop.
    assert purl_type_to_registry("gem") == "rubygems.org"


def test_purl_type_to_registry_cargo():
    """Test converting cargo to registry name."""
    assert purl_type_to_registry("cargo") == "crates.io"


def test_purl_type_to_registry_unknown():
    """Test converting unknown purl type returns the type itself."""
    assert purl_type_to_registry("unknown") == "unknown"


@pytest.mark.parametrize(
    "purl, expected",
    [
        ("pkg:npm/lodash@4.17.21", "pkg:npm/lodash@4.17.21"),
        ("pkg:NPM/Lodash@4.17.21", "pkg:npm/lodash@4.17.21"),
        ("pkg:npm/@babel/core@7.22.0", "pkg:npm/%40babel/core@7.22.0"),
        ("pkg:npm/%40babel/core@7.22.0", "pkg:npm/%40babel/core@7.22.0"),
        ("pkg:pypi/Django_Rest@1.0", "pkg:pypi/django-rest@1.0"),
        ("pkg:maven/org.apache.commons/commons-lang3@3.12.0", "pkg:maven/org.apache.commons/commons-lang3@3.12.0"),
        ("pkg:gem/rails@7.0.0?platform=ruby", "pkg:gem/rails@7.0.0?platform=ruby"),
        # Types packageurl has no rules for are passed through, not rejected.
        ("pkg:bower/jquery@3.7.1", "pkg:bower/jquery@3.7.1"),
    ],
)
def test_normalize_purl(purl, expected):
    """normalize_purl returns the canonical PURL form defined by the PURL spec."""
    assert normalize_purl(purl) == expected


@pytest.mark.parametrize(
    "purl",
    [
        "",
        "invalid-purl",
        "npm/lodash",
        "pkg:npm",
        "pkg:npm/",
        # Parse fine but break the type's rules: maven requires a namespace, pypi prohibits one.
        "pkg:maven/commons-lang3@3.12.0",
        "pkg:pypi/foo/bar@1.0",
    ],
)
def test_normalize_purl_rejects_invalid(purl):
    with pytest.raises(ValueError):
        normalize_purl(purl)


@pytest.mark.parametrize("value", [None, 42, ["pkg:npm/lodash"]])
def test_normalize_purl_rejects_non_strings(value):
    with pytest.raises(ValueError, match="Invalid PURL"):
        normalize_purl(value)


def test_normalize_purl_error_message_names_type_rule():
    with pytest.raises(ValueError) as excinfo:
        normalize_purl("pkg:maven/commons-lang3@3.12.0")
    assert "Namespace is required for purl type: 'maven'" in str(excinfo.value)


def test_normalize_purl_error_message():
    with pytest.raises(ValueError) as excinfo:
        normalize_purl("invalid-purl")
    assert str(excinfo.value) == (
        "Invalid PURL: 'invalid-purl'. Expected format: pkg:type/name[@version] (e.g. pkg:npm/lodash@4.17.21)."
    )


class TestNormalizePurlFields:
    def test_normalizes_string_field(self):
        params = {"purl": "pkg:NPM/Lodash@4.17.21", "other": "x"}
        assert normalize_purl_fields("packages", "lookupPurl", params) == {
            "purl": "pkg:npm/lodash@4.17.21",
            "other": "x",
        }
        assert params["purl"] == "pkg:NPM/Lodash@4.17.21", "input must not be mutated"

    def test_normalizes_each_list_item(self):
        body = {"purls": ["pkg:NPM/Lodash", "pkg:npm/@babel/core"], "ecosystem": "npm"}
        assert normalize_purl_fields("packages", "bulkLookupPackages", body) == {
            "purls": ["pkg:npm/lodash", "pkg:npm/%40babel/core"],
            "ecosystem": "npm",
        }

    def test_invalid_purl_raises_invalid_parameter_error(self):
        with pytest.raises(InvalidParameterError) as excinfo:
            normalize_purl_fields("packages", "bulkLookupPurls", {"purls": ["pkg:npm/lodash", "invalid-purl"]})
        assert excinfo.value.parameter_name == "purls"
        assert "Invalid PURL: 'invalid-purl'" in str(excinfo.value)

    @pytest.mark.parametrize(
        "api, operation_id, params",
        [
            ("packages", "lookupPackage", {"purl": "not-touched"}),  # API reports bad PURLs itself
            ("packages", "lookupPurl", {"other": "x"}),
            ("packages", "lookupPurl", {}),
            ("packages", "lookupPurl", None),
        ],
    )
    def test_leaves_other_params_alone(self, api, operation_id, params):
        assert normalize_purl_fields(api, operation_id, params) == params


@pytest.mark.parametrize("api, operation_id", sorted(PASS_THROUGH_PURL_FIELDS))
def test_pass_through_purl_fields_exist_in_spec(api, operation_id):
    """Every registered field is a query parameter or body property of its operation."""
    from ecosystems_cli.helpers.load_api_spec import load_api_spec

    field = PASS_THROUGH_PURL_FIELDS[(api, operation_id)]
    spec = load_api_spec(api)
    operations = [op for path in spec["paths"].values() for op in path.values() if isinstance(op, dict)]
    operation = next(op for op in operations if op.get("operationId") == operation_id)

    query = {p["name"] for p in operation.get("parameters", []) if p.get("in") == "query"}
    body_schema = operation.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {})
    assert field in query or field in body_schema.get("properties", {})
