"""
Session Analytics & Reporting System
Tracks gameplay metrics, learning curves, and generates reports
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


class DecisionType(Enum):
    """Types of decisions made by player"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    ALLOCATE = "allocate"
    EXPAND = "expand"
    STRATEGY_CHANGE = "strategy_change"
    RISK_ADJUSTMENT = "risk_adjustment"


@dataclass
class Decision:
    """Single decision made during gameplay"""
    decision_type: DecisionType
    timestamp: datetime
    outcome: str  # "profitable", "loss", "neutral", "pending"
    amount: float
    details: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0  # 0.0-1.0 rating of decision


@dataclass
class SessionMetrics:
    """Metrics for a single game session"""
    session_id: str
    user_id: str
    game_type: str
    difficulty: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: float = 0.0
    
    # Performance metrics
    starting_capital: float = 0.0
    ending_capital: float = 0.0
    profit_loss: float = 0.0
    roi: float = 0.0  # Return on investment percentage
    
    # Decision metrics
    total_decisions: int = 0
    decisions: List[Decision] = field(default_factory=list)
    profitable_decisions: int = 0
    losing_decisions: int = 0
    decision_accuracy: float = 0.0  # % of good decisions
    average_decision_quality: float = 0.0
    
    # Engagement metrics
    pause_count: int = 0
    restart_count: int = 0
    hint_used_count: int = 0
    
    # Learning metrics
    early_performance: float = 0.0  # Avg score in first 20% of session
    late_performance: float = 0.0  # Avg score in last 20% of session
    learning_improvement: float = 0.0  # late - early (positive = improvement)
    
    # Risk management
    max_drawdown: float = 0.0  # Biggest loss experienced
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    win_streak: int = 0
    loss_streak: int = 0
    
    # Knowledge assessment
    mistake_types: Dict[str, int] = field(default_factory=dict)  # Type -> count
    
    # Completion
    completed: bool = False
    session_xp_earned: int = 0
    achievement_unlocked: Optional[str] = None


class LearningCurve:
    """Tracks learning progress over multiple sessions"""
    
    def __init__(self, user_id: str, game_type: str):
        self.user_id = user_id
        self.game_type = game_type
        self.sessions: List[SessionMetrics] = []
        self.milestone_dates: Dict[str, datetime] = {}
    
    def add_session(self, session: SessionMetrics):
        """Add a completed session"""
        self.sessions.append(session)
    
    def get_improvement_trend(self) -> Dict[str, Any]:
        """Calculate improvement trend over sessions"""
        if len(self.sessions) < 2:
            return {"trend": "insufficient_data"}
        
        recent_sessions = self.sessions[-5:]  # Last 5 sessions
        roi_values = [s.roi for s in recent_sessions]
        
        # Calculate trend
        if len(roi_values) >= 2:
            trend = roi_values[-1] - roi_values[0]
            trend_percentage = (trend / max(abs(roi_values[0]), 0.01)) * 100
        else:
            trend = 0
            trend_percentage = 0
        
        return {
            "trend": "improving" if trend > 5 else "stable" if abs(trend) <= 5 else "declining",
            "roi_change": trend,
            "roi_change_percentage": trend_percentage,
            "average_roi": sum(roi_values) / len(roi_values),
            "sessions_analyzed": len(recent_sessions),
        }
    
    def get_mastery_level(self) -> Dict[str, Any]:
        """Assess player's mastery level"""
        if not self.sessions:
            return {"level": "beginner", "score": 0}
        
        avg_roi = sum(s.roi for s in self.sessions) / len(self.sessions)
        avg_accuracy = sum(s.decision_accuracy for s in self.sessions) / len(self.sessions)
        
        if avg_roi > 50 and avg_accuracy > 0.75:
            level = "expert"
            score = 90 + min(10, (avg_roi - 50) / 10)
        elif avg_roi > 25 and avg_accuracy > 0.65:
            level = "advanced"
            score = 70 + ((avg_roi - 25) / 25) * 20
        elif avg_roi > 0 and avg_accuracy > 0.55:
            level = "intermediate"
            score = 50 + (avg_roi / 25) * 20
        elif avg_accuracy > 0.45:
            level = "developing"
            score = 30 + (avg_accuracy - 0.45) / 0.1 * 20
        else:
            level = "beginner"
            score = 0 + (avg_accuracy * 30)
        
        return {
            "level": level,
            "score": min(100, score),
            "avg_roi": avg_roi,
            "avg_accuracy": avg_accuracy,
            "sessions_played": len(self.sessions),
        }


