from rich.console import Console

from ecosystems_cli.helpers.print_output import (
    TableFieldSelector,
    _format_json,
    _format_jsonl,
    _format_table,
    _format_tsv,
    _select_table_fields,
    print_output,
)


def test_format_json_with_dict():
    """Test that _format_json returns proper JSON syntax for dict data."""
    from io import StringIO

    data = {"foo": "bar", "baz": 1}
    console = Console(file=StringIO(), force_terminal=True, color_system=None, width=80)
    _format_json(data, console)

    # This test will fail initially since _format_json doesn't exist yet


def test_format_tsv_with_list():
    """Test that _format_tsv properly formats list data as TSV."""
    from io import StringIO

    data = [{"foo": "bar", "baz": 1}, {"foo": "qux", "baz": 2}]
    output = StringIO()
    console = Console(file=output, force_terminal=True, color_system=None, width=80)
    _format_tsv(data, console)

    # This test will fail initially since _format_tsv doesn't exist yet


def test_format_jsonl_with_list():
    """Test that _format_jsonl properly formats list data as JSONL."""
    from io import StringIO

    data = [{"foo": "bar"}, {"foo": "baz"}]
    output = StringIO()
    console = Console(file=output, force_terminal=True, color_system=None, width=80)
    _format_jsonl(data, console)

    # This test will fail initially since _format_jsonl doesn't exist yet


def test_print_output_json(capsys):
    data = {"foo": "bar", "baz": 1}
    console = Console(file=None, force_terminal=True, color_system=None, width=80)
    print_output(data, format_type="json", console=console)
    # No assertion: just ensure no exceptions and output is printed


def test_print_output_tsv(capsys):
    data = [{"foo": "bar", "baz": 1}, {"foo": "qux", "baz": 2}]
    console = Console(file=None, force_terminal=True, color_system=None, width=80)
    print_output(data, format_type="tsv", console=console)


def test_print_output_jsonl(capsys):
    data = [{"foo": "bar"}, {"foo": "baz"}]
    console = Console(file=None, force_terminal=True, color_system=None, width=80)
    print_output(data, format_type="jsonl", console=console)


def test_jsonl_long_records_not_wrapped(capsys):
    """Each JSONL record must stay on one physical line so piped output stays valid."""
    import json

    data = [{"description": "x" * 500, "id": 1}, {"description": "y" * 500, "id": 2}]
    print_output(data, format_type="jsonl", console=Console(width=80))

    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(lines) == 2
    for line in lines:
        json.loads(line)  # raises if a record was split across lines


def test_tsv_long_rows_not_wrapped(capsys):
    """TSV header and rows must not be wrapped when piped (Console width 80)."""
    data = [{"name": "a" * 300, "id": 1}, {"name": "b" * 300, "id": 2}]
    print_output(data, format_type="tsv", console=Console(width=80))

    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(lines) == 3  # header + 2 rows, none wrapped
    assert lines[0].split("\t") == ["name", "id"]


def test_select_table_fields_with_common_fields():
    """Test that _select_table_fields selects appropriate fields."""
    data = [{"id": 1, "name": "foo", "extra": "data"}, {"id": 2, "name": "bar", "extra": "more"}]
    headers = list(data[0].keys())

    selected = _select_table_fields(headers)

    # Should prioritize common fields like id and name
    assert "id" in selected
    assert "name" in selected
    # This test will fail initially since _select_table_fields doesn't exist yet


