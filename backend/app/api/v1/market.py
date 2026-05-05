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
        trending_data = market_data_service.get_trending_stocks(limit=3)

        return {
            "indices": indices_data.get("indices", []),
            "news": news_data.get("news", []),
            "trending": trending_data.get("trending", {"top_gainers": [], "top_losers": []}),
            "market": market.lower(),
            "indices_cached": indices_data.get("cached", False),
            "news_cached": news_data.get("cached", False),
            "trending_cached": trending_data.get("cached", False),
            "indices_cache_expires_at": indices_data.get("cache_expires_at"),
            "news_cache_expires_at": news_data.get("cache_expires_at"),
            "trending_cache_expires_at": trending_data.get("cache_expires_at"),
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


@router.get("/trending")
async def get_trending_stocks(limit: int = 3) -> Dict[str, Any]:
    """Get top gaining and losing stocks from configured Indian market provider."""
    try:
        if limit < 1 or limit > 10:
            limit = 3

        return market_data_service.get_trending_stocks(limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending stocks: {str(e)}"
        )


@router.get("/compact-analytics")
async def get_compact_market_analytics(
    symbol: str,
    market: str = "both",
    period: str = "1yr",
    filter_type: str = "price",
    measure_code: str = "EPS",
    period_type: str = "Annual",
    data_type: str = "Estimates",
    age: str = "Current",
) -> Dict[str, Any]:
    """Get a compact, card-friendly market summary for a symbol."""
    try:
        if not symbol or not symbol.strip():
            raise HTTPException(status_code=400, detail="symbol is required")

        valid_markets = {"india", "us", "both"}
        selected_market = market.lower() if market and market.lower() in valid_markets else "both"

        return market_data_service.get_compact_market_analytics(
            symbol=symbol,
            market=selected_market,
            period=period,
            filter_type=filter_type,
            measure_code=measure_code,
            period_type=period_type,
            data_type=data_type,
            age=age,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch compact analytics: {str(e)}",
        )


@router.get("/historical-data")
async def get_indian_historical_data(
    stock_name: str,
    period: str = "5yr",
    filter_type: str = "price",
) -> Dict[str, Any]:
    """Get historical datasets from Indian market provider."""
    try:
        valid_periods = {"1m", "6m", "1yr", "3yr", "5yr", "10yr", "max"}
        valid_filters = {"default", "price", "pe", "sm", "evebitda", "ptb", "mcs"}

        selected_period = period if period in valid_periods else "5yr"
        selected_filter = filter_type if filter_type in valid_filters else "price"

        return market_data_service.get_indian_historical_data(
            stock_name=stock_name,
            period=selected_period,
            filter_type=selected_filter,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch historical data: {str(e)}",
        )


@router.get("/stock-forecasts")
async def get_indian_stock_forecasts(
    stock_id: str,
    measure_code: str,
    period_type: str,
    data_type: str,
    age: str,
) -> Dict[str, Any]:
    """Get stock forecast payload from Indian market provider."""
    try:
        valid_period_types = {"Annual", "Interim"}
        valid_data_types = {"Actuals", "Estimates"}
        valid_ages = {"OneWeekAgo", "ThirtyDaysAgo", "SixtyDaysAgo", "NinetyDaysAgo", "Current"}
        valid_measure_codes = {
            "EPS", "CPS", "CPX", "DPS", "EBI", "EBT", "GPS", "GRM", "NAV", "NDT", "NET", "PRE", "ROA", "ROE", "SAL"
        }

        if measure_code not in valid_measure_codes:
            raise HTTPException(status_code=400, detail="Invalid measure_code")
        if period_type not in valid_period_types:
            raise HTTPException(status_code=400, detail="Invalid period_type")
        if data_type not in valid_data_types:
            raise HTTPException(status_code=400, detail="Invalid data_type")
        if age not in valid_ages:
            raise HTTPException(status_code=400, detail="Invalid age")

        data = market_data_service.get_indian_stock_forecasts(
            stock_id=stock_id,
            measure_code=measure_code,
            period_type=period_type,
            data_type=data_type,
            age=age,
        )

        if not data.get("forecasts"):
            raise HTTPException(status_code=404, detail="No forecasts found")

        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stock forecasts: {str(e)}",
        )
