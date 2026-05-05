"""
Gamification Database Models
All gamification-related models for achievements, streaks, sessions, etc.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, 
    Enum as SQLEnum, Boolean, JSON, Date, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum
from app.models.database import Base


class DifficultyLevel(str, Enum):
    """Game difficulty levels"""
    TUTORIAL = "tutorial"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"


class GameType(str, Enum):
    """Supported game types"""
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


class StreakType(str, Enum):
    """Types of streaks tracked"""
    DAILY_LOGIN = "daily_login"
    SIMULATION_PLAYS = "simulation_plays"
    GAME_PLAYS = "game_plays"
    ACHIEVEMENT_UNLOCKS = "achievement_unlocks"


class AchievementRarity(str, Enum):
    """Achievement rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


# ============================================================================
# SESSION TRACKING
# ============================================================================

class GameSession(Base):
    """Individual game session tracking"""
    __tablename__ = "game_sessions"
    __table_args__ = (UniqueConstraint('session_id', 'user_id'),)

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    game_type = Column(SQLEnum(GameType), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.NORMAL)
    
    # Timing
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, default=0.0)
    
    # Performance
    starting_capital = Column(Float, nullable=False)
    ending_capital = Column(Float, nullable=False)
    profit_loss = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Decision tracking
    total_decisions = Column(Integer, default=0)
    profitable_decisions = Column(Integer, default=0)
    losing_decisions = Column(Integer, default=0)
    decision_accuracy = Column(Float, default=0.0)
    average_decision_quality = Column(Float, default=0.0)
    
    # Learning metrics
    learning_improvement = Column(Float, default=0.0)
    win_streak = Column(Integer, default=0)
    loss_streak = Column(Integer, default=0)
    max_drawdown = Column(Float, default=0.0)
    
    # Rewards
    xp_earned = Column(Integer, default=0)
    achievement_unlocked = Column(String, nullable=True)
    
    # Status
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="game_sessions")
    decisions = relationship("GameDecision", back_populates="session")
    
    def __repr__(self):
        return f"<GameSession {self.session_id} ({self.game_type.value})>"


class GameDecision(Base):
    """Individual decisions made during a game session"""
    __tablename__ = "game_decisions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("game_sessions.session_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Decision details
    decision_type = Column(String, nullable=False)  # buy, sell, hold, allocate, etc.
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    outcome = Column(String, nullable=False)  # profitable, loss, neutral, pending
    amount = Column(Float, nullable=False)
    quality_score = Column(Float, default=0.0)  # 0.0-1.0
    
    # Additional data
    details = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("GameSession", back_populates="decisions")
    user = relationship("User")


# ============================================================================
# ACHIEVEMENTS & UNLOCKS
# ============================================================================

