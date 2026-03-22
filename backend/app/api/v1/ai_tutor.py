"""
AI Tutor API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.core.security import get_current_active_user
from app.models.database import get_db
from app.models.user import User
from app.models.finance import Transaction, Goal
from app.schemas.schemas import AIMessage, AIResponse
from app.services.ai_tutor.service import ai_tutor_service
from app.services.ai_personalization_engine import ai_personalization_engine

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str = None  # Optional: for grouping conversations


@router.post("/chat", response_model=AIResponse)
async def chat_with_tutor(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Chat with AI financial tutor with rich personalized context"""

    # Use provided session_id or generate new one
    session_id = request.session_id or str(uuid.uuid4())

    # Inject personalization engine into AI Tutor if not already done
    ai_tutor_service.personalization_engine = ai_personalization_engine

    # Get AI response with full personalization
    response = await ai_tutor_service.get_response(
        message=request.message,
        user_id=current_user.id,
        session_id=session_id,
        db=db,
        user_context=None,  # Let personalization engine build the context
    )

    return AIResponse(**response)


@router.get("/suggestions")
async def get_suggestions(
    current_user: User = Depends(get_current_active_user),
):
    """Get personalized suggestions"""

    return {
        "suggestions": [
            "How can I save more money?",
            "Analyze my spending patterns",
            "Should I invest or pay off debt first?",
            "Help me create a budget",
        ]
    }


@router.get("/history/{session_id}")
async def get_conversation_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 10,
):
    """Get conversation history for a session"""
    messages = await ai_personalization_engine.get_conversation_history(
        db=db, user_id=current_user.id, session_id=session_id, limit=limit
    )

    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": [
            {
                "message_index": m.message_index,
                "user_message": m.user_message,
                "ai_response": m.ai_response,
                "suggestions": m.ai_suggestions,
                "detected_biases": m.detected_biases,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }
