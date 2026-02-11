'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CreditCard, AlertTriangle, TrendingUp, DollarSign, Zap, ArrowRight, CheckCircle } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts'

// Step 1: Setup Debt
function StepDebtSetup({ onNext }: { onNext: (balance: number, apr: number) => void }) {
  const [balance, setBalance] = useState(5000)
  const [apr, setApr] = useState(22)

  const monthlyRate = apr / 100 / 12
  const minimumPayment = Math.max(25, balance * 0.02) // 2% of balance or $25
  const monthsToPayoff = Math.log(minimumPayment / (minimumPayment - balance * monthlyRate)) / Math.log(1 + monthlyRate)
  const totalPaid = minimumPayment * monthsToPayoff
  const totalInterest = totalPaid - balance

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-orange-400 to-red-500 rounded-full flex items-center justify-center">
          <CreditCard className="w-12 h-12 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The Credit Card Trap
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Discover why paying only the minimum keeps you in debt forever.
          <br />
          <span className="font-semibold text-gray-900">Let's see the math...</span>
        </p>
      </div>

      <Card className="max-w-4xl mx-auto">
        <div className="space-y-6">
          <Slider
            min={1000}
            max={15000}
            step={500}
            value={balance}
            onChange={setBalance}
            label="Credit Card Balance"
            format={(v) => formatCurrency(v)}
            color="red"
          />
          <Slider
            min={15}
            max={30}
            step={0.5}
            value={apr}
            onChange={setApr}
            label="Annual Interest Rate (APR)"
            format={(v) => `${v.toFixed(1)}%`}
            color="orange"
          />
        </div>

        <div className="mt-6 p-4 bg-gradient-to-br from-red-50 to-orange-50 rounded-lg border-2 border-red-200">
          <h3 className="font-semibold text-center mb-4 text-gray-900">
            If You Pay Only the Minimum ({formatCurrency(minimumPayment)}/month)...
          </h3>
          <div className="grid md:grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-sm text-gray-600 mb-1">Time to Pay Off</div>
              <div className="text-2xl font-bold text-red-600">
                {(monthsToPayoff / 12).toFixed(1)} years
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Total Paid</div>
              <div className="text-2xl font-bold text-red-600">
                {formatCurrency(totalPaid)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Just Interest</div>
              <div className="text-2xl font-bold text-red-600">
                {formatCurrency(totalInterest)}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <Button onClick={() => onNext(balance, apr)} size="lg">
            Compare Payment Strategies
            <ArrowRight className="w-5 h-5" />
          </Button>
        </div>
      </Card>

      <div className="text-center text-sm text-gray-500">
        💡 Average credit card APR in 2024: 22.8%
      </div>
    </motion.div>
  )
}

