"""
Coffee Shop Effect Simulation Service
Shows how small daily expenses compound into big money
"""

from dataclasses import dataclass
from typing import List, Dict
import math


@dataclass
class DailyExpense:
    """Daily expense item"""
    name: str
    cost_per_day: float
    days_per_week: int
    category: str


@dataclass
class CompoundResult:
    """Compound calculation result for a specific year"""
    year: int
    spent_total: float
    invested_total: float
    opportunity_cost: float


@dataclass
class OpportunityCostExample:
    """Example of what could be bought with the money"""
    item: str
    cost: float
    years_saved: int
    description: str


@dataclass
class CoffeeShopAnalysis:
    """Complete coffee shop effect analysis"""
    daily_cost: float
    days_per_week: int
    annual_cost: float
    five_year_cost: float
    ten_year_cost: float
    thirty_year_cost: float
    compound_results: List[CompoundResult]
    opportunity_examples: List[OpportunityCostExample]
    total_opportunity_cost: float
    recommendation: str


class CoffeeShopSimulator:
    """
    Simulates the coffee shop effect - how small daily expenses compound
    """
    
    # Investment return assumption (S&P 500 historical average)
    ANNUAL_RETURN_RATE = 0.08
    
    # Common opportunity cost examples
    OPPORTUNITY_EXAMPLES = [
        {"item": "New iPhone", "cost": 1000, "description": "Latest flagship smartphone"},
        {"item": "Weekend Getaway", "cost": 500, "description": "2-night trip for two"},
        {"item": "Nice Dinner", "cost": 150, "description": "Fancy restaurant for two"},
        {"item": "Gym Membership", "cost": 600, "description": "Annual gym membership"},
        {"item": "Streaming Services", "cost": 180, "description": "Netflix, Spotify, etc. for a year"},
        {"item": "New Laptop", "cost": 1500, "description": "Mid-range laptop"},
        {"item": "Used Car Down Payment", "cost": 5000, "description": "20% down on $25,000 car"},
        {"item": "Emergency Fund", "cost": 3000, "description": "3 months of basic expenses"},
        {"item": "Professional Course", "cost": 500, "description": "Online certification or course"},
        {"item": "Vacation", "cost": 2500, "description": "Week-long vacation abroad"},
    ]
    
    def __init__(self):
        """Initialize simulator"""
        pass
    
    def calculate(
        self,
        daily_cost: float,
        days_per_week: int = 5,
        years: int = 30
    ) -> CoffeeShopAnalysis:
        """
        Calculate the coffee shop effect
        
        Args:
            daily_cost: Cost per day (e.g., $5.50 for coffee)
            days_per_week: How many days per week (default 5 - weekdays)
            years: Years to project (default 30)
        
        Returns:
            Complete analysis with compound results
        """
        # Calculate annual cost
        weeks_per_year = 52
        annual_cost = daily_cost * days_per_week * weeks_per_year
        
        # Calculate milestone costs
        five_year_cost = annual_cost * 5
        ten_year_cost = annual_cost * 10
        thirty_year_cost = annual_cost * 30
        
        # Calculate compound growth if invested instead
        compound_results = self._calculate_compound_growth(
            annual_cost,
            years
        )
        
        # Generate opportunity cost examples
        total_saved = compound_results[-1].invested_total if compound_results else thirty_year_cost
        opportunity_examples = self._generate_opportunity_examples(total_saved)
        
        # Calculate total opportunity cost
        total_opportunity_cost = compound_results[-1].opportunity_cost if compound_results else 0
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            daily_cost,
            annual_cost,
            total_opportunity_cost
        )
        
        return CoffeeShopAnalysis(
            daily_cost=daily_cost,
            days_per_week=days_per_week,
            annual_cost=annual_cost,
            five_year_cost=five_year_cost,
            ten_year_cost=ten_year_cost,
            thirty_year_cost=thirty_year_cost,
            compound_results=compound_results,
            opportunity_examples=opportunity_examples,
            total_opportunity_cost=total_opportunity_cost,
            recommendation=recommendation
        )
    
    def _calculate_compound_growth(
        self,
        annual_amount: float,
        years: int
    ) -> List[CompoundResult]:
        """Calculate compound growth if money was invested instead"""
        results = []
        spent_total = 0
        invested_total = 0
        
        for year in range(1, years + 1):
            # Total spent (no growth)
            spent_total += annual_amount
            
            # If invested, it grows
            # Add this year's contribution
            invested_total += annual_amount
            
            # Apply growth to the total balance
            invested_total *= (1 + self.ANNUAL_RETURN_RATE)
            
            # Calculate opportunity cost
            opportunity_cost = invested_total - spent_total
            
            results.append(CompoundResult(
                year=year,
                spent_total=spent_total,
                invested_total=invested_total,
                opportunity_cost=opportunity_cost
            ))
        
        return results
    
    def _generate_opportunity_examples(
        self,
        total_saved: float
    ) -> List[OpportunityCostExample]:
        """Generate examples of what could be bought with the money"""
        examples = []
        
        for item_data in self.OPPORTUNITY_EXAMPLES:
            if item_data["cost"] <= total_saved:
                # Calculate how many years of saving needed
                # Rough calculation: how many years until invested amount >= item cost
                years_needed = self._calculate_years_to_reach(item_data["cost"])
                
                examples.append(OpportunityCostExample(
                    item=item_data["item"],
                    cost=item_data["cost"],
                    years_saved=years_needed,
                    description=item_data["description"]
                ))
        
        return examples
    
    def _calculate_years_to_reach(self, target: float) -> int:
        """Calculate years needed to reach target amount"""
        # Use default coffee shop example: $5.50/day, 5 days/week
        annual_contribution = 5.50 * 5 * 52  # ~$1,430/year
        
        balance = 0
        years = 0
        
        while balance < target and years < 30:
            years += 1
            balance += annual_contribution
            balance *= (1 + self.ANNUAL_RETURN_RATE)
        
        return years
    
    def _generate_recommendation(
        self,
        daily_cost: float,
        annual_cost: float,
        opportunity_cost: float
    ) -> str:
        """Generate personalized recommendation"""
        if daily_cost < 3:
            return (
                f"Your daily expense of ${daily_cost:.2f} is relatively modest. "
                f"However, over 30 years, that's still ${opportunity_cost:,.0f} in potential investment growth! "
                f"Consider cutting back 2-3 days per week to capture some of that growth."
            )
        elif daily_cost < 6:
            return (
                f"Your ${daily_cost:.2f} daily habit costs ${annual_cost:,.0f} per year. "
                f"If invested instead, you'd have ${opportunity_cost:,.0f} more in 30 years! "
                f"Try reducing to 3 days per week - that's ${opportunity_cost * 0.4:,.0f} saved!"
            )
        elif daily_cost < 10:
            return (
                f"At ${daily_cost:.2f} per day, you're spending ${annual_cost:,.0f} annually. "
                f"That's ${opportunity_cost:,.0f} in lost investment growth over 30 years! "
                f"Even cutting to weekends only could save you ${opportunity_cost * 0.6:,.0f}."
            )
        else:
            return (
                f"${daily_cost:.2f} per day is a significant expense - ${annual_cost:,.0f} per year! "
                f"Over 30 years, that's ${opportunity_cost:,.0f} in lost wealth. "
                f"Consider brewing at home most days and treating yourself 1-2 times per week. "
                f"You could save ${opportunity_cost * 0.8:,.0f}!"
            )
    
    def compare_scenarios(
        self,
        scenarios: List[Dict]
    ) -> Dict:
        """
        Compare multiple expense scenarios
        
        Args:
            scenarios: List of scenarios with 'name', 'daily_cost', 'days_per_week'
        
        Returns:
            Comparison results
        """
        results = {}
        
        for scenario in scenarios:
            analysis = self.calculate(
                daily_cost=scenario["daily_cost"],
                days_per_week=scenario.get("days_per_week", 5),
                years=30
            )
            
            results[scenario["name"]] = {
                "annual_cost": analysis.annual_cost,
                "thirty_year_invested": analysis.compound_results[-1].invested_total,
                "opportunity_cost": analysis.total_opportunity_cost
            }
        
        return results
    
    def calculate_breakeven(
        self,
        home_cost_per_day: float,
        shop_cost_per_day: float,
        days_per_week: int = 5
    ) -> Dict:
        """
        Calculate breakeven analysis between making at home vs buying
        
        Args:
            home_cost_per_day: Cost to make at home
            shop_cost_per_day: Cost to buy at shop
            days_per_week: Days per week
        
        Returns:
            Breakeven analysis
        """
        annual_savings = (shop_cost_per_day - home_cost_per_day) * days_per_week * 52
        
        # Calculate investment growth of the savings
        thirty_year_home = self.calculate(home_cost_per_day, days_per_week, 30)
        thirty_year_shop = self.calculate(shop_cost_per_day, days_per_week, 30)
        
        savings_invested = thirty_year_shop.compound_results[-1].invested_total - thirty_year_home.compound_results[-1].invested_total
        
        return {
            "daily_savings": shop_cost_per_day - home_cost_per_day,
            "annual_savings": annual_savings,
            "thirty_year_savings": savings_invested,
            "recommendation": f"Making it at home saves ${shop_cost_per_day - home_cost_per_day:.2f} per day. Over 30 years, that's ${savings_invested:,.0f} in extra wealth!"
        }


