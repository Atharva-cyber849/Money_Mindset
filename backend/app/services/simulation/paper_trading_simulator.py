"""
Paper Trading Simulator - Stock market simulation with paper money
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import logging
import numpy as np

logger = logging.getLogger(__name__)


class MarketType(str, Enum):
    """Market types"""
    INDIA = "india"
    US = "us"
    BOTH = "both"


class TradeSide(str, Enum):
    """Trade side"""
    BUY = "BUY"
    SELL = "SELL"


class EventType(str, Enum):
    """Market event types"""
    MARKET_CRASH = "market_crash"
    EARNINGS_SEASON = "earnings_season"
    SECTOR_ROTATION = "sector_rotation"
    FED_DECISION = "fed_decision"
    RBI_POLICY = "rbi_policy"
    GEOPOLITICAL = "geopolitical"


# India stocks (NIFTY 50 sample)
INDIA_STOCKS = {
    "RELIANCE.NS": {"name": "Reliance Industries", "sector": "Energy"},
    "TCS.NS": {"name": "Tata Consultancy Services", "sector": "IT"},
    "INFY.NS": {"name": "Infosys", "sector": "IT"},
    "WIPRO.NS": {"name": "Wipro", "sector": "IT"},
    "HDFCBANK.NS": {"name": "HDFC Bank", "sector": "Banking"},
    "ICICIBANK.NS": {"name": "ICICI Bank", "sector": "Banking"},
    "BAJAJFINSV.NS": {"name": "Bajaj Finserv", "sector": "Financial Services"},
    "SBIN.NS": {"name": "State Bank of India", "sector": "Banking"},
    "MARUTI.NS": {"name": "Maruti Suzuki", "sector": "Automotive"},
    "BHARTIARTL.NS": {"name": "Bharti Airtel", "sector": "Telecom"},
}

# US stocks (S&P 500 sample)
US_STOCKS = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology"},
    "MSFT": {"name": "Microsoft Corporation", "sector": "Technology"},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology"},
    "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer"},
    "META": {"name": "Meta Platforms Inc.", "sector": "Technology"},
    "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology"},
    "TSLA": {"name": "Tesla Inc.", "sector": "Automotive"},
    "JPM": {"name": "JPMorgan Chase", "sector": "Banking"},
    "V": {"name": "Visa Inc.", "sector": "Financials"},
    "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare"},
}


def get_stocks_for_market(market: MarketType) -> Dict[str, Dict[str, str]]:
    """Get list of stocks for market"""
    if market == MarketType.INDIA:
        return INDIA_STOCKS
    elif market == MarketType.US:
        return US_STOCKS
    else:
        # Both markets
        combined = {**INDIA_STOCKS, **US_STOCKS}
        return combined


@dataclass
class Holding:
    """A stock holding"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    sector: str
    purchased_at: datetime

    def get_value(self) -> float:
        """Get current value of holding"""
        return self.quantity * self.current_price

    def get_pnl(self) -> float:
        """Get profit/loss"""
        return (self.current_price - self.entry_price) * self.quantity

    def get_pnl_percentage(self) -> float:
        """Get profit/loss percentage"""
        if self.entry_price == 0:
            return 0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100


@dataclass
class Trade:
    """A single trade"""
    trade_id: str
    symbol: str
    quantity: int
    price: float
    side: TradeSide
    executed_at: datetime
    commission: float = 0.0

    def get_total_value(self) -> float:
        """Get total trade value before commission"""
        return self.quantity * self.price


@dataclass
class Portfolio:
    """User portfolio"""
    holdings: Dict[str, Holding] = field(default_factory=dict)
    cash: float = 0.0
    trades: List[Trade] = field(default_factory=list)
    portfolio_value_history: List[float] = field(default_factory=list)

    def get_total_value(self) -> float:
        """Get total portfolio value (cash + holdings)"""
        holdings_value = sum(h.get_value() for h in self.holdings.values())
        return self.cash + holdings_value

    def get_holdings_value(self) -> float:
        """Get total value of holdings"""
        return sum(h.get_value() for h in self.holdings.values())

    def get_total_pnl(self) -> float:
        """Get total P&L from all trades"""
        return sum(h.get_pnl() for h in self.holdings.values())

    def get_total_pnl_percentage(self) -> float:
        """Get total P&L percentage"""
        if not self.holdings:
            return 0.0
        invested = sum(h.entry_price * h.quantity for h in self.holdings.values())
        if invested == 0:
            return 0.0
        return (self.get_total_pnl() / invested) * 100

    def get_allocation(self) -> Dict[str, float]:
        """Get sector allocation percentages"""
        total_value = self.get_total_value()
        if total_value == 0:
            return {}

        allocation = {}
        for holding in self.holdings.values():
            sector = holding.sector
            allocation[sector] = allocation.get(sector, 0) + (holding.get_value() / total_value * 100)
        return allocation


