'use client'

import { useEffect, useRef, ReactNode } from 'react'
import gsap from 'gsap'

interface PageTransitionProps {
  children: ReactNode
  className?: string
}

export function PageTransition({ children, className = '' }: PageTransitionProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          ease: 'power3.out',
        }
      )
    }
  }, [])

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  )
}

interface FadeInProps {
  children: ReactNode
  delay?: number
  direction?: 'up' | 'down' | 'left' | 'right'
  className?: string
}

export function FadeIn({ 
  children, 
  delay = 0, 
  direction = 'up', 
  className = '' 
}: FadeInProps) {
  const elementRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (elementRef.current) {
      const directionMap = {
        up: { x: 0, y: 20 },
        down: { x: 0, y: -20 },
        left: { x: 20, y: 0 },
        right: { x: -20, y: 0 },
      }

      gsap.fromTo(
        elementRef.current,
        { opacity: 0, ...directionMap[direction] },
        {
          opacity: 1,
          x: 0,
          y: 0,
          duration: 0.6,
          delay,
          ease: 'power3.out',
        }
      )
    }
  }, [delay, direction])

  return (
    <div ref={elementRef} className={className}>
      {children}
    </div>
  )
}

interface SlideInProps {
  children: ReactNode
  direction?: 'left' | 'right' | 'top' | 'bottom'
  delay?: number
  className?: string
}

export function SlideIn({ 
  children, 
  direction = 'left', 
  delay = 0, 
  className = '' 
}: SlideInProps) {
  const elementRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (elementRef.current) {
      const directionMap = {
        left: { x: -100 },
        right: { x: 100 },
        top: { y: -100 },
        bottom: { y: 100 },
      }

      gsap.fromTo(
        elementRef.current,
        directionMap[direction],
        {
          x: 0,
          y: 0,
          duration: 0.8,
          delay,
          ease: 'power3.out',
        }
      )
    }
  }, [direction, delay])

  return (
    <div ref={elementRef} className={className}>
      {children}
    </div>
  )
}

interface ScaleInProps {
  children: ReactNode
  delay?: number
  className?: string
}

export function ScaleIn({ children, delay = 0, className = '' }: ScaleInProps) {
  const elementRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (elementRef.current) {
      gsap.fromTo(
        elementRef.current,
        { scale: 0, opacity: 0 },
        {
          scale: 1,
          opacity: 1,
          duration: 0.5,
          delay,
          ease: 'back.out(1.7)',
        }
      )
    }
  }, [delay])

  return (
    <div ref={elementRef} className={className}>
      {children}
    </div>
  )
}

interface StaggerContainerProps {
  children: ReactNode
  staggerDelay?: number
  className?: string
}

export function StaggerContainer({ 
  children, 
  staggerDelay = 0.1, 
  className = '' 
}: StaggerContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      const childElements = containerRef.current.children
      gsap.fromTo(
        childElements,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.5,
          stagger: staggerDelay,
          ease: 'power3.out',
        }
      )
    }
  }, [staggerDelay])

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  )
}
