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
import { getCrossGameSummary, CrossGameSummary } from '@/lib/api/analytics'
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
  const [crossGameSummary, setCrossGameSummary] = useState<CrossGameSummary | null>(null)

  // Fetch market data
  const { data: marketData } = useMarketData(8)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stats, profile] = await Promise.all([
          getUserStats(),
          userAPI.getFinancialProfile().catch(() => null), // Don't fail if profile doesn't exist
        ])
        const summary = await getCrossGameSummary().catch(() => null)
        setUserStats(stats)
        if (profile) {
          setFinanceProfile(profile)
        }
        if (summary) {
          setCrossGameSummary(summary)
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

      {/* Cross-Game Progress */}
      {crossGameSummary && (
        <div className="bg-slate-950 rounded-2xl p-6 text-white overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-transparent to-emerald-500/10" />
          <div className="relative grid gap-6 lg:grid-cols-[1.4fr_1fr]">
            <div>
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-white/10 text-cyan-100 text-xs font-semibold mb-4">
                Cross-Game Progress
              </div>
              <h3 className="text-2xl font-bold mb-2">Your portfolio carries across games</h3>
              <p className="text-sm text-slate-300 max-w-2xl mb-6">
                Use Karobaar, Paper Trading, and Dalal Street together. Build one portfolio, unlock harder simulations, and compound your learning rewards.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
                <div className="rounded-xl bg-white/8 border border-white/10 p-4">
                  <p className="text-xs text-slate-300 mb-1">Portfolio Value</p>
                  <p className="text-2xl font-bold">₹{Math.round(crossGameSummary.portfolio.value).toLocaleString('en-IN')}</p>
                </div>
                <div className="rounded-xl bg-white/8 border border-white/10 p-4">
                  <p className="text-xs text-slate-300 mb-1">Active Sessions</p>
                  <p className="text-2xl font-bold">{crossGameSummary.compound_rewards.active_sessions}</p>
                </div>
                <div className="rounded-xl bg-white/8 border border-white/10 p-4">
                  <p className="text-xs text-slate-300 mb-1">XP Boost</p>
                  <p className="text-2xl font-bold">+{Math.round(crossGameSummary.compound_rewards.xp_boost_from_progress * 100)}%</p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {crossGameSummary.recommendations.map((item) => (
                  <span key={item} className="px-3 py-2 rounded-full bg-white/10 text-sm text-slate-100 border border-white/10">
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <div className="rounded-xl bg-white text-slate-900 p-4">
                <p className="text-xs uppercase tracking-wide text-cyan-700 font-semibold mb-1">Career Path</p>
                <p className="font-bold mb-2">{crossGameSummary.career_path.next_step}</p>
                <p className="text-sm text-slate-600">
                  Karobaar: {crossGameSummary.career_path.karobaar_sessions} · Paper Trading: {crossGameSummary.career_path.paper_trading_sessions} · Dalal Street: {crossGameSummary.career_path.dalal_sessions}
                </p>
              </div>

              <div className="rounded-xl bg-white/5 border border-white/10 p-4">
                <p className="text-xs uppercase tracking-wide text-cyan-100 font-semibold mb-3">Achievement-Locked Content</p>
                <div className="space-y-2">
                  {crossGameSummary.achievement_locked_content.map((item) => (
                    <div key={item.id} className="flex items-start justify-between gap-3 text-sm">
                      <span className="text-slate-200 capitalize">{item.id.replace(/-/g, ' ')}</span>
                      <span className={item.locked ? 'text-amber-300' : 'text-emerald-300'}>{item.locked ? item.reason : 'Unlocked'}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl bg-white/5 border border-white/10 p-4">
                <p className="text-xs uppercase tracking-wide text-cyan-100 font-semibold mb-3">Technical Improvements</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-slate-200">
                  <span>Session analytics: {crossGameSummary.technical_improvements.session_analytics ? 'Ready' : 'Pending'}</span>
                  <span>Export reports: {crossGameSummary.technical_improvements.export_reports ? 'Ready' : 'Pending'}</span>
                  <span>Mobile variants: {crossGameSummary.technical_improvements.mobile_optimized_variants ? 'Ready' : 'Pending'}</span>
                  <span>Offline mode: {crossGameSummary.technical_improvements.offline_mode_ready ? 'Ready' : 'Pending'}</span>
                  <span>Live market data: {crossGameSummary.technical_improvements.real_time_data_integration ? 'Ready' : 'Pending'}</span>
                </div>
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
