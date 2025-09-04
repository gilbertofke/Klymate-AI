'use client'

import { useState, useEffect } from 'react'
import { auth } from '@/lib/auth/firebase'

export default function FirebaseStatus() {
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null)
  const [projectId, setProjectId] = useState<string | null>(null)

  useEffect(() => {
    // Check Firebase configuration
    const checkConfig = () => {
      if (auth) {
        setIsConfigured(true)
        setProjectId(auth.app.options.projectId || null)
      } else {
        setIsConfigured(false)
      }
    }

    // Check immediately and after a delay
    checkConfig()
    const timer = setTimeout(checkConfig, 1000)

    return () => clearTimeout(timer)
  }, [])

  // Only show in development
  if (process.env.NODE_ENV !== 'development') {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className={`
        px-3 py-2 rounded-lg text-sm font-medium shadow-lg
        ${isConfigured === true 
          ? 'bg-green-100 text-green-800 border border-green-200' 
          : isConfigured === false 
          ? 'bg-red-100 text-red-800 border border-red-200'
          : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
        }
      `}>
        <div className="flex items-center space-x-2">
          <div className={`
            w-2 h-2 rounded-full
            ${isConfigured === true 
              ? 'bg-green-500' 
              : isConfigured === false 
              ? 'bg-red-500'
              : 'bg-yellow-500'
            }
          `} />
          <span>
            {isConfigured === true 
              ? `Firebase: ${projectId || 'Connected'}` 
              : isConfigured === false 
              ? 'Firebase: Not Configured'
              : 'Firebase: Checking...'
            }
          </span>
        </div>
        {isConfigured === false && (
          <div className="text-xs mt-1 opacity-75">
            Check .env.local file
          </div>
        )}
      </div>
    </div>
  )
}