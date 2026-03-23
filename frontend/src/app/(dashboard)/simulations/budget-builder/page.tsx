'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'
import { IntroSlide } from '@/components/simulations/IntroSlide'
import { ExampleCardsPanel } from '@/components/simulations/ExampleCardsPanel'
import { InsightsPanel } from '@/components/simulations/InsightsPanel'
import { StepProgressBar } from '@/components/simulations/StepProgressBar'
import { BudgetFrameworkInfographic } from './components/BudgetFrameworkInfographic'
import { budgetBuilderConfig } from './config'

const steps = [
  { number: 1, label: 'Introduction' },
  { number: 2, label: 'The Framework' },
  { number: 3, label: 'Real Examples' },
  { number: 4, label: 'Your Budget' },
  { number: 5, label: 'Your Plan' }
]

export default function BudgetBuilderPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [monthlyIncome, setMonthlyIncome] = useState(100000)
  const [xpEarned, setXpEarned] = useState(false)

  const needs = monthlyIncome * 0.50
  const wants = monthlyIncome * 0.30
  const savings = monthlyIncome * 0.20

  const pieData = [
    { name: 'Needs', value: needs, fill: '#ef4444' },
    { name: 'Wants', value: wants, fill: '#f59e0b' },
    { name: 'Savings', value: savings, fill: '#10b981' }
  ]

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1)
    }
  }

  const getMainInsight = () => {
    const savingsRatio = (savings / monthlyIncome) * 100
    const threshold = savingsRatio >= 20 ? 'high' : savingsRatio >= 15 ? 'medium' : 'low'
    const template = budgetBuilderConfig.insightTemplates.find(t => t.threshold === threshold)

    if (!template) return { text: budgetBuilderConfig.fallbackInsights[0], type: 'success' as const }

    const text = template.text
      .replace('{needs}', formatCurrency(needs))
      .replace('{needs_pct}', '50')
      .replace('{wants}', formatCurrency(wants))
      .replace('{wants_pct}', '30')
      .replace('{savings}', formatCurrency(savings))
      .replace('{savings_pct}', '20')
      .replace('{reduce}', formatCurrency(wants * 0.1))
      .replace('{new_savings}', formatCurrency(savings + wants * 0.1))
      .replace('{needed}', formatCurrency(monthlyIncome * 0.05))
      .replace('{pct}', `${(savings / monthlyIncome * 100).toFixed(0)}`

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
          highlightColor="purple"
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
                  title={budgetBuilderConfig.intro.title}
                  description={budgetBuilderConfig.intro.description}
                  icon={budgetBuilderConfig.intro.icon}
                  whyItMatters={budgetBuilderConfig.intro.whyItMatters}
                  onNext={handleNext}
                  highlightColor="purple"
                />
              </motion.div>
            )}

            {/* Step 2: The Framework */}
            {currentStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <BudgetFrameworkInfographic monthlyIncome={monthlyIncome} />
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
                  title="Budget Examples by Life Stage"
                  description="How different people apply the 50/30/20 rule"
                  examples={budgetBuilderConfig.examples}
                  highlightColor="purple"
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

            {/* Step 4: Your Budget */}
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
                  <h2 className="text-3xl font-bold text-gray-900 mb-3">Build Your 50/30/20 Budget</h2>
                  <p className="text-lg text-gray-600">Enter your income to see your ideal allocation</p>
                </div>

                <Card className="p-8 border-2 border-purple-200 bg-purple-50">
                  <label className="block text-sm font-semibold text-gray-900 mb-4">
                    Monthly Income: <span className="text-lg text-purple-600">{formatCurrency(monthlyIncome)}</span>
                  </label>
                  <Slider
                    min={30000}
                    max={500000}
                    step={10000}
                    value={monthlyIncome}
                    onChange={setMonthlyIncome}
                    color="purple"
                    format={(v) => formatCurrency(v)}
                  />
                </Card>

                {/* Budget Breakdown Cards */}
                <div className="grid md:grid-cols-3 gap-6">
                  <Card className="bg-red-50 border-2 border-red-200 p-6">
                    <h3 className="font-bold text-lg text-red-900 mb-3">NEEDS (50%)</h3>
                    <p className="text-2xl font-bold text-red-600 mb-2">{formatCurrency(needs)}</p>
                    <p className="text-sm text-red-700">Rent, Food, Utilities, Insurance</p>
                  </Card>

                  <Card className="bg-amber-50 border-2 border-amber-200 p-6">
                    <h3 className="font-bold text-lg text-amber-900 mb-3">WANTS (30%)</h3>
                    <p className="text-2xl font-bold text-amber-600 mb-2">{formatCurrency(wants)}</p>
                    <p className="text-sm text-amber-700">Entertainment, Dining, Shopping</p>
                  </Card>

                  <Card className="bg-green-50 border-2 border-green-200 p-6">
                    <h3 className="font-bold text-lg text-green-900 mb-3">SAVINGS (20%)</h3>
                    <p className="text-2xl font-bold text-green-600 mb-2">{formatCurrency(savings)}</p>
                    <p className="text-sm text-green-700">Investments, Emergency Fund</p>
                  </Card>
                </div>

                {/* Pie Chart */}
                <Card className="p-6 border-2 border-gray-200">
                  <h3 className="font-bold text-lg mb-6">Your Budget Pie</h3>
                  <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={120}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => formatCurrency(value)} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </Card>

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

            {/* Step 5: Your Plan */}
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
                  title="Your Budget Plan"
                  mainInsight={getMainInsight()}
                  additionalInsights={budgetBuilderConfig.fallbackInsights.slice(0, 3).map(text => ({
                    text,
                    type: 'tip' as const
                  }))}
                  highlightColor="purple"
                />

                <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 p-6 md:p-8">
                  <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-4">📋 Your Action Plan</h3>
                  <ol className="space-y-3 text-gray-700">
                    <li><strong>1. TRACK:</strong> Categorize all expenses as Needs, Wants, or Savings</li>
                    <li><strong>2. ALLOCATE:</strong> Set spending limits: {formatCurrency(needs)} (Needs), {formatCurrency(wants)} (Wants), {formatCurrency(savings)} (Savings)</li>
                    <li><strong>3. SEPARATE:</strong> Use different accounts for each category</li>
                    <li><strong>4. AUTOMATE:</strong> Set up automatic transfers to savings on payday</li>
                    <li><strong>5. REVIEW:</strong> Check your budget monthly and adjust as needed</li>
                  </ol>
                </Card>

                <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 p-6 md:p-8">
                  <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-3">💡 Pro Tips</h3>
                  <ul className="space-y-2 text-gray-700">
                    <li>✓ Start with rough estimates, then refine based on actual spending</li>
                    <li>✓ The 50/30/20 rule is flexible—adjust based on your life stage</li>
                    <li>✓ If Needs exceed 50%, work on reducing them or increasing income</li>
                    <li>✓ Increasing the Savings% accelerates wealth building dramatically</li>
                  </ul>
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
                      ✨ Budget Master! Earned 300 XP!
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
