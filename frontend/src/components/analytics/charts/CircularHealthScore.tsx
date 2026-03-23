'use client'

import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/Card'
import gsap from 'gsap'

interface CircularHealthScoreProps {
  score: number
  rating: string
  factors?: {
    savings_rate?: number
    expense_ratio?: number
    emergency_fund?: number
  }
}

export const CircularHealthScore: React.FC<CircularHealthScoreProps> = ({
  score,
  rating,
  factors,
}) => {
  const circleRef = useRef<SVGCircleElement>(null)
  const textRef = useRef<HTMLDivElement>(null)
  const valueRef = useRef<HTMLSpanElement>(null)

  const getScoreColor = (s: number) => {
    if (s >= 90) return '#10B981' // green
    if (s >= 75) return '#06B6D4' // cyan
    if (s >= 60) return '#F59E0B' // yellow
    return '#EF4444' // red
  }

  const getRatingText = (s: number) => {
    if (s >= 90) return 'Excellent'
    if (s >= 75) return 'Good'
    if (s >= 60) return 'Fair'
    return 'Poor'
  }

  useEffect(() => {
    // Animate container fade in
    if (textRef.current) {
      gsap.fromTo(
        textRef.current,
        { opacity: 0, scale: 0.8 },
        { opacity: 1, scale: 1, duration: 0.6, ease: 'back.out(1.7)' }
      )
    }

    // Animate score counter
    if (valueRef.current) {
      const obj = { value: 0 }
      gsap.to(obj, {
        value: score,
        duration: 1.2,
        ease: 'power2.out',
        onUpdate: () => {
          if (valueRef.current) {
            valueRef.current.textContent = Math.round(obj.value).toString()
          }
        },
      })
    }

    // Animate circle progress
    if (circleRef.current) {
      const circumference = 2 * Math.PI * 45
      circleRef.current.style.strokeDasharray = `${circumference}`
      circleRef.current.style.strokeDashoffset = `${circumference}`

      gsap.to(circleRef.current, {
        strokeDashoffset: circumference * (1 - score / 100),
        duration: 1.5,
        ease: 'power2.out',
      })
    }
  }, [score])

  const scoreColor = getScoreColor(score)

  return (
    <Card className="p-6 flex flex-col items-center justify-center" ref={textRef}>
      <div className="space-y-4 w-full">
        <div className="text-center">
          <h3 className="text-lg font-bold mb-1">Budget Health Score</h3>
          <p className="text-sm text-gray-600">Overall financial wellness</p>
        </div>

        {/* Circular Progress */}
        <div className="flex justify-center items-center py-4">
          <div className="relative w-40 h-40">
            <svg
              width="160"
              height="160"
              className="transform -rotate-90"
              style={{ filter: `drop-shadow(0 0 8px ${scoreColor}20)` }}
            >
              {/* Background circle */}
              <circle
                cx="80"
                cy="80"
                r="45"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="6"
              />
              {/* Progress circle */}
              <circle
                ref={circleRef}
                cx="80"
                cy="80"
                r="45"
                fill="none"
                stroke={scoreColor}
                strokeWidth="6"
                strokeLinecap="round"
                style={{ transition: 'stroke 0.3s ease' }}
              />
            </svg>

            {/* Center content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span
                ref={valueRef}
                className="text-4xl font-bold"
                style={{ color: scoreColor }}
              >
                {score}
              </span>
              <span className="text-xs text-gray-600">out of 100</span>
            </div>
          </div>
        </div>

        {/* Rating */}
        <div className="text-center">
          <p className="text-sm font-semibold text-gray-700">
            Rating: <span style={{ color: scoreColor }}>{getRatingText(score)}</span>
          </p>
        </div>

        {/* Factors */}
        {factors && (
          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-200">
            {factors.savings_rate !== undefined && (
              <div className="text-center">
                <p className="text-xs text-gray-600">Savings Rate</p>
                <p className="text-sm font-semibold text-teal-600">
                  {factors.savings_rate}%
                </p>
              </div>
            )}
            {factors.expense_ratio !== undefined && (
              <div className="text-center">
                <p className="text-xs text-gray-600">Expense Ratio</p>
                <p className="text-sm font-semibold text-teal-600">
                  {factors.expense_ratio}%
                </p>
              </div>
            )}
            {factors.emergency_fund !== undefined && (
              <div className="text-center">
                <p className="text-xs text-gray-600">Emergency Fund</p>
                <p className="text-sm font-semibold text-teal-600">
                  {factors.emergency_fund} mo.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  )
}
