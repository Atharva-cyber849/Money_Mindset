"""
Forecasting Service
Time-series analysis to predict spending trends
Uses statistical methods and pattern recognition
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class ForecastResult:
    """Result of a forecast prediction"""
    category: str
    predicted_amount: float
    confidence_interval: Tuple[float, float]
    trend: str  # "increasing", "decreasing", "stable"
    seasonality_detected: bool


class ForecastingService:
    """
    Time-series forecasting for spending patterns.
    Uses exponential smoothing and trend analysis.
    """
    
    def __init__(self):
        self.alpha = 0.3  # Smoothing factor for exponential smoothing
        self.beta = 0.1   # Trend smoothing factor
    
    def forecast_spending(
        self,
        historical_data: List[Dict],
        category: Optional[str] = None,
        periods_ahead: int = 3
    ) -> Dict:
        """
        Forecast future spending based on historical data.
        
        Args:
            historical_data: List of transactions with date, amount, category
            category: Specific category to forecast (None = all categories)
            periods_ahead: Number of months to forecast
        
        Returns:
            Forecast results with predictions and analysis
        """
        if not historical_data:
            return {"error": "No historical data provided"}
        
        # Organize data by month and category
        monthly_data = self._aggregate_by_month(historical_data)
        
        if category:
            # Forecast single category
            category_data = [
                month_data.get(category, 0)
                for month_data in monthly_data.values()
            ]
            
            forecast = self._exponential_smoothing_forecast(
                category_data,
                periods_ahead
            )
            
            return {
                "category": category,
                "historical_months": len(category_data),
                "historical_average": round(np.mean(category_data), 2),
                "forecast": [
                    {
                        "period": i + 1,
                        "predicted_amount": round(pred, 2),
                        "confidence_low": round(pred * 0.85, 2),
                        "confidence_high": round(pred * 1.15, 2)
                    }
                    for i, pred in enumerate(forecast)
                ],
                "trend_analysis": self._analyze_trend(category_data),
                "seasonality": self._detect_seasonality(category_data)
            }
        else:
            # Forecast all categories
            forecasts = {}
            total_forecast = [0] * periods_ahead
            
            # Get all unique categories
            all_categories = set()
            for month_data in monthly_data.values():
                all_categories.update(month_data.keys())
            
            for cat in all_categories:
                cat_data = [
                    month_data.get(cat, 0)
                    for month_data in monthly_data.values()
                ]
                
                cat_forecast = self._exponential_smoothing_forecast(
                    cat_data,
                    periods_ahead
                )
                
                forecasts[cat] = {
                    "historical_average": round(np.mean(cat_data), 2),
                    "forecast": [round(pred, 2) for pred in cat_forecast],
                    "trend": self._analyze_trend(cat_data)["trend"]
                }
                
                # Accumulate total
                for i, pred in enumerate(cat_forecast):
                    total_forecast[i] += pred
            
            return {
                "forecast_type": "all_categories",
                "periods_ahead": periods_ahead,
                "categories": forecasts,
                "total_forecast": [round(total, 2) for total in total_forecast],
                "recommendations": self._generate_forecast_recommendations(forecasts)
            }
    
    def _aggregate_by_month(self, transactions: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Aggregate transactions by month and category"""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        for txn in transactions:
            # Parse date
            if isinstance(txn.get("date"), str):
                date = datetime.fromisoformat(txn["date"].replace("Z", "+00:00"))
            else:
                date = txn.get("date", datetime.now())
            
            month_key = date.strftime("%Y-%m")
            category = txn.get("category", "uncategorized")
            amount = abs(txn.get("amount", 0))
            
            monthly_data[month_key][category] += amount
        
        # Sort by month
        sorted_data = dict(sorted(monthly_data.items()))
        return sorted_data
    
    def _exponential_smoothing_forecast(
        self,
        data: List[float],
        periods: int
    ) -> List[float]:
        """
        Double exponential smoothing (Holt's method) for trend-aware forecasting.
        
        Args:
            data: Historical data points
            periods: Number of periods to forecast
        
        Returns:
            List of forecasted values
        """
        if len(data) < 2:
            # Not enough data, return average
            avg = np.mean(data) if data else 0
            return [avg] * periods
        
        # Initialize
        level = data[0]
        trend = data[1] - data[0] if len(data) > 1 else 0
        
        # Smooth historical data
        for i in range(1, len(data)):
            last_level = level
            level = self.alpha * data[i] + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - last_level) + (1 - self.beta) * trend
        
        # Forecast future periods
        forecasts = []
        for i in range(periods):
            forecast = level + (i + 1) * trend
            forecasts.append(max(0, forecast))  # Don't predict negative spending
        
        return forecasts
    
    def _analyze_trend(self, data: List[float]) -> Dict:
        """Analyze trend in time series data"""
        if len(data) < 2:
            return {
                "trend": "insufficient_data",
                "slope": 0,
                "strength": 0
            }
        
        # Calculate linear regression
        x = np.arange(len(data))
        y = np.array(data)
        
        # Slope using least squares
        n = len(data)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
        
        # Determine trend
        avg = np.mean(data)
        threshold = avg * 0.05  # 5% threshold
        
        if abs(slope) < threshold:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Calculate trend strength (R²)
        y_pred = slope * x + (np.mean(y) - slope * np.mean(x))
        ss_res = np.sum((y - y_pred)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            "trend": trend,
            "slope": round(slope, 2),
            "strength": round(abs(r_squared), 2),
            "monthly_change": round(slope, 2)
        }
    
    def _detect_seasonality(self, data: List[float]) -> Dict:
        """Detect seasonal patterns in spending"""
        if len(data) < 12:
            return {
                "detected": False,
                "reason": "Insufficient data (need 12+ months)"
            }
        
        # Simple seasonality detection using autocorrelation
        mean = np.mean(data)
        variance = np.var(data)
        
        if variance == 0:
            return {
                "detected": False,
                "reason": "No variation in data"
            }
        
        # Check for 12-month seasonality
        if len(data) >= 12:
            first_half = data[:len(data)//2]
            second_half = data[len(data)//2:]
            
            # Compare patterns
            correlation = np.corrcoef(
                first_half[:len(second_half)],
                second_half
            )[0, 1] if len(first_half) >= len(second_half) else 0
            
            if abs(correlation) > 0.5:
                return {
                    "detected": True,
                    "pattern_strength": round(abs(correlation), 2),
                    "recommendation": "Spending shows seasonal patterns. Budget accordingly."
                }
        
        return {
            "detected": False,
            "reason": "No strong seasonal pattern detected"
        }
    
    def predict_category_spending(
        self,
        category: str,
        historical_amounts: List[float],
        months_ahead: int = 1
    ) -> Dict:
        """
        Predict spending for a specific category.
        
        Args:
            category: Category name
            historical_amounts: List of historical monthly amounts
            months_ahead: How many months to predict
        
        Returns:
            Prediction with confidence intervals
        """
        if not historical_amounts:
            return {
                "error": "No historical data",
                "category": category
            }
        
        # Calculate statistics
        mean = np.mean(historical_amounts)
        std = np.std(historical_amounts)
        
        # Forecast using exponential smoothing
        forecast = self._exponential_smoothing_forecast(
            historical_amounts,
            months_ahead
        )
        
        # Trend analysis
        trend_info = self._analyze_trend(historical_amounts)
        
        # Confidence intervals (using standard deviation)
        predictions = []
        for i, pred in enumerate(forecast):
            # Wider confidence interval for further predictions
            uncertainty_factor = 1 + (i * 0.1)
            
            predictions.append({
                "month": i + 1,
                "predicted": round(pred, 2),
                "confidence_low": round(max(0, pred - std * uncertainty_factor), 2),
                "confidence_high": round(pred + std * uncertainty_factor, 2),
                "confidence_level": "68%"  # 1 std dev
            })
        
        return {
            "category": category,
            "predictions": predictions,
            "historical_stats": {
                "average": round(mean, 2),
                "std_dev": round(std, 2),
                "min": round(min(historical_amounts), 2),
                "max": round(max(historical_amounts), 2),
                "data_points": len(historical_amounts)
            },
            "trend": trend_info,
            "recommendation": self._generate_category_recommendation(
                category,
                trend_info,
                mean,
                forecast[0] if forecast else mean
            )
        }
    
    def compare_forecast_to_budget(
        self,
        forecasts: Dict[str, float],
        budgets: Dict[str, float]
    ) -> Dict:
        """
        Compare forecasted spending to budgeted amounts.
        
        Args:
            forecasts: Dict of category -> forecasted amount
            budgets: Dict of category -> budgeted amount
        
        Returns:
            Comparison analysis with warnings
        """
        comparisons = []
        warnings = []
        
        for category in set(list(forecasts.keys()) + list(budgets.keys())):
            forecast = forecasts.get(category, 0)
            budget = budgets.get(category, 0)
            
            difference = forecast - budget
            percent_diff = (difference / budget * 100) if budget > 0 else 0
            
            status = "on_track"
            if difference > budget * 0.1:  # 10% over
                status = "over_budget"
                warnings.append({
                    "category": category,
                    "message": f"Forecasted to exceed budget by ${abs(difference):.2f}",
                    "severity": "high" if percent_diff > 20 else "medium"
                })
            elif difference < 0 and abs(percent_diff) > 10:
                status = "under_budget"
            
            comparisons.append({
                "category": category,
                "forecast": round(forecast, 2),
                "budget": round(budget, 2),
                "difference": round(difference, 2),
                "percent_difference": round(percent_diff, 1),
                "status": status
            })
        
        # Sort by absolute difference
        comparisons.sort(key=lambda x: abs(x["difference"]), reverse=True)
        
        total_forecast = sum(forecasts.values())
        total_budget = sum(budgets.values())
        
        return {
            "comparisons": comparisons,
            "totals": {
                "total_forecast": round(total_forecast, 2),
                "total_budget": round(total_budget, 2),
                "total_difference": round(total_forecast - total_budget, 2)
            },
            "warnings": warnings,
            "overall_status": "needs_attention" if warnings else "on_track"
        }
    
    def _generate_category_recommendation(
        self,
        category: str,
        trend: Dict,
        historical_avg: float,
        forecast: float
    ) -> str:
        """Generate recommendation based on forecast"""
        trend_type = trend.get("trend", "stable")
        
        if trend_type == "increasing":
            return (
                f"{category.title()} spending is trending upward. "
                f"Consider setting a budget limit or finding cost-saving alternatives."
            )
        elif trend_type == "decreasing":
            return (
                f"Good news! {category.title()} spending is decreasing. "
                f"Consider reallocating savings to other financial goals."
            )
        else:
            return (
                f"{category.title()} spending is stable around ${historical_avg:.2f}/month. "
                f"Maintain current habits or look for optimization opportunities."
            )
    
    def _generate_forecast_recommendations(self, forecasts: Dict) -> List[str]:
        """Generate overall recommendations from forecast data"""
        recommendations = []
        
        # Find categories with concerning trends
        increasing_categories = [
            cat for cat, data in forecasts.items()
            if data["trend"] == "increasing"
        ]
        
        if increasing_categories:
            recommendations.append(
                f"Monitor these growing expenses: {', '.join(increasing_categories[:3])}"
            )
        
        # Find highest forecast categories
        sorted_forecasts = sorted(
            forecasts.items(),
            key=lambda x: x[1]["forecast"][0] if x[1]["forecast"] else 0,
            reverse=True
        )
        
        if sorted_forecasts:
            top_category = sorted_forecasts[0][0]
            recommendations.append(
                f"{top_category.title()} is your largest forecasted expense. "
                f"Focus optimization efforts here for maximum impact."
            )
        
        return recommendations
    
    def anomaly_detection(
        self,
        historical_data: List[float],
        threshold: float = 2.0
    ) -> Dict:
        """
        Detect anomalies in spending patterns.
        
        Args:
            historical_data: Historical spending amounts
            threshold: Number of standard deviations for anomaly (default: 2)
        
        Returns:
            Anomaly detection results
        """
        if len(historical_data) < 3:
            return {
                "anomalies_detected": False,
                "reason": "Insufficient data"
            }
        
        mean = np.mean(historical_data)
        std = np.std(historical_data)
        
        anomalies = []
        for i, value in enumerate(historical_data):
            z_score = abs((value - mean) / std) if std > 0 else 0
            
            if z_score > threshold:
                anomalies.append({
                    "index": i,
                    "value": round(value, 2),
                    "z_score": round(z_score, 2),
                    "type": "high" if value > mean else "low"
                })
        
        return {
            "anomalies_detected": len(anomalies) > 0,
            "count": len(anomalies),
            "anomalies": anomalies,
            "baseline": {
                "mean": round(mean, 2),
                "std_dev": round(std, 2)
            },
            "threshold": threshold,
            "interpretation": self._interpret_anomalies(anomalies, mean)
        }
    
    def _interpret_anomalies(self, anomalies: List[Dict], mean: float) -> str:
        """Interpret what anomalies might mean"""
        if not anomalies:
            return "No unusual spending patterns detected. Your spending is consistent."
        
        high_anomalies = [a for a in anomalies if a["type"] == "high"]
        low_anomalies = [a for a in anomalies if a["type"] == "low"]
        
        if len(high_anomalies) > len(low_anomalies):
            return (
                f"Detected {len(high_anomalies)} month(s) with unusually high spending. "
                f"Review these periods for one-time expenses or lifestyle changes."
            )
        elif len(low_anomalies) > len(high_anomalies):
            return (
                f"Detected {len(low_anomalies)} month(s) with unusually low spending. "
                f"Great job! Consider what contributed to these savings."
            )
        else:
            return "Mixed spending anomalies detected. Review individual months for patterns."
