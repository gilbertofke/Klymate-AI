'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSubmitOnboarding } from '@/lib/hooks/useApi'

interface OnboardingData {
    // Personal Info
    name: string
    location: string
    age_range: string

    // Carbon Baseline Data
    primary_transport: 'car' | 'public_transport' | 'bike' | 'walk' | 'mixed' | ''
    transport_frequency: 'daily' | 'weekly' | 'occasionally' | ''
    home_type: 'apartment' | 'house' | 'condo' | 'other' | ''
    energy_source: 'grid' | 'renewable' | 'mixed' | 'unknown' | ''
    diet_type: 'omnivore' | 'vegetarian' | 'vegan' | 'pescatarian' | 'flexitarian' | ''

    // Goals & Interests (for AI coaching)
    primary_goals: string[]
    interests: string[]
    current_habits: string[]
}

const steps = [
    { id: 'personal', title: 'About You', description: 'Tell us about yourself' },
    { id: 'transport', title: 'Transportation', description: 'How do you get around?' },
    { id: 'home', title: 'Home & Energy', description: 'Your living situation' },
    { id: 'lifestyle', title: 'Lifestyle', description: 'Diet and habits' },
    { id: 'goals', title: 'Your Goals', description: 'What do you want to achieve?' },
    { id: 'complete', title: 'Complete', description: 'Review and start your journey' },
]

