"""
Social & Leaderboard System
Manages leaderboards, achievements sharing, friend interactions, and social features
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum


class LeaderboardPeriod(Enum):
    """Leaderboard time periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


class LeaderboardCategory(Enum):
    """Leaderboard categories"""
    TOTAL_XP = "total_xp"  # Overall XP earned
    TRADING_SCORE = "trading_score"  # Paper trading + Dalal Street combined
    BUSINESS_EMPIRE = "business_empire"  # Karobaar revenue/profit
    SAVINGS_MASTER = "savings_master"  # Emergency fund + savings amount
    ACHIEVEMENT_COLLECTOR = "achievement_collector"  # Total achievements
    STREAK_MASTER = "streak_master"  # Current & all-time streaks
    WEALTH = "wealth"  # Total portfolio value
    CHALLENGE_CHAMPION = "challenge_champion"  # Current seasonal challenge


@dataclass
class LeaderboardEntry:
    """Entry on a leaderboard"""
    rank: int
    user_id: str
    username: str
    score: float
    badge_count: int
    trend: str  # "up", "down", "new", "unchanged"
    previous_rank: Optional[int] = None


@dataclass
class SocialProfile:
    """User's social profile for sharing"""
    user_id: str
    username: str
    profile_badge_count: int
    current_xp: int
    favorite_game: str
    bio: Optional[str] = None
    can_share: bool = True
    share_achievements: bool = True


@dataclass
class Achievement:
    """Shared achievement data"""
    id: str
    name: str
    icon: str
    description: str
    unlocked_date: datetime


@dataclass
class ShareableContent:
    """Content that can be shared"""
    content_type: str  # "achievement", "score", "milestone", "challenge_win"
    title: str
    description: str
    data: Dict
    user_id: str
    created_at: datetime
    share_url: str  # Short link for sharing


