'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Brain, TrendingUp, AlertCircle, Target, Sparkles, ArrowRight, Award } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useRouter } from 'next/navigation'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts'

interface PersonalityProfile {
  archetype: string
  archetype_name: string
  description: string
  strengths: string[]
  challenges: string[]
  learning_focus: string[]
  dimension_scores: {
    risk_tolerance: number
    time_horizon: number
    spending_trigger: number
    mindset: number
    decision_style: number
    stress_response: number
  }
  confidence_score: number
  strongest_dimension: {
    name: string
    score: number
  }
  weakest_dimension: {
    name: string
    score: number
  }
}

export default function PersonalityResultsPage() {
  const router = useRouter()
  const [profile, setProfile] = useState<PersonalityProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get profile from localStorage (set after quiz submission)
    const savedProfile = localStorage.getItem('personality_profile')
    
    if (savedProfile) {
      setProfile(JSON.parse(savedProfile))
      setLoading(false)
    } else {
      // If no saved profile, redirect to quiz
      router.push('/personality/quiz')
    }
  }, [router])

  if (loading || !profile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="animate-pulse text-center">
          <Brain className="w-16 h-16 mx-auto mb-4 text-purple-600" />
          <p className="text-lg text-gray-600">Loading your results...</p>
        </div>
      </div>
    )
  }

  // Prepare data for radar chart
  const radarData = [
    {
      dimension: 'Risk\nTolerance',
      score: profile.dimension_scores.risk_tolerance,
      fullMark: 10
    },
    {
      dimension: 'Time\nHorizon',
      score: profile.dimension_scores.time_horizon,
      fullMark: 10
    },
    {
      dimension: 'Spending\nControl',
      score: profile.dimension_scores.spending_trigger,
      fullMark: 10
    },
    {
      dimension: 'Mindset',
      score: profile.dimension_scores.mindset,
      fullMark: 10
    },
    {
      dimension: 'Decision\nStyle',
      score: profile.dimension_scores.decision_style,
      fullMark: 10
    },
    {
      dimension: 'Stress\nResponse',
      score: profile.dimension_scores.stress_response,
      fullMark: 10
    }
  ]

  // Archetype colors
  const archetypeColors = {
    'cautious_planner': 'from-blue-500 to-cyan-600',
    'optimistic_risk_taker': 'from-orange-500 to-red-600',
    'balanced_builder': 'from-green-500 to-emerald-600',
    'anxious_avoider': 'from-purple-500 to-pink-600'
  }

  const gradientColor = archetypeColors[profile.archetype as keyof typeof archetypeColors] || 'from-purple-500 to-indigo-600'

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className={`w-24 h-24 mx-auto mb-6 bg-gradient-to-br ${gradientColor} rounded-full flex items-center justify-center`}>
            <Brain className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Your Money Personality
          </h1>
          <div className="inline-block px-6 py-3 bg-white rounded-full shadow-sm border border-gray-200">
            <p className="text-2xl font-semibold text-gradient bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
              {profile.archetype_name}
            </p>
          </div>
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Personality Radar Chart */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <h3 className="text-xl font-semibold mb-6">Your Financial Psychology Profile</h3>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis 
                    dataKey="dimension"
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                  />
                  <PolarRadiusAxis angle={90} domain={[0, 10]} tick={{ fill: '#6b7280' }} />
                  <Radar
                    name="Your Scores"
                    dataKey="score"
                    stroke="#8b5cf6"
                    fill="#8b5cf6"
                    fillOpacity={0.5}
                  />
                </RadarChart>
              </ResponsiveContainer>
              
              <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="text-gray-600">Strongest</p>
                    <p className="font-semibold">{profile.strongest_dimension.name}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-orange-600" />
                  <div>
                    <p className="text-gray-600">Growth Area</p>
                    <p className="font-semibold">{profile.weakest_dimension.name}</p>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>

          {/* Description & Overview */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="h-full flex flex-col">
              <h3 className="text-xl font-semibold mb-4">What This Means</h3>
              <p className="text-gray-700 mb-6 flex-grow">
                {profile.description}
              </p>
              
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 mb-1">Your Strengths</p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {profile.strengths.map((strength, index) => (
                        <li key={index}>• {strength}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center flex-shrink-0">
                    <AlertCircle className="w-5 h-5 text-orange-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 mb-1">Watch Out For</p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {profile.challenges.map((challenge, index) => (
                        <li key={index}>• {challenge}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>

        {/* Learning Focus */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">Personalized Learning Path</h3>
                <p className="text-gray-600">We'll focus on these areas to help you improve</p>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              {profile.learning_focus.map((focus, index) => (
                <div key={index} className="p-4 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
                  <p className="font-semibold text-gray-900">{focus}</p>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="flex flex-col sm:flex-row gap-4 justify-center mt-12"
        >
          <Button
            size="lg"
            onClick={() => router.push('/dashboard')}
          >
            <ArrowRight className="w-5 h-5" />
            Continue to Dashboard
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => router.push('/simulations')}
          >
            <Sparkles className="w-5 h-5" />
            Start Simulations
          </Button>
        </motion.div>

        {/* Confidence Badge */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Assessment Confidence: {Math.round(profile.confidence_score * 100)}%
          </p>
        </div>
      </div>
    </div>
  )
}
