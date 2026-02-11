"""
AI Tutor Service using OpenAI + LangChain
Context-aware financial tutoring with Socratic method
"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from app.core.config import settings


class AITutorService:
    """AI-powered financial tutor with personality and context"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.system_prompt = """You are an empathetic, knowledgeable financial AI tutor for "Money Mindset" app.

Your teaching philosophy:
1. Use the Socratic method - ask questions that lead to insights
2. Never shame or judge - money habits are learned, not innate
3. Celebrate small wins and progress
4. Explain concepts using the user's actual data
5. Break down complex topics into digestible pieces
6. Adapt your language to the user's financial knowledge level

Your personality:
- Warm, encouraging, but honest
- Use metaphors and storytelling
- Provide actionable advice, not just theory
- Reference behavioral psychology and cognitive biases when relevant

Context you have access to:
{context}

User's question: {input}

Respond as their trusted financial mentor."""

        self.prompt = PromptTemplate(
            input_variables=["context", "input"],
            template=self.system_prompt
        )
        
        self.memory = ConversationBufferMemory()
        
        self.chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.prompt,
            verbose=True
        )
    
    async def get_response(
        self,
        message: str,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """Get AI tutor response with context"""
        
        # Build context string from user data
        context_str = self._build_context_string(user_context)
        
        try:
            # Get response from LangChain
            response = await self.chain.apredict(
                context=context_str,
                input=message
            )
            
            # Extract insights and suggestions
            insights = self._extract_insights(user_context)
            suggestions = self._generate_suggestions(message, user_context)
            
            return {
                "response": response,
                "suggestions": suggestions,
                "insights": insights
            }
            
        except Exception as e:
            # Fallback response
            return {
                "response": self._get_fallback_response(message),
                "suggestions": [],
                "insights": {}
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


# Export service instance
ai_tutor_service = AITutorService()
