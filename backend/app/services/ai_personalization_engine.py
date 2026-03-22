"""
Unified AI Personalization Engine
Consolidates AI Analysis + Personality Assessment + Bias Detection
Provides rich context for AI Tutor
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.finance import UserProfile, ConversationMessage, AssessmentHistory
from app.models.user import User
from app.services.personality.assessment import FinancialPersonalityAssessment
import anthropic
import json
import os


class AIPersonalizationEngine:
    """Unified AI personalization service"""

    def __init__(self):
        self.personality_assessment = FinancialPersonalityAssessment()
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def run_comprehensive_assessment(
        self,
        db: Session,
        user_id: int,
        quiz_responses: List[Dict]  # All 20 quiz responses
    ) -> Dict[str, Any]:
        """
        Run unified assessment combining AI Analysis + Personality Assessment

        Args:
            db: Database session
            user_id: User ID
            quiz_responses: List of {question_id, selected_option} for all 20 questions

        Returns:
            Unified assessment result with all dimensions, archetype, and recommendations
        """
        # Extract AI Analysis responses (questions 1-5)
        ai_analysis_responses = {
            "q1_goals": next((r["selected_option"] for r in quiz_responses if r["question_id"] == "q1"), None),
            "q2_life_stage": next((r["selected_option"] for r in quiz_responses if r["question_id"] == "q2"), None),
            "q3_knowledge": next((r["selected_option"] for r in quiz_responses if r["question_id"] == "q3"), None),
            "q4_risk_tolerance": next((r["selected_option"] for r in quiz_responses if r["question_id"] == "q4"), None),
            "q5_monthly_surplus": next((r["selected_option"] for r in quiz_responses if r["question_id"] == "q5"), None),
        }

        # Get AI Analysis results (uses Claude)
        ai_analysis_result = await self._analyze_financial_profile_internal(ai_analysis_responses)

        # Calculate personality dimensions (uses existing logic)
        dimension_scores = self.personality_assessment.calculate_dimension_scores(quiz_responses)
        archetype = self.personality_assessment.determine_archetype(dimension_scores)
        personality_insights = self.personality_assessment.generate_insights(archetype, dimension_scores)

        # Create unified result
        unified_result = {
            # From AI Analysis
            "money_personality": ai_analysis_result.get("money_personality"),
            "finance_iq_score": ai_analysis_result.get("finance_iq_score"),
            "learning_gaps": ai_analysis_result.get("learning_gaps"),
            "recommended_first_sim": ai_analysis_result.get("recommended_first_sim"),
            # From Personality Assessment
            "personality_type": archetype,
            "personality_name": personality_insights.get("archetype_name"),
            "personality_description": personality_insights.get("description"),
            "dimension_scores": dimension_scores,
            "confidence_score": personality_insights.get("confidence_score"),
            "strengths": personality_insights.get("strengths"),
            "challenges": personality_insights.get("challenges"),
            "learning_focus": personality_insights.get("learning_focus"),
        }

        # Save to UserProfile
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not user_profile:
            user_profile = UserProfile(user_id=user_id)
            db.add(user_profile)

        # Update profile with unified assessment
        user_profile.money_personality = unified_result["money_personality"]
        user_profile.finance_iq_score = unified_result["finance_iq_score"]
        user_profile.learning_gaps = unified_result["learning_gaps"]
        user_profile.recommended_first_sim = unified_result["recommended_first_sim"]
        user_profile.risk_tolerance = dimension_scores.get("risk_tolerance", 5.0)
        user_profile.time_horizon = dimension_scores.get("time_horizon", 5.0)
        user_profile.spending_trigger = dimension_scores.get("spending_trigger", 5.0)
        user_profile.mindset = dimension_scores.get("mindset", 5.0)
        user_profile.decision_style = dimension_scores.get("decision_style", 5.0)
        user_profile.stress_response = dimension_scores.get("stress_response", 5.0)
        user_profile.personality_type = archetype
        user_profile.personality_name = unified_result["personality_name"]
        user_profile.personality_description = unified_result["personality_description"]
        user_profile.personality_confidence_score = unified_result["confidence_score"]
        user_profile.last_assessment_date = datetime.utcnow()
        user_profile.quiz_completed = True

        # Save to database
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)

        # Create assessment history entry
        previous_assessment = (
            db.query(AssessmentHistory)
            .filter(AssessmentHistory.profile_id == user_profile.id)
            .order_by(AssessmentHistory.completed_at.desc())
            .first()
        )

        change_summary = None
        if previous_assessment:
            prev_scores = json.loads(previous_assessment.dimension_scores)
            improved = [dim for dim, score in dimension_scores.items() if prev_scores.get(dim, 5) < score]
            declined = [dim for dim, score in dimension_scores.items() if prev_scores.get(dim, 5) > score]
            change_summary = {"improved_dimensions": improved, "declined_dimensions": declined}

        assessment_history = AssessmentHistory(
            profile_id=user_profile.id,
            assessment_version=user_profile.assessment_version,
            quiz_responses=quiz_responses,
            dimension_scores=dimension_scores,
            personality_archetype=archetype,
            confidence_score=unified_result["confidence_score"],
            previous_assessment_id=previous_assessment.id if previous_assessment else None,
            change_summary=change_summary,
        )
        db.add(assessment_history)
        db.commit()

        return unified_result

    async def _analyze_financial_profile_internal(self, quiz_responses: Dict) -> Dict[str, Any]:
        """Internal financial profile analysis using Claude (AI Analysis logic)"""
        # Convert numeric selections to descriptive values
        goal_options = ["Save", "Invest", "Pay debt", "Emergency fund"]
        life_stage_options = ["Student", "First job", "Mid-career", "Business owner"]
        knowledge_options = [33, 66, 100]
        risk_options = ["Conservative", "Moderate", "Aggressive"]
        surplus_options = [500, 2000, 5000, 10000]

        q1_goals = goal_options[quiz_responses["q1_goals"]] if quiz_responses["q1_goals"] is not None else "Save"
        q2_life_stage = (
            life_stage_options[quiz_responses["q2_life_stage"]]
            if quiz_responses["q2_life_stage"] is not None
            else "First job"
        )
        q3_knowledge = knowledge_options[min(quiz_responses["q3_knowledge"] or 0, 2)] if quiz_responses["q3_knowledge"] is not None else 33
        q4_risk_tolerance = (
            risk_options[quiz_responses["q4_risk_tolerance"]]
            if quiz_responses["q4_risk_tolerance"] is not None
            else "Moderate"
        )
        q5_monthly_surplus = (
            surplus_options[min(quiz_responses["q5_monthly_surplus"] or 0, 3)]
            if quiz_responses["q5_monthly_surplus"] is not None
            else 2000
        )

        system_prompt = """You are a financial education AI assistant analyzing user profiles.
