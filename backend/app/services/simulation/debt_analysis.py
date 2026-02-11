"""
Credit Card & Debt Classification Simulators
Combines Credit Card Trap and Good vs Bad Debt simulations
"""
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class DebtType(Enum):
    """Classification of debt types"""
    GOOD = "good"
    BAD = "bad"
    NEUTRAL = "neutral"


@dataclass
class Debt:
    """A debt obligation"""
    name: str
    principal: float
    apr: float
    purpose: str
    type: DebtType
    monthly_minimum: float = 0
    
    def __post_init__(self):
        if self.monthly_minimum == 0:
            # Estimate 2% of principal as minimum payment
            self.monthly_minimum = max(25, self.principal * 0.02)


class CreditCardTrapSimulator:
    """Simulates the impact of credit card interest and payment strategies"""
    
    def compare_payment_strategies(
        self,
        balance: float,
        apr: float = 0.24,
        minimum_payment_pct: float = 0.02
    ) -> Dict[str, Any]:
        """
        Compare minimum payment vs accelerated payoff
        
        Args:
            balance: Current credit card balance
            apr: Annual percentage rate (e.g., 0.24 for 24%)
            minimum_payment_pct: Minimum payment as % of balance
            
        Returns:
            Comparison of payment strategies
        """
        
        monthly_rate = apr / 12
        
        # Strategy 1: Minimum payments only
        min_payment = max(25, balance * minimum_payment_pct)
        min_result = self._calculate_payoff(balance, apr, min_payment)
        
        # Strategy 2: Double minimum
        double_result = self._calculate_payoff(balance, apr, min_payment * 2)
        
        # Strategy 3: Aggressive ($500/month if possible)
        aggressive_payment = min(500, balance * 0.15)
        aggressive_result = self._calculate_payoff(balance, apr, aggressive_payment)
        
        # Show "interest clock" - cost per day/hour
        daily_interest = (balance * apr) / 365
        hourly_interest = daily_interest / 24
        
        return {
            "balance": balance,
            "apr": apr * 100,
            "minimum_payment": min_payment,
            "strategies": {
                "minimum_payment": {
                    "monthly_payment": min_payment,
                    "months_to_payoff": min_result["months"],
                    "total_paid": min_result["total_paid"],
                    "total_interest": min_result["interest_paid"],
                    "years": min_result["months"] / 12
                },
                "double_minimum": {
                    "monthly_payment": min_payment * 2,
                    "months_to_payoff": double_result["months"],
                    "total_paid": double_result["total_paid"],
                    "total_interest": double_result["interest_paid"],
                    "years": double_result["months"] / 12
                },
                "aggressive": {
                    "monthly_payment": aggressive_payment,
                    "months_to_payoff": aggressive_result["months"],
                    "total_paid": aggressive_result["total_paid"],
                    "total_interest": aggressive_result["interest_paid"],
                    "years": aggressive_result["months"] / 12
                }
            },
            "interest_clock": {
                "per_day": daily_interest,
                "per_hour": hourly_interest,
                "per_month": balance * monthly_rate
            },
            "comparison": {
                "time_saved_double": min_result["months"] - double_result["months"],
                "money_saved_double": min_result["interest_paid"] - double_result["interest_paid"],
                "time_saved_aggressive": min_result["months"] - aggressive_result["months"],
                "money_saved_aggressive": min_result["interest_paid"] - aggressive_result["interest_paid"]
            },
            "recommendation": self._generate_recommendation(
                balance,
                min_result,
                double_result,
                aggressive_result
            )
        }
    
    def _calculate_payoff(
        self,
        balance: float,
        apr: float,
        monthly_payment: float,
        max_months: int = 600  # 50 years cap
    ) -> Dict[str, Any]:
        """Calculate payoff timeline"""
        
        if monthly_payment <= balance * (apr / 12):
            # Payment doesn't cover interest - will never pay off
            return {
                "months": 999,
                "total_paid": float('inf'),
                "interest_paid": float('inf'),
                "warning": "Payment doesn't cover monthly interest!"
            }
        
        monthly_rate = apr / 12
        current_balance = balance
        months = 0
        total_paid = 0
        
        while current_balance > 0.01 and months < max_months:
            interest = current_balance * monthly_rate
            principal = min(monthly_payment - interest, current_balance)
            
            current_balance -= principal
            total_paid += (principal + interest)
            months += 1
        
        interest_paid = total_paid - balance
        
        return {
            "months": months,
            "total_paid": total_paid,
            "interest_paid": interest_paid,
            "principal": balance
        }
    
    def _generate_recommendation(
        self,
        balance: float,
        min_result: Dict,
        double_result: Dict,
        aggressive_result: Dict
    ) -> str:
        """Generate payment recommendation"""
        
        interest_saved = min_result["interest_paid"] - aggressive_result["interest_paid"]
        time_saved = min_result["months"] - aggressive_result["months"]
        
        return (
            f"Aggressive payoff saves you ${interest_saved:,.0f} in interest and "
            f"{time_saved} months ({time_saved/12:.1f} years). "
            f"Even doubling the minimum saves ${min_result['interest_paid'] - double_result['interest_paid']:,.0f}. "
            f"Minimum payments keep you in debt for {min_result['months']/12:.1f} years!"
        )
    
    def calculate_credit_card_true_cost(
        self,
        purchase_amount: float,
        apr: float = 0.22,
        months_to_pay: int = 24
    ) -> Dict[str, Any]:
        """
        Show the true cost of a purchase when paying over time
        
        Args:
            purchase_amount: Original purchase amount
            apr: Credit card APR
            months_to_pay: How long to spread payments
            
        Returns:
            True cost analysis
        """
        
        monthly_rate = apr / 12
        
        # Calculate monthly payment using amortization formula
        if months_to_pay > 0:
            monthly_payment = purchase_amount * (
                monthly_rate * (1 + monthly_rate) ** months_to_pay
            ) / ((1 + monthly_rate) ** months_to_pay - 1)
        else:
            monthly_payment = purchase_amount
        
        total_paid = monthly_payment * months_to_pay
        interest_paid = total_paid - purchase_amount
        true_cost_multiplier = total_paid / purchase_amount
        
        return {
            "purchase_amount": purchase_amount,
            "apr": apr * 100,
            "months_to_pay": months_to_pay,
            "monthly_payment": monthly_payment,
            "total_paid": total_paid,
            "interest_paid": interest_paid,
            "interest_percentage": (interest_paid / purchase_amount) * 100,
            "true_cost_multiplier": true_cost_multiplier,
            "message": (
                f"That ${purchase_amount:.0f} purchase actually costs "
                f"${total_paid:.0f} when you pay over {months_to_pay} months "
                f"at {apr*100}% APR. You're paying {true_cost_multiplier:.1f}x "
                f"the original price!"
            )
        }


