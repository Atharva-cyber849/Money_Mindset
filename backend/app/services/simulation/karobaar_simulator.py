"""
Karobaar Simulator - 43-year life simulation game
Manages career, family, and financial decisions with branching consequences
"""
import random
import json
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple
from datetime import datetime


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class City(str, Enum):
    MUMBAI = "mumbai"
    BANGALORE = "bangalore"
    DELHI = "delhi"
    TIER2 = "tier2"


class Education(str, Enum):
    UG = "ug"
    PG = "pg"
    IIT = "iit"


class EducationSubType(str, Enum):
    """Detailed education specialization"""
    IIT_NIT = "iit_nit"
    STATE_COLLEGE = "state_college"
    PRIVATE_COLLEGE = "private_college"
    IIM_MBA = "iim_mba"
    TIER2_BSCHOOL = "tier2_bschool"
    ONLINE_MBA = "online_mba"
    CA = "ca"  # Chartered Accountant
    CS = "cs"  # Company Secretary
    MEDICAL = "medical"


class MarriageType(str, Enum):
    """Marriage arrangement types"""
    ARRANGED = "arranged"
    LOVE = "love"
    LOVE_ARRANGED = "love_arranged"


class FamilyModel(str, Enum):
    """Family structure choices"""
    JOINT = "joint"
    NUCLEAR = "nuclear"
    NUCLEAR_NEARBY = "nuclear_nearby"


class CareerPath(str, Enum):
    SALARIED = "salaried"
    BUSINESS = "business"
    FREELANCE = "freelance"


class DecisionType(str, Enum):
    CAREER_PATH = "career_path"
    MBA_EDUCATION = "mba_education"
    RELOCATION = "relocation"
    MARRIAGE = "marriage"
    HOME_PURCHASE = "home_purchase"
    FIRST_CHILD = "first_child"
    JOB_CHANGE = "job_change"
    BUSINESS_STARTUP = "business_startup"
    INVESTMENT_AGGRESSION = "investment_aggression"
    PARENT_SUPPORT = "parent_support"
    RETIREMENT_TIMING = "retirement_timing"
    # New Indian-specific decision types
    MARRIAGE_NEGOTIATION = "marriage_negotiation"
    DOWRY_NEGOTIATION = "dowry_negotiation"
    FAMILY_MODEL = "family_model"
    SIBLING_SUPPORT = "sibling_support"
    RELIGIOUS_OBLIGATION = "religious_obligation"
    CHILDRENS_EDUCATION = "childrens_education"
    LOVE_MARRIAGE = "love_marriage"
    BUSINESS_PARTNERSHIP = "business_partnership"
    PROPERTY_INHERITANCE = "property_inheritance"
    POLITICAL_DISRUPTION = "political_disruption"
    MATERNAL_CAREER_BREAK = "maternal_career_break"
    CAREER_REENTRY = "career_reentry"
    PARENT_CARE = "parent_care"


# Career progression tables
CAREER_PATHS = {
    CareerPath.SALARIED: {
        "entry_salary": {Education.UG: 400000, Education.PG: 700000, Education.IIT: 900000},
        "growth_factor": 1.05,
        "max_salary": {Education.UG: 1800000, Education.PG: 3500000, Education.IIT: 6000000},
        "satisfaction_baseline": 60,
    },
    CareerPath.BUSINESS: {
        "entry_capital_needed": 500000,
        "success_probability": 0.5,
        "income_volatility": 0.4,
        "satisfaction_baseline": 75,
    },
    CareerPath.FREELANCE: {
        "entry_salary": 600000,
        "growth_factor": 1.04,
        "stability_score": 0.5,
        "satisfaction_baseline": 65,
    },
}

# City multipliers for cost & income
CITY_MULTIPLIERS = {
    City.MUMBAI: {"rent": 1.5, "salary": 1.3, "property": 1.8, "cost_of_living": 1.4},
    City.BANGALORE: {"rent": 1.2, "salary": 1.2, "property": 1.4, "cost_of_living": 1.15},
    City.DELHI: {"rent": 1.3, "salary": 1.25, "property": 1.6, "cost_of_living": 1.25},
    City.TIER2: {"rent": 0.8, "salary": 0.9, "property": 0.7, "cost_of_living": 0.8},
}

