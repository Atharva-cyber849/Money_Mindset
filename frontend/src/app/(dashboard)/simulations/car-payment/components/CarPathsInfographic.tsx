'use client'

import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { formatCurrency } from '@/lib/utils'
import { TrendingDown, TrendingUp, DollarSign, Lightbulb } from 'lucide-react'

interface CarPathsInfographicProps {
  carPrice: number
}

type ColorTheme = 'blue' | 'amber' | 'green'

const colorConfig: Record<ColorTheme, { bgColor: string; borderColor: string; textColor: string; accentBg: string; accentText: string; badgeBg: string; badgeText: string }> = {
  blue: {
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-600',
    accentBg: 'bg-blue-200',
    accentText: 'text-blue-700',
    badgeBg: 'bg-blue-100',
    badgeText: 'text-blue-800'
  },
  amber: {
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    textColor: 'text-amber-600',
    accentBg: 'bg-amber-200',
    accentText: 'text-amber-700',
    badgeBg: 'bg-amber-100',
    badgeText: 'text-amber-800'
  },
  green: {
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    textColor: 'text-green-600',
    accentBg: 'bg-green-200',
    accentText: 'text-green-700',
    badgeBg: 'bg-green-100',
    badgeText: 'text-green-800'
  }
}

export function CarPathsInfographic({ carPrice }: CarPathsInfographicProps) {
  const paths: Array<{ id: string; title: string; icon: any; color: ColorTheme; monthlyPayment: number; upfront?: number; downPayment?: number; duration: number; totalCost: number; pros: string[]; cons: string[]; best: string }> = [
    {
      id: 'lease',
      title: 'LEASE',
      icon: TrendingDown,
      color: 'blue',
      monthlyPayment: 25000,
      upfront: 0,
      duration: 36,
      totalCost: 25000 * 36 + 10000,
      pros: ['Always a new car', 'Low maintenance', 'Warranty included'],
      cons: ['No ownership', 'Mileage limits', 'Higher total cost'],
      best: 'For those who like new cars regularly'
    },
    {
      id: 'finance',
      title: 'FINANCE',
      icon: TrendingUp,
      color: 'amber',
      monthlyPayment: 22000,
      downPayment: carPrice * 0.20,
      duration: 84,
      totalCost: carPrice * 0.20 + 22000 * 84,
      pros: ['Build equity', 'Ownership after loan', 'More flexibility'],
      cons: ['High maintenance after warranty', 'Interest costs', 'Depreciation risk'],
      best: 'For balanced lifestyle and budget'
    },
    {
      id: 'cash',
      title: 'CASH',
      icon: DollarSign,
      color: 'green',
      monthlyPayment: 0,
      upfront: carPrice,
      duration: 120,
      totalCost: carPrice,
      pros: ['No debt', 'Lowest total cost', 'Full ownership'],
      cons: ['Large upfront cost', 'Maintenance expenses', 'No warranty'],
      best: 'For those with surplus cash'
    }
  ]

  return (
    <div className="space-y-8">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-gray-900 mb-3">3 Paths to Get Your Car</h2>
        <p className="text-lg text-gray-600">Choose the option that fits your financial situation</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {paths.map((path, index) => {
          const IconComponent = path.icon
          const colors = colorConfig[path.color]
          
          return (
            <motion.div
              key={path.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className={`${colors.bgColor} border-2 ${colors.borderColor} p-6 h-full flex flex-col`}>
                <div className="flex items-center gap-3 mb-6">
                  <div className={`p-3 ${colors.accentBg} rounded-lg`}>
                    <IconComponent className={`w-6 h-6 ${colors.accentText}`} />
                  </div>
                  <h3 className={`text-2xl font-bold text-gray-900`}>{path.title}</h3>
                </div>

                {/* Cost Summary */}
                <div className="space-y-3 mb-6 pb-6 border-b-2 border-gray-200">
                  {path.upfront && path.upfront > 0 && (
                    <div>
                      <p className={`text-sm ${colors.accentText}`}>Upfront</p>
                      <p className={`text-2xl font-bold ${colors.textColor}`}>
                        {formatCurrency(path.upfront)}
                      </p>
                    </div>
                  )}
                  {path.downPayment && (
                    <div>
                      <p className={`text-sm ${colors.accentText}`}>Down Payment</p>
                      <p className={`text-2xl font-bold ${colors.textColor}`}>
                        {formatCurrency(path.downPayment)}
                      </p>
                    </div>
                  )}
                  {path.monthlyPayment > 0 && (
                    <div>
                      <p className={`text-sm ${colors.accentText}`}>Monthly</p>
                      <p className={`text-2xl font-bold ${colors.textColor}`}>
                        {formatCurrency(path.monthlyPayment)}/mo
                      </p>
                    </div>
                  )}
                  <div className="pt-2">
                    <p className={`text-xs ${colors.textColor} mb-1`}>Duration</p>
                    <p className="font-semibold text-gray-900">{path.duration} months</p>
                  </div>
                </div>

                {/* Total Cost */}
                <div className="mb-6 p-4 bg-white rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Total Cost</p>
                  <p className={`text-3xl font-bold ${colors.textColor}`}>
                    {formatCurrency(path.totalCost)}
                  </p>
                </div>

                {/* Best For */}
                <div className={`mb-6 p-3 ${colors.badgeBg} rounded-lg`}>
                  <p className={`text-xs font-semibold ${colors.badgeText} mb-1`}>BEST FOR</p>
                  <p className={`text-sm text-gray-700`}>{path.best}</p>
                </div>

                {/* Pros */}
                <div className="mb-4">
                  <p className="text-xs font-semibold text-gray-700 mb-2">PROS</p>
                  <ul className="space-y-1">
                    {path.pros.map((pro, i) => (
                      <li key={i} className="text-xs text-gray-700 flex items-start gap-2">
                        <span className={`${colors.textColor} font-bold mt-0.5`}>✓</span>
                        <span>{pro}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Cons */}
                <div className="flex-1">
                  <p className="text-xs font-semibold text-gray-700 mb-2">CONS</p>
                  <ul className="space-y-1">
                    {path.cons.map((con, i) => (
                      <li key={i} className="text-xs text-gray-600 flex items-start gap-2">
                        <span className="text-gray-400 font-bold mt-0.5">✕</span>
                        <span>{con}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* Educational Note */}
      <Card className="bg-gradient-to-r from-teal-50 to-blue-50 border-2 border-teal-200 p-6">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-6 h-6 text-teal-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-lg text-gray-900 mb-3">Key Insight</h3>
            <p className="text-gray-700 mb-3">
              The best choice depends on your monthly budget and current financial situation. 
              Each path has trade-offs:
            </p>
            <ul className="space-y-2 text-sm text-gray-700">
              <li><strong>Lease:</strong> Best monthly payment but highest total cost</li>
              <li><strong>Finance:</strong> Balanced approach with ownership benefits</li>
              <li><strong>Cash:</strong> Lowest total cost if you have the money upfront</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  )
}
