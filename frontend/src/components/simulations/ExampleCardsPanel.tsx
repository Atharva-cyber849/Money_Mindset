import React from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { TrendingUp, Zap, AlertCircle } from 'lucide-react'

interface ExampleScenario {
  name: string
  story: string
  outcome: string
  outcomeType: 'positive' | 'neutral' | 'negative'
  metrics?: { label: string; value: string | number }[]
  icon?: React.ReactNode
}

interface ExampleCardsPanelProps {
  title?: string
  description?: string
  examples: ExampleScenario[]
  highlightColor?: 'teal' | 'blue' | 'green' | 'purple' | 'red' | 'amber'
}

const outcomeIcons = {
  positive: <TrendingUp className="w-5 h-5" />,
  neutral: <Zap className="w-5 h-5" />,
  negative: <AlertCircle className="w-5 h-5" />
}

const outcomeBadgeClasses = {
  positive: 'bg-green-100 text-green-800 border-green-300',
  neutral: 'bg-amber-100 text-amber-800 border-amber-300',
  negative: 'bg-red-100 text-red-800 border-red-300'
}

const outcomeCardClasses = {
  positive: 'bg-green-50 border-green-200',
  neutral: 'bg-amber-50 border-amber-200',
  negative: 'bg-red-50 border-red-200'
}

export const ExampleCardsPanel: React.FC<ExampleCardsPanelProps> = ({
  title = 'Real-World Examples',
  description = 'See how different choices lead to different outcomes',
  examples,
  highlightColor = 'teal'
}) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2
      }
    }
  }

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 }
    }
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
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">{title}</h2>
        <p className="text-gray-600 text-lg">{description}</p>
      </div>

      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {examples.map((example, index) => (
          <motion.div key={index} variants={cardVariants}>
            <Card
              className={`border-2 h-full flex flex-col ${outcomeCardClasses[example.outcomeType]} cursor-pointer hover:shadow-lg transition-all duration-300 hover:-translate-y-1`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg md:text-xl font-bold text-gray-900">{example.name}</h3>
                </div>
                <div className="flex-shrink-0 p-2 rounded-lg bg-white">
                  {example.icon || outcomeIcons[example.outcomeType]}
                </div>
              </div>

              {/* Story */}
              <p className="text-gray-700 mb-4 flex-grow">{example.story}</p>

              {/* Metrics */}
              {example.metrics && example.metrics.length > 0 && (
                <div className="mb-4 space-y-2 py-4 border-t border-gray-200">
                  {example.metrics.map((metric, idx) => (
                    <div key={idx} className="flex justify-between items-center text-sm">
                      <span className="text-gray-600">{metric.label}</span>
                      <span className="font-bold text-gray-900">{metric.value}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Outcome Badge */}
              <div className="pt-1">
                <div
                  className={`${outcomeBadgeClasses[example.outcomeType]} border-2 font-semibold px-3 py-2 rounded-lg inline-block text-sm`}
                >
                  {example.outcome}
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  )
}
