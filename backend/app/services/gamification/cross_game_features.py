"""
Cross-Game Features System
Manages persistent portfolio, career path integration, and compound rewards
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class GameType(Enum):
    """All game/simulation types"""
    PAPER_TRADING = "paper_trading"
    DALAL_STREET = "dalal_street"
    KAROBAAR = "karobaar"
    GULLAK = "gullak"
    SIP_CHRONICLES = "sip_chronicles"
    BLACK_SWAN = "black_swan"
    COFFEE_SHOP = "coffee_shop"
    PAYCHECK_GAME = "paycheck_game"
    BUDGET_BUILDER = "budget_builder"
    EMERGENCY_FUND = "emergency_fund"
    COMPOUND_INTEREST = "compound_interest"
    CAR_PAYMENT = "car_payment"
    CREDIT_CARD_DEBT = "credit_card_debt"


@dataclass
class PersistentHolding:
    """Stock held across multiple games"""
    symbol: str
    quantity: int
    entry_price: float
    entry_game: GameType
    entry_date: datetime
    current_price: float = 0.0
    unrealized_gain: float = 0.0
    source_session_id: str = ""


@dataclass
class PersistentPortfolio:
    """Portfolio that spans across games"""
    user_id: str
    total_cash: float = 0.0  # Available cash across games
    holdings: Dict[str, PersistentHolding] = field(default_factory=dict)
    total_invested: float = 0.0
    total_gains: float = 0.0
    creation_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def get_portfolio_value(self) -> float:
        """Total portfolio value (cash + holdings)"""
        holdings_value = sum(h.current_price * h.quantity for h in self.holdings.values())
        return self.total_cash + holdings_value

    def get_total_return_percentage(self) -> float:
        """Overall return percentage"""
        if self.total_invested == 0:
            return 0.0
        portfolio_value = self.get_portfolio_value()
        return ((portfolio_value - self.total_invested) / self.total_invested) * 100


@dataclass
class CareerMilestone:
    """Career progression milestone"""
    name: str
    game: GameType
    requirement: str  # e.g., "portfolio_value >= 500000"
    reward_xp: int
    unlock_game: Optional[GameType] = None  # Game unlocked after reaching this
    description: str = ""


class CareerPath:
    """User's career progression across games"""

    MILESTONES = [
        CareerMilestone(
            name="Novice Entrepreneur",
            game=GameType.KAROBAAR,
            requirement="revenue >= 100000",
            reward_xp=300,
            description="Start your first business",
        ),
        CareerMilestone(
            name="Growing Business",
            game=GameType.KAROBAAR,
            requirement="revenue >= 500000",
            reward_xp=600,
            description="Scale business to ₹5L revenue",
        ),
        CareerMilestone(
            name="Established Business",
            game=GameType.KAROBAAR,
            requirement="revenue >= 2000000 AND expansion_count >= 1",
            reward_xp=1000,
            description="Expand business operations",
            unlock_game=GameType.PAPER_TRADING,
        ),
        CareerMilestone(
            name="Novice Trader",
            game=GameType.PAPER_TRADING,
            requirement="trades >= 5",
            reward_xp=300,
            description="Execute 5 stock trades",
        ),
        CareerMilestone(
            name="Confident Trader",
            game=GameType.PAPER_TRADING,
            requirement="portfolio_value >= 1000000",
            reward_xp=800,
            description="Grow portfolio to ₹10L",
        ),
        CareerMilestone(
            name="Master Trader",
            game=GameType.PAPER_TRADING,
            requirement="profitable_trades >= 10 AND win_rate >= 0.6",
            reward_xp=1500,
            description="Achieve 60%+ win rate with 10+ profitable trades",
            unlock_game=GameType.DALAL_STREET,
        ),
        CareerMilestone(
            name="Market Analyst",
            game=GameType.DALAL_STREET,
            requirement="portfolio_value >= 500000 AND quarters_played >= 8",
            reward_xp=1000,
            description="Play through 2+ years (8 quarters) of market",
        ),
        CareerMilestone(
            name="Wealth Creator",
            game=GameType.DALAL_STREET,
            requirement="total_return >= 1.5",
            reward_xp=2000,
            description="Achieve 150% return across games",
            unlock_game=GameType.BLACK_SWAN,
        ),
    ]

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.completed_milestones: List[str] = []
        self.current_game: Optional[GameType] = None
        self.games_unlocked: List[GameType] = [
            GameType.COFFEE_SHOP,
            GameType.PAYCHECK_GAME,
            GameType.BUDGET_BUILDER,
            GameType.EMERGENCY_FUND,
            GameType.COMPOUND_INTEREST,
            GameType.CAR_PAYMENT,
            GameType.CREDIT_CARD_DEBT,
            GameType.GULLAK,
            GameType.SIP_CHRONICLES,
        ]

    def check_milestone_completion(self, stats: Dict[str, Any]) -> Optional[CareerMilestone]:
        """Check if any new milestone is completed"""
        for milestone in self.MILESTONES:
            if milestone.name in self.completed_milestones:
                continue

            # Simple condition checker (could be expanded)
            if self._check_condition(milestone.requirement, stats):
                self.completed_milestones.append(milestone.name)
                if milestone.unlock_game and milestone.unlock_game not in self.games_unlocked:
                    self.games_unlocked.append(milestone.unlock_game)
                return milestone

        return None

    def _check_condition(self, requirement: str, stats: Dict[str, Any]) -> bool:
        """Simple condition checker"""
        # This is a basic implementation - can be enhanced with expression evaluation
        for key, value in stats.items():
            if f"{key} >=" in requirement:
                threshold = float(requirement.split(">=")[1].strip())
                if value >= threshold:
                    return True
        return False


