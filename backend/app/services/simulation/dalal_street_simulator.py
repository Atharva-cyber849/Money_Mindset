"""
Dalal Street Trading Simulation - Historical Indian stock market eras
Simulates 5 major periods (1991-2020) with realistic price movements and news events.
"""

import json
import random
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class MarketEra(str, Enum):
    LIBERALIZATION_1991_1996 = "liberalization_1991_1996"
    DOTCOM_1997_2002 = "dotcom_1997_2002"
    BULL_CRASH_2003_2008 = "bull_crash_2003_2008"
    RECOVERY_2009_2014 = "recovery_2009_2014"
    MODERN_2015_2020 = "modern_2015_2020"


class TradeType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class NewsEventType(str, Enum):
    RATE_HIKE = "rate_hike"
    RATE_CUT = "rate_cut"
    SCANDAL = "scandal"
    IPO = "ipo"
    SPLIT = "split"
    CORRECTION = "correction"
    BONUS = "bonus"
    EARNINGS_BEAT = "earnings_beat"
    EARNINGS_MISS = "earnings_miss"
    CRISIS = "crisis"
    # New Indian sector disruptions
    IT_VISA_RESTRICTIONS = "it_visa_restrictions"        # -15% IT sector
    PHARMA_PRICE_CONTROL = "pharma_price_control"        # -20% Pharma
    PSU_NPA_CRISIS = "psu_npa_crisis"                    # -25% PSU banks
    NBFC_STRESS = "nbfc_stress"                          # -30% NBFC
    AUTO_EV_TRANSITION = "auto_ev_transition"            # -18% Auto
    TELECOM_DISRUPTION = "telecom_disruption"            # -40% Telecom (competition)
    REALESTATE_DEMONETIZATION = "realestate_demonetization"  # -25% Real estate
    RETAIL_ECOMMERCE = "retail_ecommerce"                # -15% Retail (competition)
    # Regulatory disruptions
    SEBI_BAN = "sebi_ban"                                # -15% sector
    PROMOTER_PLEDGING = "promoter_pledging"              # -15% stock
    CORPORATE_SCANDAL = "corporate_scandal"              # -60% company stock
    DIVIDEND_SHOCK = "dividend_shock"                    # -10% company
    FII_CAP = "fii_cap"                                  # -8% markets
    # Rupee crises
    ASIAN_CRISIS_1997 = "asian_crisis_1997"              # -20% rupee depreciation
    TAPER_TANTRUM_2013 = "taper_tantrum_2013"            # -15% outflows
    COVID_OIL_CRASH_2020 = "covid_oil_crash_2020"        # -20% imports affected
    UKRAINE_GEOPOLITICAL_2022 = "ukraine_geopolitical_2022"  # -8% rupee pressure
    # Election cycles
    ASSEMBLY_ELECTIONS = "assembly_elections"            # ±3% volatility
    GENERAL_ELECTIONS = "general_elections"              # ±5% volatility


@dataclass
class StockQuote:
    symbol: str
    name: str
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: int
    pe_ratio: float
    sector: str
    market_cap_category: str


@dataclass
class Trade:
    quarter: int
    symbol: str
    trade_type: TradeType
    quantity: int
    price_at_trade: float
    commission: float
    timestamp: str = ""

    def to_dict(self):
        return {
            "quarter": self.quarter,
            "symbol": self.symbol,
            "trade_type": self.trade_type.value,
            "quantity": self.quantity,
            "price_at_trade": self.price_at_trade,
            "commission": self.commission,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            quarter=data.get("quarter", 0),
            symbol=data.get("symbol", ""),
            trade_type=TradeType(data.get("trade_type", "hold")),
            quantity=data.get("quantity", 0),
            price_at_trade=data.get("price_at_trade", 0),
            commission=data.get("commission", 0),
            timestamp=data.get("timestamp", ""),
        )


