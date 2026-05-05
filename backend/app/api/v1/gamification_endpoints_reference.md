"""
Gamification API Endpoints Documentation
Complete reference for all new gamification endpoints
"""

# ============================================================================
# GAME SESSION MANAGEMENT
# ============================================================================

"""
POST /api/v1/gamification/sessions/start
Start a new game session with adaptive difficulty

Request:
{
    "session_id": "session_123",
    "game_type": "paper_trading",
    "requested_difficulty": "normal"  # Optional: tutorial, easy, normal, hard, expert
}

Response:
{
    "session_id": "session_123",
    "difficulty": "normal",
    "modifiers": {
        "market_volatility": 1.0,
        "ai_aggressiveness": 0.6,
        "time_pressure": 0.6,
        "mistake_tolerance": 0.6,
        "xp_multiplier": 1.0,
        "hint_availability": false,
        "starting_capital": 1000000,
        "event_frequency": 0.6
    },
    "tutorial": {...},  # null if not tutorial mode
    "daily_bonus_xp": 50,
    "current_streak": 5,
    "next_milestone": {
        "milestone_day": 7,
        "days_until": 2,
        "bonus_xp": 250
    },
    "recommended_difficulty": "hard"
}

---

POST /api/v1/gamification/sessions/end
End game session and calculate all rewards

Request:
{
    "session_id": "session_123",
    "game_type": "paper_trading",
    "ending_capital": 1250000,
    "performance_metrics": {
        "win_rate": 0.65,
        "decision_quality": 0.75,
        "decisions_per_minute": 0.5,
        "accuracy": 0.70
    }
}

Response:
{
    "xp_earned": 450,
    "new_level": 2,
    "achievements_unlocked": [
        {
            "id": "first_profitable_trade",
            "name": "First Profitable Trade",
            "xp_reward": 100,
            "rarity": "uncommon"
        }
    ],
    "difficulty_recommendation": "hard",
    "performance_score": 0.82,
    "session_summary": {...},
    "career_recommendations": [...]
}
"""

# ============================================================================
# DIFFICULTY & PROGRESSION
# ============================================================================

"""
GET /api/v1/gamification/difficulty/{game_type}
Get difficulty recommendation for a game

Response:
{
    "current": "normal",
    "recommendation": "hard",
    "reason": "You're mastering this difficulty!"
}

---

POST /api/v1/gamification/difficulty/{game_type}/set
Set specific difficulty for a game

Request:
{
    "difficulty": "hard"
}

Response:
{
    "difficulty": "hard",
    "message": "Difficulty set to hard"
}
"""

# ============================================================================
# ACHIEVEMENTS & CHAINS
# ============================================================================

"""
GET /api/v1/gamification/achievements
Get all achievements and progress

Response:
{
    "total_unlocked": 8,
    "chains": [
        {
            "chain_id": "trading_mastery",
            "name": "Trading Mastery",
            "completed_steps": 3,
            "total_steps": 5,
            "progress_percentage": 60.0,
            "next_achievement": "portfolio_milestone_1",
            "is_complete": false,
            "reward": null
        },
        {
            "chain_id": "savings_hero",
            "name": "Savings Hero",
            "completed_steps": 5,
            "total_steps": 5,
            "progress_percentage": 100.0,
            "is_complete": true,
            "reward": {
                "badge_id": "savings_hero",
                "badge_name": "Savings Hero",
                "bonus_xp": 1500
            }
        }
    ],
    "next_possible_achievements": [
        {
            "id": "portfolio_milestone_1",
            "name": "Portfolio ₹5L",
            "category": "trading",
            "rarity": "uncommon",
            "xp_reward": 300
        }
    ]
}

---

POST /api/v1/gamification/achievements/{achievement_id}/unlock
Unlock an achievement (backend validation)

Response:
{
    "achievement_id": "first_trade",
    "name": "First Trade",
    "xp_reward": 100
}

---

POST /api/v1/gamification/achievements/{achievement_id}/share
Share achievement with friends

Response:
{
    "share_url": "share/user123/first_trade/1712234567.0",
    "title": "First Trade",
    "description": "Execute your first stock trade"
}
"""

# ============================================================================
# STREAKS & DAILY BONUSES
# ============================================================================

