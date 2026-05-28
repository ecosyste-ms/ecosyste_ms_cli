"""Utility for parsing Package URLs (PURLs)."""

from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

import click
import yaml
from packageurl import PackageURL


@lru_cache(maxsize=1)
def _load_purl_type_to_registry_mapping() -> Dict[str, str]:
    """Load mapping from PURL type to registry name from registries.yaml.

    Returns a dictionary mapping purl_type to registry name.
    For purl_types with multiple registries, the first one is used.

    Returns:
        Dictionary mapping purl_type to registry name (e.g., {'npm': 'npmjs.org'})
    """
    # Get the path to registries.yaml
    current_file = Path(__file__)
    apis_dir = current_file.parent.parent / "apis"
    registries_file = apis_dir / "registries.yaml"

    if not registries_file.exists():
        return {}

    try:
        with open(registries_file, "r") as f:
            data = yaml.safe_load(f)

        mapping = {}
        if "registries" in data:
            for registry in data["registries"]:
                purl_type = registry.get("purl_type")
                name = registry.get("name")
                if purl_type and name:
                    # For purl_types with multiple registries, use the first one
                    if purl_type not in mapping:
                        mapping[purl_type] = name

        return mapping
    except Exception:
        # If we can't load the file, return empty mapping
        return {}


def purl_type_to_registry(purl_type: str) -> str:
    """Convert a PURL type to a registry name.

    Args:
        purl_type: PURL type (e.g., 'npm', 'pypi')

    Returns:
        Registry name (e.g., 'npmjs.org', 'pypi.org') or the purl_type if no mapping exists
    """
    mapping = _load_purl_type_to_registry_mapping()
    return mapping.get(purl_type, purl_type)


def parse_purl(purl: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse a Package URL (PURL) to extract ecosystem and package name.

    PURL format: pkg:type/namespace/name@version?qualifiers#subpath

    Examples:
        pkg:npm/fsa -> ('npm', 'fsa')
        pkg:npm/@types/node -> ('npm', '@types/node')
        pkg:pypi/django@4.2.0 -> ('pypi', 'django')
        pkg:maven/org.apache.commons/commons-lang3 -> ('maven', 'org.apache.commons/commons-lang3')

    Args:
        purl: Package URL string

    Returns:
        Tuple of (ecosystem, package_name) or (None, None) if parsing fails
        Note: ecosystem is the purl type (e.g., 'npm', 'pypi'), not the registry name
    """
    ecosystem, package_name, _ = parse_purl_with_version(purl)
    return ecosystem, package_name


def parse_purl_with_version(purl: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Parse a Package URL (PURL) to extract ecosystem, package name, and version.

    PURL format: pkg:type/namespace/name@version?qualifiers#subpath

    Examples:
        pkg:npm/fsa -> ('npm', 'fsa', None)
        pkg:npm/@types/node -> ('npm', '@types/node', None)
        pkg:pypi/django@4.2.0 -> ('pypi', 'django', '4.2.0')
        pkg:npm/lodash@4.17.21 -> ('npm', 'lodash', '4.17.21')
        pkg:maven/org.apache.commons/commons-lang3@3.12.0 -> ('maven', 'org.apache.commons/commons-lang3', '3.12.0')

    Args:
        purl: Package URL string

    Returns:
        Tuple of (ecosystem, package_name, version) or (None, None, None) if parsing fails
        Note: ecosystem is the purl type (e.g., 'npm', 'pypi'), not the registry name
    """
    if not purl:
        return None, None, None

    try:
        purl_obj = PackageURL.from_string(purl)

        # Construct the full package name from namespace and name
        # For npm scoped packages: namespace='@babel', name='traverse' -> '@babel/traverse'
        # For maven: namespace='org.apache.commons', name='commons-lang3' -> 'org.apache.commons/commons-lang3'
        if purl_obj.namespace:
            # Namespace and name are combined with a forward slash
            package_name = f"{purl_obj.namespace}/{purl_obj.name}"
        else:
            package_name = purl_obj.name

        return purl_obj.type, package_name, purl_obj.version
    except (ValueError, AttributeError):
        # Return None for invalid PURLs
        return None, None, None


def apply_purl(
    purl: Optional[str],
    *,
    with_version: bool = False,
    type_mapper: Callable[[str], str] = lambda purl_type: purl_type,
) -> Dict[str, str]:
    """Decompose a PURL into command parameters, raising on an unparseable PURL.

    Returns an empty dict when ``purl`` is falsy. Raises ``click.UsageError`` when
    the PURL cannot be parsed. Otherwise returns a dict with only the keys the PURL
    provided: ``ecosystem`` (passed through ``type_mapper``), ``package_name``, and
    -- when ``with_version`` is set -- ``version``.

    Callers merge the result so explicit args win, e.g.
    ``ecosystem = ecosystem or apply_purl(purl).get("ecosystem")``.
    """
    if not purl:
        return {}

    ecosystem, package_name, version = parse_purl_with_version(purl)
    if not ecosystem and not package_name:
        if with_version:
            example = "pkg:type/name@version (e.g. pkg:npm/lodash@4.17.21)"
        else:
            example = "pkg:type/name (e.g. pkg:npm/lodash)"
        raise click.UsageError(f"Invalid PURL: {purl!r}. Expected format: {example}.")

    result: Dict[str, str] = {}
    if ecosystem:
        result["ecosystem"] = type_mapper(ecosystem)
    if package_name:
        result["package_name"] = package_name
    if with_version and version:
        result["version"] = version
    return result
