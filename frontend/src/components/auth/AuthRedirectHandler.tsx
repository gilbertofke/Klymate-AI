'use client'

import { useEffect } from 'react'
import { useAuthStore } from '@/lib/auth/authStore'
import { useRouter } from 'next/navigation'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

/**
 * Component to handle Firebase redirect authentication results
 * Should be included in the main layout or auth pages
 */
export default function AuthRedirectHandler() {
  const { initialize, isInitialized, isLoading } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    // Initialize auth store which will handle redirect results
    if (!isInitialized) {
      initialize()
    }
  }, [initialize, isInitialized])

  // Don't render anything visible, this is just for handling redirects
  if (isLoading && !isInitialized) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-80 flex items-center justify-center z-50">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-text-secondary">Completing authentication...</p>
        </div>
      </div>
    )
  }

  return null
}