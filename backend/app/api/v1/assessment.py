"""
Unified Assessment API routes
Consolidates AI Analysis + Personality Assessment
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid

from app.core.security import get_current_active_user
from app.models.database import get_db
from app.models.user import User
from app.models.finance import UserProfile, AssessmentHistory
from app.services.ai_personalization_engine import ai_personalization_engine
from pydantic import BaseModel

router = APIRouter()


class QuizResponse(BaseModel):
    question_id: str
    selected_option: int


class ComprehensiveAssessmentRequest(BaseModel):
    quiz_responses: List[QuizResponse]


class AssessmentResult(BaseModel):
    money_personality: str
    finance_iq_score: float
    learning_gaps: List[str]
    recommended_first_sim: str
    personality_type: str
    personality_name: str
    personality_description: str
    dimension_scores: Dict[str, float]
    confidence_score: float
    strengths: List[str]
    challenges: List[str]
    learning_focus: List[str]


@router.post("/comprehensive-submit", response_model=AssessmentResult)
async def submit_comprehensive_assessment(
    request: ComprehensiveAssessmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Submit comprehensive 20-question assessment
    Combines AI Analysis (5 questions) + Personality Assessment (15 questions)

    Returns:
        Unified assessment result with personality type, dimensions, and recommendations
    """
    try:
        # Convert to list of dicts
        responses = [
            {"question_id": r.question_id, "selected_option": r.selected_option}
            for r in request.quiz_responses
        ]

        # Run comprehensive assessment
        result = await ai_personalization_engine.run_comprehensive_assessment(
            db=db, user_id=current_user.id, quiz_responses=responses
        )

        return AssessmentResult(**result)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Assessment failed: {str(e)}")


@router.get("/history/{user_id}")
async def get_assessment_history(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get assessment history for a user (evolution tracking)"""
    # Security: users can only see their own history
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user_profile:
        return {"assessments": []}

    assessments = (
        db.query(AssessmentHistory)
        .filter(AssessmentHistory.profile_id == user_profile.id)
        .order_by(AssessmentHistory.completed_at.desc())
        .all()
    )

    return {
        "total_assessments": len(assessments),
        "assessments": [
            {
                "id": a.id,
                "completed_at": a.completed_at.isoformat(),
                "archetype": a.personality_archetype,
                "confidence_score": a.confidence_score,
                "dimension_scores": a.dimension_scores,
                "change_summary": a.change_summary,
            }
            for a in assessments
        ],
    }


@router.get("/profile")
async def get_current_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current unified assessment profile"""
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not user_profile:
        return {"message": "No assessment completed yet"}

    return {
        "money_personality": user_profile.money_personality,
        "finance_iq_score": user_profile.finance_iq_score,
        "learning_gaps": user_profile.learning_gaps,
        "recommended_first_sim": user_profile.recommended_first_sim,
        "personality_type": user_profile.personality_type,
        "personality_name": user_profile.personality_name,
        "personality_description": user_profile.personality_description,
        "dimension_scores": {
            "risk_tolerance": user_profile.risk_tolerance,
            "time_horizon": user_profile.time_horizon,
            "spending_trigger": user_profile.spending_trigger,
            "mindset": user_profile.mindset,
            "decision_style": user_profile.decision_style,
            "stress_response": user_profile.stress_response,
        },
        "confidence_score": user_profile.personality_confidence_score,
        "last_assessment_date": user_profile.last_assessment_date.isoformat()
        if user_profile.last_assessment_date
        else None,
    }


@router.post("/retake")
async def retake_assessment(
    request: ComprehensiveAssessmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retake comprehensive assessment to track evolution
    Compares with previous assessment and shows changes
    """
    try:
        # Run new assessment
        result = await ai_personalization_engine.run_comprehensive_assessment(
            db=db,
            user_id=current_user.id,
            quiz_responses=[
                {"question_id": r.question_id, "selected_option": r.selected_option}
                for r in request.quiz_responses
            ],
        )

        # Get comparison with previous assessment
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        comparison = await ai_personalization_engine.compare_assessments(db, current_user.id)

        return {
            "new_assessment": AssessmentResult(**result).dict(),
            "comparison": comparison,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Retake failed: {str(e)}")