export default function EnhancedOnboardingPage() {
    const router = useRouter()
    const { submit: submitOnboarding, loading: isSubmitting, error: submitError } = useSubmitOnboarding()
    const [currentStep, setCurrentStep] = useState(0)
    const [data, setData] = useState<OnboardingData>({
        name: '',
        location: '',
        age_range: '',
        primary_transport: '',
        transport_frequency: '',
        home_type: '',
        energy_source: '',
        diet_type: '',
        primary_goals: [],
        interests: [],
        current_habits: []
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

    const handleSubmit = async () => {
        try {
            // Calculate baseline carbon footprint
            const baselineFootprint = calculateBaselineFootprint(data)

            // Prepare data for backend AI coaching system
            const onboardingPayload = {
                ...data,
                baseline_footprint: baselineFootprint,
            }

            console.log('Sending onboarding data to backend:', onboardingPayload)

            try {
                // Try to send to real backend API
                await submitOnboarding(onboardingPayload)
                console.log('✅ Onboarding data successfully sent to backend!')
            } catch (apiError) {
                console.log('⚠️ Backend not available, storing data locally for now')
                // Store in localStorage as fallback
                localStorage.setItem('klymate_onboarding_data', JSON.stringify(onboardingPayload))
            }
            
            // Always redirect to dashboard (it will handle missing backend gracefully)
            router.push('/dashboard-enhanced')

        } catch (error) {
            console.error('Onboarding submission failed:', error)
            alert(`Onboarding failed: ${error instanceof Error ? error.message : 'Please try again.'}`)
        }
    }

    // Simple carbon footprint estimation (will be replaced by backend calculation)
    const calculateBaselineFootprint = (userData: OnboardingData): number => {
        let footprint = 0

        // Transport (kg CO2/year)
        const transportFactors = {
            car: 4600,
            public_transport: 1200,
            bike: 0,
            walk: 0,
            mixed: 2400
        }

        // Diet (kg CO2/year)
        const dietFactors = {
            omnivore: 1996,
            pescatarian: 1518,
            vegetarian: 1041,
            vegan: 629,
            flexitarian: 1500
        }

        // Home type (kg CO2/year)
        const homeFactors = {
            house: 2300,
            apartment: 1200,
            condo: 1500,
            other: 1500
        }

        footprint += transportFactors[userData.primary_transport] || 0
        footprint += dietFactors[userData.diet_type] || 0
        footprint += homeFactors[userData.home_type] || 0

        return Math.round(footprint)
    }

    const updateData = (field: keyof OnboardingData, value: any) => {
        setData(prev => ({ ...prev, [field]: value }))
    }

    const toggleArrayItem = (field: keyof OnboardingData, item: string) => {
        const currentArray = data[field] as string[]
        const newArray = currentArray.includes(item)
            ? currentArray.filter(i => i !== item)
            : [...currentArray, item]
        updateData(field, newArray)
    }

    const renderStep = () => {
        const step = steps[currentStep]

        switch (step.id) {
            case 'personal':
                return (
                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                What's your name?
                            </label>
                            <input
                                type="text"
                                value={data.name}
                                onChange={(e) => updateData('name', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                placeholder="Enter your full name"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Where are you located?
                            </label>
                            <input
                                type="text"
                                value={data.location}
                                onChange={(e) => updateData('location', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                placeholder="City, Country"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Age Range
                            </label>
                            <select
                                value={data.age_range}
                                onChange={(e) => updateData('age_range', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                                required
                            >
                                <option value="">Select your age range</option>
                                <option value="18-25">18-25</option>
                                <option value="26-35">26-35</option>
                                <option value="36-45">36-45</option>
                                <option value="46-55">46-55</option>
                                <option value="56+">56+</option>
                            </select>
                        </div>
                    </div>
                )

            case 'transport':
                return (
                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-4">
                                What's your primary mode of transportation?
                            </label>
                            <div className="space-y-3">
                                {[
                                    { value: 'car', label: 'Car (personal vehicle)', impact: 'High CO₂ impact' },
                                    { value: 'public_transport', label: 'Public Transport', impact: 'Medium CO₂ impact' },
                                    { value: 'bike', label: 'Bicycle', impact: 'Zero CO₂ impact' },
                                    { value: 'walk', label: 'Walking', impact: 'Zero CO₂ impact' },
                                    { value: 'mixed', label: 'Mixed (varies by day)', impact: 'Variable CO₂ impact' }
                                ].map((option) => (
                                    <label key={option.value} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                                        <div className="flex items-center">
                                            <input
                                                type="radio"
                                                name="transport"
                                                value={option.value}
                                                checked={data.primary_transport === option.value}
                                                onChange={(e) => updateData('primary_transport', e.target.value)}
                                                className="w-4 h-4 text-green-600 focus:ring-green-500"
                                            />
                                            <div className="ml-3">
                                                <div className="font-medium text-gray-900">{option.label}</div>
                                                <div className="text-sm text-gray-500">{option.impact}</div>
                                            </div>
                                        </div>
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                How often do you travel?
                            </label>
                            <select
                                value={data.transport_frequency}
                                onChange={(e) => updateData('transport_frequency', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                            >
                                <option value="">Select frequency</option>
                                <option value="daily">Daily commute</option>
                                <option value="weekly">Few times per week</option>
                                <option value="occasionally">Occasionally</option>
                            </select>
                        </div>
                    </div>
                )

            case 'home':
                return (
                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-4">
                                What type of home do you live in?
                            </label>
                            <div className="grid grid-cols-2 gap-3">
                                {[
                                    { value: 'apartment', label: 'Apartment' },
                                    { value: 'house', label: 'House' },
                                    { value: 'condo', label: 'Condo' },
                                    { value: 'other', label: 'Other' }
                                ].map((option) => (
                                    <label key={option.value} className="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                                        <input
                                            type="radio"
                                            name="homeType"
                                            value={option.value}
                                            checked={data.home_type === option.value}
                                            onChange={(e) => updateData('home_type', e.target.value)}
                                            className="w-4 h-4 text-green-600 focus:ring-green-500"
                                        />
                                        <span className="ml-3 font-medium text-gray-900">{option.label}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                What's your primary energy source?
                            </label>
                            <select
                                value={data.energy_source}
                                onChange={(e) => updateData('energy_source', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                            >
                                <option value="">Select energy source</option>
                                <option value="grid">Standard electricity grid</option>
                                <option value="renewable">Renewable energy (solar, wind)</option>
                                <option value="mixed">Mix of grid and renewable</option>
                                <option value="unknown">Not sure</option>
                            </select>
                        </div>
                    </div>
                )

            case 'lifestyle':
                return (
                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-4">
                                What best describes your diet?
                            </label>
                            <div className="space-y-3">
                                {[
                                    { value: 'omnivore', label: 'Omnivore', desc: 'Eat everything including meat' },
                                    { value: 'flexitarian', label: 'Flexitarian', desc: 'Mostly vegetarian with occasional meat' },
                                    { value: 'pescatarian', label: 'Pescatarian', desc: 'Vegetarian + fish' },
                                    { value: 'vegetarian', label: 'Vegetarian', desc: 'No meat, but dairy and eggs' },
                                    { value: 'vegan', label: 'Vegan', desc: 'No animal products' }
                                ].map((option) => (
                                    <label key={option.value} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                                        <div className="flex items-center">
                                            <input
                                                type="radio"
                                                name="diet"
                                                value={option.value}
                                                checked={data.diet_type === option.value}
                                                onChange={(e) => updateData('diet_type', e.target.value)}
                                                className="w-4 h-4 text-green-600 focus:ring-green-500"
                                            />
                                            <div className="ml-3">
                                                <div className="font-medium text-gray-900">{option.label}</div>
                                                <div className="text-sm text-gray-500">{option.desc}</div>
                                            </div>
                                        </div>
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-3">
                                Current eco-friendly habits (select all that apply)
                            </label>
                            <div className="grid grid-cols-2 gap-2">
                                {[
                                    'Recycling', 'Composting', 'Energy saving', 'Water conservation',
                                    'Sustainable shopping', 'Minimal packaging', 'Second-hand buying', 'Carpooling'
                                ].map((habit) => (
                                    <label key={habit} className="flex items-center p-2 border border-gray-200 rounded cursor-pointer hover:bg-gray-50">
                                        <input
                                            type="checkbox"
                                            checked={data.current_habits.includes(habit)}
                                            onChange={() => toggleArrayItem('current_habits', habit)}
                                            className="w-4 h-4 text-green-600 focus:ring-green-500"
                                        />
                                        <span className="ml-2 text-sm text-gray-700">{habit}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    </div>
                )

            case 'goals':
                return (
                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-3">
                                What are your main climate goals? (select all that apply)
                            </label>
                            <div className="space-y-2">
                                {[
                                    'Reduce carbon footprint by 50%',
                                    'Achieve carbon neutrality',
                                    'Save money on energy bills',
                                    'Adopt sustainable transportation',
                                    'Eat more plant-based meals',
                                    'Reduce waste and consumption',
                                    'Learn about climate impact',
                                    'Earn carbon credits'
                                ].map((goal) => (
                                    <label key={goal} className="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                                        <input
                                            type="checkbox"
                                            checked={data.primary_goals.includes(goal)}
                                            onChange={() => toggleArrayItem('primary_goals', goal)}
                                            className="w-4 h-4 text-green-600 focus:ring-green-500"
                                        />
                                        <span className="ml-3 text-gray-700">{goal}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-3">
                                What interests you most? (select all that apply)
                            </label>
                            <div className="grid grid-cols-2 gap-2">
                                {[
                                    'Climate science', 'Renewable energy', 'Sustainable living',
                                    'Environmental policy', 'Green technology', 'Conservation',
                                    'Sustainable food', 'Eco-friendly products'
                                ].map((interest) => (
                                    <label key={interest} className="flex items-center p-2 border border-gray-200 rounded cursor-pointer hover:bg-gray-50">
                                        <input
                                            type="checkbox"
                                            checked={data.interests.includes(interest)}
                                            onChange={() => toggleArrayItem('interests', interest)}
                                            className="w-4 h-4 text-green-600 focus:ring-green-500"
                                        />
                                        <span className="ml-2 text-sm text-gray-700">{interest}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    </div>
                )

            case 'complete':
                const estimatedFootprint = calculateBaselineFootprint(data)
                return (
                    <div className="space-y-6">
                        <div className="text-center">
                            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                Ready to Start Your Climate Journey!
                            </h3>
                            <p className="text-gray-600">
                                Based on your responses, we've calculated your baseline and prepared personalized AI coaching.
                            </p>
                        </div>

                        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
                            <h4 className="font-semibold text-gray-900 mb-3">Your Climate Profile</h4>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-gray-600">Estimated Annual CO₂:</span>
                                    <div className="font-semibold text-lg">{estimatedFootprint.toLocaleString()} kg</div>
                                </div>
                                <div>
                                    <span className="text-gray-600">Primary Goals:</span>
                                    <div className="font-medium">{data.primary_goals.length} selected</div>
                                </div>
                                <div>
                                    <span className="text-gray-600">Current Habits:</span>
                                    <div className="font-medium">{data.current_habits.length} practices</div>
                                </div>
                                <div>
                                    <span className="text-gray-600">Interests:</span>
                                    <div className="font-medium">{data.interests.length} areas</div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-blue-50 rounded-lg p-4">
                            <h4 className="font-semibold text-blue-900 mb-2">🤖 Your AI Coach is Ready!</h4>
                            <p className="text-blue-800 text-sm">
                                We've prepared personalized recommendations based on your profile.
                                Your AI coach will help you reduce your footprint by focusing on the highest-impact areas.
                            </p>
                        </div>

                        <button
                            onClick={handleSubmit}
                            disabled={isSubmitting}
                            className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white py-4 px-6 rounded-lg font-semibold hover:from-green-600 hover:to-blue-600 transition-all disabled:opacity-50"
                        >
                            {isSubmitting ? (
                                <div className="flex items-center justify-center">
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                    Creating Your Profile...
                                </div>
                            ) : (
                                'Start My Climate Journey 🚀'
                            )}
                        </button>
                    </div>
                )

            default:
                return null
        }
    }

    const progress = ((currentStep + 1) / steps.length) * 100
    const isLastStep = currentStep === steps.length - 1
    const canProceed = () => {
        switch (steps[currentStep].id) {
            case 'personal':
                return data.name && data.location && data.age_range
            case 'transport':
                return data.primary_transport
            case 'home':
                return data.home_type
            case 'lifestyle':
                return data.diet_type
            case 'goals':
                return data.primary_goals.length > 0
            default:
                return true
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
            <div className="container mx-auto px-4 py-8">
                <div className="max-w-3xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">
                            Welcome to Klymate AI
                        </h1>
                        <p className="text-gray-600">
                            Let's create your personalized climate profile for AI-powered coaching
                        </p>
                    </div>

                    {/* Progress Bar */}
                    <div className="mb-8">
                        <div className="flex justify-between text-sm text-gray-500 mb-2">
                            <span>Step {currentStep + 1} of {steps.length}</span>
                            <span>{Math.round(progress)}% Complete</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                                className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${progress}%` }}
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

                        <div className="transition-all duration-300">
                            {renderStep()}
                        </div>
                    </div>

                    {/* Navigation */}
                    {!isLastStep && (
                        <div className="flex justify-between">
                            <button
                                onClick={handlePrevious}
                                disabled={currentStep === 0}
                                className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                </svg>
                                Previous
                            </button>

                            <button
                                onClick={handleNext}
                                disabled={!canProceed()}
                                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg hover:from-green-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Next
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Skip Onboarding Option */}
            <div className="mt-8 text-center">
                <p className="text-gray-500 text-sm mb-2">
                    Want to explore first?
                </p>
                <button
                    onClick={() => router.push('/dashboard-enhanced')}
                    className="text-blue-600 hover:text-blue-800 font-medium underline text-sm"
                >
                    Skip onboarding and explore the dashboard →
                </button>
            </div>
        </div>
    )
}