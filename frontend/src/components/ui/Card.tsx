'use client'

import { ReactNode, useRef, useEffect } from 'react'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import gsap from 'gsap'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  hover?: boolean
  animate?: boolean
}

export function Card({ children, className, hover = false, animate = false, ...props }: CardProps) {
  const cardRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (cardRef.current && animate) {
      gsap.fromTo(
        cardRef.current,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          ease: 'power3.out',
        }
      )
    }

    // Hover animation
    if (cardRef.current && hover) {
      const element = cardRef.current

      const handleMouseEnter = () => {
        gsap.to(element, {
          y: -5,
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
          duration: 0.3,
          ease: 'power2.out',
        })
      }

      const handleMouseLeave = () => {
        gsap.to(element, {
          y: 0,
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
          duration: 0.3,
          ease: 'power2.out',
        })
      }

      element.addEventListener('mouseenter', handleMouseEnter)
      element.addEventListener('mouseleave', handleMouseLeave)

      return () => {
        element.removeEventListener('mouseenter', handleMouseEnter)
        element.removeEventListener('mouseleave', handleMouseLeave)
      }
    }
  }, [hover, animate])

  return (
    <div
      ref={cardRef}
      className={cn(
        'bg-white rounded-xl shadow-sm border border-gray-200 p-6 transition-shadow',
        hover && 'cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: LucideIcon
  iconColor?: string
  trend?: 'up' | 'down' | 'neutral'
  animate?: boolean
}

export function StatCard({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  iconColor = 'bg-blue-500',
  trend = 'neutral',
  animate = false
}: StatCardProps) {
  const iconRef = useRef<HTMLDivElement>(null)
  const valueRef = useRef<HTMLParagraphElement>(null)

  useEffect(() => {
    if (animate) {
      // Animate icon with rotation and scale
      if (iconRef.current) {
        gsap.fromTo(
          iconRef.current,
          { scale: 0, rotation: -180, opacity: 0 },
          {
            scale: 1,
            rotation: 0,
            opacity: 1,
            duration: 0.6,
            delay: 0.2,
            ease: 'back.out(1.7)',
          }
        )
      }

      // Animate value with counter effect
      if (valueRef.current) {
        const numericValue = typeof value === 'string' 
          ? parseFloat(value.replace(/[^0-9.-]/g, ''))
          : value
        
        if (!isNaN(numericValue)) {
          const obj = { value: 0 }
          gsap.to(obj, {
            value: numericValue,
            duration: 1,
            delay: 0.3,
            ease: 'power2.out',
            onUpdate: () => {
              if (valueRef.current) {
                const formatted = typeof value === 'string' && value.includes('$')
                  ? `$${obj.value.toFixed(0)}`
                  : obj.value.toFixed(0)
                valueRef.current.textContent = formatted
              }
            },
          })
        }
      }
    }
  }, [animate, value])

  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600',
  }

  return (
    <Card hover animate={animate}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p ref={valueRef} className="text-2xl font-bold text-gray-900">{value}</p>
          {change !== undefined && (
            <p className={cn('text-sm font-medium mt-1', trendColors[trend])}>
              {change > 0 ? '+' : ''}{change}%
            </p>
          )}
        </div>
        <div ref={iconRef} className={cn('p-3 rounded-lg', iconColor)}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </Card>
  )
}
