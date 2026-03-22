'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { AlertCircle, Loader2, ChevronRight } from 'lucide-react'
import { userAPI } from '@/lib/api/client'

export default function ProfileSetupPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: '',
    age_group: '',
    language: 'en'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!formData.name.trim()) {
      setError('Please enter your name')
      return
    }

    if (!formData.age_group) {
      setError('Please select your age group')
      return
    }

    setLoading(true)

    try {
      await userAPI.setupProfile(formData.name, formData.age_group, formData.language)

      // Move to quiz page
      router.push('/dashboard/onboarding/quiz')
    } catch (err: any) {
      console.error('Profile setup error:', err)
      setError(err.response?.data?.detail || 'Failed to complete profile setup')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-400">Step 1 of 3</span>
            <div className="w-32 h-1 bg-slate-700 rounded-full overflow-hidden">
              <div className="w-1/3 h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"></div>
            </div>
          </div>
        </div>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-3">Let's get to know you</h1>
          <p className="text-lg text-slate-300">
            Before we build your financial profile, let's learn a little about you. This should take less than a minute.
          </p>
        </div>

        {/* Form Card */}
        <Card className="p-8 bg-slate-800 border border-slate-700">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-200">{error}</p>
              </div>
            )}

            {/* Name Field */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-slate-200 mb-2">
                What's your name?
              </label>
              <Input
                id="name"
                type="text"
                name="name"
                placeholder="John Doe"
                value={formData.name}
                onChange={handleChange}
                className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
                disabled={loading}
              />
            </div>

            {/* Age Group Field */}
            <div>
              <label htmlFor="age_group" className="block text-sm font-medium text-slate-200 mb-2">
                Your age group
              </label>
              <select
                id="age_group"
                name="age_group"
                value={formData.age_group}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
              >
                <option value="">Select an age group...</option>
                <option value="18-24">18–24</option>
                <option value="25-35">25–35</option>
                <option value="35-50">35–50</option>
                <option value="50+">50+</option>
              </select>
            </div>

            {/* Language Field */}
            <div>
              <label htmlFor="language" className="block text-sm font-medium text-slate-200 mb-2">
                Preferred language
              </label>
              <select
                id="language"
                name="language"
                value={formData.language}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
              >
                <option value="en">English</option>
                <option value="hi">Hindi</option>
                <option value="mr">Marathi</option>
                <option value="ta">Tamil</option>
              </select>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={loading || !formData.name.trim() || !formData.age_group}
              className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Setting up...
                </>
              ) : (
                <>
                  Continue
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </Button>
          </form>
        </Card>

        {/* Info Text */}
        <p className="text-center text-sm text-slate-400 mt-8">
          Your information is private and secure
        </p>
      </div>
    </div>
  )
}
