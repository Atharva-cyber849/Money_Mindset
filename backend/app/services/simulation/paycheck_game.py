"""
Paycheck Game Simulation - Income Allocation Strategies
Demonstrates the impact of different payment sequencing strategies
"""
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class PaymentStrategy(Enum):
    """Different payment sequencing strategies"""
    SPEND_FIRST = "spend_first"  # Spend freely, pay bills, save what's left
    BILLS_FIRST = "bills_first"  # Pay bills first, spend freely, save what's left
    SAVE_FIRST = "save_first"   # Auto-save first, pay bills, spend remainder


@dataclass
class MonthlyExpenses:
    """Fixed monthly expenses"""
    rent: float
    utilities: float
    groceries: float
    insurance: float
    transportation: float
    debt_payments: float
    
    @property
    def total_fixed(self) -> float:
        return (self.rent + self.utilities + self.groceries + 
                self.insurance + self.transportation + self.debt_payments)


@dataclass
class StrategyResult:
    """Results of a payment strategy simulation"""
    strategy: PaymentStrategy
    amount_saved: float
    bills_paid_on_time: bool
    discretionary_spent: float
    late_fees: float
    stress_level: str  # low, medium, high
    final_balance: float
    description: str
    monthly_breakdown: List[Dict[str, Any]]


