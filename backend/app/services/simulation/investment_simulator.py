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
    INDEX_FUND = "index_fund"           # Nifty 50 Index passive
    STOCK_PICKER = "stock_picker"       # Active NSE stock picking
    MUTUAL_FUND = "mutual_fund"         # Active fund manager (1.5% expense ratio)
    DIVERSIFIED = "diversified"         # Mix of index + stocks
    CONSERVATIVE = "conservative"       # High dividend, low volatility
    AGGRESSIVE = "aggressive"           # Growth stocks, high beta


class FundType(str, Enum):
    """Indian mutual fund categories"""
    NIFTY_50_INDEX = "nifty_50_index"   # Passive index tracking (0.1-0.3% fee)
    MIDCAP_INDEX = "midcap_index"       # Midcap 150 tracking (0.2-0.4% fee)
    LIQUID_FUND = "liquid_fund"         # Short-term, low risk (1-2% returns)
    BALANCED_FUND = "balanced_fund"     # 60/40 equity/debt (1.2% fee)
    AGGRESSIVE_FUND = "aggressive_fund" # 100% equity (1.5% fee)
    TAX_SAVER_FUND = "tax_saver_fund"   # ELSS (1-1.5% fee, 80C benefit)


class MarketCondition(Enum):
    """Market condition types - Indian context"""
    BULL = "bull"           # Strong upward trend (Sensex +8-12%)
    BEAR = "bear"           # Strong downward trend (Sensex -8-12%)
    VOLATILE = "volatile"   # High volatility (±3-5% daily swings)
    STABLE = "stable"       # Low volatility (±1-2% daily moves)
    CORRECTION = "correction"  # Market correction (-5% to -15%)
    RECOVERY = "recovery"   # Post-crisis recovery (+3-8%)


