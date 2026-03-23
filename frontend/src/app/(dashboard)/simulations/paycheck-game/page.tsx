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
import { MoneyPieInfographic } from './components/MoneyPieInfographic'
import { paycheckGameConfig } from './config'

const steps = [
  { number: 1, label: 'Introduction' },
  { number: 2, label: 'How Money Works' },
  { number: 3, label: 'Real Examples' },
  { number: 4, label: 'Your Strategy' },
  { number: 5, label: 'Your Results' }
]

export default function PaycheckGamePage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [income, setIncome] = useState(50000)
  const [strategy, setStrategy] = useState<'save_first' | 'bills_first' | 'spend_first'>('save_first')
  const [xpEarned, setXpEarned] = useState(false)

  const strategies = {
    save_first: {
      name: 'Save First',
      description: 'Save first, then spend on bills & wants (recommended)',
      savings: income * 0.20,
      stress: 'low',
      color: 'green'
    },
    bills_first: {
      name: 'Bills First',
      description: 'Pay bills, then spend and save',
      savings: income * 0.10,
      stress: 'medium',
      color: 'amber'
    },
    spend_first: {
      name: 'Spend First',
      description: 'Spend first, save what\'s left (risky)',
      savings: income * 0.02,
      stress: 'high',
      color: 'red'
    }
  }

  const currentStrategy = strategies[strategy]
  const annualSavings = currentStrategy.savings * 12
  const fiveYearSavings = annualSavings * 5

  const strategyData = [
    { name: 'Save First', saved: income * 0.20 * 12 },
    { name: 'Bills First', saved: income * 0.10 * 12 },
    { name: 'Spend First', saved: income * 0.02 * 12 }
  ]

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1)
    }
  }

  const getMainInsight = () => {
    const threshold = strategy === 'save_first' ? 'high' : strategy === 'bills_first' ? 'medium' : 'low'
    const template = paycheckGameConfig.insightTemplates.find(t => t.threshold === threshold)

    if (!template) return { text: paycheckGameConfig.fallbackInsights[0], type: 'success' as const }

    const text = template.text
      .replace('{saved_amount}', formatCurrency(currentStrategy.savings))
      .replace('{annual_saved}', formatCurrency(annualSavings))
      .replace('{five_year_savings}', formatCurrency(fiveYearSavings))
      .replace('{optimized_amount}', formatCurrency(currentStrategy.savings * 1.5))
      .replace('{recommended_amount}', formatCurrency(currentStrategy.savings + 2000))

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
          highlightColor="green"
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
                  title={paycheckGameConfig.intro.title}
                  description={paycheckGameConfig.intro.description}
                  icon={paycheckGameConfig.intro.icon}
                  whyItMatters={paycheckGameConfig.intro.whyItMatters}
                  onNext={handleNext}
                  highlightColor={paycheckGameConfig.intro.highlightColor}
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
                <MoneyPieInfographic income={income} />
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
                  title="How Different Strategies Work"
                  description="Three friends, three approaches, vastly different outcomes"
                  examples={paycheckGameConfig.examples}
                  highlightColor="green"
                />
                <div className="flex justify-between mt-8">
                  <Button
                    onClick={() => setCurrentStep(currentStep - 1)}
                    variant="outline"
                  >
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    Choose Your Strategy →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 4: Strategy Selection */}
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
                  <h2 className="text-3xl font-bold text-gray-900 mb-3">Your Paycheck Strategy</h2>
                  <p className="text-lg text-gray-600">Income: {formatCurrency(income)}/month</p>
                </div>

                {/* Income Slider */}
                <Card className="p-8 border-2 border-green-200 bg-green-50">
                  <label className="block text-sm font-semibold text-gray-900 mb-4">
                    Monthly Income: <span className="text-lg text-green-600">{formatCurrency(income)}</span>
                  </label>
                  <Slider
                    min={20000}
                    max={200000}
                    step={5000}
                    value={income}
                    onChange={setIncome}
                    color="green"
                    format={(v) => formatCurrency(v)}
                  />
                </Card>

                {/* Strategy Cards */}
                <div className="grid md:grid-cols-3 gap-6">
                  {Object.entries(strategies).map(([key, strat]) => (
                    <div
                      key={key}
                      onClick={() => setStrategy(key as 'save_first' | 'bills_first' | 'spend_first')}
                      className={`cursor-pointer transition-all transform ${
                        strategy === key ? 'ring-2 ring-offset-2 ring-green-500 scale-105' : ''
                      }`}
                    >
                      <Card className={`p-6 h-full border-2 hover:shadow-lg ${
                        strat.color === 'green' ? 'border-green-200 bg-green-50' :
                        strat.color === 'amber' ? 'border-amber-200 bg-amber-50' :
                        'border-red-200 bg-red-50'
                      }`}>
                        <h3 className={`font-bold text-lg mb-2 ${
                          strat.color === 'green' ? 'text-green-900' :
                          strat.color === 'amber' ? 'text-amber-900' :
                          'text-red-900'
                        }`}>{strat.name}</h3>
                        <p className="text-sm text-gray-700 mb-4">{strat.description}</p>
                        <div className={`p-3 rounded-lg mb-3 ${
                          strat.color === 'green' ? 'bg-green-100' :
                          strat.color === 'amber' ? 'bg-amber-100' :
                          'bg-red-100'
                        }`}>
                          <p className={`text-xs font-semibold mb-1 ${
                            strat.color === 'green' ? 'text-green-600' :
                            strat.color === 'amber' ? 'text-amber-600' :
                            'text-red-600'
                          }`}>Monthly Savings</p>
                          <p className="text-xl font-bold">{formatCurrency(strat.savings)}</p>
                        </div>
                        <div className={`px-3 py-2 rounded text-sm font-bold ${
                          strat.color === 'green' ? 'bg-green-200 text-green-900' :
                          strat.color === 'amber' ? 'bg-amber-200 text-amber-900' :
                          'bg-red-200 text-red-900'
                        }`}>
                          Stress Level: {strat.stress}
                        </div>
                      </Card>
                    </div>
                  ))}
                </div>

                {/* Comparison Chart */}
                <Card className="p-6 border-2 border-gray-200">
                  <h3 className="font-bold text-lg mb-6">Monthly Savings Comparison</h3>
                  <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={strategyData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip formatter={(value: number) => formatCurrency(value)} />
                        <Bar dataKey="saved" fill="#10b981" radius={[8, 8, 0, 0]} />
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
                  title="Your Strategy Analysis"
                  mainInsight={getMainInsight()}
                  additionalInsights={paycheckGameConfig.fallbackInsights.slice(0, 3).map(text => ({
                    text,
                    type: 'tip' as const
                  }))}
                  highlightColor="green"
                  showComparison
                  comparisonText={`You chose "${currentStrategy.name}". Compared to "Save First": You'd save ${Math.round((strategies.save_first.savings - currentStrategy.savings) / currentStrategy.savings * 100)}% less per month. Over 5 years, that's ${formatCurrency((strategies.save_first.savings - currentStrategy.savings) * 12 * 5)} difference!`}
                />

                <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 p-6 md:p-8">
                  <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-4">💡 The "Pay Yourself First" Principle</h3>
                  <p className="text-gray-700 text-lg leading-relaxed">
                    When you save first, two powerful things happen: <strong>(1)</strong> You naturally reduce spending on wants, and <strong>(2)</strong> Your savings compound and grow effortlessly. This single principle separates the wealthy from the broke.
                  </p>
                </Card>

                <div className="text-center">
                  <Button
                    onClick={() => setXpEarned(true)}
                    variant="primary"
                    size="lg"
                    className="mb-4"
                  >
                    {xpEarned ? '✓ Completed!' : 'Complete Simulation (+300 XP)'}
                  </Button>
                  {xpEarned && (
                    <p className="text-sm text-green-600 font-semibold">
                      🎉 Excellent! You've earned 300 XP!
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
