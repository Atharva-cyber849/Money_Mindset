'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard, 
  Gamepad2, 
  TrendingUp, 
  Target, 
  MessageSquare, 
  Trophy,
  BookOpen,
  Sparkles,
  Brain,
  User
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Personality', href: '/personality/quiz', icon: User },
  { name: 'Simulations', href: '/simulations', icon: Gamepad2 },
  { name: 'Analytics', href: '/analytics', icon: Brain },
  { name: 'My Progress', href: '/progress', icon: TrendingUp },
  { name: 'Goals', href: '/goals', icon: Target },
  { name: 'AI Tutor', href: '/ai-tutor', icon: MessageSquare },
  { name: 'Achievements', href: '/achievements', icon: Trophy },
  { name: 'Learn', href: '/learn', icon: BookOpen },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-gradient-to-b from-blue-900 to-blue-800 text-white flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-blue-700">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Money Mindset</h1>
            <p className="text-xs text-blue-300">Financial Freedom</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                isActive
                  ? 'bg-white text-blue-900 shadow-lg'
                  : 'text-blue-100 hover:bg-blue-700 hover:text-white'
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* Bottom CTA */}
      <div className="p-4 m-4 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg">
        <div className="text-center">
          <Trophy className="w-8 h-8 mx-auto mb-2 text-yellow-300" />
          <h3 className="font-semibold text-sm mb-1">Unlock Premium</h3>
          <p className="text-xs text-white/80 mb-3">
            Get advanced simulations & personalized coaching
          </p>
          <button className="w-full bg-white text-purple-600 text-sm font-semibold py-2 rounded-lg hover:bg-gray-100 transition-colors">
            Upgrade Now
          </button>
        </div>
      </div>
    </aside>
  )
}
