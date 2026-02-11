'use client'

import { motion } from 'framer-motion'
import { Trophy, Star, Lock, TrendingUp, Zap } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { BadgeGrid } from '@/components/ui/Badge'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { formatNumber } from '@/lib/utils'

// Badge definitions
const badges = [
  {
    id: 'coffee-calculator',
    title: 'Leak Detective',
    description: 'Discovered your spending leaks',
    icon: '☕',
    isUnlocked: true,
    rarity: 'common' as const,
  },
  {
    id: 'budget-master',
    title: 'Budget Master',
    description: 'Created your first budget',
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
  {
    id: 'debt-destroyer',
    title: 'Debt Destroyer',
    description: 'Completed debt payoff plan',
    icon: '💳',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'rare' as const,
  },
  {
    id: 'investor',
    title: 'Investor',
    description: 'Started your first investment',
    icon: '📈',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'epic' as const,
  },
  {
    id: 'time-traveler',
    title: 'Time Traveler',
    description: 'Mastered compound interest',
    icon: '⏰',
    isUnlocked: true,
    rarity: 'epic' as const,
  },
  {
    id: 'retirement-planner',
    title: 'Retirement Planner',
    description: 'Created retirement roadmap',
    icon: '🏖️',
    isUnlocked: false,
    progress: 0,
    maxProgress: 1,
    rarity: 'epic' as const,
  },
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

// Level definitions
const levels = [
  { level: 1, name: 'Financial Newbie', minXP: 0, maxXP: 1000, color: 'gray' },
  { level: 2, name: 'Money Learner', minXP: 1000, maxXP: 2500, color: 'blue' },
  { level: 3, name: 'Budget Pro', minXP: 2500, maxXP: 5000, color: 'green' },
  { level: 4, name: 'Debt Slayer', minXP: 5000, maxXP: 10000, color: 'purple' },
  { level: 5, name: 'Investment Guru', minXP: 10000, maxXP: 20000, color: 'yellow' },
  { level: 6, name: 'Financial Master', minXP: 20000, maxXP: 999999, color: 'orange' },
]

export default function ProgressPage() {
  // Mock user data - in production, fetch from API
  const userData = {
    currentXP: 1250,
    currentLevel: 2,
    simulationsCompleted: 2,
    totalSimulations: 15,
    currentStreak: 7,
    longestStreak: 12,
    totalTimeSpent: 180, // minutes
    badgesUnlocked: 2,
    totalBadges: 10,
  }

  const currentLevelData = levels.find(l => l.level === userData.currentLevel)!
  const nextLevelData = levels.find(l => l.level === userData.currentLevel + 1)!
  
  const levelProgress = ((userData.currentXP - currentLevelData.minXP) / (currentLevelData.maxXP - currentLevelData.minXP)) * 100
  const xpToNextLevel = nextLevelData.maxXP - userData.currentXP

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Progress</h1>
        <p className="text-lg text-gray-600">Track your journey to financial mastery</p>
      </div>

      {/* Level Card */}
      <Card className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="text-sm text-blue-100 mb-1">Current Level</div>
            <h2 className="text-4xl font-bold">Level {userData.currentLevel}</h2>
            <p className="text-xl text-blue-100">{currentLevelData.name}</p>
          </div>
          <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
            <Trophy className="w-12 h-12 text-yellow-300" />
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-blue-100">
              {formatNumber(userData.currentXP)} XP
            </span>
            <span className="text-blue-100">
              {formatNumber(nextLevelData.maxXP)} XP
            </span>
          </div>
          <ProgressBar percent={levelProgress} color="blue" height="h-4" />
          <p className="text-sm text-blue-100 text-center">
            {formatNumber(xpToNextLevel)} XP to {nextLevelData.name}
          </p>
        </div>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center bg-gradient-to-br from-green-50 to-emerald-50">
          <div className="text-3xl mb-2">✅</div>
          <div className="text-2xl font-bold text-gray-900">
            {userData.simulationsCompleted}/{userData.totalSimulations}
          </div>
          <div className="text-sm text-gray-600">Simulations</div>
        </Card>

        <Card className="text-center bg-gradient-to-br from-orange-50 to-red-50">
          <div className="text-3xl mb-2">🔥</div>
          <div className="text-2xl font-bold text-gray-900">
            {userData.currentStreak}
          </div>
          <div className="text-sm text-gray-600">Day Streak</div>
        </Card>

        <Card className="text-center bg-gradient-to-br from-purple-50 to-pink-50">
          <div className="text-3xl mb-2">🏆</div>
          <div className="text-2xl font-bold text-gray-900">
            {userData.badgesUnlocked}/{userData.totalBadges}
          </div>
          <div className="text-sm text-gray-600">Badges</div>
        </Card>

        <Card className="text-center bg-gradient-to-br from-blue-50 to-cyan-50">
          <div className="text-3xl mb-2">⏱️</div>
          <div className="text-2xl font-bold text-gray-900">
            {Math.floor(userData.totalTimeSpent / 60)}h {userData.totalTimeSpent % 60}m
          </div>
          <div className="text-sm text-gray-600">Learning Time</div>
        </Card>
      </div>

      {/* Level Progression Roadmap */}
      <Card>
        <h3 className="text-xl font-bold text-gray-900 mb-6">Level Progression</h3>
        <div className="space-y-4">
          {levels.map((level, index) => {
            const isCompleted = userData.currentLevel > level.level
            const isCurrent = userData.currentLevel === level.level
            const isLocked = userData.currentLevel < level.level

            return (
              <motion.div
                key={level.level}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-center gap-4 p-4 rounded-lg border-2 ${
                  isCurrent
                    ? 'bg-blue-50 border-blue-500'
                    : isCompleted
                    ? 'bg-green-50 border-green-300'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                {/* Level Number */}
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
                    isCurrent
                      ? 'bg-blue-500 text-white'
                      : isCompleted
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-300 text-gray-600'
                  }`}
                >
                  {isCompleted ? '✓' : level.level}
                </div>

                {/* Level Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-bold text-gray-900">{level.name}</h4>
                    {isCurrent && (
                      <span className="px-2 py-1 bg-blue-500 text-white text-xs font-semibold rounded-full">
                        Current
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">
                    {formatNumber(level.minXP)} - {formatNumber(level.maxXP)} XP
                  </p>
                </div>

                {/* Status Icon */}
                <div>
                  {isCompleted && <Star className="w-6 h-6 text-yellow-500 fill-yellow-500" />}
                  {isCurrent && <Zap className="w-6 h-6 text-blue-500" />}
                  {isLocked && <Lock className="w-6 h-6 text-gray-400" />}
                </div>
              </motion.div>
            )
          })}
        </div>
      </Card>

      {/* Achievements Section */}
      <div>
        <h3 className="text-2xl font-bold text-gray-900 mb-4">Achievements & Badges</h3>
        <BadgeGrid badges={badges} />
      </div>

      {/* Recent Activity */}
      <Card>
        <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
              <Trophy className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900">Unlocked "Time Traveler" badge</p>
              <p className="text-sm text-gray-600">2 hours ago</p>
            </div>
            <span className="text-green-600 font-bold">+500 XP</span>
          </div>

          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900">Completed "Compound Interest" simulation</p>
              <p className="text-sm text-gray-600">2 hours ago</p>
            </div>
            <span className="text-blue-600 font-bold">+500 XP</span>
          </div>

          <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
            <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900">7-day streak! 🔥</p>
              <p className="text-sm text-gray-600">Today</p>
            </div>
            <span className="text-orange-600 font-bold">+50 XP</span>
          </div>

          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
              <Trophy className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900">Unlocked "Leak Detective" badge</p>
              <p className="text-sm text-gray-600">1 day ago</p>
            </div>
            <span className="text-green-600 font-bold">+100 XP</span>
          </div>
        </div>
      </Card>
    </div>
  )
}