# Life event probabilities by age
LIFE_EVENTS = {
    "marriage": (24, 36, 0.65),
    "first_child": (26, 38, 0.55),
    "job_opportunity": (25, 60, 0.45),
    "health_issue": (30, 65, 0.15),
    "parent_support": (35, 55, 0.20),
}

# Regional dowry variations (cultural context)
REGIONAL_DOWRY = {
    City.DELHI: {"prevalence": 0.85, "avg_dowry": 1500000, "female_penalty": -0.15, "family_pressure": 0.9},
    City.MUMBAI: {"prevalence": 0.70, "avg_dowry": 1200000, "female_penalty": -0.12, "family_pressure": 0.7},
    City.BANGALORE: {"prevalence": 0.40, "avg_dowry": 800000, "female_penalty": -0.08, "family_pressure": 0.5},
    City.TIER2: {"prevalence": 0.50, "avg_dowry": 500000, "female_penalty": -0.10, "family_pressure": 0.6},
}

# Education salary multipliers (by sub-type)
EDUCATION_MULTIPLIERS = {
    EducationSubType.STATE_COLLEGE: 0.8,
    EducationSubType.PRIVATE_COLLEGE: 1.0,
    EducationSubType.IIT_NIT: 1.3,
    EducationSubType.TIER2_BSCHOOL: 1.25,
    EducationSubType.IIM_MBA: 1.4,
    EducationSubType.ONLINE_MBA: 1.15,
    EducationSubType.CA: 1.5,
    EducationSubType.CS: 1.4,
    EducationSubType.MEDICAL: 1.6,
}

# Family model cost multipliers
FAMILY_MODEL_COSTS = {
    FamilyModel.JOINT: 0.8,      # Cost savings, shared expenses
    FamilyModel.NUCLEAR: 1.2,    # Independence, higher costs
    FamilyModel.NUCLEAR_NEARBY: 1.0,  # Balance
}


@dataclass
class LifeState:
    age: int
    current_month: int
    current_year: int
    gender: str
    city: str
    education: str

    # Career state
    job_title: str
    company_size: str
    current_salary: float
    years_in_job: int
    career_changes_count: int
    business_status: Optional[str]
    has_mba: bool

    # Family state
    marital_status: str
    spouse_income: float
    num_children: int
    eldest_child_age: Optional[int]

    # Financial state
    net_worth: float
    monthly_savings: float
    outstanding_debt: float
    emergency_fund: float
    investments: Dict[str, float]  # stocks, gold, realestate, fd

    # Personal state
    career_satisfaction: float
    family_happiness: float
    work_life_balance: float
    health_score: float

    # New Indian-specific state
    education_subtype: Optional[str] = None
    marriage_type: Optional[str] = None
    family_model: Optional[str] = None
    dowry_paid: float = 0.0
    parent_age: int = 50  # Starting parent age
    parent_support_active: bool = False
    parent_support_amount: float = 0.0
    sibling_support_years: int = 0
    career_break_years: int = 0  # For female career break tracking

    def to_dict(self):
        return asdict(self)


@dataclass
class DecisionOption:
    id: int
    text: str
    salary_impact: float
    happiness_impact: float
    career_satisfaction_impact: float
    wealth_impact: float
    debt_impact: float
    side_effects: Dict


@dataclass
class DecisionPoint:
    id: str
    age: int
    decision_type: str
    description: str
    options: List[DecisionOption]


