"""
Streak & Daily Bonus System
Manages daily login streaks, consecutive plays, and bonus rewards
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from enum import Enum


class StreakType(Enum):
    """Types of streaks tracked"""
    DAILY_LOGIN = "daily_login"  # Consecutive days logging in
    SIMULATION_PLAYS = "simulation_plays"  # Consecutive day with ≥1 simulation
    GAME_PLAYS = "game_plays"  # Consecutive day with ≥1 game
    ACHIEVEMENT_UNLOCKS = "achievement_unlocks"  # Days with new achievements


@dataclass
class StreakBonus:
    """Bonus rewards for maintaining streaks"""
    streak_day: int  # Which day of streak (1, 2, 3, etc.)
    bonus_xp: int  # Bonus XP for this day
    bonus_description: str
    milestone_bonus: Optional[Dict] = None  # Special rewards at milestones (day 7, 14, 30, etc.)


class StreakConfiguration:
    """Configuration for streak rewards"""

    # Bonus XP tables
    XP_BONUSES = {
        1: StreakBonus(1, 25, "Getting started! +25 XP", None),
        2: StreakBonus(2, 50, "Building momentum! +50 XP", None),
        3: StreakBonus(3, 75, "On a roll! +75 XP", None),
        4: StreakBonus(4, 100, "Unstoppable! +100 XP", None),
        5: StreakBonus(5, 125, "Legend status! +125 XP", None),
        6: StreakBonus(6, 150, "Almost a week! +150 XP", None),
        7: StreakBonus(
            7,
            250,
            "1-WEEK STREAK! +250 XP",
            {
                "badge": "week_warrior",
                "badge_name": "7-Day Warrior",
                "bonus_xp": 250,
            },
        ),
        14: StreakBonus(
            14,
            500,
            "2-WEEK STREAK! +500 XP",
            {
                "badge": "fortnight_master",
                "badge_name": "Fortnight Master",
                "bonus_xp": 500,
            },
        ),
        30: StreakBonus(
            30,
            1000,
            "MONTHLY CHAMPION! +1000 XP",
            {
                "badge": "monthly_legend",
                "badge_name": "Monthly Legend",
                "bonus_xp": 1000,
                "unlock_item": "exclusive_game",
            },
        ),
        100: StreakBonus(
            100,
            5000,
            "CENTURY ACHIEVED! +5000 XP",
            {
                "badge": "streak_god",
                "badge_name": "Streak God (100 Days)",
                "bonus_xp": 5000,
                "unlock_item": "exclusive_profile_frame",
            },
        ),
    }

    # Multipliers for different streak types
    MULTIPLIERS = {
        StreakType.DAILY_LOGIN: 1.0,
        StreakType.SIMULATION_PLAYS: 1.2,  # 20% bonus for simulations
        StreakType.GAME_PLAYS: 1.3,  # 30% bonus for games
        StreakType.ACHIEVEMENT_UNLOCKS: 2.0,  # 100% bonus for achievements
    }


@dataclass
class UserStreak:
    """User's current streak data"""
    user_id: str
    streak_type: StreakType
    current_streak: int  # Consecutive days
    longest_streak: int  # All-time record
    last_activity_date: date  # Last date streak was active
    total_streak_days: int  # Total days ever in this streak (including broken streaks)
    milestones_reached: List[int] = field(default_factory=list)  # [7, 14, 30, etc.]
    total_bonus_xp_earned: int = 0  # Cumulative XP from streaks

    def is_active_today(self) -> bool:
        """Check if streak is still active today"""
        today = date.today()
        # Streak breaks if user didn't play yesterday or today
        yesterday = today - timedelta(days=1)
        return self.last_activity_date in [today, yesterday]

    def reset_if_needed(self) -> bool:
        """Reset streak if it broke. Returns True if reset occurred."""
        if not self.is_active_today() and self.current_streak > 0:
            # Streak is broken
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            self.current_streak = 0
            return True
        return False


