"""
Financial data models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.models.database import Base


class TransactionType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class Transaction(Base):
    """Transaction model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # debit, credit
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class Goal(Base):
    """Financial goal model"""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime)
    priority = Column(Integer, default=1)
    status = Column(String, default="active")  # active, completed, paused
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="goals")


class Budget(Base):
    """Budget model"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    budgeted_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="budgets")


class Conversation(Base):
    """AI conversation history"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    context = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")


# ============================================================================
# GULLAK GAME MODELS
# ============================================================================

class GullakSession(Base):
    """Gullak game session tracking"""
    __tablename__ = "gullak_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, nullable=False, index=True)

    # Game parameters
    income_type = Column(String, nullable=False)  # salaried, gig_work, business
    state_location = Column(String, default="other")  # Chosen state
    starting_age = Column(Integer, default=22)

    # Game progress
    current_month = Column(Integer, default=0)
    total_months = Column(Integer, default=120)  # 10 years

    # Financial state (stored as JSON)
    current_jars = Column(Text)  # JSON: {emergency, insurance, short_term, long_term, gold}
    jar_history = Column(Text)  # JSON array of monthly jar states

    # Game decisions
    decisions_made = Column(Text)  # JSON array of user allocation choices
    events_log = Column(Text)  # JSON array of life events encountered

    # Scores
    resilience_score = Column(Float, default=0.0)
    financial_health_index = Column(Text)  # JSON breakdown of score components

    # Status
    status = Column(String, default="active")  # active, completed, paused
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="gullak_sessions")
    events = relationship("GullakLifeEvent", back_populates="session", cascade="all, delete-orphan")


class GullakLifeEvent(Base):
    """Life events encountered in Gullak game"""
    __tablename__ = "gullak_life_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("gullak_sessions.session_id"), nullable=False)

    month = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)  # medical_emergency, wedding, etc.
    impact_amount = Column(Float, nullable=False)
    jar_affected = Column(String, nullable=True)  # emergency, insurance, etc.
    description = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("GullakSession", back_populates="events")


# ============================================================================
# SIP CHRONICLES GAME MODELS
# ============================================================================

class SIPSession(Base):
    """SIP Chronicles game session tracking"""
    __tablename__ = "sip_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, nullable=False, index=True)

    # Game config
    sip_type = Column(String, default="nifty_50")  # nifty_50, midcap_150, gold, elss
    monthly_sip = Column(Float, default=500)

    # Game progress
    current_month = Column(Integer, default=0)  # 0-456 (38 years)
    current_age = Column(Integer, default=22)

    # Financial state
    accumulated_wealth = Column(Float, default=0)
    total_contributions = Column(Float, default=0)

    # Game data (stored as JSON)
    contribution_history = Column(Text)  # JSON: monthly SIP amounts, upgrades
    interruptions_log = Column(Text)    # JSON: list of interruptions encountered
    monthly_snapshots = Column(Text)    # JSON: full history for charting

    # Scores
    final_corpus = Column(Float, default=0)
    hindsight_analysis = Column(Text)   # JSON: decisions_cost, best_decision
    tax_savings = Column(Float, default=0)  # ELSS specific
    financial_discipline_score = Column(Float, default=0)  # 0-100

    # Status
    status = Column(String, default="active")  # active, completed, paused
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sip_sessions")
    interruptions = relationship("SIPInterruption", back_populates="session", cascade="all, delete-orphan")
    decisions = relationship("SIPDecision", back_populates="session", cascade="all, delete-orphan")


class SIPInterruption(Base):
    """Interruptions encountered in SIP Chronicles game"""
    __tablename__ = "sip_interruptions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sip_sessions.session_id"), nullable=False)

    month = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    interruption_type = Column(String, nullable=False)  # salary_increase, market_crash, etc.
    description = Column(Text, nullable=False)
    options_presented = Column(Text)  # JSON: [{action, consequence_description}]
    player_choice = Column(String, nullable=True)  # Action player selected
    wealth_impact = Column(Float, default=0)  # Immediate wealth impact
    future_value_cost = Column(Float, default=0)  # Compounded cost to age 60

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("SIPSession", back_populates="interruptions")


