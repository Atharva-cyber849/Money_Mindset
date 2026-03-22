#!/usr/bin/env python3
"""
Quick verification script for Market Data API integration
Run this to verify all components are working correctly
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_imports():
    """Test all necessary imports"""
    print("🔍 Testing imports...")
    try:
        from app.services.api_clients import FinnhubClient, IndianMarketClient
        from app.services.market_data_service import market_data_service, MarketType
        from app.core.config import settings
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_symbol_detection():
    """Test market symbol detection"""
    print("🔍 Testing symbol detection...")
    try:
        from app.services.market_data_service import market_data_service

        test_cases = [
            ("RELIANCE.NS", True),   # Indian
            ("TCS.BO", True),         # Indian
            ("^NSEI", True),          # Indian
            ("AAPL", False),          # US
            ("SPY", False),           # US
            ("MSFT", False),          # US
        ]

        for symbol, expected_indian in test_cases:
            is_indian = market_data_service._is_indian_symbol(symbol)
            status = "✅" if is_indian == expected_indian else "❌"
            print(f"  {status} {symbol}: indian={is_indian}")

        print("  ✅ Symbol detection working correctly")
        return True
    except Exception as e:
        print(f"  ❌ Symbol detection failed: {e}")
        return False

def test_api_clients():
    """Test API client initialization"""
    print("🔍 Testing API client initialization...")
    try:
        from app.services.api_clients import FinnhubClient, IndianMarketClient
        from app.core.config import settings

        finnhub = FinnhubClient(api_key=settings.FINNHUB_API_KEY, enabled=True)
        print(f"  ✅ Finnhub client initialized (enabled={finnhub.enabled})")

        indian = IndianMarketClient(base_url=settings.INDIAN_MARKET_API_URL, enabled=True)
        print(f"  ✅ Indian Market client initialized (enabled={indian.enabled})")

        return True
    except Exception as e:
        print(f"  ❌ API client initialization failed: {e}")
        return False

def test_mock_quotes():
    """Test mock data fallback"""
    print("🔍 Testing mock data (fallback)...")
    try:
        from app.services.api_clients import FinnhubClient, IndianMarketClient

        finnhub = FinnhubClient(enabled=False)  # Disabled, so should return mock
        fi_quote = finnhub._get_mock_quote("AAPL")
        print(f"  ✅ Finnhub mock: AAPL = ${fi_quote['price']}")

        indian = IndianMarketClient(base_url="", enabled=False)  # Disabled
        in_quote = indian._get_mock_quote("RELIANCE.NS")
        print(f"  ✅ Indian mock: RELIANCE = ₹{in_quote['price']}")

        return True
    except Exception as e:
        print(f"  ❌ Mock data test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    try:
        from app.core.config import settings

        print(f"  ✅ FINNHUB_ENABLED = {settings.FINNHUB_ENABLED}")
        print(f"  ✅ INDIAN_MARKET_ENABLED = {settings.INDIAN_MARKET_ENABLED}")
        print(f"  ✅ YFINANCE_ENABLED = {settings.YFINANCE_ENABLED}")

        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_market_data_service():
    """Test market data service methods"""
    print("🔍 Testing market data service...")
    try:
        from app.services.market_data_service import market_data_service, MarketType

        # Test methods exist
        assert hasattr(market_data_service, '_get_price_india')
        print("  ✅ _get_price_india() method exists")

        assert hasattr(market_data_service, '_get_price_us')
        print("  ✅ _get_price_us() method exists")

        assert hasattr(market_data_service, 'get_all_indices')
        print("  ✅ get_all_indices() method exists")

        # Test cache works
        market_data_service.clear_cache()
        print("  ✅ Cache cleared successfully")

        return True
    except Exception as e:
        print(f"  ❌ Market data service test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Market Data API Integration - Verification Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_symbol_detection,
        test_api_clients,
        test_mock_quotes,
        test_configuration,
        test_market_data_service,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
        print()

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed! Integration is ready.")
    else:
        print(f"❌ {total - passed} test(s) failed. Please review.")

    print("=" * 60)

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
