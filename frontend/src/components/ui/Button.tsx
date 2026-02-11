'use client'

import { useRef } from 'react'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import gsap from 'gsap'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  icon?: LucideIcon
  isLoading?: boolean
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  isLoading = false,
  className,
  disabled,
  onClick,
  ...props
}: ButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null)

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    // GSAP click animation with scale
    if (buttonRef.current) {
      const tl = gsap.timeline()
      tl.to(buttonRef.current, {
        scale: 0.98,
        duration: 0.1,
        ease: 'power2.in',
      }).to(buttonRef.current, {
        scale: 1,
        duration: 0.2,
        ease: 'elastic.out(1, 0.3)',
      })
    }
    
    onClick?.(e)
  }

  const baseStyles = 'inline-flex items-center justify-center font-semibold transition-all rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg active:shadow-sm'
  
  const variants = {
    primary: 'bg-wealth-green text-white hover:bg-wealth-green-dark focus:ring-wealth-green shadow-md',
    secondary: 'bg-transparent border-2 border-wealth-green text-wealth-green hover:bg-wealth-green-light focus:ring-wealth-green',
    outline: 'border-2 border-border text-text-primary hover:bg-background focus:ring-info-blue',
    ghost: 'text-text-primary hover:bg-background focus:ring-text-muted',
    danger: 'bg-danger-red text-white hover:bg-red-600 focus:ring-danger-red shadow-md',
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-sm gap-1.5 h-9',
    md: 'px-6 py-3 text-base gap-2 h-12',
    lg: 'px-8 py-4 text-lg gap-2.5 h-14',
  }

  return (
    <button
      ref={buttonRef}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      disabled={disabled || isLoading}
      onClick={handleClick}
      {...props}
    >
      {isLoading ? (
        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
      ) : Icon ? (
        <Icon className={size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-6 h-6' : 'w-5 h-5'} />
      ) : null}
      {children}
    </button>
  )
}
