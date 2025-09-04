'use client'

import { ProtectedRoute } from '@/components/auth/AuthGuard'
import { OnboardingStateTest } from '@/components/dev/OnboardingStateTest'

export default function OnboardingTestPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            Onboarding State Synchronization Test
          </h1>
          
          <div className="mb-8">
            <p className="text-gray-600 mb-4">
              This page allows you to test the onboarding state synchronization functionality.
              Use the buttons below to test different aspects of the state management.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">Test Scenarios:</h3>
              <ul className="text-blue-800 space-y-1">
                <li>• <strong>Optimistic Update:</strong> Immediately updates UI state before API call</li>
                <li>• <strong>Refresh User:</strong> Fetches latest user data from backend</li>
                <li>• <strong>Debounced Refresh:</strong> Tests that multiple rapid calls are properly debounced</li>
              </ul>
            </div>
          </div>

          <OnboardingStateTest />
        </div>
      </div>
    </ProtectedRoute>
  )
}