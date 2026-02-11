'use client'

import { useEffect, useRef } from 'react'
import gsap from 'gsap'

interface ProgressBarProps {
  percent: number
  color?: 'blue' | 'green' | 'purple' | 'yellow' | 'red'
  height?: string
  showLabel?: boolean
  animate?: boolean
}

export function ProgressBar({ 
  percent, 
  color = 'blue', 
  height = 'h-3',
  showLabel = false,
  animate = true
}: ProgressBarProps) {
  const progressRef = useRef<HTMLDivElement>(null)
  const labelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (progressRef.current && animate) {
      // Animate progress bar fill
      gsap.fromTo(
        progressRef.current,
        { width: '0%' },
        {
          width: `${Math.min(100, Math.max(0, percent))}%`,
          duration: 1,
          ease: 'power2.out',
        }
      )

      // Animate label counter
      if (labelRef.current && showLabel) {
        const obj = { value: 0 }
        gsap.to(obj, {
          value: percent,
          duration: 1,
          ease: 'power2.out',
          onUpdate: () => {
            if (labelRef.current) {
              labelRef.current.textContent = `${obj.value.toFixed(0)}%`
            }
          },
        })
      }
    }
  }, [percent, animate, showLabel])

  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  }

  return (
    <div className="w-full">
      <div className={`w-full bg-gray-200 rounded-full ${height} overflow-hidden relative`}>
        <div
          ref={progressRef}
          className={`${colorClasses[color]} ${height} rounded-full`}
          style={{ width: animate ? '0%' : `${Math.min(100, Math.max(0, percent))}%` }}
        />
      </div>
      {showLabel && (
        <div ref={labelRef} className="text-xs text-gray-600 mt-1 text-right">
          {animate ? '0%' : `${percent.toFixed(0)}%`}
        </div>
      )}
    </div>
  )
}
