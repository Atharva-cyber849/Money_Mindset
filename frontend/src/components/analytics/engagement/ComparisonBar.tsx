'use client'

import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/Card'
import gsap from 'gsap'

interface ComparisonItem {
  label: string
  values: Array<{
    label: string
    value: number
    color: string
  }>
}

interface ComparisonBarProps {
  items: ComparisonItem[]
  maxValue?: number
  title?: string
}

export const ComparisonBar: React.FC<ComparisonBarProps> = ({
  items,
  maxValue = 100,
  title = 'Comparison',
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const itemRefs = useRef<(HTMLDivElement | null)[]>([])

  useEffect(() => {
    // Animate container fade in
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.5, ease: 'power3.out' }
      )
    }

    // Animate bars
    itemRefs.current.forEach((ref, index) => {
      if (ref) {
        const bars = ref.querySelectorAll('[data-bar]')
        gsap.fromTo(
          bars,
          { width: '0%' },
          {
            width: (i) => {
              const widthAttr = (bars[i] as HTMLElement).getAttribute(
                'data-width'
              )
              return widthAttr || '0%'
            },
            duration: 1,
            ease: 'power2.out',
            stagger: 0.05,
            delay: index * 0.1,
          }
        )
      }
    })
  }, [items])

  return (
    <Card className="p-6" ref={containerRef}>
      <div className="space-y-4">
        {title && (
          <div>
            <h3 className="text-lg font-bold">{title}</h3>
          </div>
        )}

        <div className="space-y-4">
          {items.map((item, index) => (
            <div
              key={index}
              ref={(el) => {
                itemRefs.current[index] = el
              }}
              className="space-y-2"
            >
              <p className="text-sm font-semibold text-gray-800">{item.label}</p>
              <div className="space-y-1">
                {item.values.map((val, valIndex) => {
                  const percentage = (val.value / maxValue) * 100
                  return (
                    <div key={valIndex} className="flex items-center gap-2">
                      <div className="w-24 text-xs text-gray-600 truncate">
                        {val.label}
                      </div>
                      <div className="flex-1">
                        <div className="h-6 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full transition-all duration-300 flex items-center justify-end pr-2"
                            style={{ backgroundColor: val.color, width: '0%' }}
                            data-bar
                            data-width={`${percentage}%`}
                          >
                            {percentage >= 15 && (
                              <span className="text-xs font-semibold text-white">
                                {Math.round(val.value)}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="w-12 text-right text-sm font-semibold text-gray-800">
                        {Math.round(val.value)}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="pt-2 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-2 text-xs">
            {items[0]?.values.map((val, index) => (
              <div key={index} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: val.color }}
                ></div>
                <span className="text-gray-600">{val.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  )
}
