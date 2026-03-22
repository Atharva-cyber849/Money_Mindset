"""Indian Stock Market API Client for NSE/BSE data"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import time

import pandas as pd
import requests

from .base_client import APIClient

logger = logging.getLogger(__name__)

# Mock data for Indian stocks
MOCK_INDIAN_STOCKS = {
    "RELIANCE.NS": {"price": 2835.50, "change": 50.25, "change_percent": 1.81},
    "TCS.NS": {"price": 3645.75, "change": -35.50, "change_percent": -0.97},
    "INFY.NS": {"price": 1895.30, "change": 75.20, "change_percent": 4.13},
    "WIPRO.NS": {"price": 445.85, "change": 12.50, "change_percent": 2.88},
    "HDFCBANK.NS": {"price": 1685.25, "change": 28.75, "change_percent": 1.73},
    "ICICIBANK.NS": {"price": 1078.90, "change": -15.85, "change_percent": -1.45},
    "BAJAJFINSV.NS": {"price": 1598.50, "change": 22.50, "change_percent": 1.43},
    "SBIN.NS": {"price": 845.35, "change": 18.65, "change_percent": 2.26},
    "MARUTI.NS": {"price": 9285.75, "change": -125.50, "change_percent": -1.33},
    "BHARTIARTL.NS": {"price": 1125.80, "change": 45.20, "change_percent": 4.19},
}

MOCK_INDIAN_INDICES = {
    "^NSEI": {"price": 20150.50, "change": 285.75, "change_percent": 1.44},
    "^BSESN": {"price": 66395.25, "change": 950.50, "change_percent": 1.45},
    "^CNXIT": {"price": 40285.30, "change": -325.40, "change_percent": -0.80},
    "^CNXBN": {"price": 48925.85, "change": 625.60, "change_percent": 1.30},
}


class IndianMarketClient(APIClient):
    """Indian Stock Market API client for NSE/BSE data

    Endpoint: https://stock.indianapi.in/
    Features: NSE/BSE support, real-time data, company data
    """

    def __init__(self, base_url: str = "", api_key: str = "", enabled: bool = True):
        """Initialize Indian Market client

        Args:
            base_url: Base URL for Indian Market API
            api_key: API key for authentication
            enabled: Whether this client is enabled
        """
        super().__init__(base_url=base_url, enabled=enabled)
        self.api_key = api_key
        self.timeout = 10
        self.name = "IndianMarketClient"

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current quote for Indian stock via /stock endpoint

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS', 'TCS', 'Reliance')

        Returns:
            Quote data or None if failed
        """
        if not self.enabled or not self.base_url:
            return self._get_mock_quote(symbol)

        try:
            start_time = time.time()

            # Extract company name from symbol (remove .NS, .BO)
            company_name = self._extract_company_name(symbol)

            # Call /stock endpoint with company name
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key

            response = requests.get(
                f"{self.base_url}/stock",
                params={"name": company_name},
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            latency = int((time.time() - start_time) * 1000)

            # Check if response is successful
            if data and "currentPrice" in data:
                # Try to get NSE price, fallback to BSE
                nse_price = data.get("currentPrice", {}).get("NSE")
                bse_price = data.get("currentPrice", {}).get("BSE")
                price = nse_price or bse_price or 0

                quote = {
                    "symbol": symbol,
                    "price": float(price),
                    "change": float(data.get("net_change", 0)),
                    "change_percent": float(data.get("percentChange", 0)),
                    "timestamp": datetime.now(),
                    "source": "indian_market_api",
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

    def get_company_data(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Fetch complete company data including financials and metrics

        Args:
            company_name: Company name (e.g., 'Reliance', 'TCS', 'INFOSYS')

        Returns:
            Complete company data or None if failed
        """
        if not self.enabled or not self.base_url:
            return None

        try:
            start_time = time.time()

            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key

            response = requests.get(
                f"{self.base_url}/stock",
                params={"name": company_name},
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            latency = int((time.time() - start_time) * 1000)

            if data:
                self._log_success("get_company_data", company_name, latency)
                return data

            return None

        except Exception as e:
            self._log_error("get_company_data", e)
            return None

    def search_industry(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search for companies within an industry

        Args:
            query: Industry or company search term

        Returns:
            List of matching companies or None
        """
        if not self.enabled or not self.base_url:
            return None

        try:
            start_time = time.time()

            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key

            response = requests.get(
                f"{self.base_url}/industry_search",
                params={"query": query},
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            latency = int((time.time() - start_time) * 1000)

            if isinstance(data, list):
                self._log_success("search_industry", query, latency)
                return data

            return None

        except Exception as e:
            self._log_error("search_industry", e)
            return None

    def get_trending_stocks(self) -> Optional[Dict[str, Any]]:
        """Get trending stocks (top gainers and losers)

        Returns:
            Trending stocks data or None
        """
        if not self.enabled or not self.base_url:
            return None

        try:
            start_time = time.time()

            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key

            response = requests.get(
                f"{self.base_url}/trending",
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            latency = int((time.time() - start_time) * 1000)

            if data:
                self._log_success("get_trending_stocks", "all", latency)
                return data

            return None

        except Exception as e:
            self._log_error("get_trending_stocks", e)
            return None

    def get_historical_data(
        self, symbol: str, start_date: datetime = None, end_date: datetime = None, period: str = "1yr"
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data for a stock

        Args:
            symbol: Stock symbol or company name
            start_date: Start date (unused with period-based API)
            end_date: End date (unused with period-based API)
            period: Period string (1m, 6m, 1yr, 3yr, 5yr, 10yr, max)

        Returns:
            DataFrame with historical price data or None
        """
        if not self.enabled or not self.base_url:
            return self._get_mock_historical(symbol)

        try:
            start_time = time.time()

            company_name = self._extract_company_name(symbol)

            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key

            response = requests.get(
                f"{self.base_url}/historical_data",
                params={
                    "stock_name": company_name,
                    "period": period,
                    "filter": "price"
                },
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            latency = int((time.time() - start_time) * 1000)

            if data and "datasets" in data:
                # Extract price data from datasets
                for dataset in data["datasets"]:
                    if dataset.get("metric") == "Price":
                        values = dataset.get("values", [])
                        if values:
                            dates = []
                            prices = []
                            for val in values:
                                if len(val) >= 2:
                                    dates.append(pd.to_datetime(val[0]))
                                    prices.append(float(val[1]))

                            if dates and prices:
                                df = pd.DataFrame({
                                    "date": dates,
                                    "close": prices,
                                    "open": prices,  # Simplified
                                    "high": [p * 1.02 for p in prices],
                                    "low": [p * 0.98 for p in prices],
                                    "volume": [1000000] * len(prices)
                                })
                                df.set_index("date", inplace=True)
                                self._log_success("get_historical_data", symbol, latency)
                                return df

            return self._get_mock_historical(symbol)

        except Exception as e:
            self._log_error("get_historical_data", e)
            return self._get_mock_historical(symbol)

    def get_quarterly_results(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get historical quarterly results

        Args:
            symbol: Stock symbol or company name

        Returns:
            Quarterly financial data or None
        """
        if not self.enabled or not self.base_url:
            return None

        try:
            start_time = time.time()

            company_name = self._extract_company_name(symbol)

            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key

            response = requests.get(
                f"{self.base_url}/historical_stats",
                params={
                    "stock_name": company_name,
                    "stats": "quarter_results"
                },
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            latency = int((time.time() - start_time) * 1000)

            if data:
                self._log_success("get_quarterly_results", symbol, latency)
                return data

            return None

        except Exception as e:
            self._log_error("get_quarterly_results", e)
            return None

    def _extract_company_name(self, symbol: str) -> str:
        """Extract company name from symbol

        Examples:
            RELIANCE.NS → Reliance
            RELIANCE.BO → Reliance
            TCS → TCS
            ^NSEI → Nifty (index)
        """
        # Remove exchange suffixes
        base = symbol.replace(".NS", "").replace(".BO", "")

        # Map indices to names
        index_map = {
            "^NSEI": "Nifty",
            "^BSESN": "Sensex",
            "^CNXIT": "Nifty IT",
            "^CNXBN": "Nifty Bank"
        }

        return index_map.get(base, base)

    def _get_mock_quote(self, symbol: str) -> Dict[str, Any]:
        """Return mock quote data"""
        # Try exact match first
        mock_data = MOCK_INDIAN_STOCKS.get(symbol) or MOCK_INDIAN_INDICES.get(symbol)

        if not mock_data:
            # Try without suffix
            base_symbol = symbol.replace(".NS", "").replace(".BO", "")
            mock_data = MOCK_INDIAN_STOCKS.get(f"{base_symbol}.NS") or MOCK_INDIAN_INDICES.get(symbol)

        if not mock_data:
            # Generate generic mock data
            mock_data = {"price": 1000.0, "change": 0.0, "change_percent": 0.0}

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
        prices = [1000 + i * 5 for i in range(60)]

        df = pd.DataFrame(
            {
                "date": dates,
                "open": prices,
                "high": [p * 1.02 for p in prices],
                "low": [p * 0.98 for p in prices],
                "close": prices,
                "volume": [5000000] * 60,
            }
        )
        df.set_index("date", inplace=True)
        return df


