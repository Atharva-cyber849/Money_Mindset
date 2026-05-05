"""
Gullak (Piggy Bank) Game Simulator
Indian personal finance educational game with jar-based allocation system.

Core Mechanics:
- 5 jars: Emergency Fund, Insurance, Short-term Goals, Long-term Investments, Gold
- 10-year simulation (120 months)
- Monthly life events with Indian-specific scenarios
- Regional variations (state-specific investment options)
- Gamification: XP, badges, achievements
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import random
import json


class JarType(str, Enum):
    """Five jar categories in Gullak"""
    EMERGENCY_FUND = "emergency"
    INSURANCE = "insurance"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    GOLD = "gold"


class IncomeType(str, Enum):
    """Income source types"""
    SALARIED = "salaried"
    GIG_WORK = "gig_work"
    BUSINESS = "business"


class LifeEventType(str, Enum):
    """Possible life events"""
    MEDICAL_EMERGENCY = "medical_emergency"
    JOB_LOSS_SIGNAL = "job_loss_signal"
    WEDDING = "wedding"
    BONUS = "bonus"
    MARKET_CORRECTION = "market_correction"
    DEMONETIZATION = "demonetization"
    SALARY_INCREASE = "salary_increase"
    CAR_ACCIDENT = "car_accident"
    EDUCATION_EXPENSE = "education_expense"
    HOME_REPAIR = "home_repair"
    FESTIVAL_BONUS = "festival_bonus"
    INFLATION_SPIKE = "inflation_spike"
    # New Indian crisis events
    GST_IMPLEMENTATION = "gst_implementation"
    LIQUIDITY_CRUNCH = "liquidity_crunch"
    MONSOON_FAILURE = "monsoon_failure"
    RUPEE_DEPRECIATION = "rupee_depreciation"
    DOWRY_NEGOTIATION = "dowry_negotiation"
    DISHONEST_CONTRACTOR = "dishonest_contractor"
    COMPETITIVE_EXAM_COACHING = "competitive_exam_coaching"
    PROPERTY_APPRECIATION_SPIKE = "property_appreciation_spike"


class StateLocation(str, Enum):
    """Indian states with regional variations"""
    MAHARASHTRA = "maharashtra"
    TAMIL_NADU = "tamil_nadu"
    KARNATAKA = "karnataka"
    DELHI = "delhi"
    PUNJAB = "punjab"
    TELANGANA = "telangana"
    RAJASTHAN = "rajasthan"
    UTTAR_PRADESH = "uttar_pradesh"
    OTHER = "other"


@dataclass
class JarAllocation:
    """Jar allocation amounts"""
    emergency: float
    insurance: float
    short_term: float
    long_term: float
    gold: float

    def total(self) -> float:
        return self.emergency + self.insurance + self.short_term + self.long_term + self.gold

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "JarAllocation":
        return cls(**data)


@dataclass
class DecisionOption:
    """Represents a decision option for a life event"""
    title: str
    description: str
    consequences: Dict[str, float]  # jar_name -> amount change
    monthly_impact: Optional[float] = None  # Monthly impact for loan options
    months: Optional[int] = None  # Duration of monthly impact
    risk_level: str = "medium"  # low, medium, high
    long_term_effect: Optional[str] = None  # Narrative description of long-term effects


@dataclass
class LifeEvent:
    """Represents a life event"""
    month: int
    event_type: LifeEventType
    impact_amount: float
    jar_affected: Optional[JarType]
    description: str
    has_decision: bool = False
    decision_title: Optional[str] = None
    decision_options: List[DecisionOption] = field(default_factory=list)
    chosen_option_idx: Optional[int] = None


@dataclass
class MonthlyState:
    """State of finances at end of each month"""
    month: int
    income: float
    expenses: float
    jars: JarAllocation
    event: Optional[LifeEvent] = None
    jar_returns: JarAllocation = field(default_factory=lambda: JarAllocation(0, 0, 0, 0, 0))


class GullakSimulator:
    """Main Gullak game simulator"""

    # Historical returns (average annual %)
    JAR_RETURNS = {
        JarType.EMERGENCY_FUND: 0.04,      # 4% (savings account)
        JarType.INSURANCE: 0.0,            # 0% (protection only)
        JarType.SHORT_TERM: 0.06,          # 6% (short-term funds)
        JarType.LONG_TERM: 0.12,           # 12% (equity)
        JarType.GOLD: 0.005,               # 0.5% (poor real returns)
    }

    # Optimal allocation targets
    OPTIMAL_ALLOCATION = {
        JarType.EMERGENCY_FUND: 0.25,      # 25% of surplus
        JarType.INSURANCE: 0.15,           # 15%
        JarType.SHORT_TERM: 0.15,          # 15%
        JarType.LONG_TERM: 0.35,           # 35%
        JarType.GOLD: 0.10,                # 10%
    }

    def __init__(
        self,
        initial_income: float = 40000,
        initial_expenses: float = 30000,
        income_type: IncomeType = IncomeType.SALARIED,
        state_location: StateLocation = StateLocation.OTHER,
        starting_age: int = 22,
        initial_jars: Optional[JarAllocation] = None,
    ):
        self.initial_income = initial_income
        self.initial_expenses = initial_expenses
        self.income_type = income_type
        self.state_location = state_location
        self.starting_age = starting_age
        self.current_month = 0
        self.history: List[MonthlyState] = []

        # Initialize jars
        if initial_jars is None:
            self.current_jars = JarAllocation(
                emergency=50000,
                insurance=10000,
                short_term=10000,
                long_term=20000,
                gold=10000,
            )
        else:
            self.current_jars = initial_jars

        self.decision_history: List[Dict] = []
        self.life_events_log: List[LifeEvent] = []

    def _get_professional_tax_by_state(self) -> float:
        """Calculate monthly professional tax by state"""
        tax_by_state = {
            StateLocation.MAHARASHTRA: 2500,
            StateLocation.TAMIL_NADU: 0,
            StateLocation.KARNATAKA: 225,
            StateLocation.DELHI: 0,
            StateLocation.PUNJAB: 0,
            StateLocation.TELANGANA: 0,
            StateLocation.RAJASTHAN: 200,
            StateLocation.UTTAR_PRADESH: 0,
            StateLocation.OTHER: 1000,
        }
        return tax_by_state.get(self.state_location, 1000) / 12  # Convert yearly to monthly

    # ==================== Decision-Based Event Methods ====================

    def _create_car_repair_decision(self, month: int, amount: float) -> LifeEvent:
        """Create car repair expense with multiple options"""
        options = [
            DecisionOption(
                title="Pay in Full from Savings",
                description=f"Deduct ₹{amount:,.0f} from current savings. Note: New Net Worth will be ₹{max(0, self.current_jars.total() - amount):,.0f}. Risk of low liquidity.",
                consequences={
                    "emergency": -amount * 0.7,
                    "short_term": -amount * 0.3,
                },
                risk_level="medium",
                long_term_effect="Maintains financial independence but reduces emergency buffer"
            ),
            DecisionOption(
                title="Take a Personal Loan",
                description=f"Borrow full ₹{amount:,.0f}. Repayment: +₹{amount * 0.08:,.0f} monthly for 24 months. Increases monthly deficit.",
                consequences={},
                monthly_impact=amount * 0.08 / 24,
                months=24,
                risk_level="high",
                long_term_effect="Increases monthly expenses, reduces debt-to-income ratio"
            ),
            DecisionOption(
                title="Hybrid: Partial Payment + Aggressive Cut",
                description=f"Pay ₹{amount * 0.5:,.0f} from savings. Cut non-essential spending by ₹{amount * 0.02:,.0f}/month for 12 months to cover rest.",
                consequences={
                    "emergency": -amount * 0.35,
                    "short_term": -amount * 0.15,
                },
                monthly_impact=amount * 0.02,
                months=12,
                risk_level="low",
                long_term_effect="Balanced approach - maintains some savings while building financial discipline"
            ),
        ]
        return LifeEvent(
            month=month,
            event_type=LifeEventType.CAR_ACCIDENT,
            impact_amount=amount,
            jar_affected=JarType.SHORT_TERM,
            description=f"Unexpected Car Repair: ₹{amount:,.0f} major mechanical issue",
            has_decision=True,
            decision_title="ALERT: Decision Required: Unexpected Car Repair Expense",
            decision_options=options,
        )

    def _create_medical_decision(self, month: int, amount: float) -> LifeEvent:
        """Create medical emergency with treatment options"""
        options = [
            DecisionOption(
                title="Premium Hospital Treatment",
                description=f"Best care at top hospital: ₹{amount:,.0f}. Full recovery in 1 month. Insurance covers ₹{amount * 0.8:,.0f}.",
                consequences={
                    "insurance": -amount * 0.2,
                    "short_term": -amount * 0.0,
                },
                risk_level="low",
                long_term_effect="Best health outcome, minimal financial impact"
            ),
            DecisionOption(
                title="Government Hospital (Cost-effective)",
                description=f"Good care at ₹{amount * 0.4:,.0f}. Recovery takes 2 months. Wait times higher but comprehensive treatment.",
                consequences={
                    "short_term": -amount * 0.4,
                },
                months=2,
                risk_level="low",
                long_term_effect="Minimal financial impact but prolonged recovery period"
            ),
            DecisionOption(
                title="Delay & Use Home Remedies",
                description=f"Skip ₹{amount:,.0f} treatment now. Risk: 50% chance condition worsens (need ₹{amount * 1.5:,.0f} later). Save immediately.",
                consequences={},
                risk_level="high",
                long_term_effect="Potential health complications and higher future costs"
            ),
        ]
        return LifeEvent(
            month=month,
            event_type=LifeEventType.MEDICAL_EMERGENCY,
            impact_amount=amount,
            jar_affected=JarType.INSURANCE,
            description=f"Medical Emergency: ₹{amount:,.0f} required for treatment",
            has_decision=True,
            decision_title="ALERT: Medical Decision Required",
            decision_options=options,
        )

    def _create_job_loss_decision(self, month: int) -> LifeEvent:
        """Create job loss scenario with response options"""
        savings = self.current_jars.total()
        monthly_expenses = self.get_monthly_expenses(month)
        runway_months = savings / monthly_expenses if monthly_expenses > 0 else 0

        options = [
            DecisionOption(
                title="Aggressive Job Search",
                description=f"Target 2 weeks job search. Maintain current spending. Runway: {runway_months:.0f} months. Risk: may take 2-3 months.",
                consequences={},
                monthly_impact=-monthly_expenses,
                months=3,
                risk_level="high",
                long_term_effect="Quick re-employment possible but uses savings rapidly"
            ),
            DecisionOption(
                title="Cut Spending + Measured Search",
                description=f"Reduce expenses 40%. Monthly budget: ₹{monthly_expenses * 0.6:,.0f}. Runway extends to {(savings / (monthly_expenses * 0.6)):.0f} months.",
                consequences={},
                monthly_impact=-monthly_expenses * 0.6,
                months=6,
                risk_level="medium",
                long_term_effect="Extends financial runway, allows broader job search"
            ),
            DecisionOption(
                title="Freelance + Part-time",
                description=f"Earn ₹{monthly_expenses * 0.5:,.0f}/month freelancing while searching. Reduces pressure. Takes 5 months to find full-time job.",
                consequences={},
                monthly_impact=-monthly_expenses * 0.5,
                months=5,
                risk_level="low",
                long_term_effect="Most sustainable but requires upskilling and effort"
            ),
        ]
        return LifeEvent(
            month=month,
            event_type=LifeEventType.JOB_LOSS_SIGNAL,
            impact_amount=0,
            jar_affected=None,
            description="Job Loss Alert: Company lay-offs announced. Your role may be affected.",
            has_decision=True,
            decision_title="ALERT: Career Decision Required",
            decision_options=options,
        )

    def _create_education_decision(self, month: int) -> LifeEvent:
        """Create education investment decision"""
        course_cost = random.uniform(50000, 200000)
        salary_increase = course_cost * random.uniform(0.5, 1.5)  # ROI between 50-150%

        options = [
            DecisionOption(
                title="Invest in Skill Course",
                description=f"Pay ₹{course_cost:,.0f} for certification. Expected salary increase: +₹{salary_increase:,.0f}/year. ROI in {(course_cost / (salary_increase / 12)):.1f} months.",
                consequences={
                    "short_term": -course_cost,
                },
                risk_level="medium",
                long_term_effect="Increases earning potential and career growth"
            ),
            DecisionOption(
                title="Finance with Student Loan",
                description=f"Borrow ₹{course_cost:,.0f} at 8% interest. EMI: ₹{course_cost * 0.08 / 12 / 5:,.0f} for 5 years. Salary increase covers EMI.",
                consequences={},
                monthly_impact=course_cost * 0.08 / 12 / 5,
                months=60,
                risk_level="low",
                long_term_effect="No immediate cash impact but adds long-term liability"
            ),
            DecisionOption(
                title="Skip for Now",
                description=f"Delay investment. May miss promotion opportunity. Defer ₹{course_cost:,.0f} spend.",
                consequences={},
                risk_level="low",
                long_term_effect="Conserves cash but may slow career progression"
            ),
        ]
        return LifeEvent(
            month=month,
            event_type=LifeEventType.EDUCATION_EXPENSE,
            impact_amount=course_cost,
            jar_affected=JarType.SHORT_TERM,
            description=f"Education Opportunity: Online certification course costs ₹{course_cost:,.0f}",
            has_decision=True,
            decision_title="ALERT: Education Investment Decision",
            decision_options=options,
        )

    def _create_marriage_decision(self, month: int) -> LifeEvent:
        """Create marriage event with budget planning options"""
        budget_options = [
            500000,   # Modest
            1000000,  # Medium
            2000000,  # Grand
        ]
        chosen_budget = random.choice(budget_options)
        moderate_budget = chosen_budget * 0.6

        options = [
            DecisionOption(
                title="Dream Wedding",
                description=f"Grand celebration: ₹{chosen_budget:,.0f}. Memorable but significantly impacts savings.",
                consequences={
                    "short_term": -chosen_budget * 0.7,
                    "long_term": -chosen_budget * 0.3,
                },
                risk_level="high",
                long_term_effect="Celebrates milestone but reduces wealth accumulation"
            ),
            DecisionOption(
                title="Balanced Celebration",
                description=f"Moderate budget: ₹{moderate_budget:,.0f}. Nice wedding without excessive spending.",
                consequences={
                    "short_term": -moderate_budget * 0.8,
                    "emergency": -moderate_budget * 0.2,
                },
                risk_level="medium",
                long_term_effect="Maintains financial balance while enjoying celebration"
            ),
            DecisionOption(
                title="Simple Ceremony + Future Travel",
                description=f"Intimate wedding: ₹{chosen_budget * 0.2:,.0f}. Save rest for honeymoon/home investment.",
                consequences={
                    "short_term": -chosen_budget * 0.2,
                },
                risk_level="low",
                long_term_effect="Prioritizes long-term wealth over one-time event"
            ),
        ]
        return LifeEvent(
            month=month,
            event_type=LifeEventType.WEDDING,
            impact_amount=chosen_budget,
            jar_affected=JarType.SHORT_TERM,
            description=f"Marriage Proposal Accepted: Wedding planning to begin",
            has_decision=True,
            decision_title="ALERT: Marriage Budget Planning",
            decision_options=options,
        )

    def _create_investment_opportunity(self, month: int) -> LifeEvent:
        """Create investment opportunity with risk-return tradeoff"""
        investment = random.uniform(100000, 500000)
        min_return = investment * 0.08
        expected_return = investment * 0.15
        max_return = investment * 0.25

        options = [
            DecisionOption(
                title="Conservative Bond Fund",
                description=f"Invest ₹{investment:,.0f}. Annual return: {min_return/investment*100:.0f}%. Low risk, guaranteed returns.",
                consequences={
                    "long_term": -investment,
                },
                risk_level="low",
                long_term_effect="Stable but slow wealth growth"
            ),
            DecisionOption(
                title="Balanced Mutual Fund",
                description=f"Invest ₹{investment:,.0f}. Expected annual return: {expected_return/investment*100:.0f}%. Moderate risk-return balance.",
                consequences={
                    "long_term": -investment,
                },
                risk_level="medium",
                long_term_effect="Reasonable wealth growth with moderate volatility"
            ),
            DecisionOption(
                title="High-Growth Equity Fund",
                description=f"Invest ₹{investment:,.0f}. Potential annual return: {max_return/investment*100:.0f}%. High volatility but long-term wealth builder.",
                consequences={
                    "long_term": -investment,
                },
                risk_level="high",
                long_term_effect="High-risk, high-reward strategy for wealth accumulation"
            ),
            DecisionOption(
                title="Skip Investment",
                description=f"Keep ₹{investment:,.0f} in cash for emergencies. Foregoes growth but maintains liquidity.",
                consequences={},
                risk_level="low",
                long_term_effect="No wealth growth but maintains emergency access"
            ),
        ]
        return LifeEvent(
            month=month,
            event_type=LifeEventType.BONUS,
            impact_amount=investment,
            jar_affected=JarType.LONG_TERM,
            description=f"Investment Opportunity: ₹{investment:,.0f} lump sum available",
            has_decision=True,
            decision_title="ALERT: Investment Decision Required",
            decision_options=options,
        )

    def apply_decision(self, event: LifeEvent, option_idx: int) -> None:
        """Apply chosen decision option to current jars"""
        if not event.has_decision or option_idx >= len(event.decision_options):
            return

        option = event.decision_options[option_idx]
        event.chosen_option_idx = option_idx

        # Apply immediate consequences
        for jar_name, amount in option.consequences.items():
            if jar_name == "emergency":
                self.current_jars.emergency = max(0, self.current_jars.emergency + amount)
            elif jar_name == "insurance":
                self.current_jars.insurance = max(0, self.current_jars.insurance + amount)
            elif jar_name == "short_term":
                self.current_jars.short_term = max(0, self.current_jars.short_term + amount)
            elif jar_name == "long_term":
                self.current_jars.long_term = max(0, self.current_jars.long_term + amount)
            elif jar_name == "gold":
                self.current_jars.gold = max(0, self.current_jars.gold + amount)

        # Store recurring impact if any
        if option.monthly_impact and option.months:
            # This will need to be tracked in the monthly state or decision history
            pass

    def _calculate_income_tax_tds(self, gross_income: float, month: int) -> float:
        """Calculate estimated income tax TDS based on slab"""
        annual_income = gross_income * 12

        # Simplified Indian tax slabs FY 2024-25
        if annual_income <= 500000:
            return 0
        elif annual_income <= 1000000:
            tax = (annual_income - 500000) * 0.05
        elif annual_income <= 2000000:
            tax = 25000 + (annual_income - 1000000) * 0.20
        else:
            tax = 225000 + (annual_income - 2000000) * 0.30

        return tax / 12  # Monthly TDS

    def get_monthly_income(self, month: int) -> float:
        """Generate monthly income with variance based on income type"""
        base = self.initial_income
        variance = 0.0

        if self.income_type == IncomeType.SALARIED:
            # Salaried: small variance + annual raise
            variance = random.uniform(-0.02, 0.05)  # ±2-5%
            annual_raise = 0.05 * (month // 12)  # 5% annual raise
            gross = base * (1 + variance + annual_raise)

            # Apply mandatory deductions (salaried employees)
            epf_deduction = gross * 0.12  # 12% EPF
            prof_tax = self._get_professional_tax_by_state()
            income_tax_tds = self._calculate_income_tax_tds(gross, month)

            return gross - epf_deduction - prof_tax - income_tax_tds

        elif self.income_type == IncomeType.GIG_WORK:
            # Gig: high variance, seasonal patterns
            variance = random.uniform(-0.3, 0.4)  # ±30-40%
            # Festival months (Oct-Dec) get 20% boost
            festival_boost = 1.2 if month % 12 in [10, 11, 12] else 1.0
            gross = base * (1 + variance) * festival_boost

            # Gig workers pay income tax on full amount
            income_tax_tds = self._calculate_income_tax_tds(gross, month)
            return gross - income_tax_tds

        else:  # BUSINESS
            # Business: high variance, market dependent
            variance = random.uniform(-0.5, 0.8)  # ±50-80%
            # Market growth factor (slight uptrend)
            market_factor = 1.0 + (month * 0.005)
            gross = base * (1 + variance) * market_factor

            # Business income tax calculation (after deductions)
            income_tax = self._calculate_income_tax_tds(gross, month)
            return gross - income_tax

    def get_monthly_expenses(self, month: int) -> float:
        """Generate monthly expenses with inflation"""
        annual_inflation = 0.06  # 6% inflation
        years = month / 12
        inflation_factor = (1 + annual_inflation) ** years

        # Add festival month expense spikes (month 10-12)
        festival_multiplier = 1.3 if month % 12 in [10, 11, 0] else 1.0

        return self.initial_expenses * inflation_factor * festival_multiplier

    def generate_life_event(self, month: int) -> Optional[LifeEvent]:
        """Randomly generate a life event based on month"""
        event_chance = 0.20  # 20% chance of event each month

        if random.random() > event_chance:
            return None

        # Special events on specific months
        if month == 36:  # Demonetization 2016
            if random.random() > 0.3:  # 70% chance to trigger for this month
                return LifeEvent(
                    month=month,
                    event_type=LifeEventType.DEMONETIZATION,
                    impact_amount=self.current_jars.emergency * 0.14,  # 14% loss on cash
                    jar_affected=JarType.EMERGENCY_FUND,
                    description="Demonetization: 86% of cash becomes worthless overnight. Digital savings unaffected.",
                )

        # Car accident with decision options
        if random.random() < 0.05:
            amount = random.uniform(50000, 120000)
            return self._create_car_repair_decision(month, amount)

        # Wedding (high impact, late game) - with decision options
        if month > 48 and random.random() < 0.08:
            return self._create_marriage_decision(month)

        # Medical emergency with treatment options
        if random.random() < 0.06:
            amount = random.uniform(50000, 150000)
            return self._create_medical_decision(month, amount)

        # Education opportunity with investment decision
        if random.random() < 0.04:
            return self._create_education_decision(month)

        # Job loss with response strategy
        if random.random() < 0.03:
            return self._create_job_loss_decision(month)

        # Investment opportunity
        if random.random() < 0.04:
            return self._create_investment_opportunity(month)

        # Salary increase on random months
        if random.random() < 0.05:
            boost = random.uniform(5000, 20000)
            return LifeEvent(
                month=month,
                event_type=LifeEventType.SALARY_INCREASE,
                impact_amount=boost,
                jar_affected=None,
                description=f"Salary increase: +₹{boost:,.0f}",
            )

        # Market correction
        if random.random() < 0.06:
            correction = -(random.uniform(5, 20) / 100)  # -5% to -20%
            return LifeEvent(
                month=month,
                event_type=LifeEventType.MARKET_CORRECTION,
                impact_amount=correction,
                jar_affected=JarType.LONG_TERM,
                description=f"Market correction: {correction*100:.1f}%",
            )

        # Home repair
        if random.random() < 0.04:
            amount = random.uniform(20000, 100000)
            return LifeEvent(
                month=month,
                event_type=LifeEventType.HOME_REPAIR,
                impact_amount=amount,
                jar_affected=JarType.SHORT_TERM,
                description=f"Home repair needed: ₹{amount:,.0f}",
            )

        # Festival bonus
        if month % 12 in [10, 11, 12] and random.random() < 0.3:
            amount = random.uniform(20000, 60000)
            return LifeEvent(
                month=month,
                event_type=LifeEventType.FESTIVAL_BONUS,
                impact_amount=amount,
                jar_affected=None,
                description=f"Festival bonus: ₹{amount:,.0f}",
            )

        # GST Implementation (July 2017 - month ~67)
        if 65 <= month <= 68 and random.random() < 0.4 and self.income_type == IncomeType.BUSINESS:
            return LifeEvent(
                month=month,
                event_type=LifeEventType.GST_IMPLEMENTATION,
                impact_amount=-0.15,  # -15% impact multiplier
                jar_affected=JarType.LONG_TERM,
                description="GST Implementation: Business income disruption for 3 months",
            )

        # Liquidity Crunch (2018-2019 - months ~84-96)
        if 84 <= month <= 100 and random.random() < 0.15:
            return LifeEvent(
                month=month,
                event_type=LifeEventType.LIQUIDITY_CRUNCH,
                impact_amount=0.03,  # +3% interest rate spike on loans
                jar_affected=None,
                description="Banking crisis: Liquidity crunch, deposit withdrawal restrictions, FD yields drop",
            )

        # Monsoon Failure (Agricultural/Rural impact, June-Sept)
        if month % 12 in [6, 7, 8, 9] and random.random() < 0.1:
            if self.state_location in [StateLocation.RAJASTHAN, StateLocation.UTTAR_PRADESH, StateLocation.OTHER]:
                loss = random.uniform(-0.4, -0.8)  # 40-80% income loss
                return LifeEvent(
                    month=month,
                    event_type=LifeEventType.MONSOON_FAILURE,
                    impact_amount=loss,
                    jar_affected=None,
                    description="Monsoon failure: Agricultural income severely impacted",
                )

        # Rupee Depreciation Crisis (2013, 2022 - random crisis years)
        if (month in range(37, 48) or month in range(132, 144)) and random.random() < 0.08:
            return LifeEvent(
                month=month,
                event_type=LifeEventType.RUPEE_DEPRECIATION,
                impact_amount=-0.15,  # -15% on import-dependent income
                jar_affected=JarType.LONG_TERM,
                description="Rupee depreciation crisis: Import inflation, foreign currency impact",
            )

        # Dowry Negotiation (Marriage-related, months 60-96)
        if 60 <= month <= 96 and random.random() < 0.05:
            dowry_amount = random.uniform(500000, 2000000)
            return LifeEvent(
                month=month,
                event_type=LifeEventType.DOWRY_NEGOTIATION,
                impact_amount=dowry_amount,
                jar_affected=JarType.SHORT_TERM,
                description=f"Family marriage negotiation: Expected dowry ₹{dowry_amount:,.0f}",
            )

        # Dishonest Contractor (Home repair scam, month 50+)
        if month > 50 and random.random() < 0.02:
            overcharge = random.uniform(100000, 300000)
            return LifeEvent(
                month=month,
                event_type=LifeEventType.DISHONEST_CONTRACTOR,
                impact_amount=overcharge,
                jar_affected=JarType.SHORT_TERM,
                description=f"Home repair contractor fraud: ₹{overcharge:,.0f} overcharge",
            )

        # Children's Competitive Exam Coaching (NEET/IIT prep, months 72-120)
        if 72 <= month <= 120 and random.random() < 0.08:
            coaching_cost = random.uniform(10000, 50000)
            return LifeEvent(
                month=month,
                event_type=LifeEventType.COMPETITIVE_EXAM_COACHING,
                impact_amount=coaching_cost,
                jar_affected=JarType.SHORT_TERM,
                description=f"NEET/IIT coaching center fees: ₹{coaching_cost:,.0f}/month commitment",
            )

        # Property Appreciation (city-specific, years 5+)
        if month > 60 and random.random() < 0.05:
            if self.state_location in [StateLocation.MAHARASHTRA, StateLocation.DELHI]:
                appreciation = random.uniform(100000, 300000)
                return LifeEvent(
                    month=month,
                    event_type=LifeEventType.PROPERTY_APPRECIATION_SPIKE,
                    impact_amount=appreciation,
                    jar_affected=JarType.LONG_TERM,
                    description=f"Property market appreciation: Estimated gain ₹{appreciation:,.0f}",
                )

        return None

    def apply_life_event(self, event: LifeEvent) -> None:
        """Apply a life event's impact to jars"""
        if event.event_type == LifeEventType.DEMONETIZATION:
            # Loss on cash in emergency fund
            self.current_jars.emergency *= 0.86

        elif event.event_type == LifeEventType.MEDICAL_EMERGENCY:
            # Insurance covers 70%, rest from short-term
            insurance_cover = min(event.impact_amount * 0.7, self.current_jars.insurance)
            remaining = event.impact_amount - insurance_cover
            self.current_jars.insurance -= insurance_cover
            self.current_jars.short_term -= min(remaining, self.current_jars.short_term)

        elif event.event_type == LifeEventType.WEDDING:
            # Draw from short-term primarily
            draw = min(event.impact_amount, self.current_jars.short_term)
            self.current_jars.short_term -= draw
            if draw < event.impact_amount:
                # Top up from long-term
                additional = min(event.impact_amount - draw, self.current_jars.long_term)
                self.current_jars.long_term -= additional

        elif event.event_type == LifeEventType.MARKET_CORRECTION:
            # Long-term jar affected by market downturn
            impact = self.current_jars.long_term * event.impact_amount
            self.current_jars.long_term += impact

        elif event.event_type == LifeEventType.HOME_REPAIR:
            # Draw from short-term
            draw = min(event.impact_amount, self.current_jars.short_term)
            self.current_jars.short_term -= draw

        elif event.event_type in [LifeEventType.SALARY_INCREASE, LifeEventType.FESTIVAL_BONUS]:
            # Bonus goes to long-term (following optimal allocation)
            multiplier = self.current_jars.long_term / max(
                self.current_jars.total(), 1
            )  # Proportional allocation
            self.current_jars.long_term += event.impact_amount * 0.35
            self.current_jars.short_term += event.impact_amount * 0.15
            self.current_jars.emergency += event.impact_amount * 0.25
            self.current_jars.insurance += event.impact_amount * 0.15
            self.current_jars.gold += event.impact_amount * 0.10

        # New Indian crisis events
        elif event.event_type == LifeEventType.GST_IMPLEMENTATION:
            # Business income drop for 3 months
            impact = self.current_jars.long_term * event.impact_amount
            self.current_jars.long_term += impact

        elif event.event_type == LifeEventType.LIQUIDITY_CRUNCH:
            # FD yields drop, affects emergency fund and short-term
            self.current_jars.emergency *= 0.95
            self.current_jars.short_term *= 0.97

        elif event.event_type == LifeEventType.MONSOON_FAILURE:
            # Agricultural income loss - draw from emergency fund
            total_loss = self.initial_income * abs(event.impact_amount) * 3  # 3-month impact
            draw = min(total_loss, self.current_jars.emergency)
            self.current_jars.emergency -= draw

        elif event.event_type == LifeEventType.RUPEE_DEPRECIATION:
            # Long-term investments affected
            impact = self.current_jars.long_term * event.impact_amount
            self.current_jars.long_term += impact

        elif event.event_type == LifeEventType.DOWRY_NEGOTIATION:
            # Major expense from short-term
            draw = min(event.impact_amount, self.current_jars.short_term)
            self.current_jars.short_term -= draw
            if draw < event.impact_amount:
                additional = min(event.impact_amount - draw, self.current_jars.long_term)
                self.current_jars.long_term -= additional

        elif event.event_type == LifeEventType.DISHONEST_CONTRACTOR:
            # Fraud loss from short-term
            draw = min(event.impact_amount, self.current_jars.short_term)
            self.current_jars.short_term -= draw

        elif event.event_type == LifeEventType.COMPETITIVE_EXAM_COACHING:
            # Monthly coaching commitment from short-term
            draw = min(event.impact_amount, self.current_jars.short_term)
            self.current_jars.short_term -= draw

        elif event.event_type == LifeEventType.PROPERTY_APPRECIATION_SPIKE:
            # Gain to long-term investments
            self.current_jars.long_term += event.impact_amount

    def apply_jar_returns(self) -> JarAllocation:
        """Apply monthly returns to each jar, return the growth amounts"""
        growth = JarAllocation(0, 0, 0, 0, 0)

        for jar_type, annual_rate in self.JAR_RETURNS.items():
            monthly_rate = (1 + annual_rate) ** (1 / 12) - 1
            current_amount = getattr(self.current_jars, jar_type.value)
            jar_growth = current_amount * monthly_rate
            setattr(self.current_jars, jar_type.value, current_amount + jar_growth)
            setattr(growth, jar_type.value, jar_growth)

        return growth

    def simulate_month(self, month: int, new_allocation: Optional[JarAllocation] = None) -> MonthlyState:
        """Simulate one month"""
        self.current_month = month

        # Get income and expenses
        income = self.get_monthly_income(month)
        expenses = self.get_monthly_expenses(month)
        surplus = income - expenses
        
        # Deduct negative surplus from emergency fund
        if surplus < 0:
            self.current_jars.emergency += surplus

        # Update allocation if provided
        if new_allocation is not None:
            self.current_jars = new_allocation

        # Apply returns from current jars
        jar_returns = self.apply_jar_returns()

        # Generate and apply life event
        event = self.generate_life_event(month)
        if event:
            self.apply_life_event(event)
            self.life_events_log.append(event)

        # Ensure no negative balances
        self.current_jars.emergency = max(0, self.current_jars.emergency)
        self.current_jars.insurance = max(0, self.current_jars.insurance)
        self.current_jars.short_term = max(0, self.current_jars.short_term)
        self.current_jars.long_term = max(0, self.current_jars.long_term)
        self.current_jars.gold = max(0, self.current_jars.gold)

        state = MonthlyState(
            month=month,
            income=income,
            expenses=expenses,
            jars=JarAllocation(
                self.current_jars.emergency,
                self.current_jars.insurance,
                self.current_jars.short_term,
                self.current_jars.long_term,
                self.current_jars.gold,
            ),
            event=event,
            jar_returns=jar_returns,
        )

        self.history.append(state)
        return state

    def calculate_optimal_allocation(self, surplus: float) -> JarAllocation:
        """Calculate optimal allocation for a given surplus"""
        return JarAllocation(
            emergency=surplus * self.OPTIMAL_ALLOCATION[JarType.EMERGENCY_FUND],
            insurance=surplus * self.OPTIMAL_ALLOCATION[JarType.INSURANCE],
            short_term=surplus * self.OPTIMAL_ALLOCATION[JarType.SHORT_TERM],
            long_term=surplus * self.OPTIMAL_ALLOCATION[JarType.LONG_TERM],
            gold=surplus * self.OPTIMAL_ALLOCATION[JarType.GOLD],
        )

    def calculate_resilience_score(self) -> Tuple[float, Dict]:
        """Calculate Financial Wellbeing Index (0-100)"""
        final_state = self.history[-1] if self.history else None
        if not final_state:
            return 0.0, {}

        jars = final_state.jars
        total_wealth = jars.total()

        # Component 1: Wealth accumulation (0-30 points)
        wealth_score = min(
            30,
            (total_wealth / (self.initial_income * 30)) * 30,  # Compare to 30 months income
        )

        # Component 2: Emergency fund adequacy (0-25 points)
        months_of_expenses = (
            jars.emergency / (self.get_monthly_expenses(self.current_month))
            if self.get_monthly_expenses(self.current_month) > 0
            else 0
        )
        emergency_score = min(25, (months_of_expenses / 6) * 25)  # 6 months ideal

        # Component 3: Diversification (0-20 points)
        allocation_efficiency = 0
        for jar_type, optimal_pct in self.OPTIMAL_ALLOCATION.items():
            actual_pct = getattr(jars, jar_type.value) / max(total_wealth, 1)
            efficiency = 1 - abs(actual_pct - optimal_pct)
            allocation_efficiency += efficiency
        diversification_score = (allocation_efficiency / len(self.OPTIMAL_ALLOCATION)) * 20

        # Component 4: Long-term wealth (0-15 points)
        long_term_pct = jars.long_term / max(total_wealth, 1)
        long_term_score = min(15, long_term_pct * 30)

        # Component 5: Gold hedge ratio (0-10 points)
        gold_pct = jars.gold / max(total_wealth, 1)
        gold_score = 10 if 0.05 <= gold_pct <= 0.15 else 5

        total_score = (
            wealth_score
            + emergency_score
            + diversification_score
            + long_term_score
            + gold_score
        )

        return total_score, {
            "wealth_score": wealth_score,
            "emergency_score": emergency_score,
            "diversification_score": diversification_score,
            "long_term_score": long_term_score,
            "gold_score": gold_score,
            "total": total_score,
        }

    def get_age_at_month(self, month: int) -> int:
        """Calculate age at a given month"""
        return self.starting_age + (month // 12)

    def get_summary(self) -> Dict:
        """Get game summary"""
        final_state = self.history[-1] if self.history else None
        resilience_score, resilience_breakdown = self.calculate_resilience_score()

        # Compile decision history
        decisions_made = [
            {
                "month": d.get("month"),
                "event_type": d.get("event_type"),
                "event_description": d.get("event_description"),
                "decision_made": d.get("decision_made"),
                "option_title": d.get("option_title"),
                "risk_level": d.get("risk_level"),
                "outcome_description": d.get("outcome_description"),
            }
            for d in self.decision_history
        ]

        return {
            "total_months": self.current_month,
            "final_age": self.get_age_at_month(self.current_month),
            "final_wealth": final_state.jars.total() if final_state else 0,
            "final_allocation": (
                final_state.jars.to_dict() if final_state else {}
            ),
            "resilience_score": resilience_score,
            "resilience_breakdown": resilience_breakdown,
            "total_events": len(self.life_events_log),
            "events_log": [
                {
                    "month": e.month,
                    "type": e.event_type.value,
                    "amount": e.impact_amount,
                    "description": e.description,
                    "has_decision": e.has_decision,
                    "decision_made": e.chosen_option_idx is not None,
                }
                for e in self.life_events_log
            ],
            "decisions_made": decisions_made,
            "decision_count": len(decisions_made),
            "average_monthly_income": (
                sum(s.income for s in self.history) / len(self.history)
                if self.history
                else 0
            ),
        }

    def get_event_with_options(self, month: int) -> Optional[Dict]:
        """Get event and decision options for current month"""
        if not self.history or month > len(self.history):
            return None

        state = self.history[month - 1] if month > 0 else None
        if not state or not state.event:
            return None

        event = state.event
        if not event.has_decision:
            return None

        # Format event with options
        options = [
            {
                "index": idx,
                "title": opt.title,
                "description": opt.description,
                "risk_level": opt.risk_level,
                "consequences": opt.consequences,
                "monthly_impact": opt.monthly_impact,
                "months": opt.months,
                "long_term_effect": opt.long_term_effect,
            }
            for idx, opt in enumerate(event.decision_options)
        ]

        return {
            "month": event.month,
            "event_type": event.event_type.value,
            "description": event.description,
            "decision_title": event.decision_title,
            "has_decision": True,
            "options": options,
        }

    def record_decision(self, month: int, option_idx: int) -> None:
        """Record a player decision"""
        if not self.history or month > len(self.history):
            return

        state = self.history[month - 1] if month > 0 else None
        if not state or not state.event or not state.event.has_decision:
            return

        event = state.event
        if option_idx >= len(event.decision_options):
            return

        option = event.decision_options[option_idx]

        # Apply the decision
        self.apply_decision(event, option_idx)

        # Record in decision history
        self.decision_history.append({
            "month": month,
            "event_type": event.event_type.value,
            "event_description": event.description,
            "decision_made": option.title,
            "option_title": option.title,
            "risk_level": option.risk_level,
            "outcome_description": option.long_term_effect,
        })

