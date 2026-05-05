"""
AI Market Participants & Order Book Simulator for Paper Trading
Generates realistic price movements based on supply/demand from 1000 simulated traders
"""

import numpy as np
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ParticipantType(str, Enum):
    """Types of AI traders"""
    HIGH_FREQUENCY = "hft"
    MOMENTUM = "momentum"
    CONSERVATIVE = "conservative"
    VALUE_INVESTOR = "value_investor"


class SignalType(str, Enum):
    """Trading signal types"""
    TREND_FOLLOWING = "trend_following"
    VALUE_BUY = "value_buy"
    REBALANCE = "rebalance"
    SCALP = "scalp"
    PORTFOLIO_ADJUSTMENT = "portfolio_adjustment"
    RANDOM = "random"


class MarketRegime(str, Enum):
    """Macro behavioral state for participant sentiment"""
    NORMAL = "normal"
    RISK_ON = "risk_on"
    RISK_OFF = "risk_off"
    PANIC = "panic"
    EUPHORIA = "euphoria"


@dataclass
class MarketEvent:
    """Scenario event that can temporarily shock prices/liquidity"""
    event_type: str
    description: str
    severity: float
    side_bias: float  # -1 sell pressure, +1 buy pressure
    volatility_multiplier: float
    affected_sectors: List[str]
    duration_ticks: int
    started_at_tick: int
    origin: str = "random"


@dataclass
class AIParticipant:
    """Single AI market participant"""
    participant_id: int
    trader_type: ParticipantType
    risk_tolerance: float  # 0-100
    preferred_sectors: List[str]
    cash_balance: float
    holdings: Dict[str, int]  # {symbol: quantity}
    entry_prices: Dict[str, float]  # {symbol: avg_entry_price}
    trade_frequency: float  # 0-1, probability of trading on each round
    panic_sensitivity: float = 0.5  # 0-1 how strongly this trader reacts to fear
    fomo_sensitivity: float = 0.5  # 0-1 how strongly this trader chases rallies
    last_trade_timestamp: float = 0
    portfolio_value: float = 0

    def get_portfolio_value(self, prices: Dict[str, float]) -> float:
        """Calculate current portfolio value"""
        value = self.cash_balance
        for symbol, qty in self.holdings.items():
            value += qty * prices.get(symbol, 0)
        return value


@dataclass
class Order:
    """Single order in order book"""
    participant_id: int
    quantity: int
    price: float
    side: str  # BUY or SELL


@dataclass
class OrderBookSnapshot:
    """Snapshot of order book state"""
    symbol: str
    timestamp: datetime
    buy_orders: List[Order]
    sell_orders: List[Order]
    best_bid: float
    best_ask: float
    mid_price: float
    bid_ask_spread: float
    spread_percentage: float
    total_buy_volume: int
    total_sell_volume: int
    imbalance: float  # -1 to 1, negative = more sellers, positive = more buyers
    volatility: float


