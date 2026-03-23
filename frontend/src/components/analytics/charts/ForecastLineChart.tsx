'use client'

import React, { useEffect, useRef } from 'react'
import {
  LineChart,
  Line,
  Area,
  AreaChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
} from 'recharts'
import { Card } from '@/components/ui/Card'
import gsap from 'gsap'

interface ForecastLineChartProps {
  historicalData: Array<{ month: string; value: number }>
  predictions: Array<{
    month: string
    value: number
    low: number
    high: number
  }>
  months: number
}

export const ForecastLineChart: React.FC<ForecastLineChartProps> = ({
  historicalData,
  predictions,
  months,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartContainerRef = useRef<HTMLDivElement>(null)

  // Combine historical and prediction data
  const chartData = [
    ...historicalData.map((d) => ({
      ...d,
      type: 'historical',
      low: d.value,
      high: d.value,
    })),
    ...predictions.map((d) => ({
      ...d,
      type: 'forecast',
    })),
  ]

  useEffect(() => {
    // Animate container fade in
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }
      )
    }

    // Animate chart entrance
    if (chartContainerRef.current) {
      const svgElements = chartContainerRef.current.querySelectorAll('path')
      gsap.fromTo(
        svgElements,
        { opacity: 0, strokeDashoffset: 100 },
        {
          opacity: 1,
          strokeDashoffset: 0,
          duration: 1.2,
          ease: 'power2.out',
          stagger: 0.1,
        }
      )
    }
  }, [])

  const CustomTooltip = (props: any) => {
    const { active, payload, label } = props
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="font-semibold text-gray-800">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index}>
              {entry.name === 'Confidence Range' ? (
                <>
                  <p className="text-xs text-gray-600">
                    Low: ₹{entry.payload.low.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-600">
                    High: ₹{entry.payload.high.toLocaleString()}
                  </p>
                </>
              ) : (
                <p className="text-sm" style={{ color: entry.color }}>
                  {entry.name}: ₹{entry.value.toLocaleString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <Card className="p-6" ref={containerRef}>
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold">Forecast Analysis</h3>
          <p className="text-sm text-gray-600">
            Historical data with {months}-month forecast
          </p>
        </div>

        <div ref={chartContainerRef}>
          <ResponsiveContainer width="100%" height={350}>
            <ComposedChart data={chartData}>
              <defs>
                <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="month"
                stroke="#9ca3af"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke="#9ca3af"
                style={{ fontSize: '12px' }}
                label={{ value: '₹', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '12px' }} />

              {/* Confidence Interval Band */}
              <Area
                type="monotone"
                dataKey="high"
                fill="url(#confidenceGradient)"
                stroke="none"
                isAnimationActive={true}
                animationDuration={1000}
                name="Confidence Range"
              />

              {/* Historical Line */}
              <Line
                type="monotone"
                dataKey="value"
                stroke="#0891B2"
                strokeWidth={2.5}
                dot={false}
                isAnimationActive={true}
                animationDuration={1000}
                name="Historical"
              />

              {/* Forecast Line */}
              <Line
                type="monotone"
                dataKey="value"
                stroke="#06B6D4"
                strokeWidth={2.5}
                strokeDasharray="5 5"
                dot={false}
                isAnimationActive={true}
                animationDuration={1200}
                name="Forecast"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Legend Info */}
        <div className="grid grid-cols-3 gap-2 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-teal-600"></div>
            <span className="text-xs text-gray-700">Historical Data</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-0.5 bg-cyan-500" style={{ opacity: 0.6 }}></div>
            <span className="text-xs text-gray-700">Forecast</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-2 bg-cyan-500"
              style={{ opacity: 0.2 }}
            ></div>
            <span className="text-xs text-gray-700">Confidence Band</span>
          </div>
        </div>
      </div>
    </Card>
  )
}
