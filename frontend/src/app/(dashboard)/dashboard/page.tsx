'use client'

import { useState, useEffect, useRef } from 'react'
import { 
  TrendingUp, 
  DollarSign, 
  Target, 
  Zap,
  Coffee,
  Calculator,
  Shield,
  CreditCard,
  AlertTriangle,
  Briefcase,
  PiggyBank,
  LineChart,
  TrendingDown,
  MessageSquare,
  Trophy
} from 'lucide-react'
import { Card, StatCard } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { ProgressBar } from '@/components/ui/ProgressBar'
import MarketWidget from '@/components/dashboard/MarketWidget'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { getUserStats, getSimulationsStatus, UserStats, SimulationStatus } from '@/lib/api/progress'
import { userAPI, marketAPI } from '@/lib/api/client'
import { useMarketData, useRefreshMarketCache } from '@/lib/api/hooks'

// Icon mapping for simulations
const iconMap: Record<string, any> = {
  'coffee-shop-effect': Coffee,
  'paycheck-game': DollarSign,
  'budget-builder': Calculator,
  'emergency-fund': Shield,
  'credit-card-trap': CreditCard,
  'debt-strategies': TrendingDown,
  'debt-classification': AlertTriangle,
  'compound-interest': Zap,
  'risk-reward': LineChart,
  'index-fund-challenge': TrendingUp,
  'retirement-calculator': PiggyBank,
  'tax-optimizer': Briefcase,
}

interface FinanceProfile {
  finance_iq_score: number
  money_personality: string
  recommended_first_sim: string
}

export default function DashboardPage() {
  const [selectedLevel, setSelectedLevel] = useState<number | 'all'>('all')
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [simulations, setSimulations] = useState<SimulationStatus[]>([])
  const [financeProfile, setFinanceProfile] = useState<FinanceProfile | null>(null)

  // Fetch market data
  const { data: marketData, isLoading: marketLoading, error: marketError, refetch: refetchMarket } = useMarketData(8)
  const { mutateAsync: refreshMarketCache } = useRefreshMarketCache()

  // Fetch user stats and simulations on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stats, simulationsData, profile] = await Promise.all([
          getUserStats(),
          getSimulationsStatus(),
          userAPI.getFinancialProfile().catch(() => null) // Don't fail if profile doesn't exist
        ])
        setUserStats(stats)
        setSimulations(simulationsData)
        if (profile) {
          setFinanceProfile(profile)
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
      }
    }

    fetchData()
  }, [])

  // Filter simulations by level
  const filteredSimulations = selectedLevel === 'all' 
    ? simulations 
    : simulations.filter(s => s.level === selectedLevel)

  // Show loading state only for initial render
  if (!userStats) {
    return null // loading.tsx will handle this
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome Back! 👋</h1>
        <p className="text-blue-100 mb-6">
          You're on a {userStats.current_streak}-day streak! Keep building your financial future.
        </p>
        <div className="flex flex-wrap gap-4">
          <Button variant="primary" className="bg-white text-blue-600 hover:bg-gray-100">
            Continue Learning
          </Button>
          <Button variant="outline" className="border-white text-white hover:bg-white/10">
            <MessageSquare className="w-5 h-5" />
            Ask AI Tutor
          </Button>
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
          iconColor="bg-blue-500"
          trend="up"
          animate={true}
        />
      </div>

      {/* Finance IQ Card */}
      {financeProfile && (
        <Card className="bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Finance IQ Score</p>
              <h3 className="text-2xl font-bold text-gray-900">{Math.round(financeProfile.finance_iq_score)}/100</h3>
              <p className="text-xs text-gray-500 mt-1">Grows with every challenge you complete</p>
            </div>
            <div className="relative w-24 h-24">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="54" fill="none" stroke="#e0e7ff" strokeWidth="4" />
                <circle
                  cx="60"
                  cy="60"
                  r="54"
                  fill="none"
                  stroke="url(#grad)"
                  strokeWidth="4"
                  strokeDasharray={`${(financeProfile.finance_iq_score / 100) * 339.29} 339.29`}
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#a78bfa" />
                    <stop offset="100%" stopColor="#60a5fa" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-sm font-semibold text-purple-600">{Math.round((financeProfile.finance_iq_score / 100) * 100)}%</span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Progress to Next Level */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Progress to Level {userStats.current_level + 1}</h3>
            <p className="text-sm text-gray-600">
              {userStats.total_xp} / {userStats.next_level_xp} XP
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-blue-600">
              {userStats.next_level_xp - userStats.total_xp} XP
            </p>
            <p className="text-sm text-gray-600">to next level</p>
          </div>
        </div>
        <ProgressBar 
          percent={(userStats.total_xp / userStats.next_level_xp) * 100}
          color="blue"
          height="h-4"
        />
      </Card>

      {/* Market Widget */}
      <MarketWidget
        data={marketData}
        loading={marketLoading}
        error={marketError instanceof Error ? marketError.message : null}
        onRefresh={async () => {
          await refreshMarketCache()
        }}
      />

      {/* Level Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => setSelectedLevel('all')}
          className={cn(
            'px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap',
            selectedLevel === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100'
          )}
        >
          All Simulations
        </button>
        {[1, 2, 3, 4].map((level) => (
          <button
            key={level}
            onClick={() => setSelectedLevel(level)}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap',
              selectedLevel === level
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            )}
          >
            Level {level}
          </button>
        ))}
      </div>

      {/* Simulations Grid */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          {selectedLevel === 'all' ? 'All Simulations' : `Level ${selectedLevel} Simulations`}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSimulations.map((sim) => {
            const Icon = iconMap[sim.id] || Target
            return (
              <Card
                key={sim.id}
                hover={sim.is_unlocked}
                className={cn(
                  'relative overflow-hidden',
                  !sim.is_unlocked && 'opacity-60'
                )}
              >
                {/* Level Badge */}
                <div className="absolute top-4 right-4">
                  <span className="bg-gray-900 text-white text-xs font-bold px-2 py-1 rounded-full">
                    Level {sim.level}
                  </span>
                </div>

                {/* Icon */}
                <div className={cn(
                  'w-16 h-16 rounded-2xl bg-gradient-to-br mb-4 flex items-center justify-center',
                  sim.color
                )}>
                  <Icon className="w-8 h-8 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-lg font-bold text-gray-900 mb-2">
                  {sim.title}
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  {sim.description}
                </p>

                {/* Meta Info */}
                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <span className="flex items-center gap-1">
                    <Zap className="w-4 h-4" />
                    +{sim.xp_reward} XP
                  </span>
                  <span>{sim.estimated_time}</span>
                </div>

                {/* Action Button */}
                {sim.is_unlocked ? (
                  <Link href={sim.href}>
                    <Button variant="primary" className="w-full">
                      {sim.is_completed ? 'Play Again' : 'Start Simulation'}
                    </Button>
                  </Link>
                ) : (
                  <Button variant="outline" className="w-full" disabled>
                    🔒 Locked
                  </Button>
                )}

                {/* Completed Badge */}
                {sim.is_completed && (
                  <div className="absolute top-4 left-4">
                    <div className="bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1">
                      ✓ Completed
                    </div>
                  </div>
                )}
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}