class SIPDecision(Base):
    """Tracking of key decisions made during SIP game"""
    __tablename__ = "sip_decisions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sip_sessions.session_id"), nullable=False)

    month = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    decision_type = Column(String, nullable=False)  # continue, pause, upgrade, withdraw
    amount_involved = Column(Float, default=0)
    wealth_at_decision = Column(Float, nullable=False)
    optimal_wealth_at_decision = Column(Float, nullable=False)
    cost_at_age_60 = Column(Float, nullable=False)  # Hindsight calculation
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("SIPSession", back_populates="decisions")


# ============================================================================
# KAROBAAR GAME MODELS
# ============================================================================

class KarobarSession(Base):
    """Karobaar life simulation game session tracking"""
    __tablename__ = "karobaar_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, nullable=False, index=True)

    # Character parameters
    gender = Column(String, nullable=False)  # male, female
    city = Column(String, nullable=False)  # mumbai, bangalore, delhi, tier2
    education = Column(String, nullable=False)  # ug, pg, iit
    starting_job = Column(String, nullable=False)  # salaried, business, freelance

    # Game progress
    current_age = Column(Integer, default=22)
    current_month = Column(Integer, default=0)
    current_year = Column(Integer, default=0)

    # Current state (stored as JSON)
    current_state = Column(Text)  # Serialized LifeState

    # Game history (stored as JSON)
    yearly_snapshots = Column(Text)  # JSON array of yearly milestones
    decision_history = Column(Text)  # JSON array of decisions made
    events_log = Column(Text)  # JSON array of life events encountered

    # Current decision pending
    pending_decision = Column(Text)  # Serialized DecisionPoint or null

    # Final scores (when completed)
    career_score = Column(Float, nullable=True)
    financial_score = Column(Float, nullable=True)
    happiness_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    final_net_worth = Column(Float, nullable=True)
    final_salary = Column(Float, nullable=True)

    # Status
    status = Column(String, default="active")  # active, paused, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="karobaar_sessions")
    decisions = relationship("KarobarDecision", back_populates="session", cascade="all, delete-orphan")
    milestones = relationship("KarobarMilestone", back_populates="session", cascade="all, delete-orphan")


class KarobarDecision(Base):
    """Decisions made during Karobaar game"""
    __tablename__ = "karobaar_decisions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("karobaar_sessions.session_id"), nullable=False)

    age = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    decision_type = Column(String, nullable=False)  # career, marriage, investment, etc.
    description = Column(Text, nullable=False)

    # What player chose
    choice_index = Column(Integer, nullable=False)
    choice_text = Column(String, nullable=False)

    # Consequences applied
    salary_impact = Column(Float, default=0)
    happiness_impact = Column(Float, default=0)
    career_satisfaction_impact = Column(Float, default=0)
    wealth_impact = Column(Float, default=0)
    debt_impact = Column(Float, default=0)

    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("KarobarSession", back_populates="decisions")


class KarobarMilestone(Base):
    """Life milestones encountered during Karobaar game"""
    __tablename__ = "karobaar_milestones"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("karobaar_sessions.session_id"), nullable=False)

    age = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)  # marriage, promotion, child_birth, etc.
    description = Column(Text, nullable=False)
    financial_impact = Column(Float, default=0)
    happiness_impact = Column(Float, default=0)

    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("KarobarSession", back_populates="milestones")


# ============================================================================
# DALAL STREET GAME MODELS
# ============================================================================

class DalalSession(Base):
    """Dalal Street trading simulation game session tracking"""
    __tablename__ = "dalal_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, nullable=False, index=True)

    # Era selection
    era = Column(String, nullable=False)  # liberalization_1991_1996, dotcom_1997_2002, etc.

    # Game progress
    current_quarter = Column(Integer, default=0)  # 0-19
    is_completed = Column(Boolean, default=False)

    # Current portfolio state (stored as JSON)
    portfolio_json = Column(Text)  # Serialized Portfolio dataclass

    # Game history (stored as JSON)
    trades_history = Column(Text)  # JSON: List[Trade]
    news_events_log = Column(Text)  # JSON: List[NewsEvent]
    quarterly_snapshots = Column(Text)  # JSON: Portfolio values at each quarter
    decisions_log = Column(Text)  # JSON: Decisions shown and choices made

    # Final scores (when completed)
    starting_value = Column(Float, nullable=True)
    ending_value = Column(Float, nullable=True)
    total_profit_loss = Column(Float, nullable=True)
    return_percentage = Column(Float, nullable=True)
    market_comparison_return = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    timing_score = Column(Float, nullable=True)  # 0-100
    portfolio_management_score = Column(Float, nullable=True)  # 0-100
    risk_score = Column(Float, nullable=True)  # 0-100
    overall_score = Column(Float, nullable=True)  # 0-100

    # Status
    status = Column(String, default="active")  # active, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="dalal_sessions")
    trades = relationship("DalalTrade", back_populates="session", cascade="all, delete-orphan")
    news_events = relationship("DalalNewsEvent", back_populates="session", cascade="all, delete-orphan")