class Achievement(Base):
    """Achievement definition"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # trading, savings, investing, business, misc
    rarity = Column(SQLEnum(AchievementRarity), default=AchievementRarity.COMMON)
    xp_reward = Column(Integer, default=100)
    icon = Column(String, default="🏆")
    
    # Chain support
    chain_id = Column(String, nullable=True, index=True)
    prerequisites = Column(JSON, default=[])  # List of achievement IDs
    hidden = Column(Boolean, default=False)  # Secret achievement
    
    created_at = Column(DateTime, default=datetime.utcnow)


class UserAchievement(Base):
    """User's unlocked achievements"""
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint('user_id', 'achievement_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(String, ForeignKey("achievements.achievement_id"), nullable=False)
    
    unlocked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    shared = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")


# ============================================================================
# STREAKS & DAILY BONUSES
# ============================================================================

class UserStreak(Base):
    """User's current and historical streaks"""
    __tablename__ = "user_streaks"
    __table_args__ = (UniqueConstraint('user_id', 'streak_type'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    streak_type = Column(SQLEnum(StreakType), nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(Date, nullable=False, default=date.today)
    total_streak_days = Column(Integer, default=0)  # Total days ever in this streak
    
    milestones_reached = Column(JSON, default=[])  # [7, 14, 30, 100, etc.]
    total_bonus_xp_earned = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="streaks")


class DailyLoginBonus(Base):
    """Track daily login bonus claims"""
    __tablename__ = "daily_login_bonuses"
    __table_args__ = (UniqueConstraint('user_id', 'bonus_date'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    bonus_date = Column(Date, nullable=False, default=date.today)
    bonus_xp = Column(Integer, nullable=False)
    claimed_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# ============================================================================
# LEADERBOARDS & SOCIAL
# ============================================================================

class LeaderboardEntry(Base):
    """Leaderboard entries across different categories"""
    __tablename__ = "leaderboard_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String, nullable=False)  # total_xp, trading_score, etc.
    period = Column(String, nullable=False)  # daily, weekly, monthly, all_time
    rank = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    badge_count = Column(Integer, default=0)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")


class UserFriendship(Base):
    """Friend relationships between users"""
    __tablename__ = "user_friendships"
    __table_args__ = (UniqueConstraint('user_id', 'friend_id'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    friend = relationship("User", foreign_keys=[friend_id])


class SharedAchievement(Base):
    """Shared achievements in social feed"""
    __tablename__ = "shared_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(String, nullable=False)
    
    content_type = Column(String, default="achievement")  # achievement, milestone, score
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    data = Column(JSON, default={})
    share_url = Column(String, unique=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")


# ============================================================================
# DIFFICULTY & PROGRESSION
# ============================================================================

class UserDifficulty(Base):
    """Track user's difficulty preference per game"""
    __tablename__ = "user_difficulties"
    __table_args__ = (UniqueConstraint('user_id', 'game_type'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    game_type = Column(SQLEnum(GameType), nullable=False)
    
    current_difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.NORMAL)
    sessions_played = Column(Integer, default=0)
    average_performance = Column(Float, default=0.0)  # 0.0-1.0
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")


# ============================================================================
# CROSS-GAME & PORTFOLIO
# ============================================================================

class PersistentPortfolio(Base):
    """Portfolio that spans across games"""
    __tablename__ = "persistent_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    total_cash = Column(Float, default=0.0)
    total_invested = Column(Float, default=0.0)
    total_gains = Column(Float, default=0.0)
    
    # Holdings stored as JSON for flexibility
    holdings = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="persistent_portfolio")


class CareerMilestone(Base):
    """Track career progression milestones"""
    __tablename__ = "career_milestones"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    milestone_name = Column(String, nullable=False)
    game_type = Column(SQLEnum(GameType), nullable=False)
    xp_reward = Column(Integer, default=0)
    
    unlocked_game = Column(SQLEnum(GameType), nullable=True)  # Game unlocked by this milestone
    
    achieved_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")


# ============================================================================
# AI COMPETITION & STATS
# ============================================================================

class AICompetition(Base):
    """AI competition tracking"""
    __tablename__ = "ai_competitions"

    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    game_type = Column(SQLEnum(GameType), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.NORMAL)
    
    # Participants (AI IDs as JSON)
    ai_competitors = Column(JSON, default=[])
    player_rank = Column(Integer, nullable=True)
    player_score = Column(Float, nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")


# ============================================================================
# USER EXTENSIONS
# ============================================================================

class UserGamification(Base):
    """Extended user gamification profile"""
    __tablename__ = "user_gamifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Core stats
    total_xp = Column(Integer, default=0, index=True)
    level = Column(Integer, default=1)
    total_sessions = Column(Integer, default=0)
    lifetime_earnings = Column(Float, default=0.0)
    
    # Unlocked content
    games_unlocked = Column(JSON, default=[])  # List of GameType values
    
    # Preferences
    show_in_leaderboards = Column(Boolean, default=True)
    share_achievements = Column(Boolean, default=True)
    allow_friend_requests = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="gamification")
