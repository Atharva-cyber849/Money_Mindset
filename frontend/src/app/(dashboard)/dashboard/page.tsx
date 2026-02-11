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
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { getUserStats, getSimulationsStatus, UserStats, SimulationStatus } from '@/lib/api/progress'

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

export default function DashboardPage() {
  const [selectedLevel, setSelectedLevel] = useState<number | 'all'>('all')
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [simulations, setSimulations] = useState<SimulationStatus[]>([])
  
  // Fetch user stats and simulations on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stats, simulationsData] = await Promise.all([
          getUserStats(),
          getSimulationsStatus()
        ])
        setUserStats(stats)
        setSimulations(simulationsData)
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
