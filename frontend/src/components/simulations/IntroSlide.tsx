import React from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { LucideIcon } from 'lucide-react'

interface IntroSlideProps {
  title: string
  description: string
  icon: LucideIcon
  whyItMatters: string
  onNext: () => void
  highlightColor?: 'teal' | 'blue' | 'green' | 'purple' | 'red' | 'amber'
}

const colorClasses = {
  teal: 'from-teal-50 to-cyan-50 border-teal-200',
  blue: 'from-blue-50 to-cyan-50 border-blue-200',
  green: 'from-green-50 to-emerald-50 border-green-200',
  purple: 'from-purple-50 to-pink-50 border-purple-200',
  red: 'from-red-50 to-orange-50 border-red-200',
  amber: 'from-amber-50 to-orange-50 border-amber-200'
}

const iconColorClasses = {
  teal: 'text-teal-600',
  blue: 'text-blue-600',
  green: 'text-green-600',
  purple: 'text-purple-600',
  red: 'text-red-600',
  amber: 'text-amber-600'
}

const buttonColorClasses = {
  teal: 'bg-teal-600 hover:bg-teal-700',
  blue: 'bg-blue-600 hover:bg-blue-700',
  green: 'bg-green-600 hover:bg-green-700',
  purple: 'bg-purple-600 hover:bg-purple-700',
  red: 'bg-red-600 hover:bg-red-700',
  amber: 'bg-amber-600 hover:bg-amber-700'
}

export const IntroSlide: React.FC<IntroSlideProps> = ({
  title,
  description,
  icon: Icon,
  whyItMatters,
  onNext,
  highlightColor = 'teal'
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <Card className={`bg-gradient-to-br ${colorClasses[highlightColor]} border-2 p-8 md:p-12`}>
        <div className="flex flex-col items-center text-center">
          {/* Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 100 }}
            className={`mb-6 p-4 bg-white rounded-full ${iconColorClasses[highlightColor]}`}
          >
            <Icon size={48} />
          </motion.div>

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-3xl md:text-4xl font-bold text-gray-900 mb-4"
          >
            {title}
          </motion.h1>

          {/* Description */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-lg md:text-xl text-gray-700 mb-6 max-w-2xl"
          >
            {description}
          </motion.p>

          {/* Why It Matters */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-lg p-4 md:p-6 mb-8 max-w-2xl w-full border-l-4 border-amber-400"
          >
            <p className="text-sm font-semibold text-amber-600 uppercase tracking-wide mb-2">Why This Matters</p>
            <p className="text-gray-700">{whyItMatters}</p>
          </motion.div>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <Button
              onClick={onNext}
              className={`${buttonColorClasses[highlightColor]} text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all`}
            >
              Learn How It Works →
            </Button>
          </motion.div>
        </div>
      </Card>
    </motion.div>
  )
}
