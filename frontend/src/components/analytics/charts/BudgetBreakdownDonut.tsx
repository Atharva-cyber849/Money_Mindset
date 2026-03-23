'use client'

import React, { useEffect, useRef } from 'react'
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'
import { Card } from '@/components/ui/Card'
import gsap from 'gsap'

interface BudgetBreakdownDonutProps {
  budget_breakdown: { needs: number; wants: number; savings: number }
  actual: { needs: number; wants: number; savings: number }
  compliance: boolean
}

const COLORS = {
  needs: '#0891B2', // teal
  wants: '#8B5CF6', // purple
  savings: '#10B981', // green
}

export const BudgetBreakdownDonut: React.FC<BudgetBreakdownDonutProps> = ({
  budget_breakdown,
  actual,
  compliance,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)

  // Calculate percentages
  const totalActual = actual.needs + actual.wants + actual.savings || 1
  const chartData = [
    {
      name: 'Needs (50%)',
      value: (actual.needs / totalActual) * 100,
      ideal: 50,
      actual: actual.needs,
    },
    {
      name: 'Wants (30%)',
      value: (actual.wants / totalActual) * 100,
      ideal: 30,
      actual: actual.wants,
    },
    {
      name: 'Savings (20%)',
      value: (actual.savings / totalActual) * 100,
      ideal: 20,
      actual: actual.savings,
    },
  ]

  useEffect(() => {
    // Animate container on mount
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }
      )
    }
  }, [])

  const CustomTooltip = (props: any) => {
    const { active, payload } = props
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
          <p className="font-semibold text-gray-800">{data.name}</p>
          <p className="text-sm text-gray-600">
            Current: {data.value.toFixed(1)}%
          </p>
          <p className="text-sm text-gray-600">Target: {data.ideal}%</p>
        </div>
      )
    }
    return null
  }

  return (
    <Card className="p-6" ref={containerRef}>
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold mb-1">Budget Allocation</h3>
          <p className="text-sm text-gray-600">50/30/20 rule breakdown</p>
        </div>

        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="value"
              label={({ name, value }) => `${value.toFixed(0)}%`}
              labelLine={false}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={
                    index === 0
                      ? COLORS.needs
                      : index === 1
                        ? COLORS.wants
                        : COLORS.savings
                  }
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>

        <div
          className={`grid grid-cols-3 gap-3 p-4 rounded-lg ${compliance ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'}`}
        >
          <div className="text-center">
            <p className="text-xs font-semibold text-gray-700">Needs</p>
            <p className="text-lg font-bold text-teal-600">
              {((actual.needs / totalActual) * 100).toFixed(0)}%
            </p>
            <p className="text-xs text-gray-500">Target: 50%</p>
          </div>
          <div className="text-center">
            <p className="text-xs font-semibold text-gray-700">Wants</p>
            <p className="text-lg font-bold text-purple-600">
              {((actual.wants / totalActual) * 100).toFixed(0)}%
            </p>
            <p className="text-xs text-gray-500">Target: 30%</p>
          </div>
          <div className="text-center">
            <p className="text-xs font-semibold text-gray-700">Savings</p>
            <p className="text-lg font-bold text-green-600">
              {((actual.savings / totalActual) * 100).toFixed(0)}%
            </p>
            <p className="text-xs text-gray-500">Target: 20%</p>
          </div>
        </div>

        {compliance && (
          <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="w-2 h-2 bg-green-600 rounded-full"></div>
            <p className="text-sm text-green-700 font-medium">
              ✓ Your budget is aligned with the 50/30/20 rule!
            </p>
          </div>
        )}
        {!compliance && (
          <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="w-2 h-2 bg-yellow-600 rounded-full"></div>
            <p className="text-sm text-yellow-700 font-medium">
              Consider rebalancing your budget to follow the 50/30/20 rule
            </p>
          </div>
        )}
      </div>
    </Card>
  )
}
