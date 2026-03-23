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
  { name: 'Games', href: '/games', icon: Gamepad2 },
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
    <aside className="w-64 bg-white text-gray-900 flex flex-col border-r border-gray-200">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-xl flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Money Mindset</h1>
            <p className="text-xs text-gray-500">Financial Freedom</p>
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
                  ? 'bg-cyan-100 text-cyan-700 shadow-md border border-cyan-200'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* Bottom CTA */}
      <div className="p-4 m-4 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg">
        <div className="text-center">
          <Trophy className="w-8 h-8 mx-auto mb-2 text-white" />
          <h3 className="font-semibold text-sm mb-1 text-white">Unlock Premium</h3>
          <p className="text-xs text-white/90 mb-3">
            Get advanced simulations & personalized coaching
          </p>
          <button className="w-full bg-white text-amber-600 text-sm font-semibold py-2 rounded-lg hover:bg-gray-100 transition-colors">
            Upgrade Now
          </button>
        </div>
      </div>
    </aside>
  )
}
