'use client'

import LoadingSpinner from '@/components/ui/LoadingSpinner'

export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-primary">
      <div className="text-center">
        <LoadingSpinner size="lg" color="white" />
        <p className="mt-4 text-white text-lg">Loading...</p>
      </div>
    </div>
  )
}