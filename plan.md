# Plan: API Spec Update Changes

Updated specs: `advisories`, `commits`, `issues`, `packages`, `repos`, `resolve`

The CLI auto-generates commands from OpenAPI specs via `APICommandGenerator`. New endpoints and query parameters are picked up automatically — but **path parameter mappings in handlers** and **tests** need manual updates.

---

## 1. Advisories API

### New endpoints
- `GET /sources` — `getSources` (no params)
- `GET /sources/{sourceKind}` — `getSource` (path: `sourceKind`)

### New query parameter
- `source` on `getAdvisories` — auto-discovered, no handler change needed

### Handler changes (`handlers/advisories.py`)
- Add `getSources` to handlers dict → `self._handle_no_params`
- Add `getSource` handler with path param `sourceKind`

### Tests (`tests/commands/test_advisories.py`)
- Add test for `get_sources` command
- Add test for `get_source` command with `sourceKind` path param

---

## 2. Commits API

### New endpoint
- `GET /hosts/{hostName}/committers/{login}` — `getHostCommitter` (path: `hostName`, `login`)

### Handler changes (`handlers/commits.py`)
- Add to `OPERATION_PARAMS`:
  ```python
  "getHostCommitter": [("hostName", ["hostname"]), ("login", ["login"])],
  ```

### Tests
- No existing `tests/commands/test_commits.py` — create one following the pattern in `test_repos.py`
- Test `get_host_committer` with hostName and login path params

---

## 3. Issues API

### New endpoints
- `GET /hosts/{hostName}/repositories/{repoName}/labels` — `getHostRepositoryLabels` (path: `hostName`, `repoName`)
- `GET /hosts/{hostName}/owners` — `getHostOwners` (path: `hostName`, query: `page`, `per_page`)
- `GET /hosts/{hostName}/owners/{ownerName}` — `getHostOwner` (path: `hostName`, `ownerName`)
- `GET /hosts/{hostName}/owners/{ownerName}/maintainers` — `getHostOwnerMaintainers` (path: `hostName`, `ownerName`)
- `GET /hosts/{hostName}/authors` — `getHostAuthors` (path: `hostName`, query: `page`, `per_page`)
- `GET /hosts/{hostName}/authors/{authorName}` — `getHostAuthor` (path: `hostName`, `authorName`)
- `POST /jobs` — `createJob` (body: `url`)
- `GET /jobs/{jobId}` — `getJob` (path: `jobId`)

### New query parameters on existing endpoint
- `pull_request`, `state`, `label` on `getHostRepositoryIssues` — auto-discovered, no handler change needed

### Removed parameters
- `page` and `per_page` removed from `getHostRepositories` — auto-discovered, no handler change needed

### Handler changes (`handlers/issues.py`)
- Add to `OPERATION_PARAMS`:
  ```python
  "getHostRepositoryLabels": [("hostName", ["hostname"]), ("repoName", ["reponame"])],
  "getHostOwners": [("hostName", ["hostname"])],
  "getHostOwner": [("hostName", ["hostname"]), ("ownerName", ["ownername"])],
  "getHostOwnerMaintainers": [("hostName", ["hostname"]), ("ownerName", ["ownername"])],
  "getHostAuthors": [("hostName", ["hostname"])],
  "getHostAuthor": [("hostName", ["hostname"]), ("authorName", ["authorname"])],
  "getJob": [("jobId", ["jobid"])],
  ```
- `createJob` needs custom handling (POST with body) — add dispatch or handle via default handler if body passthrough works

### Tests (`tests/commands/test_issues.py`)
- Add tests for all 8 new operations
- Verify `getHostRepositoryIssues` accepts new `pull_request`, `state`, `label` query params

---

## 4. Packages API

### New endpoints
- `GET /packages/critical` — `getCriticalPackagesList` (query only: `page`, `per_page`, date filters, `funding`, `sort`, `order`)
- `POST /packages/bulk_lookup` — `bulkLookupPackages` (body: `repository_urls`, `purls`, `names`, `ecosystem`)
- `GET /registries/{registryName}/packages/{packageName}/versions/{versionNumber}/codemeta` — `getRegistryPackageVersionCodeMeta` (path: `registryName`, `packageName`, `versionNumber`)

### New query parameters on existing endpoints
- `ecosystem` filter on `getRegistries` — auto-discovered
- `prefix`, `postfix` filters on `getRegistryPackages` — auto-discovered
- `sort`, `order` on `getDependencies` — auto-discovered
- `sort` enum values added to many existing operations — auto-discovered (improves validation)

