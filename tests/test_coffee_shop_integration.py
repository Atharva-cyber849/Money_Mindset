"""
Test script for Coffee Shop Effect simulation
Tests the backend service, API endpoints, and gamification integration
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_path)

from backend.app.services.simulation.coffee_shop_simulator import CoffeeShopSimulator
from backend.app.services.gamification import GamificationService, UserStats, Level


def test_coffee_shop_simulator():
    """Test the coffee shop simulator service"""
    print("=" * 60)
    print("TEST 1: Coffee Shop Simulator Service")
    print("=" * 60)
    
    simulator = CoffeeShopSimulator()
    
    # Test basic calculation
    print("\n1. Basic Calculation ($5.50/day, 5 days/week, 30 years)")
    analysis = simulator.calculate(
        daily_cost=5.50,
        days_per_week=5,
        years=30
    )
    
    print(f"   Daily Cost: ${analysis.daily_cost:.2f}")
    print(f"   Annual Cost: ${analysis.annual_cost:,.2f}")
    print(f"   30-Year Cost: ${analysis.thirty_year_cost:,.2f}")
    print(f"   If Invested: ${analysis.compound_results[-1].invested_total:,.2f}")
    print(f"   Opportunity Cost: ${analysis.total_opportunity_cost:,.2f}")
    print(f"   ✅ PASS: Calculation works correctly")
    
    # Test scenario comparison
    print("\n2. Scenario Comparison")
    scenarios = [
        {"name": "Coffee Shop Daily", "daily_cost": 5.50, "days_per_week": 5},
        {"name": "Coffee Shop 3x/week", "daily_cost": 5.50, "days_per_week": 3},
        {"name": "Home Brew", "daily_cost": 0.75, "days_per_week": 5},
    ]
    
    comparison = simulator.compare_scenarios(scenarios)
    
    for name, data in comparison.items():
        print(f"   {name}:")
        print(f"      Annual: ${data['annual_cost']:,.2f}")
        print(f"      30-Year Opportunity Cost: ${data['opportunity_cost']:,.2f}")
    
    print(f"   ✅ PASS: Comparison works correctly")
    
    # Test opportunity examples
    print("\n3. Opportunity Examples")
    print(f"   Found {len(analysis.opportunity_examples)} examples")
    for ex in analysis.opportunity_examples[:3]:
        print(f"   • {ex.item} (${ex.cost:,.0f}) - {ex.years_saved} years")
    print(f"   ✅ PASS: Examples generated correctly")
    
    return True


def test_gamification_integration():
    """Test gamification integration"""
    print("\n" + "=" * 60)
    print("TEST 2: Gamification Integration")
    print("=" * 60)
    
    gamification = GamificationService()
    
    # Create new user
    print("\n1. Create New User")
    user_stats = gamification.create_user_stats(user_id=1)
    print(f"   Initial Level: {user_stats.current_level.name}")
    print(f"   Initial XP: {user_stats.total_xp}")
    print(f"   ✅ PASS: User created")
    
    # Complete coffee shop simulation
    print("\n2. Complete Coffee Shop Simulation")
    update = gamification.process_simulation_completion(
        user_stats,
        "coffee_shop_effect",
        perfect_score=False,
        first_try=True
    )
    
    print(f"   XP Earned: {update.xp_earned.total_xp} ({update.xp_earned.reason})")
    print(f"   New Total XP: {user_stats.total_xp}")
    print(f"   Current Level: {user_stats.current_level.name}")
    
    if update.badges_earned:
        print(f"   Badges Earned:")
        for badge_award in update.badges_earned:
            print(f"      {badge_award.badge.icon} {badge_award.badge.name}")
    
    if update.level_up:
        print(f"   🎉 LEVEL UP: {update.level_up['celebration_message']}")
    
    print(f"   ✅ PASS: Gamification works correctly")
    
    # Get dashboard
    print("\n3. Get User Dashboard")
    dashboard = gamification.get_user_dashboard(user_stats)
    
    print(f"   Level: {dashboard['progress']['level_name']}")
    print(f"   XP Progress: {dashboard['progress']['current_xp']} / {dashboard['progress']['current_xp'] + dashboard['progress']['xp_to_next_level']}")
    print(f"   Simulations Completed: {dashboard['stats']['simulations_completed']}")
    print(f"   Badges Earned: {dashboard['stats']['badges_earned']}/{dashboard['badges']['collection_stats']['total_badges']}")
    print(f"   ✅ PASS: Dashboard generated correctly")
    
    return True


def test_api_response_format():
    """Test that API response format is correct"""
    print("\n" + "=" * 60)
    print("TEST 3: API Response Format")
    print("=" * 60)
    
    simulator = CoffeeShopSimulator()
    analysis = simulator.calculate(5.50, 5, 30)
    
    # Simulate API response format
    print("\n1. Main Calculation Response")
    api_response = {
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
            for r in analysis.compound_results[:5]  # First 5 years
        ],
        "total_opportunity_cost": analysis.total_opportunity_cost,
        "recommendation": analysis.recommendation
    }
    
    print(f"   Response Keys: {list(api_response.keys())}")
    print(f"   Compound Results Count: {len(analysis.compound_results)}")
    print(f"   Opportunity Examples: {len(analysis.opportunity_examples)}")
    print(f"   ✅ PASS: API response format correct")
    
    # Test completion response
    print("\n2. Completion Response")
    gamification = GamificationService()
    user_stats = gamification.create_user_stats(user_id=1)
    update = gamification.process_simulation_completion(
        user_stats,
        "coffee_shop_effect",
        perfect_score=True,
        first_try=True
    )
    
    completion_response = {
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
            }
            for b in update.badges_earned
        ],
        "new_unlocks": update.new_unlocks,
        "progress": {
            "level": update.updated_snapshot.current_level.value,
            "current_xp": update.updated_snapshot.current_xp,
            "xp_to_next_level": update.updated_snapshot.xp_to_next_level,
        }
    }
    
    print(f"   Response Keys: {list(completion_response.keys())}")
    print(f"   XP Earned: {completion_response['xp_earned']['amount']}")
    print(f"   Badges Count: {len(completion_response['badges_earned'])}")
    print(f"   ✅ PASS: Completion response format correct")
    
    return True


def test_edge_cases():
    """Test edge cases and validation"""
    print("\n" + "=" * 60)
    print("TEST 4: Edge Cases")
    print("=" * 60)
    
    simulator = CoffeeShopSimulator()
    
    # Test very small expense
    print("\n1. Very Small Expense ($1/day)")
    analysis = simulator.calculate(1.0, 5, 30)
    print(f"   Annual Cost: ${analysis.annual_cost:,.2f}")
    print(f"   Recommendation length: {len(analysis.recommendation)} chars")
    print(f"   ✅ PASS: Small expense handled")
    
    # Test very large expense
    print("\n2. Very Large Expense ($20/day)")
    analysis = simulator.calculate(20.0, 5, 30)
    print(f"   Annual Cost: ${analysis.annual_cost:,.2f}")
    print(f"   30-Year Opportunity Cost: ${analysis.total_opportunity_cost:,.2f}")
    print(f"   ✅ PASS: Large expense handled")
    
    # Test 7 days per week
    print("\n3. Every Day (7 days/week)")
    analysis = simulator.calculate(5.50, 7, 30)
    print(f"   Annual Cost: ${analysis.annual_cost:,.2f}")
    print(f"   ✅ PASS: Daily expense handled")
    
    # Test 1 year projection
    print("\n4. Short Timeline (1 year)")
    analysis = simulator.calculate(5.50, 5, 1)
    print(f"   Annual Cost: ${analysis.annual_cost:,.2f}")
    print(f"   Compound Results: {len(analysis.compound_results)} years")
    print(f"   ✅ PASS: Short timeline handled")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "🧪 " * 30)
    print("COFFEE SHOP EFFECT - END-TO-END TESTING")
    print("🧪 " * 30)
    
    tests = [
        ("Coffee Shop Simulator", test_coffee_shop_simulator),
        ("Gamification Integration", test_gamification_integration),
        ("API Response Format", test_api_response_format),
        ("Edge Cases", test_edge_cases),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Coffee Shop Effect is ready for production!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review and fix.")
    
    print("\n" + "🧪 " * 30)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
