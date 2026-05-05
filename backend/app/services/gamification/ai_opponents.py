"""
AI Opponents System
Manages AI competitors for Karobaar (business) and Dalal Street (trading)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random


class AIPersonality(Enum):
    """AI opponent personality types"""
    AGGRESSIVE = "aggressive"  # High risk, fast expansion
    CONSERVATIVE = "conservative"  # Low risk, steady growth
    BALANCED = "balanced"  # Medium risk, steady growth
    OPPORTUNIST = "opportunist"  # Adapts to market conditions
    DEFENSIVE = "defensive"  # Protects position


class AICompetitor:
    """Single AI competitor"""

    def __init__(
        self,
        ai_id: str,
        name: str,
        personality: AIPersonality,
        skill_level: float = 0.7,  # 0.0-1.0
    ):
        self.ai_id = ai_id
        self.name = name
        self.personality = personality
        self.skill_level = skill_level
        self.capital = 0.0
        self.portfolio: Dict[str, float] = {}
        self.decisions: List[Dict] = []
        self.morale = 0.7  # Affects decision quality
        self.market_knowledge = skill_level

    def make_decision(self, game_state: Dict, current_price: Optional[float] = None) -> Dict:
        """Make a decision based on personality and game state"""
        decision = {
            "action": "hold",
            "amount": 0.0,
            "confidence": self.morale,
            "reasoning": "",
        }

        # Apply personality-based logic
        if self.personality == AIPersonality.AGGRESSIVE:
            decision = self._aggressive_decision(game_state, current_price)
        elif self.personality == AIPersonality.CONSERVATIVE:
            decision = self._conservative_decision(game_state, current_price)
        elif self.personality == AIPersonality.BALANCED:
            decision = self._balanced_decision(game_state, current_price)
        elif self.personality == AIPersonality.OPPORTUNIST:
            decision = self._opportunist_decision(game_state, current_price)
        elif self.personality == AIPersonality.DEFENSIVE:
            decision = self._defensive_decision(game_state, current_price)

        # Add some randomness based on skill
        if random.random() > self.skill_level:
            # Make a random/poor decision occasionally
            decision["action"] = random.choice(["buy", "sell", "hold"])
            decision["confidence"] *= 0.5

        self.decisions.append(decision)
        return decision

    def _aggressive_decision(self, game_state: Dict, current_price: Optional[float]) -> Dict:
        """Aggressive AI - takes higher risks"""
        market_trend = game_state.get("market_trend", 0)

        if market_trend > 0:
            # Bullish - go all in
            return {
                "action": "buy",
                "amount": self.capital * 0.8,
                "confidence": self.morale * 1.2,
                "reasoning": "Market is bullish, buying aggressively",
            }
        elif market_trend < -0.3:
            # Very bearish - sell everything
            return {
                "action": "sell_all",
                "amount": sum(self.portfolio.values()),
                "confidence": 0.9,
                "reasoning": "Market crashing, selling to minimize losses",
            }
        else:
            # Neutral - check for opportunities
            if self.capital > 100000:
                return {
                    "action": "buy",
                    "amount": random.uniform(50000, self.capital * 0.5),
                    "confidence": self.morale,
                    "reasoning": "Good capital, looking for opportunities",
                }

        return {"action": "hold", "amount": 0, "confidence": self.morale, "reasoning": ""}

    def _conservative_decision(self, game_state: Dict, current_price: Optional[float]) -> Dict:
        """Conservative AI - plays it safe"""
        market_trend = game_state.get("market_trend", 0)

        if market_trend > 0.5:
            # Strongly bullish - buy carefully
            return {
                "action": "buy",
                "amount": self.capital * 0.2,
                "confidence": self.morale * 0.8,
                "reasoning": "Moderate bullish signal, buying conservatively",
            }
        elif market_trend < -0.2:
            # Bearish - sell part of portfolio
            return {
                "action": "sell",
                "amount": sum(self.portfolio.values()) * 0.3,
                "confidence": 0.7,
                "reasoning": "Bearish trend detected, reducing exposure",
            }

        return {
            "action": "hold",
            "amount": 0,
            "confidence": 0.5,
            "reasoning": "Market unclear, maintaining position",
        }

    def _balanced_decision(self, game_state: Dict, current_price: Optional[float]) -> Dict:
        """Balanced AI - moderate approach"""
        market_trend = game_state.get("market_trend", 0)
        capital_ratio = self.capital / game_state.get("max_capital", 100000)

        if market_trend > 0.2 and capital_ratio > 0.3:
            return {
                "action": "buy",
                "amount": self.capital * 0.3,
                "confidence": self.morale,
                "reasoning": "Slight bullish trend, balanced buy",
            }
        elif market_trend < -0.1 and capital_ratio < 0.5:
            return {
                "action": "sell",
                "amount": sum(self.portfolio.values()) * 0.2,
                "confidence": 0.6,
                "reasoning": "Limited downside risk, tactical sell",
            }

        return {"action": "hold", "amount": 0, "confidence": self.morale, "reasoning": ""}

    def _opportunist_decision(self, game_state: Dict, current_price: Optional[float]) -> Dict:
        """Opportunist AI - adapts to conditions"""
        volatility = game_state.get("volatility", 0.5)

        # High volatility = opportunity
        if volatility > 0.8 and current_price:
            # Buy dips
            if random.random() < 0.6:
                return {
                    "action": "buy",
                    "amount": self.capital * 0.4,
                    "confidence": self.morale * 1.1,
                    "reasoning": "High volatility = opportunity to buy",
                }

        # Momentum trading
        momentum = game_state.get("momentum", 0)
        if abs(momentum) > 0.5:
            return {
                "action": "buy" if momentum > 0 else "sell",
                "amount": self.capital * 0.3,
                "confidence": self.morale,
                "reasoning": f"Strong momentum signal, {momentum}",
            }

        return {"action": "hold", "amount": 0, "confidence": self.morale, "reasoning": ""}

    def _defensive_decision(self, game_state: Dict, current_price: Optional[float]) -> Dict:
        """Defensive AI - protects existing position"""
        portfolio_value = sum(self.portfolio.values())

        if portfolio_value > self.capital * 0.8:
            # Have strong position - protect it
            return {
                "action": "hold",
                "amount": 0,
                "confidence": 0.8,
                "reasoning": "Protecting strong position",
            }
        elif game_state.get("market_trend", 0) < 0:
            # Market down - defend aggressively
            return {
                "action": "sell",
                "amount": sum(self.portfolio.values()) * 0.5,
                "confidence": 0.9,
                "reasoning": "Market downturn, defending position",
            }

        return {"action": "hold", "amount": 0, "confidence": 0.7, "reasoning": ""}

    def update_morale(self, recent_performance: float):
        """Update morale based on performance"""
        # recent_performance: -1.0 (bad) to 1.0 (good)
        self.morale = max(0.1, min(1.0, self.morale + (recent_performance * 0.1)))


@dataclass
class CompetitionRound:
    """Single round of competition"""
    round_number: int
    competitors: List[AICompetitor]
    scores: Dict[str, float]  # ai_id -> score
    winner: Optional[str] = None
    human_player_score: float = 0.0


class AICompetitionEngine:
    """Manages AI competitors and competition mechanics"""

    # Predefined AI opponents
    PREDEFINED_AIS = [
        AICompetitor("ai_1", "Rakesh (Aggressive Trader)", AIPersonality.AGGRESSIVE, 0.8),
        AICompetitor("ai_2", "Priya (Conservative Mentor)", AIPersonality.CONSERVATIVE, 0.9),
        AICompetitor("ai_3", "Vijay (Balanced Pro)", AIPersonality.BALANCED, 0.85),
        AICompetitor("ai_4", "Shreya (Market Expert)", AIPersonality.OPPORTUNIST, 0.95),
        AICompetitor("ai_5", "Arjun (Defensive Guard)", AIPersonality.DEFENSIVE, 0.75),
    ]

    def __init__(self):
        self.active_competitions: Dict[str, CompetitionRound] = {}
        self.ai_stats: Dict[str, Dict] = {}

    def start_competition(
        self,
        competition_id: str,
        game_type: str,
        difficulty: str,
        player_count: int = 3,
    ) -> List[AICompetitor]:
        """Start a new competition with AI opponents"""
        # Select AIs based on difficulty
        if difficulty == "easy":
            selected_ais = [
                AICompetitor("ai_easy_1", "Novice Trader", AIPersonality.CONSERVATIVE, 0.4),
                AICompetitor("ai_easy_2", "Learning Investor", AIPersonality.CONSERVATIVE, 0.5),
            ]
        elif difficulty == "hard":
            selected_ais = [
                AICompetitor("ai_hard_1", "Expert Trader", AIPersonality.OPPORTUNIST, 0.95),
                AICompetitor("ai_hard_2", "Master Strategist", AIPersonality.BALANCED, 0.9),
                AICompetitor("ai_hard_3", "Market Wizard", AIPersonality.AGGRESSIVE, 0.9),
            ]
        else:  # normal
            selected_ais = random.sample(self.PREDEFINED_AIS, min(player_count, len(self.PREDEFINED_AIS)))

        round_obj = CompetitionRound(
            round_number=1,
            competitors=selected_ais,
            scores={ai.ai_id: 0.0 for ai in selected_ais},
        )

        self.active_competitions[competition_id] = round_obj
        return selected_ais

    def get_competitor_stats(self, competitor_id: str) -> Dict:
        """Get stats for a specific competitor"""
        if competitor_id not in self.ai_stats:
            self.ai_stats[competitor_id] = {
                "wins": 0,
                "losses": 0,
                "total_score": 0.0,
                "avg_score": 0.0,
                "games_played": 0,
            }
        return self.ai_stats[competitor_id]

    def get_leaderboard(self) -> List[Dict]:
        """Get AI leaderboard"""
        leaderboard = []
        for ai in self.PREDEFINED_AIS:
            stats = self.get_competitor_stats(ai.ai_id)
            leaderboard.append(
                {
                    "name": ai.name,
                    "wins": stats["wins"],
                    "games_played": stats["games_played"],
                    "win_rate": (
                        stats["wins"] / stats["games_played"]
                        if stats["games_played"] > 0
                        else 0
                    ),
                    "avg_score": stats["avg_score"],
                    "personality": ai.personality.value,
                }
            )

        return sorted(leaderboard, key=lambda x: x["win_rate"], reverse=True)

    def simulate_round(
        self,
        competition_id: str,
        game_state: Dict,
        initial_capital: float = 1000000,
    ) -> Dict:
        """Simulate one round of competition"""
        if competition_id not in self.active_competitions:
            return {"error": "Competition not found"}

        competition = self.active_competitions[competition_id]

        round_results = {
            "round_number": competition.round_number,
            "game_state": game_state,
            "decisions": {},
        }

        for ai in competition.competitors:
            if ai.capital == 0:
                ai.capital = initial_capital * (0.8 + random.random() * 0.4)  # Random variation

            decision = ai.make_decision(game_state)
            round_results["decisions"][ai.ai_id] = decision

        competition.round_number += 1
        return round_results

    def end_competition(
        self,
        competition_id: str,
        player_final_score: float,
        player_rank: int,
        total_players: int,
    ) -> Dict:
        """End competition and determine winner"""
        if competition_id not in self.active_competitions:
            return {"error": "Competition not found"}

        competition = self.active_competitions[competition_id]

        # Determine winner
        if player_rank == 1:
            result = "🏆 You won the competition!"
            bonus_xp = 1000
        elif player_rank <= total_players // 2:
            result = "✨ Great performance! Top half finish"
            bonus_xp = 500
        else:
            result = "📈 Good effort! Better luck next time"
            bonus_xp = 200

        return {
            "competition_id": competition_id,
            "result": result,
            "player_rank": player_rank,
            "player_score": player_final_score,
            "total_competitors": total_players,
            "bonus_xp": bonus_xp,
            "leaderboard": self.get_leaderboard(),
        }