class DalalTrade(Base):
    """Individual trades executed during Dalal Street game"""
    __tablename__ = "dalal_trades"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("dalal_sessions.session_id"), nullable=False)

    quarter = Column(Integer, nullable=False)
    symbol = Column(String, nullable=False)
    trade_type = Column(String, nullable=False)  # buy, sell, hold
    quantity = Column(Integer, nullable=False)
    price_at_trade = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    profit_loss_if_sold_now = Column(Float, nullable=True)  # Calculated at game end

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("DalalSession", back_populates="trades")


class DalalNewsEvent(Base):
    """Market events/news that affect stock prices in Dalal Street game"""
    __tablename__ = "dalal_news_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("dalal_sessions.session_id"), nullable=False)

    quarter = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    description = Column(Text)
    affected_symbols = Column(String)  # JSON list of symbols
    price_impact_percentage = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("DalalSession", back_populates="news_events")


# ============================================================================
# BLACK SWAN GAME MODELS
# ============================================================================

class BlackSwanSession(Base):
    """Black Swan crisis simulation game session tracking"""
    __tablename__ = "black_swan_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, nullable=False, index=True)

    # Crisis + randomization
    crisis_type = Column(String, nullable=False)  # demonetization_2016, covid_2020, etc.
    player_profile_type = Column(String, nullable=False)  # conservative, moderate, aggressive, unprepared
    random_seed = Column(Integer, nullable=False)  # For deterministic randomization
    difficulty_level = Column(String, default="medium")  # easy, medium, hard

    # Game progress
    current_quarter = Column(Integer, default=0)
    current_phase = Column(String, default="pre_crisis")  # pre_crisis, onset, trough, recovery

    # Game state (stored as JSON)
    financial_profile = Column(Text)  # Starting portfolio
    quarterly_wealth_history = Column(Text)  # Array of wealth at each quarter
    market_index_history = Column(Text)  # Array of market index values
    decisions_made = Column(Text)  # JSON array of decisions

    # Final scores (when completed)
    starting_wealth = Column(Float, nullable=True)
    trough_wealth = Column(Float, nullable=True)
    final_wealth = Column(Float, nullable=True)
    antifragility_score = Column(Float, nullable=True)  # -100 to +100
    max_drawdown_pct = Column(Float, nullable=True)
    survival = Column(Boolean, default=True)
    overall_score = Column(Float, nullable=True)

    # Status
    status = Column(String, default="active")  # active, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="black_swan_sessions")
    decisions = relationship("BlackSwanDecision", back_populates="session", cascade="all, delete-orphan")


class BlackSwanDecision(Base):
    """Decisions made during Black Swan game"""
    __tablename__ = "black_swan_decisions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("black_swan_sessions.session_id"), nullable=False)

    quarter = Column(Integer, nullable=False)
    decision_context = Column(String, nullable=False)  # pre_crisis, crisis, recovery
    decision_type = Column(String, nullable=False)  # rebalance, hold, sell, buy_dip, default_loan
    asset_class = Column(String, nullable=False)  # equity, cash, real_estate, etc.
    amount = Column(Float, nullable=False)

    # Hindsight analysis
    optimal_action = Column(String, nullable=True)
    cost_of_error = Column(Float, default=0)  # If suboptimal, opportunity cost
    outcome_at_completion = Column(Float, default=0)  # Final impact

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("BlackSwanSession", back_populates="decisions")


