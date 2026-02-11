"""
Budget Optimization Service  
Rule-based heuristics to analyze savings and expense ratios
Provides actionable recommendations for budget improvements
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class BudgetRule:
    """Represents a budgeting rule or guideline"""
    name: str
    category: str
    max_percentage: float
    ideal_percentage: float
    description: str


class BudgetOptimizer:
    """
    Analyze budgets using proven financial rules and provide optimization suggestions.
    Based on 50/30/20 rule and other financial best practices.
    """
    
    # Industry-standard budget allocation rules
    BUDGET_RULES = {
        "housing": BudgetRule(
            name="Housing Rule",
            category="housing",
            max_percentage=30.0,
            ideal_percentage=25.0,
            description="Housing costs should not exceed 30% of gross income"
        ),
        "transportation": BudgetRule(
            name="Transportation Rule",
            category="transportation",
            max_percentage=15.0,
            ideal_percentage=10.0,
            description="Transportation costs should stay under 15% of income"
        ),
        "food": BudgetRule(
            name="Food Budget",
            category="groceries",
            max_percentage=15.0,
            ideal_percentage=10.0,
            description="Food expenses (groceries + dining) should be 10-15% of income"
        ),
        "savings": BudgetRule(
            name="Savings Rule",
            category="savings",
            max_percentage=100.0,
            ideal_percentage=20.0,
            description="Save at least 20% of income for future goals"
        ),
        "debt": BudgetRule(
            name="Debt Payment Rule",
            category="debt",
            max_percentage=15.0,
            ideal_percentage=10.0,
            description="Debt payments should not exceed 15% of income"
        )
    }
    
    # 50/30/20 Rule breakdown
    BUDGET_50_30_20 = {
        "needs": {"percentage": 50.0, "description": "Essential expenses (housing, utilities, food, transport)"},
        "wants": {"percentage": 30.0, "description": "Discretionary spending (entertainment, dining out, hobbies)"},
        "savings": {"percentage": 20.0, "description": "Savings and debt repayment"}
    }
    
    def analyze_budget(
        self,
        income: float,
        expenses: Dict[str, float],
        savings: float = 0.0
    ) -> Dict:
        """
        Comprehensive budget analysis with recommendations.
        
        Args:
            income: Monthly gross income
            expenses: Dict of category -> amount
            savings: Monthly savings amount
        
        Returns:
            Detailed analysis with scores and recommendations
        """
        total_expenses = sum(expenses.values())
        total_committed = total_expenses + savings
        discretionary = income - total_committed
        
        # Calculate percentages
        expense_percentages = {
            category: (amount / income * 100) if income > 0 else 0
            for category, amount in expenses.items()
        }
        
        savings_percentage = (savings / income * 100) if income > 0 else 0
        
        # Analyze against rules
        rule_violations = []
        recommendations = []
        
        for category, amount in expenses.items():
            percentage = expense_percentages[category]
            
            # Check against specific rules
            if category in self.BUDGET_RULES:
                rule = self.BUDGET_RULES[category]
                
                if percentage > rule.max_percentage:
                    rule_violations.append({
                        "category": category,
                        "current": round(percentage, 1),
                        "max": rule.max_percentage,
                        "overage": round(percentage - rule.max_percentage, 1),
                        "amount_to_reduce": round(amount - (income * rule.max_percentage / 100), 2)
                    })
                    
                    recommendations.append({
                        "priority": "high",
                        "category": category,
                        "issue": f"{category.title()} is {round(percentage - rule.max_percentage, 1)}% over recommended",
                        "suggestion": self._get_category_suggestion(category, percentage - rule.max_percentage)
                    })
                
                elif percentage > rule.ideal_percentage:
                    recommendations.append({
                        "priority": "medium",
                        "category": category,
                        "issue": f"{category.title()} could be optimized",
                        "suggestion": f"Consider reducing to {rule.ideal_percentage}% (${income * rule.ideal_percentage / 100:.2f})"
                    })
        
        # Check savings rate
        if savings_percentage < 20.0:
            recommendations.append({
                "priority": "high",
                "category": "savings",
                "issue": f"Savings rate is only {savings_percentage:.1f}%",
                "suggestion": f"Aim to save ${income * 0.20:.2f}/month (20% of income)"
            })
        
        # 50/30/20 analysis
        budget_50_30_20_analysis = self._analyze_50_30_20(income, expenses, savings)
        
        # Calculate health score
        health_score = self._calculate_budget_health_score(
            income,
            expenses,
            savings,
            rule_violations
        )
        
        return {
            "summary": {
                "monthly_income": round(income, 2),
                "total_expenses": round(total_expenses, 2),
                "total_savings": round(savings, 2),
                "discretionary": round(discretionary, 2),
                "savings_rate_pct": round(savings_percentage, 1)
            },
            "breakdown": {
                category: {
                    "amount": round(amount, 2),
                    "percentage": round(expense_percentages[category], 1)
                }
                for category, amount in sorted(
                    expenses.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            "health_score": health_score,
            "rule_violations": rule_violations,
            "fifty_thirty_twenty": budget_50_30_20_analysis,
            "recommendations": sorted(
                recommendations,
                key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]]
            ),
            "optimization_potential": self._calculate_optimization_potential(
                income,
                expenses,
                savings
            )
        }
    
    def _analyze_50_30_20(
        self,
        income: float,
        expenses: Dict[str, float],
        savings: float
    ) -> Dict:
        """Analyze budget against 50/30/20 rule"""
        # Categorize expenses
        needs_categories = ["housing", "utilities", "groceries", "transportation", "insurance", "healthcare"]
        wants_categories = ["restaurants", "entertainment", "shopping", "subscriptions", "personal_care"]
        
        needs_total = sum(amount for cat, amount in expenses.items() if cat in needs_categories)
        wants_total = sum(amount for cat, amount in expenses.items() if cat in wants_categories)
        
        needs_pct = (needs_total / income * 100) if income > 0 else 0
        wants_pct = (wants_total / income * 100) if income > 0 else 0
        savings_pct = (savings / income * 100) if income > 0 else 0
        
        return {
            "needs": {
                "amount": round(needs_total, 2),
                "percentage": round(needs_pct, 1),
                "target": 50.0,
                "target_amount": round(income * 0.5, 2),
                "status": self._get_status(needs_pct, 50.0, tolerance=5.0)
            },
            "wants": {
                "amount": round(wants_total, 2),
                "percentage": round(wants_pct, 1),
                "target": 30.0,
                "target_amount": round(income * 0.3, 2),
                "status": self._get_status(wants_pct, 30.0, tolerance=5.0)
            },
            "savings": {
                "amount": round(savings, 2),
                "percentage": round(savings_pct, 1),
                "target": 20.0,
                "target_amount": round(income * 0.2, 2),
                "status": self._get_status(savings_pct, 20.0, tolerance=3.0)
            },
            "overall_compliance": self._calculate_50_30_20_score(needs_pct, wants_pct, savings_pct)
        }
    
    def _get_status(self, actual: float, target: float, tolerance: float) -> str:
        """Determine if value is within acceptable range"""
        if abs(actual - target) <= tolerance:
            return "on_track"
        elif actual > target:
            return "over_budget"
        else:
            return "under_budget"
    
    def _calculate_50_30_20_score(
        self,
        needs_pct: float,
        wants_pct: float,
        savings_pct: float
    ) -> Dict:
        """Calculate compliance score for 50/30/20 rule"""
        # Penalties for deviation
        needs_penalty = abs(needs_pct - 50.0) * 2
        wants_penalty = abs(wants_pct - 30.0) * 2
        savings_penalty = max(0, 20.0 - savings_pct) * 3  # Heavier penalty for low savings
        
        total_penalty = needs_penalty + wants_penalty + savings_penalty
        score = max(0, 100 - total_penalty)
        
        if score >= 90:
            grade = "A"
            message = "Excellent budget balance!"
        elif score >= 80:
            grade = "B"
            message = "Good budget, minor adjustments recommended"
        elif score >= 70:
            grade = "C"
            message = "Fair budget, needs improvement"
        elif score >= 60:
            grade = "D"
            message = "Budget needs significant adjustment"
        else:
            grade = "F"
            message = "Budget requires major restructuring"
        
        return {
            "score": round(score, 1),
            "grade": grade,
            "message": message
        }
    
    def _calculate_budget_health_score(
        self,
        income: float,
        expenses: Dict[str, float],
        savings: float,
        violations: List[Dict]
    ) -> Dict:
        """Calculate overall budget health score"""
        score = 100
        
        # Deduct points for violations
        score -= len(violations) * 10
        
        # Check savings rate
        savings_rate = (savings / income * 100) if income > 0 else 0
        if savings_rate < 10:
            score -= 20
        elif savings_rate < 15:
            score -= 10
        elif savings_rate < 20:
            score -= 5
        elif savings_rate >= 30:
            score += 10  # Bonus for high savings
        
        # Check expense-to-income ratio
        total_expenses = sum(expenses.values())
        expense_ratio = (total_expenses / income * 100) if income > 0 else 0
        
        if expense_ratio > 80:
            score -= 15
        elif expense_ratio > 70:
            score -= 10
        elif expense_ratio > 60:
            score -= 5
        
        score = max(0, min(100, score))
        
        # Determine rating
        if score >= 90:
            rating = "Excellent"
            color = "green"
        elif score >= 75:
            rating = "Good"
            color = "blue"
        elif score >= 60:
            rating = "Fair"
            color = "yellow"
        elif score >= 40:
            rating = "Needs Improvement"
            color = "orange"
        else:
            rating = "Critical"
            color = "red"
        
        return {
            "score": round(score, 1),
            "rating": rating,
            "color": color,
            "factors": {
                "savings_rate": round(savings_rate, 1),
                "expense_ratio": round(expense_ratio, 1),
                "violations": len(violations)
            }
        }
    
    def _get_category_suggestion(self, category: str, overage_pct: float) -> str:
        """Generate specific suggestions based on category"""
        suggestions = {
            "housing": "Consider refinancing, finding roommates, or relocating to reduce housing costs.",
            "transportation": "Explore public transit, carpooling, or a more affordable vehicle.",
            "groceries": "Meal plan, buy in bulk, use coupons, and reduce food waste.",
            "restaurants": "Cook more at home, pack lunches, limit dining out to special occasions.",
            "entertainment": "Find free activities, use streaming services wisely, explore budget hobbies.",
            "shopping": "Implement a 30-day rule for non-essential purchases, unsubscribe from marketing emails.",
            "subscriptions": "Audit and cancel unused subscriptions, share family plans."
        }
        
        return suggestions.get(
            category,
            f"Look for ways to reduce {category} expenses by at least {overage_pct:.0f}%."
        )
    
    def _calculate_optimization_potential(
        self,
        income: float,
        expenses: Dict[str, float],
        savings: float
    ) -> Dict:
        """Calculate how much could potentially be saved"""
        potential_savings = 0
        
        # Check each category against ideal percentages
        for category, amount in expenses.items():
            if category in self.BUDGET_RULES:
                rule = self.BUDGET_RULES[category]
                ideal_amount = income * rule.ideal_percentage / 100
                
                if amount > ideal_amount:
                    potential_savings += (amount - ideal_amount)
        
        # Calculate what savings rate could be
        current_savings_rate = (savings / income * 100) if income > 0 else 0
        potential_savings_rate = ((savings + potential_savings) / income * 100) if income > 0 else 0
        
        return {
            "current_savings": round(savings, 2),
            "potential_additional_savings": round(potential_savings, 2),
            "potential_total_savings": round(savings + potential_savings, 2),
            "current_savings_rate": round(current_savings_rate, 1),
            "potential_savings_rate": round(potential_savings_rate, 1),
            "improvement": round(potential_savings_rate - current_savings_rate, 1)
        }
    
    def suggest_budget_allocation(self, income: float) -> Dict:
        """
        Suggest ideal budget allocation based on income.
        
        Args:
            income: Monthly gross income
        
        Returns:
            Recommended budget allocation
        """
        # Use 50/30/20 as base
        needs_amount = income * 0.50
        wants_amount = income * 0.30
        savings_amount = income * 0.20
        
        # Break down needs
        needs_breakdown = {
            "housing": round(income * 0.25, 2),
            "utilities": round(income * 0.05, 2),
            "groceries": round(income * 0.08, 2),
            "transportation": round(income * 0.10, 2),
            "insurance": round(income * 0.05, 2),
            "healthcare": round(income * 0.05, 2)
        }
        
        # Break down wants
        wants_breakdown = {
            "restaurants": round(income * 0.10, 2),
            "entertainment": round(income * 0.08, 2),
            "shopping": round(income * 0.07, 2),
            "subscriptions": round(income * 0.03, 2),
            "personal_care": round(income * 0.02, 2)
        }
        
        # Break down savings
        savings_breakdown = {
            "emergency_fund": round(income * 0.10, 2),
            "retirement": round(income * 0.06, 2),
            "debt_payment": round(income * 0.02, 2),
            "goals": round(income * 0.02, 2)
        }
        
        return {
            "monthly_income": round(income, 2),
            "recommended_allocation": {
                "needs": {
                    "total": round(needs_amount, 2),
                    "percentage": 50.0,
                    "breakdown": needs_breakdown
                },
                "wants": {
                    "total": round(wants_amount, 2),
                    "percentage": 30.0,
                    "breakdown": wants_breakdown
                },
                "savings": {
                    "total": round(savings_amount, 2),
                    "percentage": 20.0,
                    "breakdown": savings_breakdown
                }
            },
            "framework": "50/30/20 Rule",
            "note": "These are guidelines. Adjust based on your location, life stage, and personal circumstances."
        }
    
    def compare_to_peers(
        self,
        income: float,
        expenses: Dict[str, float],
        savings: float,
        age_group: str,
        location: str = "national"
    ) -> Dict:
        """
        Compare budget to peer averages.
        
        Args:
            income: Monthly income
            expenses: Expense breakdown
            savings: Monthly savings
            age_group: "18-24", "25-34", "35-44", "45-54", "55-64", "65+"
            location: Geographic comparison (default: national)
        
        Returns:
            Peer comparison data
        """
        # Simplified peer data (would come from database in production)
        peer_benchmarks = {
            "18-24": {"housing": 32, "transportation": 18, "food": 15, "savings": 5},
            "25-34": {"housing": 30, "transportation": 16, "food": 13, "savings": 10},
            "35-44": {"housing": 28, "transportation": 15, "food": 12, "savings": 15},
            "45-54": {"housing": 26, "transportation": 14, "food": 11, "savings": 18},
            "55-64": {"housing": 25, "transportation": 12, "food": 10, "savings": 22},
            "65+": {"housing": 28, "transportation": 10, "food": 12, "savings": 15}
        }
        
        benchmarks = peer_benchmarks.get(age_group, peer_benchmarks["25-34"])
        
        # Calculate user percentages
        total_expenses = sum(expenses.values())
        user_percentages = {
            cat: (amt / income * 100) if income > 0 else 0
            for cat, amt in expenses.items()
        }
        user_savings_pct = (savings / income * 100) if income > 0 else 0
        
        # Compare
        comparison = {}
        for category, peer_pct in benchmarks.items():
            user_pct = user_percentages.get(category, 0)
            if category == "savings":
                user_pct = user_savings_pct
            
            comparison[category] = {
                "your_percentage": round(user_pct, 1),
                "peer_average": peer_pct,
                "difference": round(user_pct - peer_pct, 1),
                "status": "above" if user_pct > peer_pct else "below" if user_pct < peer_pct else "equal"
            }
        
        return {
            "age_group": age_group,
            "location": location,
            "comparison": comparison,
            "summary": self._generate_peer_summary(comparison)
        }
    
    def _generate_peer_summary(self, comparison: Dict) -> str:
        """Generate summary of peer comparison"""
        better = sum(1 for cat, data in comparison.items() 
                    if (data["status"] == "below" and cat != "savings") or 
                       (data["status"] == "above" and cat == "savings"))
        worse = sum(1 for cat, data in comparison.items() 
                   if (data["status"] == "above" and cat != "savings") or 
                      (data["status"] == "below" and cat == "savings"))
        
        if better > worse:
            return f"You're doing better than peers in {better} out of {len(comparison)} categories!"
        elif worse > better:
            return f"There's room for improvement in {worse} categories to match peer averages."
        else:
            return "You're performing similar to your peer group overall."
