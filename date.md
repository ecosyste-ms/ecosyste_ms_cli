# Date Filtering in Ecosystems CLI

The Ecosystems CLI supports date-based filtering across multiple APIs to help you narrow down results based on when records were created, updated, or published.

## Date Format

All date parameters accept **ISO 8601 date-time format**:

```
YYYY-MM-DDTHH:MM:SSZ
```

**Examples:**
- `2024-01-15T00:00:00Z` - Midnight on January 15, 2024 (UTC)
- `2024-06-30T23:59:59Z` - End of June 30, 2024 (UTC)
- `2024-10-23T12:30:00Z` - October 23, 2024 at 12:30 PM (UTC)

**Simplified formats** (dates without time):
- `2024-01-15` - Often accepted as shorthand for midnight UTC
- `2024-06-30`

## Available Date Parameters

### After Parameters (Filter records after a specific date)

- `--created-after` - Filter by created_at after given time
- `--updated-after` - Filter by updated_at after given time
- `--published-after` - Filter by published_at after given time

### Before Parameters (Filter records before a specific date)

- `--created-before` - Filter by created_at before given time
- `--updated-before` - Filter by updated_at before given time
- `--published-before` - Filter by published_at before given time

## APIs Supporting Date Filtering

### 1. Advisories API

**Supported parameters:** `--created-after`, `--updated-after`

**Examples:**

```bash
# Get advisories created after January 1, 2024
ecosystems advisories get_advisories --created-after "2024-01-01T00:00:00Z"

# Get advisories updated in the last month
ecosystems advisories get_advisories --updated-after "2024-09-23T00:00:00Z"

# Combine date filtering with other filters
ecosystems advisories get_advisories \
  --ecosystem npm \
  --severity HIGH \
  --created-after "2024-01-01T00:00:00Z"

# Filter advisories for a specific package updated recently
ecosystems advisories get_advisories \
  --purl "pkg:npm/lodash" \
  --updated-after "2024-10-01T00:00:00Z"
```

### 2. Packages API

**Supported parameters:** `--created-after`, `--updated-after`, `--created-before`, `--updated-before`, `--published-after`, `--published-before`

**Examples:**

```bash
# Get packages from a registry created in 2024
ecosystems packages get_registry_packages npmjs.org \
  --created-after "2024-01-01T00:00:00Z"

# Get packages updated between two dates
ecosystems packages get_registry_packages npmjs.org \
  --updated-after "2024-01-01T00:00:00Z" \
  --updated-before "2024-06-30T23:59:59Z"

# Get recently published package versions
ecosystems packages get_registry_recent_versions npmjs.org \
  --published-after "2024-10-01T00:00:00Z"

# Get package versions for a specific package published in a date range
ecosystems packages get_registry_package_versions npmjs.org react \
  --published-after "2024-01-01T00:00:00Z" \
  --published-before "2024-12-31T23:59:59Z"

# Get critical packages created recently
ecosystems packages get_registry_packages npmjs.org \
  --critical true \
  --created-after "2024-06-01T00:00:00Z"

# Filter dependent packages by creation date
ecosystems packages get_registry_package_dependent_packages npmjs.org lodash \
  --created-after "2024-01-01T00:00:00Z"
```

### 3. Repos API

**Supported parameters:** `--created-after`, `--updated-after`

**Examples:**

```bash
# Get repositories from GitHub created after a specific date
ecosystems repos get_host_repositories github.com \
  --created-after "2024-01-01T00:00:00Z"

# Get repositories for a specific owner updated recently
ecosystems repos get_host_owner_repositories github.com facebook \
  --updated-after "2024-09-01T00:00:00Z"

# Get repositories for a topic created in the last year
ecosystems repos topic javascript \
  --created-after "2023-10-23T00:00:00Z"

# Combine with other filters
ecosystems repos get_host_repositories github.com \
  --created-after "2024-01-01T00:00:00Z" \
  --fork false \
  --archived false
```

### 4. Issues API

**Supported parameters:** `--created-after`, `--updated-after`

**Examples:**

