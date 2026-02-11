'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Car, DollarSign, TrendingDown, AlertCircle, CheckCircle, ArrowRight, Calculator } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

// Step 1: Car Purchase
function StepCarChoice({ onNext }: { onNext: (carPrice: number, downPayment: number, interestRate: number, term: number) => void }) {
  const [carPrice, setCarPrice] = useState(30000)
  const [downPayment, setDownPayment] = useState(5000)
  const [interestRate, setInterestRate] = useState(6.5)
  const [term, setTerm] = useState(60) // months

  const loanAmount = carPrice - downPayment
  const monthlyRate = (interestRate / 100) / 12
  const monthlyPayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, term)) / (Math.pow(1 + monthlyRate, term) - 1)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-red-400 to-pink-500 rounded-full flex items-center justify-center">
          <Car className="w-12 h-12 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The True Cost of a Car Loan
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          That monthly payment is just the tip of the iceberg.
          <br />
          <span className="font-semibold text-gray-900">Let's calculate the REAL cost.</span>
        </p>
      </div>

      <Card className="max-w-4xl mx-auto">
        <div className="space-y-6">
          <Slider
            min={15000}
            max={60000}
            step={1000}
            value={carPrice}
            onChange={setCarPrice}
            label="Car Price"
            format={(v) => formatCurrency(v)}
            color="red"
          />
          <Slider
            min={0}
            max={carPrice * 0.4}
            step={500}
            value={downPayment}
            onChange={setDownPayment}
            label="Down Payment"
            format={(v) => formatCurrency(v)}
            color="green"
          />
          <Slider
            min={3}
            max={12}
            step={0.5}
            value={interestRate}
            onChange={setInterestRate}
            label="Interest Rate (APR)"
            format={(v) => `${v.toFixed(1)}%`}
            color="orange"
          />
          <Slider
            min={24}
            max={72}
            step={12}
            value={term}
            onChange={setTerm}
            label="Loan Term"
            format={(v) => `${v} months (${(v / 12).toFixed(0)} years)`}
            color="blue"
          />
        </div>

        <div className="mt-6 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-1">Your Monthly Payment</div>
            <div className="text-4xl font-bold text-blue-600">
              {formatCurrency(monthlyPayment)}
            </div>
            <div className="text-sm text-gray-500 mt-2">
              for {term} months
            </div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <Button onClick={() => onNext(carPrice, downPayment, interestRate, term)} size="lg">
            Calculate True Cost
            <ArrowRight className="w-5 h-5" />
          </Button>
        </div>
      </Card>
    </motion.div>
  )
}

