"""
AI Tutor Service using OpenAI + LangChain
Context-aware financial tutoring with Socratic method
Integrates with AIPersonalizationEngine for rich context
"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from app.core.config import settings
from sqlalchemy.orm import Session


class AITutorService:
    """AI-powered financial tutor with personality and context"""

    def __init__(self, personalization_engine=None):
        self.personalization_engine = personalization_engine
        self._llm = None
        self._chain = None

        self.system_prompt = """You are an empathetic, knowledgeable financial AI tutor for "Money Mindset" app.

Your teaching philosophy:
1. Use the Socratic method - ask questions that lead to insights
2. Never shame or judge - money habits are learned, not innate
3. Celebrate small wins and progress
4. Explain concepts using the user's actual data and personality
5. Break down complex topics into digestible pieces
6. Adapt your language to the user's financial knowledge level and learning style

Your personality:
- Warm, encouraging, but honest
- Use metaphors and storytelling
- Provide actionable advice, not just theory
- Reference behavioral psychology and cognitive biases when relevant
- Tailor advice to the user's personality type and dimensions

Context about this user:
{context}

User's question: {input}

Respond as their trusted financial mentor, incorporating their personality profile."""

        self.prompt_template = PromptTemplate(
            input_variables=["context", "input"],
            template=self.system_prompt
        )

    @property
    def llm(self):
        """Lazy initialization of LLM"""
        if self._llm is None:
            if not settings.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY is not set. Please add your OpenRouter API key to .env file.\n"
                    "Get a key at: https://openrouter.ai"
                )
            self._llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.7,
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
        return self._llm

    @property
    def chain(self):
        """Create LLM chain with prompt"""
        return self.prompt_template | self.llm

    async def get_response(
        self,
        message: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        db: Optional[Session] = None,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Get AI tutor response with rich personalized context

        Args:
            message: User's message/question
            user_id: User ID (for retrieving profile and saving conversation)
            session_id: Conversation session ID
            db: Database session
            user_context: Legacy context dict (deprecated, use personalization engine)
        """
        import asyncio

        # Build context string - prefer personalization engine if available
        if self.personalization_engine and user_id and db:
            context_str = self.personalization_engine.build_ai_tutor_context(db, user_id)
        else:
            context_str = self._build_context_string(user_context)

        try:
            # Run LangChain invoke in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.chain.invoke,
                {"context": context_str, "input": message}
            )
            # Extract response text from the LLM output
            response = result.content if hasattr(result, 'content') else str(result)

            # Extract insights and suggestions
            insights = self._extract_insights(user_context)
            suggestions = self._generate_suggestions(message, user_context)

            # Detect biases if personalization engine available
            detected_biases = []
            if self.personalization_engine:
                detected_biases = self.personalization_engine.detect_biases(message, None)

            # Save conversation if we have user_id and session_id
            if user_id and session_id and db and self.personalization_engine:
                await self.personalization_engine.save_conversation(
                    db=db,
                    user_id=user_id,
                    session_id=session_id,
                    user_message=message,
                    ai_response=response,
                    suggestions=suggestions,
                    detected_biases=detected_biases
                )

            return {
                "response": response,
                "suggestions": suggestions,
                "insights": insights,
                "detected_biases": detected_biases
            }

        except Exception as e:
            # Log error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"AI Tutor error for user {user_id}: {str(e)}", exc_info=True)
            # Fallback response
            return {
                "response": self._get_fallback_response(message),
                "suggestions": [],
                "insights": {},
                "detected_biases": []
            }
    
    def _build_context_string(self, context: Optional[Dict]) -> str:
        """Build formatted context string"""
        if not context:
            return "No user data available yet."
        
        parts = []
        
        # User profile
        if "user" in context:
            user = context["user"]
            parts.append(f"User: {user.get('name')}, Age {user.get('age')}, {user.get('occupation')}")
            parts.append(f"Monthly Income: ${user.get('monthly_income'):,.0f}")
            parts.append(f"Financial Knowledge: {user.get('financial_knowledge')}")
        
        # Spending summary
        if "spending" in context:
            spending = context["spending"]
            parts.append(f"\nRecent Spending: ${spending.get('total', 0):,.0f}")
            parts.append(f"Top Category: {spending.get('top_category', 'N/A')}")
        
        # Goals
        if "goals" in context:
            goals = context["goals"]
            parts.append(f"\nActive Goals: {len(goals)}")
            for goal in goals[:3]:
                progress = (goal['current'] / goal['target'] * 100) if goal['target'] > 0 else 0
                parts.append(f"  - {goal['name']}: {progress:.0f}% complete")
        
        # Recent patterns
        if "patterns" in context:
            patterns = context["patterns"]
            if patterns.get("alerts"):
                parts.append(f"\nAlerts: {len(patterns['alerts'])} spending alerts")
        
        return "\n".join(parts)
    
    def _extract_insights(self, context: Optional[Dict]) -> Dict:
        """Extract key insights from user data"""
        insights = {}
        
        if not context:
            return insights
        
        # Savings rate
        if "user" in context and "spending" in context:
            income = context["user"].get("monthly_income", 0)
            spending = context["spending"].get("total", 0)
            if income > 0:
                savings_rate = ((income - spending) / income) * 100
                insights["savings_rate"] = f"{savings_rate:.1f}%"
        
        # Goal progress
        if "goals" in context:
            goals = context["goals"]
            on_track = sum(1 for g in goals if g.get("current", 0) > 0)
            insights["goals_with_progress"] = f"{on_track}/{len(goals)}"
        
        return insights
    
    def _generate_suggestions(
        self,
        message: str,
        context: Optional[Dict]
    ) -> List[str]:
        """Generate contextual quick suggestions"""
        suggestions = []
        
        # Topic-based suggestions
        message_lower = message.lower()
        
        if "save" in message_lower or "saving" in message_lower:
            suggestions.extend([
                "How can I automate my savings?",
                "What's the 50/30/20 budget rule?",
                "Should I save or invest first?"
            ])
        
        elif "budget" in message_lower:
            suggestions.extend([
                "Help me create a realistic budget",
                "How do I track expenses easily?",
                "What if I go over budget?"
            ])
        
        elif "invest" in message_lower:
            suggestions.extend([
                "What's compound interest?",
                "Should I invest or pay off debt?",
                "Explain index funds simply"
            ])
        
        elif "debt" in message_lower:
            suggestions.extend([
                "Debt avalanche vs snowball?",
                "Should I pay minimum or extra?",
                "How does interest work?"
            ])
        
        else:
            suggestions.extend([
                "Analyze my spending patterns",
                "Help me set a financial goal",
                "Why can't I save money?"
            ])
        
        return suggestions[:4]  # Return max 4
    
    def _get_fallback_response(self, message: str) -> str:
        """Fallback response when API fails"""
        return f"""I understand you're asking about: "{message}"

While I'm having trouble connecting to my full knowledge base right now, here's what I can tell you:

Financial success comes down to three fundamentals:
1. **Spend less than you earn** - Track where your money goes
2. **Automate good habits** - Make saving automatic
3. **Learn continuously** - Financial literacy is a journey

Would you like to explore any of these areas? I'm here to help you build better money habits!"""


