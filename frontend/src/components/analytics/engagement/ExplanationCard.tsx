'use client'

import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/Card'
import { LucideIcon } from 'lucide-react'
import gsap from 'gsap'

interface ExplanationCardProps {
  icon: LucideIcon
  title: string
  description: string
  keyPoints: string[]
  color?: 'teal' | 'green' | 'blue' | 'purple' | 'orange'
  example?: string
}

const colorMap = {
  teal: { bg: 'bg-teal-50', border: 'border-teal-200', text: 'text-teal-700' },
  green: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700' },
  blue: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700' },
  purple: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700' },
  orange: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700' },
}

export const ExplanationCard: React.FC<ExplanationCardProps> = ({
  icon: Icon,
  title,
  description,
  keyPoints,
  color = 'teal',
  example,
}) => {
  const cardRef = useRef<HTMLDivElement>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const colors = colorMap[color]

  useEffect(() => {
    // Fade in card
    if (cardRef.current) {
      gsap.fromTo(
        cardRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }
      )
    }

    // Stagger list items
    if (listRef.current) {
      const items = listRef.current.querySelectorAll('li')
      gsap.fromTo(
        items,
        { opacity: 0, x: -20 },
        {
          opacity: 1,
          x: 0,
          duration: 0.5,
          ease: 'power2.out',
          stagger: 0.1,
        }
      )
    }
  }, [])

  return (
    <Card
      className={`p-6 border-l-4 ${colors.border} ${colors.bg}`}
      ref={cardRef}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start gap-3">
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${colors.bg}`}
          >
            <Icon className={`w-5 h-5 ${colors.text}`} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-700 mt-1">{description}</p>
          </div>
        </div>

        {/* Key Points */}
        <div ref={listRef}>
          <p className="text-xs font-semibold text-gray-600 mb-2 uppercase">
            Key Points
          </p>
          <ul className="space-y-2">
            {keyPoints.map((point, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <span
                  className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${colors.text}`}
                ></span>
                <span className="text-gray-700">{point}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Example */}
        {example && (
          <div className={`p-3 rounded-lg bg-white border ${colors.border}`}>
            <p className="text-xs font-semibold text-gray-600 mb-1">Example:</p>
            <p className="text-sm text-gray-700 italic">{example}</p>
          </div>
        )}
      </div>
    </Card>
  )
}
