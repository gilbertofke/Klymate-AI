'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import LoginForm from '@/components/auth/LoginForm'
import { PublicRoute } from '@/components/auth/AuthGuard'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

export default function LoginPage() {
  const router = useRouter()

  const handleLoginSuccess = () => {
    router.push('/dashboard')
  }

  return (
    <PublicRoute redirectTo="/dashboard">
      <div className="min-h-screen bg-gradient-primary flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          <LoginForm 
            onSuccess={handleLoginSuccess}
            redirectTo="/dashboard"
            showSocialAuth={true}
          />
        </motion.div>
      </div>
    </PublicRoute>
  )
}