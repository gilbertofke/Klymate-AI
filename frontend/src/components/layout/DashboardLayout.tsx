'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth/AuthProvider'
import { 
  HomeIcon,
  ChartBarIcon,
  SparklesIcon,
  TrophyIcon,
  CurrencyDollarIcon,
  UserIcon,
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'
import { 
  HomeIcon as HomeIconSolid,
  ChartBarIcon as ChartBarIconSolid,
  SparklesIcon as SparklesIconSolid,
  TrophyIcon as TrophyIconSolid,
  CurrencyDollarIcon as CurrencyDollarIconSolid,
  UserIcon as UserIconSolid
} from '@heroicons/react/24/solid'
import clsx from 'clsx'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuth()
  const pathname = usePathname()

  const navigation = [
    { 
      name: 'Dashboard', 
      href: '/dashboard', 
      icon: HomeIcon, 
      iconSolid: HomeIconSolid 
    },
    { 
      name: 'Habits', 
      href: '/habits', 
      icon: ChartBarIcon, 
      iconSolid: ChartBarIconSolid 
    },
    { 
      name: 'AI Coach', 
      href: '/coach', 
      icon: SparklesIcon, 
      iconSolid: SparklesIconSolid 
    },
    { 
      name: 'Achievements', 
      href: '/achievements', 
      icon: TrophyIcon, 
      iconSolid: TrophyIconSolid 
    },
    { 
      name: 'Credits', 
      href: '/credits', 
      icon: CurrencyDollarIcon, 
      iconSolid: CurrencyDollarIconSolid 
    },
    { 
      name: 'Profile', 
      href: '/profile', 
      icon: UserIcon, 
      iconSolid: UserIconSolid 
    },
  ]

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return (
    <div className="min-h-screen bg-bg-secondary">
      {/* Mobile sidebar */}
      <div className={clsx(
        'fixed inset-0 z-50 lg:hidden',
        sidebarOpen ? 'block' : 'hidden'
      )}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-full max-w-xs flex-col bg-bg-primary">
          <div className="flex h-16 items-center justify-between px-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">K</span>
              </div>
              <span className="ml-2 text-lg font-bold text-text-primary">Klymate AI</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-text-secondary hover:text-text-primary"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>
          <nav className="flex-1 px-4 py-4">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                const Icon = isActive ? item.iconSolid : item.icon
                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className={clsx(
                        'nav-link',
                        isActive ? 'nav-link-active' : 'nav-link-inactive'
                      )}
                      onClick={() => setSidebarOpen(false)}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      {item.name}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>
          <div className="border-t border-border-light p-4">
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-2 text-sm text-text-secondary hover:text-status-error transition-colors"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-bg-primary border-r border-border-light">
          {/* Logo */}
          <div className="flex items-center h-16 px-4 border-b border-border-light">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">K</span>
            </div>
            <div className="ml-3">
              <h1 className="text-lg font-bold text-text-primary">Klymate AI</h1>
              <p className="text-xs text-text-secondary">Climate Platform</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                const Icon = isActive ? item.iconSolid : item.icon
                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className={clsx(
                        'nav-link',
                        isActive ? 'nav-link-active' : 'nav-link-inactive'
                      )}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      {item.name}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>

          {/* User section */}
          <div className="border-t border-border-light p-4">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary truncate">
                  {user?.display_name || user?.name || 'User'}
                </p>
                <p className="text-xs text-text-secondary truncate">
                  {user?.email}
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-2 text-sm text-text-secondary hover:text-status-error transition-colors rounded-lg"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 bg-bg-primary border-b border-border-light lg:hidden">
          <div className="flex items-center justify-between h-16 px-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-text-secondary hover:text-text-primary"
            >
              <Bars3Icon className="w-6 h-6" />
            </button>
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">K</span>
              </div>
              <span className="ml-2 text-lg font-bold text-text-primary">Klymate AI</span>
            </div>
            <div className="w-6" /> {/* Spacer */}
          </div>
        </div>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}