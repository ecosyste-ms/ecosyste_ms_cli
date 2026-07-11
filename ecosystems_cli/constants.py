"""Constants for the ecosystems CLI."""

# API Configuration
API_BASE_URL_TEMPLATE = "https://{api_name}.ecosyste.ms/api/v1"
DEFAULT_TIMEOUT = 20
DEFAULT_CONTENT_TYPE = "application/json"

# Job polling: wall-clock ceiling (seconds) so a stuck job can't hang the CLI forever.
DEFAULT_MAX_POLL_WAIT = 600

# Supported APIs
SUPPORTED_APIS = [
    "advisories",
]

# Output Formats
OUTPUT_FORMATS = ["table", "json", "tsv", "jsonl"]
DEFAULT_OUTPUT_FORMAT = "table"

# Display Configuration
JSON_THEME = "monokai"
JSON_SYNTAX = "json"
MAX_SELECTED_FIELDS = 2
DEFAULT_TABLE_TITLE = "API Response"
TABLE_HEADER_STYLE = "bold cyan"
EMPTY_RESULTS_MESSAGE = "No results"

# Rich Console Styles
STYLE_BOLD_CYAN = "bold cyan"
STYLE_BOLD_GREEN = "bold green"
STYLE_BOLD_YELLOW = "bold yellow"
STYLE_BOLD_MAGENTA = "bold magenta"
STYLE_CYAN = "cyan"
STYLE_GREEN = "green"
STYLE_YELLOW = "yellow"
STYLE_MAGENTA = "magenta"
STYLE_RED = "red"
STYLE_BOLD_RED = "bold red"
STYLE_BLUE = "blue"

# Table Display Priority Fields
PRIORITY_FIELDS = {
    "advisories": ["uuid", "title", "severity", "published_at", "cvss_score"],
    "archives": ["name", "directory", "contents"],
    "commits": ["sha", "author", "message", "timestamp", "merge"],
    "repos": ["full_name", "name", "description", "stars", "language"],
    "packages": ["name", "platform", "description", "downloads", "language"],
    "summary": ["name", "type", "count", "total", "description"],
    "awesome": ["name", "title", "url", "description", "category"],
    "papers": ["doi", "title", "publication_date", "mentions_count", "openalex_id"],
    "ost": ["id", "url", "category", "language", "score"],
    "parser": ["id", "url", "status", "created_at", "sha256"],
    "resolver": ["id", "package_name", "registry", "status", "created_at"],
    "sbom": ["id", "url", "status", "created_at", "sha256"],
    "licenses": ["id", "url", "status", "created_at", "sha256"],
    "timeline": ["actor", "event_type", "repository", "owner", "payload"],
    "issues": ["number", "title", "state", "user", "created_at"],
    "sponsors": ["login", "has_sponsors_listing", "sponsors_count", "sponsorships_count", "minimum_sponsorship_amount"],
    "opencollective": ["id", "url", "name", "description", "created_at"],
    "docker": ["id", "url", "name", "description", "created_at"],
    "diff": ["id", "url", "name", "description", "created_at"],
    "ruby": ["id", "url", "language", "score", "monthly_downloads"],
}

# Operations Display
OPERATIONS_PANEL_TITLE = "Operations"
OPERATIONS_PANEL_STYLE = "yellow"
AVAILABLE_OPERATIONS_TITLE = "Available Operations"
AVAILABLE_OPERATIONS_STYLE = "blue"
OPERATION_HEADERS = {"operation": "OPERATION", "method": "METHOD", "path": "PATH", "description": "DESCRIPTION"}
DIVIDER_WIDTH_OFFSET = 40
SUMMARY_TRUNCATE_LENGTH = 50

# Error Display
ERROR_PREFIX = "[bold red]Error:[/bold red]"
ERROR_PANEL_STYLE = "red"

# File Patterns
OPENAPI_FILE_EXTENSION = ".openapi.yaml"

# HTTP Configuration
HTTP_METHODS = ["get", "post", "put", "delete", "patch"]

# Value Formatting
EMPTY_DICT_DISPLAY = "{}"
EMPTY_LIST_DISPLAY = "[]"
MAX_INLINE_ITEMS = 3
DICT_TRUNCATE_FORMAT = "{{...}} ({count} items)"
LIST_TRUNCATE_FORMAT = "[...] ({count} items)"

# Separators
DEFAULT_SEPARATOR = "_"

# Error Message Templates
ERROR_API_ONLY = "This method is only available for the {api_name} API"
ERROR_OPERATION_NOT_FOUND = "Operation '{operation_id}' not found in {api_name} API"
