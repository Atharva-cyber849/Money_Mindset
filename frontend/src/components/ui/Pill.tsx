'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { LucideIcon } from 'lucide-react'

// Badge Component
export interface BadgeProps {
  children: ReactNode
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral'
  size?: 'sm' | 'md' | 'lg'
  icon?: LucideIcon
  className?: string
}

export function Badge({ children, variant = 'neutral', size = 'md', icon: Icon, className }: BadgeProps) {
  const variants = {
    success: 'bg-wealth-green-light text-wealth-green-dark border-wealth-green',
    warning: 'bg-warning-amber-light text-amber-800 border-warning-amber',
    danger: 'bg-danger-red-light text-red-800 border-danger-red',
    info: 'bg-info-blue-light text-blue-800 border-info-blue',
    neutral: 'bg-gray-100 text-text-secondary border-border',
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-3 py-1 text-sm gap-1.5',
    lg: 'px-4 py-1.5 text-base gap-2',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center font-semibold rounded-full border',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {Icon && <Icon className={size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />}
      {children}
    </span>
  )
}

// Pill Button Component (clickable badge)
export interface PillButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral'
  icon?: LucideIcon
  active?: boolean
}

export function PillButton({
  children,
  variant = 'neutral',
  icon: Icon,
  active = false,
  className,
  ...props
}: PillButtonProps) {
  const variants = {
    success: active
      ? 'bg-wealth-green text-white'
      : 'bg-wealth-green-light text-wealth-green-dark hover:bg-wealth-green/20',
    warning: active
      ? 'bg-warning-amber text-white'
      : 'bg-warning-amber-light text-amber-800 hover:bg-warning-amber/20',
    danger: active
      ? 'bg-danger-red text-white'
      : 'bg-danger-red-light text-red-800 hover:bg-danger-red/20',
    info: active
      ? 'bg-info-blue text-white'
      : 'bg-info-blue-light text-blue-800 hover:bg-info-blue/20',
    neutral: active
      ? 'bg-text-primary text-white'
      : 'bg-gray-100 text-text-secondary hover:bg-gray-200',
  }

  return (
    <button
      className={cn(
        'inline-flex items-center gap-2 px-4 py-2 font-medium text-sm rounded-full',
        'transition-all duration-base hover:shadow-md active:scale-98',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-info-blue',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        className
      )}
      {...props}
    >
      {Icon && <Icon className="w-4 h-4" />}
      {children}
    </button>
  )
}

// Status Indicator
export interface StatusProps {
  status: 'online' | 'offline' | 'away' | 'busy'
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export function Status({ status, showLabel = false, size = 'md' }: StatusProps) {
  const colors = {
    online: 'bg-wealth-green',
    offline: 'bg-gray-400',
    away: 'bg-warning-amber',
    busy: 'bg-danger-red',
  }

  const labels = {
    online: 'Online',
    offline: 'Offline',
    away: 'Away',
    busy: 'Busy',
  }

  const sizes = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
  }

  return (
    <div className="inline-flex items-center gap-2">
      <span className={cn('rounded-full animate-pulse', colors[status], sizes[size])} />
      {showLabel && <span className="text-sm text-text-secondary">{labels[status]}</span>}
    </div>
  )
}

// Count Badge (for notifications)
export interface CountBadgeProps {
  count: number
  max?: number
  variant?: 'success' | 'warning' | 'danger' | 'info'
}

export function CountBadge({ count, max = 99, variant = 'danger' }: CountBadgeProps) {
  const displayCount = count > max ? `${max}+` : count

  const variants = {
    success: 'bg-wealth-green text-white',
    warning: 'bg-warning-amber text-white',
    danger: 'bg-danger-red text-white',
    info: 'bg-info-blue text-white',
  }

  if (count === 0) return null

  return (
    <span
      className={cn(
        'inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-bold rounded-full',
        variants[variant]
      )}
    >
      {displayCount}
    </span>
  )
}
