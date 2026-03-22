"""
AI Analysis Service - Uses Claude API to analyze financial profiles
"""
import json
import os
from typing import Dict, Any, List
import anthropic
import numpy as np
from enum import Enum


async def analyze_financial_profile(
    q1_goals: str,
    q2_life_stage: str,
    q3_knowledge: int,
    q4_risk_tolerance: str,
    q5_monthly_surplus: int,
) -> Dict[str, Any]:
    """
    Analyze user's financial profile using Claude API

    Returns a dict with:
    - money_personality: str (The Careful Builder, Ambitious Investor, Overwhelmed Earner, Smart Saver)
    - finance_iq_score: float (0-100)
    - learning_gaps: List[str] (3-5 priority topics)
    - recommended_first_sim: str (e.g., 'gullak')
    """

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment variables")

    client = anthropic.Anthropic(api_key=api_key)

    # Build the prompt
    system_prompt = """You are a financial education AI assistant helping analyze user profiles.
Based on the user's quiz responses, provide:
1. Money Personality Type (one of: "The Careful Builder", "The Ambitious Investor", "The Overwhelmed Earner", "The Smart Saver")
2. Finance IQ Score (0-100, based on their knowledge and risk tolerance)
3. Learning Gaps (3-5 priority topics they should learn, as an array)
4. Recommended First Simulation (one of: "gullak", "sip-chronicles", "karobaar", "compound-interest", "emergency-fund", "coffee-shop-effect", "credit-card-debt", "budget-builder", "car-payment", "paycheck-game")

Return ONLY valid JSON with these 4 keys: money_personality, finance_iq_score, learning_gaps, recommended_first_sim."""

    user_message = f"""Analyze this user's financial profile:
- Financial Goals: {q1_goals}
- Life Stage: {q2_life_stage}
- Financial Knowledge Level (0-100): {q3_knowledge}
- Risk Tolerance: {q4_risk_tolerance}
- Monthly Surplus: ₹{q5_monthly_surplus}

Respond with ONLY valid JSON (no markdown, no explanation)."""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        response_text = response.content[0].text.strip()

        # Parse the JSON response
        analysis_result = json.loads(response_text)

        # Validate response structure
        required_fields = [
            "money_personality",
            "finance_iq_score",
            "learning_gaps",
            "recommended_first_sim"
        ]

        for field in required_fields:
            if field not in analysis_result:
                raise ValueError(f"Missing required field in AI response: {field}")

        # Ensure finance_iq_score is a float
        analysis_result["finance_iq_score"] = float(analysis_result["finance_iq_score"])

        # Ensure learning_gaps is a list
        if not isinstance(analysis_result["learning_gaps"], list):
            analysis_result["learning_gaps"] = [analysis_result["learning_gaps"]]

        return analysis_result

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")


# Mapping of money personality types
PERSONALITY_DESCRIPTIONS = {
    "The Careful Builder": "Conservative approach, focus on stability and emergency funds",
    "The Ambitious Investor": "Growth-focused, willing to take calculated risks",
    "The Overwhelmed Earner": "High income but overwhelmed with financial decisions",
    "The Smart Saver": "Good savings habits, seeks optimization",
}

# Common learning gaps
LEARNING_TOPICS = [
    "Emergency Fund Fundamentals",
    "Investment Basics",
    "Debt Management",
    "Compound Interest",
    "Tax Optimization",
    "Insurance Planning",
    "Retirement Planning",
    "SIP Strategy",
    "Market Cycles",
    "Risk Assessment",
]

# Simulation recommendations by profile
SIMULATION_RECOMMENDATIONS = {
    "beginner": "gullak",
    "novice": "sip-chronicles",
    "intermediate": "karobaar",
    "advanced": "dalal-street",
}


class MarketType(str, Enum):
    """Market types for asset allocation"""
    INDIA = "india"
    US = "us"


# Asset class definitions for India market
INDIA_ASSET_CLASSES = {
    "Large Cap": {
        "name": "Large Cap (NIFTY 50)",
        "annual_return": 0.08,  # 8%
        "annual_volatility": 0.16,  # 16%
        "description": "Established companies with stable growth"
    },
    "Mid Cap": {
        "name": "Mid Cap (NIFTY MID)",
        "annual_return": 0.10,  # 10%
        "annual_volatility": 0.22,  # 22%
        "description": "Emerging companies with growth potential"
    },
    "Small Cap": {
        "name": "Small Cap",
        "annual_return": 0.12,  # 12%
        "annual_volatility": 0.28,  # 28%
        "description": "High growth potential, higher risk"
    },
    "Bonds": {
        "name": "Government Securities & Bonds",
        "annual_return": 0.06,  # 6%
        "annual_volatility": 0.05,  # 5%
        "description": "Low risk, steady returns"
    },
    "Gold": {
        "name": "Gold / Precious Metals",
        "annual_return": 0.05,  # 5%
        "annual_volatility": 0.12,  # 12%
        "description": "Hedge against inflation and currency risk"
    },
}

