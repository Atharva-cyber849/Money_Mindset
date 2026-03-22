#!/usr/bin/env python3
"""
Data Pre-fetching Utility - Pre-fetch historical data for Paper Trading
Use this to cache historical market data as static JSON for competition demo
(zero API dependency during demo)
"""

import json
import os
from datetime import datetime
import yfinance as yf
from pathlib import Path

# Configuration
DATA_DIR = Path(__file__).parent / "data" / "paper_trading"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Historical periods for demo
DEMO_PERIODS = {
    "2024_ytd": ("2024-01-01", datetime.now().strftime("%Y-%m-%d")),
    "2023_full": ("2023-01-01", "2023-12-31"),
    "2022_2024": ("2022-01-01", "2024-12-31"),
    "covid_crash": ("2020-01-01", "2020-12-31"),
    "recovery": ("2020-03-01", "2021-12-31"),
}

# Indian stocks (NIFTY 50 sample)
INDIA_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "WIPRO.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "BAJAJFINSV.NS", "SBIN.NS", "MARUTI.NS", "BHARTIARTL.NS"
]

# US stocks (S&P 500 sample)
US_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "NVDA", "TSLA", "JPM", "V", "JNJ"
]

# Indices
INDIA_INDICES = ["^NSEI", "^BSESN"]
US_INDICES = ["SPY", "QQQ", "DIA"]


def fetch_data(symbol: str, start_date: str, end_date: str) -> dict:
    """Fetch OHLCV data from yfinance"""
    try:
        print(f"  Fetching {symbol}...", end=" ", flush=True)
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if df.empty:
            print("⚠️ No data")
            return {}

        # Convert to JSON-serializable format
        data = {
            "symbol": symbol,
            "period_start": start_date,
            "period_end": end_date,
            "records": []
        }

        for date, row in df.iterrows():
            data["records"].append({
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0,
            })

        print(f"✓ ({len(data['records'])} days)")
        return data

    except Exception as e:
        print(f"✗ Error: {e}")
        return {}


def prefetch_india_data():
    """Pre-fetch Indian market data"""
    print("\n🇮🇳 Fetching Indian Market Data")
    print("=" * 50)

    for period_name, (start, end) in DEMO_PERIODS.items():
        print(f"\n📅 Period: {period_name} ({start} to {end})")

        # Indices
        print("  Indices:")
        indices_data = {}
        for symbol in INDIA_INDICES:
            data = fetch_data(symbol, start, end)
            if data:
                indices_data[symbol] = data

        # Stocks
        print("  Stocks:")
        stocks_data = {}
        for symbol in INDIA_STOCKS:
            data = fetch_data(symbol, start, end)
            if data:
                stocks_data[symbol] = data

        # Save to file
        output = {
            "market": "india",
            "period": period_name,
            "date_range": {"start": start, "end": end},
            "indices": indices_data,
            "stocks": stocks_data,
            "fetched_at": datetime.utcnow().isoformat()
        }

        filename = DATA_DIR / f"india_{period_name}.json"
        with open(filename, "w") as f:
            json.dump(output, f, indent=2)
        print(f"  ✅ Saved to {filename}")


def prefetch_us_data():
    """Pre-fetch US market data"""
    print("\n🇺🇸 Fetching US Market Data")
    print("=" * 50)

    for period_name, (start, end) in DEMO_PERIODS.items():
        print(f"\n📅 Period: {period_name} ({start} to {end})")

        # Indices
        print("  Indices:")
        indices_data = {}
        for symbol in US_INDICES:
            data = fetch_data(symbol, start, end)
            if data:
                indices_data[symbol] = data

        # Stocks
        print("  Stocks:")
        stocks_data = {}
        for symbol in US_STOCKS:
            data = fetch_data(symbol, start, end)
            if data:
                stocks_data[symbol] = data

        # Save to file
        output = {
            "market": "us",
            "period": period_name,
            "date_range": {"start": start, "end": end},
            "indices": indices_data,
            "stocks": stocks_data,
            "fetched_at": datetime.utcnow().isoformat()
        }

        filename = DATA_DIR / f"us_{period_name}.json"
        with open(filename, "w") as f:
            json.dump(output, f, indent=2)
        print(f"  ✅ Saved to {filename}")


def prefetch_latest_prices():
    """Pre-fetch current prices for all stocks"""
    print("\n💰 Fetching Latest Prices")
    print("=" * 50)

    prices = {
        "india": {},
        "us": {},
        "fetched_at": datetime.utcnow().isoformat()
    }

    print("India stocks:")
    for symbol in INDIA_STOCKS:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                price = float(data["Close"].iloc[-1])
                prices["india"][symbol] = price
                print(f"  {symbol}: ₹{price:.2f}")
        except Exception as e:
            print(f"  {symbol}: ⚠️ Error - {e}")

    print("\nUS stocks:")
    for symbol in US_STOCKS:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                price = float(data["Close"].iloc[-1])
                prices["us"][symbol] = price
                print(f"  {symbol}: ${price:.2f}")
        except Exception as e:
            print(f"  {symbol}: ⚠️ Error - {e}")

    # Save prices
    filename = DATA_DIR / "latest_prices.json"
    with open(filename, "w") as f:
        json.dump(prices, f, indent=2)
    print(f"\n✅ Saved to {filename}")


if __name__ == "__main__":
    print("📊 Money Mindset - Paper Trading Data Pre-fetcher")
    print("=" * 50)
    print(f"Output directory: {DATA_DIR}")

    try:
        import pandas as pd  # Required for yfinance
        prefetch_india_data()
        prefetch_us_data()
        prefetch_latest_prices()

        print("\n" + "=" * 50)
        print("✅ Data pre-fetching complete!")
        print(f"📁 All data saved to: {DATA_DIR}")
        print("\nFor competition demo:")
        print("  1. Deploy with these JSON files")
        print("  2. Paper trading reads from JSON (zero API calls)")
        print("  3. Zero latency, 100% reliable")

    except ImportError:
        print("❌ Missing dependency: pandas")
        print("   Install: pip install pandas yfinance")
    except Exception as e:
        print(f"❌ Error: {e}")