class KarobarSimulator:
    """Main simulator for 43-year life simulation game"""

    def __init__(
        self,
        gender: str,
        city: str,
        education: str,
        starting_job: str,
    ):
        """Initialize game state"""
        self.gender = gender
        self.city = city
        self.education = education
        self.starting_job = starting_job

        # Calculate starting salary
        start_salary = CAREER_PATHS[CareerPath(starting_job)]["entry_salary"][
            Education(education)
        ]
        city_mult = CITY_MULTIPLIERS[City(city)]["salary"]
        self.starting_salary = start_salary * city_mult

        # Apply gender penalty (15% for women in India - realistic representation)
        if gender == "female":
            self.starting_salary *= 0.85

        # Initialize game state
        self.state = LifeState(
            age=22,
            current_month=0,
            current_year=0,
            gender=gender,
            city=city,
            education=education,
            job_title="Associate",
            company_size="large",
            current_salary=self.starting_salary,
            years_in_job=0,
            career_changes_count=0,
            business_status=None,
            has_mba=False,
            marital_status="single",
            spouse_income=0,
            num_children=0,
            eldest_child_age=None,
            net_worth=100000,
            monthly_savings=0,
            outstanding_debt=0,
            emergency_fund=50000,
            investments={"stocks": 50000, "gold": 0, "realestate": 0, "fd": 0},
            career_satisfaction=60,
            family_happiness=70,
            work_life_balance=70,
            health_score=85,
        )

        self.decision_history = []
        self.yearly_snapshots = []
        self.events_log = []
        self.random_seed = random.randint(0, 100000)

    def advance_year(self) -> Optional[DecisionPoint]:
        """Advance one year and check for decision points"""
        if self.state.age >= 65:
            return None

        # Age increment
        self.state.age += 1
        self.state.current_year += 1
        self.state.current_month += 12
        self.state.years_in_job += 1

        # Apply salary growth & adjustments
        self._apply_salary_growth()

        # Calculate expenses
        expenses = self._calculate_yearly_expenses()

        # Calculate savings
        annual_income = (self.state.current_salary + self.state.spouse_income) / 12
        annual_savings = max(0, annual_income - expenses)
        self.state.monthly_savings = annual_savings / 12

        # Apply investment returns
        self._apply_investment_returns()

        # Update net worth
        total_assets = (
            self.emergency_fund
            + sum(self.state.investments.values())
            + (self.state.net_worth - self.emergency_fund - sum(self.state.investments.values()))
        )
        self.state.net_worth += annual_savings

        # Create yearly snapshot
        snapshot = {
            "year": self.state.current_year,
            "age": self.state.age,
            "salary": self.state.current_salary,
            "net_worth": self.state.net_worth,
            "family_status": self.state.marital_status,
            "career_satisfaction": self.state.career_satisfaction,
            "happiness": self.state.family_happiness,
        }
        self.yearly_snapshots.append(snapshot)

        # Generate next decision point
        return self._generate_decision_point()

    def _apply_salary_growth(self):
        """Apply annual salary growth based on career satisfaction and experience"""
        if self.state.business_status == "active":
            # Business income more volatile
            growth_factor = 1 + (0.08 + random.random() * 0.12)
        else:
            # Standard growth 5% + bonus based on satisfaction
            satisfaction_boost = (self.state.career_satisfaction - 60) / 1000
            growth_factor = 1 + (0.05 + satisfaction_boost)

        self.state.current_salary *= growth_factor

        # Cap based on career path
        if self.state.business_status != "active":
            max_salary = CAREER_PATHS[CareerPath(self.state.starting_job)]["max_salary"][
                Education(self.education)
            ]
            self.state.current_salary = min(self.state.current_salary, max_salary)

    def _calculate_yearly_expenses(self) -> float:
        """Calculate yearly expenses based on family size and city"""
        base_expense = 300000  # Base annual expense
        city_mult = CITY_MULTIPLIERS[City(self.city)]["cost_of_living"]

        # Adjust for family size
        family_mult = 1.0
        if self.state.marital_status == "married":
            family_mult += 0.25
        family_mult += self.state.num_children * 0.15

        # Add home loan if applicable
        home_loan_amt = 0
        if self.state.outstanding_debt > 0:
            home_loan_amt = self.state.outstanding_debt * 0.06  # 6% annual on outstanding

        total = (base_expense * city_mult * family_mult) + home_loan_amt
        return total

    def _apply_investment_returns(self):
        """Apply annual investment returns"""
        returns_rates = {
            "stocks": 0.10,
            "gold": 0.05,
            "realestate": 0.08,
            "fd": 0.06,
        }

        for asset_type, rate in returns_rates.items():
            self.state.investments[asset_type] *= 1 + rate

    def _generate_decision_point(self) -> Optional[DecisionPoint]:
        """Generate next decision point based on age and randomness"""
        # Age-based decision triggers
        decision = None

        if self.state.age == 24 and self.state.current_year == 2:
            # MBA opportunity
            if not self.state.has_mba:
                decision = self._create_mba_decision()

        elif self.state.age == 25 and self.state.current_year == 3:
            # Job opportunity (relocation)
            if random.random() < 0.6:
                decision = self._create_relocation_decision()

        elif (
            25 <= self.state.age <= 35
            and self.state.marital_status == "single"
            and random.random() < 0.15
        ):
            # Marriage opportunity
            decision = self._create_marriage_decision()

        elif (
            self.state.marital_status == "married"
            and self.state.num_children == 0
            and 26 <= self.state.age <= 38
            and random.random() < 0.15
        ):
            # First child
            decision = self._create_child_decision()

        elif 30 <= self.state.age <= 50 and random.random() < 0.1:
            # Business opportunity
            if not self.state.business_status:
                decision = self._create_business_decision()

        elif self.state.age == 35 and self.state.outstanding_debt == 0:
            # Home purchase opportunity
            decision = self._create_home_purchase_decision()

        elif 55 <= self.state.age <= 60 and self.state.current_year <= 38:
            # Retirement planning
            decision = self._create_retirement_decision()

        return decision

    def _create_mba_decision(self) -> DecisionPoint:
        """Create MBA education decision"""
        options = [
            DecisionOption(
                id=0,
                text="Pursue MBA (2-year opportunity cost but +30% salary ceiling)",
                salary_impact=0.30,
                happiness_impact=-5,
                career_satisfaction_impact=10,
                wealth_impact=-500000,
                debt_impact=800000,
                side_effects={"has_mba": True, "years_delayed": 2},
            ),
            DecisionOption(
                id=1,
                text="Skip MBA, focus on work experience",
                salary_impact=0,
                happiness_impact=0,
                career_satisfaction_impact=5,
                wealth_impact=500000,
                debt_impact=0,
                side_effects={},
            ),
        ]

        return DecisionPoint(
            id=f"mba_{self.state.age}",
            age=self.state.age,
            decision_type="mba_education",
            description="Your company offers MBA sponsorship. Will you accept the 2-year program?",
            options=options,
        )

    def _create_relocation_decision(self) -> DecisionPoint:
        """Create relocation decision (job offer in bigger city)"""
        salary_increase = 0.2
        options = [
            DecisionOption(
                id=0,
                text="Accept relocation to Mumbai (+20% salary, +exploration)",
                salary_impact=salary_increase,
                happiness_impact=-5,
                career_satisfaction_impact=15,
                wealth_impact=0,
                debt_impact=0,
                side_effects={"relocated": True},
            ),
            DecisionOption(
                id=1,
                text="Stay in current city",
                salary_impact=0.05,
                happiness_impact=0,
                career_satisfaction_impact=0,
                wealth_impact=0,
                debt_impact=0,
                side_effects={},
            ),
        ]

        return DecisionPoint(
            id=f"relocation_{self.state.age}",
            age=self.state.age,
            decision_type="relocation",
            description="Top tech company in Mumbai offers you a role. Will you relocate?",
            options=options,
        )

    def _create_marriage_decision(self) -> DecisionPoint:
        """Create marriage decision"""
        options = [
            DecisionOption(
                id=0,
                text="Accept marriage proposal",
                salary_impact=0,
                happiness_impact=30,
                career_satisfaction_impact=-5,
                wealth_impact=0,
                debt_impact=300000 if self.gender == "male" else 0,  # Dowry scenario for males
                side_effects={"married": True, "spouse_income": self.starting_salary * 0.8},
            ),
            DecisionOption(
                id=1,
                text="Decline, focus on career for now",
                salary_impact=0,
                happiness_impact=-8,
                career_satisfaction_impact=10,
                wealth_impact=0,
                debt_impact=0,
                side_effects={},
            ),
        ]

        return DecisionPoint(
            id=f"marriage_{self.state.age}",
            age=self.state.age,
            decision_type="marriage",
            description="Your parents found a perfect match. Will you consider marriage?",
            options=options,
        )

    def _create_child_decision(self) -> DecisionPoint:
        """Create first child decision"""
        options = [
            DecisionOption(
                id=0,
                text="Plan first child (happiness +20, expenses +30%)",
                salary_impact=0,
                happiness_impact=20,
                career_satisfaction_impact=-8,
                wealth_impact=0,
                debt_impact=0,
                side_effects={"num_children": 1},
            ),
            DecisionOption(
                id=1,
                text="Wait a few more years",
                salary_impact=0,
                happiness_impact=-5,
                career_satisfaction_impact=5,
                wealth_impact=0,
                debt_impact=0,
                side_effects={},
            ),
        ]

        return DecisionPoint(
            id=f"child_{self.state.age}",
            age=self.state.age,
            decision_type="first_child",
            description="You and your spouse discuss having your first child. Ready?",
            options=options,
        )

    def _create_home_purchase_decision(self) -> DecisionPoint:
        """Create home purchase decision"""
        city_property_multiplier = CITY_MULTIPLIERS[City(self.city)]["property"]
        home_price = 2500000 * city_property_multiplier

        options = [
            DecisionOption(
                id=0,
                text=f"Buy a home (₹{home_price/100000:.0f}L, 20-year loan)",
                salary_impact=0,
                happiness_impact=15,
                career_satisfaction_impact=0,
                wealth_impact=home_price * 0.3,  # Down payment
                debt_impact=home_price * 0.8,
                side_effects={"home_owned": True},
            ),
            DecisionOption(
                id=1,
                text="Continue renting, invest instead",
                salary_impact=0,
                happiness_impact=0,
                career_satisfaction_impact=5,
                wealth_impact=0,
                debt_impact=0,
                side_effects={},
            ),
        ]

        return DecisionPoint(
            id=f"home_{self.state.age}",
            age=self.state.age,
            decision_type="home_purchase",
            description="Your financial situation is stable. Consider buying a home?",
            options=options,
        )

    def _create_business_decision(self) -> DecisionPoint:
        """Create business startup decision"""
        options = [
            DecisionOption(
                id=0,
                text="Start your own business (high risk, high reward)",
                salary_impact=0,
                happiness_impact=10,
                career_satisfaction_impact=25,
                wealth_impact=-1000000,  # Initial capital
                debt_impact=0,
                side_effects={"business_status": "active"},
            ),
            DecisionOption(
                id=1,
                text="Stay employed, side business later",
                salary_impact=0,
                happiness_impact=0,
                career_satisfaction_impact=-5,
                wealth_impact=0,
                debt_impact=0,
                side_effects={},
            ),
        ]

        return DecisionPoint(
            id=f"business_{self.state.age}",
            age=self.state.age,
            decision_type="business_startup",
            description="You've been offered a chance to launch your startup. Will you take it?",
            options=options,
        )

    def _create_retirement_decision(self) -> DecisionPoint:
        """Create retirement timing decision"""
        options = [
            DecisionOption(
                id=0,
                text="Retire at 55 (enjoy youth, lower final corpus)",
                salary_impact=0,
                happiness_impact=20,
                career_satisfaction_impact=-30,
                wealth_impact=0,
                debt_impact=0,
                side_effects={"retire_age": 55},
            ),
            DecisionOption(
                id=1,
                text="Work until 60 (maximize wealth)",
                salary_impact=0,
                happiness_impact=0,
                career_satisfaction_impact=10,
                wealth_impact=0,
                debt_impact=0,
                side_effects={"retire_age": 60},
            ),
            DecisionOption(
                id=2,
                text="Work until 65 (max wealth but less leisure)",
                salary_impact=0,
                happiness_impact=-15,
                career_satisfaction_impact=-20,
                wealth_impact=0,
                debt_impact=0,
                side_effects={"retire_age": 65},
            ),
        ]

        return DecisionPoint(
            id=f"retirement_{self.state.age}",
            age=self.state.age,
            decision_type="retirement_timing",
            description="You're approaching retirement. When would you like to retire?",
            options=options,
        )

    def apply_decision(self, decision_id: str, option_id: int) -> Dict:
        """Apply a decision and return consequences"""
        # Find decision point in history
        decision_point = None
        for snapshot in self.yearly_snapshots:
            if snapshot.get("decision_id") == decision_id:
                decision_point = snapshot.get("decision_point")
                break

        if not decision_point:
            raise ValueError(f"Decision {decision_id} not found")

        option = decision_point.options[option_id]

        # Apply impacts
        self.state.current_salary *= 1 + option.salary_impact
        self.state.career_satisfaction += option.career_satisfaction_impact
        self.state.family_happiness += option.happiness_impact
        self.state.net_worth += option.wealth_impact
        self.state.outstanding_debt += option.debt_impact

        # Apply side effects
        for key, value in option.side_effects.items():
            if key == "married":
                self.state.marital_status = "married"
                self.state.spouse_income = value
            elif key == "spouse_income":
                self.state.spouse_income = value
            elif key == "num_children":
                self.state.num_children = value
                self.state.eldest_child_age = 0
            elif key == "has_mba":
                self.state.has_mba = True
            elif key == "business_status":
                self.state.business_status = value

        # Record decision
        self.decision_history.append(
            {
                "age": self.state.age,
                "decision_type": decision_point.decision_type,
                "choice": option.text,
                "impacts": {
                    "salary": option.salary_impact,
                    "happiness": option.happiness_impact,
                    "career": option.career_satisfaction_impact,
                    "wealth": option.wealth_impact,
                },
            }
        )

        return {
            "message": f"Decision applied: {option.text}",
            "impacts": {
                "salary_impact": option.salary_impact,
                "happiness_impact": option.happiness_impact,
                "career_satisfaction_impact": option.career_satisfaction_impact,
                "wealth_impact": option.wealth_impact,
                "debt_impact": option.debt_impact,
            },
        }

    def get_final_scores(self) -> Dict:
        """Calculate final scores at age 65"""
        # Career score (0-100)
        career_score = min(
            100,
            (self.state.career_satisfaction * 0.4)
            + (min(self.state.current_salary, 5000000) / 50000 * 0.6),
        )

        # Financial score (0-100)
        financial_benchmark = 2000000 * self.state.age  # Benchmark for this age
        financial_score = min(
            100,
            max(
                0,
                ((self.state.net_worth - self.state.outstanding_debt) / financial_benchmark)
                * 100,
            ),
        )

        # Happiness score (0-100)
        happiness_score = (
            (self.state.family_happiness * 0.4)
            + (self.state.work_life_balance * 0.35)
            + (self.state.health_score * 0.25)
        )

        # Overall score (weighted)
        overall_score = (career_score * 0.35) + (financial_score * 0.40) + (happiness_score * 0.25)

        return {
            "career_score": round(career_score, 1),
            "financial_score": round(financial_score, 1),
            "happiness_score": round(happiness_score, 1),
            "overall_score": round(overall_score, 1),
            "final_net_worth": round(self.state.net_worth, 0),
            "final_salary": round(self.state.current_salary, 0),
            "final_age": self.state.age,
            "decisions_made": len(self.decision_history),
        }

    def get_summary(self) -> Dict:
        """Get complete game summary"""
        return {
            "session_data": self.state.to_dict(),
            "yearly_snapshots": self.yearly_snapshots,
            "decision_history": self.decision_history,
            "events_log": self.events_log,
        }
