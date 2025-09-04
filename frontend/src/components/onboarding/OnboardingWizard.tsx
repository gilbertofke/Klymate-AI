'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, Check, Save, X } from 'lucide-react'
import { ProfileStep } from './steps/ProfileStep'
import { TransportStep } from './steps/TransportStep'
import { EnergyStep } from './steps/EnergyStep'
import { DietStep } from './steps/DietStep'
import { CompletionStep } from './steps/CompletionStep'
import { useOnboardingStore } from '@/lib/stores/onboardingStore'
import { useEnhancedOnboarding } from '@/lib/hooks/useEnhancedOnboarding'
import { useAuthStore } from '@/lib/auth/authStore'
import { ErrorDisplay } from '@/components/ui/ErrorDisplay'
import { LoadingIndicator, LoadingOverlay, StageIndicator } from '@/components/ui/LoadingIndicator'
import type { OnboardingData } from '@/types'
import { cn } from '@/lib/utils'

interface OnboardingWizardProps {
  onComplete?: () => void
  className?: string
}

const steps = [
  { id: 'profile', title: 'Profile', description: 'Tell us about yourself' },
  { id: 'transport', title: 'Transportation', description: 'How do you get around?' },
  { id: 'energy', title: 'Energy', description: 'How do you power your home?' },
  { id: 'diet', title: 'Diet', description: 'What do you eat?' },
  { id: 'completion', title: 'Complete', description: 'Review and finish setup' },
]

