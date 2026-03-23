'use client'

import React, { useEffect, useRef, useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { Card } from '@/components/ui/Card'
import gsap from 'gsap'

interface DistributionBellCurveProps {
  percentiles: { p10: number; p25: number; p50: number; p75: number; p90: number }
  probability: { profit: number; double: number; loss: number }
}

// Generate bell curve data from percentiles
const generateBellCurveData = (percentiles: Record<string, number>) => {
  const values = Object.values(percentiles).sort((a, b) => a - b)
  const min = values[0]
  const max = values[values.length - 1]
  const mean = (min + max) / 2
  const stdDev = (max - min) / 4

  const data = []
  const step = (max - min) / 50

  for (let x = min; x <= max; x += step) {
    const z = (x - mean) / stdDev
    const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) * Math.exp(-(z * z) / 2)
    data.push({
      value: Math.round(x),
      probability: y * 1000, // Scale for visibility
      z,
    })
  }

  return data
}

export const DistributionBellCurve: React.FC<DistributionBellCurveProps> = ({
  percentiles,
  probability,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<HTMLDivElement>(null)
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null)

  const bellCurveData = generateBellCurveData(percentiles)

  useEffect(() => {
    // Animate container fade in
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }
      )
    }

    // Animate chart area
    if (chartRef.current) {
      const area = chartRef.current.querySelector('path')
      if (area) {
        gsap.fromTo(
          area,
          { opacity: 0 },
          { opacity: 1, duration: 1, ease: 'power2.out' }
        )
      }
    }
  }, [])

  const CustomTooltip = (props: any) => {
    const { active, payload } = props
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-2 border border-gray-300 rounded shadow-lg">
          <p className="text-sm font-semibold">
            ₹{payload[0].payload.value.toLocaleString()}
          </p>
          <p className="text-xs text-gray-600">
            Probability: {(payload[0].value / 10).toFixed(2)}%
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <Card className="p-6" ref={containerRef}>
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold">Outcome Distribution</h3>
          <p className="text-sm text-gray-600">1000 simulations</p>
        </div>

        {/* Bell Curve Chart */}
        <div ref={chartRef} className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={bellCurveData}
              margin={{ top: 0, right: 20, left: 0, bottom: 20 }}
            >
              <defs>
                <linearGradient id="bellGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0891B2" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#0891B2" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="value"
                label={{ value: 'Portfolio Value (₹)', position: 'bottom', offset: 10 }}
                tick={{ fontSize: 12 }}
              />
              <YAxis hide label={{ value: 'Probability', angle: -90, position: 'insideLeft' }} />
              <Tooltip content={<CustomTooltip />} />

              {/* Percentile Reference Lines */}
              <ReferenceLine
                x={percentiles.p10}
                stroke="#EF4444"
                strokeDasharray="5"
                label={{ value: `P10: ₹${percentiles.p10.toLocaleString()}`, position: 'top', fill: '#EF4444', fontSize: 11 }}
              />
              <ReferenceLine
                x={percentiles.p25}
                stroke="#F59E0B"
                strokeDasharray="5"
                label={{ value: `P25`, position: 'top', fill: '#F59E0B', fontSize: 11 }}
              />
              <ReferenceLine
                x={percentiles.p50}
                stroke="#0891B2"
                strokeDasharray="3"
                label={{ value: `Median: ₹${percentiles.p50.toLocaleString()}`, position: 'top', fill: '#0891B2', fontSize: 11, offset: 10 }}
              />
              <ReferenceLine
                x={percentiles.p75}
                stroke="#10B981"
                strokeDasharray="5"
                label={{ value: `P75`, position: 'top', fill: '#10B981', fontSize: 11 }}
              />
              <ReferenceLine
                x={percentiles.p90}
                stroke="#10B981"
                strokeDasharray="5"
                label={{ value: `P90: ₹${percentiles.p90.toLocaleString()}`, position: 'top', fill: '#10B981', fontSize: 11 }}
              />

              {/* Bell Curve Area */}
              <Area
                type="monotone"
                dataKey="probability"
                fill="url(#bellGradient)"
                stroke="#0891B2"
                strokeWidth={2}
                isAnimationActive={true}
                animationDuration={1000}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Percentile Summary */}
        <div className="grid grid-cols-3 gap-2 text-center text-sm">
          <div className="p-2 bg-red-50 rounded-lg border border-red-200">
            <p className="text-xs text-gray-600">P10 (Pessimistic)</p>
            <p className="font-semibold text-red-600">
              ₹{percentiles.p10.toLocaleString()}
            </p>
          </div>
          <div className="p-2 bg-teal-50 rounded-lg border border-teal-200">
            <p className="text-xs text-gray-600">P50 (Median)</p>
            <p className="font-semibold text-teal-600">
              ₹{percentiles.p50.toLocaleString()}
            </p>
          </div>
          <div className="p-2 bg-green-50 rounded-lg border border-green-200">
            <p className="text-xs text-gray-600">P90 (Optimistic)</p>
            <p className="font-semibold text-green-600">
              ₹{percentiles.p90.toLocaleString()}
            </p>
          </div>
        </div>

        {/* Probability Cards */}
        <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-200">
          <button
            onClick={() => setSelectedRegion(selectedRegion === 'profit' ? null : 'profit')}
            className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
              selectedRegion === 'profit'
                ? 'bg-green-50 border-green-600'
                : 'bg-green-50 border-green-200'
            }`}
          >
            <p className="text-xs text-gray-600">Profit</p>
            <p className="text-lg font-bold text-green-600">{probability.profit}%</p>
          </button>
          <button
            onClick={() => setSelectedRegion(selectedRegion === 'double' ? null : 'double')}
            className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
              selectedRegion === 'double'
                ? 'bg-cyan-50 border-cyan-600'
                : 'bg-cyan-50 border-cyan-200'
            }`}
          >
            <p className="text-xs text-gray-600">Double</p>
            <p className="text-lg font-bold text-cyan-600">{probability.double}%</p>
          </button>
          <button
            onClick={() => setSelectedRegion(selectedRegion === 'loss' ? null : 'loss')}
            className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
              selectedRegion === 'loss'
                ? 'bg-red-50 border-red-600'
                : 'bg-red-50 border-red-200'
            }`}
          >
            <p className="text-xs text-gray-600">Loss</p>
            <p className="text-lg font-bold text-red-600">{probability.loss}%</p>
          </button>
        </div>
      </div>
    </Card>
  )
}