class PaycheckGameSimulator:
    """Simulates different paycheck allocation strategies"""
    
    def __init__(self):
        self.late_fee_per_bill = 35.0
        self.discretionary_categories = [
            "dining_out",
            "entertainment",
            "shopping",
            "subscriptions"
        ]
    
    def simulate_month(
        self,
        monthly_income: float,
        expenses: MonthlyExpenses,
        savings_goal_pct: float = 10.0,
        strategy: PaymentStrategy = PaymentStrategy.SAVE_FIRST
    ) -> StrategyResult:
        """
        Simulate one month with given payment strategy
        
        Args:
            monthly_income: Gross monthly income
            expenses: Fixed monthly expenses
            savings_goal_pct: Target savings percentage (default 10%)
            strategy: Payment sequencing strategy
            
        Returns:
            StrategyResult with outcomes
        """
        savings_target = monthly_income * (savings_goal_pct / 100)
        
        if strategy == PaymentStrategy.SPEND_FIRST:
            return self._simulate_spend_first(monthly_income, expenses, savings_target)
        elif strategy == PaymentStrategy.BILLS_FIRST:
            return self._simulate_bills_first(monthly_income, expenses, savings_target)
        else:  # SAVE_FIRST
            return self._simulate_save_first(monthly_income, expenses, savings_target)
    
    def _simulate_spend_first(
        self,
        income: float,
        expenses: MonthlyExpenses,
        savings_target: float
    ) -> StrategyResult:
        """Strategy A: Spend freely, pay bills, save what's left"""
        
        balance = income
        monthly_breakdown = []
        
        # Week 1: Paycheck arrives, immediate spending
        week1_spending = income * 0.20  # Spend 20% on wants immediately
        balance -= week1_spending
        monthly_breakdown.append({
            "week": 1,
            "event": "Paycheck + immediate spending",
            "amount": -week1_spending,
            "balance": balance,
            "notes": "Dining out, shopping spree"
        })
        
        # Week 2: More discretionary spending
        week2_spending = income * 0.15
        balance -= week2_spending
        monthly_breakdown.append({
            "week": 2,
            "event": "Continued spending",
            "amount": -week2_spending,
            "balance": balance,
            "notes": "Entertainment, subscriptions"
        })
        
        # Week 3: Bills start coming due
        bills_due = expenses.total_fixed
        late_fees = 0
        
        if balance < bills_due:
            # Can't pay all bills - incur late fees
            paid_bills = balance
            unpaid = bills_due - balance
            late_fees = self.late_fee_per_bill * 3  # Multiple bills late
            balance = 0
            bills_paid_on_time = False
            monthly_breakdown.append({
                "week": 3,
                "event": "Bills due - insufficient funds",
                "amount": -(paid_bills + late_fees),
                "balance": balance,
                "notes": f"Only paid ${paid_bills:.0f} of ${bills_due:.0f}. ${late_fees:.0f} in late fees!"
            })
        else:
            balance -= bills_due
            bills_paid_on_time = True
            monthly_breakdown.append({
                "week": 3,
                "event": "Bills paid",
                "amount": -bills_due,
                "balance": balance,
                "notes": "All bills paid on time"
            })
        
        # Week 4: Try to save what's left
        amount_saved = max(0, balance)
        
        total_discretionary = week1_spending + week2_spending
        
        return StrategyResult(
            strategy=PaymentStrategy.SPEND_FIRST,
            amount_saved=amount_saved,
            bills_paid_on_time=bills_paid_on_time,
            discretionary_spent=total_discretionary,
            late_fees=late_fees,
            stress_level="high",
            final_balance=balance,
            description=(
                "Spent freely at the start of the month. "
                "Struggled to pay bills. No meaningful savings. "
                "High stress and late fees."
            ),
            monthly_breakdown=monthly_breakdown
        )
    
    def _simulate_bills_first(
        self,
        income: float,
        expenses: MonthlyExpenses,
        savings_target: float
    ) -> StrategyResult:
        """Strategy B: Pay bills first, spend freely, save what's left"""
        
        balance = income
        monthly_breakdown = []
        
        # Week 1: Paycheck arrives, immediately pay bills
        bills_due = expenses.total_fixed
        balance -= bills_due
        monthly_breakdown.append({
            "week": 1,
            "event": "Paycheck + bills paid",
            "amount": -bills_due,
            "balance": balance,
            "notes": "All bills paid immediately"
        })
        
        # Week 2-3: Discretionary spending
        available_for_spending = balance * 0.60  # Spend 60% of remaining
        balance -= available_for_spending
        monthly_breakdown.append({
            "week": 2,
            "event": "Discretionary spending",
            "amount": -available_for_spending * 0.6,
            "balance": balance - (available_for_spending * 0.4),
            "notes": "Dining, shopping, entertainment"
        })
        
        monthly_breakdown.append({
            "week": 3,
            "event": "More spending",
            "amount": -available_for_spending * 0.4,
            "balance": balance,
            "notes": "Continue spending freely"
        })
        
        # Week 4: Try to save what's left
        amount_saved = max(0, balance)
        
        # Often very little left to save
        if amount_saved < savings_target * 0.2:
            stress_level = "medium"
            description = (
                "Paid bills on time (good!). "
                "Spent freely after. "
                f"Only saved ${amount_saved:.0f}, far below ${savings_target:.0f} goal. "
                "Tight at month-end."
            )
        else:
            stress_level = "medium"
            description = (
                "Paid bills on time. "
                "Had comfortable spending. "
                f"Saved ${amount_saved:.0f}."
            )
        
        return StrategyResult(
            strategy=PaymentStrategy.BILLS_FIRST,
            amount_saved=amount_saved,
            bills_paid_on_time=True,
            discretionary_spent=available_for_spending,
            late_fees=0,
            stress_level=stress_level,
            final_balance=balance,
            description=description,
            monthly_breakdown=monthly_breakdown
        )
    
    def _simulate_save_first(
        self,
        income: float,
        expenses: MonthlyExpenses,
        savings_target: float
    ) -> StrategyResult:
        """Strategy C: Auto-save first, pay bills, spend remainder"""
        
        balance = income
        monthly_breakdown = []
        
        # Week 1: Paycheck arrives, AUTO-SAVE immediately
        amount_saved = savings_target
        balance -= amount_saved
        monthly_breakdown.append({
            "week": 1,
            "event": "Paycheck + auto-save",
            "amount": -amount_saved,
            "balance": balance,
            "notes": f"${amount_saved:.0f} automatically transferred to savings"
        })
        
        # Pay bills
        bills_due = expenses.total_fixed
        balance -= bills_due
        monthly_breakdown.append({
            "week": 1,
            "event": "Bills paid",
            "amount": -bills_due,
            "balance": balance,
            "notes": "All bills paid on time"
        })
        
        # Week 2-4: Spend remainder guilt-free
        discretionary_budget = balance
        weekly_spending = discretionary_budget / 3
        
        for week in range(2, 5):
            balance -= weekly_spending
            monthly_breakdown.append({
                "week": week,
                "event": "Planned spending",
                "amount": -weekly_spending,
                "balance": balance,
                "notes": "Spending from planned discretionary budget"
            })
        
        return StrategyResult(
            strategy=PaymentStrategy.SAVE_FIRST,
            amount_saved=amount_saved,
            bills_paid_on_time=True,
            discretionary_spent=discretionary_budget,
            late_fees=0,
            stress_level="low",
            final_balance=balance,
            description=(
                f"Automatically saved ${amount_saved:.0f} (goal: ${savings_target:.0f}). "
                "Paid all bills on time. "
                "Spent remainder guilt-free. "
                "Low stress, clear financial picture."
            ),
            monthly_breakdown=monthly_breakdown
        )
    
    def compare_strategies(
        self,
        monthly_income: float,
        expenses: MonthlyExpenses,
        savings_goal_pct: float = 10.0,
        num_months: int = 12
    ) -> Dict[str, Any]:
        """
        Compare all three strategies over multiple months
        
        Args:
            monthly_income: Monthly income
            expenses: Fixed monthly expenses
            savings_goal_pct: Target savings percentage
            num_months: Number of months to simulate
            
        Returns:
            Comprehensive comparison data
        """
        
        results = {}
        
        for strategy in PaymentStrategy:
            monthly_result = self.simulate_month(
                monthly_income,
                expenses,
                savings_goal_pct,
                strategy
            )
            
            # Project over multiple months
            total_saved = monthly_result.amount_saved * num_months
            total_late_fees = monthly_result.late_fees * num_months
            total_discretionary = monthly_result.discretionary_spent * num_months
            
            results[strategy.value] = {
                "single_month": {
                    "amount_saved": monthly_result.amount_saved,
                    "bills_paid_on_time": monthly_result.bills_paid_on_time,
                    "discretionary_spent": monthly_result.discretionary_spent,
                    "late_fees": monthly_result.late_fees,
                    "stress_level": monthly_result.stress_level,
                    "final_balance": monthly_result.final_balance,
                    "description": monthly_result.description,
                    "breakdown": monthly_result.monthly_breakdown
                },
                "annual_projection": {
                    "total_saved": total_saved,
                    "total_late_fees": total_late_fees,
                    "total_discretionary": total_discretionary,
                    "net_worth_impact": total_saved - total_late_fees,
                    "months_with_late_fees": num_months if not monthly_result.bills_paid_on_time else 0
                }
            }
        
        # Calculate winner
        save_first_result = results[PaymentStrategy.SAVE_FIRST.value]
        bills_first_result = results[PaymentStrategy.BILLS_FIRST.value]
        spend_first_result = results[PaymentStrategy.SPEND_FIRST.value]
        
        return {
            "strategies": results,
            "comparison": {
                "best_strategy": PaymentStrategy.SAVE_FIRST.value,
                "worst_strategy": PaymentStrategy.SPEND_FIRST.value,
                "savings_difference": {
                    "save_vs_bills": save_first_result["annual_projection"]["total_saved"] - 
                                    bills_first_result["annual_projection"]["total_saved"],
                    "save_vs_spend": save_first_result["annual_projection"]["total_saved"] - 
                                    spend_first_result["annual_projection"]["total_saved"]
                },
                "recommendation": (
                    f"Pay Yourself First (Save First) is the clear winner. "
                    f"You'll save ${save_first_result['annual_projection']['total_saved']:,.0f} vs "
                    f"${spend_first_result['annual_projection']['total_saved']:,.0f} with Spend First - "
                    f"a difference of ${save_first_result['annual_projection']['total_saved'] - spend_first_result['annual_projection']['total_saved']:,.0f} per year!"
                )
            },
            "inputs": {
                "monthly_income": monthly_income,
                "total_fixed_expenses": expenses.total_fixed,
                "savings_goal_pct": savings_goal_pct,
                "num_months": num_months
            }
        }
    
    def calculate_optimal_savings_rate(
        self,
        monthly_income: float,
        expenses: MonthlyExpenses,
        min_discretionary: float = 300.0
    ) -> Dict[str, Any]:
        """
        Calculate the optimal savings rate given constraints
        
        Args:
            monthly_income: Monthly income
            expenses: Fixed monthly expenses
            min_discretionary: Minimum desired discretionary spending
            
        Returns:
            Optimal savings rate and breakdown
        """
        
        total_fixed = expenses.total_fixed
        available_after_bills = monthly_income - total_fixed
        
        if available_after_bills <= min_discretionary:
            return {
                "optimal_savings_rate": 0,
                "optimal_savings_amount": 0,
                "warning": "Income barely covers fixed expenses and minimum discretionary spending",
                "recommendation": "Focus on increasing income or reducing fixed expenses"
            }
        
        max_saveable = available_after_bills - min_discretionary
        optimal_rate = (max_saveable / monthly_income) * 100
        
        # Standard recommendations
        if optimal_rate >= 20:
            tier = "excellent"
            message = "You can save 20%+ comfortably"
        elif optimal_rate >= 15:
            tier = "great"
            message = "You can save 15-20% comfortably"
        elif optimal_rate >= 10:
            tier = "good"
            message = "You can save 10-15% (recommended minimum)"
        else:
            tier = "tight"
            message = "Savings will be challenging below 10%"
        
        return {
            "optimal_savings_rate": optimal_rate,
            "optimal_savings_amount": max_saveable,
            "tier": tier,
            "message": message,
            "breakdown": {
                "monthly_income": monthly_income,
                "fixed_expenses": total_fixed,
                "min_discretionary": min_discretionary,
                "available_to_save": max_saveable
            }
        }
