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
  isRedirecting: false,
  redirectHistory: [] as string[]
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
  const { user, isAuthenticated, loading, isInitialized } = useAuth()
  
  // Refs to track state and prevent unnecessary effects
  const lastAuthStateRef = useRef<string>('')
  const debounceTimeoutRef = useRef<NodeJS.Timeout>()
  const hasRedirectedRef = useRef(false)
  const mountedRef = useRef(false)

  // Log component mount and state
  useEffect(() => {
    mountedRef.current = true;
    console.log('AuthGuard mounted:', {
      pathname,
      requireAuth,
      requireOnboarding,
      isInitialized,
      isAuthenticated,
      isLoading,
      userId: user?.uid
    });
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Create a stable auth state key for comparison
  const authStateKey = `${isInitialized}-${isAuthenticated}-${user?.uid || 'null'}-${user?.onboarding_completed || 'null'}-${pathname}`

  // Debounced redirect function to prevent rapid successive redirects
  const debouncedRedirect = useCallback((url: string, reason: string) => {
    // Clear any existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current)
    }

    // Check for redirect loops
    const now = Date.now()
    const timeSinceLastRedirect = now - redirectTracker.lastRedirectTime

    // Add to redirect history
    redirectTracker.redirectHistory.push(url)
    // Keep only last 5 redirects
    if (redirectTracker.redirectHistory.length > 5) {
      redirectTracker.redirectHistory.shift()
    }

    // Check for oscillating redirects
    if (redirectTracker.redirectHistory.length >= 2) {
      const lastTwo = redirectTracker.redirectHistory.slice(-2)
      if (lastTwo[0] === url) {
        console.error('AuthGuard: Detected oscillating redirects between', lastTwo)
        return // Break the loop
      }
    }
    
    // Prevent rapid redirects to the same URL
    if (redirectTracker.lastRedirect === url && timeSinceLastRedirect < 2000) {
      console.warn('AuthGuard: Preventing rapid redirect to', url)
      return
    }

    if (redirectTracker.isRedirecting) {
      console.warn('AuthGuard: Already redirecting, skipping redirect to', url)
      return
    }

    // Stop if we've redirected too many times
    if (redirectTracker.redirectCount > 5) {
      console.error('AuthGuard: Too many redirects, stopping redirect chain')
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
    // Don't make any decisions until initialization is complete
    if (!isInitialized || loading) {
      return { action: 'loading', reason: 'Auth state not ready' }
    }

    // Log current evaluation
    console.log('AuthGuard evaluation:', {
      pathname,
      isAuthenticated,
      requireAuth,
      mountedTime: mountedRef.current,
      redirectCount: redirectTracker.redirectCount,
      redirectHistory: redirectTracker.redirectHistory
    });

    // Only evaluate redirects if the component is mounted
    if (!mountedRef.current) {
      return { action: 'loading', reason: 'Component not mounted' }
    }

    // Don't redirect if we've already handled this state
    if (hasRedirectedRef.current) {
      console.log('Skipping redirect - already handled this state');
      return { action: 'allow', reason: 'State already handled' }
    }

    // Protected route but not authenticated
    if (requireAuth && !isAuthenticated) {
      console.log('User not authenticated for protected route');
      return { action: 'redirect', url: '/auth/login', reason: 'Authentication required' }
    }

    // Auth pages but already authenticated
    if (!requireAuth && isAuthenticated && pathname.startsWith('/auth/')) {
      console.log('Authenticated user on auth page');
      return { action: 'redirect', url: '/dashboard', reason: 'Already authenticated' }
    }

    // Check if user needs onboarding
    if (isAuthenticated && user && !user.onboarding_completed && !pathname.startsWith('/onboarding')) {
      console.log('User needs to complete onboarding');
      return { action: 'redirect', url: '/onboarding', reason: 'Onboarding required' }
    }

    // Prevent accessing onboarding if already completed
    if (isAuthenticated && user?.onboarding_completed && pathname.startsWith('/onboarding')) {
      console.log('User already completed onboarding');
      return { action: 'redirect', url: '/dashboard', reason: 'Onboarding already completed' }
    }

    // Default - allow access
    console.log('Access allowed');
    return { action: 'allow', reason: 'All checks passed' }
  }, [isInitialized, isAuthenticated, requireAuth, pathname, redirectTo, authStateKey])

  useEffect(() => {
    // Don't process redirects until component is properly mounted and initialized
    if (!mountedRef.current || !isInitialized) {
      return;
    }

    // Skip if auth state hasn't changed
    if (lastAuthStateRef.current === authStateKey) {
      return;
    }

    // Get the required action
    const requiredAction = getRequiredAction();
    
    // Log the evaluation
    console.log('Processing auth state change:', {
      from: lastAuthStateRef.current,
      to: authStateKey,
      action: requiredAction.action,
      reason: requiredAction.reason,
      redirectCount: redirectTracker.redirectCount
    });

    // Update last auth state
    lastAuthStateRef.current = authStateKey;

    // Only process redirect if explicitly required and we haven't hit our limit
    if (requiredAction.action === 'redirect' && 
        requiredAction.url && 
        redirectTracker.redirectCount < 3 &&
        mountedRef.current) {
      debouncedRedirect(requiredAction.url, requiredAction.reason);
    }
  }, [authStateKey, getRequiredAction, debouncedRedirect, isInitialized])

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
    const userKey = `${isAuthenticated}-${user?.uid || 'null'}-${user?.onboarding_completed || 'null'}`
    
    // Reset redirect tracking when user changes (login/logout) or onboarding status changes
    if (lastAuthStateRef.current && !lastAuthStateRef.current.includes(userKey)) {
      console.log('User state changed significantly, resetting redirect tracker', {
        from: lastAuthStateRef.current,
        to: userKey,
        isAuthenticated,
        userId: user?.uid,
        onboardingCompleted: user?.onboarding_completed
      })
      redirectTracker.redirectCount = 0
      redirectTracker.lastRedirect = ''
      redirectTracker.isRedirecting = false
      redirectTracker.redirectHistory = []
      hasRedirectedRef.current = false
    }
  }, [isAuthenticated, user?.uid, user?.onboarding_completed])

  // Determine what to render based on current state
  const requiredAction = getRequiredAction()

  // Show loading while initializing or during auth loading
  if (!isInitialized || loading) {
    console.log('AuthGuard loading state:', { isInitialized, loading })
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