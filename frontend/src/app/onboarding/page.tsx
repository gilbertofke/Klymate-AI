'use client'

import { ProtectedRoute } from '@/components/auth/AuthGuard'
import { useRouter } from 'next/navigation'

export default function OnboardingPage() {
  const router = useRouter()

  return (
    <ProtectedRoute>
      <div style={{
        padding: '40px',
        backgroundColor: '#f0f9ff',
        minHeight: '100vh',
        fontFamily: 'system-ui, sans-serif'
      }}>
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          backgroundColor: 'white',
          padding: '40px',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: 'bold',
            marginBottom: '16px',
            color: '#1f2937'
          }}>
            Welcome to Klymate AI
          </h1>

          <p style={{
            fontSize: '18px',
            color: '#6b7280',
            marginBottom: '32px'
          }}>
            Choose your onboarding experience to get started with personalized carbon tracking and AI coaching.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <button
              onClick={() => router.push('/onboarding-enhanced')}
              style={{
                width: '100%',
                padding: '20px',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              <div style={{ fontSize: '18px', marginBottom: '4px' }}>🚀 Enhanced Onboarding</div>
              <div style={{ fontSize: '14px', opacity: '0.9' }}>Complete setup with AI coaching, goals, and personalized recommendations</div>
            </button>

            <button
              onClick={() => router.push('/onboarding-simple')}
              style={{
                width: '100%',
                padding: '20px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              <div style={{ fontSize: '18px', marginBottom: '4px' }}>⚡ Quick Setup</div>
              <div style={{ fontSize: '14px', opacity: '0.9' }}>Basic onboarding to get started quickly</div>
            </button>

            <button
              onClick={() => router.push('/dashboard-enhanced')}
              style={{
                width: '100%',
                padding: '20px',
                backgroundColor: '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              <div style={{ fontSize: '18px', marginBottom: '4px' }}>📊 Skip to Dashboard</div>
              <div style={{ fontSize: '14px', opacity: '0.9' }}>Go directly to your carbon tracking dashboard</div>
            </button>
          </div>

          <div style={{
            marginTop: '24px',
            padding: '16px',
            backgroundColor: '#f3f4f6',
            borderRadius: '6px',
            fontSize: '14px',
            color: '#6b7280'
          }}>
            💡 <strong>Tip:</strong> The Enhanced Onboarding provides the best experience with personalized AI coaching and goal setting.
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}