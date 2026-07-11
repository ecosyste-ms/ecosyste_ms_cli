"""Tests for the OpenAPI client."""

from datetime import datetime
from unittest import mock

import pytest
import requests
import yaml

from ecosystems_cli.exceptions import (
    APIAuthenticationError,
    APIConnectionError,
    APIHTTPError,
    APINotFoundError,
    APIRateLimitError,
    APIServerError,
    APITimeoutError,
    InvalidAPIError,
    InvalidOperationError,
)
from ecosystems_cli.openapi_client import OpenAPIClientFactory, get_client


def _make_response(status_code=200, json_data=None, text="", headers=None, content=None, raise_on_json=False):
    """Build a fake ``requests.Response`` for driving ``OpenAPIClientFactory.call``."""
    resp = mock.Mock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.text = text
    if content is not None:
        resp.content = content
    elif json_data is not None:
        resp.content = b"{}"
    else:
        resp.content = text.encode() if text else b""
    if raise_on_json:
        resp.json.side_effect = ValueError("not json")
    else:
        resp.json.return_value = json_data if json_data is not None else {}
    return resp


@pytest.fixture
def call_factory(mock_spec_file):
    """A factory with the test spec loaded and a mocked HTTP session."""
    factory = OpenAPIClientFactory(specs_dir=mock_spec_file)
    factory.get_openapi("test")
    factory._session = mock.Mock()
    return factory


