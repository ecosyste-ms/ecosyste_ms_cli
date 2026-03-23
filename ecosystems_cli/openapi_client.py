"""OpenAPI-core based API client for ecosystems CLI.

This module provides a client implementation using openapi-core for OpenAPI v3 specs.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urljoin

import requests
import yaml
from openapi_core import OpenAPI

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files

from ecosystems_cli import __version__
from ecosystems_cli.constants import (
    API_BASE_URL_TEMPLATE,
    DEFAULT_TIMEOUT,
    OPENAPI_FILE_EXTENSION,
)
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


class OpenAPIClientFactory:
    """Factory for creating and managing OpenAPI clients using openapi-core."""

    def __init__(self, specs_dir: Optional[Path] = None):
        """Initialize the factory.

        Args:
            specs_dir: Directory containing OpenAPI specs. Only used for testing with custom specs.
        """
        self.specs_dir = Path(specs_dir) if specs_dir else None
        self._specs: Dict[str, Dict[str, Any]] = {}
        self._openapi: Dict[str, OpenAPI] = {}
        self._operation_map: Dict[str, Dict[str, Any]] = {}
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": f"ecosyste_ms_cli ({__version__})"})

    def _discover_apis(self) -> List[str]:
        """Discover all available API specs."""
        if self.specs_dir:
            # Custom specs directory for testing
            if not self.specs_dir.exists():
                return []
            return [f.name.replace(OPENAPI_FILE_EXTENSION, "") for f in self.specs_dir.glob(f"*{OPENAPI_FILE_EXTENSION}")]
        else:
            # Use importlib.resources to discover specs in the package
            try:
                api_files = files("ecosystems_cli.apis").iterdir()
                return [
                    f.name.replace(OPENAPI_FILE_EXTENSION, "") for f in api_files if f.name.endswith(OPENAPI_FILE_EXTENSION)
                ]
            except (FileNotFoundError, ModuleNotFoundError):
                return []

    def _get_default_base_url(self, api_name: str, spec: Dict[str, Any]) -> str:
        """Get default base URL from OpenAPI specification."""
        servers = spec.get("servers", [])
        if servers and "url" in servers[0]:
            return servers[0]["url"]
        return API_BASE_URL_TEMPLATE.format(api_name=api_name)

    def _fix_response_codes(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Convert integer response codes to strings in OpenAPI spec.

        YAML parses numeric response codes (e.g., 200, 301) as integers,
        but OpenAPI 3.0 spec requires them to be strings.

        Args:
            spec: The OpenAPI specification dictionary

        Returns:
            Fixed specification dictionary with string response codes
        """
        if "paths" not in spec:
            return spec

        for path, methods in spec["paths"].items():
            for method, operation in methods.items():
                if isinstance(operation, dict) and "responses" in operation:
                    # Convert integer keys to strings
                    responses = operation["responses"]
                    if isinstance(responses, dict):
                        operation["responses"] = {str(k): v for k, v in responses.items()}

        return spec

    def _build_operation_map(self, api_name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Build operation ID to path/method mapping."""
        operation_map = {}
        paths = spec.get("paths", {})

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    operation_id = operation.get("operationId")
                    if operation_id:
                        operation_map[operation_id] = {
                            "path": path,
                            "method": method.upper(),
                            "operation": operation,
                            "summary": operation.get("summary", ""),
                            "description": operation.get("description", ""),
                        }

        return operation_map

    def get_openapi(self, api_name: str) -> OpenAPI:
        """Get or create an OpenAPI instance for the specified API.

        Args:
            api_name: Name of the API

        Returns:
            Configured OpenAPI instance

        Raises:
            InvalidAPIError: If API spec not found
        """
        if api_name in self._openapi:
            return self._openapi[api_name]

        try:
            # Load the OpenAPI spec
            if self.specs_dir:
                # Custom specs directory for testing
                spec_path = self.specs_dir / f"{api_name}{OPENAPI_FILE_EXTENSION}"
                if not spec_path.exists():
                    raise InvalidAPIError(api_name)
                with open(spec_path, "r") as f:
                    spec_dict = yaml.safe_load(f)
            else:
                # Use importlib.resources for packaged specs
                api_file_name = f"{api_name}{OPENAPI_FILE_EXTENSION}"
                spec_content = files("ecosystems_cli.apis").joinpath(api_file_name).read_text()
                spec_dict = yaml.safe_load(spec_content)

            # Fix response codes: OpenAPI spec requires string keys, but YAML parses numeric keys as integers
            spec_dict = self._fix_response_codes(spec_dict)

            # Create OpenAPI instance
            openapi = OpenAPI.from_dict(spec_dict)

            # Cache spec and openapi instance
            self._specs[api_name] = spec_dict
            self._openapi[api_name] = openapi
            self._operation_map[api_name] = self._build_operation_map(api_name, spec_dict)

            return openapi

        except InvalidAPIError:
            # Re-raise InvalidAPIError as-is
            raise
        except (FileNotFoundError, ModuleNotFoundError):
            raise InvalidAPIError(api_name)
        except Exception as e:
            raise APIConnectionError(f"Failed to load spec for {api_name}: {str(e)}")

    def call(
        self,
        api_name: str,
        operation_id: str,
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        mailto: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Call an API operation by operation ID.

        Args:
            api_name: Name of the API
            operation_id: Operation ID from OpenAPI spec
            path_params: Path parameters
            query_params: Query parameters
            body: Request body
            headers: Additional headers
            timeout: Request timeout
            mailto: Email for polite pool
            base_url: Override base URL

        Returns:
            API response as dictionary

        Raises:
            InvalidOperationError: If operation ID not found
            Various API errors based on response
        """
        # Ensure OpenAPI spec is loaded and operation map is populated
        self.get_openapi(api_name)

        # Get operation mapping
        if api_name not in self._operation_map:
            raise InvalidAPIError(api_name)

        if operation_id not in self._operation_map[api_name]:
            raise InvalidOperationError(operation_id)

        operation_info = self._operation_map[api_name][operation_id]

        # Determine base URL
        if base_url is None:
            base_url = self._get_default_base_url(api_name, self._specs[api_name])

        # Build the request URL
        path = operation_info["path"]

        # Replace path parameters with URL-encoded values
        if path_params:
            for param_name, param_value in path_params.items():
                # URL-encode the parameter value (safe='' means encode everything including '/')
                encoded_value = quote(str(param_value), safe="")
                path = path.replace(f"{{{param_name}}}", encoded_value)

        # Ensure proper URL joining by adding trailing slash to base_url
        # urljoin replaces the last component if base_url doesn't end with /
        if not base_url.endswith("/"):
            base_url += "/"
        url = urljoin(base_url, path.lstrip("/"))

        # Build headers
        request_headers = {}
        if mailto:
            request_headers["User-Agent"] = f"ecosyste_ms_cli ({__version__}) mailto:{mailto}"
        if headers:
            request_headers.update(headers)

        # Build query parameters
        params = {}
        if query_params:
            params.update(query_params)
        if mailto and "mailto" not in params:
            params["mailto"] = mailto

        # Prepare the request
        method = operation_info["method"]

        try:
            # Make the HTTP request
            response = self._session.request(
                method=method,
                url=url,
                params=params if params else None,
                json=body if body else None,
                headers=request_headers if request_headers else None,
                timeout=timeout,
                allow_redirects=False,  # Handle redirects manually
            )

            # Handle redirects
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("Location")
                if location:
                    return {"location": location, "status_code": response.status_code}

            # Check for HTTP errors
            self._handle_http_errors(response)

            # Parse the response
            return self._parse_response(response)

        except requests.exceptions.Timeout:
            raise APITimeoutError(timeout)
        except requests.exceptions.ConnectionError as e:
            raise APIConnectionError(f"Failed to connect to {url}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Request failed: {str(e)}")

    def _handle_http_errors(self, response: requests.Response) -> None:
        """Handle HTTP error responses.

        Args:
            response: The HTTP response

        Raises:
            Various API exceptions based on status code
        """
        if response.status_code < 400:
            return

        error_text = response.text[:500] if response.text else ""

        if response.status_code == 401:
            raise APIAuthenticationError(f"Unauthorized: {error_text}")
        elif response.status_code == 404:
            raise APINotFoundError(f"Not found: {error_text}")
        elif response.status_code == 429:
            # Parse rate limit headers if available
            headers = response.headers
            rate_limit_info = {}

            if "X-RateLimit-Limit" in headers:
                try:
                    rate_limit_info["limit"] = int(headers["X-RateLimit-Limit"])
                except ValueError:
                    pass

            if "X-RateLimit-Remaining" in headers:
                try:
                    rate_limit_info["remaining"] = int(headers["X-RateLimit-Remaining"])
                except ValueError:
                    pass

            if "X-RateLimit-Reset" in headers:
                try:
                    reset_timestamp = int(headers["X-RateLimit-Reset"])
                    reset_datetime = datetime.fromtimestamp(reset_timestamp, tz=timezone.utc)
                    rate_limit_info["reset_time"] = reset_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
                except (ValueError, OSError):
                    pass

            if "Retry-After" in headers:
                try:
                    rate_limit_info["retry_after"] = int(headers["Retry-After"])
                except ValueError:
                    pass

            raise APIRateLimitError(
                limit=rate_limit_info.get("limit"),
                remaining=rate_limit_info.get("remaining"),
                reset_time=rate_limit_info.get("reset_time"),
                retry_after=rate_limit_info.get("retry_after"),
            )
        elif response.status_code >= 500:
            raise APIServerError(response.status_code, f"Server error: {error_text}")
        else:
            raise APIHTTPError(response.status_code, f"HTTP error: {error_text}")

    def _parse_response(self, response: requests.Response) -> Any:
        """Parse HTTP response.

        Args:
            response: The HTTP response

        Returns:
            Parsed response data
        """
        # Handle empty responses
        if not response.content:
            return {}

        # Try to parse JSON
        try:
            data = response.json()
            return self._convert_dates(data)
        except ValueError:
            # Not JSON, return text
            return {"result": response.text}

    def _convert_dates(self, obj: Any) -> Any:
        """Convert date strings to datetime objects recursively."""
        if isinstance(obj, dict):
            return {k: self._convert_dates(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_dates(item) for item in obj]
        elif isinstance(obj, str):
            # Try to parse as datetime
            for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(obj, fmt)
                except ValueError:
                    continue
            return obj
        else:
            return obj

    def list_operations(self, api_name: str) -> List[Dict[str, str]]:
        """List all operations for an API.

        Args:
            api_name: Name of the API

        Returns:
            List of operation information dictionaries
        """
        # Ensure openapi is loaded to populate operation map
        self.get_openapi(api_name)

        if api_name not in self._operation_map:
            return []

        operations = []
        for op_id, details in self._operation_map[api_name].items():
            operations.append(
                {
                    "id": op_id,
                    "method": details["method"],
                    "path": details["path"],
                    "summary": details["summary"],
                }
            )

        return operations

    def get_client(
        self,
        api_name: str,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        mailto: Optional[str] = None,
    ) -> "OpenAPIClientFactory":
        """Get a client instance for the specified API.

        Note: This returns the factory itself since we don't use a separate client object.
        The factory provides all necessary methods.

        Args:
            api_name: Name of the API
            base_url: Override base URL
            timeout: Request timeout
            mailto: Email for polite pool

        Returns:
            The factory instance (for compatibility)
        """
        # Ensure the API spec is loaded
        self.get_openapi(api_name)
        return self


# Global factory instance
_factory = OpenAPIClientFactory()


def get_client(
    api_name: str,
    base_url: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
    mailto: Optional[str] = None,
) -> OpenAPIClientFactory:
    """Get API client for specified API.

    Args:
        api_name: Name of the API
        base_url: Base URL for the API. If not provided, uses default.
        timeout: Timeout in seconds for HTTP requests.
        mailto: Email address for polite pool access.

    Returns:
        Configured client factory instance
    """
    return _factory.get_client(api_name, base_url=base_url, timeout=timeout, mailto=mailto)
