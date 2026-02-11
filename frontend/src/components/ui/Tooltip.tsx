'use client'

import { useState, useRef, useEffect, ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { cn } from '@/lib/utils'

export interface TooltipProps {
  content: ReactNode
  children: ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
  className?: string
}

export function Tooltip({
  content,
  children,
  position = 'top',
  delay = 500,
  className,
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [coords, setCoords] = useState({ top: 0, left: 0 })
  const timeoutRef = useRef<NodeJS.Timeout>()
  const triggerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  const updatePosition = () => {
    if (!triggerRef.current) return

    const rect = triggerRef.current.getBoundingClientRect()
    const tooltipOffset = 8

    let top = 0
    let left = 0

    switch (position) {
      case 'top':
        top = rect.top - tooltipOffset
        left = rect.left + rect.width / 2
        break
      case 'bottom':
        top = rect.bottom + tooltipOffset
        left = rect.left + rect.width / 2
        break
      case 'left':
        top = rect.top + rect.height / 2
        left = rect.left - tooltipOffset
        break
      case 'right':
        top = rect.top + rect.height / 2
        left = rect.right + tooltipOffset
        break
    }

    setCoords({ top, left })
  }

  const handleMouseEnter = () => {
    updatePosition()
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true)
    }, delay)
  }

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setIsVisible(false)
  }

  const positionClasses = {
    top: '-translate-x-1/2 -translate-y-full',
    bottom: '-translate-x-1/2',
    left: '-translate-y-1/2 -translate-x-full',
    right: '-translate-y-1/2',
  }

  const arrowClasses = {
    top: 'bottom-0 left-1/2 -translate-x-1/2 translate-y-full border-t-text-primary',
    bottom: 'top-0 left-1/2 -translate-x-1/2 -translate-y-full border-b-text-primary',
    left: 'right-0 top-1/2 -translate-y-1/2 translate-x-full border-l-text-primary',
    right: 'left-0 top-1/2 -translate-y-1/2 -translate-x-full border-r-text-primary',
  }

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="inline-block"
      >
        {children}
      </div>

      {isVisible &&
        typeof window !== 'undefined' &&
        createPortal(
          <div
            className={cn(
              'fixed z-50 pointer-events-none',
              'animate-fade-in'
            )}
            style={{
              top: `${coords.top}px`,
              left: `${coords.left}px`,
            }}
          >
            <div
              className={cn(
                'relative bg-text-primary text-white text-sm px-3 py-2 rounded-lg shadow-xl max-w-[200px]',
                positionClasses[position],
                className
              )}
            >
              {content}
              <div
                className={cn(
                  'absolute w-0 h-0 border-4 border-transparent',
                  arrowClasses[position]
                )}
              />
            </div>
          </div>,
          document.body
        )}
    </>
  )
}

// Simple inline tooltip (no portal)
export function SimpleTooltip({ content, children, className }: Omit<TooltipProps, 'position' | 'delay'>) {
  return (
    <div className="group relative inline-block">
      {children}
      <div
        className={cn(
          'absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 text-sm text-white bg-text-primary rounded-lg shadow-xl',
          'opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200',
          'pointer-events-none max-w-[200px] z-50',
          className
        )}
      >
        {content}
        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-text-primary" />
      </div>
    </div>
  )
}
