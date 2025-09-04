'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { OnboardingGuard } from '@/components/auth/AuthGuard'
import { OnboardingWizard } from '@/components/onboarding/OnboardingWizard'
import { useAuth } from '@/lib/auth/AuthProvider'
import { useAuthStore } from '@/lib/auth/authStore'

export default function OnboardingPage() {
  const router = useRouter()
  const { user } = useAuth()
  const { debouncedRefreshUser } = useAuthStore()

  // Refresh user data when the onboarding page loads to ensure we have the latest state
  useEffect(() => {
    const refreshUserData = async () => {
      try {
        console.log('Onboarding page loaded, refreshing user data...')
        await debouncedRefreshUser(300)
      } catch (error) {
        console.error('Failed to refresh user data on onboarding page load:', error)
      }
    }

    refreshUserData()
  }, [debouncedRefreshUser])

  const handleOnboardingComplete = async () => {
    console.log('Onboarding completed, AuthGuard will handle redirect...')
    // Let AuthGuard handle the redirect based on updated user state
    // No manual redirect needed - AuthGuard will detect the onboarding_completed change
  }

  return (
    <OnboardingGuard>
      <div className="min-h-screen bg-gradient-primary">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div 
            className="absolute inset-0" 
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              backgroundRepeat: 'repeat'
            }}
          />
        </div>

        <div className="relative z-10 min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="w-full max-w-4xl"
          >
            {/* Header */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6"
              >
                <span className="text-white font-bold text-2xl">K</span>
              </motion.div>
              
              <motion.h1
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="text-3xl md:text-4xl font-bold text-white mb-4"
              >
                Welcome to Klymate AI
              </motion.h1>
              
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="text-xl text-white/90 mb-2"
              >
                Let's personalize your climate journey
              </motion.p>
              
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 }}
                className="text-white/70 max-w-2xl mx-auto"
              >
                We'll ask you a few questions to understand your lifestyle and provide 
                personalized AI coaching to help reduce your carbon footprint.
              </motion.p>
            </div>

            {/* Onboarding Wizard */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-8"
            >
              <OnboardingWizard onComplete={handleOnboardingComplete} />
            </motion.div>
          </motion.div>
        </div>
      </div>
    </OnboardingGuard>
  )
}