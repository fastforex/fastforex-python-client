"""
FastForex Python Client

A Python SDK for the FastForex.io currency and cryptocurrency exchange rate API.
"""

from .client import FastForexClient
from .exceptions import (
    FastForexError,
    FastForexAPIError,
    FastForexAuthError,
    FastForexRateLimitError,
    FastForexNotFoundError,
)

__version__ = "1.0.0"
__all__ = [
    "FastForexClient",
    "FastForexError",
    "FastForexAPIError",
    "FastForexAuthError",
    "FastForexRateLimitError",
    "FastForexNotFoundError",
]
