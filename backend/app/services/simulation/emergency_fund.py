"""
Emergency Fund Race Simulation
Compare two characters over 12 months with/without emergency fund
"""
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import random


class EmergencyType(Enum):
    """Types of emergencies that can occur"""
    CAR_REPAIR = "car_repair"
    MEDICAL = "medical"
    HOME_REPAIR = "home_repair"
    JOB_LOSS = "job_loss"
    APPLIANCE = "appliance"
    PET_EMERGENCY = "pet_emergency"


@dataclass
class Emergency:
    """An emergency event"""
    month: int
    type: EmergencyType
    cost: float
    description: str
    severity: str  # 'minor', 'moderate', 'major'


@dataclass
class CharacterState:
    """Monthly state of a character"""
    month: int
    income: float
    expenses: float
    emergency_fund: float
    credit_card_debt: float
    stress_level: int  # 1-10
    can_handle_emergency: bool


@dataclass
class SimulationResult:
    """Final results for a character"""
    character_name: str
    strategy: str
    monthly_states: List[CharacterState]
    emergencies_faced: List[Emergency]
    total_saved: float
    total_debt_incurred: float
    total_interest_paid: float
    final_net_worth: float
    average_stress: float
    success_score: int


class EmergencyFundSimulator:
    """Simulate the value of having an emergency fund"""
    
    def __init__(self, seed: int = 42):
        """
        Args:
            seed: Random seed for reproducible emergencies
        """
        self.random = random.Random(seed)
        self.credit_card_apr = 0.22  # 22% APR
        self.monthly_interest_rate = self.credit_card_apr / 12
        
        # Emergency probabilities and costs
        self.emergency_templates = {
            EmergencyType.CAR_REPAIR: {
                "probability": 0.15,  # 15% chance per month
                "cost_range": (300, 1500),
                "descriptions": [
                    "Flat tire needs replacement",
                    "Battery died",
                    "Brake pads worn out",
                    "Transmission issue",
                    "Engine trouble"
                ]
            },
            EmergencyType.MEDICAL: {
                "probability": 0.10,
                "cost_range": (200, 2000),
                "descriptions": [
                    "Urgent care visit",
                    "Prescription medication",
                    "Dental emergency",
                    "ER visit",
                    "Medical test"
                ]
            },
            EmergencyType.HOME_REPAIR: {
                "probability": 0.08,
                "cost_range": (400, 1800),
                "descriptions": [
                    "Plumbing leak",
                    "Broken water heater",
                    "Roof leak",
                    "HVAC repair",
                    "Electrical issue"
                ]
            },
            EmergencyType.APPLIANCE: {
                "probability": 0.06,
                "cost_range": (200, 800),
                "descriptions": [
                    "Refrigerator broke",
                    "Washing machine died",
                    "Microwave replacement",
                    "Dishwasher repair"
                ]
            },
            EmergencyType.PET_EMERGENCY: {
                "probability": 0.05,
                "cost_range": (300, 1500),
                "descriptions": [
                    "Pet needs vet visit",
                    "Emergency pet surgery",
                    "Pet medication"
                ]
            }
        }
    
    def simulate_race(
        self,
        monthly_income: float = 3500,
        monthly_expenses: float = 2800,
        duration_months: int = 12
    ) -> Dict[str, Any]:
        """
        Simulate two characters over time
        
        Character A (Alex): Builds emergency fund ($500/month)
        Character B (Jordan): No emergency fund, spends everything
        
        Args:
            monthly_income: Monthly take-home pay
            monthly_expenses: Fixed monthly expenses
            duration_months: Number of months to simulate
            
        Returns:
            Complete simulation results
        """
        
        monthly_savings = monthly_income - monthly_expenses
        
        # Generate emergencies (same for both characters)
        emergencies = self._generate_emergencies(duration_months)
        
        # Simulate Alex (with emergency fund)
        alex_result = self._simulate_character(
            name="Alex",
            strategy="Saves $500/month for emergencies",
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            monthly_savings=500,
            emergencies=emergencies
        )
        
        # Simulate Jordan (no emergency fund)
        jordan_result = self._simulate_character(
            name="Jordan",
            strategy="Spends everything, no emergency fund",
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            monthly_savings=0,
            emergencies=emergencies
        )
        
        # Compare outcomes
        comparison = self._compare_outcomes(alex_result, jordan_result)
        
        return {
            "setup": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "available_to_save": monthly_savings,
                "duration_months": duration_months
            },
            "alex": self._format_result(alex_result),
            "jordan": self._format_result(jordan_result),
            "comparison": comparison,
            "emergencies": [
                {
                    "month": e.month,
                    "type": e.type.value,
                    "cost": e.cost,
                    "description": e.description,
                    "severity": e.severity
                }
                for e in emergencies
            ],
            "lesson": (
                f"Alex saved ${alex_result.total_saved:,.0f} and had ${alex_result.final_net_worth:,.0f} at the end. "
                f"Jordan went ${jordan_result.total_debt_incurred:,.0f} into debt and paid ${jordan_result.total_interest_paid:,.0f} in interest. "
                f"Emergency fund prevented a ${alex_result.final_net_worth - jordan_result.final_net_worth:,.0f} swing in net worth!"
            )
        }
    
    def _generate_emergencies(self, duration_months: int) -> List[Emergency]:
        """Generate random emergencies over the simulation period"""
        
        emergencies = []
        
        for month in range(1, duration_months + 1):
            # Check each emergency type
            for emergency_type, config in self.emergency_templates.items():
                if self.random.random() < config["probability"]:
                    # Emergency occurs!
                    cost = self.random.uniform(*config["cost_range"])
                    description = self.random.choice(config["descriptions"])
                    
                    # Determine severity
                    if cost < 500:
                        severity = "minor"
                    elif cost < 1000:
                        severity = "moderate"
                    else:
                        severity = "major"
                    
                    emergencies.append(Emergency(
                        month=month,
                        type=emergency_type,
                        cost=cost,
                        description=description,
                        severity=severity
                    ))
        
        # Ensure at least one major emergency for demonstration
        if not any(e.severity == "major" for e in emergencies):
            major_month = self.random.randint(6, duration_months - 2)
            emergencies.append(Emergency(
                month=major_month,
                type=EmergencyType.CAR_REPAIR,
                cost=1200,
                description="Major car repair needed",
                severity="major"
            ))
        
        return sorted(emergencies, key=lambda e: e.month)
    
    def _simulate_character(
        self,
        name: str,
        strategy: str,
        monthly_income: float,
        monthly_expenses: float,
        monthly_savings: float,
        emergencies: List[Emergency]
    ) -> SimulationResult:
        """Simulate one character's journey"""
        
        emergency_fund = 0.0
        credit_card_debt = 0.0
        total_interest_paid = 0.0
        monthly_states = []
        stress_levels = []
        
        emergencies_this_month = {e.month: e for e in emergencies}
        
        for month in range(1, 13):
            # Regular monthly cycle
            emergency_fund += monthly_savings
            
            # Check for emergencies this month
            if month in emergencies_this_month:
                emergency = emergencies_this_month[month]
                
                if emergency_fund >= emergency.cost:
                    # Can pay from emergency fund
                    emergency_fund -= emergency.cost
                    stress_level = 3  # Low stress - handled easily
                    can_handle = True
                else:
                    # Must use credit card
                    deficit = emergency.cost - emergency_fund
                    emergency_fund = 0  # Depleted fund
                    credit_card_debt += deficit
                    stress_level = 8  # High stress
                    can_handle = False
            else:
                stress_level = 2 if emergency_fund > 1000 else 5
                can_handle = True
            
            # Pay credit card interest if in debt
            if credit_card_debt > 0:
                interest = credit_card_debt * self.monthly_interest_rate
                credit_card_debt += interest
                total_interest_paid += interest
                stress_level = min(10, stress_level + 2)
                
                # Try to pay down debt
                available_for_debt = max(0, monthly_savings)
                payment = min(credit_card_debt, available_for_debt)
                credit_card_debt -= payment
            
            stress_levels.append(stress_level)
            
            monthly_states.append(CharacterState(
                month=month,
                income=monthly_income,
                expenses=monthly_expenses,
                emergency_fund=emergency_fund,
                credit_card_debt=credit_card_debt,
                stress_level=stress_level,
                can_handle_emergency=can_handle
            ))
        
        final_net_worth = emergency_fund - credit_card_debt
        average_stress = sum(stress_levels) / len(stress_levels)
        
        # Calculate success score (0-100)
        success_score = 100
        success_score -= min(50, credit_card_debt / 50)  # Penalty for debt
        success_score -= min(30, total_interest_paid / 10)  # Penalty for interest
        success_score += min(20, emergency_fund / 100)  # Bonus for savings
        
        return SimulationResult(
            character_name=name,
            strategy=strategy,
            monthly_states=monthly_states,
            emergencies_faced=emergencies,
            total_saved=emergency_fund,
            total_debt_incurred=max(0, -final_net_worth) if final_net_worth < 0 else 0,
            total_interest_paid=total_interest_paid,
            final_net_worth=final_net_worth,
            average_stress=average_stress,
            success_score=int(max(0, min(100, success_score)))
        )
    
    def _format_result(self, result: SimulationResult) -> Dict[str, Any]:
        """Format simulation result for output"""
        
        return {
            "name": result.character_name,
            "strategy": result.strategy,
            "final_emergency_fund": result.total_saved,
            "final_debt": result.total_debt_incurred,
            "interest_paid": result.total_interest_paid,
            "final_net_worth": result.final_net_worth,
            "average_stress": result.average_stress,
            "success_score": result.success_score,
            "monthly_timeline": [
                {
                    "month": state.month,
                    "emergency_fund": state.emergency_fund,
                    "credit_card_debt": state.credit_card_debt,
                    "net_worth": state.emergency_fund - state.credit_card_debt,
                    "stress_level": state.stress_level
                }
                for state in result.monthly_states
            ]
        }
    
    def _compare_outcomes(
        self,
        alex: SimulationResult,
        jordan: SimulationResult
    ) -> Dict[str, Any]:
        """Compare outcomes between two characters"""
        
        net_worth_difference = alex.final_net_worth - jordan.final_net_worth
        stress_difference = jordan.average_stress - alex.average_stress
        
        return {
            "net_worth_difference": net_worth_difference,
            "alex_advantage": net_worth_difference,
            "stress_difference": stress_difference,
            "alex_had_lower_stress": stress_difference > 0,
            "interest_saved": jordan.total_interest_paid - alex.total_interest_paid,
            "winner": "Alex" if alex.success_score > jordan.success_score else "Jordan",
            "key_insights": [
                f"Alex ended with ${alex.final_net_worth:,.0f} vs Jordan's ${jordan.final_net_worth:,.0f}",
                f"Jordan paid ${jordan.total_interest_paid:,.0f} in credit card interest, Alex paid ${alex.total_interest_paid:,.0f}",
                f"Alex's average stress: {alex.average_stress:.1f}/10, Jordan's: {jordan.average_stress:.1f}/10",
                f"Emergency fund prevented ${net_worth_difference:,.0f} loss"
            ],
            "recommendation": (
                "Emergency funds prevent debt spirals. "
                "Even saving $500/month creates a safety net that avoids "
                "high-interest debt and reduces financial stress significantly."
            )
        }
    
    def calculate_emergency_fund_target(
        self,
        monthly_expenses: float,
        employment_stability: str = "stable",
        dependents: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate recommended emergency fund size
        
        Args:
            monthly_expenses: Fixed monthly expenses
            employment_stability: 'stable', 'variable', 'unstable'
            dependents: Number of dependents
            
        Returns:
            Emergency fund recommendations
        """
        
        # Base recommendation: 3-6 months of expenses
        if employment_stability == "stable":
            min_months = 3
            target_months = 6
        elif employment_stability == "variable":
            min_months = 6
            target_months = 9
        else:  # unstable
            min_months = 9
            target_months = 12
        
        # Adjust for dependents
        target_months += dependents * 1
        
        min_fund = monthly_expenses * min_months
        target_fund = monthly_expenses * target_months
        
        # Milestone approach
        milestones = [
            {
                "amount": 1000,
                "description": "Starter emergency fund",
                "covers": "Most minor emergencies (car repair, appliance)"
            },
            {
                "amount": monthly_expenses * 1,
                "description": "1 month of expenses",
                "covers": "One major emergency or short job gap"
            },
            {
                "amount": monthly_expenses * 3,
                "description": "3 months of expenses (minimum)",
                "covers": "Multiple emergencies or job search period"
            },
            {
                "amount": monthly_expenses * 6,
                "description": "6 months of expenses (ideal)",
                "covers": "Extended job loss or major life event"
            }
        ]
        
        return {
            "recommended_minimum": min_fund,
            "recommended_target": target_fund,
            "months_minimum": min_months,
            "months_target": target_months,
            "milestones": milestones,
            "priority": (
                "HIGH" if employment_stability == "unstable" or dependents > 0
                else "MEDIUM"
            ),
            "strategy": (
                f"Start with $1,000 starter fund, then build to ${min_fund:,.0f} "
                f"({min_months} months of expenses), and eventually ${target_fund:,.0f} "
                f"({target_months} months of expenses)."
            )
        }
    
    def simulate_job_loss_scenario(
        self,
        monthly_expenses: float,
        emergency_fund_amount: float,
        job_search_duration_months: int = 4
    ) -> Dict[str, Any]:
        """
        Simulate job loss with/without emergency fund
        
        Args:
            monthly_expenses: Monthly expenses
            emergency_fund_amount: Current emergency fund
            job_search_duration_months: Expected job search time
            
        Returns:
            Scenario analysis
        """
        
        total_needed = monthly_expenses * job_search_duration_months
        
        if emergency_fund_amount >= total_needed:
            outcome = "covered"
            shortfall = 0
            stress_level = "low"
            message = (
                f"Your ${emergency_fund_amount:,.0f} emergency fund fully covers "
                f"{job_search_duration_months} months of expenses (${total_needed:,.0f}). "
                f"You can focus on job search without financial panic."
            )
        elif emergency_fund_amount >= total_needed * 0.5:
            outcome = "partial"
            shortfall = total_needed - emergency_fund_amount
            stress_level = "medium"
            message = (
                f"Your ${emergency_fund_amount:,.0f} covers {emergency_fund_amount/monthly_expenses:.1f} months. "
                f"You'd need ${shortfall:,.0f} more from credit cards or family. "
                f"Some stress, but manageable."
            )
        else:
            outcome = "insufficient"
            shortfall = total_needed - emergency_fund_amount
            stress_level = "high"
            message = (
                f"Your ${emergency_fund_amount:,.0f} only covers {emergency_fund_amount/monthly_expenses:.1f} months. "
                f"You'd face ${shortfall:,.0f} shortfall, likely requiring credit card debt, "
                f"loans from family, or drastic lifestyle cuts. High stress situation."
            )
        
        return {
            "scenario": "Job Loss",
            "duration": job_search_duration_months,
            "total_needed": total_needed,
            "emergency_fund": emergency_fund_amount,
            "shortfall": shortfall,
            "outcome": outcome,
            "stress_level": stress_level,
            "message": message,
            "recommendation": (
                f"Target: ${total_needed:,.0f} ({job_search_duration_months} months) "
                f"for full peace of mind."
            )
        }
