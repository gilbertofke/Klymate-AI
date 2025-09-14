'use client'

export default function RedirectTestPage() {
  const handleRedirect = () => {
    console.log('Testing redirect...')
    window.location.href = '/dashboard-simple'
  }

  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1>Redirect Test</h1>
      <p>Click the button to test redirect to dashboard-simple</p>
      <button 
        onClick={handleRedirect}
        style={{
          padding: '16px 32px',
          background: '#10b981',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '16px',
          cursor: 'pointer'
        }}
      >
        Go to Dashboard
      </button>
    </div>
  )
}