def test_format_table_with_list():
    """Test that _format_table properly formats list data as table."""
    from io import StringIO

    data = [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
    output = StringIO()
    console = Console(file=output, force_terminal=True, color_system=None, width=80)
    _format_table(data, console)

    # This test will fail initially since _format_table doesn't exist yet


def test_print_output_table(capsys):
    data = [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
    console = Console(file=None, force_terminal=True, color_system=None, width=80)
    print_output(data, format_type="table", console=console)


class TestTableFieldSelector:
    """Test the TableFieldSelector class."""

    def test_init(self):
        """Test TableFieldSelector initialization."""
        priority_fields = {"repos": ["full_name", "name"]}
        selector = TableFieldSelector(priority_fields, max_selected_fields=3)

        assert selector.max_selected_fields == 3
        assert "repos" in selector.priority_fields
        assert "common" in selector.priority_fields
        assert selector.priority_fields["common"] == ["id", "name", "title"]

    def test_detect_api_type_with_matching_fields(self):
        """Test API type detection when fields match."""
        priority_fields = {"repos": ["full_name", "stars"], "packages": ["platform", "downloads"]}
        selector = TableFieldSelector(priority_fields)

        # Test repos detection
        headers = ["full_name", "description", "language"]
        assert selector._detect_api_type(headers) == "repos"

        # Test packages detection
        headers = ["name", "platform", "version"]
        assert selector._detect_api_type(headers) == "packages"

    def test_detect_api_type_defaults_to_common(self):
        """Test API type detection defaults to common."""
        priority_fields = {"repos": ["full_name", "stars"]}
        selector = TableFieldSelector(priority_fields)

        headers = ["id", "name", "description"]
        assert selector._detect_api_type(headers) == "common"

    def test_select_fields_api_specific(self):
        """Test field selection for API-specific fields."""
        priority_fields = {
            "repos": ["full_name", "stars", "language"],
        }
        selector = TableFieldSelector(priority_fields, max_selected_fields=2)

        headers = ["full_name", "stars", "language", "description"]
        selected = selector.select_fields(headers)

        assert len(selected) == 2
        assert "full_name" in selected
        assert "stars" in selected

    def test_select_fields_falls_back_to_common(self):
        """Test field selection falls back to common fields."""
        priority_fields = {"repos": ["not_present", "also_not_present"]}
        selector = TableFieldSelector(priority_fields, max_selected_fields=2)

        headers = ["id", "name", "description"]
        selected = selector.select_fields(headers)

        assert len(selected) == 2
        assert "id" in selected
        assert "name" in selected

    def test_select_fields_uses_remaining_headers(self):
        """Test field selection uses remaining headers when needed."""
        priority_fields = {}
        selector = TableFieldSelector(priority_fields, max_selected_fields=2)

        headers = ["custom1", "custom2", "custom3"]
        selected = selector.select_fields(headers)

        assert len(selected) == 2
        assert "custom1" in selected
        assert "custom2" in selected

    def test_ensure_minimum_fields(self):
        """Test ensuring minimum of 2 fields."""
        priority_fields = {"repos": ["full_name"]}
        selector = TableFieldSelector(priority_fields, max_selected_fields=2)

        headers = ["full_name", "other_field"]
        selected = selector.select_fields(headers)

        assert len(selected) == 2
        assert "full_name" in selected
        assert "other_field" in selected

    def test_no_duplicate_fields(self):
        """Test that fields are not duplicated."""
        priority_fields = {"repos": ["name"], "common": ["name", "id"]}
        selector = TableFieldSelector(priority_fields, max_selected_fields=3)

        headers = ["name", "id", "description"]
        selected = selector.select_fields(headers)

        assert len(selected) == len(set(selected))  # No duplicates
        assert "name" in selected
        assert "id" in selected

    def test_empty_headers(self):
        """Test behavior with empty headers."""
        priority_fields = {"repos": ["full_name"]}
        selector = TableFieldSelector(priority_fields)

        selected = selector.select_fields([])
        assert selected == []

    def test_select_table_fields_uses_selector(self):
        """Test that _select_table_fields uses TableFieldSelector."""
        headers = ["full_name", "stars", "language", "description"]
        selected = _select_table_fields(headers)

        assert isinstance(selected, list)
        assert len(selected) >= 1
        assert len(selected) <= 2
