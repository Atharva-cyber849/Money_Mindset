'use client'

import { useState } from 'react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Bell, Lock, Globe, Palette, Shield, CreditCard } from 'lucide-react'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general')

  const tabs = [
    { id: 'general', label: 'General', icon: Globe },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'billing', label: 'Billing', icon: CreditCard },
  ]

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <Card className="p-4 lg:col-span-1 h-fit">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-50 text-blue-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </Card>

        {/* Content */}
        <div className="lg:col-span-3 space-y-6">
          {activeTab === 'general' && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">General Settings</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <Input placeholder="John Doe" defaultValue="Demo User" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <Input type="email" placeholder="you@example.com" defaultValue="demo@moneymindset.com" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Occupation
                  </label>
                  <Input placeholder="Software Engineer" defaultValue="Software Engineer" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Income
                  </label>
                  <Input type="number" placeholder="5500" defaultValue="5500" />
                </div>
                <div className="pt-4">
                  <Button variant="primary">Save Changes</Button>
                </div>
              </div>
            </Card>
          )}

          {activeTab === 'notifications' && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Notification Preferences</h2>
              <div className="space-y-6">
                {[
                  { title: 'Email Notifications', description: 'Receive email updates about your progress' },
                  { title: 'Push Notifications', description: 'Get browser notifications for important events' },
                  { title: 'Weekly Digest', description: 'Receive a weekly summary of your financial activity' },
                  { title: 'Achievement Alerts', description: 'Get notified when you earn new badges' },
                  { title: 'Simulation Reminders', description: 'Reminders to complete pending simulations' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between py-4 border-b border-gray-200 last:border-0">
                    <div>
                      <div className="font-medium text-gray-900">{item.title}</div>
                      <div className="text-sm text-gray-600">{item.description}</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked={index < 3} />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {activeTab === 'security' && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Security Settings</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current Password
                  </label>
                  <Input type="password" placeholder="••••••••" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    New Password
                  </label>
                  <Input type="password" placeholder="••••••••" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirm New Password
                  </label>
                  <Input type="password" placeholder="••••••••" />
                </div>
                <div className="pt-4">
                  <Button variant="primary">Update Password</Button>
                </div>
              </div>
            </Card>
          )}

          {activeTab === 'appearance' && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Appearance</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-4">Theme</label>
                  <div className="grid grid-cols-3 gap-4">
                    {['Light', 'Dark', 'Auto'].map((theme) => (
                      <button
                        key={theme}
                        className={`p-4 border-2 rounded-lg text-center hover:border-blue-500 transition-colors ${
                          theme === 'Light' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                        }`}
                      >
                        <div className="font-medium">{theme}</div>
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-4">Accent Color</label>
                  <div className="flex gap-3">
                    {['blue', 'purple', 'green', 'orange', 'pink'].map((color) => (
                      <button
                        key={color}
                        className={`w-10 h-10 rounded-full bg-${color}-500 border-2 border-white shadow-md hover:scale-110 transition-transform`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          )}

          {activeTab === 'privacy' && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Privacy Settings</h2>
              <div className="space-y-6">
                {[
                  { title: 'Profile Visibility', description: 'Make your profile visible to other users' },
                  { title: 'Activity Status', description: 'Show when you are active' },
                  { title: 'Progress Sharing', description: 'Allow others to see your progress' },
                  { title: 'Data Analytics', description: 'Help us improve by sharing anonymous usage data' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between py-4 border-b border-gray-200 last:border-0">
                    <div>
                      <div className="font-medium text-gray-900">{item.title}</div>
                      <div className="text-sm text-gray-600">{item.description}</div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked={index === 3} />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {activeTab === 'billing' && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Billing & Subscription</h2>
              <div className="space-y-6">
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border border-blue-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-lg font-semibold text-gray-900">Free Plan</div>
                      <div className="text-sm text-gray-600 mt-1">All basic features included</div>
                    </div>
                    <Button variant="primary">Upgrade to Pro</Button>
                  </div>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900 mb-4">Billing History</h3>
                  <div className="text-gray-600 text-center py-8">No billing history available</div>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