export function OnboardingWizard({ onComplete, className }: OnboardingWizardProps) {
  const {
    currentStep,
    totalSteps,
    progress,
    collectedData,
    stepValidation,
    nextStep,
    previousStep,
    updateData,
    validateStep,
    canProceed,
    resetOnboarding
  } = useOnboardingStore()
  
  const [isValid, setIsValid] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [showErrorDetails, setShowErrorDetails] = useState(false)
  
  const completeOnboarding = useEnhancedOnboarding({
    maxRetries: 3,
    retryDelay: 1000,
    onSuccess: (result) => {
      console.log('Onboarding completed successfully:', result)
      if (onComplete) {
        onComplete()
      }
    },
    onError: (error) => {
      console.error('Onboarding failed:', error)
    },
    onRetryAttempt: (attempt, error) => {
      console.log(`Retry attempt ${attempt}:`, error)
    },
  })
  
  // Update validation when step validity changes
  useEffect(() => {
    validateStep(currentStep, isValid)
  }, [isValid, currentStep, validateStep])
  
  // Auto-save data periodically
  useEffect(() => {
    const saveInterval = setInterval(() => {
      if (Object.keys(collectedData).length > 0) {
        setIsSaving(true)
        // Simulate save delay
        setTimeout(() => setIsSaving(false), 1000)
      }
    }, 30000) // Save every 30 seconds
    
    return () => clearInterval(saveInterval)
  }, [collectedData])
  
  const handleNext = () => {
    if (canProceed()) {
      nextStep()
      setIsValid(false) // Reset validation for next step
    }
  }
  
  const handlePrevious = () => {
    previousStep()
    setIsValid(stepValidation[currentStep - 1] || false)
  }
  
  const handleComplete = async () => {
    try {
      await completeOnboarding.submitOnboarding(collectedData as OnboardingData)
    } catch (error) {
      // Error is already handled by the enhanced hook
      console.error('Onboarding completion failed:', error)
    }
  }

  const handleRetry = () => {
    if (completeOnboarding.canRetry) {
      handleComplete()
    }
  }

  const handleDismissError = () => {
    completeOnboarding.clearError()
    setShowErrorDetails(false)
  }
  
  const handleSaveProgress = () => {
    setIsSaving(true)
    // Data is automatically persisted via Zustand persist middleware
    setTimeout(() => setIsSaving(false), 1000)
  }
  
  const renderStep = () => {
    const stepIndex = currentStep - 1 // Convert to 0-based index
    
    switch (steps[stepIndex]?.id) {
      case 'profile':
        return (
          <ProfileStep
            data={collectedData}
            onUpdate={updateData}
            onValidChange={setIsValid}
          />
        )
      case 'transport':
        return (
          <TransportStep
            data={collectedData}
            onUpdate={updateData}
            onValidChange={setIsValid}
          />
        )
      case 'energy':
        return (
          <EnergyStep
            data={collectedData}
            onUpdate={updateData}
            onValidChange={setIsValid}
          />
        )
      case 'diet':
        return (
          <DietStep
            data={collectedData}
            onUpdate={updateData}
            onValidChange={setIsValid}
          />
        )
      case 'completion':
        return (
          <CompletionStep
            data={collectedData}
            onComplete={handleComplete}
            onPrevious={handlePrevious}
            isLoading={completeOnboarding.isLoading}
            error={completeOnboarding.error}
          />
        )
      default:
        return null
    }
  }
  
  const isLastStep = currentStep === totalSteps
  const stepIndex = currentStep - 1 // Convert to 0-based index for steps array
  
  return (
    <LoadingOverlay
      isLoading={completeOnboarding.isLoading}
      progress={completeOnboarding.progress}
      message={completeOnboarding.currentMessage}
      stage={completeOnboarding.currentStage}
      className={cn('max-w-4xl mx-auto', className)}
    >
      {/* Enhanced Progress Bar with Stage Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              Welcome to Klymate AI
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Let's personalize your climate journey
            </p>
          </div>
          <div className="flex items-center gap-3">
            {isSaving && (
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <div className="w-3 h-3 border-2 border-gray-300 border-t-green-500 rounded-full animate-spin" />
                Saving...
              </div>
            )}
            <button
              onClick={handleSaveProgress}
              className="flex items-center gap-2 px-3 py-1 text-sm text-gray-600 hover:text-gray-800 transition-colors"
              title="Save progress"
              disabled={completeOnboarding.isLoading}
            >
              <Save className="w-4 h-4" />
              Save
            </button>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Step {currentStep} of {totalSteps}
            </span>
          </div>
        </div>

        {/* Show onboarding stages when completing */}
        {completeOnboarding.isLoading && (
          <div className="mb-6">
            <StageIndicator stages={completeOnboarding.stages} />
          </div>
        )}
        
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <motion.div
            className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
        
        {/* Step Indicators */}
        <div className="flex justify-between mt-4">
          {steps.map((step, index) => {
            const stepNumber = index + 1
            const isCompleted = stepNumber < currentStep
            const isCurrent = stepNumber === currentStep
            const isValid = stepValidation[stepNumber] === true
            
            return (
              <div
                key={step.id}
                className={cn(
                  'flex flex-col items-center text-center cursor-pointer transition-colors',
                  isCompleted || isCurrent ? 'text-blue-600' : 'text-gray-400'
                )}
                onClick={() => {
                  // Allow navigation to completed steps or current step
                  if (stepNumber <= currentStep) {
                    useOnboardingStore.getState().goToStep(stepNumber)
                  }
                }}
              >
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium mb-2 transition-all',
                    isCompleted
                      ? 'bg-gradient-to-r from-green-500 to-blue-500 text-white'
                      : isCurrent
                      ? isValid
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-600 border-2 border-green-500'
                        : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 border-2 border-blue-500'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                  )}
                >
                  {isCompleted ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    stepNumber
                  )}
                </div>
                <span className="text-xs font-medium hidden sm:block">
                  {step.title}
                </span>
                {isCurrent && isValid && (
                  <div className="w-1 h-1 bg-green-500 rounded-full mt-1" />
                )}
              </div>
            )
          })}
        </div>
      </div>
      
      {/* Step Content */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8 min-h-[500px]">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
            {steps[stepIndex]?.title}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {steps[stepIndex]?.description}
          </p>
        </div>
        
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="min-h-[400px]"
          >
            {renderStep()}
          </motion.div>
        </AnimatePresence>
      </div>
      
      {/* Navigation */}
      {!isLastStep && (
        <div className="flex items-center justify-between mt-8">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>
          
          <div className="flex items-center gap-3">
            <div className="text-sm text-gray-500">
              {isValid ? (
                <span className="text-green-600 flex items-center gap-1">
                  <Check className="w-4 h-4" />
                  Ready to continue
                </span>
              ) : (
                'Please complete this step'
              )}
            </div>
            <button
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg hover:from-green-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
      
      {/* Enhanced Error Display */}
      {completeOnboarding.error && (
        <div className="mt-6">
          <ErrorDisplay
            error={completeOnboarding.error}
            onRetry={completeOnboarding.canRetry ? handleRetry : undefined}
            onDismiss={handleDismissError}
            className="mb-4"
          />
          
          {/* Retry Information */}
          {completeOnboarding.isRetrying && (
            <div className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg text-sm text-blue-700 dark:text-blue-300">
              <LoadingIndicator
                isLoading={true}
                size="sm"
                variant="spinner"
              />
              <span>
                Retrying... (Attempt {completeOnboarding.retryCount} of 3)
              </span>
            </div>
          )}
        </div>
      )}

      {/* Network Status Indicator */}
      {!navigator.onLine && (
        <div className="mt-4 p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
          <div className="flex items-center gap-2 text-orange-700 dark:text-orange-300 text-sm">
            <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
            You appear to be offline. Please check your connection.
          </div>
        </div>
      )}
    </LoadingOverlay>
  )
}