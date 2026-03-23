'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { IntroSlide } from '@/components/simulations/IntroSlide'
import { ExampleCardsPanel } from '@/components/simulations/ExampleCardsPanel'
import { InsightsPanel } from '@/components/simulations/InsightsPanel'
import { StepProgressBar } from '@/components/simulations/StepProgressBar'
import { SafetyNetInfographic } from './components/SafetyNetInfographic'
import { emergencyFundConfig } from './config'

const steps = [
  { number: 1, label: 'Introduction' },
  { number: 2, label: 'Why It Matters' },
  { number: 3, label: 'Real Examples' },
  { number: 4, label: 'Build Yours' },
  { number: 5, label: 'Your Plan' }
]

export default function EmergencyFundPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [monthlyExpenses, setMonthlyExpenses] = useState(50000)
  const [targetMonths, setTargetMonths] = useState(6)
  const [xpEarned, setXpEarned] = useState(false)

  const targetAmount = monthlyExpenses * targetMonths
  const annualSavings = (monthlyExpenses * 0.20) * 12 // Assuming 20% of income
  const monthsToTarget = Math.ceil(targetAmount / (annualSavings / 12))

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1)
    }
  }

  const getMainInsight = () => {
    const threshold = targetMonths >= 6 ? 'high' : targetMonths >= 3 ? 'medium' : 'low'
    const template = emergencyFundConfig.insightTemplates.find(t => t.threshold === threshold)

    if (!template) return { text: emergencyFundConfig.fallbackInsights[0], type: 'success' as const }

    const text = template.text
      .replace('{fund_amount}', formatCurrency(targetAmount))
      .replace('{months}', `${targetMonths}`)
      .replace('{full_target}', formatCurrency(monthlyExpenses * 6))
      .replace('{monthly_needed}', formatCurrency((monthlyExpenses * 6) / 12))
      .replace('{months_to_goal}', `${Math.ceil((monthlyExpenses * 6) / ((monthlyExpenses * 0.20)))}`)
      .replace('{target}', formatCurrency(monthlyExpenses * 3))
      .replace('{months_needed}', `${Math.ceil((monthlyExpenses * 3) / ((monthlyExpenses * 0.20)))}`)

    return {
      text,
      type: threshold === 'high' ? 'success' : threshold === 'medium' ? 'recommendation' : 'tip'
    }
  }

  return (
    <motion.div className="min-h-screen bg-gradient-to-b from-gray-50 to-white p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
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
                  title={emergencyFundConfig.intro.title}
                  description={emergencyFundConfig.intro.description}
                  icon={emergencyFundConfig.intro.icon}
                  whyItMatters={emergencyFundConfig.intro.whyItMatters}
                  onNext={handleNext}
                  highlightColor="blue"
                />
              </motion.div>
            )}

            {/* Step 2: Impact Visualization */}
            {currentStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <SafetyNetInfographic monthlyExpenses={monthlyExpenses} />
                <div className="flex justify-between mt-8">
                  <Button onClick={() => setCurrentStep(currentStep - 1)} variant="outline">
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    See Examples →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 3: Real Examples */}
            {currentStep === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <ExampleCardsPanel
                  title="Emergency Fund Stories"
                  description="See how different fund sizes impact financial security"
                  examples={emergencyFundConfig.examples}
                  highlightColor="blue"
                />
                <div className="flex justify-between mt-8">
                  <Button onClick={() => setCurrentStep(currentStep - 1)} variant="outline">
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    Build Yours →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 4: Build Your Fund */}
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
                  <h2 className="text-3xl font-bold text-gray-900 mb-3">Build Your Safety Net</h2>
                  <p className="text-lg text-gray-600">Plan your emergency fund</p>
                </div>

                <Card className="p-8 border-2 border-blue-200 bg-blue-50">
                  <div className="space-y-8">
                    {/* Monthly Expenses */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-4">
                        Monthly Expenses: <span className="text-lg text-blue-600">{formatCurrency(monthlyExpenses)}</span>
                      </label>
                      <Slider
                        min={20000}
                        max={150000}
                        step={5000}
                        value={monthlyExpenses}
                        onChange={setMonthlyExpenses}
                        color="blue"
                        format={(v) => formatCurrency(v)}
                      />
                    </div>

                    {/* Target Months */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-4">
                        Target Months: <span className="text-lg text-blue-600">{targetMonths} months</span>
                      </label>
                      <Slider
                        min={1}
                        max={12}
                        step={1}
                        value={targetMonths}
                        onChange={setTargetMonths}
                        color="blue"
                        format={(v) => `${v} months`}
                      />
                      <p className="text-xs text-gray-600 mt-2">Recommended: 6 months</p>
                    </div>
                  </div>
                </Card>

                {/* Target Summary */}
                <div className="grid md:grid-cols-2 gap-6">
                  <Card className="bg-red-50 border-2 border-red-200 p-6">
                    <h3 className="font-bold text-lg text-red-900 mb-3">Your Target</h3>
                    <p className="text-3xl font-bold text-red-600">{formatCurrency(targetAmount)}</p>
                    <p className="text-sm text-red-700 mt-2">{monthsToTarget} months of saving</p>
                  </Card>

                  <Card className="bg-green-50 border-2 border-green-200 p-6">
                    <h3 className="font-bold text-lg text-green-900 mb-3">Monthly Savings Needed</h3>
                    <p className="text-3xl font-bold text-green-600">{formatCurrency(Math.round(targetAmount / monthsToTarget))}</p>
                    <p className="text-sm text-green-700 mt-2">Starting today (at {monthsToTarget} month pace)</p>
                  </Card>
                </div>

                <div className="flex justify-between">
                  <Button onClick={() => setCurrentStep(currentStep - 1)} variant="outline">
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    See Your Results →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 5: Results & Insights */}
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
                  title="Your Emergency Fund Plan"
                  mainInsight={getMainInsight()}
                  additionalInsights={emergencyFundConfig.fallbackInsights.slice(0, 3).map(text => ({
                    text,
                    type: 'tip' as const
                  }))}
                  highlightColor="blue"
                />

                <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 p-6 md:p-8">
                  <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-4">💡 Action Plan</h3>
                  <ol className="space-y-3 text-gray-700">
                    <li><strong>1. Set Target:</strong> {targetMonths} months of expenses = {formatCurrency(targetAmount)}</li>
                    <li><strong>2. Monthly Contribution:</strong> Save {formatCurrency(Math.round(targetAmount / monthsToTarget))} per month</li>
                    <li><strong>3. Keep it Separate:</strong> Use a dedicated savings account (not invested)</li>
                    <li><strong>4. Don't Touch It:</strong> Reserve only for true emergencies</li>
                    <li><strong>5. Automate:</strong> Set up automatic transfers on payday</li>
                  </ol>
                </Card>

                <div className="text-center">
                  <Button
                    onClick={() => setXpEarned(true)}
                    variant="primary"
                    size="lg"
                    className="mb-4"
                  >
                    {xpEarned ? '✓ Completed!' : 'Complete Simulation (+350 XP)'}
                  </Button>
                  {xpEarned && (
                    <p className="text-sm text-green-600 font-semibold">
                      🎉 Safety Net Built! You've earned 350 XP!
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
