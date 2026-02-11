'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { 
  Brain, 
  TrendingUp, 
  Target, 
  Sparkles, 
  Zap, 
  Shield, 
  Trophy,
  ArrowRight,
  CheckCircle2
} from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Insights',
    description: 'Get personalized financial guidance powered by advanced machine learning',
    color: 'bg-purple-500'
  },
  {
    icon: Zap,
    title: 'Interactive Simulations',
    description: 'Learn through engaging scenarios that make complex concepts simple',
    color: 'bg-blue-500'
  },
  {
    icon: Target,
    title: 'Goal Tracking',
    description: 'Set financial goals and watch your progress with smart recommendations',
    color: 'bg-green-500'
  },
  {
    icon: Trophy,
    title: 'Gamified Learning',
    description: 'Earn XP, unlock achievements, and level up your financial knowledge',
    color: 'bg-yellow-500'
  },
  {
    icon: Shield,
    title: 'Privacy First',
    description: 'Your data is encrypted and secure. We never share your information',
    color: 'bg-red-500'
  },
  {
    icon: TrendingUp,
    title: 'Real Results',
    description: 'Join thousands who have transformed their financial future',
    color: 'bg-indigo-500'
  }
]

const benefits = [
  'Master budgeting and expense tracking',
  'Understand investments and compound interest',
  'Learn debt management strategies',
  'Build emergency funds effectively',
  'Plan for retirement with confidence',
  'Get personalized AI coaching 24/7'
]

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">Money Mindset</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/login">
                <Button variant="outline">Login</Button>
              </Link>
              <Link href="/register">
                <Button variant="primary">Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Master Your Money,
              <br />Transform Your Life
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Learn personal finance through interactive simulations, AI guidance, 
              and gamified lessons. Start your journey to financial freedom today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register">
                <Button size="lg" className="gap-2">
                  Start Learning Free
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button size="lg" variant="outline">
                  Explore Demo
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Why Money Mindset?</h2>
            <p className="text-xl text-gray-600">Everything you need to build financial confidence</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, idx) => {
              const Icon = feature.icon
              return (
                <Card key={idx} hover className="p-6">
                  <div className={`w-12 h-12 ${feature.color} rounded-lg flex items-center justify-center mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">What You'll Learn</h2>
              <div className="space-y-4">
                {benefits.map((benefit, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-lg text-gray-700">{benefit}</span>
                  </div>
                ))}
              </div>
              <div className="mt-8">
                <Link href="/register">
                  <Button size="lg" className="gap-2">
                    Start Your Journey
                    <ArrowRight className="w-5 h-5" />
                  </Button>
                </Link>
              </div>
            </div>
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
              <div className="text-center">
                <Trophy className="w-16 h-16 mx-auto mb-4" />
                <h3 className="text-3xl font-bold mb-4">Join 10,000+ Learners</h3>
                <p className="text-blue-100 mb-6">
                  People just like you are building better financial futures every day
                </p>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-3xl font-bold">12+</div>
                    <div className="text-sm text-blue-200">Simulations</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold">50+</div>
                    <div className="text-sm text-blue-200">Lessons</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold">24/7</div>
                    <div className="text-sm text-blue-200">AI Support</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <h2 className="text-4xl font-bold mb-4">Ready to Take Control?</h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of learners who are mastering their finances
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
                Create Free Account
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">Money Mindset</span>
          </div>
          <p className="mb-4">Master your money, transform your life</p>
          <p className="text-sm">© 2026 Money Mindset. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