class DailyBonusSystem:
    """
    Manages daily login bonuses, consecutive play streaks, and rewards
    """

    def __init__(self):
        self.user_streaks: Dict[str, Dict[str, UserStreak]] = {}  # user_id -> {streak_type -> UserStreak}
        self.daily_login_bonus: Dict[str, datetime] = {}  # user_id -> last login datetime

    def record_activity(
        self,
        user_id: str,
        activity_type: str,  # "login", "simulation_play", "game_play", "achievement_unlock"
        game_type: Optional[str] = None,  # "paper_trading", "dalal_street", "karobaar", etc.
    ) -> Dict[str, int]:
        """
        Record user activity and calculate streak bonuses

        Returns:
            {'base_xp': int, 'streak_bonus_xp': int, 'multiplier': float, 'milestone': bool}
        """
        today = date.today()
        result = {
            "base_xp": 0,
            "streak_bonus_xp": 0,
            "multiplier": 1.0,
            "milestone_reached": None,
            "new_milestone": False,
        }

        # Initialize user streaks if needed
        if user_id not in self.user_streaks:
            self.user_streaks[user_id] = {}
            for streak_type in StreakType:
                self.user_streaks[user_id][streak_type.value] = UserStreak(
                    user_id=user_id,
                    streak_type=streak_type,
                    current_streak=0,
                    longest_streak=0,
                    last_activity_date=today - timedelta(days=1),  # Will activate today
                    total_streak_days=0,
                )

        # Determine streak type based on activity
        streak_type_map = {
            "login": StreakType.DAILY_LOGIN.value,
            "simulation_play": StreakType.SIMULATION_PLAYS.value,
            "game_play": StreakType.GAME_PLAYS.value,
            "achievement_unlock": StreakType.ACHIEVEMENT_UNLOCKS.value,
        }
        streak_key = streak_type_map.get(activity_type, StreakType.DAILY_LOGIN.value)
        streak = self.user_streaks[user_id][streak_key]

        # Check if streak is broken
        streak.reset_if_needed()

        # Update streak if not already updated today
        if streak.last_activity_date != today:
            streak.current_streak += 1
            streak.total_streak_days += 1
            streak.last_activity_date = today

            # Check for milestone
            if streak.current_streak in StreakConfiguration.XP_BONUSES:
                bonus_config = StreakConfiguration.XP_BONUSES[streak.current_streak]
                result["streak_bonus_xp"] = bonus_config.bonus_xp
                result["milestone_reached"] = bonus_config
                if bonus_config.milestone_bonus:
                    result["new_milestone"] = True
                    streak.milestones_reached.append(streak.current_streak)
            else:
                # Default bonus for continuing streaks
                if streak.current_streak <= 6:
                    result["streak_bonus_xp"] = streak.current_streak * 25
                else:
                    result["streak_bonus_xp"] = 150 + ((streak.current_streak - 6) * 10)

            streak.total_bonus_xp_earned += result["streak_bonus_xp"]

        # Apply multiplier for streak type
        streak_enum = StreakType(streak_key)
        result["multiplier"] = StreakConfiguration.MULTIPLIERS.get(
            streak_enum, 1.0
        )

        return result

    def get_user_total_streaks(self, user_id: str) -> Dict[str, Dict]:
        """Get all streaks for a user"""
        if user_id not in self.user_streaks:
            return {}

        result = {}
        for streak_key, streak in self.user_streaks[user_id].items():
            streak.reset_if_needed()
            result[streak_key] = {
                "current_streak": streak.current_streak,
                "longest_streak": streak.longest_streak,
                "is_active": streak.is_active_today(),
                "last_activity": streak.last_activity_date.isoformat(),
                "milestones": streak.milestones_reached,
                "total_bonus_xp": streak.total_bonus_xp_earned,
            }
        return result

    def get_next_milestone(self, user_id: str, streak_type: str) -> Optional[Dict]:
        """Get next milestone info for a streak"""
        if user_id not in self.user_streaks:
            return None

        streak = self.user_streaks[user_id].get(streak_type)
        if not streak:
            return None

        current = streak.current_streak

        # Find next milestone
        milestones = sorted(StreakConfiguration.XP_BONUSES.keys())
        for milestone in milestones:
            if milestone > current:
                days_until = milestone - current
                bonus_config = StreakConfiguration.XP_BONUSES[milestone]
                return {
                    "milestone_day": milestone,
                    "days_until": days_until,
                    "bonus_xp": bonus_config.bonus_xp,
                    "description": bonus_config.bonus_description,
                    "has_special_reward": bonus_config.milestone_bonus is not None,
                }

        return None

    def get_daily_login_bonus(self, user_id: str) -> Dict[str, int]:
        """Get today's login bonus"""
        today = date.today()
        last_login = self.daily_login_bonus.get(user_id)

        # Check if already claimed today
        if last_login and last_login.date() == today:
            return {
                "bonus_xp": 0,
                "reason": "Already claimed today",
                "can_claim": False,
            }

        # Record login
        self.daily_login_bonus[user_id] = datetime.now()
        activity_result = self.record_activity(user_id, "login")

        return {
            "bonus_xp": activity_result["streak_bonus_xp"],
            "current_streak": self.user_streaks[user_id][StreakType.DAILY_LOGIN.value].current_streak,
            "reason": "Daily login bonus",
            "can_claim": True,
            "milestone": activity_result.get("milestone_reached"),
        }

    def get_seasonal_bonus(self, user_id: str, event_name: str) -> Dict[str, int]:
        """Get bonus for seasonal events"""
        today = date.today()
        month = today.month

        seasonal_events = {
            "diwali_race": {
                "months": [10, 11],  # October-November
                "base_bonus": 500,
                "description": "Diwali Savings Race - Save smart for the festival!",
            },
            "tax_season": {
                "months": [3, 4],  # March-April
                "base_bonus": 400,
                "description": "Tax Planning Challenge - Optimize your taxes!",
            },
            "new_year_resolution": {
                "months": [1],
                "base_bonus": 300,
                "description": "New Year Resolution - Set financial goals!",
            },
            "summer_challenge": {
                "months": [5, 6],
                "base_bonus": 250,
                "description": "Summer Challenge - Build good habits!",
            },
        }

        event = seasonal_events.get(event_name, {})
        if month in event.get("months", []):
            return {
                "event_active": True,
                "bonus_xp": event.get("base_bonus", 0),
                "description": event.get("description", ""),
            }

        return {
            "event_active": False,
            "bonus_xp": 0,
            "description": f"{event_name} is not active this month",
        }
