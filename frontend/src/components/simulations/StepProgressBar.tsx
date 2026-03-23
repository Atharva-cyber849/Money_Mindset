import React from 'react'
import { motion } from 'framer-motion'

interface Step {
  number: number
  label: string
}

interface StepProgressBarProps {
  currentStep: number
  totalSteps: number
  steps?: Step[]
  highlightColor?: 'teal' | 'blue' | 'green' | 'purple' | 'red' | 'amber'
}

const colorClasses = {
  teal: {
    completed: 'bg-teal-600',
    current: 'bg-teal-500 ring-2 ring-teal-300',
    upcoming: 'bg-gray-200'
  },
  blue: {
    completed: 'bg-blue-600',
    current: 'bg-blue-500 ring-2 ring-blue-300',
    upcoming: 'bg-gray-200'
  },
  green: {
    completed: 'bg-green-600',
    current: 'bg-green-500 ring-2 ring-green-300',
    upcoming: 'bg-gray-200'
  },
  purple: {
    completed: 'bg-purple-600',
    current: 'bg-purple-500 ring-2 ring-purple-300',
    upcoming: 'bg-gray-200'
  },
  red: {
    completed: 'bg-red-600',
    current: 'bg-red-500 ring-2 ring-red-300',
    upcoming: 'bg-gray-200'
  },
  amber: {
    completed: 'bg-amber-600',
    current: 'bg-amber-500 ring-2 ring-amber-300',
    upcoming: 'bg-gray-200'
  }
}

const textColorClasses = {
  teal: 'text-teal-600',
  blue: 'text-blue-600',
  green: 'text-green-600',
  purple: 'text-purple-600',
  red: 'text-red-600',
  amber: 'text-amber-600'
}

export const StepProgressBar: React.FC<StepProgressBarProps> = ({
  currentStep,
  totalSteps,
  steps,
  highlightColor = 'teal'
}) => {
  const colors = colorClasses[highlightColor]
  const textColor = textColorClasses[highlightColor]

  const progress = ((currentStep - 1) / (totalSteps - 1)) * 100

  return (
    <div className="w-full py-8">
      {/* Compact Progress Bar */}
      <div className="flex items-center justify-between mb-6">
        <div className="text-sm">
          <span className={`${textColor} font-bold text-lg`}>{currentStep}</span>
          <span className="text-gray-500 ml-1">of {totalSteps}</span>
        </div>

        <div className="flex-grow mx-4 relative h-2 bg-gray-200 rounded-full overflow-hidden">
          <motion.div
            className={`h-full ${colors.completed} rounded-full`}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </div>

        <div className="text-sm text-gray-600 font-medium">
          {Math.round(progress)}%
        </div>
      </div>

      {/* Step Indicators */}
      {steps && steps.length > 0 && (
        <div className="flex items-start justify-between relative">
          {/* Connection Lines */}
          <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200 -z-10">
            <motion.div
              className={`h-full ${colors.completed} rounded-full`}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            />
          </div>

          {/* Step Items */}
          {steps.map((step) => {
            const isCompleted = step.number < currentStep
            const isCurrent = step.number === currentStep

            return (
              <motion.div
                key={step.number}
                className="flex flex-col items-center flex-1"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: step.number * 0.05, duration: 0.3 }}
              >
                {/* Circle */}
                <motion.div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center
                    font-bold text-white mb-2
                    ${isCompleted ? colors.completed : ''}
                    ${isCurrent ? colors.current : ''}
                    ${!isCompleted && !isCurrent ? `${colors.upcoming} text-gray-600` : ''}
                    transition-all duration-300
                  `}
                  animate={isCurrent ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ repeat: Infinity, duration: 2 }}
                >
                  {isCompleted ? (
                    <svg
                      className="w-6 h-6"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    step.number
                  )}
                </motion.div>

                {/* Label */}
                <div className="text-center">
                  <p className={`text-xs md:text-sm font-semibold ${isCurrent ? textColor : 'text-gray-600'}`}>
                    {step.label}
                  </p>
                  {isCurrent && (
                    <motion.p
                      className={`text-xs ${textColor} font-bold mt-1`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      In Progress
                    </motion.p>
                  )}
                </div>
              </motion.div>
            )
          })}
        </div>
      )}
    </div>
  )
}
