"""
Test script for AI Analytics features
Run with: python -m pytest tests/test_analytics_features.py -v
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.analytics import (
    ExpenseClassifier,
    MarketSimulator,
    BudgetOptimizer,
    ForecastingService
)


def test_expense_classifier():
    """Test expense classification"""
    print("\n=== Testing Expense Classifier ===")
    
    classifier = ExpenseClassifier()
    
    # Test single classification
    result = classifier.classify("Starbucks Coffee", 5.50)
    print(f"\nClassification for 'Starbucks Coffee':")
    print(f"  Category: {result['category']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Needs Review: {result['needs_review']}")
    
    assert result['category'] in ['restaurants', 'groceries', 'shopping']
    assert 0 <= result['confidence'] <= 1
    
    # Test batch classification
    transactions = [
        {"id": 1, "description": "Shell Gas Station", "amount": 45.00},
        {"id": 2, "description": "Amazon.com", "amount": 89.99},
        {"id": 3, "description": "Whole Foods", "amount": 125.50},
    ]
    
    batch_results = classifier.classify_batch(transactions)
    print(f"\nBatch classification results: {len(batch_results)} transactions")
    
    for result in batch_results:
        print(f"  - {result['original_description']}: {result['category']} ({result['confidence']:.2f})")
    
    print("✓ Expense Classifier tests passed")


def test_market_simulator():
    """Test market simulation"""
    print("\n=== Testing Market Simulator ===")
    
    simulator = MarketSimulator()
    
    # Test simple simulation
    result = simulator.simulate_investment(
        initial_amount=10000,
        monthly_contribution=500,
        years=10,
        asset_class="balanced",
        num_simulations=100  # Fewer for speed
    )
    
    print(f"\nInvestment Simulation (Balanced Portfolio):")
    print(f"  Total Invested: ${result['total_invested']:,.2f}")
    print(f"  Expected Value: ${result['statistics']['median']:,.2f}")
    print(f"  Expected Gain: ${result['returns']['expected_gain']:,.2f}")
    print(f"  Probability of Profit: {result['probability_analysis']['prob_profit']}%")
    
    assert result['total_invested'] == 10000 + (500 * 10 * 12)
    assert result['statistics']['median'] > result['total_invested']
    
    # Test asset comparison
    comparison = simulator.compare_asset_classes(
        initial_amount=10000,
        monthly_contribution=500,
        years=10,
        asset_classes=["conservative", "balanced", "aggressive_stocks"]
    )
    
    print(f"\nAsset Class Comparison:")
    for asset in comparison['comparison']:
        print(f"  {asset['name']}: ${asset['median_value']:,.2f} (Risk: ${asset['risk_score']:,.2f})")
    
    print("✓ Market Simulator tests passed")


def test_budget_optimizer():
    """Test budget optimization"""
    print("\n=== Testing Budget Optimizer ===")
    
    optimizer = BudgetOptimizer()
    
    # Test budget analysis
    result = optimizer.analyze_budget(
        income=5000,
        expenses={
            "housing": 1250,
            "transportation": 500,
            "groceries": 400,
            "restaurants": 300,
            "utilities": 150,
        },
        savings=1000
    )
    
    print(f"\nBudget Analysis:")
    print(f"  Health Score: {result['health_score']['score']} ({result['health_score']['rating']})")
    print(f"  Savings Rate: {result['summary']['savings_rate_pct']}%")
    print(f"  50/30/20 Grade: {result['fifty_thirty_twenty']['overall_compliance']['grade']}")
    
    assert 0 <= result['health_score']['score'] <= 100
    assert result['summary']['savings_rate_pct'] == 20.0
    
    # Test suggested allocation
    suggestion = optimizer.suggest_budget_allocation(5000)
    
    print(f"\nSuggested Allocation:")
    print(f"  Needs: ${suggestion['recommended_allocation']['needs']['total']:,.2f}")
    print(f"  Wants: ${suggestion['recommended_allocation']['wants']['total']:,.2f}")
    print(f"  Savings: ${suggestion['recommended_allocation']['savings']['total']:,.2f}")
    
    assert suggestion['monthly_income'] == 5000
    
    print("✓ Budget Optimizer tests passed")


def test_forecasting_service():
    """Test forecasting models"""
    print("\n=== Testing Forecasting Service ===")
    
    forecaster = ForecastingService()
    
    # Test category forecast
    historical_data = [500, 520, 480, 510, 495, 530, 515, 505, 525, 490, 500, 510]
    
    result = forecaster.predict_category_spending(
        category="groceries",
        historical_amounts=historical_data,
        months_ahead=3
    )
    
    print(f"\nSpending Forecast (Groceries):")
    print(f"  Historical Average: ${result['historical_stats']['average']:.2f}")
    print(f"  Trend: {result['trend']['trend']} ({result['trend']['monthly_change']:.2f}/month)")
    
    print(f"  Predictions:")
    for pred in result['predictions']:
        print(f"    Month {pred['month']}: ${pred['predicted']:.2f} "
              f"(${pred['confidence_low']:.2f} - ${pred['confidence_high']:.2f})")
    
    assert len(result['predictions']) == 3
    assert result['trend']['trend'] in ['increasing', 'decreasing', 'stable']
    
    # Test anomaly detection
    anomaly_data = [500, 520, 480, 510, 495, 1500, 515, 505, 525, 490, 500, 510]
    
    anomalies = forecaster.anomaly_detection(anomaly_data, threshold=2.0)
    
    print(f"\nAnomaly Detection:")
    print(f"  Anomalies Found: {anomalies['count']}")
    if anomalies['anomalies']:
        for anomaly in anomalies['anomalies']:
            print(f"    Month {anomaly['index'] + 1}: ${anomaly['value']:.2f} (z-score: {anomaly['z_score']:.2f})")
    
    assert anomalies['anomalies_detected'] == True
    assert anomalies['count'] >= 1
    
    print("✓ Forecasting Service tests passed")


def run_all_tests():
    """Run all analytics tests"""
    print("\n" + "="*60)
    print("AI ANALYTICS FEATURES TEST SUITE")
    print("="*60)
    
    try:
        test_expense_classifier()
        test_market_simulator()
        test_budget_optimizer()
        test_forecasting_service()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        return True
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
