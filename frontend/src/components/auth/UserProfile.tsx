'use client'

import { useState, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { 
  UserIcon, 
  EnvelopeIcon, 
  CameraIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '@/lib/auth/AuthProvider'
import { useAuthStore } from '@/lib/auth/authStore'
import { AuthAPI } from '@/lib/api/auth'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import toast from 'react-hot-toast'

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  display_name: z.string().optional(),
  email: z.string().email('Please enter a valid email address')
})

type ProfileFormData = z.infer<typeof profileSchema>

interface UserProfileProps {
  onClose?: () => void
  className?: string
}

export default function UserProfile({ onClose, className = '' }: UserProfileProps) {
  const { user } = useAuth()
  const { refreshUser, isLoading } = useAuthStore()
  const [isEditing, setIsEditing] = useState(false)
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: user?.name || '',
      display_name: user?.display_name || '',
      email: user?.email || ''
    }
  })

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast.error('Please select an image file')
        return
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Image must be less than 5MB')
        return
      }

      setAvatarFile(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        setAvatarPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const onSubmit = async (data: ProfileFormData) => {
    try {
      // Update profile data
      const updatedUser = await AuthAPI.updateProfile({
        name: data.name,
        display_name: data.display_name || data.name,
        email: data.email
      })

      // TODO: Handle avatar upload when backend supports it
      if (avatarFile) {
        // This would be implemented when the backend supports file uploads
        console.log('Avatar upload would happen here:', avatarFile)
      }

      // Refresh user data
      await refreshUser()
      
      setIsEditing(false)
      setAvatarFile(null)
      setAvatarPreview(null)
      
      toast.success('Profile updated successfully!')
    } catch (error: any) {
      toast.error(error.message || 'Failed to update profile')
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    setAvatarFile(null)
    setAvatarPreview(null)
    reset({
      name: user?.name || '',
      display_name: user?.display_name || '',
      email: user?.email || ''
    })
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-2xl shadow-lg p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-text-primary">Profile Settings</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 hover:bg-bg-secondary rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5 text-text-muted" />
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Avatar Section */}
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-gradient-primary flex items-center justify-center overflow-hidden">
              {avatarPreview || user.profile_picture_url ? (
                <img
                  src={avatarPreview || user.profile_picture_url}
                  alt="Profile"
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-white font-bold text-2xl">
                  {(user.display_name || user.name || user.email)?.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            
            {isEditing && (
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="absolute -bottom-1 -right-1 w-8 h-8 bg-primary-green hover:bg-primary-greenLight rounded-full flex items-center justify-center transition-colors"
              >
                <CameraIcon className="w-4 h-4 text-white" />
              </button>
            )}
          </div>

          <div>
            <h3 className="font-semibold text-text-primary">
              {user.display_name || user.name || 'User'}
            </h3>
            <p className="text-sm text-text-secondary">{user.email}</p>
            {user.email_verified ? (
              <div className="flex items-center mt-1">
                <CheckCircleIcon className="w-4 h-4 text-status-success mr-1" />
                <span className="text-xs text-status-success">Email verified</span>
              </div>
            ) : (
              <div className="flex items-center mt-1">
                <span className="text-xs text-status-warning">Email not verified</span>
              </div>
            )}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleAvatarChange}
            className="hidden"
          />
        </div>

        {/* Form Fields */}
        <div className="space-y-4">
          {/* Name Field */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-text-primary mb-2">
              Full Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <UserIcon className="h-5 w-5 text-text-muted" />
              </div>
              <input
                {...register('name')}
                type="text"
                id="name"
                disabled={!isEditing}
                className={`
                  block w-full pl-10 pr-3 py-3 border rounded-lg
                  ${isEditing 
                    ? 'focus:ring-2 focus:ring-primary-green focus:border-primary-green' 
                    : 'bg-bg-secondary cursor-not-allowed'
                  }
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

          {/* Display Name Field */}
          <div>
            <label htmlFor="display_name" className="block text-sm font-medium text-text-primary mb-2">
              Display Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <UserIcon className="h-5 w-5 text-text-muted" />
              </div>
              <input
                {...register('display_name')}
                type="text"
                id="display_name"
                disabled={!isEditing}
                className={`
                  block w-full pl-10 pr-3 py-3 border rounded-lg
                  ${isEditing 
                    ? 'focus:ring-2 focus:ring-primary-green focus:border-primary-green' 
                    : 'bg-bg-secondary cursor-not-allowed'
                  }
                  ${errors.display_name 
                    ? 'border-status-error focus:ring-status-error focus:border-status-error' 
                    : 'border-border-medium'
                  }
                `}
                placeholder="How you'd like to be displayed"
              />
            </div>
            {errors.display_name && (
              <p className="mt-1 text-sm text-status-error">{errors.display_name.message}</p>
            )}
          </div>

          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-2">
              Email Address
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <EnvelopeIcon className="h-5 w-5 text-text-muted" />
              </div>
              <input
                {...register('email')}
                type="email"
                id="email"
                disabled={!isEditing}
                className={`
                  block w-full pl-10 pr-3 py-3 border rounded-lg
                  ${isEditing 
                    ? 'focus:ring-2 focus:ring-primary-green focus:border-primary-green' 
                    : 'bg-bg-secondary cursor-not-allowed'
                  }
                  ${errors.email 
                    ? 'border-status-error focus:ring-status-error focus:border-status-error' 
                    : 'border-border-medium'
                  }
                `}
                placeholder="Enter your email address"
              />
            </div>
            {errors.email && (
              <p className="mt-1 text-sm text-status-error">{errors.email.message}</p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-border-light">
          {isEditing ? (
            <>
              <button
                type="button"
                onClick={handleCancel}
                disabled={isSubmitting || isLoading}
                className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary border border-border-medium hover:border-border-dark rounded-lg transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || isLoading}
                className="px-4 py-2 text-sm font-medium bg-primary-green hover:bg-primary-greenLight text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting || isLoading ? (
                  <div className="flex items-center">
                    <LoadingSpinner size="sm" color="white" className="mr-2" />
                    Saving...
                  </div>
                ) : (
                  'Save Changes'
                )}
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 text-sm font-medium bg-primary-green hover:bg-primary-greenLight text-white rounded-lg transition-colors"
            >
              Edit Profile
            </button>
          )}
        </div>
      </form>
    </div>
  )
}