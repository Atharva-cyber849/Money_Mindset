"""
Progress Tracker - XP, Levels, and User Progression
Manages user leveling, XP calculations, and progress milestones
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime, timedelta


class Level(Enum):
    """User progression levels"""
    FINANCIAL_NEWBIE = 1
    MONEY_APPRENTICE = 2
    BUDGET_WARRIOR = 3
    WEALTH_BUILDER = 4
    INVESTMENT_GURU = 5
    FINANCIAL_MASTER = 6


@dataclass
class LevelInfo:
    """Information about a level"""
    level: Level
    name: str
    xp_required: int
    xp_range: tuple  # (min, max)
    description: str
    perks: List[str]
    icon: str


@dataclass
class XPReward:
    """XP reward for an action"""
    action: str
    base_xp: int
    bonus_multiplier: float
    total_xp: int
    reason: str


@dataclass
class ProgressSnapshot:
    """User's current progress state"""
    user_id: int
    current_level: Level
    current_xp: int
    xp_to_next_level: int
    progress_percentage: float
    total_simulations_completed: int
    total_badges_earned: int
    current_streak: int
    longest_streak: int
    last_activity_date: datetime
    total_xp_earned: int
    next_level_info: Optional[LevelInfo]


class ProgressTracker:
    """
    Manages user progression through the financial learning journey
    """
    
    # XP requirements for each level
    LEVEL_REQUIREMENTS = {
        Level.FINANCIAL_NEWBIE: LevelInfo(
            level=Level.FINANCIAL_NEWBIE,
            name="Financial Newbie",
            xp_required=0,
            xp_range=(0, 999),
            description="Just starting your financial journey. Every expert was once a beginner!",
            perks=["Access to Level 1 simulations", "Basic progress tracking"],
            icon="🌱"
        ),
        Level.MONEY_APPRENTICE: LevelInfo(
            level=Level.MONEY_APPRENTICE,
            name="Money Apprentice",
            xp_required=1000,
            xp_range=(1000, 2999),
            description="You're learning the basics! Budget creation and emergency funds unlocked.",
            perks=["Access to Level 2 simulations", "Debt analysis tools", "Budget templates"],
            icon="📚"
        ),
        Level.BUDGET_WARRIOR: LevelInfo(
            level=Level.BUDGET_WARRIOR,
            name="Budget Warrior",
            xp_required=3000,
            xp_range=(3000, 6999),
            description="Master of budgets and debt strategies. You're building a solid foundation!",
            perks=["Access to Level 3 simulations", "Investment basics", "AI Tutor priority access"],
            icon="⚔️"
        ),
        Level.WEALTH_BUILDER: LevelInfo(
            level=Level.WEALTH_BUILDER,
            name="Wealth Builder",
            xp_required=7000,
            xp_range=(7000, 12999),
            description="Building real wealth through investments and smart decisions.",
            perks=["Access to Level 4 simulations", "Advanced investment strategies", "Tax optimization"],
            icon="🏗️"
        ),
        Level.INVESTMENT_GURU: LevelInfo(
            level=Level.INVESTMENT_GURU,
            name="Investment Guru",
            xp_required=13000,
            xp_range=(13000, 19999),
            description="You understand compound interest, index funds, and long-term thinking.",
            perks=["All simulations unlocked", "Monte Carlo analysis", "Portfolio optimization"],
            icon="🧙"
        ),
        Level.FINANCIAL_MASTER: LevelInfo(
            level=Level.FINANCIAL_MASTER,
            name="Financial Master",
            xp_required=20000,
            xp_range=(20000, 999999),
            description="Master of money! You've completed the journey and achieved financial wisdom.",
            perks=["Master badge", "All features unlocked", "Mentor status", "Exclusive insights"],
            icon="👑"
        )
    }
    
    # XP rewards for different actions
    XP_REWARDS = {
        # Simulations (Base XP)
        "coffee_shop_effect": 100,
        "paycheck_game": 200,
        "budget_builder": 300,
        "emergency_fund": 300,
        "credit_card_trap": 250,
        "debt_classification": 250,
        "compound_interest": 400,
        "risk_vs_reward": 400,
        "index_fund_challenge": 500,
        "monte_carlo": 600,
        "tax_optimizer": 500,
        "sarah_journey": 800,  # Complete journey
        
        # Activities
        "daily_login": 10,
        "first_simulation": 50,
        "ai_tutor_question": 20,
        "budget_created": 100,
        "goal_created": 50,
        "goal_completed": 200,
        "streak_3_days": 50,
        "streak_7_days": 150,
        "streak_30_days": 500,
        "profile_complete": 100,
        "share_achievement": 25,
    }
    
    # Bonus multipliers
    STREAK_BONUS = {
        3: 1.1,   # 10% bonus for 3-day streak
        7: 1.25,  # 25% bonus for 7-day streak
        14: 1.5,  # 50% bonus for 14-day streak
        30: 2.0,  # 100% bonus for 30-day streak
    }
    
    PERFECT_SCORE_BONUS = 1.5  # 50% bonus for perfect simulation scores
    FIRST_TRY_BONUS = 1.2      # 20% bonus for completing on first try
    
    def __init__(self):
        """Initialize progress tracker"""
        pass
    
    def calculate_xp_reward(
        self,
        action: str,
        current_streak: int = 0,
        perfect_score: bool = False,
        first_try: bool = False,
        custom_multiplier: float = 1.0
    ) -> XPReward:
        """
        Calculate XP reward with bonuses
        
        Args:
            action: Action that earned XP
            current_streak: Current daily streak
            perfect_score: Whether user got perfect score
            first_try: Whether completed on first try
            custom_multiplier: Additional custom multiplier
        
        Returns:
            XPReward with breakdown
        """
        base_xp = self.XP_REWARDS.get(action, 0)
        
        if base_xp == 0:
            return XPReward(
                action=action,
                base_xp=0,
                bonus_multiplier=1.0,
                total_xp=0,
                reason="Unknown action"
            )
        
        # Calculate bonus multiplier
        multiplier = custom_multiplier
        bonus_reasons = []
        
        # Streak bonus
        streak_bonus = 1.0
        for days, bonus in sorted(self.STREAK_BONUS.items(), reverse=True):
            if current_streak >= days:
                streak_bonus = bonus
                bonus_reasons.append(f"{days}-day streak")
                break
        multiplier *= streak_bonus
        
        # Perfect score bonus
        if perfect_score:
            multiplier *= self.PERFECT_SCORE_BONUS
            bonus_reasons.append("perfect score")
        
        # First try bonus
        if first_try:
            multiplier *= self.FIRST_TRY_BONUS
            bonus_reasons.append("first try")
        
        total_xp = int(base_xp * multiplier)
        
        reason_text = f"Base {base_xp} XP"
        if bonus_reasons:
            reason_text += f" + bonuses ({', '.join(bonus_reasons)})"
        
        return XPReward(
            action=action,
            base_xp=base_xp,
            bonus_multiplier=multiplier,
            total_xp=total_xp,
            reason=reason_text
        )
    
    def get_level_from_xp(self, total_xp: int) -> Level:
        """Determine level based on total XP"""
        for level in reversed(list(Level)):
            level_info = self.LEVEL_REQUIREMENTS[level]
            if total_xp >= level_info.xp_required:
                return level
        return Level.FINANCIAL_NEWBIE
    
    def get_level_info(self, level: Level) -> LevelInfo:
        """Get information about a level"""
        return self.LEVEL_REQUIREMENTS[level]
    
    def get_next_level_info(self, current_level: Level) -> Optional[LevelInfo]:
        """Get information about next level"""
        current_value = current_level.value
        if current_value < len(Level):
            next_level = Level(current_value + 1)
            return self.LEVEL_REQUIREMENTS[next_level]
        return None
    
    def calculate_progress_to_next_level(
        self,
        current_xp: int,
        current_level: Level
    ) -> Dict:
        """Calculate progress to next level"""
        current_level_info = self.LEVEL_REQUIREMENTS[current_level]
        next_level_info = self.get_next_level_info(current_level)
        
        if not next_level_info:
            # Max level reached
            return {
                "at_max_level": True,
                "current_xp": current_xp,
                "xp_to_next": 0,
                "progress_percentage": 100.0
            }
        
        # XP needed for next level
        xp_to_next = next_level_info.xp_required - current_xp
        
        # Progress percentage within current level
        level_xp_range = current_level_info.xp_range[1] - current_level_info.xp_range[0]
        xp_within_level = current_xp - current_level_info.xp_range[0]
        progress_percentage = (xp_within_level / level_xp_range) * 100 if level_xp_range > 0 else 0
        
        return {
            "at_max_level": False,
            "current_xp": current_xp,
            "xp_to_next": xp_to_next,
            "progress_percentage": min(progress_percentage, 100.0),
            "next_level": next_level_info
        }
    
    def check_level_up(
        self,
        old_xp: int,
        new_xp: int
    ) -> Dict:
        """
        Check if user leveled up
        
        Returns:
            Dict with level_up status and new level info
        """
        old_level = self.get_level_from_xp(old_xp)
        new_level = self.get_level_from_xp(new_xp)
        
        if new_level.value > old_level.value:
            return {
                "leveled_up": True,
                "old_level": old_level,
                "new_level": new_level,
                "new_level_info": self.LEVEL_REQUIREMENTS[new_level],
                "celebration_message": self._generate_level_up_message(new_level)
            }
        
        return {
            "leveled_up": False,
            "old_level": old_level,
            "new_level": old_level
        }
    
    def _generate_level_up_message(self, new_level: Level) -> str:
        """Generate celebration message for level up"""
        level_info = self.LEVEL_REQUIREMENTS[new_level]
        
        messages = {
            Level.MONEY_APPRENTICE: "🎉 You're no longer a newbie! You've learned the basics of budgeting and saving.",
            Level.BUDGET_WARRIOR: "⚔️ Budget Warrior unlocked! You're mastering debt management and financial planning.",
            Level.WEALTH_BUILDER: "🏗️ You're building real wealth! Investment strategies unlocked.",
            Level.INVESTMENT_GURU: "🧙 Investment Guru achieved! You understand the power of compound interest.",
            Level.FINANCIAL_MASTER: "👑 FINANCIAL MASTER! You've reached the pinnacle of financial wisdom!"
        }
        
        return messages.get(new_level, f"{level_info.icon} Level up! Welcome to {level_info.name}!")
    
    def calculate_streak(
        self,
        last_activity_date: Optional[datetime],
        current_date: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate current streak
        
        Args:
            last_activity_date: Last time user was active
            current_date: Current date (defaults to now)
        
        Returns:
            Streak information
        """
        if current_date is None:
            current_date = datetime.now()
        
        if last_activity_date is None:
            return {
                "current_streak": 1,
                "streak_active": True,
                "streak_broken": False,
                "days_since_last": 0
            }
        
        # Calculate days since last activity
        days_diff = (current_date.date() - last_activity_date.date()).days
        
        if days_diff == 0:
            # Same day - streak continues
            return {
                "current_streak": None,  # Don't increment, same day
                "streak_active": True,
                "streak_broken": False,
                "days_since_last": 0
            }
        elif days_diff == 1:
            # Next day - streak continues
            return {
                "current_streak": "increment",
                "streak_active": True,
                "streak_broken": False,
                "days_since_last": 1
            }
        else:
            # Missed days - streak broken
            return {
                "current_streak": 1,  # Reset to 1
                "streak_active": False,
                "streak_broken": True,
                "days_since_last": days_diff
            }
    
    def get_streak_milestone_rewards(self, streak: int) -> List[XPReward]:
        """Get any milestone rewards earned at this streak"""
        rewards = []
        
        if streak == 3:
            rewards.append(self.calculate_xp_reward("streak_3_days"))
        elif streak == 7:
            rewards.append(self.calculate_xp_reward("streak_7_days"))
        elif streak == 30:
            rewards.append(self.calculate_xp_reward("streak_30_days"))
        
        return rewards
    
    def create_progress_snapshot(
        self,
        user_id: int,
        total_xp: int,
        simulations_completed: int,
        badges_earned: int,
        current_streak: int,
        longest_streak: int,
        last_activity: datetime
    ) -> ProgressSnapshot:
        """Create a complete snapshot of user progress"""
        current_level = self.get_level_from_xp(total_xp)
        progress_info = self.calculate_progress_to_next_level(total_xp, current_level)
        
        return ProgressSnapshot(
            user_id=user_id,
            current_level=current_level,
            current_xp=total_xp,
            xp_to_next_level=progress_info["xp_to_next"],
            progress_percentage=progress_info["progress_percentage"],
            total_simulations_completed=simulations_completed,
            total_badges_earned=badges_earned,
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_activity_date=last_activity,
            total_xp_earned=total_xp,
            next_level_info=progress_info.get("next_level")
        )
    
    def get_recommended_next_steps(
        self,
        current_level: Level,
        completed_simulations: List[str]
    ) -> List[Dict]:
        """Recommend next steps based on progress"""
        recommendations = []
        
        # Level-based recommendations
        if current_level == Level.FINANCIAL_NEWBIE:
            if "coffee_shop_effect" not in completed_simulations:
                recommendations.append({
                    "priority": 1,
                    "simulation": "coffee_shop_effect",
                    "reason": "Start here! Learn how small expenses add up.",
                    "xp": self.XP_REWARDS["coffee_shop_effect"]
                })
            if "paycheck_game" not in completed_simulations:
                recommendations.append({
                    "priority": 2,
                    "simulation": "paycheck_game",
                    "reason": "Master the 'pay yourself first' principle.",
                    "xp": self.XP_REWARDS["paycheck_game"]
                })
        
        elif current_level == Level.MONEY_APPRENTICE:
            if "budget_builder" not in completed_simulations:
                recommendations.append({
                    "priority": 1,
                    "simulation": "budget_builder",
                    "reason": "Build your first 50/30/20 budget.",
                    "xp": self.XP_REWARDS["budget_builder"]
                })
            if "emergency_fund" not in completed_simulations:
                recommendations.append({
                    "priority": 2,
                    "simulation": "emergency_fund",
                    "reason": "See why emergency funds prevent debt spirals.",
                    "xp": self.XP_REWARDS["emergency_fund"]
                })
        
        elif current_level == Level.BUDGET_WARRIOR:
            if "compound_interest" not in completed_simulations:
                recommendations.append({
                    "priority": 1,
                    "simulation": "compound_interest",
                    "reason": "Unlock the power of compound interest!",
                    "xp": self.XP_REWARDS["compound_interest"]
                })
        
        elif current_level >= Level.WEALTH_BUILDER:
            if "monte_carlo" not in completed_simulations:
                recommendations.append({
                    "priority": 1,
                    "simulation": "monte_carlo",
                    "reason": "Advanced: Run thousands of scenarios.",
                    "xp": self.XP_REWARDS["monte_carlo"]
                })
        
        return recommendations
    
    def get_all_levels(self) -> List[LevelInfo]:
        """Get information about all levels"""
        return [self.LEVEL_REQUIREMENTS[level] for level in Level]
    
    def estimate_time_to_next_level(
        self,
        current_xp: int,
        avg_xp_per_day: float
    ) -> Dict:
        """Estimate time to reach next level"""
        current_level = self.get_level_from_xp(current_xp)
        next_level_info = self.get_next_level_info(current_level)
        
        if not next_level_info:
            return {
                "at_max_level": True,
                "days_remaining": 0,
                "estimated_date": None
            }
        
        xp_needed = next_level_info.xp_required - current_xp
        
        if avg_xp_per_day <= 0:
            return {
                "at_max_level": False,
                "days_remaining": None,
                "estimated_date": None,
                "message": "Complete simulations to start earning XP!"
            }
        
        days_remaining = int(xp_needed / avg_xp_per_day)
        estimated_date = datetime.now() + timedelta(days=days_remaining)
        
        return {
            "at_max_level": False,
            "days_remaining": days_remaining,
            "estimated_date": estimated_date,
            "xp_needed": xp_needed,
            "message": f"About {days_remaining} days at your current pace!"
        }
