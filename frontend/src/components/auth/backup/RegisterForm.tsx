'use client'

import { useState, useEffect } from 'react'
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
  LockClosedIcon,
  UserIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'
import { useAuthStore } from '@/lib/auth/authStore'
import { AuthAPI } from '@/lib/api/auth'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import KlymateLogoButton from '@/components/ui/KlymateLogoButton'
import SocialAuthButtons from './SocialAuthButtons'
import { RegisterCredentials } from '@/types'

// Password validation schema
const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/\d/, 'Password must contain at least one number')
  .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Password must contain at least one special character')

// Registration validation schema
const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: passwordSchema,
  confirmPassword: z.string(),
  acceptTerms: z.boolean().refine(val => val === true, {
    message: 'You must accept the terms and conditions'
  })
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
})

type RegisterFormData = z.infer<typeof registerSchema>

interface RegisterFormProps {
  onSuccess?: () => void
  onError?: (error: string) => void
  redirectTo?: string
  showSocialAuth?: boolean
  className?: string
}

export default function RegisterForm({ 
  onSuccess, 
  onError, 
  redirectTo = '/dashboard',
  showSocialAuth = true,
  className = '' 
}: RegisterFormProps) {
  const router = useRouter()
  const { registerWithEmail, isLoading, error, clearError } = useAuthStore()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState<{
    isValid: boolean
    errors: string[]
    strength: 'weak' | 'medium' | 'strong'
  } | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    setError: setFormError
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      acceptTerms: false
    }
  })

  const watchPassword = watch('password')

  // Update password strength when password changes
  useEffect(() => {
    if (watchPassword) {
      const validation = AuthAPI.validatePassword(watchPassword)
      setPasswordStrength(validation)
    } else {
      setPasswordStrength(null)
    }
  }, [watchPassword])

  const onSubmit = async (data: RegisterFormData) => {
    try {
      clearError()
      
      const credentials: RegisterCredentials = {
        email: data.email,
        password: data.password,
        name: data.name,
        acceptTerms: data.acceptTerms
      }

      const result = await registerWithEmail(credentials)
      
      if (onSuccess) {
        onSuccess()
      } else {
        // Let AuthGuard handle the redirect - new users will go to onboarding
        console.log('Registration successful, AuthGuard will handle redirect')
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Registration failed'
      
      // Set specific field errors if available
      if (err.code === 'auth/email-already-in-use') {
        setFormError('email', { message: 'An account with this email already exists' })
      } else if (err.code === 'auth/invalid-email') {
        setFormError('email', { message: 'Invalid email address' })
      } else if (err.code === 'auth/weak-password') {
        setFormError('password', { message: 'Password is too weak' })
      }
      
      if (onError) {
        onError(errorMessage)
      }
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
          <h1 className="text-2xl font-bold text-text-primary mb-2">Create your account</h1>
          <p className="text-text-secondary">Join Klymate AI and start your climate journey</p>
        </div>

        {/* Social Auth */}
        {showSocialAuth && (
          <div className="mb-6">
            <SocialAuthButtons 
              mode="register" 
              onSuccess={onSuccess}
              onError={onError}
            />
            
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border-light" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-text-muted">Or create account with email</span>
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

        {/* Registration Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Name Field */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-text-primary mb-2">
              Full name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <UserIcon className="h-5 w-5 text-text-muted" />
              </div>
              <input
                {...register('name')}
                type="text"
                id="name"
                autoComplete="name"
                className={`
                  block w-full pl-10 pr-3 py-3 border rounded-lg
                  focus:ring-2 focus:ring-primary-green focus:border-primary-green
                  ${errors.name 
                    ? 'border-status-error focus:ring-status-error focus:border-status-error' 
                    : 'border-border-medium'
                  }
                `}
                placeholder="Enter your full name"
              />
            </div>
            {errors.name && (
              <p className="mt-1 text-sm text-status-error">{errors.name.message}</p>
            )}
          </div>

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
              Confirm password
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
                placeholder="Confirm your password"
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

          {/* Terms and Conditions */}
          <div>
            <div className="flex items-start">
              <input
                {...register('acceptTerms')}
                id="acceptTerms"
                type="checkbox"
                className="h-4 w-4 text-primary-green focus:ring-primary-green border-border-medium rounded mt-1"
              />
              <label htmlFor="acceptTerms" className="ml-2 block text-sm text-text-secondary">
                I agree to the{' '}
                <Link href="/terms" className="text-primary-green hover:text-primary-greenLight">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link href="/privacy" className="text-primary-green hover:text-primary-greenLight">
                  Privacy Policy
                </Link>
              </label>
            </div>
            {errors.acceptTerms && (
              <p className="mt-1 text-sm text-status-error">{errors.acceptTerms.message}</p>
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
                Creating account...
              </div>
            ) : (
              'Create account'
            )}
          </button>
        </form>

        {/* Sign In Link */}
        <div className="mt-6 text-center">
          <p className="text-text-secondary">
            Already have an account?{' '}
            <Link
              href="/auth/login"
              className="text-primary-green hover:text-primary-greenLight font-medium transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}