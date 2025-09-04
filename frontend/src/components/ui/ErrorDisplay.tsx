'use client'

import React from 'react'
import { AlertTriangle, RefreshCw, Wifi, WifiOff, Server, Shield, AlertCircle } from 'lucide-react'
import { ErrorInfo } from '@/lib/utils/errorHandling'
import { cn } from '@/lib/utils'

interface ErrorDisplayProps {
  error: ErrorInfo
  onRetry?: () => void
  onDismiss?: () => void
  className?: string
  compact?: boolean
  showIcon?: boolean
}

const errorIcons = {
  network: WifiOff,
  cors: Wifi,
  validation: AlertCircle,
  auth: Shield,
  server: Server,
  unknown: AlertTriangle,
}

const errorColors = {
  network: 'text-orange-500 bg-orange-50 border-orange-200 dark:bg-orange-900/20 dark:border-orange-800',
  cors: 'text-blue-500 bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800',
  validation: 'text-yellow-500 bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800',
  auth: 'text-purple-500 bg-purple-50 border-purple-200 dark:bg-purple-900/20 dark:border-purple-800',
  server: 'text-red-500 bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800',
  unknown: 'text-gray-500 bg-gray-50 border-gray-200 dark:bg-gray-900/20 dark:border-gray-800',
}

export function ErrorDisplay({
  error,
  onRetry,
  onDismiss,
  className,
  compact = false,
  showIcon = true,
}: ErrorDisplayProps) {
  const Icon = errorIcons[error.type]
  const colorClass = errorColors[error.type]

  if (compact) {
    return (
      <div className={cn(
        'flex items-center gap-2 p-3 rounded-lg border text-sm',
        colorClass,
        className
      )}>
        {showIcon && <Icon className="w-4 h-4 flex-shrink-0" />}
        <span className="flex-1">{error.userMessage}</span>
        {error.retryable && onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-1 px-2 py-1 text-xs font-medium rounded hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </button>
        )}
      </div>
    )
  }

  return (
    <div className={cn(
      'p-4 rounded-lg border',
      colorClass,
      className
    )}>
      <div className="flex items-start gap-3">
        {showIcon && <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />}
        
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-sm mb-1">
            {error.type === 'network' && 'Connection Problem'}
            {error.type === 'cors' && 'Connection Issue'}
            {error.type === 'validation' && 'Input Error'}
            {error.type === 'auth' && 'Authentication Required'}
            {error.type === 'server' && 'Server Error'}
            {error.type === 'unknown' && 'Unexpected Error'}
          </h3>
          
          <p className="text-sm opacity-90 mb-3">
            {error.userMessage}
          </p>

          {error.details && (
            <div className="mb-3">
              <details className="text-xs">
                <summary className="cursor-pointer font-medium mb-1">
                  Error Details
                </summary>
                <div className="pl-2 border-l-2 border-current/20">
                  {typeof error.details === 'string' ? (
                    <p>{error.details}</p>
                  ) : Array.isArray(error.details) ? (
                    <ul className="list-disc list-inside space-y-1">
                      {error.details.map((detail, index) => (
                        <li key={index}>{detail}</li>
                      ))}
                    </ul>
                  ) : (
                    <pre className="whitespace-pre-wrap font-mono text-xs">
                      {JSON.stringify(error.details, null, 2)}
                    </pre>
                  )}
                </div>
              </details>
            </div>
          )}

          <div className="flex items-center gap-2">
            {error.retryable && onRetry && (
              <button
                onClick={onRetry}
                className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md bg-current/10 hover:bg-current/20 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
              </button>
            )}
            
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="px-3 py-1.5 text-sm font-medium rounded-md hover:bg-current/10 transition-colors"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

interface ErrorBoundaryFallbackProps {
  error: Error
  onRetry?: () => void
}

export function ErrorBoundaryFallback({ error, onRetry }: ErrorBoundaryFallbackProps) {
  const errorInfo: ErrorInfo = {
    type: 'unknown',
    message: error.message,
    userMessage: 'Something went wrong. Please try refreshing the page.',
    retryable: true,
  }

  return (
    <div className="flex items-center justify-center min-h-[400px] p-8">
      <div className="max-w-md w-full">
        <ErrorDisplay
          error={errorInfo}
          onRetry={onRetry}
          className="text-center"
        />
      </div>
    </div>
  )
}