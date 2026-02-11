"""
Investment Simulation Services
Simulations: Index Fund vs Stock Picker Challenge, Risk vs Reward
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum
import random
from datetime import datetime


class InvestmentStrategy(Enum):
    """Investment strategy types"""
    INDEX_FUND = "index_fund"
    STOCK_PICKER = "stock_picker"
    DIVERSIFIED = "diversified"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"


class MarketCondition(Enum):
    """Market condition types"""
    BULL = "bull"  # Strong upward trend
    BEAR = "bear"  # Strong downward trend
    VOLATILE = "volatile"  # High volatility
    STABLE = "stable"  # Low volatility


@dataclass
class MonthlyReturn:
    """Monthly investment return data"""
    month: int
    strategy: InvestmentStrategy
    starting_balance: float
    monthly_contribution: float
    return_rate: float
    return_amount: float
    ending_balance: float
    market_condition: MarketCondition
    fees: float
    stress_level: int  # 1-10


@dataclass
class InvestmentResult:
    """Complete investment simulation result"""
    strategy: InvestmentStrategy
    initial_investment: float
    monthly_contribution: float
    total_months: int
    total_contributed: float
    final_balance: float
    total_return: float
    return_percentage: float
    total_fees: float
    monthly_breakdown: List[MonthlyReturn]
    average_stress: float
    best_month: MonthlyReturn
    worst_month: MonthlyReturn


@dataclass
class StockPerformance:
    """Individual stock performance"""
    ticker: str
    name: str
    initial_price: float
    final_price: float
    return_percentage: float
    volatility: float  # Standard deviation of returns


class IndexFundChallengeSimulator:
    """
    Simulation 10: Index Fund vs Stock Picker
    Shows the difficulty of beating index funds through stock picking
    """
    
    # Historical data suggests index funds return ~10% annually on average
    INDEX_FUND_BASE_RETURN = 0.10 / 12  # Monthly
    INDEX_FUND_VOLATILITY = 0.04  # Monthly standard deviation
    INDEX_FUND_FEE = 0.0003  # 0.03% annual (very low)
    
    # Stock pickers typically underperform due to fees and poor timing
    STOCK_PICKER_FEE = 0.01  # 1% annual (higher due to trading)
    
    # Sample stocks with different characteristics
    STOCK_UNIVERSE = [
        {"ticker": "TECH", "name": "Tech Giant", "base_return": 0.15, "volatility": 0.08},
        {"ticker": "STABL", "name": "Stable Corp", "base_return": 0.08, "volatility": 0.03},
        {"ticker": "GROW", "name": "Growth Co", "base_return": 0.20, "volatility": 0.12},
        {"ticker": "RISK", "name": "Risky Inc", "base_return": 0.25, "volatility": 0.20},
        {"ticker": "DIV", "name": "Dividend Co", "base_return": 0.06, "volatility": 0.02},
        {"ticker": "CYCL", "name": "Cyclical Corp", "base_return": 0.10, "volatility": 0.15},
    ]
    
    def __init__(self, seed: int = None):
        """Initialize simulator with optional seed for reproducibility"""
        if seed:
            random.seed(seed)
    
    def simulate_race(
        self,
        initial_investment: float,
        monthly_contribution: float,
        months: int = 60,
        stock_picker_skill: str = "average"  # poor, average, good
    ) -> Dict[str, InvestmentResult]:
        """
        Simulate index fund vs stock picker over time
        
        Args:
            initial_investment: Starting amount
            monthly_contribution: Monthly investment amount
            months: Number of months to simulate (default 5 years)
            stock_picker_skill: Skill level of stock picker
        
        Returns:
            Dictionary with 'index_fund' and 'stock_picker' results
        """
        # Generate market conditions for all months
        market_conditions = self._generate_market_conditions(months)
        
        # Simulate index fund (passive strategy)
        index_result = self._simulate_index_fund(
            initial_investment,
            monthly_contribution,
            months,
            market_conditions
        )
        
        # Simulate stock picker (active strategy)
        picker_result = self._simulate_stock_picker(
            initial_investment,
            monthly_contribution,
            months,
            market_conditions,
            stock_picker_skill
        )
        
        return {
            "index_fund": index_result,
            "stock_picker": picker_result,
            "comparison": self._compare_strategies(index_result, picker_result)
        }
    
    def _generate_market_conditions(self, months: int) -> List[MarketCondition]:
        """Generate realistic market conditions over time"""
        conditions = []
        
        # Markets trend - periods of bull/bear markets
        current_trend = random.choice([MarketCondition.BULL, MarketCondition.STABLE])
        trend_duration = random.randint(6, 24)
        
        for month in range(months):
            # Change trend occasionally
            if month > 0 and month % trend_duration == 0:
                current_trend = random.choice(list(MarketCondition))
                trend_duration = random.randint(6, 24)
            
            conditions.append(current_trend)
        
        return conditions
    
    def _simulate_index_fund(
        self,
        initial: float,
        monthly: float,
        months: int,
        market_conditions: List[MarketCondition]
    ) -> InvestmentResult:
        """Simulate passive index fund investment"""
        balance = initial
        monthly_breakdown = []
        total_fees = 0
        
        for month in range(1, months + 1):
            starting_balance = balance
            
            # Add monthly contribution
            balance += monthly
            
            # Calculate return based on market conditions
            condition = market_conditions[month - 1]
            return_rate = self._get_index_return(condition)
            return_amount = balance * return_rate
            
            # Apply fee (very low for index funds)
            monthly_fee = balance * (self.INDEX_FUND_FEE / 12)
            total_fees += monthly_fee
            
            balance = balance + return_amount - monthly_fee
            
            # Index fund investing is low stress (set and forget)
            stress_level = 2 if condition == MarketCondition.BEAR else 1
            
            monthly_data = MonthlyReturn(
                month=month,
                strategy=InvestmentStrategy.INDEX_FUND,
                starting_balance=starting_balance,
                monthly_contribution=monthly,
                return_rate=return_rate,
                return_amount=return_amount,
                ending_balance=balance,
                market_condition=condition,
                fees=monthly_fee,
                stress_level=stress_level
            )
            monthly_breakdown.append(monthly_data)
        
        total_contributed = initial + (monthly * months)
        total_return = balance - total_contributed
        
        return InvestmentResult(
            strategy=InvestmentStrategy.INDEX_FUND,
            initial_investment=initial,
            monthly_contribution=monthly,
            total_months=months,
            total_contributed=total_contributed,
            final_balance=balance,
            total_return=total_return,
            return_percentage=(total_return / total_contributed) * 100,
            total_fees=total_fees,
            monthly_breakdown=monthly_breakdown,
            average_stress=sum(m.stress_level for m in monthly_breakdown) / len(monthly_breakdown),
            best_month=max(monthly_breakdown, key=lambda m: m.return_rate),
            worst_month=min(monthly_breakdown, key=lambda m: m.return_rate)
        )
    
    def _simulate_stock_picker(
        self,
        initial: float,
        monthly: float,
        months: int,
        market_conditions: List[MarketCondition],
        skill_level: str
    ) -> InvestmentResult:
        """Simulate active stock picking strategy"""
        balance = initial
        monthly_breakdown = []
        total_fees = 0
        
        # Skill level affects ability to pick good stocks
        skill_multiplier = {
            "poor": 0.7,      # Worse than index
            "average": 0.9,   # Slightly worse than index
            "good": 1.0       # Matches index (very rare!)
        }[skill_level]
        
        for month in range(1, months + 1):
            starting_balance = balance
            
            # Add monthly contribution
            balance += monthly
            
            # Stock picker makes picks each month (higher stress)
            condition = market_conditions[month - 1]
            
            # Random stock selection (mimics picking behavior)
            picked_stock = random.choice(self.STOCK_UNIVERSE)
            
            # Calculate return with skill adjustment
            base_return = self._get_stock_return(
                picked_stock["base_return"] / 12,
                picked_stock["volatility"],
                condition
            )
            return_rate = base_return * skill_multiplier
            return_amount = balance * return_rate
            
            # Higher fees due to active trading
            monthly_fee = balance * (self.STOCK_PICKER_FEE / 12)
            total_fees += monthly_fee
            
            balance = balance + return_amount - monthly_fee
            
            # Stock picking is more stressful (watching prices daily)
            stress_level = self._calculate_picker_stress(condition, return_rate)
            
            monthly_data = MonthlyReturn(
                month=month,
                strategy=InvestmentStrategy.STOCK_PICKER,
                starting_balance=starting_balance,
                monthly_contribution=monthly,
                return_rate=return_rate,
                return_amount=return_amount,
                ending_balance=balance,
                market_condition=condition,
                fees=monthly_fee,
                stress_level=stress_level
            )
            monthly_breakdown.append(monthly_data)
        
        total_contributed = initial + (monthly * months)
        total_return = balance - total_contributed
        
        return InvestmentResult(
            strategy=InvestmentStrategy.STOCK_PICKER,
            initial_investment=initial,
            monthly_contribution=monthly,
            total_months=months,
            total_contributed=total_contributed,
            final_balance=balance,
            total_return=total_return,
            return_percentage=(total_return / total_contributed) * 100,
            total_fees=total_fees,
            monthly_breakdown=monthly_breakdown,
            average_stress=sum(m.stress_level for m in monthly_breakdown) / len(monthly_breakdown),
            best_month=max(monthly_breakdown, key=lambda m: m.return_rate),
            worst_month=min(monthly_breakdown, key=lambda m: m.return_rate)
        )
    
    def _get_index_return(self, condition: MarketCondition) -> float:
        """Calculate index fund return based on market conditions"""
        base = self.INDEX_FUND_BASE_RETURN
        volatility = self.INDEX_FUND_VOLATILITY
        
        # Adjust for market conditions
        if condition == MarketCondition.BULL:
            base *= 1.3
        elif condition == MarketCondition.BEAR:
            base *= -0.5
        elif condition == MarketCondition.VOLATILE:
            volatility *= 2
        
        # Add randomness
        return random.gauss(base, volatility)
    
    def _get_stock_return(
        self,
        base_return: float,
        volatility: float,
        condition: MarketCondition
    ) -> float:
        """Calculate individual stock return"""
        # Stocks are more volatile than index
        if condition == MarketCondition.BULL:
            base_return *= 1.5
        elif condition == MarketCondition.BEAR:
            base_return *= -0.8
        elif condition == MarketCondition.VOLATILE:
            volatility *= 3
        
        return random.gauss(base_return, volatility)
    
    def _calculate_picker_stress(self, condition: MarketCondition, return_rate: float) -> int:
        """Calculate stress level for stock picker"""
        base_stress = 5  # Stock picking is inherently stressful
        
        if condition == MarketCondition.BEAR:
            base_stress += 3
        elif condition == MarketCondition.VOLATILE:
            base_stress += 2
        
        if return_rate < -0.05:  # Big loss
            base_stress += 2
        
        return min(base_stress, 10)
    
    def _compare_strategies(
        self,
        index_result: InvestmentResult,
        picker_result: InvestmentResult
    ) -> Dict:
        """Compare the two strategies"""
        return {
            "winner": "index_fund" if index_result.final_balance > picker_result.final_balance else "stock_picker",
            "difference_amount": abs(index_result.final_balance - picker_result.final_balance),
            "difference_percentage": abs(index_result.return_percentage - picker_result.return_percentage),
            "index_advantage": {
                "lower_fees": index_result.total_fees < picker_result.total_fees,
                "lower_stress": index_result.average_stress < picker_result.average_stress,
                "better_return": index_result.final_balance > picker_result.final_balance,
                "fee_savings": picker_result.total_fees - index_result.total_fees
            },
            "lesson": self._generate_lesson(index_result, picker_result)
        }
    
    def _generate_lesson(
        self,
        index_result: InvestmentResult,
        picker_result: InvestmentResult
    ) -> str:
        """Generate educational lesson from comparison"""
        if index_result.final_balance > picker_result.final_balance:
            diff = index_result.final_balance - picker_result.final_balance
            return (
                f"The index fund won by ${diff:,.2f}! This demonstrates why "
                f"even professional fund managers struggle to beat index funds. "
                f"Lower fees (${index_result.total_fees:,.2f} vs ${picker_result.total_fees:,.2f}) "
                f"and consistent returns add up over time. Plus, you can sleep better "
                f"with stress level {index_result.average_stress:.1f} vs {picker_result.average_stress:.1f}."
            )
        else:
            return (
                "The stock picker got lucky this time, but this is rare! "
                "Most stock pickers underperform index funds over the long term. "
                "The question is: can you consistently pick winners AND time the market?"
            )


class RiskRewardSimulator:
    """
    Simulation 9: Risk vs Reward
    Demonstrates relationship between risk tolerance and investment returns
    """
    
    @dataclass
    class RiskProfile:
        """Investment risk profile"""
        name: str
        stocks_percentage: int  # 0-100
        bonds_percentage: int   # 0-100
        expected_return: float  # Annual
        volatility: float       # Standard deviation
        stress_factor: int      # 1-10
    
    RISK_PROFILES = {
        "conservative": RiskProfile(
            name="Conservative",
            stocks_percentage=20,
            bonds_percentage=80,
            expected_return=0.05,
            volatility=0.05,
            stress_factor=2
        ),
        "moderate": RiskProfile(
            name="Moderate",
            stocks_percentage=60,
            bonds_percentage=40,
            expected_return=0.08,
            volatility=0.10,
            stress_factor=5
        ),
        "aggressive": RiskProfile(
            name="Aggressive",
            stocks_percentage=90,
            bonds_percentage=10,
            expected_return=0.10,
            volatility=0.15,
            stress_factor=8
        ),
        "very_aggressive": RiskProfile(
            name="Very Aggressive",
            stocks_percentage=100,
            bonds_percentage=0,
            expected_return=0.12,
            volatility=0.20,
            stress_factor=10
        )
    }
    
    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
    
    def simulate_risk_profiles(
        self,
        initial: float,
        monthly: float,
        years: int = 30
    ) -> Dict[str, InvestmentResult]:
        """Simulate all risk profiles over time"""
        months = years * 12
        results = {}
        
        for profile_name, profile in self.RISK_PROFILES.items():
            results[profile_name] = self._simulate_profile(
                initial,
                monthly,
                months,
                profile
            )
        
        return results
    
    def _simulate_profile(
        self,
        initial: float,
        monthly: float,
        months: int,
        profile: RiskProfile
    ) -> InvestmentResult:
        """Simulate specific risk profile"""
        balance = initial
        monthly_breakdown = []
        
        for month in range(1, months + 1):
            starting_balance = balance
            balance += monthly
            
            # Calculate monthly return
            monthly_return = (profile.expected_return / 12)
            monthly_volatility = (profile.volatility / 12)
            
            # Add randomness
            actual_return = random.gauss(monthly_return, monthly_volatility)
            return_amount = balance * actual_return
            
            balance += return_amount
            
            # Determine stress based on volatility
            if actual_return < -0.05:
                stress = min(profile.stress_factor + 3, 10)
            elif actual_return < 0:
                stress = min(profile.stress_factor + 1, 10)
            else:
                stress = profile.stress_factor
            
            monthly_breakdown.append(MonthlyReturn(
                month=month,
                strategy=InvestmentStrategy.DIVERSIFIED,
                starting_balance=starting_balance,
                monthly_contribution=monthly,
                return_rate=actual_return,
                return_amount=return_amount,
                ending_balance=balance,
                market_condition=MarketCondition.STABLE,
                fees=0,
                stress_level=stress
            ))
        
        total_contributed = initial + (monthly * months)
        total_return = balance - total_contributed
        
        return InvestmentResult(
            strategy=InvestmentStrategy.DIVERSIFIED,
            initial_investment=initial,
            monthly_contribution=monthly,
            total_months=months,
            total_contributed=total_contributed,
            final_balance=balance,
            total_return=total_return,
            return_percentage=(total_return / total_contributed) * 100,
            total_fees=0,
            monthly_breakdown=monthly_breakdown,
            average_stress=sum(m.stress_level for m in monthly_breakdown) / len(monthly_breakdown),
            best_month=max(monthly_breakdown, key=lambda m: m.return_rate),
            worst_month=min(monthly_breakdown, key=lambda m: m.return_rate)
        )
    
    def recommend_profile(self, age: int, risk_tolerance: str, time_horizon: int) -> str:
        """Recommend risk profile based on user factors"""
        # Younger = more aggressive (more time to recover)
        # Longer time horizon = more aggressive
        # Higher risk tolerance = more aggressive
        
        score = 0
        
        # Age factor
        if age < 30:
            score += 3
        elif age < 40:
            score += 2
        elif age < 50:
            score += 1
        
        # Time horizon factor
        if time_horizon > 20:
            score += 3
        elif time_horizon > 10:
            score += 2
        elif time_horizon > 5:
            score += 1
        
        # Risk tolerance factor
        tolerance_scores = {"low": 0, "medium": 2, "high": 4}
        score += tolerance_scores.get(risk_tolerance, 2)
        
        # Map score to profile
        if score >= 8:
            return "very_aggressive"
        elif score >= 6:
            return "aggressive"
        elif score >= 3:
            return "moderate"
        else:
            return "conservative"
