'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  UserIcon, 
  LockClosedIcon,
  BellIcon,
  ShieldCheckIcon,
  TrashIcon
} from '@heroicons/react/24/outline'
import { ProtectedRoute } from '@/components/auth/AuthGuard'
import UserProfile from '@/components/auth/UserProfile'
import ChangePassword from '@/components/auth/ChangePassword'

type TabType = 'profile' | 'password' | 'notifications' | 'privacy' | 'danger'

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<TabType>('profile')

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserIcon },
    { id: 'password', name: 'Password', icon: LockClosedIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'privacy', name: 'Privacy', icon: ShieldCheckIcon },
    { id: 'danger', name: 'Danger Zone', icon: TrashIcon },
  ] as const

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return <UserProfile />
      case 'password':
        return <ChangePassword />
      case 'notifications':
        return (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-text-primary mb-4">Notification Settings</h2>
            <p className="text-text-secondary">Notification settings will be implemented in a future update.</p>
          </div>
        )
      case 'privacy':
        return (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-text-primary mb-4">Privacy Settings</h2>
            <p className="text-text-secondary">Privacy settings will be implemented in a future update.</p>
          </div>
        )
      case 'danger':
        return (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-status-error mb-4">Danger Zone</h2>
            <p className="text-text-secondary mb-4">Account deletion and other dangerous actions will be implemented in a future update.</p>
            <button
              disabled
              className="px-4 py-2 bg-status-error/10 text-status-error border border-status-error/20 rounded-lg opacity-50 cursor-not-allowed"
            >
              Delete Account (Coming Soon)
            </button>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-bg-primary">
        {/* Header */}
        <div className="bg-gradient-primary">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-3xl font-bold text-white">Account Settings</h1>
              <p className="mt-2 text-white/80">Manage your account preferences and security settings</p>
            </motion.div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="lg:grid lg:grid-cols-12 lg:gap-8">
            {/* Sidebar */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="lg:col-span-3"
            >
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`
                        w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
                        ${activeTab === tab.id
                          ? 'bg-primary-green text-white'
                          : 'text-text-secondary hover:text-text-primary hover:bg-bg-secondary'
                        }
                      `}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      {tab.name}
                    </button>
                  )
                })}
              </nav>
            </motion.div>

            {/* Main Content */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mt-8 lg:mt-0 lg:col-span-9"
            >
              {renderTabContent()}
            </motion.div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}