"""
FastForex API Exceptions

Custom exception classes for handling FastForex API errors.
"""


class FastForexError(Exception):
    """Base exception for all FastForex errors."""

    pass


class FastForexAPIError(FastForexError):
    """Exception raised when the API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class FastForexAuthError(FastForexAPIError):
    """Exception raised when authentication fails (401)."""

    pass


class FastForexForbiddenError(FastForexAPIError):
    """Exception raised when access is forbidden (403)."""

    pass


class FastForexRateLimitError(FastForexAPIError):
    """Exception raised when rate limit is exceeded (429)."""

    pass


class FastForexNotFoundError(FastForexAPIError):
    """Exception raised when a resource is not found (404)."""

    pass


class FastForexBadRequestError(FastForexAPIError):
    """Exception raised when the request is malformed (400)."""

    pass
