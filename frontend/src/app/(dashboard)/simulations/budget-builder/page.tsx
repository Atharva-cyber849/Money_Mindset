'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { PieChart, Wallet, AlertCircle, CheckCircle, TrendingUp, Home, ShoppingBag, Sparkles, ArrowRight } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'

interface BudgetItem {
  category: string
  amount: number
  type: 'needs' | 'wants' | 'savings'
}

// Step 1: Set Income
function StepIncome({ onNext }: { onNext: (income: number) => void }) {
  const [income, setIncome] = useState(4000)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
          <Wallet className="w-12 h-12 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Build Your Perfect Budget
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Follow the proven <span className="font-bold text-purple-600">50/30/20 Rule</span>
          <br />
          <span className="text-sm">50% Needs • 30% Wants • 20% Savings</span>
        </p>
      </div>

      <Card className="max-w-2xl mx-auto">
        <Slider
          min={2000}
          max={15000}
          step={100}
          value={income}
          onChange={setIncome}
          label="Monthly Take-Home Income"
          format={(v) => formatCurrency(v)}
          color="purple"
        />

        <div className="mt-6 grid grid-cols-3 gap-4 text-center">
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Needs (50%)</div>
            <div className="text-2xl font-bold text-blue-600">{formatCurrency(income * 0.5)}</div>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Wants (30%)</div>
            <div className="text-2xl font-bold text-orange-600">{formatCurrency(income * 0.3)}</div>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Savings (20%)</div>
            <div className="text-2xl font-bold text-green-600">{formatCurrency(income * 0.2)}</div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <Button onClick={() => onNext(income)} size="lg">
            Start Building
            <ArrowRight className="w-5 h-5" />
          </Button>
        </div>
      </Card>

      <div className="text-center text-sm text-gray-500">
        💡 The 50/30/20 rule is a simple budget framework created by Elizabeth Warren
      </div>
    </motion.div>
  )
}

