"""
News Service - Fetches financial news articles
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class NewsService:
    """Service for fetching financial news articles"""

    def __init__(self, cache_ttl: int = 1800):
        """
        Initialize news service

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 30 minutes)
        """
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_timestamps = {}

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

    def get_financial_news(self, limit: int = 8) -> Dict[str, Any]:
        """
        Fetch financial news articles

        Args:
            limit: Number of articles to return

        Returns:
            Dict with news articles
        """
        cache_key = "financial_news"

        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return {
                "news": cached_data,
                "cached": True,
                "cache_expires_at": (
                    self._cache_timestamps[cache_key] + timedelta(seconds=self.cache_ttl)
                ).isoformat() + "Z",
            }

        try:
            # Try to fetch from NewsAPI
            articles = self._fetch_from_newsapi(limit)

            if articles:
                result = {
                    "news": articles,
                    "cached": False,
                    "cache_expires_at": (
                        datetime.utcnow() + timedelta(seconds=self.cache_ttl)
                    ).isoformat() + "Z",
                }
                self._set_cache(cache_key, articles)
                return result

        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")

        # Fallback to mock articles
        mock_articles = self._get_mock_articles(limit)
        return {
            "news": mock_articles,
            "cached": False,
            "cache_expires_at": (
                datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            ).isoformat() + "Z",
        }

    def _fetch_from_newsapi(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch articles from NewsAPI

        Args:
            limit: Number of articles to return

        Returns:
            List of articles or None
        """
        try:
            import newsapi
            from os import getenv

            api_key = getenv("NEWSAPI_KEY")
            if not api_key:
                logger.warning("NEWSAPI_KEY not set, using mock data")
                return None

            client = newsapi.NewsApiClient(api_key=api_key)
            response = client.get_top_headlines(
                q="finance market India stocks",
                language="en",
                page_size=limit,
                sort_by="publishedAt"
            )

            if response and response.get("articles"):
                articles = []
                for article in response["articles"][:limit]:
                    articles.append({
                        "title": article.get("title", ""),
                        "source": article.get("source", {}).get("name", "")[:30],
                        "url": article.get("url", ""),
                        "image": article.get("urlToImage", ""),
                        "published_date": article.get("publishedAt", ""),
                        "description": (article.get("description", "")[:150] + "...")
                        if article.get("description") else "",
                    })
                return articles

        except ImportError:
            logger.warning("newsapi not installed, using mock data")
        except Exception as e:
            logger.error(f"NewsAPI error: {str(e)}")

        return None

    def _get_mock_articles(self, limit: int = 8) -> List[Dict[str, Any]]:
        """Return mock financial news articles"""
        mock_articles = [
            {
                "title": "RBI Maintains Policy Rate at 6.5%, Focus on Inflation Control",
                "source": "Economic Times",
                "url": "https://economictimes.indiatimes.com",
                "image": "",
                "published_date": (datetime.utcnow() - timedelta(hours=4)).isoformat() + "Z",
                "description": "The Reserve Bank of India maintained its benchmark policy rate at 6.5% in its latest monetary policy meeting, signaling a pause in rate hikes...",
            },
            {
                "title": "Sensex Ends at Record High; Nifty Closes Above 20,000 Mark",
                "source": "Moneycontrol",
                "url": "https://moneycontrol.com",
                "image": "",
                "published_date": (datetime.utcnow() - timedelta(hours=8)).isoformat() + "Z",
                "description": "The BSE Sensex index closed at an all-time high on the back of strong buying in IT stocks and banking sector shares...",
            },
            {
                "title": "IT Sector Gains Ground Amid Strong Q4 Results and Global Recovery",
                "source": "Business Standard",
                "url": "https://business-standard.com",
                "image": "",
                "published_date": (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z",
                "description": "Indian IT companies reported strong quarterly results, benefiting from increased outsourcing demand from global clients...",
            },
            {
                "title": "Gold Prices Edge Up on Currency Weakness and Global Uncertainty",
                "source": "Reuters India",
                "url": "https://reuters.com",
                "image": "",
                "published_date": (datetime.utcnow() - timedelta(hours=16)).isoformat() + "Z",
                "description": "Gold prices in India rose marginally amid weakness in the rupee and safe-haven demand internationally...",
            },
            {
                "title": "Union Budget: Tax Relief for Middle Class, Focus on Infrastructure",
                "source": "Financial Express",
                "url": "https://financial-express.com",
                "image": "",
                "published_date": (datetime.utcnow() - timedelta(hours=20)).isoformat() + "Z",
                "description": "The new budget focuses on infrastructure development and provides tax incentives for middle-class citizens...",
            },
            {
                "title": "Rupee Strengthens Against Dollar on Portfolio Inflows",
                "source": "Hindu Business Line",
                "url": "https://thehindubusinessline.com",
                "image": "",
                "published_date": (datetime.utcnow() - timedelta(hours=24)).isoformat() + "Z",
                "description": "The Indian rupee strengthened against the US dollar due to increased foreign portfolio investments...",
            },
            {
                "title": "Banking Sector Shows Recovery with Strong Loan Growth",
                "source": "Mint",
                "url": "https://mint.com",
                "image": "",
                "published_date": (datetime.utcnow() - timedelta(hours=28)).isoformat() + "Z",
                "description": "Indian banks reported strong loan growth in the latest quarter, indicating robust economic activity...",
            },
            {
                "title": "Pharma Stocks Rally on Strong Export Orders and R&D Progress",
                "source": "CNBC-TV18",
                "url": "https://cnbctv18.com",
                "image": "",
                "published_date": (datetime.utcnow() - timedelta(hours=32)).isoformat() + "Z",
                "description": "Indian pharmaceutical companies gained on the back of strong pharmaceutical export orders from international markets...",
            },
        ]

        return mock_articles[:limit]

    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("News cache cleared")


# Global instance
news_service = NewsService()
