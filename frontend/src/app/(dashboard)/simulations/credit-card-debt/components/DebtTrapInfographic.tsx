import React from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { AlertTriangle, TrendingUp } from 'lucide-react'

interface DebtTrapInfographicProps {
  initialBalance?: number
}

export const DebtTrapInfographic: React.FC<DebtTrapInfographicProps> = ({
  initialBalance = 100000
}) => {
  const containerVariants = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } } }
  const itemVariants = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5 } } }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.5 }} className="w-full">
      <div className="mb-8">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">The Debt Trap</h2>
        <p className="text-gray-600 text-lg">How credit card debt compounds and destroys wealth</p>
      </div>

      <motion.div className="space-y-8" variants={containerVariants} initial="hidden" animate="visible">
        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-200 p-6 md:p-8">
            <div className="flex items-start gap-4">
              <AlertTriangle className="text-red-600 flex-shrink-0" size={28} />
              <div>
                <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-3">How Debt Traps You</h3>
                <ul className="space-y-2 text-gray-700">
                  <li>❌ Interest compounds daily, not periodically</li>
                  <li>❌ Minimum payments trap you for years</li>
                  <li>❌ Credit score damage hurts future finances</li>
                  <li>❌ Psychological burden of debt</li>
                  <li>❌ Opportunity cost: money for debt = no investments</li>
                </ul>
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 p-6 md:p-8">
            <div className="flex items-start gap-4">
              <TrendingUp className="text-green-600 flex-shrink-0" size={28} />
              <div>
                <h3 className="font-bold text-lg md:text-xl text-gray-900 mb-2">The Path to Freedom</h3>
                <p className="text-gray-700 leading-relaxed mb-3">
                  Credit card debt is one of the fastest ways to financial destruction, but also fastest to fix if you act decisively.
                </p>
                <ul className="space-y-2 text-gray-700 ml-4">
                  <li>✓ Pay more than minimum whenever possible</li>
                  <li>✓ Stop using the card until paid off</li>
                  <li>✓ Create a payment plan</li>
                </ul>
              </div>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
