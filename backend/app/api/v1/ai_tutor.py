"""
AI Tutor API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.models.database import get_db
from app.models.user import User
from app.models.finance import Transaction, Goal
from app.schemas.schemas import AIMessage, AIResponse
from app.services.ai_tutor.service import ai_tutor_service

router = APIRouter()


@router.post("/chat", response_model=AIResponse)
async def chat_with_tutor(
    message: AIMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with AI financial tutor"""
    
    # Build user context
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.date.desc()).limit(100).all()
    
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == "active"
    ).all()
    
    # Calculate spending
    total_spending = sum(abs(t.amount) for t in transactions if t.transaction_type == "debit")
    
    context = {
        "user": {
            "name": current_user.name,
            "age": current_user.age,
            "occupation": current_user.occupation,
            "monthly_income": current_user.monthly_income,
            "financial_knowledge": current_user.financial_knowledge
        },
        "spending": {
            "total": total_spending,
            "transaction_count": len(transactions)
        },
        "goals": [
            {
                "name": g.name,
                "target": g.target_amount,
                "current": g.current_amount
            } for g in goals
        ]
    }
    
    # Get AI response
    response = await ai_tutor_service.get_response(
        message=message.message,
        user_context=context
    )
    
    return AIResponse(**response)


@router.get("/suggestions")
async def get_suggestions(
    current_user: User = Depends(get_current_active_user)
):
    """Get personalized suggestions"""
    
    return {
        "suggestions": [
            "How can I save more money?",
            "Analyze my spending patterns",
            "Should I invest or pay off debt first?",
            "Help me create a budget"
        ]
    }
