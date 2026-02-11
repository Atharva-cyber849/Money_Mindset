'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

export interface ContainerProps {
  children: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  padding?: boolean
  className?: string
}

export function Container({
  children,
  size = 'xl',
  padding = true,
  className,
}: ContainerProps) {
  const sizes = {
    sm: 'max-w-3xl',
    md: 'max-w-5xl',
    lg: 'max-w-6xl',
    xl: 'max-w-7xl',
    full: 'max-w-full',
  }

  return (
    <div
      className={cn(
        'mx-auto w-full',
        sizes[size],
        padding && 'px-4 sm:px-6 lg:px-8',
        className
      )}
    >
      {children}
    </div>
  )
}

export interface PageHeaderProps {
  title: string
  subtitle?: string
  action?: ReactNode
  backLink?: {
    href: string
    label: string
  }
  className?: string
}

export function PageHeader({
  title,
  subtitle,
  action,
  backLink,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn('mb-8', className)}>
      {backLink && (
        <a
          href={backLink.href}
          className="inline-flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary mb-4 transition-colors"
        >
          ← {backLink.label}
        </a>
      )}
      
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h1 className="text-4xl font-bold text-text-primary font-display mb-2">
            {title}
          </h1>
          {subtitle && (
            <p className="text-lg text-text-secondary">{subtitle}</p>
          )}
        </div>
        
        {action && (
          <div className="flex-shrink-0">
            {action}
          </div>
        )}
      </div>
    </div>
  )
}

export interface SectionProps {
  children: ReactNode
  title?: string
  subtitle?: string
  action?: ReactNode
  spacing?: 'none' | 'sm' | 'md' | 'lg'
  className?: string
}

export function Section({
  children,
  title,
  subtitle,
  action,
  spacing = 'md',
  className,
}: SectionProps) {
  const spacingClasses = {
    none: '',
    sm: 'mb-6',
    md: 'mb-8',
    lg: 'mb-12',
  }

  return (
    <section className={cn(spacingClasses[spacing], className)}>
      {(title || subtitle || action) && (
        <div className="flex items-start justify-between gap-4 mb-6">
          <div className="flex-1">
            {title && (
              <h2 className="text-2xl font-bold text-text-primary font-display mb-2">
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="text-base text-text-secondary">{subtitle}</p>
            )}
          </div>
          
          {action && (
            <div className="flex-shrink-0">
              {action}
            </div>
          )}
        </div>
      )}
      
      {children}
    </section>
  )
}

export interface GridProps {
  children: ReactNode
  cols?: 1 | 2 | 3 | 4 | 5 | 6
  gap?: 2 | 3 | 4 | 6 | 8
  responsive?: boolean
  className?: string
}

export function Grid({
  children,
  cols = 3,
  gap = 6,
  responsive = true,
  className,
}: GridProps) {
  const colsClasses = {
    1: responsive ? 'grid-cols-1' : 'grid-cols-1',
    2: responsive ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-2',
    3: responsive ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-3',
    4: responsive ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4' : 'grid-cols-4',
    5: responsive ? 'grid-cols-2 md:grid-cols-3 lg:grid-cols-5' : 'grid-cols-5',
    6: responsive ? 'grid-cols-2 md:grid-cols-3 lg:grid-cols-6' : 'grid-cols-6',
  }

  const gapClasses = {
    2: 'gap-2',
    3: 'gap-3',
    4: 'gap-4',
    6: 'gap-6',
    8: 'gap-8',
  }

  return (
    <div className={cn('grid', colsClasses[cols], gapClasses[gap], className)}>
      {children}
    </div>
  )
}

export interface StackProps {
  children: ReactNode
  direction?: 'horizontal' | 'vertical'
  gap?: 2 | 3 | 4 | 6 | 8
  align?: 'start' | 'center' | 'end' | 'stretch'
  justify?: 'start' | 'center' | 'end' | 'between'
  className?: string
}

export function Stack({
  children,
  direction = 'vertical',
  gap = 4,
  align = 'stretch',
  justify = 'start',
  className,
}: StackProps) {
  const directionClasses = {
    horizontal: 'flex-row',
    vertical: 'flex-col',
  }

  const gapClasses = {
    2: 'gap-2',
    3: 'gap-3',
    4: 'gap-4',
    6: 'gap-6',
    8: 'gap-8',
  }

  const alignClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch',
  }

  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
  }

  return (
    <div
      className={cn(
        'flex',
        directionClasses[direction],
        gapClasses[gap],
        alignClasses[align],
        justifyClasses[justify],
        className
      )}
    >
      {children}
    </div>
  )
}
