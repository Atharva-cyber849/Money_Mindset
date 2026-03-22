"""
Market Data Service - Fetches live India and US indices
Routes requests to specialized APIs with fallback chain
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

from app.core.config import settings
from app.services.api_clients import FinnhubClient, IndianMarketClient

logger = logging.getLogger(__name__)


class MarketType(str, Enum):
    """Market types supported"""
    INDIA = "india"
    US = "us"
    BOTH = "both"


class MarketDataService:
    """Service for fetching live India and US market indices"""

    # India indices symbols
    INDIA_INDICES = {
        "NIFTY_50": "^NSEI",
        "SENSEX": "^BSESN",
        "NIFTY_IT": "^CNXIT",
        "NIFTY_BANK": "^CNXBN",
    }

    # US indices symbols (ETFs)
    US_INDICES = {
        "SPY": "SPY",           # S&P 500
        "QQQ": "QQQ",           # NASDAQ 100
        "DIA": "DIA",           # Dow Jones
        "IWM": "IWM",           # Russell 2000 (Small Cap)
    }

    def __init__(self, cache_ttl: int = 300):
        """
        Initialize market data service with API clients

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_timestamps = {}

        # Initialize API clients
        self.finnhub_client = FinnhubClient(
            api_key=settings.FINNHUB_API_KEY, enabled=settings.FINNHUB_ENABLED
        )
        self.indian_market_client = IndianMarketClient(
            base_url=settings.INDIAN_MARKET_API_URL,
            api_key=settings.INDIAN_MARKET_API_KEY,
            enabled=settings.INDIAN_MARKET_ENABLED,
        )
        self.yfinance_enabled = settings.YFINANCE_ENABLED

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self._cache_timestamps:
            return False

        cache_age = (datetime.utcnow() - self._cache_timestamps[key]).total_seconds()
        return cache_age < self.cache_ttl

    def _get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            logger.info(f"Cache HIT for {key}")
            return self._cache.get(key)
        logger.info(f"Cache MISS for {key}")
        return None

    def _set_cache(self, key: str, data: Any) -> None:
        """Store data in cache"""
        self._cache[key] = data
        self._cache_timestamps[key] = datetime.utcnow()

    def _is_indian_symbol(self, symbol: str) -> bool:
        """Detect if symbol is Indian (NSE/BSE)"""
        return symbol.endswith((".NS", ".BO")) or symbol.startswith(("^NSEI", "^BSE", "^CNX"))

    def _is_us_symbol(self, symbol: str) -> bool:
        """Detect if symbol is US"""
        return not self._is_indian_symbol(symbol)

    def _get_price_india(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch Indian stock price with fallback chain"""
        try:
            # Try Indian Market API first
            if self.indian_market_client.enabled:
                quote = self.indian_market_client.get_quote(symbol)
                if quote and quote.get("source") != "mock":
                    logger.info(f"Fetched {symbol} from Indian Market API")
                    return quote
        except Exception as e:
            logger.warning(f"Indian Market API failed for {symbol}: {str(e)}")

        # Fallback to yfinance
        if self.yfinance_enabled:
            try:
                return self._fetch_from_yfinance(symbol)
            except Exception as e:
                logger.warning(f"yfinance failed for {symbol}: {str(e)}")

        # Last resort: mock data
        return self.indian_market_client._get_mock_quote(symbol)

    def _get_price_us(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch US stock price with fallback chain"""
        try:
            # Try Finnhub first
            if self.finnhub_client.enabled:
                quote = self.finnhub_client.get_quote(symbol)
                if quote and quote.get("source") != "mock":
                    logger.info(f"Fetched {symbol} from Finnhub")
                    return quote
        except Exception as e:
            logger.warning(f"Finnhub failed for {symbol}: {str(e)}")

        # Fallback to yfinance
        if self.yfinance_enabled:
            try:
                return self._fetch_from_yfinance(symbol)
            except Exception as e:
                logger.warning(f"yfinance failed for {symbol}: {str(e)}")

        # Last resort: mock data
        return self.finnhub_client._get_mock_quote(symbol)

    def _fetch_from_yfinance(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from yfinance"""
        ticker = yf.Ticker(symbol)
        info = ticker.info
        history = ticker.history(period="1d")

        if history.empty:
            raise ValueError(f"No data from yfinance for {symbol}")

        latest = history.iloc[-1]
        current_price = float(latest["Close"])
        previous_close = float(info.get("previousClose", current_price))
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close > 0 else 0

        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "timestamp": datetime.now(),
            "source": "yfinance",
        }

    def get_index_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch live index data for a single symbol

        Args:
            symbol: Index symbol (e.g., "^NSEI" for NIFTY 50)

        Returns:
            Dict with index data or None on error
        """
        cache_key = f"index_{symbol}"

        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return {**cached_data, "from_cache": True}

        try:
            # Route to appropriate API based on symbol type
            if self._is_indian_symbol(symbol):
                quote = self._get_price_india(symbol)
            else:
                quote = self._get_price_us(symbol)

            if not quote:
                return self._get_mock_data(symbol)

            data = {
                "symbol": symbol,
                "name": self._get_index_name(symbol),
                "current_price": quote.get("price", 0),
                "previous_close": quote.get("price", 0) - quote.get("change", 0),
                "percentage_change": quote.get("change_percent", 0),
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "from_cache": False,
            }

            # Store in cache
            self._set_cache(cache_key, {k: v for k, v in data.items() if k != "from_cache"})

            return data

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return self._get_mock_data(symbol)

    def get_all_indices(self, market: MarketType = MarketType.BOTH) -> Dict[str, Any]:
        """
        Fetch all indices for specified market(s)

        Args:
            market: MarketType.INDIA, MarketType.US, or MarketType.BOTH

        Returns:
            Dict with all indices data
        """
        cache_key = f"all_indices_{market.value}"

        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return {
                "indices": cached_data,
                "market": market.value,
                "cached": True,
                "cache_expires_at": (
                    self._cache_timestamps[cache_key] + timedelta(seconds=self.cache_ttl)
                ).isoformat() + "Z",
            }

        indices = []

        # Fetch India indices if requested
        if market in (MarketType.INDIA, MarketType.BOTH):
            for name, symbol in self.INDIA_INDICES.items():
                data = self.get_index_data(symbol)
                if data:
                    indices.append(data)

        # Fetch US indices if requested
        if market in (MarketType.US, MarketType.BOTH):
            for name, symbol in self.US_INDICES.items():
                data = self.get_index_data(symbol)
                if data:
                    indices.append(data)

        result = {
            "indices": indices,
            "market": market.value,
            "cached": False,
            "cache_expires_at": (
                datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            ).isoformat() + "Z",
        }

        # Cache the result
        if indices:
            self._set_cache(cache_key, indices)

        return result

    def get_indian_indices(self) -> Dict[str, Any]:
        """
        Fetch all India indices

        Returns:
            Dict with India indices data
        """
        return self.get_all_indices(MarketType.INDIA)

    def get_us_indices(self) -> Dict[str, Any]:
        """
        Fetch all US indices

        Returns:
            Dict with US indices data
        """
        return self.get_all_indices(MarketType.US)

    def _get_index_name(self, symbol: str) -> str:
        """Get human-readable name for index symbol"""
        name_map = {
            # India
            "^NSEI": "NIFTY 50",
            "^BSESN": "SENSEX",
            "^CNXIT": "NIFTY IT",
            "^CNXBN": "NIFTY BANK",
            # US
            "SPY": "S&P 500 (SPY)",
            "QQQ": "NASDAQ 100 (QQQ)",
            "DIA": "Dow Jones (DIA)",
            "IWM": "Russell 2000 (IWM)",
        }
        return name_map.get(symbol, symbol)

    def _get_mock_data(self, symbol: str) -> Dict[str, Any]:
        """Return mock data when API fails"""
        mock_data = {
            # India
            "^NSEI": {
                "symbol": "^NSEI",
                "name": "NIFTY 50",
                "current_price": 20150.50,
                "previous_close": 20120.00,
                "percentage_change": 0.15,
                "from_cache": False,
            },
            "^BSESN": {
                "symbol": "^BSESN",
                "name": "SENSEX",
                "current_price": 67150.25,
                "previous_close": 67100.00,
                "percentage_change": 0.07,
                "from_cache": False,
            },
            "^CNXIT": {
                "symbol": "^CNXIT",
                "name": "NIFTY IT",
                "current_price": 43200.00,
                "previous_close": 43000.00,
                "percentage_change": 0.46,
                "from_cache": False,
            },
            "^CNXBN": {
                "symbol": "^CNXBN",
                "name": "NIFTY BANK",
                "current_price": 52800.75,
                "previous_close": 52600.00,
                "percentage_change": 0.39,
                "from_cache": False,
            },
            # US
            "SPY": {
                "symbol": "SPY",
                "name": "S&P 500 (SPY)",
                "current_price": 585.45,
                "previous_close": 583.20,
                "percentage_change": 0.39,
                "from_cache": False,
            },
            "QQQ": {
                "symbol": "QQQ",
                "name": "NASDAQ 100 (QQQ)",
                "current_price": 425.30,
                "previous_close": 423.10,
                "percentage_change": 0.52,
                "from_cache": False,
            },
            "DIA": {
                "symbol": "DIA",
                "name": "Dow Jones (DIA)",
                "current_price": 418.75,
                "previous_close": 417.30,
                "percentage_change": 0.35,
                "from_cache": False,
            },
            "IWM": {
                "symbol": "IWM",
                "name": "Russell 2000 (IWM)",
                "current_price": 220.15,
                "previous_close": 219.80,
                "percentage_change": 0.16,
                "from_cache": False,
            },
        }

        data = mock_data.get(symbol, {
            "symbol": symbol,
            "name": self._get_index_name(symbol),
            "current_price": 0,
            "previous_close": 0,
            "percentage_change": 0,
            "from_cache": False,
        })

        data["last_updated"] = datetime.utcnow().isoformat() + "Z"
        return data

    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Market data cache cleared")


# Global instance
market_data_service = MarketDataService()
