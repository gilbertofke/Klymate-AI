'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { ChevronLeft, ChevronRight, Check } from 'lucide-react'
import { useAuth } from '@/lib/auth/AuthProvider'

interface OnboardingData {
  name: string
  age: string
  location: string
  transport: string
  homeType: string
  diet: string
}

const steps = [
  { id: 'profile', title: 'Profile', description: 'Tell us about yourself' },
  { id: 'transport', title: 'Transportation', description: 'How do you get around?' },
  { id: 'energy', title: 'Energy', description: 'How do you power your home?' },
  { id: 'diet', title: 'Diet', description: 'What do you eat?' },
  { id: 'complete', title: 'Complete', description: 'Finish setup' },
]

export default function SimpleOnboardingPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [currentStep, setCurrentStep] = useState(0)
  const [data, setData] = useState<OnboardingData>({
    name: user?.displayName || '',
    age: '',
    location: '',
    transport: '',
    homeType: '',
    diet: ''
  })

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleComplete = async () => {
    try {
      // Simulate API call
      console.log('Completing onboarding with data:', data)
      
      // Redirect to dashboard
      router.push('/dashboard')
    } catch (error) {
      console.error('Onboarding failed:', error)
    }
  }

  const updateData = (field: keyof OnboardingData, value: string) => {
    setData(prev => ({ ...prev, [field]: value }))
  }

  const renderStep = () => {
    const step = steps[currentStep]
    
    switch (step.id) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={data.name}
                onChange={(e) => updateData('name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                placeholder="Enter your full name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Age
              </label>
              <select
                value={data.age}
                onChange={(e) => updateData('age', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                <option value="">Select your age range</option>
                <option value="18-25">18-25</option>
                <option value="26-35">26-35</option>
                <option value="36-45">36-45</option>
                <option value="46-55">46-55</option>
                <option value="56+">56+</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <input
                type="text"
                value={data.location}
                onChange={(e) => updateData('location', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                placeholder="City, Country"
              />
            </div>
          </div>
        )
      
      case 'transport':
        return (
          <div className="space-y-4">
            <p className="text-gray-600 mb-4">How do you primarily get around?</p>
            {['Car', 'Public Transport', 'Bicycle', 'Walking', 'Mixed'].map((option) => (
              <label key={option} className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="transport"
                  value={option.toLowerCase().replace(' ', '_')}
                  checked={data.transport === option.toLowerCase().replace(' ', '_')}
                  onChange={(e) => updateData('transport', e.target.value)}
                  className="w-4 h-4 text-green-600 focus:ring-green-500"
                />
                <span className="text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        )
      
      case 'energy':
        return (
          <div className="space-y-4">
            <p className="text-gray-600 mb-4">What type of home do you live in?</p>
            {['Apartment', 'House', 'Condo', 'Other'].map((option) => (
              <label key={option} className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="homeType"
                  value={option.toLowerCase()}
                  checked={data.homeType === option.toLowerCase()}
                  onChange={(e) => updateData('homeType', e.target.value)}
                  className="w-4 h-4 text-green-600 focus:ring-green-500"
                />
                <span className="text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        )
      
      case 'diet':
        return (
          <div className="space-y-4">
            <p className="text-gray-600 mb-4">What best describes your diet?</p>
            {['Omnivore', 'Vegetarian', 'Vegan', 'Pescatarian', 'Flexitarian'].map((option) => (
              <label key={option} className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="diet"
                  value={option.toLowerCase()}
                  checked={data.diet === option.toLowerCase()}
                  onChange={(e) => updateData('diet', e.target.value)}
                  className="w-4 h-4 text-green-600 focus:ring-green-500"
                />
                <span className="text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        )
      
      case 'complete':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Check className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Almost Done!
              </h3>
              <p className="text-gray-600">
                Review your information and complete your setup.
              </p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div><strong>Name:</strong> {data.name}</div>
              <div><strong>Age:</strong> {data.age}</div>
              <div><strong>Location:</strong> {data.location}</div>
              <div><strong>Transport:</strong> {data.transport}</div>
              <div><strong>Home:</strong> {data.homeType}</div>
              <div><strong>Diet:</strong> {data.diet}</div>
            </div>
            
            <button
              onClick={handleComplete}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white py-3 px-6 rounded-lg font-semibold hover:from-green-600 hover:to-blue-600 transition-all"
            >
              Complete Setup
            </button>
          </div>
        )
      
      default:
        return null
    }
  }

  const progress = ((currentStep + 1) / steps.length) * 100
  const isLastStep = currentStep === steps.length - 1

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome to Klymate AI
            </h1>
            <p className="text-gray-600">
              Let's personalize your climate journey
            </p>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-gray-500 mb-2">
              <span>Step {currentStep + 1} of {steps.length}</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>

          {/* Step Content */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {steps[currentStep].title}
              </h2>
              <p className="text-gray-600">
                {steps[currentStep].description}
              </p>
            </div>

            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              {renderStep()}
            </motion.div>
          </div>

          {/* Navigation */}
          {!isLastStep && (
            <div className="flex justify-between">
              <button
                onClick={handlePrevious}
                disabled={currentStep === 0}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>

              <button
                onClick={handleNext}
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg hover:from-green-600 hover:to-blue-600"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}