```bash
# Get issues from a repository created in 2024
ecosystems issues get_host_repository_issues github.com facebook/react \
  --created-after "2024-01-01T00:00:00Z"

# Get recently updated issues
ecosystems issues get_host_repository_issues github.com microsoft/vscode \
  --updated-after "2024-10-01T00:00:00Z"

# Get recent pull requests (issues are both issues and PRs)
ecosystems issues get_host_repository_issues github.com nodejs/node \
  --created-after "2024-09-01T00:00:00Z" \
  --sort created_at \
  --order desc
```

### 5. Docker API

**Supported parameters:** `--created-after`, `--updated-after`, `--published-after`

**Examples:**

```bash
# Get Docker packages created recently
ecosystems docker get_packages \
  --created-after "2024-01-01T00:00:00Z"

# Get package versions published in the last month
ecosystems docker get_package_versions nginx \
  --published-after "2024-09-23T00:00:00Z"

# Get recently updated Docker packages
ecosystems docker get_packages \
  --updated-after "2024-10-01T00:00:00Z"
```

### 6. Dependabot API

**Supported parameters:** `--created-after`, `--updated-after`

**Examples:**

```bash
# Get Dependabot issues created after a specific date
ecosystems dependabot get_host_repository_issues github.com rails/rails \
  --created-after "2024-01-01T00:00:00Z"

# Get repositories with recent Dependabot activity
ecosystems dependabot get_host_repositories github.com \
  --updated-after "2024-09-01T00:00:00Z"
```

### 7. Commits API

**Supported parameters:** `--created-after`, `--updated-after`

**Examples:**

```bash
# Get commit data for repositories created recently
# (Note: Exact endpoints depend on the commits API implementation)
# Check with: ecosystems commits --help
```

### 8. Resolve API (Special Case)

**Special parameter:** `--before`

The resolve API uses a special `--before` parameter to resolve dependencies using only versions published before a specific date. This is useful for reproducing historical dependency trees.

**Examples:**

```bash
# Resolve dependencies as they existed on January 1, 2024
ecosystems resolve create_job react npmjs.org \
  --before "2024-01-01T00:00:00Z"

# Resolve a specific version with historical dependencies
ecosystems resolve create_job react npmjs.org \
  --version "^18.0.0" \
  --before "2024-06-30T23:59:59Z"

# Poll for job completion
ecosystems resolve create_job lodash npmjs.org \
  --before "2023-12-31T23:59:59Z" \
  --polling-interval 2
```

## Combining Date Filters

You can combine multiple date parameters to create date ranges:

```bash
# Get packages created in Q1 2024
ecosystems packages get_registry_packages npmjs.org \
  --created-after "2024-01-01T00:00:00Z" \
  --created-before "2024-04-01T00:00:00Z"

# Get packages updated in a specific month
ecosystems packages get_registry_packages npmjs.org \
  --updated-after "2024-10-01T00:00:00Z" \
  --updated-before "2024-10-31T23:59:59Z"

# Get versions published in a specific time range
ecosystems packages get_registry_package_versions npmjs.org react \
  --published-after "2024-01-01T00:00:00Z" \
  --published-before "2024-12-31T23:59:59Z"
```

## Combining with Other Filters

Date filters work seamlessly with other filtering options:

```bash
# Security advisories for NPM packages created recently
ecosystems advisories get_advisories \
  --ecosystem npm \
  --severity CRITICAL \
  --created-after "2024-09-01T00:00:00Z"

# Non-archived, non-fork repositories updated in the last month
ecosystems repos get_host_repositories github.com \
  --updated-after "2024-09-23T00:00:00Z" \
  --fork false \
  --archived false

# Critical packages from a specific registry created this year
ecosystems packages get_registry_packages npmjs.org \
  --critical true \
  --created-after "2024-01-01T00:00:00Z"
```

## Combining with Sorting and Pagination

```bash
# Get the 50 most recently created packages
ecosystems packages get_registry_packages npmjs.org \
  --created-after "2024-01-01T00:00:00Z" \
  --sort created_at \
  --order desc \
  --per-page 50

# Paginate through updated repositories
ecosystems repos get_host_repositories github.com \
  --updated-after "2024-09-01T00:00:00Z" \
  --page 2 \
  --per-page 100
```