class SessionAnalytics:
    """Main analytics engine"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionMetrics] = {}
        self.learning_curves: Dict[str, Dict[str, LearningCurve]] = {}  # user_id -> {game_type -> curve}
    
    def start_session(
        self, session_id: str, user_id: str, game_type: str, difficulty: str,
        starting_capital: float
    ) -> SessionMetrics:
        """Start tracking a new session"""
        session = SessionMetrics(
            session_id=session_id,
            user_id=user_id,
            game_type=game_type,
            difficulty=difficulty,
            start_time=datetime.now(),
            starting_capital=starting_capital,
        )
        
        self.sessions[session_id] = session
        return session
    
    def record_decision(
        self,
        session_id: str,
        decision_type: DecisionType,
        amount: float,
        outcome: str,
        quality_score: float,
        details: Optional[Dict] = None,
    ) -> bool:
        """Record a decision in a session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        decision = Decision(
            decision_type=decision_type,
            timestamp=datetime.now(),
            outcome=outcome,
            amount=amount,
            details=details or {},
            quality_score=quality_score,
        )
        
        session.decisions.append(decision)
        session.total_decisions += 1
        
        # Update metrics
        if outcome == "profitable":
            session.profitable_decisions += 1
        elif outcome == "loss":
            session.losing_decisions += 1
        
        session.average_decision_quality = (
            sum(d.quality_score for d in session.decisions) / len(session.decisions)
        )
        session.decision_accuracy = session.profitable_decisions / max(session.total_decisions, 1)
        
        return True
    
    def end_session(
        self,
        session_id: str,
        ending_capital: float,
        achievement_unlocked: Optional[str] = None,
        session_xp: int = 0,
    ) -> SessionMetrics:
        """End session and calculate metrics"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        session.end_time = datetime.now()
        session.ending_capital = ending_capital
        session.completed = True
        session.achievement_unlocked = achievement_unlocked
        session.session_xp_earned = session_xp
        
        # Calculate duration
        session.duration_minutes = (session.end_time - session.start_time).total_seconds() / 60
        
        # Calculate profit/loss and ROI
        session.profit_loss = ending_capital - session.starting_capital
        if session.starting_capital > 0:
            session.roi = (session.profit_loss / session.starting_capital) * 100
        
        # Calculate learning improvement
        if session.decisions:
            mid_point = len(session.decisions) // 5
            early_decisions = session.decisions[:mid_point] if mid_point > 0 else session.decisions
            late_decisions = session.decisions[-mid_point:] if mid_point > 0 else session.decisions
            
            session.early_performance = (
                sum(d.quality_score for d in early_decisions) / len(early_decisions)
                if early_decisions else 0
            )
            session.late_performance = (
                sum(d.quality_score for d in late_decisions) / len(late_decisions)
                if late_decisions else 0
            )
            session.learning_improvement = session.late_performance - session.early_performance
        
        # Calculate streaks
        win_streak = 0
        loss_streak = 0
        for decision in session.decisions:
            if decision.outcome == "profitable":
                win_streak += 1
                loss_streak = 0
                session.win_streak = max(session.win_streak, win_streak)
            else:
                loss_streak += 1
                win_streak = 0
                session.loss_streak = max(session.loss_streak, loss_streak)
        
        # Track learning curve
        if session.user_id not in self.learning_curves:
            self.learning_curves[session.user_id] = {}
        
        if session.game_type not in self.learning_curves[session.user_id]:
            self.learning_curves[session.user_id][session.game_type] = LearningCurve(
                session.user_id, session.game_type
            )
        
        self.learning_curves[session.user_id][session.game_type].add_session(session)
        
        return session
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a completed session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "game_type": session.game_type,
            "difficulty": session.difficulty,
            "duration_minutes": round(session.duration_minutes, 1),
            "profit_loss": round(session.profit_loss, 2),
            "roi": round(session.roi, 2),
            "total_decisions": session.total_decisions,
            "decision_accuracy": round(session.decision_accuracy * 100, 1),
            "average_decision_quality": round(session.average_decision_quality, 2),
            "learning_improvement": round(session.learning_improvement, 2),
            "win_streak": session.win_streak,
            "loss_streak": session.loss_streak,
            "xp_earned": session.session_xp_earned,
            "achievement": session.achievement_unlocked,
        }
    
    def get_learning_insights(self, user_id: str, game_type: str) -> Dict[str, Any]:
        """Get learning insights for a user in a game"""
        if user_id not in self.learning_curves:
            return {"message": "No data available"}
        
        if game_type not in self.learning_curves[user_id]:
            return {"message": "No data for this game"}
        
        curve = self.learning_curves[user_id][game_type]
        
        return {
            "mastery_level": curve.get_mastery_level(),
            "improvement_trend": curve.get_improvement_trend(),
            "recent_sessions": len(curve.sessions),
            "recommendation": self._get_recommendation(curve),
        }
    
    def _get_recommendation(self, curve: LearningCurve) -> str:
        """Generate recommendation based on learning curve"""
        if not curve.sessions:
            return "Keep practicing to unlock recommendations!"
        
        trend = curve.get_improvement_trend()
        mastery = curve.get_mastery_level()
        
        if mastery["level"] == "expert":
            return "🎯 You're mastering this game! Try higher difficulty to stay challenged."
        elif mastery["level"] == "advanced":
            return "✨ Great progress! Try advanced strategies to improve further."
        elif trend.get("trend") == "improving":
            return "📈 You're improving! Keep practicing with your current difficulty."
        elif trend.get("trend") == "declining":
            return "📉 Try reducing difficulty to rebuild confidence and fundamentals."
        else:
            return "🎓 You've found a good difficulty level. Focus on consistent practice."
    
    def generate_pdf_report(self, session_id: str) -> str:
        """Generate PDF report summary (returns placeholder)"""
        session = self.sessions.get(session_id)
        if not session:
            return ""
        
        # This is a placeholder - actual PDF generation would use reportlab
        report = f"""
# Game Session Report - {session.game_type}

## Performance Summary
- Duration: {session.duration_minutes:.1f} minutes
- Starting Capital: ₹{session.starting_capital:,.0f}
- Ending Capital: ₹{session.ending_capital:,.0f}
- Profit/Loss: ₹{session.profit_loss:,.0f} ({session.roi:.1f}% ROI)

## Decision Analysis
- Total Decisions: {session.total_decisions}
- Profitable: {session.profitable_decisions}
- Accuracy: {session.decision_accuracy*100:.1f}%
- Avg Quality Score: {session.average_decision_quality:.2f}/1.0

## Learning Metrics
- Early Performance: {session.early_performance:.2f}
- Late Performance: {session.late_performance:.2f}
- Improvement: {session.learning_improvement:.2f}

## Risk Management
- Win Streak: {session.win_streak}
- Loss Streak: {session.loss_streak}

## Rewards
- XP Earned: {session.session_xp_earned}
- Achievement: {session.achievement_unlocked or 'None'}
        """
        return report
