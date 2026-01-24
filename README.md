# fastFOREX Currency Exchange Rate API Client for Python

A Python SDK for the [fastFOREX.io](https://www.fastforex.io) currency and cryptocurrency exchange rate API.

## Features

- **Currency Exchange Rates**: Fetch single, multiple, or all currency rates
- **Currency Conversion**: Convert amounts between currencies
- **Historical Data**: Access historical exchange rates back to 1970
- **Time Series**: Get daily rate data over date ranges
- **Cryptocurrency**: 500+ cryptocurrencies with real-time prices
- **FX Trading**: Live bid/ask quotes, OHLC data for 2,300+ trading pairs
- **Usage Tracking**: Monitor your API quota and usage

You'll need an API key to use the API client. [Get a Free Trial API Key](https://console.fastforex.io).

- 160+ Currencies
- 500+ Crypto Currencies
- 2,300+ FX trading pairs
- Up 55 years of historical data

## Installation

```bash
pip install -r requirements.txt
```

Then copy the `fastforex` package to your project, or install directly:

```bash
pip install -e .
```

## Quick Start

```python
from fastforex import FastForexClient

# Initialize the client
client = FastForexClient(api_key="your-api-key")

# Fetch a single exchange rate
result = client.fetch_one(to="EUR")
print(f"1 USD = {result['result']['EUR']} EUR")

# Convert an amount
result = client.convert(to="EUR", amount=100)
print(f"100 USD = {result['result']['EUR']} EUR")

# Don't forget to close the client when done
client.close()
```

### Using as Context Manager

```python
from fastforex import FastForexClient

with FastForexClient(api_key="your-api-key") as client:
    result = client.fetch_one(to="EUR")
    print(result)
```

## API Reference

### Currency Methods

#### `fetch_one(to, from_currency=None)`
Fetch a single currency exchange rate.

```python
result = client.fetch_one(to="EUR", from_currency="USD")
# {'base': 'USD', 'result': {'EUR': 0.8799}, 'updated': '2025-01-24T12:00:00Z', 'ms': 4}
```

#### `fetch_multi(to, from_currency=None)`
Fetch multiple currency rates at once.

```python
result = client.fetch_multi(to=["EUR", "GBP", "JPY"])
# {'base': 'USD', 'results': {'EUR': 0.8799, 'GBP': 0.7642, 'JPY': 143.52}, ...}
```

#### `fetch_all(from_currency=None)`
Fetch all available currency rates (130+ currencies).

```python
result = client.fetch_all()
print(len(result['results']))  # 130+
```

#### `fetch_many_to_one(from_currencies, to)`
Fetch rates from multiple source currencies to a single target.

```python
result = client.fetch_many_to_one(from_currencies=["JPY", "CHF", "AUD"], to="USD")
# {'to': 'USD', 'from': {'JPY': 0.00679, 'CHF': 1.2539, 'AUD': 0.65962}, ...}
```

#### `fetch_matrix(from_currencies, to_currencies)`
Fetch a matrix of multiple from/to currency pairs.

```python
result = client.fetch_matrix(
    from_currencies=["USD", "EUR"],
    to_currencies=["GBP", "JPY"]
)
# {'matrix': {'USD': {'GBP': 0.74, 'JPY': 147.5}, 'EUR': {'GBP': 0.84, 'JPY': 167.5}}, ...}
```

#### `convert(to, amount, from_currency=None, precision=None)`
Convert an amount from one currency to another.

```python
result = client.convert(to="EUR", amount=1000, precision=4)
# {'base': 'USD', 'amount': 1000, 'result': {'EUR': 879.90, 'rate': 0.8799}, ...}
```

#### `historical(date, from_currency=None, to=None)`
Fetch exchange rates for a historical date.

```python
result = client.historical(date="2024-01-15", to=["EUR", "GBP"])
# {'date': '2024-01-15', 'base': 'USD', 'results': {'EUR': 0.8795, 'GBP': 0.7851}, ...}
```

#### `time_series(to, start, end, from_currency=None, interval=None)`
Fetch time-series data for a currency pair.

```python
result = client.time_series(to="EUR", start="2024-01-01", end="2024-01-07")
# {'results': {'EUR': {'2024-01-01': 0.88, '2024-01-02': 0.879, ...}}, ...}
```

#### `currencies()`
List all supported physical currencies.

```python
result = client.currencies()
# {'currencies': {'USD': 'United States Dollar', 'EUR': 'Euro', ...}, 'ms': 3}
```

### Cryptocurrency Methods

#### `crypto_currencies()`
List 500+ supported cryptocurrencies.

```python
result = client.crypto_currencies()
# {'currencies': {'BTC': 'Bitcoin', 'ETH': 'Ethereum', ...}, 'ms': 8}
```

#### `crypto_pairs()`
List 400+ supported cryptocurrency pairs.

```python
result = client.crypto_pairs()
# {'pairs': {'BTC/USD': {'base': 'BTC', 'quote': 'USD'}, ...}, 'ms': 8}
```

#### `crypto_fetch_prices(pairs)`
Fetch real-time cryptocurrency prices.

```python
result = client.crypto_fetch_prices(pairs=["BTC/USD", "ETH/USD"])
# {'prices': {'BTC/USD': 42500.21, 'ETH/USD': 2250.50}, 'ms': 8}
```

### FX Trading Methods

#### `fx_pairs()`
List ~2,300 supported FX trading pairs.

```python
result = client.fx_pairs()
# {'pairs': {'EUR/USD': {'base': 'EUR', 'quote': 'USD', 'alt': 'EURUSD'}, ...}}
```

#### `fx_pairs_historical_limits(interval=None, price=None)`
Get earliest available historical data for FX pairs.

```python
result = client.fx_pairs_historical_limits(interval="P1D", price="bid")
# {'pairs': {'EURUSD': '1976-01-02T00:00:00Z', ...}}
```

#### `fx_pairs_quote_sizes()`
List FX pairs with non-standard quote sizes.

```python
result = client.fx_pairs_quote_sizes()
# {'sizes': {'IRRUSD': 100000, 'VNDUSD': 10000}, 'ms': 12}
```

#### `fx_currencies()`
List supported FX trading currencies.

```python
result = client.fx_currencies()
# {'currencies': {'EUR': 'Euro', 'USD': 'United States Dollar', ...}}
```

#### `fx_quote(pairs)`
Get live bid/ask quotes for FX trading pairs.

```python
result = client.fx_quote(pairs=["EURUSD", "GBPUSD"])
# {'quotes': {'EURUSD': {'bid': 1.0850, 'ask': 1.0851, 'tsp': 1706100000000, 'size': 1}, ...}}
```

#### `fx_quote_time_series(pair, start=None, end=None, interval=None, limit=None, dtmfmt=None)`
Get bid/ask time-series data for an FX pair.

```python
result = client.fx_quote_time_series(
    pair="EURUSD",
    end="2024-01-15",
    interval="PT1H",
    limit=24
)
# {'results': [{'dtm': '2024-01-15T23:00:00Z', 'bid': 1.0850, 'ask': 1.0851}, ...]}
```

#### `fx_ohlc_time_series(pair, start=None, end=None, interval=None, limit=None, dtmfmt=None)`
Get OHLC time-series data for an FX pair.

```python
result = client.fx_ohlc_time_series(
    pair="EURUSD",
    end="2024-01-15",
    interval="P1D",
    limit=5
)
# {'results': [{'dtm': '2024-01-15T00:00:00Z', 'o': 1.08, 'h': 1.09, 'l': 1.07, 'c': 1.085}, ...]}
```

### Account Methods

#### `usage()`
Get API usage statistics.

```python
result = client.usage()
# {
#     'monthly_quota': 500000,
#     'current_period': {'start': '2024-01-01', 'end': '2024-01-31', 'usage': 1234, 'remaining_quota': 498766},
#     'usage': {'2024-01-20': 100, '2024-01-21': 150, ...}
# }
```

## Error Handling

The client raises specific exceptions for different error types:

```python
from fastforex import (
    FastForexClient,
    FastForexError,
    FastForexAPIError,
    FastForexAuthError,
    FastForexRateLimitError,
    FastForexNotFoundError,
)

client = FastForexClient(api_key="your-api-key")

try:
    result = client.fetch_one(to="EUR")
except FastForexAuthError as e:
    print(f"Authentication failed: {e}")
except FastForexRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except FastForexNotFoundError as e:
    print(f"Resource not found: {e}")
except FastForexAPIError as e:
    print(f"API error ({e.status_code}): {e}")
except FastForexError as e:
    print(f"General error: {e}")
```

## Configuration

### Base URL

By default, the client uses the production API. You can switch to the beta API:

```python
client = FastForexClient(
    api_key="your-api-key",
    base_url=FastForexClient.BETA_URL
)
```

### Timeout

Set a custom request timeout (default is 30 seconds):

```python
client = FastForexClient(
    api_key="your-api-key",
    timeout=60
)
```

## Example Script

See `bin/example.py` for a complete example demonstrating all features:

```bash
export FASTFOREX_API_KEY="your-api-key"
python bin/example.py
```

## Requirements

- Python 3.10+
- requests

## License

Apache 2.0 - See the FastForex [Terms of Service](https://www.fastforex.io/terms-of-sale) for API usage terms.

## Links

- [FastForex Website](https://www.fastforex.io)
- [API Documentation](https://fastforex.readme.io)