Based on the user's quiz responses, provide:
1. Money Personality Type (one of: "The Careful Builder", "The Ambitious Investor", "The Overwhelmed Earner", "The Smart Saver")
2. Finance IQ Score (0-100, based on their knowledge and risk tolerance)
3. Learning Gaps (3-5 priority topics they should learn, as an array)
4. Recommended First Simulation (one of: "gullak", "sip-chronicles", "karobaar", "compound-interest", "emergency-fund", "coffee-shop-effect", "credit-card-debt", "budget-builder", "car-payment", "paycheck-game")

Return ONLY valid JSON with these 4 keys: money_personality, finance_iq_score, learning_gaps, recommended_first_sim."""

        user_message = f"""Analyze this user's financial profile:
- Financial Goals: {q1_goals}
- Life Stage: {q2_life_stage}
- Financial Knowledge Level (0-100): {q3_knowledge}
- Risk Tolerance: {q4_risk_tolerance}
- Monthly Surplus: ₹{q5_monthly_surplus}

Respond with ONLY valid JSON (no markdown, no explanation)."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            response_text = response.content[0].text.strip()
            analysis_result = json.loads(response_text)

            # Validate
            required_fields = ["money_personality", "finance_iq_score", "learning_gaps", "recommended_first_sim"]
            for field in required_fields:
                if field not in analysis_result:
                    raise ValueError(f"Missing required field: {field}")

            analysis_result["finance_iq_score"] = float(analysis_result["finance_iq_score"])
            if not isinstance(analysis_result["learning_gaps"], list):
                analysis_result["learning_gaps"] = [analysis_result["learning_gaps"]]

            return analysis_result

        except Exception as e:
            # Fallback
            return {
                "money_personality": "The Balanced Learner",
                "finance_iq_score": 50.0,
                "learning_gaps": ["Emergency Fund Fundamentals", "Investment Basics", "Debt Management"],
                "recommended_first_sim": "gullak",
            }

    def build_ai_tutor_context(self, db: Session, user_id: int, recent_messages_count: int = 5) -> str:
        """
        Build rich context for AI Tutor that includes:
        - Personality profile
        - Money personality and Finance IQ
        - Learning gaps
        - Recent conversation history
        - Detected biases pattern
        """
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        user = db.query(User).filter(User.id == user_id).first()

        if not user_profile or not user:
            return "No user profile data available yet."

        parts = []

        # User identity
        parts.append(f"User: {user.name}, Age {user.age}, {user.occupation or 'Occupation not specified'}")
        parts.append(f"Monthly Income: ₹{user.monthly_income:,.0f}")

        # Personality profile
        if user_profile.personality_name:
            parts.append(f"\nPersonality Type: {user_profile.personality_name}")
            parts.append(f"Description: {user_profile.personality_description}")

        # Dimension scores
        parts.append("\nPersonality Dimensions (0-10 scale):")
        parts.append(f"  - Risk Tolerance: {user_profile.risk_tolerance:.1f}")
        parts.append(f"  - Time Horizon: {user_profile.time_horizon:.1f}")
        parts.append(f"  - Spending Trigger: {user_profile.spending_trigger:.1f}")
        parts.append(f"  - Mindset: {user_profile.mindset:.1f}")
        parts.append(f"  - Decision Style: {user_profile.decision_style:.1f}")
        parts.append(f"  - Stress Response: {user_profile.stress_response:.1f}")

        # Money personality and IQ
        if user_profile.money_personality:
            parts.append(f"\nMoney Personality: {user_profile.money_personality}")
            parts.append(f"Finance IQ Score: {user_profile.finance_iq_score:.0f}/100")

        # Learning gaps
        if user_profile.learning_gaps:
            gaps = user_profile.learning_gaps
            if isinstance(gaps, list):
                parts.append(f"\nLearning Focus Areas: {', '.join(gaps)}")

        # Recent conversation history
        recent_messages = (
            db.query(ConversationMessage)
            .filter(ConversationMessage.user_id == user_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(recent_messages_count)
            .all()
        )

        if recent_messages:
            parts.append(f"\nRecent Conversation (last {len(recent_messages)} messages):")
            for msg in reversed(recent_messages):
                parts.append(f"  User: {msg.user_message[:100]}...")
                parts.append(f"  You: {msg.ai_response[:100]}...")

        # Detected biases pattern
        if recent_messages:
            all_biases = []
            for msg in recent_messages:
                if msg.detected_biases:
                    try:
                        biases = msg.detected_biases if isinstance(msg.detected_biases, list) else [msg.detected_biases]
                        all_biases.extend([b.get("bias", b.get("bias_type", "unknown")) for b in biases])
                    except:
                        pass

            if all_biases:
                from collections import Counter

                bias_counts = Counter(all_biases)
                parts.append(f"\nRecognized Biases in Recent Interactions:")
                for bias, count in bias_counts.most_common(3):
                    parts.append(f"  - {bias} (mentioned {count}x)")

        return "\n".join(parts)

    async def save_conversation(
        self,
        db: Session,
        user_id: int,
        session_id: str,
        user_message: str,
        ai_response: str,
        suggestions: List[str] = None,
        detected_biases: List[Dict] = None,
    ) -> ConversationMessage:
        """Persist conversation message to database"""
        # Get the next message index for this session
        last_message = (
            db.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.message_index.desc())
            .first()
        )
        message_index = (last_message.message_index + 1) if last_message else 0

        conversation_msg = ConversationMessage(
            user_id=user_id,
            session_id=session_id,
            message_index=message_index,
            user_message=user_message,
            ai_response=ai_response,
            ai_suggestions=suggestions or [],
            detected_biases=detected_biases or [],
        )

        db.add(conversation_msg)
        db.commit()
        db.refresh(conversation_msg)

        return conversation_msg

    async def get_conversation_history(
        self, db: Session, user_id: int, session_id: str, limit: int = 10
    ) -> List[ConversationMessage]:
        """Retrieve conversation history for a session"""
        return (
            db.query(ConversationMessage)
            .filter(ConversationMessage.user_id == user_id, ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(limit)
            .all()
        )

    def detect_biases(self, message: str, user_profile: Optional[UserProfile]) -> List[Dict]:
        """
        Detect cognitive biases in user message
        Uses BehavioralAnalyzer logic from AI Tutor
        """
        biases = []
        message_lower = message.lower()

        # Loss aversion
        if any(word in message_lower for word in ["small", "little", "save", "buy", "expensive"]):
            if "can't" in message_lower or "too much" in message_lower or "afraid" in message_lower:
                biases.append(
                    {
                        "bias": "Loss Aversion",
                        "severity": "moderate",
                        "explanation": "Tendency to feel the pain of losing money more acutely than the pleasure of gaining it",
                        "suggestion": "Focus on potential gains from investments rather than fear of losses",
                    }
                )

        # Present bias
        if any(word in message_lower for word in ["now", "today", "immediate", "urgent", "right now"]):
            if "future" not in message_lower and "long term" not in message_lower:
                biases.append(
                    {
                        "bias": "Present Bias",
                        "severity": "moderate",
                        "explanation": "Overvaluing immediate rewards at the expense of long-term benefits",
                        "suggestion": "Automate savings so your future self gets priority",
                    }
                )

        # Anchoring bias
        if any(word in message_lower for word in ["can only", "must spend", "maximum", "budget", "limit"]):
            biases.append(
                {
                    "bias": "Anchoring",
                    "severity": "minor",
                    "explanation": "Your budget may have become a target to reach rather than a limit to stay under",
                    "suggestion": "Try beating last month's spending instead of just hitting your budget",
                }
            )

        # Overconfidence
        if any(word in message_lower for word in ["always", "never", "guaranteed", "sure", "definitely"]):
            biases.append(
                {
                    "bias": "Overconfidence",
                    "severity": "minor",
                    "explanation": "High certainty about financial decisions can mask unknown risks",
                    "suggestion": "Consider alternative scenarios and stress-test your assumptions",
                }
            )

        return biases

    async def compare_assessments(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Compare current assessment with previous to track growth"""
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not user_profile:
            return {}

        assessment_history = (
            db.query(AssessmentHistory)
            .filter(AssessmentHistory.profile_id == user_profile.id)
            .order_by(AssessmentHistory.completed_at.desc())
            .limit(2)
            .all()
        )

        if len(assessment_history) < 2:
            return {"message": "Only one assessment completed"}

        current = assessment_history[0]
        previous = assessment_history[1]

        current_scores = json.loads(current.dimension_scores)
        previous_scores = json.loads(previous.dimension_scores)

        comparison = {
            "assessment_dates": {
                "previous": previous.completed_at.isoformat(),
                "current": current.completed_at.isoformat(),
            },
            "dimension_changes": {},
        }

        for dimension in current_scores.keys():
            prev_val = previous_scores.get(dimension, 5.0)
            curr_val = current_scores.get(dimension, 5.0)
            change = curr_val - prev_val
            comparison["dimension_changes"][dimension] = {"previous": prev_val, "current": curr_val, "change": change}

        return comparison


# Singleton instance
ai_personalization_engine = AIPersonalizationEngine()
