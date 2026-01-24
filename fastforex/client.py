"""
FastForex API Client

A Python client for the FastForex.io currency and cryptocurrency exchange rate API.
"""

from typing import Any
from urllib.parse import urlencode

import requests

from .exceptions import (
    FastForexAPIError,
    FastForexAuthError,
    FastForexBadRequestError,
    FastForexForbiddenError,
    FastForexNotFoundError,
    FastForexRateLimitError,
)


class FastForexClient:
    """
    Client for interacting with the FastForex.io API.

    Provides methods for fetching currency exchange rates, cryptocurrency prices,
    FX trading pair data, and account usage information.

    Args:
        api_key: Your FastForex API key.
        base_url: The API base URL. Defaults to production.
        timeout: Request timeout in seconds. Defaults to 30.

    Example:
        >>> client = FastForexClient(api_key="your-api-key")
        >>> rate = client.fetch_one(from_currency="USD", to="EUR")
        >>> print(rate)
    """

    PRODUCTION_URL = "https://api.fastforex.io"
    BETA_URL = "https://api.beta.fastforex.io"

    def __init__(
        self,
        api_key: str,
        base_url: str = PRODUCTION_URL,
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "fastforex-python-client"

    def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Make a GET request to the API.

        Args:
            endpoint: The API endpoint path.
            params: Query parameters for the request.

        Returns:
            The JSON response as a dictionary.

        Raises:
            FastForexAuthError: If authentication fails.
            FastForexForbiddenError: If access is forbidden.
            FastForexRateLimitError: If rate limit is exceeded.
            FastForexNotFoundError: If resource is not found.
            FastForexBadRequestError: If the request is malformed.
            FastForexAPIError: For other API errors.
        """
        if params is None:
            params = {}

        # Add API key to params
        params["api_key"] = self.api_key

        # Filter out None values
        params = {k: v for k, v in params.items() if v is not None}

        url = f"{self.base_url}{endpoint}"

        try:
            response = self._session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            raise FastForexAPIError(f"Request failed: {e}") from e

        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        """Handle the API response and raise appropriate exceptions for errors."""
        try:
            data: dict[str, Any] | None = response.json()
        except ValueError:
            data = None

        if response.status_code == 200:
            if data is None:
                raise FastForexAPIError("Empty response from API", status_code=200)
            return data

        error_message = data.get("error", response.text) if data else response.text

        if response.status_code == 400:
            raise FastForexBadRequestError(
                f"Bad request: {error_message}",
                status_code=response.status_code,
                response=data,
            )
        elif response.status_code == 401:
            raise FastForexAuthError(
                f"Authentication failed: {error_message}",
                status_code=response.status_code,
                response=data,
            )
        elif response.status_code == 403:
            raise FastForexForbiddenError(
                f"Access forbidden: {error_message}",
                status_code=response.status_code,
                response=data,
            )
        elif response.status_code == 404:
            raise FastForexNotFoundError(
                f"Resource not found: {error_message}",
                status_code=response.status_code,
                response=data,
            )
        elif response.status_code == 429:
            raise FastForexRateLimitError(
                f"Rate limit exceeded: {error_message}",
                status_code=response.status_code,
                response=data,
            )
        else:
            raise FastForexAPIError(
                f"API error ({response.status_code}): {error_message}",
                status_code=response.status_code,
                response=data,
            )

    # -------------------------------------------------------------------------
    # Currency Endpoints
    # -------------------------------------------------------------------------

    def fetch_one(
        self,
        to: str,
        from_currency: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch a single currency exchange rate.

        Args:
            to: Target currency symbol (physical or digital).
            from_currency: Base currency symbol. Defaults to USD.

        Returns:
            Dict containing 'base', 'result', 'updated', and 'ms' keys.

        Example:
            >>> client.fetch_one(to="EUR")
            {'base': 'USD', 'result': {'EUR': 0.82791}, 'updated': '2021-01-16T16:34:29Z', 'ms': 4}
        """
        params = {"to": to, "from": from_currency}
        return self._request("/fetch-one", params)

    def fetch_multi(
        self,
        to: str | list[str],
        from_currency: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch multiple currency rates at once.

        Args:
            to: Target currencies as comma-separated string or list.
            from_currency: Base currency symbol. Defaults to USD.

        Returns:
            Dict containing 'base', 'results', 'updated', and 'ms' keys.

        Example:
            >>> client.fetch_multi(to=["EUR", "GBP"])
            {'base': 'USD', 'results': {'EUR': 0.82791, 'GBP': 0.73605}, ...}
        """
        if isinstance(to, list):
            to = ",".join(to)
        params = {"to": to, "from": from_currency}
        return self._request("/fetch-multi", params)

    def fetch_all(self, from_currency: str | None = None) -> dict[str, Any]:
        """
        Fetch all available currency rates.

        Args:
            from_currency: Base currency symbol. Defaults to USD.

        Returns:
            Dict containing 'base', 'results', 'updated', and 'ms' keys.
            Results contains 130+ currency rates.

        Example:
            >>> result = client.fetch_all()
            >>> print(result['results']['EUR'])
            0.8799
        """
        params = {"from": from_currency}
        return self._request("/fetch-all", params)

    def fetch_many_to_one(
        self,
        from_currencies: str | list[str],
        to: str,
    ) -> dict[str, Any]:
        """
        Fetch rates from multiple source currencies to a single target currency.

        This is the inverse of fetch_multi. Costs one API call per pair returned.

        Args:
            from_currencies: Source currencies as comma-separated string or list.
            to: Target currency symbol.

        Returns:
            Dict containing 'to', 'from', 'updated', 'calls', and 'ms' keys.

        Example:
            >>> client.fetch_many_to_one(from_currencies=["JPY", "CHF", "AUD"], to="USD")
            {'to': 'USD', 'from': {'JPY': 0.00679, 'CHF': 1.2539, 'AUD': 0.65962}, ...}
        """
        if isinstance(from_currencies, list):
            from_currencies = ",".join(from_currencies)
        params = {"from": from_currencies, "to": to}
        return self._request("/fetch-many-to-one", params)

    def fetch_matrix(
        self,
        from_currencies: str | list[str],
        to_currencies: str | list[str],
    ) -> dict[str, Any]:
        """
        Fetch a matrix of multiple from/to currency pairs.

        Costs one API call per pair returned.

        Args:
            from_currencies: Source currencies as comma-separated string or list.
            to_currencies: Target currencies as comma-separated string or list.

        Returns:
            Dict containing 'from', 'to', 'matrix', 'updated', 'calls', and 'ms' keys.

        Example:
            >>> client.fetch_matrix(from_currencies=["USD", "EUR"], to_currencies=["GBP", "JPY"])
            {'matrix': {'USD': {'GBP': 0.74196, 'JPY': 147.488}, 'EUR': {...}}, ...}
        """
        if isinstance(from_currencies, list):
            from_currencies = ",".join(from_currencies)
        if isinstance(to_currencies, list):
            to_currencies = ",".join(to_currencies)
        params = {"from": from_currencies, "to": to_currencies}
        return self._request("/fetch-matrix", params)

    def convert(
        self,
        to: str,
        amount: float,
        from_currency: str | None = None,
        precision: int | None = None,
    ) -> dict[str, Any]:
        """
        Convert an amount from one currency to another.

        Supports both physical and digital currencies.

        Args:
            to: Target currency symbol.
            amount: Amount of source currency to convert.
            from_currency: Base currency symbol. Defaults to USD.
            precision: Rounding precision (0-20 decimal places). Defaults to 2.

        Returns:
            Dict containing 'base', 'amount', 'result', and 'ms' keys.
            Result contains 'rate' and the converted amount.

        Example:
            >>> client.convert(to="EUR", amount=100)
            {'base': 'USD', 'amount': 100, 'result': {'EUR': 82.35, 'rate': 0.82353}, 'ms': 7}
        """
        params = {
            "to": to,
            "amount": amount,
            "from": from_currency,
            "precision": precision,
        }
        return self._request("/convert", params)

    def historical(
        self,
        date: str,
        from_currency: str | None = None,
        to: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Fetch exchange rates for a historical date.

        Args:
            date: UTC date in YYYY-MM-DD format. Data available back to Jan 1970
                  for some pairs.
            from_currency: Base currency symbol. Defaults to USD.
            to: Target currencies as comma-separated string or list. Defaults to all.

        Returns:
            Dict containing 'date', 'base', 'results', and 'ms' keys.

        Example:
            >>> client.historical(date="2021-01-16", to=["EUR", "GBP"])
            {'date': '2021-01-16', 'base': 'USD', 'results': {'EUR': 0.82791, 'GBP': 0.73605}, ...}
        """
        if isinstance(to, list):
            to = ",".join(to)
        params = {"date": date, "from": from_currency, "to": to}
        return self._request("/historical", params)

    def time_series(
        self,
        to: str,
        start: str,
        end: str,
        from_currency: str | None = None,
        interval: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch a time-series dataset of currency rates.

        Args:
            to: Target currency symbol.
            start: UTC start date in YYYY-MM-DD format.
            end: UTC end date in YYYY-MM-DD format.
            from_currency: Base currency symbol. Defaults to USD.
            interval: ISO8601 duration (e.g., "P1D" for daily). Defaults to P1D.

        Returns:
            Dict containing 'start', 'end', 'interval', 'base', 'results', and 'ms' keys.

        Example:
            >>> client.time_series(to="GBP", start="2021-01-24", end="2021-01-30")
            {'results': {'GBP': {'2021-01-24': 1.14, '2021-01-25': 1.14, ...}}, ...}
        """
        params = {
            "to": to,
            "start": start,
            "end": end,
            "from": from_currency,
            "interval": interval,
        }
        return self._request("/time-series", params)

    def currencies(self) -> dict[str, Any]:
        """
        Fetch a list of supported physical currencies.

        Returns:
            Dict containing 'currencies' and 'ms' keys.
            Currencies is a dict mapping currency codes to names.

        Example:
            >>> result = client.currencies()
            >>> print(result['currencies']['USD'])
            'United States Dollar'
        """
        return self._request("/currencies")

    # -------------------------------------------------------------------------
    # Crypto Endpoints
    # -------------------------------------------------------------------------

    def crypto_currencies(self) -> dict[str, Any]:
        """
        Fetch a list of 500+ supported cryptocurrencies.

        Returns:
            Dict containing 'currencies' and 'ms' keys.
            Currencies is a dict mapping crypto codes to names.

        Example:
            >>> result = client.crypto_currencies()
            >>> print(result['currencies']['BTC'])
            'Bitcoin'
        """
        return self._request("/crypto/currencies")

    def crypto_pairs(self) -> dict[str, Any]:
        """
        Fetch a list of 400+ supported cryptocurrency pairs.

        Returns:
            Dict containing 'pairs' and 'ms' keys.
            Pairs is a dict mapping pair names to base/quote info.

        Example:
            >>> result = client.crypto_pairs()
            >>> print(result['pairs']['BTC/USD'])
            {'base': 'BTC', 'quote': 'USD'}
        """
        return self._request("/crypto/pairs")

    def crypto_fetch_prices(self, pairs: str | list[str]) -> dict[str, Any]:
        """
        Fetch real-time prices for cryptocurrency pairs.

        Args:
            pairs: Up to 10 pairs in XXX/YYY format, as string or list.

        Returns:
            Dict containing 'prices' and 'ms' keys.

        Example:
            >>> client.crypto_fetch_prices(pairs=["BTC/USD", "ETH/BTC"])
            {'prices': {'BTC/USD': 20624.21, 'ETH/BTC': 0.075316}, 'ms': 8}
        """
        if isinstance(pairs, list):
            pairs = ",".join(pairs)
        params = {"pairs": pairs}
        return self._request("/crypto/fetch-prices", params)

    # -------------------------------------------------------------------------
    # FX Trading Endpoints
    # -------------------------------------------------------------------------

    def fx_pairs(self) -> dict[str, Any]:
        """
        List approximately 2,300 supported FX trading pairs.

        Returns:
            Dict containing 'pairs' and 'ms' keys.
            Pairs includes base, quote, and alternative identifier for each pair.

        Example:
            >>> result = client.fx_pairs()
            >>> print(result['pairs']['EUR/USD'])
            {'base': 'EUR', 'quote': 'USD', 'alt': 'EURUSD'}
        """
        return self._request("/fx/pairs")

    def fx_pairs_historical_limits(
        self,
        interval: str | None = None,
        price: str | None = None,
    ) -> dict[str, Any]:
        """
        Get earliest available historical data point for FX pairs.

        Args:
            interval: ISO8601 duration (P1D, PT1H, or PT1M). Defaults to P1D.
            price: Price type ('bid' or 'ask'). Defaults to 'bid'.

        Returns:
            Dict containing 'interval', 'price', 'pairs', and 'ms' keys.

        Example:
            >>> client.fx_pairs_historical_limits()
            {'pairs': {'EURUSD': '1976-01-02T00:00:00Z', 'GBPUSD': '1970-01-02T00:00:00Z', ...}}
        """
        params = {"interval": interval, "price": price}
        return self._request("/fx/pairs/historical-limits", params)

    def fx_pairs_quote_sizes(self) -> dict[str, Any]:
        """
        List FX trading pairs with non-standard quote sizes.

        Returns:
            Dict containing 'sizes' and 'ms' keys.

        Example:
            >>> client.fx_pairs_quote_sizes()
            {'sizes': {'IRRUSD': 100000, 'VNDUSD': 10000, ...}, 'ms': 12}
        """
        return self._request("/fx/pairs/quote-sizes")

    def fx_currencies(self) -> dict[str, Any]:
        """
        List supported FX trading currency symbols and descriptions.

        Returns:
            Dict containing 'currencies' and 'ms' keys.

        Example:
            >>> result = client.fx_currencies()
            >>> print(result['currencies']['EUR'])
            'Euro'
        """
        return self._request("/fx/currencies")

    def fx_quote(self, pairs: str | list[str]) -> dict[str, Any]:
        """
        Get live bid & ask quotes for FX trading pairs.

        Args:
            pairs: Up to 10 pairs in XXXYYY or XXX/YYY format, as string or list.

        Returns:
            Dict containing 'quotes' and 'ms' keys.
            Each quote has bid, ask, tsp (timestamp), and size.

        Example:
            >>> client.fx_quote(pairs=["EURUSD", "GBPUSD"])
            {'quotes': {'EURUSD': {'bid': 1.2145, 'ask': 1.2146, 'tsp': 1739305030072, 'size': 1}, ...}}
        """
        if isinstance(pairs, list):
            pairs = ",".join(pairs)
        params = {"pairs": pairs}
        return self._request("/fx/quote", params)

    def fx_quote_time_series(
        self,
        pair: str,
        start: str | int | None = None,
        end: str | int | None = None,
        interval: str | None = None,
        limit: int | None = None,
        dtmfmt: str | None = None,
    ) -> dict[str, Any]:
        """
        Get bid/ask time-series data for an FX trading pair.

        Values are the closing bid/ask for each interval.

        Args:
            pair: Trading pair (e.g., "EURUSD" or "EUR/USD").
            start: Time-series start (date, datetime, ISO8601, or timestamp in ms).
            end: Time-series end (date, datetime, ISO8601, or timestamp in ms).
            interval: ISO8601 duration (P1D, PT1H, or PT1M). Defaults to P1D.
            limit: Maximum data points to return (1-100).
            dtmfmt: Response datetime format ('ISO', 'TSP', or 'UTCYMD').

        Returns:
            Dict containing pair, interval, results (array of dtm/bid/ask), and ms.

        Example:
            >>> client.fx_quote_time_series(pair="GBPUSD", end="2025-02-13", interval="PT1M", limit=5)
            {'results': [{'dtm': '2025-02-13T16:29:00Z', 'bid': 1.25377, 'ask': 1.25379}, ...]}
        """
        params = {
            "pair": pair,
            "start": start,
            "end": end,
            "interval": interval,
            "limit": limit,
            "dtmfmt": dtmfmt,
        }
        return self._request("/fx/quote/time-series", params)

    def fx_ohlc_time_series(
        self,
        pair: str,
        start: str | int | None = None,
        end: str | int | None = None,
        interval: str | None = None,
        limit: int | None = None,
        dtmfmt: str | None = None,
    ) -> dict[str, Any]:
        """
        Get OHLC (Open/High/Low/Close) time-series data for an FX pair.

        Values are based on the BID price.

        Args:
            pair: Trading pair (e.g., "EURUSD" or "EUR/USD").
            start: Time-series start (date, datetime, ISO8601, or timestamp in ms).
            end: Time-series end (date, datetime, ISO8601, or timestamp in ms).
            interval: ISO8601 duration (P1D, PT1H, or PT1M). Defaults to P1D.
            limit: Maximum data points to return (1-100).
            dtmfmt: Response datetime format ('ISO', 'TSP', or 'UTCYMD').

        Returns:
            Dict containing pair, interval, results (array of dtm/o/h/l/c), and ms.

        Example:
            >>> client.fx_ohlc_time_series(pair="EURUSD", end="2021-01-26", interval="P1D", limit=3)
            {'results': [{'dtm': '2021-01-24T00:00:00Z', 'o': 1.2145, 'h': 1.2156, 'l': 1.2134, 'c': 1.2142}, ...]}
        """
        params = {
            "pair": pair,
            "start": start,
            "end": end,
            "interval": interval,
            "limit": limit,
            "dtmfmt": dtmfmt,
        }
        return self._request("/fx/ohlc/time-series", params)

    # -------------------------------------------------------------------------
    # Admin Endpoints
    # -------------------------------------------------------------------------

    def usage(self) -> dict[str, Any]:
        """
        Fetch recent API usage data for your account.

        Returns:
            Dict containing 'usage', 'monthly_quota', 'current_period', and 'ms' keys.
            Current period includes start, end, usage, and remaining_quota.

        Example:
            >>> result = client.usage()
            >>> print(f"Remaining: {result['current_period']['remaining_quota']}")
        """
        return self._request("/usage")

    # -------------------------------------------------------------------------
    # Context Manager Support
    # -------------------------------------------------------------------------

    def __enter__(self) -> "FastForexClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()
