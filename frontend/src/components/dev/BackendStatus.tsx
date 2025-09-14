'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'

export default function BackendStatus() {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')
  const [backendInfo, setBackendInfo] = useState<any>(null)

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const result = await apiClient.healthCheck()
        if (result.data) {
          setStatus('connected')
          setBackendInfo(result.data)
        } else {
          setStatus('disconnected')
        }
      } catch (error) {
        setStatus('disconnected')
      }
    }

    checkBackend()
    const interval = setInterval(checkBackend, 30000) // Check every 30 seconds

    return () => clearInterval(interval)
  }, [])

  // Only show in development
  if (process.env.NODE_ENV !== 'development') {
    return null
  }

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <div className={`
        px-3 py-2 rounded-lg text-sm font-medium shadow-lg
        ${status === 'connected' 
          ? 'bg-green-100 text-green-800 border border-green-200' 
          : status === 'disconnected'
          ? 'bg-red-100 text-red-800 border border-red-200'
          : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
        }
      `}>
        <div className="flex items-center space-x-2">
          <div className={`
            w-2 h-2 rounded-full
            ${status === 'connected' 
              ? 'bg-green-500' 
              : status === 'disconnected'
              ? 'bg-red-500'
              : 'bg-yellow-500 animate-pulse'
            }
          `} />
          <span>
            {status === 'connected' 
              ? `Backend: Connected (${process.env.NEXT_PUBLIC_API_URL})` 
              : status === 'disconnected'
              ? 'Backend: Disconnected'
              : 'Backend: Checking...'
            }
          </span>
        </div>
        {status === 'disconnected' && (
          <div className="text-xs mt-1 opacity-75">
            Using demo data - start backend to see real features
          </div>
        )}
        {status === 'connected' && backendInfo && (
          <div className="text-xs mt-1 opacity-75">
            {backendInfo.message || 'API Ready'}
          </div>
        )}
      </div>
    </div>
  )
}