# Specialized tutoring modules
class SocraticTutor:
    """Socratic method questioning for deeper learning"""
    
    @staticmethod
    def generate_followup_questions(topic: str, user_level: str) -> List[str]:
        """Generate Socratic questions based on topic"""
        
        questions_map = {
            "saving": [
                "What would having $1000 saved change for you?",
                "What's stopping you from saving $50 this week?",
                "If your future self could talk to you, what would they say about saving?"
            ],
            "spending": [
                "When you make impulse purchases, what emotion precedes them?",
                "Which expenses bring you genuine joy vs temporary satisfaction?",
                "If you had to cut spending by 20%, what would you eliminate first?"
            ],
            "investing": [
                "What's riskier: not investing, or investing poorly?",
                "How would you explain compound interest to a 10-year-old?",
                "What keeps you from starting to invest today?"
            ]
        }
        
        return questions_map.get(topic, [
            "What's your biggest money worry right now?",
            "What would financial freedom look like for you?"
        ])


class BehavioralAnalyzer:
    """Analyze money behaviors and biases"""
    
    @staticmethod
    def detect_biases(spending_patterns: Dict) -> List[Dict]:
        """Detect cognitive biases in spending"""
        biases = []
        
        # Loss aversion
        if spending_patterns.get("frequent_small_purchases"):
            biases.append({
                "bias": "Loss Aversion",
                "explanation": "Small purchases feel less painful than one large purchase, even if total is higher",
                "suggestion": "Try the '48-hour rule' for purchases over $50"
            })
        
        # Present bias
        if spending_patterns.get("no_savings_but_high_discretionary"):
            biases.append({
                "bias": "Present Bias",
                "explanation": "We value immediate pleasure over future security",
                "suggestion": "Automate savings so future-you gets paid first"
            })
        
        # Anchoring
        if spending_patterns.get("budget_always_maxed"):
            biases.append({
                "bias": "Anchoring",
                "explanation": "Your budget became a target to hit, not a limit to stay under",
                "suggestion": "Try a spending challenge: beat last month's spending"
            })
        
        return biases


# Export service instance (personalization engine injected at runtime in API)
ai_tutor_service = AITutorService()
