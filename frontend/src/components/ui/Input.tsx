'use client'

import { forwardRef, InputHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'
import { LucideIcon } from 'lucide-react'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: LucideIcon
  prefix?: string
  suffix?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, icon: Icon, prefix, suffix, type = 'text', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-primary mb-2">
            {label}
          </label>
        )}
        
        <div className="relative">
          {Icon && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted">
              <Icon className="w-5 h-5" />
            </div>
          )}
          
          {prefix && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-text-primary font-mono font-medium">
              {prefix}
            </div>
          )}
          
          <input
            ref={ref}
            type={type}
            className={cn(
              'w-full h-12 px-4 text-base border-2 rounded-lg transition-all',
              'focus:outline-none focus:border-info-blue focus:ring-4 focus:ring-info-blue/10',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-background',
              error ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/10' : 'border-border',
              Icon && 'pl-12',
              prefix && 'pl-10 font-mono text-right',
              suffix && 'pr-12',
              className
            )}
            {...props}
          />
          
          {suffix && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-text-muted text-sm">
              {suffix}
            </div>
          )}
        </div>
        
        {error && (
          <p className="mt-1.5 text-sm text-danger-red">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

// Currency Input Component
export interface CurrencyInputProps extends Omit<InputProps, 'prefix' | 'type'> {
  value?: number | string
  onValueChange?: (value: number) => void
}

export function CurrencyInput({ value, onValueChange, className, ...props }: CurrencyInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const numValue = parseFloat(e.target.value.replace(/[^0-9.-]/g, ''))
    if (!isNaN(numValue) && onValueChange) {
      onValueChange(numValue)
    }
  }

  return (
    <Input
      {...props}
      type="text"
      prefix="$"
      value={value}
      onChange={handleChange}
      className={cn('text-right', className)}
    />
  )
}

// Textarea Component
export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-primary mb-2">
            {label}
          </label>
        )}
        
        <textarea
          ref={ref}
          className={cn(
            'w-full min-h-[120px] px-4 py-3 text-base border-2 rounded-lg transition-all resize-none',
            'focus:outline-none focus:border-info-blue focus:ring-4 focus:ring-info-blue/10',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-background',
            error ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/10' : 'border-border',
            className
          )}
          {...props}
        />
        
        {error && (
          <p className="mt-1.5 text-sm text-danger-red">{error}</p>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'
