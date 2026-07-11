"""Tests for PURL parser."""

from ecosystems_cli.helpers.purl_parser import parse_purl, parse_purl_with_version, purl_type_to_registry


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
