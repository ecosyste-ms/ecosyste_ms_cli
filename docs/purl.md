# Package URL (PURL) Support in Ecosystems CLI

The Ecosystems CLI supports [Package URL (PURL)](https://github.com/package-url/purl-spec) as a convenient way to specify packages across different ecosystems and registries.

## What is a PURL?

A Package URL (PURL) is a standardized way to identify software packages across different package managers and ecosystems. The general format is:

```
pkg:<type>/<namespace>/<name>@<version>
```

## Commands Supporting `--purl`

### 1. Advisories API

#### Get Advisories

Use `--purl` as an alternative to specifying `--ecosystem` and `--package-name` separately.

**Examples:**

```bash
# Search advisories for a specific package
ecosystems advisories get_advisories --purl "pkg:npm/@babel/traverse"

# Search advisories with additional filters
ecosystems advisories get_advisories --purl "pkg:npm/fsa" --severity high
```

**Note:** When using `--purl` with `get_advisories`, you cannot also specify `--ecosystem` and `--package-name` separately. The PURL overrides these parameters.

#### Lookup Advisories by PURL

Directly lookup advisories for a specific package version.

**Example:**

```bash
ecosystems advisories lookup_advisories_by_purl --purl "pkg:npm/lodash@4.17.20"
```

### 2. Packages API

#### Lookup Package

Lookup a package by PURL across the ecosystem.

**Example:**

```bash
ecosystems packages lookup_package --purl "pkg:pypi/django"
```

#### Get Registry Package

Use `--purl` as an alternative to specifying `REGISTRY_NAME` and `PACKAGE_NAME` arguments.

**Examples:**

```bash
# Simple package lookup
ecosystems packages get_registry_package --purl "pkg:npm/lodash"

# Scoped package lookup
ecosystems packages get_registry_package --purl "pkg:npm/@types/node"

# Equivalent traditional syntax (without PURL)
ecosystems packages get_registry_package npmjs.org lodash
```

#### Get Registry Package Version

Use `--purl` with a version to get a specific package version. The PURL **must** include a version.

**Examples:**

```bash
# Get specific version of a package
ecosystems packages get_registry_package_version --purl "pkg:npm/lodash@4.17.21"

# Get specific version of a scoped package
ecosystems packages get_registry_package_version --purl "pkg:npm/@babel/core@7.22.0"

# Equivalent traditional syntax (without PURL)
ecosystems packages get_registry_package_version npmjs.org lodash 4.17.21
```

**Error:** If you provide a PURL without a version to `get_registry_package_version`, you'll get an error:

```bash
# This will fail - no version specified
ecosystems packages get_registry_package_version --purl "pkg:npm/lodash"
# Error: Either --purl (with version) or all three arguments are required
```

### 3. Repos API

#### Repository Lookup

Lookup repository metadata using a PURL.

**Example:**

```bash
ecosystems repos repositories_lookup --purl "pkg:github/facebook/react"
```

## Common PURL Formats

### NPM (JavaScript)

```bash
# Regular package
pkg:npm/lodash@4.17.21

# Scoped package
pkg:npm/@types/node@18.0.0
pkg:npm/@babel/core@7.22.0
```

### PyPI (Python)

```bash
pkg:pypi/django@4.2.0
pkg:pypi/requests@2.28.0
```

### GitHub

```bash
pkg:github/facebook/react
pkg:github/microsoft/vscode
```

### Other Ecosystems

The PURL specification supports many other ecosystems including:
- `pkg:cargo/...` (Rust)
- `pkg:gem/...` (Ruby)
- `pkg:maven/...` (Java)
- `pkg:nuget/...` (.NET)
- And many more

## Benefits of Using PURL

1. **Consistency:** Unified way to specify packages across different ecosystems
2. **Convenience:** Single parameter instead of multiple arguments
3. **Portability:** PURLs are standardized and can be used across different tools
4. **Clarity:** Self-documenting format that includes all necessary package information

## Error Handling

### Invalid PURL Format

If you provide an invalid PURL, you'll receive an error:

```bash
ecosystems advisories lookup_advisories_by_purl --purl "invalid-purl"
# Error: Invalid PURL format
```

### Missing Required Parameters

If you don't provide either a PURL or the traditional arguments:

```bash
ecosystems packages get_registry_package
# Error: Either --purl or both REGISTRY_NAME and PACKAGE_NAME arguments are required
```

### Conflicting Parameters

When using `--purl`, you generally cannot also specify the traditional arguments. For example:

```bash
# This may cause unexpected behavior - avoid mixing PURL with traditional args
ecosystems advisories get_advisories --purl "pkg:npm/fsa" --ecosystem "pypi" --package-name "django"
```

The PURL parameters will typically override the traditional parameters.

## Implementation Notes

The PURL parsing is handled by the `parse_purl_with_version` function in `ecosystems_cli/helpers/purl_parser.py`, which extracts:
- Ecosystem/registry type (e.g., "npm", "pypi", "github")
- Package name (including namespace/scope if present)
- Version (if specified)

This allows the CLI to seamlessly convert PURL format into the appropriate API parameters.
