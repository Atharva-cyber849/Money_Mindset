'use client'

import { ReactNode, useState } from 'react'
import { ChevronDown } from 'lucide-react'
import gsap from 'gsap'
import { useRef, useEffect } from 'react'

interface CollapsibleProps {
  title: string
  icon?: ReactNode
  defaultOpen?: boolean
  children: ReactNode
  className?: string
}

export default function Collapsible({
  title,
  icon,
  defaultOpen = true,
  children,
  className = '',
}: CollapsibleProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  const contentRef = useRef<HTMLDivElement>(null)
  const chevronRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (contentRef.current) {
      if (isOpen) {
        // Slide down animation
        gsap.to(contentRef.current, {
          height: 'auto',
          opacity: 1,
          duration: 0.4,
          ease: 'power2.out',
        })
      } else {
        // Slide up animation
        gsap.to(contentRef.current, {
          height: 0,
          opacity: 0,
          duration: 0.4,
          ease: 'power2.in',
        })
      }
    }

    if (chevronRef.current) {
      gsap.to(chevronRef.current, {
        rotation: isOpen ? 180 : 0,
        duration: 0.3,
        ease: 'power2.out',
      })
    }
  }, [isOpen])

  const handleToggle = () => {
    setIsOpen(!isOpen)
  }

  return (
    <div className={`rounded-xl border border-gray-200 bg-white overflow-hidden shadow-sm hover:shadow-md transition-shadow ${className}`}>
      {/* Header */}
      <button
        onClick={handleToggle}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          {icon && <div className="text-xl">{icon}</div>}
          <h3 className="font-semibold text-gray-900">{title}</h3>
        </div>
        <div ref={chevronRef} className="text-gray-600">
          <ChevronDown className="w-5 h-5" />
        </div>
      </button>

      {/* Divider */}
      <div className="h-px bg-gray-200" />

      {/* Content */}
      <div
        ref={contentRef}
        className="overflow-hidden"
        style={{ height: defaultOpen ? 'auto' : 0, opacity: defaultOpen ? 1 : 0 }}
      >
        <div className="px-6 py-4">
          {children}
        </div>
      </div>
    </div>
  )
}
