"""
Gullak Game API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
import uuid
from datetime import datetime

from app.core.security import get_current_active_user
from app.models.database import get_db
from app.models.user import User
from app.models.finance import GullakSession, GullakLifeEvent, SIPSession, SIPInterruption, SIPDecision, KarobarSession, KarobarDecision, KarobarMilestone, DalalSession, DalalTrade, DalalNewsEvent, BlackSwanSession, BlackSwanDecision, PaperTradingSession, PaperTrade, PaperPortfolioSnapshot, PaperTradingEvent
from app.services.simulation.gullak_simulator import (
    GullakSimulator,
    JarType,
    IncomeType,
    StateLocation,
    JarAllocation,
)
from app.services.simulation.sip_chronicles_simulator import (
    SIPChroniclesSimulator,
    SIPType,
    InterruptionType,
    InterruptionResponse,
)
from app.services.simulation.karobaar_simulator import (
    KarobarSimulator,
    Gender,
    City,
    Education,
    CareerPath,
    LifeState,
)
from app.services.simulation.dalal_street_simulator import (
    DalalStreetSimulator,
    MarketEra,
    TradeType,
    NewsEventType,
    Portfolio,
)
from app.services.simulation.black_swan_simulator import (
    BlackSwanSimulator,
    CrisisType,
    PlayerProfile,
    CrisisPhase,
    DecisionType,
    generate_random_profile,
)
from app.services.simulation.paper_trading_simulator import (
    PaperTradingSimulator,
    MarketType,
    TradeSide,
)
from app.services.gamification import GamificationService

router = APIRouter()


@router.post("/gullak/create")
async def create_gullak_session(
    income_type: str = "salaried",
    state_location: str = "other",
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
            income_type=IncomeType(income_type),
            state_location=StateLocation(state_location),
            starting_age=22,
        )

        # Create database session
        db_session = GullakSession(
            user_id=current_user.id,
            session_id=session_id,
            income_type=income_type,
            state_location=state_location,
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
            "income_type": income_type,
            "state_location": state_location,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PAPER TRADING GAME ENDPOINTS
# ============================================================================

@router.post("/paper-trading/create")
async def create_paper_trading_session(
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gullak/{session_id}/allocate")
async def allocate_monthly_jars(
    session_id: str,
    emergency: float,
    insurance: float,
    short_term: float,
    long_term: float,
    gold: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Submit monthly jar allocation"""
    try:
        # Get session
        db_session = db.query(GullakSession).filter(
            GullakSession.session_id == session_id,
            GullakSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        # Recreate simulator state
        current_jars_dict = json.loads(db_session.current_jars)
        simulator = GullakSimulator(
            initial_income=40000,
            initial_expenses=30000,
            income_type=IncomeType(db_session.income_type),
            state_location=StateLocation(db_session.state_location),
            starting_age=db_session.starting_age,
            initial_jars=JarAllocation.from_dict(current_jars_dict),
        )

        # Restore history
        simulator.current_month = db_session.current_month

        # New allocation
        new_allocation = JarAllocation(
            emergency=emergency,
            insurance=insurance,
            short_term=short_term,
            long_term=long_term,
            gold=gold,
        )

        # Simulate next month
        month_state = simulator.simulate_month(db_session.current_month + 1, new_allocation)

        # Save decision
        decisions = json.loads(db_session.decisions_made)
        decisions.append({
            "month": db_session.current_month + 1,
            "allocation": new_allocation.to_dict(),
        })

        # Update session
        db_session.current_month = simulator.current_month
        db_session.current_jars = json.dumps(simulator.current_jars.to_dict())
        db_session.decisions_made = json.dumps(decisions)

        # Update events log if event occurred
        if month_state.event:
            events = json.loads(db_session.events_log)
            events.append({
                "month": month_state.event.month,
                "type": month_state.event.event_type.value,
                "amount": month_state.event.impact_amount,
                "description": month_state.event.description,
            })
            db_session.events_log = json.dumps(events)

            # Save to database
            db_event = GullakLifeEvent(
                session_id=session_id,
                month=month_state.event.month,
                event_type=month_state.event.event_type.value,
                impact_amount=month_state.event.impact_amount,
                jar_affected=month_state.event.jar_affected.value if month_state.event.jar_affected else None,
                description=month_state.event.description,
            )
            db.add(db_event)

        db.commit()

        return {
            "session_id": session_id,
            "current_month": simulator.current_month,
            "income": month_state.income,
            "expenses": month_state.expenses,
            "current_jars": month_state.jars.to_dict(),
            "jar_returns": month_state.jar_returns.to_dict(),
            "event": {
                "month": month_state.event.month,
                "type": month_state.event.event_type.value,
                "description": month_state.event.description,
                "impact_amount": month_state.event.impact_amount,
            } if month_state.event else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gullak/{session_id}/complete")
async def complete_gullak_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete a Gullak game session and calculate final scores"""
    try:
        # Get session
        db_session = db.query(GullakSession).filter(
            GullakSession.session_id == session_id,
            GullakSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Recreate full simulator to get proper summary
        current_jars_dict = json.loads(db_session.current_jars)
        simulator = GullakSimulator(
            initial_income=40000,
            initial_expenses=30000,
            income_type=IncomeType(db_session.income_type),
            state_location=StateLocation(db_session.state_location),
            starting_age=db_session.starting_age,
            initial_jars=JarAllocation.from_dict(current_jars_dict),
        )

        simulator.current_month = db_session.current_month

        # Get final scores
        resilience_score, resilience_breakdown = simulator.calculate_resilience_score()
        summary = simulator.get_summary()

        # Update session
        db_session.resilience_score = resilience_score
        db_session.financial_health_index = json.dumps(resilience_breakdown)
        db_session.status = "completed"
        db_session.completed_at = datetime.utcnow()

        db.commit()

        # Award gamification points
        gamification = GamificationService()
        xp_earned = 100 * db_session.current_month + int(resilience_score * 10)
        gamification.add_xp(current_user.id, xp_earned, "gullak_completion")

        return {
            "session_id": session_id,
            "status": "completed",
            "resilience_score": resilience_score,
            "resilience_breakdown": resilience_breakdown,
            "summary": summary,
            "xp_earned": xp_earned,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gullak/{session_id}")
async def get_gullak_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get Gullak session details"""
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


# ============================================================================
# PAPER TRADING GAME ENDPOINTS
# ============================================================================

@router.post("/paper-trading/create")
async def create_paper_trading_session(
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

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
                    "current_month": s.current_month,
                    "resilience_score": s.resilience_score,
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SIP CHRONICLES GAME ENDPOINTS
# ============================================================================


@router.post("/sip/create")
async def create_sip_session(
    sip_type: str = "nifty_50",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new SIP Chronicles game session"""
    try:
        session_id = str(uuid.uuid4())

        # Validate SIP type
        try:
            sip_type_enum = SIPType(sip_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid SIP type: {sip_type}")

        # Create simulator
        simulator = SIPChroniclesSimulator(
            monthly_sip=500,
            sip_type=sip_type_enum,
            starting_age=22,
        )

        # Create database session
        db_session = SIPSession(
            user_id=current_user.id,
            session_id=session_id,
            sip_type=sip_type,
            monthly_sip=500,
            current_month=0,
            current_age=22,
            accumulated_wealth=0,
            total_contributions=0,
            contribution_history=json.dumps([]),
            interruptions_log=json.dumps([]),
            monthly_snapshots=json.dumps([]),
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
            "current_age": 22,
            "accumulated_wealth": 0,
            "total_contributions": 0,
            "monthly_sip": 500,
            "sip_type": sip_type,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sip/{session_id}/progress")
async def progress_sip_month(
    session_id: str,
    fast_forward_months: int = 1,
    interruption_response: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Progress SIP game by specified months"""
    try:
        # Get session
        db_session = db.query(SIPSession).filter(
            SIPSession.session_id == session_id,
            SIPSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        # Recreate simulator state
        simulator = SIPChroniclesSimulator(
            monthly_sip=db_session.monthly_sip,
            sip_type=SIPType(db_session.sip_type),
            starting_age=22,
        )

        simulator.current_month = db_session.current_month
        simulator.current_age = db_session.current_age
        simulator.accumulated_wealth = db_session.accumulated_wealth
        simulator.total_contributions = db_session.total_contributions

        # Simulate months
        last_snapshot = None
        interruption_event = None

        for month_offset in range(fast_forward_months):
            next_month = db_session.current_month + month_offset + 1

            # Apply interruption response if provided and this is first month
            response = None
            if month_offset == 0 and interruption_response:
                try:
                    response = InterruptionResponse(interruption_response)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid response: {interruption_response}")

            snapshot = simulator.simulate_month(next_month, response)
            last_snapshot = snapshot
            if snapshot.interruption:
                interruption_event = snapshot.interruption

        # Update session
        db_session.current_month = simulator.current_month
        db_session.current_age = simulator.current_age
        db_session.accumulated_wealth = simulator.accumulated_wealth
        db_session.total_contributions = simulator.total_contributions
        db_session.monthly_sip = simulator.monthly_sip

        # Save snapshots
        snapshots = json.loads(db_session.monthly_snapshots or "[]")
        if last_snapshot:
            snapshots.append({
                "month": last_snapshot.month,
                "age": last_snapshot.age,
                "wealth": last_snapshot.accumulated_wealth,
                "contributions": last_snapshot.total_contributions,
                "monthly_sip": last_snapshot.monthly_sip,
            })
        db_session.monthly_snapshots = json.dumps(snapshots)

        db.commit()

        # Build response
        response_data = {
            "current_month": simulator.current_month,
            "current_age": simulator.current_age,
            "accumulated_wealth": last_snapshot.accumulated_wealth if last_snapshot else simulator.accumulated_wealth,
            "total_contributions": simulator.total_contributions,
            "monthly_sip": simulator.monthly_sip,
            "interruption": None,
        }

        if interruption_event:
            response_data["interruption"] = {
                "month": interruption_event.month,
                "age": interruption_event.age,
                "type": interruption_event.interruption_type.value,
                "description": interruption_event.description,
                "options": interruption_event.options,
            }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sip/{session_id}/complete")
async def complete_sip_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete SIP Chronicles game and calculate final scores"""
    try:
        db_session = db.query(SIPSession).filter(
            SIPSession.session_id == session_id,
            SIPSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Recreate simulator for final calculations
        simulator = SIPChroniclesSimulator(
            monthly_sip=db_session.monthly_sip,
            sip_type=SIPType(db_session.sip_type),
            starting_age=22,
        )

        simulator.current_month = db_session.current_month
        simulator.accumulated_wealth = db_session.accumulated_wealth
        simulator.total_contributions = db_session.total_contributions

        # Get final summary
        summary = simulator.get_game_summary()

        # Calculate discipline score (0-100)
        multiplier = summary["multiplier"]
        # Perfect is 4x (12% CAGR), baseline is 1x
        discipline_score = min(100, max(0, (multiplier - 1) / 3 * 100))

        # Update session
        db_session.final_corpus = summary["final_corpus"]
        db_session.tax_savings = summary["tax_savings"]
        db_session.financial_discipline_score = discipline_score
        db_session.status = "completed"
        db_session.completed_at = datetime.utcnow()

        db.commit()

        # Award gamification points
        gamification = GamificationService()
        xp_earned = int(50 * summary["interruptions_count"] + (discipline_score * 2))
        gamification.add_xp(current_user.id, xp_earned, "sip_completion")

        return {
            "session_id": session_id,
            "status": "completed",
            "final_corpus": summary["final_corpus"],
            "final_age": summary["final_age"],
            "total_contributions": summary["total_contributions"],
            "total_months": summary["total_months"],
            "multiplier": summary["multiplier"],
            "financial_discipline_score": discipline_score,
            "tax_savings": summary["tax_savings"],
            "interruptions_count": summary["interruptions_count"],
            "xp_earned": xp_earned,
            "interruptions_log": summary["interruptions_log"],
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sip/{session_id}")
async def get_sip_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get SIP session details"""
    try:
        db_session = db.query(SIPSession).filter(
            SIPSession.session_id == session_id,
            SIPSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "current_month": db_session.current_month,
            "current_age": db_session.current_age,
            "status": db_session.status,
            "sip_type": db_session.sip_type,
            "monthly_sip": db_session.monthly_sip,
            "accumulated_wealth": db_session.accumulated_wealth,
            "total_contributions": db_session.total_contributions,
            "interruptions_log": json.loads(db_session.interruptions_log or "[]"),
            "monthly_snapshots": json.loads(db_session.monthly_snapshots or "[]"),
            "final_corpus": db_session.final_corpus,
            "financial_discipline_score": db_session.financial_discipline_score,
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
            "completed_at": db_session.completed_at.isoformat() if db_session.completed_at else None,
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sip/user/sessions")
async def get_user_sip_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all SIP sessions for current user"""
    try:
        sessions = db.query(SIPSession).filter(
            SIPSession.user_id == current_user.id
        ).order_by(SIPSession.created_at.desc()).all()

        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "status": s.status,
                    "current_month": s.current_month,
                    "current_age": s.current_age,
                    "accumulated_wealth": s.accumulated_wealth,
                    "sip_type": s.sip_type,
                    "financial_discipline_score": s.financial_discipline_score,
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
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
    gender: str = "male",
    city: str = "bangalore",
    education: str = "ug",
    starting_job: str = "salaried",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new Karobaar game session"""
    try:
        session_id = str(uuid.uuid4())

        # Create simulator
        simulator = KarobarSimulator(
            gender=gender,
            city=city,
            education=education,
            starting_job=starting_job,
        )

        # Create database session
        db_session = KarobarSession(
            user_id=current_user.id,
            session_id=session_id,
            gender=gender,
            city=city,
            education=education,
            starting_job=starting_job,
            current_age=22,
            current_month=0,
            current_year=0,
            current_state=json.dumps(simulator.state.to_dict()),
            yearly_snapshots=json.dumps(simulator.yearly_snapshots),
            decision_history=json.dumps(simulator.decision_history),
            events_log=json.dumps(simulator.events_log),
            pending_decision=None,
            status="active",
            started_at=datetime.utcnow(),
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": "created",
            "current_age": 22,
            "current_year": 0,
            "initial_state": {
                "salary": simulator.state.current_salary,
                "net_worth": simulator.state.net_worth,
                "job_title": simulator.state.job_title,
                "marital_status": simulator.state.marital_status,
                "career_satisfaction": simulator.state.career_satisfaction,
                "family_happiness": simulator.state.family_happiness,
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PAPER TRADING GAME ENDPOINTS
# ============================================================================

@router.post("/paper-trading/create")
async def create_paper_trading_session(
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/karobaar/{session_id}/progress")
async def advance_karobaar_year(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Advance one year in Karobaar game"""
    try:
        db_session = db.query(KarobarSession).filter(
            KarobarSession.session_id == session_id,
            KarobarSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Game is not active")

        # Recreate simulator from saved state
        state_dict = json.loads(db_session.current_state or "{}")
        simulator = KarobarSimulator(
            gender=db_session.gender,
            city=db_session.city,
            education=db_session.education,
            starting_job=db_session.starting_job,
        )

        if state_dict:
            simulator.state = LifeState(**state_dict)

        # Load history
        simulator.yearly_snapshots = json.loads(db_session.yearly_snapshots or "[]")
        simulator.decision_history = json.loads(db_session.decision_history or "[]")

        # Advance one year
        next_decision = simulator.advance_year()

        # Save updated state
        db_session.current_age = simulator.state.age
        db_session.current_month = simulator.state.current_month
        db_session.current_year = simulator.state.current_year
        db_session.current_state = json.dumps(simulator.state.to_dict())
        db_session.yearly_snapshots = json.dumps(simulator.yearly_snapshots)
        db_session.decision_history = json.dumps(simulator.decision_history)
        db_session.pending_decision = json.dumps(next_decision.__dict__) if next_decision else None
        db_session.updated_at = datetime.utcnow()

        db.commit()

        return {
            "current_age": simulator.state.age,
            "current_year": simulator.state.current_year,
            "updated_state": {
                "salary": simulator.state.current_salary,
                "net_worth": simulator.state.net_worth,
                "career_satisfaction": simulator.state.career_satisfaction,
                "family_happiness": simulator.state.family_happiness,
                "marital_status": simulator.state.marital_status,
                "num_children": simulator.state.num_children,
            },
            "pending_decision": next_decision.__dict__ if next_decision else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/karobaar/{session_id}/decide")
async def make_karobaar_decision(
    session_id: str,
    decision_id: str,
    choice_index: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Make a decision in Karobaar game"""
    try:
        db_session = db.query(KarobarSession).filter(
            KarobarSession.session_id == session_id,
            KarobarSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Recreate simulator
        state_dict = json.loads(db_session.current_state or "{}")
        simulator = KarobarSimulator(
            gender=db_session.gender,
            city=db_session.city,
            education=db_session.education,
            starting_job=db_session.starting_job,
        )

        if state_dict:
            simulator.state = LifeState(**state_dict)

        simulator.yearly_snapshots = json.loads(db_session.yearly_snapshots or "[]")
        simulator.decision_history = json.loads(db_session.decision_history or "[]")

        # Get pending decision
        pending_decision_data = json.loads(db_session.pending_decision or "{}")
        if not pending_decision_data:
            raise HTTPException(status_code=400, detail="No pending decision")

        # Parse the pending decision (need to recreate DecisionPoint)
        # For now, we'll apply a basic decision and return consequences
        try:
            result = simulator.apply_decision(decision_id, choice_index)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Record decision in database
        decision_record = KarobarDecision(
            session_id=session_id,
            age=simulator.state.age,
            month=simulator.state.current_month,
            year=simulator.state.current_year,
            decision_type=pending_decision_data.get("decision_type", "unknown"),
            description=pending_decision_data.get("description", ""),
            choice_index=choice_index,
            choice_text="User choice",
            salary_impact=result["impacts"].get("salary_impact", 0),
            happiness_impact=result["impacts"].get("happiness_impact", 0),
            career_satisfaction_impact=result["impacts"].get("career_satisfaction_impact", 0),
            wealth_impact=result["impacts"].get("wealth_impact", 0),
            debt_impact=result["impacts"].get("debt_impact", 0),
        )

        db.add(decision_record)

        # Advance to next year/decision
        next_decision = simulator.advance_year()

        # Save updated state
        db_session.current_age = simulator.state.age
        db_session.current_month = simulator.state.current_month
        db_session.current_year = simulator.state.current_year
        db_session.current_state = json.dumps(simulator.state.to_dict())
        db_session.yearly_snapshots = json.dumps(simulator.yearly_snapshots)
        db_session.decision_history = json.dumps(simulator.decision_history)
        db_session.pending_decision = json.dumps(next_decision.__dict__) if next_decision else None
        db_session.updated_at = datetime.utcnow()

        db.commit()

        return {
            "current_age": simulator.state.age,
            "current_year": simulator.state.current_year,
            "decision_consequence": result,
            "updated_state": {
                "salary": simulator.state.current_salary,
                "net_worth": simulator.state.net_worth,
                "career_satisfaction": simulator.state.career_satisfaction,
                "family_happiness": simulator.state.family_happiness,
            },
            "next_decision": next_decision.__dict__ if next_decision else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/karobaar/{session_id}/complete")
async def complete_karobaar_game(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete Karobaar game and calculate final scores"""
    try:
        db_session = db.query(KarobarSession).filter(
            KarobarSession.session_id == session_id,
            KarobarSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Recreate simulator
        state_dict = json.loads(db_session.current_state or "{}")
        simulator = KarobarSimulator(
            gender=db_session.gender,
            city=db_session.city,
            education=db_session.education,
            starting_job=db_session.starting_job,
        )

        if state_dict:
            simulator.state = LifeState(**state_dict)

        simulator.yearly_snapshots = json.loads(db_session.yearly_snapshots or "[]")
        simulator.decision_history = json.loads(db_session.decision_history or "[]")

        # Calculate final scores
        final_scores = simulator.get_final_scores()

        # Award gamification XP based on scores
        gamification = GamificationService()
        career_bonus = (final_scores["career_score"] / 100) * 500
        financial_bonus = (final_scores["financial_score"] / 100) * 500
        happiness_bonus = (final_scores["happiness_score"] / 100) * 300
        base_xp = 100
        total_xp = int(base_xp + career_bonus + financial_bonus + happiness_bonus)

        # Note: Actual XP award would happen through gamification service
        # gamification.add_xp(current_user.id, total_xp, "karobaar_completion")

        # Update database session
        db_session.career_score = final_scores["career_score"]
        db_session.financial_score = final_scores["financial_score"]
        db_session.happiness_score = final_scores["happiness_score"]
        db_session.overall_score = final_scores["overall_score"]
        db_session.final_net_worth = final_scores["final_net_worth"]
        db_session.final_salary = final_scores["final_salary"]
        db_session.status = "completed"
        db_session.completed_at = datetime.utcnow()

        db.commit()

        return {
            "session_id": session_id,
            "status": "completed",
            "final_age": final_scores["final_age"],
            "final_scores": {
                "career": final_scores["career_score"],
                "financial": final_scores["financial_score"],
                "happiness": final_scores["happiness_score"],
                "overall": final_scores["overall_score"],
            },
            "final_net_worth": final_scores["final_net_worth"],
            "final_salary": final_scores["final_salary"],
            "decisions_made": final_scores["decisions_made"],
            "xp_earned": total_xp,
            "decision_history": simulator.decision_history,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
            "current_age": db_session.current_age,
            "current_year": db_session.current_year,
            "status": db_session.status,
            "gender": db_session.gender,
            "city": db_session.city,
            "education": db_session.education,
            "current_state": json.loads(db_session.current_state or "{}"),
            "yearly_snapshots": json.loads(db_session.yearly_snapshots or "[]"),
            "decision_history": json.loads(db_session.decision_history or "[]"),
            "career_score": db_session.career_score,
            "financial_score": db_session.financial_score,
            "happiness_score": db_session.happiness_score,
            "overall_score": db_session.overall_score,
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
            "completed_at": db_session.completed_at.isoformat() if db_session.completed_at else None,
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

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
                    "current_age": s.current_age,
                    "current_year": s.current_year,
                    "gender": s.gender,
                    "city": s.city,
                    "overall_score": s.overall_score,
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
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
    era: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new Dalal Street game session"""
    try:
        session_id = str(uuid.uuid4())
        market_era = MarketEra(era)

        # Create simulator
        simulator = DalalStreetSimulator(era=market_era)

        # Create DB session
        db_session = DalalSession(
            user_id=current_user.id,
            session_id=session_id,
            era=era,
            current_quarter=0,
            portfolio_json=simulator.serialize_state(),
            trades_history=json.dumps([]),
            news_events_log=json.dumps([n.to_dict() for n in simulator.news_log]),
            quarterly_snapshots=json.dumps([]),
            decisions_log=json.dumps([]),
            status="active",
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "status": "created",
            "era": era,
            "current_quarter": 0,
            "era_narrative": simulator.config.get("narrative"),
            "starting_capital": simulator.portfolio.cash,
            "available_stocks": len(simulator.stock_quotes),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid era: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dalal/{session_id}/advance-quarter")
async def advance_dalal_quarter(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Advance to next quarter in Dalal Street game"""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        # Restore simulator state
        simulator = DalalStreetSimulator.deserialize_state(
            MarketEra(db_session.era), db_session.portfolio_json
        )

        # Advance quarter
        market_movement, news_event = simulator.advance_quarter()

        # Save updated state
        db_session.current_quarter += 1
        db_session.portfolio_json = simulator.serialize_state()

        news_list = json.loads(db_session.news_events_log or "[]")
        if news_event:
            news_list.append(news_event.to_dict())
        db_session.news_events_log = json.dumps(news_list)

        portfolio_summary = simulator.get_portfolio_value_summary()
        snapshots = json.loads(db_session.quarterly_snapshots or "[]")
        snapshots.append({
            "quarter": db_session.current_quarter,
            "portfolio_value": portfolio_summary["total_value"],
            "market_index": simulator.market_index_history[-1],
        })
        db_session.quarterly_snapshots = json.dumps(snapshots)

        db.commit()

        return {
            "session_id": session_id,
            "current_quarter": db_session.current_quarter,
            "market_movement": market_movement,
            "portfolio_value": portfolio_summary["total_value"],
            "cash": portfolio_summary["cash"],
            "holdings_value": portfolio_summary["holdings_value"],
            "news_event": news_event.to_dict() if news_event else None,
            "market_index": simulator.market_index_history[-1],
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dalal/{session_id}/trade")
async def execute_dalal_trade(
    session_id: str,
    symbol: str,
    trade_type: str,
    quantity: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in Dalal Street"""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Restore simulator state
        simulator = DalalStreetSimulator.deserialize_state(
            MarketEra(db_session.era), db_session.portfolio_json
        )

        # Execute trade
        success, message = simulator.execute_trade(
            symbol=symbol,
            trade_type=TradeType(trade_type),
            quantity=quantity
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        # Save updated state
        db_session.portfolio_json = simulator.serialize_state()
        trades_list = json.loads(db_session.trades_history or "[]")

        # Add latest trade
        if simulator.portfolio.trades:
            latest_trade = simulator.portfolio.trades[-1]
            trades_list.append(latest_trade.to_dict())

        db_session.trades_history = json.dumps(trades_list)
        db.commit()

        portfolio_summary = simulator.get_portfolio_value_summary()
        return {
            "success": True,
            "message": message,
            "portfolio_value": portfolio_summary["total_value"],
            "cash": portfolio_summary["cash"],
            "holdings_value": portfolio_summary["holdings_value"],
            "holdings": portfolio_summary["holdings"],
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dalal/{session_id}/make-decision")
async def make_dalal_decision(
    session_id: str,
    decision_id: int,
    choice_index: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Make a quarterly strategic decision in Dalal Street"""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Restore simulator state
        simulator = DalalStreetSimulator.deserialize_state(
            MarketEra(db_session.era), db_session.portfolio_json
        )

        # Get decision
        decision = simulator.generate_quarterly_decision()

        if choice_index >= len(decision["options"]):
            raise HTTPException(status_code=400, detail="Invalid choice")

        choice = decision["options"][choice_index]

        # Record decision
        decisions_log = json.loads(db_session.decisions_log or "[]")
        decisions_log.append({
            "quarter": db_session.current_quarter,
            "decision_id": decision_id,
            "choice_index": choice_index,
            "choice_text": choice["text"],
            "action": choice["action"],
        })
        db_session.decisions_log = json.dumps(decisions_log)
        db_session.portfolio_json = simulator.serialize_state()
        db.commit()

        return {
            "session_id": session_id,
            "decision_recorded": True,
            "choice": choice["text"],
            "next_quarter_available": db_session.current_quarter < 19,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dalal/{session_id}/available-stocks")
async def get_dalal_available_stocks(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get available stocks for trading"""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Restore simulator state
        simulator = DalalStreetSimulator.deserialize_state(
            MarketEra(db_session.era), db_session.portfolio_json
        )

        stocks_list = []
        for symbol, quote in simulator.stock_quotes.items():
            # Calculate trend
            if len(simulator.quarterly_snapshots) > 0:
                # Simplified trend calculation
                trend = "stable"
                if quote.current_price > quote.open_price * 1.05:
                    trend = "up"
                elif quote.current_price < quote.open_price * 0.95:
                    trend = "down"
            else:
                trend = "stable"

            stocks_list.append({
                "symbol": symbol,
                "name": quote.name,
                "current_price": quote.current_price,
                "open_price": quote.open_price,
                "high_price": quote.high_price,
                "low_price": quote.low_price,
                "pe_ratio": quote.pe_ratio,
                "sector": quote.sector,
                "market_cap_category": quote.market_cap_category,
                "trend": trend,
            })

        return {"stocks": stocks_list}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PAPER TRADING GAME ENDPOINTS
# ============================================================================

@router.post("/paper-trading/create")
async def create_paper_trading_session(
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dalal/{session_id}/complete")
async def complete_dalal_game(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete Dalal Street game and calculate final scores"""
    try:
        db_session = db.query(DalalSession).filter(
            DalalSession.session_id == session_id,
            DalalSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Restore simulator state
        simulator = DalalStreetSimulator.deserialize_state(
            MarketEra(db_session.era), db_session.portfolio_json
        )

        # Calculate final scores
        scores = simulator.get_final_scores()

        # Award XP
        base_xp = 100
        timing_bonus = int((scores["timing_score"] / 100) * 300)
        portfolio_bonus = int((scores["portfolio_management_score"] / 100) * 300)
        risk_bonus = int((scores["risk_score"] / 100) * 200)
        total_xp = base_xp + timing_bonus + portfolio_bonus + risk_bonus

        gamification = GamificationService(db)
        gamification.add_xp(current_user.id, total_xp, "dalal_completion")

        # Update DB session with final scores
        db_session.status = "completed"
        db_session.is_completed = True
        db_session.starting_value = scores["starting_value"]
        db_session.ending_value = scores["ending_value"]
        db_session.total_profit_loss = scores["return_amount"]
        db_session.return_percentage = scores["return_pct"]
        db_session.market_comparison_return = scores["market_return_pct"]
        db_session.max_drawdown = scores["max_drawdown"]
        db_session.timing_score = scores["timing_score"]
        db_session.portfolio_management_score = scores["portfolio_management_score"]
        db_session.risk_score = scores["risk_score"]
        db_session.overall_score = scores["overall_score"]
        db_session.completed_at = datetime.utcnow()

        db.commit()

        return {
            "session_id": session_id,
            "status": "completed",
            "final_scores": {
                "timing": scores["timing_score"],
                "portfolio_management": scores["portfolio_management_score"],
                "risk_management": scores["risk_score"],
                "overall": scores["overall_score"],
            },
            "portfolio_performance": {
                "starting_value": scores["starting_value"],
                "ending_value": scores["ending_value"],
                "profit_loss": scores["return_amount"],
                "return_percentage": scores["return_pct"],
                "market_return_percentage": scores["market_return_pct"],
                "max_drawdown": scores["max_drawdown"],
            },
            "xp_earned": total_xp,
            "trades_count": len(simulator.portfolio.trades),
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
            "current_quarter": db_session.current_quarter,
            "portfolio": json.loads(db_session.portfolio_json or "{}"),
            "trades_history": json.loads(db_session.trades_history or "[]"),
            "news_events_log": json.loads(db_session.news_events_log or "[]"),
            "quarterly_snapshots": json.loads(db_session.quarterly_snapshots or "[]"),
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
            "completed_at": db_session.completed_at.isoformat() if db_session.completed_at else None,
            "overall_score": db_session.overall_score,
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

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
                    "current_quarter": s.current_quarter,
                    "overall_score": s.overall_score,
                    "return_percentage": s.return_percentage,
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
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
    crisis_type: str,
    profile_type: str,
    difficulty: str = "medium",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new Black Swan crisis simulation session"""
    try:
        session_id = str(uuid.uuid4())
        crisis = CrisisType(crisis_type)
        profile = PlayerProfile(profile_type)
        random_seed = random.randint(100000, 999999)

        # Generate random financial profile
        financial_profile = generate_random_profile(profile, random_seed)

        # Create simulator
        simulator = BlackSwanSimulator(
            crisis_type=crisis,
            player_profile=profile,
            random_seed=random_seed,
            difficulty=difficulty,
        )
        simulator.player_profile = financial_profile

        # Create DB session
        db_session = BlackSwanSession(
            user_id=current_user.id,
            session_id=session_id,
            crisis_type=crisis_type,
            player_profile_type=profile_type,
            random_seed=random_seed,
            difficulty_level=difficulty,
            financial_profile=json.dumps(financial_profile.to_dict()),
            quarterly_wealth_history=json.dumps(simulator.quarterly_wealth_history),
            market_index_history=json.dumps(simulator.market_index_history),
            decisions_made=json.dumps([]),
            status="active",
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        crisis_config = simulator.crisis_config
        return {
            "session_id": session_id,
            "crisis_type": crisis_type,
            "profile_type": profile_type,
            "difficulty": difficulty,
            "crisis_name": crisis_config["name"],
            "crisis_description": crisis_config["description"],
            "starting_wealth": financial_profile.get_net_worth(),
            "financial_profile": financial_profile.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/black-swan/{session_id}/advance-quarter")
async def advance_black_swan_quarter(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Advance to next quarter in Black Swan game"""
    try:
        db_session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        if db_session.status != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        # Restore simulator state
        profile = FinancialProfile.from_dict(json.loads(db_session.financial_profile))
        simulator = BlackSwanSimulator(
            crisis_type=CrisisType(db_session.crisis_type),
            player_profile=profile,
            random_seed=db_session.random_seed,
            difficulty=db_session.difficulty_level,
        )
        simulator.current_quarter = db_session.current_quarter
        simulator.quarterly_wealth_history = json.loads(db_session.quarterly_wealth_history)
        simulator.market_index_history = json.loads(db_session.market_index_history)

        # Advance quarter
        result = simulator.advance_quarter()

        # Save state
        db_session.current_quarter += 1
        db_session.current_phase = result["phase"]
        db_session.quarterly_wealth_history = json.dumps(simulator.quarterly_wealth_history)
        db_session.market_index_history = json.dumps(simulator.market_index_history)
        db.commit()

        return {
            "session_id": session_id,
            "current_quarter": db_session.current_quarter,
            "phase": result["phase"],
            "wealth": result["wealth"],
            "market_index": result["market_index"],
            "market_return": result["market_return"],
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/black-swan/{session_id}/make-decision")
async def make_black_swan_decision(
    session_id: str,
    decision_type: str,
    asset_class: str,
    amount: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Make a decision during Black Swan game"""
    try:
        db_session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Restore simulator state
        profile = FinancialProfile.from_dict(json.loads(db_session.financial_profile))
        simulator = BlackSwanSimulator(
            crisis_type=CrisisType(db_session.crisis_type),
            player_profile=profile,
            random_seed=db_session.random_seed,
            difficulty=db_session.difficulty_level,
        )

        # Make decision
        success, message = simulator.make_decision(
            decision_type=DecisionType(decision_type),
            asset_class=asset_class,
            amount=amount,
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        # Record decision in DB
        decision = BlackSwanDecision(
            session_id=session_id,
            quarter=db_session.current_quarter,
            decision_context="crisis" if db_session.current_phase != "pre_crisis" else "pre_crisis",
            decision_type=decision_type,
            asset_class=asset_class,
            amount=amount,
        )
        db.add(decision)

        # Update state
        db_session.financial_profile = json.dumps(profile.to_dict())
        db.commit()

        return {
            "success": True,
            "message": message,
            "wealth": profile.get_net_worth(),
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/black-swan/{session_id}/recommendations")
async def get_black_swan_recommendations(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get educational pre-crisis recommendations"""
    try:
        db_session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        profile = FinancialProfile.from_dict(json.loads(db_session.financial_profile))
        simulator = BlackSwanSimulator(
            crisis_type=CrisisType(db_session.crisis_type),
            player_profile=PlayerProfile(db_session.player_profile_type),
            random_seed=db_session.random_seed,
            difficulty=db_session.difficulty_level,
        )

        recommendations = simulator.get_recommendations()
        return {"recommendations": recommendations}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PAPER TRADING GAME ENDPOINTS
# ============================================================================

@router.post("/paper-trading/create")
async def create_paper_trading_session(
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/black-swan/{session_id}/complete")
async def complete_black_swan_game(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Complete Black Swan game and calculate antifragility scores"""
    try:
        db_session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Restore simulator state
        profile = FinancialProfile.from_dict(json.loads(db_session.financial_profile))
        simulator = BlackSwanSimulator(
            crisis_type=CrisisType(db_session.crisis_type),
            player_profile=PlayerProfile(db_session.player_profile_type),
            random_seed=db_session.random_seed,
            difficulty=db_session.difficulty_level,
        )
        simulator.quarterly_wealth_history = json.loads(db_session.quarterly_wealth_history)

        # Calculate scores
        scores = simulator.calculate_antifragility_score()

        # Award XP
        base_xp = 200
        antifragility_bonus = max(0, int(scores["antifragility_score"] * 5))
        survival_bonus = 100 if scores["survival"] else 0
        total_xp = base_xp + antifragility_bonus + survival_bonus

        gamification = GamificationService(db)
        gamification.add_xp(current_user.id, total_xp, "black_swan_completion")

        # Update DB
        db_session.status = "completed"
        db_session.starting_wealth = scores["starting_wealth"]
        db_session.trough_wealth = scores["trough_wealth"]
        db_session.final_wealth = scores["final_wealth"]
        db_session.antifragility_score = scores["antifragility_score"]
        db_session.max_drawdown_pct = scores["max_drawdown_pct"]
        db_session.survival = scores["survival"]
        db_session.overall_score = max(0, 50 + scores["antifragility_score"])
        db_session.completed_at = datetime.utcnow()
        db.commit()

        return {
            "session_id": session_id,
            "status": "completed",
            "scores": {
                "antifragility": scores["antifragility_score"],
                "overall": db_session.overall_score,
                "survival": scores["survival"],
            },
            "performance": {
                "starting_wealth": scores["starting_wealth"],
                "trough_wealth": scores["trough_wealth"],
                "final_wealth": scores["final_wealth"],
                "max_drawdown_pct": scores["max_drawdown_pct"],
            },
            "xp_earned": total_xp,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
            "profile_type": db_session.player_profile_type,
            "difficulty": db_session.difficulty_level,
            "current_quarter": db_session.current_quarter,
            "current_phase": db_session.current_phase,
            "financial_profile": json.loads(db_session.financial_profile),
            "quarterly_wealth_history": json.loads(db_session.quarterly_wealth_history),
            "antifragility_score": db_session.antifragility_score,
            "overall_score": db_session.overall_score,
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
            "completed_at": db_session.completed_at.isoformat() if db_session.completed_at else None,
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/black-swan/{session_id}/hindsight")
async def get_black_swan_hindsight(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get hindsight analysis of decisions made"""
    try:
        db_session = db.query(BlackSwanSession).filter(
            BlackSwanSession.session_id == session_id,
            BlackSwanSession.user_id == current_user.id,
        ).first()

        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        decisions = db.query(BlackSwanDecision).filter(
            BlackSwanDecision.session_id == session_id
        ).all()

        return {
            "decisions": [
                {
                    "quarter": d.quarter,
                    "context": d.decision_context,
                    "decision": d.decision_type,
                    "asset": d.asset_class,
                    "amount": d.amount,
                    "optimal_action": d.optimal_action,
                    "cost_of_error": d.cost_of_error,
                }
                for d in decisions
            ],
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

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
                    "profile_type": s.player_profile_type,
                    "difficulty": s.difficulty_level,
                    "antifragility_score": s.antifragility_score,
                    "overall_score": s.overall_score,
                    "survival": s.survival,
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
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
    market: str,
    strategy: str,
    initial_capital: float,
    start_date: str,
    end_date: str,
    symbols: Optional[list] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new paper trading session"""
    try:
        session_id = str(uuid.uuid4())

        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Create simulator
        market_type = MarketType(market.lower())
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=initial_capital,
            strategy=strategy,
            start_date=start_dt,
            end_date=end_dt,
        )

        # Create database session
        db_session = PaperTradingSession(
            user_id=current_user.id,
            session_id=session_id,
            market=market.lower(),
            strategy=strategy,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            start_date=start_dt,
            end_date=end_dt,
            current_date=start_dt,
            current_portfolio=json.dumps({
                "holdings": {},
                "cash": initial_capital,
                "total_value": initial_capital,
            }),
            all_holdings=json.dumps([]),
            status="active",
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return {
            "session_id": session_id,
            "market": market,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "active",
        }

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

        portfolio = json.loads(session.current_portfolio)

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
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paper-trading/{session_id}/trade")
async def execute_paper_trade(
    session_id: str,
    symbol: str,
    quantity: int,
    price: float,
    side: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Execute a trade in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create simulator instance
        market_type = MarketType(session.market)
        simulator = PaperTradingSimulator(
            market=market_type,
            initial_capital=session.initial_capital,
            strategy=session.strategy,
            start_date=session.start_date,
            end_date=session.end_date,
        )

        # Restore portfolio state
        portfolio_data = json.loads(session.current_portfolio)
        simulator.portfolio.cash = portfolio_data.get("cash", session.current_capital)

        # Execute trade
        trade_side = TradeSide(side.upper())
        result = simulator.execute_trade(symbol, quantity, price, trade_side)

        if result["success"]:
            # Update session
            session.current_capital = simulator.portfolio.cash
            session.current_portfolio = json.dumps({
                "holdings": {
                    sym: {
                        "quantity": h.quantity,
                        "entry_price": h.entry_price,
                        "current_price": h.current_price,
                        "value": h.get_value(),
                        "pnl": h.get_pnl(),
                        "pnl_percentage": h.get_pnl_percentage(),
                    }
                    for sym, h in simulator.portfolio.holdings.items()
                },
                "cash": simulator.portfolio.cash,
                "total_value": simulator.portfolio.get_total_value(),
            })

            # Record trade
            db_trade = PaperTrade(
                session_id_fk=session.id,
                trade_id=result["trade_id"],
                symbol=symbol,
                quantity=quantity,
                price=price,
                side=side.upper(),
                executed_at=session.current_date,
                commission=result.get("commission", 0.0),
                total_value=result.get("total_value", quantity * price),
            )

            db.add(db_trade)
            db.commit()

            return {
                "success": True,
                "trade": result,
                "portfolio": json.loads(session.current_portfolio),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Trade failed"),
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/holdings")
async def get_paper_trading_holdings(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current holdings in paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        portfolio_data = json.loads(session.current_portfolio)
        holdings = portfolio_data.get("holdings", {})

        return {
            "holdings": [
                {
                    "symbol": symbol,
                    **holding,
                    "allocation_percentage": (holding.get("value", 0) / portfolio_data.get("total_value", 1) * 100),
                }
                for symbol, holding in holdings.items()
            ],
            "cash": portfolio_data.get("cash", 0),
            "total_value": portfolio_data.get("total_value", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paper-trading/{session_id}/history")
async def get_paper_trading_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get trade history for paper trading session"""
    try:
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.session_id == session_id,
            PaperTradingSession.user_id == current_user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id_fk == session.id
        ).order_by(PaperTrade.executed_at.desc()).all()

        return {
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                    "total_value": t.total_value,
                    "commission": t.commission,
                    "pnl": t.profit_loss,
                    "executed_at": t.executed_at.isoformat(),
                }
                for t in trades
            ]
        }

    except HTTPException:
        raise
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
        session.total_profit_loss = metrics["total_pnl"]
        session.profit_loss_percentage = metrics["pnl_percentage"]
        session.portfolio_score = scores["portfolio_score"]
        session.diversification_score = scores["diversification_score"]
        session.risk_adjusted_score = scores["risk_adjusted_score"]
        session.timing_score = scores["timing_score"]
        session.adherence_score = scores["adherence_score"]
        session.total_score = scores["total_score"]
        session.max_drawdown = metrics["max_drawdown"]
        session.win_rate = metrics["win_rate"]

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
                    "created_at": s.created_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
