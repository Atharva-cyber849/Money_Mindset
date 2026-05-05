"""
Adaptive Difficulty Engine
Manages game difficulty levels, adaptivity, and progression
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class DifficultyLevel(Enum):
    """Game difficulty levels"""
    TUTORIAL = "tutorial"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"


@dataclass
class DifficultyModifiers:
    """Modifiers applied at each difficulty level"""
    level: DifficultyLevel
    market_volatility: float  # % multiplier for price changes
    ai_aggressiveness: float  # 0.0-1.0, how smart AI opponents are
    time_pressure: float  # 0.0-1.0, time limit multiplier
    mistake_tolerance: float  # 0.0-1.0, how forgiving the game is
    xp_multiplier: float  # XP reward multiplier
    hint_availability: bool  # Whether hints/tooltips are shown
    starting_capital_ratio: float  # Multiplier for starting capital
    event_frequency: float  # How often random events occur

    @staticmethod
    def get_modifiers(level: DifficultyLevel) -> 'DifficultyModifiers':
        """Get modifiers for a difficulty level"""
        configs = {
            DifficultyLevel.TUTORIAL: DifficultyModifiers(
                level=DifficultyLevel.TUTORIAL,
                market_volatility=0.3,  # 30% of realistic
                ai_aggressiveness=0.2,
                time_pressure=0.0,  # No time limit
                mistake_tolerance=1.0,  # Very forgiving
                xp_multiplier=0.5,  # Half XP
                hint_availability=True,  # All hints shown
                starting_capital_ratio=1.0,
                event_frequency=0.2,  # Few random events
            ),
            DifficultyLevel.EASY: DifficultyModifiers(
                level=DifficultyLevel.EASY,
                market_volatility=0.6,
                ai_aggressiveness=0.4,
                time_pressure=0.3,
                mistake_tolerance=0.8,
                xp_multiplier=0.75,
                hint_availability=True,
                starting_capital_ratio=1.2,  # +20% capital
                event_frequency=0.4,
            ),
            DifficultyLevel.NORMAL: DifficultyModifiers(
                level=DifficultyLevel.NORMAL,
                market_volatility=1.0,  # Realistic
                ai_aggressiveness=0.6,
                time_pressure=0.6,
                mistake_tolerance=0.6,
                xp_multiplier=1.0,  # Full XP
                hint_availability=False,
                starting_capital_ratio=1.0,
                event_frequency=0.6,
            ),
            DifficultyLevel.HARD: DifficultyModifiers(
                level=DifficultyLevel.HARD,
                market_volatility=1.4,
                ai_aggressiveness=0.85,
                time_pressure=0.85,
                mistake_tolerance=0.4,
                xp_multiplier=1.5,  # 50% bonus XP
                hint_availability=False,
                starting_capital_ratio=0.8,  # -20% capital
                event_frequency=0.8,
            ),
            DifficultyLevel.EXPERT: DifficultyModifiers(
                level=DifficultyLevel.EXPERT,
                market_volatility=1.8,
                ai_aggressiveness=0.95,
                time_pressure=1.0,  # Strict time limits
                mistake_tolerance=0.2,  # Very unforgiving
                xp_multiplier=2.0,  # Double XP
                hint_availability=False,
                starting_capital_ratio=0.5,  # -50% capital
                event_frequency=1.0,  # Frequent events
            ),
        }
        return configs.get(level, configs[DifficultyLevel.NORMAL])


@dataclass
class PerformanceMetrics:
    """Tracks user performance for adaptive difficulty"""
    profit_loss: float  # Net profit/loss
    win_rate: float  # Percentage of successful decisions
    decision_quality: float  # 0.0-1.0 rating of decisions
    speed: float  # Decisions per minute
    accuracy: float  # % of decisions without mistakes
    loss_streak: int  # Consecutive losses
    win_streak: int  # Consecutive wins
    average_session_duration: float  # Minutes


class AdaptiveDifficultyEngine:
    """
    Manages adaptive difficulty based on user performance
    Automatically adjusts game difficulty to maintain engagement
    """

    def __init__(self):
        self.user_difficulty_history: Dict[str, List[Dict]] = {}
        self.performance_thresholds = {
            "excellent": 0.85,  # Suggest harder difficulty
            "good": 0.70,
            "average": 0.50,
            "poor": 0.30,  # Suggest easier difficulty
        }

    def calculate_performance_score(self, metrics: PerformanceMetrics) -> float:
        """Calculate overall performance (0.0-1.0)"""
        score = (
            (metrics.win_rate * 0.3) +  # Decision quality weight
            (metrics.accuracy * 0.3) +  # Accuracy weight
            (max(0, metrics.profit_loss / 1000) * 0.2) +  # Profitability (capped)
            (min(metrics.speed / 5, 1.0) * 0.2)  # Speed (0-5 decisions/min baseline)
        )
        return min(max(score, 0.0), 1.0)

    def recommend_difficulty(
        self,
        current_difficulty: DifficultyLevel,
        performance_score: float,
        session_count: int,
    ) -> DifficultyLevel:
        """Recommend difficulty based on performance"""
        
        # Need at least 2 sessions in a difficulty before recommending change
        if session_count < 2:
            return current_difficulty

        if performance_score >= self.performance_thresholds["excellent"]:
            # Step up difficulty
            progression = [
                DifficultyLevel.TUTORIAL,
                DifficultyLevel.EASY,
                DifficultyLevel.NORMAL,
                DifficultyLevel.HARD,
                DifficultyLevel.EXPERT,
            ]
            current_idx = progression.index(current_difficulty)
            if current_idx < len(progression) - 1:
                return progression[current_idx + 1]

        elif performance_score <= self.performance_thresholds["poor"]:
            # Step down difficulty
            progression = [
                DifficultyLevel.TUTORIAL,
                DifficultyLevel.EASY,
                DifficultyLevel.NORMAL,
                DifficultyLevel.HARD,
                DifficultyLevel.EXPERT,
            ]
            current_idx = progression.index(current_difficulty)
            if current_idx > 0:
                return progression[current_idx - 1]

        return current_difficulty

    def get_dynamic_parameters(
        self,
        difficulty: DifficultyLevel,
        session_count: int,
        recent_performance: Optional[float] = None,
    ) -> DifficultyModifiers:
        """Get difficulty parameters with optional performance-based tweaks"""
        modifiers = DifficultyModifiers.get_modifiers(difficulty)

        # Micro-adjustments based on recent performance
        if recent_performance is not None:
            if recent_performance > 0.9:
                # User dominating, increase difficulty slightly
                modifiers.market_volatility *= 1.1
                modifiers.ai_aggressiveness *= 1.1
                modifiers.time_pressure *= 1.05
            elif recent_performance < 0.4:
                # User struggling, decrease difficulty slightly
                modifiers.market_volatility *= 0.9
                modifiers.ai_aggressiveness *= 0.85
                modifiers.time_pressure *= 0.8

        return modifiers

    def get_tutorial_content(self, game_type: str) -> Dict[str, Any]:
        """Get tutorial steps for game"""
        tutorials = {
            "paper_trading": {
                "steps": [
                    {
                        "title": "Welcome to Paper Trading",
                        "content": "Learn stock trading risk-free with virtual money!",
                        "hint": "You have ₹10,00,000 (10 lakhs) to invest.",
                    },
                    {
                        "title": "Buying Stocks",
                        "content": "Click 'Buy' to purchase shares of a company.",
                        "hint": "Lower prices = more shares you can buy",
                    },
                    {
                        "title": "Selling Stocks",
                        "content": "Click 'Sell' to make a profit. Watch for price increases!",
                        "hint": "Sell high to make profit = (sell price - buy price) × quantity",
                    },
                    {
                        "title": "Portfolio View",
                        "content": "Track all your holdings and their performance.",
                        "hint": "Green = profit, Red = loss",
                    },
                ],
                "max_trades_per_session": 50,
                "starting_capital": 1000000,
            },
            "dalal_street": {
                "steps": [
                    {
                        "title": "Dalal Street Eras",
                        "content": "Each era has different eras (1980s, 2000s, 2020s) with unique market conditions.",
                        "hint": "Choose an era that interests you!",
                    },
                    {
                        "title": "Economic News",
                        "content": "News events happen each quarter. They affect stock prices!",
                        "hint": "Positive news = stock prices rise, Negative news = stock prices fall",
                    },
                    {
                        "title": "Strategic Trading",
                        "content": "Use news predictions to make profitable trades.",
                        "hint": "Buy before good news, sell before bad news",
                    },
                    {
                        "title": "Long-term Growth",
                        "content": "Play through 10+ quarters to see portfolio growth.",
                        "hint": "Average ₹50,000 profit per era for good players!",
                    },
                ],
                "max_trades_per_session": 30,
                "starting_capital": 500000,
            },
            "karobaar": {
                "steps": [
                    {
                        "title": "Choose Your Path",
                        "content": "Decide your business path: small shop, online store, or manufacturing.",
                        "hint": "Each path has different risk/reward profiles",
                    },
                    {
                        "title": "Daily Decisions",
                        "content": "Make decisions on inventory, pricing, and marketing.",
                        "hint": "Balance growth with profitability",
                    },
                    {
                        "title": "Seasonal Changes",
                        "content": "Different seasons affect demand and costs.",
                        "hint": "Plan ahead for peak and off seasons!",
                    },
                    {
                        "title": "Expand Your Business",
                        "content": "Reinvest profits to expand and scale up.",
                        "hint": "Target ₹10 lakh revenue in 4 years!",
                    },
                ],
                "max_decisions_per_session": 20,
                "starting_capital": 100000,
            },
        }
        return tutorials.get(game_type, {})
