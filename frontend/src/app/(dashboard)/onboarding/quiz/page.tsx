'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { AlertCircle, Loader2, ChevronRight, ChevronLeft } from 'lucide-react'
import { userAPI } from '@/lib/api/client'

const QUESTIONS = [
  {
    id: 1,
    title: 'What are your financial goals?',
    subtitle: 'Select the goal that resonates most with you',
    type: 'chips',
    options: ['Save money', 'Invest wisely', 'Pay off debt', 'Build emergency fund'],
    key: 'q1_goals'
  },
  {
    id: 2,
    title: 'What stage of life are you in?',
    subtitle: 'Select your current life stage',
    type: 'chips',
    options: ['Student', 'First job', 'Mid-career', 'Business owner'],
    key: 'q2_life_stage'
  },
  {
    id: 3,
    title: 'What is a SIP?',
    subtitle: 'Test your financial knowledge',
    type: 'options',
    options: [
      'A type of tea served in cafés',
      'Systematic Investment Plan - regular small investments',
      'A savings account with fixed interest'
    ],
    key: 'q3_knowledge',
    scoreMap: { 1: 80, 0: 10, 2: 20 } // Index to score mapping
  },
  {
    id: 4,
    title: 'The stock market drops 20%. What do you do?',
    subtitle: 'Understand your risk tolerance',
    type: 'options',
    options: [
      'Panic and sell everything',
      'Hold and wait for recovery',
      'Buy more at lower prices',
      'Rebalance my portfolio'
    ],
    key: 'q4_risk_tolerance',
    riskMap: { 0: 'Conservative', 1: 'Moderate', 2: 'Aggressive', 3: 'Aggressive' }
  },
  {
    id: 5,
    title: 'What is your monthly surplus?',
    subtitle: 'How much can you invest each month?',
    type: 'options',
    options: ['₹500', '₹2,000', '₹5,000', '₹10,000+'],
    key: 'q5_monthly_surplus',
    valueMap: { 0: 500, 1: 2000, 2: 5000, 3: 10000 }
  }
]

export default function QuizPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [answers, setAnswers] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const question = QUESTIONS[currentStep]
  const isAnswered = answers[question.key] !== undefined

  const handleSelect = (value: string | number) => {
    setAnswers(prev => ({
      ...prev,
      [question.key]: value
    }))
  }

  const handleNext = () => {
    if (!isAnswered) {
      setError('Please select an answer')
      return
    }
    setError(null)
    if (currentStep < QUESTIONS.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
      setError(null)
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate all answers
    if (Object.keys(answers).length !== QUESTIONS.length) {
      setError('Please answer all questions')
      return
    }

    setSubmitting(true)

    try {
      // Transform answers to match API format
      const q3Knowledge = question.id === 3
        ? QUESTIONS[2].scoreMap?.[answers.q3_knowledge as keyof typeof QUESTIONS[2].scoreMap] || 50
        : answers.q3_knowledge || 50

      const q4RiskTolerance = answers.q4_risk_tolerance
        ? QUESTIONS[3].riskMap?.[answers.q4_risk_tolerance as keyof typeof QUESTIONS[3].riskMap] || 'Moderate'
        : 'Moderate'

      const q5MonthlySurplus = answers.q5_monthly_surplus
        ? QUESTIONS[4].valueMap?.[answers.q5_monthly_surplus as keyof typeof QUESTIONS[4].valueMap] || 5000
        : 5000

      // Submit quiz
      const result = await userAPI.submitQuiz(
        answers.q1_goals as string,
        answers.q2_life_stage as string,
        q3Knowledge as number,
        q4RiskTolerance as string,
        q5MonthlySurplus as number
      )

      // Redirect to results page
      router.push('/dashboard/onboarding/results')
    } catch (err: any) {
      console.error('Quiz submission error:', err)
      setError(err.response?.data?.detail || 'Failed to submit quiz. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-400">Question {currentStep + 1} of {QUESTIONS.length}</span>
            <div className="w-32 h-1 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / QUESTIONS.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Question Card */}
        <Card className="p-8 bg-slate-800 border border-slate-700 mb-8">
          {/* Question Header */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">{question.title}</h2>
            <p className="text-slate-300">{question.subtitle}</p>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3 mb-6">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-200">{error}</p>
            </div>
          )}

          {/* Options */}
          <div className="space-y-3">
            {question.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleSelect(index)}
                className={`w-full p-4 rounded-lg border-2 transition-all text-left font-medium text-base ${
                  answers[question.key] === index
                    ? 'bg-blue-600/20 border-blue-500 text-white'
                    : 'bg-slate-700/50 border-slate-600 text-slate-200 hover:border-slate-500'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
        </Card>

        {/* Navigation Buttons */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-4">
            <Button
              type="button"
              onClick={handlePrev}
              disabled={currentStep === 0 || submitting}
              variant="outline"
              className="flex-1 h-12 flex items-center justify-center gap-2"
            >
              <ChevronLeft className="w-4 h-4" />
              Back
            </Button>

            {currentStep === QUESTIONS.length - 1 ? (
              <Button
                type="submit"
                disabled={!isAnswered || submitting}
                className="flex-1 h-12 bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:shadow-lg disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    Complete Quiz
                    <ChevronRight className="w-4 h-4" />
                  </>
                )}
              </Button>
            ) : (
              <Button
                type="button"
                onClick={handleNext}
                disabled={!isAnswered}
                className="flex-1 h-12 bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg disabled:opacity-50 flex items-center justify-center gap-2"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </Button>
            )}
          </div>
        </form>

        {/* Info Text */}
        <p className="text-center text-sm text-slate-400 mt-8">
          No time limit · No wrong answers · Takes ~3 minutes
        </p>
      </div>
    </div>
  )
}
