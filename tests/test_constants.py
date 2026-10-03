"""Tests for constants module."""

from ecosystems_cli import constants


class TestAPIConfiguration:
    """Test API configuration constants."""

    def test_api_base_url_template(self):
        """Test API base URL template format."""
        assert constants.API_BASE_URL_TEMPLATE == "https://{api_name}.ecosyste.ms/api/v1"
        # Test that it's a valid format string
        result = constants.API_BASE_URL_TEMPLATE.format(api_name="test")
        assert result == "https://test.ecosyste.ms/api/v1"

    def test_default_timeout(self):
        """Test default timeout value."""
        assert constants.DEFAULT_TIMEOUT == 20
        assert isinstance(constants.DEFAULT_TIMEOUT, int)
        assert constants.DEFAULT_TIMEOUT > 0

    def test_default_content_type(self):
        """Test default content type."""
        assert constants.DEFAULT_CONTENT_TYPE == "application/json"
        assert isinstance(constants.DEFAULT_CONTENT_TYPE, str)

    def test_supported_apis(self):
        """Test supported APIs list."""
        expected_apis = [
            "advisories",
        ]
        assert constants.SUPPORTED_APIS == expected_apis
        assert isinstance(constants.SUPPORTED_APIS, list)
        assert len(constants.SUPPORTED_APIS) == 1
        assert all(isinstance(api, str) for api in constants.SUPPORTED_APIS)


class TestOutputFormats:
    """Test output format constants."""

    def test_output_formats(self):
        """Test available output formats."""
        assert constants.OUTPUT_FORMATS == ["table", "json", "tsv", "jsonl"]
        assert isinstance(constants.OUTPUT_FORMATS, list)
        assert len(constants.OUTPUT_FORMATS) == 4

    def test_default_output_format(self):
        """Test default output format."""
        assert constants.DEFAULT_OUTPUT_FORMAT == "table"
        assert constants.DEFAULT_OUTPUT_FORMAT in constants.OUTPUT_FORMATS


class TestDisplayConfiguration:
    """Test display configuration constants."""

    def test_json_display_settings(self):
        """Test JSON display settings."""
        assert constants.JSON_THEME == "monokai"
        assert constants.JSON_SYNTAX == "json"

    def test_table_display_settings(self):
        """Test table display settings."""
        assert constants.MAX_SELECTED_FIELDS == 2
        assert isinstance(constants.MAX_SELECTED_FIELDS, int)
        assert constants.DEFAULT_TABLE_TITLE == "API Response"
        assert constants.TABLE_HEADER_STYLE == "bold cyan"

    def test_style_constants(self):
        """Test Rich console style constants."""
        styles = [
            ("STYLE_BOLD_CYAN", "bold cyan"),
            ("STYLE_BOLD_GREEN", "bold green"),
            ("STYLE_BOLD_YELLOW", "bold yellow"),
            ("STYLE_BOLD_MAGENTA", "bold magenta"),
            ("STYLE_CYAN", "cyan"),
            ("STYLE_GREEN", "green"),
            ("STYLE_YELLOW", "yellow"),
            ("STYLE_MAGENTA", "magenta"),
            ("STYLE_RED", "red"),
            ("STYLE_BOLD_RED", "bold red"),
            ("STYLE_BLUE", "blue"),
        ]
        for attr_name, expected_value in styles:
            assert hasattr(constants, attr_name)
            assert getattr(constants, attr_name) == expected_value

    def test_priority_fields(self):
        """Test priority fields dictionary."""
        assert isinstance(constants.PRIORITY_FIELDS, dict)
        expected_keys = {
            "advisories",
            "archives",
            "commits",
            "repos",
            "packages",
            "summary",
            "awesome",
            "papers",
            "ost",
            "parser",
            "resolver",
            "sbom",
            "licenses",
            "timeline",
            "issues",
            "sponsors",
            "opencollective",
            "docker",
            "diff",
            "ruby",
        }
        assert set(constants.PRIORITY_FIELDS.keys()) == expected_keys

        # Check each API has appropriate priority fields
        assert constants.PRIORITY_FIELDS["advisories"] == ["uuid", "title", "severity", "published_at", "cvss_score"]
        assert constants.PRIORITY_FIELDS["archives"] == ["name", "directory", "contents"]
        assert constants.PRIORITY_FIELDS["repos"] == ["full_name", "name", "description", "stars", "language"]
        assert constants.PRIORITY_FIELDS["packages"] == ["name", "platform", "description", "downloads", "language"]
        assert constants.PRIORITY_FIELDS["summary"] == ["name", "type", "count", "total", "description"]
        assert constants.PRIORITY_FIELDS["awesome"] == ["name", "slug", "url", "category", "language"]
        assert constants.PRIORITY_FIELDS["ost"] == ["id", "url", "category", "language", "score"]
        assert constants.PRIORITY_FIELDS["papers"] == ["doi", "title", "publication_date", "mentions_count", "openalex_id"]
        assert constants.PRIORITY_FIELDS["parser"] == ["id", "url", "status", "created_at", "sha256"]
        assert constants.PRIORITY_FIELDS["resolver"] == ["id", "package_name", "registry", "status", "created_at"]
        assert constants.PRIORITY_FIELDS["sbom"] == ["id", "url", "status", "created_at", "sha256"]
        assert constants.PRIORITY_FIELDS["licenses"] == ["id", "url", "status", "created_at", "sha256"]
        assert constants.PRIORITY_FIELDS["timeline"] == ["actor", "event_type", "repository", "owner", "payload"]
        assert constants.PRIORITY_FIELDS["sbom"] == ["id", "url", "status", "created_at", "sha256"]
        assert constants.PRIORITY_FIELDS["issues"] == ["number", "title", "state", "user", "created_at"]
        assert constants.PRIORITY_FIELDS["sponsors"] == [
            "login",
            "has_sponsors_listing",
            "sponsors_count",
            "sponsorships_count",
            "minimum_sponsorship_amount",
        ]
        assert constants.PRIORITY_FIELDS["ruby"] == ["id", "url", "language", "score", "monthly_downloads"]


