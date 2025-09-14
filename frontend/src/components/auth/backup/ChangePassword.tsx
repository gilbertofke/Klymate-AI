'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { 
  LockClosedIcon, 
  EyeIcon, 
  EyeSlashIcon,
  XCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { useAuthStore } from '@/lib/auth/authStore'
import { AuthAPI } from '@/lib/api/auth'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/\d/, 'Password must contain at least one number')
    .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Password must contain at least one special character'),
  confirmPassword: z.string()
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
})

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>

interface ChangePasswordProps {
  onClose?: () => void
  onSuccess?: () => void
  className?: string
}

export default function ChangePassword({ onClose, onSuccess, className = '' }: ChangePasswordProps) {
  const { changePassword, isLoading } = useAuthStore()
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
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
    reset
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema)
  })

  const watchNewPassword = watch('newPassword')

  // Update password strength when new password changes
  useEffect(() => {
    if (watchNewPassword) {
      const validation = AuthAPI.validatePassword(watchNewPassword)
      setPasswordStrength(validation)
    } else {
      setPasswordStrength(null)
    }
  }, [watchNewPassword])

  const onSubmit = async (data: ChangePasswordFormData) => {
    try {
      await changePassword(data.currentPassword, data.newPassword)
      
      // Reset form
      reset()
      
      if (onSuccess) {
        onSuccess()
      }
      
      if (onClose) {
        onClose()
      }
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

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`bg-white rounded-2xl shadow-lg p-6 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-text-primary">Change Password</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 hover:bg-bg-secondary rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5 text-text-muted" />
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Current Password Field */}
        <div>
          <label htmlFor="currentPassword" className="block text-sm font-medium text-text-primary mb-2">
            Current Password
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <LockClosedIcon className="h-5 w-5 text-text-muted" />
            </div>
            <input
              {...register('currentPassword')}
              type={showCurrentPassword ? 'text' : 'password'}
              id="currentPassword"
              autoComplete="current-password"
              className={`
                block w-full pl-10 pr-10 py-3 border rounded-lg
                focus:ring-2 focus:ring-primary-green focus:border-primary-green
                ${errors.currentPassword 
                  ? 'border-status-error focus:ring-status-error focus:border-status-error' 
                  : 'border-border-medium'
                }
              `}
              placeholder="Enter your current password"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowCurrentPassword(!showCurrentPassword)}
            >
              {showCurrentPassword ? (
                <EyeSlashIcon className="h-5 w-5 text-text-muted hover:text-text-primary" />
              ) : (
                <EyeIcon className="h-5 w-5 text-text-muted hover:text-text-primary" />
              )}
            </button>
          </div>
          {errors.currentPassword && (
            <p className="mt-1 text-sm text-status-error">{errors.currentPassword.message}</p>
          )}
        </div>

        {/* New Password Field */}
        <div>
          <label htmlFor="newPassword" className="block text-sm font-medium text-text-primary mb-2">
            New Password
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <LockClosedIcon className="h-5 w-5 text-text-muted" />
            </div>
            <input
              {...register('newPassword')}
              type={showNewPassword ? 'text' : 'password'}
              id="newPassword"
              autoComplete="new-password"
              className={`
                block w-full pl-10 pr-10 py-3 border rounded-lg
                focus:ring-2 focus:ring-primary-green focus:border-primary-green
                ${errors.newPassword 
                  ? 'border-status-error focus:ring-status-error focus:border-status-error' 
                  : 'border-border-medium'
                }
              `}
              placeholder="Enter your new password"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowNewPassword(!showNewPassword)}
            >
              {showNewPassword ? (
                <EyeSlashIcon className="h-5 w-5 text-text-muted hover:text-text-primary" />
              ) : (
                <EyeIcon className="h-5 w-5 text-text-muted hover:text-text-primary" />
              )}
            </button>
          </div>
          
          {/* Password Strength Indicator */}
          {passwordStrength && watchNewPassword && (
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
          
          {errors.newPassword && (
            <p className="mt-1 text-sm text-status-error">{errors.newPassword.message}</p>
          )}
        </div>

        {/* Confirm Password Field */}
        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-text-primary mb-2">
            Confirm New Password
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

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-border-light">
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting || isLoading}
              className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary border border-border-medium hover:border-border-dark rounded-lg transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={isSubmitting || isLoading || (passwordStrength ? !passwordStrength.isValid : false)}
            className="px-4 py-2 text-sm font-medium bg-primary-green hover:bg-primary-greenLight text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting || isLoading ? (
              <div className="flex items-center">
                <LoadingSpinner size="sm" color="white" className="mr-2" />
                Changing...
              </div>
            ) : (
              'Change Password'
            )}
          </button>
        </div>
      </form>
    </motion.div>
  )
}