"""
GET /api/v1/gamification/streaks
Get all user streaks

Response:
{
    "daily_login": {
        "current_streak": 5,
        "longest_streak": 12,
        "is_active": true,
        "last_activity": "2026-04-04",
        "milestones": [7],
        "total_bonus_xp": 250
    },
    "game_plays": {
        "current_streak": 3,
        "longest_streak": 8,
        "is_active": true,
        "last_activity": "2026-04-04",
        "milestones": [],
        "total_bonus_xp": 75
    }
}

---

POST /api/v1/gamification/daily-bonus/claim
Claim daily login bonus

Response:
{
    "bonus_xp": 50,
    "current_streak": 5,
    "can_claim": true,
    "milestone": {
        "milestone_day": 7,
        "bonus_xp": 250,
        "description": "1-WEEK STREAK! +250 XP"
    }
}

---

GET /api/v1/gamification/events/seasonal/{event_name}
Get seasonal event bonus

Response:
{
    "event_active": true,
    "bonus_xp": 500,
    "description": "Diwali Savings Race - Save smart for the festival!"
}
"""

# ============================================================================
# LEADERBOARDS
# ============================================================================

"""
GET /api/v1/gamification/leaderboards?category=total_xp&period=monthly&view=top
Get leaderboard

Query Parameters:
- category: total_xp, trading_score, business_empire, savings_master, 
            achievement_collector, streak_master, wealth, challenge_champion
- period: daily, weekly, monthly, all_time
- view: top (default), nearby, friends

Response:
{
    "category": "total_xp",
    "period": "monthly",
    "last_updated": "2026-04-04T12:30:00",
    "entries": [
        {
            "rank": 1,
            "username": "Ajay",
            "score": 5000,
            "badges": 12,
            "trend": "up"
        },
        {
            "rank": 2,
            "username": "Priya",
            "score": 4800,
            "badges": 10,
            "trend": "unchanged"
        }
    ]
}

---

GET /api/v1/gamification/leaderboards/friends?category=trading_score
Get friend leaderboard

Response:
[
    {
        "username": "Your Name",
        "score": 3500,
        "rank": 3,
        "period": "monthly"
    },
    {
        "username": "Friend 1",
        "score": 4200,
        "rank": 2,
        "period": "monthly"
    }
]
"""

# ============================================================================
# SOCIAL FEATURES
# ============================================================================

"""
POST /api/v1/gamification/friends/{friend_id}/add
Add friend

Response:
{
    "success": true,
    "friend_id": "user456",
    "username": "Priya"
}

---

GET /api/v1/gamification/social/feed
Get social feed from friends

Response:
[
    {
        "username": "Ajay",
        "content_type": "achievement",
        "title": "Trading Expert",
        "description": "Just unlocked: Trading Expert 🎯",
        "created_at": "2026-04-04T10:30:00",
        "data": {
            "icon": "👑"
        }
    },
    {
        "username": "Priya",
        "content_type": "milestone",
        "title": "Portfolio ₹10L",
        "description": "🏆 Achieved milestone: Portfolio ₹10L",
        "created_at": "2026-04-04T09:15:00"
    }
]

---

POST /api/v1/gamification/friends/{friend_id}/invite-challenge
Invite friend to challenge

Request:
{
    "challenge_id": "diwali_race_2026"
}

Response:
{
    "success": true,
    "challenge_id": "diwali_race_2026",
    "participants": ["user123", "user456"]
}

---

GET /api/v1/gamification/friends/{friend_id}/compare
Compare stats with friend

Response:
{
    "user": {
        "username": "Your Name",
        "xp": 3500,
        "badges": 8,
        "favorite_game": "paper_trading"
    },
    "friend": {
        "username": "Priya",
        "xp": 4200,
        "badges": 10,
        "favorite_game": "dalal_street"
    },
    "comparison": {
        "xp_difference": -700,
        "badge_difference": -2
    }
}
"""

# ============================================================================
# AI COMPETITIONS
# ============================================================================

