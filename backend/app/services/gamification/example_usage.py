"""
Example usage and testing of the gamification system
"""

from datetime import datetime, timedelta
from backend.app.services.gamification import (
    GamificationService,
    UserStats,
    Level
)


def demo_user_journey():
    """Demonstrate a complete user journey through the gamification system"""
    
    # Initialize gamification service
    gamification = GamificationService()
    
    # Create new user
    user_stats = gamification.create_user_stats(user_id=1)
    
    print("=== NEW USER CREATED ===")
    print(f"Level: {user_stats.current_level.name}")
    print(f"XP: {user_stats.total_xp}")
    print(f"Badges: {len(user_stats.earned_badges)}")
    print()
    
    # Day 1: Complete first simulation
    print("=== DAY 1: Coffee Shop Effect ===")
    update = gamification.process_simulation_completion(
        user_stats,
        "coffee_shop_effect",
        perfect_score=False,
        first_try=True
    )
    
    print(f"XP Earned: {update.xp_earned.total_xp} ({update.xp_earned.reason})")
    print(f"New Total XP: {user_stats.total_xp}")
    print(f"Badges Earned: {[b.badge.name for b in update.badges_earned]}")
    
    if update.level_up:
        print(f"🎉 LEVEL UP! {update.level_up['celebration_message']}")
    print()
    
    # Day 2: Paycheck Game
    print("=== DAY 2: Paycheck Game ===")
    user_stats.last_activity_date = datetime.now() - timedelta(days=1)
    
    update = gamification.process_simulation_completion(
        user_stats,
        "paycheck_game",
        perfect_score=True,
        first_try=True
    )
    
    print(f"XP Earned: {update.xp_earned.total_xp} ({update.xp_earned.reason})")
    print(f"New Total XP: {user_stats.total_xp}")
    print(f"Current Streak: {user_stats.current_streak} days")
    print(f"Badges Earned: {[b.badge.name for b in update.badges_earned]}")
    print()
    
    # Day 3: Multiple simulations
    print("=== DAY 3: Budget Builder ===")
    user_stats.last_activity_date = datetime.now() - timedelta(days=1)
    
    update = gamification.process_simulation_completion(
        user_stats,
        "budget_builder",
        perfect_score=False,
        first_try=True
    )
    
    print(f"XP Earned: {update.xp_earned.total_xp}")
    print(f"New Total XP: {user_stats.total_xp}")
    print(f"Current Level: {user_stats.current_level.name}")
    print(f"Current Streak: {user_stats.current_streak} days")
    
    if update.level_up:
        print(f"🎉 LEVEL UP to {update.level_up['new_level_info'].name}!")
    
    print(f"Badges Earned: {[b.badge.name for b in update.badges_earned]}")
    print(f"New Unlocks: {[u['simulation_name'] for u in update.new_unlocks]}")
    print()
    
    # Get dashboard
    print("=== USER DASHBOARD ===")
    dashboard = gamification.get_user_dashboard(user_stats)
    
    print(f"Level: {dashboard['progress']['level_name']}")
    print(f"XP: {dashboard['progress']['current_xp']} / {dashboard['progress']['current_xp'] + dashboard['progress']['xp_to_next_level']}")
    print(f"Progress: {dashboard['progress']['progress_percentage']:.1f}%")
    print(f"Simulations: {dashboard['stats']['simulations_completed']} completed")
    print(f"Badges: {dashboard['stats']['badges_earned']}/{dashboard['badges']['collection_stats']['total_badges']}")
    print(f"Streak: {dashboard['stats']['current_streak']} days (best: {dashboard['stats']['longest_streak']})")
    print()
    
    print("Next Badges to Earn:")
    for item in dashboard['badges']['next_to_earn'][:3]:
        badge = item['badge']
        progress = item['progress']
        print(f"  {badge['icon']} {badge['name']} - {progress['current_progress']}/{progress['required_progress']} ({progress['progress_percentage']:.0f}%)")
    print()
    
    print("Recommended Next Steps:")
    for rec in dashboard['recommendations'][:3]:
        print(f"  📌 {rec['simulation']}: {rec['reason']} (+{rec['xp']} XP)")
    print()
    
    # Simulate full journey
    print("=== SIMULATING FULL JOURNEY ===")
    all_simulations = [
        "coffee_shop_effect",
        "paycheck_game",
        "budget_builder",
        "emergency_fund",
        "credit_card_trap",
        "debt_classification",
        "compound_interest",
        "risk_vs_reward",
        "index_fund_challenge",
        "tax_optimizer",
        "monte_carlo",
        "sarah_journey"
    ]
    
    journey = gamification.simulate_user_journey(all_simulations)
    
    print("Journey Summary:")
    for step in journey['journey']:
        level_indicator = "⬆️ LEVEL UP!" if step['leveled_up'] else ""
        badges = f" + Badges: {', '.join(step['badges_earned'])}" if step['badges_earned'] else ""
        print(f"  {step['simulation']}: +{step['xp_earned']} XP → {step['total_xp']} XP (Level {step['level']}) {level_indicator}{badges}")
    
    print()
    print("Final Stats:")
    print(f"  Total XP: {journey['final_stats']['total_xp']}")
    print(f"  Level: {journey['final_stats']['level']}")
    print(f"  Simulations: {journey['final_stats']['simulations_completed']}")
    print(f"  Badges: {journey['final_stats']['badges_earned']}")
    print()


def demo_badge_progression():
    """Demonstrate badge earning progression"""
    from backend.app.services.gamification import BadgeSystem, BadgeRarity
    
    badge_system = BadgeSystem()
    
    print("=== ALL BADGES BY RARITY ===")
    
    for rarity in BadgeRarity:
        badges = badge_system.get_badges_by_rarity(rarity)
        print(f"\n{rarity.value.upper()} ({len(badges)} badges):")
        for badge in badges:
            print(f"  {badge.icon} {badge.name}")
            print(f"     {badge.description}")
            print(f"     Unlock: {badge.hint}")
            print(f"     Reward: {badge.xp_reward} XP")
    
    print()


def demo_simulation_unlocks():
    """Demonstrate simulation unlock progression"""
    from backend.app.services.gamification import AchievementEngine
    
    engine = AchievementEngine()
    
    print("=== SIMULATION UNLOCK REQUIREMENTS ===")
    
    for level in range(1, 6):
        sims = engine.get_simulations_by_level(level)
        print(f"\nLevel {level} Simulations:")
        for sim in sims:
            print(f"  📚 {sim.name}")
            print(f"     {sim.description}")
            print(f"     Reward: {sim.xp_reward} XP | Time: {sim.estimated_time} | Difficulty: {sim.difficulty}")
            print(f"     Unlock: {sim.unlock_conditions[0].description}")
    
    print()


if __name__ == "__main__":
    print("🎮 GAMIFICATION SYSTEM DEMO 🎮\n")
    
    # Run demos
    demo_user_journey()
    print("\n" + "="*60 + "\n")
    
    demo_badge_progression()
    print("\n" + "="*60 + "\n")
    
    demo_simulation_unlocks()
