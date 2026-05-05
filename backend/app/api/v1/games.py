"""
Games API routes - Financial Education Games
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime
from pydantic import BaseModel

from app.core.security import get_current_active_user
from app.models.database import get_db
from app.models.user import User
from app.models.finance import (
    GullakSession, GullakLifeEvent,
    SIPSession, SIPInterruption, SIPDecision,
    KarobarSession, KarobarDecision, KarobarMilestone,
    DalalSession, DalalTrade, DalalNewsEvent,
    BlackSwanSession, BlackSwanDecision,
    PaperTradingSession, PaperTrade, PaperPortfolioSnapshot, PaperTradingEvent,
    MarketParticipantProfile, MarketOrderBookSnapshot, AIParticipantTrade,
)
from app.services.simulation.gullak_simulator import (
    GullakSimulator, JarType, IncomeType, StateLocation, JarAllocation,
)
from app.services.simulation.sip_chronicles_simulator import (
    SIPChroniclesSimulator, SIPType, InterruptionType, InterruptionResponse,
)
from app.services.simulation.karobaar_simulator import (
    KarobarSimulator, Gender, City, Education, CareerPath, LifeState, DecisionPoint, DecisionOption,
)
from app.services.simulation.dalal_street_simulator import (
    DalalStreetSimulator, MarketEra, TradeType, NewsEventType, Portfolio,
)
from app.services.simulation.black_swan_simulator import (
    BlackSwanSimulator, CrisisType, PlayerProfile, CrisisPhase,
    DecisionType, FinancialProfile, generate_random_profile,
)
from app.services.simulation.paper_trading_simulator import (
    PaperTradingSimulator, MarketType, TradeSide, Holding,
)
from app.services.simulation.market_simulator import (
    AITraderEngine, ParticipantType, OrderBookSnapshot,
)
from app.services.gamification import GamificationService
from app.schemas.schemas import (
    PaperTradingCreateRequest,
    PaperTradingTradeRequest,
    GullakCreateRequest,
    SIPCreateRequest,
    KarobarCreateRequest,
    DalalCreateRequest,
    BlackSwanCreateRequest,
)

router = APIRouter()

# Session cache for AI trader engines (in-memory, per HTTP session lifetime)
# Maps session_id -> AITraderEngine instance
_market_simulator_cache: Dict[str, AITraderEngine] = {}


class GullakAllocationRequest(BaseModel):
    emergency: float
    insurance: float
    short_term: float
    long_term: float
    gold: float


class DalalTradeRequest(BaseModel):
    symbol: str
    trade_type: str
    quantity: int = 1


def _safe_json(value: Any, default: Any):
    """Normalize JSON/db values that may be dict/list or JSON-encoded strings."""
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default
    return default


def _build_paper_simulator_from_session(session: PaperTradingSession) -> PaperTradingSimulator:
    """Rehydrate simulator state from a persisted paper trading session."""
    simulator = PaperTradingSimulator(
        market=MarketType(session.market),
        initial_capital=session.initial_capital,
        strategy=session.strategy,
        start_date=session.start_date,
        end_date=session.end_date,
    )
    simulator.current_date = session.current_date

    portfolio_data = _safe_json(session.current_portfolio, {})
    simulator.portfolio.cash = float(portfolio_data.get("cash", session.current_capital or session.initial_capital))

    holdings_data = portfolio_data.get("holdings", {}) if isinstance(portfolio_data, dict) else {}
    holdings: Dict[str, Holding] = {}

    if isinstance(holdings_data, dict):
        for symbol, payload in holdings_data.items():
            if not isinstance(payload, dict):
                continue

            purchased_at_raw = payload.get("purchased_at")
            purchased_at = session.start_date
            if isinstance(purchased_at_raw, str):
                try:
                    purchased_at = datetime.fromisoformat(purchased_at_raw)
                except ValueError:
                    purchased_at = session.start_date

            stock_info = simulator.stocks.get(symbol, {})
            holdings[symbol] = Holding(
                symbol=symbol,
                quantity=int(payload.get("quantity", 0)),
                entry_price=float(payload.get("entry_price", 0)),
                current_price=float(payload.get("current_price", payload.get("entry_price", 0))),
                sector=str(payload.get("sector") or stock_info.get("sector") or "Unknown"),
                purchased_at=purchased_at,
            )

    simulator.portfolio.holdings = holdings
    return simulator


def _build_dalal_simulator_from_session(session: DalalSession) -> DalalStreetSimulator:
    """Rehydrate Dalal simulator from persisted session data."""
    portfolio_data = _safe_json(
        session.portfolio_json,
        {
            "cash": session.ending_value or session.starting_value or 100000,
            "holdings": {},
            "trades": [],
            "portfolio_value_history": [],
        },
    )
    if not isinstance(portfolio_data, dict):
        portfolio_data = {
            "cash": session.ending_value or session.starting_value or 100000,
            "holdings": {},
            "trades": [],
            "portfolio_value_history": [],
        }

    portfolio = Portfolio.from_dict(portfolio_data)
    simulator = DalalStreetSimulator(
        era=MarketEra(session.era),
        starting_portfolio=portfolio,
        inherited_capital=session.ending_value,
    )
    simulator.current_quarter = session.current_quarter or 0

    news_events = _safe_json(session.news_events_log, [])
    if isinstance(news_events, list):
        simulator.news_log = [
            n for n in news_events if isinstance(n, dict)
        ]

    quarterly_snapshots = _safe_json(session.quarterly_snapshots, [])
    if isinstance(quarterly_snapshots, list):
        simulator.quarterly_snapshots = [
            s for s in quarterly_snapshots if isinstance(s, dict)
        ]
        market_points = [100.0]
        for snapshot in simulator.quarterly_snapshots:
            market_value = snapshot.get("market_index")
            if isinstance(market_value, (int, float)):
                market_points.append(float(market_value))
        simulator.market_index_history = market_points

    return simulator


def _serialize_holdings(holdings: Dict[str, Holding]) -> Dict[str, Dict[str, Any]]:
    """Serialize in-memory holdings to JSON-safe payload for storage."""
    payload: Dict[str, Dict[str, Any]] = {}
    for symbol, holding in holdings.items():
        payload[symbol] = {
            "symbol": holding.symbol,
            "quantity": holding.quantity,
            "entry_price": holding.entry_price,
            "current_price": holding.current_price,
            "sector": holding.sector,
            "purchased_at": holding.purchased_at.isoformat() if holding.purchased_at else None,
        }
    return payload


def _sync_simulator_with_market_engine(simulator: PaperTradingSimulator, market_engine: AITraderEngine):
    """Keep paper simulator symbol universe aligned with dynamic market engine (e.g., IPOs)."""
    for symbol, price in market_engine.base_prices.items():
        if symbol in simulator.stocks:
            continue
        meta = market_engine.symbol_metadata.get(symbol, {})
        simulator.stocks[symbol] = {
            "name": meta.get("name", symbol),
            "sector": meta.get("sector", "Diversified"),
        }


def _format_trade(trade: PaperTrade) -> Dict[str, Any]:
    """Format DB trade rows for API responses."""
    return {
        "trade_id": trade.trade_id,
        "symbol": trade.symbol,
        "quantity": trade.quantity,
        "price": trade.price,
        "side": trade.side,
        "commission": trade.commission,
        "total_value": trade.total_value,
        "profit_loss": trade.profit_loss,
        "profit_loss_percentage": trade.profit_loss_percentage,
        "executed_at": trade.executed_at.isoformat() if trade.executed_at else None,
    }


def _get_or_create_market_simulator(session_id: str, session: PaperTradingSession) -> AITraderEngine:
    """Get or create AI trader engine for a paper trading session (cached)."""
    if session_id in _market_simulator_cache:
        return _market_simulator_cache[session_id]

    # Create new engine
    simulator = AITraderEngine(
        session_id=session_id,
        market_type=session.market,
        random_seed=hash(session_id) % 2**31,  # Deterministic seed from session_id
        participant_count=1000,
        hft_pct=10,
        momentum_pct=30,
        conservative_pct=40,
        value_investor_pct=20,
    )

    # Set base prices from yfinance reference
    paper_sim = _build_paper_simulator_from_session(session)
    base_prices = {}
    for symbol in paper_sim.stocks:
        price = paper_sim.get_current_price(symbol)
        if price:
            base_prices[symbol] = float(price)

    simulator.set_base_prices(base_prices)

    # Cache it
    _market_simulator_cache[session_id] = simulator
    return simulator


def _get_dynamic_quote(
    market_engine: AITraderEngine,
    symbol: str,
    previous_prices: Optional[Dict[str, float]] = None,
    advance_tick: bool = True,
) -> Dict[str, float]:
    """
    Get dynamic quote from market simulator (with bid/ask/spread)

    Returns:
        Dict with mid_price, bid, ask, bid_ask_spread, market_trend
    """
    if symbol not in market_engine.base_prices:
        return None

    # Advance simulation tick to keep market continuously moving
    if advance_tick:
        market_engine.advance_market_state()

    # Calculate market trend
    market_trend = market_engine.calculate_market_trend(symbol)

    # Generate orders from AI participants
    buy_orders, sell_orders = market_engine.generate_orders(
        symbol=symbol,
        current_price=market_engine.base_prices.get(symbol, 100),
        market_trend=market_trend,
    )

    # Build order book
    order_book = market_engine.build_order_book(
        buy_orders=buy_orders,
        sell_orders=sell_orders,
        symbol=symbol,
        current_price=market_engine.base_prices.get(symbol, 100),
    )

    # Calculate new price based on supply/demand
    new_price = market_engine.apply_order_book_price_update(
        symbol=symbol,
        order_book=order_book,
        market_trend=market_trend,
    )

    # Store order book snapshot for reference
    if symbol not in market_engine.order_book_history:
        market_engine.order_book_history[symbol] = []
    market_engine.order_book_history[symbol].append(order_book)

    market_state = market_engine.get_market_state()

    return {
        "mid_price": new_price,
        "bid": order_book.best_bid,
        "ask": order_book.best_ask,
        "bid_ask_spread": order_book.bid_ask_spread,
        "spread_percentage": order_book.spread_percentage,
        "market_trend": market_trend,
        "buy_volume": order_book.total_buy_volume,
        "sell_volume": order_book.total_sell_volume,
        "imbalance": order_book.imbalance,
        "market_state": market_state,
    }


def _resolve_paper_order_fill(
    market_engine: AITraderEngine,
    order_book,
    symbol: str,
    side: str,
    quantity: int,
    order_type: str,
    requested_price: float,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
    trailing_stop_pct: Optional[float] = None,
) -> Dict[str, Any]:
    """Resolve execution rules for market, limit, stop-loss, and trailing-stop orders."""
    side = side.upper()
    order_type = (order_type or "market").lower()
    current_price = float(order_book.mid_price)
    bid = float(order_book.best_bid)
    ask = float(order_book.best_ask)

    available_liquidity = int(order_book.total_sell_volume if side == "BUY" else order_book.total_buy_volume)
    filled_quantity = min(quantity, available_liquidity) if available_liquidity > 0 else 0
    status = "filled"
    trigger_price = current_price
    effective_price = requested_price or current_price

    def no_fill(reason: str) -> Dict[str, Any]:
        return {
            "status": "waiting",
            "filled_quantity": 0,
            "unfilled_quantity": quantity,
            "execution_price": 0.0,
            "requested_price": requested_price,
            "trigger_price": trigger_price,
            "available_liquidity": available_liquidity,
            "reason": reason,
        }

    if order_type == "limit":
        limit = limit_price or requested_price
        if side == "BUY":
            if limit < ask:
                return no_fill("buy_limit_below_ask")
            effective_price = min(limit, ask)
        else:
            if limit > bid:
                return no_fill("sell_limit_above_bid")
            effective_price = max(limit, bid)

    elif order_type == "stop_loss":
        stop = stop_price or requested_price
        if side == "SELL":
            if current_price > stop:
                return no_fill("stop_not_triggered")
            effective_price = min(current_price, bid)
            trigger_price = stop
        else:
            if current_price < stop:
                return no_fill("stop_not_triggered")
            effective_price = max(current_price, ask)
            trigger_price = stop

    elif order_type == "trailing_stop":
        if side != "SELL":
            return no_fill("trailing_stop_supported_for_sell_only")
        trail_pct = max(0.1, float(trailing_stop_pct or 5.0)) / 100.0
        price_history = market_engine.price_history.get(symbol, [])
        recent_high = max(price_history[-20:]) if price_history else current_price
        trail_stop = recent_high * (1 - trail_pct)
        if current_price > trail_stop:
            return no_fill("trailing_stop_not_triggered")
        effective_price = min(current_price, bid)
        trigger_price = trail_stop

    elif order_type != "market":
        return no_fill("unsupported_order_type")

    if filled_quantity <= 0:
        return no_fill("insufficient_liquidity")

    market_execution_price, market_execution_total = market_engine.calculate_execution_price(
        order_book=order_book,
        player_side=side,
        player_quantity=filled_quantity,
    )
    execution_price = float(market_execution_price if market_execution_price > 0 else effective_price)
    executed_total = float(execution_price * filled_quantity)

    return {
        "status": "filled" if filled_quantity == quantity else "partial_fill",
        "filled_quantity": filled_quantity,
        "unfilled_quantity": max(0, quantity - filled_quantity),
        "execution_price": execution_price,
        "executed_total": executed_total,
        "requested_price": requested_price,
        "trigger_price": trigger_price,
        "available_liquidity": available_liquidity,
        "reason": "",
    }


# ============================================================================
# GULLAK GAME ENDPOINTS
# ============================================================================

@router.post("/gullak/create")
async def create_gullak_session(
    body: GullakCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new Gullak game session"""
    try:
        session_id = str(uuid.uuid4())

        # Create simulator
        simulator = GullakSimulator(
            initial_income=40000,
            initial_expenses=30000,
            income_type=IncomeType(body.income_type),
            state_location=StateLocation(body.state_location),
            starting_age=22,
        )

        # Create database session
        db_session = GullakSession(
            user_id=current_user.id,
            session_id=session_id,
            income_type=body.income_type,
            state_location=body.state_location,
            starting_age=22,
            current_month=0,
            current_jars=json.dumps(simulator.current_jars.to_dict()),
            decisions_made=json.dumps([]),
            events_log=json.dumps([]),
            status="active",
            started_at=datetime.utcnow(),
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": "created",
            "current_month": 0,
            "current_jars": simulator.current_jars.to_dict(),
            "income_type": body.income_type,
            "state_location": body.state_location,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gullak/{session_id}")
async def get_gullak_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get Gullak game session details"""
    try:
        db_session = db.query(GullakSession).filter(
            GullakSession.session_id == session_id,
            GullakSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "current_month": db_session.current_month,
            "status": db_session.status,
            "income_type": db_session.income_type,
            "state_location": db_session.state_location,
            "current_jars": json.loads(db_session.current_jars),
            "decisions_made": json.loads(db_session.decisions_made),
            "events_log": json.loads(db_session.events_log),
            "resilience_score": db_session.resilience_score,
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
            "completed_at": db_session.completed_at.isoformat() if db_session.completed_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gullak/user/sessions")
async def get_user_gullak_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all Gullak sessions for current user"""
    try:
        sessions = db.query(GullakSession).filter(
            GullakSession.user_id == current_user.id
        ).order_by(GullakSession.created_at.desc()).all()

        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "status": s.status,
                    "income_type": s.income_type,
                    "current_month": s.current_month,
                    "resilience_score": s.resilience_score,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gullak/{session_id}/allocate")
async def allocate_gullak_month(
    session_id: str,
    body: GullakAllocationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Apply jar allocation for next month and simulate Gullak state progression."""
    try:
        db_session = db.query(GullakSession).filter(
            GullakSession.session_id == session_id,
            GullakSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        current_jars = _safe_json(db_session.current_jars, {
            "emergency": 50000,
            "insurance": 10000,
            "short_term": 10000,
            "long_term": 20000,
            "gold": 10000,
        })

        simulator = GullakSimulator(
            initial_income=40000,
            initial_expenses=30000,
            income_type=IncomeType(db_session.income_type),
            state_location=StateLocation(db_session.state_location),
            starting_age=db_session.starting_age or 22,
            initial_jars=JarAllocation.from_dict(current_jars),
        )

        next_month = (db_session.current_month or 0) + 1
        monthly_allocation = JarAllocation(
            emergency=max(0, body.emergency),
            insurance=max(0, body.insurance),
            short_term=max(0, body.short_term),
            long_term=max(0, body.long_term),
            gold=max(0, body.gold),
        )

        # Monthly allocations are contributions; add them on top of existing balances.
        simulator.current_jars = JarAllocation(
            emergency=simulator.current_jars.emergency + monthly_allocation.emergency,
            insurance=simulator.current_jars.insurance + monthly_allocation.insurance,
            short_term=simulator.current_jars.short_term + monthly_allocation.short_term,
            long_term=simulator.current_jars.long_term + monthly_allocation.long_term,
            gold=simulator.current_jars.gold + monthly_allocation.gold,
        )

        monthly_state = simulator.simulate_month(next_month, None)

        decisions = _safe_json(db_session.decisions_made, [])
        if not isinstance(decisions, list):
            decisions = []

        decision_row = {
            "month": next_month,
            "allocation": monthly_allocation.to_dict(),
            "current_jars": monthly_state.jars.to_dict(),
            "income": monthly_state.income,
            "expenses": monthly_state.expenses,
            "surplus": monthly_state.income - monthly_state.expenses,
            "jar_returns": monthly_state.jar_returns.to_dict(),
            "created_at": datetime.utcnow().isoformat(),
        }
        decisions.append(decision_row)

        events = _safe_json(db_session.events_log, [])
        if not isinstance(events, list):
            events = []

        event_payload = None
        if monthly_state.event:
            event_payload = {
                "month": monthly_state.event.month,
                "type": monthly_state.event.event_type.value,
                "description": monthly_state.event.description,
                "impact_amount": monthly_state.event.impact_amount,
                "jar_affected": monthly_state.event.jar_affected.value if monthly_state.event.jar_affected else None,
            }
            events.append(event_payload)

        db_session.current_month = next_month
        db_session.current_jars = json.dumps(monthly_state.jars.to_dict())
        db_session.decisions_made = json.dumps(decisions)
        db_session.events_log = json.dumps(events)

        total_wealth = monthly_state.jars.total()
        db_session.resilience_score = min(100.0, (total_wealth / max(1, simulator.initial_income * 24)) * 100)
        db_session.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "month": next_month,
            "income": monthly_state.income,
            "expenses": monthly_state.expenses,
            "surplus": monthly_state.income - monthly_state.expenses,
            "current_jars": monthly_state.jars.to_dict(),
            "jar_returns": monthly_state.jar_returns.to_dict(),
            "event": event_payload,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid allocation payload: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gullak/{session_id}/complete")
async def complete_gullak_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete Gullak game and return summary metrics."""
    try:
        db_session = db.query(GullakSession).filter(
            GullakSession.session_id == session_id,
            GullakSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        jars = _safe_json(db_session.current_jars, {
            "emergency": 0,
            "insurance": 0,
            "short_term": 0,
            "long_term": 0,
            "gold": 0,
        })
        total_wealth = float(sum(jars.values())) if isinstance(jars, dict) else 0.0

        db_session.status = "completed"
        db_session.completed_at = datetime.utcnow()
        db_session.resilience_score = min(100.0, (total_wealth / max(1, 40000 * 24)) * 100)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": "completed",
            "current_month": db_session.current_month,
            "final_wealth": total_wealth,
            "resilience_score": db_session.resilience_score,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gullak/{session_id}/event-options")
async def get_gullak_event_options(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current month's event with decision options (if available)."""
    try:
        db_session = db.query(GullakSession).filter(
            GullakSession.session_id == session_id,
            GullakSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        # Reconstruct simulator from session data
        current_jars = _safe_json(db_session.current_jars, {
            "emergency": 50000,
            "insurance": 10000,
            "short_term": 10000,
            "long_term": 20000,
            "gold": 10000,
        })

        simulator = GullakSimulator(
            initial_income=40000,
            initial_expenses=30000,
            income_type=IncomeType(db_session.income_type),
            state_location=StateLocation(db_session.state_location),
            starting_age=db_session.starting_age or 22,
            initial_jars=JarAllocation.from_dict(current_jars),
        )

        # Get event with options for current month
        event_data = simulator.get_event_with_options(db_session.current_month)

        if not event_data:
            return {"has_event": False, "options": []}

        return {
            "has_event": True,
            "month": event_data["month"],
            "event_type": event_data["event_type"],
            "description": event_data["description"],
            "decision_title": event_data["decision_title"],
            "options": event_data["options"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GullakDecisionRequest(BaseModel):
    option_index: int


class PaperTradingDecisionRequest(BaseModel):
    option_index: int


@router.post("/gullak/{session_id}/decide")
async def submit_gullak_decision(
    session_id: str,
    body: GullakDecisionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit a decision for the current month's event."""
    try:
        db_session = db.query(GullakSession).filter(
            GullakSession.session_id == session_id,
            GullakSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        # Reconstruct simulator
        current_jars = _safe_json(db_session.current_jars, {
            "emergency": 50000,
            "insurance": 10000,
            "short_term": 10000,
            "long_term": 20000,
            "gold": 10000,
        })

        simulator = GullakSimulator(
            initial_income=40000,
            initial_expenses=30000,
            income_type=IncomeType(db_session.income_type),
            state_location=StateLocation(db_session.state_location),
            starting_age=db_session.starting_age or 22,
            initial_jars=JarAllocation.from_dict(current_jars),
        )

        # Apply decision
        simulator.record_decision(db_session.current_month, body.option_index)

        # Update decision history in DB
        decision_history = _safe_json(db_session.decisions_made, [])
        if not isinstance(decision_history, list):
            decision_history = []

        # Find and update latest decision entry with the chosen option
        if decision_history:
            decision_history[-1]["chosen_option_idx"] = body.option_index

        db_session.decisions_made = json.dumps(decision_history)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "month": db_session.current_month,
            "option_index": body.option_index,
            "status": "decision_recorded",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SIP CHRONICLES GAME ENDPOINTS
# ============================================================================


class SIPProgressRequest(BaseModel):
    fast_forward_months: int = 1
    interruption_response: Optional[str] = None

@router.post("/sip/create")
async def create_sip_session(
    body: SIPCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new SIP Chronicles game session"""
    try:
        session_id = str(uuid.uuid4())

        # Create simulator
        simulator = SIPChroniclesSimulator(
            monthly_sip=5000,
            sip_type=SIPType(body.sip_type),
            starting_age=22,
        )

        # Create database session
        db_session = SIPSession(
            user_id=current_user.id,
            session_id=session_id,
            sip_type=body.sip_type,
            current_month=0,
            current_age=22,
            accumulated_wealth=0,
            total_contributions=0,
            contribution_history=json.dumps([]),
            interruptions_log=json.dumps([]),
            monthly_snapshots=json.dumps([]),
            final_corpus=0,
            hindsight_analysis=json.dumps({}),
            tax_savings=0,
            financial_discipline_score=0,
            status="active",
            started_at=datetime.utcnow(),
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": db_session.status,
            "sip_type": body.sip_type,
            "current_month": db_session.current_month,
            "current_age": db_session.current_age,
            "accumulated_wealth": db_session.accumulated_wealth,
            "total_contributions": db_session.total_contributions,
            "monthly_sip": db_session.monthly_sip,
            "monthly_snapshots": json.loads(db_session.monthly_snapshots) if db_session.monthly_snapshots else [],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sip/{session_id}/progress")
async def progress_sip_session(
    session_id: str,
    body: SIPProgressRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Advance SIP game by one or more months."""
    try:
        db_session = db.query(SIPSession).filter(
            SIPSession.session_id == session_id,
            SIPSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        months_to_advance = max(1, min(12, int(body.fast_forward_months or 1)))

        try:
            sip_type = SIPType(db_session.sip_type or "nifty_50")
        except ValueError:
            sip_type = SIPType.NIFTY_50

        simulator = SIPChroniclesSimulator(
            monthly_sip=float(db_session.monthly_sip or 5000),
            sip_type=sip_type,
            starting_age=22,
        )

        simulator.current_month = int(db_session.current_month or 0)
        simulator.current_age = int(db_session.current_age or 22)
        simulator.accumulated_wealth = float(db_session.accumulated_wealth or 0)
        simulator.total_contributions = float(db_session.total_contributions or 0)

        snapshots = _safe_json(db_session.monthly_snapshots, [])
        if not isinstance(snapshots, list):
            snapshots = []

        contribution_history = _safe_json(db_session.contribution_history, [])
        if not isinstance(contribution_history, list):
            contribution_history = []

        interruptions_log = _safe_json(db_session.interruptions_log, [])
        if not isinstance(interruptions_log, list):
            interruptions_log = []

        interruption_payload = None

        for step in range(months_to_advance):
            next_month = simulator.current_month + 1

            parsed_response = None
            if step == 0 and body.interruption_response:
                try:
                    parsed_response = InterruptionResponse(body.interruption_response.lower())
                except ValueError:
                    parsed_response = None

            monthly_state = simulator.simulate_month(next_month, parsed_response)

            snapshots.append(
                {
                    "month": monthly_state.month,
                    "age": monthly_state.age,
                    "wealth": monthly_state.accumulated_wealth,
                    "total_contributions": monthly_state.total_contributions,
                    "monthly_sip": monthly_state.monthly_sip,
                    "monthly_return": monthly_state.monthly_return,
                }
            )

            contribution_history.append(
                {
                    "month": monthly_state.month,
                    "amount": monthly_state.monthly_sip,
                }
            )

            if monthly_state.interruption:
                interruption_payload = {
                    "month": monthly_state.interruption.month,
                    "age": monthly_state.interruption.age,
                    "type": monthly_state.interruption.interruption_type.value,
                    "description": monthly_state.interruption.description,
                    "options": monthly_state.interruption.options,
                }

                interruption_log_entry = {
                    "month": monthly_state.interruption.month,
                    "age": monthly_state.interruption.age,
                    "type": monthly_state.interruption.interruption_type.value,
                    "description": monthly_state.interruption.description,
                    "options": monthly_state.interruption.options,
                }
                if parsed_response:
                    interruption_log_entry["response"] = parsed_response.value
                interruptions_log.append(interruption_log_entry)

        db_session.current_month = simulator.current_month
        db_session.current_age = simulator.current_age
        db_session.accumulated_wealth = max(0.0, simulator.accumulated_wealth)
        db_session.total_contributions = max(0.0, simulator.total_contributions)
        db_session.monthly_sip = simulator.monthly_sip
        db_session.monthly_snapshots = json.dumps(snapshots)
        db_session.contribution_history = json.dumps(contribution_history)
        db_session.interruptions_log = json.dumps(interruptions_log)
        db_session.updated_at = datetime.utcnow()

        if db_session.current_month >= 456:
            db_session.status = "completed"
            db_session.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": db_session.status,
            "current_month": db_session.current_month,
            "current_age": db_session.current_age,
            "accumulated_wealth": db_session.accumulated_wealth,
            "total_contributions": db_session.total_contributions,
            "monthly_sip": db_session.monthly_sip,
            "interruption": interruption_payload,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sip/{session_id}/complete")
async def complete_sip_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete SIP game and return summary metrics."""
    try:
        db_session = db.query(SIPSession).filter(
            SIPSession.session_id == session_id,
            SIPSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        interruptions_log = _safe_json(db_session.interruptions_log, [])
        if not isinstance(interruptions_log, list):
            interruptions_log = []

        total_contributions = float(db_session.total_contributions or 0)
        final_corpus = float(db_session.accumulated_wealth or 0)
        multiplier = (final_corpus / total_contributions) if total_contributions > 0 else 1.0

        interruptions_count = len(interruptions_log)
        discipline_base = max(40.0, 100.0 - interruptions_count * 2.5)
        discipline_from_multiplier = min(35.0, multiplier * 12.0)
        financial_discipline_score = min(100.0, discipline_base + discipline_from_multiplier)

        tax_savings = 0.0
        if (db_session.sip_type or "") == "elss":
            tax_savings = float(db_session.monthly_sip or 0) * 12 * 0.30

        xp_earned = int(100 + min(300, multiplier * 50) + interruptions_count * 3)

        db_session.final_corpus = final_corpus
        db_session.financial_discipline_score = financial_discipline_score
        db_session.tax_savings = tax_savings
        db_session.status = "completed"
        if not db_session.completed_at:
            db_session.completed_at = datetime.utcnow()
        db_session.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_session)

        return {
            "final_corpus": db_session.final_corpus,
            "final_age": db_session.current_age,
            "total_contributions": db_session.total_contributions,
            "total_months": db_session.current_month,
            "multiplier": multiplier,
            "financial_discipline_score": db_session.financial_discipline_score,
            "tax_savings": db_session.tax_savings,
            "interruptions_count": interruptions_count,
            "xp_earned": xp_earned,
            "interruptions_log": interruptions_log,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sip/{session_id}")
async def get_sip_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get SIP Chronicles session details"""
    try:
        db_session = db.query(SIPSession).filter(
            SIPSession.session_id == session_id,
            SIPSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "status": db_session.status,
            "sip_type": db_session.sip_type,
            "current_month": db_session.current_month,
            "current_age": db_session.current_age,
            "accumulated_wealth": db_session.accumulated_wealth,
            "total_contributions": db_session.total_contributions,
            "monthly_sip": db_session.monthly_sip,
            "monthly_snapshots": _safe_json(db_session.monthly_snapshots, []),
            "interruptions_log": _safe_json(db_session.interruptions_log, []),
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sip/user/sessions")
async def get_user_sip_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all SIP Chronicles sessions for current user"""
    try:
        sessions = db.query(SIPSession).filter(
            SIPSession.user_id == current_user.id
        ).order_by(SIPSession.created_at.desc()).all()

        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "status": s.status,
                    "sip_type": s.sip_type,
                    "current_month": s.current_month,
                    "accumulated_wealth": s.accumulated_wealth,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# KAROBAAR GAME ENDPOINTS
# ============================================================================

def _serialize_karobaar_decision(decision: Optional[DecisionPoint | Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not decision:
        return None

    if isinstance(decision, dict):
        return decision

    return {
        "id": decision.id,
        "age": decision.age,
        "decision_type": decision.decision_type,
        "description": decision.description,
        "options": [
            {
                "id": option.id,
                "text": option.text,
                "salary_impact": option.salary_impact,
                "happiness_impact": option.happiness_impact,
                "career_satisfaction_impact": option.career_satisfaction_impact,
                "wealth_impact": option.wealth_impact,
                "debt_impact": option.debt_impact,
                "side_effects": option.side_effects,
            }
            for option in decision.options
        ],
    }


def _hydrate_karobaar_simulator(db_session: KarobarSession) -> KarobarSimulator:
    simulator = KarobarSimulator(
        gender=Gender(db_session.gender),
        city=City(db_session.city),
        education=Education(db_session.education),
        starting_job=db_session.starting_job,
    )

    persisted_state = _safe_json(db_session.current_state, {})
    if isinstance(persisted_state, dict) and persisted_state:
        merged_state = simulator.state.to_dict()
        merged_state.update(persisted_state)
        merged_state.setdefault("starting_job", db_session.starting_job)
        simulator.state = LifeState(**merged_state)

    decision_history = _safe_json(db_session.decision_history, [])
    simulator.decision_history = decision_history if isinstance(decision_history, list) else []

    yearly_snapshots = _safe_json(db_session.yearly_snapshots, [])
    simulator.yearly_snapshots = yearly_snapshots if isinstance(yearly_snapshots, list) else []

    events_log = _safe_json(db_session.events_log, [])
    simulator.events_log = events_log if isinstance(events_log, list) else []

    return simulator


def _build_karobaar_response(
    db_session: KarobarSession,
    *,
    pending_decision: Optional[Dict[str, Any]] = None,
    next_decision: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    current_state = _safe_json(db_session.current_state, {})
    if not isinstance(current_state, dict):
        current_state = {}

    decision_history = _safe_json(db_session.decision_history, [])
    if not isinstance(decision_history, list):
        decision_history = []

    stored_pending = _safe_json(db_session.pending_decision, None)
    if pending_decision is None and isinstance(stored_pending, dict):
        pending_decision = stored_pending

    current_age = db_session.current_age or int(current_state.get("age", 22))
    current_year = db_session.current_year or int(current_state.get("current_year", 0))
    current_month = db_session.current_month or int(current_state.get("current_month", 0))

    return {
        "session_id": db_session.session_id,
        "status": db_session.status,
        "gender": db_session.gender,
        "city": db_session.city,
        "education": db_session.education,
        "starting_job": db_session.starting_job,
        "current_age": current_age,
        "current_year": current_year,
        "current_month": current_month,
        "current_state": current_state,
        "decision_history": decision_history,
        "pending_decision": pending_decision,
        "next_decision": next_decision,
        "milestones": [
            {
                "age": milestone.age,
                "year": milestone.year,
                "event_type": milestone.event_type,
                "description": milestone.description,
                "financial_impact": milestone.financial_impact,
                "happiness_impact": milestone.happiness_impact,
                "created_at": milestone.created_at.isoformat() if milestone.created_at else None,
            }
            for milestone in db_session.milestones
        ],
        "final_age": current_age,
        "final_scores": {
            "career": db_session.career_score,
            "financial": db_session.financial_score,
            "happiness": db_session.happiness_score,
            "overall": db_session.overall_score,
        },
        "final_net_worth": db_session.final_net_worth,
        "final_salary": db_session.final_salary,
        "decisions_made": len(decision_history),
        "xp_earned": len(decision_history) * 10,
        "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
    }


class KarobarDecisionRequest(BaseModel):
    decision_id: str
    choice_index: int

@router.post("/karobaar/create")
async def create_karobaar_session(
    body: KarobarCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new Karobaar game session"""
    try:
        session_id = str(uuid.uuid4())

        # Create simulator
        simulator = KarobarSimulator(
            gender=Gender(body.gender),
            city=City(body.city),
            education=Education(body.education),
            starting_job=body.starting_job,
        )

        # Create database session
        db_session = KarobarSession(
            user_id=current_user.id,
            session_id=session_id,
            gender=body.gender,
            city=body.city,
            education=body.education,
            starting_job=body.starting_job,
            current_age=simulator.state.age,
            current_month=simulator.state.current_month,
            current_year=0,
            current_state=json.dumps(simulator.state.to_dict() if hasattr(simulator.state, 'to_dict') else {}),
            decision_history=json.dumps([]),
            yearly_snapshots=json.dumps([]),
            events_log=json.dumps([]),
            pending_decision=None,
            status="active",
            started_at=datetime.utcnow(),
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return _build_karobaar_response(db_session)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/karobaar/{session_id}")
async def get_karobaar_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get Karobaar session details"""
    try:
        db_session = db.query(KarobarSession).filter(
            KarobarSession.session_id == session_id,
            KarobarSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        return _build_karobaar_response(db_session)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/karobaar/user/sessions")
async def get_user_karobaar_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all Karobaar sessions for current user"""
    try:
        sessions = db.query(KarobarSession).filter(
            KarobarSession.user_id == current_user.id
        ).order_by(KarobarSession.created_at.desc()).all()

        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "status": s.status,
                    "gender": s.gender,
                    "city": s.city,
                    "current_age": s.current_age,
                    "current_year": s.current_year,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/karobaar/{session_id}/business-decision")
async def get_karobaar_business_decision(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get business/career decision point during Karobaar simulation."""
    try:
        session = db.query(KarobarSession).filter(
            KarobarSession.session_id == session_id,
            KarobarSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Business decision logic based on career year
        year = session.current_year
        
        business_decisions = {
            "career_switch": {
                "title": "Career Crossroads",
                "description": f"After {year} years in your career, a major opportunity emerges. What's your move?",
                "event_type": "career_decision",
                "options": [
                    {
                        "index": 0,
                        "title": "Stay & Climb",
                        "description": "Keep your job. Pursue promotions and gradual salary growth. Stable but slower wealth building.",
                        "risk_level": "low",
                        "best_for": "Risk-averse, family-focused"
                    },
                    {
                        "index": 1,
                        "title": "Switch Companies",
                        "description": "Jump to a better-paying role. 25-40% salary bump, but learning curve.",
                        "risk_level": "medium",
                        "best_for": "Growth-focused, comfortable with change"
                    },
                    {
                        "index": 2,
                        "title": "Start Your Business",
                        "description": "Launch your own venture. High upside, but significant risk. Needs 2-3 years runway.",
                        "risk_level": "high",
                        "best_for": "Entrepreneurs with emergency fund"
                    },
                ],
            },
            "investment_strategy": {
                "title": "Investment Philosophy",
                "description": f"Your portfolio has grown to ₹{50000 * (1 + (year * 0.1)):.0f}. How aggressive should you be?",
                "event_type": "investment_decision",
                "options": [
                    {
                        "index": 0,
                        "title": "Conservative (FDs & Debt)",
                        "description": "Prioritize safety. FDs, bonds, insurance. 5-6% returns, capital protected.",
                        "risk_level": "low",
                        "best_for": "Near retirement, dependents"
                    },
                    {
                        "index": 1,
                        "title": "Balanced Portfolio",
                        "description": "50% equity, 30% debt, 20% gold. 8-10% returns with moderate volatility.",
                        "risk_level": "medium",
                        "best_for": "Most Indian investors"
                    },
                    {
                        "index": 2,
                        "title": "Aggressive Growth",
                        "description": "80% equity, 10% crypto, 10% bonds. 12-15% returns but 40% drawdown risk.",
                        "risk_level": "high",
                        "best_for": "Young, high income, long horizon"
                    },
                ],
            },
            "family_expansion": {
                "title": "Family Planning Decision",
                "description": "Your family is considering expansion. Major financial implications ahead.",
                "event_type": "family_decision",
                "options": [
                    {
                        "index": 0,
                        "title": "Now is the Time",
                        "description": "Proceed with expansion plans. Increases expenses, but builds long-term assets (education, legacy).",
                        "risk_level": "medium",
                        "best_for": "Stable income, strong savings"
                    },
                    {
                        "index": 1,
                        "title": "Wait & Build",
                        "description": "Delay by 2-3 years. Build emergency fund and investments first. Safer but emotionally harder.",
                        "risk_level": "low",
                        "best_for": "Conservative planners"
                    },
                    {
                        "index": 2,
                        "title": "Strategic Timing",
                        "description": "Plan around career peaks and market cycles. Requires discipline and flexibility.",
                        "risk_level": "medium",
                        "best_for": "Detail-oriented planners"
                    },
                ],
            },
        }

        # Determine decision based on year
        if year < 8:
            decision_key = "career_switch"
        elif year < 20:
            decision_key = "investment_strategy"
        else:
            decision_key = "family_expansion"

        decision_data = business_decisions.get(decision_key, business_decisions["career_switch"])

        return {
            "has_decision": True,
            "decision_title": decision_data["title"],
            "description": decision_data["description"],
            "event_type": decision_data["event_type"],
            "options": decision_data["options"],
            "current_year": year,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class KarobarBusinessDecisionRequest(BaseModel):
    option_index: int


@router.post("/karobaar/{session_id}/progress")
async def progress_karobaar_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Advance Karobaar by one year and optionally return a decision point."""
    try:
        session = db.query(KarobarSession).filter(
            KarobarSession.session_id == session_id,
            KarobarSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        existing_pending = _safe_json(session.pending_decision, None)
        if isinstance(existing_pending, dict):
            raise HTTPException(status_code=400, detail="Resolve the current decision before progressing")

        simulator = _hydrate_karobaar_simulator(session)
        pending_decision = simulator.advance_year()
        pending_payload = _serialize_karobaar_decision(pending_decision)

        session.current_age = simulator.state.age
        session.current_month = simulator.state.current_month
        session.current_year = simulator.state.current_year
        session.current_state = json.dumps(simulator.state.to_dict())
        session.decision_history = json.dumps(simulator.decision_history)
        session.yearly_snapshots = json.dumps(simulator.yearly_snapshots)
        session.events_log = json.dumps(simulator.events_log)
        session.pending_decision = json.dumps(pending_payload) if pending_payload else None
        session.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(session)

        return _build_karobaar_response(session, pending_decision=pending_payload)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/karobaar/{session_id}/decide")
async def decide_karobaar_session(
    session_id: str,
    body: KarobarDecisionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Apply a user decision to the current Karobaar decision point."""
    try:
        session = db.query(KarobarSession).filter(
            KarobarSession.session_id == session_id,
            KarobarSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        pending_decision = _safe_json(session.pending_decision, None)
        if not isinstance(pending_decision, dict):
            raise HTTPException(status_code=400, detail="No pending decision available")

        if pending_decision.get("id") != body.decision_id:
            raise HTTPException(status_code=400, detail="Decision id mismatch")

        options = pending_decision.get("options", [])
        if not isinstance(options, list) or body.choice_index < 0 or body.choice_index >= len(options):
            raise HTTPException(status_code=400, detail="Invalid choice index")

        simulator = _hydrate_karobaar_simulator(session)

        if not any(
            isinstance(snapshot, dict) and snapshot.get("decision_id") == body.decision_id
            for snapshot in simulator.yearly_snapshots
        ):
            simulator.yearly_snapshots.append(
                {
                    "year": simulator.state.current_year,
                    "age": simulator.state.age,
                    "salary": simulator.state.current_salary,
                    "net_worth": simulator.state.net_worth,
                    "family_status": simulator.state.marital_status,
                    "career_satisfaction": simulator.state.career_satisfaction,
                    "happiness": simulator.state.family_happiness,
                    "decision_id": body.decision_id,
                    "decision_point": pending_decision,
                }
            )

        simulator.apply_decision(body.decision_id, body.choice_index)

        session.current_age = simulator.state.age
        session.current_month = simulator.state.current_month
        session.current_year = simulator.state.current_year
        session.current_state = json.dumps(simulator.state.to_dict())
        session.decision_history = json.dumps(simulator.decision_history)
        session.yearly_snapshots = json.dumps(simulator.yearly_snapshots)
        session.events_log = json.dumps(simulator.events_log)
        session.pending_decision = None
        session.updated_at = datetime.utcnow()

        if simulator.state.age >= 65:
            final_scores = simulator.get_final_scores()
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            session.career_score = final_scores["career_score"]
            session.financial_score = final_scores["financial_score"]
            session.happiness_score = final_scores["happiness_score"]
            session.overall_score = final_scores["overall_score"]
            session.final_net_worth = final_scores["final_net_worth"]
            session.final_salary = final_scores["final_salary"]

        db.commit()
        db.refresh(session)

        return _build_karobaar_response(session)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/karobaar/{session_id}/complete")
async def complete_karobaar_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark Karobaar session as complete and persist final scores."""
    try:
        session = db.query(KarobarSession).filter(
            KarobarSession.session_id == session_id,
            KarobarSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        simulator = _hydrate_karobaar_simulator(session)
        final_scores = simulator.get_final_scores()

        session.current_age = simulator.state.age
        session.current_month = simulator.state.current_month
        session.current_year = simulator.state.current_year
        session.current_state = json.dumps(simulator.state.to_dict())
        session.decision_history = json.dumps(simulator.decision_history)
        session.yearly_snapshots = json.dumps(simulator.yearly_snapshots)
        session.events_log = json.dumps(simulator.events_log)
        session.pending_decision = None
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        session.career_score = final_scores["career_score"]
        session.financial_score = final_scores["financial_score"]
        session.happiness_score = final_scores["happiness_score"]
        session.overall_score = final_scores["overall_score"]
        session.final_net_worth = final_scores["final_net_worth"]
        session.final_salary = final_scores["final_salary"]

        db.commit()
        db.refresh(session)

        return _build_karobaar_response(session)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/karobaar/{session_id}/business-decision")
async def submit_karobaar_business_decision(
    session_id: str,
    body: KarobarBusinessDecisionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit a business/career decision."""
    try:
        session = db.query(KarobarSession).filter(
            KarobarSession.session_id == session_id,
            KarobarSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        state = _safe_json(session.current_state, {})
        if not isinstance(state, dict) or not state:
            raise HTTPException(status_code=400, detail="Session state is invalid")

        option_index = max(0, min(body.option_index, 2))
        year = session.current_year or int(state.get("current_year", 0))

        # Apply lightweight strategic impacts based on lifecycle stage.
        if year < 8:
            if option_index == 0:  # Stay & Climb
                state["current_salary"] = float(state.get("current_salary", 0)) * 1.08
                state["career_satisfaction"] = float(state.get("career_satisfaction", 60)) + 4
            elif option_index == 1:  # Switch Companies
                state["current_salary"] = float(state.get("current_salary", 0)) * 1.18
                state["career_satisfaction"] = float(state.get("career_satisfaction", 60)) + 7
                state["work_life_balance"] = float(state.get("work_life_balance", 70)) - 2
            else:  # Start Business
                state["business_status"] = "active"
                state["job_title"] = "Founder"
                state["company_size"] = "startup"
                state["current_salary"] = float(state.get("current_salary", 0)) * 0.88
                state["net_worth"] = float(state.get("net_worth", 0)) - 250000
        elif year < 20:
            if option_index == 0:  # Conservative
                state["work_life_balance"] = float(state.get("work_life_balance", 70)) + 2
                state["current_salary"] = float(state.get("current_salary", 0)) * 1.04
            elif option_index == 1:  # Balanced
                state["current_salary"] = float(state.get("current_salary", 0)) * 1.07
                state["net_worth"] = float(state.get("net_worth", 0)) * 1.03
            else:  # Aggressive
                state["current_salary"] = float(state.get("current_salary", 0)) * 1.10
                state["net_worth"] = float(state.get("net_worth", 0)) * 1.06
                state["family_happiness"] = float(state.get("family_happiness", 70)) - 3
        else:
            if option_index == 0:  # Family now
                state["family_happiness"] = float(state.get("family_happiness", 70)) + 6
                state["num_children"] = max(int(state.get("num_children", 0)), 1)
                state["net_worth"] = float(state.get("net_worth", 0)) - 150000
            elif option_index == 1:  # Wait
                state["family_happiness"] = float(state.get("family_happiness", 70)) - 2
                state["net_worth"] = float(state.get("net_worth", 0)) + 120000
            else:  # Strategic timing
                state["family_happiness"] = float(state.get("family_happiness", 70)) + 2
                state["net_worth"] = float(state.get("net_worth", 0)) + 60000

        state["current_salary"] = max(0.0, float(state.get("current_salary", 0)))
        state["net_worth"] = float(state.get("net_worth", 0))

        session.current_state = json.dumps(state)
        session.current_age = int(state.get("age", session.current_age or 22))
        session.current_month = int(state.get("current_month", session.current_month or 0))

        # Record decision in decision_history
        decisions = _safe_json(session.decision_history, [])
        if not isinstance(decisions, list):
            decisions = []

        decision_record = {
            "year": session.current_year,
            "decision_type": "business",
            "option_chosen": option_index,
            "timestamp": datetime.utcnow().isoformat(),
            "job_title": state.get("job_title"),
            "salary": state.get("current_salary"),
            "net_worth": state.get("net_worth"),
        }
        decisions.append(decision_record)

        session.decision_history = json.dumps(decisions)
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)

        return {
            "status": "recorded",
            "decision_index": option_index,
            "message": "Business decision recorded successfully",
            "current_state": state,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DALAL STREET GAME ENDPOINTS
# ============================================================================

@router.post("/dalal/create")
async def create_dalal_session(
    body: DalalCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new Dalal Street game session"""
    try:
        session_id = str(uuid.uuid4())

        # Create simulator
        simulator = DalalStreetSimulator(
            era=MarketEra(body.era),
            starting_capital=100000,
        )

        # Create database session
        db_session = DalalSession(
            user_id=current_user.id,
            session_id=session_id,
            era=body.era,
            starting_value=100000,
            ending_value=100000,
            current_quarter=0,
            portfolio_json=json.dumps(simulator.portfolio.to_dict() if hasattr(simulator.portfolio, 'to_dict') else {"stocks": {}, "cash": 100000}),
            trades_history=json.dumps([]),
            news_events_log=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": db_session.status,
            "era": body.era,
            "starting_capital": 100000,
            "current_quarter": 0,
            "portfolio_value": 100000,
            "cash": 100000,
            "holdings_value": 0,
            "market_index": 100,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dalal/{session_id}")
async def get_dalal_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get Dalal Street session details"""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "status": db_session.status,
            "era": db_session.era,
            "current_capital": db_session.ending_value,
            "current_quarter": db_session.current_quarter,
            "portfolio": json.loads(db_session.portfolio_json) if db_session.portfolio_json else {},
            "trades_made": json.loads(db_session.trades_history) if db_session.trades_history else [],
            "news_events": json.loads(db_session.news_events_log) if db_session.news_events_log else [],
            "quarterly_snapshots": db_session.quarterly_snapshots or "[]",
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dalal/{session_id}/available-stocks")
async def get_dalal_available_stocks(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get available stocks for current Dalal session."""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        simulator = _build_dalal_simulator_from_session(db_session)
        stocks = []
        for symbol, quote in simulator.stock_quotes.items():
            trend = "up" if quote.current_price >= quote.open_price else "down"
            stocks.append(
                {
                    "symbol": symbol,
                    "name": quote.name,
                    "current_price": round(quote.current_price, 2),
                    "trend": trend,
                    "sector": quote.sector,
                }
            )

        return {"session_id": session_id, "stocks": stocks}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dalal/{session_id}/trade")
async def execute_dalal_trade(
    session_id: str,
    body: DalalTradeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in Dalal Street session."""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        simulator = _build_dalal_simulator_from_session(db_session)

        try:
            trade_type = TradeType(body.trade_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid trade type")

        quantity = body.quantity if body.quantity and body.quantity > 0 else 1
        ok, message = simulator.execute_trade(body.symbol, trade_type, quantity)
        if not ok:
            raise HTTPException(status_code=400, detail=message)

        summary = simulator.get_portfolio_value_summary()
        db_session.portfolio_json = json.dumps(simulator.portfolio.to_dict())
        db_session.ending_value = summary["total_value"]
        db_session.trades_history = json.dumps([t.to_dict() for t in simulator.portfolio.trades])

        latest_trade = simulator.portfolio.trades[-1] if simulator.portfolio.trades else None
        if latest_trade:
            db_trade = DalalTrade(
                session_id=session_id,
                quarter=latest_trade.quarter,
                symbol=latest_trade.symbol,
                trade_type=latest_trade.trade_type.value,
                quantity=latest_trade.quantity,
                price_at_trade=latest_trade.price_at_trade,
                commission=latest_trade.commission,
            )
            db.add(db_trade)

        db.commit()

        return {
            "session_id": session_id,
            "message": message,
            "portfolio_value": summary["total_value"],
            "cash": summary["cash"],
            "holdings_value": summary["holdings_value"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dalal/{session_id}/advance-quarter")
async def advance_dalal_quarter(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Advance Dalal Street simulation by one quarter."""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")
        if (db_session.current_quarter or 0) >= 20:
            raise HTTPException(status_code=400, detail="Game already completed")

        simulator = _build_dalal_simulator_from_session(db_session)
        _, news_event = simulator.advance_quarter()
        summary = simulator.get_portfolio_value_summary()

        db_session.current_quarter = simulator.current_quarter
        db_session.ending_value = summary["total_value"]
        db_session.portfolio_json = json.dumps(simulator.portfolio.to_dict())
        db_session.news_events_log = json.dumps(
            [n.to_dict() if hasattr(n, "to_dict") else n for n in simulator.news_log]
        )
        db_session.quarterly_snapshots = json.dumps(simulator.quarterly_snapshots)

        if news_event:
            db_news = DalalNewsEvent(
                session_id=session_id,
                quarter=news_event.quarter,
                event_type=news_event.event_type.value,
                headline=news_event.headline,
                description=news_event.description,
                affected_symbols=json.dumps(news_event.affected_symbols),
                price_impact_percentage=news_event.price_impact,
            )
            db.add(db_news)

        db.commit()

        return {
            "session_id": session_id,
            "current_quarter": simulator.current_quarter,
            "portfolio_value": summary["total_value"],
            "cash": summary["cash"],
            "holdings_value": summary["holdings_value"],
            "market_index": simulator.market_index_history[-1] if simulator.market_index_history else 100,
            "news_event": news_event.to_dict() if news_event else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dalal/{session_id}/complete")
async def complete_dalal_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete Dalal Street session and calculate summary metrics."""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        simulator = _build_dalal_simulator_from_session(db_session)
        performance = simulator.get_portfolio_performance()

        db_session.status = "completed"
        db_session.is_completed = True
        db_session.completed_at = datetime.utcnow()
        db_session.starting_value = performance.get("starting_value", db_session.starting_value)
        db_session.ending_value = performance.get("ending_value", db_session.ending_value)
        db_session.total_profit_loss = performance.get("return_amount", 0)
        db_session.return_percentage = performance.get("return_pct", 0)
        db_session.market_comparison_return = performance.get("market_return_pct", 0)
        db_session.max_drawdown = performance.get("max_drawdown", 0)

        db.commit()

        return {
            "session_id": session_id,
            "status": db_session.status,
            "portfolio_performance": {
                "starting_value": db_session.starting_value,
                "ending_value": db_session.ending_value,
                "profit_loss": db_session.total_profit_loss,
                "return_percentage": db_session.return_percentage,
                "market_return_percentage": db_session.market_comparison_return,
                "max_drawdown": db_session.max_drawdown,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dalal/user/sessions")
async def get_user_dalal_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all Dalal Street sessions for current user"""
    try:
        sessions = db.query(DalalSession).filter(
            DalalSession.user_id == current_user.id
        ).order_by(DalalSession.created_at.desc()).all()

        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "status": s.status,
                    "era": s.era,
                    "current_capital": s.ending_value,
                    "current_quarter": s.current_quarter,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DalalDecisionRequest(BaseModel):
    option_index: int


class BlackSwanCrisisDecisionRequest(BaseModel):
    option_index: int


class BlackSwanDecisionActionRequest(BaseModel):
    decision_type: str
    asset_class: str
    amount: float


def _hydrate_black_swan_simulator(session: BlackSwanSession) -> BlackSwanSimulator:
    profile_data = _safe_json(session.financial_profile, {})
    if not isinstance(profile_data, dict):
        profile_data = {}

    profile = FinancialProfile.from_dict(profile_data)
    simulator = BlackSwanSimulator(
        crisis_type=CrisisType(session.crisis_type),
        player_profile=profile,
        random_seed=session.random_seed,
        difficulty=session.difficulty_level or "medium",
    )

    simulator.current_quarter = session.current_quarter or 0
    try:
        simulator.current_phase = CrisisPhase(session.current_phase or "pre_crisis")
    except Exception:
        simulator.current_phase = CrisisPhase.PRE_CRISIS

    wealth_history = _safe_json(session.quarterly_wealth_history, [])
    if isinstance(wealth_history, list):
        simulator.quarterly_wealth_history = wealth_history

    market_history = _safe_json(session.market_index_history, [100.0])
    if isinstance(market_history, list) and market_history:
        simulator.market_index_history = market_history

    decisions = _safe_json(session.decisions_made, [])
    if isinstance(decisions, list):
        for d in decisions:
            if not isinstance(d, dict):
                continue
            try:
                simulator.decisions_made.append(
                    __import__('app.services.simulation.black_swan_simulator', fromlist=['Decision']).Decision(
                        quarter=int(d.get("quarter", simulator.current_quarter)),
                        decision_type=DecisionType(d.get("decision_type", "hold")),
                        asset_class=d.get("asset_class", "cash"),
                        amount=float(d.get("amount", 0)),
                    )
                )
            except Exception:
                continue

    return simulator


def _phase_key(phase: str) -> str:
    if phase == "onset":
        return "onset"
    if phase == "trough":
        return "trough"
    if phase == "recovery":
        return "recovery"
    return "pre_crisis"


def _build_black_swan_response(session: BlackSwanSession) -> Dict[str, Any]:
    profile = _safe_json(session.financial_profile, {})
    if not isinstance(profile, dict):
        profile = {}

    assets = profile.get("assets", {}) if isinstance(profile.get("assets", {}), dict) else {}
    liabilities = profile.get("liabilities", {}) if isinstance(profile.get("liabilities", {}), dict) else {}

    total_assets = float(sum(float(v) for v in assets.values())) if assets else 0.0
    total_liabilities = float(sum(float(v) for v in liabilities.values())) if liabilities else 0.0
    wealth = total_assets - total_liabilities

    wealth_history = _safe_json(session.quarterly_wealth_history, [])
    if not isinstance(wealth_history, list):
        wealth_history = []

    starting_wealth = float(session.starting_wealth) if session.starting_wealth is not None else (float(wealth_history[0]) if wealth_history else wealth)
    current_phase = session.current_phase or "pre_crisis"

    crisis_labels = {
        "demonetization_2016": ("Demonetization Shock", "Currency invalidation and liquidity crunch"),
        "covid_2020": ("COVID-19 Crash", "Global pandemic, demand collapse, and sharp market drawdown"),
        "il_fs_2021": ("Credit Freeze", "NBFC stress spills into broader markets"),
        "yes_bank_2021": ("Banking Stress", "Confidence shock in financial services"),
        "crypto_2022": ("Crypto Winter", "Speculative assets unwind quickly"),
        "shadow_banking_2023": ("Shadow Banking Crisis", "Credit channels tighten rapidly"),
        "rupee_2024": ("Rupee Depreciation", "Imported inflation and FX pressure"),
    }
    crisis_name, crisis_description = crisis_labels.get(session.crisis_type, (session.crisis_type.replace('_', ' ').title(), "High-impact macro shock scenario"))

    return {
        "session_id": session.session_id,
        "status": session.status,
        "crisis_type": session.crisis_type,
        "profile_type": session.player_profile_type,
        "difficulty": session.difficulty_level,
        "current_quarter": session.current_quarter,
        "current_phase": current_phase,
        "starting_wealth": starting_wealth,
        "wealth": wealth,
        "financial_profile": profile,
        "crisis_name": crisis_name,
        "crisis_description": crisis_description,
        "phase_key": _phase_key(current_phase),
        "decisions_made": _safe_json(session.decisions_made, []),
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }


@router.get("/dalal/{session_id}/era-decision")
async def get_dalal_era_decision(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get era-specific trading decision."""
    try:
        session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        # Get decision based on current era
        era = session.era or "liberalization"
        quarter = session.current_quarter or 1

        decisions_by_era = {
            "liberalization": {
                "title": "India's IT Boom (1999-2002)",
                "description": "Technology stocks are soaring. Many predict the boom will continue indefinitely.",
                "options": [
                    {
                        "index": 0,
                        "title": "Ride the Hype Wave",
                        "description": "Allocate 60% to IT stocks like TCS, Infosys, Wipro",
                        "reasoning": "Massive gains short-term if boom continues",
                        "risk_level": "high",
                        "best_case": "₹100K → ₹500K by next era",
                        "worst_case": "₹100K → ₹40K (crash)",
                    },
                    {
                        "index": 1,
                        "title": "Balanced Tech + Value",
                        "description": "30% IT, 40% Blue-chips, 30% Defensive sectors",
                        "reasoning": "Participate in growth, buffer against crash",
                        "risk_level": "medium",
                        "best_case": "₹100K → ₹280K (steady)",
                        "worst_case": "₹100K → ₹85K (limited downside)",
                    },
                    {
                        "index": 2,
                        "title": "Avoid the Bubble",
                        "description": "Stay in banks, energy, and defensive sectors only",
                        "reasoning": "Protect capital, miss out on gains",
                        "risk_level": "low",
                        "best_case": "₹100K → ₹160K (safe)",
                        "worst_case": "₹100K → ₹95K",
                    },
                ],
            },
            "dotcom": {
                "title": "Tech Bubble Burst (2000-2002)",
                "description": "Markets are crashing. IT stocks down 80%. Panic selling everywhere.",
                "options": [
                    {
                        "index": 0,
                        "title": "Panic Sell Everything",
                        "description": "Exit all tech positions immediately",
                        "reasoning": "Avoid further losses",
                        "risk_level": "high_regret",
                        "best_case": "Preserve ₹30K",
                        "worst_case": "Sold at bottom, miss recovery",
                    },
                    {
                        "index": 1,
                        "title": "Hold & Average Down",
                        "description": "Use cash to buy more fallen IT stocks at discount",
                        "reasoning": "Buy assets cheap before recovery",
                        "risk_level": "medium",
                        "best_case": "₹30K → ₹250K next era",
                        "worst_case": "₹30K → ₹15K (deeper crash)",
                    },
                    {
                        "index": 2,
                        "title": "Shift to Sectors",
                        "description": "Rotate to banks, pharma, FMCG that remain stable",
                        "reasoning": "Cut losses, buy stability",
                        "risk_level": "low",
                        "best_case": "₹30K → ₹80K (steady)",
                        "worst_case": "₹30K → ₹28K",
                    },
                ],
            },
            "bull_run": {
                "title": "Extended Bull Run (2003-2007)",
                "description": "The economy is booming. Growth stocks running fast. New All-Time Highs daily.",
                "options": [
                    {
                        "index": 0,
                        "title": "Go Aggressive",
                        "description": "70% equities, chase momentum stocks",
                        "reasoning": "Bull runs don't last - maximize gains",
                        "risk_level": "high",
                        "best_case": "₹200K → ₹1M",
                        "worst_case": "₹200K → ₹80K (crash)",
                    },
                    {
                        "index": 1,
                        "title": "Gradual Profit Taking",
                        "description": "Book profits in winners, keep growth runners",
                        "reasoning": "Balance growth with risk management",
                        "risk_level": "medium",
                        "best_case": "₹200K → ₹650K",
                        "worst_case": "₹200K → ₹140K",
                    },
                    {
                        "index": 2,
                        "title": "Build Cash Position",
                        "description": "Increase to 40% cash, reduce equity exposure",
                        "reasoning": "Prepare for inevitable correction",
                        "risk_level": "low",
                        "best_case": "₹200K → ₹400K + safety",
                        "worst_case": "₹200K → ₹190K (opportunity cost)",
                    },
                ],
            },
            "crisis": {
                "title": "Financial Crisis (2008-2009)",
                "description": "Global credit freeze. Markets down 60%. Fear & panic everywhere.",
                "options": [
                    {
                        "index": 0,
                        "title": "Survive at Any Cost",
                        "description": "Convert to 100% cash immediately",
                        "reasoning": "Live to fight another day",
                        "risk_level": "preserve_capital",
                        "best_case": "Save ₹50K",
                        "worst_case": "Miss recovery gains",
                    },
                    {
                        "index": 1,
                        "title": "Calculated Buying",
                        "description": "Use 30% cash to buy blue-chips at 50% discount",
                        "reasoning": "Legendary returns come from buying scared",
                        "risk_level": "medium",
                        "best_case": "₹50K → ₹500K next era",
                        "worst_case": "₹50K → ₹20K (deeper fall)",
                    },
                    {
                        "index": 2,
                        "title": "Halve & Hold",
                        "description": "Cut positions in half, hold quality stocks",
                        "reasoning": "Reduce risk, maintain upside",
                        "risk_level": "medium_low",
                        "best_case": "₹50K → ₹300K",
                        "worst_case": "₹50K → ₹30K",
                    },
                ],
            },
        }

        era_decision = decisions_by_era.get(era, decisions_by_era["liberalization"])

        return {
            "has_decision": True,
            "decision_type": "era_decision",
            "era": era,
            "decision_title": era_decision["title"],
            "description": era_decision["description"],
            "options": era_decision["options"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dalal/{session_id}/era-decision")
async def submit_dalal_era_decision(
    session_id: str,
    body: DalalDecisionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit era-specific trading decision."""
    try:
        session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        # Record decision
        decisions = _safe_json(session.decisions_log, []) if session.decisions_log else []
        if not isinstance(decisions, list):
            decisions = []

        decisions.append({
            "quarter": session.current_quarter,
            "era": session.era,
            "decision_type": "era_decision",
            "chosen_option": body.option_index,
            "created_at": datetime.utcnow().isoformat(),
        })

        session.decisions_log = json.dumps(decisions)
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)

        return {
            "session_id": session_id,
            "decision_type": "era_decision",
            "chosen_option": body.option_index,
            "status": "decision_recorded",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BLACK SWAN GAME ENDPOINTS
# ============================================================================

@router.post("/black-swan/create")
async def create_black_swan_session(
    body: BlackSwanCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new Black Swan game session"""
    try:
        session_id = str(uuid.uuid4())
        random_seed = hash(session_id) % (2 ** 32)

        profile_type = PlayerProfile(body.profile_type)
        generated_profile = generate_random_profile(profile_type, random_seed)

        # Create simulator
        simulator = BlackSwanSimulator(
            crisis_type=CrisisType(body.crisis_type),
            player_profile=generated_profile,
            random_seed=random_seed,
            difficulty=body.difficulty,
        )

        # Create database session
        db_session = BlackSwanSession(
            user_id=current_user.id,
            session_id=session_id,
            crisis_type=body.crisis_type,
            player_profile_type=body.profile_type,
            difficulty_level=body.difficulty,
            random_seed=random_seed,
            current_quarter=0,
            current_phase="pre_crisis",
            financial_profile=json.dumps(simulator.player_profile.to_dict()),
            quarterly_wealth_history=json.dumps([]),
            market_index_history=json.dumps([100.0]),
            decisions_made=json.dumps([]),
            starting_wealth=simulator.player_profile.get_net_worth(),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return _build_black_swan_response(db_session)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/black-swan/{session_id}")
async def get_black_swan_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get Black Swan session details"""
    try:
        db_session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        return _build_black_swan_response(db_session)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/black-swan/user/sessions")
async def get_user_black_swan_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all Black Swan sessions for current user"""
    try:
        sessions = db.query(BlackSwanSession).filter(
            BlackSwanSession.user_id == current_user.id
        ).order_by(BlackSwanSession.created_at.desc()).all()

        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "status": s.status,
                    "crisis_type": s.crisis_type,
                    "player_profile_type": s.player_profile_type,
                    "current_quarter": s.current_quarter,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/black-swan/{session_id}/crisis-decision")
async def get_black_swan_crisis_decision(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get crisis phase decision options."""
    try:
        session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Crisis phase decision logic
        crisis_decisions = {
            "pre_crisis": {
                "title": "Pre-Crisis Opportunity",
                "description": "Markets are stable. How do you position for potential downturns?",
                "event_type": "pre_crisis",
                "options": [
                    {
                        "index": 0,
                        "title": "Build Emergency Fund",
                        "description": "Move 30% to cash, accumulate 6+ months expenses. Safe but low returns.",
                        "risk_level": "low",
                        "best_for": "Building resilience before crisis"
                    },
                    {
                        "index": 1,
                        "title": "Diversify Globally",
                        "description": "Add USD holdings, gold, international equity. Hedge rupee risk.",
                        "risk_level": "medium",
                        "best_for": "Currency and market risk hedging"
                    },
                    {
                        "index": 2,
                        "title": "Maximize Returns",
                        "description": "Stay fully invested in growth assets. Ignore warning signs.",
                        "risk_level": "high",
                        "best_for": "Bull market continuation"
                    },
                ],
            },
            "onset": {
                "title": "Crisis Hits!",
                "description": "Markets crash 20-30%. Your assets are under pressure. What now?",
                "event_type": "crisis_onset",
                "options": [
                    {
                        "index": 0,
                        "title": "Panic Sell",
                        "description": "Exit positions at market bottom. Lock in losses.",
                        "risk_level": "high",
                        "best_for": "Preserving capital (but misses recovery)"
                    },
                    {
                        "index": 1,
                        "title": "Hold & Hope",
                        "description": "Do nothing. Wait for recovery. Emotionally taxing.",
                        "risk_level": "medium",
                        "best_for": "Long-term believers"
                    },
                    {
                        "index": 2,
                        "title": "Buy the Dip",
                        "description": "Deploy cash reserves. Add quality assets at 30% discount.",
                        "risk_level": "medium",
                        "best_for": "Contrarian investors with conviction"
                    },
                ],
            },
            "recovery": {
                "title": "Recovery Begins",
                "description": "Markets bounce 15-20% off lows. Sentiment shifting. Your move?",
                "event_type": "crisis_recovery",
                "options": [
                    {
                        "index": 0,
                        "title": "Take Profits",
                        "description": "Sell winners, lock in gains, return to cash.",
                        "risk_level": "low",
                        "best_for": "Risk-averse traders"
                    },
                    {
                        "index": 1,
                        "title": "Rebalance Portfolio",
                        "description": "Adjust to maintain target allocations as markets recover.",
                        "risk_level": "low",
                        "best_for": "Disciplined long-term investors"
                    },
                    {
                        "index": 2,
                        "title": "Ride the Recovery",
                        "description": "Stay invested. Recovery often extends 12+ months.",
                        "risk_level": "high",
                        "best_for": "Growth seekers"
                    },
                ],
            },
        }

        # Determine which phase based on quarter
        quarter = session.current_quarter
        if quarter < 3:
            phase_key = "pre_crisis"
        elif quarter < 8:
            phase_key = "onset"
        else:
            phase_key = "recovery"

        decision_data = crisis_decisions.get(phase_key, crisis_decisions["onset"])

        return {
            "has_decision": True,
            "decision_title": decision_data["title"],
            "description": decision_data["description"],
            "event_type": decision_data["event_type"],
            "options": decision_data["options"],
            "current_quarter": quarter,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/black-swan/{session_id}/crisis-decision")
async def submit_black_swan_crisis_decision(
    session_id: str,
    body: BlackSwanCrisisDecisionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit a crisis phase decision."""
    try:
        session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Record decision in decisions_made
        decisions = _safe_json(session.decisions_made, [])
        decision_record = {
            "quarter": session.current_quarter,
            "phase": "crisis",
            "option_chosen": body.option_index,
            "timestamp": datetime.utcnow().isoformat(),
        }
        decisions.append(decision_record)

        session.decisions_made = json.dumps(decisions)
        profile_payload = _safe_json(session.financial_profile, {})
        if not isinstance(profile_payload, dict):
            profile_payload = {}

        assets = profile_payload.get("assets", {}) if isinstance(profile_payload.get("assets", {}), dict) else {}
        liabilities = profile_payload.get("liabilities", {}) if isinstance(profile_payload.get("liabilities", {}), dict) else {}
        wealth = float(sum(float(v) for v in assets.values())) - float(sum(float(v) for v in liabilities.values()))

        db.commit()

        return {
            "status": "recorded",
            "decision_index": body.option_index,
            "message": "Crisis decision recorded successfully",
            "wealth": wealth,
            "current_phase": session.current_phase or "pre_crisis",
            "financial_profile": profile_payload,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/black-swan/{session_id}/advance-quarter")
async def advance_black_swan_quarter(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Advance Black Swan simulation by one quarter."""
    try:
        session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        simulator = _hydrate_black_swan_simulator(session)
        result = simulator.advance_quarter()

        session.current_quarter = simulator.current_quarter
        session.current_phase = simulator.current_phase.value
        session.financial_profile = json.dumps(simulator.player_profile.to_dict())
        session.quarterly_wealth_history = json.dumps(simulator.quarterly_wealth_history)
        session.market_index_history = json.dumps(simulator.market_index_history)
        session.updated_at = datetime.utcnow()

        if session.starting_wealth is None and simulator.quarterly_wealth_history:
            session.starting_wealth = float(simulator.quarterly_wealth_history[0])

        db.commit()
        db.refresh(session)

        return {
            "session_id": session_id,
            "current_quarter": simulator.current_quarter,
            "phase": simulator.current_phase.value,
            "wealth": result.get("wealth", 0),
            "market_index": result.get("market_index", 100),
            "market_return": result.get("market_return", 0),
            "portfolio": result.get("portfolio", {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/black-swan/{session_id}/make-decision")
async def make_black_swan_decision(
    session_id: str,
    body: BlackSwanDecisionActionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute tactical Black Swan decision for current quarter."""
    try:
        session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        simulator = _hydrate_black_swan_simulator(session)

        try:
            decision_type = DecisionType(body.decision_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid decision type")

        success, message = simulator.make_decision(
            decision_type=decision_type,
            asset_class=body.asset_class,
            amount=float(body.amount),
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        session.financial_profile = json.dumps(simulator.player_profile.to_dict())
        session.decisions_made = json.dumps([
            {
                "quarter": d.quarter,
                "decision_type": d.decision_type.value,
                "asset_class": d.asset_class,
                "amount": d.amount,
            }
            for d in simulator.decisions_made
        ])
        session.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(session)

        return {
            "status": "decision_executed",
            "message": message,
            "wealth": simulator.player_profile.get_net_worth(),
            "portfolio": simulator.player_profile.assets,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/black-swan/{session_id}/complete")
async def complete_black_swan_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete Black Swan session and persist antifragility outcomes."""
    try:
        session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        simulator = _hydrate_black_swan_simulator(session)
        metrics = simulator.calculate_antifragility_score()

        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        session.current_phase = simulator.current_phase.value
        session.financial_profile = json.dumps(simulator.player_profile.to_dict())
        session.quarterly_wealth_history = json.dumps(simulator.quarterly_wealth_history)
        session.market_index_history = json.dumps(simulator.market_index_history)
        session.starting_wealth = metrics.get("starting_wealth")
        session.trough_wealth = metrics.get("trough_wealth")
        session.final_wealth = metrics.get("final_wealth")
        session.antifragility_score = metrics.get("antifragility_score")
        session.max_drawdown_pct = metrics.get("max_drawdown_pct")
        session.survival = metrics.get("survival")
        session.overall_score = metrics.get("antifragility_score")

        db.commit()
        db.refresh(session)

        return {
            "session_id": session_id,
            "status": session.status,
            "metrics": metrics,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PAPER TRADING GAME ENDPOINTS
# ============================================================================

@router.post("/paper-trading/create")
async def create_paper_trading_session(
    body: PaperTradingCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(body.start_date)
        end_dt = datetime.fromisoformat(body.end_date)

        # Create simulator
        market_type = MarketType(body.market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=body.initial_capital,
            strategy=body.strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=body.market.lower(),
            strategy=body.strategy,
            initial_capital=body.initial_capital,
            current_capital=body.initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": body.initial_capital,
                "total_value": body.initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        # Initialize market simulator and cache it (creates 1000 AI traders)
        market_engine = _get_or_create_market_simulator(session_id, db_session)

        # Store market participant profile in DB for reproducibility
        market_profile = MarketParticipantProfile(
            session_id=session_id,
            participant_count=1000,
            market_type=body.market.lower(),
            random_seed=hash(session_id) % 2**31,
            hft_percentage=10,
            momentum_percentage=30,
            conservative_percentage=40,
            value_investor_percentage=20,
            initial_capital_per_trader=100000,
            total_market_capital=1000 * 100000,
        )
        db.add(market_profile)
        db.commit()

        return {
            "session_id": session_id,
            "market": body.market,
            "strategy": body.strategy,
            "initial_capital": body.initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
            "market_participants": 1000,
            "market_simulation_enabled": True,
            "realism_features": [
                "continuous_order_book",
                "ai_behavior_regimes",
                "panic_and_euphoria_states",
                "random_market_scenarios",
                "dynamic_ipo_listings",
            ],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid dates: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}")
async def get_paper_trading_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get paper trading session details"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio = _safe_json(session.current_portfolio, {
            "holdings": {},
            "cash": session.current_capital,
            "total_value": session.current_capital,
        })

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id,
        ).order_by(PaperTrade.executed_at.desc()).all()

        sell_trades = [t for t in trades if t.side == "SELL"]
        profitable_trades = len([t for t in sell_trades if (t.profit_loss or 0) > 0])
        win_rate = (profitable_trades / len(sell_trades) * 100) if sell_trades else 0.0

        return {
            "session_id": session_id,
            "market": session.market,
            "strategy": session.strategy,
            "status": session.status,
            "current_date": session.current_date.isoformat(),
            "initial_capital": session.initial_capital,
            "current_capital": session.current_capital,
            "portfolio": portfolio,
            "metrics": {
                "total_pnl": session.total_profit_loss,
                "pnl_percentage": session.profit_loss_percentage,
                "portfolio_value": portfolio.get("total_value", session.current_capital),
                "max_drawdown": session.max_drawdown,
                "sharpe_ratio": session.sharpe_ratio,
                "win_rate": win_rate,
                "total_trades": len(trades),
                "profitable_trades": profitable_trades,
            },
            "trades": [_format_trade(t) for t in trades],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/quote")
async def get_paper_trading_quote(
    session_id: str,
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current quote for a symbol with dynamic AI market pricing."""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        normalized_symbol = symbol.strip().upper()
        simulator = _build_paper_simulator_from_session(session)

        _sync_simulator_with_market_engine(simulator, _get_or_create_market_simulator(session_id, session))

        if normalized_symbol not in simulator.stocks:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported symbol for this market: {normalized_symbol}",
            )

        # Get dynamic quote from AI market participants
        market_engine = _get_or_create_market_simulator(session_id, session)
        quote_data = _get_dynamic_quote(market_engine, normalized_symbol)

        if quote_data is None:
            raise HTTPException(status_code=404, detail=f"Price not available for {normalized_symbol}")

        return {
            "symbol": normalized_symbol,
            "price": round(float(quote_data["mid_price"]), 2),
            "bid": round(float(quote_data["bid"]), 2),
            "ask": round(float(quote_data["ask"]), 2),
            "bid_ask_spread": round(float(quote_data["bid_ask_spread"]), 4),
            "spread_percentage": round(float(quote_data["spread_percentage"]), 3),
            "market_trend": round(float(quote_data["market_trend"]), 2),
            "buy_volume": quote_data["buy_volume"],
            "sell_volume": quote_data["sell_volume"],
            "imbalance": round(float(quote_data["imbalance"]), 3),
            "market": session.market,
            "currency": "INR" if normalized_symbol.endswith(".NS") else "USD",
            "fetched_at": datetime.utcnow().isoformat(),
            "note": "Prices generated by simulated market with 1000 AI traders",
            "market_state": quote_data.get("market_state"),
            "available_symbols": sorted(list(market_engine.base_prices.keys())),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/market-state")
async def get_paper_trading_market_state(
    session_id: str,
    limit: int = 12,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get live market state snapshot (regime, events, IPOs, and top-of-book quotes)."""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        simulator = _build_paper_simulator_from_session(session)
        market_engine = _get_or_create_market_simulator(session_id, session)
        _sync_simulator_with_market_engine(simulator, market_engine)

        symbols = sorted(list(simulator.stocks.keys()))[: max(1, min(50, limit))]
        market_engine.advance_market_state()
        quotes = []
        for symbol in symbols:
            quote_data = _get_dynamic_quote(market_engine, symbol, advance_tick=False)
            if not quote_data:
                continue
            quotes.append(
                {
                    "symbol": symbol,
                    "price": round(float(quote_data["mid_price"]), 2),
                    "bid": round(float(quote_data["bid"]), 2),
                    "ask": round(float(quote_data["ask"]), 2),
                    "spread": round(float(quote_data["bid_ask_spread"]), 4),
                    "trend": round(float(quote_data["market_trend"]), 3),
                    "buy_volume": int(quote_data["buy_volume"]),
                    "sell_volume": int(quote_data["sell_volume"]),
                    "imbalance": round(float(quote_data["imbalance"]), 3),
                }
            )

        return {
            "session_id": session_id,
            "market": session.market,
            "tick": market_engine.tick_count,
            "market_state": market_engine.get_market_state(),
            "quotes": quotes,
            "total_symbols": len(simulator.stocks),
            "generated_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    body: PaperTradingTradeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a BUY/SELL trade against order book with market-based pricing."""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        simulator = _build_paper_simulator_from_session(session)
        market_engine = _get_or_create_market_simulator(session_id, session)
        _sync_simulator_with_market_engine(simulator, market_engine)

        normalized_symbol = body.symbol.strip().upper()
        if normalized_symbol not in simulator.stocks:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported symbol for this market: {normalized_symbol}",
            )

        # Get market order book to calculate realistic execution price
        quote_data = _get_dynamic_quote(market_engine, normalized_symbol)
        if quote_data is None:
            raise HTTPException(status_code=404, detail=f"Price not available for {normalized_symbol}")

        # Build order book for execution calculation
        market_trend = market_engine.calculate_market_trend(normalized_symbol)
        buy_orders, sell_orders = market_engine.generate_orders(
            symbol=normalized_symbol,
            current_price=quote_data["mid_price"],
            market_trend=market_trend,
        )
        order_book = market_engine.build_order_book(
            buy_orders=buy_orders,
            sell_orders=sell_orders,
            symbol=normalized_symbol,
            current_price=quote_data["mid_price"],
        )

        # Calculate execution price from market order book
        side = TradeSide(body.side.upper())
        fill_info = _resolve_paper_order_fill(
            market_engine=market_engine,
            order_book=order_book,
            symbol=normalized_symbol,
            side=body.side,
            quantity=body.quantity,
            order_type=body.order_type,
            requested_price=body.price,
            limit_price=body.limit_price,
            stop_price=body.stop_price,
            trailing_stop_pct=body.trailing_stop_pct,
        )

        if fill_info["status"] == "waiting":
            return {
                "status": "pending",
                "trade": None,
                "fill": fill_info,
                "market_state": quote_data.get("market_state"),
                "message": "Order submitted but not triggered or not crossable yet",
            }

        actual_price = float(fill_info["execution_price"] if fill_info["execution_price"] > 0 else body.price)
        filled_quantity = int(fill_info["filled_quantity"])

        # Execute trade at market price
        result = simulator.execute_trade(
            symbol=normalized_symbol,
            quantity=filled_quantity,
            price=actual_price,
            side=side,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Trade failed"))

        holdings_payload = _serialize_holdings(simulator.portfolio.holdings)
        total_value = simulator.portfolio.get_total_value()

        session.current_capital = simulator.portfolio.cash
        session.current_portfolio = json.dumps({
            "holdings": holdings_payload,
            "cash": simulator.portfolio.cash,
            "total_value": total_value,
        })
        session.all_holdings = json.dumps(list(holdings_payload.values()))
        session.total_profit_loss = simulator.portfolio.get_total_pnl()
        session.profit_loss_percentage = simulator.portfolio.get_total_pnl_percentage()
        session.updated_at = datetime.utcnow()

        db_trade = PaperTrade(
            session_id_fk=session.id,
            trade_id=result["trade_id"],
            symbol=result["symbol"],
            quantity=result["quantity"],
            price=actual_price,
            side=side.value,
            executed_at=simulator.current_date,
            commission=result.get("commission", 0.0),
            total_value=result.get("total_value", filled_quantity * actual_price),
            entry_price=holdings_payload.get(result["symbol"], {}).get("entry_price"),
            profit_loss=result.get("pnl"),
            profit_loss_percentage=result.get("pnl_percentage"),
        )

        snapshot_holdings = [
            {
                "symbol": h["symbol"],
                "quantity": h["quantity"],
                "entry_price": h["entry_price"],
                "current_price": h["current_price"],
            }
            for h in holdings_payload.values()
        ]
        db_snapshot = PaperPortfolioSnapshot(
            session_id_fk=session.id,
            snapshot_date=datetime.utcnow(),
            holdings=snapshot_holdings,
            cash=simulator.portfolio.cash,
            total_value=total_value,
            daily_pnl=session.total_profit_loss,
            daily_pnl_percentage=session.profit_loss_percentage,
        )

        db.add(db_trade)
        db.add(db_snapshot)
        db.commit()
        db.refresh(session)

        return {
            "status": "success",
            "trade": _format_trade(db_trade),
            "fill": {
                **fill_info,
                "requested_quantity": body.quantity,
            },
            "portfolio": json.loads(session.current_portfolio) if isinstance(session.current_portfolio, str) else session.current_portfolio,
            "metrics": {
                "total_pnl": session.total_profit_loss,
                "pnl_percentage": session.profit_loss_percentage,
                "portfolio_value": total_value,
            },
            "execution_price": round(actual_price, 2),
            "price_source": "market_order_book",
            "market_state": quote_data.get("market_state"),
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid trade side. Use BUY or SELL")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/user/sessions")
async def get_user_paper_trading_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all paper trading sessions for current user"""
    try:
        sessions = db.query(PaperTradingSession).filter(
            PaperTradingSession.user_id == current_user.id
        ).order_by(PaperTradingSession.created_at.desc()).all()

        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "market": s.market,
                    "strategy": s.strategy,
                    "status": s.status,
                    "initial_capital": s.initial_capital,
                    "final_wealth": s.final_wealth,
                    "total_score": s.total_score,
                    "total_pnl": s.total_profit_loss,
                    "pnl_percentage": s.profit_loss_percentage,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/complete")
async def complete_paper_trading_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete paper trading session and calculate final scores"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator to calculate scores
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Calculate scores
        scores = simulator.calculate_scores(session.initial_capital)
        metrics = simulator.calculate_metrics()

        # Update session
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.final_wealth = portfolio_data.get("total_value", session.current_capital)
        session.total_profit_loss = metrics.get("total_pnl", 0)
        session.profit_loss_percentage = metrics.get("pnl_percentage", 0)
        session.portfolio_score = scores.get("portfolio_score", 0)
        session.diversification_score = scores.get("diversification_score", 0)
        session.risk_adjusted_score = scores.get("risk_adjusted_score", 0)
        session.timing_score = scores.get("timing_score", 0)
        session.adherence_score = scores.get("adherence_score", 0)
        session.total_score = scores.get("total_score", 0)
        session.max_drawdown = metrics.get("max_drawdown", 0)
        session.win_rate = metrics.get("win_rate", 0)

        db.commit()
        db.refresh(session)

        return {
            "session_id": session_id,
            "status": "completed",
            "final_wealth": session.final_wealth,
            "total_pnl": session.total_profit_loss,
            "pnl_percentage": session.profit_loss_percentage,
            "scores": {
                "portfolio_score": session.portfolio_score,
                "diversification_score": session.diversification_score,
                "risk_adjusted_score": session.risk_adjusted_score,
                "timing_score": session.timing_score,
                "adherence_score": session.adherence_score,
                "total_score": session.total_score,
            },
            "metrics": {
                "max_drawdown": session.max_drawdown,
                "win_rate": session.win_rate,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/portfolio-decision")
async def get_paper_trading_portfolio_decision(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get portfolio setup decision (shown at game start)."""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        # Portfolio setup decision options
        options = [
            {
                "index": 0,
                "title": "Aggressive Growth Portfolio",
                "description": "80% stocks (growth), 15% mid-cap, 5% cash",
                "risk_level": "high",
                "sector_weights": {"IT": 0.35, "Finance": 0.25, "Healthcare": 0.15, "Energy": 0.15, "Retail": 0.1},
                "expected_return": "12-15% annually",
                "volatility": "25-30%",
                "best_for": "Young investors with long time horizon",
            },
            {
                "index": 1,
                "title": "Balanced Portfolio",
                "description": "60% large-cap, 20% mid-cap, 15% small-cap, 5% cash",
                "risk_level": "medium",
                "sector_weights": {"IT": 0.2, "Finance": 0.25, "Healthcare": 0.2, "Energy": 0.15, "Retail": 0.1, "Telecom": 0.1},
                "expected_return": "10-12% annually",
                "volatility": "15-18%",
                "best_for": "Balanced risk-return seekers",
            },
            {
                "index": 2,
                "title": "Conservative Portfolio",
                "description": "40% blue-chip, 30% dividend stocks, 20% bonds proxy, 10% cash",
                "risk_level": "low",
                "sector_weights": {"Finance": 0.3, "Healthcare": 0.2, "Utility": 0.15, "FMCG": 0.15, "IT": 0.1, "Telecom": 0.1},
                "expected_return": "7-9% annually",
                "volatility": "8-10%",
                "best_for": "Risk-averse investors, near retirement",
            },
        ]

        return {
            "has_decision": True,
            "decision_type": "portfolio_setup",
            "decision_title": "Choose Your Portfolio Strategy",
            "description": "This decision shapes your trading approach. Choose wisely—it affects diversification and volatility.",
            "options": options,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/portfolio-decision")
async def submit_paper_trading_portfolio_decision(
    session_id: str,
    body: PaperTradingDecisionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit portfolio setup decision."""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        portfolio_strategies = [
            {"name": "Aggressive Growth", "risk": "high"},
            {"name": "Balanced", "risk": "medium"},
            {"name": "Conservative", "risk": "low"},
        ]

        chosen_strategy = portfolio_strategies[min(body.option_index, 2)]

        events_payload = {
            "decision_type": "portfolio_setup",
            "chosen_option": body.option_index,
            "chosen_strategy": chosen_strategy["name"],
            "risk_profile": chosen_strategy["risk"],
            "created_at": datetime.utcnow().isoformat(),
        }

        event = PaperTradingEvent(
            session_id_fk=session.id,
            event_date=datetime.utcnow(),
            event_type="portfolio_decision",
            description=f"Portfolio strategy selected: {chosen_strategy['name']}",
            impact=events_payload,
        )
        db.add(event)

        # Store the chosen strategy in all_holdings metadata for quick retrieval on load.
        all_holdings_payload = _safe_json(session.all_holdings, [])
        if not isinstance(all_holdings_payload, list):
            all_holdings_payload = []
        all_holdings_payload.append({"meta": events_payload})
        session.all_holdings = json.dumps(all_holdings_payload)
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)

        return {
            "session_id": session_id,
            "decision_type": "portfolio_setup",
            "chosen_option": body.option_index,
            "status": "decision_recorded",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/diversification-alert")
async def get_paper_trading_diversification_alert(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Check if portfolio needs diversification (sector concentration >40%)."""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio = _safe_json(session.current_portfolio, {"holdings": {}, "cash": session.current_capital})
        holdings = portfolio.get("holdings", {})

        if not holdings:
            return {"alert_triggered": False}

        # Calculate sector weights
        sector_weights = {}
        total_value = session.current_capital
        for symbol, holding_data in holdings.items():
            sector = holding_data.get("sector", "Unknown")
            value = holding_data.get("value", 0)
            sector_weights[sector] = sector_weights.get(sector, 0) + value
            total_value += value

        # Check if any sector exceeds 40%
        max_sector = max(sector_weights.values()) if sector_weights else 0
        max_sector_pct = (max_sector / total_value * 100) if total_value > 0 else 0
        max_sector_name = max(sector_weights, key=sector_weights.get) if sector_weights else "Unknown"

        if max_sector_pct > 40:
            options = [
                {
                    "index": 0,
                    "title": "Sell & Diversify",
                    "description": f"Reduce {max_sector_name} exposure by selling 30% of holdings",
                    "action": "sell_and_diversify",
                    "expected_impact": "Reduces portfolio volatility, may miss upside",
                },
                {
                    "index": 1,
                    "title": "Gradually Shift",
                    "description": "Start accumulating stocks in underweighted sectors",
                    "action": "gradual_shift",
                    "expected_impact": "Balanced approach, slower transition",
                },
                {
                    "index": 2,
                    "title": "Ignore & Stay Invested",
                    "description": "Maintain current allocation and keep holding",
                    "action": "stay_invested",
                    "expected_impact": "Amplifies gains/losses, high concentration risk",
                },
            ]

            return {
                "alert_triggered": True,
                "decision_type": "diversification_alert",
                "decision_title": "Portfolio Concentration Warning",
                "description": f"Your portfolio is {max_sector_pct:.1f}% concentrated in {max_sector_name}. This exceeds our 40% recommendation.",
                "current_concentration": max_sector_pct,
                "concentrated_sector": max_sector_name,
                "options": options,
            }
        else:
            return {"alert_triggered": False}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


