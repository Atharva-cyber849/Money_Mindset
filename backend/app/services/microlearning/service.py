"""
Microlearning content service.
Curated bite-sized lessons from books and podcasts for fast financial learning.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class MicrolearningItem:
    id: str
    title: str
    source_type: str
    source_title: str
    creator: str
    topic: str
    takeaway: str
    action: str
    duration_minutes: int
    difficulty: str
    tags: List[str]


MICROLEARNING_LIBRARY: List[MicrolearningItem] = [
    MicrolearningItem(
        id="psychology_of_money_behavior",
        title="Wealth is behavior, not just math",
        source_type="book",
        source_title="The Psychology of Money",
        creator="Morgan Housel",
        topic="mindset",
        takeaway="Small repeatable habits often matter more than trying to find the perfect investment.",
        action="Automate one money habit today: savings, SIP, or bill payment.",
        duration_minutes=2,
        difficulty="Beginner",
        tags=["habit", "behavior", "saving"],
    ),
    MicrolearningItem(
        id="atomic_habits_finance",
        title="Design your money habits for success",
        source_type="book",
        source_title="Atomic Habits",
        creator="James Clear",
        topic="habits",
        takeaway="Tiny changes become powerful when the process is easy to repeat.",
        action="Reduce friction for one good habit and increase friction for one bad habit.",
        duration_minutes=2,
        difficulty="Beginner",
        tags=["habits", "routine", "consistency"],
    ),
    MicrolearningItem(
        id="automate_investing",
        title="Pay yourself first with automation",
        source_type="book",
        source_title="I Will Teach You to Be Rich",
        creator="Ramit Sethi",
        topic="investing",
        takeaway="Automating investments and savings removes decision fatigue and improves consistency.",
        action="Set up an auto-transfer for your next savings contribution.",
        duration_minutes=3,
        difficulty="Beginner",
        tags=["automation", "investing", "savings"],
    ),
    MicrolearningItem(
        id="cash_flow_vs_price",
        title="Focus on cash flow and quality of decisions",
        source_type="book",
        source_title="Rich Dad Poor Dad",
        creator="Robert Kiyosaki",
        topic="cash_flow",
        takeaway="Income that compounds over time can matter more than visible status purchases.",
        action="List one asset that could generate recurring cash flow in your life.",
        duration_minutes=2,
        difficulty="Beginner",
        tags=["cash flow", "assets", "mindset"],
    ),
    MicrolearningItem(
        id="financial_order_of_operations",
        title="Follow the financial order of operations",
        source_type="podcast",
        source_title="The Money Guy Show",
        creator="Brian Preston and Bo Hanson",
        topic="planning",
        takeaway="Build the right sequence: emergency fund, debt payoff, retirement, then extra investing.",
        action="Identify the next step in your financial order of operations.",
        duration_minutes=3,
        difficulty="Intermediate",
        tags=["planning", "debt", "emergency fund"],
    ),
    MicrolearningItem(
        id="opportunity_cost_check",
        title="Ask what this choice costs you",
        source_type="podcast",
        source_title="Afford Anything",
        creator="Paula Pant",
        topic="decisions",
        takeaway="Every money decision has an opportunity cost, even when it feels small.",
        action="Before your next impulse buy, compare it to one future goal it delays.",
        duration_minutes=2,
        difficulty="Beginner",
        tags=["opportunity cost", "spending", "goals"],
    ),
    MicrolearningItem(
        id="values_based_money",
        title="Spend in ways that match your values",
        source_type="podcast",
        source_title="ChooseFI",
        creator="Chris Mamula and Brad Barrett",
        topic="values",
        takeaway="Financial independence is easier when money decisions reflect what actually matters to you.",
        action="Name one expense you would happily keep and one you would cut.",
        duration_minutes=2,
        difficulty="Intermediate",
        tags=["values", "independence", "priorities"],
    ),
    MicrolearningItem(
        id="housing_tradeoff",
        title="Housing can quietly shape the whole budget",
        source_type="podcast",
        source_title="BiggerPockets Money",
        creator="Mindy Jensen and Scott Trench",
        topic="budgeting",
        takeaway="Big recurring fixed costs deserve careful tradeoff thinking because they affect every other goal.",
        action="Check whether housing is crowding out savings or investing.",
        duration_minutes=3,
        difficulty="Intermediate",
        tags=["budget", "housing", "tradeoffs"],
    ),
]


class MicrolearningService:
    """Curates quick lessons from books and podcasts."""

    SIMULATION_TOPIC_MAP = {
        "gullak": "savings",
        "sip-chronicles": "investing",
        "sip_chronicles": "investing",
        "budget-builder": "budgeting",
        "budget_builder": "budgeting",
        "credit-card-debt": "debt",
        "credit_card_debt": "debt",
        "emergency-fund": "emergency fund",
        "emergency_fund": "emergency fund",
        "car-payment": "planning",
        "car_payment": "planning",
        "paycheck-game": "budgeting",
        "paycheck_game": "budgeting",
        "compound-interest": "investing",
        "compound_interest": "investing",
        "coffee-shop-effect": "habits",
        "coffee_shop_effect": "habits",
    }

    def __init__(self, items: Optional[List[MicrolearningItem]] = None):
        self.items = items or MICROLEARNING_LIBRARY

    def list_items(self) -> List[Dict[str, Any]]:
        return [self._serialize_item(item) for item in self.items]

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        for item in self.items:
            if item.id == item_id:
                return self._serialize_item(item)
        return None

    def recommend_items(
        self,
        learning_gaps: Optional[List[str]] = None,
        preferred_topic: Optional[str] = None,
        limit: int = 4,
    ) -> List[Dict[str, Any]]:
        learning_gaps = [gap.lower() for gap in (learning_gaps or [])]
        preferred_topic = (preferred_topic or "").lower().strip()
        normalized_topic = self.SIMULATION_TOPIC_MAP.get(preferred_topic, preferred_topic)

        def score(item: MicrolearningItem) -> int:
            item_text = " ".join([item.topic, item.title, item.takeaway, " ".join(item.tags)]).lower()
            item_score = 0
            if normalized_topic and normalized_topic in item_text:
                item_score += 3
            for gap in learning_gaps:
                if gap and gap in item_text:
                    item_score += 2
            if item.source_type == "book":
                item_score += 1
            if item.difficulty == "Beginner":
                item_score += 1
            return item_score

        ranked = sorted(self.items, key=score, reverse=True)
        return [self._serialize_item(item) for item in ranked[:limit]]

    def get_daily_microlearning_queue(self, learning_gaps: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return self.recommend_items(learning_gaps=learning_gaps, limit=3)

    @staticmethod
    def _serialize_item(item: MicrolearningItem) -> Dict[str, Any]:
        return {
            "id": item.id,
            "title": item.title,
            "source_type": item.source_type,
            "source_title": item.source_title,
            "creator": item.creator,
            "topic": item.topic,
            "takeaway": item.takeaway,
            "action": item.action,
            "duration_minutes": item.duration_minutes,
            "difficulty": item.difficulty,
            "tags": item.tags,
        }


microlearning_service = MicrolearningService()
