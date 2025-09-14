'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function SimpleOnboardingPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    transport: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (isSubmitting) return // Prevent double submission
    
    setIsSubmitting(true)
    console.log('Onboarding data:', formData)
    
    // Save onboarding data and redirect
    console.log('Saving onboarding data:', formData)
    
    // Show success message
    alert('🎉 Welcome to Klymate AI! Taking you to your dashboard...')
    
    // Immediate redirect
    console.log('Redirecting to dashboard...')
    window.location.href = '/dashboard-simple'
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div style={{
      fontFamily: 'system-ui, -apple-system, sans-serif',
      background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '600px',
        margin: '0 auto',
        background: 'white',
        padding: '40px',
        borderRadius: '12px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 'bold',
          marginBottom: '8px',
          color: '#1f2937',
          textAlign: 'center'
        }}>
          Welcome to Klymate AI
        </h1>

        <p style={{
          fontSize: '18px',
          color: '#6b7280',
          marginBottom: '32px',
          textAlign: 'center'
        }}>
          Let's personalize your climate journey
        </p>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '14px',
          color: '#6b7280',
          marginBottom: '8px'
        }}>
          <span>Step 1 of 3</span>
          <span>33% Complete</span>
        </div>

        <div style={{
          width: '100%',
          height: '8px',
          background: '#e5e7eb',
          borderRadius: '4px',
          marginBottom: '32px',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            background: 'linear-gradient(90deg, #10b981 0%, #3b82f6 100%)',
            width: '33%',
            transition: 'width 0.3s'
          }} />
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              marginBottom: '8px',
              color: '#374151'
            }}>
              What's your name?
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Enter your full name"
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                outline: 'none'
              }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              marginBottom: '8px',
              color: '#374151'
            }}>
              Where are you located?
            </label>
            <input
              type="text"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              placeholder="City, Country"
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '16px',
                outline: 'none'
              }}
            />
          </div>

          <div style={{ marginBottom: '32px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              marginBottom: '16px',
              color: '#374151'
            }}>
              How do you primarily get around?
            </label>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }}>
              {[
                { value: 'car', label: 'Car' },
                { value: 'public', label: 'Public Transport' },
                { value: 'bike', label: 'Bicycle' },
                { value: 'walk', label: 'Walking' }
              ].map((option) => (
                <label
                  key={option.value}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    cursor: 'pointer'
                  }}
                >
                  <input
                    type="radio"
                    name="transport"
                    value={option.value}
                    checked={formData.transport === option.value}
                    onChange={(e) => handleInputChange('transport', e.target.value)}
                    style={{ margin: 0 }}
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '16px',
              background: isSubmitting 
                ? 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)'
                : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'transform 0.2s',
              opacity: isSubmitting ? 0.7 : 1
            }}
            onMouseOver={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.transform = 'translateY(-2px)'
              }
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
            {isSubmitting ? 'Completing Setup...' : 'Complete Setup'}
          </button>

          {/* Manual redirect button as backup */}
          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <button
              type="button"
              onClick={() => {
                console.log('Manual redirect clicked')
                window.location.href = '/dashboard-enhanced'
              }}
              style={{
                background: 'none',
                border: '1px solid #d1d5db',
                color: '#6b7280',
                padding: '8px 16px',
                borderRadius: '6px',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Skip to Dashboard →
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}