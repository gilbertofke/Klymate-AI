'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, Edit, Sparkles, ArrowRight } from 'lucide-react'
import { ErrorDisplay } from '@/components/ui/ErrorDisplay'
import { cn } from '@/lib/utils'
import type { OnboardingData } from '@/types'
import type { ErrorInfo } from '@/lib/utils/errorHandling'

interface CompletionStepProps {
  data: Partial<OnboardingData>
  onComplete: () => void
  onPrevious: () => void
  isLoading?: boolean
  error?: ErrorInfo | null
}

export function CompletionStep({ data, onComplete, onPrevious, isLoading, error }: CompletionStepProps) {
  const [showFullSummary, setShowFullSummary] = useState(false)
  
  // Helper functions to get display values
  const getDisplayValue = (value: any, fallback = 'Not specified'): string => {
    if (Array.isArray(value)) {
      return value.length > 0 ? `${value.length} selected` : fallback
    }
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No'
    }
    if (typeof value === 'string' && value) {
      return value.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
    if (typeof value === 'number') {
      return value.toString()
    }
    return fallback
  }
  
  const summaryData = [
    {
      category: 'Profile',
      icon: '👤',
      items: [
        { label: 'Location', value: getDisplayValue(data.location) },
        { label: 'Household Size', value: data.household_size ? `${data.household_size} ${data.household_size === 1 ? 'person' : 'people'}` : 'Not specified' },
        { label: 'Income Level', value: getDisplayValue(data.income_level) },
        { label: 'Lifestyle Goals', value: getDisplayValue(data.lifestyle_goals) },
      ]
    },
    {
      category: 'Transportation',
      icon: '🚗',
      items: [
        { label: 'Primary Transport', value: getDisplayValue(data.primary_transport) },
        { label: 'Daily Commute', value: data.commute_distance ? `${data.commute_distance} km` : 'Not specified' },
        { label: 'Vehicle Type', value: getDisplayValue(data.vehicle_type) },
        { label: 'Public Transport Usage', value: getDisplayValue(data.public_transport_usage) },
        { label: 'Travel Frequency', value: getDisplayValue(data.travel_frequency) },
      ]
    },
    {
      category: 'Energy',
      icon: '⚡',
      items: [
        { label: 'Home Type', value: getDisplayValue(data.home_type) },
        { label: 'Home Size', value: getDisplayValue(data.home_size) },
        { label: 'Heating Type', value: getDisplayValue(data.heating_type) },
        { label: 'Cooling Methods', value: getDisplayValue(data.cooling_preferences) },
        { label: 'Renewable Interest', value: getDisplayValue(data.renewable_energy_interest) },
      ]
    },
    {
      category: 'Diet',
      icon: '🍽️',
      items: [
        { label: 'Diet Type', value: getDisplayValue(data.diet_type) },
        { label: 'Meals Per Day', value: data.meal_frequency ? `${data.meal_frequency} meals` : 'Not specified' },
        { label: 'Meal Patterns', value: getDisplayValue(data.meal_patterns) },
        { label: 'Local Food Preference', value: getDisplayValue(data.local_food_preference) },
        { label: 'Organic Food Preference', value: getDisplayValue(data.organic_food_preference) },
      ]
    }
  ]
  
  const completionPercentage = Math.round(
    (Object.values(data).filter(value => 
      value !== undefined && 
      value !== null && 
      value !== '' && 
      !(Array.isArray(value) && value.length === 0)
    ).length / Object.keys(data).length) * 100
  )
  
  return (
    <div className="space-y-8">
      <div className="text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", duration: 0.6 }}
          className="w-20 h-20 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6"
        >
          <CheckCircle className="w-10 h-10 text-white" />
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-3">
            You're All Set!
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-2">
            Your personalized climate profile is ready
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
            <Sparkles className="w-4 h-4" />
            <span>Profile {completionPercentage}% complete</span>
          </div>
        </motion.div>
      </div>
      
      {/* Progress Indicator */}
      <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Profile Completion
          </span>
          <span className="text-sm font-semibold text-green-600">
            {completionPercentage}%
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <motion.div
            className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${completionPercentage}%` }}
            transition={{ duration: 1, delay: 0.5 }}
          />
        </div>
      </div>
      
      {/* Summary Preview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Your Profile Summary
            </h3>
            <button
              onClick={() => setShowFullSummary(!showFullSummary)}
              className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 transition-colors"
            >
              <Edit className="w-4 h-4" />
              {showFullSummary ? 'Hide Details' : 'View Details'}
            </button>
          </div>
        </div>
        
        <div className="p-4">
          {showFullSummary ? (
            <div className="space-y-6">
              {summaryData.map((section) => (
                <div key={section.category}>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xl">{section.icon}</span>
                    <h4 className="font-medium text-gray-900 dark:text-gray-100">
                      {section.category}
                    </h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 ml-7">
                    {section.items.map((item) => (
                      <div key={item.label} className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {item.label}:
                        </span>
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {item.value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {summaryData.map((section) => (
                <div key={section.category} className="text-center">
                  <div className="text-2xl mb-2">{section.icon}</div>
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {section.category}
                  </div>
                  <div className="text-xs text-green-600">
                    ✓ Complete
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* What's Next */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg p-6 border border-green-200 dark:border-green-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          What's Next?
        </h3>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-white text-xs font-bold">1</span>
            </div>
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">
                Personalized Dashboard
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Access your customized climate dashboard with AI-powered insights
              </div>
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-white text-xs font-bold">2</span>
            </div>
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">
                AI Coach Recommendations
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Get personalized suggestions based on your profile and goals
              </div>
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-white text-xs font-bold">3</span>
            </div>
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">
                Track Your Progress
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Log habits, earn badges, and see your environmental impact
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Enhanced Error Display */}
      {error && (
        <ErrorDisplay
          error={error}
          onRetry={error.retryable ? onComplete : undefined}
          compact={false}
        />
      )}
      
      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-4">
        <button
          onClick={onPrevious}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Edit className="w-4 h-4" />
          Edit Profile
        </button>
        
        <motion.button
          onClick={onComplete}
          disabled={isLoading}
          className={cn(
            'flex items-center gap-2 px-8 py-3 rounded-lg font-medium transition-all',
            'bg-gradient-to-r from-green-500 to-blue-500 text-white',
            'hover:from-green-600 hover:to-blue-600',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'shadow-lg hover:shadow-xl'
          )}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Setting up your dashboard...
            </>
          ) : (
            <>
              Complete Setup
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </motion.button>
      </div>
      
      {/* Privacy Notice */}
      <div className="text-center">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Your data is encrypted and secure. You can update your preferences anytime in settings.
        </p>
      </div>
    </div>
  )
}