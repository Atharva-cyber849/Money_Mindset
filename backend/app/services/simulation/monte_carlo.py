"""
Monte Carlo Simulation Engine for Financial Scenarios
Real-time "what-if" modeling with 10,000 iterations
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ScenarioType(str, Enum):
    SAVINGS = "savings"
    INVESTMENT = "investment"
    DEBT_PAYOFF = "debt_payoff"
    RETIREMENT = "retirement"
    EMERGENCY_FUND = "emergency_fund"


class AssetClass(str, Enum):
    """Indian asset classes with historical volatility"""
    NIFTY_50 = "nifty_50"              # Large cap equity (10.5% CAGR, 16% volatility)
    MIDCAP = "midcap"                  # Midcap 150 (13% CAGR, 22% volatility)
    GOLD = "gold"                      # Gold/Silver (5% CAGR, 12% volatility)
    BONDS = "bonds"                    # GOI securities (6.5% CAGR, 3% volatility)
    FD = "fd"                          # Fixed Deposits (6% CAGR, 0% volatility)
    REAL_ESTATE = "real_estate"        # Property (7% CAGR, 8% volatility)
    BALANCED = "balanced"              # 60/40 equity/debt (8.5% CAGR, 10% volatility)


# Indian asset class return and volatility parameters (historical 10-year avg)
ASSET_CLASS_PARAMS = {
    AssetClass.NIFTY_50: {"return": 0.105, "volatility": 0.16},      # High return, high risk
    AssetClass.MIDCAP: {"return": 0.13, "volatility": 0.22},         # Higher return, higher volatility
    AssetClass.GOLD: {"return": 0.05, "volatility": 0.12},           # Hedge asset
    AssetClass.BONDS: {"return": 0.065, "volatility": 0.03},         # Stable income
    AssetClass.FD: {"return": 0.06, "volatility": 0.0},              # Guaranteed, no risk
    AssetClass.REAL_ESTATE: {"return": 0.07, "volatility": 0.08},    # Capital appreciation
    AssetClass.BALANCED: {"return": 0.085, "volatility": 0.10},      # Moderate risk/return
}

# Regional crisis impact on returns (sudden market shocks)
CRISIS_SCENARIOS = {
    "demonetization": {"probability": 0.02, "impact": -0.15, "recovery_months": 6},
    "covid_2020": {"probability": 0.05, "impact": -0.35, "recovery_months": 12},
    "interest_rate_hike": {"probability": 0.15, "impact": -0.08, "recovery_months": 3},
    "rupee_crisis": {"probability": 0.08, "impact": -0.12, "recovery_months": 9},
}


@dataclass
class SimulationParams:
    """Parameters for simulation - Indian-specific defaults"""
    initial_amount: float
    monthly_contribution: float
    time_horizon_months: int
    annual_return: float = 0.085  # 8.5% (balanced portfolio average)
    volatility: float = 0.10  # 10% (balanced portfolio volatility)
    inflation_rate: float = 0.065  # 6.5% (Indian inflation avg)
    iterations: int = 10000

    # Indian-specific parameters
    asset_class: str = "balanced"  # Which asset class to simulate
    include_crisis_risk: bool = True  # Include tail risk (crises)
    tax_rate: float = 0.20  # 20% LTCG tax for growth



class MonteCarloEngine:
    """
    Monte Carlo simulation engine - Indian market context

    Includes:
    - Asset class-specific volatility (Nifty 50, Gold, FD, etc.)
    - Crisis scenarios (Demonetization, COVID, rupee crises)
    - Sequence-of-returns risk
    - Inflation erosion (Indian real returns)
    """

    def __init__(self, params: SimulationParams):
        self.params = params
        np.random.seed(42)  # For reproducibility in testing

        # Load asset class parameters if specified
        if params.asset_class in ASSET_CLASS_PARAMS:
            asset_params = ASSET_CLASS_PARAMS[params.asset_class]
            if params.annual_return == 0.085:  # Default value
                self.params.annual_return = asset_params["return"]
            if params.volatility == 0.10:  # Default value
                self.params.volatility = asset_params["volatility"]

    def run_simulation(self) -> Dict:
        """Run Monte Carlo simulation - Indian market context"""

        results = []
        crisis_count = 0

        for _ in range(self.params.iterations):
            trajectory, hit_crisis = self._simulate_single_path()
            if hit_crisis:
                crisis_count += 1
            results.append(trajectory[-1])  # Final value

        results = np.array(results)

        # Calculate real returns (inflation-adjusted)
        inflation_adjusted = results / ((1 + self.params.inflation_rate) ** (self.params.time_horizon_months / 12))

        return {
            "mean": float(np.mean(results)),
            "median": float(np.median(results)),
            "std_dev": float(np.std(results)),
            "percentile_10": float(np.percentile(results, 10)),
            "percentile_25": float(np.percentile(results, 25)),
            "percentile_50": float(np.percentile(results, 50)),
            "percentile_75": float(np.percentile(results, 75)),
            "percentile_90": float(np.percentile(results, 90)),
            "best_case": float(np.max(results)),
            "worst_case": float(np.min(results)),
            "probability_positive": float(np.sum(results > self.params.initial_amount) / len(results)),
            # Indian-specific metrics
            "real_return_mean": float(np.mean(inflation_adjusted)),
            "real_return_median": float(np.median(inflation_adjusted)),
            "crisis_probability": float(crisis_count / self.params.iterations),
            "asset_class": self.params.asset_class,
            "tax_impact_estimate": float(np.mean(results) * self.params.tax_rate),
        }

    def _simulate_single_path(self) -> Tuple[np.ndarray, bool]:
        """Simulate a single trajectory with Indian crisis risk"""
        balance = self.params.initial_amount
        trajectory = [balance]
        hit_crisis = False

        # Monthly return parameters
        monthly_return = self.params.annual_return / 12
        monthly_volatility = self.params.volatility / np.sqrt(12)

        for month in range(self.params.time_horizon_months):
            # Check for crisis event this month
            if self.params.include_crisis_risk and not hit_crisis:
                for crisis_name, crisis_params in CRISIS_SCENARIOS.items():
                    if np.random.random() < crisis_params["probability"] / 12:
                        # Crisis hit!
                        random_return = crisis_params["impact"]
                        hit_crisis = True
                        trajectory.append(max(0, balance * (1 + random_return) + self.params.monthly_contribution))
                        balance = trajectory[-1]
                        continue

            # Normal market return
            random_return = np.random.normal(monthly_return, monthly_volatility)

            # Update balance
            balance = balance * (1 + random_return) + self.params.monthly_contribution
            trajectory.append(max(0, balance))  # Can't go negative

        return np.array(trajectory), hit_crisis
    
    def get_sample_trajectories(self, num_samples: int = 100) -> List[List[float]]:
        """Get sample trajectories for visualization"""
        trajectories = []
        
        for _ in range(num_samples):
            trajectory = self._simulate_single_path()
            trajectories.append(trajectory.tolist())
        
        return trajectories


class SavingsSimulator:
    """Specialized simulator for savings goals"""
    
    @staticmethod
    def simple_savings(
        monthly_contribution: float,
        months: int,
        annual_interest_rate: float = 0.045  # 4.5% HYSA
    ) -> Dict:
        """Simple savings calculation (no volatility)"""
        
        monthly_rate = annual_interest_rate / 12
        trajectory = []
        balance = 0
        
        for month in range(months + 1):
            if month > 0:
                balance = balance * (1 + monthly_rate) + monthly_contribution
            trajectory.append(balance)
        
        total_contributed = monthly_contribution * months
        total_interest = balance - total_contributed
        
        return {
            "final_balance": balance,
            "total_contributed": total_contributed,
            "total_interest": total_interest,
            "trajectory": trajectory,
            "time_to_goal": months,
        }
    
    @staticmethod
    def calculate_time_to_goal(
        target_amount: float,
        monthly_contribution: float,
        annual_interest_rate: float = 0.045
    ) -> int:
        """Calculate months needed to reach goal"""
        
        if monthly_contribution <= 0:
            return -1  # Impossible
        
        monthly_rate = annual_interest_rate / 12
        balance = 0
        months = 0
        
        while balance < target_amount and months < 1000:  # Max 83 years
            balance = balance * (1 + monthly_rate) + monthly_contribution
            months += 1
        
        return months if balance >= target_amount else -1


class InvestmentSimulator:
    """Investment portfolio simulator"""
    
    @staticmethod
    def compound_growth(
        initial: float,
        monthly_contribution: float,
        years: int,
        annual_return: float
    ) -> Dict:
        """Calculate compound growth"""
        
        months = years * 12
        monthly_return = annual_return / 12
        
        balance = initial
        trajectory = [initial]
        
        for _ in range(months):
            balance = balance * (1 + monthly_return) + monthly_contribution
            trajectory.append(balance)
        
        total_contributed = initial + (monthly_contribution * months)
        total_earnings = balance - total_contributed
        
        return {
            "final_balance": balance,
            "total_contributed": total_contributed,
            "total_earnings": total_earnings,
            "roi_percentage": (total_earnings / total_contributed * 100) if total_contributed > 0 else 0,
            "trajectory": trajectory
        }
    
    @staticmethod
    def compare_scenarios(
        initial: float,
        monthly: float,
        years: int
    ) -> Dict:
        """Compare conservative vs aggressive strategies"""
        
        scenarios = {
            "high_yield_savings": InvestmentSimulator.compound_growth(
                initial, monthly, years, 0.045
            ),
            "conservative_60_40": InvestmentSimulator.compound_growth(
                initial, monthly, years, 0.06
            ),
            "moderate_80_20": InvestmentSimulator.compound_growth(
                initial, monthly, years, 0.08
            ),
            "aggressive_100_stocks": InvestmentSimulator.compound_growth(
                initial, monthly, years, 0.10
            ),
        }
        
        return scenarios


class DebtPayoffSimulator:
    """Debt payoff strategy simulator"""
    
    @staticmethod
    def avalanche_vs_snowball(
        debts: List[Dict],  # [{"name": str, "balance": float, "apr": float, "minimum": float}]
        extra_payment: float
    ) -> Dict:
        """Compare avalanche (highest interest) vs snowball (smallest balance)"""
        
        # Avalanche: Sort by APR (highest first)
        avalanche_result = DebtPayoffSimulator._simulate_payoff(
            sorted(debts, key=lambda x: x["apr"], reverse=True),
            extra_payment
        )
        
        # Snowball: Sort by balance (lowest first)
        snowball_result = DebtPayoffSimulator._simulate_payoff(
            sorted(debts, key=lambda x: x["balance"]),
            extra_payment
        )
        
        return {
            "avalanche": avalanche_result,
            "snowball": snowball_result,
            "savings_with_avalanche": snowball_result["total_interest"] - avalanche_result["total_interest"],
            "recommendation": "avalanche" if avalanche_result["total_interest"] < snowball_result["total_interest"] else "snowball"
        }
    
    @staticmethod
    def _simulate_payoff(debts: List[Dict], extra_payment: float) -> Dict:
        """Simulate debt payoff"""
        
        debts = [d.copy() for d in debts]  # Don't modify original
        month = 0
        total_interest = 0
        payoff_timeline = []
        
        while any(d["balance"] > 0 for d in debts) and month < 1000:
            month += 1
            
            # Apply interest
            for debt in debts:
                if debt["balance"] > 0:
                    monthly_interest = debt["balance"] * (debt["apr"] / 12)
                    debt["balance"] += monthly_interest
                    total_interest += monthly_interest
            
            # Make minimum payments
            for debt in debts:
                if debt["balance"] > 0:
                    payment = min(debt["minimum"], debt["balance"])
                    debt["balance"] -= payment
            
            # Apply extra payment to first debt with balance
            remaining_extra = extra_payment
            for debt in debts:
                if debt["balance"] > 0 and remaining_extra > 0:
                    payment = min(remaining_extra, debt["balance"])
                    debt["balance"] -= payment
                    remaining_extra -= payment
                    
                    if debt["balance"] <= 0:
                        payoff_timeline.append({
                            "month": month,
                            "debt": debt["name"]
                        })
                    break
        
        return {
            "months_to_payoff": month,
            "total_interest": total_interest,
            "payoff_timeline": payoff_timeline
        }


class RetirementSimulator:
    """Retirement planning simulator"""
    
    @staticmethod
    def estimate_retirement_needs(
        current_age: int,
        retirement_age: int,
        current_income: float,
        replacement_rate: float = 0.80  # 80% of current income
    ) -> Dict:
        """Estimate retirement savings needed"""
        
        years_to_retirement = retirement_age - current_age
        years_in_retirement = 90 - retirement_age  # Assume living to 90
        
        # Annual retirement income needed
        retirement_income = current_income * replacement_rate
        
        # Total needed (simplified - doesn't account for social security, inflation adjustments)
        total_needed = retirement_income * years_in_retirement
        
        # Required monthly contribution
        # Assuming 7% return during accumulation
        required_monthly = RetirementSimulator._calculate_required_contribution(
            total_needed, years_to_retirement * 12, 0.07
        )
        
        return {
            "years_to_retirement": years_to_retirement,
            "annual_retirement_income": retirement_income,
            "total_needed": total_needed,
            "required_monthly_contribution": required_monthly,
            "current_age": current_age,
            "retirement_age": retirement_age
        }
    
    @staticmethod
    def _calculate_required_contribution(target: float, months: int, annual_return: float) -> float:
        """Calculate required monthly contribution to reach target"""
        
        monthly_rate = annual_return / 12
        
        if monthly_rate == 0:
            return target / months
        
        # Future value of annuity formula, solved for payment
        payment = target * monthly_rate / ((1 + monthly_rate) ** months - 1)
        
        return payment


# Factory function
def create_simulation(scenario_type: ScenarioType, params: Dict) -> Dict:
    """Create and run simulation based on type"""
    
    if scenario_type == ScenarioType.SAVINGS:
        return SavingsSimulator.simple_savings(
            monthly_contribution=params.get("monthly_contribution", 0),
            months=params.get("months", 12),
            annual_interest_rate=params.get("interest_rate", 0.045)
        )
    
    elif scenario_type == ScenarioType.INVESTMENT:
        return InvestmentSimulator.compare_scenarios(
            initial=params.get("initial", 0),
            monthly=params.get("monthly", 0),
            years=params.get("years", 30)
        )
    
    elif scenario_type == ScenarioType.DEBT_PAYOFF:
        return DebtPayoffSimulator.avalanche_vs_snowball(
            debts=params.get("debts", []),
            extra_payment=params.get("extra_payment", 0)
        )
    
    elif scenario_type == ScenarioType.RETIREMENT:
        return RetirementSimulator.estimate_retirement_needs(
            current_age=params.get("current_age", 30),
            retirement_age=params.get("retirement_age", 65),
            current_income=params.get("current_income", 50000)
        )
    
    else:
        # Default Monte Carlo
        sim_params = SimulationParams(**params)
        engine = MonteCarloEngine(sim_params)
        return engine.run_simulation()
