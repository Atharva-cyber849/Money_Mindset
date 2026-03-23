'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { IntroSlide } from '@/components/simulations/IntroSlide'
import { ExampleCardsPanel } from '@/components/simulations/ExampleCardsPanel'
import { InsightsPanel } from '@/components/simulations/InsightsPanel'
import { StepProgressBar } from '@/components/simulations/StepProgressBar'
import { CompoundingCurveInfographic } from './components/CompoundingCurveInfographic'
import { compoundInterestConfig } from './config'

const steps = [
  { number: 1, label: 'Introduction' },
  { number: 2, label: 'How It Works' },
  { number: 3, label: 'Real Examples' },
  { number: 4, label: 'Your Plan' },
  { number: 5, label: 'Your Results' }
]

export default function CompoundInterestPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [investmentAge, setInvestmentAge] = useState(35)
  const [monthlyAmount, setMonthlyAmount] = useState(5000)
  const [yearsInvesting, setYearsInvesting] = useState(30)
  const [xpEarned, setXpEarned] = useState(false)

  // Calculate investment outcome
  const calculateFinalAmount = () => {
    const monthlyRate = 0.12 / 12
    const months = yearsInvesting * 12
    const finalAmount = monthlyAmount * (((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate))
    const totalInvested = monthlyAmount * months
    const growth = finalAmount - totalInvested
    return { finalAmount, totalInvested, growth }
  }

  const result = calculateFinalAmount()

  // Generate chart data
  const generateChartData = () => {
    const data = []
    let balance = 0
    const monthlyRate = 0.12 / 12

    for (let year = 0; year <= yearsInvesting; year++) {
      data.push({
        year,
        amount: balance,
        contributions: monthlyAmount * 12 * year
      })

      for (let month = 0; month < 12; month++) {
        balance = (balance + monthlyAmount) * (1 + monthlyRate)
      }
    }

    return data
  }

  const chartData = generateChartData()

  const determineInsightThreshold = () => {
    const optimalGrowth = monthlyAmount * 365 * yearsInvesting * 1.5
    const growthRatio = result.growth / optimalGrowth

    if (growthRatio >= 0.8) return 'high'
    if (growthRatio >= 0.5) return 'medium'
    return 'low'
  }

  const getMainInsight = () => {
    const threshold = determineInsightThreshold()
    const template = compoundInterestConfig.insightTemplates.find(t => t.threshold === threshold)

    if (!template) return { text: compoundInterestConfig.fallbackInsights[0], type: 'success' }

    const text = template.text
      .replace('{total}', formatCurrency(result.finalAmount))
      .replace('{growth}', formatCurrency(result.growth))
      .replace('{pure_growth}', formatCurrency(result.growth))
      .replace('{multiple}', ((result.finalAmount / result.totalInvested) || 1).toFixed(1))
      .replace('{increase_amount}', formatCurrency(monthlyAmount * 0.5))
      .replace('{optimized}', formatCurrency(result.finalAmount * 1.5))
      .replace('{potential}', formatCurrency(result.finalAmount * 1.2))

    return {
      text,
      type: threshold === 'high' ? 'success' : threshold === 'medium' ? 'recommendation' : 'tip'
    }
  }

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleComplete = () => {
    setXpEarned(true)
  }

  return (
    <motion.div className="min-h-screen bg-gradient-to-b from-gray-50 to-white p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Progress Bar */}
        <StepProgressBar
          currentStep={currentStep}
          totalSteps={5}
          steps={steps}
          highlightColor="blue"
        />

        <div className="mt-12">
          <AnimatePresence mode="wait">
            {/* Step 1: Introduction */}
            {currentStep === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <IntroSlide
                  title={compoundInterestConfig.intro.title}
                  description={compoundInterestConfig.intro.description}
                  icon={compoundInterestConfig.intro.icon}
                  whyItMatters={compoundInterestConfig.intro.whyItMatters}
                  onNext={handleNext}
                  highlightColor={compoundInterestConfig.intro.highlightColor}
                />
              </motion.div>
            )}

            {/* Step 2: Mechanics Infographic */}
            {currentStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <CompoundingCurveInfographic />
                <div className="flex justify-between mt-8">
                  <Button
                    onClick={() => setCurrentStep(currentStep - 1)}
                    variant="outline"
                  >
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    Ready to Try? →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 3: Real-World Examples */}
            {currentStep === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <ExampleCardsPanel
                  title="How Different People Started"
                  description="These are real scenarios showing how age impacts final wealth"
                  examples={compoundInterestConfig.examples}
                  highlightColor="blue"
                />
                <div className="flex justify-between mt-8">
                  <Button
                    onClick={() => setCurrentStep(currentStep - 1)}
                    variant="outline"
                  >
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    Calculate Yours →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 4: Personal Calculator */}
            {currentStep === 4 && (
              <motion.div
                key="step4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="space-y-6"
              >
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold text-gray-900 mb-3">Your Investment Scenario</h2>
                  <p className="text-lg text-gray-600">Adjust the sliders to see how your personal investments could grow</p>
                </div>

                <Card className="p-8 border-2 border-blue-200 bg-blue-50">
                  <div className="space-y-8">
                    {/* Age Slider */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-4">
                        Starting Age: <span className="text-lg text-blue-600">{investmentAge}</span>
                      </label>
                      <Slider
                        min={18}
                        max={55}
                        step={1}
                        value={investmentAge}
                        onChange={setInvestmentAge}
                        color="blue"
                        format={(v) => `Age ${v}`}
                      />
                    </div>

                    {/* Monthly Amount Slider */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-4">
                        Monthly Investment: <span className="text-lg text-blue-600">{formatCurrency(monthlyAmount)}</span>
                      </label>
                      <Slider
                        min={1000}
                        max={50000}
                        step={1000}
                        value={monthlyAmount}
                        onChange={setMonthlyAmount}
                        color="blue"
                        format={(v) => formatCurrency(v)}
                      />
                    </div>

                    {/* Years Slider */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-4">
                        Years to Invest: <span className="text-lg text-blue-600">{yearsInvesting}</span>
                      </label>
                      <Slider
                        min={1}
                        max={40}
                        step={1}
                        value={yearsInvesting}
                        onChange={setYearsInvesting}
                        color="blue"
                        format={(v) => `${v} years`}
                      />
                    </div>
                  </div>
                </Card>

                {/* Results Summary */}
                <div className="grid md:grid-cols-3 gap-6">
                  <Card className="bg-gradient-to-br from-gray-50 to-gray-100 border-2 border-gray-200 p-6">
                    <p className="text-sm text-gray-600 font-semibold mb-2">Your Contributions</p>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(result.totalInvested)}</p>
                  </Card>
                  <Card className="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 p-6">
                    <p className="text-sm text-green-600 font-semibold mb-2">Investment Growth</p>
                    <p className="text-2xl font-bold text-green-900">{formatCurrency(result.growth)}</p>
                  </Card>
                  <Card className="bg-gradient-to-br from-blue-50 to-cyan-100 border-2 border-blue-200 p-6">
                    <p className="text-sm text-blue-600 font-semibold mb-2">Total Value at Age 65</p>
                    <p className="text-2xl font-bold text-blue-900">{formatCurrency(result.finalAmount)}</p>
                  </Card>
                </div>

                {/* Chart */}
                <Card className="p-6 border-2 border-gray-200">
                  <h3 className="font-bold text-lg mb-6">Growth Over Time</h3>
                  <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="year" />
                        <YAxis />
                        <Tooltip formatter={(value: number) => formatCurrency(value)} />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="amount"
                          stroke="#0891b2"
                          strokeWidth={3}
                          dot={false}
                          name="Total Value"
                        />
                        <Line
                          type="monotone"
                          dataKey="contributions"
                          stroke="#6b7280"
                          strokeWidth={2}
                          dot={false}
                          strokeDasharray="5 5"
                          name="Your Contributions"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </Card>

                <div className="flex justify-between">
                  <Button
                    onClick={() => setCurrentStep(currentStep - 1)}
                    variant="outline"
                  >
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    See Your Results →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 5: Insights & Results */}
            {currentStep === 5 && (
              <motion.div
                key="step5"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="space-y-6"
              >
                <InsightsPanel
                  title="Your Personalized Insights"
                  mainInsight={getMainInsight()}
                  additionalInsights={compoundInterestConfig.fallbackInsights.slice(0, 3).map(text => ({
                    text,
                    type: 'tip' as const
                  }))}
                  highlightColor="blue"
                  showComparison
                  comparisonText={`You're planning to start at age ${investmentAge}. Compared to Emma (started at 25): You'll have less time to compound, but starting NOW is still better than waiting to age 45!`}
                />

                <Card className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-200 p-6 md:p-8">
                  <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-4">💡 Key Takeaway</h3>
                  <p className="text-gray-700 text-lg leading-relaxed mb-4">
                    Time is your greatest wealth-building asset. Every year you delay matters. But the good news: <strong>starting today is always better than waiting</strong>.
                  </p>
                  <p className="text-gray-700">
                    Even if you're starting at age 35 or 45, consistent investing will pay off. Use this plan to stay committed and auto-invest monthly through SIP.
                  </p>
                </Card>

                <div className="text-center">
                  <Button
                    onClick={handleComplete}
                    variant="primary"
                    size="lg"
                    className="mb-4"
                  >
                    {xpEarned ? '✓ Completed!' : 'Complete Simulation (+500 XP)'}
                  </Button>
                  {xpEarned && (
                    <p className="text-sm text-green-600 font-semibold">
                      🎉 Great job! You've earned 500 XP and unlocked the "Time Traveler" badge!
                    </p>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  )
}
