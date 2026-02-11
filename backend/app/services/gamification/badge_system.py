"""
Badge System - Awards and Collections
Defines all badges, unlock conditions, and award logic
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime


class BadgeRarity(Enum):
    """Badge rarity tiers"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class BadgeCategory(Enum):
    """Badge categories"""
    FOUNDATION = "foundation"
    DEBT_MASTER = "debt_master"
    INVESTMENT = "investment"
    COMPLETION = "completion"
    STREAK = "streak"
    SPECIAL = "special"


@dataclass
class Badge:
    """Badge definition"""
    id: str
    name: str
    description: str
    rarity: BadgeRarity
    category: BadgeCategory
    icon: str
    unlock_condition: str
    xp_reward: int
    hint: str  # How to earn it


@dataclass
class BadgeProgress:
    """Progress toward earning a badge"""
    badge_id: str
    current_progress: int
    required_progress: int
    progress_percentage: float
    unlocked: bool
    date_earned: Optional[datetime]


@dataclass
class BadgeAward:
    """A badge being awarded to user"""
    badge: Badge
    date_earned: datetime
    celebration_message: str


class BadgeSystem:
    """
    Manages all badges, unlock conditions, and awards
    """
    
    # All 16 badges defined
    BADGES = {
        # COMMON BADGES (4) - Foundation & First Steps
        "first_steps": Badge(
            id="first_steps",
            name="First Steps",
            description="Completed your first simulation",
            rarity=BadgeRarity.COMMON,
            category=BadgeCategory.FOUNDATION,
            icon="👣",
            unlock_condition="complete_1_simulation",
            xp_reward=50,
            hint="Complete any simulation"
        ),
        "coffee_conscious": Badge(
            id="coffee_conscious",
            name="Coffee Conscious",
            description="Discovered the coffee shop effect",
            rarity=BadgeRarity.COMMON,
            category=BadgeCategory.FOUNDATION,
            icon="☕",
            unlock_condition="complete_coffee_shop",
            xp_reward=100,
            hint="Complete 'The Coffee Shop Effect' simulation"
        ),
        "budget_beginner": Badge(
            id="budget_beginner",
            name="Budget Beginner",
            description="Created your first budget",
            rarity=BadgeRarity.COMMON,
            category=BadgeCategory.FOUNDATION,
            icon="📊",
            unlock_condition="complete_budget_builder",
            xp_reward=100,
            hint="Complete 'Budget Builder' simulation"
        ),
        "paycheck_pro": Badge(
            id="paycheck_pro",
            name="Paycheck Pro",
            description="Mastered the paycheck game",
            rarity=BadgeRarity.COMMON,
            category=BadgeCategory.FOUNDATION,
            icon="💰",
            unlock_condition="complete_paycheck_game",
            xp_reward=100,
            hint="Complete 'Paycheck Game' simulation"
        ),
        
        # RARE BADGES (5) - Debt & Emergency Fund
        "debt_destroyer": Badge(
            id="debt_destroyer",
            name="Debt Destroyer",
            description="Completed all debt simulations",
            rarity=BadgeRarity.RARE,
            category=BadgeCategory.DEBT_MASTER,
            icon="💣",
            unlock_condition="complete_all_debt_simulations",
            xp_reward=250,
            hint="Complete Credit Card Trap and Debt Classification"
        ),
        "emergency_ready": Badge(
            id="emergency_ready",
            name="Emergency Ready",
            description="Built a strong emergency fund strategy",
            rarity=BadgeRarity.RARE,
            category=BadgeCategory.FOUNDATION,
            icon="🛡️",
            unlock_condition="complete_emergency_fund",
            xp_reward=200,
            hint="Complete 'Emergency Fund Race' simulation"
        ),
        "streak_warrior": Badge(
            id="streak_warrior",
            name="Streak Warrior",
            description="7-day learning streak",
            rarity=BadgeRarity.RARE,
            category=BadgeCategory.STREAK,
            icon="🔥",
            unlock_condition="achieve_7_day_streak",
            xp_reward=200,
            hint="Log in and complete activities for 7 days straight"
        ),
        "level_3_achieved": Badge(
            id="level_3_achieved",
            name="Budget Warrior",
            description="Reached Level 3: Budget Warrior",
            rarity=BadgeRarity.RARE,
            category=BadgeCategory.COMPLETION,
            icon="⚔️",
            unlock_condition="reach_level_3",
            xp_reward=300,
            hint="Earn 3,000 XP to reach Level 3"
        ),
        "perfect_score": Badge(
            id="perfect_score",
            name="Perfect Score",
            description="Achieved perfect score in any simulation",
            rarity=BadgeRarity.RARE,
            category=BadgeCategory.SPECIAL,
            icon="💯",
            unlock_condition="perfect_simulation_score",
            xp_reward=250,
            hint="Get 100% score in a simulation"
        ),
        
        # EPIC BADGES (4) - Investment & Advanced
        "compound_master": Badge(
            id="compound_master",
            name="Compound Master",
            description="Unlocked the power of compound interest",
            rarity=BadgeRarity.EPIC,
            category=BadgeCategory.INVESTMENT,
            icon="📈",
            unlock_condition="complete_compound_interest",
            xp_reward=400,
            hint="Complete 'Compound Interest Time Machine' simulation"
        ),
        "index_fund_believer": Badge(
            id="index_fund_believer",
            name="Index Fund Believer",
            description="Learned why index funds win",
            rarity=BadgeRarity.EPIC,
            category=BadgeCategory.INVESTMENT,
            icon="📊",
            unlock_condition="complete_index_fund_challenge",
            xp_reward=400,
            hint="Complete 'Index Fund vs Stock Picker' simulation"
        ),
        "tax_optimizer": Badge(
            id="tax_optimizer",
            name="Tax Optimizer",
            description="Mastered tax-advantaged accounts",
            rarity=BadgeRarity.EPIC,
            category=BadgeCategory.INVESTMENT,
            icon="🎯",
            unlock_condition="complete_tax_optimizer",
            xp_reward=400,
            hint="Complete 'Tax-Advantaged Optimizer' simulation"
        ),
        "simulation_completionist": Badge(
            id="simulation_completionist",
            name="Simulation Completionist",
            description="Completed 10+ simulations",
            rarity=BadgeRarity.EPIC,
            category=BadgeCategory.COMPLETION,
            icon="🏆",
            unlock_condition="complete_10_simulations",
            xp_reward=500,
            hint="Complete 10 different simulations"
        ),
        
        # LEGENDARY BADGES (3) - Ultimate Achievements
        "financial_master": Badge(
            id="financial_master",
            name="Financial Master",
            description="Reached Level 6: Financial Master",
            rarity=BadgeRarity.LEGENDARY,
            category=BadgeCategory.COMPLETION,
            icon="👑",
            unlock_condition="reach_level_6",
            xp_reward=1000,
            hint="Earn 20,000 XP to reach max level"
        ),
        "monte_carlo_expert": Badge(
            id="monte_carlo_expert",
            name="Monte Carlo Expert",
            description="Ran advanced Monte Carlo simulations",
            rarity=BadgeRarity.LEGENDARY,
            category=BadgeCategory.INVESTMENT,
            icon="🎲",
            unlock_condition="complete_monte_carlo",
            xp_reward=600,
            hint="Complete 'Monte Carlo' simulation"
        ),
        "sarah_journey_complete": Badge(
            id="sarah_journey_complete",
            name="Journey Complete",
            description="Completed Sarah's 30-day transformation",
            rarity=BadgeRarity.LEGENDARY,
            category=BadgeCategory.COMPLETION,
            icon="✨",
            unlock_condition="complete_sarah_journey",
            xp_reward=800,
            hint="Complete the full 'Sarah's Journey' simulation"
        ),
    }
    
    def __init__(self):
        """Initialize badge system"""
        pass
    
    def get_badge(self, badge_id: str) -> Optional[Badge]:
        """Get badge by ID"""
        return self.BADGES.get(badge_id)
    
    def get_all_badges(self) -> List[Badge]:
        """Get all badges"""
        return list(self.BADGES.values())
    
    def get_badges_by_rarity(self, rarity: BadgeRarity) -> List[Badge]:
        """Get all badges of specific rarity"""
        return [badge for badge in self.BADGES.values() if badge.rarity == rarity]
    
    def get_badges_by_category(self, category: BadgeCategory) -> List[Badge]:
        """Get all badges in a category"""
        return [badge for badge in self.BADGES.values() if badge.category == category]
    
    def check_badge_unlocks(
        self,
        user_data: Dict
    ) -> List[BadgeAward]:
        """
        Check if user has unlocked any new badges
        
        Args:
            user_data: Dictionary with user's stats:
                - completed_simulations: List[str]
                - current_level: int
                - current_streak: int
                - total_simulations: int
                - has_perfect_score: bool
                - earned_badges: Set[str] (already earned badge IDs)
        
        Returns:
            List of newly unlocked badges
        """
        newly_unlocked = []
        completed_sims = set(user_data.get("completed_simulations", []))
        current_level = user_data.get("current_level", 1)
        current_streak = user_data.get("current_streak", 0)
        total_sims = user_data.get("total_simulations", 0)
        has_perfect = user_data.get("has_perfect_score", False)
        earned_badges = set(user_data.get("earned_badges", []))
        
        # Check each badge's unlock condition
        for badge_id, badge in self.BADGES.items():
            # Skip if already earned
            if badge_id in earned_badges:
                continue
            
            unlocked = False
            
            # Check unlock conditions
            if badge.unlock_condition == "complete_1_simulation":
                unlocked = total_sims >= 1
            
            elif badge.unlock_condition == "complete_coffee_shop":
                unlocked = "coffee_shop_effect" in completed_sims
            
            elif badge.unlock_condition == "complete_budget_builder":
                unlocked = "budget_builder" in completed_sims
            
            elif badge.unlock_condition == "complete_paycheck_game":
                unlocked = "paycheck_game" in completed_sims
            
            elif badge.unlock_condition == "complete_all_debt_simulations":
                unlocked = (
                    "credit_card_trap" in completed_sims and
                    "debt_classification" in completed_sims
                )
            
            elif badge.unlock_condition == "complete_emergency_fund":
                unlocked = "emergency_fund" in completed_sims
            
            elif badge.unlock_condition == "achieve_7_day_streak":
                unlocked = current_streak >= 7
            
            elif badge.unlock_condition == "reach_level_3":
                unlocked = current_level >= 3
            
            elif badge.unlock_condition == "perfect_simulation_score":
                unlocked = has_perfect
            
            elif badge.unlock_condition == "complete_compound_interest":
                unlocked = "compound_interest" in completed_sims
            
            elif badge.unlock_condition == "complete_index_fund_challenge":
                unlocked = "index_fund_challenge" in completed_sims
            
            elif badge.unlock_condition == "complete_tax_optimizer":
                unlocked = "tax_optimizer" in completed_sims
            
            elif badge.unlock_condition == "complete_10_simulations":
                unlocked = total_sims >= 10
            
            elif badge.unlock_condition == "reach_level_6":
                unlocked = current_level >= 6
            
            elif badge.unlock_condition == "complete_monte_carlo":
                unlocked = "monte_carlo" in completed_sims
            
            elif badge.unlock_condition == "complete_sarah_journey":
                unlocked = "sarah_journey" in completed_sims
            
            if unlocked:
                newly_unlocked.append(BadgeAward(
                    badge=badge,
                    date_earned=datetime.now(),
                    celebration_message=self._generate_badge_message(badge)
                ))
        
        return newly_unlocked
    
    def _generate_badge_message(self, badge: Badge) -> str:
        """Generate celebration message for badge unlock"""
        rarity_messages = {
            BadgeRarity.COMMON: "🎉 Badge Unlocked!",
            BadgeRarity.RARE: "✨ Rare Badge Unlocked!",
            BadgeRarity.EPIC: "🌟 EPIC Badge Unlocked!",
            BadgeRarity.LEGENDARY: "👑 LEGENDARY Badge Unlocked!"
        }
        
        prefix = rarity_messages[badge.rarity]
        return f"{prefix} {badge.icon} {badge.name} - {badge.description}"
    
    def calculate_badge_progress(
        self,
        badge_id: str,
        user_data: Dict
    ) -> BadgeProgress:
        """
        Calculate progress toward a specific badge
        
        Args:
            badge_id: Badge to check progress for
            user_data: User's current stats
        
        Returns:
            BadgeProgress with current progress
        """
        badge = self.BADGES.get(badge_id)
        if not badge:
            return None
        
        completed_sims = set(user_data.get("completed_simulations", []))
        current_level = user_data.get("current_level", 1)
        current_streak = user_data.get("current_streak", 0)
        total_sims = user_data.get("total_simulations", 0)
        earned_badges = set(user_data.get("earned_badges", []))
        
        unlocked = badge_id in earned_badges
        
        # Calculate progress based on condition
        if badge.unlock_condition == "complete_1_simulation":
            progress = min(total_sims, 1)
            required = 1
        
        elif "complete_" in badge.unlock_condition and "_simulations" not in badge.unlock_condition:
            # Single simulation badges
            sim_name = badge.unlock_condition.replace("complete_", "")
            progress = 1 if sim_name in completed_sims else 0
            required = 1
        
        elif badge.unlock_condition == "complete_all_debt_simulations":
            debt_sims = ["credit_card_trap", "debt_classification"]
            progress = len([s for s in debt_sims if s in completed_sims])
            required = 2
        
        elif badge.unlock_condition == "achieve_7_day_streak":
            progress = min(current_streak, 7)
            required = 7
        
        elif "reach_level_" in badge.unlock_condition:
            target_level = int(badge.unlock_condition.split("_")[-1])
            progress = current_level
            required = target_level
        
        elif badge.unlock_condition == "complete_10_simulations":
            progress = min(total_sims, 10)
            required = 10
        
        else:
            # Binary conditions (perfect score, etc.)
            progress = 1 if unlocked else 0
            required = 1
        
        progress_pct = (progress / required * 100) if required > 0 else 0
        
        return BadgeProgress(
            badge_id=badge_id,
            current_progress=progress,
            required_progress=required,
            progress_percentage=min(progress_pct, 100.0),
            unlocked=unlocked,
            date_earned=user_data.get("badge_dates", {}).get(badge_id)
        )
    
    def get_badge_collection_stats(
        self,
        earned_badge_ids: Set[str]
    ) -> Dict:
        """
        Get statistics about badge collection
        
        Args:
            earned_badge_ids: Set of earned badge IDs
        
        Returns:
            Collection statistics
        """
        total_badges = len(self.BADGES)
        earned_count = len(earned_badge_ids)
        
        # Count by rarity
        rarity_counts = {rarity: 0 for rarity in BadgeRarity}
        rarity_totals = {rarity: 0 for rarity in BadgeRarity}
        
        for badge_id, badge in self.BADGES.items():
            rarity_totals[badge.rarity] += 1
            if badge_id in earned_badge_ids:
                rarity_counts[badge.rarity] += 1
        
        # Count by category
        category_counts = {category: 0 for category in BadgeCategory}
        category_totals = {category: 0 for category in BadgeCategory}
        
        for badge_id, badge in self.BADGES.items():
            category_totals[badge.category] += 1
            if badge_id in earned_badge_ids:
                category_counts[badge.category] += 1
        
        # Calculate completion percentage
        completion_percentage = (earned_count / total_badges * 100) if total_badges > 0 else 0
        
        return {
            "total_badges": total_badges,
            "earned_badges": earned_count,
            "completion_percentage": completion_percentage,
            "by_rarity": {
                "common": {
                    "earned": rarity_counts[BadgeRarity.COMMON],
                    "total": rarity_totals[BadgeRarity.COMMON]
                },
                "rare": {
                    "earned": rarity_counts[BadgeRarity.RARE],
                    "total": rarity_totals[BadgeRarity.RARE]
                },
                "epic": {
                    "earned": rarity_counts[BadgeRarity.EPIC],
                    "total": rarity_totals[BadgeRarity.EPIC]
                },
                "legendary": {
                    "earned": rarity_counts[BadgeRarity.LEGENDARY],
                    "total": rarity_totals[BadgeRarity.LEGENDARY]
                }
            },
            "by_category": {
                category.value: {
                    "earned": category_counts[category],
                    "total": category_totals[category]
                }
                for category in BadgeCategory
            }
        }
    
    def get_next_badges_to_earn(
        self,
        user_data: Dict,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get suggestions for next badges to earn
        
        Args:
            user_data: User's current stats
            limit: Max number of suggestions
        
        Returns:
            List of badge suggestions with progress
        """
        earned_badges = set(user_data.get("earned_badges", []))
        suggestions = []
        
        for badge_id, badge in self.BADGES.items():
            if badge_id in earned_badges:
                continue
            
            progress = self.calculate_badge_progress(badge_id, user_data)
            
            suggestions.append({
                "badge": badge,
                "progress": progress,
                "hint": badge.hint
            })
        
        # Sort by progress (closest to completion first)
        suggestions.sort(key=lambda x: x["progress"].progress_percentage, reverse=True)
        
        return suggestions[:limit]
    
    def calculate_badge_xp_earned(self, earned_badge_ids: Set[str]) -> int:
        """Calculate total XP earned from badges"""
        total_xp = 0
        for badge_id in earned_badge_ids:
            badge = self.BADGES.get(badge_id)
            if badge:
                total_xp += badge.xp_reward
        return total_xp
