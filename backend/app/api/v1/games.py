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
    PaperTradingSession, PaperTrade, PaperPortfolioSnapshot, PaperTradingEvent
)
from app.services.simulation.gullak_simulator import (
    GullakSimulator, JarType, IncomeType, StateLocation, JarAllocation,
)
from app.services.simulation.sip_chronicles_simulator import (
    SIPChroniclesSimulator, SIPType, InterruptionType, InterruptionResponse,
)
from app.services.simulation.karobaar_simulator import (
    KarobarSimulator, Gender, City, Education, CareerPath, LifeState,
)
from app.services.simulation.dalal_street_simulator import (
    DalalStreetSimulator, MarketEra, TradeType, NewsEventType, Portfolio,
)
from app.services.simulation.black_swan_simulator import (
    BlackSwanSimulator, CrisisType, PlayerProfile, CrisisPhase,
    DecisionType, generate_random_profile,
)
from app.services.simulation.paper_trading_simulator import (
    PaperTradingSimulator, MarketType, TradeSide, Holding,
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


class GullakAllocationRequest(BaseModel):
    emergency: float
    insurance: float
    short_term: float
    long_term: float
    gold: float


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


# ============================================================================
# SIP CHRONICLES GAME ENDPOINTS
# ============================================================================

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
            starting_capital=50000,
            monthly_investment=5000,
            current_month=0,
            current_value=50000,
            portfolio_data=json.dumps(simulator.portfolio.to_dict() if hasattr(simulator, 'portfolio') else {}),
            interruptions_faced=json.dumps([]),
            decisions_made=json.dumps([]),
            status="active",
            started_at=datetime.utcnow(),
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": "created",
            "sip_type": body.sip_type,
            "starting_capital": 50000,
            "monthly_investment": 5000,
            "current_month": 0,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
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
            "current_value": db_session.current_value,
            "portfolio_data": json.loads(db_session.portfolio_data) if db_session.portfolio_data else {},
            "interruptions_faced": json.loads(db_session.interruptions_faced) if db_session.interruptions_faced else [],
            "decisions_made": json.loads(db_session.decisions_made) if db_session.decisions_made else [],
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
                    "current_value": s.current_value,
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
            starting_job_type=body.starting_job,
        )

        # Create database session
        db_session = KarobarSession(
            user_id=current_user.id,
            session_id=session_id,
            gender=body.gender,
            city=body.city,
            education=body.education,
            starting_job=body.starting_job,
            current_year=0,
            current_life_state=json.dumps(simulator.life_state.to_dict() if hasattr(simulator.life_state, 'to_dict') else {}),
            decisions_made=json.dumps([]),
            milestones=json.dumps([]),
            status="active",
            started_at=datetime.utcnow(),
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": "created",
            "gender": body.gender,
            "city": body.city,
            "education": body.education,
            "starting_job": body.starting_job,
            "current_year": 0,
        }

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

        return {
            "session_id": session_id,
            "status": db_session.status,
            "gender": db_session.gender,
            "city": db_session.city,
            "education": db_session.education,
            "current_year": db_session.current_year,
            "current_life_state": json.loads(db_session.current_life_state) if db_session.current_life_state else {},
            "decisions_made": json.loads(db_session.decisions_made) if db_session.decisions_made else [],
            "milestones": json.loads(db_session.milestones) if db_session.milestones else [],
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
        }

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
                    "current_year": s.current_year,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ]
        }

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
            starting_capital=100000,
            current_capital=100000,
            current_quarter=0,
            portfolio=json.dumps(simulator.portfolio.to_dict() if hasattr(simulator.portfolio, 'to_dict') else {"stocks": {}, "cash": 100000}),
            trades_made=json.dumps([]),
            news_events=json.dumps([]),
            status="active",
            started_at=datetime.utcnow(),
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": "created",
            "era": body.era,
            "starting_capital": 100000,
            "current_quarter": 0,
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
            "current_capital": db_session.current_capital,
            "current_quarter": db_session.current_quarter,
            "portfolio": json.loads(db_session.portfolio) if db_session.portfolio else {},
            "trades_made": json.loads(db_session.trades_made) if db_session.trades_made else [],
            "news_events": json.loads(db_session.news_events) if db_session.news_events else [],
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
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
                    "current_capital": s.current_capital,
                    "current_quarter": s.current_quarter,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ]
        }

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

        # Create simulator
        simulator = BlackSwanSimulator(
            crisis_type=CrisisType(body.crisis_type),
            player_profile=PlayerProfile(body.profile_type),
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
            financial_profile=json.dumps(simulator.profile.to_dict() if hasattr(simulator.profile, 'to_dict') else {}),
            decisions_made=json.dumps([]),
            status="active",
            started_at=datetime.utcnow(),
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": "created",
            "crisis_type": body.crisis_type,
            "profile_type": body.profile_type,
            "difficulty": body.difficulty,
            "current_quarter": 0,
        }

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

        return {
            "session_id": session_id,
            "status": db_session.status,
            "crisis_type": db_session.crisis_type,
            "player_profile_type": db_session.player_profile_type,
            "difficulty_level": db_session.difficulty_level,
            "current_quarter": db_session.current_quarter,
            "financial_profile": json.loads(db_session.financial_profile) if db_session.financial_profile else {},
            "decisions_made": json.loads(db_session.decisions_made) if db_session.decisions_made else [],
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
        }

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

        return {
            "session_id": session_id,
            "market": body.market,
            "strategy": body.strategy,
            "initial_capital": body.initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
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
    """Get current quote for a symbol in the context of a paper trading session."""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        normalized_symbol = symbol.strip().upper()
        simulator = _build_paper_simulator_from_session(session)

        if normalized_symbol not in simulator.stocks:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported symbol for this market: {normalized_symbol}",
            )

        price = simulator.get_current_price(normalized_symbol)
        if price is None:
            raise HTTPException(status_code=404, detail=f"Price not available for {normalized_symbol}")

        return {
            "symbol": normalized_symbol,
            "price": round(float(price), 2),
            "market": session.market,
            "currency": "INR" if normalized_symbol.endswith(".NS") else "USD",
            "fetched_at": datetime.utcnow().isoformat(),
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
    """Execute a BUY/SELL trade and persist portfolio/trade history."""
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

        normalized_symbol = body.symbol.strip().upper()
        if normalized_symbol not in simulator.stocks:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported symbol for this market: {normalized_symbol}",
            )

        side = TradeSide(body.side.upper())
        result = simulator.execute_trade(
            symbol=normalized_symbol,
            quantity=body.quantity,
            price=body.price,
            side=side,
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Trade failed"))

        holdings_payload = _serialize_holdings(simulator.portfolio.holdings)
        total_value = simulator.portfolio.get_total_value()

        session.current_capital = simulator.portfolio.cash
        session.current_portfolio = {
            "holdings": holdings_payload,
            "cash": simulator.portfolio.cash,
            "total_value": total_value,
        }
        session.all_holdings = list(holdings_payload.values())
        session.total_profit_loss = simulator.portfolio.get_total_pnl()
        session.profit_loss_percentage = simulator.portfolio.get_total_pnl_percentage()
        session.updated_at = datetime.utcnow()

        db_trade = PaperTrade(
            session_id_fk=session.id,
            trade_id=result["trade_id"],
            symbol=result["symbol"],
            quantity=result["quantity"],
            price=result["price"],
            side=side.value,
            executed_at=simulator.current_date,
            commission=result.get("commission", 0.0),
            total_value=result.get("total_value", body.quantity * body.price),
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
            "portfolio": session.current_portfolio,
            "metrics": {
                "total_pnl": session.total_profit_loss,
                "pnl_percentage": session.profit_loss_percentage,
                "portfolio_value": total_value,
            },
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


