#!/usr/bin/env python3
"""
FastForex API Client Example Script

This script demonstrates the various capabilities of the FastForex Python client.
Set your API key via the FASTFOREX_API_KEY environment variable or pass it directly.

Usage:
    export FASTFOREX_API_KEY="your-api-key"
    python bin/example.py
"""

import os
import sys

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastforex import FastForexClient, FastForexAPIError


def main():
    # Get API key from environment
    api_key = os.environ.get("FASTFOREX_API_KEY")
    if not api_key:
        print("Error: FASTFOREX_API_KEY environment variable not set")
        print("Usage: export FASTFOREX_API_KEY='your-api-key' && python bin/example.py")
        sys.exit(1)

    # Initialize the client
    client = FastForexClient(api_key=api_key)

    try:
        # =====================================================================
        # Currency Exchange Rate Examples
        # =====================================================================
        print("=" * 60)
        print("CURRENCY EXCHANGE RATES")
        print("=" * 60)

        # Fetch a single exchange rate
        print("\n1. Fetch single rate (USD to EUR):")
        result = client.fetch_one(to="EUR")
        print(f"   1 USD = {result['result']['EUR']} EUR")
        print(f"   Updated: {result['updated']}")

        # Fetch multiple rates at once
        print("\n2. Fetch multiple rates (USD to EUR, GBP, JPY):")
        result = client.fetch_multi(to=["EUR", "GBP", "JPY"])
        for currency, rate in result["results"].items():
            print(f"   1 USD = {rate} {currency}")

        # Fetch all available rates
        print("\n3. Fetch all rates (showing first 5):")
        result = client.fetch_all()
        currencies = list(result["results"].items())[:5]
        for currency, rate in currencies:
            print(f"   1 USD = {rate} {currency}")
        print(f"   ... and {len(result['results']) - 5} more currencies")

        # Convert an amount
        print("\n4. Convert 1000 USD to EUR:")
        result = client.convert(to="EUR", amount=1000)
        converted = result["result"]["EUR"]
        rate = result["result"]["rate"]
        print(f"   1000 USD = {converted} EUR (rate: {rate})")

        # Fetch historical rates
        print("\n5. Historical rates for 2024-01-15:")
        result = client.historical(date="2024-01-15", to=["EUR", "GBP"])
        for currency, rate in result["results"].items():
            print(f"   1 USD = {rate} {currency}")

        # Fetch time series data
        print("\n6. Time series (USD to GBP, last 5 days of 2024):")
        result = client.time_series(
            to="GBP",
            start="2024-12-26",
            end="2024-12-31",
        )
        for date, rate in list(result["results"]["GBP"].items())[:5]:
            print(f"   {date}: 1 USD = {rate} GBP")

        # List supported currencies
        print("\n7. Supported currencies (showing first 5):")
        result = client.currencies()
        currencies = list(result["currencies"].items())[:5]
        for code, name in currencies:
            print(f"   {code}: {name}")
        print(f"   ... and {len(result['currencies']) - 5} more")

        # =====================================================================
        # Cryptocurrency Examples
        # =====================================================================
        print("\n" + "=" * 60)
        print("CRYPTOCURRENCY")
        print("=" * 60)

        # List crypto currencies
        print("\n8. Supported cryptocurrencies (showing first 5):")
        result = client.crypto_currencies()
        cryptos = list(result["currencies"].items())[:5]
        for code, name in cryptos:
            print(f"   {code}: {name}")
        print(f"   ... and {len(result['currencies']) - 5} more")

        # Fetch crypto prices
        print("\n9. Crypto prices:")
        result = client.crypto_fetch_prices(pairs=["BTC/USD", "ETH/USD"])
        for pair, price in result["prices"].items():
            print(f"   {pair}: ${price:,.2f}")

        # =====================================================================
        # FX Trading Examples
        # =====================================================================
        print("\n" + "=" * 60)
        print("FX TRADING")
        print("=" * 60)

        # Get FX quote
        print("\n10. Live FX quotes:")
        result = client.fx_quote(pairs=["EURUSD", "GBPUSD"])
        for pair, quote in result["quotes"].items():
            print(f"   {pair}: Bid={quote['bid']}, Ask={quote['ask']}")

        # =====================================================================
        # Account Usage
        # =====================================================================
        print("\n" + "=" * 60)
        print("ACCOUNT USAGE")
        print("=" * 60)

        print("\n11. API usage stats:")
        result = client.usage()
        period = result["current_period"]
        print(f"   Period: {period['start']} to {period['end']}")
        print(f"   Monthly quota: {result['monthly_quota']:,}")
        print(f"   Used this period: {period['usage']:,}")
        print(f"   Remaining: {period['remaining_quota']:,}")

    except FastForexAPIError as e:
        print(f"\nAPI Error: {e}")
        if e.status_code:
            print(f"Status code: {e.status_code}")
        sys.exit(1)

    finally:
        client.close()

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
