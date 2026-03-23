'use client'

import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/Card'
import { LucideIcon, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import gsap from 'gsap'

interface InsightCardProps {
  icon: LucideIcon
  title: string
  description: string
  color?: 'teal' | 'green' | 'red' | 'cyan' | 'yellow' | 'blue'
  action?: {
    label: string
    onClick: () => void
  }
  featured?: boolean
}

const colorMap = {
  teal: {
    border: 'border-teal-600',
    bg: 'bg-teal-50',
    text: 'text-teal-600',
    icon: 'text-teal-600',
  },
  green: {
    border: 'border-green-600',
    bg: 'bg-green-50',
    text: 'text-green-600',
    icon: 'text-green-600',
  },
  red: {
    border: 'border-red-600',
    bg: 'bg-red-50',
    text: 'text-red-600',
    icon: 'text-red-600',
  },
  cyan: {
    border: 'border-cyan-600',
    bg: 'bg-cyan-50',
    text: 'text-cyan-600',
    icon: 'text-cyan-600',
  },
  yellow: {
    border: 'border-yellow-600',
    bg: 'bg-yellow-50',
    text: 'text-yellow-600',
    icon: 'text-yellow-600',
  },
  blue: {
    border: 'border-blue-600',
    bg: 'bg-blue-50',
    text: 'text-blue-600',
    icon: 'text-blue-600',
  },
}

export const InsightCard: React.FC<InsightCardProps> = ({
  icon: Icon,
  title,
  description,
  color = 'teal',
  action,
  featured = false,
}) => {
  const cardRef = useRef<HTMLDivElement>(null)
  const borderRef = useRef<HTMLDivElement>(null)

  const colors = colorMap[color]

  useEffect(() => {
    // Animate card entrance
    if (cardRef.current) {
      gsap.fromTo(
        cardRef.current,
        { opacity: 0, x: -30 },
        { opacity: 1, x: 0, duration: 0.6, ease: 'power3.out' }
      )
    }

    // Animate left border
    if (borderRef.current) {
      gsap.fromTo(
        borderRef.current,
        { height: '0%' },
        { height: '100%', duration: 0.8, delay: 0.2, ease: 'power2.out' }
      )
    }
  }, [])

  return (
    <Card
      className={`p-5 relative overflow-hidden ${featured ? 'ring-2 ring-teal-300' : ''}`}
      ref={cardRef}
    >
      {/* Left accent border */}
      <div
        ref={borderRef}
        className={`absolute left-0 top-0 bottom-0 w-1 ${colors.border}`}
        style={{ height: '0%' }}
      ></div>

      <div className="relative z-10 pl-1">
        <div className="flex items-start gap-3 mb-2">
          <div className={`w-10 h-10 ${colors.bg} rounded-lg flex items-center justify-center flex-shrink-0`}>
            <Icon className={`w-5 h-5 ${colors.icon}`} />
          </div>
          <h4 className="font-semibold text-gray-800 text-sm leading-tight pt-1">
            {title}
          </h4>
        </div>

        <p className="text-sm text-gray-600 mb-3 leading-relaxed">{description}</p>

        {action && (
          <button
            onClick={action.onClick}
            className={`inline-flex items-center gap-1 text-sm font-medium ${colors.text} hover:opacity-75 transition-opacity`}
          >
            {action.label}
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </Card>
  )
}
