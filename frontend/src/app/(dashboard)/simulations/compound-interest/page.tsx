'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Zap, TrendingUp, Clock, DollarSign, ArrowRight, Users, AlertCircle } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency, formatNumber } from '@/lib/utils'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area, AreaChart } from 'recharts'

// Character profiles
interface Character {
  name: string
  age: number
  startAge: number
  endAge: number
  monthlyInvestment: number
  totalInvested: number
  finalValue: number
  color: string
  emoji: string
  strategy: string
}

// Step 1: Meet the Characters
function StepIntro({ onNext }: { onNext: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
          <Zap className="w-12 h-12 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The Compound Interest Time Machine ⏰
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Meet three friends who made different investing decisions. 
          Their stories will show you the incredible power of starting early.
        </p>
      </div>

      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-300">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-orange-500 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            The Question
          </h3>
          <p className="text-lg text-gray-700">
            Who will end up with the most money at age 65?
          </p>
        </div>
      </Card>

      {/* Character Preview Cards */}
      <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-6">
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50">
          <div className="text-center">
            <div className="text-6xl mb-3">👩‍💼</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Early Bird Emma</h3>
            <div className="space-y-1 text-sm text-gray-700">
              <p><strong>Starts:</strong> Age 25</p>
              <p><strong>Invests:</strong> $300/month</p>
              <p><strong>Stops:</strong> Age 35</p>
              <p className="text-green-600 font-semibold">10 years total</p>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-cyan-50">
          <div className="text-center">
            <div className="text-6xl mb-3">👨‍💻</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Steady Steven</h3>
            <div className="space-y-1 text-sm text-gray-700">
              <p><strong>Starts:</strong> Age 35</p>
              <p><strong>Invests:</strong> $300/month</p>
              <p><strong>Stops:</strong> Age 65</p>
              <p className="text-blue-600 font-semibold">30 years total</p>
            </div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-pink-50">
          <div className="text-center">
            <div className="text-6xl mb-3">🧑‍🔬</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Late Larry</h3>
            <div className="space-y-1 text-sm text-gray-700">
              <p><strong>Starts:</strong> Age 45</p>
              <p><strong>Invests:</strong> $500/month</p>
              <p><strong>Stops:</strong> Age 65</p>
              <p className="text-purple-600 font-semibold">20 years total</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="text-center">
        <Button onClick={onNext} size="lg">
          See Who Wins
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 2: The Race (Animated)
function StepRace({ onNext }: { onNext: () => void }) {
  const [currentAge, setCurrentAge] = useState(25)
  const [isPlaying, setIsPlaying] = useState(false)
  const returnRate = 0.08 // 8% annual return

  // Calculate values for each character at current age
  const calculateValue = (startAge: number, endAge: number, monthlyAmount: number, currentAge: number) => {
    if (currentAge < startAge || currentAge > endAge) {
      const yearsInvesting = Math.max(0, Math.min(endAge, currentAge) - startAge)
      const yearsGrowing = Math.max(0, currentAge - startAge)
      
      if (yearsInvesting === 0) return { balance: 0, invested: 0 }
      
      // Calculate final value with compound growth after stopping contributions
      const monthlyRate = returnRate / 12
      const months = yearsInvesting * 12
      
      // Future value of annuity
      let balance = monthlyAmount * (((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate))
      
      // Continue growing after contributions stop
      const additionalYears = currentAge - endAge
      if (additionalYears > 0) {
        balance = balance * Math.pow(1 + returnRate, additionalYears)
      }
      
      return { 
        balance, 
        invested: monthlyAmount * months 
      }
    }
    
    const months = (currentAge - startAge) * 12
    const monthlyRate = returnRate / 12
    const balance = monthlyAmount * (((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate))
    
    return { 
      balance, 
      invested: monthlyAmount * months 
    }
  }

  const emma = calculateValue(25, 35, 300, currentAge)
  const steven = calculateValue(35, 65, 300, currentAge)
  const larry = calculateValue(45, 65, 500, currentAge)

  const maxValue = Math.max(emma.balance, steven.balance, larry.balance, 100000)

  // Auto-play animation
  useState(() => {
    if (isPlaying && currentAge < 65) {
      const timer = setTimeout(() => {
        setCurrentAge(currentAge + 1)
      }, 200)
      return () => clearTimeout(timer)
    } else if (currentAge >= 65) {
      setIsPlaying(false)
    }
  })

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The Race to Retirement
        </h2>
        <p className="text-lg text-gray-600">
          Watch how their investments grow over time
        </p>
      </div>

      {/* Age Control */}
      <Card className="max-w-4xl mx-auto">
        <div className="text-center mb-6">
          <div className="text-sm text-gray-600 mb-2">Current Age</div>
          <div className="text-5xl font-bold text-blue-600 mb-4">
            {currentAge}
          </div>
        </div>
        
        <Slider
          min={25}
          max={65}
          step={1}
          value={currentAge}
          onChange={setCurrentAge}
          label="Age Slider"
          format={(v) => `Age ${v}`}
          color="blue"
        />

        <div className="flex justify-center gap-4 mt-6">
          <Button
            onClick={() => {
              setCurrentAge(25)
              setIsPlaying(false)
            }}
            variant="outline"
          >
            Reset
          </Button>
          <Button
            onClick={() => setIsPlaying(!isPlaying)}
            variant="primary"
          >
            {isPlaying ? 'Pause' : 'Play Animation'}
          </Button>
          <Button
            onClick={() => setCurrentAge(65)}
            variant="secondary"
          >
            Skip to End
          </Button>
        </div>
      </Card>

      {/* Character Progress Bars */}
      <div className="max-w-4xl mx-auto space-y-4">
        {/* Emma */}
        <Card className="bg-green-50">
          <div className="flex items-center gap-4">
            <div className="text-4xl">👩‍💼</div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-gray-900">Early Bird Emma</span>
                <span className="text-lg font-bold text-green-600">
                  {formatCurrency(emma.balance)}
                </span>
              </div>
              <div className="h-8 bg-gray-200 rounded-full overflow-hidden relative">
                <motion.div
                  className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-end pr-3"
                  initial={{ width: '0%' }}
                  animate={{ width: `${(emma.balance / maxValue) * 100}%` }}
                  transition={{ duration: 0.5 }}
                >
                  {emma.balance > 0 && (
                    <span className="text-white text-sm font-semibold">
                      {formatCurrency(emma.balance)}
                    </span>
                  )}
                </motion.div>
              </div>
              <div className="text-xs text-gray-600 mt-1">
                Invested: {formatCurrency(emma.invested)} | 
                {currentAge >= 25 && currentAge <= 35 ? ' 💰 Contributing' : currentAge > 35 ? ' ✅ Done investing' : ' ⏳ Not started'}
              </div>
            </div>
          </div>
        </Card>

        {/* Steven */}
        <Card className="bg-blue-50">
          <div className="flex items-center gap-4">
            <div className="text-4xl">👨‍💻</div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-gray-900">Steady Steven</span>
                <span className="text-lg font-bold text-blue-600">
                  {formatCurrency(steven.balance)}
                </span>
              </div>
              <div className="h-8 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-400 to-cyan-500 rounded-full flex items-center justify-end pr-3"
                  initial={{ width: '0%' }}
                  animate={{ width: `${(steven.balance / maxValue) * 100}%` }}
                  transition={{ duration: 0.5 }}
                >
                  {steven.balance > 0 && (
                    <span className="text-white text-sm font-semibold">
                      {formatCurrency(steven.balance)}
                    </span>
                  )}
                </motion.div>
              </div>
              <div className="text-xs text-gray-600 mt-1">
                Invested: {formatCurrency(steven.invested)} | 
                {currentAge >= 35 && currentAge <= 65 ? ' 💰 Contributing' : currentAge < 35 ? ' ⏳ Not started' : ' ✅ Done'}
              </div>
            </div>
          </div>
        </Card>

        {/* Larry */}
        <Card className="bg-purple-50">
          <div className="flex items-center gap-4">
            <div className="text-4xl">🧑‍🔬</div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-gray-900">Late Larry</span>
                <span className="text-lg font-bold text-purple-600">
                  {formatCurrency(larry.balance)}
                </span>
              </div>
              <div className="h-8 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-end pr-3"
                  initial={{ width: '0%' }}
                  animate={{ width: `${(larry.balance / maxValue) * 100}%` }}
                  transition={{ duration: 0.5 }}
                >
                  {larry.balance > 0 && (
                    <span className="text-white text-sm font-semibold">
                      {formatCurrency(larry.balance)}
                    </span>
                  )}
                </motion.div>
              </div>
              <div className="text-xs text-gray-600 mt-1">
                Invested: {formatCurrency(larry.invested)} | 
                {currentAge >= 45 && currentAge <= 65 ? ' 💰 Contributing' : currentAge < 45 ? ' ⏳ Not started' : ' ✅ Done'}
              </div>
            </div>
          </div>
        </Card>
      </div>

      {currentAge >= 65 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <Button onClick={onNext} size="lg">
            See Final Results
            <ArrowRight className="w-5 h-5" />
          </Button>
        </motion.div>
      )}
    </motion.div>
  )
}

// Step 3: Final Results & Key Insights
function StepResults({ onNext }: { onNext: () => void }) {
  const returnRate = 0.08

  // Final calculations
  const emma = {
    name: 'Emma',
    totalInvested: 300 * 12 * 10,
    finalValue: 518000,
    years: 10,
    color: 'green',
    emoji: '👩‍💼'
  }

  const steven = {
    name: 'Steven',
    totalInvested: 300 * 12 * 30,
    finalValue: 446000,
    years: 30,
    color: 'blue',
    emoji: '👨‍💻'
  }

  const larry = {
    name: 'Larry',
    totalInvested: 500 * 12 * 20,
    finalValue: 274000,
    years: 20,
    color: 'purple',
    emoji: '🧑‍🔬'
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
          The Shocking Results! 🎯
        </h2>
      </div>

      {/* Podium */}
      <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-6">
        {/* 1st Place: Emma */}
        <Card className="bg-gradient-to-br from-yellow-100 to-yellow-200 border-4 border-yellow-400 relative">
          <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-12 h-12 bg-yellow-400 rounded-full flex items-center justify-center text-2xl font-bold border-4 border-white">
            🥇
          </div>
          <div className="text-center pt-6">
            <div className="text-6xl mb-3">{emma.emoji}</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Early Bird Emma</h3>
            <div className="text-3xl font-bold text-green-600 mb-2">
              {formatCurrency(emma.finalValue)}
            </div>
            <div className="space-y-1 text-sm text-gray-700">
              <p>Invested: {formatCurrency(emma.totalInvested)}</p>
              <p>Years: {emma.years}</p>
              <p className="text-green-600 font-semibold">
                Growth: {formatCurrency(emma.finalValue - emma.totalInvested)}
              </p>
            </div>
          </div>
        </Card>

        {/* 2nd Place: Steven */}
        <Card className="bg-gradient-to-br from-gray-100 to-gray-200 border-4 border-gray-400 relative">
          <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-12 h-12 bg-gray-400 rounded-full flex items-center justify-center text-2xl font-bold border-4 border-white">
            🥈
          </div>
          <div className="text-center pt-6">
            <div className="text-6xl mb-3">{steven.emoji}</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Steady Steven</h3>
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {formatCurrency(steven.finalValue)}
            </div>
            <div className="space-y-1 text-sm text-gray-700">
              <p>Invested: {formatCurrency(steven.totalInvested)}</p>
              <p>Years: {steven.years}</p>
              <p className="text-blue-600 font-semibold">
                Growth: {formatCurrency(steven.finalValue - steven.totalInvested)}
              </p>
            </div>
          </div>
        </Card>

        {/* 3rd Place: Larry */}
        <Card className="bg-gradient-to-br from-orange-100 to-orange-200 border-4 border-orange-400 relative">
          <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-12 h-12 bg-orange-400 rounded-full flex items-center justify-center text-2xl font-bold border-4 border-white">
            🥉
          </div>
          <div className="text-center pt-6">
            <div className="text-6xl mb-3">{larry.emoji}</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Late Larry</h3>
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {formatCurrency(larry.finalValue)}
            </div>
            <div className="space-y-1 text-sm text-gray-700">
              <p>Invested: {formatCurrency(larry.totalInvested)}</p>
              <p>Years: {larry.years}</p>
              <p className="text-purple-600 font-semibold">
                Growth: {formatCurrency(larry.finalValue - larry.totalInvested)}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Mind-Blowing Insights */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-300">
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            🤯 Mind-Blowing Facts
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6 text-left">
            <div className="bg-white rounded-lg p-4">
              <div className="text-4xl mb-2">💰</div>
              <h4 className="font-bold text-gray-900 mb-2">Emma invested 1/3 as much as Larry</h4>
              <p className="text-sm text-gray-700">
                Emma: {formatCurrency(emma.totalInvested)}<br/>
                Larry: {formatCurrency(larry.totalInvested)}<br/>
                <span className="text-green-600 font-semibold">
                  But ended up with {formatCurrency(emma.finalValue - larry.finalValue)} MORE!
                </span>
              </p>
            </div>

            <div className="bg-white rounded-lg p-4">
              <div className="text-4xl mb-2">⏰</div>
              <h4 className="font-bold text-gray-900 mb-2">Steven invested 3x longer than Emma</h4>
              <p className="text-sm text-gray-700">
                Steven: 30 years<br/>
                Emma: 10 years<br/>
                <span className="text-blue-600 font-semibold">
                  But Emma still won by {formatCurrency(emma.finalValue - steven.finalValue)}!
                </span>
              </p>
            </div>

            <div className="bg-white rounded-lg p-4">
              <div className="text-4xl mb-2">🚀</div>
              <h4 className="font-bold text-gray-900 mb-2">Emma's secret weapon</h4>
              <p className="text-sm text-gray-700">
                Her money had <span className="font-bold">40 YEARS</span> to compound (ages 25-65),
                even though she only contributed for 10 years.
              </p>
            </div>

            <div className="bg-white rounded-lg p-4">
              <div className="text-4xl mb-2">📈</div>
              <h4 className="font-bold text-gray-900 mb-2">The power of compounding</h4>
              <p className="text-sm text-gray-700">
                Emma's {formatCurrency(36000)} turned into {formatCurrency(518000)}<br/>
                <span className="text-green-600 font-semibold">
                  That's a {((emma.finalValue / emma.totalInvested - 1) * 100).toFixed(0)}x return!
                </span>
              </p>
            </div>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <Button onClick={onNext} size="lg">
          Calculate Your Own Scenario
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 4: Personal Calculator
function StepCalculator({ onComplete }: { onComplete: () => void }) {
  const [age, setAge] = useState(25)
  const [monthlyAmount, setMonthlyAmount] = useState(300)
  const [yearsInvesting, setYearsInvesting] = useState(10)
  const returnRate = 0.08

  // Calculate values
  const retirementAge = 65
  const endInvestingAge = age + yearsInvesting
  const yearsGrowing = retirementAge - age

  const monthlyRate = returnRate / 12
  const months = yearsInvesting * 12

  // Future value of annuity
  let finalValue = monthlyAmount * (((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate))
  
  // Continue growing after contributions stop
  const additionalYears = retirementAge - endInvestingAge
  if (additionalYears > 0) {
    finalValue = finalValue * Math.pow(1 + returnRate, additionalYears)
  }

  const totalInvested = monthlyAmount * months
  const totalGrowth = finalValue - totalInvested

  // Generate chart data
  const chartData = []
  for (let i = 0; i <= retirementAge - age; i++) {
    const currentAge = age + i
    const contributionYears = Math.min(i, yearsInvesting)
    const contributionMonths = contributionYears * 12
    
    let value = 0
    if (contributionMonths > 0) {
      value = monthlyAmount * (((Math.pow(1 + monthlyRate, contributionMonths) - 1) / monthlyRate))
      
      // Compound growth after stopping contributions
      const growthYears = Math.max(0, i - yearsInvesting)
      if (growthYears > 0) {
        value = value * Math.pow(1 + returnRate, growthYears)
      }
    }
    
    const invested = monthlyAmount * contributionMonths
    
    chartData.push({
      age: currentAge,
      balance: value,
      invested: invested,
    })
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
          Your Personal Scenario 🎯
        </h2>
        <p className="text-lg text-gray-600">
          Adjust the sliders to see your potential retirement wealth
        </p>
      </div>

      {/* Input Controls */}
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <Slider
            min={18}
            max={60}
            step={1}
            value={age}
            onChange={setAge}
            label="Your Current Age"
            format={(v) => `${v} years old`}
            color="blue"
          />
        </Card>

        <Card>
          <Slider
            min={50}
            max={1000}
            step={50}
            value={monthlyAmount}
            onChange={setMonthlyAmount}
            label="Monthly Investment"
            format={(v) => formatCurrency(v)}
            color="green"
          />
        </Card>

        <Card>
          <Slider
            min={1}
            max={Math.min(40, 65 - age)}
            step={1}
            value={Math.min(yearsInvesting, 65 - age)}
            onChange={setYearsInvesting}
            label="Years You'll Invest"
            format={(v) => `${v} years`}
            color="purple"
          />
        </Card>
      </div>

      {/* Results */}
      <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-4">
        <Card className="bg-blue-50 text-center">
          <DollarSign className="w-8 h-8 text-blue-500 mx-auto mb-2" />
          <div className="text-sm text-gray-600 mb-1">Total Invested</div>
          <div className="text-2xl font-bold text-blue-600">
            {formatCurrency(totalInvested)}
          </div>
        </Card>

        <Card className="bg-green-50 text-center">
          <TrendingUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
          <div className="text-sm text-gray-600 mb-1">Investment Growth</div>
          <div className="text-2xl font-bold text-green-600">
            {formatCurrency(totalGrowth)}
          </div>
        </Card>

        <Card className="bg-purple-50 text-center">
          <Zap className="w-8 h-8 text-purple-500 mx-auto mb-2" />
          <div className="text-sm text-gray-600 mb-1">At Age 65</div>
          <div className="text-2xl font-bold text-purple-600">
            {formatCurrency(finalValue)}
          </div>
        </Card>
      </div>

      {/* Chart */}
      <Card className="max-w-4xl mx-auto">
        <h3 className="text-lg font-semibold mb-4 text-center">
          Your Investment Growth Timeline
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="colorInvested" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="age" label={{ value: 'Age', position: 'insideBottom', offset: -5 }} />
            <YAxis tickFormatter={(value) => formatCurrency(value)} />
            <Tooltip 
              formatter={(value: number, name: string) => [formatCurrency(value), name === 'balance' ? 'Total Balance' : 'Amount Invested']}
              labelFormatter={(label) => `Age ${label}`}
            />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="invested" 
              stroke="#3b82f6" 
              fillOpacity={1} 
              fill="url(#colorInvested)" 
              name="Amount Invested"
            />
            <Area 
              type="monotone" 
              dataKey="balance" 
              stroke="#8b5cf6" 
              fillOpacity={1} 
              fill="url(#colorBalance)" 
              name="Total Balance"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Key Takeaway */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-300">
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            💡 The Golden Rule of Investing
          </h3>
          <p className="text-xl text-gray-700 mb-4 font-semibold">
            "Time in the market beats timing the market"
          </p>
          <p className="text-lg text-gray-700">
            Starting early is MORE important than investing large amounts.
            <br />
            Even small monthly investments can grow into life-changing wealth.
          </p>
        </div>
      </Card>

      <div className="text-center space-y-4">
        <Button onClick={onComplete} size="lg" variant="primary">
          Complete Simulation (+500 XP)
        </Button>
        <p className="text-sm text-gray-500">
          🎉 Congratulations! You've unlocked the "Time Traveler" badge
        </p>
      </div>
    </motion.div>
  )
}

// Main Component
export default function CompoundInterestPage() {
  const [step, setStep] = useState(1)

  const handleComplete = () => {
    alert('Simulation complete! +500 XP earned')
    window.location.href = '/dashboard'
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Step {step} of 4</span>
          <span className="text-sm text-gray-500">15 min remaining</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500"
            initial={{ width: '0%' }}
            animate={{ width: `${(step / 4) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {/* Steps */}
      <AnimatePresence mode="wait">
        {step === 1 && <StepIntro onNext={() => setStep(2)} />}
        {step === 2 && <StepRace onNext={() => setStep(3)} />}
        {step === 3 && <StepResults onNext={() => setStep(4)} />}
        {step === 4 && <StepCalculator onComplete={handleComplete} />}
      </AnimatePresence>
    </div>
  )
}
