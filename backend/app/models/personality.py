"""
Personality and Behavioral Psychology Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base


class UserPersonality(Base):
    """Financial personality profile"""
    __tablename__ = "user_personality"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Core dimension scores (0-10 scale)
    risk_tolerance = Column(Float, default=5.0)
    time_horizon = Column(Float, default=5.0)
    spending_trigger = Column(Float, default=5.0)  # emotional (low) vs rational (high)
    mindset = Column(Float, default=5.0)  # scarcity (low) vs abundance (high)
    decision_style = Column(Float, default=5.0)  # impulsive (low) vs analytical (high)
    stress_response = Column(Float, default=5.0)  # panic (low) vs calm (high)
    
    # Computed archetype
    personality_type = Column(String, nullable=False)  # cautious_planner, optimistic_risk_taker, etc.
    personality_name = Column(String, nullable=False)  # Display name
    description = Column(Text)
    
    # Assessment metadata
    confidence_score = Column(Float, default=0.5)  # How certain is the assessment
    quiz_completed = Column(Boolean, default=False)
    quiz_responses = Column(JSON)  # Store complete quiz responses
    
    # Insights
    strengths = Column(JSON)  # List of strengths
    challenges = Column(JSON)  # List of challenges
    learning_focus = Column(JSON)  # Recommended learning areas
    
    # Timestamps
    assessed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="personality")
    evolution_history = relationship("PersonalityEvolution", back_populates="personality", cascade="all, delete-orphan")


class PersonalityEvolution(Base):
    """Track how personality dimensions change over time"""
    __tablename__ = "personality_evolution"
    
    id = Column(Integer, primary_key=True, index=True)
    personality_id = Column(Integer, ForeignKey("user_personality.id"), nullable=False)
    
    # What changed
    dimension = Column(String, nullable=False)  # Which trait (risk_tolerance, etc.)
    old_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    change_amount = Column(Float, nullable=False)  # new - old
    
    # Why it changed
    trigger_simulation = Column(String)  # Which simulation caused the update
    trigger_behavior = Column(Text)  # What behavior was observed
    
    # When it changed
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    personality = relationship("UserPersonality", back_populates="evolution_history")


class BiasDetection(Base):
    """Track when behavioral biases are detected"""
    __tablename__ = "bias_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # What bias was detected
    bias_type = Column(String, nullable=False)  # loss_aversion, recency_bias, anchoring, etc.
    severity = Column(String, default="moderate")  # minor, moderate, significant
    
    # Context
    simulation_id = Column(String)  # Which simulation
    simulation_step = Column(Integer)  # Which step in simulation
    decision_context = Column(JSON)  # What they did
    
    # Feedback
    feedback_shown = Column(Text)  # What we told them
    teaching_provided = Column(Text)  # Educational content shown
    user_acknowledged = Column(Boolean, default=False)
    user_reaction = Column(String)  # helpful, not_helpful, dismissive
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="bias_detections")


class MindsetScore(Base):
    """Overall behavioral finance mindset scoring"""
    __tablename__ = "mindset_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Individual bias scores (lower is better - less affected by bias)
    loss_aversion_score = Column(Float, default=5.0)
    overconfidence_score = Column(Float, default=5.0)
    present_bias_score = Column(Float, default=5.0)
    mental_accounting_score = Column(Float, default=5.0)
    herd_mentality_score = Column(Float, default=5.0)
    anchoring_score = Column(Float, default=5.0)
    confirmation_bias_score = Column(Float, default=5.0)
    
    # Composite rationality score (0-100, higher is better)
    overall_rationality = Column(Float, default=50.0)
    
    # Progress tracking
    baseline_rationality = Column(Float)  # Initial score
    improvement_rate = Column(Float, default=0.0)  # % improvement over time
    
    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="mindset_score", uselist=False)


class ConfidenceTracking(Base):
    """Track user confidence vs actual competence"""
    __tablename__ = "confidence_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # The decision
    decision_id = Column(String, nullable=False)  # Unique identifier
    decision_type = Column(String)  # investment, spending, saving, etc.
    decision_context = Column(JSON)  # Details of the decision
    
    # Metacognition
    stated_confidence = Column(Integer, nullable=False)  # 0-100 user's confidence
    actual_correctness = Column(Float)  # 0-1 how correct they were
    calibration_gap = Column(Float)  # Difference between confidence and correctness
    
    # Feedback
    intervention_shown = Column(Text)  # If we warned them about overconfidence
    decision_changed = Column(Boolean, default=False)  # Did they change after warning
    final_outcome = Column(JSON)  # What actually happened
    
    # Timestamps
    decision_made_at = Column(DateTime, default=datetime.utcnow)
    outcome_recorded_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", backref="confidence_tracking")
