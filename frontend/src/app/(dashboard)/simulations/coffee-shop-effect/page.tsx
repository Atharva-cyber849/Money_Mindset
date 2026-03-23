'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { IntroSlide } from '@/components/simulations/IntroSlide'
import { ExampleCardsPanel } from '@/components/simulations/ExampleCardsPanel'
import { InsightsPanel } from '@/components/simulations/InsightsPanel'
import { StepProgressBar } from '@/components/simulations/StepProgressBar'
import { DailyLeakInfographic } from './components/DailyLeakInfographic'
import { coffeeShopEffectConfig } from './config'

const steps = [
  { number: 1, label: 'Introduction' },
  { number: 2, label: 'The Impact' },
  { number: 3, label: 'Real Examples' },
  { number: 4, label: 'Your Spending' },
  { number: 5, label: 'The Potential' }
]

export default function CoffeeShopEffectPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [dailyAmount, setDailyAmount] = useState(100)
  const [xpEarned, setXpEarned] = useState(false)

  const annualAmount = dailyAmount * 365
  const fiveYearAmount = annualAmount * 5
  const tenYearAmount = annualAmount * 10
  const invested10Years = annualAmount * 10 * (Math.pow(1.12, 10))

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1)
    }
  }

  const getMainInsight = () => {
    const template = coffeeShopEffectConfig.insightTemplates[0]
    const text = template.text
      .replace('{annual_amount}', formatCurrency(annualAmount))
      .replace('{invested_value}', formatCurrency(invested10Years))

    return {
      text,
      type: 'success' as const
    }
  }

  const chartData = [
    { period: '1 Year', spent: annualAmount },
    { period: '5 Years', spent: fiveYearAmount },
    { period: '10 Years', spent: tenYearAmount },
    { period: '20 Years', spent: annualAmount * 20 }
  ]

  return (
    <motion.div className="min-h-screen bg-gradient-to-b from-gray-50 to-white p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <StepProgressBar
          currentStep={currentStep}
          totalSteps={5}
          steps={steps}
          highlightColor="amber"
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
                  title={coffeeShopEffectConfig.intro.title}
                  description={coffeeShopEffectConfig.intro.description}
                  icon={coffeeShopEffectConfig.intro.icon}
                  whyItMatters={coffeeShopEffectConfig.intro.whyItMatters}
                  onNext={handleNext}
                  highlightColor="amber"
                />
              </motion.div>
            )}

            {/* Step 2: Impact Infographic */}
            {currentStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <DailyLeakInfographic dailyAmount={dailyAmount} />
                <div className="flex justify-between mt-8">
                  <Button
                    onClick={() => setCurrentStep(currentStep - 1)}
                    variant="outline"
                  >
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
                  title="Different Daily Spending Habits"
                  description="See how small daily differences compound over years"
                  examples={coffeeShopEffectConfig.examples}
                  highlightColor="amber"
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
                  <h2 className="text-3xl font-bold text-gray-900 mb-3">Your Daily Spending</h2>
                  <p className="text-lg text-gray-600">How much do you spend daily on discretionary items?</p>
                </div>

                <Card className="p-8 border-2 border-amber-200 bg-amber-50">
                  <label className="block text-sm font-semibold text-gray-900 mb-4">
                    Daily Amount: <span className="text-lg text-amber-600">₹{dailyAmount}</span>
                  </label>
                  <Slider
                    min={10}
                    max={500}
                    step={10}
                    value={dailyAmount}
                    onChange={setDailyAmount}
                    color="yellow"
                    format={(v) => `₹${v}/day`}
                  />
                </Card>

                {/* Impact Cards */}
                <div className="grid md:grid-cols-2 gap-6">
                  <Card className="bg-red-50 border-2 border-red-200 p-6">
                    <h3 className="font-bold text-lg text-red-900 mb-3">Annual Cost</h3>
                    <p className="text-3xl font-bold text-red-600">{formatCurrency(annualAmount)}</p>
                    <p className="text-sm text-red-700 mt-2">That's like {Math.round(annualAmount / 500)} movies or {Math.round(annualAmount / 2000)} dinners!</p>
                  </Card>

                  <Card className="bg-green-50 border-2 border-green-200 p-6">
                    <h3 className="font-bold text-lg text-green-900 mb-3">If Invested (10 years @ 12%)</h3>
                    <p className="text-3xl font-bold text-green-600">{formatCurrency(invested10Years)}</p>
                    <p className="text-sm text-green-700 mt-2">That's {Math.round(invested10Years / annualAmount)}x your annual spending!</p>
                  </Card>
                </div>

                {/* Comparison Chart */}
                <Card className="p-6 border-2 border-gray-200">
                  <h3 className="font-bold text-lg mb-6">Cumulative Spending Over Time</h3>
                  <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="period" />
                        <YAxis />
                        <Tooltip formatter={(value: number) => formatCurrency(value)} />
                        <Bar dataKey="spent" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                      </BarChart>
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
                    See the Potential →
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
                  title="The Real Cost of Your Spending"
                  mainInsight={getMainInsight()}
                  additionalInsights={coffeeShopEffectConfig.fallbackInsights.slice(0, 4).map(text => ({
                    text,
                    type: 'tip' as const
                  }))}
                  highlightColor="amber"
                />

                <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 p-6 md:p-8">
                  <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-4">💡 What Could You Do Instead?</h3>
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="bg-white rounded p-4 border border-blue-200">
                      <p className="font-bold text-blue-900 mb-2">Save It</p>
                      <p className="text-sm text-gray-700">Build {formatCurrency(annualAmount)} emergency fund yearly</p>
                    </div>
                    <div className="bg-white rounded p-4 border border-blue-200">
                      <p className="font-bold text-blue-900 mb-2">Invest It</p>
                      <p className="text-sm text-gray-700">Grow to {formatCurrency(invested10Years)} in 10 years</p>
                    </div>
                    <div className="bg-white rounded p-4 border border-blue-200">
                      <p className="font-bold text-blue-900 mb-2">Enjoy Mindfully</p>
                      <p className="text-sm text-gray-700">Reduce by 50% = {formatCurrency(annualAmount / 2)} saved yearly</p>
                    </div>
                  </div>
                </Card>

                <div className="text-center">
                  <Button
                    onClick={() => setXpEarned(true)}
                    variant="primary"
                    size="lg"
                    className="mb-4"
                  >
                    {xpEarned ? '✓ Completed!' : 'Complete Simulation (+250 XP)'}
                  </Button>
                  {xpEarned && (
                    <p className="text-sm text-green-600 font-semibold">
                      🎉 Great awareness! You've earned 250 XP!
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
