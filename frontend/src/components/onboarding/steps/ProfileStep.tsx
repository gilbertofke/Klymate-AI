'use client'

import React, { useState, useEffect } from 'react'
import { MapPin, Users, DollarSign, Target, Shield } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { OnboardingData } from '@/types'

interface ProfileStepProps {
  data: Partial<OnboardingData>
  onUpdate: (data: Partial<OnboardingData>) => void
  onValidChange: (isValid: boolean) => void
}

export function ProfileStep({ data, onUpdate, onValidChange }: ProfileStepProps) {
  const [formData, setFormData] = useState({
    location: data.location || '',
    household_size: data.household_size || 1,
    income_level: data.income_level || '' as 'low' | 'medium' | 'high' | '',
    lifestyle_goals: data.lifestyle_goals || [],
    privacy_preferences: data.privacy_preferences || {
      share_progress: true,
      anonymous_comparison: true,
      data_analytics: true,
    }
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  // Validation
  useEffect(() => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.location.trim()) {
      newErrors.location = 'Location is required'
    }
    
    if (formData.household_size < 1 || formData.household_size > 20) {
      newErrors.household_size = 'Household size must be between 1 and 20'
    }
    
    if (!formData.income_level) {
      newErrors.income_level = 'Income level is required'
    }
    
    if (formData.lifestyle_goals.length === 0) {
      newErrors.lifestyle_goals = 'Please select at least one goal'
    }
    
    setErrors(newErrors)
    
    const isValid = Object.keys(newErrors).length === 0
    onValidChange(isValid)
    
    if (isValid) {
      onUpdate({
        ...formData,
        income_level: formData.income_level as 'low' | 'medium' | 'high' | undefined
      })
    }
  }, [formData, onUpdate, onValidChange])
  
  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }
  
  const toggleGoal = (goal: string) => {
    const currentGoals = formData.lifestyle_goals
    const newGoals = currentGoals.includes(goal)
      ? currentGoals.filter(g => g !== goal)
      : [...currentGoals, goal]
    
    updateField('lifestyle_goals', newGoals)
  }
  
  const togglePrivacySetting = (setting: string) => {
    updateField('privacy_preferences', {
      ...formData.privacy_preferences,
      [setting]: !formData.privacy_preferences[setting]
    })
  }
  
  const incomeOptions = [
    { value: 'low', label: 'Under $50,000', description: 'Budget-conscious recommendations' },
    { value: 'medium', label: '$50,000 - $100,000', description: 'Balanced approach' },
    { value: 'high', label: 'Over $100,000', description: 'Premium solutions available' },
  ]
  
  const goalOptions = [
    { id: 'reduce_carbon', label: 'Reduce Carbon Footprint', icon: '🌱' },
    { id: 'save_money', label: 'Save Money', icon: '💰' },
    { id: 'live_sustainably', label: 'Live More Sustainably', icon: '♻️' },
    { id: 'learn_habits', label: 'Learn New Habits', icon: '📚' },
    { id: 'track_progress', label: 'Track My Progress', icon: '📊' },
    { id: 'join_community', label: 'Join Community', icon: '👥' },
  ]
  
  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-green-100 to-blue-100 dark:from-green-900/20 dark:to-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Users className="w-8 h-8 text-green-600" />
        </div>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Help us personalize your experience by sharing some basic information about yourself and your goals.
        </p>
      </div>
      
      {/* Location */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <MapPin className="w-4 h-4" />
          Location
        </label>
        <input
          type="text"
          value={formData.location}
          onChange={(e) => updateField('location', e.target.value)}
          placeholder="Enter your city or region"
          className={cn(
            'w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors',
            errors.location
              ? 'border-red-300 bg-red-50 dark:bg-red-900/20'
              : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800'
          )}
        />
        {errors.location && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.location}</p>
        )}
      </div>
      
      {/* Household Size */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <Users className="w-4 h-4" />
          Household Size
        </label>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="1"
            max="10"
            value={formData.household_size}
            onChange={(e) => updateField('household_size', parseInt(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <div className="flex items-center justify-center w-16 h-12 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <span className="text-lg font-semibold text-blue-600">{formData.household_size}</span>
          </div>
        </div>
        <p className="text-sm text-gray-500">
          {formData.household_size === 1 ? 'Just me' : `${formData.household_size} people`}
        </p>
        {errors.household_size && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.household_size}</p>
        )}
      </div>
      
      {/* Income Level */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <DollarSign className="w-4 h-4" />
          Income Level (Optional - helps with recommendations)
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {incomeOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => updateField('income_level', option.value)}
              className={cn(
                'p-4 rounded-lg border-2 text-left transition-all',
                formData.income_level === option.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              <div className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                {option.label}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {option.description}
              </div>
            </button>
          ))}
        </div>
        {errors.income_level && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.income_level}</p>
        )}
      </div>
      
      {/* Lifestyle Goals */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <Target className="w-4 h-4" />
          What are your main goals? (Select all that apply)
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {goalOptions.map((goal) => (
            <button
              key={goal.id}
              type="button"
              onClick={() => toggleGoal(goal.id)}
              className={cn(
                'p-4 rounded-lg border-2 text-left transition-all',
                formData.lifestyle_goals.includes(goal.id)
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{goal.icon}</span>
                <span className="font-medium text-gray-900 dark:text-gray-100">
                  {goal.label}
                </span>
              </div>
            </button>
          ))}
        </div>
        {errors.lifestyle_goals && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.lifestyle_goals}</p>
        )}
      </div>
      
      {/* Privacy Preferences */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <Shield className="w-4 h-4" />
          Privacy Preferences
        </label>
        <div className="space-y-3 bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">Share Progress</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Allow others to see your achievements</div>
            </div>
            <button
              type="button"
              onClick={() => togglePrivacySetting('share_progress')}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                formData.privacy_preferences.share_progress ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  formData.privacy_preferences.share_progress ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">Anonymous Comparisons</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Compare your progress with similar users</div>
            </div>
            <button
              type="button"
              onClick={() => togglePrivacySetting('anonymous_comparison')}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                formData.privacy_preferences.anonymous_comparison ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  formData.privacy_preferences.anonymous_comparison ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">Data Analytics</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Help improve our platform with usage data</div>
            </div>
            <button
              type="button"
              onClick={() => togglePrivacySetting('data_analytics')}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                formData.privacy_preferences.data_analytics ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  formData.privacy_preferences.data_analytics ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>
        </div>
      </div>
      
      {/* Summary */}
      {Object.keys(errors).length === 0 && formData.location && formData.income_level && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
          <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">
            Profile Summary
          </h4>
          <div className="text-sm text-green-700 dark:text-green-300 space-y-1">
            <p>📍 Location: {formData.location}</p>
            <p>👥 Household: {formData.household_size} {formData.household_size === 1 ? 'person' : 'people'}</p>
            <p>💰 Income: {incomeOptions.find(o => o.value === formData.income_level)?.label}</p>
            <p>🎯 Goals: {formData.lifestyle_goals.length} selected</p>
          </div>
        </div>
      )}
    </div>
  )
}