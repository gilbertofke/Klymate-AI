'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth/AuthProvider'

interface NavigationItem {
  path: string
  label: string
  description: string
  icon: string
  requiresAuth?: boolean
}

const navigationItems: NavigationItem[] = [
  {
    path: '/',
    label: 'Home',
    description: 'Landing page',
    icon: '🏠'
  },
  {
    path: '/auth/login',
    label: 'Login',
    description: 'Sign in to your account',
    icon: '🔑'
  },
  {
    path: '/auth/register',
    label: 'Register',
    description: 'Create new account',
    icon: '📝'
  },
  {
    path: '/onboarding',
    label: 'Onboarding Hub',
    description: 'Choose your setup experience',
    icon: '🚀',
    requiresAuth: true
  },
  {
    path: '/onboarding-simple',
    label: 'Quick Setup',
    description: 'Basic onboarding',
    icon: '⚡',
    requiresAuth: true
  },
  {
    path: '/onboarding-enhanced',
    label: 'Enhanced Onboarding',
    description: 'Complete setup with AI coaching',
    icon: '🎯',
    requiresAuth: true
  },
  {
    path: '/dashboard-enhanced',
    label: 'Dashboard',
    description: 'Your carbon tracking dashboard',
    icon: '📊',
    requiresAuth: true
  },
  {
    path: '/ai-coach',
    label: 'AI Coach',
    description: 'Get personalized climate advice',
    icon: '🤖',
    requiresAuth: true
  },
  {
    path: '/habits',
    label: 'Track Habits',
    description: 'Log your daily eco-friendly actions',
    icon: '📝',
    requiresAuth: true
  },
  {
    path: '/progress',
    label: 'My Progress',
    description: 'View your carbon reduction journey',
    icon: '📈',
    requiresAuth: true
  },
  {
    path: '/credits',
    label: 'Carbon Credits',
    description: 'Earn and manage your carbon credits',
    icon: '🌱',
    requiresAuth: true
  }
]

export default function AppNavigation() {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const router = useRouter()
  const pathname = usePathname()
  const { user, logout } = useAuth()

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = async () => {
    try {
      // Import signOut from firebase/auth
      const { signOut } = await import('firebase/auth')
      const { auth } = await import('@/lib/auth/firebase')
      await signOut(auth)
      setIsOpen(false)
      router.push('/')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const handleNavigation = (path: string) => {
    router.push(path)
    setIsOpen(false)
  }

  const filteredItems = navigationItems.filter(item => {
    if (item.requiresAuth && !user) return false
    if (!item.requiresAuth && user && (item.path === '/auth/login' || item.path === '/auth/register')) return false
    return true
  })

  return (
    <div ref={dropdownRef} style={{ position: 'fixed', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: 1000 }}>
      {/* Klymate AI Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '12px 16px',
          backgroundColor: '#10b981',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '16px',
          fontWeight: '600',
          cursor: 'pointer',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#059669'
          e.currentTarget.style.transform = 'translateY(-1px)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = '#10b981'
          e.currentTarget.style.transform = 'translateY(0)'
        }}
      >
        <span>🌱</span>
        <span>Klymate AI</span>
        <span style={{
          transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform 0.2s ease'
        }}>
          ▼
        </span>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '60px',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
          padding: '16px',
          minWidth: '280px',
          maxHeight: '70vh',
          overflowY: 'auto'
        }}>
          <div style={{ marginBottom: '16px', borderBottom: '1px solid #e5e7eb', paddingBottom: '12px' }}>
            <h3 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: '600', color: '#1f2937' }}>
              🧭 Navigation
            </h3>
            {user && (
              <div style={{ fontSize: '12px', color: '#6b7280' }}>
                Logged in as: {user.email}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {filteredItems.map((item) => (
              <button
                key={item.path}
                onClick={() => handleNavigation(item.path)}
                style={{
                  padding: '12px',
                  border: pathname === item.path ? '2px solid #10b981' : '1px solid #e5e7eb',
                  borderRadius: '6px',
                  backgroundColor: pathname === item.path ? '#f0fdf4' : 'white',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontSize: '14px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (pathname !== item.path) {
                    e.currentTarget.style.backgroundColor = '#f9fafb'
                    e.currentTarget.style.borderColor = '#d1d5db'
                  }
                }}
                onMouseLeave={(e) => {
                  if (pathname !== item.path) {
                    e.currentTarget.style.backgroundColor = 'white'
                    e.currentTarget.style.borderColor = '#e5e7eb'
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span>{item.icon}</span>
                  <span style={{ fontWeight: '500' }}>{item.label}</span>
                </div>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>
                  {item.description}
                </div>
              </button>
            ))}
          </div>

          {user && (
            <div style={{ marginTop: '16px', borderTop: '1px solid #e5e7eb', paddingTop: '12px' }}>
              <button
                onClick={handleLogout}
                style={{
                  width: '100%',
                  padding: '8px',
                  backgroundColor: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '14px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#dc2626'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#ef4444'
                }}
              >
                🚪 Logout
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}