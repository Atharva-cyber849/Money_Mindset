"""
Achievement Chains System
Manages achievement prerequisites, chains, and unlocking mechanisms
Enables collecting related achievements to unlock special rewards
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum


class AchievementRarity(Enum):
    """Achievement rarity levels"""
    COMMON = "common"  # Default achievements
    UNCOMMON = "uncommon"  # Harder to get
    RARE = "rare"  # Very challenging
    EPIC = "epic"  # Requires multiple achievements
    LEGENDARY = "legendary"  # Chain completion


@dataclass
class ChainReward:
    """Reward for completing an achievement chain"""
    badge_id: str
    badge_name: str
    bonus_xp: int
    unlock_item: Optional[str] = None  # e.g., "exclusive_game", "profile_frame"
    cosmetic: Optional[str] = None  # e.g., "gold_trophy"


@dataclass
class Achievement:
    """Achievement definition with chain support"""
    id: str
    name: str
    description: str
    category: str  # "trading", "savings", "investing", "business", "misc"
    rarity: AchievementRarity
    xp_reward: int
    unlock_condition: str
    icon: str
    chain_id: Optional[str] = None  # Which chain this belongs to
    prerequisites: List[str] = field(default_factory=list)  # Must unlock these first
    related_achievements: List[str] = field(default_factory=list)  # Related but not required
    hidden: bool = False  # Secret achievement
    difficulty_multiplier: float = 1.0  # 0.5 for easy, 2.0 for hard


class AchievementChain:
    """
    Linked achievements that build on each other
    Complete all to unlock special rewards
    """

    def __init__(
        self,
        chain_id: str,
        name: str,
        description: str,
        achievements: List[str],  # Achievement IDs in order
        chain_reward: ChainReward,
    ):
        self.chain_id = chain_id
        self.name = name
        self.description = description
        self.achievements = achievements
        self.chain_reward = chain_reward
        self.total_steps = len(achievements)

    def get_progress(self, unlocked_achievements: Set[str]) -> Dict:
        """Get user progress on this chain"""
        completed = len([a for a in self.achievements if a in unlocked_achievements])
        return {
            "chain_id": self.chain_id,
            "name": self.name,
            "completed_steps": completed,
            "total_steps": self.total_steps,
            "progress_percentage": (completed / self.total_steps) * 100,
            "next_achievement": (
                self.achievements[completed] if completed < self.total_steps else None
            ),
            "is_complete": completed == self.total_steps,
            "reward": self.chain_reward if completed == self.total_steps else None,
        }


class AchievementChainSystem:
    """
    Manages achievement chains, prerequisites, and unlocks
    """

    def __init__(self):
        self.chains: Dict[str, AchievementChain] = {}
        self.achievements: Dict[str, Achievement] = {}
        self._initialize_achievements()

    def _initialize_achievements(self):
        """Initialize all achievements and chains"""

        # === TRADING CHAIN ===
        trading_chain = AchievementChain(
            chain_id="trading_mastery",
            name="Trading Mastery",
            description="Progress from novice to expert trader",
            achievements=[
                "first_trade",
                "profitable_trade",
                "portfolio_milestone_1",
                "portfolio_milestone_2",
                "trading_expert",
            ],
            chain_reward=ChainReward(
                badge_id="trading_master",
                badge_name="Trading Master",
                bonus_xp=2000,
                unlock_item="advanced_paper_trading",
            ),
        )
        self.chains["trading_mastery"] = trading_chain

        # Achievement definitions
        self.achievements["first_trade"] = Achievement(
            id="first_trade",
            name="First Trade",
            description="Execute your first stock trade",
            category="trading",
            rarity=AchievementRarity.COMMON,
            xp_reward=100,
            unlock_condition="trades_count >= 1",
            icon="📈",
            chain_id="trading_mastery",
        )

        self.achievements["profitable_trade"] = Achievement(
            id="profitable_trade",
            name="Profitable Trade",
            description="Make your first profitable trade",
            category="trading",
            rarity=AchievementRarity.UNCOMMON,
            xp_reward=250,
            unlock_condition="profitable_trades >= 1",
            icon="💰",
            chain_id="trading_mastery",
            prerequisites=["first_trade"],
        )

        self.achievements["portfolio_milestone_1"] = Achievement(
            id="portfolio_milestone_1",
            name="Portfolio ₹5L",
            description="Grow portfolio to ₹5,00,000",
            category="trading",
            rarity=AchievementRarity.UNCOMMON,
            xp_reward=300,
            unlock_condition="portfolio_value >= 500000",
            icon="🎯",
            chain_id="trading_mastery",
            prerequisites=["profitable_trade"],
        )

        self.achievements["portfolio_milestone_2"] = Achievement(
            id="portfolio_milestone_2",
            name="Portfolio ₹10L",
            description="Grow portfolio to ₹10,00,000",
            category="trading",
            rarity=AchievementRarity.RARE,
            xp_reward=500,
            unlock_condition="portfolio_value >= 1000000",
            icon="🚀",
            chain_id="trading_mastery",
            prerequisites=["portfolio_milestone_1"],
        )

        self.achievements["trading_expert"] = Achievement(
            id="trading_expert",
            name="Trading Expert",
            description="Complete Trading Mastery chain",
            category="trading",
            rarity=AchievementRarity.EPIC,
            xp_reward=1000,
            unlock_condition="chain_trading_mastery_complete",
            icon="👑",
            chain_id="trading_mastery",
            prerequisites=["portfolio_milestone_2"],
        )

        # === SAVINGS CHAIN ===
        savings_chain = AchievementChain(
            chain_id="savings_hero",
            name="Savings Hero",
            description="Master the art of saving and emergency funds",
            achievements=[
                "first_savings_goal",
                "emergency_fund_starter",
                "emergency_fund_complete",
                "savings_streak_30",
                "savings_hero_complete",
            ],
            chain_reward=ChainReward(
                badge_id="savings_hero",
                badge_name="Savings Hero",
                bonus_xp=1500,
                unlock_item="special_savings_games",
            ),
        )
        self.chains["savings_hero"] = savings_chain

        self.achievements["first_savings_goal"] = Achievement(
            id="first_savings_goal",
            name="First Savings Goal",
            description="Set your first savings goal",
            category="savings",
            rarity=AchievementRarity.COMMON,
            xp_reward=100,
            unlock_condition="savings_goals_count >= 1",
            icon="🎯",
            chain_id="savings_hero",
        )

        self.achievements["emergency_fund_starter"] = Achievement(
            id="emergency_fund_starter",
            name="Emergency Fund Started",
            description="Build an emergency fund of ₹1,00,000",
            category="savings",
            rarity=AchievementRarity.UNCOMMON,
            xp_reward=300,
            unlock_condition="emergency_fund >= 100000",
            icon="🛡️",
            chain_id="savings_hero",
            prerequisites=["first_savings_goal"],
        )

        self.achievements["emergency_fund_complete"] = Achievement(
            id="emergency_fund_complete",
            name="Emergency Fund Complete",
            description="Build a 6-month emergency fund",
            category="savings",
            rarity=AchievementRarity.RARE,
            xp_reward=500,
            unlock_condition="emergency_fund_months >= 6",
            icon="💪",
            chain_id="savings_hero",
            prerequisites=["emergency_fund_starter"],
        )

        self.achievements["savings_streak_30"] = Achievement(
            id="savings_streak_30",
            name="30-Day Saver",
            description="Maintain 30-day savings streak",
            category="savings",
            rarity=AchievementRarity.RARE,
            xp_reward=500,
            unlock_condition="savings_streak_days >= 30",
            icon="🔥",
            chain_id="savings_hero",
            prerequisites=["emergency_fund_starter"],
        )

        self.achievements["savings_hero_complete"] = Achievement(
            id="savings_hero_complete",
            name="Complete Savings Hero",
            description="Master all savings achievements",
            category="savings",
            rarity=AchievementRarity.EPIC,
            xp_reward=1000,
            unlock_condition="chain_savings_hero_complete",
            icon="🏆",
            chain_id="savings_hero",
            prerequisites=["emergency_fund_complete", "savings_streak_30"],
        )

        # === INVESTING CHAIN ===
        investing_chain = AchievementChain(
            chain_id="sip_master",
            name="SIP Master",
            description="Master systematic investing for wealth",
            achievements=[
                "first_sip",
                "sip_1_year",
                "sip_5_year",
                "sip_power",
                "sip_master_complete",
            ],
            chain_reward=ChainReward(
                badge_id="sip_master",
                badge_name="SIP Master",
                bonus_xp=2500,
                unlock_item="exclusive_compound_interest_game",
            ),
        )
        self.chains["sip_master"] = investing_chain

        self.achievements["first_sip"] = Achievement(
            id="first_sip",
            name="First SIP",
            description="Start your first Systematic Investment Plan",
            category="investing",
            rarity=AchievementRarity.COMMON,
            xp_reward=150,
            unlock_condition="sip_count >= 1",
            icon="📊",
            chain_id="sip_master",
        )

        self.achievements["sip_1_year"] = Achievement(
            id="sip_1_year",
            name="1-Year Investor",
            description="Maintain SIP for 1 year",
            category="investing",
            rarity=AchievementRarity.UNCOMMON,
            xp_reward=300,
            unlock_condition="sip_months >= 12",
            icon="📈",
            chain_id="sip_master",
            prerequisites=["first_sip"],
        )

        self.achievements["sip_5_year"] = Achievement(
            id="sip_5_year",
            name="5-Year Champion",
            description="Maintain SIP for 5 years",
            category="investing",
            rarity=AchievementRarity.RARE,
            xp_reward=600,
            unlock_condition="sip_months >= 60",
            icon="💎",
            chain_id="sip_master",
            prerequisites=["sip_1_year"],
        )

        self.achievements["sip_power"] = Achievement(
            id="sip_power",
            name="Power of Compounding",
            description="Grow SIP to ₹2,000,000 through returns",
            category="investing",
            rarity=AchievementRarity.RARE,
            xp_reward=800,
            unlock_condition="sip_value >= 2000000",
            icon="💰",
            chain_id="sip_master",
            prerequisites=["sip_5_year"],
        )

        self.achievements["sip_master_complete"] = Achievement(
            id="sip_master_complete",
            name="SIP Master Complete",
            description="Achieve all SIP milestones",
            category="investing",
            rarity=AchievementRarity.EPIC,
            xp_reward=1500,
            unlock_condition="chain_sip_master_complete",
            icon="👑",
            chain_id="sip_master",
            prerequisites=["sip_power"],
        )

        # === BUSINESS CHAIN ===
        business_chain = AchievementChain(
            chain_id="entrepreneur",
            name="Entrepreneur",
            description="Build and scale a successful business",
            achievements=[
                "business_started",
                "revenue_100k",
                "revenue_500k",
                "expansion_milestone",
                "entrepreneur_complete",
            ],
            chain_reward=ChainReward(
                badge_id="entrepreneur",
                badge_name="Entrepreneur",
                bonus_xp=2000,
                unlock_item="exclusive_business_game",
            ),
        )
        self.chains["entrepreneur"] = business_chain

        self.achievements["business_started"] = Achievement(
            id="business_started",
            name="Business Started",
            description="Launch your first business",
            category="business",
            rarity=AchievementRarity.COMMON,
            xp_reward=100,
            unlock_condition="business_count >= 1",
            icon="🏪",
            chain_id="entrepreneur",
        )

        self.achievements["revenue_100k"] = Achievement(
            id="revenue_100k",
            name="₹1L Revenue",
            description="Generate ₹1,00,000 in revenue",
            category="business",
            rarity=AchievementRarity.UNCOMMON,
            xp_reward=300,
            unlock_condition="business_revenue >= 100000",
            icon="📊",
            chain_id="entrepreneur",
            prerequisites=["business_started"],
        )

        self.achievements["revenue_500k"] = Achievement(
            id="revenue_500k",
            name="₹5L Revenue",
            description="Generate ₹5,00,000 in revenue",
            category="business",
            rarity=AchievementRarity.RARE,
            xp_reward=500,
            unlock_condition="business_revenue >= 500000",
            icon="💼",
            chain_id="entrepreneur",
            prerequisites=["revenue_100k"],
        )

        self.achievements["expansion_milestone"] = Achievement(
            id="expansion_milestone",
            name="Business Expansion",
            description="Successfully expand your business",
            category="business",
            rarity=AchievementRarity.RARE,
            xp_reward=600,
            unlock_condition="business_expansion_count >= 1",
            icon="🚀",
            chain_id="entrepreneur",
            prerequisites=["revenue_500k"],
        )

        self.achievements["entrepreneur_complete"] = Achievement(
            id="entrepreneur_complete",
            name="Complete Entrepreneur",
            description="Achieve all business milestones",
            category="business",
            rarity=AchievementRarity.EPIC,
            xp_reward=1200,
            unlock_condition="chain_entrepreneur_complete",
            icon="🏆",
            chain_id="entrepreneur",
            prerequisites=["expansion_milestone"],
        )

    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID"""
        return self.achievements.get(achievement_id)

    def get_chain(self, chain_id: str) -> Optional[AchievementChain]:
        """Get chain by ID"""
        return self.chains.get(chain_id)

    def get_all_chains(self) -> Dict[str, AchievementChain]:
        """Get all achievement chains"""
        return self.chains.copy()

    def can_unlock_achievement(
        self, achievement_id: str, unlocked_achievements: Set[str]
    ) -> bool:
        """Check if an achievement can be unlocked"""
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return False

        # Check all prerequisites are met
        for prerequisite in achievement.prerequisites:
            if prerequisite not in unlocked_achievements:
                return False

        return True

    def get_next_achievements(self, unlocked_achievements: Set[str]) -> List[Achievement]:
        """Get list of achievements that can be unlocked next"""
        available = []
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in unlocked_achievements:
                if self.can_unlock_achievement(achievement_id, unlocked_achievements):
                    available.append(achievement)
        return sorted(
            available, key=lambda a: (a.rarity.value, a.xp_reward), reverse=True
        )

    def get_user_chain_progress(
        self, unlocked_achievements: Set[str]
    ) -> List[Dict]:
        """Get all chain progress for a user"""
        progress = []
        for chain_id, chain in self.chains.items():
            progress.append(chain.get_progress(unlocked_achievements))
        return progress

    def get_chain_completion_percentage(self, user_id: str, unlocked_achievements: Set[str]) -> Dict[str, float]:
        """Get completion percentage for each chain"""
        percentages = {}
        for chain_id, chain in self.chains.items():
            progress = chain.get_progress(unlocked_achievements)
            percentages[chain_id] = progress["progress_percentage"]
        return percentages
