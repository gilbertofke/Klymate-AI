'use client'

import React, { useState } from 'react'
import { ErrorDisplay } from '@/components/ui/ErrorDisplay'
import { LoadingIndicator, StageIndicator } from '@/components/ui/LoadingIndicator'
import { categorizeError, createApiRetryManager } from '@/lib/utils/errorHandling'
import { useLoadingState } from '@/lib/utils/loadingStates'

/**
 * Demo component to showcase error handling and loading states
 * This can be used for testing and development purposes
 */
export function ErrorHandlingDemo() {
  const [selectedError, setSelectedError] = useState<string>('')
  const [isRetrying, setIsRetrying] = useState(false)
  const loadingState = useLoadingState()

  const errorExamples = {
    network: {
      code: 'ERR_NETWORK',
      message: 'Network Error'
    },
    cors: {
      response: { status: 0 },
      message: 'Network Error'
    },
    validation: {
      response: {
        status: 422,
        data: {
          detail: 'Validation failed',
          errors: {
            location: ['This field is required'],
            household_size: ['Must be a positive number']
          }
        }
      }
    },
    auth: {
      response: {
        status: 401,
        data: {
          detail: 'Authentication required'
        }
      }
    },
    server: {
      response: {
        status: 500,
        data: {
          detail: 'Internal server error'
        }
      }
    },
    timeout: {
      code: 'ECONNABORTED',
      message: 'timeout of 30000ms exceeded'
    }
  }

  const stages = [
    { key: 'validating', label: 'Validating', completed: true, current: false, error: false },
    { key: 'submitting', label: 'Submitting', completed: true, current: false, error: false },
    { key: 'calculating', label: 'Calculating', completed: false, current: true, error: false },
    { key: 'personalizing', label: 'Personalizing', completed: false, current: false, error: false },
    { key: 'finalizing', label: 'Finalizing', completed: false, current: false, error: false },
  ]

  const handleTestError = (errorType: string) => {
    setSelectedError(errorType)
  }

  const handleTestRetry = async () => {
    setIsRetrying(true)
    
    // Simulate retry with exponential backoff
    const retryManager = createApiRetryManager({ maxAttempts: 3 })
    
    try {
      await retryManager.execute(
        async () => {
          // Simulate API call that might fail
          if (Math.random() < 0.7) {
            throw new Error('Simulated failure')
          }
          return 'Success!'
        },
        (attempt, error) => {
          console.log(`Retry attempt ${attempt}:`, error.message)
        }
      )
      
      setSelectedError('')
      alert('Retry successful!')
    } catch (error) {
      console.error('All retries failed:', error)
    } finally {
      setIsRetrying(false)
    }
  }

  const handleTestLoading = () => {
    loadingState.setLoading(true, { message: 'Testing loading state...' })
    
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      loadingState.setProgress(progress, `Progress: ${progress}%`)
      
      if (progress >= 100) {
        clearInterval(interval)
        loadingState.setLoading(false)
      }
    }, 500)
  }

  const currentError = selectedError ? categorizeError(errorExamples[selectedError as keyof typeof errorExamples]) : null

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-4">Error Handling & Loading States Demo</h1>
        <p className="text-gray-600 dark:text-gray-400">
          This demo showcases the enhanced error handling and loading states implemented for the OnboardingWizard.
        </p>
      </div>

      {/* Error Testing */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">Error Handling</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
          {Object.keys(errorExamples).map((errorType) => (
            <button
              key={errorType}
              onClick={() => handleTestError(errorType)}
              className="px-4 py-2 bg-red-100 hover:bg-red-200 dark:bg-red-900/20 dark:hover:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg transition-colors capitalize"
            >
              {errorType} Error
            </button>
          ))}
        </div>

        {currentError && (
          <div className="mb-4">
            <ErrorDisplay
              error={currentError}
              onRetry={currentError.retryable ? handleTestRetry : undefined}
              onDismiss={() => setSelectedError('')}
            />
          </div>
        )}

        {isRetrying && (
          <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300 text-sm">
              <LoadingIndicator isLoading={true} size="sm" variant="spinner" />
              <span>Testing retry mechanism...</span>
            </div>
          </div>
        )}
      </div>

      {/* Loading States Testing */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">Loading States</h2>
        
        <div className="space-y-4">
          <button
            onClick={handleTestLoading}
            disabled={loadingState.isLoading}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            Test Progress Loading
          </button>

          {loadingState.isLoading && (
            <div className="space-y-4">
              <LoadingIndicator
                isLoading={true}
                progress={loadingState.progress}
                message={loadingState.message}
                variant="progress"
                size="md"
              />
            </div>
          )}
        </div>
      </div>

      {/* Stage Indicator Demo */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">Stage Indicator</h2>
        <StageIndicator stages={stages} />
      </div>

      {/* Loading Variants */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">Loading Variants</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <h3 className="text-sm font-medium mb-2">Spinner</h3>
            <LoadingIndicator isLoading={true} variant="spinner" size="md" />
          </div>
          
          <div className="text-center">
            <h3 className="text-sm font-medium mb-2">Dots</h3>
            <LoadingIndicator isLoading={true} variant="dots" size="md" />
          </div>
          
          <div className="text-center">
            <h3 className="text-sm font-medium mb-2">Pulse</h3>
            <LoadingIndicator isLoading={true} variant="pulse" size="md" />
          </div>
          
          <div className="text-center">
            <h3 className="text-sm font-medium mb-2">Progress</h3>
            <LoadingIndicator 
              isLoading={true} 
              variant="progress" 
              progress={65} 
              message="Loading..."
              size="md" 
            />
          </div>
        </div>
      </div>

      {/* Network Status */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border p-6">
        <h2 className="text-lg font-semibold mb-4">Network Status</h2>
        
        <div className={`p-3 rounded-lg ${
          navigator.onLine 
            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300'
            : 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 text-orange-700 dark:text-orange-300'
        }`}>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              navigator.onLine ? 'bg-green-500' : 'bg-orange-500 animate-pulse'
            }`} />
            <span className="text-sm font-medium">
              {navigator.onLine ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}