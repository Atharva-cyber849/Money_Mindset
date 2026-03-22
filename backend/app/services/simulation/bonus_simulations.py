"""
Bonus Simulations: Advanced Financial Concepts
- Inflation Impact Simulator
- Rent vs Buy Calculator
- Side Hustle Income Multiplier
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum
import random


class PropertyType(Enum):
    """Property types for rent vs buy"""
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    SINGLE_FAMILY = "single_family"


class SideHustleType(Enum):
    """Side hustle categories"""
    FREELANCE = "freelance"
    GIGS = "gigs"
    PASSIVE_INCOME = "passive_income"
    SMALL_BUSINESS = "small_business"


@dataclass
class InflationScenario:
    """Inflation impact over time"""
    year: int
    inflation_rate: float
    starting_amount: float
    purchasing_power: float
    loss_percentage: float


@dataclass
class RentVsBuyComparison:
    """Complete rent vs buy analysis"""
    scenario: str
    total_cost: float
    equity_built: float
    net_wealth: float
    monthly_payment: float
    total_paid: float
    opportunity_cost: float
    flexibility_score: int  # 1-10


@dataclass
class SideHustleResult:
    """Side hustle income progression"""
    month: int
    hours_per_week: float
    hourly_rate: float
    monthly_income: float
    cumulative_income: float
    skill_level: int  # 1-10
    stress_level: int  # 1-10


class InflationSimulator:
    """
    Demonstrates the hidden tax of inflation
    Shows how purchasing power erodes over time
    Indian context: Higher food inflation, regional variations, seasonal spikes
    """

    # Historical inflation rates (1960-2023 average ~3.8% global, 6-7% India)
    HISTORICAL_AVERAGE = 0.038
    LOW_INFLATION = 0.02
    MODERATE_INFLATION = 0.04
    HIGH_INFLATION = 0.08

    # Indian inflation context (higher than developed countries)
    INDIA_LOW_INFLATION = 0.05
    INDIA_MODERATE_INFLATION = 0.065
    INDIA_HIGH_INFLATION = 0.10

    # Indian inflation basket composition (% weights)
    INFLATION_BASKET = {
        "food": 0.40,        # Highly volatile in India (8-10% typical)
        "energy": 0.10,      # Oil import dependent
        "housing": 0.20,     # Real estate driven
        "others": 0.30,      # Goods and services
    }

    # Regional inflation variations (multiplier)
    REGIONAL_MULTIPLIERS = {
        "metro": 1.15,       # Mumbai, Delhi, Bangalore (15% higher)
        "tier2": 1.0,        # Pune, Hyderabad, Chennai (baseline)
        "tier3": 0.85,       # Smaller cities (15% lower)
    }

    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)

    def simulate_purchasing_power(
        self,
        starting_amount: float,
        years: int,
        inflation_scenario: str = "moderate",
        region: str = "tier2",
        is_india: bool = True
    ) -> List[InflationScenario]:
        """
        Simulate how much purchasing power erodes

        Args:
            starting_amount: Current rupee amount
            years: Years to project
            inflation_scenario: low, moderate, or high
            region: metro, tier2, tier3
            is_india: Use Indian inflation rates if True

        Returns:
            List of yearly purchasing power calculations
        """
        scenarios = []

        # Select inflation rate
        if is_india:
            if inflation_scenario == "low":
                base_rate = self.INDIA_LOW_INFLATION
            elif inflation_scenario == "high":
                base_rate = self.INDIA_HIGH_INFLATION
            else:
                base_rate = self.INDIA_MODERATE_INFLATION
        else:
            if inflation_scenario == "low":
                base_rate = self.LOW_INFLATION
            elif inflation_scenario == "high":
                base_rate = self.HIGH_INFLATION
            else:
                base_rate = self.MODERATE_INFLATION

        # Apply regional multiplier
        regional_mult = self.REGIONAL_MULTIPLIERS.get(region, 1.0)
        base_rate *= regional_mult

        purchasing_power = starting_amount

        for year in range(1, years + 1):
            # Add some variance to inflation rate + seasonal spikes
            seasonal_factor = 1.0
            if year % 12 in [10, 11, 12]:  # Post-monsoon & festival season
                seasonal_factor = 1.15  # 15% inflation spike

            # Food inflation dominates in India
            annual_rate = random.gauss(base_rate, base_rate * 0.25)
            annual_rate = max(0.01, annual_rate)  # Minimum 1% inflation
            annual_rate *= seasonal_factor

            # Calculate purchasing power
            purchasing_power /= (1 + annual_rate)
            loss_percentage = ((starting_amount - purchasing_power) / starting_amount) * 100

            scenarios.append(InflationScenario(
                year=year,
                inflation_rate=annual_rate,
                starting_amount=starting_amount,
                purchasing_power=purchasing_power,
                loss_percentage=loss_percentage
            ))

        return scenarios
    
    def calculate_salary_needed(
        self,
        current_salary: float,
        years: int,
        inflation_rate: float = None
    ) -> Dict:
        """
        Calculate how much salary must increase to maintain purchasing power
        """
        if inflation_rate is None:
            inflation_rate = self.MODERATE_INFLATION
        
        needed_salaries = []
        salary = current_salary
        
        for year in range(1, years + 1):
            # Salary must grow by inflation to maintain purchasing power
            salary *= (1 + inflation_rate)
            needed_salaries.append({
                "year": year,
                "needed_salary": salary,
                "increase_from_start": salary - current_salary,
                "increase_percentage": ((salary - current_salary) / current_salary) * 100
            })
        
        return {
            "current_salary": current_salary,
            "needed_salaries": needed_salaries,
            "key_insight": f"After {years} years at {inflation_rate*100:.1f}% inflation, you need ${salary:,.2f} just to maintain today's purchasing power!"
        }
    
    def demonstrate_compound_loss(
        self,
        amount: float,
        years: int = 30
    ) -> Dict:
        """
        Dramatic demonstration of cash losing value
        Example: $10,000 under mattress for 30 years
        """
        scenarios_low = self.simulate_purchasing_power(amount, years, "low")
        scenarios_mod = self.simulate_purchasing_power(amount, years, "moderate")
        scenarios_high = self.simulate_purchasing_power(amount, years, "high")
        
        return {
            "starting_amount": amount,
            "years": years,
            "low_inflation": {
                "final_purchasing_power": scenarios_low[-1].purchasing_power,
                "loss": amount - scenarios_low[-1].purchasing_power,
                "loss_percentage": scenarios_low[-1].loss_percentage
            },
            "moderate_inflation": {
                "final_purchasing_power": scenarios_mod[-1].purchasing_power,
                "loss": amount - scenarios_mod[-1].purchasing_power,
                "loss_percentage": scenarios_mod[-1].loss_percentage
            },
            "high_inflation": {
                "final_purchasing_power": scenarios_high[-1].purchasing_power,
                "loss": amount - scenarios_high[-1].purchasing_power,
                "loss_percentage": scenarios_high[-1].loss_percentage
            },
            "lesson": f"Even at moderate inflation, ${amount:,.0f} loses {scenarios_mod[-1].loss_percentage:.0f}% of its value in {years} years. This is why investing beats saving!"
        }


class RentVsBuySimulator:
    """
    Comprehensive rent vs buy calculator
    Indian context: Property registration tax, maintenance with servants, land ownership cultural importance
    """

    # Indian property costs (₹ based)
    PROPERTY_TAX_RATE = 0.002  # 0.2% of home value annually (varies by state 0.1-0.3%)
    HOME_INSURANCE_RATE = 0.005  # 0.5% of home value annually
    MAINTENANCE_RATE = 0.015  # 1.5% of home value annually (higher due to servants, repairs)
    REGISTRATION_COST_RATE = 0.07  # 5-11% registration (avg 7% in major states)
    STAMP_DUTY_RATE = 0.05  # 5% stamp duty on purchase
    CLOSING_COSTS_RATE = 0.12  # Total 12% for registration + stamp duty
    CAPITAL_GAINS_TAX_LTCG = 0.20  # 20% LTCG after 2 years
    REALTOR_FEE = 0.01  # 1% broker fees when selling (lower in India)

    # Market assumptions (Indian context)
    HOME_APPRECIATION = 0.065  # 6-8% annual appreciation (city specific)
    RENT_INCREASE = 0.05  # 5% annual rent increase (higher in India)
    INVESTMENT_RETURN = 0.10  # 10% stock market return (Indian markets)

    # City-specific property appreciation rates
    CITY_APPRECIATION_RATES = {
        "mumbai": 0.08,
        "delhi": 0.07,
        "bangalore": 0.07,
        "tier2": 0.05,
        "tier3": 0.04,
    }

    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
    
    def compare_scenarios(
        self,
        home_price: float,
        down_payment_percentage: float,
        interest_rate: float,
        monthly_rent: float,
        years: int = 30,
        city: str = "tier2",
        is_india: bool = True
    ) -> Dict[str, RentVsBuyComparison]:
        """
        Comprehensive rent vs buy analysis

        Args:
            home_price: Purchase price of home (₹)
            down_payment_percentage: Down payment as percentage (e.g., 0.20 for 20%)
            interest_rate: Mortgage interest rate (e.g., 0.07 for 7%)
            monthly_rent: Current monthly rent (₹)
            years: Analysis period
            city: City for appreciation rate (mumbai, delhi, bangalore, tier2, tier3)
            is_india: Use Indian tax and cost structure if True

        Returns:
            Comparison of rent vs buy scenarios
        """
        buy_scenario = self._simulate_buying(
            home_price,
            down_payment_percentage,
            interest_rate,
            years,
            city,
            is_india
        )

        rent_scenario = self._simulate_renting(
            monthly_rent,
            home_price * down_payment_percentage,  # Invest down payment instead
            years,
            is_india
        )

        return {
            "buy": buy_scenario,
            "rent": rent_scenario,
            "verdict": self._generate_verdict(buy_scenario, rent_scenario),
            "breakeven_year": self._calculate_breakeven(buy_scenario, rent_scenario, years),
            "cultural_note": "In Indian culture, property ownership is a significant wealth and status indicator beyond financial returns"
        }
    
    def _simulate_buying(
        self,
        home_price: float,
        down_payment_pct: float,
        interest_rate: float,
        years: int,
        city: str = "tier2",
        is_india: bool = True
    ) -> RentVsBuyComparison:
        """Simulate home buying scenario (Indian context)"""
        # Initial costs
        down_payment = home_price * down_payment_pct

        # Indian registration/stamp duty costs
        if is_india:
            registration_and_stamp = home_price * self.CLOSING_COSTS_RATE
        else:
            registration_and_stamp = home_price * 0.03

        total_upfront = down_payment + registration_and_stamp
        loan_amount = home_price - down_payment

        # Calculate monthly mortgage payment (P&I)
        monthly_rate = interest_rate / 12
        num_payments = years * 12

        if monthly_rate > 0:
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** num_payments
            ) / ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_payment = loan_amount / num_payments

        # Additional monthly costs (Indian context - no HOA, but servants/maintenance)
        monthly_property_tax = (home_price * self.PROPERTY_TAX_RATE) / 12
        monthly_insurance = (home_price * self.HOME_INSURANCE_RATE) / 12
        monthly_maintenance = (home_price * self.MAINTENANCE_RATE) / 12

        total_monthly = (
            monthly_payment +
            monthly_property_tax +
            monthly_insurance +
            monthly_maintenance
        )

        # Calculate equity built
        total_paid = (total_monthly * years * 12) + total_upfront

        # Home appreciation (city-specific for India)
        if is_india:
            appreciation_rate = self.CITY_APPRECIATION_RATES.get(city, self.HOME_APPRECIATION)
        else:
            appreciation_rate = self.HOME_APPRECIATION

        future_home_value = home_price * ((1 + appreciation_rate) ** years)

        # Remaining loan balance (simplified)
        total_interest = (monthly_payment * num_payments) - loan_amount
        equity_from_paydown = monthly_payment * num_payments - total_interest

        # Equity = home value - remaining loan + appreciation
        remaining_balance = max(0, loan_amount - equity_from_paydown)
        equity_gained = future_home_value - remaining_balance

        # Account for capital gains tax on sale (India: 20% LTCG after 2 years)
        if is_india and years >= 2:
            capital_gain = future_home_value - home_price
            capital_gains_tax = capital_gain * self.CAPITAL_GAINS_TAX_LTCG
        else:
            capital_gains_tax = 0

        net_wealth = equity_gained - capital_gains_tax

        return RentVsBuyComparison(
            scenario="buy",
            total_cost=total_paid,
            equity_built=equity_gained,
            net_wealth=net_wealth,
            monthly_payment=total_monthly,
            total_paid=total_paid,
            opportunity_cost=0,  # Calculated in verdict
            flexibility_score=3  # Lower flexibility when owning
        )
        
        # Equity = home value - remaining loan
        equity = future_home_value - remaining_balance
        
        # Selling costs
        selling_costs = future_home_value * self.REALTOR_FEE
        net_equity = equity - selling_costs
        
        # Net wealth = equity minus all money spent
        net_wealth = net_equity - total_paid
        
        return RentVsBuyComparison(
            scenario="Buy",
            total_cost=total_paid,
            equity_built=net_equity,
            net_wealth=net_wealth,
            monthly_payment=total_monthly,
            total_paid=total_paid,
            opportunity_cost=0,  # Benchmark scenario
            flexibility_score=3  # Low flexibility (tied to location)
        )
    
    def _simulate_renting(
        self,
        monthly_rent: float,
        investment_amount: float,  # Down payment invested instead
        years: int,
        is_india: bool = True
    ) -> RentVsBuyComparison:
        """Simulate renting + investing scenario"""
        # Rent increases over time
        total_rent_paid = 0
        current_rent = monthly_rent

        if is_india:
            rent_increase_rate = 0.05  # 5% annual in India
        else:
            rent_increase_rate = 0.03  # 3% in developed countries

        for year in range(years):
            total_rent_paid += current_rent * 12
            current_rent *= (1 + rent_increase_rate)

        # Investment growth (down payment invested in stocks/MF)
        investment_balance = investment_amount

        if is_india:
            investment_return = 0.10  # 10% Indian market return
        else:
            investment_return = self.INVESTMENT_RETURN

        for year in range(years):
            investment_balance *= (1 + investment_return)

        # Net wealth = investment value
        net_wealth = investment_balance

        return RentVsBuyComparison(
            scenario="Rent + Invest",
            total_cost=total_rent_paid,
            equity_built=0,  # No home equity
            net_wealth=net_wealth,  # Wealth from investments
            monthly_payment=monthly_rent,
            total_paid=total_rent_paid,
            opportunity_cost=investment_balance,
            flexibility_score=9  # High flexibility (can move anytime)
        )
    
    def _generate_verdict(
        self,
        buy: RentVsBuyComparison,
        rent: RentVsBuyComparison
    ) -> Dict:
        """Generate verdict based on comparison"""
        if buy.net_wealth > rent.net_wealth:
            wealth_difference = buy.net_wealth - rent.net_wealth
            verdict = "Buy wins financially"
            explanation = f"Buying builds ${wealth_difference:,.2f} more wealth over this period. Home equity beats rent payments."
        else:
            wealth_difference = rent.net_wealth - buy.net_wealth
            verdict = "Rent + Invest wins financially"
            explanation = f"Renting and investing the difference creates ${wealth_difference:,.2f} more wealth. Flexibility and investment returns win."
        
        return {
            "verdict": verdict,
            "explanation": explanation,
            "wealth_difference": wealth_difference,
            "considerations": [
                f"Buying: Low flexibility (score {buy.flexibility_score}/10), builds equity",
                f"Renting: High flexibility (score {rent.flexibility_score}/10), liquidity",
                "Buying: Forced savings through mortgage payments",
                "Renting: Requires discipline to invest the difference",
                "Buying: Risk of market downturns affecting home value",
                "Renting: No maintenance headaches or surprise costs"
            ]
        }
    
    def _calculate_breakeven(
        self,
        buy: RentVsBuyComparison,
        rent: RentVsBuyComparison,
        years: int
    ) -> int:
        """Calculate breakeven year (when buying starts winning)"""
        # Simplified: typically 5-7 years
        # This would require year-by-year simulation for accuracy
        if buy.net_wealth > rent.net_wealth:
            return min(5, years)  # Assume 5 years for this simulation
        else:
            return years + 1  # Never breaks even in this period


class SideHustleSimulator:
    """
    Side Hustle Income Multiplier
    Shows how extra income can accelerate financial goals
    """
    
    # Hourly rates by hustle type
    STARTING_RATES = {
        SideHustleType.FREELANCE: 25,
        SideHustleType.GIGS: 15,
        SideHustleType.PASSIVE_INCOME: 10,
        SideHustleType.SMALL_BUSINESS: 20
    }
    
    # Growth potential (skill improvement)
    SKILL_GROWTH_RATE = {
        SideHustleType.FREELANCE: 0.10,  # 10% rate increase per year
        SideHustleType.GIGS: 0.05,
        SideHustleType.PASSIVE_INCOME: 0.15,  # Scales well
        SideHustleType.SMALL_BUSINESS: 0.20  # Highest potential
    }
    
    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
    
    def simulate_side_hustle(
        self,
        hustle_type: SideHustleType,
        hours_per_week: float,
        months: int = 12
    ) -> List[SideHustleResult]:
        """
        Simulate side hustle income over time
        
        Args:
            hustle_type: Type of side hustle
            hours_per_week: Hours committed per week
            months: Duration in months
        
        Returns:
            Monthly progression of income
        """
        results = []
        
        starting_rate = self.STARTING_RATES[hustle_type]
        growth_rate = self.SKILL_GROWTH_RATE[hustle_type]
        
        cumulative_income = 0
        skill_level = 1
        
        for month in range(1, months + 1):
            # Skill improves over time
            months_experience = month / 12
            skill_multiplier = 1 + (growth_rate * months_experience)
            current_rate = starting_rate * skill_multiplier
            
            # Update skill level (1-10 scale)
            skill_level = min(1 + (months_experience * 2), 10)
            
            # Calculate monthly income
            monthly_income = current_rate * hours_per_week * 4  # 4 weeks per month
            cumulative_income += monthly_income
            
            # Stress level depends on hours
            if hours_per_week <= 5:
                stress = 2
            elif hours_per_week <= 10:
                stress = 4
            elif hours_per_week <= 15:
                stress = 6
            else:
                stress = 8
            
            results.append(SideHustleResult(
                month=month,
                hours_per_week=hours_per_week,
                hourly_rate=current_rate,
                monthly_income=monthly_income,
                cumulative_income=cumulative_income,
                skill_level=int(skill_level),
                stress_level=stress
            ))
        
        return results
    
    def compare_scenarios(
        self,
        hours_per_week: float,
        months: int = 12
    ) -> Dict[str, List[SideHustleResult]]:
        """Compare all side hustle types"""
        return {
            hustle.name: self.simulate_side_hustle(hustle, hours_per_week, months)
            for hustle in SideHustleType
        }
    
    def calculate_impact(
        self,
        side_hustle_income: float,
        main_income: float,
        savings_rate: float = 0.50  # Save 50% of side hustle
    ) -> Dict:
        """
        Calculate impact on financial goals
        
        Args:
            side_hustle_income: Monthly side income
            main_income: Monthly main job income
            savings_rate: Percentage of side income saved
        
        Returns:
            Impact analysis
        """
        # Side hustle income saved
        monthly_savings = side_hustle_income * savings_rate
        annual_savings = monthly_savings * 12
        
        # Example goals
        emergency_fund_goal = main_income * 6
        down_payment_goal = 60000  # $60k down payment
        
        # Time to reach goals
        months_to_emergency_fund = emergency_fund_goal / monthly_savings
        months_to_down_payment = down_payment_goal / monthly_savings
        
        return {
            "side_income_monthly": side_hustle_income,
            "saved_monthly": monthly_savings,
            "saved_annually": annual_savings,
            "time_to_emergency_fund": {
                "months": months_to_emergency_fund,
                "years": months_to_emergency_fund / 12
            },
            "time_to_down_payment": {
                "months": months_to_down_payment,
                "years": months_to_down_payment / 12
            },
            "income_boost_percentage": (side_hustle_income / main_income) * 100,
            "lesson": f"A ${side_hustle_income:,.0f}/month side hustle accelerates your goals! Emergency fund in {months_to_emergency_fund:.1f} months, down payment in {months_to_down_payment:.1f} months."
        }
    
    def generate_hustle_ideas(self, skills: List[str]) -> Dict:
        """Generate personalized side hustle ideas"""
        ideas = {
            "freelance": [],
            "gigs": [],
            "passive": [],
            "business": []
        }
        
        # Skill-based suggestions
        skill_map = {
            "writing": {"type": "freelance", "idea": "Content writing or copywriting", "rate": "$30-100/hr"},
            "coding": {"type": "freelance", "idea": "Web development or app building", "rate": "$50-150/hr"},
            "design": {"type": "freelance", "idea": "Graphic design or UI/UX", "rate": "$40-120/hr"},
            "teaching": {"type": "freelance", "idea": "Online tutoring or courses", "rate": "$25-75/hr"},
            "marketing": {"type": "freelance", "idea": "Social media management", "rate": "$30-100/hr"},
            "driving": {"type": "gigs", "idea": "Rideshare or delivery", "rate": "$15-25/hr"},
            "handyman": {"type": "gigs", "idea": "TaskRabbit or home repairs", "rate": "$30-60/hr"},
            "photography": {"type": "business", "idea": "Event photography", "rate": "$50-200/hr"},
        }
        
        for skill in skills:
            if skill.lower() in skill_map:
                idea = skill_map[skill.lower()]
                ideas[idea["type"]].append(idea)
        
        # General ideas always available
        ideas["passive"].append({
            "idea": "Create digital products (templates, ebooks)",
            "rate": "Variable - $100-1000/month potential"
        })
        ideas["gigs"].append({
            "idea": "Pet sitting or dog walking",
            "rate": "$20-40/hr"
        })
        
        return ideas
