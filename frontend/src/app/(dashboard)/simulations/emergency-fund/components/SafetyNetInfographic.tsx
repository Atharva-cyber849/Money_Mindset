import React from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Shield, AlertTriangle } from 'lucide-react'

interface SafetyNetInfographicProps {
  monthlyExpenses?: number
}

export const SafetyNetInfographic: React.FC<SafetyNetInfographicProps> = ({
  monthlyExpenses = 50000
}) => {
  const months3 = monthlyExpenses * 3
  const months6 = monthlyExpenses * 6
  const months12 = monthlyExpenses * 12

  const containerVariants = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } } }
  const itemVariants = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5 } } }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.5 }} className="w-full">
      <div className="mb-8">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">The Safety Net</h2>
        <p className="text-gray-600 text-lg">Why having an emergency fund is crucial for financial security</p>
      </div>

      <motion.div className="space-y-8" variants={containerVariants} initial="hidden" animate="visible">
        <motion.div variants={itemVariants}>
          <Card className="border-2 border-gray-200 p-6 md:p-8">
            <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-6">Emergency Fund Targets</h3>
            <div className="space-y-4">
              {[
                { months: 3, amount: months3, level: 'Minimum', stress: 'High', color: 'bg-red-100 text-red-800 border-red-300' },
                { months: 6, amount: months6, level: 'Ideal', stress: 'Low', color: 'bg-green-100 text-green-800 border-green-300' }
              ].map((fund, idx) => (
                <div key={idx} className="flex items-center gap-4">
                  <div className="w-24 font-bold text-gray-700">{fund.months} months</div>
                  <div className="flex-grow">
                    <div className="h-12 bg-gray-200 rounded-lg overflow-hidden">
                      <motion.div className={fund.color} initial={{ width: 0 }} animate={{ width: `${(fund.months / 12) * 100}%` }} transition={{ delay: idx * 0.2, duration: 0.8 }} />
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold whitespace-nowrap">₹{(fund.amount / 100000).toFixed(1)}L</p>
                    <p className="text-xs text-gray-600">{fund.level}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="bg-red-50 border-2 border-red-200 p-6">
              <div className="flex gap-3 mb-4">
                <AlertTriangle className="text-red-600 flex-shrink-0" size={24} />
                <h4 className="font-bold text-lg text-red-900">Without Emergency Fund</h4>
              </div>
              <ul className="space-y-2 text-sm text-red-800">
                <li>❌ Job loss = immediate financial crisis</li>
                <li>❌ Medical emergency = credit card debt</li>
                <li>❌ Forced to borrow at high rates</li>
              </ul>
            </Card>

            <Card className="bg-green-50 border-2 border-green-200 p-6">
              <div className="flex gap-3 mb-4">
                <Shield className="text-green-600 flex-shrink-0" size={24} />
                <h4 className="font-bold text-lg text-green-900">With Emergency Fund</h4>
              </div>
              <ul className="space-y-2 text-sm text-green-800">
                <li>✅ Handle unexpected expenses calmly</li>
                <li>✅ No need for expensive loans</li>
                <li>✅ Sleep peacefully at night</li>
              </ul>
            </Card>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