// Step 2: Compare Strategies
function StepCompare({ balance, apr, onNext }: { balance: number; apr: number; onNext: () => void }) {
  const monthlyRate = apr / 100 / 12
  
  const strategies = [
    {
      name: 'Minimum Only',
      monthlyPayment: Math.max(25, balance * 0.02),
      color: '#ef4444',
      emoji: '😰',
    },
    {
      name: 'Fixed $100',
      monthlyPayment: 100,
      color: '#f59e0b',
      emoji: '😐',
    },
    {
      name: 'Fixed $200',
      monthlyPayment: 200,
      color: '#10b981',
      emoji: '😊',
    },
    {
      name: 'Aggressive $400',
      monthlyPayment: 400,
      color: '#3b82f6',
      emoji: '🚀',
    },
  ]

  const calculatePayoff = (monthlyPayment: number) => {
    let remainingBalance = balance
    let totalPaid = 0
    let months = 0
    
    while (remainingBalance > 0 && months < 600) { // Cap at 50 years
      const interestCharge = remainingBalance * monthlyRate
      const principalPayment = Math.min(monthlyPayment - interestCharge, remainingBalance)
      
      if (principalPayment <= 0) {
        return { months: 600, totalPaid: Infinity, totalInterest: Infinity }
      }
      
      remainingBalance -= principalPayment
      totalPaid += monthlyPayment
      months++
    }
    
    return {
      months,
      totalPaid,
      totalInterest: totalPaid - balance,
    }
  }

  const results = strategies.map(strategy => {
    const result = calculatePayoff(strategy.monthlyPayment)
    return {
      ...strategy,
      ...result,
    }
  })

  // Data for chart
  const chartData = results.map(r => ({
    name: r.name,
    months: r.months,
    interest: r.totalInterest,
  }))

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Payment Strategy Comparison
        </h2>
        <p className="text-lg text-gray-600">
          Paying more each month makes a HUGE difference!
        </p>
      </div>

      {/* Strategy Cards */}
      <div className="max-w-6xl mx-auto grid md:grid-cols-4 gap-4">
        {results.map((result, index) => (
          <Card
            key={index}
            className={`text-center ${
              index === 0 ? 'bg-red-50' :
              index === 1 ? 'bg-yellow-50' :
              index === 2 ? 'bg-green-50' :
              'bg-blue-50'
            }`}
          >
            <div className="text-5xl mb-3">{result.emoji}</div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              {result.name}
            </h3>
            <div className="space-y-2">
              <div>
                <div className="text-sm text-gray-600">Monthly Payment</div>
                <div className="text-xl font-bold" style={{ color: result.color }}>
                  {formatCurrency(result.monthlyPayment)}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Time to Pay Off</div>
                <div className="text-lg font-semibold text-gray-900">
                  {result.months > 500 ? '50+ years' : `${(result.months / 12).toFixed(1)} years`}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Total Interest</div>
                <div className="text-lg font-semibold text-red-600">
                  {result.totalInterest === Infinity ? '∞' : formatCurrency(result.totalInterest)}
                </div>
              </div>
            </div>
            {index === 3 && (
              <div className="mt-3 p-2 bg-blue-600 text-white rounded font-semibold">
                💪 Best Strategy!
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Comparison Charts */}
      <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Time Comparison */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 text-center">Months to Pay Off</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-15} textAnchor="end" height={80} />
              <YAxis label={{ value: 'Months', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="months" fill="#8884d8">
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={results[index].color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Interest Comparison */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 text-center">Total Interest Paid</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-15} textAnchor="end" height={80} />
              <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`} />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              <Bar dataKey="interest" fill="#8884d8">
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={results[index].color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Key Insight */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
        <div className="text-center">
          <Zap className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            The Difference is Staggering!
          </h3>
          <div className="grid md:grid-cols-2 gap-4 mt-4">
            <div>
              <div className="text-sm text-gray-600 mb-1">Minimum Payment</div>
              <div className="text-2xl font-bold text-red-600">
                {results[0].months > 500 ? '50+ years' : `${(results[0].months / 12).toFixed(1)} years`}
              </div>
              <div className="text-sm text-red-600">{formatCurrency(results[0].totalInterest)} interest</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Aggressive Payment</div>
              <div className="text-2xl font-bold text-green-600">
                {(results[3].months / 12).toFixed(1)} years
              </div>
              <div className="text-sm text-green-600">{formatCurrency(results[3].totalInterest)} interest</div>
            </div>
          </div>
          <p className="mt-4 text-gray-700">
            You save <span className="font-bold text-green-600">{formatCurrency(results[0].totalInterest - results[3].totalInterest)}</span> by paying more aggressively!
          </p>
        </div>
      </Card>

      <div className="text-center">
        <Button onClick={onNext} size="lg">
          See Debt Payoff Strategies
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 3: Strategies
function StepStrategies({ onNext }: { onNext: () => void }) {
  const strategies = [
    {
      name: 'Debt Snowball',
      icon: '❄️',
      description: 'Pay off smallest debts first',
      pros: ['Quick wins boost motivation', 'Simple to track', 'Psychological momentum'],
      cons: ['May pay more interest', 'Not mathematically optimal'],
      bestFor: 'People who need motivation and quick wins',
    },
    {
      name: 'Debt Avalanche',
      icon: '🏔️',
      description: 'Pay off highest interest rate first',
      pros: ['Saves the most money', 'Mathematically optimal', 'Fastest payoff'],
      cons: ['Takes longer for first win', 'Requires discipline'],
      bestFor: 'People who are disciplined and want to save most',
    },
    {
      name: 'Balance Transfer',
      icon: '🔄',
      description: '0% APR for 12-18 months',
      pros: ['No interest for intro period', 'Time to pay down principal', 'Can save thousands'],
      cons: ['Transfer fee (3-5%)', 'Must pay off before promo ends', 'Need good credit'],
      bestFor: 'People with good credit and discipline',
    },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Debt Payoff Strategies
        </h2>
        <p className="text-lg text-gray-600">
          Choose the right strategy for your situation
        </p>
      </div>

      <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-6">
        {strategies.map((strategy, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <div className="text-center">
              <div className="text-6xl mb-4">{strategy.icon}</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {strategy.name}
              </h3>
              <p className="text-gray-600 mb-4">{strategy.description}</p>
              
              <div className="text-left space-y-3">
                <div>
                  <div className="font-semibold text-green-700 mb-2">✅ Pros:</div>
                  <ul className="space-y-1 text-sm text-gray-700">
                    {strategy.pros.map((pro, i) => (
                      <li key={i}>• {pro}</li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <div className="font-semibold text-red-700 mb-2">❌ Cons:</div>
                  <ul className="space-y-1 text-sm text-gray-700">
                    {strategy.cons.map((con, i) => (
                      <li key={i}>• {con}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="pt-2 border-t">
                  <div className="font-semibold text-blue-700 mb-1">Best For:</div>
                  <p className="text-sm text-gray-700">{strategy.bestFor}</p>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Action Steps */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-purple-50 to-pink-50">
        <h3 className="text-xl font-bold mb-4 text-center">Your Action Plan</h3>
        <div className="space-y-3">
          <div className="flex items-start">
            <span className="mr-2 text-lg">1️⃣</span>
            <div>
              <span className="font-semibold">Stop using your credit cards</span>
              <p className="text-sm text-gray-600">Can't dig out of a hole while still digging</p>
            </div>
          </div>
          <div className="flex items-start">
            <span className="mr-2 text-lg">2️⃣</span>
            <div>
              <span className="font-semibold">List all your debts</span>
              <p className="text-sm text-gray-600">Balance, interest rate, minimum payment</p>
            </div>
          </div>
          <div className="flex items-start">
            <span className="mr-2 text-lg">3️⃣</span>
            <div>
              <span className="font-semibold">Choose your strategy</span>
              <p className="text-sm text-gray-600">Snowball for motivation, Avalanche to save money</p>
            </div>
          </div>
          <div className="flex items-start">
            <span className="mr-2 text-lg">4️⃣</span>
            <div>
              <span className="font-semibold">Pay more than the minimum</span>
              <p className="text-sm text-gray-600">Even $50 extra per month makes a huge difference</p>
            </div>
          </div>
          <div className="flex items-start">
            <span className="mr-2 text-lg">5️⃣</span>
            <div>
              <span className="font-semibold">Automate your payments</span>
              <p className="text-sm text-gray-600">Set it and forget it - consistency is key</p>
            </div>
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
      <div className="w-24 h-24 mx-auto bg-gradient-to-br from-orange-400 to-red-500 rounded-full flex items-center justify-center">
        <CheckCircle className="w-12 h-12 text-white" />
      </div>
      
      <h2 className="text-4xl font-bold text-gray-900">
        Simulation Complete! 🎉
      </h2>
      
      <Card className="bg-gradient-to-br from-orange-50 to-red-50">
        <div className="text-center">
          <div className="text-6xl mb-4">⭐</div>
          <div className="text-3xl font-bold text-orange-600 mb-2">+150 XP</div>
          <div className="text-gray-600">You've escaped the credit card trap!</div>
        </div>
      </Card>

      <div className="space-y-3">
        <h3 className="font-semibold text-lg">Key Takeaways:</h3>
        <div className="text-left space-y-2">
          <div className="flex items-start">
            <span className="mr-2">💳</span>
            <span>Minimum payments keep you in debt for decades</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">💰</span>
            <span>Small increases in payment = huge savings in interest</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">🎯</span>
            <span>Choose Snowball (motivation) or Avalanche (savings)</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">🚫</span>
            <span>Stop using cards while paying them off</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">⚡</span>
            <span>Automate payments to stay consistent</span>
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
export default function CreditCardPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [balance, setBalance] = useState(0)
  const [apr, setApr] = useState(0)

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Progress Bar */}
        <div className="max-w-3xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-2">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
                  currentStep >= step
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {step}
              </div>
            ))}
          </div>
          <div className="h-2 bg-gray-300 rounded-full overflow-hidden">
            <div
              className="h-full bg-orange-600 transition-all duration-500"
              style={{ width: `${(currentStep / 4) * 100}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <StepDebtSetup
              key="setup"
              onNext={(bal, rate) => {
                setBalance(bal)
                setApr(rate)
                setCurrentStep(2)
              }}
            />
          )}
          {currentStep === 2 && (
            <StepCompare
              key="compare"
              balance={balance}
              apr={apr}
              onNext={() => setCurrentStep(3)}
            />
          )}
          {currentStep === 3 && (
            <StepStrategies
              key="strategies"
              onNext={() => setCurrentStep(4)}
            />
          )}
          {currentStep === 4 && <StepComplete key="complete" />}
        </AnimatePresence>
      </div>
    </div>
  )
}
