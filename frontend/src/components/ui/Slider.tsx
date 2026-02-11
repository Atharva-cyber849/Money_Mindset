'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils'

interface SliderProps {
  min: number
  max: number
  step?: number
  value: number
  onChange: (value: number) => void
  label?: string
  format?: (value: number) => string
  color?: 'blue' | 'green' | 'purple' | 'yellow'
}

export function Slider({
  min,
  max,
  step = 1,
  value,
  onChange,
  label,
  format,
  color = 'blue'
}: SliderProps) {
  const [isDragging, setIsDragging] = useState(false)

  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    yellow: 'bg-yellow-500',
  }

  const thumbColorClasses = {
    blue: 'bg-blue-600 ring-blue-200',
    green: 'bg-green-600 ring-green-200',
    purple: 'bg-purple-600 ring-purple-200',
    yellow: 'bg-yellow-600 ring-yellow-200',
  }

  const percent = ((value - min) / (max - min)) * 100
  const displayValue = format ? format(value) : value.toString()

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-gray-700">{label}</label>
          <span className="text-sm font-semibold text-gray-900">{displayValue}</span>
        </div>
      )}
      
      <div className="relative pt-1">
        {/* Track */}
        <div className="h-2 bg-gray-200 rounded-full relative overflow-hidden">
          {/* Progress */}
          <div
            className={cn(
              'h-full rounded-full transition-all duration-200',
              colorClasses[color]
            )}
            style={{ width: `${percent}%` }}
          />
        </div>

        {/* Slider Input */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          onMouseDown={() => setIsDragging(true)}
          onMouseUp={() => setIsDragging(false)}
          onTouchStart={() => setIsDragging(true)}
          onTouchEnd={() => setIsDragging(false)}
          className="absolute top-0 left-0 w-full h-2 opacity-0 cursor-pointer"
        />

        {/* Thumb */}
        <div
          className={cn(
            'absolute top-1/2 -translate-y-1/2 w-5 h-5 rounded-full shadow-lg transition-all duration-200',
            thumbColorClasses[color],
            isDragging ? 'scale-110 ring-4' : 'scale-100'
          )}
          style={{ left: `calc(${percent}% - 10px)` }}
        />
      </div>

      {/* Min/Max Labels */}
      <div className="flex justify-between mt-1">
        <span className="text-xs text-gray-500">{format ? format(min) : min}</span>
        <span className="text-xs text-gray-500">{format ? format(max) : max}</span>
      </div>
    </div>
  )
}
