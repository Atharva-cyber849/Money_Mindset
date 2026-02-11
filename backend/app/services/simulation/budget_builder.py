"""
Budget Builder Simulation - 50/30/20 Rule Implementation
Interactive budget creation with real-world constraints
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class BudgetCategory(Enum):
    """Budget category types"""
    # NEEDS (50%)
    HOUSING = "housing"
    UTILITIES = "utilities"
    GROCERIES = "groceries"
    TRANSPORTATION = "transportation"
    INSURANCE = "insurance"
    MINIMUM_DEBT_PAYMENTS = "minimum_debt_payments"
    HEALTHCARE = "healthcare"
    
    # WANTS (30%)
    DINING_OUT = "dining_out"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    HOBBIES = "hobbies"
    SUBSCRIPTIONS = "subscriptions"
    TRAVEL = "travel"
    
    # SAVINGS (20%)
    EMERGENCY_FUND = "emergency_fund"
    RETIREMENT = "retirement"
    INVESTMENTS = "investments"
    DEBT_PAYOFF = "debt_payoff"
    GOALS = "goals"


@dataclass
class CategoryAllocation:
    """Budget allocation for a category"""
    category: BudgetCategory
    amount: float
    percentage: float
    is_fixed: bool = False
    notes: Optional[str] = None


@dataclass
class BudgetValidation:
    """Budget validation results"""
    is_balanced: bool
    needs_percentage: float
    wants_percentage: float
    savings_percentage: float
    total_allocated: float
    warnings: List[str]
    recommendations: List[str]
    score: int  # 0-100


class BudgetBuilderSimulator:
    """Interactive 50/30/20 budget builder with constraints"""
    
    # Ideal percentages
    IDEAL_NEEDS = 50.0
    IDEAL_WANTS = 30.0
    IDEAL_SAVINGS = 20.0
    
    # Acceptable ranges
    NEEDS_MIN = 40.0
    NEEDS_MAX = 65.0
    WANTS_MIN = 15.0
    WANTS_MAX = 40.0
    SAVINGS_MIN = 10.0
    SAVINGS_MAX = 35.0
    
    def __init__(self):
        self.needs_categories = [
            BudgetCategory.HOUSING,
            BudgetCategory.UTILITIES,
            BudgetCategory.GROCERIES,
            BudgetCategory.TRANSPORTATION,
            BudgetCategory.INSURANCE,
            BudgetCategory.MINIMUM_DEBT_PAYMENTS,
            BudgetCategory.HEALTHCARE
        ]
        
        self.wants_categories = [
            BudgetCategory.DINING_OUT,
            BudgetCategory.ENTERTAINMENT,
            BudgetCategory.SHOPPING,
            BudgetCategory.HOBBIES,
            BudgetCategory.SUBSCRIPTIONS,
            BudgetCategory.TRAVEL
        ]
        
        self.savings_categories = [
            BudgetCategory.EMERGENCY_FUND,
            BudgetCategory.RETIREMENT,
            BudgetCategory.INVESTMENTS,
            BudgetCategory.DEBT_PAYOFF,
            BudgetCategory.GOALS
        ]
    
    def create_budget(
        self,
        monthly_income: float,
        allocations: Dict[str, float],
        location_col_multiplier: float = 1.0
    ) -> Dict[str, Any]:
        """
        Create and validate a budget
        
        Args:
            monthly_income: Monthly income
            allocations: Dict of category names to amounts
            location_col_multiplier: Cost of living multiplier (1.0 = average)
            
        Returns:
            Budget analysis with validation
        """
        
        # Parse allocations
        category_allocations = []
        for category_str, amount in allocations.items():
            try:
                category = BudgetCategory(category_str)
                percentage = (amount / monthly_income) * 100
                category_allocations.append(
                    CategoryAllocation(
                        category=category,
                        amount=amount,
                        percentage=percentage
                    )
                )
            except ValueError:
                continue
        
        # Calculate totals by type
        needs_total = sum(
            a.amount for a in category_allocations 
            if a.category in self.needs_categories
        )
        wants_total = sum(
            a.amount for a in category_allocations 
            if a.category in self.wants_categories
        )
        savings_total = sum(
            a.amount for a in category_allocations 
            if a.category in self.savings_categories
        )
        
        total_allocated = needs_total + wants_total + savings_total
        
        needs_pct = (needs_total / monthly_income) * 100
        wants_pct = (wants_total / monthly_income) * 100
        savings_pct = (savings_total / monthly_income) * 100
        
        # Validate and score
        validation = self._validate_budget(
            monthly_income,
            needs_pct,
            wants_pct,
            savings_pct,
            total_allocated,
            category_allocations,
            location_col_multiplier
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            monthly_income,
            needs_pct,
            wants_pct,
            savings_pct,
            category_allocations,
            location_col_multiplier
        )
        
        return {
            "summary": {
                "monthly_income": monthly_income,
                "total_allocated": total_allocated,
                "remaining": monthly_income - total_allocated,
                "needs_total": needs_total,
                "wants_total": wants_total,
                "savings_total": savings_total,
                "needs_percentage": needs_pct,
                "wants_percentage": wants_pct,
                "savings_percentage": savings_pct
            },
            "allocations": [
                {
                    "category": a.category.value,
                    "amount": a.amount,
                    "percentage": a.percentage,
                    "type": self._get_category_type(a.category)
                }
                for a in category_allocations
            ],
            "validation": {
                "is_balanced": validation.is_balanced,
                "score": validation.score,
                "warnings": validation.warnings,
                "recommendations": validation.recommendations
            },
            "comparison_to_ideal": {
                "needs": {
                    "actual": needs_pct,
                    "ideal": self.IDEAL_NEEDS,
                    "difference": needs_pct - self.IDEAL_NEEDS,
                    "status": self._get_status(needs_pct, self.IDEAL_NEEDS, self.NEEDS_MIN, self.NEEDS_MAX)
                },
                "wants": {
                    "actual": wants_pct,
                    "ideal": self.IDEAL_WANTS,
                    "difference": wants_pct - self.IDEAL_WANTS,
                    "status": self._get_status(wants_pct, self.IDEAL_WANTS, self.WANTS_MIN, self.WANTS_MAX)
                },
                "savings": {
                    "actual": savings_pct,
                    "ideal": self.IDEAL_SAVINGS,
                    "difference": savings_pct - self.IDEAL_SAVINGS,
                    "status": self._get_status(savings_pct, self.IDEAL_SAVINGS, self.SAVINGS_MIN, self.SAVINGS_MAX)
                }
            },
            "recommendations": recommendations
        }
    
    def _validate_budget(
        self,
        monthly_income: float,
        needs_pct: float,
        wants_pct: float,
        savings_pct: float,
        total_allocated: float,
        allocations: List[CategoryAllocation],
        col_multiplier: float
    ) -> BudgetValidation:
        """Validate budget and generate warnings"""
        
        warnings = []
        recommendations = []
        score = 100
        
        # Check if balanced (allocates all income)
        remaining = monthly_income - total_allocated
        is_balanced = abs(remaining) < 1.0
        
        if remaining > 100:
            warnings.append(f"${remaining:.0f} unallocated - assign to a category")
            score -= 10
        elif remaining < -1:
            warnings.append(f"Over budget by ${abs(remaining):.0f}")
            score -= 20
        
        # Check needs percentage
        if needs_pct > self.NEEDS_MAX:
            warnings.append(
                f"Needs at {needs_pct:.1f}% (high). "
                f"Target: {self.IDEAL_NEEDS}%. "
                f"Consider reducing housing or transportation costs."
            )
            score -= 15
        elif needs_pct < self.NEEDS_MIN:
            warnings.append(
                f"Needs at {needs_pct:.1f}% (low). "
                f"Ensure all essential expenses are included."
            )
            score -= 5
        
        # Check wants percentage
        if wants_pct > self.WANTS_MAX:
            warnings.append(
                f"Wants at {wants_pct:.1f}% (high). "
                f"Target: {self.IDEAL_WANTS}%. "
                f"Consider cutting discretionary spending."
            )
            score -= 10
        elif wants_pct < self.WANTS_MIN:
            recommendations.append(
                f"Wants at {wants_pct:.1f}% - you're being frugal! "
                f"Consider allocating more for enjoyment."
            )
        
        # Check savings percentage
        if savings_pct < self.SAVINGS_MIN:
            warnings.append(
                f"Savings at {savings_pct:.1f}% (too low). "
                f"Target: {self.IDEAL_SAVINGS}%. "
                f"Try to save at least 10% for financial security."
            )
            score -= 25
        elif savings_pct > self.SAVINGS_MAX:
            recommendations.append(
                f"Savings at {savings_pct:.1f}% - excellent! "
                f"You're saving more than the recommended 20%."
            )
            score += 10
        
        # Check specific categories
        housing_alloc = next(
            (a for a in allocations if a.category == BudgetCategory.HOUSING),
            None
        )
        if housing_alloc:
            housing_pct = housing_alloc.percentage
            max_housing = 30 * col_multiplier  # Adjust for location
            
            if housing_pct > max_housing:
                warnings.append(
                    f"Housing at {housing_pct:.1f}% is above recommended {max_housing:.0f}%. "
                    f"This is limiting your financial flexibility."
                )
                score -= 10
        
        # Ensure minimum emergency fund allocation
        emergency_alloc = next(
            (a for a in allocations if a.category == BudgetCategory.EMERGENCY_FUND),
            None
        )
        if not emergency_alloc or emergency_alloc.amount < monthly_income * 0.05:
            warnings.append(
                "No emergency fund allocation. "
                "Aim to save at least 5% for emergencies."
            )
            score -= 15
        
        return BudgetValidation(
            is_balanced=is_balanced,
            needs_percentage=needs_pct,
            wants_percentage=wants_pct,
            savings_percentage=savings_pct,
            total_allocated=total_allocated,
            warnings=warnings,
            recommendations=recommendations,
            score=max(0, min(100, score))
        )
    
    def _generate_recommendations(
        self,
        monthly_income: float,
        needs_pct: float,
        wants_pct: float,
        savings_pct: float,
        allocations: List[CategoryAllocation],
        col_multiplier: float
    ) -> List[Dict[str, Any]]:
        """Generate specific budget improvement recommendations"""
        
        recommendations = []
        
        # If needs are too high, suggest cuts
        if needs_pct > self.NEEDS_MAX:
            housing = next(
                (a for a in allocations if a.category == BudgetCategory.HOUSING),
                None
            )
            if housing and housing.percentage > 30:
                recommendations.append({
                    "priority": "high",
                    "category": "housing",
                    "current": housing.amount,
                    "suggested": monthly_income * 0.30,
                    "savings": housing.amount - (monthly_income * 0.30),
                    "action": "Consider moving to a more affordable place or getting a roommate"
                })
        
        # If savings are too low
        if savings_pct < self.IDEAL_SAVINGS:
            target_savings = monthly_income * (self.IDEAL_SAVINGS / 100)
            current_savings = monthly_income * (savings_pct / 100)
            gap = target_savings - current_savings
            
            recommendations.append({
                "priority": "high",
                "category": "savings",
                "current": current_savings,
                "suggested": target_savings,
                "savings": gap,
                "action": f"Increase savings by ${gap:.0f}/month to reach 20% target"
            })
            
            # Suggest where to cut
            wants_total = monthly_income * (wants_pct / 100)
            if wants_total >= gap:
                recommendations.append({
                    "priority": "medium",
                    "category": "wants",
                    "current": wants_total,
                    "suggested": wants_total - gap,
                    "savings": gap,
                    "action": f"Reduce discretionary spending by ${gap:.0f}/month"
                })
        
        # Subscription optimization
        subscriptions = next(
            (a for a in allocations if a.category == BudgetCategory.SUBSCRIPTIONS),
            None
        )
        if subscriptions and subscriptions.amount > 100:
            recommendations.append({
                "priority": "low",
                "category": "subscriptions",
                "current": subscriptions.amount,
                "suggested": 50,
                "savings": subscriptions.amount - 50,
                "action": "Audit and cancel unused subscriptions. Most people can cut this by 50%."
            })
        
        return recommendations
    
    def _get_category_type(self, category: BudgetCategory) -> str:
        """Get the budget type for a category"""
        if category in self.needs_categories:
            return "needs"
        elif category in self.wants_categories:
            return "wants"
        else:
            return "savings"
    
    def _get_status(
        self,
        actual: float,
        ideal: float,
        min_acceptable: float,
        max_acceptable: float
    ) -> str:
        """Get status for a budget category"""
        if actual < min_acceptable:
            return "too_low"
        elif actual > max_acceptable:
            return "too_high"
        elif abs(actual - ideal) < 5:
            return "excellent"
        elif min_acceptable <= actual <= max_acceptable:
            return "good"
        else:
            return "needs_adjustment"
    
    def generate_challenge_scenario(
        self,
        monthly_income: float,
        location: str = "average"
    ) -> Dict[str, Any]:
        """
        Generate a realistic budget challenge with constraints
        
        Args:
            monthly_income: Monthly income
            location: 'low_cost', 'average', 'high_cost'
            
        Returns:
            Challenge scenario with constraints
        """
        
        # Cost of living multipliers
        col_multipliers = {
            "low_cost": 0.85,
            "average": 1.0,
            "high_cost": 1.35
        }
        multiplier = col_multipliers.get(location, 1.0)
        
        # Generate realistic constraints
        rent_baseline = monthly_income * 0.35
        rent = rent_baseline * multiplier
        
        constraints = {
            "housing": {
                "amount": rent,
                "fixed": True,
                "note": f"Your rent is ${rent:.0f} - that's already {(rent/monthly_income)*100:.1f}% of income"
            },
            "minimum_debt": {
                "amount": monthly_income * 0.10,
                "fixed": True,
                "note": "Minimum debt payments required"
            },
            "groceries": {
                "amount": monthly_income * 0.08 * multiplier,
                "fixed": False,
                "note": "Average grocery spending for your area"
            }
        }
        
        return {
            "monthly_income": monthly_income,
            "location": location,
            "col_multiplier": multiplier,
            "constraints": constraints,
            "challenge": (
                f"Create a balanced budget with ${monthly_income:,.0f}/month. "
                f"You live in a {location.replace('_', ' ')} city. "
                f"Rent is ${rent:.0f} (fixed). "
                f"Can you still save 20%?"
            ),
            "difficulty": "hard" if multiplier > 1.2 else "medium" if multiplier > 1.0 else "easy"
        }
    
    def compare_to_national_average(
        self,
        monthly_income: float,
        allocations: Dict[str, float]
    ) -> Dict[str, Any]:
        """Compare user's budget to national averages"""
        
        # National average percentages (approximate)
        national_avg = {
            "needs": 58.0,  # Most Americans spend too much on needs
            "wants": 28.0,
            "savings": 14.0  # Below recommended 20%
        }
        
        # Calculate user percentages
        needs_total = sum(
            amount for cat, amount in allocations.items()
            if BudgetCategory(cat) in self.needs_categories
        )
        wants_total = sum(
            amount for cat, amount in allocations.items()
            if BudgetCategory(cat) in self.wants_categories
        )
        savings_total = sum(
            amount for cat, amount in allocations.items()
            if BudgetCategory(cat) in self.savings_categories
        )
        
        user_pct = {
            "needs": (needs_total / monthly_income) * 100,
            "wants": (wants_total / monthly_income) * 100,
            "savings": (savings_total / monthly_income) * 100
        }
        
        comparison = {}
        for category in ["needs", "wants", "savings"]:
            user_val = user_pct[category]
            avg_val = national_avg[category]
            diff = user_val - avg_val
            
            if category == "savings":
                better = diff > 0
                message = "saving more" if better else "saving less"
            elif category == "needs":
                better = diff < 0
                message = "spending less" if better else "spending more"
            else:  # wants
                better = abs(diff) < 5
                message = "similar to average"
            
            comparison[category] = {
                "your_percentage": user_val,
                "national_average": avg_val,
                "difference": diff,
                "better_than_average": better,
                "message": message
            }
        
        return {
            "comparison": comparison,
            "overall_assessment": self._assess_vs_average(comparison)
        }
    
    def _assess_vs_average(self, comparison: Dict) -> str:
        """Assess overall budget vs national average"""
        
        savings_better = comparison["savings"]["better_than_average"]
        needs_better = comparison["needs"]["better_than_average"]
        
        if savings_better and needs_better:
            return "Excellent! You're saving more and spending less on needs than average."
        elif savings_better:
            return "Good! You're saving more than the average American."
        elif needs_better:
            return "Your needs spending is controlled, but try to increase savings."
        else:
            return "There's room for improvement. Focus on reducing needs and increasing savings."
