"""
Market Simulation Service
Historical data-based simulations to visualize risk vs return
Uses Monte Carlo simulation with historical market data patterns
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class AssetClass:
    """Represents an asset class with historical characteristics"""
    name: str
    mean_return: float  # Annual expected return
    std_dev: float  # Annual volatility (standard deviation)
    description: str


class MarketSimulator:
    """
    Simulate investment returns based on historical market data.
    Uses Monte Carlo simulation for probabilistic outcomes.
    """
    
    # Historical data-based asset classes (simplified annual figures)
    ASSET_CLASSES = {
        "aggressive_stocks": AssetClass(
            name="Aggressive Growth Stocks",
            mean_return=0.12,  # 12% annually
            std_dev=0.22,  # 22% volatility
            description="High-risk, high-reward stocks (tech, emerging markets)"
        ),
        "large_cap_stocks": AssetClass(
            name="Large Cap Stocks (S&P 500)",
            mean_return=0.10,  # 10% annually
            std_dev=0.16,  # 16% volatility
            description="Established US companies, moderate risk"
        ),
        "balanced": AssetClass(
            name="Balanced Portfolio (60/40)",
            mean_return=0.08,  # 8% annually
            std_dev=0.10,  # 10% volatility
            description="60% stocks, 40% bonds - moderate risk"
        ),
        "conservative": AssetClass(
            name="Conservative Portfolio",
            mean_return=0.06,  # 6% annually
            std_dev=0.07,  # 7% volatility
            description="Heavy bonds, low stocks - low risk"
        ),
        "bonds": AssetClass(
            name="Investment Grade Bonds",
            mean_return=0.04,  # 4% annually
            std_dev=0.05,  # 5% volatility
            description="Fixed income, very low risk"
        ),
        "savings": AssetClass(
            name="High-Yield Savings",
            mean_return=0.025,  # 2.5% annually
            std_dev=0.001,  # Virtually no volatility
            description="FDIC insured, no risk"
        )
    }
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize simulator with optional random seed for reproducibility"""
        if seed:
            np.random.seed(seed)
    
    def simulate_investment(
        self,
        initial_amount: float,
        monthly_contribution: float,
        years: int,
        asset_class: str,
        num_simulations: int = 1000
    ) -> Dict:
        """
        Run Monte Carlo simulation for investment growth.
        
        Args:
            initial_amount: Starting investment
            monthly_contribution: Monthly additional investment
            years: Time horizon in years
            asset_class: Key from ASSET_CLASSES
            num_simulations: Number of simulation runs
        
        Returns:
            Dict with simulation results and statistics
        """
        if asset_class not in self.ASSET_CLASSES:
            raise ValueError(f"Unknown asset class: {asset_class}")
        
        asset = self.ASSET_CLASSES[asset_class]
        months = years * 12
        
        # Run simulations
        final_values = []
        for _ in range(num_simulations):
            portfolio_value = initial_amount
            
            for month in range(months):
                # Add monthly contribution
                portfolio_value += monthly_contribution
                
                # Monthly return (convert annual to monthly)
                monthly_return = np.random.normal(
                    asset.mean_return / 12,
                    asset.std_dev / np.sqrt(12)
                )
                
                # Apply return
                portfolio_value *= (1 + monthly_return)
            
            final_values.append(portfolio_value)
        
        final_values = np.array(final_values)
        total_invested = initial_amount + (monthly_contribution * months)
        
        # Calculate statistics
        percentiles = {
            "p10": np.percentile(final_values, 10),
            "p25": np.percentile(final_values, 25),
            "p50": np.percentile(final_values, 50),  # Median
            "p75": np.percentile(final_values, 75),
            "p90": np.percentile(final_values, 90)
        }
        
        return {
            "asset_class": asset.name,
            "description": asset.description,
            "total_invested": round(total_invested, 2),
            "statistics": {
                "mean": round(np.mean(final_values), 2),
                "median": round(percentiles["p50"], 2),
                "std_dev": round(np.std(final_values), 2),
                "min": round(np.min(final_values), 2),
                "max": round(np.max(final_values), 2)
            },
            "percentiles": {k: round(v, 2) for k, v in percentiles.items()},
            "probability_analysis": {
                "prob_profit": round(
                    np.sum(final_values > total_invested) / num_simulations * 100,
                    1
                ),
                "prob_double": round(
                    np.sum(final_values > total_invested * 2) / num_simulations * 100,
                    1
                ),
                "prob_loss": round(
                    np.sum(final_values < total_invested) / num_simulations * 100,
                    1
                )
            },
            "returns": {
                "expected_gain": round(np.mean(final_values) - total_invested, 2),
                "expected_return_pct": round(
                    (np.mean(final_values) - total_invested) / total_invested * 100,
                    2
                )
            },
            "simulations_run": num_simulations,
            "time_horizon_years": years
        }
    
    def compare_asset_classes(
        self,
        initial_amount: float,
        monthly_contribution: float,
        years: int,
        asset_classes: Optional[List[str]] = None
    ) -> Dict:
        """
        Compare multiple asset classes side by side.
        
        Args:
            initial_amount: Starting investment
            monthly_contribution: Monthly additional investment
            years: Time horizon in years
            asset_classes: List of asset class keys (default: all)
        
        Returns:
            Dict with comparison data
        """
        if asset_classes is None:
            asset_classes = list(self.ASSET_CLASSES.keys())
        
        results = []
        for asset_class in asset_classes:
            sim_result = self.simulate_investment(
                initial_amount,
                monthly_contribution,
                years,
                asset_class,
                num_simulations=500  # Fewer for speed when comparing
            )
            
            results.append({
                "asset_class": asset_class,
                "name": sim_result["asset_class"],
                "median_value": sim_result["statistics"]["median"],
                "expected_gain": sim_result["returns"]["expected_gain"],
                "risk_score": sim_result["statistics"]["std_dev"],
                "prob_profit": sim_result["probability_analysis"]["prob_profit"],
                "prob_loss": sim_result["probability_analysis"]["prob_loss"]
            })
        
        # Sort by expected return
        results.sort(key=lambda x: x["expected_gain"], reverse=True)
        
        return {
            "comparison": results,
            "parameters": {
                "initial_amount": initial_amount,
                "monthly_contribution": monthly_contribution,
                "years": years
            },
            "recommendation": self._get_risk_recommendation(results)
        }
    
    def _get_risk_recommendation(self, results: List[Dict]) -> str:
        """Generate risk-based recommendation"""
        # Find balanced option
        balanced_result = next(
            (r for r in results if "balanced" in r["asset_class"].lower()),
            results[len(results) // 2]  # Middle option if no balanced
        )
        
        return (
            f"For most investors, a {balanced_result['name']} offers a good "
            f"balance of growth potential ({balanced_result['prob_profit']:.0f}% "
            f"chance of profit) and manageable risk. Choose more aggressive options "
            f"if you have a long time horizon and can weather volatility, or more "
            f"conservative options if you need stability and are close to your goal."
        )
    
    def risk_vs_return_analysis(
        self,
        initial_amount: float,
        years: int,
        target_amount: float
    ) -> Dict:
        """
        Analyze what asset allocation is needed to reach a target.
        
        Args:
            initial_amount: Starting investment
            years: Time horizon
            target_amount: Desired end value
        
        Returns:
            Analysis of required returns and recommended asset classes
        """
        # Calculate required annual return
        required_monthly = 0
        required_return = (target_amount / initial_amount) ** (1 / years) - 1
        
        # Find suitable asset classes
        suitable_assets = []
        for key, asset in self.ASSET_CLASSES.items():
            # Check if expected return meets target
            expected_value = initial_amount * ((1 + asset.mean_return) ** years)
            probability_success = self._calculate_success_probability(
                initial_amount,
                0,
                years,
                asset,
                target_amount
            )
            
            suitable_assets.append({
                "asset_class": key,
                "name": asset.name,
                "expected_return": round(asset.mean_return * 100, 1),
                "risk_level": self._risk_label(asset.std_dev),
                "expected_value": round(expected_value, 2),
                "meets_target": expected_value >= target_amount,
                "probability_success": round(probability_success * 100, 1)
            })
        
        # Sort by probability of success
        suitable_assets.sort(key=lambda x: x["probability_success"], reverse=True)
        
        return {
            "target": target_amount,
            "initial": initial_amount,
            "years": years,
            "required_return_pct": round(required_return * 100, 2),
            "feasibility": "achievable" if required_return <= 0.15 else "challenging",
            "asset_recommendations": suitable_assets,
            "advice": self._generate_target_advice(required_return, suitable_assets)
        }
    
    def _calculate_success_probability(
        self,
        initial: float,
        monthly: float,
        years: int,
        asset: AssetClass,
        target: float,
        simulations: int = 500
    ) -> float:
        """Calculate probability of reaching target"""
        months = years * 12
        successes = 0
        
        for _ in range(simulations):
            value = initial
            for _ in range(months):
                value += monthly
                monthly_return = np.random.normal(
                    asset.mean_return / 12,
                    asset.std_dev / np.sqrt(12)
                )
                value *= (1 + monthly_return)
            
            if value >= target:
                successes += 1
        
        return successes / simulations
    
    def _risk_label(self, std_dev: float) -> str:
        """Convert standard deviation to risk label"""
        if std_dev < 0.05:
            return "Very Low"
        elif std_dev < 0.10:
            return "Low"
        elif std_dev < 0.15:
            return "Moderate"
        elif std_dev < 0.20:
            return "High"
        else:
            return "Very High"
    
    def _generate_target_advice(
        self,
        required_return: float,
        assets: List[Dict]
    ) -> str:
        """Generate personalized advice for reaching target"""
        if required_return < 0.03:
            return "Your target is very achievable with low-risk investments. Consider a conservative portfolio."
        elif required_return < 0.08:
            return "A balanced portfolio should help you reach your target with moderate risk."
        elif required_return < 0.12:
            return "You'll need growth-focused investments. Consider a stock-heavy portfolio with 10+ year horizon."
        else:
            return "This target requires aggressive growth. Consider increasing contributions or extending timeline."
    
    def simulate_market_crash(
        self,
        initial_amount: float,
        monthly_contribution: float,
        years: int,
        asset_class: str,
        crash_year: int,
        crash_magnitude: float = -0.30
    ) -> Dict:
        """
        Simulate investment with a market crash event.
        
        Args:
            initial_amount: Starting investment
            monthly_contribution: Monthly additional investment
            years: Time horizon
            asset_class: Asset class to simulate
            crash_year: Year when crash occurs
            crash_magnitude: Crash size (e.g., -0.30 = 30% drop)
        
        Returns:
            Simulation with and without crash for comparison
        """
        # Normal simulation
        normal_result = self.simulate_investment(
            initial_amount,
            monthly_contribution,
            years,
            asset_class,
            num_simulations=500
        )
        
        # Crash simulation
        asset = self.ASSET_CLASSES[asset_class]
        months = years * 12
        crash_month = crash_year * 12
        
        final_values = []
        for _ in range(500):
            portfolio_value = initial_amount
            
            for month in range(months):
                portfolio_value += monthly_contribution
                
                # Apply crash at specific month
                if month == crash_month:
                    portfolio_value *= (1 + crash_magnitude)
                
                monthly_return = np.random.normal(
                    asset.mean_return / 12,
                    asset.std_dev / np.sqrt(12)
                )
                portfolio_value *= (1 + monthly_return)
            
            final_values.append(portfolio_value)
        
        crash_median = np.percentile(final_values, 50)
        recovery_pct = (crash_median / normal_result["statistics"]["median"]) * 100
        
        return {
            "normal_scenario": {
                "median_value": normal_result["statistics"]["median"],
                "expected_gain": normal_result["returns"]["expected_gain"]
            },
            "crash_scenario": {
                "crash_year": crash_year,
                "crash_magnitude_pct": crash_magnitude * 100,
                "median_value": round(crash_median, 2),
                "recovery_rate_pct": round(recovery_pct, 1)
            },
            "impact_analysis": {
                "value_difference": round(
                    normal_result["statistics"]["median"] - crash_median,
                    2
                ),
                "still_profitable": crash_median > (initial_amount + monthly_contribution * months),
                "years_to_recover": max(0, years - crash_year)
            },
            "lesson": (
                f"Even with a {abs(crash_magnitude)*100:.0f}% crash in year {crash_year}, "
                f"continuing to invest helps you recover to {recovery_pct:.0f}% of the "
                f"normal scenario. Time in the market beats timing the market!"
            )
        }
