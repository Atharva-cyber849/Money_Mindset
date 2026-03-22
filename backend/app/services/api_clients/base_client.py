"""Base API Client class with common functionality"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)


class APIClient(ABC):
    """Abstract base class for market data API clients"""

    def __init__(self, api_key: str = "", base_url: str = "", enabled: bool = True):
        """Initialize API client

        Args:
            api_key: API authentication key
            base_url: Base URL for API endpoints
            enabled: Whether this client is enabled
        """
        self.api_key = api_key
        self.base_url = base_url
        self.enabled = enabled
        self.name = self.__class__.__name__

    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current quote for a symbol

        Returns:
            {
                "symbol": str,
                "price": float,
                "change": float,
                "change_percent": float,
                "timestamp": datetime,
                "source": str
            }
        """
        pass

    @abstractmethod
    def get_historical_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """Fetch historical OHLCV data

        Returns DataFrame with columns:
            - date: index
            - open, high, low, close, volume
        """
        pass

    def _log_error(self, method: str, error: Exception) -> None:
        """Log API errors"""
        logger.warning(f"{self.name}.{method} failed: {str(error)}")

    def _log_success(self, method: str, symbol: str, latency_ms: int = 0) -> None:
        """Log successful API calls"""
        logger.debug(f"{self.name}.{method}({symbol}) - {latency_ms}ms")