class UserProfile(Base):
    """User financial profile from onboarding quiz"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Profile info
    age_group = Column(String, nullable=True)  # 18-24, 25-35, 35-50, 50+
    language = Column(String, default="en")  # en, hi, mr, ta, etc.

    # Quiz results (from AI Analysis)
    money_personality = Column(String, nullable=True)  # The Careful Builder, Ambitious Investor, Overwhelmed Earner, Smart Saver
    finance_iq_score = Column(Float, default=0.0)  # 0-100
    learning_gaps = Column(JSON, nullable=True)  # 3-5 priority topics as JSON
    recommended_first_sim = Column(String, nullable=True)  # e.g., "gullak"

    # Personality dimensions (0-10 scale, from Personality Assessment)
    risk_tolerance = Column(Float, default=5.0)
    time_horizon = Column(Float, default=5.0)
    spending_trigger = Column(Float, default=5.0)  # emotional (low) vs rational (high)
    mindset = Column(Float, default=5.0)  # scarcity (low) vs abundance (high)
    decision_style = Column(Float, default=5.0)  # impulsive (low) vs analytical (high)
    stress_response = Column(Float, default=5.0)  # panic (low) vs calm (high)

    # Personality archetype
    personality_type = Column(String, nullable=True)  # cautious_planner, optimistic_risk_taker, balanced_builder, anxious_avoider
    personality_name = Column(String, nullable=True)  # Display name (e.g., "Cautious Planner")
    personality_description = Column(String, nullable=True)  # Short description of archetype

    # Assessment metadata
    personality_confidence_score = Column(Float, default=0.5)  # 0-1, how certain is the assessment
    assessment_version = Column(Integer, default=1)  # Track quiz format changes
    last_assessment_date = Column(DateTime, nullable=True)

    # Onboarding status
    profile_setup_completed = Column(Boolean, default=False)
    quiz_completed = Column(Boolean, default=False)
    onboarding_completed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    quiz_responses = relationship("QuizResponse", back_populates="user_profile", cascade="all, delete-orphan")
    assessment_history = relationship("AssessmentHistory", back_populates="user_profile", cascade="all, delete-orphan")


class QuizResponse(Base):
    """User responses to onboarding quiz"""
    __tablename__ = "quiz_responses"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    # Quiz answers
    q1_goals = Column(String, nullable=False)  # Save, Invest, Pay debt, Build emergency fund
    q2_life_stage = Column(String, nullable=False)  # Student, First job, Mid-career, Business owner
    q3_knowledge = Column(Integer, nullable=False)  # 0-100 knowledge score from 3 options
    q4_risk_tolerance = Column(String, nullable=False)  # Conservative, Moderate, Aggressive
    q5_monthly_surplus = Column(Integer, nullable=False)  # 500, 2000, 5000, 10000+

    completed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_profile = relationship("UserProfile", back_populates="quiz_responses")


class ConversationMessage(Base):
    """AI Tutor conversation messages (persisted)"""
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Session management
    session_id = Column(String, nullable=False, index=True)  # Groups messages by conversation
    message_index = Column(Integer, nullable=False)  # Turn number in conversation

    # Message content
    user_message = Column(String, nullable=False)  # What user asked
    ai_response = Column(String, nullable=False)  # What AI answered
    ai_suggestions = Column(JSON, nullable=True)  # Follow-up suggestions offered
    ai_insights = Column(JSON, nullable=True)  # Extracted insights from response

    # Context and detection
    context_snapshot = Column(JSON, nullable=True)  # Context used to generate response
    detected_biases = Column(JSON, nullable=True)  # Biases detected in this exchange

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="conversation_messages")


class AssessmentHistory(Base):
    """Track assessment retakes and personality evolution"""
    __tablename__ = "assessment_history"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    # Assessment metadata
    assessment_version = Column(Integer, default=1)  # Which quiz version (1, 2, etc.)

    # Complete responses and scores
    quiz_responses = Column(JSON, nullable=False)  # All 20 quiz responses
    dimension_scores = Column(JSON, nullable=False)  # {risk_tolerance: 7.5, time_horizon: 6.2, ...}

    # Results
    personality_archetype = Column(String, nullable=False)  # cautious_planner, etc.
    confidence_score = Column(Float, nullable=False)  # 0-1

    # Evolution tracking
    previous_assessment_id = Column(Integer, ForeignKey("assessment_history.id"), nullable=True)
    change_summary = Column(JSON, nullable=True)  # {improved_dimensions: [...], declined_dimensions: [...]}

    # Timestamps
    completed_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user_profile = relationship("UserProfile", back_populates="assessment_history", foreign_keys=[profile_id])
    previous_assessment = relationship("AssessmentHistory", remote_side=[id], backref="next_assessment")


class UserProgress(Base):
    """User XP, level, and engagement tracking"""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # XP and level
    total_xp = Column(Integer, default=0)
    current_level = Column(Integer, default=1)  # 1-6 levels

    # Engagement
    current_streak = Column(Integer, default=0)  # Days of consecutive activity
    last_activity_date = Column(DateTime, nullable=True)

    # Activity counts
    simulations_completed = Column(Integer, default=0)
    games_completed = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])


# ============================================================================
# PAPER TRADING GAME MODELS
# ============================================================================

class PaperTradingMarket(str, Enum):
    """Market types for paper trading"""
    INDIA = "india"
    US = "us"
    BOTH = "both"


class PaperTradingStrategy(str, Enum):
    """Trading strategies"""
    PORTFOLIO_BUILDER = "portfolio_builder"
    DAY_TRADER = "day_trader"
    VALUE_INVESTOR = "value_investor"
    ETF_INVESTOR = "etf_investor"
    DIVERSIFIER = "diversifier"


class PaperTradingSession(Base):
    """Paper trading game session"""
    __tablename__ = "paper_trading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, nullable=False, index=True)

    # Game parameters
    market = Column(String, nullable=False)  # india, us, both
    strategy = Column(String, nullable=False)  # strategy type
    initial_capital = Column(Float, nullable=False)
    current_capital = Column(Float, nullable=False)

    # Time period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    current_date = Column(DateTime, nullable=False)

    # Portfolio state
    current_portfolio = Column(JSON, nullable=False)  # {holdings: {...}, cash: float, total_value: float}
    all_holdings = Column(JSON, nullable=False)  # Historical records of all holdings

    # Game status
    status = Column(String, default="active")  # active, completed, paused
    total_profit_loss = Column(Float, default=0.0)
    profit_loss_percentage = Column(Float, default=0.0)

    # Scoring
    portfolio_score = Column(Float, default=0.0)  # 0-30
    diversification_score = Column(Float, default=0.0)  # 0-25
    risk_adjusted_score = Column(Float, default=0.0)  # 0-20
    timing_score = Column(Float, default=0.0)  # 0-15
    adherence_score = Column(Float, default=0.0)  # 0-10
    total_score = Column(Float, default=0.0)  # 0-100

    # Metrics
    initial_holdings = Column(JSON, nullable=True)  # Initial positions
    final_wealth = Column(Float, nullable=True)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)  # Percentage of profitable trades

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="paper_trading_sessions")
    trades = relationship("PaperTrade", back_populates="session")
    snapshots = relationship("PaperPortfolioSnapshot", back_populates="session")
    events = relationship("PaperTradingEvent", back_populates="session")


class PaperTrade(Base):
    """Individual paper trade"""
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True, index=True)
    session_id_fk = Column(Integer, ForeignKey("paper_trading_sessions.id"), nullable=False)
    trade_id = Column(String, nullable=False, index=True)

    # Trade details
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    side = Column(String, nullable=False)  # BUY or SELL

    # Execution
    executed_at = Column(DateTime, nullable=False)
    commission = Column(Float, default=0.0)
    total_value = Column(Float, nullable=False)  # price * quantity

    # P&L (for sell orders)
    entry_price = Column(Float, nullable=True)  # Average entry price
    profit_loss = Column(Float, nullable=True)
    profit_loss_percentage = Column(Float, nullable=True)

    # Relationships
    session = relationship("PaperTradingSession", back_populates="trades")


class PaperPortfolioSnapshot(Base):
    """Daily portfolio snapshot for historical tracking"""
    __tablename__ = "paper_portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    session_id_fk = Column(Integer, ForeignKey("paper_trading_sessions.id"), nullable=False)

    # Snapshot date
    snapshot_date = Column(DateTime, nullable=False)

    # Holdings
    holdings = Column(JSON, nullable=False)  # [{symbol, qty, price}, ...]
    cash = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)

    # Daily performance
    daily_pnl = Column(Float, nullable=False)
    daily_pnl_percentage = Column(Float, nullable=False)

    # Relationships
    session = relationship("PaperTradingSession", back_populates="snapshots")


class PaperTradingEvent(Base):
    """Market events during paper trading"""
    __tablename__ = "paper_trading_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id_fk = Column(Integer, ForeignKey("paper_trading_sessions.id"), nullable=False)

    # Event details
    event_date = Column(DateTime, nullable=False)
    event_type = Column(String, nullable=False)  # market_crash, earnings_season, sector_rotation, etc.
    description = Column(Text, nullable=False)

    # Impact
    impact = Column(JSON, nullable=False)  # {affected_symbols: [symbols], sector: str, multiplier: float}

    # Relationships
    session = relationship("PaperTradingSession", back_populates="events")
