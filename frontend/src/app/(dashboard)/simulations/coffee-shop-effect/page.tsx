'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Coffee, TrendingUp, Lightbulb, ArrowRight } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

// Step 1: Initial Guess
function StepGuess({ onNext }: { onNext: (guess: number) => void }) {
  const [guess, setGuess] = useState(5000)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center">
          <Coffee className="w-12 h-12 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The Daily Chai Challenge ☕
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          You buy a ₹20 chai from the local tea stall every workday (Monday-Friday). 
          <br />
          <span className="font-semibold text-gray-900">How much do you think this costs per year?</span>
        </p>
      </div>

      <Card className="max-w-2xl mx-auto">
        <Slider
          min={1000}
          max={20000}
          step={500}
          value={guess}
          onChange={setGuess}
          label="Your Guess"
          format={(v) => formatCurrency(v)}
          color="blue"
        />
        
        <div className="mt-8 text-center">
          <Button onClick={() => onNext(guess)} size="lg">
            Lock in My Guess
            <ArrowRight className="w-5 h-5" />
          </Button>
        </div>
      </Card>

      <div className="text-center text-sm text-gray-500">
        💡 Most people guess between ₹4,000-₹8,000
      </div>
    </motion.div>
  )
}

// Step 2: The Reality
function StepReality({ guess, onNext }: { guess: number; onNext: () => void }) {
  const dailyCost = 20
  const workdaysPerWeek = 5
  const weeksPerYear = 52
  const actualCost = dailyCost * workdaysPerWeek * weeksPerYear
  const difference = Math.abs(actualCost - guess)
  const percentOff = ((difference / actualCost) * 100).toFixed(0)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The Reality 😱
        </h2>
      </div>

      <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Your Guess */}
        <Card className="text-center">
          <div className="text-sm text-gray-600 mb-2">Your Guess</div>
          <div className="text-4xl font-bold text-blue-600 mb-2">
            {formatCurrency(guess)}
          </div>
          <div className="text-sm text-gray-500">per year</div>
        </Card>

        {/* Actual Cost */}
        <Card className="text-center bg-gradient-to-br from-red-50 to-orange-50">
          <div className="text-sm text-gray-600 mb-2">Actual Cost</div>
          <div className="text-4xl font-bold text-red-600 mb-2">
            {formatCurrency(actualCost)}
          </div>
          <div className="text-sm text-red-600 font-semibold">per year</div>
        </Card>
      </div>

      {/* Analysis */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-orange-200">
        <div className="text-center">
          <Lightbulb className="w-12 h-12 text-orange-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            You were off by {formatCurrency(difference)}!
          </h3>
          <p className="text-gray-700 text-lg">
            That's <span className="font-bold text-orange-600">{percentOff}%</span> off from the actual cost
          </p>
          <div className="mt-6 p-4 bg-white rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Here's the math:</div>
            <div className="text-left max-w-md mx-auto font-mono text-sm space-y-1">
              <div>₹20 per chai</div>
              <div>× 5 workdays per week</div>
              <div>× 52 weeks per year</div>
              <div className="border-t-2 border-gray-300 pt-1 font-bold text-lg text-red-600">
                = {formatCurrency(actualCost)} / year
              </div>
            </div>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <Button onClick={onNext} size="lg">
          See Long-Term Impact
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 3: Long-Term Compound Effect
function StepCompound({ onNext }: { onNext: () => void }) {
  const [years, setYears] = useState(10)
  
  const dailyCost = 20
  const workdaysPerWeek = 5
  const weeksPerYear = 52
  const annualCost = dailyCost * workdaysPerWeek * weeksPerYear

  // Calculate compound data
  const data = Array.from({ length: years + 1 }, (_, i) => ({
    year: i,
    spending: annualCost * i,
    invested: calculateFutureValue(annualCost, 0.08, i), // 8% return
  }))

  function calculateFutureValue(pmt: number, rate: number, years: number): number {
    if (years === 0) return 0
    return pmt * (((Math.pow(1 + rate, years) - 1) / rate))
  }

  const totalSpent = annualCost * years
  const ifInvested = data[years].invested
  const difference = ifInvested - totalSpent

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The Compound Effect Over Time
        </h2>
        <p className="text-lg text-gray-600">
          What if you invested that chai money instead?
        </p>
      </div>

      {/* Year Slider */}
      <Card className="max-w-4xl mx-auto">
        <Slider
          min={1}
          max={30}
          step={1}
          value={years}
          onChange={setYears}
          label="Time Horizon"
          format={(v) => `${v} years`}
          color="purple"
        />
      </Card>

      {/* Comparison Cards */}
      <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-6">
        <Card className="bg-red-50">
          <div className="text-center">
            <Coffee className="w-12 h-12 text-red-500 mx-auto mb-3" />
            <div className="text-sm text-gray-600 mb-2">Money Spent on Chai</div>
            <div className="text-3xl font-bold text-red-600 mb-2">
              {formatCurrency(totalSpent)}
            </div>
            <div className="text-sm text-gray-600">
              After {years} years
            </div>
          </div>
        </Card>

        <Card className="bg-green-50">
          <div className="text-center">
            <TrendingUp className="w-12 h-12 text-green-500 mx-auto mb-3" />
            <div className="text-sm text-gray-600 mb-2">If Invested (8% return)</div>
            <div className="text-3xl font-bold text-green-600 mb-2">
              {formatCurrency(ifInvested)}
            </div>
            <div className="text-sm text-green-600 font-semibold">
              +{formatCurrency(difference)} more!
            </div>
          </div>
        </Card>
      </div>

      {/* Chart */}
      <Card className="max-w-4xl mx-auto">
        <h3 className="text-lg font-semibold mb-4 text-center">
          Chai Spending vs Investment Growth
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorSpending" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorInvested" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" label={{ value: 'Years', position: 'insideBottom', offset: -5 }} />
            <YAxis tickFormatter={(value) => formatCurrency(value)} />
            <Tooltip formatter={(value) => formatCurrency(Number(value))} />
            <Area type="monotone" dataKey="spending" stroke="#ef4444" fillOpacity={1} fill="url(#colorSpending)" name="Chai Spending" />
            <Area type="monotone" dataKey="invested" stroke="#10b981" fillOpacity={1} fill="url(#colorInvested)" name="If Invested" />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      <div className="text-center">
        <Button onClick={onNext} size="lg">
          What Could You Buy Instead?
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 4: Opportunity Cost Visualizations
function StepOpportunityCost({ onComplete }: { onComplete: () => void }) {
  const annualCost = 5200
  const [selectedYears, setSelectedYears] = useState(5)
  const totalSavings = annualCost * selectedYears

  const purchases = [
    { name: 'iPhone 15 Pro', cost: 79900, icon: '📱' },
    { name: 'Trip to Goa/Maldives', cost: 200000, icon: '🏝️' },
    { name: 'MacBook Air', cost: 99900, icon: '💻' },
    { name: 'Gold Chain / Jewelry', cost: 300000, icon: '⛓️' },
    { name: 'Emergency Fund', cost: totalSavings, icon: '🛡️' },
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
          What Could You Buy Instead?
        </h2>
        <p className="text-lg text-gray-600">
          This is called "opportunity cost" - what you're giving up by spending on daily chai
        </p>
      </div>

      {/* Year Selector */}
      <Card className="max-w-4xl mx-auto">
        <div className="text-center mb-6">
          <div className="text-sm text-gray-600 mb-2">Total Savings Over</div>
          <div className="text-5xl font-bold text-blue-600 mb-4">
            {formatCurrency(totalSavings)}
          </div>
        </div>
        
        <Slider
          min={1}
          max={10}
          step={1}
          value={selectedYears}
          onChange={setSelectedYears}
          label="Years of Chai Savings"
          format={(v) => `${v} years`}
          color="blue"
        />
      </Card>

      {/* Affordable Purchases Grid */}
      <div className="max-w-4xl mx-auto">
        <h3 className="text-xl font-semibold text-gray-900 mb-4 text-center">
          You Could Afford:
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {purchases.map((purchase) => {
            const canAfford = purchase.cost <= totalSavings
            return (
              <Card
                key={purchase.name}
                className={canAfford ? 'bg-green-50 border-2 border-green-300' : 'opacity-50'}
              >
                <div className="text-center">
                  <div className="text-4xl mb-2">{purchase.icon}</div>
                  <div className="text-sm font-semibold text-gray-900 mb-1">
                    {purchase.name}
                  </div>
                  <div className="text-sm text-gray-600">
                    {formatCurrency(purchase.cost)}
                  </div>
                  {canAfford && (
                    <div className="mt-2 text-xs font-semibold text-green-600">
                      ✓ Affordable!
                    </div>
                  )}
                </div>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Key Takeaway */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-300">
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            💡 Key Takeaway
          </h3>
          <p className="text-lg text-gray-700 mb-4">
            Small daily expenses add up. Your ₹20 daily chai habit could become:
          </p>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="bg-white rounded-lg p-4">
              <div className="font-bold text-blue-600 mb-1">Entertainment Budget</div>
              <div className="text-gray-600">Every month</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="font-bold text-purple-600 mb-1">Weekend Outing</div>
              <div className="text-gray-600">Every quarter</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="font-bold text-green-600 mb-1">Emergency Fund</div>
              <div className="text-gray-600">Building security</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Alternative Solution */}
      <Card className="max-w-4xl mx-auto">
        <h3 className="text-xl font-semibold text-gray-900 mb-4 text-center">
          💰 Smart Alternative: The 3-Day Rule
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <div className="text-center mb-4">
              <div className="text-3xl mb-2">☕</div>
              <div className="font-semibold text-gray-900">Chai Daily (5 Days)</div>
              <div className="text-2xl font-bold text-red-600">{formatCurrency(5200)}/year</div>
            </div>
          </div>
          <div>
            <div className="text-center mb-4">
              <div className="text-3xl mb-2">🏠</div>
              <div className="font-semibold text-gray-900">Chai 2 Days + Home Made 3 Days</div>
              <div className="text-2xl font-bold text-green-600">{formatCurrency(2080)}/year</div>
              <div className="text-sm text-green-600 font-semibold mt-1">
                Save {formatCurrency(3120)}/year!
              </div>
            </div>
          </div>
        </div>
      </Card>

      <div className="text-center space-y-4">
        <div className="flex justify-center gap-4">
          <Button onClick={onComplete} size="lg" variant="primary">
            Complete Simulation (+100 XP)
          </Button>
        </div>
        <p className="text-sm text-gray-500">
          🎉 Congratulations! You've unlocked the "Money Mindful" badge
        </p>
      </div>
    </motion.div>
  )
}

// Main Component
export default function CoffeeShopEffectPage() {
  const [step, setStep] = useState(1)
  const [userGuess, setUserGuess] = useState(0)

  const handleComplete = async () => {
    try {
      // Calculate score based on guess accuracy
      const actualCost = 20 * 5 * 52 // ₹5,200
      const difference = Math.abs(actualCost - userGuess)
      const accuracyPercent = Math.max(0, 100 - (difference / actualCost * 100))
      const score = Math.round(accuracyPercent)
      const isPerfect = score >= 95
      
      // Call API to mark completion and award XP
      const response = await fetch('/api/v1/simulations/coffee-shop-effect/complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}` // Get from auth context in production
        },
        body: JSON.stringify({
          user_score: score,
          perfect_score: isPerfect
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        
        // Show success message with XP earned
        const xpMessage = `+${result.xp_earned.amount} XP earned! ${result.xp_earned.reason}`
        
        let alertMessage = `🎉 Simulation Complete!\n\n${xpMessage}`
        
        // Add level up message
        if (result.level_up) {
          alertMessage += `\n\n⬆️ ${result.level_up.celebration_message}`
        }
        
        // Add badges
        if (result.badges_earned.length > 0) {
          alertMessage += `\n\n🏆 Badges Earned:`
          result.badges_earned.forEach((badge: any) => {
            alertMessage += `\n${badge.icon} ${badge.name} - ${badge.description}`
          })
        }
        
        // Add new unlocks
        if (result.new_unlocks.length > 0) {
          alertMessage += `\n\n🔓 New Simulations Unlocked:`
          result.new_unlocks.forEach((unlock: any) => {
            alertMessage += `\n• ${unlock.simulation_name} (+${unlock.xp_reward} XP)`
          })
        }
        
        alert(alertMessage)
        window.location.href = '/dashboard'
      } else {
        throw new Error('Failed to complete simulation')
      }
    } catch (error) {
      console.error('Error completing simulation:', error)
      // Fallback to local completion
      alert('Simulation complete! +100 XP earned')
      window.location.href = '/dashboard'
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Step {step} of 4</span>
          <span className="text-sm text-gray-500">5 min remaining</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
            initial={{ width: '0%' }}
            animate={{ width: `${(step / 4) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {/* Steps */}
      <AnimatePresence mode="wait">
        {step === 1 && (
          <StepGuess
            onNext={(guess) => {
              setUserGuess(guess)
              setStep(2)
            }}
          />
        )}
        {step === 2 && (
          <StepReality
            guess={userGuess}
            onNext={() => setStep(3)}
          />
        )}
        {step === 3 && (
          <StepCompound onNext={() => setStep(4)} />
        )}
        {step === 4 && (
          <StepOpportunityCost onComplete={handleComplete} />
        )}
      </AnimatePresence>
    </div>
  )
}
