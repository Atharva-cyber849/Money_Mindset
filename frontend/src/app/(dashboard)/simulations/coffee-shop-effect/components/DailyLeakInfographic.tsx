import React from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { AlertTriangle, TrendingUp } from 'lucide-react'

interface DailyLeakInfographicProps {
  dailyAmount?: number
}

export const DailyLeakInfographic: React.FC<DailyLeakInfographicProps> = ({
  dailyAmount = 100
}) => {
  const monthlyAmount = dailyAmount * 30
  const annualAmount = dailyAmount * 365

  const comparisonData = [
    { period: '1 Year', amount: annualAmount },
    { period: '5 Years', amount: annualAmount * 5 },
    { period: '10 Years', amount: annualAmount * 10 }
  ]

  const containerVariants = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } } }
  const itemVariants = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5 } } }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.5 }} className="w-full">
      <div className="mb-8">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">The Daily Leak Effect</h2>
        <p className="text-gray-600 text-lg">How small daily expenses add up to big money over time</p>
      </div>

      <motion.div className="space-y-8" variants={containerVariants} initial="hidden" animate="visible">
        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-200 p-6 md:p-8">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 p-3 bg-red-100 rounded-lg text-red-600"><AlertTriangle size={24} /></div>
              <div>
                <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-2">Your Daily ₹{dailyAmount} Habit</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
                  <div className="bg-white rounded p-3 border border-red-200">
                    <p className="text-xs text-gray-600">Monthly</p>
                    <p className="text-lg font-bold text-red-600">₹{(monthlyAmount/1000).toFixed(0)}K</p>
                  </div>
                  <div className="bg-white rounded p-3 border border-red-200">
                    <p className="text-xs text-gray-600">Yearly</p>
                    <p className="text-lg font-bold text-red-600">₹{(annualAmount/100000).toFixed(1)}L</p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="p-6 border-2 border-gray-200">
            <h3 className="font-bold text-lg mb-6">Cumulative Over Time</h3>
            <div className="w-full h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={comparisonData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => `₹${(value / 100000).toFixed(1)}L`} />
                  <Bar dataKey="amount" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-teal-50 to-cyan-50 border-2 border-teal-200 p-6 md:p-8">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 p-3 bg-teal-100 rounded-lg text-teal-600"><TrendingUp size={24} /></div>
              <div>
                <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-2">The Real Cost</h3>
                <p className="text-gray-700">This isn't about never enjoying - it's about awareness. Small changes compound into serious wealth.</p>
              </div>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
