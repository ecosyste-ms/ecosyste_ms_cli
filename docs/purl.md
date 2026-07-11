# Package URL (PURL) Support in Ecosystems CLI

The Ecosystems CLI accepts [Package URLs (PURLs)](https://github.com/package-url/purl-spec) as a convenient, unambiguous way to identify packages across ecosystems and registries with a single `--purl` flag instead of multiple positional arguments or flags.

## What is a PURL?

A Package URL is a standardized identifier for a software package. The general format is:

```
pkg:<type>/<namespace>/<name>@<version>
```

For example, `pkg:npm/lodash@4.17.21` or `pkg:npm/@babel/core@7.22.0` (scoped). The `namespace` is optional and is used for scopes (`@babel`) or group ids (`org.apache.commons`).

## Two ways `--purl` is used

Commands fall into two categories depending on how the PURL is consumed:

1. **Decomposed locally** — the CLI parses the PURL and fills in the command's
   ecosystem/registry and package-name parameters before calling the API.
2. **Passed through to the API** — the PURL is sent verbatim as a `purl` query
   parameter and the API resolves it server-side.

The distinction matters for two things: precedence (below) and the ecosystem-vs-registry-name handling (below).

### Precedence: explicit arguments win over the PURL

For commands that decompose a PURL, any value you also pass explicitly (a positional argument or a flag) **takes precedence** over the value derived from the PURL. The PURL only fills in parameters you did *not* otherwise provide. Mixing them is allowed; it does not error.

```bash
# PURL says npm/lodash, but the positional args win -> looks up pypi/django
ecosystems packages get_registry_package --purl "pkg:npm/lodash" pypi.org django

# PURL says npm/fsa, but the flags win -> filters advisories for pypi/django
ecosystems advisories get_advisories --purl "pkg:npm/fsa" --ecosystem pypi --package-name django
```

### Ecosystem name vs. registry name

Decomposing commands map the PURL type two different ways:

- **Ecosystem-name commands** keep the raw PURL type (e.g. `npm`, `pypi`). These
  filter by ecosystem: `advisories get_advisories`, `dependabot get_advisories`,
  `packages get_dependencies`, and the three `repos usage_package*` commands.
- **Registry-name commands** map the PURL type to a registry name (e.g. `npm` ->
  `npmjs.org`) because they address a specific registry. These are the
  `packages get_registry_package*` commands.

The mapping comes from `registries.yaml` and is applied by `purl_type_to_registry`.

### A note on positional argument order

The auto-generated `packages get_registry_package*` and `repos usage_package*` commands take their positional arguments in the order `PACKAGE_NAME` then `REGISTRY_NAME`/`ECOSYSTEM` (package first). This is easy to get wrong on the command line — using `--purl` sidesteps the ambiguity entirely, since it assigns each parameter by name.

## Commands supporting `--purl`

Every example below is verified against the live API.

### Advisories API

#### `get_advisories` (decomposes into `--ecosystem` + `--package-name`)

```bash
# Search advisories for a package
ecosystems advisories get_advisories --purl "pkg:npm/@babel/traverse"

# Combine with other filters
ecosystems advisories get_advisories --purl "pkg:npm/fsa" --severity high
```

#### `lookup_advisories` (PURL passed to the API)

Look up advisories for a specific package, optionally pinned to a version. A
source repository URL may be used instead via `--repository-url`.

```bash
ecosystems advisories lookup_advisories --purl "pkg:npm/lodash@4.17.20"
```

### Dependabot API

#### `get_advisories` (decomposes into `--ecosystem` + `--package-name`)

```bash
ecosystems dependabot get_advisories --purl "pkg:npm/lodash"
```

### Packages API

#### `get_dependencies` (decomposes into `--ecosystem` + `--package-name`)

```bash
ecosystems packages get_dependencies --purl "pkg:npm/express@4.18.2"
```

> The version in the PURL is ignored by this endpoint; only ecosystem and package name are used.

#### `lookup_package` (PURL passed to the API)

Look up a package across all registries for its ecosystem.

```bash
ecosystems packages lookup_package --purl "pkg:pypi/django"
```

#### `lookup_registry_package` (PURL passed to the API, registry required)

Look up a package **within a specific registry**. The registry name is a required
positional argument; `--purl` supplies the package identity.

```bash
ecosystems packages lookup_registry_package npmjs.org --purl "pkg:npm/lodash"
```

#### `get_registry_package` (decomposes into `REGISTRY_NAME` + `PACKAGE_NAME`)

```bash
# Simple package
ecosystems packages get_registry_package --purl "pkg:npm/lodash"

# Scoped package
ecosystems packages get_registry_package --purl "pkg:npm/@types/node"

# Equivalent without PURL
ecosystems packages get_registry_package npmjs.org lodash
```

#### `get_registry_package_version` (decomposes into `REGISTRY_NAME` + `PACKAGE_NAME` + `VERSION_NUMBER`)

The PURL **must** include a version.

```bash
ecosystems packages get_registry_package_version --purl "pkg:npm/lodash@4.17.21"
ecosystems packages get_registry_package_version --purl "pkg:npm/@babel/core@7.22.0"

# Equivalent without PURL
ecosystems packages get_registry_package_version npmjs.org lodash 4.17.21
```

If the PURL has no version, the command errors:

```bash
ecosystems packages get_registry_package_version --purl "pkg:npm/lodash"
# Error: Either --purl (with version) or all three arguments
#        (REGISTRY_NAME, PACKAGE_NAME, VERSION_NUMBER) are required
```

#### `get_registry_package_versions` (decomposes into `REGISTRY_NAME` + `PACKAGE_NAME`)

```bash
ecosystems packages get_registry_package_versions --purl "pkg:npm/lodash"
```

#### `get_registry_package_version_numbers` (decomposes into `REGISTRY_NAME` + `PACKAGE_NAME`)

```bash
ecosystems packages get_registry_package_version_numbers --purl "pkg:npm/lodash"
```

#### `get_registry_package_dependent_packages` (decomposes into `REGISTRY_NAME` + `PACKAGE_NAME`)

```bash
ecosystems packages get_registry_package_dependent_packages --purl "pkg:npm/left-pad"
```

> For very widely-used packages this endpoint can be slow; raise `--timeout` (e.g.
> `--timeout 90`) if the request times out.

### Repos API

#### `repositories_lookup` (PURL passed to the API)

Look up repository metadata.

```bash
ecosystems repos repositories_lookup --purl "pkg:github/facebook/react"
```

#### `usage_package` (decomposes into `ECOSYSTEM` + `PACKAGE`)

```bash
ecosystems repos usage_package --purl "pkg:npm/lodash"
```

#### `usage_package_dependencies` (decomposes into `ECOSYSTEM` + `PACKAGE`)

```bash
ecosystems repos usage_package_dependencies --purl "pkg:npm/lodash"
```

#### `usage_package_dependent_repositories` (decomposes into `ECOSYSTEM` + `PACKAGE`)

```bash
ecosystems repos usage_package_dependent_repositories --purl "pkg:npm/lodash"
```

> `--purl` decomposes correctly here, but at the time of writing the underlying
> ecosyste.ms endpoint returns a server-side error for this route; the example is
> shown for completeness.

## Common PURL formats

```bash
# NPM (JavaScript)
pkg:npm/lodash@4.17.21
pkg:npm/@types/node@18.0.0          # scoped
pkg:npm/@babel/core@7.22.0          # scoped

# PyPI (Python)
pkg:pypi/django@4.2.0
pkg:pypi/requests@2.28.0

# GitHub
pkg:github/facebook/react

# Others supported by the spec
pkg:cargo/serde       # Rust
pkg:gem/rails         # Ruby
pkg:maven/org.apache.commons/commons-lang3@3.12.0   # Java (group/artifact)
pkg:nuget/Newtonsoft.Json
```

## Error handling

### Invalid PURL

Decomposing commands validate the PURL locally and raise a usage error:

```bash
ecosystems packages get_registry_package --purl "invalid-purl"
# Error: Invalid PURL: 'invalid-purl'. Expected format: pkg:type/name (e.g. pkg:npm/lodash).
```

Pass-through commands forward the PURL to the API, which reports the problem:

```bash
ecosystems advisories lookup_advisories --purl "invalid-purl"
# Error: HTTP error: {"error":"Invalid PURL format"}
```

### Missing required parameters

```bash
ecosystems packages get_registry_package
# Error: Either --purl or both REGISTRY_NAME and PACKAGE_NAME arguments are required
```

## Implementation notes

PURL parsing lives in `ecosystems_cli/helpers/purl_parser.py`:

- `parse_purl(purl)` returns `(type, name)`.
- `parse_purl_with_version(purl)` returns `(type, name, version)`.
- `purl_type_to_registry(type)` maps a PURL type to a registry name using
  `registries.yaml` (used only by the registry-name commands).

For a scoped or namespaced PURL, the namespace and name are recombined with
the ecosystem's separator: a forward slash for most types (e.g.
`pkg:npm/@babel/core` -> name `@babel/core`,
`pkg:golang/github.com/gorilla/mux` -> name `github.com/gorilla/mux`), and a
colon for maven (`pkg:maven/org.apache.commons/commons-lang3` -> name
`org.apache.commons:commons-lang3`), matching how the ecosyste.ms APIs store
package names.

For PURL types served by more than one registry, the canonical registry is
preferred over the first entry in `registries.yaml` (e.g. `maven` ->
`repo1.maven.org`, `gem` -> `rubygems.org`).
