"""
Gamification Service - Main Integration Layer
Coordinates progress tracking, badges, achievements, and user updates
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
from datetime import datetime
from .progress_tracker import ProgressTracker, Level, XPReward, ProgressSnapshot
from .badge_system import BadgeSystem, BadgeAward, BadgeProgress
from .achievement_engine import AchievementEngine, UnlockStatus, Achievement


@dataclass
class GamificationUpdate:
    """Complete update from a user action"""
    xp_earned: XPReward
    level_up: Optional[Dict]
    badges_earned: List[BadgeAward]
    achievements_unlocked: List[Achievement]
    new_unlocks: List[Dict]
    streak_update: Dict
    updated_snapshot: ProgressSnapshot


@dataclass
class UserStats:
    """User's gamification statistics"""
    user_id: int
    total_xp: int
    current_level: Level
    completed_simulations: Set[str]
    earned_badges: Set[str]
    earned_achievements: Set[str]
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[datetime]
    perfect_score_simulations: Set[str]
    ai_questions_asked: int
    goals_completed: int


class GamificationService:
    """
    Main service coordinating all gamification systems
    Handles user actions, awards, and progress updates
    """
    
    def __init__(self):
        """Initialize all gamification components"""
        self.progress_tracker = ProgressTracker()
        self.badge_system = BadgeSystem()
        self.achievement_engine = AchievementEngine()
    
    def process_simulation_completion(
        self,
        user_stats: UserStats,
        simulation_id: str,
        perfect_score: bool = False,
        first_try: bool = False
    ) -> GamificationUpdate:
        """
        Process a simulation completion and award XP, badges, achievements
        
        Args:
            user_stats: User's current stats
            simulation_id: Simulation that was completed
            perfect_score: Whether user got perfect score
            first_try: Whether completed on first try
        
        Returns:
            Complete gamification update
        """
        old_xp = user_stats.total_xp
        
        # 1. Calculate XP reward
        xp_reward = self.progress_tracker.calculate_xp_reward(
            action=simulation_id,
            current_streak=user_stats.current_streak,
            perfect_score=perfect_score,
            first_try=first_try
        )
        
        new_xp = old_xp + xp_reward.total_xp
        
        # 2. Check for level up
        level_up_info = self.progress_tracker.check_level_up(old_xp, new_xp)
        
        # 3. Update completed simulations
        user_stats.completed_simulations.add(simulation_id)
        if perfect_score:
            user_stats.perfect_score_simulations.add(simulation_id)
        
        # 4. Check for badge unlocks
        user_data = self._build_user_data(user_stats, new_xp)
        badges_earned = self.badge_system.check_badge_unlocks(user_data)
        
        # Update earned badges
        for badge_award in badges_earned:
            user_stats.earned_badges.add(badge_award.badge.id)
        
        # 5. Check for achievements
        achievements_unlocked = self.achievement_engine.check_achievements(user_data)
        for achievement in achievements_unlocked:
            user_stats.earned_achievements.add(achievement.id)
            # Add achievement XP
            new_xp += achievement.reward_xp
        
        # 6. Check for new simulation unlocks
        new_level = self.progress_tracker.get_level_from_xp(new_xp)
        new_unlocks = self._check_new_unlocks(user_stats, new_level.value, new_xp)
        
        # 7. Update streak
        streak_update = self.progress_tracker.calculate_streak(
            user_stats.last_activity_date,
            datetime.now()
        )
        
        if streak_update["current_streak"] == "increment":
            user_stats.current_streak += 1
            user_stats.longest_streak = max(user_stats.current_streak, user_stats.longest_streak)
        elif streak_update["streak_broken"]:
            user_stats.current_streak = 1
        
        # Check for streak milestone rewards
        streak_rewards = self.progress_tracker.get_streak_milestone_rewards(user_stats.current_streak)
        for streak_reward in streak_rewards:
            new_xp += streak_reward.total_xp
        
        # 8. Update user stats
        user_stats.total_xp = new_xp
        user_stats.current_level = new_level
        user_stats.last_activity_date = datetime.now()
        
        # 9. Create progress snapshot
        snapshot = self.progress_tracker.create_progress_snapshot(
            user_id=user_stats.user_id,
            total_xp=new_xp,
            simulations_completed=len(user_stats.completed_simulations),
            badges_earned=len(user_stats.earned_badges),
            current_streak=user_stats.current_streak,
            longest_streak=user_stats.longest_streak,
            last_activity=user_stats.last_activity_date
        )
        
        return GamificationUpdate(
            xp_earned=xp_reward,
            level_up=level_up_info if level_up_info["leveled_up"] else None,
            badges_earned=badges_earned,
            achievements_unlocked=achievements_unlocked,
            new_unlocks=new_unlocks,
            streak_update=streak_update,
            updated_snapshot=snapshot
        )
    
    def process_activity(
        self,
        user_stats: UserStats,
        activity_type: str,
        custom_multiplier: float = 1.0
    ) -> GamificationUpdate:
        """
        Process non-simulation activities (daily login, AI tutor, etc.)
        
        Args:
            user_stats: User's current stats
            activity_type: Type of activity ("daily_login", "ai_tutor_question", etc.)
            custom_multiplier: Optional XP multiplier
        
        Returns:
            Gamification update
        """
        old_xp = user_stats.total_xp
        
        # Calculate XP
        xp_reward = self.progress_tracker.calculate_xp_reward(
            action=activity_type,
            current_streak=user_stats.current_streak,
            custom_multiplier=custom_multiplier
        )
        
        new_xp = old_xp + xp_reward.total_xp
        
        # Check level up
        level_up_info = self.progress_tracker.check_level_up(old_xp, new_xp)
        
        # Update specific counters
        if activity_type == "ai_tutor_question":
            user_stats.ai_questions_asked += 1
        elif activity_type == "goal_completed":
            user_stats.goals_completed += 1
        
        # Check badges and achievements
        user_data = self._build_user_data(user_stats, new_xp)
        badges_earned = self.badge_system.check_badge_unlocks(user_data)
        achievements_unlocked = self.achievement_engine.check_achievements(user_data)
        
        # Update earned items
        for badge_award in badges_earned:
            user_stats.earned_badges.add(badge_award.badge.id)
        for achievement in achievements_unlocked:
            user_stats.earned_achievements.add(achievement.id)
            new_xp += achievement.reward_xp
        
        # Update streak
        streak_update = self.progress_tracker.calculate_streak(
            user_stats.last_activity_date,
            datetime.now()
        )
        
        if streak_update["current_streak"] == "increment":
            user_stats.current_streak += 1
            user_stats.longest_streak = max(user_stats.current_streak, user_stats.longest_streak)
        elif streak_update["streak_broken"]:
            user_stats.current_streak = 1
        
        # Update stats
        new_level = self.progress_tracker.get_level_from_xp(new_xp)
        user_stats.total_xp = new_xp
        user_stats.current_level = new_level
        user_stats.last_activity_date = datetime.now()
        
        # Create snapshot
        snapshot = self.progress_tracker.create_progress_snapshot(
            user_id=user_stats.user_id,
            total_xp=new_xp,
            simulations_completed=len(user_stats.completed_simulations),
            badges_earned=len(user_stats.earned_badges),
            current_streak=user_stats.current_streak,
            longest_streak=user_stats.longest_streak,
            last_activity=user_stats.last_activity_date
        )
        
        return GamificationUpdate(
            xp_earned=xp_reward,
            level_up=level_up_info if level_up_info["leveled_up"] else None,
            badges_earned=badges_earned,
            achievements_unlocked=achievements_unlocked,
            new_unlocks=[],
            streak_update=streak_update,
            updated_snapshot=snapshot
        )
    
    def get_user_dashboard(self, user_stats: UserStats) -> Dict:
        """
        Get complete dashboard data for user
        
        Returns:
            Comprehensive dashboard with all gamification info
        """
        # Progress snapshot
        snapshot = self.progress_tracker.create_progress_snapshot(
            user_id=user_stats.user_id,
            total_xp=user_stats.total_xp,
            simulations_completed=len(user_stats.completed_simulations),
            badges_earned=len(user_stats.earned_badges),
            current_streak=user_stats.current_streak,
            longest_streak=user_stats.longest_streak,
            last_activity=user_stats.last_activity_date or datetime.now()
        )
        
        # Badge collection stats
        badge_stats = self.badge_system.get_badge_collection_stats(user_stats.earned_badges)
        
        # Next badges to earn
        user_data = self._build_user_data(user_stats, user_stats.total_xp)
        next_badges = self.badge_system.get_next_badges_to_earn(user_data, limit=3)
        
        # Unlocked simulations
        unlocked_sims = self.achievement_engine.get_unlocked_simulations(
            user_stats.current_level.value,
            user_stats.total_xp,
            user_stats.completed_simulations,
            user_stats.earned_badges
        )
        
        # Locked simulations
        locked_sims = self.achievement_engine.get_locked_simulations(
            user_stats.current_level.value,
            user_stats.total_xp,
            user_stats.completed_simulations,
            user_stats.earned_badges
        )
        
        # Learning path
        learning_path = self.achievement_engine.get_learning_path(
            user_stats.completed_simulations
        )
        
        # Recommended next steps
        next_steps = self.progress_tracker.get_recommended_next_steps(
            user_stats.current_level,
            list(user_stats.completed_simulations)
        )
        
        # Completion percentage
        completion_pct = self.achievement_engine.calculate_completion_percentage(
            user_stats.completed_simulations
        )
        
        return {
            "user_id": user_stats.user_id,
            "progress": {
                "level": snapshot.current_level.value,
                "level_name": self.progress_tracker.get_level_info(snapshot.current_level).name,
                "current_xp": snapshot.current_xp,
                "xp_to_next_level": snapshot.xp_to_next_level,
                "progress_percentage": snapshot.progress_percentage,
                "next_level": asdict(snapshot.next_level_info) if snapshot.next_level_info else None
            },
            "stats": {
                "simulations_completed": snapshot.total_simulations_completed,
                "badges_earned": snapshot.total_badges_earned,
                "current_streak": snapshot.current_streak,
                "longest_streak": snapshot.longest_streak,
                "completion_percentage": completion_pct
            },
            "badges": {
                "collection_stats": badge_stats,
                "next_to_earn": [
                    {
                        "badge": asdict(item["badge"]),
                        "progress": asdict(item["progress"]),
                        "hint": item["hint"]
                    }
                    for item in next_badges
                ]
            },
            "simulations": {
                "unlocked": [asdict(sim) for sim in unlocked_sims],
                "locked": [
                    {
                        "simulation": asdict(item["simulation"]),
                        "unlock_message": item["status"].unlock_message
                    }
                    for item in locked_sims
                ],
                "learning_path": learning_path
            },
            "recommendations": next_steps,
            "last_activity": snapshot.last_activity_date.isoformat()
        }
    
    def get_leaderboard_stats(self, user_stats: UserStats) -> Dict:
        """
        Get stats formatted for leaderboard
        
        Returns:
            Leaderboard-ready user stats
        """
        level_info = self.progress_tracker.get_level_info(user_stats.current_level)
        
        return {
            "user_id": user_stats.user_id,
            "total_xp": user_stats.total_xp,
            "level": user_stats.current_level.value,
            "level_name": level_info.name,
            "level_icon": level_info.icon,
            "simulations_completed": len(user_stats.completed_simulations),
            "badges_earned": len(user_stats.earned_badges),
            "current_streak": user_stats.current_streak,
            "longest_streak": user_stats.longest_streak,
            "completion_percentage": self.achievement_engine.calculate_completion_percentage(
                user_stats.completed_simulations
            )
        }
    
    def _build_user_data(self, user_stats: UserStats, total_xp: int) -> Dict:
        """Build user data dict for checking unlocks"""
        current_level = self.progress_tracker.get_level_from_xp(total_xp)
        
        return {
            "completed_simulations": list(user_stats.completed_simulations),
            "current_level": current_level.value,
            "current_streak": user_stats.current_streak,
            "total_simulations": len(user_stats.completed_simulations),
            "has_perfect_score": len(user_stats.perfect_score_simulations) > 0,
            "earned_badges": user_stats.earned_badges,
            "perfect_score_simulations": list(user_stats.perfect_score_simulations),
            "ai_questions_asked": user_stats.ai_questions_asked,
            "goals_completed": user_stats.goals_completed,
            "earned_achievements": user_stats.earned_achievements
        }
    
    def _check_new_unlocks(
        self,
        user_stats: UserStats,
        new_level: int,
        new_xp: int
    ) -> List[Dict]:
        """Check for newly unlocked simulations"""
        new_unlocks = []
        
        # Get all simulations
        for sim_id, simulation in self.achievement_engine.SIMULATIONS.items():
            # Skip if already completed
            if sim_id in user_stats.completed_simulations:
                continue
            
            # Check unlock status
            status = self.achievement_engine.check_simulation_unlock(
                sim_id,
                new_level,
                new_xp,
                user_stats.completed_simulations,
                user_stats.earned_badges
            )
            
            if status.unlocked:
                new_unlocks.append({
                    "simulation_id": sim_id,
                    "simulation_name": simulation.name,
                    "xp_reward": simulation.xp_reward,
                    "message": f"🎉 {simulation.name} is now unlocked!"
                })
        
        return new_unlocks
    
    def create_user_stats(self, user_id: int) -> UserStats:
        """Create new user stats (for new users)"""
        return UserStats(
            user_id=user_id,
            total_xp=0,
            current_level=Level.FINANCIAL_NEWBIE,
            completed_simulations=set(),
            earned_badges=set(),
            earned_achievements=set(),
            current_streak=0,
            longest_streak=0,
            last_activity_date=None,
            perfect_score_simulations=set(),
            ai_questions_asked=0,
            goals_completed=0
        )
    
    def get_all_levels_info(self) -> List[Dict]:
        """Get information about all levels"""
        levels = self.progress_tracker.get_all_levels()
        return [asdict(level) for level in levels]
    
    def get_all_badges_info(self) -> List[Dict]:
        """Get information about all badges"""
        badges = self.badge_system.get_all_badges()
        return [asdict(badge) for badge in badges]
    
    def simulate_user_journey(self, completed_simulations: List[str]) -> Dict:
        """
        Simulate a user's journey through simulations
        Useful for testing and demonstrations
        
        Args:
            completed_simulations: List of simulation IDs in order
        
        Returns:
            Journey summary with XP, levels, badges
        """
        user_stats = self.create_user_stats(user_id=1)
        journey = []
        
        for sim_id in completed_simulations:
            update = self.process_simulation_completion(user_stats, sim_id)
            
            journey.append({
                "simulation": sim_id,
                "xp_earned": update.xp_earned.total_xp,
                "total_xp": user_stats.total_xp,
                "level": user_stats.current_level.value,
                "badges_earned": [b.badge.name for b in update.badges_earned],
                "leveled_up": update.level_up is not None
            })
        
        return {
            "journey": journey,
            "final_stats": {
                "total_xp": user_stats.total_xp,
                "level": user_stats.current_level.value,
                "simulations_completed": len(user_stats.completed_simulations),
                "badges_earned": len(user_stats.earned_badges)
            }
        }
