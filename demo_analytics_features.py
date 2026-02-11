"""
Quick demo script for AI Analytics features
Run with: python demo_analytics_features.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.services.analytics import (
    ExpenseClassifier,
    MarketSimulator,
    BudgetOptimizer,
    ForecastingService
)


def demo_expense_classification():
    """Demo expense classification"""
    print("\n" + "="*70)
    print("🧠 EXPENSE CLASSIFICATION DEMO")
    print("="*70)
    
    classifier = ExpenseClassifier()
    
    transactions = [
        ("Starbucks Downtown", 5.50),
        ("Shell Gas Station", 45.00),
        ("Amazon.com Order", 89.99),
        ("Whole Foods Market", 125.50),
        ("Netflix Subscription", 15.99),
        ("LA Fitness Membership", 29.99),
    ]
    
    print("\nClassifying transactions...")
    for description, amount in transactions:
        result = classifier.classify(description, amount)
        
        confidence_bar = "█" * int(result['confidence'] * 20)
        print(f"\n📝 {description} (${amount:.2f})")
        print(f"   Category: {result['category'].upper()}")
        print(f"   Confidence: {confidence_bar} {result['confidence']*100:.0f}%")
        
        if result['alternatives']:
            alt = result['alternatives'][0]
            print(f"   Alternative: {alt['category']} ({alt['confidence']*100:.0f}%)")


def demo_market_simulation():
    """Demo market simulation"""
    print("\n" + "="*70)
    print("📈 MARKET SIMULATION DEMO")
    print("="*70)
    
    simulator = MarketSimulator()
    
    print("\nScenario: Invest $10,000 initially + $500/month for 10 years")
    print("Asset Class: Balanced Portfolio (60% stocks / 40% bonds)")
    
    result = simulator.simulate_investment(
        initial_amount=10000,
        monthly_contribution=500,
        years=10,
        asset_class="balanced",
        num_simulations=500
    )
    
    print(f"\n💰 Investment Results (500 simulations):")
    print(f"   Total Invested: ${result['total_invested']:,.0f}")
    print(f"   Expected Value: ${result['statistics']['median']:,.0f}")
    print(f"   Expected Gain: ${result['returns']['expected_gain']:,.0f}")
    print(f"\n📊 Outcome Distribution:")
    print(f"   10th Percentile: ${result['percentiles']['p10']:,.0f}")
    print(f"   50th Percentile: ${result['percentiles']['p50']:,.0f}")
    print(f"   90th Percentile: ${result['percentiles']['p90']:,.0f}")
    print(f"\n🎲 Probabilities:")
    print(f"   Chance of Profit: {result['probability_analysis']['prob_profit']}%")
    print(f"   Chance to Double: {result['probability_analysis']['prob_double']}%")
    print(f"   Risk of Loss: {result['probability_analysis']['prob_loss']}%")


def demo_budget_optimization():
    """Demo budget optimization"""
    print("\n" + "="*70)
    print("🎯 BUDGET OPTIMIZATION DEMO")
    print("="*70)
    
    optimizer = BudgetOptimizer()
    
    print("\nAnalyzing monthly budget...")
    print("Income: $5,000/month")
    
    result = optimizer.analyze_budget(
        income=5000,
        expenses={
            "housing": 1500,  # Higher than recommended
            "transportation": 500,
            "groceries": 400,
            "restaurants": 350,
            "utilities": 150,
            "entertainment": 200,
        },
        savings=800
    )
    
    print(f"\n💯 Budget Health Score: {result['health_score']['score']}/100")
    print(f"   Rating: {result['health_score']['rating']}")
    print(f"   Savings Rate: {result['summary']['savings_rate_pct']}%")
    
    print(f"\n📐 50/30/20 Analysis:")
    for category, data in result['fifty_thirty_twenty'].items():
        if category != 'overall_compliance':
            status_emoji = "✅" if data['status'] == 'on_track' else "⚠️"
            print(f"   {status_emoji} {category.title()}: {data['percentage']}% (target: {data['target']}%)")
    
    if result['recommendations']:
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡"
            print(f"   {i}. {priority_emoji} {rec['issue']}")
            print(f"      → {rec['suggestion']}")


def demo_forecasting():
    """Demo spending forecasting"""
    print("\n" + "="*70)
    print("🔮 FORECASTING DEMO")
    print("="*70)
    
    forecaster = ForecastingService()
    
    # Historical grocery spending (12 months)
    historical = [500, 520, 480, 510, 495, 530, 515, 505, 525, 490, 540, 510]
    
    print("\nHistorical Grocery Spending (12 months):")
    print("  " + ", ".join([f"${x}" for x in historical]))
    
    result = forecaster.predict_category_spending(
        category="groceries",
        historical_amounts=historical,
        months_ahead=3
    )
    
    print(f"\n📊 Historical Statistics:")
    print(f"   Average: ${result['historical_stats']['average']:.2f}/month")
    print(f"   Range: ${result['historical_stats']['min']:.2f} - ${result['historical_stats']['max']:.2f}")
    print(f"   Std Dev: ${result['historical_stats']['std_dev']:.2f}")
    
    print(f"\n📈 Trend Analysis:")
    trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}
    print(f"   {trend_emoji[result['trend']['trend']]} {result['trend']['trend'].title()}")
    print(f"   Monthly Change: ${result['trend']['monthly_change']:.2f}")
    
    print(f"\n🔮 3-Month Forecast:")
    for pred in result['predictions']:
        print(f"   Month {pred['month']}: ${pred['predicted']:.2f}")
        print(f"      Range: ${pred['confidence_low']:.2f} - ${pred['confidence_high']:.2f} ({pred['confidence_level']})")
    
    print(f"\n💭 {result['recommendation']}")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("🚀 AI-POWERED ANALYTICS FEATURE DEMOS")
    print("   Money Mindset - Financial Intelligence System")
    print("="*70)
    
    demo_expense_classification()
    demo_market_simulation()
    demo_budget_optimization()
    demo_forecasting()
    
    print("\n" + "="*70)
    print("✓ All demos completed successfully!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("  2. Start the frontend: cd frontend && npm run dev")
    print("  3. Visit http://localhost:3000/analytics")
    print("\n")


if __name__ == "__main__":
    main()
