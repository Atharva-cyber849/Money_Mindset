"""
Interactive Demo: Coffee Shop Effect Simulation
Shows the complete end-to-end flow
"""

import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_path)

from backend.app.services.simulation.coffee_shop_simulator import CoffeeShopSimulator
from backend.app.services.gamification import GamificationService, UserStats, Level


def demo_complete_flow():
    """Demonstrate the complete user flow"""
    
    print("=" * 70)
    print("☕ COFFEE SHOP EFFECT - INTERACTIVE SIMULATION DEMO")
    print("=" * 70)
    
    # Step 1: User starts simulation
    print("\n📱 USER STARTS SIMULATION")
    print("-" * 70)
    print("Frontend: User clicks 'Start' on Coffee Shop Effect card")
    print("Frontend: Shows Step 1 - Make Your Guess")
    print()
    
    user_guess = 600
    print(f"User guesses: ${user_guess:,.0f} per year")
    input("\nPress Enter to reveal the reality...\n")
    
    # Step 2: Calculate actual cost
    print("\n💰 CALCULATING ACTUAL COST")
    print("-" * 70)
    
    simulator = CoffeeShopSimulator()
    analysis = simulator.calculate(
        daily_cost=5.50,
        days_per_week=5,
        years=30
    )
    
    print("Backend API Call: POST /api/v1/simulations/coffee-shop-effect")
    print(f"Request: {{'daily_cost': 5.50, 'days_per_week': 5, 'years': 30}}")
    print()
    
    print("📊 RESULTS:")
    print(f"   Your Guess: ${user_guess:,.0f}")
    print(f"   Actual Cost: ${analysis.annual_cost:,.0f} per year")
    print(f"   Difference: ${abs(user_guess - analysis.annual_cost):,.0f}")
    print()
    
    print("   Breakdown:")
    print(f"      $5.50 per coffee")
    print(f"      × 5 workdays per week")
    print(f"      × 52 weeks per year")
    print(f"      = ${analysis.annual_cost:,.0f} / year")
    print()
    
    input("Press Enter to see long-term impact...\n")
    
    # Step 3: Show compound effect
    print("\n📈 LONG-TERM COMPOUND EFFECT")
    print("-" * 70)
    
    print("If you SPENT this money:")
    print(f"   5 years:  ${analysis.five_year_cost:,.0f}")
    print(f"   10 years: ${analysis.ten_year_cost:,.0f}")
    print(f"   30 years: ${analysis.thirty_year_cost:,.0f}")
    print()
    
    print("If you INVESTED this money (8% return):")
    print(f"   5 years:  ${analysis.compound_results[4].invested_total:,.0f}")
    print(f"   10 years: ${analysis.compound_results[9].invested_total:,.0f}")
    print(f"   30 years: ${analysis.compound_results[29].invested_total:,.0f}")
    print()
    
    print("💸 OPPORTUNITY COST:")
    print(f"   Total lost wealth: ${analysis.total_opportunity_cost:,.0f}")
    print()
    
    input("Press Enter to see what you could buy instead...\n")
    
    # Step 4: Opportunity examples
    print("\n🎁 WHAT YOU COULD BUY INSTEAD")
    print("-" * 70)
    
    print("With the money saved by cutting back to 3 days/week:")
    print()
    
    for example in analysis.opportunity_examples[:6]:
        print(f"   {example.item} (${example.cost:,.0f})")
        print(f"      Achievable in: {example.years_saved} years")
        print(f"      {example.description}")
        print()
    
    input("Press Enter to complete simulation...\n")
    
    # Step 5: Complete simulation and earn rewards
    print("\n🎮 COMPLETING SIMULATION")
    print("-" * 70)
    
    # Calculate user score
    actual = analysis.annual_cost
    difference = abs(actual - user_guess)
    accuracy = max(0, 100 - (difference / actual * 100))
    score = round(accuracy)
    is_perfect = score >= 95
    
    print(f"Your Score: {score}/100")
    print(f"Perfect Score: {'Yes! 🎯' if is_perfect else 'No, but great effort!'}")
    print()
    
    print("Backend API Call: POST /api/v1/simulations/coffee-shop-effect/complete")
    print(f"Request: {{'user_score': {score}, 'perfect_score': {is_perfect}}}")
    print()
    
    # Process gamification
    gamification = GamificationService()
    user_stats = gamification.create_user_stats(user_id=1)
    
    update = gamification.process_simulation_completion(
        user_stats,
        "coffee_shop_effect",
        perfect_score=is_perfect,
        first_try=True
    )
    
    print("🎉 REWARDS EARNED:")
    print()
    
    # XP
    print(f"   ⭐ +{update.xp_earned.total_xp} XP")
    print(f"      {update.xp_earned.reason}")
    print()
    
    # Badges
    if update.badges_earned:
        print("   🏆 BADGES UNLOCKED:")
        for badge_award in update.badges_earned:
            badge = badge_award.badge
            print(f"      {badge.icon} {badge.name} ({badge.rarity.value})")
            print(f"         {badge.description}")
        print()
    
    # Level up
    if update.level_up:
        print(f"   ⬆️ LEVEL UP!")
        print(f"      {update.level_up['celebration_message']}")
        print()
    
    # Progress
    print("   📊 YOUR PROGRESS:")
    snapshot = update.updated_snapshot
    print(f"      Level: {snapshot.current_level.name}")
    print(f"      XP: {snapshot.current_xp} / {snapshot.current_xp + snapshot.xp_to_next_level}")
    print(f"      Progress: {snapshot.progress_percentage:.1f}%")
    print(f"      Simulations: {snapshot.total_simulations_completed}")
    print(f"      Badges: {snapshot.total_badges_earned}/16")
    print()
    
    # Recommendation
    print("💡 RECOMMENDATION:")
    print(f"   {analysis.recommendation}")
    print()
    
    input("Press Enter to see what's unlocked next...\n")
    
    # Step 6: What's next
    print("\n🔓 WHAT'S UNLOCKED NEXT")
    print("-" * 70)
    
    dashboard = gamification.get_user_dashboard(user_stats)
    
    print("Available Simulations:")
    for sim in dashboard['simulations']['unlocked'][:3]:
        print(f"   📚 {sim['name']} (+{sim['xp_reward']} XP)")
        print(f"      {sim['description']}")
        print()
    
    print("Recommended Next Steps:")
    for rec in dashboard['recommendations'][:2]:
        print(f"   👉 {rec['simulation']}")
        print(f"      {rec['reason']}")
        print(f"      +{rec['xp']} XP")
        print()
    
    print("\n" + "=" * 70)
    print("✅ SIMULATION COMPLETE!")
    print("=" * 70)
    print()
    print("This demonstrates the complete end-to-end flow:")
    print("  1. Frontend interactive experience (4 steps)")
    print("  2. Backend calculation engine")
    print("  3. API endpoints for data and completion")
    print("  4. Gamification system (XP, badges, levels)")
    print("  5. Progress tracking and recommendations")
    print()
    print("The user is now motivated to continue learning! 🚀")
    print()


if __name__ == "__main__":
    try:
        demo_complete_flow()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Thanks for watching!")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
