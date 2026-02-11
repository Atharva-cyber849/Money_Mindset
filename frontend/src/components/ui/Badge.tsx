'use client'

import { useRef, useEffect } from 'react'
import { Trophy, Lock } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { cn } from '@/lib/utils'
import gsap from 'gsap'

interface BadgeProps {
  id: string
  title: string
  description: string
  icon: string
  isUnlocked: boolean
  progress?: number
  maxProgress?: number
  rarity?: 'common' | 'rare' | 'epic' | 'legendary'
  animate?: boolean
}

export function Badge({ 
  title, 
  description, 
  icon, 
  isUnlocked, 
  progress,
  maxProgress,
  rarity = 'common',
  animate = false
}: BadgeProps) {
  const badgeRef = useRef<HTMLDivElement>(null)
  const iconRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (animate && badgeRef.current) {
      gsap.fromTo(
        badgeRef.current,
        { opacity: 0, scale: 0.8, rotateY: -180 },
        {
          opacity: 1,
          scale: 1,
          rotateY: 0,
          duration: 0.8,
          ease: 'back.out(1.7)',
        }
      )
    }

    // Add sparkle animation for unlocked badges
    if (isUnlocked && iconRef.current) {
      const handleMouseEnter = () => {
        gsap.to(iconRef.current, {
          scale: 1.2,
          rotation: 360,
          duration: 0.5,
          ease: 'power2.out',
        })
      }

      const handleMouseLeave = () => {
        gsap.to(iconRef.current, {
          scale: 1,
          rotation: 0,
          duration: 0.3,
          ease: 'power2.out',
        })
      }

      iconRef.current.addEventListener('mouseenter', handleMouseEnter)
      iconRef.current.addEventListener('mouseleave', handleMouseLeave)

      return () => {
        iconRef.current?.removeEventListener('mouseenter', handleMouseEnter)
        iconRef.current?.removeEventListener('mouseleave', handleMouseLeave)
      }
    }
  }, [animate, isUnlocked])

  const rarityColors = {
    common: 'from-gray-400 to-gray-500',
    rare: 'from-blue-400 to-blue-600',
    epic: 'from-purple-400 to-purple-600',
    legendary: 'from-yellow-400 to-orange-500',
  }

  const rarityBorders = {
    common: 'border-gray-300',
    rare: 'border-blue-400',
    epic: 'border-purple-400',
    legendary: 'border-yellow-400',
  }

  return (
    <Card ref={badgeRef} className={cn(
      'relative overflow-hidden transition-all duration-300',
      isUnlocked ? 'opacity-100' : 'opacity-60'
    )}>
      {/* Badge Icon */}
      <div className="flex flex-col items-center">
        <div
          ref={iconRef}
          className={cn(
            'w-20 h-20 rounded-full flex items-center justify-center text-4xl mb-3 border-4',
            rarityBorders[rarity],
            isUnlocked 
              ? `bg-gradient-to-br ${rarityColors[rarity]} shadow-lg cursor-pointer`
              : 'bg-gray-300'
          )}
        >
          {isUnlocked ? icon : <Lock className="w-8 h-8 text-gray-500" />}
        </div>

        {/* Badge Info */}
        <h3 className={cn(
          'text-lg font-bold text-center mb-1',
          isUnlocked ? 'text-gray-900' : 'text-gray-500'
        )}>
          {title}
        </h3>
        <p className="text-sm text-gray-600 text-center mb-3">
          {description}
        </p>

        {/* Progress (if applicable) */}
        {!isUnlocked && progress !== undefined && maxProgress !== undefined && (
          <div className="w-full">
            <ProgressBar 
              percent={(progress / maxProgress) * 100} 
              color="blue"
              height="h-2"
            />
            <p className="text-xs text-gray-500 text-center mt-1">
              {progress} / {maxProgress}
            </p>
          </div>
        )}

        {/* Unlocked Badge */}
        {isUnlocked && (
          <div className="flex items-center gap-1 text-green-600 text-sm font-semibold">
            <Trophy className="w-4 h-4" />
            Unlocked!
          </div>
        )}
      </div>

      {/* Rarity Shine Effect */}
      {isUnlocked && rarity !== 'common' && (
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20 animate-pulse-slow" />
      )}
    </Card>
  )
}

interface BadgeGridProps {
  badges: BadgeProps[]
  animate?: boolean
}

export function BadgeGrid({ badges, animate = true }: BadgeGridProps) {
  const gridRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (animate && gridRef.current) {
      const children = gridRef.current.children
      gsap.fromTo(
        children,
        { opacity: 0, y: 30, scale: 0.8 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.5,
          stagger: 0.1,
          ease: 'back.out(1.2)',
        }
      )
    }
  }, [animate])

  return (
    <div ref={gridRef} className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {badges.map((badge) => (
        <Badge key={badge.id} {...badge} animate={false} />
      ))}
    </div>
  )
}