class DebtClassificationSimulator:
    """Classify and analyze different types of debt"""
    
    def __init__(self):
        self.debt_examples = {
            DebtType.GOOD: [
                {
                    "name": "Student loan for nursing degree",
                    "cost": 30000,
                    "apr": 0.06,
                    "purpose": "Education leading to $65K salary",
                    "annual_return": 0.15,  # Career advancement
                    "explanation": "Investment in career that increases earning potential"
                },
                {
                    "name": "Mortgage on home",
                    "cost": 250000,
                    "apr": 0.04,
                    "purpose": "Home that appreciates + builds equity",
                    "annual_return": 0.04,  # Avg home appreciation
                    "explanation": "Asset that typically appreciates over time"
                },
                {
                    "name": "Car loan for reliable commute",
                    "cost": 15000,
                    "apr": 0.07,
                    "purpose": "Transportation to keep job",
                    "annual_return": 0.10,  # Job retention value
                    "explanation": "Necessary for income generation"
                }
            ],
            DebtType.BAD: [
                {
                    "name": "Vacation on credit card",
                    "cost": 5000,
                    "apr": 0.22,
                    "purpose": "2-week vacation",
                    "annual_return": -0.22,  # Just loses money
                    "explanation": "No lasting value, high interest rate"
                },
                {
                    "name": "Furniture on credit",
                    "cost": 8000,
                    "apr": 0.19,
                    "purpose": "New living room set",
                    "annual_return": -0.15,  # Depreciates
                    "explanation": "Depreciating asset + high interest"
                },
                {
                    "name": "Payday loan",
                    "cost": 2000,
                    "apr": 4.00,  # 400% APR!
                    "purpose": "Emergency cash",
                    "annual_return": -4.00,
                    "explanation": "Predatory rates that trap borrowers"
                }
            ],
            DebtType.NEUTRAL: [
                {
                    "name": "Car loan for luxury vehicle",
                    "cost": 45000,
                    "apr": 0.08,
                    "purpose": "Want vs need",
                    "annual_return": -0.12,  # Depreciates
                    "explanation": "Can be good or bad depending on need vs want"
                }
            ]
        }
    
    def classify_debt(
        self,
        debt_name: str,
        amount: float,
        apr: float,
        purpose: str,
        increases_income: bool = False,
        appreciates: bool = False,
        necessary: bool = False
    ) -> Dict[str, Any]:
        """
        Classify a debt as good, bad, or neutral
        
        Args:
            debt_name: Name of the debt
            amount: Debt amount
            apr: Annual percentage rate
            purpose: What the debt is for
            increases_income: Does it increase earning potential?
            appreciates: Does the asset appreciate?
            necessary: Is it necessary for income/safety?
            
        Returns:
            Classification and analysis
        """
        
        # Classification logic
        score = 0
        reasons = []
        
        if increases_income:
            score += 3
            reasons.append("Increases earning potential")
        
        if appreciates:
            score += 3
            reasons.append("Asset appreciates over time")
        
        if necessary:
            score += 2
            reasons.append("Necessary for income/safety")
        
        if apr < 0.07:
            score += 1
            reasons.append("Low interest rate")
        elif apr > 0.15:
            score -= 2
            reasons.append("High interest rate")
        
        # Determine classification
        if score >= 4:
            classification = DebtType.GOOD
            color = "green"
            recommendation = "This is strategic borrowing that can build wealth."
        elif score <= 1:
            classification = DebtType.BAD
            color = "red"
            recommendation = "This debt destroys wealth. Avoid or pay off aggressively."
        else:
            classification = DebtType.NEUTRAL
            color = "yellow"
            recommendation = "This debt is situation-dependent. Evaluate carefully."
        
        return {
            "debt_name": debt_name,
            "amount": amount,
            "apr": apr * 100,
            "purpose": purpose,
            "classification": classification.value,
            "score": score,
            "reasons": reasons,
            "color": color,
            "recommendation": recommendation,
            "monthly_interest_cost": amount * (apr / 12),
            "annual_interest_cost": amount * apr
        }
    
    def simulate_debt_decisions(
        self,
        starting_age: int = 25,
        years_to_simulate: int = 5
    ) -> Dict[str, Any]:
        """
        Simulate 5-year outcomes of good vs bad debt decisions
        
        Args:
            starting_age: Starting age
            years_to_simulate: Number of years
            
        Returns:
            Net worth impact comparison
        """
        
        # Good debt path
        good_path = {
            "decisions": [],
            "net_worth_progression": [0]  # Start at 0
        }
        
        current_net_worth = 0
        
        # Year 1: Student loan
        current_net_worth -= 30000  # Take on debt
        good_path["decisions"].append({
            "year": 1,
            "decision": "Take $30K student loan for nursing degree (6% APR)",
            "net_worth_change": -30000,
            "net_worth": current_net_worth
        })
        
        # Years 2-5: Earning higher salary, paying down loan
        for year in range(2, years_to_simulate + 1):
            salary_gain = 15000  # Extra $15K/year from degree
            loan_payment = 6000  # Pay down loan
            
            current_net_worth += salary_gain - loan_payment - (30000 * 0.06)  # Minus interest
            
            good_path["net_worth_progression"].append(current_net_worth)
            good_path["decisions"].append({
                "year": year,
                "decision": f"Earn extra ${salary_gain:,} from nursing career",
                "net_worth_change": salary_gain - loan_payment,
                "net_worth": current_net_worth
            })
        
        # Bad debt path
        bad_path = {
            "decisions": [],
            "net_worth_progression": [0]
        }
        
        current_net_worth = 0
        
        # Year 1: Vacation on credit card
        current_net_worth -= 5000
        bad_path["decisions"].append({
            "year": 1,
            "decision": "Charge $5K vacation to credit card (22% APR)",
            "net_worth_change": -5000,
            "net_worth": current_net_worth
        })
        
        # Year 2: Furniture on credit
        current_net_worth -= 8000
        current_net_worth -= 5000 * 0.22  # Previous year's interest
        bad_path["decisions"].append({
            "year": 2,
            "decision": "Buy $8K furniture on credit (19% APR)",
            "net_worth_change": -8000 - (5000 * 0.22),
            "net_worth": current_net_worth
        })
        
        # Years 3-5: Struggling with debt
        for year in range(3, years_to_simulate + 1):
            interest = (5000 + 8000) * 0.20  # Avg interest
            current_net_worth -= interest
            
            bad_path["net_worth_progression"].append(current_net_worth)
            bad_path["decisions"].append({
                "year": year,
                "decision": f"Pay ${interest:,.0f} in credit card interest",
                "net_worth_change": -interest,
                "net_worth": current_net_worth
            })
        
        difference = good_path["net_worth_progression"][-1] - bad_path["net_worth_progression"][-1]
        
        return {
            "years_simulated": years_to_simulate,
            "good_debt_path": good_path,
            "bad_debt_path": bad_path,
            "final_comparison": {
                "good_debt_net_worth": good_path["net_worth_progression"][-1],
                "bad_debt_net_worth": bad_path["net_worth_progression"][-1],
                "difference": difference
            },
            "lesson": (
                f"After {years_to_simulate} years, good debt led to "
                f"${good_path['net_worth_progression'][-1]:,.0f} net worth, "
                f"while bad debt led to ${bad_path['net_worth_progression'][-1]:,.0f}. "
                f"That's a ${difference:,.0f} difference!"
            )
        }
    
    def get_debt_decision_framework(self) -> Dict[str, Any]:
        """Provide a framework for evaluating debt decisions"""
        
        return {
            "questions_to_ask": [
                {
                    "question": "Will this debt increase my earning potential?",
                    "good_answer": "Yes",
                    "examples": ["Education", "Professional certification", "Reliable transportation"]
                },
                {
                    "question": "Will the asset appreciate or hold value?",
                    "good_answer": "Yes",
                    "examples": ["Real estate in growing market", "Investment property"]
                },
                {
                    "question": "Is the interest rate below 7%?",
                    "good_answer": "Yes",
                    "examples": ["Mortgages", "Federal student loans", "Some auto loans"]
                },
                {
                    "question": "Is this purchase necessary for income/safety?",
                    "good_answer": "Yes",
                    "examples": ["Reliable car for work commute", "Tools for business"]
                },
                {
                    "question": "Could I save up and pay cash instead?",
                    "good_answer": "No",
                    "examples": ["Time-sensitive opportunities", "Home purchase"]
                }
            ],
            "red_flags": [
                "Interest rate above 15%",
                "Depreciating asset (electronics, furniture, vacation)",
                "Want vs need",
                "Could save up instead",
                "Payday loans or cash advances"
            ],
            "rules_of_thumb": {
                "good_debt": "Borrows against your future to invest in your earning potential or appreciating assets",
                "bad_debt": "Borrows against your future to fund current consumption of depreciating assets",
                "neutral": "Depends on circumstances - a car loan can be good (reliable commute) or bad (luxury want)"
            }
        }