# Indian stock market indices and contexts
NIFTY_50_STOCKS = [
    {"symbol": "INFY", "name": "Infosys", "sector": "IT", "base_return": 0.12, "volatility": 0.06},
    {"symbol": "TCS", "name": "Tata Consultancy", "sector": "IT", "base_return": 0.11, "volatility": 0.05},
    {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy", "base_return": 0.10, "volatility": 0.07},
    {"symbol": "HDFC", "name": "HDFC Bank", "sector": "Banking", "base_return": 0.14, "volatility": 0.08},
    {"symbol": "ICICI", "name": "ICICI Bank", "sector": "Banking", "base_return": 0.13, "volatility": 0.09},
    {"symbol": "SBIN", "name": "State Bank", "sector": "Banking", "base_return": 0.12, "volatility": 0.10},
    {"symbol": "ITC", "name": "ITC Limited", "sector": "FMCG", "base_return": 0.08, "volatility": 0.04},
    {"symbol": "LT", "name": "L&T", "sector": "Infrastructure", "base_return": 0.11, "volatility": 0.08},
    {"symbol": "MARUTI", "name": "Maruti Suzuki", "sector": "Auto", "base_return": 0.10, "volatility": 0.12},
    {"symbol": "SUNPHARMA", "name": "Sun Pharma", "sector": "Pharma", "base_return": 0.09, "volatility": 0.11},
]


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
    Simulation: Nifty 50 Index vs Active Stock Picker
    Indian context: Shows why passive index fund investing beats active management

    Key Indian Context:
    - Nifty 50 index: 10.5% CAGR historical average
    - Active fund manager fees: 1-1.5% (reduces returns significantly)
    - TDS on dividends: 10-15% for residents, withholding tax
    - SEBI regulations: Limits on portfolio concentration
    - Tax-loss harvesting: Capital gains tax treatment (20% LTCG after 1 year, indexation)
    """

    # Nifty 50 historical performance
    NIFTY_50_BASE_RETURN = 0.105 / 12  # 10.5% annual (~0.875% monthly)
    NIFTY_50_VOLATILITY = 0.04  # Monthly standard deviation
    NIFTY_50_EXPENSE_RATIO = 0.001  # 0.1% annual (very low for index funds)

    # Active management returns (SEBI data: 80% of fund managers underperform)
    ACTIVE_MANAGER_BASE_RETURN = 0.095 / 12  # 9.5% annual (underperformance)
    ACTIVE_MANAGER_EXPENSE_RATIO = 0.015  # 1.5% annual (typical MF fee)

    # Dividend TDS treatment
    DIVIDEND_TDS_RATE = 0.10  # 10% TDS on dividends (can be higher for non-residents)

    # Indian fund expense ratios by type
    FUND_EXPENSE_RATIOS = {
        FundType.NIFTY_50_INDEX: 0.001,        # ₹100Cr+ funds = 0.03-0.15%
        FundType.MIDCAP_INDEX: 0.002,         # Midcap funds = 0.2-0.4%
        FundType.LIQUID_FUND: 0.004,          # Liquid funds = 0.3-0.5%
        FundType.BALANCED_FUND: 0.010,        # 1.0% typical
        FundType.AGGRESSIVE_FUND: 0.015,      # 1.5% typical
        FundType.TAX_SAVER_FUND: 0.012,       # 1.2% with 80C benefit
    }

    def __init__(self, seed: int = None):
        """Initialize simulator with optional seed for reproducibility"""
        if seed:
            random.seed(seed)

    def simulate_race(
        self,
        initial_investment: float,
        monthly_contribution: float,
        months: int = 360,  # 30 years
        strategy: InvestmentStrategy = InvestmentStrategy.INDEX_FUND,
        fund_type: FundType = FundType.NIFTY_50_INDEX,
        show_dividend_tax: bool = True
    ) -> Dict[str, InvestmentResult]:
        """
        Simulate Nifty 50 Index vs Active Manager over time

        Args:
            initial_investment: Starting amount (₹)
            monthly_contribution: Monthly SIP amount (₹)
            months: Number of months to simulate (default 30 years)
            strategy: Investment strategy to compare
            fund_type: Type of Indian mutual fund
            show_dividend_tax: Whether to show dividend TDS impact

        Returns:
            Dictionary with results and SEBI-compliant analysis
        """
        # Generate market conditions for all months (Indian context)
        market_conditions = self._generate_market_conditions(months)

        # Simulate index fund (passive strategy - Nifty 50 tracking)
        index_result = self._simulate_index_fund(
            initial_investment,
            monthly_contribution,
            months,
            market_conditions,
            fund_type
        )

        # Simulate active manager (underperforms 80% of the time per SEBI)
        manager_result = self._simulate_active_manager(
            initial_investment,
            monthly_contribution,
            months,
            market_conditions,
            show_dividend_tax
        )

        return {
            "index_fund": index_result,
            "active_manager": manager_result,
            "comparison": self._compare_strategies(index_result, manager_result),
            "sebi_insight": self._generate_sebi_insight(index_result, manager_result)
        }

    def _simulate_index_fund(
        self,
        initial_investment: float,
        monthly_contribution: float,
        months: int,
        market_conditions: List[MarketCondition],
        fund_type: FundType
    ) -> InvestmentResult:
        """Simulate Nifty 50 index fund (low cost, predictable)"""
        expense_ratio = self.FUND_EXPENSE_RATIOS[fund_type]
        balance = initial_investment
        total_contributed = initial_investment
        monthly_returns = []
        total_fees = 0

        for month in range(1, months + 1):
            # Base Nifty 50 return for this market condition
            base_return = self._get_return_for_condition(market_conditions[month - 1], True)

            # Apply expense ratio
            monthly_fee = (balance * expense_ratio) / 12
            total_fees += monthly_fee

            # Calculate return
            return_amount = (balance * base_return) - monthly_fee
            balance += monthly_contribution + return_amount
            total_contributed += monthly_contribution

            monthly_returns.append(MonthlyReturn(
                month=month,
                strategy=InvestmentStrategy.INDEX_FUND,
                starting_balance=balance - monthly_contribution - return_amount,
                monthly_contribution=monthly_contribution,
                return_rate=base_return,
                return_amount=return_amount,
                ending_balance=balance,
                market_condition=market_conditions[month - 1],
                fees=monthly_fee,
                stress_level=3  # Index investing = low stress
            ))

        final_return = ((balance - total_contributed) / total_contributed) * 100 if total_contributed > 0 else 0

        return InvestmentResult(
            strategy=InvestmentStrategy.INDEX_FUND,
            initial_investment=initial_investment,
            monthly_contribution=monthly_contribution,
            total_months=months,
            total_contributed=total_contributed,
            final_balance=balance,
            total_return=balance - total_contributed,
            return_percentage=final_return,
            total_fees=total_fees,
            monthly_breakdown=monthly_returns,
            average_stress=3,
            best_month=max(monthly_returns, key=lambda x: x.return_amount, default=monthly_returns[0]),
            worst_month=min(monthly_returns, key=lambda x: x.return_amount, default=monthly_returns[0])
        )

    def _simulate_active_manager(
        self,
        initial_investment: float,
        monthly_contribution: float,
        months: int,
        market_conditions: List[MarketCondition],
        include_dividend_tax: bool = True
    ) -> InvestmentResult:
        """Simulate active fund manager (higher fees, underperformance)"""
        balance = initial_investment
        total_contributed = initial_investment
        monthly_returns = []
        total_fees = 0
        total_dividend_tax = 0

        for month in range(1, months + 1):
            # Active managers underperform (return slightly less than Nifty)
            base_return = self._get_return_for_condition(market_conditions[month - 1], False)

            # Apply expense ratio (1.5% typical)
            monthly_fee = (balance * self.ACTIVE_MANAGER_EXPENSE_RATIO) / 12
            total_fees += monthly_fee

            # TDS on dividends (if dividend payout month - 5% probability)
            dividend_tax = 0
            if include_dividend_tax and random.random() < 0.05:
                dividend_amount = balance * 0.015  # ~1.5% dividend per annum
                dividend_tax = dividend_amount * self.DIVIDEND_TDS_RATE
                total_dividend_tax += dividend_tax

            # Calculate return
            return_amount = (balance * base_return) - monthly_fee - dividend_tax
            balance += monthly_contribution + return_amount
            total_contributed += monthly_contribution

            monthly_returns.append(MonthlyReturn(
                month=month,
                strategy=InvestmentStrategy.MUTUAL_FUND,
                starting_balance=balance - monthly_contribution - return_amount,
                monthly_contribution=monthly_contribution,
                return_rate=base_return,
                return_amount=return_amount,
                ending_balance=balance,
                market_condition=market_conditions[month - 1],
                fees=monthly_fee + dividend_tax,
                stress_level=6  # Active investing = moderate stress
            ))

        final_return = ((balance - total_contributed) / total_contributed) * 100 if total_contributed > 0 else 0

        return InvestmentResult(
            strategy=InvestmentStrategy.MUTUAL_FUND,
            initial_investment=initial_investment,
            monthly_contribution=monthly_contribution,
            total_months=months,
            total_contributed=total_contributed,
            final_balance=balance,
            total_return=balance - total_contributed,
            return_percentage=final_return,
            total_fees=total_fees + total_dividend_tax,
            monthly_breakdown=monthly_returns,
            average_stress=6,
            best_month=max(monthly_returns, key=lambda x: x.return_amount, default=monthly_returns[0]),
            worst_month=min(monthly_returns, key=lambda x: x.return_amount, default=monthly_returns[0])
        )

    def _get_return_for_condition(self, condition: MarketCondition, is_index: bool) -> float:
        """Get monthly return based on market condition"""
        if is_index:
            base = self.NIFTY_50_BASE_RETURN
        else:
            base = self.ACTIVE_MANAGER_BASE_RETURN

        # Market condition impacts
        if condition == MarketCondition.BULL:
            return base * random.gauss(1.2, 0.1)
        elif condition == MarketCondition.BEAR:
            return base * random.gauss(0.3, 0.2)
        elif condition == MarketCondition.CORRECTION:
            return base * random.gauss(-0.15, 0.15)
        elif condition == MarketCondition.RECOVERY:
            return base * random.gauss(1.3, 0.15)
        elif condition == MarketCondition.VOLATILE:
            return base * random.gauss(1.0, 0.2)
        else:  # STABLE
            return base * random.gauss(1.0, 0.05)

    def _generate_sebi_insight(self, index_result: InvestmentResult, manager_result: InvestmentResult) -> Dict:
        """Generate SEBI-based insight about fund performance"""
        difference = index_result.final_balance - manager_result.final_balance
        difference_pct = (difference / manager_result.final_balance) * 100 if manager_result.final_balance > 0 else 0

        return {
            "key_finding": "SEBI research shows 80% of active fund managers underperform index funds",
            "index_fund_winner": index_result.final_balance > manager_result.final_balance,
            "wealth_difference": difference,
            "outperformance_pct": difference_pct,
            "message": f"Index fund build ₹{difference:,.0f} ({difference_pct:.1f}%) MORE wealth over {index_result.total_months} months",
            "recommendations": [
                "✅ Start with Nifty 50 index funds (lowest cost)",
                "✅ Add ELSS funds for tax benefits (Section 80C)",
                "✅ Use SIP for rupee-cost averaging",
                "❌ Avoid active fund managers with 1-1.5% fees",
                "❌ Don't chase past performance (SEBI disclaimer applies)",
            ]
        }

    def _generate_market_conditions(self, months: int) -> List[MarketCondition]:
        """Generate realistic Indian market conditions over time"""
        conditions = []

        # Markets trend - periods of bull/bear markets by historical patterns
        current_trend = random.choice([MarketCondition.BULL, MarketCondition.STABLE])
        trend_duration = random.randint(12, 60)  # 1-5 year trends typical

        for month in range(months):
            # Change trend occasionally
            if month > 0 and month % trend_duration == 0:
                # Weight towards bull (Indian markets trend positive long-term)
                current_trend = random.choices(
                    list(MarketCondition),
                    weights=[0.35, 0.15, 0.15, 0.25, 0.05, 0.05]  # Bull weighted
                )[0]
                trend_duration = random.randint(12, 60)

            conditions.append(current_trend)

        return conditions

    def _compare_strategies(self, index_result: InvestmentResult, manager_result: InvestmentResult) -> Dict:
        """Compare index fund vs active manager performance"""
        return {
            "index_fund_final": index_result.final_balance,
            "active_manager_final": manager_result.final_balance,
            "difference": index_result.final_balance - manager_result.final_balance,
            "index_outperformance_pct": ((index_result.final_balance - manager_result.final_balance) / manager_result.final_balance) * 100 if manager_result.final_balance > 0 else 0,
            "index_fees_total": index_result.total_fees,
            "manager_fees_total": manager_result.total_fees,
            "fee_difference": manager_result.total_fees - index_result.total_fees,
            "winner": "Index Fund" if index_result.final_balance > manager_result.final_balance else "Active Manager",
        }
    
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
