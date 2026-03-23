import React from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { TrendingUp } from 'lucide-react'

interface BudgetFrameworkInfographicProps {
  monthlyIncome?: number
}

export const BudgetFrameworkInfographic: React.FC<BudgetFrameworkInfographicProps> = ({
  monthlyIncome = 100000
}) => {
  const needs = monthlyIncome * 0.50
  const wants = monthlyIncome * 0.30
  const savings = monthlyIncome * 0.20

  const containerVariants = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } } }
  const itemVariants = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5 } } }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.5 }} className="w-full">
      <div className="mb-8">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">The 50/30/20 Rule</h2>
        <p className="text-gray-600 text-lg">A proven framework for budgeting that works for everyone</p>
      </div>

      <motion.div className="space-y-8" variants={containerVariants} initial="hidden" animate="visible">
        <motion.div variants={itemVariants}>
          <Card className="border-2 border-gray-200 p-6 md:p-8">
            <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-6">Your ₹{(monthlyIncome/100000).toFixed(1)}L Monthly Income</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-full">
                  <div className="flex justify-between mb-2">
                    <span className="font-bold text-gray-900">50% - NEEDS</span>
                    <span className="font-bold text-red-600">₹{(needs/1000).toFixed(0)}K</span>
                  </div>
                  <div className="h-16 bg-red-100 rounded-lg border-2 border-red-300 flex items-center justify-center text-sm font-semibold text-red-900">
                    Rent, Food, Utilities, Insurance, Transport
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-full">
                  <div className="flex justify-between mb-2">
                    <span className="font-bold text-gray-900">30% - WANTS</span>
                   <span className="font-bold text-amber-600">₹{(wants/1000).toFixed(0)}K</span>
                  </div>
                  <div className="h-16 bg-amber-100 rounded-lg border-2 border-amber-300 flex items-center justify-center text-sm font-semibold text-amber-900">
                    Entertainment, Dining, Hobbies, Shopping
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-full">
                  <div className="flex justify-between mb-2">
                    <span className="font-bold text-gray-900">20% - SAVINGS & GOALS</span>
                    <span className="font-bold text-green-600">₹{(savings/1000).toFixed(0)}K</span>
                  </div>
                  <div className="h-16 bg-green-100 rounded-lg border-2 border-green-300 flex items-center justify-center text-sm font-semibold text-green-900">
                    Emergency Fund, Investments, Retirement
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 p-6 md:p-8">
            <div className="flex items-start gap-4">
              <TrendingUp className="text-purple-600 flex-shrink-0" size={28} />
              <div>
                <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-2">Why This Framework Works</h3>
                <ul className="space-y-2 text-gray-700">
                  <li>✓ <strong>Simple:</strong> Only 3 categories to track</li>
                  <li>✓ <strong>Balanced:</strong> You can save AND enjoy life</li>
                  <li>✓ <strong>Scalable:</strong> Works for any income level</li>
                  <li>✓ <strong>Proven:</strong> Millions use it successfully</li>
                  <li>✓ <strong>Flexible:</strong> Can adjust for your situation</li>
                </ul>
              </div>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