# Asset class definitions for US market
US_ASSET_CLASSES = {
    "Large Cap": {
        "name": "Large Cap (S&P 500)",
        "annual_return": 0.10,  # 10%
        "annual_volatility": 0.15,  # 15%
        "description": "Established companies (AAPL, MSFT, etc.)"
    },
    "Mid Cap": {
        "name": "Mid Cap",
        "annual_return": 0.09,  # 9%
        "annual_volatility": 0.18,  # 18%
        "description": "Mid-sized companies with growth"
    },
    "Tech": {
        "name": "Technology (NASDAQ)",
        "annual_return": 0.12,  # 12%
        "annual_volatility": 0.22,  # 22%
        "description": "Tech sector including FAANG stocks"
    },
    "Bonds": {
        "name": "US Treasury & Corporate Bonds",
        "annual_return": 0.05,  # 5%
        "annual_volatility": 0.06,  # 6%
        "description": "Low risk, stable income"
    },
    "Cash": {
        "name": "Money Market / Cash",
        "annual_return": 0.05,  # 5% (current rates)
        "annual_volatility": 0.00,  # 0%
        "description": "Highly liquid, no risk"
    },
}


def get_asset_classes_for_market(market: MarketType) -> Dict[str, Dict[str, Any]]:
    """Get asset class definitions for specified market"""
    if market == MarketType.INDIA:
        return INDIA_ASSET_CLASSES
    else:
        return US_ASSET_CLASSES


def run_monte_carlo_simulation(
    initial_investment: float,
    monthly_contribution: float,
    years: int,
    allocation: Dict[str, float],
    market: MarketType = MarketType.INDIA,
    num_simulations: int = 1000
) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation for given allocation

    Args:
        initial_investment: Starting amount in rupees/dollars
        monthly_contribution: Monthly SIP amount
        years: Number of years to simulate
        allocation: Dict with asset class names as keys and allocation % as values (should sum to 100)
        market: Market type (INDIA or US)
        num_simulations: Number of Monte Carlo runs

    Returns:
        Dict with simulation results including percentiles and statistics
    """
    asset_classes = get_asset_classes_for_market(market)

    # Validate allocation
    total_allocation = sum(allocation.values())
    if abs(total_allocation - 100) > 0.01:
        raise ValueError(f"Allocation must sum to 100%, got {total_allocation}%")

    # Simulation parameters
    months = years * 12
    daily_simulations = np.zeros((num_simulations, months + 1))

    for sim in range(num_simulations):
        portfolio_value = initial_investment
        daily_simulations[sim, 0] = portfolio_value

        for month in range(1, months + 1):
            # Add monthly contribution
            portfolio_value += monthly_contribution

            # Calculate returns for each asset class based on their allocation
            monthly_return = 0
            for asset_class, allocation_pct in allocation.items():
                if asset_class not in asset_classes:
                    continue

                asset_config = asset_classes[asset_class]
                annual_return = asset_config["annual_return"]
                annual_volatility = asset_config["annual_volatility"]

                # Convert annual to monthly
                monthly_volatility = annual_volatility / np.sqrt(12)
                monthly_expected_return = annual_return / 12

                # Random return for this month (normal distribution)
                random_return = np.random.normal(
                    monthly_expected_return,
                    monthly_volatility
                )

                # Add weighted return to portfolio
                monthly_return += (allocation_pct / 100) * random_return

            # Apply monthly return
            portfolio_value *= (1 + monthly_return)
            daily_simulations[sim, month] = max(portfolio_value, 0)

    # Calculate statistics
    final_values = daily_simulations[:, -1]

    results = {
        "all_simulations": daily_simulations.tolist(),
        "statistics": {
            "mean_final_value": float(np.mean(final_values)),
            "median_final_value": float(np.median(final_values)),
            "std_dev": float(np.std(final_values)),
            "min_value": float(np.min(final_values)),
            "max_value": float(np.max(final_values)),
        },
        "percentiles": {
            "p10": float(np.percentile(final_values, 10)),  # Pessimistic
            "p25": float(np.percentile(final_values, 25)),
            "p50": float(np.percentile(final_values, 50)),  # Median
            "p75": float(np.percentile(final_values, 75)),
            "p90": float(np.percentile(final_values, 90)),  # Optimistic
        },
        "probability_of_success": {
            "beats_inflation": float(
                np.sum(final_values > initial_investment * (1.06 ** years)) / num_simulations * 100
            ),
            "doubles_investment": float(
                np.sum(final_values > initial_investment * 2) / num_simulations * 100
            ),
        },
        "allocation": allocation,
        "asset_classes": {
            name: {
                "return": config["annual_return"],
                "volatility": config["annual_volatility"],
                "description": config["description"]
            }
            for name, config in asset_classes.items()
        }
    }

    return results
