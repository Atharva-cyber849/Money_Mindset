"""
User routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.models.database import get_db
from app.models.user import User
from app.models.finance import UserProfile, QuizResponse, UserProgress
from app.core.security import get_current_user
from app.schemas.schemas import UserResponse
from app.services.ai_analysis import analyze_financial_profile

router = APIRouter()


class ProfileSetupRequest(BaseModel):
    name: str
    age_group: str  # 18-24, 25-35, 35-50, 50+
    language: str = "en"


class QuizSubmissionRequest(BaseModel):
    q1_goals: str  # Save, Invest, Pay debt, Build emergency fund
    q2_life_stage: str  # Student, First job, Mid-career, Business owner
    q3_knowledge: int  # 0-100
    q4_risk_tolerance: str  # Conservative, Moderate, Aggressive
    q5_monthly_surplus: int  # 500, 2000, 5000, 10000+


class FinancialProfileResponse(BaseModel):
    money_personality: str
    finance_iq_score: float
    learning_gaps: Optional[List[str]]
    recommended_first_sim: str

    class Config:
        from_attributes = True


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user info"""
    return current_user


@router.post("/profile-setup")
async def setup_profile(
    request: ProfileSetupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Setup user profile with basic info"""

    # Get or create user profile
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not user_profile:
        user_profile = UserProfile(user_id=current_user.id)
        db.add(user_profile)

    # Update profile
    user_profile.age_group = request.age_group
    user_profile.language = request.language
    user_profile.profile_setup_completed = True

    # Update user name if provided
    if request.name:
        current_user.name = request.name

    db.commit()
    db.refresh(user_profile)

    return {
        "status": "success",
        "message": "Profile setup completed"
    }


@router.post("/quiz-submit")
async def submit_quiz(
    request: QuizSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit onboarding quiz and trigger AI analysis"""

    # Get or create user profile
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not user_profile:
        user_profile = UserProfile(user_id=current_user.id)
        db.add(user_profile)
        db.flush()

    # Store quiz response
    quiz_response = QuizResponse(
        profile_id=user_profile.id,
        q1_goals=request.q1_goals,
        q2_life_stage=request.q2_life_stage,
        q3_knowledge=request.q3_knowledge,
        q4_risk_tolerance=request.q4_risk_tolerance,
        q5_monthly_surplus=request.q5_monthly_surplus
    )
    db.add(quiz_response)
    db.flush()

    # Perform AI analysis
    try:
        analysis_result = await analyze_financial_profile(
            q1_goals=request.q1_goals,
            q2_life_stage=request.q2_life_stage,
            q3_knowledge=request.q3_knowledge,
            q4_risk_tolerance=request.q4_risk_tolerance,
            q5_monthly_surplus=request.q5_monthly_surplus
        )

        # Update profile with AI analysis results
        user_profile.money_personality = analysis_result["money_personality"]
        user_profile.finance_iq_score = analysis_result["finance_iq_score"]
        user_profile.learning_gaps = analysis_result["learning_gaps"]
        user_profile.recommended_first_sim = analysis_result["recommended_first_sim"]
        user_profile.quiz_completed = True
        user_profile.onboarding_completed = True

    except Exception as e:
        # If AI analysis fails, still mark quiz as completed
        user_profile.quiz_completed = True
        print(f"AI analysis failed: {str(e)}")

    db.commit()
    db.refresh(user_profile)

    return {
        "status": "success",
        "message": "Quiz submitted successfully",
        "profile": {
            "money_personality": user_profile.money_personality,
            "finance_iq_score": user_profile.finance_iq_score,
            "learning_gaps": user_profile.learning_gaps,
            "recommended_first_sim": user_profile.recommended_first_sim
        }
    }


@router.get("/financial-profile", response_model=FinancialProfileResponse)
async def get_financial_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's financial profile from onboarding"""

    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return user_profile


@router.get("/progress")
async def get_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress (XP, level, streak)"""

    user_progress = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).first()
    if not user_progress:
        # Create if doesn't exist
        user_progress = UserProgress(user_id=current_user.id)
        db.add(user_progress)
        db.commit()
        db.refresh(user_progress)

    return {
        "total_xp": user_progress.total_xp,
        "current_level": user_progress.current_level,
        "current_streak": user_progress.current_streak,
        "simulations_completed": user_progress.simulations_completed,
        "games_completed": user_progress.games_completed
    }
