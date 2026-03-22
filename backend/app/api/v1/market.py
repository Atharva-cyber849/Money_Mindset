"""
Market Data API Routes
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional

from app.services.market_data_service import market_data_service, MarketType
from app.services.news_service import news_service

router = APIRouter()


@router.get("/indices")
async def get_market_indices(market: Optional[str] = "both") -> Dict[str, Any]:
    """
    Get current market indices (India, US, or both)

    Args:
        market: Market type - "india", "us", or "both" (default: "both")

    Returns:
        Dict with current indices data
    """
    try:
        # Validate market parameter
        valid_markets = {"india", "us", "both"}
        if market.lower() not in valid_markets:
            market = "both"

        market_type = MarketType(market.lower())
        data = market_data_service.get_all_indices(market_type)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market indices: {str(e)}"
        )


@router.get("/news")
async def get_financial_news(limit: int = 8) -> Dict[str, Any]:
    """
    Get latest financial news articles

    Args:
        limit: Number of articles to return (default: 8)

    Returns:
        Dict with financial news articles
    """
    try:
        if limit < 1 or limit > 20:
            limit = 8

        data = news_service.get_financial_news(limit)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch news: {str(e)}"
        )


@router.get("/combined")
async def get_combined_market_data(market: Optional[str] = "both", news_limit: int = 8) -> Dict[str, Any]:
    """
    Get combined market indices and financial news

    Args:
        market: Market type - "india", "us", or "both" (default: "both")
        news_limit: Number of news articles to include (default: 8)

    Returns:
        Dict with both indices and news
    """
    try:
        # Validate market parameter
        valid_markets = {"india", "us", "both"}
        if market.lower() not in valid_markets:
            market = "both"

        market_type = MarketType(market.lower())
        indices_data = market_data_service.get_all_indices(market_type)
        news_data = news_service.get_financial_news(news_limit)

        return {
            "indices": indices_data.get("indices", []),
            "news": news_data.get("news", []),
            "market": market.lower(),
            "indices_cached": indices_data.get("cached", False),
            "news_cached": news_data.get("cached", False),
            "indices_cache_expires_at": indices_data.get("cache_expires_at"),
            "news_cache_expires_at": news_data.get("cache_expires_at"),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market data: {str(e)}"
        )


@router.post("/refresh-cache")
async def refresh_market_cache() -> Dict[str, str]:
    """
    Manually refresh market data cache (clear and refetch)

    Returns:
        Status message
    """
    try:
        market_data_service.clear_cache()
        news_service.clear_cache()
        return {"status": "success", "message": "Market data cache refreshed"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh cache: {str(e)}"
        )