// Step 2: Allocate Budget
function StepAllocate({ income, onNext }: { income: number; onNext: (budget: BudgetItem[]) => void }) {
  // Needs (50%)
  const [housing, setHousing] = useState(income * 0.30)
  const [utilities, setUtilities] = useState(income * 0.05)
  const [groceries, setGroceries] = useState(income * 0.08)
  const [transportation, setTransportation] = useState(income * 0.05)
  const [insurance, setInsurance] = useState(income * 0.02)

  // Wants (30%)
  const [dining, setDining] = useState(income * 0.10)
  const [entertainment, setEntertainment] = useState(income * 0.08)
  const [shopping, setShopping] = useState(income * 0.07)
  const [subscriptions, setSubscriptions] = useState(income * 0.05)

  // Savings (20%)
  const [emergency, setEmergency] = useState(income * 0.08)
  const [retirement, setRetirement] = useState(income * 0.10)
  const [goals, setGoals] = useState(income * 0.02)

  const totalNeeds = housing + utilities + groceries + transportation + insurance
  const totalWants = dining + entertainment + shopping + subscriptions
  const totalSavings = emergency + retirement + goals
  const totalAllocated = totalNeeds + totalWants + totalSavings

  const needsPercent = (totalNeeds / income) * 100
  const wantsPercent = (totalWants / income) * 100
  const savingsPercent = (totalSavings / income) * 100

  const isBalanced = Math.abs(totalAllocated - income) < 10
  const needsGood = needsPercent >= 40 && needsPercent <= 60
  const wantsGood = wantsPercent >= 20 && wantsPercent <= 40
  const savingsGood = savingsPercent >= 15 && savingsPercent <= 30

  const handleSubmit = () => {
    const budget: BudgetItem[] = [
      { category: 'Housing', amount: housing, type: 'needs' },
      { category: 'Utilities', amount: utilities, type: 'needs' },
      { category: 'Groceries', amount: groceries, type: 'needs' },
      { category: 'Transportation', amount: transportation, type: 'needs' },
      { category: 'Insurance', amount: insurance, type: 'needs' },
      { category: 'Dining Out', amount: dining, type: 'wants' },
      { category: 'Entertainment', amount: entertainment, type: 'wants' },
      { category: 'Shopping', amount: shopping, type: 'wants' },
      { category: 'Subscriptions', amount: subscriptions, type: 'wants' },
      { category: 'Emergency Fund', amount: emergency, type: 'savings' },
      { category: 'Retirement', amount: retirement, type: 'savings' },
      { category: 'Goals', amount: goals, type: 'savings' },
    ]
    onNext(budget)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Allocate Your {formatCurrency(income)}
        </h2>
        <p className="text-lg text-gray-600">
          Adjust the sliders to build your personalized budget
        </p>
      </div>

      {/* Budget Progress */}
      <Card className="max-w-5xl mx-auto">
        <div className="grid grid-cols-4 gap-4 text-center">
          <div className={`p-3 rounded-lg ${needsGood ? 'bg-blue-50' : 'bg-red-50'}`}>
            <div className="text-sm text-gray-600 mb-1">Needs</div>
            <div className={`text-2xl font-bold ${needsGood ? 'text-blue-600' : 'text-red-600'}`}>
              {needsPercent.toFixed(0)}%
            </div>
            <div className="text-xs text-gray-500">Target: 50%</div>
          </div>
          <div className={`p-3 rounded-lg ${wantsGood ? 'bg-orange-50' : 'bg-red-50'}`}>
            <div className="text-sm text-gray-600 mb-1">Wants</div>
            <div className={`text-2xl font-bold ${wantsGood ? 'text-orange-600' : 'text-red-600'}`}>
              {wantsPercent.toFixed(0)}%
            </div>
            <div className="text-xs text-gray-500">Target: 30%</div>
          </div>
          <div className={`p-3 rounded-lg ${savingsGood ? 'bg-green-50' : 'bg-red-50'}`}>
            <div className="text-sm text-gray-600 mb-1">Savings</div>
            <div className={`text-2xl font-bold ${savingsGood ? 'text-green-600' : 'text-red-600'}`}>
              {savingsPercent.toFixed(0)}%
            </div>
            <div className="text-xs text-gray-500">Target: 20%</div>
          </div>
          <div className={`p-3 rounded-lg ${isBalanced ? 'bg-green-50' : 'bg-yellow-50'}`}>
            <div className="text-sm text-gray-600 mb-1">Balance</div>
            <div className={`text-2xl font-bold ${isBalanced ? 'text-green-600' : 'text-yellow-600'}`}>
              {formatCurrency(income - totalAllocated)}
            </div>
            <div className="text-xs text-gray-500">{isBalanced ? 'Balanced!' : 'Adjust'}</div>
          </div>
        </div>
      </Card>

      <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-6">
        {/* Needs */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Home className="w-5 h-5 mr-2 text-blue-500" />
            Needs (50%)
          </h3>
          <div className="space-y-3">
            <Slider
              min={0}
              max={income * 0.5}
              step={50}
              value={housing}
              onChange={setHousing}
              label="Housing"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
            <Slider
              min={0}
              max={income * 0.2}
              step={25}
              value={utilities}
              onChange={setUtilities}
              label="Utilities"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
            <Slider
              min={0}
              max={income * 0.3}
              step={25}
              value={groceries}
              onChange={setGroceries}
              label="Groceries"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
            <Slider
              min={0}
              max={income * 0.2}
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
              max={income * 0.15}
              step={25}
              value={insurance}
              onChange={setInsurance}
              label="Insurance"
              format={(v) => formatCurrency(v)}
              color="blue"
              showValue={false}
            />
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm font-semibold">
                <span>Total Needs:</span>
                <span className="text-blue-600">{formatCurrency(totalNeeds)}</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Wants */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <ShoppingBag className="w-5 h-5 mr-2 text-orange-500" />
            Wants (30%)
          </h3>
          <div className="space-y-3">
            <Slider
              min={0}
              max={income * 0.3}
              step={25}
              value={dining}
              onChange={setDining}
              label="Dining Out"
              format={(v) => formatCurrency(v)}
              color="orange"
              showValue={false}
            />
            <Slider
              min={0}
              max={income * 0.2}
              step={25}
              value={entertainment}
              onChange={setEntertainment}
              label="Entertainment"
              format={(v) => formatCurrency(v)}
              color="orange"
              showValue={false}
            />
            <Slider
              min={0}
              max={income * 0.2}
              step={25}
              value={shopping}
              onChange={setShopping}
              label="Shopping"
              format={(v) => formatCurrency(v)}
              color="orange"
              showValue={false}
            />
            <Slider
              min={0}
              max={income * 0.15}
              step={10}
              value={subscriptions}
              onChange={setSubscriptions}
              label="Subscriptions"
              format={(v) => formatCurrency(v)}
              color="orange"
              showValue={false}
            />
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm font-semibold">
                <span>Total Wants:</span>
                <span className="text-orange-600">{formatCurrency(totalWants)}</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Savings */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-500" />
            Savings (20%)
          </h3>
          <div className="space-y-3">
            <Slider
              min={0}
              max={income * 0.3}
              step={25}
              value={emergency}
              onChange={setEmergency}
              label="Emergency Fund"
              format={(v) => formatCurrency(v)}
              color="green"
              showValue={false}
            />
            <Slider
              min={0}
              max={income * 0.3}
              step={25}
              value={retirement}
              onChange={setRetirement}
              label="Retirement"
              format={(v) => formatCurrency(v)}
              color="green"
              showValue={false}
            />
            <Slider
              min={0}
              max={income * 0.2}
              step={25}
              value={goals}
              onChange={setGoals}
              label="Goals/Debt"
              format={(v) => formatCurrency(v)}
              color="green"
              showValue={false}
            />
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm font-semibold">
                <span>Total Savings:</span>
                <span className="text-green-600">{formatCurrency(totalSavings)}</span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <div className="text-center">
        <Button onClick={handleSubmit} size="lg" disabled={!isBalanced}>
          {isBalanced ? 'Review Budget' : 'Balance Your Budget First'}
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 3: Visualization & Analysis
function StepVisualize({ income, budget, onNext }: { income: number; budget: BudgetItem[]; onNext: () => void }) {
  const needs = budget.filter(item => item.type === 'needs')
  const wants = budget.filter(item => item.type === 'wants')
  const savings = budget.filter(item => item.type === 'savings')

  const totalNeeds = needs.reduce((sum, item) => sum + item.amount, 0)
  const totalWants = wants.reduce((sum, item) => sum + item.amount, 0)
  const totalSavings = savings.reduce((sum, item) => sum + item.amount, 0)

  const needsPercent = (totalNeeds / income) * 100
  const wantsPercent = (totalWants / income) * 100
  const savingsPercent = (totalSavings / income) * 100

  // Calculate score
  const needsScore = Math.max(0, 100 - Math.abs(needsPercent - 50) * 2)
  const wantsScore = Math.max(0, 100 - Math.abs(wantsPercent - 30) * 3)
  const savingsScore = Math.max(0, 100 - Math.abs(savingsPercent - 20) * 4)
  const overallScore = Math.round((needsScore + wantsScore + savingsScore) / 3)

  // Pie chart data
  const pieData = [
    { name: 'Needs', value: totalNeeds, color: '#3b82f6', percent: needsPercent },
    { name: 'Wants', value: totalWants, color: '#f97316', percent: wantsPercent },
    { name: 'Savings', value: totalSavings, color: '#10b981', percent: savingsPercent },
  ]

  // Bar chart data
  const barData = budget.map(item => ({
    name: item.category,
    amount: item.amount,
    type: item.type,
  }))

  // Future projection
  const monthsInYear = 12
  const annualSavings = totalSavings * monthsInYear
  const fiveYearSavings = annualSavings * 5 * 1.08 // With 8% return

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Your Budget Analysis
        </h2>
      </div>

      {/* Score Card */}
      <Card className={`max-w-4xl mx-auto text-center ${
        overallScore >= 80 ? 'bg-green-50 border-green-200' :
        overallScore >= 60 ? 'bg-yellow-50 border-yellow-200' :
        'bg-red-50 border-red-200'
      } border-2`}>
        <div className="text-6xl mb-4">
          {overallScore >= 80 ? '🎉' : overallScore >= 60 ? '👍' : '⚠️'}
        </div>
        <div className="text-4xl font-bold mb-2">
          {overallScore >= 80 ? 'Excellent Budget!' : overallScore >= 60 ? 'Good Start!' : 'Needs Work'}
        </div>
        <div className="text-2xl text-gray-700 mb-4">
          Score: <span className="font-bold">{overallScore}/100</span>
        </div>
        <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
          <div>
            <div className="text-sm text-gray-600">Needs</div>
            <div className="text-xl font-bold text-blue-600">{needsPercent.toFixed(1)}%</div>
            <div className="text-xs text-gray-500">(Target: 50%)</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Wants</div>
            <div className="text-xl font-bold text-orange-600">{wantsPercent.toFixed(1)}%</div>
            <div className="text-xs text-gray-500">(Target: 30%)</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Savings</div>
            <div className="text-xl font-bold text-green-600">{savingsPercent.toFixed(1)}%</div>
            <div className="text-xs text-gray-500">(Target: 20%)</div>
          </div>
        </div>
      </Card>

      {/* Visualizations */}
      <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 text-center">Budget Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RechartsPie>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${percent.toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
            </RechartsPie>
          </ResponsiveContainer>
        </Card>

        {/* Bar Chart */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 text-center">Category Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} fontSize={12} />
              <YAxis tickFormatter={(value) => `$${value}`} />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              <Bar dataKey="amount" fill="#8884d8">
                {barData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={
                    entry.type === 'needs' ? '#3b82f6' :
                    entry.type === 'wants' ? '#f97316' :
                    '#10b981'
                  } />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Future Projection */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-green-50 to-emerald-50">
        <div className="text-center">
          <Sparkles className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            Your Savings Potential
          </h3>
          <div className="grid md:grid-cols-3 gap-4 mt-4">
            <div>
              <div className="text-sm text-gray-600 mb-1">Monthly Savings</div>
              <div className="text-2xl font-bold text-green-600">{formatCurrency(totalSavings)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Annual Savings</div>
              <div className="text-2xl font-bold text-green-600">{formatCurrency(annualSavings)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">5-Year Growth (8%)</div>
              <div className="text-3xl font-bold text-green-600">{formatCurrency(fiveYearSavings)}</div>
            </div>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <Button onClick={onNext} size="lg">
          Complete Budget
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
      <div className="w-24 h-24 mx-auto bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center">
        <CheckCircle className="w-12 h-12 text-white" />
      </div>
      
      <h2 className="text-4xl font-bold text-gray-900">
        Budget Created! 🎉
      </h2>
      
      <Card className="bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="text-center">
          <div className="text-6xl mb-4">⭐</div>
          <div className="text-3xl font-bold text-purple-600 mb-2">+150 XP</div>
          <div className="text-gray-600">You've mastered the 50/30/20 rule!</div>
        </div>
      </Card>

      <div className="space-y-3">
        <h3 className="font-semibold text-lg">Next Steps:</h3>
        <div className="text-left space-y-2">
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Track your spending for 30 days to validate your budget</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Set up automatic transfers to savings accounts</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Review and adjust quarterly as income/expenses change</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">✅</span>
            <span>Use budgeting apps to stay on track</span>
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
export default function BudgetBuilderPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [income, setIncome] = useState(0)
  const [budget, setBudget] = useState<BudgetItem[]>([])

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Progress Bar */}
        <div className="max-w-3xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-2">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className={`flex items-center justify-center w-10 h-10 rounded-full font-bold ${
                  currentStep >= step
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {step}
              </div>
            ))}
          </div>
          <div className="h-2 bg-gray-300 rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-600 transition-all duration-500"
              style={{ width: `${(currentStep / 4) * 100}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <StepIncome
              key="income"
              onNext={(inc) => {
                setIncome(inc)
                setCurrentStep(2)
              }}
            />
          )}
          {currentStep === 2 && (
            <StepAllocate
              key="allocate"
              income={income}
              onNext={(bgt) => {
                setBudget(bgt)
                setCurrentStep(3)
              }}
            />
          )}
          {currentStep === 3 && (
            <StepVisualize
              key="visualize"
              income={income}
              budget={budget}
              onNext={() => setCurrentStep(4)}
            />
          )}
          {currentStep === 4 && <StepComplete key="complete" />}
        </AnimatePresence>
      </div>
    </div>
  )
}
