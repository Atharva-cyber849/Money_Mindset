"""
Complete Gamification System Integration
Orchestrates all gamification components for unified experience
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from app.services.gamification.difficulty_engine import (
    AdaptiveDifficultyEngine,
    DifficultyLevel,
    PerformanceMetrics,
)
from app.services.gamification.daily_bonus_system import (
    DailyBonusSystem,
    StreakType,
)
from app.services.gamification.achievement_chains import (
    AchievementChainSystem,
    Achievement,
)
from app.services.gamification.cross_game_features import (
    CrossGameFeatures,
    GameType,
)
from app.services.gamification.social_system import (
    SocialSystem,
    LeaderboardCategory,
    LeaderboardPeriod,
)
from app.services.gamification.ai_opponents import (
    AICompetitionEngine,
    AIPersonality,
)
from app.services.gamification.session_analytics import (
    SessionAnalytics,
    DecisionType,
)


class ComprehensiveGamificationSystem:
    """
    Main orchestrator for the complete gamification system
    Integrates difficulty, streaks, achievements, cross-game features,
    social systems, AI opponents, and analytics
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # Core systems
        self.difficulty_engine = AdaptiveDifficultyEngine()
        self.bonus_system = DailyBonusSystem()
        self.achievement_system = AchievementChainSystem()
        self.cross_game = CrossGameFeatures(user_id)
        self.social_system = SocialSystem()
        self.ai_engine = AICompetitionEngine()
        self.session_analytics = SessionAnalytics()
        
        # Initialize social systems
        self.social_system.create_leaderboards()
        
        # User state
        self.current_difficulty: Dict[str, DifficultyLevel] = {}
        self.unlocked_achievements: set = set()
        self.user_stats: Dict[str, Any] = {
            "total_xp": 0,
            "level": 1,
            "total_sessions": 0,
            "lifetime_earnings": 0.0,
        }

    # ============================================================================
    # GAME SESSION LIFECYCLE
    # ============================================================================

    def start_game_session(
        self,
        session_id: str,
        game_type: str,
        requested_difficulty: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initialize a new game session with all gamification hooks
        
        Returns session config with difficulty modifiers, difficulty tutorialif needed, etc.
        """
        # Determine difficulty
        game_key = f"{game_type}_difficulty"
        
        if requested_difficulty:
            difficulty = DifficultyLevel(requested_difficulty)
        else:
            difficulty = self.current_difficulty.get(
                game_key, DifficultyLevel.NORMAL
            )
        
        # Get modifiers
        modifiers = self.difficulty_engine.get_dynamic_parameters(
            difficulty,
            self.user_stats.get(f"{game_type}_sessions_played", 0),
        )
        
        # Get tutorial if needed
        tutorial = None
        if difficulty == DifficultyLevel.TUTORIAL:
            tutorial = self.difficulty_engine.get_tutorial_content(game_type)
        
        # Start analytics session
        starting_capital = modifiers.starting_capital_ratio * 1000000
        analytics_session = self.session_analytics.start_session(
            session_id, self.user_id, game_type, difficulty.value, starting_capital
        )
        
        # Record daily activity for streaks
        activity_result = self.bonus_system.record_activity(
            self.user_id, "game_play", game_type
        )
        
        # Get next milestone for motivation
        next_milestone = self.bonus_system.get_next_milestone(
            self.user_id, StreakType.GAME_PLAYS.value
        )
        
        return {
            "session_id": session_id,
            "difficulty": difficulty.value,
            "modifiers": {
                "market_volatility": modifiers.market_volatility,
                "ai_aggressiveness": modifiers.ai_aggressiveness,
                "time_pressure": modifiers.time_pressure,
                "mistake_tolerance": modifiers.mistake_tolerance,
                "xp_multiplier": modifiers.xp_multiplier,
                "hint_availability": modifiers.hint_availability,
                "starting_capital": starting_capital,
                "event_frequency": modifiers.event_frequency,
            },
            "tutorial": tutorial,
            "daily_bonus_xp": activity_result.get("streak_bonus_xp", 0),
            "current_streak": self.bonus_system.user_streaks.get(
                self.user_id, {}
            ).get(StreakType.GAME_PLAYS.value, {}).current_streak
            if self.user_id in self.bonus_system.user_streaks
            else 0,
            "next_milestone": next_milestone,
            "recommended_difficulty": (
                self._recommend_difficulty_adjustment(game_type)
            ),
        }

    def end_game_session(
        self,
        session_id: str,
        game_type: str,
        ending_capital: float,
        performance_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        End a game session and calculate all rewards/unlocks
        
        Returns XP earned, achievements unlocked, difficulty recommendation, etc.
        """
        
        # Calculate session analytics
        session_summary = self.session_analytics.end_session(
            session_id, ending_capital, session_xp=0
        )
        
        # Calculate performance score
        perf_metrics = PerformanceMetrics(
            profit_loss=session_summary.profit_loss,
            win_rate=performance_metrics.get("win_rate", 0),
            decision_quality=performance_metrics.get("decision_quality", 0),
            speed=performance_metrics.get("decisions_per_minute", 0),
            accuracy=performance_metrics.get("accuracy", 0),
            loss_streak=session_summary.loss_streak,
            win_streak=session_summary.win_streak,
            average_session_duration=session_summary.duration_minutes,
        )
        
        performance_score = self.difficulty_engine.calculate_performance_score(
            perf_metrics
        )
        
        # Recommend difficulty adjustment
        game_sessions_count = self.user_stats.get(f"{game_type}_sessions_played", 0)
        recommended_difficulty = self.difficulty_engine.recommend_difficulty(
            self.current_difficulty.get(f"{game_type}_difficulty", DifficultyLevel.NORMAL),
            performance_score,
            game_sessions_count,
        )
        
        # Calculate XP rewards
        base_xp = 100 + (session_summary.roi * 10)  # ROI-based bonus
        difficulty_multiplier = self.difficulty_engine.get_dynamic_parameters(
            self.current_difficulty.get(f"{game_type}_difficulty", DifficultyLevel.NORMAL),
            game_sessions_count,
        ).xp_multiplier
        streak_bonus = self.bonus_system.record_activity(
            self.user_id, "game_play", game_type
        )["streak_bonus_xp"]
        compound_bonus = self.cross_game.compound_rewards.calculate_compound_bonus(
            GameType(game_type), performance_metrics
        )
        
        total_xp = int(
            (base_xp * difficulty_multiplier * compound_bonus["xp_multiplier"])
            + streak_bonus
        )
        
        # Check for achievements
        unlocked_achievements = []
        if performance_score > 0.85:
            # Check if achievement-triggering condition met
            achievement = self.achievement_system.get_achievement("expert_trader")
            if achievement and "expert_trader" not in self.unlocked_achievements:
                unlocked_achievements.append(achievement)
                self.unlocked_achievements.add("expert_trader")
        
        # Update user stats
        self.user_stats["total_xp"] += total_xp
        self.user_stats["total_sessions"] += 1
        self.user_stats["lifetime_earnings"] += session_summary.profit_loss
        self.user_stats[f"{game_type}_sessions_played"] = game_sessions_count + 1
        self.user_stats["level"] = 1 + (self.user_stats["total_xp"] // 1000)
        
        # Update difficulty preference
        self.current_difficulty[f"{game_type}_difficulty"] = recommended_difficulty
        
        # Update leaderboards
        self.social_system.update_user_leaderboard(
            self.user_id,
            "Player",  # Would be actual username from user profile
            LeaderboardCategory.TRADING_SCORE,
            total_xp,
            len(self.unlocked_achievements),
        )
        
        # Get career recommendations
        career_recommendations = self.cross_game.get_career_recommendations()
        
        return {
            "xp_earned": total_xp,
            "base_xp": int(base_xp),
            "difficulty_multiplier": difficulty_multiplier,
            "streak_bonus": streak_bonus,
            "compound_bonus": compound_bonus.get("insights", []),
            "new_level": self.user_stats["level"],
            "achievements_unlocked": [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "xp_reward": a.xp_reward,
                    "rarity": a.rarity.value,
                }
                for a in unlocked_achievements
            ],
            "difficulty_recommendation": recommended_difficulty.value,
            "performance_score": round(performance_score, 2),
            "session_summary": session_summary,
            "career_recommendations": career_recommendations,
            "next_milestone": self.bonus_system.get_next_milestone(
                self.user_id, StreakType.GAME_PLAYS.value
            ),
        }

    # ============================================================================
    # DIFFICULTY & PROGRESSION
    # ============================================================================

    def get_difficulty_recommendation(self, game_type: str) -> Dict[str, Any]:
        """Get personalized difficulty recommendation"""
        game_key = f"{game_type}_difficulty"
        current = self.current_difficulty.get(game_key, DifficultyLevel.NORMAL)
        
        recent_sessions = [
            s for s in self.session_analytics.sessions.values()
            if s.game_type == game_type and s.completed
        ]
        
        if not recent_sessions:
            return {
                "current": current.value,
                "recommendation": DifficultyLevel.EASY.value,
                "reason": "New to this game - start with Easy",
            }
        
        avg_roi = sum(s.roi for s in recent_sessions[-5:]) / min(5, len(recent_sessions))
        
        if avg_roi > 50:
            return {
                "current": current.value,
                "recommendation": DifficultyLevel.HARD.value,
                "reason": "You're mastering this difficulty!",
            }
        elif avg_roi < -10:
            return {
                "current": current.value,
                "recommendation": DifficultyLevel.EASY.value,
                "reason": "Try easier difficulty to rebuild confidence",
            }
        
        return {
            "current": current.value,
            "recommendation": current.value,
            "reason": "You're doing great at this level!",
        }

    def _recommend_difficulty_adjustment(self, game_type: str) -> Optional[str]:
        """Internal helper to recommend difficulty"""
        rec = self.get_difficulty_recommendation(game_type)
        return rec.get("recommendation")

    # ============================================================================
    # ACHIEVEMENTS & UNLOCKS
    # ============================================================================

    def get_achievement_progress(self) -> Dict[str, Any]:
        """Get all achievement chains and progress"""
        chain_progress = self.achievement_system.get_user_chain_progress(
            self.unlocked_achievements
        )
        
        next_achievements = self.achievement_system.get_next_achievements(
            self.unlocked_achievements
        )
        
        return {
            "total_unlocked": len(self.unlocked_achievements),
            "chains": chain_progress,
            "next_possible_achievements": [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "category": a.category,
                    "rarity": a.rarity.value,
                    "xp_reward": a.xp_reward,
                }
                for a in next_achievements[:5]  # Top 5
            ],
        }

    def unlock_achievement(self, achievement_id: str) -> Optional[Dict]:
        """Unlock an achievement"""
        if achievement_id in self.unlocked_achievements:
            return None
        
        achievement = self.achievement_system.get_achievement(achievement_id)
        if not achievement:
            return None
        
        # Check prerequisites
        if not self.achievement_system.can_unlock_achievement(
            achievement_id, self.unlocked_achievements
        ):
            return None
        
        self.unlocked_achievements.add(achievement_id)
        self.user_stats["total_xp"] += achievement.xp_reward
        
        return {
            "achievement_id": achievement_id,
            "name": achievement.name,
            "xp_reward": achievement.xp_reward,
            "description": achievement.description,
        }

    # ============================================================================
    # STREAKS & DAILY BONUSES
    # ============================================================================

    def claim_daily_login_bonus(self) -> Dict[str, Any]:
        """Claim daily login bonus"""
        bonus = self.bonus_system.get_daily_login_bonus(self.user_id)
        
        if bonus["can_claim"]:
            self.user_stats["total_xp"] += bonus["bonus_xp"]
        
        return bonus

    def get_streak_status(self) -> Dict[str, Any]:
        """Get all active streaks"""
        return self.bonus_system.get_user_total_streaks(self.user_id)

    # ============================================================================
    # SOCIAL & LEADERBOARDS
    # ============================================================================

    def get_leaderboard(
        self,
        category: str,
        period: str = "all_time",
        view: str = "top",
    ) -> Dict:
        """Get leaderboard"""
        return self.social_system.get_leaderboard(
            LeaderboardCategory(category),
            LeaderboardPeriod(period),
            view,
            self.user_id,
        )

    def share_achievement(self, achievement_id: str) -> Optional[Dict]:
        """Share an achievement with friends"""
        achievement = self.achievement_system.get_achievement(achievement_id)
        if not achievement:
            return None
        
        # Convert to shareable format
        shareable_achievement = Achievement(
            id=achievement.id,
            name=achievement.name,
            icon="🏆",
            description=achievement.description,
            unlocked_date=datetime.now(),
        )
        
        result = self.social_system.share_achievement(
            self.user_id, shareable_achievement
        )
        
        return {
            "share_url": result.share_url,
            "title": result.title,
            "description": result.description,
        }

    def get_social_feed(self) -> List[Dict]:
        """Get social feed from friends"""
        return self.social_system.get_shared_feed(self.user_id)

    # ============================================================================
    # AI COMPETITIONS
    # ============================================================================

    def start_ai_competition(
        self,
        competition_id: str,
        game_type: str,
        difficulty: str,
    ) -> List[Dict]:
        """Start competition with AI opponents"""
        ai_competitors = self.ai_engine.start_competition(
            competition_id, game_type, difficulty
        )
        
        return [
            {
                "ai_id": ai.ai_id,
                "name": ai.name,
                "personality": ai.personality.value,
                "skill_level": ai.skill_level,
            }
            for ai in ai_competitors
        ]

    # ============================================================================
    # ANALYTICS & REPORTING
    # ============================================================================

    def get_session_insights(self, session_id: str) -> Dict:
        """Get detailed insights from a session"""
        return self.session_analytics.get_session_summary(session_id)

    def get_learning_curve(self, game_type: str) -> Dict:
        """Get learning curve analysis"""
        return self.session_analytics.get_learning_insights(
            self.user_id, game_type
        )

    def generate_session_report(self, session_id: str) -> str:
        """Generate PDF report for session"""
        return self.session_analytics.generate_pdf_report(session_id)

    # ============================================================================
    # COMPOUND REWARDS & CROSS-GAME
    # ============================================================================

    def get_cross_game_summary(self) -> Dict[str, Any]:
        """Get comprehensive cross-game summary"""
        return self.cross_game.get_cross_game_summary()

    def get_user_dashboard(self) -> Dict[str, Any]:
        """Get complete user dashboard with all gamification data"""
        return {
            "user_stats": self.user_stats,
            "current_streaks": self.bonus_system.get_user_total_streaks(
                self.user_id
            ),
            "achievement_progress": self.get_achievement_progress(),
            "cross_game_summary": self.get_cross_game_summary(),
            "upcoming_challenges": self._get_upcoming_challenges(),
            "leaderboard_position": self._get_leaderboard_position(),
            "recommendations": self._get_personalized_recommendations(),
        }

    def _get_upcoming_challenges(self) -> List[Dict]:
        """Get upcoming seasonal challenges"""
        return [
            {
                "name": "Diwali Savings Race",
                "description": "Save ₹50,000 in one week",
                "reward_xp": 1000,
                "active": True,
            },
            {
                "name": "Tax Season Planning",
                "description": "Optimize your investments for taxes",
                "reward_xp": 800,
                "active": False,
            },
        ]

    def _get_leaderboard_position(self) -> Dict:
        """Get user's current leaderboard position"""
        for category in [
            LeaderboardCategory.TOTAL_XP,
            LeaderboardCategory.ACHIEVEMENT_COLLECTOR,
        ]:
            leaderboard = self.social_system.get_leaderboard(
                category, LeaderboardPeriod.MONTHLY, "nearby", self.user_id
            )
            if leaderboard.get("entries"):
                for entry in leaderboard["entries"]:
                    if entry["username"] == self.user_id:
                        return {
                            "category": category.value,
                            "rank": entry["rank"],
                            "score": entry["score"],
                        }
        
        return {"rank": "N/A", "category": "all_time", "score": self.user_stats["total_xp"]}

    def _get_personalized_recommendations(self) -> List[str]:
        """Get personalized recommendations for user"""
        recommendations = []
        
        if self.user_stats["total_sessions"] < 5:
            recommendations.append(
                "🎓 Complete 5 games to unlock advanced features"
            )
        
        if self.user_stats["total_xp"] < 500:
            recommendations.append("📈 Earn 500 XP to reach level 2")
        
        streaks = self.get_streak_status()
        if streaks.get(StreakType.DAILY_LOGIN.value, {}).get("current_streak", 0) < 7:
            recommendations.append("🔥 Build a 7-day login streak for bonus XP")
        
        return recommendations
