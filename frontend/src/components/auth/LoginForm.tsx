'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  EyeIcon, 
  EyeSlashIcon,
  EnvelopeIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline'
import { useAuthStore } from '@/lib/auth/authStore'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import KlymateLogoButton from '@/components/ui/KlymateLogoButton'
import SocialAuthButtons from './SocialAuthButtons'
import { LoginCredentials } from '@/types'

// Validation schema
const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional()
})

type LoginFormData = z.infer<typeof loginSchema>

interface LoginFormProps {
  onSuccess?: () => void
  onError?: (error: string) => void
  redirectTo?: string
  showSocialAuth?: boolean
  className?: string
}

export default function LoginForm({ 
  onSuccess, 
  onError, 
  redirectTo = '/dashboard',
  showSocialAuth = true,
  className = '' 
}: LoginFormProps) {
  const router = useRouter()
  const { loginWithEmail, isLoading, error, clearError } = useAuthStore()
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError: setFormError
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      rememberMe: false
    }
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      clearError()
      
      const credentials: LoginCredentials = {
        email: data.email,
        password: data.password,
        rememberMe: data.rememberMe
      }

      const result = await loginWithEmail(credentials)
      
      if (onSuccess) {
        onSuccess()
      } else {
        // Let AuthGuard handle the redirect based on user's onboarding status
        console.log('Login successful, AuthGuard will handle redirect')
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Login failed'
      
      // Set specific field errors if available
      if (err.code === 'auth/user-not-found') {
        setFormError('email', { message: 'No account found with this email' })
      } else if (err.code === 'auth/wrong-password') {
        setFormError('password', { message: 'Incorrect password' })
      } else if (err.code === 'auth/invalid-email') {
        setFormError('email', { message: 'Invalid email address' })
      } else if (err.code === 'auth/user-disabled') {
        setFormError('email', { message: 'This account has been disabled' })
      }
      
      if (onError) {
        onError(errorMessage)
      }
    }
  }

  return (
    <div className={`w-full max-w-md mx-auto ${className}`}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-white rounded-2xl shadow-lg p-8"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <KlymateLogoButton size="md" href="/" />
          </div>
          <h1 className="text-2xl font-bold text-text-primary mb-2">Welcome back</h1>
          <p className="text-text-secondary">Sign in to your Klymate AI account</p>
        </div>

        {/* Social Auth */}
        {showSocialAuth && (
          <div className="mb-6">
            <SocialAuthButtons 
              mode="login" 
              onSuccess={onSuccess}
              onError={onError}
            />
            
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border-light" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-text-muted">Or continue with email</span>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-4 p-3 bg-status-error/10 border border-status-error/20 rounded-lg"
          >
            <p className="text-sm text-status-error">{error.message}</p>
          </motion.div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-2">
              Email address
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <EnvelopeIcon className="h-5 w-5 text-text-muted" />
              </div>
              <input
                {...register('email')}
                type="email"
                id="email"
                autoComplete="email"
                className={`
                  block w-full pl-10 pr-3 py-3 border rounded-lg
                  focus:ring-2 focus:ring-primary-green focus:border-primary-green
                  ${errors.email 
                    ? 'border-status-error focus:ring-status-error focus:border-status-error' 
                    : 'border-border-medium'
                  }
                `}
                placeholder="Enter your email"
              />
            </div>
            {errors.email && (
              <p className="mt-1 text-sm text-status-error">{errors.email.message}</p>
            )}
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-2">
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <LockClosedIcon className="h-5 w-5 text-text-muted" />
              </div>
              <input
                {...register('password')}
                type={showPassword ? 'text' : 'password'}
                id="password"
                autoComplete="current-password"
                className={`
                  block w-full pl-10 pr-10 py-3 border rounded-lg
                  focus:ring-2 focus:ring-primary-green focus:border-primary-green
                  ${errors.password 
                    ? 'border-status-error focus:ring-status-error focus:border-status-error' 
                    : 'border-border-medium'
                  }
                `}
                placeholder="Enter your password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeSlashIcon className="h-5 w-5 text-text-muted hover:text-text-primary" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-text-muted hover:text-text-primary" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="mt-1 text-sm text-status-error">{errors.password.message}</p>
            )}
          </div>

          {/* Remember Me & Forgot Password */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                {...register('rememberMe')}
                id="rememberMe"
                type="checkbox"
                className="h-4 w-4 text-primary-green focus:ring-primary-green border-border-medium rounded"
              />
              <label htmlFor="rememberMe" className="ml-2 block text-sm text-text-secondary">
                Remember me
              </label>
            </div>
            <Link
              href="/auth/forgot-password"
              className="text-sm text-primary-green hover:text-primary-greenLight transition-colors"
            >
              Forgot password?
            </Link>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting || isLoading}
            className="w-full btn-primary py-3 text-base font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting || isLoading ? (
              <div className="flex items-center justify-center">
                <LoadingSpinner size="sm" color="white" className="mr-2" />
                Signing in...
              </div>
            ) : (
              'Sign in'
            )}
          </button>
        </form>

        {/* Sign Up Link */}
        <div className="mt-6 text-center">
          <p className="text-text-secondary">
            Don't have an account?{' '}
            <Link
              href="/auth/register"
              className="text-primary-green hover:text-primary-greenLight font-medium transition-colors"
            >
              Sign up
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}