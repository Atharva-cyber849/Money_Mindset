'use client'

import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/Card'
import gsap from 'gsap'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface Segment {
  label: string
  percentage: number
  color: string
  description?: string
}

interface ConceptInfographicProps {
  title: string
  subtitle?: string
  type: '50-30-20' | 'percentages' | 'bars' | 'circular'
  segments: Segment[]
}

export const ConceptInfographic: React.FC<ConceptInfographicProps> = ({
  title,
  subtitle,
  type,
  segments,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<HTMLDivElement>(null)
  const legendRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }
      )
    }

    if (chartRef.current) {
      gsap.fromTo(
        chartRef.current,
        { opacity: 0, scale: 0.9 },
        { opacity: 1, scale: 1, duration: 0.5, ease: 'power2.out' }
      )
    }

    if (legendRef.current) {
      const items = legendRef.current.querySelectorAll('[data-legend-item]')
      gsap.fromTo(
        items,
        { opacity: 0, x: -15 },
        {
          opacity: 1,
          x: 0,
          duration: 0.5,
          stagger: 0.08,
          ease: 'power2.out',
        }
      )
    }
  }, [])

  const renderBudgetPie = () => {
    return (
      <div className="h-52 w-52 mx-auto" ref={chartRef}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={segments}
              dataKey="percentage"
              nameKey="label"
              cx="50%"
              cy="50%"
              outerRadius={74}
              innerRadius={0}
              stroke="#ffffff"
              strokeWidth={2}
              label={({ value }) => `${value}%`}
              labelLine={false}
            >
              {segments.map((segment, idx) => (
                <Cell key={`segment-${idx}`} fill={segment.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
    )
  }

  const renderBars = () => {
    return (
      <div className="flex items-end gap-4 h-40 justify-center">
        {segments.map((segment, idx) => (
          <div
            key={idx}
            className="flex flex-col items-center gap-2 flex-1"
            style={{ maxWidth: '100px' }}
          >
            <div className="relative w-full h-32 rounded-t-lg overflow-hidden bg-gray-100">
              <div
                className="w-full rounded-t-lg transition-all duration-500"
                style={{
                  height: `${segment.percentage}%`,
                  backgroundColor: segment.color,
                }}
              />
            </div>
            <div className="text-center">
              <p className="text-xs font-bold text-gray-900">
                {segment.percentage}%
              </p>
              <p className="text-xs text-gray-600">{segment.label}</p>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderPercentages = () => {
    return (
      <div className="space-y-3">
        {segments.map((segment, idx) => (
          <div key={idx} className="flex items-center gap-3">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-semibold text-gray-900">
                  {segment.label}
                </span>
                <span className="text-sm font-bold" style={{ color: segment.color }}>
                  {segment.percentage}%
                </span>
              </div>
              <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${segment.percentage}%`,
                    backgroundColor: segment.color,
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <Card className="p-6" ref={containerRef}>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h3 className="text-lg font-bold text-gray-900">{title}</h3>
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>

        {/* Visualization */}
        <div className="flex justify-center">
          {type === '50-30-20' && renderBudgetPie()}
          {type === 'bars' && renderBars()}
          {(type === 'percentages' || type === 'circular') && renderPercentages()}
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3" ref={legendRef}>
          {segments.map((segment, idx) => (
            <div
              key={idx}
              data-legend-item
              className="flex items-center gap-2 p-2 rounded-lg bg-gray-50"
            >
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: segment.color }}
              />
              <div className="min-w-0">
                <p className="text-xs font-semibold text-gray-900 truncate">
                  {segment.label}
                </p>
                {segment.description && (
                  <p className="text-xs text-gray-600 truncate">
                    {segment.description}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}