class TestOperationsDisplay:
    """Test operations display constants."""

    def test_panel_settings(self):
        """Test panel title and style settings."""
        assert constants.OPERATIONS_PANEL_TITLE == "Operations"
        assert constants.OPERATIONS_PANEL_STYLE == "yellow"
        assert constants.AVAILABLE_OPERATIONS_TITLE == "Available Operations"
        assert constants.AVAILABLE_OPERATIONS_STYLE == "blue"

    def test_operation_headers(self):
        """Test operation header constants."""
        assert isinstance(constants.OPERATION_HEADERS, dict)
        expected_headers = {
            "operation": "OPERATION",
            "method": "METHOD",
            "path": "PATH",
            "description": "DESCRIPTION",
        }
        assert constants.OPERATION_HEADERS == expected_headers

    def test_formatting_settings(self):
        """Test formatting settings."""
        assert constants.DIVIDER_WIDTH_OFFSET == 40
        assert isinstance(constants.DIVIDER_WIDTH_OFFSET, int)
        assert constants.SUMMARY_TRUNCATE_LENGTH == 50
        assert isinstance(constants.SUMMARY_TRUNCATE_LENGTH, int)


class TestErrorDisplay:
    """Test error display constants."""

    def test_error_settings(self):
        """Test error display settings."""
        assert constants.ERROR_PREFIX == "[bold red]Error:[/bold red]"
        assert constants.ERROR_PANEL_STYLE == "red"


class TestFilePatterns:
    """Test file pattern constants."""

    def test_file_patterns(self):
        """Test file pattern settings."""
        assert constants.OPENAPI_FILE_EXTENSION == ".openapi.yaml"


class TestHTTPConfiguration:
    """Test HTTP configuration constants."""

    def test_http_methods(self):
        """Test HTTP methods list."""
        assert constants.HTTP_METHODS == ["get", "post", "put", "delete", "patch"]
        assert isinstance(constants.HTTP_METHODS, list)
        assert all(isinstance(method, str) for method in constants.HTTP_METHODS)
        assert all(method.islower() for method in constants.HTTP_METHODS)


class TestValueFormatting:
    """Test value formatting constants."""

    def test_empty_displays(self):
        """Test empty collection display strings."""
        assert constants.EMPTY_DICT_DISPLAY == "{}"
        assert constants.EMPTY_LIST_DISPLAY == "[]"

    def test_truncation_settings(self):
        """Test truncation settings."""
        assert constants.MAX_INLINE_ITEMS == 3
        assert isinstance(constants.MAX_INLINE_ITEMS, int)
        assert constants.DICT_TRUNCATE_FORMAT == "{{...}} ({count} items)"
        assert constants.LIST_TRUNCATE_FORMAT == "[...] ({count} items)"

        # Test format strings work correctly
        assert constants.DICT_TRUNCATE_FORMAT.format(count=5) == "{...} (5 items)"
        assert constants.LIST_TRUNCATE_FORMAT.format(count=10) == "[...] (10 items)"


