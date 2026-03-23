'use client'

import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/Card'
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'
import gsap from 'gsap'

interface Stat {
  label: string
  value: string | number
  icon: LucideIcon
  color: 'teal' | 'green' | 'red' | 'cyan' | 'yellow' | 'purple'
  trend?: 'up' | 'down'
  trendValue?: number
}

interface StatisticsPulseProps {
  stats: Stat[]
}

const colorMap = {
  teal: 'text-teal-600 bg-teal-50',
  green: 'text-green-600 bg-green-50',
  red: 'text-red-600 bg-red-50',
  cyan: 'text-cyan-600 bg-cyan-50',
  yellow: 'text-yellow-600 bg-yellow-50',
  purple: 'text-purple-600 bg-purple-50',
}

export const StatisticsPulse: React.FC<StatisticsPulseProps> = ({ stats }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const statRefs = useRef<(HTMLDivElement | null)[]>([])

  useEffect(() => {
    // Animate container fade in
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.5, ease: 'power3.out' }
      )
    }

    // Stagger animate individual stats
    if (statRefs.current.length > 0) {
      gsap.fromTo(
        statRefs.current.filter((ref) => ref !== null),
        { opacity: 0, y: 20, scale: 0.9 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.5,
          ease: 'back.out(1.7)',
          stagger: 0.1,
        }
      )
    }

    // Animate value counters
    statRefs.current.forEach((ref, index) => {
      if (ref) {
        const valueElement = ref.querySelector('[data-value]') as HTMLElement
        if (valueElement && typeof stats[index].value === 'number') {
          const obj = { value: 0 }
          gsap.to(obj, {
            value: stats[index].value,
            duration: 1,
            ease: 'power2.out',
            onUpdate: () => {
              if (valueElement) {
                valueElement.textContent = Math.round(obj.value).toString()
              }
            },
          })
        }
      }
    })
  }, [stats])

  return (
    <div ref={containerRef} className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map((stat, index) => {
        const Icon = stat.icon
        const colorClasses = colorMap[stat.color]

        return (
          <div
            key={index}
            ref={(el) => {
              statRefs.current[index] = el
            }}
            className="p-3"
          >
            <Card className="p-4 text-center h-full">
              <div className={`w-10 h-10 ${colorClasses} rounded-lg mx-auto mb-2 flex items-center justify-center`}>
                <Icon className="w-5 h-5" />
              </div>
              <p className="text-xs text-gray-600 mb-1">{stat.label}</p>
              <div className="flex items-baseline justify-center gap-1">
                <p
                  className="text-2xl font-bold text-gray-800"
                  data-value={typeof stat.value === 'number' ? stat.value : undefined}
                >
                  {typeof stat.value === 'number' ? '0' : stat.value}
                </p>
              </div>
              {stat.trend && stat.trendValue !== undefined && (
                <div
                  className={`flex items-center justify-center gap-1 mt-2 text-xs font-semibold ${stat.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}
                >
                  {stat.trend === 'up' ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  <span>{Math.abs(stat.trendValue)}%</span>
                </div>
              )}
            </Card>
          </div>
        )
      })}
    </div>
  )
}