class PaperTradingSimulator:
    """Paper trading game simulator"""

    def __init__(
        self,
        market: MarketType,
        initial_capital: float,
        strategy: str,
        start_date: datetime,
        end_date: datetime,
    ):
        """
        Initialize paper trading simulator

        Args:
            market: MarketType (INDIA, US, or BOTH)
            initial_capital: Starting capital in rupees/dollars
            strategy: Trading strategy name
            start_date: Start date for simulation
            end_date: End date for simulation
        """
        self.market = market
        self.initial_capital = initial_capital
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = start_date

        # Initialize portfolio
        self.portfolio = Portfolio(cash=initial_capital)
        self.stocks = get_stocks_for_market(market)
        self.events: List[Dict[str, Any]] = []

        logger.info(f"Initialized paper trading simulator: {market.value}, capital: {initial_capital}")

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a stock symbol using yfinance (real data)

        Args:
            symbol: Stock symbol

        Returns:
            Current price or None if unavailable
        """
        try:
            ticker = yf.Ticker(symbol)

            # Try to get the most recent data
            data = ticker.history(period="1d")
            if data.empty:
                data = ticker.history(period="5d")

            if data.empty:
                logger.warning(f"No recent data for {symbol}, trying info")
                # Fallback to ticker info
                info = ticker.info
                if 'currentPrice' in info:
                    return float(info['currentPrice'])
                elif 'regularMarketPrice' in info:
                    return float(info['regularMarketPrice'])
                return self._get_mock_price(symbol)

            return float(data["Close"].iloc[-1])
        except Exception as e:
            logger.warning(f"Failed to fetch price for {symbol}: {e}")
            return self._get_mock_price(symbol)

    def _get_mock_price(self, symbol: str) -> float:
        """Return mock price for testing"""
        mock_prices = {
            # India
            "RELIANCE.NS": 3000.0,
            "TCS.NS": 3800.0,
            "INFY.NS": 2200.0,
            "WIPRO.NS": 450.0,
            "HDFCBANK.NS": 1800.0,
            "ICICIBANK.NS": 950.0,
            "BAJAJFINSV.NS": 1850.0,
            "SBIN.NS": 750.0,
            "MARUTI.NS": 9500.0,
            "BHARTIARTL.NS": 750.0,
            # US
            "AAPL": 180.0,
            "MSFT": 380.0,
            "GOOGL": 140.0,
            "AMZN": 170.0,
            "META": 500.0,
            "NVDA": 850.0,
            "TSLA": 250.0,
            "JPM": 195.0,
            "V": 270.0,
            "JNJ": 155.0,
        }
        return mock_prices.get(symbol, 100.0)

    def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime):
        """
        Get historical data for a symbol for backtesting

        Args:
            symbol: Stock symbol
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            DataFrame with OHLCV data or empty DataFrame if unavailable
        """
        try:
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            return data
        except Exception as e:
            logger.warning(f"Failed to fetch historical data for {symbol}: {e}")
            return None

    def execute_trade(
        self,
        symbol: str,
        quantity: int,
        price: float,
        side: TradeSide,
    ) -> Dict[str, Any]:
        """
        Execute a trade (BUY or SELL)

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Price per share
            side: BUY or SELL

        Returns:
            Trade result dict with success status and details
        """
        total_value = quantity * price
        commission = total_value * 0.001  # 0.1% commission

        if side == TradeSide.BUY:
            required_cash = total_value + commission
            if self.portfolio.cash < required_cash:
                return {
                    "success": False,
                    "error": f"Insufficient funds. Required: {required_cash:.2f}, Available: {self.portfolio.cash:.2f}"
                }

            # Deduct cash
            self.portfolio.cash -= required_cash

            # Update or create holding
            if symbol in self.portfolio.holdings:
                holding = self.portfolio.holdings[symbol]
                # Calculate new average entry price
                old_total = holding.quantity * holding.entry_price
                new_total = old_total + (quantity * price)
                holding.quantity += quantity
                holding.entry_price = new_total / holding.quantity
                holding.current_price = price
            else:
                # Create new holding
                if symbol not in self.stocks:
                    return {"success": False, "error": f"Symbol not found: {symbol}"}

                stock_info = self.stocks[symbol]
                holding = Holding(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=price,
                    current_price=price,
                    sector=stock_info["sector"],
                    purchased_at=self.current_date,
                )
                self.portfolio.holdings[symbol] = holding

            # Record trade
            trade = Trade(
                trade_id=str(uuid.uuid4()),
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side,
                executed_at=self.current_date,
                commission=commission,
            )
            self.portfolio.trades.append(trade)

            return {
                "success": True,
                "trade_id": trade.trade_id,
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total_value": total_value,
                "commission": commission,
                "cash_remaining": self.portfolio.cash,
            }

        elif side == TradeSide.SELL:
            if symbol not in self.portfolio.holdings:
                return {"success": False, "error": f"No holdings for {symbol}"}

            holding = self.portfolio.holdings[symbol]
            if holding.quantity < quantity:
                return {
                    "success": False,
                    "error": f"Insufficient shares. Have: {holding.quantity}, Wanting to sell: {quantity}"
                }

            # Calculate P&L
            pnl = (price - holding.entry_price) * quantity
            pnl_percentage = ((price - holding.entry_price) / holding.entry_price * 100) if holding.entry_price > 0 else 0

            # Add cash
            self.portfolio.cash += total_value - commission

            # Update holding
            holding.quantity -= quantity
            holding.current_price = price

            # Remove holding if empty
            if holding.quantity == 0:
                del self.portfolio.holdings[symbol]

            # Record trade
            trade = Trade(
                trade_id=str(uuid.uuid4()),
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side,
                executed_at=self.current_date,
                commission=commission,
            )
            self.portfolio.trades.append(trade)

            return {
                "success": True,
                "trade_id": trade.trade_id,
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total_value": total_value,
                "commission": commission,
                "pnl": pnl,
                "pnl_percentage": pnl_percentage,
                "cash_remaining": self.portfolio.cash,
            }

        return {"success": False, "error": "Invalid trade side"}

    def update_prices(self, new_prices: Dict[str, float]) -> None:
        """Update prices for holdings"""
        for symbol, price in new_prices.items():
            if symbol in self.portfolio.holdings:
                self.portfolio.holdings[symbol].current_price = price

    def generate_market_event(self) -> Optional[Dict[str, Any]]:
        """Generate market event for current date"""
        # 10% chance of event each month
        if np.random.random() > 0.1:
            return None

        event_types = [
            EventType.MARKET_CRASH,
            EventType.EARNINGS_SEASON,
            EventType.SECTOR_ROTATION,
        ]

        if self.market == MarketType.US:
            event_types.extend([EventType.FED_DECISION, EventType.GEOPOLITICAL])
        elif self.market == MarketType.INDIA:
            event_types.extend([EventType.RBI_POLICY, EventType.GEOPOLITICAL])

        event_type = np.random.choice(event_types)

        event_descriptions = {
            EventType.MARKET_CRASH: {
                "description": "Market correction detected - indices down 5-10%",
                "multiplier": 0.93,  # 7% decline
                "sectors": None,  # All sectors affected
            },
            EventType.EARNINGS_SEASON: {
                "description": "Earnings season - volatility in Tech and Finance sectors",
                "multiplier": 0.98,
                "sectors": ["Technology", "Banking", "Financial Services"],
            },
            EventType.SECTOR_ROTATION: {
                "description": "Fund rotation - value stocks gaining, growth stocks declining",
                "multiplier": 0.97,
                "sectors": ["Technology"],
            },
            EventType.FED_DECISION: {
                "description": "Fed rate decision announced - mixed market reaction",
                "multiplier": 0.96,
                "sectors": None,
            },
            EventType.RBI_POLICY: {
                "description": "RBI monetary policy meeting - expected rate hike",
                "multiplier": 0.94,
                "sectors": None,
            },
            EventType.GEOPOLITICAL: {
                "description": "Geopolitical tensions rising - risk-off sentiment",
                "multiplier": 0.92,
                "sectors": None,
            },
        }

        event_info = event_descriptions[event_type]
        event = {
            "date": self.current_date,
            "type": event_type.value,
            "description": event_info["description"],
            "multiplier": event_info["multiplier"],
            "affected_sectors": event_info["sectors"],
        }

        # Apply event impact to prices
        for symbol in self.portfolio.holdings:
            if symbol in self.stocks:
                holding = self.portfolio.holdings[symbol]
                if event_info["sectors"] is None or holding.sector in event_info["sectors"]:
                    holding.current_price *= event_info["multiplier"]

        self.events.append(event)
        return event

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        portfolio_value = self.portfolio.get_total_value()
        total_pnl = self.portfolio.get_total_pnl()
        pnl_percentage = self.portfolio.get_total_pnl_percentage()

        # Calculate max drawdown
        max_value = max(self.portfolio.portfolio_value_history) if self.portfolio.portfolio_value_history else portfolio_value
        max_drawdown = ((max_value - portfolio_value) / max_value * 100) if max_value > 0 else 0

        # Calculate win rate
        sell_trades = [t for t in self.portfolio.trades if t.side == TradeSide.SELL]
        if sell_trades:
            # Estimate wins (trades with positive P&L)
            profitable_trades = sum(1 for holding in self.portfolio.holdings.values() if holding.get_pnl() > 0)
            win_rate = (profitable_trades / len(self.portfolio.holdings)) * 100 if self.portfolio.holdings else 0
        else:
            win_rate = 0

        return {
            "portfolio_value": portfolio_value,
            "total_pnl": total_pnl,
            "pnl_percentage": pnl_percentage,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "allocation": self.portfolio.get_allocation(),
            "holdings_count": len(self.portfolio.holdings),
        }

    def calculate_scores(self, initial_capital: float) -> Dict[str, float]:
        """
        Calculate multi-dimensional scoring (0-100 total)

        Returns:
            Dict with score breakdown
        """
        metrics = self.calculate_metrics()
        portfolio_value = metrics["portfolio_value"]
        pnl_percentage = metrics["pnl_percentage"]
        allocation = metrics["allocation"]

        # Portfolio Score (0-30): Based on wealth growth
        if portfolio_value >= initial_capital * 1.5:
            portfolio_score = 30
        elif portfolio_value >= initial_capital * 1.2:
            portfolio_score = 25
        elif portfolio_value >= initial_capital:
            portfolio_score = 20
        elif portfolio_value >= initial_capital * 0.9:
            portfolio_score = 10
        else:
            portfolio_score = max(0, 5 - (initial_capital - portfolio_value) / (initial_capital * 0.1) * 5)

        # Diversification Score (0-25): Based on sector spread
        sector_count = len(allocation)
        if sector_count >= 4:
            diversification_score = 25
        elif sector_count == 3:
            diversification_score = 20
        elif sector_count == 2:
            diversification_score = 10
        else:
            diversification_score = 5

        # Risk-Adjusted Score (0-20): Based on Sharpe ratio approximation
        max_drawdown = metrics["max_drawdown"]
        if max_drawdown < 5:
            risk_score = 20
        elif max_drawdown < 10:
            risk_score = 15
        elif max_drawdown < 20:
            risk_score = 10
        else:
            risk_score = 5

        # Timing Score (0-15): Based on win rate (approximated from holdings)
        win_rate = metrics["win_rate"]
        if win_rate >= 70:
            timing_score = 15
        elif win_rate >= 50:
            timing_score = 10
        else:
            timing_score = 5

        # Adherence Score (0-10): Based on strategy consistency
        adherence_score = 10  # Full points if using strategy

        total_score = portfolio_score + diversification_score + risk_score + timing_score + adherence_score

        return {
            "portfolio_score": portfolio_score,
            "diversification_score": diversification_score,
            "risk_adjusted_score": risk_score,
            "timing_score": timing_score,
            "adherence_score": adherence_score,
            "total_score": total_score,
        }

    def get_state(self) -> Dict[str, Any]:
        """Get current game state"""
        metrics = self.calculate_metrics()

        return {
            "market": self.market.value,
            "strategy": self.strategy,
            "current_date": self.current_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "initial_capital": self.initial_capital,
            "portfolio": {
                "cash": self.portfolio.cash,
                "holdings": {
                    symbol: {
                        "quantity": holding.quantity,
                        "entry_price": holding.entry_price,
                        "current_price": holding.current_price,
                        "value": holding.get_value(),
                        "pnl": holding.get_pnl(),
                        "pnl_percentage": holding.get_pnl_percentage(),
                        "sector": holding.sector,
                    }
                    for symbol, holding in self.portfolio.holdings.items()
                },
                "total_value": metrics["portfolio_value"],
                "total_pnl": metrics["total_pnl"],
                "pnl_percentage": metrics["pnl_percentage"],
            },
            "metrics": metrics,
            "events": self.events,
        }
