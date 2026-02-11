"""
Personality Assessment API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.models.database import get_db
from app.models.user import User
from app.models.personality import UserPersonality, PersonalityEvolution
from app.services.personality.assessment import personality_assessment_service
from app.core.security import get_current_user


router = APIRouter()


# Pydantic schemas
class QuizResponse(BaseModel):
    question_id: str
    selected_option: int


class QuizSubmission(BaseModel):
    responses: List[QuizResponse]


class PersonalityProfileResponse(BaseModel):
    archetype: str
    archetype_name: str
    description: str
    strengths: List[str]
    challenges: List[str]
    learning_focus: List[str]
    strongest_dimension: Dict[str, Any]
    weakest_dimension: Dict[str, Any]
    dimension_scores: Dict[str, float]
    confidence_score: float
    assessed_at: datetime


class PersonalityEvolutionResponse(BaseModel):
    dimension: str
    old_value: float
    new_value: float
    change_amount: float
    trigger_simulation: str
    recorded_at: datetime


# Endpoints
@router.get("/quiz/questions")
async def get_quiz_questions():
    """Get all personality quiz questions"""
    return {
        "questions": personality_assessment_service.get_quiz_questions(),
        "total_questions": len(personality_assessment_service.QUIZ_QUESTIONS),
        "estimated_time_minutes": 5
    }


@router.post("/quiz/submit")
async def submit_quiz(
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit personality quiz responses and get personality profile
    """
    # Convert Pydantic models to dicts for processing
    responses = [
        {
            'question_id': r.question_id,
            'selected_option': r.selected_option
        }
        for r in submission.responses
    ]
    
    # Validate response count
    if len(responses) != len(personality_assessment_service.QUIZ_QUESTIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected {len(personality_assessment_service.QUIZ_QUESTIONS)} responses, got {len(responses)}"
        )
    
    # Run assessment
    insights = personality_assessment_service.assess_personality(responses)
    
    # Check if user already has a personality profile
    existing_profile = db.query(UserPersonality).filter(
        UserPersonality.user_id == current_user.id
    ).first()
    
    if existing_profile:
        # Update existing profile
        # Store evolution if dimensions changed significantly
        old_scores = {
            'risk_tolerance': existing_profile.risk_tolerance,
            'time_horizon': existing_profile.time_horizon,
            'spending_trigger': existing_profile.spending_trigger,
            'mindset': existing_profile.mindset,
            'decision_style': existing_profile.decision_style,
            'stress_response': existing_profile.stress_response
        }
        
        # Update profile
        existing_profile.risk_tolerance = insights['dimension_scores']['risk_tolerance']
        existing_profile.time_horizon = insights['dimension_scores']['time_horizon']
        existing_profile.spending_trigger = insights['dimension_scores']['spending_trigger']
        existing_profile.mindset = insights['dimension_scores']['mindset']
        existing_profile.decision_style = insights['dimension_scores']['decision_style']
        existing_profile.stress_response = insights['dimension_scores']['stress_response']
        existing_profile.personality_type = insights['archetype']
        existing_profile.personality_name = insights['archetype_name']
        existing_profile.description = insights['description']
        existing_profile.confidence_score = insights['confidence_score']
        existing_profile.quiz_completed = True
        existing_profile.quiz_responses = responses
        existing_profile.strengths = insights['strengths']
        existing_profile.challenges = insights['challenges']
        existing_profile.learning_focus = insights['learning_focus']
        existing_profile.updated_at = datetime.utcnow()
        
        # Record significant changes in evolution
        for dimension, new_score in insights['dimension_scores'].items():
            old_score = old_scores.get(dimension, 5.0)
            change = new_score - old_score
            
            # Only record if change is significant (> 1.5 points)
            if abs(change) > 1.5:
                evolution = PersonalityEvolution(
                    personality_id=existing_profile.id,
                    dimension=dimension,
                    old_value=old_score,
                    new_value=new_score,
                    change_amount=change,
                    trigger_simulation='personality_quiz',
                    trigger_behavior='Retook personality quiz'
                )
                db.add(evolution)
        
        db.commit()
        db.refresh(existing_profile)
        personality_profile = existing_profile
        
    else:
        # Create new profile
        personality_profile = UserPersonality(
            user_id=current_user.id,
            risk_tolerance=insights['dimension_scores']['risk_tolerance'],
            time_horizon=insights['dimension_scores']['time_horizon'],
            spending_trigger=insights['dimension_scores']['spending_trigger'],
            mindset=insights['dimension_scores']['mindset'],
            decision_style=insights['dimension_scores']['decision_style'],
            stress_response=insights['dimension_scores']['stress_response'],
            personality_type=insights['archetype'],
            personality_name=insights['archetype_name'],
            description=insights['description'],
            confidence_score=insights['confidence_score'],
            quiz_completed=True,
            quiz_responses=responses,
            strengths=insights['strengths'],
            challenges=insights['challenges'],
            learning_focus=insights['learning_focus']
        )
        
        db.add(personality_profile)
        db.commit()
        db.refresh(personality_profile)
    
    return {
        "success": True,
        "profile": {
            "archetype": personality_profile.personality_type,
            "archetype_name": personality_profile.personality_name,
            "description": personality_profile.description,
            "strengths": personality_profile.strengths,
            "challenges": personality_profile.challenges,
            "learning_focus": personality_profile.learning_focus,
            "strongest_dimension": insights['strongest_dimension'],
            "weakest_dimension": insights['weakest_dimension'],
            "dimension_scores": insights['dimension_scores'],
            "confidence_score": personality_profile.confidence_score,
            "assessed_at": personality_profile.assessed_at
        }
    }


