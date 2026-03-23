'use client'

import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/Card'
import { LucideIcon } from 'lucide-react'
import gsap from 'gsap'

interface Step {
  number: number
  title: string
  description: string
  icon: LucideIcon
}

interface HowItWorksProps {
  title: string
  subtitle?: string
  steps: Step[]
  color?: 'teal' | 'green' | 'blue' | 'purple'
}

const colorMap = {
  teal: '#0891B2',
  green: '#10B981',
  blue: '#3B82F6',
  purple: '#8B5CF6',
}

export const HowItWorks: React.FC<HowItWorksProps> = ({
  title,
  subtitle,
  steps,
  color = 'teal',
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const stepRefs = useRef<(HTMLDivElement | null)[]>([])
  const accentColor = colorMap[color]

  useEffect(() => {
    // Animate container
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.5, ease: 'power3.out' }
      )
    }

    // Animate steps with stagger
    stepRefs.current.forEach((ref, index) => {
      if (ref) {
        gsap.fromTo(
          ref,
          { opacity: 0, y: 30 },
          {
            opacity: 1,
            y: 0,
            duration: 0.6,
            delay: index * 0.15,
            ease: 'power3.out',
          }
        )
      }
    })
  }, [])

  return (
    <Card className="p-6" ref={containerRef}>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h3 className="text-xl font-bold text-gray-900">{title}</h3>
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>

        {/* Steps */}
        <div>
          {steps.map((step, index) => {
            const Icon = step.icon
            const isLast = index === steps.length - 1

            return (
              <div key={step.number}>
                <div
                  className="flex gap-4 pb-8"
                  ref={(el) => {
                    stepRefs.current[index] = el
                  }}
                >
                  {/* Number Circle */}
                  <div className="flex flex-col items-center">
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0 shadow-md"
                      style={{ backgroundColor: accentColor }}
                    >
                      {step.number}
                    </div>
                    {!isLast && (
                      <div
                        className="w-0.5 h-12 my-2"
                        style={{ backgroundColor: accentColor, opacity: 0.3 }}
                      ></div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 pt-1">
                    <div className="flex items-start gap-3 mb-2">
                      <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 opacity-75"
                        style={{ backgroundColor: accentColor + '20' }}
                      >
                        <Icon
                          className="w-4 h-4"
                          style={{ color: accentColor }}
                        />
                      </div>
                      <h4 className="font-semibold text-gray-900">
                        {step.title}
                      </h4>
                    </div>
                    <p className="text-sm text-gray-600 ml-11">
                      {step.description}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </Card>
  )
}
