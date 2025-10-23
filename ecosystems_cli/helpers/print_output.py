import json
from datetime import datetime
from typing import Any, List

from rich.console import Console

from ecosystems_cli.constants import (
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_TABLE_TITLE,
    MAX_SELECTED_FIELDS,
    PRIORITY_FIELDS,
    TABLE_HEADER_STYLE,
)
from ecosystems_cli.helpers.flatten_dict import flatten_dict
from ecosystems_cli.helpers.format_value import format_value


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class TableFieldSelector:
    """Selects appropriate fields for table display based on API type and priorities."""

    def __init__(self, priority_fields: dict, max_selected_fields: int = 2):
        self.priority_fields = priority_fields.copy()
        self.priority_fields["common"] = ["id", "name", "title"]
        self.max_selected_fields = max_selected_fields

    def select_fields(self, headers: List[str]) -> List[str]:
        """Select which fields to display in the table."""
        api_type = self._detect_api_type(headers)
        selected_fields = []

        # Apply selection strategies in order
        strategies = [
            lambda: self._select_from_priority(headers, selected_fields, api_type),
            lambda: self._select_from_common(headers, selected_fields),
            lambda: self._select_remaining(headers, selected_fields),
            lambda: self._ensure_minimum(headers, selected_fields),
        ]

        for strategy in strategies:
            strategy()
            if len(selected_fields) >= self.max_selected_fields:
                break

        return selected_fields

    def _detect_api_type(self, headers: List[str]) -> str:
        """Detect the API type based on available headers."""
        for api_name, fields in self.priority_fields.items():
            if api_name != "common" and any(field in headers for field in fields):
                return api_name
        return "common"

    def _select_from_priority(self, headers: List[str], selected: List[str], api_type: str) -> None:
        """Select fields from API-specific priority list."""
        self._add_fields(headers, selected, self.priority_fields[api_type])

    def _select_from_common(self, headers: List[str], selected: List[str]) -> None:
        """Select fields from common priority list if needed."""
        if len(selected) < 2:
            self._add_fields(headers, selected, self.priority_fields["common"])

    def _select_remaining(self, headers: List[str], selected: List[str]) -> None:
        """Select any remaining headers if still needed."""
        if len(selected) < 2:
            self._add_fields(headers, selected, headers)

    def _add_fields(self, headers: List[str], selected: List[str], candidates: List[str]) -> None:
        """Add fields from candidates to selected list."""
        for field in candidates:
            if field in headers and field not in selected and len(selected) < self.max_selected_fields:
                selected.append(field)

    def _ensure_minimum(self, headers: List[str], selected: List[str]) -> None:
        """Ensure we have at least 2 fields if possible."""
        if len(selected) == 1 and headers:
            for field in headers:
                if field not in selected:
                    selected.append(field)
                    break


def _format_json(data: Any, console: Console) -> None:
    """Format and print data as JSON."""
    json_str = json.dumps(data, cls=DateTimeEncoder)
    # Use plain print to avoid Rich formatting
    print(json_str)


def _format_tsv(data: Any, console: Console) -> None:
    """Format and print data as TSV (Tab-Separated Values)."""
    if isinstance(data, list) and len(data) > 0:
        headers = list(data[0].keys())
        console.print("\t".join(headers))
        for item in data:
            console.print("\t".join(str(format_value(item.get(h, ""))) for h in headers))
    else:
        flat_data = flatten_dict(data) if isinstance(data, dict) else {"value": str(data)}
        console.print("\t".join(flat_data.keys()))
        console.print("\t".join(str(v) for v in flat_data.values()))


def _format_jsonl(data: Any, console: Console) -> None:
    """Format and print data as JSONL (JSON Lines)."""
    if isinstance(data, list):
        for item in data:
            console.print(json.dumps(item, cls=DateTimeEncoder))
    else:
        console.print(json.dumps(data, cls=DateTimeEncoder))


def _select_table_fields(headers: list[str]) -> list[str]:
    """Select which fields to display in the table based on priority."""
    selector = TableFieldSelector(PRIORITY_FIELDS, MAX_SELECTED_FIELDS)
    return selector.select_fields(headers)


def _format_table(data: Any, console: Console) -> None:
    """Format and print data as a rich table."""
    from rich.table import Table

    if isinstance(data, list) and len(data) > 0:
        # Select fields to display
        headers = list(data[0].keys())
        selected_headers = _select_table_fields(headers)

        # Create and populate table
        table = Table(title=DEFAULT_TABLE_TITLE, show_header=True, header_style=TABLE_HEADER_STYLE)
        for header in selected_headers:
            table.add_column(header.capitalize())

        for item in data:
            table.add_row(*[format_value(item.get(h, "")) for h in selected_headers])

        console.print(table)
    elif isinstance(data, dict):
        # Create a key-value table for dict data
        table = Table(title=DEFAULT_TABLE_TITLE, show_header=True, header_style=TABLE_HEADER_STYLE)
        table.add_column("Field")
        table.add_column("Value")

        for key, value in data.items():
            table.add_row(key, format_value(value))

        console.print(table)
    else:
        # Fall back to JSON for other data types
        _format_json(data, console)


# Formatter registry
_FORMATTERS = {
    "json": _format_json,
    "tsv": _format_tsv,
    "jsonl": _format_jsonl,
    "table": _format_table,
}


def print_output(data: Any, format_type: str = DEFAULT_OUTPUT_FORMAT, console: Console = None):
    """Print data in the specified format.

    Args:
        data: The data to print
        format_type: One of 'table', 'json', 'tsv', or 'jsonl'
        console: Optional rich Console instance
    """
    if console is None:
        from rich.console import Console

        console = Console()

    # Get the formatter function from the registry
    formatter = _FORMATTERS.get(format_type, _format_table)
    formatter(data, console)
