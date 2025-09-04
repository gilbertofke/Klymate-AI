'use client'

import { useState } from 'react'
import { useAuthStore } from '@/lib/auth/authStore'
import { useAuth } from '@/lib/auth/AuthProvider'

export function OnboardingStateTest() {
  const { user } = useAuth()
  const { setUser, refreshUser, debouncedRefreshUser } = useAuthStore()
  const [testLog, setTestLog] = useState<string[]>([])

  const addLog = (message: string) => {
    setTestLog(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const testOptimisticUpdate = () => {
    if (!user) return
    
    addLog('Testing optimistic update...')
    
    // Simulate optimistic update
    setUser({
      ...user,
      onboarding_completed: !user.onboarding_completed
    })
    
    addLog(`Optimistically updated onboarding_completed to: ${!user.onboarding_completed}`)
  }

  const testRefreshUser = async () => {
    addLog('Testing refresh user...')
    try {
      await refreshUser()
      addLog('User refreshed successfully')
    } catch (error) {
      addLog(`Refresh failed: ${error}`)
    }
  }

  const testDebouncedRefresh = async () => {
    addLog('Testing debounced refresh (multiple calls)...')
    try {
      // Make multiple rapid calls
      const promises = [
        debouncedRefreshUser(100),
        debouncedRefreshUser(100),
        debouncedRefreshUser(100)
      ]
      
      await Promise.all(promises)
      addLog('Debounced refresh completed')
    } catch (error) {
      addLog(`Debounced refresh failed: ${error}`)
    }
  }

  const clearLog = () => {
    setTestLog([])
  }

  if (!user) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-800">Please log in to test onboarding state synchronization</p>
      </div>
    )
  }

  return (
    <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Onboarding State Synchronization Test</h3>
      
      <div className="mb-4 p-3 bg-gray-50 rounded">
        <h4 className="font-medium mb-2">Current User State:</h4>
        <p><strong>ID:</strong> {user.id}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Onboarding Completed:</strong> {user.onboarding_completed ? 'Yes' : 'No'}</p>
      </div>

      <div className="space-y-2 mb-4">
        <button
          onClick={testOptimisticUpdate}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 mr-2"
        >
          Test Optimistic Update
        </button>
        
        <button
          onClick={testRefreshUser}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 mr-2"
        >
          Test Refresh User
        </button>
        
        <button
          onClick={testDebouncedRefresh}
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 mr-2"
        >
          Test Debounced Refresh
        </button>
        
        <button
          onClick={clearLog}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Clear Log
        </button>
      </div>

      <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm max-h-64 overflow-y-auto">
        <h4 className="text-white mb-2">Test Log:</h4>
        {testLog.length === 0 ? (
          <p className="text-gray-500">No tests run yet...</p>
        ) : (
          testLog.map((log, index) => (
            <div key={index}>{log}</div>
          ))
        )}
      </div>
    </div>
  )
}