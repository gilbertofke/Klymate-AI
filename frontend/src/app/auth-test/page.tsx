'use client'

import { useState } from 'react'
import { useAuthStore } from '@/lib/auth/authStore'
import { useAuth } from '@/lib/auth/AuthProvider'

export default function AuthTestPage() {
  const [email, setEmail] = useState('test@example.com')
  const [password, setPassword] = useState('password123')
  const [result, setResult] = useState('')
  
  const { loginWithEmail, signInWithGoogle, loading, error } = useAuthStore()
  const { user, isAuthenticated } = useAuth()

  const testEmailLogin = async () => {
    try {
      setResult('Testing email login...')
      await loginWithEmail({ email, password })
      setResult('Email login successful!')
    } catch (error: any) {
      setResult(`Email login failed: ${error.message}`)
    }
  }

  const testGoogleLogin = async () => {
    try {
      setResult('Testing Google login...')
      await signInWithGoogle()
      setResult('Google login successful!')
    } catch (error: any) {
      setResult(`Google login failed: ${error.message}`)
    }
  }

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Authentication Test Page</h1>
      
      <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#f5f5f5' }}>
        <h3>Current Auth State:</h3>
        <p>User: {user ? user.email : 'Not logged in'}</p>
        <p>Authenticated: {isAuthenticated ? 'Yes' : 'No'}</p>
        <p>Loading: {loading ? 'Yes' : 'No'}</p>
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>Test Email Login:</h3>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          style={{ padding: '8px', marginRight: '10px', width: '200px' }}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          style={{ padding: '8px', marginRight: '10px', width: '200px' }}
        />
        <button 
          onClick={testEmailLogin}
          disabled={loading}
          style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Test Email Login
        </button>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>Test Google Login:</h3>
        <button 
          onClick={testGoogleLogin}
          disabled={loading}
          style={{ padding: '8px 16px', backgroundColor: '#db4437', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Test Google Login
        </button>
      </div>

      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0' }}>
        <h3>Test Result:</h3>
        <p>{result}</p>
      </div>
    </div>
  )
}