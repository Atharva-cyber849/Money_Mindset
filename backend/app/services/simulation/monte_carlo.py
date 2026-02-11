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


@dataclass
class SimulationParams:
    """Parameters for simulation"""
    initial_amount: float
    monthly_contribution: float
    time_horizon_months: int
    annual_return: float = 0.07  # 7% default
    volatility: float = 0.15  # 15% volatility
    inflation_rate: float = 0.03  # 3% inflation
    iterations: int = 10000


class MonteCarloEngine:
    """Monte Carlo simulation engine"""
    
    def __init__(self, params: SimulationParams):
        self.params = params
        np.random.seed(42)  # For reproducibility in testing
    
    def run_simulation(self) -> Dict:
        """Run Monte Carlo simulation"""
        
        results = []
        
        for _ in range(self.params.iterations):
            trajectory = self._simulate_single_path()
            results.append(trajectory[-1])  # Final value
        
        results = np.array(results)
        
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
        }
    
    def _simulate_single_path(self) -> np.ndarray:
        """Simulate a single trajectory"""
        balance = self.params.initial_amount
        trajectory = [balance]
        
        # Monthly return parameters
        monthly_return = self.params.annual_return / 12
        monthly_volatility = self.params.volatility / np.sqrt(12)
        
        for month in range(self.params.time_horizon_months):
            # Random return for this month
            random_return = np.random.normal(monthly_return, monthly_volatility)
            
            # Update balance
            balance = balance * (1 + random_return) + self.params.monthly_contribution
            trajectory.append(max(0, balance))  # Can't go negative
        
        return np.array(trajectory)
    
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
