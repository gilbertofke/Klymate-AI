'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'

interface ConnectionStatus {
    status: 'checking' | 'connected' | 'disconnected' | 'error'
    message: string
    lastChecked: Date
}

export default function BackendConnectionStatus() {
    const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
        status: 'checking',
        message: 'Checking backend connection...',
        lastChecked: new Date()
    })

    const checkConnection = async () => {
        try {
            setConnectionStatus(prev => ({ ...prev, status: 'checking', message: 'Checking connection...' }))

            // Try multiple endpoints to get a better picture
            const tests = [
                { name: 'Backend Root', test: () => fetch('http://127.0.0.1:8000/') },
                { name: 'API Client', test: () => apiClient.healthCheck() }
            ]

            let successCount = 0
            const results = []

            for (const test of tests) {
                try {
                    const result = await test.test()
                    if (result && (result.ok || result.data)) {
                        successCount++
                        results.push(`✅ ${test.name}`)
                    } else {
                        results.push(`❌ ${test.name}`)
                    }
                } catch (error) {
                    results.push(`❌ ${test.name}: ${error.message}`)
                }
            }

            if (successCount > 0) {
                setConnectionStatus({
                    status: 'connected',
                    message: `Backend connected (${successCount}/${tests.length} tests passed)`,
                    lastChecked: new Date()
                })
            } else {
                setConnectionStatus({
                    status: 'disconnected',
                    message: 'Backend not available - using demo data',
                    lastChecked: new Date()
                })
            }

        } catch (error) {
            setConnectionStatus({
                status: 'error',
                message: `Connection error: ${error.message}`,
                lastChecked: new Date()
            })
        }
    }

    useEffect(() => {
        checkConnection()
        const interval = setInterval(checkConnection, 10000) // Check every 10 seconds
        return () => clearInterval(interval)
    }, [])

    const getStatusColor = () => {
        switch (connectionStatus.status) {
            case 'connected': return 'bg-green-100 border-green-300 text-green-800'
            case 'disconnected': return 'bg-yellow-100 border-yellow-300 text-yellow-800'
            case 'error': return 'bg-red-100 border-red-300 text-red-800'
            default: return 'bg-blue-100 border-blue-300 text-blue-800'
        }
    }

    const getStatusIcon = () => {
        switch (connectionStatus.status) {
            case 'connected': return '✅'
            case 'disconnected': return '⚠️'
            case 'error': return '❌'
            default: return '🔄'
        }
    }

    return (
        <div className={`fixed bottom-4 right-4 p-4 rounded-lg border-2 shadow-lg max-w-sm ${getStatusColor()}`}>
            <div className="flex items-center space-x-2 mb-2">
                <span className="text-lg">{getStatusIcon()}</span>
                <span className="font-semibold">Backend Status</span>
            </div>

            <div className="text-sm mb-2">{connectionStatus.message}</div>

            <div className="text-xs opacity-75">
                Last checked: {connectionStatus.lastChecked.toLocaleTimeString()}
            </div>

            <button
                onClick={checkConnection}
                className="mt-2 px-3 py-1 bg-white bg-opacity-50 rounded text-xs hover:bg-opacity-75 transition-colors"
            >
                Retry Connection
            </button>

            {connectionStatus.status === 'disconnected' && (
                <div className="mt-2 text-xs">
                    <div className="font-medium mb-1">To start backend:</div>
                    <code className="bg-black bg-opacity-20 px-2 py-1 rounded text-xs">
                        cd backend && python -m uvicorn app.main:app --reload
                    </code>
                </div>
            )}
        </div>
    )
}