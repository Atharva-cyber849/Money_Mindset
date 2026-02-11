'use client'

import { useState, useEffect, useRef } from 'react'
import { Bell, Search, User, LogOut, Settings } from 'lucide-react'
import { useAuth } from '@/lib/auth/AuthContext'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { useRouter } from 'next/navigation'
import gsap from 'gsap'

export function Navbar() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const notificationRef = useRef<HTMLSpanElement>(null)

  // Pulse animation for notification badge
  useEffect(() => {
    if (notificationRef.current) {
      gsap.to(notificationRef.current, {
        scale: 1.2,
        duration: 0.6,
        ease: 'power2.inOut',
        repeat: -1,
        yoyo: true,
      })
    }
  }, [])

  // Animate dropdown menu
  useEffect(() => {
    if (menuRef.current) {
      if (showUserMenu) {
        gsap.fromTo(
          menuRef.current,
          { opacity: 0, y: -10, scale: 0.95 },
          {
            opacity: 1,
            y: 0,
            scale: 1,
            duration: 0.2,
            ease: 'power2.out',
          }
        )
      }
    }
  }, [showUserMenu])

  // Mock user progress - in real app, fetch from API
  const userProgress = {
    level: 2,
    currentXP: 1250,
    nextLevelXP: 2000,
    simulationsCompleted: 5,
    totalSimulations: 15,
  }

  const progressPercent = (userProgress.currentXP / userProgress.nextLevelXP) * 100

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search Bar */}
        <div className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search simulations, lessons, or ask AI tutor..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Right Side: Progress, Notifications, User Menu */}
        <div className="flex items-center gap-6 ml-6">
          {/* User Progress */}
          <div className="hidden lg:flex items-center gap-3">
            <div className="text-right">
              <div className="text-sm font-semibold text-gray-700">
                Level {userProgress.level}
              </div>
              <div className="text-xs text-gray-500">
                {userProgress.currentXP} / {userProgress.nextLevelXP} XP
              </div>
            </div>
            <div className="w-32">
              <ProgressBar 
                percent={progressPercent} 
                color="blue"
                height="h-2"
              />
            </div>
          </div>

          {/* Notifications */}
          <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell className="w-6 h-6" />
            <span ref={notificationRef} className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <span className="hidden md:block text-sm font-medium text-gray-700">
                {user?.email || 'Guest'}
              </span>
            </button>

            {/* Dropdown Menu */}
            {showUserMenu && (
              <div ref={menuRef} className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                <button 
                  onClick={() => {
                    setShowUserMenu(false)
                    router.push('/profile')
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                >
                  <User className="w-4 h-4" />
                  Profile
                </button>
                <button 
                  onClick={() => {
                    setShowUserMenu(false)
                    router.push('/settings')
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                >
                  <Settings className="w-4 h-4" />
                  Settings
                </button>
                <hr className="my-2" />
                <button 
                  onClick={() => {
                    setShowUserMenu(false)
                    logout()
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