@pytest.fixture
def mock_spec():
    """Create a mock OpenAPI spec for testing."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "servers": [{"url": "https://test.example.com/api/v1"}],
        "paths": {
            "/test": {
                "get": {
                    "operationId": "getTest",
                    "summary": "Get test data",
                    "tags": ["test"],
                    "parameters": [
                        {
                            "name": "id",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {"schema": {"type": "object", "properties": {"data": {"type": "string"}}}}
                            },
                        }
                    },
                }
            },
            "/items/{itemId}": {
                "get": {
                    "operationId": "getItem",
                    "summary": "Get item by ID",
                    "tags": ["items"],
                    "parameters": [
                        {
                            "name": "itemId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/jobs": {
                "post": {
                    "operationId": "createTest",
                    "summary": "Submit a job",
                    "responses": {"301": {"description": "Redirect"}},
                }
            },
        },
    }


@pytest.fixture
def mock_spec_file(tmp_path, mock_spec):
    """Create a temporary spec file."""
    spec_dir = tmp_path / "apis"
    spec_dir.mkdir()
    spec_file = spec_dir / "test.openapi.yaml"
    with open(spec_file, "w") as f:
        yaml.dump(mock_spec, f)
    return spec_dir


class TestOpenAPIClientFactory:
    """Test the OpenAPIClientFactory class."""

    def test_init_with_custom_specs_dir(self, mock_spec_file):
        """Test factory initialization with custom specs directory."""
        factory = OpenAPIClientFactory(specs_dir=mock_spec_file)
        assert factory.specs_dir == mock_spec_file

    def test_discover_apis(self, mock_spec_file):
        """Test API discovery from specs directory."""
        factory = OpenAPIClientFactory(specs_dir=mock_spec_file)
        apis = factory._discover_apis()
        assert "test" in apis

    def test_get_client_invalid_api(self, mock_spec_file):
        """Test getting client for non-existent API."""
        factory = OpenAPIClientFactory(specs_dir=mock_spec_file)
        with pytest.raises(InvalidAPIError):
            factory.get_client("nonexistent")

    def test_get_client_success(self, mock_spec_file):
        """Test successful client creation."""
        factory = OpenAPIClientFactory(specs_dir=mock_spec_file)

        # Act
        client = factory.get_client("test")

        # Assert
        assert client is not None
        assert client == factory  # get_client returns the factory itself

    def test_get_client_with_mailto(self, mock_spec_file):
        """Test client creation with mailto parameter."""
        factory = OpenAPIClientFactory(specs_dir=mock_spec_file)

        # Act
        client = factory.get_client("test", mailto="test@example.com")

        # Assert
        assert client is not None
        assert client == factory  # get_client returns the factory itself

    def test_get_client_caching(self, mock_spec_file):
        """Test that clients are cached."""
        factory = OpenAPIClientFactory(specs_dir=mock_spec_file)

        # Act
        client1 = factory.get_client("test", timeout=20)
        client2 = factory.get_client("test", timeout=20)

        # Assert
        assert client1 is client2  # Both return the same factory instance
        # Verify OpenAPI instance is cached
        assert "test" in factory._openapi

    def test_build_operation_map(self, mock_spec_file, mock_spec):
        """Test operation mapping building."""
        factory = OpenAPIClientFactory(specs_dir=mock_spec_file)
        operation_map = factory._build_operation_map("test", mock_spec)

        assert "getTest" in operation_map
        assert "getItem" in operation_map
        assert operation_map["getTest"]["path"] == "/test"
        assert operation_map["getTest"]["method"] == "GET"
        assert operation_map["getItem"]["path"] == "/items/{itemId}"

    def test_list_operations(self, mock_spec_file):
        """Test listing operations."""
        factory = OpenAPIClientFactory(specs_dir=mock_spec_file)

        # Act
        operations = factory.list_operations("test")

        # Assert
        assert len(operations) == 3
        operation_ids = [op["id"] for op in operations]
        assert "getTest" in operation_ids
        assert "getItem" in operation_ids
        assert "createTest" in operation_ids

    def test_call_invalid_operation(self, mock_spec_file):
        """Test calling non-existent operation."""
        factory = OpenAPIClientFactory(specs_dir=mock_spec_file)

        # Act & Assert
        with pytest.raises(InvalidOperationError):
            factory.call("test", "nonexistentOperation")


class TestGetClient:
    """Test the get_client convenience function."""

    @mock.patch("ecosystems_cli.openapi_client._factory.get_client")
    def test_get_client_delegates_to_factory(self, mock_factory_get_client):
        """Test that get_client delegates to factory."""
        # Act
        get_client("test", timeout=30, mailto="test@example.com")

        # Assert
        mock_factory_get_client.assert_called_once_with("test", base_url=None, timeout=30, mailto="test@example.com")


class TestCallRequestBuilding:
    """How call() turns operation + params into an HTTP request."""

    def test_successful_get_returns_parsed_body(self, call_factory):
        call_factory._session.request.return_value = _make_response(json_data={"data": "ok"})

        result = call_factory.call("test", "getTest", query_params={"id": "abc"})

        assert result == {"data": "ok"}
        kwargs = call_factory._session.request.call_args.kwargs
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "https://test.example.com/api/v1/test"
        assert kwargs["params"] == {"id": "abc"}
        # GET requests follow redirects so data endpoints that 301/302 return
        # the real payload instead of a redirect envelope.
        assert kwargs["allow_redirects"] is True

    def test_path_params_are_url_encoded(self, call_factory):
        """Path values are fully encoded (safe=''), so '/' and spaces can't escape the segment."""
        call_factory._session.request.return_value = _make_response(json_data={"id": "x"})

        call_factory.call("test", "getItem", path_params={"itemId": "a/b c"})

        url = call_factory._session.request.call_args.kwargs["url"]
        assert url == "https://test.example.com/api/v1/items/a%2Fb%20c"

    def test_base_url_override_is_used(self, call_factory):
        call_factory._session.request.return_value = _make_response(json_data={})

        call_factory.call("test", "getTest", base_url="https://override.example.com")

        url = call_factory._session.request.call_args.kwargs["url"]
        assert url.startswith("https://override.example.com/")

    def test_mailto_adds_query_param_and_user_agent(self, call_factory):
        call_factory._session.request.return_value = _make_response(json_data={})

        call_factory.call("test", "getTest", mailto="me@example.com")

        kwargs = call_factory._session.request.call_args.kwargs
        assert kwargs["params"]["mailto"] == "me@example.com"
        assert "mailto:me@example.com" in kwargs["headers"]["User-Agent"]

    def test_body_is_sent_as_json(self, call_factory):
        call_factory._session.request.return_value = _make_response(json_data={})

        call_factory.call("test", "getTest", body={"url": "https://x"})

        assert call_factory._session.request.call_args.kwargs["json"] == {"url": "https://x"}


class TestCallRedirectHandling:
    """GET redirects are followed; non-GET redirects surface the Location.

    The job APIs answer createJob POSTs with a 301 whose Location is the
    created job, so that envelope must keep reaching submit_and_poll.
    """

    @pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
    def test_post_redirect_returns_location(self, call_factory, status):
        call_factory._session.request.return_value = _make_response(
            status_code=status, headers={"Location": "https://jobs.example.com/jobs/42"}
        )

        result = call_factory.call("test", "createTest")

        assert result == {"location": "https://jobs.example.com/jobs/42", "status_code": status}
        assert call_factory._session.request.call_args.kwargs["allow_redirects"] is False


