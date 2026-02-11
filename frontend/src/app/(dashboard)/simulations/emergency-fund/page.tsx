'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, AlertTriangle, CreditCard, TrendingUp, DollarSign, Heart, Zap, ArrowRight, Check, X } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { formatCurrency } from '@/lib/utils'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

interface Character {
  name: string
  avatar: string
  hasEmergencyFund: boolean
  emergencyFund: number
  debt: number
  stress: number
}

interface Emergency {
  month: number
  type: string
  cost: number
  description: string
}

// Step 1: Introduction
function StepIntro({ onNext }: { onNext: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center">
          <Shield className="w-12 h-12 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          The Emergency Fund Race
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Follow two people through 12 months of life's surprises.
          <br />
          <span className="font-semibold text-gray-900">One has an emergency fund. One doesn't.</span>
        </p>
      </div>

      <Card className="max-w-4xl mx-auto">
        <div className="grid md:grid-cols-2 gap-6">
          {/* Character 1: Prepared */}
          <div className="text-center p-6 bg-green-50 rounded-lg">
            <div className="text-6xl mb-4">👩‍💼</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Sarah</h3>
            <div className="space-y-2 text-left">
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-2" />
                <span>Has $5,000 emergency fund</span>
              </div>
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-2" />
                <span>Saves $400/month</span>
              </div>
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-2" />
                <span>Feels financially secure</span>
              </div>
            </div>
          </div>

          {/* Character 2: Unprepared */}
          <div className="text-center p-6 bg-red-50 rounded-lg">
            <div className="text-6xl mb-4">👨‍💼</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Mike</h3>
            <div className="space-y-2 text-left">
              <div className="flex items-center">
                <X className="w-5 h-5 text-red-500 mr-2" />
                <span>$0 emergency fund</span>
              </div>
              <div className="flex items-center">
                <X className="w-5 h-5 text-red-500 mr-2" />
                <span>Lives paycheck to paycheck</span>
              </div>
              <div className="flex items-center">
                <X className="w-5 h-5 text-red-500 mr-2" />
                <span>One emergency away from debt</span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <div className="text-center">
        <p className="text-gray-600 mb-4">
          Both earn $4,000/month and have $3,200 in expenses.
          <br />
          Let's see what happens when life throws curveballs...
        </p>
        <Button onClick={onNext} size="lg">
          Start Simulation
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </motion.div>
  )
}