// Step 2: True Cost Breakdown
function StepTrueCost({ carPrice, downPayment, interestRate, term, onNext }: {
  carPrice: number
  downPayment: number
  interestRate: number
  term: number
  onNext: () => void
}) {
  const loanAmount = carPrice - downPayment
  const monthlyRate = (interestRate / 100) / 12
  const monthlyPayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, term)) / (Math.pow(1 + monthlyRate, term) - 1)
  
  const totalPaid = monthlyPayment * term + downPayment
  const totalInterest = totalPaid - carPrice
  
  // Additional costs
  const insurance = 150 * term // $150/month
  const maintenance = 100 * term // $100/month
  const gas = 150 * term // $150/month
  const registration = 200 * (term / 12) // $200/year
  const depreciation = carPrice * 0.60 // 60% depreciation
  
  const totalOwnershipCost = totalPaid + insurance + maintenance + gas + registration
  const finalCarValue = carPrice - depreciation

  // Opportunity cost - what if invested instead
  const monthlyInvestment = monthlyPayment + 150 + 100 + 150 // payment + insurance + maintenance + gas
  const investmentYears = term / 12
  const investmentReturn = 0.08
  const futureValue = monthlyInvestment * (((Math.pow(1 + investmentReturn / 12, term) - 1) / (investmentReturn / 12)))

  const costsBreakdown = [
    { name: 'Principal', value: carPrice, color: '#3b82f6' },
    { name: 'Interest', value: totalInterest, color: '#ef4444' },
    { name: 'Insurance', value: insurance, color: '#f59e0b' },
    { name: 'Maintenance', value: maintenance, color: '#10b981' },
    { name: 'Gas', value: gas, color: '#8b5cf6' },
    { name: 'Registration', value: registration, color: '#ec4899' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The Shocking Reality 😱
        </h2>
      </div>

      {/* Main Cost Comparison */}
      <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-4">
        <Card className="text-center">
          <div className="text-sm text-gray-600 mb-2">Car Sticker Price</div>
          <div className="text-3xl font-bold text-blue-600">{formatCurrency(carPrice)}</div>
        </Card>
        <Card className="text-center bg-red-50">
          <div className="text-sm text-gray-600 mb-2">Total You'll Pay</div>
          <div className="text-3xl font-bold text-red-600">{formatCurrency(totalOwnershipCost)}</div>
        </Card>
        <Card className="text-center bg-yellow-50">
          <div className="text-sm text-gray-600 mb-2">Car's Value After</div>
          <div className="text-3xl font-bold text-yellow-600">{formatCurrency(finalCarValue)}</div>
        </Card>
      </div>

      {/* Interest Paid */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            You'll Pay {formatCurrency(totalInterest)} in Interest Alone!
          </h3>
          <p className="text-gray-700">
            That's {((totalInterest / carPrice) * 100).toFixed(0)}% extra on top of the car price
          </p>
        </div>
      </Card>

      {/* Cost Breakdown */}
      <Card className="max-w-4xl mx-auto">
        <h3 className="text-lg font-semibold mb-4 text-center">Complete Cost Breakdown</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={costsBreakdown}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
            <Tooltip formatter={(value) => formatCurrency(Number(value))} />
            <Bar dataKey="value" fill="#8884d8">
              {costsBreakdown.map((entry, index) => (
                <Bar key={`bar-${index}`} dataKey="value" fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Opportunity Cost */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
        <div className="text-center">
          <TrendingDown className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            The Opportunity Cost
          </h3>
          <p className="text-gray-700 mb-4">
            If you invested {formatCurrency(monthlyInvestment)}/month instead (8% return):
          </p>
          <div className="text-5xl font-bold text-green-600 mb-2">
            {formatCurrency(futureValue)}
          </div>
          <p className="text-sm text-gray-600">
            You'd have this much after {investmentYears.toFixed(0)} years!
          </p>
        </div>
      </Card>

      {/* Breakdown Table */}
      <Card className="max-w-4xl mx-auto">
        <h3 className="text-lg font-semibold mb-4">Monthly Costs</h3>
        <div className="space-y-2">
          <div className="flex justify-between p-2 bg-blue-50 rounded">
            <span>Loan Payment</span>
            <span className="font-bold">{formatCurrency(monthlyPayment)}</span>
          </div>
          <div className="flex justify-between p-2 bg-orange-50 rounded">
            <span>Insurance</span>
            <span className="font-bold">$150</span>
          </div>
          <div className="flex justify-between p-2 bg-green-50 rounded">
            <span>Maintenance</span>
            <span className="font-bold">$100</span>
          </div>
          <div className="flex justify-between p-2 bg-purple-50 rounded">
            <span>Gas</span>
            <span className="font-bold">$150</span>
          </div>
          <div className="flex justify-between p-3 bg-red-50 rounded border-t-2 border-red-200">
            <span className="font-bold">Total Monthly Cost</span>
            <span className="font-bold text-red-600">{formatCurrency(monthlyPayment + 400)}</span>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <Button onClick={onNext} size="lg">
          See Smarter Options
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 3: Better Alternatives
function StepAlternatives({ onNext }: { onNext: () => void }) {
  const scenarios = [
    {
      name: 'Buy New with Loan',
      carPrice: 30000,
      downPayment: 5000,
      loan: true,
      interestRate: 6.5,
      term: 60,
      color: 'red',
      icon: '🚗',
      description: 'The typical approach'
    },
    {
      name: 'Buy Used with Cash',
      carPrice: 15000,
      downPayment: 15000,
      loan: false,
      interestRate: 0,
      term: 0,
      color: 'yellow',
      icon: '🚙',
      description: 'Save first, then buy'
    },
    {
      name: 'Buy Reliable Used',
      carPrice: 8000,
      downPayment: 8000,
      loan: false,
      interestRate: 0,
      term: 0,
      color: 'green',
      icon: '🚕',
      description: 'Maximum value'
    },
  ]

  const calculateTotal = (scenario: typeof scenarios[0]) => {
    const years = Math.max(scenario.term / 12, 5)
    const insurance = 150 * 12 * years * (scenario.name.includes('New') ? 1 : 0.7)
    const maintenance = 100 * 12 * years * (scenario.name.includes('New') ? 1 : 1.3)
    const gas = 150 * 12 * years
    
    if (scenario.loan) {
      const loanAmount = scenario.carPrice - scenario.downPayment
      const monthlyRate = (scenario.interestRate / 100) / 12
      const monthlyPayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, scenario.term)) / (Math.pow(1 + monthlyRate, scenario.term) - 1)
      const totalPaid = monthlyPayment * scenario.term + scenario.downPayment
      return totalPaid + insurance + maintenance + gas
    }
    
    return scenario.carPrice + insurance + maintenance + gas
  }

  const comparisonData = scenarios.map(s => ({
    name: s.name,
    cost: calculateTotal(s),
  }))

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Smarter Alternatives
        </h2>
        <p className="text-lg text-gray-600">
          Compare the 5-year total cost
        </p>
      </div>

      {/* Comparison Chart */}
      <Card className="max-w-5xl mx-auto">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={comparisonData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
            <Tooltip formatter={(value) => formatCurrency(Number(value))} />
            <Bar dataKey="cost" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Strategy Cards */}
      <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-6">
        {scenarios.map((scenario, index) => (
          <Card key={index} className={`text-center ${
            index === 0 ? 'bg-red-50' :
            index === 1 ? 'bg-yellow-50' :
            'bg-green-50'
          }`}>
            <div className="text-6xl mb-4">{scenario.icon}</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              {scenario.name}
            </h3>
            <p className="text-sm text-gray-600 mb-4">{scenario.description}</p>
            <div className="text-3xl font-bold text-gray-900 mb-2">
              {formatCurrency(calculateTotal(scenario))}
            </div>
            <div className="text-sm text-gray-600">5-year total cost</div>
            {index === 2 && (
              <div className="mt-3 p-2 bg-green-600 text-white rounded font-semibold">
                💰 Best Value!
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Key Insights */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-purple-50 to-pink-50">
        <h3 className="text-xl font-bold mb-4 text-center">Smart Car Buying Tips</h3>
        <div className="space-y-2">
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Save up and pay cash - avoid interest completely</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Buy a 2-3 year old used car - let someone else take the depreciation hit</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Look for reliable brands (Honda, Toyota) with good resale value</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Budget for total ownership cost, not just monthly payment</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Keep your car longer - drive it for 10+ years to maximize value</span>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <Button onClick={onNext} size="lg">
          Complete Simulation
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 4: Complete
function StepComplete() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center space-y-6 max-w-2xl mx-auto"
    >
      <div className="w-24 h-24 mx-auto bg-gradient-to-br from-red-400 to-pink-500 rounded-full flex items-center justify-center">
        <CheckCircle className="w-12 h-12 text-white" />
      </div>
      
      <h2 className="text-4xl font-bold text-gray-900">
        Simulation Complete! 🎉
      </h2>
      
      <Card className="bg-gradient-to-br from-red-50 to-pink-50">
        <div className="text-center">
          <div className="text-6xl mb-4">⭐</div>
          <div className="text-3xl font-bold text-red-600 mb-2">+150 XP</div>
          <div className="text-gray-600">You've uncovered the true cost of car loans!</div>
        </div>
      </Card>

      <div className="space-y-3">
        <h3 className="font-semibold text-lg">Remember:</h3>
        <div className="text-left space-y-2">
          <div className="flex items-start">
            <span className="mr-2">🚗</span>
            <span>A car loses 60% of its value in the first 5 years</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">💸</span>
            <span>The total cost is 2-3× the sticker price</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">💰</span>
            <span>Save and pay cash to avoid interest</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">🎯</span>
            <span>Buy used - let someone else take the depreciation hit</span>
          </div>
        </div>
      </div>

      <div className="pt-4">
        <Button size="lg" onClick={() => window.location.href = '/dashboard'}>
          Return to Dashboard
        </Button>
      </div>
    </motion.div>
  )
}

// Main Component
export default function CarPaymentPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [carPrice, setCarPrice] = useState(0)
  const [downPayment, setDownPayment] = useState(0)
  const [interestRate, setInterestRate] = useState(0)
  const [term, setTerm] = useState(0)

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-pink-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Progress Bar */}
        <div className="max-w-3xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-2">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
                  currentStep >= step
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {step}
              </div>
            ))}
          </div>
          <div className="h-2 bg-gray-300 rounded-full overflow-hidden">
            <div
              className="h-full bg-red-600 transition-all duration-500"
              style={{ width: `${(currentStep / 4) * 100}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <StepCarChoice
              key="choice"
              onNext={(price, down, rate, months) => {
                setCarPrice(price)
                setDownPayment(down)
                setInterestRate(rate)
                setTerm(months)
                setCurrentStep(2)
              }}
            />
          )}
          {currentStep === 2 && (
            <StepTrueCost
              key="cost"
              carPrice={carPrice}
              downPayment={downPayment}
              interestRate={interestRate}
              term={term}
              onNext={() => setCurrentStep(3)}
            />
          )}
          {currentStep === 3 && (
            <StepAlternatives
              key="alternatives"
              onNext={() => setCurrentStep(4)}
            />
          )}
          {currentStep === 4 && <StepComplete key="complete" />}
        </AnimatePresence>
      </div>
    </div>
  )
}
