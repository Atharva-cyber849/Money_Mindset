'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, ChevronRight, ChevronLeft, Check, Sparkles } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useRouter } from 'next/navigation'

interface QuizQuestion {
  id: string
  question: string
  options: string[]
}

interface QuizResponse {
  question_id: string
  selected_option: number
}

export default function PersonalityQuizPage() {
  const router = useRouter()
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [responses, setResponses] = useState<QuizResponse[]>([])
  const [selectedOption, setSelectedOption] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch quiz questions
  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/personality/quiz/questions')
        const data = await response.json()
        setQuestions(data.questions)
        setLoading(false)
      } catch (err) {
        setError('Failed to load quiz questions')
        setLoading(false)
      }
    }

    fetchQuestions()
  }, [])

  const handleOptionSelect = (optionIndex: number) => {
    setSelectedOption(optionIndex)
  }

  const handleNext = () => {
    if (selectedOption === null) return

    // Save response
    setResponses([
      ...responses,
      {
        question_id: questions[currentQuestion].id,
        selected_option: selectedOption
      }
    ])

    // Move to next question
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setSelectedOption(null)
    } else {
      // Submit quiz
      submitQuiz()
    }
  }

  const handleBack = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
      // Restore previous selection
      const previousResponse = responses[currentQuestion - 1]
      if (previousResponse) {
        setSelectedOption(previousResponse.selected_option)
      }
    }
  }

  const submitQuiz = async () => {
    setSubmitting(true)
    
    const allResponses = [
      ...responses,
      {
        question_id: questions[currentQuestion].id,
        selected_option: selectedOption!
      }
    ]

    try {
      const token = localStorage.getItem('jwt_token')
      const response = await fetch('http://localhost:8000/api/v1/personality/quiz/submit', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ responses: allResponses })
      })

      if (!response.ok) throw new Error('Failed to submit quiz')

      const data = await response.json()
      
      // Store results and navigate to results page
      localStorage.setItem('personality_profile', JSON.stringify(data.profile))
      router.push('/personality/results')
      
    } catch (err) {
      setError('Failed to submit quiz. Please try again.')
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <Brain className="w-16 h-16 mx-auto mb-4 text-purple-600 animate-pulse" />
          <p className="text-lg text-gray-600">Loading personality quiz...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <Card className="max-w-md text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Try Again</Button>
        </Card>
      </div>
    )
  }

  const progress = ((currentQuestion + 1) / questions.length) * 100
  const question = questions[currentQuestion]

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Discover Your Money Personality
          </h1>
          <p className="text-gray-600">
            Question {currentQuestion + 1} of {questions.length}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-purple-500 to-indigo-600"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Question Card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestion}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                {question.question}
              </h2>

              <div className="space-y-3">
                {question.options.map((option, index) => (
                  <motion.button
                    key={index}
                    onClick={() => handleOptionSelect(index)}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      selectedOption === index
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-purple-300 hover:bg-gray-50'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-gray-900">{option}</span>
                      {selectedOption === index && (
                        <Check className="w-5 h-5 text-purple-600" />
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>
            </Card>
          </motion.div>
        </AnimatePresence>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentQuestion === 0}
          >
            <ChevronLeft className="w-5 h-5" />
            Back
          </Button>

          <Button
            onClick={handleNext}
            disabled={selectedOption === null || submitting}
            isLoading={submitting}
          >
            {currentQuestion === questions.length - 1 ? (
              <>
                <Sparkles className="w-5 h-5" />
                See Results
              </>
            ) : (
              <>
                Next
                <ChevronRight className="w-5 h-5" />
              </>
            )}
          </Button>
        </div>

        {/* Progress Indicator */}
        <div className="mt-8 text-center">
          <div className="flex items-center justify-center gap-2">
            {questions.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full transition-all ${
                  index < currentQuestion
                    ? 'bg-purple-600'
                    : index === currentQuestion
                    ? 'bg-purple-600 w-8'
                    : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