class TestSeparators:
    """Test separator constants."""

    def test_default_separator(self):
        """Test default separator."""
        assert constants.DEFAULT_SEPARATOR == "_"
        assert isinstance(constants.DEFAULT_SEPARATOR, str)
        assert len(constants.DEFAULT_SEPARATOR) == 1


class TestErrorMessages:
    """Test error message templates."""

    def test_error_templates(self):
        """Test error message templates."""
        assert constants.ERROR_API_ONLY == "This method is only available for the {api_name} API"
        assert constants.ERROR_OPERATION_NOT_FOUND == "Operation '{operation_id}' not found in {api_name} API"

        # Test that they're valid format strings
        api_only_msg = constants.ERROR_API_ONLY.format(api_name="test")
        assert api_only_msg == "This method is only available for the test API"

        op_not_found_msg = constants.ERROR_OPERATION_NOT_FOUND.format(operation_id="testOp", api_name="test")
        assert op_not_found_msg == "Operation 'testOp' not found in test API"


class TestConstantsCompleteness:
    """Test that all expected constants are defined."""

    def test_all_constants_defined(self):
        """Test that all documented constants exist."""
        expected_constants = [
            # API Configuration
            "API_BASE_URL_TEMPLATE",
            "DEFAULT_TIMEOUT",
            "DEFAULT_CONTENT_TYPE",
            "SUPPORTED_APIS",
            # Output Formats
            "OUTPUT_FORMATS",
            "DEFAULT_OUTPUT_FORMAT",
            # Display Configuration
            "JSON_THEME",
            "JSON_SYNTAX",
            "MAX_SELECTED_FIELDS",
            "DEFAULT_TABLE_TITLE",
            "TABLE_HEADER_STYLE",
            "PRIORITY_FIELDS",
            # Styles
            "STYLE_BOLD_CYAN",
            "STYLE_BOLD_GREEN",
            "STYLE_BOLD_YELLOW",
            "STYLE_BOLD_MAGENTA",
            "STYLE_CYAN",
            "STYLE_GREEN",
            "STYLE_YELLOW",
            "STYLE_MAGENTA",
            "STYLE_RED",
            "STYLE_BOLD_RED",
            "STYLE_BLUE",
            # Operations Display
            "OPERATIONS_PANEL_TITLE",
            "OPERATIONS_PANEL_STYLE",
            "AVAILABLE_OPERATIONS_TITLE",
            "AVAILABLE_OPERATIONS_STYLE",
            "OPERATION_HEADERS",
            "DIVIDER_WIDTH_OFFSET",
            "SUMMARY_TRUNCATE_LENGTH",
            # Error Display
            "ERROR_PREFIX",
            "ERROR_PANEL_STYLE",
            # File Patterns
            "OPENAPI_FILE_EXTENSION",
            # HTTP Configuration
            "HTTP_METHODS",
            # Value Formatting
            "EMPTY_DICT_DISPLAY",
            "EMPTY_LIST_DISPLAY",
            "MAX_INLINE_ITEMS",
            "DICT_TRUNCATE_FORMAT",
            "LIST_TRUNCATE_FORMAT",
            # Separators
            "DEFAULT_SEPARATOR",
            # Error Messages
            "ERROR_API_ONLY",
            "ERROR_OPERATION_NOT_FOUND",
        ]

        for constant_name in expected_constants:
            assert hasattr(constants, constant_name), f"Missing constant: {constant_name}"

    def test_no_unexpected_private_constants(self):
        """Test that there are no unexpected private constants."""
        # All public constants should not start with underscore
        public_attrs = [attr for attr in dir(constants) if not attr.startswith("_")]
        for attr in public_attrs:
            # Skip module attributes
            if attr in [
                "__builtins__",
                "__cached__",
                "__doc__",
                "__file__",
                "__loader__",
                "__name__",
                "__package__",
                "__spec__",
            ]:
                continue
            # All remaining should be uppercase (constants)
            assert attr.isupper(), f"Non-constant public attribute found: {attr}"