def demo():
    """Demo the coffee shop simulator"""
    simulator = CoffeeShopSimulator()
    
    # Calculate coffee shop effect
    print("=== COFFEE SHOP EFFECT DEMO ===\n")
    
    analysis = simulator.calculate(
        daily_cost=5.50,
        days_per_week=5,
        years=30
    )
    
    print(f"Daily Cost: ${analysis.daily_cost:.2f}")
    print(f"Days per Week: {analysis.days_per_week}")
    print(f"Annual Cost: ${analysis.annual_cost:,.2f}")
    print(f"5-Year Cost: ${analysis.five_year_cost:,.2f}")
    print(f"10-Year Cost: ${analysis.ten_year_cost:,.2f}")
    print(f"30-Year Cost: ${analysis.thirty_year_cost:,.2f}")
    print()
    
    print("If Invested Instead (8% annual return):")
    milestones = [5, 10, 20, 30]
    for year in milestones:
        result = analysis.compound_results[year - 1]
        print(f"  Year {year}: ${result.invested_total:,.2f} (vs ${result.spent_total:,.2f} spent)")
    print()
    
    print(f"Total Opportunity Cost: ${analysis.total_opportunity_cost:,.2f}")
    print()
    
    print("What You Could Buy Instead:")
    for example in analysis.opportunity_examples[:5]:
        print(f"  • {example.item} (${example.cost:,.0f}) - achievable in {example.years_saved} years")
    print()
    
    print("Recommendation:")
    print(f"  {analysis.recommendation}")
    print()
    
    # Compare scenarios
    print("=== SCENARIO COMPARISON ===\n")
    
    scenarios = [
        {"name": "Coffee Shop Daily", "daily_cost": 5.50, "days_per_week": 5},
        {"name": "Coffee Shop 3x/week", "daily_cost": 5.50, "days_per_week": 3},
        {"name": "Home Brew", "daily_cost": 0.75, "days_per_week": 5},
    ]
    
    comparison = simulator.compare_scenarios(scenarios)
    
    for name, data in comparison.items():
        print(f"{name}:")
        print(f"  Annual: ${data['annual_cost']:,.2f}")
        print(f"  30-Year Invested: ${data['thirty_year_invested']:,.2f}")
        print(f"  Opportunity Cost: ${data['opportunity_cost']:,.2f}")
    print()


if __name__ == "__main__":
    demo()