### Handler changes (`handlers/packages.py`)
- Add to `OPERATION_PARAMS`:
  ```python
  "getRegistryPackageVersionCodeMeta": [
      ("registryName", ["registryname"]),
      ("packageName", ["packagename"]),
      ("versionNumber", ["versionnumber"]),
  ],
  ```
- `getCriticalPackagesList` — query-only, should work via default fallback (remaining kwargs become query params)
- `bulkLookupPackages` — POST with body, needs custom handling or body passthrough

### Tests (`tests/commands/test_packages.py`)
- Add test for `get_critical_packages_list`
- Add test for `bulk_lookup_packages`
- Add test for `get_registry_package_version_code_meta`

---

## 5. Repos API

### New endpoints
- `GET /usage/{ecosystem}/{package}/dependent_repositories` — `usagePackageDependentRepositories` (path: `ecosystem`, `package`, query: `page`, `per_page`, `sort`, `order`, `after_id`, `fork`, `archived`, `starred`, `min_stars`)
- `GET /hosts/{hostName}/owners/sponsors_logins` — `getHostOwnerSponsorsLogins` (path: `hostName`)

### Changed endpoints
- `GET /usage/{ecosystem}/{package}/dependencies` — response changed from single object to **array** of `DependencyWithRepository`. Summary also updated: "Get dependencies for a package" (was "Get dependent repositories")
- `GET /usage/{ecosystem}/{package}/dependencies` — new query params: `page`, `per_page`, `after`
- `GET /usage` and `/usage/{ecosystem}/{package}` — new query params: `page`, `per_page`
- `GET /hosts/{hostName}/owners` — new query params: `kind` (enum: user/organization), `has_sponsors_listing`

### Handler changes (`handlers/repos.py`)
- Add to `OPERATION_PARAMS`:
  ```python
  "usagePackageDependentRepositories": [("ecosystem", ["ecosystem"]), ("package", ["package"])],
  "getHostOwnerSponsorsLogins": [("hostName", ["hostname"])],
  ```
- Query params for new endpoints are auto-discovered

### Tests (`tests/commands/test_repos.py`)
- Add test for `usage_package_dependent_repositories`
- Add test for `get_host_owner_sponsors_logins`
- Update existing `usage_package_dependencies` test if response shape expectations changed

---

## 6. Resolve API

### New endpoint
- `GET /registries` — `listRegistries` (no params)

### Handler changes (`handlers/resolve.py`)
- Add `listRegistries` to handlers dict → `self._handle_default`

### Tests (`tests/commands/test_resolve.py`)
- Add test for `list_registries`

---

## 7. MCP Server

No changes needed — the MCP server auto-discovers all operations from specs. The `self.apis` list already includes all 6 affected APIs. New operations will appear as MCP tools automatically.

---

## 8. Schema-only changes (no code impact)

These are response schema additions that don't require code changes:
- `advisories`: new `api_url`, `html_url`, `related_advisories` fields on Advisory; new `RelatedAdvisory`, `Source` schemas
- `commits`: new `Committer` schema
- `issues`: new `OwnerSummary`, `Owner`, `Maintainers`, `AuthorSummary`, `Author`, `Job`, `RepoCount`, `AuthorAssociationCount`, `LabelCount`, `AuthorCount`, `MaintainerCount` schemas
- `packages`: `codemeta_url` field added to `Version` and `VersionWithDependencies` schemas; `sort` enum values formalized
- `repos`: response type fix on `usagePackageDependencies` (single → array)

---

## Summary of files to change

| File | Changes |
|------|---------|
| `handlers/advisories.py` | Add `getSources`, `getSource` |
| `handlers/commits.py` | Add `getHostCommitter` |
| `handlers/issues.py` | Add 8 new operations to `OPERATION_PARAMS` |
| `handlers/packages.py` | Add `getRegistryPackageVersionCodeMeta`, handle `bulkLookupPackages` |
| `handlers/repos.py` | Add `usagePackageDependentRepositories`, `getHostOwnerSponsorsLogins` |
| `handlers/resolve.py` | Add `listRegistries` |
| `tests/commands/test_advisories.py` | Tests for 2 new operations |
| `tests/commands/test_commits.py` | **New file** — tests for `getHostCommitter` |
| `tests/commands/test_issues.py` | Tests for 8 new operations + new query params |
| `tests/commands/test_packages.py` | Tests for 3 new operations |
| `tests/commands/test_repos.py` | Tests for 2 new operations |
| `tests/commands/test_resolve.py` | Test for 1 new operation |
