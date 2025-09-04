'use client'

import { useEffect, useRef, useCallback, ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth/AuthProvider'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

interface AuthGuardProps {
  children: ReactNode
  requireAuth?: boolean
  requireOnboarding?: boolean
  redirectTo?: string
  fallback?: ReactNode
}

// Track redirect state to prevent loops
const redirectTracker = {
  lastRedirect: '',
  lastRedirectTime: 0,
  redirectCount: 0,
  isRedirecting: false
}

export default function AuthGuard({ 
  children, 
  requireAuth = true,
  requireOnboarding = false,
  redirectTo,
  fallback
}: AuthGuardProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, isAuthenticated, isLoading, isInitialized } = useAuth()
  
  // Refs to track state and prevent unnecessary effects
  const lastAuthStateRef = useRef<string>('')
  const debounceTimeoutRef = useRef<NodeJS.Timeout>()
  const hasRedirectedRef = useRef(false)

  // Create a stable auth state key for comparison
  const authStateKey = `${isInitialized}-${isAuthenticated}-${user?.id || 'null'}-${user?.onboarding_completed || 'null'}-${pathname}`

  // Debounced redirect function to prevent rapid successive redirects
  const debouncedRedirect = useCallback((url: string, reason: string) => {
    // Clear any existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current)
    }

    // Check for redirect loops
    const now = Date.now()
    const timeSinceLastRedirect = now - redirectTracker.lastRedirectTime
    
    if (redirectTracker.lastRedirect === url && timeSinceLastRedirect < 1000) {
      console.warn('AuthGuard: Preventing potential redirect loop to', url)
      return
    }

    if (redirectTracker.isRedirecting) {
      console.warn('AuthGuard: Already redirecting, skipping redirect to', url)
      return
    }

    // Set debounce timeout
    debounceTimeoutRef.current = setTimeout(() => {
      // Double-check we should still redirect
      if (redirectTracker.isRedirecting) return

      console.log(`AuthGuard: ${reason} - redirecting to:`, url)
      
      // Update redirect tracker
      redirectTracker.lastRedirect = url
      redirectTracker.lastRedirectTime = now
      redirectTracker.redirectCount++
      redirectTracker.isRedirecting = true
      hasRedirectedRef.current = true

      // Perform redirect
      router.replace(url)

      // Reset redirecting flag after a delay
      setTimeout(() => {
        redirectTracker.isRedirecting = false
      }, 500)
    }, 100) // 100ms debounce
  }, [router])

  // Determine what action should be taken based on current state
  const getRequiredAction = useCallback(() => {
    if (!isInitialized) {
      return { action: 'loading', reason: 'Auth not initialized' }
    }

    // Reset redirect flag when auth state changes significantly
    if (lastAuthStateRef.current !== authStateKey) {
      hasRedirectedRef.current = false
    }

    // If we already redirected for this state, don't redirect again
    if (hasRedirectedRef.current) {
      return { action: 'allow', reason: 'Already handled this state' }
    }

    // Authentication required but user not authenticated
    if (requireAuth && !isAuthenticated) {
      const loginUrl = redirectTo || `/auth/login?redirect=${encodeURIComponent(pathname)}`
      return { action: 'redirect', url: loginUrl, reason: 'Authentication required' }
    }

    // User authenticated but on public-only pages (login/register)
    if (!requireAuth && isAuthenticated && user) {
      if (!user.onboarding_completed) {
        return { action: 'redirect', url: '/onboarding', reason: 'User needs onboarding' }
      } else {
        const dashboardUrl = redirectTo || '/dashboard'
        return { action: 'redirect', url: dashboardUrl, reason: 'User already authenticated' }
      }
    }

    // Onboarding page specific logic
    if (pathname === '/onboarding') {
      if (!isAuthenticated) {
        const loginUrl = `/auth/login?redirect=${encodeURIComponent(pathname)}`
        return { action: 'redirect', url: loginUrl, reason: 'Onboarding requires authentication' }
      }
      if (user?.onboarding_completed) {
        return { action: 'redirect', url: '/dashboard', reason: 'Onboarding already completed' }
      }
      // Allow access to onboarding page for authenticated, non-onboarded users
      return { action: 'allow', reason: 'Valid onboarding access' }
    }

    // Dashboard and other protected pages
    if (isAuthenticated && user) {
      if (!user.onboarding_completed && pathname !== '/onboarding') {
        return { action: 'redirect', url: '/onboarding', reason: 'Onboarding required for protected pages' }
      }
    }

    // Onboarding requirement check for other pages
    if (requireOnboarding && isAuthenticated && user && !user.onboarding_completed) {
      return { action: 'redirect', url: '/onboarding', reason: 'Onboarding required by page' }
    }

    // Default: allow access
    return { action: 'allow', reason: 'All checks passed' }
  }, [isInitialized, isAuthenticated, user, requireAuth, requireOnboarding, pathname, redirectTo, authStateKey])

  useEffect(() => {
    // Skip if auth state hasn't changed
    if (lastAuthStateRef.current === authStateKey) {
      return
    }

    const requiredAction = getRequiredAction()
    
    console.log('AuthGuard evaluation:', {
      pathname,
      isAuthenticated,
      user: user ? { id: user.id, onboarding_completed: user.onboarding_completed } : null,
      requireAuth,
      requireOnboarding,
      action: requiredAction.action,
      reason: requiredAction.reason,
      authStateKey
    })

    // Update last auth state
    lastAuthStateRef.current = authStateKey

    // Handle the required action
    if (requiredAction.action === 'redirect' && requiredAction.url) {
      debouncedRedirect(requiredAction.url, requiredAction.reason)
    }
  }, [authStateKey, getRequiredAction, debouncedRedirect])

  // Cleanup effect
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current)
      }
      // Reset redirect tracker when component unmounts
      redirectTracker.isRedirecting = false
    }
  }, [])

  // Reset redirect tracker when user authentication status changes significantly
  useEffect(() => {
    const userKey = `${isAuthenticated}-${user?.id || 'null'}-${user?.onboarding_completed || 'null'}`
    
    // Reset redirect tracking when user changes (login/logout) or onboarding status changes
    if (lastAuthStateRef.current && !lastAuthStateRef.current.includes(userKey)) {
      console.log('User state changed significantly, resetting redirect tracker')
      redirectTracker.redirectCount = 0
      redirectTracker.lastRedirect = ''
      redirectTracker.isRedirecting = false
      hasRedirectedRef.current = false
    }
  }, [isAuthenticated, user?.id, user?.onboarding_completed])

  // Determine what to render based on current state
  const requiredAction = getRequiredAction()

  // Show loading while initializing or during auth loading
  if (!isInitialized || isLoading) {
    console.log('AuthGuard loading state:', { isInitialized, isLoading })
    if (fallback) {
      return <>{fallback}</>
    }

    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-primary">
        <div className="text-center">
          <LoadingSpinner size="lg" color="white" />
          <p className="mt-4 text-white text-lg">
            {!isInitialized ? 'Initializing...' : 'Loading...'}
          </p>
        </div>
      </div>
    )
  }

  // Show loading during authentication state changes (authenticated but no user data yet)
  if (isAuthenticated && user === null) {
    console.log('AuthGuard: authenticated but no user data')
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-primary">
        <div className="text-center">
          <LoadingSpinner size="lg" color="white" />
          <p className="mt-4 text-white text-lg">Setting up your account...</p>
        </div>
      </div>
    )
  }

  // Show loading during redirects to prevent flash of content
  if (requiredAction.action === 'redirect' || redirectTracker.isRedirecting) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-primary">
        <div className="text-center">
          <LoadingSpinner size="lg" color="white" />
          <p className="mt-4 text-white text-lg">Redirecting...</p>
        </div>
      </div>
    )
  }

  // Only render children if action is 'allow'
  if (requiredAction.action === 'allow') {
    return <>{children}</>
  }

  // Default fallback - should not reach here
  return null
}

// Higher-order component for protecting pages
export function withAuthGuard<P extends object>(
  Component: React.ComponentType<P>,
  options: Omit<AuthGuardProps, 'children'> = {}
) {
  return function AuthGuardedComponent(props: P) {
    return (
      <AuthGuard {...options}>
        <Component {...props} />
      </AuthGuard>
    )
  }
}

// Specific guard components for common use cases
export function ProtectedRoute({ children, ...props }: Omit<AuthGuardProps, 'requireAuth'>) {
  return (
    <AuthGuard requireAuth={true} {...props}>
      {children}
    </AuthGuard>
  )
}

export function PublicRoute({ children, ...props }: Omit<AuthGuardProps, 'requireAuth'>) {
  return (
    <AuthGuard requireAuth={false} {...props}>
      {children}
    </AuthGuard>
  )
}

export function OnboardingGuard({ children, ...props }: Omit<AuthGuardProps, 'requireAuth' | 'requireOnboarding'>) {
  // OnboardingGuard should allow access only to authenticated users who haven't completed onboarding
  return (
    <AuthGuard requireAuth={true} {...props}>
      {children}
    </AuthGuard>
  )
}