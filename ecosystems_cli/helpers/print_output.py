import json
import os
import sys
from datetime import datetime
from typing import Any, List

from rich.console import Console

from ecosystems_cli.constants import (
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_TABLE_TITLE,
    EMPTY_RESULTS_MESSAGE,
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
            # UTC datetimes serialize with the API's original "Z" designator
            # rather than "+00:00", staying close to the upstream payload.
            return obj.isoformat().replace("+00:00", "Z")
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


def exit_on_broken_pipe():
    """Exit quietly after a BrokenPipeError from writing to stdout.

    A downstream consumer closing the pipe early (``ecosystems ... | head``)
    is not an error: exit with the conventional SIGPIPE status (128 + 13)
    instead of reporting "Unexpected error: [Errno 32] Broken pipe". stdout
    is redirected to devnull first so the interpreter's shutdown flush does
    not raise a second EPIPE.
    """
    # Only touch the file descriptor when stdout is the real process stdout;
    # test runners (pytest capture, CliRunner) swap sys.stdout for wrappers
    # whose descriptors must not be clobbered.
    if sys.stdout is sys.__stdout__:
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
        except (OSError, ValueError):
            pass
    sys.exit(141)


# Machine-readable formats use the builtin print() rather than console.print().
# A Rich Console wraps long lines at its width (80 when stdout is not a TTY, i.e.
# when piped), which would split a single record across physical lines and
# corrupt JSON/JSONL/TSV consumers. Plain print() emits each record verbatim.


def _format_json(data: Any, console: Console) -> None:
    """Format and print data as JSON."""
    print(json.dumps(data, cls=DateTimeEncoder))


def _escape_tsv(value: Any) -> str:
    """Escape tabs and newlines so each TSV record stays on one physical line.

    Field values (e.g. advisory descriptions) can embed tabs and newlines,
    which would fragment a record across lines and break column counts.
    Backslash is escaped first so the encoding stays unambiguous (the same
    convention as e.g. Postgres COPY: \\t, \\n, \\r).
    """
    return str(value).replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def _tsv_cell(value: Any) -> str:
    """Render one TSV cell: TSV conventions instead of Python literals.

    Nulls become empty cells and booleans lowercase true/false, so TSV
    consumers do not have to special-case str(None)/str(True). Everything
    else goes through the shared format_value (which keeps Python-style
    rendering for the human-facing table output).
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return format_value(value)


def _format_tsv(data: Any, console: Console) -> None:
    """Format and print data as TSV (Tab-Separated Values)."""
    if isinstance(data, list):
        if len(data) == 0:
            # An empty result set has no records to derive columns from;
            # emit nothing rather than a fabricated "value/[]" row.
            return
        if all(isinstance(item, dict) for item in data):
            headers = list(data[0].keys())
            print("\t".join(_escape_tsv(h) for h in headers))
            for item in data:
                print("\t".join(_escape_tsv(_tsv_cell(item.get(h, ""))) for h in headers))
        else:
            # A list of scalars (e.g. package names) has no columns; emit one
            # value per line under a single header.
            print("value")
            for item in data:
                print(_escape_tsv(_tsv_cell(item)))
    else:
        flat_data = flatten_dict(data) if isinstance(data, dict) else {"value": str(data)}
        print("\t".join(_escape_tsv(k) for k in flat_data.keys()))
        print("\t".join(_escape_tsv(_tsv_cell(v)) for v in flat_data.values()))


def _format_jsonl(data: Any, console: Console) -> None:
    """Format and print data as JSONL (JSON Lines)."""
    if isinstance(data, list):
        for item in data:
            print(json.dumps(item, cls=DateTimeEncoder))
    else:
        print(json.dumps(data, cls=DateTimeEncoder))


def _select_table_fields(headers: list[str]) -> list[str]:
    """Select which fields to display in the table based on priority."""
    selector = TableFieldSelector(PRIORITY_FIELDS, MAX_SELECTED_FIELDS)
    return selector.select_fields(headers)


def _format_table(data: Any, console: Console) -> None:
    """Format and print data as a rich table."""
    from rich.table import Table

    if isinstance(data, list) and len(data) > 0 and all(isinstance(item, dict) for item in data):
        # Select fields to display
        headers = list(data[0].keys())
        selected_headers = _select_table_fields(headers)

        # Create and populate table. overflow="fold" wraps long values (URLs,
        # ids) onto extra lines instead of truncating them with an ellipsis.
        table = Table(title=DEFAULT_TABLE_TITLE, show_header=True, header_style=TABLE_HEADER_STYLE)
        for header in selected_headers:
            table.add_column(header.capitalize(), overflow="fold")

        for item in data:
            table.add_row(*[format_value(item.get(h, "")) for h in selected_headers])

        console.print(table)
    elif isinstance(data, list) and len(data) > 0:
        # A list of scalars (e.g. package names) has no columns; render each
        # value in a single column instead of assuming dict-shaped rows.
        table = Table(title=DEFAULT_TABLE_TITLE, show_header=True, header_style=TABLE_HEADER_STYLE)
        table.add_column("Value", overflow="fold")
        for item in data:
            table.add_row(format_value(item))
        console.print(table)
    elif isinstance(data, list):
        # An empty result set: say so instead of printing a bare "[]".
        console.print(EMPTY_RESULTS_MESSAGE)
    elif isinstance(data, dict):
        # Create a key-value table for dict data. Values must fold rather
        # than truncate: a create_job response's location URL carries the job
        # id needed for get_job, which an ellipsis would destroy.
        table = Table(title=DEFAULT_TABLE_TITLE, show_header=True, header_style=TABLE_HEADER_STYLE)
        table.add_column("Field")
        table.add_column("Value", overflow="fold")

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
