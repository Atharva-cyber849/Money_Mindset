'use client'

import { useState, FormEvent, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Sparkles, AlertCircle, CheckCircle2, Mail, Loader2 } from 'lucide-react'
import { authAPI } from '@/lib/api/client'

export default function VerifyEmailPage() {
  const router = useRouter()
  const [email, setEmail] = useState<string>('')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    // Get email from localStorage
    const pendingEmail = localStorage.getItem('pendingEmail')
    if (!pendingEmail) {
      router.push('/register')
    } else {
      setEmail(pendingEmail)
    }
  }, [router])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!otp || otp.length !== 6) {
      setError('Please enter a valid 6-digit OTP')
      return
    }

    setLoading(true)

    try {
      // Verify OTP
      const response = await authAPI.verifyOtp(email, otp)
      localStorage.setItem('token', response.access_token)

      // Clear pending email
      localStorage.removeItem('pendingEmail')

      // Show success message
      setSuccess(true)

      // Redirect to onboarding profile after 1 second
      setTimeout(() => {
        router.push('/dashboard/onboarding/profile')
      }, 1000)
    } catch (err: any) {
      console.error('OTP verification error:', err)
      setError(err.response?.data?.detail || 'Invalid OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-600 to-purple-600 rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold">Money Mindset</span>
          </Link>
          <h1 className="text-3xl font-bold mb-2">Verify Your Email</h1>
          <p className="text-gray-600">We've sent a code to your email</p>
        </div>

        {/* Verification Form */}
        <Card className="p-8">
          {success ? (
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckCircle2 className="w-8 h-8 text-green-600" />
                </div>
              </div>
              <p className="text-lg font-semibold text-green-600">Email verified!</p>
              <p className="text-gray-600">Redirecting you to set up your profile...</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              )}

              {/* Email Display */}
              <div className="bg-cyan-50 border border-cyan-200 rounded-lg p-4 flex items-start gap-3">
                <Mail className="w-5 h-5 text-cyan-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-cyan-800">{email}</p>
              </div>

              {/* OTP Input */}
              <div>
                <label htmlFor="otp" className="block text-sm font-medium text-gray-700 mb-2">
                  Enter OTP Code
                </label>
                <Input
                  id="otp"
                  type="text"
                  placeholder="000000"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                  className="text-center text-2xl tracking-widest font-mono"
                  disabled={loading}
                />
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Check your email for the 6-digit code. In development mode, use: 123456
                </p>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="w-full h-12 bg-gradient-to-r from-cyan-600 to-purple-600 text-white hover:shadow-lg disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Verify Email'
                )}
              </Button>

              {/* Help Text */}
              <p className="text-center text-sm text-gray-600">
                Did not receive code? Check your spam folder or register again
              </p>
            </form>
          )}
        </Card>

        {/* Login Link */}
        <p className="text-center text-sm text-gray-600 mt-8">
          Already have an account?{' '}
          <Link href="/login" className="font-semibold text-cyan-600 hover:text-cyan-700">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
