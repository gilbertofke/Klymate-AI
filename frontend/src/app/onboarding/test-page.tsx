'use client'

export default function TestOnboardingPage() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Onboarding Test
        </h1>
        <p className="text-gray-600 mb-6">
          If you can see this, the onboarding route is working!
        </p>
        <button 
          onClick={() => window.location.href = '/dashboard'}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          Go to Dashboard
        </button>
      </div>
    </div>
  )
}