'use client'

import { useState, useEffect } from 'react'
import {
  TrendingUp,
  Zap,
  MessageSquare,
  Trophy,
  Target
} from 'lucide-react'
import { StatCard } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { ProgressBar } from '@/components/ui/ProgressBar'
import MarketWidget from '@/components/dashboard/MarketWidget'
import { getUserStats, UserStats } from '@/lib/api/progress'
import { userAPI } from '@/lib/api/client'
import { useMarketData } from '@/lib/api/hooks'
import { gamesCatalog } from '@/lib/data/games'
import GameSection from '@/components/dashboard/GameSection'
import SimulationSection from '@/components/dashboard/SimulationSection'

interface FinanceProfile {
  finance_iq_score: number
  money_personality: string
  recommended_first_sim: string
}

export default function DashboardPage() {
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [financeProfile, setFinanceProfile] = useState<FinanceProfile | null>(null)

  // Fetch market data
  const { data: marketData } = useMarketData(8)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stats, profile] = await Promise.all([
          getUserStats(),
          userAPI.getFinancialProfile().catch(() => null) // Don't fail if profile doesn't exist
        ])
        setUserStats(stats)
        if (profile) {
          setFinanceProfile(profile)
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
      }
    }

    fetchData()
  }, [])

  // Show loading state only for initial render
  if (!userStats) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Loading Banner */}
        <div className="bg-gradient-to-r from-cyan-600 to-purple-600 rounded-2xl p-8 text-white h-32 animate-pulse" />
        
        {/* Loading Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-32 animate-pulse" />
          ))}
        </div>

        {/* Loading Card */}
        <div className="bg-gray-200 rounded-lg h-48 animate-pulse" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="bg-gradient-to-r from-cyan-500 to-blue-500 p-6 text-white">
          <h1 className="text-2xl font-bold mb-1">Welcome Back! 👋</h1>
          <p className="text-cyan-100 text-sm mb-4">
            You're on a {userStats.current_streak}-day streak! Keep building your financial future.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button variant="primary" className="bg-white text-cyan-600 hover:bg-gray-50 text-sm">
              Continue Learning
            </Button>
            <Button variant="outline" className="border-white text-white hover:bg-white/10 text-sm">
              <MessageSquare className="w-4 h-4" />
              Ask AI Tutor
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Current Level"
          value={`Level ${userStats.current_level}`}
          icon={Trophy}
          iconColor="bg-yellow-500"
          change={undefined}
          animate={true}
        />
        <StatCard
          title="Total XP"
          value={userStats.total_xp.toLocaleString()}
          icon={Zap}
          iconColor="bg-purple-500"
          change={undefined}
          animate={true}
        />
        <StatCard
          title="Completed"
          value={`${userStats.simulations_completed}/${userStats.total_simulations}`}
          icon={Target}
          iconColor="bg-green-500"
          change={undefined}
          animate={true}
        />
        <StatCard
          title="Streak"
          value={`${userStats.current_streak} days`}
          icon={TrendingUp}
          iconColor="bg-cyan-500"
          trend="up"
          animate={true}
        />
      </div>

      {/* Finance IQ Card */}
      {financeProfile && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between gap-6">
            <div>
              <p className="text-xs text-gray-600 mb-2 font-medium">Finance IQ Score</p>
              <h3 className="text-3xl font-bold text-gray-900">{Math.round(financeProfile.finance_iq_score)}<span className="text-lg text-gray-600">/100</span></h3>
              <p className="text-xs text-gray-500 mt-2">Grows with every challenge you complete</p>
            </div>
            <div className="relative w-28 h-28 flex-shrink-0">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="54" fill="none" stroke="#f3f4f6" strokeWidth="3" />
                <circle
                  cx="60"
                  cy="60"
                  r="54"
                  fill="none"
                  stroke="url(#iqGrad)"
                  strokeWidth="3"
                  strokeDasharray={`${(financeProfile.finance_iq_score / 100) * 339.29} 339.29`}
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="iqGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#8b5cf6" />
                    <stop offset="100%" stopColor="#3b82f6" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-sm font-bold text-purple-600">{Math.round((financeProfile.finance_iq_score / 100) * 100)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Progress to Next Level */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Progress to Level {userStats.current_level + 1}</h3>
              <p className="text-xs text-gray-600 mt-1">
                {userStats.total_xp} / {userStats.next_level_xp} XP
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-cyan-600">
                {userStats.next_level_xp - userStats.total_xp}
              </p>
              <p className="text-xs text-gray-600">XP to next</p>
            </div>
          </div>
          <ProgressBar 
            percent={(userStats.total_xp / userStats.next_level_xp) * 100}
            color="blue"
            height="h-3"
          />
        </div>
        <div className="h-1 bg-cyan-400" />
      </div>

      {/* Market Widget */}
      <MarketWidget
        data={marketData}
      />

      {/* Games Section */}
      <GameSection
        games={gamesCatalog}
        title="Featured Games"
        description="Play hands-on simulations to level up your money skills"
      />

      {/* Simulations Section */}
      <SimulationSection />
    </div>
  )
}