class Leaderboard:
    """Individual leaderboard"""

    def __init__(self, category: LeaderboardCategory, period: LeaderboardPeriod):
        self.category = category
        self.period = period
        self.entries: List[LeaderboardEntry] = []
        self.last_updated = datetime.now()

    def add_entry(
        self,
        user_id: str,
        username: str,
        score: float,
        badge_count: int = 0,
        previous_rank: Optional[int] = None,
    ):
        """Add or update an entry"""
        # Remove existing entry if present
        self.entries = [e for e in self.entries if e.user_id != user_id]

        # Determine trend
        if previous_rank is None:
            trend = "new"
        elif len(self.entries) == 0:
            trend = "new"
        else:
            current_rank = len(self.entries) + 1
            if current_rank < previous_rank:
                trend = "up"
            elif current_rank > previous_rank:
                trend = "down"
            else:
                trend = "unchanged"

        entry = LeaderboardEntry(
            rank=len(self.entries) + 1,
            user_id=user_id,
            username=username,
            score=score,
            badge_count=badge_count,
            trend=trend,
            previous_rank=previous_rank,
        )
        self.entries.append(entry)
        self.entries.sort(key=lambda x: x.score, reverse=True)

        # Update ranks after sorting
        for i, e in enumerate(self.entries):
            e.rank = i + 1

    def get_entry(self, user_id: str) -> Optional[LeaderboardEntry]:
        """Get user's entry"""
        for entry in self.entries:
            if entry.user_id == user_id:
                return entry
        return None

    def get_top_entries(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top entries"""
        return self.entries[:limit]

    def get_nearby_entries(self, user_id: str, radius: int = 5) -> List[LeaderboardEntry]:
        """Get entries near user's rank"""
        user_entry = self.get_entry(user_id)
        if not user_entry:
            return []

        start_idx = max(0, user_entry.rank - radius - 1)
        end_idx = min(len(self.entries), user_entry.rank + radius)
        return self.entries[start_idx:end_idx]


class SocialSystem:
    """
    Manages social features, leaderboards, and friend interactions
    """

    def __init__(self):
        self.leaderboards: Dict[str, Leaderboard] = {}
        self.social_profiles: Dict[str, SocialProfile] = {}
        self.friendships: Dict[str, Set[str]] = {}  # user_id -> set of friend user_ids
        self.shared_achievements: Dict[str, List[ShareableContent]] = {}
        self.challenge_participants: Dict[str, Set[str]] = {}  # challenge_id -> user_ids

    def create_leaderboards(self):
        """Initialize all leaderboards"""
        for category in LeaderboardCategory:
            for period in LeaderboardPeriod:
                key = f"{category.value}_{period.value}"
                self.leaderboards[key] = Leaderboard(category, period)

    def update_user_leaderboard(
        self,
        user_id: str,
        username: str,
        category: LeaderboardCategory,
        score: float,
        badge_count: int = 0,
    ):
        """Update user on all leaderboards of a category"""
        for period in LeaderboardPeriod:
            key = f"{category.value}_{period.value}"
            if key not in self.leaderboards:
                self.leaderboards[key] = Leaderboard(category, period)

            leaderboard = self.leaderboards[key]
            current_entry = leaderboard.get_entry(user_id)
            previous_rank = current_entry.rank if current_entry else None

            leaderboard.add_entry(
                user_id=user_id,
                username=username,
                score=score,
                badge_count=badge_count,
                previous_rank=previous_rank,
            )

    def get_leaderboard(
        self,
        category: LeaderboardCategory,
        period: LeaderboardPeriod,
        view: str = "top",  # "top", "nearby" for user_id context
        user_id: Optional[str] = None,
    ) -> Dict:
        """Get leaderboard data"""
        key = f"{category.value}_{period.value}"
        leaderboard = self.leaderboards.get(key)

        if not leaderboard:
            return {"error": "Leaderboard not found"}

        if view == "top":
            entries = leaderboard.get_top_entries(20)
        elif view == "nearby" and user_id:
            entries = leaderboard.get_nearby_entries(user_id, radius=10)
        else:
            entries = leaderboard.get_top_entries(20)

        return {
            "category": category.value,
            "period": period.value,
            "last_updated": leaderboard.last_updated.isoformat(),
            "entries": [
                {
                    "rank": e.rank,
                    "username": e.username,
                    "score": e.score,
                    "badges": e.badge_count,
                    "trend": e.trend,
                }
                for e in entries
            ],
        }

    def add_friend(self, user_id: str, friend_id: str) -> bool:
        """Add friend (bidirectional)"""
        if user_id == friend_id:
            return False

        if user_id not in self.friendships:
            self.friendships[user_id] = set()
        if friend_id not in self.friendships:
            self.friendships[friend_id] = set()

        self.friendships[user_id].add(friend_id)
        self.friendships[friend_id].add(user_id)
        return True

    def remove_friend(self, user_id: str, friend_id: str) -> bool:
        """Remove friend (bidirectional)"""
        if user_id in self.friendships:
            self.friendships[user_id].discard(friend_id)
        if friend_id in self.friendships:
            self.friendships[friend_id].discard(user_id)
        return True

    def get_friends(self, user_id: str) -> List[str]:
        """Get list of friends"""
        return list(self.friendships.get(user_id, set()))

    def get_friend_leaderboard(
        self, user_id: str, category: LeaderboardCategory
    ) -> List[Dict]:
        """Get leaderboard filtered to friends only"""
        friends = self.get_friends(user_id)
        friends.append(user_id)  # Include user

        result = []
        for period in LeaderboardPeriod:
            key = f"{category.value}_{period.value}"
            leaderboard = self.leaderboards.get(key)
            if not leaderboard:
                continue

            for entry in leaderboard.entries:
                if entry.user_id in friends:
                    result.append(
                        {
                            "username": entry.username,
                            "score": entry.score,
                            "rank": entry.rank,
                            "period": period.value,
                        }
                    )

        return result

    def share_achievement(
        self, user_id: str, achievement: Achievement, audience: str = "friends"
    ) -> ShareableContent:
        """Share an achievement with friends or publicly"""
        share_url = f"share/{user_id}/{achievement.id}/{datetime.now().timestamp()}"

        shareable = ShareableContent(
            content_type="achievement",
            title=achievement.name,
            description=f"Just unlocked: {achievement.name} 🎯",
            data={
                "achievement_id": achievement.id,
                "icon": achievement.icon,
                "description": achievement.description,
            },
            user_id=user_id,
            created_at=datetime.now(),
            share_url=share_url,
        )

        if user_id not in self.shared_achievements:
            self.shared_achievements[user_id] = []

        self.shared_achievements[user_id].append(shareable)
        return shareable

    def share_milestone(
        self, user_id: str, milestone_name: str, milestone_data: Dict
    ) -> ShareableContent:
        """Share a milestone achievement"""
        share_url = f"share/{user_id}/milestone/{datetime.now().timestamp()}"

        shareable = ShareableContent(
            content_type="milestone",
            title=milestone_name,
            description=f"🏆 Achieved milestone: {milestone_name}",
            data=milestone_data,
            user_id=user_id,
            created_at=datetime.now(),
            share_url=share_url,
        )

        if user_id not in self.shared_achievements:
            self.shared_achievements[user_id] = []

        self.shared_achievements[user_id].append(shareable)
        return shareable

    def get_shared_feed(self, user_id: str) -> List[Dict]:
        """Get social feed of friends' shared content"""
        friends = self.get_friends(user_id)
        feed = []

        for friend_id in friends:
            if friend_id in self.shared_achievements:
                for content in self.shared_achievements[friend_id]:
                    friend_profile = self.social_profiles.get(friend_id)
                    feed.append(
                        {
                            "username": friend_profile.username if friend_profile else friend_id,
                            "content_type": content.content_type,
                            "title": content.title,
                            "description": content.description,
                            "created_at": content.created_at.isoformat(),
                            "data": content.data,
                        }
                    )

        # Sort by newest first
        feed.sort(key=lambda x: x["created_at"], reverse=True)
        return feed[:20]  # Return latest 20

    def invite_friend_to_challenge(
        self, user_id: str, friend_id: str, challenge_id: str
    ) -> bool:
        """Invite friend to competitive challenge"""
        if challenge_id not in self.challenge_participants:
            self.challenge_participants[challenge_id] = set()

        # Assume friend accepts for now
        self.challenge_participants[challenge_id].add(user_id)
        self.challenge_participants[challenge_id].add(friend_id)
        return True

    def get_challenge_participants(self, challenge_id: str) -> List[str]:
        """Get list of participants in a challenge"""
        return list(self.challenge_participants.get(challenge_id, set()))

    def get_friend_stats_comparison(
        self, user_id: str, friend_id: str
    ) -> Dict[str, Any]:
        """Compare stats between two friends"""
        user_profile = self.social_profiles.get(user_id)
        friend_profile = self.social_profiles.get(friend_id)

        if not user_profile or not friend_profile:
            return {"error": "Profile not found"}

        return {
            "user": {
                "username": user_profile.username,
                "xp": user_profile.current_xp,
                "badges": user_profile.badge_count,
                "favorite_game": user_profile.favorite_game,
            },
            "friend": {
                "username": friend_profile.username,
                "xp": friend_profile.current_xp,
                "badges": friend_profile.badge_count,
                "favorite_game": friend_profile.favorite_game,
            },
            "comparison": {
                "xp_difference": user_profile.current_xp - friend_profile.current_xp,
                "badge_difference": user_profile.badge_count - friend_profile.badge_count,
            },
        }
