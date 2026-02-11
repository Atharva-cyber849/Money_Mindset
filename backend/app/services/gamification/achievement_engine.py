"""
Achievement & Unlock Engine
Manages simulation unlocks, achievements, and progression gates
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Any
from enum import Enum
from datetime import datetime


class UnlockType(Enum):
    """Types of unlock conditions"""
    LEVEL = "level"
    SIMULATION = "simulation"
    BADGE = "badge"
    XP = "xp"
    ALWAYS_UNLOCKED = "always_unlocked"


@dataclass
class UnlockCondition:
    """Condition required to unlock content"""
    type: UnlockType
    requirement: Any  # Level number, simulation name, badge ID, or XP amount
    description: str


@dataclass
class Simulation:
    """Simulation definition with unlock requirements"""
    id: str
    name: str
    description: str
    level: int
    xp_reward: int
    estimated_time: str  # e.g., "15 min"
    difficulty: str  # "Beginner", "Intermediate", "Advanced"
    unlock_conditions: List[UnlockCondition]
    prerequisites: List[str]  # List of simulation IDs
    category: str


@dataclass
class Achievement:
    """Achievement definition"""
    id: str
    name: str
    description: str
    unlock_condition: str
    reward_xp: int
    reward_badge: Optional[str]
    hidden: bool  # Secret achievements


@dataclass
class UnlockStatus:
    """Status of unlockable content"""
    content_id: str
    content_type: str
    unlocked: bool
    unlock_progress: List[Dict]  # Progress on each condition
    unlock_message: Optional[str]


class AchievementEngine:
    """
    Manages simulation unlocks, achievements, and progression
    """
    
    # Define all 12 core simulations + bonus
    SIMULATIONS = {
        # Level 1: Foundation (Always unlocked)
        "coffee_shop_effect": Simulation(
            id="coffee_shop_effect",
            name="The Coffee Shop Effect",
            description="Discover how small daily expenses compound into big money",
            level=1,
            xp_reward=100,
            estimated_time="10 min",
            difficulty="Beginner",
            unlock_conditions=[
                UnlockCondition(UnlockType.ALWAYS_UNLOCKED, None, "Available to everyone")
            ],
            prerequisites=[],
            category="Foundation"
        ),
        "paycheck_game": Simulation(
            id="paycheck_game",
            name="The Paycheck Game",
            description="Compare 3 strategies: Spend First, Bills First, or Save First?",
            level=1,
            xp_reward=200,
            estimated_time="15 min",
            difficulty="Beginner",
            unlock_conditions=[
                UnlockCondition(UnlockType.ALWAYS_UNLOCKED, None, "Available to everyone")
            ],
            prerequisites=[],
            category="Foundation"
        ),
        
        # Level 2: Budgeting & Emergency Funds
        "budget_builder": Simulation(
            id="budget_builder",
            name="Budget Builder Challenge",
            description="Build your first 50/30/20 budget with realistic constraints",
            level=2,
            xp_reward=300,
            estimated_time="20 min",
            difficulty="Beginner",
            unlock_conditions=[
                UnlockCondition(UnlockType.LEVEL, 2, "Reach Level 2: Money Apprentice")
            ],
            prerequisites=["paycheck_game"],
            category="Budgeting"
        ),
        "emergency_fund": Simulation(
            id="emergency_fund",
            name="Emergency Fund Race",
            description="Watch Alex vs Jordan: Who survives emergencies better?",
            level=2,
            xp_reward=300,
            estimated_time="15 min",
            difficulty="Beginner",
            unlock_conditions=[
                UnlockCondition(UnlockType.LEVEL, 2, "Reach Level 2: Money Apprentice")
            ],
            prerequisites=["budget_builder"],
            category="Safety Net"
        ),
        
        # Level 2: Debt Understanding
        "credit_card_trap": Simulation(
            id="credit_card_trap",
            name="Credit Card Trap",
            description="See how minimum payments turn $5,000 into decades of debt",
            level=2,
            xp_reward=250,
            estimated_time="15 min",
            difficulty="Intermediate",
            unlock_conditions=[
                UnlockCondition(UnlockType.LEVEL, 2, "Reach Level 2: Money Apprentice")
            ],
            prerequisites=["emergency_fund"],
            category="Debt Management"
        ),
        "debt_classification": Simulation(
            id="debt_classification",
            name="Good Debt vs Bad Debt",
            description="Learn to distinguish good debt from bad debt with real examples",
            level=2,
            xp_reward=250,
            estimated_time="15 min",
            difficulty="Intermediate",
            unlock_conditions=[
                UnlockCondition(UnlockType.SIMULATION, "credit_card_trap", "Complete Credit Card Trap")
            ],
            prerequisites=["credit_card_trap"],
            category="Debt Management"
        ),
        
        # Level 3: Investment Foundations
        "compound_interest": Simulation(
            id="compound_interest",
            name="Compound Interest Time Machine",
            description="Race through time: Emma vs Steven vs Larry. Time beats money!",
            level=3,
            xp_reward=400,
            estimated_time="20 min",
            difficulty="Intermediate",
            unlock_conditions=[
                UnlockCondition(UnlockType.LEVEL, 3, "Reach Level 3: Budget Warrior")
            ],
            prerequisites=["debt_classification"],
            category="Investing Basics"
        ),
        "risk_vs_reward": Simulation(
            id="risk_vs_reward",
            name="Risk vs Reward Explorer",
            description="Compare conservative, moderate, and aggressive investment strategies",
            level=3,
            xp_reward=400,
            estimated_time="20 min",
            difficulty="Intermediate",
            unlock_conditions=[
                UnlockCondition(UnlockType.LEVEL, 3, "Reach Level 3: Budget Warrior")
            ],
            prerequisites=["compound_interest"],
            category="Investing Basics"
        ),
        
        # Level 4: Advanced Investing
        "index_fund_challenge": Simulation(
            id="index_fund_challenge",
            name="Index Fund vs Stock Picker",
            description="Can you beat the index fund? (Spoiler: probably not!)",
            level=4,
            xp_reward=500,
            estimated_time="25 min",
            difficulty="Advanced",
            unlock_conditions=[
                UnlockCondition(UnlockType.LEVEL, 4, "Reach Level 4: Wealth Builder")
            ],
            prerequisites=["risk_vs_reward"],
            category="Advanced Investing"
        ),
        "monte_carlo": Simulation(
            id="monte_carlo",
            name="Monte Carlo: 10,000 Futures",
            description="Run thousands of scenarios to see all possible financial futures",
            level=4,
            xp_reward=600,
            estimated_time="30 min",
            difficulty="Advanced",
            unlock_conditions=[
                UnlockCondition(UnlockType.LEVEL, 4, "Reach Level 4: Wealth Builder"),
                UnlockCondition(UnlockType.SIMULATION, "index_fund_challenge", "Complete Index Fund Challenge")
            ],
            prerequisites=["index_fund_challenge"],
            category="Advanced Investing"
        ),
        
        # Level 4: Tax Optimization
        "tax_optimizer": Simulation(
            id="tax_optimizer",
            name="Tax-Advantaged Account Optimizer",
            description="Master 401k, Roth IRA, HSA, and tax strategies",
            level=4,
            xp_reward=500,
            estimated_time="25 min",
            difficulty="Advanced",
            unlock_conditions=[
                UnlockCondition(UnlockType.LEVEL, 4, "Reach Level 4: Wealth Builder")
            ],
            prerequisites=["compound_interest"],
            category="Tax Strategy"
        ),
        
        # Level 5: Complete Journey
        "sarah_journey": Simulation(
            id="sarah_journey",
            name="Sarah's 30-Day Transformation",
            description="Experience the complete journey from $0 to financial freedom",
            level=5,
            xp_reward=800,
            estimated_time="45 min",
            difficulty="Advanced",
            unlock_conditions=[
                UnlockCondition(UnlockType.LEVEL, 5, "Reach Level 5: Investment Guru"),
                UnlockCondition(UnlockType.XP, 10000, "Earn 10,000 total XP")
            ],
            prerequisites=["monte_carlo", "tax_optimizer"],
            category="Complete Journey"
        ),
    }
    
    # Define achievements
    ACHIEVEMENTS = {
        "speed_runner": Achievement(
            id="speed_runner",
            name="Speed Runner",
            description="Complete 5 simulations in one day",
            unlock_condition="complete_5_sims_one_day",
            reward_xp=300,
            reward_badge=None,
            hidden=False
        ),
        "perfectionist": Achievement(
            id="perfectionist",
            name="Perfectionist",
            description="Get perfect scores on 3 different simulations",
            unlock_condition="perfect_score_3_sims",
            reward_xp=400,
            reward_badge="perfect_score",
            hidden=False
        ),
        "dedicated_learner": Achievement(
            id="dedicated_learner",
            name="Dedicated Learner",
            description="Maintain a 30-day streak",
            unlock_condition="30_day_streak",
            reward_xp=500,
            reward_badge=None,
            hidden=False
        ),
        "early_bird": Achievement(
            id="early_bird",
            name="Early Bird",
            description="Complete a simulation before 7 AM",
            unlock_condition="complete_before_7am",
            reward_xp=100,
            reward_badge=None,
            hidden=True
        ),
        "night_owl": Achievement(
            id="night_owl",
            name="Night Owl",
            description="Complete a simulation after 11 PM",
            unlock_condition="complete_after_11pm",
            reward_xp=100,
            reward_badge=None,
            hidden=True
        ),
        "tutor_enthusiast": Achievement(
            id="tutor_enthusiast",
            name="Tutor Enthusiast",
            description="Ask AI Tutor 50 questions",
            unlock_condition="ai_tutor_50_questions",
            reward_xp=250,
            reward_badge=None,
            hidden=False
        ),
        "goal_getter": Achievement(
            id="goal_getter",
            name="Goal Getter",
            description="Complete 5 financial goals",
            unlock_condition="complete_5_goals",
            reward_xp=400,
            reward_badge=None,
            hidden=False
        ),
    }
    
    def __init__(self):
        """Initialize achievement engine"""
        pass
    
    def check_simulation_unlock(
        self,
        simulation_id: str,
        user_level: int,
        user_xp: int,
        completed_simulations: Set[str],
        earned_badges: Set[str]
    ) -> UnlockStatus:
        """
        Check if simulation is unlocked for user
        
        Args:
            simulation_id: Simulation to check
            user_level: User's current level
            user_xp: User's total XP
            completed_simulations: Set of completed simulation IDs
            earned_badges: Set of earned badge IDs
        
        Returns:
            UnlockStatus with details
        """
        simulation = self.SIMULATIONS.get(simulation_id)
        if not simulation:
            return UnlockStatus(
                content_id=simulation_id,
                content_type="simulation",
                unlocked=False,
                unlock_progress=[],
                unlock_message="Simulation not found"
            )
        
        unlocked = True
        progress = []
        
        # Check each unlock condition
        for condition in simulation.unlock_conditions:
            condition_met = False
            
            if condition.type == UnlockType.ALWAYS_UNLOCKED:
                condition_met = True
            
            elif condition.type == UnlockType.LEVEL:
                condition_met = user_level >= condition.requirement
                progress.append({
                    "type": "level",
                    "required": condition.requirement,
                    "current": user_level,
                    "met": condition_met,
                    "description": condition.description
                })
            
            elif condition.type == UnlockType.XP:
                condition_met = user_xp >= condition.requirement
                progress.append({
                    "type": "xp",
                    "required": condition.requirement,
                    "current": user_xp,
                    "met": condition_met,
                    "description": condition.description
                })
            
            elif condition.type == UnlockType.SIMULATION:
                condition_met = condition.requirement in completed_simulations
                progress.append({
                    "type": "simulation",
                    "required": condition.requirement,
                    "met": condition_met,
                    "description": condition.description
                })
            
            elif condition.type == UnlockType.BADGE:
                condition_met = condition.requirement in earned_badges
                progress.append({
                    "type": "badge",
                    "required": condition.requirement,
                    "met": condition_met,
                    "description": condition.description
                })
            
            if not condition_met:
                unlocked = False
        
        # Check prerequisites
        for prereq in simulation.prerequisites:
            if prereq not in completed_simulations:
                unlocked = False
                progress.append({
                    "type": "prerequisite",
                    "required": prereq,
                    "met": False,
                    "description": f"Complete {self.SIMULATIONS[prereq].name} first"
                })
        
        unlock_message = None
        if unlocked:
            unlock_message = f"✅ {simulation.name} is unlocked!"
        else:
            unmet = [p for p in progress if not p["met"]]
            if unmet:
                unlock_message = f"🔒 {unmet[0]['description']}"
        
        return UnlockStatus(
            content_id=simulation_id,
            content_type="simulation",
            unlocked=unlocked,
            unlock_progress=progress,
            unlock_message=unlock_message
        )
    
    def get_unlocked_simulations(
        self,
        user_level: int,
        user_xp: int,
        completed_simulations: Set[str],
        earned_badges: Set[str]
    ) -> List[Simulation]:
        """Get all unlocked simulations for user"""
        unlocked = []
        
        for sim_id, simulation in self.SIMULATIONS.items():
            status = self.check_simulation_unlock(
                sim_id,
                user_level,
                user_xp,
                completed_simulations,
                earned_badges
            )
            
            if status.unlocked:
                unlocked.append(simulation)
        
        return unlocked
    
    def get_locked_simulations(
        self,
        user_level: int,
        user_xp: int,
        completed_simulations: Set[str],
        earned_badges: Set[str]
    ) -> List[Dict]:
        """Get all locked simulations with unlock requirements"""
        locked = []
        
        for sim_id, simulation in self.SIMULATIONS.items():
            status = self.check_simulation_unlock(
                sim_id,
                user_level,
                user_xp,
                completed_simulations,
                earned_badges
            )
            
            if not status.unlocked:
                locked.append({
                    "simulation": simulation,
                    "status": status
                })
        
        return locked
    
    def get_next_unlock_recommendation(
        self,
        user_level: int,
        user_xp: int,
        completed_simulations: Set[str],
        earned_badges: Set[str]
    ) -> Optional[Dict]:
        """Recommend next simulation to unlock"""
        locked = self.get_locked_simulations(
            user_level,
            user_xp,
            completed_simulations,
            earned_badges
        )
        
        if not locked:
            return None
        
        # Find closest to unlocking
        for item in locked:
            # Check if only one condition is unmet
            unmet = [p for p in item["status"].unlock_progress if not p["met"]]
            if len(unmet) == 1:
                return {
                    "simulation": item["simulation"],
                    "missing_requirement": unmet[0],
                    "recommendation": self._generate_unlock_recommendation(unmet[0])
                }
        
        # If no close unlocks, recommend general progression
        return {
            "simulation": locked[0]["simulation"],
            "missing_requirement": None,
            "recommendation": f"Keep earning XP to reach Level {locked[0]['simulation'].level}!"
        }
    
    def _generate_unlock_recommendation(self, requirement: Dict) -> str:
        """Generate recommendation for unlocking content"""
        if requirement["type"] == "level":
            xp_needed = requirement["required"] * 1000  # Rough estimate
            return f"Earn {xp_needed - requirement['current']} more XP to reach Level {requirement['required']}"
        
        elif requirement["type"] == "xp":
            needed = requirement["required"] - requirement["current"]
            return f"Earn {needed} more XP to unlock"
        
        elif requirement["type"] == "simulation":
            sim_name = self.SIMULATIONS[requirement["required"]].name
            return f"Complete '{sim_name}' first"
        
        elif requirement["type"] == "badge":
            return f"Earn the '{requirement['required']}' badge"
        
        return "Continue your learning journey"
    
    def check_achievements(
        self,
        user_data: Dict
    ) -> List[Achievement]:
        """Check if user has unlocked any achievements"""
        unlocked_achievements = []
        
        completed_sims = user_data.get("completed_simulations", [])
        perfect_scores = user_data.get("perfect_score_simulations", [])
        current_streak = user_data.get("current_streak", 0)
        ai_questions_count = user_data.get("ai_questions_asked", 0)
        goals_completed = user_data.get("goals_completed", 0)
        earned_achievements = set(user_data.get("earned_achievements", []))
        
        # Get completion times if available
        completion_times = user_data.get("simulation_completion_times", {})
        
        for achievement_id, achievement in self.ACHIEVEMENTS.items():
            if achievement_id in earned_achievements:
                continue
            
            unlocked = False
            
            if achievement.unlock_condition == "complete_5_sims_one_day":
                # Check if 5 sims completed on same day
                # This would need date tracking in completion_times
                pass  # Implement with date tracking
            
            elif achievement.unlock_condition == "perfect_score_3_sims":
                unlocked = len(perfect_scores) >= 3
            
            elif achievement.unlock_condition == "30_day_streak":
                unlocked = current_streak >= 30
            
            elif achievement.unlock_condition == "complete_before_7am":
                # Check completion times
                pass  # Implement with timestamp tracking
            
            elif achievement.unlock_condition == "complete_after_11pm":
                # Check completion times
                pass  # Implement with timestamp tracking
            
            elif achievement.unlock_condition == "ai_tutor_50_questions":
                unlocked = ai_questions_count >= 50
            
            elif achievement.unlock_condition == "complete_5_goals":
                unlocked = goals_completed >= 5
            
            if unlocked:
                unlocked_achievements.append(achievement)
        
        return unlocked_achievements
    
    def get_simulation_by_id(self, simulation_id: str) -> Optional[Simulation]:
        """Get simulation by ID"""
        return self.SIMULATIONS.get(simulation_id)
    
    def get_all_simulations(self) -> List[Simulation]:
        """Get all simulations"""
        return list(self.SIMULATIONS.values())
    
    def get_simulations_by_level(self, level: int) -> List[Simulation]:
        """Get simulations for specific level"""
        return [sim for sim in self.SIMULATIONS.values() if sim.level == level]
    
    def get_learning_path(
        self,
        completed_simulations: Set[str]
    ) -> List[Dict]:
        """
        Generate recommended learning path
        
        Returns ordered list of simulations with completion status
        """
        path = []
        
        # Recommended order based on prerequisites
        recommended_order = [
            "coffee_shop_effect",
            "paycheck_game",
            "budget_builder",
            "emergency_fund",
            "credit_card_trap",
            "debt_classification",
            "compound_interest",
            "risk_vs_reward",
            "index_fund_challenge",
            "tax_optimizer",
            "monte_carlo",
            "sarah_journey",
        ]
        
        for sim_id in recommended_order:
            simulation = self.SIMULATIONS.get(sim_id)
            if simulation:
                path.append({
                    "simulation": simulation,
                    "completed": sim_id in completed_simulations,
                    "order": len(path) + 1
                })
        
        return path
    
    def calculate_completion_percentage(
        self,
        completed_simulations: Set[str]
    ) -> float:
        """Calculate overall completion percentage"""
        total = len(self.SIMULATIONS)
        completed = len([s for s in completed_simulations if s in self.SIMULATIONS])
        return (completed / total * 100) if total > 0 else 0
