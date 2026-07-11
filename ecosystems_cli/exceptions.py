"""Custom exceptions for the Ecosystems CLI."""


class EcosystemsCLIError(Exception):
    """Base exception for all ecosystems CLI errors."""

    pass


class APIError(EcosystemsCLIError):
    """Base exception for API-related errors."""

    pass


class APIConnectionError(APIError):
    """Raised when unable to connect to the API."""

    pass


class APITimeoutError(APIError):
    """Raised when an API request times out."""

    def __init__(self, timeout=None):
        self.timeout = timeout
        # str(exception) is shown to the user verbatim; a bare timeout value
        # would render as the meaningless "Error: 20".
        if timeout is not None:
            unit = "second" if timeout == 1 else "seconds"
            message = f"Request timed out after {timeout} {unit}"
        else:
            message = "Request timed out"
        super().__init__(message)


class APIHTTPError(APIError):
    """Base exception for HTTP errors from the API."""

    def __init__(self, status_code: int, message: str = None):
        self.status_code = status_code
        super().__init__(message or f"HTTP {status_code} error")


class APIAuthenticationError(APIHTTPError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = None):
        super().__init__(401, message or "Authentication failed")


class APINotFoundError(APIHTTPError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = None):
        super().__init__(404, message or "Resource not found")


class APIServerError(APIHTTPError):
    """Raised when the server encounters an error (5xx)."""

    def __init__(self, status_code: int = 500, message: str = None):
        super().__init__(status_code, message or f"Server error (HTTP {status_code})")


class APIRateLimitError(APIHTTPError):
    """Raised when API rate limit is exceeded (429)."""

    def __init__(self, limit: int = None, remaining: int = None, reset_time: str = None, retry_after: int = None):
        self.limit = limit
        self.remaining = remaining
        self.reset_time = reset_time
        self.retry_after = retry_after

        message = "Rate limit exceeded."
        if limit is not None:
            message += f"\nLimit: {limit} requests per window"
        if remaining is not None:
            message += f"\nRemaining: {remaining} requests"
        if reset_time:
            message += f"\nReset: {reset_time}"
        if retry_after is not None:
            message += f"\nRetry after: {retry_after} seconds"
        message += "\nPlease wait before retrying."

        super().__init__(429, message)


class ConfigurationError(EcosystemsCLIError):
    """Base exception for configuration-related errors."""

    pass


class InvalidAPIError(ConfigurationError):
    """Raised when an invalid API is specified."""

    def __init__(self, api_name: str):
        super().__init__(f"Invalid API: {api_name}")
        self.api_name = api_name


class MissingSpecificationError(ConfigurationError):
    """Raised when an API specification file is missing."""

    def __init__(self, api_name: str):
        super().__init__(f"Missing specification for API: {api_name}")
        self.api_name = api_name


class OperationError(EcosystemsCLIError):
    """Base exception for operation-related errors."""

    pass


class InvalidOperationError(OperationError):
    """Raised when an invalid operation is requested."""

    def __init__(self, operation_id: str):
        super().__init__(f"Invalid operation: {operation_id}")
        self.operation_id = operation_id


class MissingParameterError(OperationError):
    """Raised when a required parameter is missing."""

    def __init__(self, parameter_name: str):
        super().__init__(f"Missing required parameter: {parameter_name}")
        self.parameter_name = parameter_name


class InvalidParameterError(OperationError):
    """Raised when a parameter has an invalid value."""

    def __init__(self, parameter_name: str, message: str = None):
        super().__init__(message or f"Invalid parameter: {parameter_name}")
        self.parameter_name = parameter_name


class DataError(EcosystemsCLIError):
    """Base exception for data processing errors."""

    pass


class JSONParseError(DataError):
    """Raised when JSON parsing fails."""

    def __init__(self, message: str = None):
        super().__init__(message or "Failed to parse JSON")


class InvalidResponseFormatError(DataError):
    """Raised when the API response has an unexpected format."""

    def __init__(self, message: str = None):
        super().__init__(message or "Invalid response format")
