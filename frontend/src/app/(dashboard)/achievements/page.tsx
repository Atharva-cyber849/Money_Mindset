'use client'

import { Card } from '@/components/ui/Card'
import { BadgeGrid } from '@/components/ui/Badge'

const allBadges = [
  // Foundation Badges (Level 1)
  {
    id: 'coffee-calculator',
    title: 'Leak Detective',
    description: 'Discovered your spending leaks',
    icon: '☕',
    isUnlocked: true,
    rarity: 'common' as const,
  },
  {
    id: 'paycheck-pro',
    title: 'Paycheck Pro',
    description: 'Mastered income allocation',
    icon: '💵',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'common' as const,
  },
  {
    id: 'budget-master',
    title: 'Budget Master',
    description: 'Created a balanced budget',
    icon: '📊',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'common' as const,
  },
  {
    id: 'emergency-ready',
    title: 'Emergency Ready',
    description: 'Built $1,000 emergency fund',
    icon: '🛡️',
    isUnlocked: false,
    progress: 450,
    maxProgress: 1000,
    rarity: 'rare' as const,
  },

  // Debt Mastery Badges (Level 2)
  {
    id: 'interest-aware',
    title: 'Interest Aware',
    description: 'Understood credit card traps',
    icon: '💳',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'rare' as const,
  },
  {
    id: 'debt-strategist',
    title: 'Debt Strategist',
    description: 'Compared avalanche vs snowball',
    icon: '❄️',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'rare' as const,
  },
  {
    id: 'debt-destroyer',
    title: 'Debt Destroyer',
    description: 'Created debt payoff plan',
    icon: '🔥',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'epic' as const,
  },

  // Investing Badges (Level 3)
  {
    id: 'time-traveler',
    title: 'Time Traveler',
    description: 'Mastered compound interest',
    icon: '⏰',
    isUnlocked: true,
    rarity: 'epic' as const,
  },
  {
    id: 'risk-manager',
    title: 'Risk Manager',
    description: 'Understood risk vs reward',
    icon: '⚖️',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'epic' as const,
  },
  {
    id: 'index-fund-investor',
    title: 'Index Fund Investor',
    description: 'Learned passive investing',
    icon: '📈',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'epic' as const,
  },

  // Advanced Badges (Level 4)
  {
    id: 'retirement-planner',
    title: 'Retirement Planner',
    description: 'Created retirement roadmap',
    icon: '🏖️',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'legendary' as const,
  },
  {
    id: 'tax-optimizer',
    title: 'Tax Optimizer',
    description: 'Mastered tax-advantaged accounts',
    icon: '🎯',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'legendary' as const,
  },

  // Special Achievements
  {
    id: 'financial-graduate',
    title: 'Financial Graduate',
    description: 'Completed all 12 core simulations',
    icon: '🎓',
    isUnlocked: false,
    progress: 2,
    maxProgress: 12,
    rarity: 'legendary' as const,
  },
  {
    id: 'streak-master',
    title: 'Streak Master',
    description: '30-day learning streak',
    icon: '🔥',
    isUnlocked: false,
    progress: 7,
    maxProgress: 30,
    rarity: 'rare' as const,
  },
  {
    id: 'quick-learner',
    title: 'Quick Learner',
    description: 'Completed 5 simulations in one day',
    icon: '⚡',
    isUnlocked: false,
    progress: 2,
    maxProgress: 5,
    rarity: 'epic' as const,
  },
  {
    id: 'wealth-builder',
    title: 'Wealth Builder',
    description: 'Net worth increased 25%',
    icon: '💰',
    isUnlocked: false,
    progress: 12,
    maxProgress: 25,
    rarity: 'legendary' as const,
  },
]

export default function AchievementsPage() {
  const unlockedCount = allBadges.filter(b => b.isUnlocked).length
  const totalCount = allBadges.length

  const rarityCount = {
    common: allBadges.filter(b => b.rarity === 'common' && b.isUnlocked).length,
    rare: allBadges.filter(b => b.rarity === 'rare' && b.isUnlocked).length,
    epic: allBadges.filter(b => b.rarity === 'epic' && b.isUnlocked).length,
    legendary: allBadges.filter(b => b.rarity === 'legendary' && b.isUnlocked).length,
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Achievements</h1>
        <p className="text-lg text-gray-600">
          Unlock badges by completing simulations and reaching milestones
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="text-center bg-gradient-to-br from-blue-50 to-blue-100">
          <div className="text-3xl mb-2">🏆</div>
          <div className="text-2xl font-bold text-gray-900">
            {unlockedCount}/{totalCount}
          </div>
          <div className="text-sm text-gray-600">Total Unlocked</div>
        </Card>

        <Card className="text-center bg-gradient-to-br from-gray-50 to-gray-100">
          <div className="text-3xl mb-2">⚪</div>
          <div className="text-2xl font-bold text-gray-700">{rarityCount.common}</div>
          <div className="text-sm text-gray-600">Common</div>
        </Card>

        <Card className="text-center bg-gradient-to-br from-blue-50 to-blue-100">
          <div className="text-3xl mb-2">🔵</div>
          <div className="text-2xl font-bold text-blue-600">{rarityCount.rare}</div>
          <div className="text-sm text-gray-600">Rare</div>
        </Card>

        <Card className="text-center bg-gradient-to-br from-purple-50 to-purple-100">
          <div className="text-3xl mb-2">🟣</div>
          <div className="text-2xl font-bold text-purple-600">{rarityCount.epic}</div>
          <div className="text-sm text-gray-600">Epic</div>
        </Card>

        <Card className="text-center bg-gradient-to-br from-yellow-50 to-orange-100">
          <div className="text-3xl mb-2">🟠</div>
          <div className="text-2xl font-bold text-orange-600">{rarityCount.legendary}</div>
          <div className="text-sm text-gray-600">Legendary</div>
        </Card>
      </div>

      {/* Badge Grid */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">All Badges</h2>
        <BadgeGrid badges={allBadges} />
      </div>
    </div>
  )
}
