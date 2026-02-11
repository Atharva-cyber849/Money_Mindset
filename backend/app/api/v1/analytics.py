"""
Analytics API Endpoints
AI-powered financial features: classification, simulation, optimization, forecasting
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.analytics import (
    ExpenseClassifier,
    MarketSimulator,
    BudgetOptimizer,
    ForecastingService
)

router = APIRouter()

# Initialize services
expense_classifier = ExpenseClassifier()
market_simulator = MarketSimulator()
budget_optimizer = BudgetOptimizer()
forecasting_service = ForecastingService()


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
