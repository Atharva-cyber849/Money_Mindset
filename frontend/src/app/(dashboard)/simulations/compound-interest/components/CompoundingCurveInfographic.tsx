import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card } from '@/components/ui/Card'
import { Zap, TrendingUp } from 'lucide-react'

interface CompoundingCurveInfographicProps {
  data?: Array<{ year: number; amount: number }>
}

export const CompoundingCurveInfographic: React.FC<CompoundingCurveInfographicProps> = ({
  data
}) => {
  const defaultData = useMemo(() => {
    const data = []
    const principal = 100000
    const monthlyInvestment = 5000
    const annualRate = 0.12

    let balance = principal
    for (let year = 0; year <= 30; year++) {
      data.push({
        year,
        amount: Math.round(balance),
        contributions: Math.round(principal + monthlyInvestment * 12 * year),
        growth: Math.round(balance - (principal + monthlyInvestment * 12 * year))
      })

      for (let month = 0; month < 12; month++) {
        balance = (balance + monthlyInvestment) * (1 + annualRate / 12)
      }
    }

    return data
  }, [])

  const chartData = data || defaultData

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <div className="mb-8">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">How Compounding Works</h2>
        <p className="text-gray-600 text-lg">Your money grows not just from your contributions, but from growth on your growth!</p>
      </div>

      <motion.div
        className="space-y-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 p-6 md:p-8">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 p-3 bg-blue-100 rounded-lg text-blue-600">
                <Zap size={24} />
              </div>
              <div>
                <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-2">The Formula</h3>
                <div className="bg-white rounded p-4 font-mono text-sm md:text-base border border-blue-200">
                  <p className="text-gray-800 mb-2">A = P(1 + r/n)<sup>nt</sup> + PMT × [((1 + r/n)<sup>nt</sup> - 1) / (r/n)]</p>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="p-6 border-2 border-gray-200">
            <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-6">Growth Over Time</h3>
            <div className="w-full h-80 md:h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="amount"
                    stroke="#0891b2"
                    strokeWidth={3}
                    dot={false}
                    name="Total Value"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 p-6 md:p-8">
            <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-4">Key Principles</h3>
            <ul className="space-y-3">
              {[
                'Time is your biggest asset - start as early as possible',
                'Consistency matters - regular investments beat lump sums',
                'Higher returns accelerate compounding exponentially',
                'Small amounts grow into large fortunes over time'
              ].map((principle, idx) => (
                <li key={idx} className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-200 text-purple-900 font-bold flex items-center justify-center text-sm">
                    {idx + 1}
                  </span>
                  <span className="text-gray-700">{principle}</span>
                </li>
              ))}
            </ul>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