class TestCallErrorHandling:
    """Status codes map to typed exceptions."""

    def test_404_raises_not_found(self, call_factory):
        call_factory._session.request.return_value = _make_response(status_code=404, text="missing")
        with pytest.raises(APINotFoundError):
            call_factory.call("test", "getTest")

    def test_401_raises_authentication_error(self, call_factory):
        call_factory._session.request.return_value = _make_response(status_code=401, text="nope")
        with pytest.raises(APIAuthenticationError):
            call_factory.call("test", "getTest")

    def test_500_raises_server_error_with_status(self, call_factory):
        call_factory._session.request.return_value = _make_response(status_code=503, text="down")
        with pytest.raises(APIServerError) as exc:
            call_factory.call("test", "getTest")
        assert exc.value.status_code == 503

    def test_generic_4xx_raises_http_error(self, call_factory):
        call_factory._session.request.return_value = _make_response(status_code=422, text="bad")
        with pytest.raises(APIHTTPError) as exc:
            call_factory.call("test", "getTest")
        assert exc.value.status_code == 422

    def test_429_parses_rate_limit_headers(self, call_factory):
        call_factory._session.request.return_value = _make_response(
            status_code=429,
            headers={
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "1700000000",
                "Retry-After": "30",
            },
        )
        with pytest.raises(APIRateLimitError) as exc:
            call_factory.call("test", "getTest")
        assert exc.value.limit == 60
        assert exc.value.remaining == 0
        assert exc.value.retry_after == 30
        assert exc.value.reset_time is not None

    def test_429_tolerates_malformed_rate_limit_headers(self, call_factory):
        call_factory._session.request.return_value = _make_response(
            status_code=429, headers={"X-RateLimit-Limit": "not-a-number"}
        )
        with pytest.raises(APIRateLimitError) as exc:
            call_factory.call("test", "getTest")
        assert exc.value.limit is None

    def test_timeout_raises_api_timeout(self, call_factory):
        call_factory._session.request.side_effect = requests.exceptions.Timeout()
        with pytest.raises(APITimeoutError):
            call_factory.call("test", "getTest", timeout=5)

    def test_connection_error_raises_api_connection_error(self, call_factory):
        call_factory._session.request.side_effect = requests.exceptions.ConnectionError("boom")
        with pytest.raises(APIConnectionError):
            call_factory.call("test", "getTest")

    def test_generic_request_exception_raises_api_connection_error(self, call_factory):
        call_factory._session.request.side_effect = requests.exceptions.RequestException("weird")
        with pytest.raises(APIConnectionError):
            call_factory.call("test", "getTest")


class TestConvertDates:
    """The regex gate: datetime-shaped strings convert, everything else passes through."""

    def setup_method(self):
        self.factory = OpenAPIClientFactory()

    def test_full_timestamps_convert(self):
        assert isinstance(self.factory._convert_dates("2024-01-15T10:30:00Z"), datetime)
        assert isinstance(self.factory._convert_dates("2024-01-15T10:30:00.500Z"), datetime)
        assert isinstance(self.factory._convert_dates("2024-01-15T10:30:00"), datetime)

    def test_non_datetime_strings_pass_through_untouched(self):
        # Versions, date-only strings, URLs and free text must stay strings.
        for value in ["4.17.21", "2024-01-15", "https://example.com/2024-01-15", "lodash", "T", ""]:
            assert self.factory._convert_dates(value) == value
            assert isinstance(self.factory._convert_dates(value), str)

    def test_nested_structures_convert_recursively(self):
        result = self.factory._convert_dates(
            {"created_at": "2024-01-15T10:30:00Z", "name": "x", "items": ["2024-01-15T10:30:00Z", "plain"]}
        )
        assert isinstance(result["created_at"], datetime)
        assert result["name"] == "x"
        assert isinstance(result["items"][0], datetime)
        assert result["items"][1] == "plain"

    def test_non_string_scalars_unchanged(self):
        assert self.factory._convert_dates(42) == 42
        assert self.factory._convert_dates(None) is None
        assert self.factory._convert_dates(True) is True


class TestCallResponseParsing:
    """_parse_response and _convert_dates."""

    def test_empty_body_returns_empty_dict(self, call_factory):
        call_factory._session.request.return_value = _make_response(content=b"")
        assert call_factory.call("test", "getTest") == {}

    def test_non_json_body_returns_result_wrapper(self, call_factory):
        call_factory._session.request.return_value = _make_response(text="plain text", raise_on_json=True)
        assert call_factory.call("test", "getTest") == {"result": "plain text"}

    def test_iso_date_strings_become_datetimes(self, call_factory):
        call_factory._session.request.return_value = _make_response(
            json_data={
                "created_at": "2024-01-15T10:30:00Z",
                "fractional": "2024-01-15T10:30:00.500Z",
                "no_zone": "2024-01-15T10:30:00",
                "name": "lodash",
                "date_only": "2024-01-15",
                "nested": {"updated_at": "2024-01-15T10:30:00Z"},
                "items": ["2024-01-15T10:30:00Z"],
            }
        )

        result = call_factory.call("test", "getTest")

        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["fractional"], datetime)
        assert isinstance(result["no_zone"], datetime)
        assert isinstance(result["nested"]["updated_at"], datetime)
        assert isinstance(result["items"][0], datetime)
        # Non-ISO strings are left untouched.
        assert result["name"] == "lodash"
        assert result["date_only"] == "2024-01-15"