// Step 2: Month-by-Month Race
function StepRace({ onNext }: { onNext: (sarah: Character, mike: Character, emergencies: Emergency[]) => void }) {
  const [currentMonth, setCurrentMonth] = useState(0)
  const [sarah, setSarah] = useState<Character>({
    name: 'Sarah',
    avatar: '👩‍💼',
    hasEmergencyFund: true,
    emergencyFund: 5000,
    debt: 0,
    stress: 2,
  })
  const [mike, setMike] = useState<Character>({
    name: 'Mike',
    avatar: '👨‍💼',
    hasEmergencyFund: false,
    emergencyFund: 0,
    debt: 0,
    stress: 5,
  })
  const [emergencies, setEmergencies] = useState<Emergency[]>([])
  const [showEmergency, setShowEmergency] = useState(false)
  const [currentEmergency, setCurrentEmergency] = useState<Emergency | null>(null)

  const monthlyIncome = 4000
  const monthlyExpenses = 3200
  const monthlySurplus = monthlyIncome - monthlyExpenses

  // Predefined emergencies
  const emergencyEvents: Emergency[] = [
    { month: 2, type: 'car', cost: 800, description: '🚗 Car broke down - needs new battery and brakes' },
    { month: 5, type: 'medical', cost: 1200, description: '🏥 Emergency dental work required' },
    { month: 8, type: 'home', cost: 600, description: '🏠 Water heater failed and needs replacement' },
    { month: 11, type: 'appliance', cost: 900, description: '❄️ Refrigerator died - need new one ASAP' },
  ]

  useEffect(() => {
    if (currentMonth >= 12) {
      onNext(sarah, mike, emergencies)
      return
    }

    const timer = setTimeout(() => {
      // Check for emergency this month
      const emergency = emergencyEvents.find(e => e.month === currentMonth)
      
      if (emergency) {
        setCurrentEmergency(emergency)
        setShowEmergency(true)
        setEmergencies(prev => [...prev, emergency])

        // Handle emergency for both characters
        setTimeout(() => {
          setSarah(prev => {
            const canPayFromFund = prev.emergencyFund >= emergency.cost
            if (canPayFromFund) {
              return {
                ...prev,
                emergencyFund: prev.emergencyFund - emergency.cost,
                stress: Math.min(prev.stress + 1, 10),
              }
            } else {
              const debtAdded = emergency.cost - prev.emergencyFund
              return {
                ...prev,
                emergencyFund: 0,
                debt: prev.debt + debtAdded,
                stress: Math.min(prev.stress + 3, 10),
              }
            }
          })

          setMike(prev => ({
            ...prev,
            debt: prev.debt + emergency.cost,
            stress: Math.min(prev.stress + 3, 10),
          }))

          setShowEmergency(false)
          setCurrentMonth(prev => prev + 1)
        }, 3000)
      } else {
        // Normal month - add savings
        setSarah(prev => ({
          ...prev,
          emergencyFund: prev.emergencyFund + 400,
          debt: Math.max(0, prev.debt - prev.debt * 0.05),
          stress: Math.max(1, prev.stress - 0.5),
        }))

        setMike(prev => ({
          ...prev,
          debt: prev.debt + (prev.debt > 0 ? prev.debt * 0.018 : 0), // 22% APR
          stress: prev.debt > 0 ? Math.min(prev.stress + 0.5, 10) : prev.stress,
        }))

        setCurrentMonth(prev => prev + 1)
      }
    }, 1500)

    return () => clearTimeout(timer)
  }, [currentMonth])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Month {currentMonth} of 12
        </h2>
        <p className="text-gray-600">Watch how they handle life's surprises</p>
      </div>

      {/* Progress Bar */}
      <div className="max-w-4xl mx-auto">
        <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 transition-all duration-500"
            style={{ width: `${(currentMonth / 12) * 100}%` }}
          />
        </div>
      </div>

      {/* Emergency Alert */}
      <AnimatePresence>
        {showEmergency && currentEmergency && (
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="max-w-2xl mx-auto"
          >
            <Card className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-300">
              <div className="text-center">
                <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  Emergency!
                </h3>
                <p className="text-lg text-gray-700 mb-4">{currentEmergency.description}</p>
                <div className="text-3xl font-bold text-red-600">
                  Cost: {formatCurrency(currentEmergency.cost)}
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Characters */}
      <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Sarah */}
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50">
          <div className="text-center">
            <div className="text-6xl mb-3">{sarah.avatar}</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">{sarah.name}</h3>
            
            <div className="space-y-3">
              <div className="bg-white p-3 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Emergency Fund</div>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(sarah.emergencyFund)}
                </div>
              </div>
              
              <div className="bg-white p-3 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Debt</div>
                <div className={`text-2xl font-bold ${sarah.debt > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {formatCurrency(sarah.debt)}
                </div>
              </div>
              
              <div className="bg-white p-3 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Stress Level</div>
                <div className="flex justify-center gap-1">
                  {Array.from({ length: 10 }).map((_, i) => (
                    <div
                      key={i}
                      className={`w-3 h-6 rounded ${
                        i < sarah.stress ? 'bg-yellow-400' : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Mike */}
        <Card className="bg-gradient-to-br from-red-50 to-orange-50">
          <div className="text-center">
            <div className="text-6xl mb-3">{mike.avatar}</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">{mike.name}</h3>
            
            <div className="space-y-3">
              <div className="bg-white p-3 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Emergency Fund</div>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(mike.emergencyFund)}
                </div>
              </div>
              
              <div className="bg-white p-3 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Credit Card Debt</div>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(mike.debt)}
                </div>
              </div>
              
              <div className="bg-white p-3 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Stress Level</div>
                <div className="flex justify-center gap-1">
                  {Array.from({ length: 10 }).map((_, i) => (
                    <div
                      key={i}
                      className={`w-3 h-6 rounded ${
                        i < mike.stress ? 'bg-red-500' : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {currentMonth >= 12 && (
        <div className="text-center">
          <Button onClick={() => onNext(sarah, mike, emergencies)} size="lg">
            See Final Results
            <ArrowRight className="w-5 h-5" />
          </Button>
        </div>
      )}
    </motion.div>
  )
}

// Step 3: Results
function StepResults({ sarah, mike, emergencies, onNext }: {
  sarah: Character
  mike: Character
  emergencies: Emergency[]
  onNext: () => void
}) {
  // Calculate net worth
  const sarahNetWorth = sarah.emergencyFund - sarah.debt
  const mikeNetWorth = mike.emergencyFund - mike.debt
  const difference = sarahNetWorth - mikeNetWorth

  // Timeline data
  const timelineData = Array.from({ length: 13 }, (_, month) => {
    let sarahFund = 5000
    let sarahDebt = 0
    let mikeDebt = 0

    emergencies.forEach(emergency => {
      if (emergency.month <= month) {
        // Sarah handles emergency
        if (sarahFund >= emergency.cost) {
          sarahFund -= emergency.cost
        } else {
          sarahDebt += emergency.cost - sarahFund
          sarahFund = 0
        }
        // Mike goes into debt
        mikeDebt += emergency.cost
      }
    })

    // Add monthly savings for Sarah (excluding emergency months)
    const normalMonths = month - emergencies.filter(e => e.month <= month).length
    sarahFund += normalMonths * 400

    // Add credit card interest for Mike
    emergencies.forEach(emergency => {
      if (emergency.month < month) {
        const monthsOfInterest = month - emergency.month
        mikeDebt *= Math.pow(1.018, monthsOfInterest)
      }
    })

    return {
      month,
      sarah: sarahFund - sarahDebt,
      mike: -mikeDebt,
    }
  })

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          One Year Later...
        </h2>
      </div>

      {/* Final Comparison */}
      <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Sarah */}
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300">
          <div className="text-center">
            <div className="text-6xl mb-3">👩‍💼</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Sarah</h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Emergency Fund</div>
                <div className="text-3xl font-bold text-green-600">{formatCurrency(sarah.emergencyFund)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Debt</div>
                <div className="text-2xl font-bold text-green-600">{formatCurrency(sarah.debt)}</div>
              </div>
              <div className="pt-3 border-t">
                <div className="text-sm text-gray-600">Net Worth</div>
                <div className="text-4xl font-bold text-green-600">{formatCurrency(sarahNetWorth)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Average Stress</div>
                <div className="text-xl font-bold text-green-600">😊 Low (3/10)</div>
              </div>
            </div>
          </div>
        </Card>

        {/* Mike */}
        <Card className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-300">
          <div className="text-center">
            <div className="text-6xl mb-3">👨‍💼</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Mike</h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Emergency Fund</div>
                <div className="text-3xl font-bold text-red-600">{formatCurrency(mike.emergencyFund)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Credit Card Debt</div>
                <div className="text-2xl font-bold text-red-600">{formatCurrency(mike.debt)}</div>
              </div>
              <div className="pt-3 border-t">
                <div className="text-sm text-gray-600">Net Worth</div>
                <div className="text-4xl font-bold text-red-600">{formatCurrency(mikeNetWorth)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Average Stress</div>
                <div className="text-xl font-bold text-red-600">😰 High (8/10)</div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Difference */}
      <Card className="max-w-4xl mx-auto bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-300">
        <div className="text-center">
          <Zap className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            The Emergency Fund Difference
          </h3>
          <div className="text-5xl font-bold text-green-600 mb-2">
            {formatCurrency(difference)}
          </div>
          <p className="text-gray-700 text-lg">
            Sarah is {formatCurrency(difference)} better off than Mike!
          </p>
        </div>
      </Card>

      {/* Timeline Chart */}
      <Card className="max-w-5xl mx-auto">
        <h3 className="text-lg font-semibold mb-4 text-center">Net Worth Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={timelineData}>
            <defs>
              <linearGradient id="colorSarah" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorMike" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" label={{ value: 'Months', position: 'insideBottom', offset: -5 }} />
            <YAxis tickFormatter={(value) => formatCurrency(value)} />
            <Tooltip formatter={(value) => formatCurrency(Number(value))} />
            <Area type="monotone" dataKey="sarah" stroke="#10b981" fillOpacity={1} fill="url(#colorSarah)" name="Sarah (With Fund)" />
            <Area type="monotone" dataKey="mike" stroke="#ef4444" fillOpacity={1} fill="url(#colorMike)" name="Mike (No Fund)" />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Key Insights */}
      <Card className="max-w-4xl mx-auto">
        <h3 className="text-xl font-bold mb-4 text-center">Key Insights</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="font-semibold text-green-900 mb-2">✅ With Emergency Fund:</div>
            <ul className="space-y-1 text-sm text-gray-700">
              <li>• Handled 4 emergencies without debt</li>
              <li>• Still has money saved</li>
              <li>• Low stress throughout year</li>
              <li>• Building wealth steadily</li>
            </ul>
          </div>
          <div className="p-4 bg-red-50 rounded-lg">
            <div className="font-semibold text-red-900 mb-2">❌ Without Emergency Fund:</div>
            <ul className="space-y-1 text-sm text-gray-700">
              <li>• Went into debt for every emergency</li>
              <li>• Paying 22% interest on debt</li>
              <li>• High stress all year</li>
              <li>• Net worth is negative</li>
            </ul>
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
      <div className="w-24 h-24 mx-auto bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center">
        <Shield className="w-12 h-12 text-white" />
      </div>
      
      <h2 className="text-4xl font-bold text-gray-900">
        Simulation Complete! 🎉
      </h2>
      
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="text-center">
          <div className="text-6xl mb-4">⭐</div>
          <div className="text-3xl font-bold text-blue-600 mb-2">+150 XP</div>
          <div className="text-gray-600">You've learned the power of emergency funds!</div>
        </div>
      </Card>

      <div className="space-y-3">
        <h3 className="font-semibold text-lg">How to Build Your Emergency Fund:</h3>
        <div className="text-left space-y-2">
          <div className="flex items-start">
            <span className="mr-2">1️⃣</span>
            <span>Start with $1,000 as your first goal</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">2️⃣</span>
            <span>Save in a high-yield savings account (separate from checking)</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">3️⃣</span>
            <span>Aim for 3-6 months of expenses as your final goal</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">4️⃣</span>
            <span>Automate monthly transfers on payday</span>
          </div>
          <div className="flex items-start">
            <span className="mr-2">5️⃣</span>
            <span>Only use for true emergencies, then replenish</span>
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
export default function EmergencyFundPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [sarah, setSarah] = useState<Character | null>(null)
  const [mike, setMike] = useState<Character | null>(null)
  const [emergencies, setEmergencies] = useState<Emergency[]>([])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
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
            <StepIntro key="intro" onNext={() => setCurrentStep(2)} />
          )}
          {currentStep === 2 && (
            <StepRace
              key="race"
              onNext={(s, m, e) => {
                setSarah(s)
                setMike(m)
                setEmergencies(e)
                setCurrentStep(3)
              }}
            />
          )}
          {currentStep === 3 && sarah && mike && (
            <StepResults
              key="results"
              sarah={sarah}
              mike={mike}
              emergencies={emergencies}
              onNext={() => setCurrentStep(4)}
            />
          )}
          {currentStep === 4 && <StepComplete key="complete" />}
        </AnimatePresence>
      </div>
    </div>
  )
}
