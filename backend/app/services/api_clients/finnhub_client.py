"""Finnhub API Client for US market data"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
import time

import pandas as pd
import requests

from .base_client import APIClient

logger = logging.getLogger(__name__)

# Mock data for fallback
MOCK_US_STOCKS = {
    "AAPL": {"price": 185.50, "change": 2.50, "change_percent": 1.37},
    "MSFT": {"price": 420.75, "change": -1.25, "change_percent": -0.30},
    "GOOGL": {"price": 155.30, "change": 3.10, "change_percent": 2.04},
    "AMZN": {"price": 195.90, "change": 1.85, "change_percent": 0.96},
    "META": {"price": 528.25, "change": 5.50, "change_percent": 1.05},
    "NVDA": {"price": 912.50, "change": -8.75, "change_percent": -0.95},
    "TSLA": {"price": 245.80, "change": 2.40, "change_percent": 0.99},
    "JPM": {"price": 198.60, "change": 0.50, "change_percent": 0.25},
    "V": {"price": 289.75, "change": 1.50, "change_percent": 0.52},
    "JNJ": {"price": 156.30, "change": -0.75, "change_percent": -0.48},
}

MOCK_US_INDICES = {
    "SPY": {"price": 480.50, "change": 2.50, "change_percent": 0.52},
    "QQQ": {"price": 385.75, "change": -1.25, "change_percent": -0.32},
    "DIA": {"price": 395.30, "change": 1.50, "change_percent": 0.38},
    "IWM": {"price": 198.90, "change": -0.85, "change_percent": -0.43},
}


class FinnhubClient(APIClient):
    """Finnhub API client for US market data"""

    def __init__(self, api_key: str = "", enabled: bool = True):
        """Initialize Finnhub client

        Args:
            api_key: Finnhub API key
            enabled: Whether this client is enabled
        """
        super().__init__(
            api_key=api_key, base_url="https://finnhub.io/api/v1", enabled=enabled
        )
        self.timeout = 10
        self.max_retries = 2

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current quote from Finnhub

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Quote data or None if failed
        """
        if not self.enabled or not self.api_key:
            return self._get_mock_quote(symbol)

        try:
            start_time = time.time()
            params = {"symbol": symbol, "token": self.api_key}

            response = requests.get(
                f"{self.base_url}/quote", params=params, timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            latency = int((time.time() - start_time) * 1000)

            if data and "c" in data:
                quote = {
                    "symbol": symbol,
                    "price": float(data.get("c", 0)),
                    "change": float(data.get("d", 0)),
                    "change_percent": float(data.get("dp", 0)),
                    "timestamp": datetime.fromtimestamp(data.get("t", int(time.time()))),
                    "source": "finnhub",
                }
                self._log_success("get_quote", symbol, latency)
                return quote

            return self._get_mock_quote(symbol)

        except requests.exceptions.RequestException as e:
            self._log_error("get_quote", e)
            return self._get_mock_quote(symbol)
        except Exception as e:
            self._log_error("get_quote", e)
            return self._get_mock_quote(symbol)

    def get_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """Fetch historical OHLCV data from Finnhub

        Args:
            symbol: Stock symbol
            start_date: Start date for history
            end_date: End date for history

        Returns:
            DataFrame with OHLCV data or None if failed
        """
        if not self.enabled or not self.api_key:
            return self._get_mock_historical(symbol)

        try:
            start_time = time.time()
            resolution = "D"  # Daily

            # Finnhub API parameters
            params = {
                "symbol": symbol,
                "resolution": resolution,
                "from": int(start_date.timestamp()),
                "to": int(end_date.timestamp()),
                "token": self.api_key,
            }

            response = requests.get(
                f"{self.base_url}/stock/candle", params=params, timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            latency = int((time.time() - start_time) * 1000)

            if data.get("s") == "ok" and "c" in data:
                df = pd.DataFrame(
                    {
                        "date": pd.to_datetime(data["t"], unit="s"),
                        "open": data["o"],
                        "high": data["h"],
                        "low": data["l"],
                        "close": data["c"],
                        "volume": data.get("v", [0] * len(data["c"])),
                    }
                )
                df.set_index("date", inplace=True)
                self._log_success("get_historical_data", symbol, latency)
                return df

            return self._get_mock_historical(symbol)

        except Exception as e:
            self._log_error("get_historical_data", e)
            return self._get_mock_historical(symbol)

    def _get_mock_quote(self, symbol: str) -> Dict[str, Any]:
        """Return mock quote data"""
        mock_data = MOCK_US_STOCKS.get(symbol) or MOCK_US_INDICES.get(symbol)

        if not mock_data:
            # Generate generic mock data
            mock_data = {"price": 100.0, "change": 0.0, "change_percent": 0.0}

        return {
            "symbol": symbol,
            "price": mock_data["price"],
            "change": mock_data["change"],
            "change_percent": mock_data["change_percent"],
            "timestamp": datetime.now(),
            "source": "mock",
        }

    def _get_mock_historical(self, symbol: str) -> pd.DataFrame:
        """Return mock historical data"""
        # Generate mock OHLCV data for the past 60 days
        dates = pd.date_range(end=datetime.now(), periods=60, freq="D")
        prices = [100 + i * 0.5 for i in range(60)]

        df = pd.DataFrame(
            {
                "date": dates,
                "open": prices,
                "high": [p * 1.02 for p in prices],
                "low": [p * 0.98 for p in prices],
                "close": prices,
                "volume": [1000000] * 60,
            }
        )
        df.set_index("date", inplace=True)
        return df
