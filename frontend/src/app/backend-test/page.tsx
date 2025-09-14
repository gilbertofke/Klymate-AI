'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'
import { 
  useDashboardData, 
  useUserProfile, 
  useAIInsight, 
  useUserStats,
  useCarbonCredits,
  useRecommendations,
  useChatWithAI,
  useLogHabit
} from '@/lib/hooks/useApi'

export default function BackendTestPage() {
  const [connectionStatus, setConnectionStatus] = useState<'testing' | 'connected' | 'failed'>('testing')
  const [testResults, setTestResults] = useState<any[]>([])
  const [chatMessage, setChatMessage] = useState('How can I reduce my carbon footprint?')
  const [chatResponse, setChatResponse] = useState('')

  // API hooks for testing
  const { data: dashboardData, loading: dashboardLoading, error: dashboardError } = useDashboardData()
  const { data: userProfile, loading: profileLoading, error: profileError } = useUserProfile()
  const { data: aiInsight, loading: aiLoading, error: aiError } = useAIInsight()
  const { data: userStats, loading: statsLoading, error: statsError } = useUserStats()
  const { data: carbonCredits, loading: creditsLoading, error: creditsError } = useCarbonCredits()
  const { data: recommendations, loading: recommendationsLoading, error: recommendationsError } = useRecommendations()
  
  const { sendMessage: chatWithAI, loading: chatLoading, error: chatError } = useChatWithAI()
  const { logHabit, loading: habitLoading, error: habitError } = useLogHabit()

  // Test backend connection
  useEffect(() => {
    const testConnection = async () => {
      try {
        const result = await apiClient.healthCheck()
        if (result.error) {
          setConnectionStatus('failed')
        } else {
          setConnectionStatus('connected')
        }
      } catch (error) {
        setConnectionStatus('failed')
      }
    }

    testConnection()
  }, [])

  // Collect all test results
  useEffect(() => {
    const results = [
      { name: 'Dashboard Data', loading: dashboardLoading, data: dashboardData, error: dashboardError },
      { name: 'User Profile', loading: profileLoading, data: userProfile, error: profileError },
      { name: 'AI Insight', loading: aiLoading, data: aiInsight, error: aiError },
      { name: 'User Stats', loading: statsLoading, data: userStats, error: statsError },
      { name: 'Carbon Credits', loading: creditsLoading, data: carbonCredits, error: creditsError },
      { name: 'Recommendations', loading: recommendationsLoading, data: recommendations, error: recommendationsError }
    ]
    setTestResults(results)
  }, [
    dashboardLoading, dashboardData, dashboardError,
    profileLoading, userProfile, profileError,
    aiLoading, aiInsight, aiError,
    statsLoading, userStats, statsError,
    creditsLoading, carbonCredits, creditsError,
    recommendationsLoading, recommendations, recommendationsError
  ])

  const handleChatTest = async () => {
    try {
      const response = await chatWithAI(chatMessage)
      setChatResponse(JSON.stringify(response, null, 2))
    } catch (error: any) {
      setChatResponse(`Error: ${error.message}`)
    }
  }

  const handleHabitTest = async () => {
    try {
      const habitData = {
        type: 'transport' as const,
        activity: 'Walked to work',
        impact: -2.5,
        date: new Date().toISOString().split('T')[0],
        notes: 'Test habit from frontend'
      }
      const response = await logHabit(habitData)
      alert(`Habit logged successfully: ${JSON.stringify(response)}`)
    } catch (error: any) {
      alert(`Habit logging failed: ${error.message}`)
    }
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'system-ui' }}>
      <h1 style={{ fontSize: '32px', marginBottom: '20px' }}>🔧 Backend API Test Dashboard</h1>
      
      {/* Connection Status */}
      <div style={{ 
        padding: '16px', 
        marginBottom: '20px', 
        borderRadius: '8px',
        backgroundColor: connectionStatus === 'connected' ? '#d4edda' : connectionStatus === 'failed' ? '#f8d7da' : '#fff3cd',
        border: `1px solid ${connectionStatus === 'connected' ? '#c3e6cb' : connectionStatus === 'failed' ? '#f5c6cb' : '#ffeaa7'}`
      }}>
        <h3>Backend Connection Status: 
          <span style={{ 
            color: connectionStatus === 'connected' ? '#155724' : connectionStatus === 'failed' ? '#721c24' : '#856404',
            marginLeft: '10px'
          }}>
            {connectionStatus === 'connected' ? '✅ Connected' : connectionStatus === 'failed' ? '❌ Failed' : '⏳ Testing...'}
          </span>
        </h3>
        <p>Backend URL: <code>{process.env.NEXT_PUBLIC_API_URL}</code></p>
      </div>

      {/* API Endpoints Test Results */}
      <div style={{ marginBottom: '30px' }}>
        <h2>📡 API Endpoints Test Results</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          {testResults.map((result, index) => (
            <div key={index} style={{
              padding: '16px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              backgroundColor: result.error ? '#fff5f5' : result.data ? '#f0fff4' : '#fffbf0'
            }}>
              <h4 style={{ margin: '0 0 8px 0' }}>{result.name}</h4>
              <p><strong>Status:</strong> {result.loading ? '⏳ Loading...' : result.error ? '❌ Error' : result.data ? '✅ Success' : '⚪ No Data'}</p>
              {result.error && <p style={{ color: '#d32f2f', fontSize: '12px' }}><strong>Error:</strong> {result.error}</p>}
              {result.data && (
                <details style={{ marginTop: '8px' }}>
                  <summary style={{ cursor: 'pointer', fontSize: '12px' }}>View Data</summary>
                  <pre style={{ fontSize: '10px', overflow: 'auto', maxHeight: '100px', backgroundColor: '#f5f5f5', padding: '8px', marginTop: '4px' }}>
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* AI Chat Test */}
      <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h2>🤖 AI Coaching Test</h2>
        <div style={{ marginBottom: '16px' }}>
          <input
            type="text"
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
            placeholder="Ask the AI coach something..."
            style={{ width: '70%', padding: '8px', marginRight: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <button 
            onClick={handleChatTest}
            disabled={chatLoading}
            style={{ 
              padding: '8px 16px', 
              backgroundColor: '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: chatLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {chatLoading ? 'Sending...' : 'Send Message'}
          </button>
        </div>
        {chatError && <p style={{ color: '#d32f2f' }}>Error: {chatError}</p>}
        {chatResponse && (
          <div style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px', marginTop: '10px' }}>
            <strong>AI Response:</strong>
            <pre style={{ whiteSpace: 'pre-wrap', fontSize: '14px', marginTop: '8px' }}>{chatResponse}</pre>
          </div>
        )}
      </div>

      {/* Habit Logging Test */}
      <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h2>📝 Habit Logging Test</h2>
        <button 
          onClick={handleHabitTest}
          disabled={habitLoading}
          style={{ 
            padding: '12px 24px', 
            backgroundColor: '#28a745', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: habitLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {habitLoading ? 'Logging...' : 'Log Test Habit (Walk to Work)'}
        </button>
        {habitError && <p style={{ color: '#d32f2f', marginTop: '10px' }}>Error: {habitError}</p>}
      </div>

      {/* Instructions */}
      <div style={{ padding: '20px', backgroundColor: '#e7f3ff', border: '1px solid #b3d9ff', borderRadius: '8px' }}>
        <h3>🔍 How to Use This Test</h3>
        <ol>
          <li><strong>Check Connection Status:</strong> Ensure backend is running and accessible</li>
          <li><strong>Review API Results:</strong> See which endpoints are working and which have errors</li>
          <li><strong>Test AI Chat:</strong> Try asking the AI coach questions</li>
          <li><strong>Test Habit Logging:</strong> Log a test habit to verify data persistence</li>
          <li><strong>Debug Issues:</strong> Use error messages to identify configuration problems</li>
        </ol>
        <p><strong>Expected:</strong> If backend is running, you should see ✅ Success for most endpoints. If you see errors, check that your backend server is running on the correct port.</p>
      </div>
    </div>
  )
}