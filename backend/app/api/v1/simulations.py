"""
Simulation API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.security import get_current_active_user
from app.models.database import get_db
from app.models.user import User
from app.schemas.schemas import SimulationRequest, SimulationResponse
from app.services.simulation.monte_carlo import (
    create_simulation,
    ScenarioType,
    MonteCarloEngine,
    SimulationParams
)
from app.services.simulation.coffee_shop_simulator import CoffeeShopSimulator
from app.services.simulation.paycheck_game import PaycheckGameSimulator, MonthlyExpenses, PaymentStrategy
from app.services.simulation.budget_builder import BudgetBuilderSimulator, BudgetCategory
from app.services.simulation.emergency_fund import EmergencyFundSimulator
from app.services.gamification import GamificationService

router = APIRouter()


@router.post("/run", response_model=SimulationResponse)
async def run_simulation(
    request: SimulationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run financial simulation"""
    
    try:
        # Create simulation based on type
        scenario_type = ScenarioType(request.scenario_type)
        
        params = {
            "initial": request.initial_amount,
            "monthly": request.monthly_contribution,
            "monthly_contribution": request.monthly_contribution,
            "months": request.time_horizon_months,
            "years": request.time_horizon_months // 12,
            **(request.parameters or {})
        }
        
        # Run simulation
        outcomes = create_simulation(scenario_type, params)
        
        # Generate recommendations based on results
        recommendations = generate_recommendations(scenario_type, outcomes, current_user)
        
        return SimulationResponse(
            scenario_type=request.scenario_type,
            outcomes=outcomes,
            visualizations={
                "chart_type": "line",
                "data_points": outcomes.get("trajectory", [])[:100]  # Limit for performance
            },
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/monte-carlo")
async def run_monte_carlo(
    request: SimulationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Run Monte Carlo simulation"""
    
    params = SimulationParams(
        initial_amount=request.initial_amount,
        monthly_contribution=request.monthly_contribution,
        time_horizon_months=request.time_horizon_months,
        **(request.parameters or {})
    )
    
    engine = MonteCarloEngine(params)
    results = engine.run_simulation()
    
    # Get sample trajectories for visualization
    sample_trajectories = engine.get_sample_trajectories(num_samples=50)
    
    return {
        "statistics": results,
        "sample_trajectories": sample_trajectories[:10],  # First 10 for demo
        "confidence_intervals": {
            "80_percent": [results["percentile_10"], results["percentile_90"]],
            "50_percent": [results["percentile_25"], results["percentile_75"]]
        }
    }


def generate_recommendations(
    scenario_type: ScenarioType,
    outcomes: dict,
    user: User
) -> list:
    """Generate personalized recommendations"""
    
    recommendations = []
    
    if scenario_type == ScenarioType.SAVINGS:
        months = outcomes.get("time_to_goal", 0)
        if months > 0:
            years = months / 12
            recommendations.append(
                f"You'll reach your goal in {years:.1f} years with consistent contributions"
            )
        
        interest = outcomes.get("total_interest", 0)
        if interest > 0:
            recommendations.append(
                f"You'll earn ${interest:,.0f} in interest - that's free money!"
            )
    
    elif scenario_type == ScenarioType.INVESTMENT:
        for strategy, result in outcomes.items():
            roi = result.get("roi_percentage", 0)
            if roi > 100:
                recommendations.append(
                    f"{strategy.replace('_', ' ').title()}: {roi:.0f}% return - your money more than doubles!"
                )
    
    elif scenario_type == ScenarioType.DEBT_PAYOFF:
        recommended = outcomes.get("recommendation", "")
        savings = outcomes.get("savings_with_avalanche", 0)
        if savings > 0:
            recommendations.append(
                f"Use the avalanche method to save ${savings:,.0f} in interest"
            )
    
    return recommendations or ["Keep up the great work! Consistency is key."]


@router.post("/coffee-shop-effect")
async def coffee_shop_effect(
    daily_cost: float,
    days_per_week: int = 5,
    years: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Calculate the coffee shop effect
    
    Shows how small daily expenses compound into big money over time
    """
    try:
        simulator = CoffeeShopSimulator()
        
        # Run calculation
        analysis = simulator.calculate(
            daily_cost=daily_cost,
            days_per_week=days_per_week,
            years=years
        )
        
        # Format response
        return {
            "daily_cost": analysis.daily_cost,
            "days_per_week": analysis.days_per_week,
            "costs": {
                "annual": analysis.annual_cost,
                "five_year": analysis.five_year_cost,
                "ten_year": analysis.ten_year_cost,
                "thirty_year": analysis.thirty_year_cost
            },
            "compound_results": [
                {
                    "year": r.year,
                    "spent_total": r.spent_total,
                    "invested_total": r.invested_total,
                    "opportunity_cost": r.opportunity_cost
                }
                for r in analysis.compound_results
            ],
            "opportunity_examples": [
                {
                    "item": e.item,
                    "cost": e.cost,
                    "years_saved": e.years_saved,
                    "description": e.description
                }
                for e in analysis.opportunity_examples
            ],
            "total_opportunity_cost": analysis.total_opportunity_cost,
            "recommendation": analysis.recommendation
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/coffee-shop-effect/compare")
async def coffee_shop_compare(
    scenarios: list[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user)
):
    """
    Compare multiple coffee shop scenarios
    
    Example scenarios:
    [
        {"name": "Coffee Shop Daily", "daily_cost": 5.50, "days_per_week": 5},
        {"name": "Home Brew", "daily_cost": 0.75, "days_per_week": 5}
    ]
    """
    try:
        simulator = CoffeeShopSimulator()
        comparison = simulator.compare_scenarios(scenarios)
        
        return {
            "scenarios": comparison,
            "winner": min(comparison.items(), key=lambda x: x[1]["opportunity_cost"])[0]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/coffee-shop-effect/complete")
async def complete_coffee_shop(
    user_score: int,
    perfect_score: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark coffee shop simulation as complete and award XP/badges
    
    Args:
        user_score: User's score (0-100)
        perfect_score: Whether user got perfect score
    """
    try:
        # TODO: Load user's gamification stats from database
        # For now, create demo stats
        from app.services.gamification import UserStats, Level
        
        user_stats = UserStats(
            user_id=current_user.id,
            total_xp=0,
            current_level=Level.FINANCIAL_NEWBIE,
            completed_simulations=set(),
            earned_badges=set(),
            earned_achievements=set(),
            current_streak=0,
            longest_streak=0,
            last_activity_date=None,
            perfect_score_simulations=set(),
            ai_questions_asked=0,
            goals_completed=0
        )
        
        # Process completion
        gamification_service = GamificationService()
        update = gamification_service.process_simulation_completion(
            user_stats,
            "coffee_shop_effect",
            perfect_score=perfect_score,
            first_try=True
        )
        
        # TODO: Save updated stats to database
        
        return {
            "xp_earned": {
                "amount": update.xp_earned.total_xp,
                "reason": update.xp_earned.reason
            },
            "level_up": update.level_up,
            "badges_earned": [
                {
                    "id": b.badge.id,
                    "name": b.badge.name,
                    "description": b.badge.description,
                    "rarity": b.badge.rarity.value,
                    "icon": b.badge.icon,
                    "message": b.celebration_message
                }
                for b in update.badges_earned
            ],
            "new_unlocks": update.new_unlocks,
            "streak_info": {
                "current_streak": user_stats.current_streak,
                "longest_streak": user_stats.longest_streak
            },
            "progress": {
                "level": update.updated_snapshot.current_level.value,
                "current_xp": update.updated_snapshot.current_xp,
                "xp_to_next_level": update.updated_snapshot.xp_to_next_level,
                "progress_percentage": update.updated_snapshot.progress_percentage
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paycheck-game/calculate")
async def paycheck_game_calculate(
    monthly_income: float,
    rent: float,
    utilities: float,
    groceries: float,
    insurance: float,
    transportation: float,
    debt_payments: float,
    strategy: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Simulate paycheck allocation strategy
    
    Args:
        monthly_income: Monthly gross income
        rent, utilities, groceries, insurance, transportation, debt_payments: Monthly expenses
        strategy: 'spend_first', 'bills_first', or 'save_first'
    """
    try:
        simulator = PaycheckGameSimulator()
        
        expenses = MonthlyExpenses(
            rent=rent,
            utilities=utilities,
            groceries=groceries,
            insurance=insurance,
            transportation=transportation,
            debt_payments=debt_payments
        )
        
        result = simulator.simulate_month(
            monthly_income=monthly_income,
            expenses=expenses,
            strategy=PaymentStrategy(strategy)
        )
        
        return {
            "strategy": result.strategy.value,
            "amount_saved": result.amount_saved,
            "bills_paid_on_time": result.bills_paid_on_time,
            "discretionary_spent": result.discretionary_spent,
            "late_fees": result.late_fees,
            "stress_level": result.stress_level,
            "final_balance": result.final_balance,
            "description": result.description,
            "monthly_breakdown": result.monthly_breakdown
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/paycheck-game/complete")
async def complete_paycheck_game(
    user_score: int,
    perfect_score: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark paycheck game as complete and award XP/badges"""
    return await _complete_simulation(
        "paycheck_game",
        user_score,
        perfect_score,
        current_user,
        db
    )


@router.post("/budget-builder/validate")
async def budget_builder_validate(
    monthly_income: float,
    allocations: Dict[str, float],
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate budget allocations against 50/30/20 rule
    
    Args:
        monthly_income: Monthly income
        allocations: Dict of category -> amount
    """
    try:
        simulator = BudgetBuilderSimulator()
        
        # Convert allocations to CategoryAllocation objects
        from app.services.simulation.budget_builder import CategoryAllocation
        
        category_allocations = []
        for category_name, amount in allocations.items():
            try:
                category = BudgetCategory(category_name)
                category_allocations.append(
                    CategoryAllocation(
                        category=category,
                        amount=amount,
                        percentage=(amount / monthly_income) * 100
                    )
                )
            except ValueError:
                continue
        
        validation = simulator.validate_budget(monthly_income, category_allocations)
        
        return {
            "is_balanced": validation.is_balanced,
            "needs_percentage": validation.needs_percentage,
            "wants_percentage": validation.wants_percentage,
            "savings_percentage": validation.savings_percentage,
            "total_allocated": validation.total_allocated,
            "warnings": validation.warnings,
            "recommendations": validation.recommendations,
            "score": validation.score
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/budget-builder/complete")
async def complete_budget_builder(
    user_score: int,
    perfect_score: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark budget builder as complete and award XP/badges"""
    return await _complete_simulation(
        "budget_builder",
        user_score,
        perfect_score,
        current_user,
        db
    )


@router.post("/emergency-fund/simulate")
async def emergency_fund_simulate(
    monthly_income: float,
    monthly_expenses: float,
    starting_fund: float = 0,
    seed: int = 42,
    current_user: User = Depends(get_current_active_user)
):
    """
    Simulate emergency fund scenario over 12 months
    
    Args:
        monthly_income: Monthly income
        monthly_expenses: Monthly expenses
        starting_fund: Initial emergency fund balance
        seed: Random seed for reproducible results
    """
    try:
        simulator = EmergencyFundSimulator(seed=seed)
        
        # Simulate character with emergency fund
        result_with_fund = simulator.run_simulation(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            starting_emergency_fund=starting_fund,
            months=12
        )
        
        # Simulate character without emergency fund
        result_without_fund = simulator.run_simulation(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            starting_emergency_fund=0,
            months=12
        )
        
        return {
            "with_fund": {
                "character_name": result_with_fund.character_name,
                "total_saved": result_with_fund.total_saved,
                "total_debt_incurred": result_with_fund.total_debt_incurred,
                "total_interest_paid": result_with_fund.total_interest_paid,
                "final_net_worth": result_with_fund.final_net_worth,
                "average_stress": result_with_fund.average_stress,
                "success_score": result_with_fund.success_score,
                "emergencies_faced": len(result_with_fund.emergencies_faced),
                "monthly_states": [
                    {
                        "month": s.month,
                        "emergency_fund": s.emergency_fund,
                        "credit_card_debt": s.credit_card_debt,
                        "stress_level": s.stress_level
                    }
                    for s in result_with_fund.monthly_states
                ]
            },
            "without_fund": {
                "character_name": result_without_fund.character_name,
                "total_saved": result_without_fund.total_saved,
                "total_debt_incurred": result_without_fund.total_debt_incurred,
                "total_interest_paid": result_without_fund.total_interest_paid,
                "final_net_worth": result_without_fund.final_net_worth,
                "average_stress": result_without_fund.average_stress,
                "success_score": result_without_fund.success_score,
                "emergencies_faced": len(result_without_fund.emergencies_faced),
                "monthly_states": [
                    {
                        "month": s.month,
                        "emergency_fund": s.emergency_fund,
                        "credit_card_debt": s.credit_card_debt,
                        "stress_level": s.stress_level
                    }
                    for s in result_without_fund.monthly_states
                ]
            },
            "difference": {
                "net_worth": result_with_fund.final_net_worth - result_without_fund.final_net_worth,
                "stress": result_with_fund.average_stress - result_without_fund.average_stress,
                "debt": result_without_fund.total_debt_incurred - result_with_fund.total_debt_incurred
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/emergency-fund/complete")
async def complete_emergency_fund(
    user_score: int,
    perfect_score: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark emergency fund as complete and award XP/badges"""
    return await _complete_simulation(
        "emergency_fund",
        user_score,
        perfect_score,
        current_user,
        db
    )


@router.post("/car-payment/calculate")
async def car_payment_calculate(
    car_price: float,
    down_payment: float,
    interest_rate: float,
    term_months: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate true cost of car loan including all ownership costs
    
    Args:
        car_price: Vehicle sticker price
        down_payment: Down payment amount
        interest_rate: Annual interest rate (APR)
        term_months: Loan term in months
    """
    try:
        loan_amount = car_price - down_payment
        monthly_rate = (interest_rate / 100) / 12
        
        # Monthly payment calculation
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term_months) / \
                            ((1 + monthly_rate) ** term_months - 1)
        else:
            monthly_payment = loan_amount / term_months
        
        total_paid = monthly_payment * term_months + down_payment
        total_interest = total_paid - car_price
        
        # Additional ownership costs
        years = term_months / 12
        insurance = 150 * term_months  # $150/month
        maintenance = 100 * term_months  # $100/month
        gas = 150 * term_months  # $150/month
        registration = 200 * years  # $200/year
        
        total_ownership_cost = total_paid + insurance + maintenance + gas + registration
        
        # Depreciation (cars lose 60% in 5 years)
        depreciation_rate = 0.60
        final_car_value = car_price * (1 - depreciation_rate * min(years / 5, 1))
        
        # Opportunity cost - if invested instead
        monthly_investment = monthly_payment + 400  # payment + insurance + maintenance + gas
        investment_return = 0.08
        future_value = monthly_investment * (((1 + investment_return / 12) ** term_months - 1) / (investment_return / 12))
        
        return {
            "loan_details": {
                "car_price": car_price,
                "down_payment": down_payment,
                "loan_amount": loan_amount,
                "interest_rate": interest_rate,
                "term_months": term_months,
                "monthly_payment": monthly_payment
            },
            "costs": {
                "total_paid": total_paid,
                "total_interest": total_interest,
                "insurance": insurance,
                "maintenance": maintenance,
                "gas": gas,
                "registration": registration,
                "total_ownership_cost": total_ownership_cost
            },
            "value": {
                "initial_value": car_price,
                "final_value": final_car_value,
                "depreciation": car_price - final_car_value
            },
            "opportunity_cost": {
                "if_invested": future_value,
                "lost_wealth": future_value - car_price
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/car-payment/complete")
async def complete_car_payment(
    user_score: int,
    perfect_score: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark car payment as complete and award XP/badges"""
    return await _complete_simulation(
        "car_payment",
        user_score,
        perfect_score,
        current_user,
        db
    )


@router.post("/credit-card-debt/calculate")
async def credit_card_calculate(
    balance: float,
    apr: float,
    monthly_payment: float,
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate credit card payoff timeline and total interest
    
    Args:
        balance: Current credit card balance
        apr: Annual percentage rate
        monthly_payment: Planned monthly payment
    """
    try:
        monthly_rate = (apr / 100) / 12
        
        # Calculate payoff
        remaining_balance = balance
        total_paid = 0
        months = 0
        monthly_breakdown = []
        
        while remaining_balance > 0 and months < 600:  # Cap at 50 years
            interest_charge = remaining_balance * monthly_rate
            principal_payment = min(monthly_payment - interest_charge, remaining_balance)
            
            if principal_payment <= 0:
                return {
                    "error": "Monthly payment is too low - you'll never pay off the debt!",
                    "minimum_payment_needed": remaining_balance * monthly_rate + 10
                }
            
            remaining_balance -= principal_payment
            total_paid += monthly_payment
            months += 1
            
            if months <= 12 or months % 6 == 0:  # First year monthly, then every 6 months
                monthly_breakdown.append({
                    "month": months,
                    "balance": remaining_balance,
                    "interest_paid": interest_charge,
                    "principal_paid": principal_payment
                })
        
        total_interest = total_paid - balance
        
        return {
            "initial_balance": balance,
            "apr": apr,
            "monthly_payment": monthly_payment,
            "months_to_payoff": months,
            "years_to_payoff": months / 12,
            "total_paid": total_paid,
            "total_interest": total_interest,
            "interest_as_percentage": (total_interest / balance) * 100,
            "monthly_breakdown": monthly_breakdown
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/credit-card-debt/complete")
async def complete_credit_card(
    user_score: int,
    perfect_score: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark credit card debt as complete and award XP/badges"""
    return await _complete_simulation(
        "credit_card_debt",
        user_score,
        perfect_score,
        current_user,
        db
    )


async def _complete_simulation(
    simulation_id: str,
    user_score: int,
    perfect_score: bool,
    current_user: User,
    db: Session
):
    """
    Helper function to complete any simulation
    
    Args:
        simulation_id: ID of the simulation
        user_score: User's score (0-100)
        perfect_score: Whether user got perfect score
        current_user: Current user
        db: Database session
    """
    try:
        # TODO: Load user's gamification stats from database
        from app.services.gamification import UserStats, Level
        
        user_stats = UserStats(
            user_id=current_user.id,
            total_xp=0,
            current_level=Level.FINANCIAL_NEWBIE,
            completed_simulations=set(),
            earned_badges=set(),
            earned_achievements=set(),
            current_streak=0,
            longest_streak=0,
            last_activity_date=None,
            perfect_score_simulations=set(),
            ai_questions_asked=0,
            goals_completed=0
        )
        
        # Process completion
        gamification_service = GamificationService()
        update = gamification_service.process_simulation_completion(
            user_stats,
            simulation_id,
            perfect_score=perfect_score,
            first_try=True
        )
        
        # TODO: Save updated stats to database
        
        return {
            "xp_earned": {
                "amount": update.xp_earned.total_xp,
                "reason": update.xp_earned.reason
            },
            "level_up": update.level_up,
            "badges_earned": [
                {
                    "id": b.badge.id,
                    "name": b.badge.name,
                    "description": b.badge.description,
                    "rarity": b.badge.rarity.value,
                    "icon": b.badge.icon,
                    "message": b.celebration_message
                }
                for b in update.badges_earned
            ],
            "new_unlocks": update.new_unlocks,
            "streak_info": {
                "current_streak": user_stats.current_streak,
                "longest_streak": user_stats.longest_streak
            },
            "progress": {
                "level": update.updated_snapshot.current_level.value,
                "current_xp": update.updated_snapshot.current_xp,
                "xp_to_next_level": update.updated_snapshot.xp_to_next_level,
                "progress_percentage": update.updated_snapshot.progress_percentage
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
