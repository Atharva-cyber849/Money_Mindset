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
import { DebtTrapInfographic } from './components/DebtTrapInfographic'
import { creditCardDebtConfig } from './config'

const steps = [
  { number: 1, label: 'Introduction' },
  { number: 2, label: 'How It Compounds' },
  { number: 3, label: 'Real Scenarios' },
  { number: 4, label: 'Your Debt' },
  { number: 5, label: 'Payoff Plan' }
]

export default function CreditCardDebtPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [debtAmount, setDebtAmount] = useState(100000)
  const [monthlyPayment, setMonthlyPayment] = useState(5000)
  const [xpEarned, setXpEarned] = useState(false)

  const interestRate = 0.02 // 2% monthly (24% annual)

  // Calculate payoff time and interest
  let balance = debtAmount
  let totalInterest = 0
  let months = 0

  while (balance > 0 && months < 360) {
    const interest = balance * interestRate
    totalInterest += interest
    balance -= (monthlyPayment - interest)
    months++
  }

  const totalPaid = debtAmount + totalInterest

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1)
    }
  }

  const getMainInsight = () => {
    const threshold = monthlyPayment > debtAmount * 0.05 ? 'high' : monthlyPayment > debtAmount * 0.02 ? 'medium' : 'low'
    const template = creditCardDebtConfig.insightTemplates.find(t => t.threshold === threshold)

    if (!template) return { text: creditCardDebtConfig.fallbackInsights[0], type: 'success' as const }

    const text = template.text
      .replace('{amount}', formatCurrency(debtAmount))
      .replace('{payment_amount}', formatCurrency(monthlyPayment))
      .replace('{interest_monthly}', formatCurrency(debtAmount * interestRate))
      .replace('{needed_payment}', formatCurrency(Math.round(debtAmount * 0.05)))
      .replace('{months_aggressive}', `${Math.max(1, Math.ceil(debtAmount / monthlyPayment))}`)
      .replace('{months_minimum}', `${months}`)
      .replace('{total_interest}', formatCurrency(totalInterest))
      .replace('{payment}', formatCurrency(monthlyPayment))
      .replace('{months_total}', `${months}`)
      .replace('{optimized_payment}', formatCurrency(monthlyPayment * 1.5))
      .replace('{interest_saved}', formatCurrency(totalInterest * 0.3))

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
          highlightColor="red"
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
                  title={creditCardDebtConfig.intro.title}
                  description={creditCardDebtConfig.intro.description}
                  icon={creditCardDebtConfig.intro.icon}
                  whyItMatters={creditCardDebtConfig.intro.whyItMatters}
                  onNext={handleNext}
                  highlightColor="red"
                />
              </motion.div>
            )}

            {/* Step 2: How It Compounds */}
            {currentStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <DebtTrapInfographic initialBalance={debtAmount} />
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

            {/* Step 3: Real Scenarios */}
            {currentStep === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <ExampleCardsPanel
                  title="Debt Payoff Scenarios"
                  description="Compare minimum vs aggressive payment strategies"
                  examples={creditCardDebtConfig.examples}
                  highlightColor="red"
                />
                <div className="flex justify-between mt-8">
                  <Button onClick={() => setCurrentStep(currentStep - 1)} variant="outline">
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    Your Debt →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 4: Your Debt Calculator */}
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
                  <h2 className="text-3xl font-bold text-gray-900 mb-3">Your Debt Payoff Plan</h2>
                  <p className="text-lg text-gray-600">Let's calculate your fastest path to freedom</p>
                </div>

                <Card className="p-8 border-2 border-red-200 bg-red-50">
                  <div className="space-y-8">
                    {/* Debt Amount */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-4">
                        Total Debt: <span className="text-lg text-red-600">{formatCurrency(debtAmount)}</span>
                      </label>
                      <Slider
                        min={10000}
                        max={500000}
                        step={10000}
                        value={debtAmount}
                        onChange={setDebtAmount}
                        color="red"
                        format={(v) => formatCurrency(v)}
                      />
                    </div>

                    {/* Monthly Payment */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-4">
                        Monthly Payment: <span className="text-lg text-red-600">{formatCurrency(monthlyPayment)}</span>
                      </label>
                      <Slider
                        min={Math.round(debtAmount * 0.02)}
                        max={Math.round(debtAmount * 0.10)}
                        step={1000}
                        value={monthlyPayment}
                        onChange={setMonthlyPayment}
                        color="red"
                        format={(v) => formatCurrency(v)}
                      />
                      <p className="text-xs text-gray-600 mt-2">
                        Minimum recommended: {formatCurrency(Math.round(debtAmount * 0.05))}
                      </p>
                    </div>
                  </div>
                </Card>

                {/* Payoff Summary */}
                <div className="grid md:grid-cols-3 gap-6">
                  <Card className="bg-gray-50 border-2 border-gray-200 p-6">
                    <h3 className="font-bold text-lg text-gray-900 mb-3">Debt Amount</h3>
                    <p className="text-2xl font-bold text-gray-800">{formatCurrency(debtAmount)}</p>
                  </Card>

                  <Card className="bg-amber-50 border-2 border-amber-200 p-6">
                    <h3 className="font-bold text-lg text-amber-900 mb-3">Interest Paid</h3>
                    <p className="text-2xl font-bold text-amber-600">{formatCurrency(totalInterest)}</p>
                  </Card>

                  <Card className="bg-green-50 border-2 border-green-200 p-6">
                    <h3 className="font-bold text-lg text-green-900 mb-3">Months to Clear</h3>
                    <p className="text-2xl font-bold text-green-600">{months} months</p>
                    <p className="text-xs text-green-700 mt-1">({Math.floor(months / 12)} years {months % 12} months)</p>
                  </Card>
                </div>

                <div className="flex justify-between">
                  <Button onClick={() => setCurrentStep(currentStep - 1)} variant="outline">
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    See Your Plan →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 5: Payoff Plan & Insights */}
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
                  title="Your Debt Payoff Plan"
                  mainInsight={getMainInsight()}
                  additionalInsights={creditCardDebtConfig.fallbackInsights.slice(0, 3).map(text => ({
                    text,
                    type: 'tip' as const
                  }))}
                  highlightColor="red"
                />

                <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 p-6 md:p-8">
                  <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-4">📋 Your Action Plan</h3>
                  <ol className="space-y-3 text-gray-700">
                    <li><strong>1. TODAY:</strong> Pay {formatCurrency(monthlyPayment)} immediately</li>
                    <li><strong>2. MONTHLY:</strong> Set auto-payment for {formatCurrency(monthlyPayment)} on payday</li>
                    <li><strong>3. STOP USING:</strong> Don't make new charges on this card</li>
                    <li><strong>4. AGGRESSIVE PAY:</strong> Increase payment by 10% every 3 months if possible</li>
                    <li><strong>5. CELEBRATE:</strong> Debt-free in {months} months! 🎉</li>
                  </ol>
                </Card>

                <Card className="bg-red-50 border-2 border-red-200 p-6">
                  <p className="text-sm text-red-800">
                    <strong>Warning:</strong> At current payment rate, you'll pay {formatCurrency(totalInterest)} in interest. Every month you delay costs more!
                  </p>
                </Card>

                <div className="text-center">
                  <Button
                    onClick={() => setXpEarned(true)}
                    variant="primary"
                    size="lg"
                    className="mb-4"
                  >
                    {xpEarned ? '✓ Completed!' : 'Complete Simulation (+400 XP)'}
                  </Button>
                  {xpEarned && (
                    <p className="text-sm text-green-600 font-semibold">
                      💪 You've Got This! Earned 400 XP!
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