@dataclass
class NewsEvent:
    quarter: int
    event_type: NewsEventType
    affected_symbols: List[str]
    headline: str
    description: str
    price_impact: float

    def to_dict(self):
        return {
            "quarter": self.quarter,
            "event_type": self.event_type.value,
            "affected_symbols": self.affected_symbols,
            "headline": self.headline,
            "description": self.description,
            "price_impact": self.price_impact,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            quarter=data.get("quarter", 0),
            event_type=NewsEventType(data.get("event_type", "correction")),
            affected_symbols=data.get("affected_symbols", []),
            headline=data.get("headline", ""),
            description=data.get("description", ""),
            price_impact=data.get("price_impact", 0),
        )


@dataclass
class Portfolio:
    cash: float
    holdings: Dict[str, int] = field(default_factory=dict)
    trades: List[Trade] = field(default_factory=list)
    portfolio_value_history: List[float] = field(default_factory=list)

    def to_dict(self):
        return {
            "cash": self.cash,
            "holdings": self.holdings,
            "trades": [t.to_dict() for t in self.trades],
            "portfolio_value_history": self.portfolio_value_history,
        }

    @classmethod
    def from_dict(cls, data):
        trades = [Trade.from_dict(t) for t in data.get("trades", [])]
        return cls(
            cash=data.get("cash", 0),
            holdings=data.get("holdings", {}),
            trades=trades,
            portfolio_value_history=data.get("portfolio_value_history", []),
        )


