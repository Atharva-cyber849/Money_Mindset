"""
User Progress and Gamification API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.models.database import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()


# Response Models
class UserStatsResponse(BaseModel):
    total_xp: int
    current_level: int
    next_level_xp: int
    simulations_completed: int
    total_simulations: int
    current_streak: int
    longest_streak: int
    badges_earned: int
    achievements_unlocked: int


class SimulationStatus(BaseModel):
    id: str
    title: str
    description: str
    level: int
    level_name: str
    is_unlocked: bool
    is_completed: bool
    xp_reward: int
    estimated_time: str
    href: str
    color: str
    completion_count: int


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's gamification stats and progress"""
    
    # TODO: Get actual data from database
    # For now, return mock data that can be customized per user
    
    # Calculate level from XP (every 1000 XP = 1 level)
    total_xp = getattr(current_user, 'total_xp', 1250)
    current_level = (total_xp // 1000) + 1
    next_level_xp = current_level * 1000
    
    return {
        "total_xp": total_xp,
        "current_level": current_level,
        "next_level_xp": next_level_xp,
        "simulations_completed": 5,
        "total_simulations": 15,
        "current_streak": 7,
        "longest_streak": 12,
        "badges_earned": 3,
        "achievements_unlocked": 8
    }


@router.get("/simulations", response_model=List[SimulationStatus])
async def get_simulations_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all simulations with user's unlock and completion status"""
    
    # TODO: Get user's actual completion status from database
    # For now, returning structured simulation data
    
    simulations = [
        # LEVEL 1: FOUNDATION
        {
            "id": "coffee-shop-effect",
            "title": "The Coffee Shop Effect",
            "description": "Discover how small daily expenses compound over time",
            "level": 1,
            "level_name": "Foundation",
            "is_unlocked": True,
            "is_completed": False,
            "xp_reward": 100,
            "estimated_time": "5 min",
            "href": "/simulations/coffee-shop-effect",
            "color": "from-amber-400 to-orange-500",
            "completion_count": 0
        },
        {
            "id": "paycheck-game",
            "title": "The Paycheck Game",
            "description": "Learn income allocation and \"paying yourself first\"",
            "level": 1,
            "level_name": "Foundation",
            "is_unlocked": True,
            "is_completed": False,
            "xp_reward": 150,
            "estimated_time": "10 min",
            "href": "/simulations/paycheck-game",
            "color": "from-green-400 to-emerald-500",
            "completion_count": 0
        },
        {
            "id": "budget-builder",
            "title": "Budget Builder Challenge",
            "description": "Create a realistic 50/30/20 budget",
            "level": 1,
            "level_name": "Foundation",
            "is_unlocked": True,
            "is_completed": False,
            "xp_reward": 200,
            "estimated_time": "15 min",
            "href": "/simulations/budget-builder",
            "color": "from-blue-400 to-blue-600",
            "completion_count": 0
        },
        {
            "id": "emergency-fund",
            "title": "Emergency Fund Race",
            "description": "See why emergency funds prevent debt spirals",
            "level": 1,
            "level_name": "Foundation",
            "is_unlocked": False,
            "is_completed": False,
            "xp_reward": 250,
            "estimated_time": "12 min",
            "href": "/simulations/emergency-fund",
            "color": "from-purple-400 to-purple-600",
            "completion_count": 0
        },
        # LEVEL 2: DEBT MASTERY
        {
            "id": "credit-card-trap",
            "title": "The Credit Card Trap",
            "description": "How credit card interest compounds against you",
            "level": 2,
            "level_name": "Debt Mastery",
            "is_unlocked": False,
            "is_completed": False,
            "xp_reward": 300,
            "estimated_time": "10 min",
            "href": "/simulations/credit-card-debt",
            "color": "from-red-400 to-red-600",
            "completion_count": 0
        },
        {
            "id": "debt-strategies",
            "title": "Avalanche vs Snowball",
            "description": "Compare debt payoff strategies",
            "level": 2,
            "level_name": "Debt Mastery",
            "is_unlocked": False,
            "is_completed": False,
            "xp_reward": 350,
            "estimated_time": "15 min",
            "href": "/simulations/debt-strategies",
            "color": "from-indigo-400 to-indigo-600",
            "completion_count": 0
        },
        {
            "id": "debt-classification",
            "title": "Good Debt vs Bad Debt",
            "description": "Not all debt is created equal",
            "level": 2,
            "level_name": "Debt Mastery",
            "is_unlocked": False,
            "is_completed": False,
            "xp_reward": 400,
            "estimated_time": "20 min",
            "href": "/simulations/debt-classification",
            "color": "from-yellow-400 to-orange-500",
            "completion_count": 0
        },
        # LEVEL 3: SAVING & INVESTING
        {
            "id": "compound-interest",
            "title": "Compound Interest Time Machine",
            "description": "Time is your most powerful wealth-building tool",
            "level": 3,
            "level_name": "Saving & Investing",
            "is_unlocked": False,
            "is_completed": False,
            "xp_reward": 500,
            "estimated_time": "15 min",
            "href": "/simulations/compound-interest",
            "color": "from-cyan-400 to-blue-500",
            "completion_count": 0
        },
        {
            "id": "risk-reward",
            "title": "Risk vs Reward Adventure",
            "description": "Understanding investment risk tolerance",
            "level": 3,
            "level_name": "Saving & Investing",
            "is_unlocked": False,
            "is_completed": False,
            "xp_reward": 550,
            "estimated_time": "20 min",
            "href": "/simulations/risk-reward",
            "color": "from-purple-400 to-pink-500",
            "completion_count": 0
        },
        {
            "id": "index-fund-challenge",
            "title": "Index Fund Challenge",
            "description": "Why index funds beat active picking",
            "level": 3,
            "level_name": "Saving & Investing",
            "is_unlocked": False,
            "is_completed": False,
            "xp_reward": 600,
            "estimated_time": "25 min",
            "href": "/simulations/index-fund-challenge",
            "color": "from-green-400 to-teal-500",
            "completion_count": 0
        },
        # LEVEL 4: ADVANCED
        {
            "id": "retirement-calculator",
            "title": "Retirement Reality Check",
            "description": "How much you actually need to retire",
            "level": 4,
            "level_name": "Advanced",
            "is_unlocked": False,
            "is_completed": False,
            "xp_reward": 700,
            "estimated_time": "20 min",
            "href": "/simulations/retirement-calculator",
            "color": "from-emerald-400 to-green-600",
            "completion_count": 0
        },
        {
            "id": "tax-optimizer",
            "title": "Tax-Advantaged Optimizer",
            "description": "Understanding 401(k), IRA, Roth, HSA benefits",
            "level": 4,
            "level_name": "Advanced",
            "is_unlocked": False,
            "is_completed": False,
            "xp_reward": 800,
            "estimated_time": "25 min",
            "href": "/simulations/tax-optimizer",
            "color": "from-blue-400 to-indigo-600",
            "completion_count": 0
        }
    ]
    
    return simulations


@router.post("/simulations/{simulation_id}/complete")
async def mark_simulation_complete(
    simulation_id: str,
    perfect_score: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a simulation as completed and award XP"""
    
    # TODO: Implement actual database update and XP calculation
    # For now, return success
    
    return {
        "success": True,
        "message": f"Simulation '{simulation_id}' marked as completed",
        "xp_earned": 100,
        "new_total_xp": 1350
    }