"""
POST /api/v1/gamification/competitions/start
Start competition with AI opponents

Request:
{
    "competition_id": "comp_001",
    "game_type": "paper_trading",
    "difficulty": "hard"
}

Response:
[
    {
        "ai_id": "ai_hard_1",
        "name": "Expert Trader",
        "personality": "opportunist",
        "skill_level": 0.95
    },
    {
        "ai_id": "ai_hard_2",
        "name": "Master Strategist",
        "personality": "balanced",
        "skill_level": 0.9
    }
]

---

GET /api/v1/gamification/competitions/{competition_id}/round
Get current competition round

Response:
{
    "round_number": 3,
    "decisions": {
        "ai_hard_1": {
            "action": "buy",
            "amount": 80000,
            "confidence": 0.95,
            "reasoning": "High volatility = opportunity to buy"
        }
    }
}

---

POST /api/v1/gamification/competitions/{competition_id}/end
End competition

Request:
{
    "player_final_score": 1250000,
    "player_rank": 2,
    "total_players": 3
}

Response:
{
    "result": "✨ Great performance! Top half finish",
    "player_rank": 2,
    "player_score": 1250000,
    "total_competitors": 3,
    "bonus_xp": 500,
    "leaderboard": [...]
}
"""

# ============================================================================
# ANALYTICS & REPORTING
# ============================================================================

"""
GET /api/v1/gamification/analytics/session/{session_id}
Get session analytics

Response:
{
    "session_id": "session_123",
    "game_type": "paper_trading",
    "difficulty": "hard",
    "duration_minutes": 45.5,
    "profit_loss": 250000,
    "roi": 25.0,
    "total_decisions": 15,
    "decision_accuracy": 73.3,
    "average_decision_quality": 0.65,
    "learning_improvement": 0.15,
    "win_streak": 5,
    "xp_earned": 500,
    "achievement": "portfolio_milestone_1"
}

---

GET /api/v1/gamification/analytics/learning-curve?game_type=paper_trading
Get learning curve analysis

Response:
{
    "mastery_level": {
        "level": "advanced",
        "score": 72.5,
        "avg_roi": 18.5,
        "avg_accuracy": 0.68,
        "sessions_played": 12
    },
    "improvement_trend": {
        "trend": "improving",
        "roi_change": 5.2,
        "roi_change_percentage": 15.3,
        "average_roi": 18.5,
        "sessions_analyzed": 5
    },
    "recommendation": "📈 You're improving! Keep practicing with your current difficulty."
}

---

POST /api/v1/gamification/analytics/export-report
Generate PDF report

Request:
{
    "session_id": "session_123",
    "format": "pdf"  # or "json"
}

Response:
(PDF file or JSON report)
"""

# ============================================================================
# CROSS-GAME FEATURES
# ============================================================================

"""
GET /api/v1/gamification/cross-game/portfolio
Get persistent portfolio

Response:
{
    "portfolio_value": 1500000,
    "total_holdings": 5,
    "holdings": [
        {
            "symbol": "RELIANCE",
            "quantity": 10,
            "entry_price": 2500,
            "current_price": 2750,
            "unrealized_gain": 2500,
            "source_game": "paper_trading"
        }
    ],
    "total_invested": 1200000,
    "total_gains": 300000,
    "creation_date": "2026-03-01"
}

---

GET /api/v1/gamification/cross-game/summary
Get comprehensive cross-game summary

Response:
{
    "portfolio_value": 1500000,
    "total_holdings": 5,
    "portfolio_return": 25.0,
    "career_milestones_completed": 3,
    "games_unlocked": [
        "coffee_shop",
        "paycheck_game",
        "budget_builder",
        "paper_trading",
        "dalal_street"
    ],
    "portfolio_insights": [
        "💎 Significant Portfolio: Over ₹50 Lakh invested",
        "📈 Strong Performance: Over 50% return"
    ],
    "recommendations": [
        "🎓 Try Paper Trading - Practice stock market investing risk-free"
    ]
}
"""

# ============================================================================
# USER DASHBOARD
# ============================================================================

"""
GET /api/v1/gamification/dashboard
Get complete user dashboard

Response:
{
    "user_stats": {
        "total_xp": 3500,
        "level": 4,
        "total_sessions": 25,
        "lifetime_earnings": 500000
    },
    "current_streaks": {
        "daily_login": {
            "current_streak": 5,
            "longest_streak": 12,
            "is_active": true
        }
    },
    "achievement_progress": {
        "total_unlocked": 8,
        "chains": [...],
        "next_possible_achievements": [...]
    },
    "cross_game_summary": {...},
    "upcoming_challenges": [
        {
            "name": "Diwali Savings Race",
            "description": "Save ₹50,000 in one week",
            "reward_xp": 1000,
            "active": true
        }
    ],
    "leaderboard_position": {
        "rank": 45,
        "category": "all_time",
        "score": 3500
    },
    "recommendations": [
        "🔥 Build a 7-day login streak for bonus XP"
    ]
}
"""
