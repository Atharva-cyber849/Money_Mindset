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
import { CarPathsInfographic } from './components/CarPathsInfographic'
import { carPaymentConfig } from './config'

const steps = [
  { number: 1, label: 'Introduction' },
  { number: 2, label: '3 Paths' },
  { number: 3, label: 'Examples' },
  { number: 4, label: 'Your Budget' },
  { number: 5, label: 'Recommendation' }
]

export default function CarPaymentPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [carPrice, setCarPrice] = useState(1500000)
  const [monthlyBudget, setMonthlyBudget] = useState(30000)
  const [xpEarned, setXpEarned] = useState(false)

  // Three options
  const lease = {
    monthlyPayment: 25000,
    upfront: 0,
    duration: 36,
    totalCost: 25000 * 36 + 10000
  }

  const finance = {
    downPayment: carPrice * 0.20,
    monthlyPayment: 22000,
    duration: 84,
    totalCost: carPrice * .20 + 22000 * 84
  }

  const cash = {
    upfront: carPrice,
    monthlyPayment: 0,
    duration: 120,
    totalCost: carPrice
  }

  const comparisonData = [
    { option: 'Lease', totalCost: lease.totalCost },
    { option: 'Finance', totalCost: finance.totalCost },
    { option: 'Cash', totalCost: cash.totalCost }
  ]

  const handleNext = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1)
    }
  }

  const getBestOption = () => {
    if (monthlyBudget < lease.monthlyPayment) {
      return 'cash'
    } else if (monthlyBudget < finance.monthlyPayment) {
      return 'lease'
    } else {
      return 'finance'
    }
  }

  const getMainInsight = () => {
    const best = getBestOption()
    const template = carPaymentConfig.insightTemplates.find(t => t.threshold === best)

    if (!template) return { text: carPaymentConfig.fallbackInsights[0], type: 'success' as const }

    const text = template.text
      .replace('{strategy}', best === 'cash' ? 'PAY CASH' : best === 'lease' ? 'LEASE' : 'FINANCE')
      .replace('{total_cost}', formatCurrency(best === 'cash' ? cash.totalCost : best === 'lease' ? lease.totalCost : finance.totalCost))
      .replace('{percentage}', `${((monthlyBudget / (finance.monthlyPayment + finance.downPayment/84)) * 100).toFixed(0)}`)
      .replace('{recommended_budget}', formatCurrency(Math.round((finance.monthlyPayment + finance.downPayment/84) * 0.15)))

    return {
      text,
      type: 'success'
    }
  }

  return (
    <motion.div className="min-h-screen bg-gradient-to-b from-gray-50 to-white p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <StepProgressBar
          currentStep={currentStep}
          totalSteps={5}
          steps={steps}
          highlightColor="teal"
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
                  title={carPaymentConfig.intro.title}
                  description={carPaymentConfig.intro.description}
                  icon={carPaymentConfig.intro.icon}
                  whyItMatters={carPaymentConfig.intro.whyItMatters}
                  onNext={handleNext}
                  highlightColor="teal"
                />
              </motion.div>
            )}

            {/* Step 2: The 3 Paths */}
            {currentStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <CarPathsInfographic carPrice={carPrice} />
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

            {/* Step 3: Examples */}
            {currentStep === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <ExampleCardsPanel
                  title="Real Car Purchase Scenarios"
                  description="See how different choices play out over time"
                  examples={carPaymentConfig.examples}
                  highlightColor="teal"
                />
                <div className="flex justify-between mt-8">
                  <Button onClick={() => setCurrentStep(currentStep - 1)} variant="outline">
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    Find Your Best Option →
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
                  <h2 className="text-3xl font-bold text-gray-900 mb-3">Find Your Best Car Option</h2>
                  <p className="text-lg text-gray-600">Adjust your budget and car price</p>
                </div>

                <Card className="p-8 border-2 border-teal-200 bg-teal-50">
                  <div className="space-y-8">
                    {/* Car Price */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-4">
                        Car Price: <span className="text-lg text-teal-600">{formatCurrency(carPrice)}</span>
                      </label>
                      <Slider
                        min={500000}
                        max={3000000}
                        step={100000}
                        value={carPrice}
                        onChange={setCarPrice}
                        color="blue"
                        format={(v) => formatCurrency(v)}
                      />
                    </div>

                    {/* Monthly Budget */}
                    <div>
                      <label className="block text-sm font-semibold text-gray-900 mb-4">
                        Monthly Budget: <span className="text-lg text-teal-600">{formatCurrency(monthlyBudget)}</span>
                      </label>
                      <Slider
                        min={10000}
                        max={100000}
                        step={5000}
                        value={monthlyBudget}
                        onChange={setMonthlyBudget}
                        color="blue"
                        format={(v) => formatCurrency(v)}
                      />
                    </div>
                  </div>
                </Card>

                {/* Option Comparison */}
                <div className="grid md:grid-cols-3 gap-6">
                  <Card className="bg-blue-50 border-2 border-blue-200 p-6">
                    <h3 className="font-bold text-lg text-blue-900 mb-3">LEASE</h3>
                    <p className="text-xl font-bold text-blue-600 mb-2">{formatCurrency(lease.monthlyPayment)}/mo</p>
                    <p className="text-sm text-blue-700">Always new car</p>
                    <p className="text-xs text-blue-600 mt-2">Total: {formatCurrency(lease.totalCost)}</p>
                  </Card>

                  <Card className="bg-amber-50 border-2 border-amber-200 p-6">
                    <h3 className="font-bold text-lg text-amber-900 mb-3">FINANCE</h3>
                    <p className="text-xl font-bold text-amber-600 mb-2">{formatCurrency(finance.monthlyPayment)}/mo</p>
                    <p className="text-sm text-amber-700">Down: {formatCurrency(finance.downPayment)}</p>
                    <p className="text-xs text-amber-600 mt-2">Total: {formatCurrency(finance.totalCost)}</p>
                  </Card>

                  <Card className="bg-green-50 border-2 border-green-200 p-6">
                    <h3 className="font-bold text-lg text-green-900 mb-3">CASH</h3>
                    <p className="text-xl font-bold text-green-600 mb-2">Upfront</p>
                    <p className="text-sm text-green-700">No EMI ever</p>
                    <p className="text-xs text-green-600 mt-2">Total: {formatCurrency(cash.totalCost)}</p>
                  </Card>
                </div>

                {/* Chart */}
                <Card className="p-6 border-2 border-gray-200">
                  <h3 className="font-bold text-lg mb-6">Total Cost Comparison</h3>
                  <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={comparisonData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="option" />
                        <YAxis />
                        <Tooltip formatter={(value: number) => formatCurrency(value)} />
                        <Bar dataKey="totalCost" fill="#0891b2" radius={[8, 8, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>

                <div className="flex justify-between">
                  <Button onClick={() => setCurrentStep(currentStep - 1)} variant="outline">
                    ← Back
                  </Button>
                  <Button onClick={handleNext} variant="primary">
                    See My Recommendation →
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Step 5: Recommendation */}
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
                  title="Your Best Car Option"
                  mainInsight={getMainInsight()}
                  additionalInsights={carPaymentConfig.fallbackInsights.slice(0, 3).map(text => ({
                    text,
                    type: 'tip' as const
                  }))}
                  highlightColor="teal"
                />

                <Card className="bg-gradient-to-r from-teal-50 to-cyan-50 border-2 border-teal-200 p-6 md:p-8">
                  <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-4">📋 Next Steps</h3>
                  <ol className="space-y-3 text-gray-700">
                    <li><strong>1. RESEARCH:</strong> Compare models within your budget</li>
                    <li><strong>2. NEGOTIATE:</strong> Dealers often have room to negotiate</li>
                    <li><strong>3. INSURANCE:</strong> Get quotes before committing</li>
                    <li><strong>4. MAINTENANCE:</strong> Budget ₹1-2K/month for upkeep</li>
                    <li><strong>5. REVIEW:</strong> Reassess after 3-5 years</li>
                  </ol>
                </Card>

                <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 p-6 md:p-8">
                  <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-3">💡 Golden Rule</h3>
                  <p className="text-gray-700 text-lg leading-relaxed">
                    Never buy a car that costs more than 50% of your annual income. Keep total car expenses (EMI + insurance + fuel + maintenance) below 15% of monthly income for financial health.
                  </p>
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
                      🚗 Smart Shopper! Earned 350 XP!
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