class DalalStreetSimulator:
    """Historical Indian stock market trading simulator"""

    ERA_CONFIGS = {
        MarketEra.LIBERALIZATION_1991_1996: {
            "starting_capital": 10000,
            "num_stocks": 10,
            "base_volatility": 0.15,
            "avg_annual_return": 0.10,
            "narrative": "The Indian economy opens to foreign investment. New opportunities emerge for retail investors.",
            "crisis_config": None,
        },
        MarketEra.DOTCOM_1997_2002: {
            "starting_capital": None,  # Inherited from previous era
            "num_stocks": 20,
            "base_volatility": 0.25,
            "avg_annual_return": 0.35,  # Bubble years average
            "narrative": "The IT boom drives valuations to unprecedented heights. Tech stocks soar while fundamentals are ignored.",
            "crisis_config": {"quarter": 12, "name": "Dot-Com Crash", "severity": -0.45},
        },
        MarketEra.BULL_CRASH_2003_2008: {
            "starting_capital": None,
            "num_stocks": 25,
            "base_volatility": 0.20,
            "avg_annual_return": 0.28,  # Bull years before crash
            "narrative": "A powerful bull market drives valuations higher. Infrastructure spending fuels growth. But cracks form beneath the surface.",
            "crisis_config": {"quarter": 18, "name": "Global Financial Crisis", "severity": -0.55},
        },
        MarketEra.RECOVERY_2009_2014: {
            "starting_capital": 100000,
            "num_stocks": 30,
            "base_volatility": 0.12,
            "avg_annual_return": 0.22,
            "narrative": "Markets recover slowly from the 2008 crisis. Regulatory reforms strengthen the system. Growth returns cautiously.",
            "crisis_config": None,
        },
        MarketEra.MODERN_2015_2020: {
            "starting_capital": None,
            "num_stocks": 40,
            "base_volatility": 0.18,
            "avg_annual_return": 0.18,
            "narrative": "Markets ride through demonetization, GST roll-out, and finally, the COVID-19 pandemic. Resilience becomes key.",
            "crisis_config": {"quarter": 16, "name": "COVID-19 Pandemic", "severity": -0.35},
        },
    }

    STOCKS = {
        "liberalization": [
            ("INFY", "Infosys", "IT", "Large Cap", 1200),
            ("TCS", "Tata Consultancy Services", "IT", "Large Cap", 2000),
            ("RELIANCE", "Reliance Industries", "Energy", "Large Cap", 800),
            ("HDFC", "HDFC Bank", "Banking", "Large Cap", 500),
            ("ICICI", "ICICI Bank", "Banking", "Large Cap", 450),
            ("ITC", "ITC Limited", "FMCG", "Large Cap", 250),
            ("SBIN", "State Bank of India", "Banking", "Large Cap", 300),
            ("BHARTI", "Bharti Airtel", "Telecom", "Large Cap", 600),
            ("MARUTI", "Maruti Suzuki", "Auto", "Large Cap", 2500),
            ("AXIS", "Axis Bank", "Banking", "Large Cap", 350),
        ],
        "dotcom": [
            ("INFY", "Infosys", "IT", "Large Cap", 1500),
            ("TCS", "Tata Consultancy Services", "IT", "Large Cap", 2200),
            ("WIPRO", "Wipro", "IT", "Large Cap", 1800),
            ("HCL", "HCL Technologies", "IT", "Mid Cap", 1200),
            ("PEGATECH", "Pegasus Tech", "IT", "Mid Cap", 800),
            ("MINDTREE", "MindTree", "IT", "Mid Cap", 950),
            ("RELIANCE", "Reliance Industries", "Energy", "Large Cap", 950),
            ("HDFC", "HDFC Bank", "Banking", "Large Cap", 600),
            ("ICICI", "ICICI Bank", "Banking", "Large Cap", 550),
            ("ITC", "ITC Limited", "FMCG", "Large Cap", 300),
            ("SBIN", "State Bank of India", "Banking", "Large Cap", 400),
            ("BHARTI", "Bharti Airtel", "Telecom", "Large Cap", 800),
            ("MARUTI", "Maruti Suzuki", "Auto", "Large Cap", 3000),
            ("AXIS", "Axis Bank", "Banking", "Large Cap", 450),
            ("SUNPHARMA", "Sun Pharmaceuticals", "Pharma", "Mid Cap", 500),
            ("DMART", "Avenue Supermarts", "Retail", "Large Cap", 1200),
            ("BAJAJ", "Bajaj Auto", "Auto", "Large Cap", 2200),
            ("POWERGRID", "Power Grid", "Utilities", "Large Cap", 120),
            ("ONGC", "Oil & Natural Gas Corp", "Energy", "Large Cap", 900),
            ("TATASTEEL", "Tata Steel", "Steel", "Large Cap", 1100),
            ("NYKAA", "Nykaa Fashion", "Retail", "Mid Cap", 400),
            # Additional modern stocks (2010+)
            ("BAJAJFINSV", "Bajaj Financial Services", "Finance", "Large Cap", 650),
            ("HDFCBANK", "HDFC Bank New", "Banking", "Large Cap", 780),
            ("SBILIFE", "SBI Life Insurance", "Finance", "Large Cap", 520),
            ("KOTAKBANK", "Kotak Mahindra Bank", "Banking", "Large Cap", 1100),
            ("LTIM", "LTI MindTree", "IT", "Large Cap", 2800),
            ("PAYTM", "Paytm", "FinTech", "Mid Cap", 450),
            ("ZOMATO", "Zomato Limited", "Tech", "Mid Cap", 85),
            ("NYKAA_NEW", "Nykaa Online", "E-commerce", "Mid Cap", 150),
            ("ASHOKLEYLAND", "Ashok Leyland", "Auto", "Mid Cap", 180),
            ("HEROMOTOCORP", "Hero MotoC", "Auto", "Large Cap", 2500),
            ("MAHABANK", "Mahanagar Bank", "Banking", "Small Cap", 50),
            ("SHRIRAM", "Shriram Transport", "Finance", "Mid Cap", 1300),
            ("FEDERALBANK", "Federal Bank", "Banking", "Mid Cap", 420),
            ("PIRAMALENTERP", "Piramal Enterprises", "Pharma", "Mid Cap", 2100),
            ("LUPIN", "Lupin Limited", "Pharma", "Large Cap", 800),
            ("CIPLA", "Cipla Limited", "Pharma", "Large Cap", 900),
            ("DABUR", "Dabur India", "FMCG", "Large Cap", 580),
            ("NESTLEIND", "Nestle India", "FMCG", "Large Cap", 23000),
            ("BRITANNIA", "Britannia Industries", "FMCG", "Large Cap", 4400),
        ],
    }

    def __init__(
        self,
        era: MarketEra,
        starting_portfolio: Optional[Portfolio] = None,
        inherited_capital: Optional[float] = None,
    ):
        self.era = era
        self.current_quarter = 0
        self.config = self.ERA_CONFIGS[era]

        # Initialize portfolio
        if starting_portfolio:
            self.portfolio = starting_portfolio
        else:
            capital = inherited_capital or self.config.get("starting_capital", 0)
            self.portfolio = Portfolio(cash=capital, holdings={}, trades=[])

        # Initialize stocks
        self.stock_quotes: Dict[str, StockQuote] = self._initialize_stocks()
        self.stock_base_prices: Dict[str, float] = {}  # Track base prices for calculation
        for symbol, quote in self.stock_quotes.items():
            self.stock_base_prices[symbol] = quote.current_price

        # Market state
        self.market_index_history: List[float] = [100.0]
        self.news_log: List[NewsEvent] = []
        self.quarterly_snapshots: List[Dict] = []

    def _initialize_stocks(self) -> Dict[str, StockQuote]:
        """Create initial stock quotes for the era"""
        stocks = {}

        # Use liberalization stocks as base, expand for later eras
        base_stocks = self.STOCKS.get("liberalization", [])
        if self.era in [
            MarketEra.DOTCOM_1997_2002,
            MarketEra.BULL_CRASH_2003_2008,
            MarketEra.RECOVERY_2009_2014,
            MarketEra.MODERN_2015_2020,
        ]:
            base_stocks = self.STOCKS.get("dotcom", [])

        for symbol, name, sector, cap_category, base_price in base_stocks[
            : self.config["num_stocks"]
        ]:
            # Add slight variance to starting prices
            current_price = base_price * random.uniform(0.95, 1.05)
            stocks[symbol] = StockQuote(
                symbol=symbol,
                name=name,
                current_price=current_price,
                open_price=current_price,
                high_price=current_price * 1.02,
                low_price=current_price * 0.98,
                volume=random.randint(1000000, 50000000),
                pe_ratio=random.uniform(12, 40),
                sector=sector,
                market_cap_category=cap_category,
            )

        return stocks

    def _generate_quarterly_return(self, base_return: float) -> float:
        """Generate quarterly return with volatility"""
        volatility = self.config["base_volatility"]
        random_component = random.gauss(0, volatility)
        quarterly_base = (base_return / 4) * random.uniform(0.8, 1.2)
        return quarterly_base + random_component

    def _apply_crisis_if_applies(self) -> bool:
        """Check if crisis applies this quarter and apply it"""
        crisis = self.config.get("crisis_config")
        if crisis and self.current_quarter == crisis["quarter"]:
            return True
        return False

    def _generate_news_event(self) -> Optional[NewsEvent]:
        """30% chance to generate a news event each quarter"""
        if random.random() > 0.30:
            return None

        event_types = list(NewsEventType)
        event_type = random.choice(event_types)

        # Determine affected stocks
        num_affected = random.randint(1, 3)
        affected = random.sample(list(self.stock_quotes.keys()), num_affected)

        # Generate impact
        impact_map = {
            NewsEventType.RATE_HIKE: -0.03,
            NewsEventType.RATE_CUT: 0.02,
            NewsEventType.SCANDAL: -0.05,
            NewsEventType.IPO: 0.03,
            NewsEventType.SPLIT: 0.02,
            NewsEventType.CORRECTION: -0.08,
            NewsEventType.BONUS: 0.01,
            NewsEventType.EARNINGS_BEAT: 0.04,
            NewsEventType.EARNINGS_MISS: -0.03,
            NewsEventType.CRISIS: -0.30,
        }

        impact = impact_map.get(event_type, 0) + random.gauss(0, 0.01)

        headlines = {
            NewsEventType.RATE_HIKE: "RBI Raises Interest Rates",
            NewsEventType.RATE_CUT: "RBI Cuts Interest Rates",
            NewsEventType.SCANDAL: "Corporate Scandal Emerges",
            NewsEventType.IPO: "New IPO Launches Successfully",
            NewsEventType.SPLIT: "Stock Split Announced",
            NewsEventType.CORRECTION: "Market Correction Underway",
            NewsEventType.BONUS: "Bonus Announcement",
            NewsEventType.EARNINGS_BEAT: "Earnings Beat Expectations",
            NewsEventType.EARNINGS_MISS: "Earnings Miss Estimates",
            NewsEventType.CRISIS: "Market Crisis Unfolds",
        }

        event = NewsEvent(
            quarter=self.current_quarter,
            event_type=event_type,
            affected_symbols=affected,
            headline=headlines.get(event_type, "Market Event"),
            description=f"Affects {affected} - Impact: {impact*100:.1f}%",
            price_impact=impact,
        )

        self.news_log.append(event)
        return event

    def advance_quarter(self) -> Tuple[float, Optional[NewsEvent]]:
        """Progress simulation by one quarter"""
        self.current_quarter += 1

        # Check for crisis
        is_crisis = self._apply_crisis_if_applies()
        if is_crisis:
            crisis = self.config.get("crisis_config")
            crisis_impact = crisis["severity"]
            news = NewsEvent(
                quarter=self.current_quarter,
                event_type=NewsEventType.CRISIS,
                affected_symbols=list(self.stock_quotes.keys()),
                headline=crisis["name"],
                description=f"Market impact: {crisis_impact*100:.1f}%",
                price_impact=crisis_impact,
            )
            self.news_log.append(news)
        else:
            news = self._generate_news_event()

        # Update stock prices
        base_return = self._generate_quarterly_return(
            self.config["avg_annual_return"]
        )
        total_market_movement = base_return

        for symbol in self.stock_quotes:
            quote = self.stock_quotes[symbol]

            # Calculate direction and magnitude
            stock_return = base_return + random.gauss(0, 0.02)

            # Apply news impact if this stock is affected
            if news and symbol in news.affected_symbols:
                stock_return += news.price_impact

            # Apply crisis impact if applicable
            if is_crisis:
                stock_return += crisis_impact

            # Update price
            new_price = quote.current_price * (1 + stock_return)
            quote.current_price = max(new_price, quote.open_price * 0.5)  # Floor at 50% of open
            quote.high_price = max(quote.high_price, quote.current_price)
            quote.low_price = min(quote.low_price, quote.current_price)

        # Update market index
        market_index = self.market_index_history[-1] * (1 + total_market_movement)
        self.market_index_history.append(market_index)

        # Record portfolio snapshot
        portfolio_value = self._calculate_portfolio_value()
        self.portfolio.portfolio_value_history.append(portfolio_value)
        self.quarterly_snapshots.append(
            {
                "quarter": self.current_quarter,
                "portfolio_value": portfolio_value,
                "market_index": market_index,
            }
        )

        return total_market_movement, news

    def execute_trade(
        self, symbol: str, trade_type: TradeType, quantity: int
    ) -> Tuple[bool, str]:
        """Execute a trade"""
        if symbol not in self.stock_quotes:
            return False, f"Stock {symbol} not available"

        quote = self.stock_quotes[symbol]
        price = quote.current_price

        if trade_type == TradeType.BUY:
            cost = price * quantity
            commission = cost * 0.005  # 0.5% commission
            total_cost = cost + commission

            if self.portfolio.cash < total_cost:
                return False, f"Insufficient cash. Need ₹{total_cost:.0f}, have ₹{self.portfolio.cash:.0f}"

            self.portfolio.cash -= total_cost
            self.portfolio.holdings[symbol] = self.portfolio.holdings.get(symbol, 0) + quantity
            trade = Trade(
                quarter=self.current_quarter,
                symbol=symbol,
                trade_type=trade_type,
                quantity=quantity,
                price_at_trade=price,
                commission=commission,
            )
            self.portfolio.trades.append(trade)
            return True, f"Bought {quantity} of {symbol} @ ₹{price:.0f}"

        elif trade_type == TradeType.SELL:
            current_holding = self.portfolio.holdings.get(symbol, 0)
            if current_holding < quantity:
                return False, f"Cannot sell {quantity}, holding {current_holding} only"

            proceeds = price * quantity
            commission = proceeds * 0.005
            net_proceeds = proceeds - commission

            self.portfolio.cash += net_proceeds
            self.portfolio.holdings[symbol] -= quantity
            if self.portfolio.holdings[symbol] == 0:
                del self.portfolio.holdings[symbol]

            trade = Trade(
                quarter=self.current_quarter,
                symbol=symbol,
                trade_type=trade_type,
                quantity=quantity,
                price_at_trade=price,
                commission=commission,
            )
            self.portfolio.trades.append(trade)
            return True, f"Sold {quantity} of {symbol} @ ₹{price:.0f}"

        elif trade_type == TradeType.HOLD:
            trade = Trade(
                quarter=self.current_quarter,
                symbol=symbol,
                trade_type=trade_type,
                quantity=0,
                price_at_trade=price,
                commission=0,
            )
            self.portfolio.trades.append(trade)
            return True, f"Hold decision recorded for {symbol}"

        return False, "Unknown trade type"

    def _calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        holdings_value = 0
        for symbol, quantity in self.portfolio.holdings.items():
            if symbol in self.stock_quotes:
                holdings_value += self.stock_quotes[symbol].current_price * quantity
        return self.portfolio.cash + holdings_value

    def get_portfolio_value_summary(self) -> Dict:
        """Get portfolio summary"""
        total = self._calculate_portfolio_value()
        holdings_value = total - self.portfolio.cash
        return {
            "total_value": total,
            "cash": self.portfolio.cash,
            "holdings_value": holdings_value,
            "holdings": self.portfolio.holdings.copy(),
        }

    def get_portfolio_performance(self) -> Dict:
        """Calculate performance metrics"""
        if not self.portfolio.portfolio_value_history:
            return {"starting": 0, "ending": 0, "return_pct": 0}

        starting_value = (
            self.portfolio.portfolio_value_history[0]
            if self.portfolio.portfolio_value_history
            else self._calculate_portfolio_value()
        )
        ending_value = self._calculate_portfolio_value()
        return_pct = (ending_value - starting_value) / starting_value * 100 if starting_value > 0 else 0

        # Calculate max drawdown
        max_value = max(self.portfolio.portfolio_value_history)
        min_value = min(self.portfolio.portfolio_value_history)
        max_drawdown = (max_value - min_value) / max_value * 100 if max_value > 0 else 0

        # Market comparison
        market_starting = self.market_index_history[0]
        market_ending = self.market_index_history[-1]
        market_return_pct = (market_ending - market_starting) / market_starting * 100

        return {
            "starting_value": starting_value,
            "ending_value": ending_value,
            "return_pct": return_pct,
            "return_amount": ending_value - starting_value,
            "max_drawdown": max_drawdown,
            "market_return_pct": market_return_pct,
        }

    def generate_quarterly_decision(self) -> Dict:
        """Generate a strategic decision point for the quarter"""
        context = f"You're at the end of Quarter {self.current_quarter}. Your portfolio is worth ₹{self._calculate_portfolio_value():.0f}."

        # Get top performers and underperformers
        top_performers = sorted(
            self.stock_quotes.items(),
            key=lambda x: x[1].current_price,
            reverse=True,
        )[:3]
        underperformers = sorted(
            self.stock_quotes.items(),
            key=lambda x: x[1].current_price,
        )[:3]

        options = [
            {
                "id": 0,
                "text": f"Increase exposure to top performers ({top_performers[0][0]}, {top_performers[1][0]})",
                "action": "buy_leaders",
                "symbols": [t[0] for t in top_performers],
            },
            {
                "id": 1,
                "text": f"Reduce risk by exiting underperformers",
                "action": "sell_losers",
                "symbols": [t[0] for t in underperformers],
            },
            {
                "id": 2,
                "text": f"Maintain current position and hold",
                "action": "hold",
                "symbols": [],
            },
        ]

        return {
            "quarter": self.current_quarter,
            "title": "Quarterly Strategic Decision",
            "context": context,
            "options": options,
        }

    def get_final_scores(self) -> Dict:
        """Calculate final performance scores"""
        perf = self.get_portfolio_performance()

        # Timing score: How well did they catch the moves?
        # Compare their trades to market movements
        timing_score = min(100, max(0, 50 + (perf["return_pct"] - perf["market_return_pct"]) / 2))

        # Portfolio management: Sector and stock selection quality
        holdings_performance = 0
        for symbol, quantity in self.portfolio.holdings.items():
            if symbol in self.stock_quotes:
                # Estimate gain on current holding (simplified)
                holdings_performance += quantity

        portfolio_mgmt_score = min(
            100,
            max(0, 50 + (len(self.portfolio.holdings) / max(1, self.config["num_stocks"])) * 20),
        )

        # Risk score: Lower drawdown = higher risk management
        risk_score = min(100, 100 - perf.get("max_drawdown", 50))

        # Overall: Weighted combination
        overall_score = (
            timing_score * 0.35 + portfolio_mgmt_score * 0.35 + risk_score * 0.30
        )

        return {
            "starting_value": perf["starting_value"],
            "ending_value": perf["ending_value"],
            "return_percentage": perf["return_pct"],
            "return_amount": perf["return_amount"],
            "market_return_percentage": perf["market_return_pct"],
            "max_drawdown": perf["max_drawdown"],
            "timing_score": timing_score,
            "portfolio_management_score": portfolio_mgmt_score,
            "risk_score": risk_score,
            "overall_score": overall_score,
        }

    def get_trade_summary(self) -> List[Dict]:
        """Get summary of all trades made"""
        trades_list = []
        for trade in self.portfolio.trades:
            trades_list.append(
                {
                    "quarter": trade.quarter,
                    "symbol": trade.symbol,
                    "type": trade.trade_type.value,
                    "quantity": trade.quantity,
                    "price": trade.price_at_trade,
                    "commission": trade.commission,
                }
            )
        return trades_list

    def serialize_state(self) -> str:
        """Serialize full game state to JSON"""
        return json.dumps(
            {
                "era": self.era.value,
                "current_quarter": self.current_quarter,
                "portfolio": self.portfolio.to_dict(),
                "market_index_history": self.market_index_history,
                "news_log": [n.to_dict() for n in self.news_log],
                "quarterly_snapshots": self.quarterly_snapshots,
            }
        )

    @classmethod
    def deserialize_state(cls, era: MarketEra, state_json: str):
        """Deserialize and restore game state"""
        data = json.loads(state_json)

        simulator = cls(era=era)
        simulator.current_quarter = data.get("current_quarter", 0)
        simulator.portfolio = Portfolio.from_dict(data.get("portfolio", {}))
        simulator.market_index_history = data.get("market_index_history", [100.0])
        simulator.news_log = [
            NewsEvent.from_dict(n) for n in data.get("news_log", [])
        ]
        simulator.quarterly_snapshots = data.get("quarterly_snapshots", [])

        return simulator
