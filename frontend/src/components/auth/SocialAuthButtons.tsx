'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/lib/auth/authStore'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
// Note: Popup utilities will be added when needed
import toast from 'react-hot-toast'

interface SocialAuthButtonsProps {
  mode: 'login' | 'register'
  onSuccess?: () => void
  onError?: (error: string) => void
  className?: string
}

export default function SocialAuthButtons({ 
  mode, 
  onSuccess, 
  onError,
  className = '' 
}: SocialAuthButtonsProps) {
  const { 
    signInWithGoogle,
    loading 
  } = useAuthStore()
  
  const [loadingProvider, setLoadingProvider] = useState<string | null>(null)
  // Popup help functionality will be added when needed

  const handleSocialAuth = async (provider: 'google' | 'facebook' | 'apple') => {
    try {
      setLoadingProvider(provider)
      
      // Popup blocker detection will be added when needed
      
      // For now, only Google authentication is supported
      if (provider === 'google') {
        await signInWithGoogle()
      } else {
        throw new Error(`${provider} authentication is not yet implemented`)
      }
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error: any) {
      // Handle specific auth errors
      if (error.message === 'REDIRECT_IN_PROGRESS') {
        return // Silent return for redirect flow
      }

      let errorMessage = error.message || `${provider} ${mode} failed`
      
      // Enhanced error messages with specific instructions
      if (errorMessage.includes('popup')) {
        errorMessage = `${provider} authentication popup was blocked. Please allow popups for this site and try again.`
      } else if (errorMessage.includes('network')) {
        errorMessage = 'Network error. Please check your internet connection and try again.'
      } else if (errorMessage.includes('blocked') || errorMessage.includes('cancelled')) {
        errorMessage = `${provider} authentication was interrupted. Please ensure popups are allowed and try again.`
      } else if (errorMessage.includes('closed')) {
        errorMessage = 'Authentication window was closed. Please keep the popup open until sign-in is complete.'
      }
      
        if (onError) {
          onError(errorMessage)
        } else {
          toast.error(errorMessage)
        }

      } finally {
        setLoadingProvider(null)
      }
    }

    const buttonVariants = {
      hover: { scale: 1.02 },
      tap: { scale: 0.98 }
    };
    
    return (
    <>
      {/* The PopupHelpDialog component is now rendered correctly through the hook */}
      <div className={`space-y-3 ${className}`}>
        {/* Help text for social sign-in */}
        <div className="text-center mb-2">
          <p className="text-xs text-text-secondary">
            Having trouble? Make sure popups are enabled for this site.
          </p>
        </div>
      {/* Google */}
      <motion.button
        variants={buttonVariants}
        whileHover="hover"
        whileTap="tap"
        type="button"
        onClick={() => handleSocialAuth('google')}
        disabled={loading || loadingProvider !== null}
        className="w-full flex items-center justify-center px-4 py-3 border border-border-medium rounded-lg bg-white hover:bg-bg-secondary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loadingProvider === 'google' ? (
          <LoadingSpinner size="sm" className="mr-2" />
        ) : (
          <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
        )}
        <span className="text-text-primary font-medium">
          Continue with Google
        </span>
      </motion.button>

      {/* Note: Facebook and Apple authentication will be added in future updates */}
    </div>
  </>
  );
}