@router.get("/profile")
async def get_personality_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current personality profile"""
    profile = db.query(UserPersonality).filter(
        UserPersonality.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personality profile not found. Please complete the quiz first."
        )
    
    return {
        "archetype": profile.personality_type,
        "archetype_name": profile.personality_name,
        "description": profile.description,
        "strengths": profile.strengths,
        "challenges": profile.challenges,
        "learning_focus": profile.learning_focus,
        "dimension_scores": {
            "risk_tolerance": profile.risk_tolerance,
            "time_horizon": profile.time_horizon,
            "spending_trigger": profile.spending_trigger,
            "mindset": profile.mindset,
            "decision_style": profile.decision_style,
            "stress_response": profile.stress_response
        },
        "confidence_score": profile.confidence_score,
        "quiz_completed": profile.quiz_completed,
        "assessed_at": profile.assessed_at,
        "updated_at": profile.updated_at
    }


@router.get("/evolution")
async def get_personality_evolution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history of personality changes over time"""
    profile = db.query(UserPersonality).filter(
        UserPersonality.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personality profile not found"
        )
    
    # Get all evolution records
    evolution_records = db.query(PersonalityEvolution).filter(
        PersonalityEvolution.personality_id == profile.id
    ).order_by(PersonalityEvolution.recorded_at.desc()).all()
    
    return {
        "total_changes": len(evolution_records),
        "evolution_history": [
            {
                "dimension": record.dimension,
                "old_value": record.old_value,
                "new_value": record.new_value,
                "change_amount": record.change_amount,
                "trigger_simulation": record.trigger_simulation,
                "trigger_behavior": record.trigger_behavior,
                "recorded_at": record.recorded_at
            }
            for record in evolution_records
        ]
    }


@router.get("/archetypes")
async def get_all_archetypes():
    """Get information about all personality archetypes"""
    return {
        "archetypes": {
            name: {
                "name": name.replace('_', ' ').title(),
                "description": info['description'],
                "strengths": info['strengths'],
                "challenges": info['challenges'],
                "learning_focus": info['learning_focus']
            }
            for name, info in personality_assessment_service.ARCHETYPES.items()
        }
    }
