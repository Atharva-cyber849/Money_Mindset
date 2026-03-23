import React from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Lightbulb, TrendingUp, Target } from 'lucide-react'

interface Insight {
  text: string
  type?: 'tip' | 'success' | 'recommendation'
}

interface InsightsPanelProps {
  title?: string
  mainInsight: Insight
  additionalInsights?: Insight[]
  highlightColor?: 'teal' | 'blue' | 'green' | 'purple' | 'red' | 'amber'
  showComparison?: boolean
  comparisonText?: string
}

const insightTypeConfig = {
  tip: {
    icon: Lightbulb,
    bgClass: 'bg-blue-50 border-blue-200',
    headerClass: 'text-blue-900',
    textClass: 'text-blue-700',
    accentClass: 'bg-blue-100 text-blue-800'
  },
  success: {
    icon: TrendingUp,
    bgClass: 'bg-green-50 border-green-200',
    headerClass: 'text-green-900',
    textClass: 'text-green-700',
    accentClass: 'bg-green-100 text-green-800'
  },
  recommendation: {
    icon: Target,
    bgClass: 'bg-purple-50 border-purple-200',
    headerClass: 'text-purple-900',
    textClass: 'text-purple-700',
    accentClass: 'bg-purple-100 text-purple-800'
  }
}

export const InsightsPanel: React.FC<InsightsPanelProps> = ({
  title = 'Your Personalized Insights',
  mainInsight,
  additionalInsights = [],
  highlightColor = 'teal',
  showComparison = false,
  comparisonText
}) => {
  const mainType = mainInsight.type || 'success'
  const config = insightTypeConfig[mainType]
  const Icon = config.icon

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.5 } }
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
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">{title}</h2>
      </div>

      <motion.div
        className="space-y-6"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Main Insight */}
        <motion.div variants={itemVariants}>
          <Card className={`${config.bgClass} border-2 overflow-hidden`}>
            <div className="flex gap-4 items-start">
              <div className={`flex-shrink-0 p-3 rounded-lg ${config.accentClass}`}>
                <Icon size={24} />
              </div>
              <div className="flex-grow py-2">
                <h3 className={`${config.headerClass} font-bold text-lg mb-2 capitalize`}>
                  {mainType === 'success' && 'Great News!'}
                  {mainType === 'recommendation' && 'Our Recommendation'}
                  {mainType === 'tip' && 'Pro Tip'}
                </h3>
                <p className={`${config.textClass} leading-relaxed text-base`}>
                  {mainInsight.text}
                </p>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Additional Insights */}
        {additionalInsights.length > 0 && (
          <div className="space-y-4">
            {additionalInsights.map((insight, index) => {
              const insightType = insight.type || 'tip'
              const insightConfig = insightTypeConfig[insightType]
              const InsightIcon = insightConfig.icon

              return (
                <motion.div key={index} variants={itemVariants}>
                  <Card
                    className={`${insightConfig.bgClass} border border-gray-200 p-4 hover:shadow-md transition-shadow`}
                  >
                    <div className="flex gap-3">
                      <div className={`flex-shrink-0 p-2 rounded-md ${insightConfig.accentClass}`}>
                        <InsightIcon size={18} />
                      </div>
                      <p className={`${insightConfig.textClass} text-sm leading-relaxed flex-grow`}>
                        {insight.text}
                      </p>
                    </div>
                  </Card>
                </motion.div>
              )
            })}
          </div>
        )}

        {/* Comparison Section */}
        {showComparison && comparisonText && (
          <motion.div variants={itemVariants}>
            <Card className="bg-gray-50 border-2 border-gray-200 p-6">
              <h4 className="text-gray-900 font-bold mb-3">How You Compare to Others</h4>
              <p className="text-gray-700">{comparisonText}</p>
            </Card>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  )
}
