'use client'

import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/Card'
import gsap from 'gsap'

interface ExampleData {
  label: string
  value: string | number
  icon?: string
  highlight?: boolean
}

interface ExampleShowcaseProps {
  title: string
  description: string
  inputExample: ExampleData[]
  outputExample: ExampleData[]
  color?: 'green' | 'blue' | 'purple' | 'teal'
}

const colorMap = {
  green: { bg: 'bg-green-50', border: 'border-green-200', icon: 'bg-green-100' },
  blue: { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'bg-blue-100' },
  purple: {
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    icon: 'bg-purple-100',
  },
  teal: { bg: 'bg-teal-50', border: 'border-teal-200', icon: 'bg-teal-100' },
}

export const ExampleShowcase: React.FC<ExampleShowcaseProps> = ({
  title,
  description,
  inputExample,
  outputExample,
  color = 'teal',
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLDivElement>(null)
  const outputRef = useRef<HTMLDivElement>(null)
  const arrowRef = useRef<HTMLDivElement>(null)
  const colors = colorMap[color]

  useEffect(() => {
    // Fade in container
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.5, ease: 'power3.out' }
      )
    }

    // Slide in input from left
    if (inputRef.current) {
      gsap.fromTo(
        inputRef.current,
        { opacity: 0, x: -30 },
        { opacity: 1, x: 0, duration: 0.6, delay: 0.2, ease: 'power3.out' }
      )
    }

    // Slide in output from right
    if (outputRef.current) {
      gsap.fromTo(
        outputRef.current,
        { opacity: 0, x: 30 },
        { opacity: 1, x: 0, duration: 0.6, delay: 0.3, ease: 'power3.out' }
      )
    }

    // Animate arrow
    if (arrowRef.current) {
      gsap.fromTo(
        arrowRef.current,
        { scale: 0.5, opacity: 0 },
        {
          scale: 1,
          opacity: 1,
          duration: 0.5,
          delay: 0.4,
          ease: 'back.out(1.7)',
        }
      )
    }
  }, [])

  return (
    <Card className="p-6" ref={containerRef}>
      <div className="space-y-4">
        {/* Header */}
        <div>
          <h3 className="text-lg font-bold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>

        {/* Example Flow */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Input Example */}
          <div
            className={`p-4 rounded-lg border-2 ${colors.border} ${colors.bg}`}
            ref={inputRef}
          >
            <p className="text-xs font-bold text-gray-700 mb-3 uppercase">
              Input Example
            </p>
            <div className="space-y-2">
              {inputExample.map((item, idx) => (
                <div
                  key={idx}
                  className={`flex items-center justify-between p-2 rounded bg-white ${
                    item.highlight ? 'ring-2 ring-cyan-500' : ''
                  }`}
                >
                  <span className="text-xs text-gray-600">{item.label}</span>
                  <span
                    className={`text-sm font-semibold ${
                      item.highlight ? 'text-cyan-600' : 'text-gray-900'
                    }`}
                  >
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Arrow */}
          <div className="flex items-center justify-center" ref={arrowRef}>
            <div className="hidden lg:block text-2xl font-bold text-gray-400">
              →
            </div>
            <div className="lg:hidden w-full h-0.5 bg-gradient-to-r from-transparent via-gray-400 to-transparent"></div>
          </div>

          {/* Output Example */}
          <div
            className={`p-4 rounded-lg border-2 border-green-200 bg-green-50`}
            ref={outputRef}
          >
            <p className="text-xs font-bold text-gray-700 mb-3 uppercase">
              Expected Output
            </p>
            <div className="space-y-2">
              {outputExample.map((item, idx) => (
                <div
                  key={idx}
                  className={`flex items-center justify-between p-2 rounded bg-white ${
                    item.highlight ? 'ring-2 ring-green-500' : ''
                  }`}
                >
                  <span className="text-xs text-gray-600">{item.label}</span>
                  <span
                    className={`text-sm font-semibold ${
                      item.highlight ? 'text-green-600' : 'text-gray-900'
                    }`}
                  >
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
