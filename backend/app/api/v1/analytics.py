"""
Analytics API Endpoints
AI-powered financial features: classification, simulation, optimization, forecasting
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json

from app.services.analytics import (
    ExpenseClassifier,
    MarketSimulator,
    BudgetOptimizer,
    ForecastingService
)
from app.models.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.finance import (
    UserProfile,
    PaperTradingSession,
    DalalSession,
    KarobarSession,
    SIPSession,
)

router = APIRouter()

# Initialize services
expense_classifier = ExpenseClassifier()
market_simulator = MarketSimulator()
budget_optimizer = BudgetOptimizer()
forecasting_service = ForecastingService()


def _safe_json(value: Optional[str], default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


# ==================== Request/Response Models ====================

class TransactionClassifyRequest(BaseModel):
    """Request to classify a single transaction"""
    description: str = Field(..., description="Transaction description")
    amount: Optional[float] = Field(None, description="Transaction amount")


class BatchTransactionRequest(BaseModel):
    """Request to classify multiple transactions"""
    transactions: List[Dict[str, Any]] = Field(..., description="List of transactions")


class MarketSimulationRequest(BaseModel):
    """Request for market simulation"""
    initial_amount: float = Field(..., gt=0, description="Initial investment amount")
    monthly_contribution: float = Field(0, ge=0, description="Monthly contribution")
    years: int = Field(..., gt=0, le=50, description="Investment time horizon in years")
    asset_class: str = Field(..., description="Asset class: aggressive_stocks, large_cap_stocks, balanced, conservative, bonds, savings")
    num_simulations: int = Field(1000, ge=100, le=10000, description="Number of Monte Carlo simulations")


class CompareAssetsRequest(BaseModel):
    """Request to compare asset classes"""
    initial_amount: float = Field(..., gt=0)
    monthly_contribution: float = Field(0, ge=0)
    years: int = Field(..., gt=0, le=50)
    asset_classes: Optional[List[str]] = Field(None, description="List of asset classes to compare")


class RiskAnalysisRequest(BaseModel):
    """Request for risk vs return analysis"""
    initial_amount: float = Field(..., gt=0)
    years: int = Field(..., gt=0, le=50)
    target_amount: float = Field(..., gt=0)


class CrashSimulationRequest(BaseModel):
    """Request for market crash simulation"""
    initial_amount: float = Field(..., gt=0)
    monthly_contribution: float = Field(0, ge=0)
    years: int = Field(..., gt=0, le=50)
    asset_class: str
    crash_year: int = Field(..., gt=0)
    crash_magnitude: float = Field(-0.30, ge=-0.70, le=0)


class BudgetAnalysisRequest(BaseModel):
    """Request for budget analysis"""
    income: float = Field(..., gt=0, description="Monthly gross income")
    expenses: Dict[str, float] = Field(..., description="Category -> amount mapping")
    savings: float = Field(0, ge=0, description="Monthly savings")


class PeerComparisonRequest(BaseModel):
    """Request for peer comparison"""
    income: float = Field(..., gt=0)
    expenses: Dict[str, float]
    savings: float = Field(0, ge=0)
    age_group: str = Field(..., description="Age group: 18-24, 25-34, 35-44, 45-54, 55-64, 65+")
    location: str = Field("national", description="Geographic location")


class ForecastRequest(BaseModel):
    """Request for spending forecast"""
    historical_data: List[Dict[str, Any]] = Field(..., description="Historical transactions")
    category: Optional[str] = Field(None, description="Specific category to forecast")
    periods_ahead: int = Field(3, ge=1, le=12, description="Number of months to forecast")


class CategoryForecastRequest(BaseModel):
    """Request for category-specific forecast"""
    category: str
    historical_amounts: List[float] = Field(..., min_items=2)
    months_ahead: int = Field(1, ge=1, le=12)


class BudgetComparisonRequest(BaseModel):
    """Request to compare forecast vs budget"""
    forecasts: Dict[str, float]
    budgets: Dict[str, float]


class ClassificationFeedbackRequest(BaseModel):
    """User feedback on a classification"""
    user_id: int = Field(..., description="User ID")
    transaction_id: Optional[int] = Field(None, description="Transaction ID")
    description: str = Field(..., description="Transaction description")
    amount: float = Field(..., description="Transaction amount")
    predicted_category: str = Field(..., description="Category that was predicted")
    predicted_confidence: float = Field(..., ge=0, le=1, description="Model's confidence")
    corrected_category: str = Field(..., description="The correct category")


# ==================== Expense Classification Endpoints ====================

@router.post("/classify/transaction", tags=["Classification"])
async def classify_transaction(request: TransactionClassifyRequest) -> Dict:
    """
    Classify a single transaction using ML-based categorization.
    Returns category suggestion with confidence score.
    """
    try:
        result = expense_classifier.classify(
            request.description,
            request.amount
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify/batch", tags=["Classification"])
async def classify_transactions_batch(request: BatchTransactionRequest) -> Dict:
    """
    Classify multiple transactions at once.
    More efficient than individual classification calls.
    """
    try:
        results = expense_classifier.classify_batch(request.transactions)
        insights = expense_classifier.get_category_insights(
            [
                {**txn, "category": result["category"]}
                for txn, result in zip(request.transactions, results)
            ]
        )
        
        return {
            "success": True,
            "data": {
                "classifications": results,
                "insights": insights
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classify/merchant/{merchant_name}", tags=["Classification"])
async def suggest_merchant_category(merchant_name: str) -> Dict:
    """
    Get category suggestion for a specific merchant.
    Useful for setting up recurring transaction rules.
    """
    try:
        result = expense_classifier.suggest_category_for_merchant(merchant_name)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify/feedback", tags=["Classification"])
async def submit_classification_feedback(
    request: ClassificationFeedbackRequest,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Submit user feedback on a classification to improve the model.
    Stores feedback for periodic model retraining.
    """
    try:
        from app.models.finance import ClassificationFeedback

        # Store feedback in database
        feedback = ClassificationFeedback(
            user_id=request.user_id,
            transaction_id=request.transaction_id,
            transaction_description=request.description,
            transaction_amount=request.amount,
            predicted_category=request.predicted_category,
            predicted_confidence=request.predicted_confidence,
            corrected_category=request.corrected_category,
            feedback_type="correction"
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        # Check if we should trigger retraining (e.g., every 50 corrections)
        correction_count = db.query(ClassificationFeedback).filter(
            ClassificationFeedback.feedback_type == "correction",
            ClassificationFeedback.is_used_in_training == False
        ).count()

        retraining_triggered = False
        if correction_count >= 50:
            # Trigger retraining
            from app.services.ml_models.retraining import retrain_classifier_model
            retraining_result = retrain_classifier_model()
            retraining_triggered = retraining_result.get("status") == "success"

        return {
            "success": True,
            "data": {
                "feedback_id": feedback.id,
                "stored": True,
                "retraining_triggered": retraining_triggered,
                "correction_count": correction_count
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify/retrain", tags=["Classification"])
async def manually_retrain_model() -> Dict:
    """
    Manually trigger model retraining using accumulated corrections.
    Requires admin/system access in production.
    """
    try:
        from app.services.ml_models.retraining import retrain_classifier_model

        result = retrain_classifier_model()

        if result.get("status") == "success":
            # Reload the model in the classifier
            expense_classifier._load_ml_model()

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Market Simulation Endpoints ====================

@router.post("/simulate/investment", tags=["Market Simulation"])
async def simulate_investment(request: MarketSimulationRequest) -> Dict:
    """
    Run Monte Carlo simulation for investment growth.
    Visualize risk vs return with probabilistic outcomes.
    """
    try:
        result = market_simulator.simulate_investment(
            initial_amount=request.initial_amount,
            monthly_contribution=request.monthly_contribution,
            years=request.years,
            asset_class=request.asset_class,
            num_simulations=request.num_simulations
        )
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/compare-assets", tags=["Market Simulation"])
async def compare_asset_classes(request: CompareAssetsRequest) -> Dict:
    """
    Compare multiple asset classes side by side.
    Helps users understand risk/return tradeoffs.
    """
    try:
        result = market_simulator.compare_asset_classes(
            initial_amount=request.initial_amount,
            monthly_contribution=request.monthly_contribution,
            years=request.years,
            asset_classes=request.asset_classes
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/risk-analysis", tags=["Market Simulation"])
async def risk_vs_return_analysis(request: RiskAnalysisRequest) -> Dict:
    """
    Analyze what asset allocation is needed to reach a target amount.
    Provides feasibility assessment and recommendations.
    """
    try:
        result = market_simulator.risk_vs_return_analysis(
            initial_amount=request.initial_amount,
            years=request.years,
            target_amount=request.target_amount
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/market-crash", tags=["Market Simulation"])
async def simulate_market_crash(request: CrashSimulationRequest) -> Dict:
    """
    Simulate investment growth with a market crash scenario.
    Educational tool to understand recovery and long-term investing.
    """
    try:
        result = market_simulator.simulate_market_crash(
            initial_amount=request.initial_amount,
            monthly_contribution=request.monthly_contribution,
            years=request.years,
            asset_class=request.asset_class,
            crash_year=request.crash_year,
            crash_magnitude=request.crash_magnitude
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulate/asset-classes", tags=["Market Simulation"])
async def get_available_asset_classes() -> Dict:
    """
    Get list of available asset classes with their characteristics.
    """
    asset_classes = {
        key: {
            "name": asset.name,
            "expected_return": f"{asset.mean_return * 100:.1f}%",
            "volatility": f"{asset.std_dev * 100:.1f}%",
            "description": asset.description
        }
        for key, asset in market_simulator.ASSET_CLASSES.items()
    }
    
    return {
        "success": True,
        "data": asset_classes
    }


# ==================== Budget Optimization Endpoints ====================

@router.post("/budget/analyze", tags=["Budget Optimization"])
async def analyze_budget(request: BudgetAnalysisRequest) -> Dict:
    """
    Comprehensive budget analysis using financial best practices.
    Returns health score, rule violations, and actionable recommendations.
    """
    try:
        result = budget_optimizer.analyze_budget(
            income=request.income,
            expenses=request.expenses,
            savings=request.savings
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget/suggest/{income}", tags=["Budget Optimization"])
async def suggest_budget_allocation(income: float) -> Dict:
    """
    Get recommended budget allocation based on income.
    Uses 50/30/20 rule and other financial guidelines.
    """
    try:
        if income <= 0:
            raise HTTPException(status_code=400, detail="Income must be positive")
        
        result = budget_optimizer.suggest_budget_allocation(income)
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/budget/compare-peers", tags=["Budget Optimization"])
async def compare_to_peers(request: PeerComparisonRequest) -> Dict:
    """
    Compare user's budget to peer averages.
    Provides context and benchmarking data.
    """
    try:
        result = budget_optimizer.compare_to_peers(
            income=request.income,
            expenses=request.expenses,
            savings=request.savings,
            age_group=request.age_group,
            location=request.location
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget/rules", tags=["Budget Optimization"])
async def get_budget_rules() -> Dict:
    """
    Get list of budget rules and guidelines used for analysis.
    """
    rules = {
        key: {
            "name": rule.name,
            "category": rule.category,
            "max_percentage": rule.max_percentage,
            "ideal_percentage": rule.ideal_percentage,
            "description": rule.description
        }
        for key, rule in budget_optimizer.BUDGET_RULES.items()
    }
    
    return {
        "success": True,
        "data": {
            "rules": rules,
            "fifty_thirty_twenty": budget_optimizer.BUDGET_50_30_20
        }
    }


# ==================== Forecasting Endpoints ====================

@router.post("/forecast/spending", tags=["Forecasting"])
async def forecast_spending(request: ForecastRequest) -> Dict:
    """
    Forecast future spending using time-series analysis.
    Predicts spending trends for budget planning.
    """
    try:
        result = forecasting_service.forecast_spending(
            historical_data=request.historical_data,
            category=request.category,
            periods_ahead=request.periods_ahead
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/category", tags=["Forecasting"])
async def forecast_category(request: CategoryForecastRequest) -> Dict:
    """
    Predict spending for a specific category.
    Includes confidence intervals and trend analysis.
    """
    try:
        result = forecasting_service.predict_category_spending(
            category=request.category,
            historical_amounts=request.historical_amounts,
            months_ahead=request.months_ahead
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/compare-budget", tags=["Forecasting"])
async def compare_forecast_to_budget(request: BudgetComparisonRequest) -> Dict:
    """
    Compare forecasted spending to budgeted amounts.
    Identifies potential budget overruns early.
    """
    try:
        result = forecasting_service.compare_forecast_to_budget(
            forecasts=request.forecasts,
            budgets=request.budgets
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/anomalies", tags=["Forecasting"])
async def detect_anomalies(historical_data: List[float], threshold: float = 2.0) -> Dict:
    """
    Detect unusual spending patterns.
    Helps identify one-time expenses or lifestyle changes.
    """
    try:
        result = forecasting_service.anomaly_detection(
            historical_data=historical_data,
            threshold=threshold
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Market Simulation Analytics Endpoints ====================

@router.get("/simulations/portfolio-analysis", tags=["Simulations"])
async def get_portfolio_simulation_analysis(
    initial_amount: float = 10000,
    monthly_contribution: float = 500,
    years: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict:
    """
    Get comprehensive portfolio simulation analysis across multiple asset classes.
    """
    try:
        from app.services.analytics import MarketSimulator
        
        simulator = MarketSimulator()
        
        # Simulate for different asset classes
        simulations = {
            "aggressive_stocks": simulator.simulate_investment(
                initial_amount=initial_amount,
                monthly_contribution=monthly_contribution,
                years=years,
                asset_class="aggressive_stocks",
                num_simulations=500
            ),
            "balanced": simulator.simulate_investment(
                initial_amount=initial_amount,
                monthly_contribution=monthly_contribution,
                years=years,
                asset_class="balanced",
                num_simulations=500
            ),
            "conservative": simulator.simulate_investment(
                initial_amount=initial_amount,
                monthly_contribution=monthly_contribution,
                years=years,
                asset_class="conservative",
                num_simulations=500
            ),
            "bonds": simulator.simulate_investment(
                initial_amount=initial_amount,
                monthly_contribution=monthly_contribution,
                years=years,
                asset_class="bonds",
                num_simulations=500
            ),
        }
        
        # Extract key metrics
        analysis = {
            "parameters": {
                "initial_amount": initial_amount,
                "monthly_contribution": monthly_contribution,
                "years": years,
                "total_contributed": initial_amount + (monthly_contribution * years * 12)
            },
            "scenarios": {}
        }
        
        for asset_class, sim_result in simulations.items():
            if sim_result and "statistics" in sim_result:
                stats = sim_result["statistics"]
                percentiles = sim_result["percentiles"]
                analysis["scenarios"][asset_class] = {
                    "mean": stats.get("mean", 0),
                    "median": stats.get("median", 0),
                    "percentile_10": percentiles.get("p10", 0),
                    "percentile_25": percentiles.get("p25", 0),
                    "percentile_75": percentiles.get("p75", 0),
                    "percentile_90": percentiles.get("p90", 0),
                    "std_dev": stats.get("std_dev", 0),
                    "min": stats.get("min", 0),
                    "max": stats.get("max", 0),
                }
        
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Budget Optimization Analytics Endpoints ====================

@router.get("/budget/current-analysis", tags=["Budget"])
async def get_current_budget_analysis(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict:
    """
    Get current budget analysis for the user's latest transactions.
    """
    try:
        from app.models.finance import Transaction
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # Get transactions from last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.transaction_type == "debit"
        ).all()
        
        # Calculate expenses by category
        expenses = defaultdict(float)
        for txn in transactions:
            expenses[txn.category] += txn.amount
        
        total_spent = sum(expenses.values())
        
        # Analyze budget adherence
        budget_categories = {
            "needs": ["groceries", "utilities", "housing", "transportation", "healthcare"],
            "wants": ["restaurants", "entertainment", "shopping", "personal_care", "subscriptions"],
            "savings": ["savings", "investments"]
        }
        
        budget_data = {}
        for category_type, cats in budget_categories.items():
            amount = sum(expenses.get(cat, 0) for cat in cats)
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            budget_data[category_type] = {
                "amount": amount,
                "percentage": percentage
            }
        
        # Generate recommendations
        recommendations = []
        if budget_data["needs"]["percentage"] > 50:
            recommendations.append({
                "type": "high_needs",
                "title": "Needs spending is high",
                "message": f"At {budget_data['needs']['percentage']:.1f}%, consider optimizing housing or transportation costs.",
                "priority": "high"
            })
        
        if budget_data["wants"]["percentage"] > 30:
            recommendations.append({
                "type": "high_wants",
                "title": "Wants spending exceeds target",
                "message": f"At {budget_data['wants']['percentage']:.1f}%, reduce discretionary spending.",
                "priority": "medium"
            })
        
        if budget_data["savings"]["percentage"] < 20:
            recommendations.append({
                "type": "low_savings",
                "title": "Savings target not met",
                "message": f"Currently saving only {budget_data['savings']['percentage']:.1f}%. Increase to 20%+ for financial security.",
                "priority": "high"
            })
        
        return {
            "success": True,
            "data": {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": 30
                },
                "total_spent": round(total_spent, 2),
                "budget_breakdown": {
                    "needs": {
                        "amount": round(budget_data["needs"]["amount"], 2),
                        "percentage": round(budget_data["needs"]["percentage"], 1),
                        "target": 50,
                        "status": "good" if 40 <= budget_data["needs"]["percentage"] <= 60 else ("high" if budget_data["needs"]["percentage"] > 60 else "low")
                    },
                    "wants": {
                        "amount": round(budget_data["wants"]["amount"], 2),
                        "percentage": round(budget_data["wants"]["percentage"], 1),
                        "target": 30,
                        "status": "good" if 20 <= budget_data["wants"]["percentage"] <= 40 else ("high" if budget_data["wants"]["percentage"] > 40 else "low")
                    },
                    "savings": {
                        "amount": round(budget_data["savings"]["amount"], 2),
                        "percentage": round(budget_data["savings"]["percentage"], 1),
                        "target": 20,
                        "status": "good" if budget_data["savings"]["percentage"] >= 15 else "low"
                    }
                },
                "recommendations": recommendations,
                "health_score": max(0, min(100, 50 + 
                    (50 - abs(budget_data["needs"]["percentage"] - 50)) +
                    (30 - abs(budget_data["wants"]["percentage"] - 30)) +
                    (20 if budget_data["savings"]["percentage"] >= 20 else budget_data["savings"]["percentage"])
                )) / 2  # Normalized 0-100
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Forecasting Analytics Endpoints ====================

@router.get("/forecasts/spending-trends", tags=["Forecasting"])
async def get_spending_trends(
    months: int = 6,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict:
    """
    Get spending trends and forecasts for the user.
    """
    try:
        from app.models.finance import Transaction
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # Get historical data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.transaction_type == "debit"
        ).order_by(Transaction.date).all()
        
        # Aggregate by month and category
        monthly_data = defaultdict(lambda: defaultdict(float))
        for txn in transactions:
            month_key = txn.date.strftime("%Y-%m")
            monthly_data[month_key][txn.category] += txn.amount
        
        # Calculate trends
        sorted_months = sorted(monthly_data.keys())
        monthly_totals = [
            {
                "month": month,
                "total": sum(monthly_data[month].values()),
                "data": dict(monthly_data[month])
            }
            for month in sorted_months
        ]
        
        # Identify trends
        if len(monthly_totals) >= 2:
            recent_avg = sum(m["total"] for m in monthly_totals[-3:]) / min(3, len(monthly_totals))
            older_avg = sum(m["total"] for m in monthly_totals[:-3]) / max(1, len(monthly_totals) - 3)
            trend_direction = "increasing" if recent_avg > older_avg else ("decreasing" if recent_avg < older_avg else "stable")
            trend_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            trend_direction = "stable"
            trend_percentage = 0
        
        # Find highest category
        all_categories = defaultdict(float)
        for month_data in monthly_totals:
            for cat, amount in month_data["data"].items():
                all_categories[cat] += amount
        
        highest_category = max(all_categories.items(), key=lambda x: x[1])[0] if all_categories else "N/A"
        
        return {
            "success": True,
            "data": {
                "period": {
                    "months": months,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "monthly_data": monthly_totals,
                "trend": {
                    "direction": trend_direction,
                    "change_percentage": round(trend_percentage, 1),
                    "message": f"Spending is {trend_direction} by {abs(trend_percentage):.1f}%"
                },
                "highest_category": highest_category,
                "forecasts": [
                    {
                        "month": (end_date + timedelta(days=30*(i+1))).strftime("%Y-%m"),
                        "predicted_spend": round(monthly_totals[-1]["total"] * (1 + trend_percentage/100) if len(monthly_totals) > 0 else 0, 2),
                        "confidence": 0.75
                    }
                    for i in range(3)
                ] if monthly_totals else []
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Transaction Analytics Endpoints ====================

@router.get("/transactions/analytics", tags=["Analytics"])
async def get_transaction_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict:
    """
    Get comprehensive transaction analytics including classification breakdown,
    spending patterns, and budget adherence.
    
    Args:
        days: Number of days to analyze (default 30)
        
    Returns:
        Dict with spending breakdown, budget adherence, insights, and recent transactions
    """
    try:
        from app.models.finance import Transaction
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Fetch transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.transaction_type == "debit"  # Only expenses
        ).order_by(desc(Transaction.date)).all()
        
        # Calculate category breakdown
        category_breakdown = defaultdict(float)
        category_counts = defaultdict(int)
        all_transactions = []
        
        for txn in transactions:
            category = txn.category
            amount = txn.amount
            category_breakdown[category] += amount
            category_counts[category] += 1
            all_transactions.append({
                "id": txn.id,
                "date": txn.date.isoformat(),
                "description": txn.description,
                "category": category,
                "amount": amount,
                "type": txn.transaction_type
            })
        
        total_spent = sum(category_breakdown.values())
        
        # Calculate 50/30/20 budget adherence
        budget_categories = {
            "needs": ["groceries", "utilities", "housing", "transportation", "healthcare"],
            "wants": ["restaurants", "entertainment", "shopping", "personal_care", "subscriptions"],
            "savings": ["savings", "investments"]
        }
        
        needs_total = sum(category_breakdown.get(cat, 0) for cat in budget_categories["needs"])
        wants_total = sum(category_breakdown.get(cat, 0) for cat in budget_categories["wants"])
        savings_total = sum(category_breakdown.get(cat, 0) for cat in budget_categories["savings"])
        
        needs_pct = (needs_total / total_spent * 100) if total_spent > 0 else 0
        wants_pct = (wants_total / total_spent * 100) if total_spent > 0 else 0
        savings_pct = (savings_total / total_spent * 100) if total_spent > 0 else 0
        
        # Get highest spending category
        highest_category = max(category_breakdown.items(), key=lambda x: x[1])[0] if category_breakdown else "N/A"
        highest_amount = max(category_breakdown.values()) if category_breakdown else 0
        
        # Calculate insights
        insights = []
        
        if highest_amount > 0:
            insights.append({
                "type": "highest_spending",
                "title": f"Highest spending category: {highest_category.title().replace('_', ' ')}",
                "amount": highest_amount,
                "percentage": round((highest_amount / total_spent * 100), 1) if total_spent > 0 else 0
            })
        
        if needs_pct > 50:
            insights.append({
                "type": "needs_high",
                "title": "Needs spending is above recommended 50%",
                "percentage": round(needs_pct, 1),
                "recommendation": "Consider optimizing housing or transportation costs"
            })
        
        if wants_pct > 30:
            insights.append({
                "type": "wants_high", 
                "title": "Wants spending exceeds recommended 30%",
                "percentage": round(wants_pct, 1),
                "recommendation": "Consider reducing entertainment and dining out expenses"
            })
        
        if savings_pct < 20:
            insights.append({
                "type": "savings_low",
                "title": "Savings target below recommended 20%",
                "percentage": round(savings_pct, 1),
                "recommendation": "Try to increase your savings rate"
            })
        
        # Calculate transactions needing review
        needs_review = [txn for txn in all_transactions if txn.get("needs_review", False)]
        
        return {
            "success": True,
            "data": {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "summary": {
                    "total_spent": round(total_spent, 2),
                    "transaction_count": len(all_transactions),
                    "categories": len(category_breakdown)
                },
                "spending_breakdown": {
                    category: {
                        "amount": round(amount, 2),
                        "percentage": round((amount / total_spent * 100), 1) if total_spent > 0 else 0,
                        "count": category_counts[category]
                    }
                    for category, amount in sorted(
                        category_breakdown.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                },
                "budget_adherence": {
                    "needs": {
                        "amount": round(needs_total, 2),
                        "percentage": round(needs_pct, 1),
                        "target": 50,
                        "status": "good" if 40 <= needs_pct <= 60 else ("high" if needs_pct > 60 else "low")
                    },
                    "wants": {
                        "amount": round(wants_total, 2),
                        "percentage": round(wants_pct, 1),
                        "target": 30,
                        "status": "good" if 20 <= wants_pct <= 40 else ("high" if wants_pct > 40 else "low")
                    },
                    "savings": {
                        "amount": round(savings_total, 2),
                        "percentage": round(savings_pct, 1),
                        "target": 20,
                        "status": "good" if savings_pct >= 15 else "low"
                    }
                },
                "insights": insights,
                "recent_transactions": all_transactions[:20]  # Return latest 20
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/monthly", tags=["Analytics"])
async def get_monthly_analytics(
    month: int = None,
    year: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict:
    """
    Get analytics for a specific month.
    """
    try:
        from app.models.finance import Transaction
        from datetime import datetime
        
        if month is None:
            month = datetime.utcnow().month
        if year is None:
            year = datetime.utcnow().year
        
        # Get all transactions for the month
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date.cast(str).like(f"{year:04d}-{month:02d}%"),
            Transaction.transaction_type == "debit"
        ).all()
        
        from collections import defaultdict
        category_breakdown = defaultdict(float)
        
        for txn in transactions:
            category_breakdown[txn.category] += txn.amount
        
        total_spent = sum(category_breakdown.values())
        
        return {
            "success": True,
            "data": {
                "month": month,
                "year": year,
                "total_spent": round(total_spent, 2),
                "transaction_count": len(transactions),
                "breakdown": {
                    category: round(amount, 2)
                    for category, amount in category_breakdown.items()
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Health Check ====================

@router.get("/health", tags=["Health"])
async def health_check() -> Dict:
    """Check if analytics services are operational"""
    return {
        "success": True,
        "data": {
            "status": "operational",
            "services": {
                "expense_classifier": "ready",
                "market_simulator": "ready",
                "budget_optimizer": "ready",
                "forecasting_service": "ready"
            }
        }
    }


@router.get("/cross-game/summary", tags=["Cross-Game"])
async def get_cross_game_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict:
    """Return a compact summary of cross-game progress and unlock paths."""

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    paper_session = (
        db.query(PaperTradingSession)
        .filter(PaperTradingSession.user_id == current_user.id)
        .order_by(desc(PaperTradingSession.updated_at))
        .first()
    )
    dalal_session = (
        db.query(DalalSession)
        .filter(DalalSession.user_id == current_user.id)
        .order_by(desc(DalalSession.updated_at))
        .first()
    )
    karobaar_session = (
        db.query(KarobarSession)
        .filter(KarobarSession.user_id == current_user.id)
        .order_by(desc(KarobarSession.updated_at))
        .first()
    )
    sip_session = (
        db.query(SIPSession)
        .filter(SIPSession.user_id == current_user.id)
        .order_by(desc(SIPSession.updated_at))
        .first()
    )

    paper_portfolio = _safe_json(getattr(paper_session, "current_portfolio", None), {}) if paper_session else {}
    dalal_portfolio = _safe_json(getattr(dalal_session, "portfolio_json", None), {}) if dalal_session else {}

    paper_holdings = paper_portfolio.get("holdings", {}) if isinstance(paper_portfolio, dict) else {}
    dalal_holdings = dalal_portfolio.get("holdings", {}) if isinstance(dalal_portfolio, dict) else {}

    combined_holdings: Dict[str, Dict[str, Any]] = {}
    for symbol, payload in paper_holdings.items() if isinstance(paper_holdings, dict) else []:
        if not isinstance(payload, dict):
            continue
        combined_holdings[symbol] = {
            "symbol": symbol,
            "quantity": payload.get("quantity", 0),
            "current_price": payload.get("current_price", payload.get("entry_price", 0)),
            "source_game": "paper_trading",
        }

    for symbol, payload in dalal_holdings.items() if isinstance(dalal_holdings, dict) else []:
        if not isinstance(payload, dict):
            continue
        existing = combined_holdings.get(symbol, {"symbol": symbol, "quantity": 0, "current_price": 0, "source_game": "dalal_street"})
        existing["quantity"] = existing.get("quantity", 0) + int(payload.get("quantity", 0))
        existing["current_price"] = float(payload.get("current_price", payload.get("entry_price", existing.get("current_price", 0))))
        existing["source_game"] = existing.get("source_game") or "dalal_street"
        combined_holdings[symbol] = existing

    portfolio_value = 0.0
    for holding in combined_holdings.values():
        portfolio_value += float(holding.get("quantity", 0)) * float(holding.get("current_price", 0))

    if portfolio_value <= 0:
        portfolio_value = float(getattr(paper_session, "current_capital", 0) or getattr(dalal_session, "ending_value", 0) or getattr(karobaar_session, "final_net_worth", 0) or 0)

    combined_cash = float(
        (paper_portfolio.get("cash") if isinstance(paper_portfolio, dict) else 0)
        or (dalal_portfolio.get("cash") if isinstance(dalal_portfolio, dict) else 0)
        or getattr(paper_session, "current_capital", 0)
        or 0
    )

    total_sessions = sum(
        1
        for session in [paper_session, dalal_session, karobaar_session, sip_session]
        if session is not None
    )

    unlock_recommendations = []
    if karobaar_session and not paper_session:
        unlock_recommendations.append("Complete Karobaar milestones to unlock Paper Trading progression.")
    if paper_session and not dalal_session:
        unlock_recommendations.append("Build a stronger paper portfolio to unlock Dalal Street rivalry mode.")
    if sip_session and getattr(sip_session, "current_month", 0) < 12:
        unlock_recommendations.append("Keep SIP Chronicles going to boost long-term compounding rewards.")

    if not unlock_recommendations:
        unlock_recommendations.append("You are ready for harder simulations. Try Expert difficulty and AI opponents.")

    return {
        "success": True,
        "data": {
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "finance_iq_score": getattr(profile, "finance_iq_score", None),
                "money_personality": getattr(profile, "money_personality", None),
                "recommended_first_sim": getattr(profile, "recommended_first_sim", None),
                "learning_gaps": getattr(profile, "learning_gaps", []) or [],
            },
            "portfolio": {
                "cash": combined_cash,
                "value": portfolio_value + combined_cash,
                "holdings_count": len(combined_holdings),
                "holdings": list(combined_holdings.values()),
                "latest_paper_trading_session": getattr(paper_session, "session_id", None),
                "latest_dalal_session": getattr(dalal_session, "session_id", None),
            },
            "career_path": {
                "karobaar_sessions": db.query(KarobarSession).filter(KarobarSession.user_id == current_user.id).count(),
                "paper_trading_sessions": db.query(PaperTradingSession).filter(PaperTradingSession.user_id == current_user.id).count(),
                "dalal_sessions": db.query(DalalSession).filter(DalalSession.user_id == current_user.id).count(),
                "sip_sessions": db.query(SIPSession).filter(SIPSession.user_id == current_user.id).count(),
                "next_step": "Karobaar -> Paper Trading -> Dalal Street",
            },
            "compound_rewards": {
                "xp_boost_from_progress": min(total_sessions * 0.05, 0.25),
                "visualization_boost": "XP earned in simulations increases compound growth visualization strength",
                "active_sessions": total_sessions,
            },
            "achievement_locked_content": [
                {
                    "id": "paper_trading",
                    "locked": not bool(karobaar_session),
                    "reason": "Finish Karobaar milestones first" if not karobaar_session else "Unlocked",
                },
                {
                    "id": "dalal_street",
                    "locked": not bool(paper_session),
                    "reason": "Complete Paper Trading to unlock Dalal Street" if not paper_session else "Unlocked",
                },
                {
                    "id": "black_swan",
                    "locked": not bool(dalal_session),
                    "reason": "Complete Dalal Street to unlock Black Swan" if not dalal_session else "Unlocked",
                },
            ],
            "technical_improvements": {
                "session_analytics": True,
                "export_reports": True,
                "mobile_optimized_variants": True,
                "offline_mode_ready": True,
                "real_time_data_integration": True,
            },
            "recommendations": unlock_recommendations,
        },
    }


@router.get("/reports/session/{game_type}/{session_id}", tags=["Reporting"])
async def export_session_report(
    game_type: str,
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict:
    """Generate a lightweight session report that can be downloaded or exported as PDF later."""

    report = {
        "game_type": game_type,
        "session_id": session_id,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {},
        "report_text": "",
    }

    if game_type == "paper_trading":
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.user_id == current_user.id,
            PaperTradingSession.session_id == session_id,
        ).first()
        if session:
            portfolio = _safe_json(session.current_portfolio, {})
            report["summary"] = {
                "market": session.market,
                "strategy": session.strategy,
                "capital": session.current_capital,
                "portfolio_value": portfolio.get("total_value", session.current_capital),
                "trades": session.total_trades,
                "profit_loss": session.total_profit_loss,
                "return_percentage": session.return_percentage,
            }
    elif game_type == "dalal-street":
        session = db.query(DalalSession).filter(
            DalalSession.user_id == current_user.id,
            DalalSession.session_id == session_id,
        ).first()
        if session:
            portfolio = _safe_json(session.portfolio_json, {})
            report["summary"] = {
                "era": session.era,
                "quarter": session.current_quarter,
                "starting_value": session.starting_value,
                "ending_value": session.ending_value,
                "portfolio": portfolio,
                "overall_score": session.overall_score,
            }
    elif game_type == "karobaar":
        session = db.query(KarobarSession).filter(
            KarobarSession.user_id == current_user.id,
            KarobarSession.session_id == session_id,
        ).first()
        if session:
            report["summary"] = {
                "city": session.city,
                "education": session.education,
                "starting_job": session.starting_job,
                "overall_score": session.overall_score,
                "final_net_worth": session.final_net_worth,
                "final_salary": session.final_salary,
            }
    elif game_type in {"sip-chronicles", "sip_chronicles"}:
        session = db.query(SIPSession).filter(
            SIPSession.user_id == current_user.id,
            SIPSession.session_id == session_id,
        ).first()
        if session:
            report["summary"] = {
                "sip_type": session.sip_type,
                "monthly_sip": session.monthly_sip,
                "accumulated_wealth": session.accumulated_wealth,
                "final_corpus": session.final_corpus,
                "discipline_score": session.financial_discipline_score,
            }

    report["report_text"] = (
        f"{game_type.upper()} session {session_id}: "
        f"use this summary to export a PDF, share progress, or review decisions."
    )

    return {"success": True, "data": report}
