'use client'

import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/Card'
import { AlertCircle, CheckCircle } from 'lucide-react'
import gsap from 'gsap'

interface ConfidenceGaugeProps {
  confidence: number
  showWarning?: boolean
}

export const ConfidenceGauge: React.FC<ConfidenceGaugeProps> = ({
  confidence,
  showWarning = false,
}) => {
  const barRef = useRef<HTMLDivElement>(null)
  const percentageRef = useRef<HTMLSpanElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const getConfidenceColor = (conf: number) => {
    if (conf >= 70) return '#10B981' // green
    if (conf >= 40) return '#F59E0B' // yellow
    return '#EF4444' // red
  }

  const getConfidenceLabel = (conf: number) => {
    if (conf >= 70) return 'High Confidence'
    if (conf >= 40) return 'Medium Confidence'
    return 'Low Confidence'
  }

  useEffect(() => {
    // Animate container fade in
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' }
      )
    }

    // Animate gauge bar
    if (barRef.current) {
      gsap.fromTo(
        barRef.current,
        { width: '0%' },
        {
          width: `${confidence}%`,
          duration: 1.2,
          ease: 'power2.out',
        }
      )
    }

    // Animate percentage counter
    if (percentageRef.current) {
      const obj = { value: 0 }
      gsap.to(obj, {
        value: confidence,
        duration: 1,
        ease: 'power2.out',
        onUpdate: () => {
          if (percentageRef.current) {
            percentageRef.current.textContent = Math.round(obj.value).toString()
          }
        },
      })
    }
  }, [confidence])

  const gaugeColor = getConfidenceColor(confidence)

  return (
    <Card className="p-6" ref={containerRef}>
      <div className="space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-bold">Classification Confidence</h3>
            <p className="text-sm text-gray-600">
              {getConfidenceLabel(confidence)}
            </p>
          </div>
          {confidence >= 70 ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <AlertCircle className="w-5 h-5 text-yellow-600" />
          )}
        </div>

        {/* Gauge Container */}
        <div className="space-y-2">
          {/* Background bar */}
          <div className="w-full h-6 bg-gray-200 rounded-full overflow-hidden">
            {/* Progress bar */}
            <div
              ref={barRef}
              className="h-full transition-all duration-300 rounded-full"
              style={{
                backgroundColor: gaugeColor,
                width: '0%',
              }}
            ></div>
          </div>

          {/* Percentage display */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Confidence Level</span>
            <div className="flex items-center gap-1">
              <span
                ref={percentageRef}
                className="text-2xl font-bold"
                style={{ color: gaugeColor }}
              >
                0
              </span>
              <span className="text-lg text-gray-600">%</span>
            </div>
          </div>
        </div>

        {/* Confidence ranges */}
        <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-200">
          <div className="text-center">
            <div className="w-2 h-2 bg-red-500 rounded-full mx-auto mb-1"></div>
            <p className="text-xs text-gray-600">Low (0-40%)</p>
          </div>
          <div className="text-center">
            <div className="w-2 h-2 bg-yellow-500 rounded-full mx-auto mb-1"></div>
            <p className="text-xs text-gray-600">Medium (40-70%)</p>
          </div>
          <div className="text-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mx-auto mb-1"></div>
            <p className="text-xs text-gray-600">High (70%+)</p>
          </div>
        </div>

        {/* Warning for low confidence */}
        {showWarning && confidence < 70 && (
          <div className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-yellow-800">
                Review Recommended
              </p>
              <p className="text-xs text-yellow-700 mt-1">
                This classification has lower confidence. Consider verifying the
                category manually.
              </p>
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}