## Output Formats with Date Filtering

Date filtering works with all output formats:

```bash
# JSON output for programmatic processing
ecosystems advisories get_advisories \
  --created-after "2024-01-01T00:00:00Z" \
  --format json

# TSV output for spreadsheet import
ecosystems packages get_registry_packages npmjs.org \
  --created-after "2024-01-01T00:00:00Z" \
  --format tsv

# JSONL output for streaming processing
ecosystems repos get_host_repositories github.com \
  --updated-after "2024-09-01T00:00:00Z" \
  --format jsonl
```

## Common Use Cases

### 1. Monitor Recent Security Advisories

```bash
# Get security advisories from the last 7 days
ecosystems advisories get_advisories \
  --created-after "2024-10-16T00:00:00Z" \
  --severity HIGH \
  --format json
```

### 2. Track New Package Releases

```bash
# Get new versions published today
ecosystems packages get_registry_recent_versions npmjs.org \
  --published-after "2024-10-23T00:00:00Z" \
  --format table
```

### 3. Analyze Repository Activity

```bash
# Find active repositories (updated in last 30 days)
ecosystems repos get_host_repositories github.com \
  --updated-after "2024-09-23T00:00:00Z" \
  --archived false
```

### 4. Historical Dependency Resolution

```bash
# Reproduce a build from 6 months ago
ecosystems resolve create_job express npmjs.org \
  --before "2024-04-23T00:00:00Z" \
  --polling-interval 2
```

### 5. Audit Package Changes in a Time Period

```bash
# Get all package updates in Q3 2024
ecosystems packages get_registry_packages npmjs.org \
  --updated-after "2024-07-01T00:00:00Z" \
  --updated-before "2024-09-30T23:59:59Z" \
  --format jsonl
```

## Tips and Best Practices

1. **Use UTC timezone**: All dates should be in UTC (denoted by the `Z` suffix)

2. **Be specific with time ranges**: Combining `*_after` and `*_before` parameters gives you precise control

3. **Consider API rate limits**: Filtering by date can help reduce the number of results and avoid rate limiting

4. **Combine with pagination**: For large date ranges, use `--page` and `--per-page` to manage results

5. **Use appropriate formats for automation**: Use `--format json` or `--format jsonl` when processing results programmatically

6. **Sort results**: Combine date filters with `--sort` and `--order` for consistent, predictable results

## Error Handling

### Invalid Date Format

If you provide an invalid date format, the API may reject the request:

```bash
# Invalid - wrong format
ecosystems advisories get_advisories --created-after "01/15/2024"

# Valid - ISO 8601 format
ecosystems advisories get_advisories --created-after "2024-01-15T00:00:00Z"
```

### Logical Date Ranges

Make sure `*_before` dates come after `*_after` dates:

```bash
# Invalid - before date is earlier than after date
ecosystems packages get_registry_packages npmjs.org \
  --created-after "2024-06-01T00:00:00Z" \
  --created-before "2024-01-01T00:00:00Z"

# Valid - proper date range
ecosystems packages get_registry_packages npmjs.org \
  --created-after "2024-01-01T00:00:00Z" \
  --created-before "2024-06-01T00:00:00Z"
```

## Reference Summary

| API | created_after | updated_after | published_after | created_before | updated_before | published_before |
|-----|---------------|---------------|-----------------|----------------|----------------|------------------|
| advisories | ✓ | ✓ | | | | |
| packages | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| repos | ✓ | ✓ | | | | |
| issues | ✓ | ✓ | | | | |
| docker | ✓ | ✓ | ✓ | | | |
| dependabot | ✓ | ✓ | | | | |
| commits | ✓ | ✓ | | | | |
| resolve | special `--before` parameter | | | | | |

## Further Reading

- [PURL Support](purl.md) - Package URL support in the CLI
- [Development Guide](docs/DEVELOPMENT.md) - Contributing to the CLI
- [Ecosyste.ms API Documentation](https://ecosyste.ms/api) - Official API docs
