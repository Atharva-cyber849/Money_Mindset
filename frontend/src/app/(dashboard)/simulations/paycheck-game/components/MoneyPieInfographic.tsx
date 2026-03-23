import React from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'
import { Wallet, TrendingUp } from 'lucide-react'

interface MoneyPieInfographicProps {
  income?: number
}

export const MoneyPieInfographic: React.FC<MoneyPieInfographicProps> = ({
  income = 50000
}) => {
  const rentExpense = income * 0.30
  const utilitiesExpense = income * 0.10
  const insuranceExpense = income * 0.05
  const discretionary = income * 0.25
  const savings = income * 0.30

  const pieData = [
    { name: 'Essential Expenses', value: rentExpense + utilitiesExpense + insuranceExpense, fill: '#ef4444' },
    { name: 'Discretionary Spending', value: discretionary, fill: '#f59e0b' },
    { name: 'Savings & Investment', value: savings, fill: '#10b981' }
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } }
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
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">The Money Pie</h2>
        <p className="text-gray-600 text-lg">How a typical ₹{(income/100000).toFixed(1)}L income breaks down</p>
      </div>

      <motion.div className="space-y-8" variants={containerVariants} initial="hidden" animate="visible">
        <motion.div variants={itemVariants}>
          <Card className="border-2 border-gray-200 p-6 md:p-8">
            <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-6">Ideal Budget Breakdown (50/30/20 Rule)</h3>
            <div className="w-full h-80 md:h-96">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `₹${(value / 1000).toFixed(0)}K`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 p-6 md:p-8">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 p-3 bg-blue-100 rounded-lg text-blue-600">
                <Wallet size={24} />
              </div>
              <div>
                <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-3">The 50/30/20 Rule</h3>
                <ul className="space-y-2 text-gray-700">
                  <li><strong>50%</strong> for Needs (rent, utilities, food, transport, insurance)</li>
                  <li><strong>30%</strong> for Wants (entertainment, dining, hobbies, shopping)</li>
                  <li><strong>20%</strong> for Savings & Debt Repayment (investments, emergency fund)</li>
                </ul>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-200 p-6 md:p-8">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 p-3 bg-amber-100 rounded-lg text-amber-600">
                <TrendingUp size={24} />
              </div>
              <div>
                <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-2">The Best Strategy?</h3>
                <p className="text-gray-700 leading-relaxed"><strong>"Pay Yourself First"</strong> is the most powerful principle.</p>
              </div>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
