'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Loader2, Share2, CheckCircle2, Zap, Trophy, Target } from 'lucide-react'
import { userAPI } from '@/lib/api/client'

interface FinancialProfile {
  money_personality: string
  finance_iq_score: number
  learning_gaps: string[]
  recommended_first_sim: string
}

const PERSONALITY_EMOJIS: Record<string, string> = {
  'The Careful Builder': '🏗️',
  'The Ambitious Investor': '🚀',
  'The Overwhelmed Earner': '😰',
  'The Smart Saver': '💰',
}

const PERSONALITY_COLORS: Record<string, string> = {
  'The Careful Builder': 'from-cyan-600 to-blue-800',
  'The Ambitious Investor': 'from-purple-600 to-pink-600',
  'The Overwhelmed Earner': 'from-orange-600 to-red-600',
  'The Smart Saver': 'from-emerald-600 to-teal-600',
}

export default function ResultsPage() {
  const router = useRouter()
  const [profile, setProfile] = useState<FinancialProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [animating, setAnimating] = useState(false)
  const [showShare, setShowShare] = useState(false)

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await userAPI.getFinancialProfile()
        setProfile(data)
        setLoading(false)
        // Start animations after 500ms
        setTimeout(() => setAnimating(true), 500)
      } catch (err) {
        console.error('Failed to load profile:', err)
        setLoading(false)
      }
    }

    fetchProfile()
  }, [])

  const handleShare = () => {
    const text = `I just discovered my Money Personality: ${profile?.money_personality}! 💰

My Finance IQ Score: ${Math.round(profile?.finance_iq_score || 0)}/100

Ready to master my finances with Money Mindset! 🚀`

    if (navigator.share) {
      navigator.share({
        title: 'Money Mindset - Financial Fingerprint',
        text: text,
      }).catch(err => console.log('Error sharing:', err))
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(text)
      setShowShare(true)
      setTimeout(() => setShowShare(false), 2000)
    }
  }

  const handleStart = () => {
    router.push('/dashboard')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-cyan-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-300">Analysing your financial fingerprint...</p>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-300">Failed to load profile</p>
        </div>
      </div>
    )
  }

  const personalityEmoji = PERSONALITY_EMOJIS[profile.money_personality] || '💎'
  const personalityColor = PERSONALITY_COLORS[profile.money_personality] || 'from-cyan-600 to-purple-600'

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-3xl mx-auto">
        {/* Main Results Card */}
        <Card className="bg-slate-800 border border-slate-700 overflow-hidden mb-8">
          <div className="p-8 text-center">
            {/* Personality Section - Animates in first */}
            <div
              className={`mb-8 transition-all duration-700 transform ${
                animating
                  ? 'opacity-100 translate-y-0'
                  : 'opacity-0 translate-y-8'
              }`}
            >
              <div className="text-6xl mb-4">{personalityEmoji}</div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Your Money Personality
              </h1>
              <div className={`inline-block px-6 py-3 rounded-full bg-gradient-to-r ${personalityColor} text-white font-semibold text-lg`}>
                {profile.money_personality}
              </div>
            </div>

            {/* IQ Score Section - Animates in second */}
            <div
              className={`mb-8 transition-all duration-700 transform delay-200 ${
                animating
                  ? 'opacity-100 translate-y-0'
                  : 'opacity-0 translate-y-8'
              }`}
            >
              <div className="flex justify-center mb-4">
                <div className="relative w-32 h-32">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                    <circle
                      cx="60"
                      cy="60"
                      r="56"
                      fill="none"
                      stroke="#334155"
                      strokeWidth="8"
                    />
                    <circle
                      cx="60"
                      cy="60"
                      r="56"
                      fill="none"
                      stroke="url(#grad)"
                      strokeWidth="8"
                      strokeDasharray={`${(profile.finance_iq_score / 100) * 351.86} 351.86`}
                      strokeLinecap="round"
                      className="transition-all duration-1000"
                    />
                    <defs>
                      <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#a855f7" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-4xl font-bold text-white">
                      {Math.round(profile.finance_iq_score)}
                    </span>
                    <span className="text-sm text-slate-400">/100</span>
                  </div>
                </div>
              </div>
              <p className="text-slate-300">Finance IQ Score</p>
              <p className="text-sm text-slate-400 mt-2">
                This score grows every time you learn and complete challenges
              </p>
            </div>

            {/* Learning Path Section - Animates in third */}
            <div
              className={`mb-8 transition-all duration-700 transform delay-400 ${
                animating
                  ? 'opacity-100 translate-y-0'
                  : 'opacity-0 translate-y-8'
              }`}
            >
              <h2 className="text-xl font-bold text-white mb-4">Your Learning Path</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {profile.learning_gaps?.slice(0, 4).map((gap, index) => (
                  <div
                    key={index}
                    className="bg-slate-700/50 border border-slate-600 rounded-lg p-4 text-slate-200 text-sm"
                  >
                    <div className="flex items-start gap-3">
                      <Zap className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                      {gap}
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-400 mt-3">
                Focus on these topics to level up your financial knowledge
              </p>
            </div>

            {/* Recommended Simulation Section - Animates in fourth */}
            <div
              className={`transition-all duration-700 transform delay-600 ${
                animating
                  ? 'opacity-100 translate-y-0'
                  : 'opacity-0 translate-y-8'
              }`}
            >
              <p className="text-slate-400 mb-3">Your First Challenge</p>
              <div className="bg-gradient-to-r from-emerald-600 to-teal-600 rounded-lg p-6 text-white">
                <div className="flex items-center gap-2 mb-2">
                  <Trophy className="w-5 h-5" />
                  <span className="font-semibold">Recommended for You</span>
                </div>
                <p className="text-2xl font-bold capitalize mb-2">
                  {profile.recommended_first_sim?.replace('-', ' ')}
                </p>
                <p className="text-sm text-emerald-100">
                  Based on your profile, this simulation is perfect for your next step
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            onClick={handleShare}
            variant="outline"
            className="flex-1 h-12 flex items-center justify-center gap-2 border-slate-600 text-slate-200 hover:bg-slate-700"
          >
            <Share2 className="w-4 h-4" />
            Share My Results
          </Button>
          <Button
            onClick={handleStart}
            className="flex-1 h-12 bg-gradient-to-r from-cyan-600 to-purple-600 text-white hover:shadow-lg flex items-center justify-center gap-2"
          >
            <CheckCircle2 className="w-4 h-4" />
            Let's Get Started
          </Button>
        </div>

        {/* Share Confirmation */}
        {showShare && (
          <div className="fixed bottom-4 left-4 right-4 bg-emerald-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            Copied to clipboard!
          </div>
        )}

        {/* Footer */}
        <p className="text-center text-sm text-slate-400 mt-8">
          Your financial profile will evolve as you learn more. Update your preferences anytime in settings.
        </p>
      </div>
    </div>
  )
}
