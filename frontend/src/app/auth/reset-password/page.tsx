'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  LockClosedIcon, 
  EyeIcon, 
  EyeSlashIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'
import { useAuthStore } from '@/lib/auth/authStore'
import { AuthAPI } from '@/lib/api/auth'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const resetPasswordSchema = z.object({
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/\d/, 'Password must contain at least one number')
    .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Password must contain at least one special character'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
})

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>

export default function ResetPasswordPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { resetPassword, isLoading } = useAuthStore()
  
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState<{
    isValid: boolean
    errors: string[]
    strength: 'weak' | 'medium' | 'strong'
  } | null>(null)
  const [resetSuccess, setResetSuccess] = useState(false)
  const [tokenError, setTokenError] = useState(false)

  const token = searchParams.get('token')

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting }
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema)
  })

  const watchPassword = watch('password')

  // Validate token on mount
  useEffect(() => {
    if (!token) {
      setTokenError(true)
    }
  }, [token])

  // Update password strength when password changes
  useEffect(() => {
    if (watchPassword) {
      const validation = AuthAPI.validatePassword(watchPassword)
      setPasswordStrength(validation)
    } else {
      setPasswordStrength(null)
    }
  }, [watchPassword])

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      setTokenError(true)
      return
    }

    try {
      await resetPassword(token, data.password)
      setResetSuccess(true)
    } catch (error) {
      // Error is already handled by the store and toast
    }
  }

  const getPasswordStrengthColor = (strength: string) => {
    switch (strength) {
      case 'strong': return 'text-status-success'
      case 'medium': return 'text-status-warning'
      default: return 'text-status-error'
    }
  }

  const getPasswordStrengthBg = (strength: string) => {
    switch (strength) {
      case 'strong': return 'bg-status-success'
      case 'medium': return 'bg-status-warning'
      default: return 'bg-status-error'
    }
  }

  // Show error if no token
  if (tokenError) {
    return (
      <div className="min-h-screen bg-gradient-primary flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-status-error/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <XCircleIcon className="w-8 h-8 text-status-error" />
            </div>
            <h1 className="text-2xl font-bold text-text-primary mb-2">Invalid Reset Link</h1>
            <p className="text-text-secondary mb-6">
              This password reset link is invalid or has expired. Please request a new one.
            </p>
            <Link
              href="/auth/forgot-password"
              className="btn-primary inline-block px-6 py-3 text-base font-semibold"
            >
              Request New Link
            </Link>
          </div>
        </motion.div>
      </div>
    )
  }

  // Show success message
  if (resetSuccess) {
    return (
      <div className="min-h-screen bg-gradient-primary flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-status-success/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <CheckCircleIcon className="w-8 h-8 text-status-success" />
            </div>
            <h1 className="text-2xl font-bold text-text-primary mb-2">Password Reset Successful</h1>
            <p className="text-text-secondary mb-6">
              Your password has been successfully reset. You can now log in with your new password.
            </p>
            <Link
              href="/auth/login"
              className="btn-primary inline-block px-6 py-3 text-base font-semibold"
            >
              Go to Login
            </Link>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-primary flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md"
      >
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-xl">K</span>
            </div>
            <h1 className="text-2xl font-bold text-text-primary mb-2">Reset your password</h1>
            <p className="text-text-secondary">
              Enter your new password below.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-2">
                New password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockClosedIcon className="h-5 w-5 text-text-muted" />
                </div>
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  autoComplete="new-password"
                  className={`
                    block w-full pl-10 pr-10 py-3 border rounded-lg
                    focus:ring-2 focus:ring-primary-green focus:border-primary-green
                    ${errors.password 
                      ? 'border-status-error focus:ring-status-error focus:border-status-error' 
                      : 'border-border-medium'
                    }
                  `}
                  placeholder="Create a strong password"
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
              
              {/* Password Strength Indicator */}
              {passwordStrength && watchPassword && (
                <div className="mt-2">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="flex-1 bg-border-light rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${getPasswordStrengthBg(passwordStrength.strength)}`}
                        style={{ 
                          width: passwordStrength.strength === 'strong' ? '100%' : 
                                 passwordStrength.strength === 'medium' ? '66%' : '33%' 
                        }}
                      />
                    </div>
                    <span className={`text-xs font-medium ${getPasswordStrengthColor(passwordStrength.strength)}`}>
                      {passwordStrength.strength.charAt(0).toUpperCase() + passwordStrength.strength.slice(1)}
                    </span>
                  </div>
                  
                  {passwordStrength.errors.length > 0 && (
                    <div className="space-y-1">
                      {passwordStrength.errors.map((error, index) => (
                        <div key={index} className="flex items-center space-x-2 text-xs">
                          <XCircleIcon className="h-3 w-3 text-status-error" />
                          <span className="text-status-error">{error}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              
              {errors.password && (
                <p className="mt-1 text-sm text-status-error">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-text-primary mb-2">
                Confirm new password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockClosedIcon className="h-5 w-5 text-text-muted" />
                </div>
                <input
                  {...register('confirmPassword')}
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  autoComplete="new-password"
                  className={`
                    block w-full pl-10 pr-10 py-3 border rounded-lg
                    focus:ring-2 focus:ring-primary-green focus:border-primary-green
                    ${errors.confirmPassword 
                      ? 'border-status-error focus:ring-status-error focus:border-status-error' 
                      : 'border-border-medium'
                    }
                  `}
                  placeholder="Confirm your new password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-text-muted hover:text-text-primary" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-text-muted hover:text-text-primary" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-status-error">{errors.confirmPassword.message}</p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting || isLoading || (passwordStrength ? !passwordStrength.isValid : false)}
              className="w-full btn-primary py-3 text-base font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting || isLoading ? (
                <div className="flex items-center justify-center">
                  <LoadingSpinner size="sm" color="white" className="mr-2" />
                  Resetting password...
                </div>
              ) : (
                'Reset password'
              )}
            </button>
          </form>

          {/* Back to Login */}
          <div className="mt-6 text-center">
            <Link
              href="/auth/login"
              className="text-sm text-primary-green hover:text-primary-greenLight font-medium"
            >
              Back to login
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}