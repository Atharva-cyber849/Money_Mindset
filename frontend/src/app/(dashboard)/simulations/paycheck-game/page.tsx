'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Wallet, TrendingUp, AlertTriangle, CheckCircle, DollarSign, ArrowRight, Zap, ShoppingBag, Home, CreditCard } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts'

type Strategy = 'spend_first' | 'bills_first' | 'save_first'

interface StrategyResult {
  strategy: Strategy
  amount_saved: number
  bills_paid_on_time: boolean
  discretionary_spent: number
  late_fees: number
  stress_level: 'low' | 'medium' | 'high'
  final_balance: number
  description: string
}

// Step 1: Setup Your Finances
function StepSetup({ onNext }: { onNext: (income: number, expenses: number) => void }) {
  const [income, setIncome] = useState(4000)
  const [rent, setRent] = useState(1200)
  const [utilities, setUtilities] = useState(200)
  const [groceries, setGroceries] = useState(400)
  const [insurance, setInsurance] = useState(300)
  const [transportation, setTransportation] = useState(200)
  const [debt, setDebt] = useState(300)

  const totalExpenses = rent + utilities + groceries + insurance + transportation + debt
  const remaining = income - totalExpenses

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center">
          <Wallet className="w-12 h-12 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The Paycheck Game
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          When your paycheck arrives, the order you pay things matters.
          <br />
          <span className="font-semibold text-gray-900">Let's set up your monthly finances</span>
        </p>
      </div>

      <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Income */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <DollarSign className="w-5 h-5 mr-2 text-green-500" />
            Monthly Income
          </h3>
          <Slider
            min={2000}
            max={10000}
            step={100}
            value={income}
            onChange={setIncome}
            label="Gross Income"
            format={(v) => formatCurrency(v)}
            color="green"
          />
        </Card>

        {/* Fixed Expenses */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Home className="w-5 h-5 mr-2 text-blue-500" />
            Fixed Expenses
          </h3>
          <div className="space-y-3">
            <Slider
              min={500}
              max={3000}
              step={50}
              value={rent}
              onChange={setRent}
              label="Rent/Mortgage"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
            <Slider
              min={50}
              max={500}
              step={10}
              value={utilities}
              onChange={setUtilities}
              label="Utilities"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
            <Slider
              min={200}
              max={800}
              step={25}
              value={groceries}
              onChange={setGroceries}
              label="Groceries"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
            <Slider
              min={100}
              max={600}
              step={25}
              value={insurance}
              onChange={setInsurance}
              label="Insurance"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
            <Slider
              min={100}
              max={500}
              step={25}
              value={transportation}
              onChange={setTransportation}
              label="Transportation"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
            <Slider
              min={0}
              max={1000}
              step={25}
              value={debt}
              onChange={setDebt}
              label="Debt Payments"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
          </div>
        </Card>
      </div>

      {/* Summary */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-sm text-gray-600 mb-1">Monthly Income</div>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(income)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600 mb-1">Fixed Expenses</div>
            <div className="text-2xl font-bold text-blue-600">{formatCurrency(totalExpenses)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600 mb-1">Remaining</div>
            <div className={`text-2xl font-bold ${remaining > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(remaining)}
            </div>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <Button 
          onClick={() => onNext(income, totalExpenses)} 
          size="lg"
          disabled={remaining <= 0}
        >
          Choose Your Strategy
          <ArrowRight className="w-5 h-5" />
        </Button>
        {remaining <= 0 && (
          <p className="mt-2 text-sm text-red-600">⚠️ Your expenses exceed your income. Adjust the sliders!</p>
        )}
      </div>
    </motion.div>
  )
}

// Step 2: Pick Your Strategy
function StepStrategy({ income, expenses, onNext }: { income: number; expenses: number; onNext: (strategy: Strategy) => void }) {
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null)

  const strategies = [
    {
      id: 'spend_first' as Strategy,
      name: 'Spend First',
      icon: ShoppingBag,
      color: 'red',
      description: 'Have fun first, pay bills later',
      behavior: 'Treat yourself, then handle responsibilities',
      risk: 'High risk of overspending',
    },
    {
      id: 'bills_first' as Strategy,
      name: 'Bills First',
      icon: Home,
      color: 'yellow',
      description: 'Pay bills, then enjoy what\'s left',
      behavior: 'Responsible but reactive',
      risk: 'Medium risk - might not save',
    },
    {
      id: 'save_first' as Strategy,
      name: 'Save First',
      icon: Zap,
      color: 'green',
      description: 'Automate savings, then live on the rest',
      behavior: 'Pay yourself first, build wealth',
      risk: 'Low risk - guaranteed savings',
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
          Choose Your Payment Strategy
        </h2>
        <p className="text-lg text-gray-600">
          How will you allocate your {formatCurrency(income)} paycheck?
        </p>
      </div>

      <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-6">
        {strategies.map((strategy) => {
          const Icon = strategy.icon
          const isSelected = selectedStrategy === strategy.id
          const colorClasses = {
            red: 'from-red-400 to-pink-500',
            yellow: 'from-yellow-400 to-orange-500',
            green: 'from-green-400 to-emerald-500',
          }

          return (
            <motion.div
              key={strategy.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Card
                className={`cursor-pointer transition-all ${
                  isSelected
                    ? 'ring-4 ring-blue-500 shadow-xl'
                    : 'hover:shadow-lg'
                }`}
                onClick={() => setSelectedStrategy(strategy.id)}
              >
                <div className="text-center">
                  <div className={`w-20 h-20 mx-auto mb-4 bg-gradient-to-br ${colorClasses[strategy.color]} rounded-full flex items-center justify-center`}>
                    <Icon className="w-10 h-10 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {strategy.name}
                  </h3>
                  <p className="text-gray-600 mb-4">{strategy.description}</p>
                  <div className="text-sm text-gray-500 space-y-2">
                    <div className="flex items-start">
                      <span className="mr-2">💡</span>
                      <span>{strategy.behavior}</span>
                    </div>
                    <div className="flex items-start">
                      <span className="mr-2">⚠️</span>
                      <span>{strategy.risk}</span>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          )
        })}
      </div>

      <div className="text-center">
        <Button
          onClick={() => selectedStrategy && onNext(selectedStrategy)}
          size="lg"
          disabled={!selectedStrategy}
        >
          See What Happens
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 3: Results & Comparison
function StepResults({ income, expenses, strategy, onNext }: { 
  income: number
  expenses: number
  strategy: Strategy
  onNext: () => void 
}) {
  // Simulate results for all three strategies
  const simulateStrategy = (strat: Strategy): StrategyResult => {
    const remaining = income - expenses
    const savingsTarget = income * 0.10

    if (strat === 'spend_first') {
      // Overspend on discretionary, miss bills
      const discretionary = remaining * 1.3 // Overspend
      const saved = 0
      const lateFees = 70 // 2 bills late
      return {
        strategy: strat,
        amount_saved: saved,
        bills_paid_on_time: false,
        discretionary_spent: discretionary,
        late_fees: lateFees,
        stress_level: 'high',
        final_balance: income - expenses - discretionary - lateFees,
        description: 'You overspent on fun stuff and couldn\'t pay all your bills on time'
      }
    } else if (strat === 'bills_first') {
      // Pay bills, spend rest, save nothing
      const discretionary = remaining * 0.95
      const saved = remaining * 0.05
      return {
        strategy: strat,
        amount_saved: saved,
        bills_paid_on_time: true,
        discretionary_spent: discretionary,
        late_fees: 0,
        stress_level: 'medium',
        final_balance: income - expenses - discretionary,
        description: 'Bills paid, but you barely saved anything for emergencies'
      }
    } else {
      // Save first, then handle rest
      const saved = savingsTarget
      const discretionary = remaining - saved
      return {
        strategy: strat,
        amount_saved: saved,
        bills_paid_on_time: true,
        discretionary_spent: discretionary,
        late_fees: 0,
        stress_level: 'low',
        final_balance: income - expenses - discretionary,
        description: 'You automated savings and still had money for fun!'
      }
    }
  }

  const results = {
    spend_first: simulateStrategy('spend_first'),
    bills_first: simulateStrategy('bills_first'),
    save_first: simulateStrategy('save_first'),
  }

  const yourResult = results[strategy]

  // Comparison data for chart
  const comparisonData = [
    { name: 'Spend First', saved: results.spend_first.amount_saved, fees: results.spend_first.late_fees },
    { name: 'Bills First', saved: results.bills_first.amount_saved, fees: results.bills_first.late_fees },
    { name: 'Save First', saved: results.save_first.amount_saved, fees: results.save_first.late_fees },
  ]

  // Breakdown pie chart data
  const breakdownData = [
    { name: 'Fixed Expenses', value: expenses, color: '#3b82f6' },
    { name: 'Discretionary', value: yourResult.discretionary_spent, color: '#f59e0b' },
    { name: 'Saved', value: yourResult.amount_saved, color: '#10b981' },
    { name: 'Late Fees', value: yourResult.late_fees, color: '#ef4444' },
  ].filter(item => item.value > 0)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Your Results: {strategy.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
        </h2>
      </div>

      {/* Your Result Card */}
      <Card className={`max-w-4xl mx-auto ${
        yourResult.stress_level === 'low' ? 'bg-green-50 border-green-200' :
        yourResult.stress_level === 'medium' ? 'bg-yellow-50 border-yellow-200' :
        'bg-red-50 border-red-200'
      } border-2`}>
        <div className="grid md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-sm text-gray-600 mb-1">Amount Saved</div>
            <div className={`text-2xl font-bold ${yourResult.amount_saved > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(yourResult.amount_saved)}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 mb-1">Bills Status</div>
            <div className="flex items-center justify-center">
              {yourResult.bills_paid_on_time ? (
                <CheckCircle className="w-8 h-8 text-green-500" />
              ) : (
                <AlertTriangle className="w-8 h-8 text-red-500" />
              )}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 mb-1">Late Fees</div>
            <div className={`text-2xl font-bold ${yourResult.late_fees > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {yourResult.late_fees > 0 ? `-${formatCurrency(yourResult.late_fees)}` : formatCurrency(0)}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 mb-1">Stress Level</div>
            <div className={`text-lg font-bold ${
              yourResult.stress_level === 'low' ? 'text-green-600' :
              yourResult.stress_level === 'medium' ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {yourResult.stress_level.toUpperCase()}
            </div>
          </div>
        </div>
        <div className="mt-4 text-center text-gray-700 font-medium">
          {yourResult.description}
        </div>
      </Card>

      {/* Money Breakdown Pie Chart */}
      <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold mb-4 text-center">Your Money Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={breakdownData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {breakdownData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        {/* Compare All Strategies */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 text-center">Strategy Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-15} textAnchor="end" height={80} />
              <YAxis tickFormatter={(value) => formatCurrency(value)} />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              <Bar dataKey="saved" fill="#10b981" name="Saved" />
              <Bar dataKey="fees" fill="#ef4444" name="Late Fees" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* All Strategies Comparison */}
      <Card className="max-w-4xl mx-auto">
        <h3 className="text-xl font-bold mb-4 text-center">Complete Strategy Comparison</h3>
        <div className="grid md:grid-cols-3 gap-4">
          {(['spend_first', 'bills_first', 'save_first'] as Strategy[]).map((strat) => {
            const result = results[strat]
            const isYourChoice = strat === strategy
            return (
              <div
                key={strat}
                className={`p-4 rounded-lg ${
                  isYourChoice ? 'bg-blue-50 ring-2 ring-blue-500' : 'bg-gray-50'
                }`}
              >
                <div className="font-semibold mb-2">
                  {strat.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                  {isYourChoice && ' (You)'}
                </div>
                <div className="space-y-2 text-sm">
                  <div>💰 Saved: <span className="font-bold">{formatCurrency(result.amount_saved)}</span></div>
                  <div>📋 Bills: {result.bills_paid_on_time ? '✅ On time' : '❌ Late'}</div>
                  <div>💸 Fees: <span className="font-bold text-red-600">{formatCurrency(result.late_fees)}</span></div>
                  <div>😰 Stress: <span className="font-bold">{result.stress_level}</span></div>
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Key Insight */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
        <div className="text-center">
          <Zap className="w-12 h-12 text-purple-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            The "Pay Yourself First" Principle
          </h3>
          <p className="text-gray-700 text-lg">
            Automate your savings BEFORE you see your paycheck. What you don't see, you don't spend.
          </p>
          <div className="mt-4 p-4 bg-white rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Over 1 year:</div>
            <div className="text-3xl font-bold text-green-600">
              {formatCurrency(results.save_first.amount_saved * 12)}
            </div>
            <div className="text-sm text-gray-600 mt-1">saved automatically with "Save First"</div>
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

// Step 4: Completion
function StepComplete() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center space-y-6 max-w-2xl mx-auto"
    >
      <div className="w-24 h-24 mx-auto bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center">
        <CheckCircle className="w-12 h-12 text-white" />
      </div>
      
      <h2 className="text-4xl font-bold text-gray-900">
        Simulation Complete! 🎉
      </h2>
      
      <Card className="bg-gradient-to-br from-green-50 to-emerald-50">
        <div className="text-center">
          <div className="text-6xl mb-4">⭐</div>
          <div className="text-3xl font-bold text-green-600 mb-2">+200 XP</div>
          <div className="text-gray-600">You've mastered the Paycheck Game!</div>
        </div>
      </Card>

      <div className="space-y-3">
        <h3 className="font-semibold text-lg">Key Takeaways:</h3>
        <div className="text-left space-y-2">
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Automate savings first - pay yourself before anyone else</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Set up automatic transfers on payday</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Avoid late fees by paying bills on time</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Live on what's left after saving</span>
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
export default function PaycheckGamePage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [income, setIncome] = useState(0)
  const [expenses, setExpenses] = useState(0)
  const [strategy, setStrategy] = useState<Strategy>('save_first')

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Progress Bar */}
        <div className="max-w-3xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-2">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
                  currentStep >= step
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {step}
              </div>
            ))}
          </div>
          <div className="h-2 bg-gray-300 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all duration-500"
              style={{ width: `${(currentStep / 4) * 100}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <StepSetup
              key="setup"
              onNext={(inc, exp) => {
                setIncome(inc)
                setExpenses(exp)
                setCurrentStep(2)
              }}
            />
          )}
          {currentStep === 2 && (
            <StepStrategy
              key="strategy"
              income={income}
              expenses={expenses}
              onNext={(strat) => {
                setStrategy(strat)
                setCurrentStep(3)
              }}
            />
          )}
          {currentStep === 3 && (
            <StepResults
              key="results"
              income={income}
              expenses={expenses}
              strategy={strategy}
              onNext={() => setCurrentStep(4)}
            />
          )}
          {currentStep === 4 && <StepComplete key="complete" />}
        </AnimatePresence>
      </div>
    </div>
  )
}