class CompoundRewardsSystem:
    """
    Manages rewards that carry over between games
    XP from simulations boosts compound interest visualization
    """

    def __init__(self):
        self.cross_game_multipliers: Dict[str, float] = {
            # Playing games feeds real simulations
            GameType.PAPER_TRADING.value: 1.0,
            GameType.KAROBAAR.value: 1.0,
            GameType.DALAL_STREET.value: 1.0,
            # Completing simulations boosts other areas
            GameType.COFFEE_SHOP.value: 0.1,  # Coffee shop affects budget
            GameType.BUDGET_BUILDER.value: 0.3,  # Budget affects all games
            GameType.EMERGENCY_FUND.value: 0.25,  # Emergency fund stability
            GameType.COMPOUND_INTEREST.value: 0.5,  # Increases investment growth
        }

    def calculate_compound_bonus(
        self, primary_game: GameType, secondary_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate bonus from other game performance
        e.g., Emergency fund balance boosts stability in paper trading
        """
        bonuses = {
            "stability_bonus": 0.0,
            "capital_boost": 0.0,
            "xp_multiplier": 1.0,
            "insights": [],
        }

        # If user has strong emergency fund, add trading stability
        if secondary_stats.get("emergency_fund_months", 0) >= 3:
            bonuses["stability_bonus"] = 0.1
            bonuses["insights"].append(
                "Strong emergency fund = 10% trading stability boost"
            )

        # If budget score is high, reduce risk in all games
        if secondary_stats.get("budget_score", 0) >= 80:
            bonuses["capital_boost"] = 0.05  # +5% capital
            bonuses["insights"].append(
                "Excellent budgeting = +5% starting capital boost"
            )

        # SIP experience boosts compound interest
        if secondary_stats.get("sip_months", 0) >= 12:
            bonuses["xp_multiplier"] += 0.2
            bonuses["insights"].append(
                "SIP experience = +20% XP in compound interest"
            )

        # Overall XP multiplier
        total_gameplay_hours = secondary_stats.get("total_gameplay_hours", 0)
        if total_gameplay_hours >= 10:
            bonuses["xp_multiplier"] = min(bonuses["xp_multiplier"] * 1.1, 2.0)

        return bonuses

    def transfer_stocks_to_persistent_portfolio(
        self,
        from_game: GameType,
        holdings: Dict[str, Any],
        user_portfolio: PersistentPortfolio,
    ) -> List[str]:
        """Transfer holdings from one game to persistent portfolio"""
        transferred = []
        for symbol, holding in holdings.items():
            if symbol not in user_portfolio.holdings:
                persistent_holding = PersistentHolding(
                    symbol=symbol,
                    quantity=holding.get("quantity", 0),
                    entry_price=holding.get("entry_price", 0),
                    entry_game=from_game,
                    entry_date=datetime.now(),
                    current_price=holding.get("current_price", 0),
                    source_session_id=holding.get("session_id", ""),
                )
                user_portfolio.holdings[symbol] = persistent_holding
                transferred.append(symbol)
        
        user_portfolio.last_updated = datetime.now()
        return transferred

    def get_portfolio_insights(self, portfolio: PersistentPortfolio) -> List[str]:
        """Generate insights about portfolio"""
        insights = []

        total_value = portfolio.get_portfolio_value()
        portfolio_return = portfolio.get_total_return_percentage()

        if total_value > 10000000:
            insights.append("🏆 Elite Portfolio: Over ₹1 Crore invested!")
        elif total_value > 5000000:
            insights.append("💎 Significant Portfolio: Over ₹50 Lakh invested")
        elif total_value > 1000000:
            insights.append("✨ Growing Portfolio: Over ₹10 Lakh invested")

        if portfolio_return > 100:
            insights.append("🚀 Exceptional Returns: Over 100% gain!")
        elif portfolio_return > 50:
            insights.append("📈 Strong Performance: Over 50% return")
        elif portfolio_return > 0:
            insights.append("✅ Positive Returns: Your investments are growing")

        if len(portfolio.holdings) > 10:
            insights.append("🎯 Well Diversified: 10+ holdings")

        if portfolio.total_cash / portfolio.get_portfolio_value() < 0.2:
            insights.append("⚠️ Fully Invested: Less than 20% cash reserves")

        return insights


class CrossGameFeatures:
    """Main orchestrator for cross-game features"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.persistent_portfolio = PersistentPortfolio(user_id=user_id)
        self.career_path = CareerPath(user_id)
        self.compound_rewards = CompoundRewardsSystem()
        self.game_stats: Dict[GameType, Dict[str, Any]] = {}

    def update_game_stats(self, game: GameType, stats: Dict[str, Any]):
        """Update stats for a game"""
        self.game_stats[game] = stats
        self.persistent_portfolio.last_updated = datetime.now()

    def get_career_recommendations(self) -> List[str]:
        """Get personalized career recommendations"""
        recommendations = []

        # Check which games are unlocked
        if GameType.PAPER_TRADING in self.career_path.games_unlocked:
            recommendations.append(
                "🎓 Try Paper Trading - Practice stock market investing risk-free"
            )

        if GameType.DALAL_STREET in self.career_path.games_unlocked:
            recommendations.append(
                "📽️ Explore Dalal Street - Experience Indian stock market through different eras"
            )

        # Career progression insights
        if len(self.career_path.completed_milestones) >= 3:
            recommendations.append(
                "🌟 You're a seasoned player! Try a new game category"
            )

        return recommendations

    def get_cross_game_summary(self) -> Dict[str, Any]:
        """Get comprehensive cross-game summary"""
        return {
            "portfolio_value": self.persistent_portfolio.get_portfolio_value(),
            "total_holdings": len(self.persistent_portfolio.holdings),
            "portfolio_return": self.persistent_portfolio.get_total_return_percentage(),
            "career_milestones_completed": len(self.career_path.completed_milestones),
            "games_unlocked": [g.value for g in self.career_path.games_unlocked],
            "portfolio_insights": self.compound_rewards.get_portfolio_insights(
                self.persistent_portfolio
            ),
            "recommendations": self.get_career_recommendations(),
        }
