"""
Market Data Service - Fetches live India and US indices
Routes requests to specialized APIs with fallback chain
"""
import yfinance as yf
import pandas as pd
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
        "NIFTY_BANK": "^NSEBANK",
    }

    # yfinance aliases for symbols that may vary or be retired.
    YFINANCE_SYMBOL_ALIASES = {
        "^CNXBN": ["^NSEBANK"],
        "^NSEBANK": ["^CNXBN"],
        "^CNXIT": ["NIFTY_IT.NS"],
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
        return symbol.endswith((".NS", ".BO")) or symbol.startswith(("^NSEI", "^BSE", "^CNX", "^NSE"))

    def _is_us_symbol(self, symbol: str) -> bool:
        """Detect if symbol is US"""
        return not self._is_indian_symbol(symbol)

    def _get_price_india(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch Indian stock price with fallback chain"""
        # Index tickers (e.g., ^NSEI, ^BSESN, ^CNXIT, ^CNXBN) should not go through
        # stock-name based APIs because they can map to the wrong instrument.
        is_index_symbol = symbol.startswith("^")

        if is_index_symbol:
            if self.yfinance_enabled:
                try:
                    quote = self._fetch_from_yfinance(symbol)
                    if quote:
                        logger.info(f"Fetched index {symbol} from yfinance")
                        return quote
                except Exception as e:
                    logger.warning(f"yfinance failed for index {symbol}: {str(e)}")

            # Last resort for index symbols
            return self._get_mock_data(symbol)

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
        """Fetch data from yfinance with alias fallbacks for fragile symbols."""
        candidates = [symbol, *self.YFINANCE_SYMBOL_ALIASES.get(symbol, [])]
        last_error: Optional[Exception] = None

        for candidate in candidates:
            try:
                ticker = yf.Ticker(candidate)
                info = ticker.info
                history = ticker.history(period="1d")

                if history.empty:
                    raise ValueError(f"No data from yfinance for {candidate}")

                latest = history.iloc[-1]
                current_price = float(latest["Close"])
                previous_close = float(info.get("previousClose", current_price))
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close > 0 else 0

                if candidate != symbol:
                    logger.info(f"Resolved yfinance symbol {symbol} via alias {candidate}")

                return {
                    "symbol": symbol,
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "timestamp": datetime.now(),
                    "source": "yfinance",
                }
            except Exception as e:
                last_error = e
                logger.warning(f"yfinance candidate failed for {symbol} -> {candidate}: {str(e)}")

        raise ValueError(f"No data from yfinance for {symbol}: {str(last_error) if last_error else 'unknown error'}")

    def _to_float(self, value: Any, default: float = 0.0) -> float:
        """Safely parse numbers from API payloads that may include strings/symbols."""
        try:
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return float(value)

            cleaned = str(value).strip().replace(",", "")
            if cleaned.endswith("%"):
                cleaned = cleaned[:-1].strip()
            return float(cleaned)
        except Exception:
            return default

    def get_trending_stocks(self, limit: int = 3) -> Dict[str, Any]:
        """Fetch and normalize top gainers/losers from Indian Market API trending endpoint."""
        cache_key = f"trending_stocks_{limit}"

        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return {
                "trending": cached_data,
                "cached": True,
                "cache_expires_at": (
                    self._cache_timestamps[cache_key] + timedelta(seconds=self.cache_ttl)
                ).isoformat() + "Z",
            }

        def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "symbol": row.get("ticker_id") or row.get("ric") or "",
                "company_name": row.get("company_name") or "",
                "price": self._to_float(row.get("price")),
                "percent_change": self._to_float(row.get("percent_change")),
                "net_change": self._to_float(row.get("net_change")),
                "exchange_type": row.get("exchange_type") or "",
                "volume": self._to_float(row.get("volume")),
                "time": row.get("time") or "",
                "date": row.get("date") or "",
            }

        trending = {"top_gainers": [], "top_losers": []}

        if self.indian_market_client.enabled:
            try:
                raw = self.indian_market_client.get_trending_stocks() or {}
                raw_trending = raw.get("trending_stocks", {}) if isinstance(raw, dict) else {}

                gainers = raw_trending.get("top_gainers", []) if isinstance(raw_trending, dict) else []
                losers = raw_trending.get("top_losers", []) if isinstance(raw_trending, dict) else []

                trending["top_gainers"] = [
                    normalize_row(item) for item in gainers[:limit] if isinstance(item, dict)
                ]
                trending["top_losers"] = [
                    normalize_row(item) for item in losers[:limit] if isinstance(item, dict)
                ]
            except Exception as e:
                logger.warning(f"Trending fetch failed: {str(e)}")

        # Fallback to index-based momentum when trending endpoint is unavailable.
        if not trending["top_gainers"] and not trending["top_losers"]:
            india_indices = self.get_all_indices(MarketType.INDIA).get("indices", [])
            sorted_indices = sorted(
                [i for i in india_indices if isinstance(i, dict)],
                key=lambda i: i.get("percentage_change", 0),
                reverse=True,
            )

            gainers = sorted_indices[:limit]
            losers = list(reversed(sorted_indices[-limit:]))

            trending["top_gainers"] = [
                {
                    "symbol": i.get("symbol", ""),
                    "company_name": i.get("name", ""),
                    "price": self._to_float(i.get("current_price", 0)),
                    "percent_change": self._to_float(i.get("percentage_change", 0)),
                    "net_change": 0.0,
                    "exchange_type": "INDEX",
                    "volume": 0.0,
                    "time": "",
                    "date": "",
                }
                for i in gainers
            ]
            trending["top_losers"] = [
                {
                    "symbol": i.get("symbol", ""),
                    "company_name": i.get("name", ""),
                    "price": self._to_float(i.get("current_price", 0)),
                    "percent_change": self._to_float(i.get("percentage_change", 0)),
                    "net_change": 0.0,
                    "exchange_type": "INDEX",
                    "volume": 0.0,
                    "time": "",
                    "date": "",
                }
                for i in losers
            ]

        self._set_cache(cache_key, trending)
        return {
            "trending": trending,
            "cached": False,
            "cache_expires_at": (
                datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            ).isoformat() + "Z",
        }

    def get_indian_historical_data(
        self,
        stock_name: str,
        period: str = "5yr",
        filter_type: str = "price",
    ) -> Dict[str, Any]:
        """Fetch raw historical datasets for an Indian stock."""
        cache_key = f"indian_historical_{stock_name}_{period}_{filter_type}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return {
                "historical_data": cached_data,
                "cached": True,
                "cache_expires_at": (
                    self._cache_timestamps[cache_key] + timedelta(seconds=self.cache_ttl)
                ).isoformat() + "Z",
            }

        payload = self.indian_market_client.get_historical_data_payload(
            stock_name=stock_name,
            period=period,
            filter_type=filter_type,
        )

        if payload:
            self._set_cache(cache_key, payload)
            return {
                "historical_data": payload,
                "cached": False,
                "cache_expires_at": (
                    datetime.utcnow() + timedelta(seconds=self.cache_ttl)
                ).isoformat() + "Z",
            }

        return {
            "historical_data": {"datasets": []},
            "cached": False,
            "cache_expires_at": (
                datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            ).isoformat() + "Z",
        }

    def get_indian_stock_forecasts(
        self,
        stock_id: str,
        measure_code: str,
        period_type: str,
        data_type: str,
        age: str,
    ) -> Dict[str, Any]:
        """Fetch stock forecast payload for an Indian stock."""
        cache_key = f"indian_forecast_{stock_id}_{measure_code}_{period_type}_{data_type}_{age}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return {
                "forecasts": cached_data,
                "cached": True,
                "cache_expires_at": (
                    self._cache_timestamps[cache_key] + timedelta(seconds=self.cache_ttl)
                ).isoformat() + "Z",
            }

        payload = self.indian_market_client.get_stock_forecasts(
            stock_id=stock_id,
            measure_code=measure_code,
            period_type=period_type,
            data_type=data_type,
            age=age,
        )

        if payload:
            self._set_cache(cache_key, payload)
            return {
                "forecasts": payload,
                "cached": False,
                "cache_expires_at": (
                    datetime.utcnow() + timedelta(seconds=self.cache_ttl)
                ).isoformat() + "Z",
            }

        return {
            "forecasts": None,
            "cached": False,
            "cache_expires_at": (
                datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            ).isoformat() + "Z",
        }

    def _extract_close_series(self, history: Any) -> Optional[pd.Series]:
        """Return a close series from a history payload with flexible column names."""
        if history is None:
            return None
        if not isinstance(history, pd.DataFrame) or history.empty:
            return None

        for column in ("close", "Close", "adjclose", "Adj Close"):
            if column in history.columns:
                series = pd.to_numeric(history[column], errors="coerce").dropna()
                if not series.empty:
                    return series
        return None

    def _summarize_forecast_payload(self, payload: Optional[Dict[str, Any]], current_price: float) -> Dict[str, Any]:
        """Create a compact, readable forecast summary from provider payloads."""
        if not payload:
            return {
                "available": False,
                "direction": "neutral",
                "confidence": 0,
                "summary": "No forecast feed available.",
                "source": "none",
            }

        forecast_rows: List[Dict[str, Any]] = []
        for key in ("forecasts", "data", "results", "values"):
            value = payload.get(key)
            if isinstance(value, list):
                forecast_rows = [item for item in value if isinstance(item, dict)]
                if forecast_rows:
                    break
            elif isinstance(value, dict):
                nested_rows = [item for item in value.values() if isinstance(item, dict)]
                if nested_rows:
                    forecast_rows = nested_rows
                    break

        numeric_points: List[float] = []
        for row in forecast_rows:
            for field in ("estimate", "forecast", "value", "price", "target", "eps", "cps"):
                if field in row:
                    parsed = self._to_float(row.get(field), default=float("nan"))
                    if not pd.isna(parsed):
                        numeric_points.append(parsed)
                        break

        if numeric_points:
            start_value = numeric_points[0]
            end_value = numeric_points[-1]
            delta = end_value - start_value
            delta_pct = (delta / start_value * 100) if start_value else 0
            direction = "bullish" if delta_pct > 1 else "bearish" if delta_pct < -1 else "neutral"
            confidence = int(min(95, max(25, 55 + abs(delta_pct) * 4)))
            return {
                "available": True,
                "direction": direction,
                "confidence": confidence,
                "summary": (
                    f"Forecasts skew {direction} with a {delta_pct:+.1f}% move across the latest provider points."
                ),
                "source": "indian_market_api",
                "points": len(numeric_points),
                "latest_value": round(end_value, 2),
                "change_pct": round(delta_pct, 2),
            }

        # Fallback to payload shape if we cannot infer numeric projections.
        payload_keys = ", ".join(sorted(list(payload.keys()))[:5])
        current_bias = "above" if payload.get("target_mean_price", 0) and self._to_float(payload.get("target_mean_price"), 0) > current_price else "around"
        return {
            "available": True,
            "direction": "neutral",
            "confidence": 45,
            "summary": f"Forecast data received ({payload_keys}); guidance is {current_bias} the current price.",
            "source": "indian_market_api",
        }

    def get_compact_market_analytics(
        self,
        symbol: str,
        market: str = "both",
        period: str = "1yr",
        filter_type: str = "price",
        measure_code: str = "EPS",
        period_type: str = "Annual",
        data_type: str = "Estimates",
        age: str = "Current",
    ) -> Dict[str, Any]:
        """Return compact market analytics with trend, forecast, and 52-week context."""
        normalized_symbol = symbol.strip().upper()
        cache_key = (
            f"compact_analytics_{normalized_symbol}_{market}_{period}_{filter_type}_{measure_code}_{period_type}_{data_type}_{age}"
        )

        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return {
                "analytics": cached_data,
                "cached": True,
                "cache_expires_at": (
                    self._cache_timestamps[cache_key] + timedelta(seconds=self.cache_ttl)
                ).isoformat() + "Z",
            }

        market_type = MarketType(market.lower()) if market.lower() in {"india", "us", "both"} else MarketType.BOTH
        is_indian_symbol = self._is_indian_symbol(normalized_symbol)
        is_index_symbol = normalized_symbol.startswith("^")

        if is_index_symbol:
            quote = self.get_index_data(normalized_symbol) or self._get_mock_data(normalized_symbol)
        elif is_indian_symbol or market_type == MarketType.INDIA:
            quote = self._get_price_india(normalized_symbol)
        else:
            quote = self._get_price_us(normalized_symbol)

        quote = quote or self._get_mock_data(normalized_symbol)
        current_price = self._to_float(quote.get("price"), 0.0)
        previous_close = self._to_float(quote.get("previous_close"), current_price - self._to_float(quote.get("change"), 0.0))
        change_percent = self._to_float(quote.get("change_percent"), 0.0)

        history: Optional[pd.DataFrame] = None
        if is_indian_symbol and self.indian_market_client.enabled:
            try:
                history = self.indian_market_client.get_historical_data(
                    normalized_symbol,
                    period=period,
                    filter_type=filter_type,
                )
            except Exception as e:
                logger.warning(f"Indian historical analytics fetch failed for {normalized_symbol}: {str(e)}")

        if history is None or getattr(history, "empty", True):
            try:
                history = yf.Ticker(normalized_symbol).history(period="1y", interval="1d")
            except Exception as e:
                logger.warning(f"yfinance history failed for {normalized_symbol}: {str(e)}")
                history = None

        close_series = self._extract_close_series(history)
        trend_score = 0.0
        trend_direction = "sideways"
        trend_summary = "Recent price action is balanced."
        if close_series is not None and len(close_series) >= 5:
            recent_window = close_series.tail(20)
            prior_window = close_series.iloc[-40:-20] if len(close_series) >= 40 else close_series.iloc[: max(1, len(close_series) // 2)]
            recent_mean = float(recent_window.mean()) if not recent_window.empty else current_price
            prior_mean = float(prior_window.mean()) if not prior_window.empty else recent_mean
            trend_pct = ((recent_mean - prior_mean) / prior_mean * 100) if prior_mean else 0.0
            trend_score = float(max(-1.0, min(1.0, trend_pct / 5.0)))
            if trend_pct > 1.0:
                trend_direction = "bullish"
            elif trend_pct < -1.0:
                trend_direction = "bearish"
            trend_summary = (
                f"{trend_direction.title()} momentum over the last few weeks is {trend_pct:+.1f}%."
            )

        fifty_two_week_high = None
        fifty_two_week_low = None
        history_high = None
        history_low = None
        try:
            info = yf.Ticker(normalized_symbol).info
            fifty_two_week_high = self._to_float(info.get("fiftyTwoWeekHigh"), 0.0) or None
            fifty_two_week_low = self._to_float(info.get("fiftyTwoWeekLow"), 0.0) or None
        except Exception:
            info = {}

        if close_series is not None and not close_series.empty:
            history_high = float(close_series.tail(min(len(close_series), 252)).max())
            history_low = float(close_series.tail(min(len(close_series), 252)).min())

        high = fifty_two_week_high or history_high or current_price
        low = fifty_two_week_low or history_low or current_price
        range_span = max(high - low, 1e-9)
        position_pct = max(0.0, min(100.0, ((current_price - low) / range_span) * 100))
        distance_from_high_pct = max(0.0, ((high - current_price) / high) * 100) if high else 0.0
        distance_from_low_pct = max(0.0, ((current_price - low) / max(low, 1e-9)) * 100) if low else 0.0

        if position_pct >= 80:
            range_state = "near_52w_high"
        elif position_pct <= 20:
            range_state = "near_52w_low"
        else:
            range_state = "mid_range"

        forecast_payload = None
        forecast_summary = {
            "available": False,
            "direction": "neutral",
            "confidence": 0,
            "summary": "Forecast data not available.",
            "source": "none",
        }

        if is_indian_symbol and self.indian_market_client.enabled:
            try:
                forecast_payload = self.get_indian_stock_forecasts(
                    stock_id=normalized_symbol.replace(".NS", "").replace(".BO", "").lower(),
                    measure_code=measure_code,
                    period_type=period_type,
                    data_type=data_type,
                    age=age,
                ).get("forecasts")
            except Exception as e:
                logger.warning(f"Indian forecast analytics failed for {normalized_symbol}: {str(e)}")

        if forecast_payload:
            forecast_summary = self._summarize_forecast_payload(forecast_payload, current_price)
        else:
            target_price = 0.0
            recommendation_mean = 0.0
            try:
                target_price = self._to_float(info.get("targetMeanPrice"), 0.0)
                recommendation_mean = self._to_float(info.get("recommendationMean"), 0.0)
            except Exception:
                pass

            if target_price > 0:
                forecast_gap_pct = ((target_price - current_price) / current_price * 100) if current_price else 0.0
                forecast_summary = {
                    "available": True,
                    "direction": "bullish" if forecast_gap_pct > 1 else "bearish" if forecast_gap_pct < -1 else "neutral",
                    "confidence": int(min(90, max(35, 50 + abs(forecast_gap_pct) * 3))),
                    "summary": f"Analyst target implies {forecast_gap_pct:+.1f}% vs the current price.",
                    "source": "yfinance",
                    "target_price": round(target_price, 2),
                    "recommendation_mean": round(recommendation_mean, 2) if recommendation_mean else None,
                }

        analytics = {
            "symbol": normalized_symbol,
            "name": quote.get("name") or self._get_index_name(normalized_symbol),
            "market": market_type.value,
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "change_percent": round(change_percent, 2),
            "trend": {
                "score": round(trend_score, 3),
                "direction": trend_direction,
                "summary": trend_summary,
            },
            "forecast": forecast_summary,
            "range_52w": {
                "high": round(high, 2),
                "low": round(low, 2),
                "position_pct": round(position_pct, 2),
                "distance_from_high_pct": round(distance_from_high_pct, 2),
                "distance_from_low_pct": round(distance_from_low_pct, 2),
                "range_state": range_state,
            },
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "source": quote.get("source", "unknown"),
        }

        self._set_cache(cache_key, analytics)
        return {
            "analytics": analytics,
            "cached": False,
            "cache_expires_at": (
                datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            ).isoformat() + "Z",
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
            "NIFTY_IT.NS": "NIFTY IT",
            "^CNXBN": "NIFTY BANK",
            "^NSEBANK": "NIFTY BANK",
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