class AITraderEngine:
    """Generates market dynamics from 1000 AI participants"""

    def __init__(
        self,
        session_id: str,
        market_type: str,
        random_seed: int,
        participant_count: int = 1000,
        hft_pct: float = 10,
        momentum_pct: float = 30,
        conservative_pct: float = 40,
        value_investor_pct: float = 20,
    ):
        """
        Initialize AI trader engine

        Args:
            session_id: Paper trading session ID (for determinism)
            market_type: 'india', 'us', or 'both'
            random_seed: Seed for reproducible participants
            participant_count: Total number of AI traders
            hft_pct, momentum_pct, conservative_pct, value_investor_pct: Distribution
        """
        self.session_id = session_id
        self.market_type = market_type
        self.random_seed = random_seed
        self.participant_count = participant_count

        # Initialize random generator for determinism
        self.rng = np.random.RandomState(random_seed)
        random.seed(random_seed)

        # Composition
        self.hft_count = int(participant_count * hft_pct / 100)
        self.momentum_count = int(participant_count * momentum_pct / 100)
        self.conservative_count = int(participant_count * conservative_pct / 100)
        self.value_investor_count = max(0, participant_count - self.hft_count - self.momentum_count - self.conservative_count)

        # Initialize participants
        self.participants: List[AIParticipant] = []
        self.base_prices: Dict[str, float] = {}
        self.symbol_metadata: Dict[str, Dict[str, str]] = {}
        self.price_history: Dict[str, List[float]] = {}
        self.order_book_history: Dict[str, List[OrderBookSnapshot]] = {}

        # Market state for realistic behavior over time
        self.tick_count: int = 0
        self.market_regime: MarketRegime = MarketRegime.NORMAL
        self.regime_ticks_remaining: int = 0
        self.active_event: Optional[MarketEvent] = None
        self.recent_events: List[Dict] = []
        self.recent_ipos: List[Dict] = []
        self.pending_ipos: List[Dict] = self._build_ipo_pipeline()
        self.macro_calendar: List[Dict] = self._build_macro_calendar()

        self._initialize_participants()

    def _initialize_participants(self):
        """Create 1000 AI trader profiles deterministically"""
        self.participants = []
        participant_id = 0

        # Create HFT traders
        for _ in range(self.hft_count):
            self.participants.append(self._create_participant(participant_id, ParticipantType.HIGH_FREQUENCY))
            participant_id += 1

        # Create momentum traders
        for _ in range(self.momentum_count):
            self.participants.append(self._create_participant(participant_id, ParticipantType.MOMENTUM))
            participant_id += 1

        # Create conservative traders
        for _ in range(self.conservative_count):
            self.participants.append(self._create_participant(participant_id, ParticipantType.CONSERVATIVE))
            participant_id += 1

        # Create value investors
        for _ in range(self.value_investor_count):
            self.participants.append(self._create_participant(participant_id, ParticipantType.VALUE_INVESTOR))
            participant_id += 1

        logger.info(
            f"Initialized {len(self.participants)} AI participants: "
            f"{self.hft_count} HFT, {self.momentum_count} momentum, "
            f"{self.conservative_count} conservative, {self.value_investor_count} value investors"
        )

    def _create_participant(self, participant_id: int, trader_type: ParticipantType) -> AIParticipant:
        """Create single participant with type-specific traits"""
        if trader_type == ParticipantType.HIGH_FREQUENCY:
            risk_tolerance = self.rng.uniform(60, 100)
            trade_frequency = 0.9  # Trade almost every round
            cash = self.rng.uniform(50000, 200000)
        elif trader_type == ParticipantType.MOMENTUM:
            risk_tolerance = self.rng.uniform(50, 80)
            trade_frequency = 0.6  # Trade 60% of rounds
            cash = self.rng.uniform(100000, 300000)
        elif trader_type == ParticipantType.CONSERVATIVE:
            risk_tolerance = self.rng.uniform(20, 50)
            trade_frequency = 0.2  # Trade 20% of rounds
            cash = self.rng.uniform(150000, 400000)
        else:  # VALUE_INVESTOR
            risk_tolerance = self.rng.uniform(30, 60)
            trade_frequency = 0.15  # Trade 15% of rounds
            cash = self.rng.uniform(200000, 500000)

        # Random preferred sectors
        sectors = ["Technology", "Banking", "Financials", "Energy", "Healthcare", "IT", "Automotive", "Consumer"]
        preferred_sectors = self.rng.choice(sectors, size=self.rng.randint(2, 4), replace=False).tolist()

        return AIParticipant(
            participant_id=participant_id,
            trader_type=trader_type,
            risk_tolerance=risk_tolerance,
            preferred_sectors=preferred_sectors,
            cash_balance=cash,
            holdings={},
            entry_prices={},
            trade_frequency=trade_frequency,
            panic_sensitivity=self.rng.uniform(0.2, 1.0),
            fomo_sensitivity=self.rng.uniform(0.2, 1.0),
        )

    def set_base_prices(self, prices: Dict[str, float]):
        """Set reference prices (from yfinance) to anchor market"""
        self.base_prices = prices.copy()
        # Initialize price history
        for symbol in prices:
            self.price_history[symbol] = [prices[symbol]]
            self.order_book_history[symbol] = []
            self.symbol_metadata.setdefault(
                symbol,
                {
                    "name": symbol,
                    "sector": self._infer_sector(symbol),
                },
            )

        # Seed starting holdings so AI can continuously buy and sell from tick 1
        self._seed_initial_holdings()

    def generate_orders(
        self,
        symbol: str,
        current_price: float,
        market_trend: float,  # -1 to 1, direction of price trend
    ) -> Tuple[List[Order], List[Order]]:
        """
        Generate buy/sell orders from all participants for a symbol

        Args:
            symbol: Stock symbol
            current_price: Current market price
            market_trend: -1 (downtrend) to +1 (uptrend)

        Returns:
            (buy_orders, sell_orders)
        """
        buy_orders = []
        sell_orders = []

        for participant in self.participants:
            # Decide if participant trades this round
            activity = self._get_participant_activity(participant, symbol)
            if self.rng.random() > activity:
                continue

            # Determine trading signal
            decision = self._generate_trading_decision(
                participant,
                symbol,
                current_price,
                market_trend,
            )

            if decision and decision["quantity"] > 0:
                order = Order(
                    participant_id=participant.participant_id,
                    quantity=decision["quantity"],
                    price=decision["price"],
                    side=decision["side"],
                )

                if decision["side"] == "BUY":
                    buy_orders.append(order)
                else:
                    sell_orders.append(order)

                # Keep participant inventory stateful to mimic continuous market making
                self._apply_ai_fill(participant, symbol, decision["side"], decision["quantity"], decision["price"])

        return buy_orders, sell_orders

    def _generate_trading_decision(
        self,
        participant: AIParticipant,
        symbol: str,
        current_price: float,
        market_trend: float,
    ) -> Optional[Dict]:
        """
        Decide if participant should trade and at what price/quantity

        Returns:
            Dict with {side, quantity, price, signal_type} or None
        """
        signal_type = None
        decision = None

        # Get participant's portfolio value
        portfolio_value = participant.get_portfolio_value(self.base_prices)

        # Decision logic by trader type
        if participant.trader_type == ParticipantType.HIGH_FREQUENCY:
            decision = self._hft_decision(participant, symbol, current_price, market_trend)
            signal_type = SignalType.SCALP

        elif participant.trader_type == ParticipantType.MOMENTUM:
            decision = self._momentum_decision(participant, symbol, current_price, market_trend)
            signal_type = SignalType.TREND_FOLLOWING

        elif participant.trader_type == ParticipantType.CONSERVATIVE:
            decision = self._conservative_decision(participant, symbol, current_price, portfolio_value)
            signal_type = SignalType.PORTFOLIO_ADJUSTMENT

        elif participant.trader_type == ParticipantType.VALUE_INVESTOR:
            decision = self._value_investor_decision(participant, symbol, current_price)
            signal_type = SignalType.VALUE_BUY

        if decision:
            decision = self._apply_behavioral_overlay(participant, symbol, current_price, decision)
            decision["signal_type"] = signal_type

        return decision

    def _hft_decision(
        self,
        participant: AIParticipant,
        symbol: str,
        current_price: float,
        market_trend: float,
    ) -> Optional[Dict]:
        """High-frequency trader: scalp bid-ask spreads, follow momentum"""
        if participant.cash_balance < current_price * 10:
            return None  # Need cash to trade

        # Follow market trend strongly
        if market_trend > 0.3:
            return {
                "side": "BUY",
                "quantity": self.rng.randint(5, 50),
                "price": current_price * (1 + self.rng.uniform(0, 0.001)),  # Buy slightly above market
            }
        elif market_trend < -0.3:
            return {
                "side": "SELL",
                "quantity": self.rng.randint(5, 50) if symbol in participant.holdings else 0,
                "price": current_price * (1 - self.rng.uniform(0, 0.001)),
            }

        return None

    def _seed_initial_holdings(self):
        """Initialize participants with diverse portfolios for realistic sell pressure."""
        if not self.base_prices:
            return

        symbols = list(self.base_prices.keys())
        for participant in self.participants:
            if not symbols:
                continue

            allocation_pct = self.rng.uniform(0.25, 0.75)
            investable = participant.cash_balance * allocation_pct
            target_count = self.rng.randint(2, min(6, len(symbols)) + 1)
            picks = self.rng.choice(symbols, size=target_count, replace=False)

            for sym in picks:
                px = max(self.base_prices.get(sym, 0), 0.01)
                budget = investable / target_count
                qty = int(budget / px)
                if qty <= 0:
                    continue
                cost = qty * px
                if cost > participant.cash_balance:
                    continue
                participant.cash_balance -= cost
                participant.holdings[sym] = participant.holdings.get(sym, 0) + qty
                participant.entry_prices[sym] = px

    def _get_participant_activity(self, participant: AIParticipant, symbol: str) -> float:
        """Dynamic participation rate driven by regime and events."""
        base = participant.trade_frequency
        regime_boost = {
            MarketRegime.NORMAL: 1.0,
            MarketRegime.RISK_ON: 1.2,
            MarketRegime.RISK_OFF: 1.15,
            MarketRegime.PANIC: 1.45,
            MarketRegime.EUPHORIA: 1.35,
        }.get(self.market_regime, 1.0)

        if self.active_event:
            sector = self.symbol_metadata.get(symbol, {}).get("sector", "")
            if not self.active_event.affected_sectors or sector in self.active_event.affected_sectors:
                regime_boost *= 1 + (self.active_event.severity * 0.4)

        return float(np.clip(base * regime_boost, 0.02, 0.98))

    def _apply_ai_fill(self, participant: AIParticipant, symbol: str, side: str, quantity: int, price: float):
        """Apply immediate fills to participant books to keep inventories evolving."""
        quantity = max(0, int(quantity))
        if quantity == 0 or price <= 0:
            return

        if side == "BUY":
            max_affordable = int(participant.cash_balance / price)
            filled_qty = min(quantity, max_affordable)
            if filled_qty <= 0:
                return
            cost = filled_qty * price
            participant.cash_balance -= cost
            current_qty = participant.holdings.get(symbol, 0)
            avg_entry = participant.entry_prices.get(symbol, price)
            new_qty = current_qty + filled_qty
            participant.entry_prices[symbol] = ((avg_entry * current_qty) + (price * filled_qty)) / max(new_qty, 1)
            participant.holdings[symbol] = new_qty
            return

        existing_qty = participant.holdings.get(symbol, 0)
        filled_qty = min(quantity, existing_qty)
        if filled_qty <= 0:
            return
        participant.cash_balance += filled_qty * price
        remaining = existing_qty - filled_qty
        if remaining <= 0:
            participant.holdings.pop(symbol, None)
            participant.entry_prices.pop(symbol, None)
        else:
            participant.holdings[symbol] = remaining

    def _apply_behavioral_overlay(
        self,
        participant: AIParticipant,
        symbol: str,
        current_price: float,
        decision: Dict,
    ) -> Dict:
        """Inject panic/FOMO behavior and event side-bias into base trade decisions."""
        adjusted = decision.copy()
        side_bias = 0.0

        if self.market_regime == MarketRegime.PANIC:
            side_bias -= 0.6 * participant.panic_sensitivity
        elif self.market_regime == MarketRegime.RISK_OFF:
            side_bias -= 0.2 * participant.panic_sensitivity
        elif self.market_regime == MarketRegime.RISK_ON:
            side_bias += 0.2 * participant.fomo_sensitivity
        elif self.market_regime == MarketRegime.EUPHORIA:
            side_bias += 0.55 * participant.fomo_sensitivity

        if self.active_event:
            sector = self.symbol_metadata.get(symbol, {}).get("sector", "")
            if not self.active_event.affected_sectors or sector in self.active_event.affected_sectors:
                side_bias += self.active_event.side_bias * self.active_event.severity

        if side_bias <= -0.35:
            adjusted["side"] = "SELL"
            adjusted["quantity"] = int(max(1, adjusted["quantity"] * (1.2 + abs(side_bias))))
            adjusted["price"] = current_price * (1 - self.rng.uniform(0.0005, 0.008))
        elif side_bias >= 0.35:
            adjusted["side"] = "BUY"
            adjusted["quantity"] = int(max(1, adjusted["quantity"] * (1.2 + side_bias)))
            adjusted["price"] = current_price * (1 + self.rng.uniform(0.0005, 0.008))

        return adjusted

    def _momentum_decision(
        self,
        participant: AIParticipant,
        symbol: str,
        current_price: float,
        market_trend: float,
    ) -> Optional[Dict]:
        """Momentum trader: follow price trends"""
        if abs(market_trend) < 0.1:  # only trade if clear trend
            return None

        base_qty = int((participant.cash_balance / current_price) * 0.01)  # allocate 1% to position

        if market_trend > 0.2:  # Strong uptrend
            return {
                "side": "BUY",
                "quantity": base_qty,
                "price": current_price * (1 + self.rng.uniform(0.001, 0.01)),
            }
        elif market_trend < -0.2:  # Strong downtrend
            holdings = participant.holdings.get(symbol, 0)
            if holdings > 0:
                return {
                    "side": "SELL",
                    "quantity": min(base_qty, holdings),
                    "price": current_price * (1 - self.rng.uniform(0.001, 0.01)),
                }

        return None

    def _conservative_decision(
        self,
        participant: AIParticipant,
        symbol: str,
        current_price: float,
        portfolio_value: float,
    ) -> Optional[Dict]:
        """Conservative trader: rebalance portfolio periodically"""
        # Check if needs rebalancing
        in_portfolio = participant.holdings.get(symbol, 0) > 0
        target_allocation = portfolio_value * 0.05  # 5% per position max

        if not in_portfolio and participant.cash_balance > current_price * 10:
            # Add to portfolio if have cash
            desired_qty = int(target_allocation / current_price)
            if desired_qty > 0 and self.rng.random() > 0.7:  # Wait for good price
                return {
                    "side": "BUY",
                    "quantity": desired_qty,
                    "price": current_price * (1 + self.rng.uniform(0, 0.005)),
                }

        return None

    def _value_investor_decision(
        self,
        participant: AIParticipant,
        symbol: str,
        current_price: float,
    ) -> Optional[Dict]:
        """Value investor: buy if price drops below moving average"""
        if symbol not in self.base_prices:
            return None

        base_price = self.base_prices[symbol]
        discount = (base_price - current_price) / base_price

        # Buy on 5%+ drop
        if discount > 0.05 and participant.cash_balance > current_price * 20:
            return {
                "side": "BUY",
                "quantity": int(participant.cash_balance * 0.05 / current_price),
                "price": current_price,
            }

        # Sell on 10%+ gain
        holdings = participant.holdings.get(symbol, 0)
        if holdings > 0:
            entry_price = participant.entry_prices.get(symbol, current_price)
            gain = (current_price - entry_price) / entry_price
            if gain > 0.10:
                return {
                    "side": "SELL",
                    "quantity": holdings,
                    "price": current_price,
                }

        return None

    def build_order_book(
        self,
        buy_orders: List[Order],
        sell_orders: List[Order],
        symbol: str,
        current_price: float,
    ) -> OrderBookSnapshot:
        """
        Create order book snapshot from all orders
        Calculates bid/ask/spread

        Returns:
            OrderBookSnapshot with market-clearing information
        """
        # Sort orders by price
        buy_orders_sorted = sorted(buy_orders, key=lambda x: x.price, reverse=True)  # Best bid first
        sell_orders_sorted = sorted(sell_orders, key=lambda x: x.price)  # Best ask first

        # Calculate best bid/ask
        # If no orders on one side, use mid-price reference
        if not buy_orders_sorted:
            buy_orders_sorted = [
                Order(participant_id=-1, quantity=self.rng.randint(100, 400), price=current_price * 0.998, side="BUY")
            ]
        if not sell_orders_sorted:
            sell_orders_sorted = [
                Order(participant_id=-1, quantity=self.rng.randint(100, 400), price=current_price * 1.002, side="SELL")
            ]

        best_bid = buy_orders_sorted[0].price if buy_orders_sorted else current_price * 0.98
        best_ask = sell_orders_sorted[0].price if sell_orders_sorted else current_price * 1.02

        # Ensure bid < ask
        if best_bid >= best_ask:
            mid = (best_bid + best_ask) / 2
            best_bid = mid - 0.01 * current_price / 100  # 0.01% spread
            best_ask = mid + 0.01 * current_price / 100

        mid_price = (best_bid + best_ask) / 2
        bid_ask_spread = best_ask - best_bid
        spread_percentage = (bid_ask_spread / mid_price * 100) if mid_price > 0 else 0

        # Calculate volumes
        total_buy_volume = sum(o.quantity for o in buy_orders)
        total_sell_volume = sum(o.quantity for o in sell_orders)
        total_volume = total_buy_volume + total_sell_volume
        imbalance = (total_buy_volume - total_sell_volume) / total_volume if total_volume > 0 else 0

        # Estimate volatility from recent spread
        volatility = abs(spread_percentage) / 100 if spread_percentage > 0 else 0.01

        return OrderBookSnapshot(
            symbol=symbol,
            timestamp=datetime.utcnow(),
            buy_orders=buy_orders_sorted,
            sell_orders=sell_orders_sorted,
            best_bid=best_bid,
            best_ask=best_ask,
            mid_price=mid_price,
            bid_ask_spread=bid_ask_spread,
            spread_percentage=spread_percentage,
            total_buy_volume=total_buy_volume,
            total_sell_volume=total_sell_volume,
            imbalance=imbalance,
            volatility=volatility,
        )

    def calculate_execution_price(
        self,
        order_book: OrderBookSnapshot,
        player_side: str,
        player_quantity: int,
    ) -> Tuple[float, float]:
        """
        Calculate execution price for player's order against order book

        Args:
            order_book: Current order book
            player_side: BUY or SELL
            player_quantity: Number of shares player wants

        Returns:
            (execution_price, total_cost_or_proceeds, price_impact)
        """
        if player_side == "BUY":
            # Player buys, so crosses the ask side
            orders = sorted(order_book.sell_orders, key=lambda x: x.price)
            remaining = player_quantity
            total_cost = 0
            volume_used = 0

            for order in orders:
                if remaining <= 0:
                    break
                filled = min(remaining, order.quantity)
                total_cost += filled * order.price
                volume_used += filled
                remaining -= filled

            # If more to buy than available, price walks up the book
            if remaining > 0:
                # Price impact: move up by spread per unit needed
                price_impact = order_book.bid_ask_spread * (remaining / player_quantity)
                avg_execution_price = (order_book.best_ask * (volume_used / player_quantity) +
                                      (order_book.best_ask + price_impact) * (remaining / player_quantity))
            else:
                avg_execution_price = total_cost / volume_used if volume_used > 0 else order_book.mid_price

            return avg_execution_price, avg_execution_price * player_quantity

        else:  # SELL
            # Player sells, crosses bid side
            orders = sorted(order_book.buy_orders, key=lambda x: x.price, reverse=True)
            remaining = player_quantity
            total_proceeds = 0
            volume_used = 0

            for order in orders:
                if remaining <= 0:
                    break
                filled = min(remaining, order.quantity)
                total_proceeds += filled * order.price
                volume_used += filled
                remaining -= filled

            # If more to sell than available, price walks down
            if remaining > 0:
                price_impact = order_book.bid_ask_spread * (remaining / player_quantity)
                avg_execution_price = (order_book.best_bid * (volume_used / player_quantity) -
                                      (price_impact) * (remaining / player_quantity))
            else:
                avg_execution_price = total_proceeds / volume_used if volume_used > 0 else order_book.mid_price

            return avg_execution_price, avg_execution_price * player_quantity

    def apply_order_book_price_update(
        self,
        symbol: str,
        order_book: OrderBookSnapshot,
        market_trend: float = 0,
    ) -> float:
        """
        Calculate new price based on order book supply/demand imbalance

        Returns:
            New price for the symbol
        """
        # Price moves toward side with more orders (demand-supply)
        # Positive imbalance (more buyers) pushes price up
        # Negative imbalance (more sellers) pushes price down

        current_price = order_book.mid_price

        # Base movement from imbalance (up to 1% per round)
        imbalance_impact = order_book.imbalance * 0.01 * current_price

        # Trend reinforcement (momentum)
        trend_impact = market_trend * 0.005 * current_price

        # Regime/event level macro pressure
        regime_shift = {
            MarketRegime.NORMAL: 0.0,
            MarketRegime.RISK_ON: 0.0015,
            MarketRegime.RISK_OFF: -0.0015,
            MarketRegime.PANIC: -0.006,
            MarketRegime.EUPHORIA: 0.006,
        }.get(self.market_regime, 0.0)
        macro_impact = regime_shift * current_price
        if self.active_event:
            sector = self.symbol_metadata.get(symbol, {}).get("sector", "")
            if not self.active_event.affected_sectors or sector in self.active_event.affected_sectors:
                macro_impact += self.active_event.side_bias * self.active_event.severity * 0.01 * current_price

        # Random noise (market microstructure volatility)
        noise = self.rng.normal(0, current_price * 0.001 * self._volatility_multiplier(symbol))

        new_price = current_price + imbalance_impact + trend_impact + macro_impact + noise

        # Per-tick move guards similar to simplified circuit breakers
        move_cap = 0.12 if self.market_regime == MarketRegime.PANIC else 0.06
        lower = current_price * (1 - move_cap)
        upper = current_price * (1 + move_cap)
        new_price = float(np.clip(new_price, lower, upper))

        # Track price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(new_price)

        return max(new_price, current_price * 0.5)  # Prevent price crashes

    def calculate_market_trend(self, symbol: str) -> float:
        """
        Calculate market trend from price history (-1 to 1)

        Returns:
            -1 = strong downtrend, 0 = sideways, +1 = strong uptrend
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < 2:
            return 0

        prices = self.price_history[symbol][-20:]  # Last 20 updates
        if len(prices) < 2:
            return 0

        # Simple trend: compare recent prices to old
        old_avg = np.mean(prices[: len(prices) // 2])
        new_avg = np.mean(prices[len(prices) // 2 :])

        trend_magnitude = (new_avg - old_avg) / old_avg if old_avg > 0 else 0
        # Clamp to -1 to 1
        return np.clip(trend_magnitude / 0.05, -1, 1)  # 5% move = magnitude 1

    def _infer_sector(self, symbol: str) -> str:
        symbol = symbol.upper()
        sector_map = {
            "BANK": "Banking",
            "FIN": "Financials",
            "TCS": "IT",
            "INFY": "IT",
            "WIPRO": "IT",
            "TECH": "Technology",
            "NVDA": "Technology",
            "AAPL": "Technology",
            "MSFT": "Technology",
            "GOOGL": "Technology",
            "META": "Technology",
            "RELIANCE": "Energy",
            "OIL": "Energy",
            "MARUTI": "Automotive",
            "TSLA": "Automotive",
            "PHARMA": "Healthcare",
            "JNJ": "Healthcare",
            "BHARTI": "Telecom",
        }
        for token, sector in sector_map.items():
            if token in symbol:
                return sector
        return "Diversified"

    def _build_ipo_pipeline(self) -> List[Dict]:
        if self.market_type == "india":
            return [
                {"symbol": "ZESTPOWER.NS", "name": "Zest Power Infra", "sector": "Energy", "price": 342.0},
                {"symbol": "NEUROBYTE.NS", "name": "Neurobyte Systems", "sector": "IT", "price": 618.0},
                {"symbol": "URBANMOBI.NS", "name": "UrbanMobi Logistics", "sector": "Consumer", "price": 275.0},
            ]
        if self.market_type == "us":
            return [
                {"symbol": "SOLR", "name": "Solr Grid Energy", "sector": "Energy", "price": 41.0},
                {"symbol": "SYNX", "name": "Synx BioCompute", "sector": "Healthcare", "price": 52.0},
                {"symbol": "RIVT", "name": "Rivet Cloud", "sector": "Technology", "price": 67.0},
            ]
        return [
            {"symbol": "ZESTPOWER.NS", "name": "Zest Power Infra", "sector": "Energy", "price": 342.0},
            {"symbol": "NEUROBYTE.NS", "name": "Neurobyte Systems", "sector": "IT", "price": 618.0},
            {"symbol": "SOLR", "name": "Solr Grid Energy", "sector": "Energy", "price": 41.0},
            {"symbol": "RIVT", "name": "Rivet Cloud", "sector": "Technology", "price": 67.0},
        ]

    def _build_macro_calendar(self) -> List[Dict]:
        """Create a deterministic macro calendar for simulated market-time events."""
        if self.market_type == "india":
            return [
                {"tick": 8, "event_type": "cpi", "description": "India CPI print shakes rate-sensitive names", "severity": 0.45, "side_bias": -0.25, "volatility_multiplier": 1.35, "affected_sectors": ["Banking", "Financials", "Consumer"]},
                {"tick": 18, "event_type": "rbi_policy", "description": "RBI policy decision hits financials and rate cyclicals", "severity": 0.6, "side_bias": -0.35, "volatility_multiplier": 1.45, "affected_sectors": ["Banking", "Financials", "IT"]},
                {"tick": 30, "event_type": "earnings_window", "description": "Quarterly earnings window creates single-stock volatility", "severity": 0.5, "side_bias": 0.1, "volatility_multiplier": 1.25, "affected_sectors": ["IT", "Banking", "Energy", "Consumer"]},
                {"tick": 48, "event_type": "cpi", "description": "Inflation surprise resets growth expectations", "severity": 0.55, "side_bias": -0.2, "volatility_multiplier": 1.3, "affected_sectors": ["Banking", "Consumer", "Automotive"]},
            ]

        if self.market_type == "us":
            return [
                {"tick": 10, "event_type": "cpi", "description": "US CPI print moves duration-sensitive assets", "severity": 0.5, "side_bias": -0.3, "volatility_multiplier": 1.35, "affected_sectors": ["Technology", "Financials", "Consumer"]},
                {"tick": 20, "event_type": "fomc", "description": "FOMC decision triggers repricing across the tape", "severity": 0.7, "side_bias": -0.4, "volatility_multiplier": 1.55, "affected_sectors": ["Technology", "Financials", "Consumer"]},
                {"tick": 32, "event_type": "earnings_window", "description": "Earnings season creates gap risk in growth leaders", "severity": 0.55, "side_bias": 0.15, "volatility_multiplier": 1.3, "affected_sectors": ["Technology", "Healthcare", "Consumer"]},
                {"tick": 50, "event_type": "cpi", "description": "Sticky inflation reignites bond-market volatility", "severity": 0.6, "side_bias": -0.25, "volatility_multiplier": 1.4, "affected_sectors": ["Technology", "Financials", "Healthcare"]},
            ]

        return [
            {"tick": 8, "event_type": "cpi", "description": "Global inflation print drives risk-off positioning", "severity": 0.45, "side_bias": -0.25, "volatility_multiplier": 1.3, "affected_sectors": ["Technology", "Financials", "Consumer"]},
            {"tick": 16, "event_type": "rbi_policy", "description": "RBI policy commentary moves Indian financials", "severity": 0.55, "side_bias": -0.3, "volatility_multiplier": 1.4, "affected_sectors": ["Banking", "Financials"]},
            {"tick": 24, "event_type": "fomc", "description": "FOMC statement spills over into global growth names", "severity": 0.65, "side_bias": -0.35, "volatility_multiplier": 1.5, "affected_sectors": ["Technology", "Financials"]},
            {"tick": 32, "event_type": "earnings_window", "description": "Earnings window creates single-name volatility", "severity": 0.5, "side_bias": 0.1, "volatility_multiplier": 1.25, "affected_sectors": ["Technology", "Banking", "Energy", "Consumer"]},
        ]

    def _maybe_rotate_regime(self):
        if self.regime_ticks_remaining > 0:
            self.regime_ticks_remaining -= 1
            return

        if self.market_regime != MarketRegime.NORMAL and self.rng.random() < 0.55:
            self.market_regime = MarketRegime.NORMAL
            self.regime_ticks_remaining = self.rng.randint(3, 9)
            return

        if self.rng.random() < 0.09:
            regimes = [
                MarketRegime.RISK_ON,
                MarketRegime.RISK_OFF,
                MarketRegime.PANIC,
                MarketRegime.EUPHORIA,
            ]
            regime_index = int(self.rng.choice(len(regimes), p=[0.35, 0.30, 0.20, 0.15]))
            self.market_regime = regimes[regime_index]
            self.regime_ticks_remaining = int(self.rng.randint(6, 18))

    def _maybe_spawn_market_event(self):
        if self.active_event:
            if self.tick_count - self.active_event.started_at_tick >= self.active_event.duration_ticks:
                self.active_event = None
            return

        if self.rng.random() > 0.06:
            return

        templates = [
            {
                "event_type": "flash_crash",
                "description": "Large fund deleveraging triggers broad risk-off selling",
                "severity": self.rng.uniform(0.45, 0.9),
                "side_bias": -1.0,
                "volatility_multiplier": self.rng.uniform(1.5, 2.8),
                "affected_sectors": ["Technology", "Financials", "Banking"],
            },
            {
                "event_type": "short_squeeze",
                "description": "Crowded shorts unwind aggressively in growth names",
                "severity": self.rng.uniform(0.35, 0.75),
                "side_bias": 1.0,
                "volatility_multiplier": self.rng.uniform(1.4, 2.3),
                "affected_sectors": ["Technology", "Consumer"],
            },
            {
                "event_type": "policy_shock",
                "description": "Unexpected policy commentary shifts bond and equity sentiment",
                "severity": self.rng.uniform(0.25, 0.6),
                "side_bias": self.rng.choice([-1.0, 1.0]),
                "volatility_multiplier": self.rng.uniform(1.2, 2.0),
                "affected_sectors": [],
            },
        ]
        tpl = templates[int(self.rng.randint(0, len(templates)))]
        self.active_event = MarketEvent(
            event_type=tpl["event_type"],
            description=tpl["description"],
            severity=float(tpl["severity"]),
            side_bias=float(tpl["side_bias"]),
            volatility_multiplier=float(tpl["volatility_multiplier"]),
            affected_sectors=tpl["affected_sectors"],
            duration_ticks=int(self.rng.randint(4, 12)),
            started_at_tick=self.tick_count,
            origin="random",
        )
        self.recent_events.append(
            {
                "tick": self.tick_count,
                "event_type": self.active_event.event_type,
                "description": self.active_event.description,
                "severity": round(self.active_event.severity, 3),
                "origin": self.active_event.origin,
            }
        )
        self.recent_events = self.recent_events[-10:]

    def _maybe_trigger_macro_calendar_event(self):
        """Trigger scheduled macro events on predefined ticks."""
        if self.active_event:
            return

        due_event = None
        for event in self.macro_calendar:
            if event.get("tick") == self.tick_count:
                due_event = event
                break

        if not due_event:
            return

        self.active_event = MarketEvent(
            event_type=str(due_event["event_type"]),
            description=str(due_event["description"]),
            severity=float(due_event["severity"]),
            side_bias=float(due_event["side_bias"]),
            volatility_multiplier=float(due_event["volatility_multiplier"]),
            affected_sectors=list(due_event.get("affected_sectors", [])),
            duration_ticks=int(due_event.get("duration_ticks", 4)),
            started_at_tick=self.tick_count,
            origin="calendar",
        )
        self.recent_events.append(
            {
                "tick": self.tick_count,
                "event_type": self.active_event.event_type,
                "description": self.active_event.description,
                "severity": round(self.active_event.severity, 3),
                "origin": self.active_event.origin,
            }
        )
        self.recent_events = self.recent_events[-10:]
        self.macro_calendar = [event for event in self.macro_calendar if event.get("tick") != self.tick_count]

    def _maybe_launch_ipo(self):
        if not self.pending_ipos:
            return
        if self.tick_count < 5 or self.rng.random() > 0.045:
            return

        ipo = self.pending_ipos.pop(0)
        symbol = ipo["symbol"]
        issue_price = float(ipo["price"])
        listing_pop = 1 + float(self.rng.uniform(-0.05, 0.18))
        listing_price = max(issue_price * listing_pop, issue_price * 0.7)

        self.base_prices[symbol] = listing_price
        self.price_history[symbol] = [listing_price]
        self.order_book_history[symbol] = []
        self.symbol_metadata[symbol] = {"name": ipo["name"], "sector": ipo["sector"]}

        self.recent_ipos.append(
            {
                "tick": self.tick_count,
                "symbol": symbol,
                "name": ipo["name"],
                "sector": ipo["sector"],
                "issue_price": round(issue_price, 2),
                "listing_price": round(listing_price, 2),
            }
        )
        self.recent_ipos = self.recent_ipos[-8:]

    def _volatility_multiplier(self, symbol: str) -> float:
        mult = 1.0
        if self.market_regime in {MarketRegime.PANIC, MarketRegime.EUPHORIA}:
            mult *= 1.7
        elif self.market_regime in {MarketRegime.RISK_ON, MarketRegime.RISK_OFF}:
            mult *= 1.25

        if self.active_event:
            sector = self.symbol_metadata.get(symbol, {}).get("sector", "")
            if not self.active_event.affected_sectors or sector in self.active_event.affected_sectors:
                mult *= self.active_event.volatility_multiplier
        return float(np.clip(mult, 1.0, 4.0))

    def advance_market_state(self):
        """Advance one market tick and update regime/scenarios/IPO listings."""
        self.tick_count += 1
        self._maybe_rotate_regime()
        self._maybe_trigger_macro_calendar_event()
        self._maybe_spawn_market_event()
        self._maybe_launch_ipo()

    def get_market_state(self) -> Dict:
        """Expose current market state for API/UI telemetry."""
        market_regime_value = self.market_regime.value if isinstance(self.market_regime, MarketRegime) else str(self.market_regime)

        event_payload = None
        if self.active_event:
            event_payload = {
                "event_type": self.active_event.event_type,
                "description": self.active_event.description,
                "severity": round(self.active_event.severity, 3),
                "side_bias": round(self.active_event.side_bias, 3),
                "duration_ticks": self.active_event.duration_ticks,
                "ticks_elapsed": self.tick_count - self.active_event.started_at_tick,
            }

        return {
            "tick": self.tick_count,
            "market_regime": market_regime_value,
            "regime_ticks_remaining": max(0, self.regime_ticks_remaining),
            "active_event": event_payload,
            "recent_events": self.recent_events[-5:],
            "upcoming_calendar_events": self.macro_calendar[:5],
            "recent_ipos": self.recent_ipos[-5:],
            "newly_listed_symbols": [x["symbol"] for x in self.recent_ipos[-3:]],
        }
