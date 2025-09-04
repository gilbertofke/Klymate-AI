'use client'

import React, { useState, useEffect } from 'react'
import { Utensils, Apple, Leaf, Fish, ChefHat, ShoppingCart } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { OnboardingData } from '@/types'

interface DietStepProps {
  data: Partial<OnboardingData>
  onUpdate: (data: Partial<OnboardingData>) => void
  onValidChange: (isValid: boolean) => void
}

export function DietStep({ data, onUpdate, onValidChange }: DietStepProps) {
  const [formData, setFormData] = useState({
    diet_type: data.diet_type || '' as 'omnivore' | 'vegetarian' | 'vegan' | 'pescatarian' | 'flexitarian' | '',
    meal_frequency: data.meal_frequency || 3,
    meal_patterns: data.meal_patterns || [],
    food_sourcing_preferences: data.food_sourcing_preferences || [],
    local_food_preference: data.local_food_preference || false,
    organic_food_preference: data.organic_food_preference || false,
    cooking_habits: data.cooking_habits || [],
    food_waste_considerations: data.food_waste_considerations || []
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  useEffect(() => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.diet_type) {
      newErrors.diet_type = 'Please select your diet type'
    }
    
    if (formData.meal_frequency < 1 || formData.meal_frequency > 10) {
      newErrors.meal_frequency = 'Meal frequency must be between 1 and 10'
    }
    
    setErrors(newErrors)
    
    const isValid = Object.keys(newErrors).length === 0
    onValidChange(isValid)
    
    if (isValid) {
      onUpdate({
        ...formData,
        diet_type: formData.diet_type as 'omnivore' | 'vegetarian' | 'vegan' | 'pescatarian' | 'flexitarian' | undefined
      })
    }
  }, [formData, onUpdate, onValidChange])
  
  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }
  
  const toggleArrayItem = (field: string, item: string) => {
    const current = formData[field as keyof typeof formData] as string[]
    const updated = current.includes(item)
      ? current.filter(i => i !== item)
      : [...current, item]
    
    updateField(field, updated)
  }
  
  const dietTypes = [
    { 
      value: 'omnivore', 
      label: 'Omnivore', 
      description: 'I eat meat, fish, and plants',
      icon: '🍖',
      impact: 'High CO₂',
      color: 'text-red-600'
    },
    { 
      value: 'flexitarian', 
      label: 'Flexitarian', 
      description: 'Mostly plants, occasional meat',
      icon: '🥗',
      impact: 'Medium CO₂',
      color: 'text-yellow-600'
    },
    { 
      value: 'pescatarian', 
      label: 'Pescatarian', 
      description: 'Fish and plants, no meat',
      icon: '🐟',
      impact: 'Medium CO₂',
      color: 'text-blue-600'
    },
    { 
      value: 'vegetarian', 
      label: 'Vegetarian', 
      description: 'Plants and dairy, no meat/fish',
      icon: '🥕',
      impact: 'Low CO₂',
      color: 'text-green-600'
    },
    { 
      value: 'vegan', 
      label: 'Vegan', 
      description: 'Plants only, no animal products',
      icon: '🌱',
      impact: 'Lowest CO₂',
      color: 'text-green-700'
    },
  ]
  
  const mealPatterns = [
    'breakfast_daily',
    'lunch_daily',
    'dinner_daily',
    'snacks_frequent',
    'meal_prep',
    'eating_out_frequent',
    'fast_food_occasional',
    'home_cooking_preferred'
  ]
  
  const sourcingPreferences = [
    'local_farmers_markets',
    'organic_stores',
    'bulk_buying',
    'seasonal_eating',
    'fair_trade_products',
    'minimal_packaging',
    'community_supported_agriculture',
    'grow_own_food'
  ]
  
  const cookingHabits = [
    'cook_from_scratch',
    'meal_planning',
    'batch_cooking',
    'use_leftovers',
    'preserve_food',
    'compost_scraps',
    'energy_efficient_cooking',
    'minimal_food_waste'
  ]
  
  const wasteConsiderations = [
    'plan_portions_carefully',
    'use_all_parts_of_food',
    'repurpose_leftovers',
    'compost_organic_waste',
    'donate_excess_food',
    'buy_imperfect_produce',
    'track_food_waste',
    'educate_family_about_waste'
  ]
  
  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-green-100 to-blue-100 dark:from-green-900/20 dark:to-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Utensils className="w-8 h-8 text-green-600" />
        </div>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Tell us about your dietary preferences and eating habits so we can provide personalized 
          recommendations to reduce your food-related carbon footprint.
        </p>
      </div>
      
      {/* Diet Type */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Which diet type best describes you?
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {dietTypes.map((diet) => (
            <button
              key={diet.value}
              type="button"
              onClick={() => updateField('diet_type', diet.value)}
              className={cn(
                'p-4 rounded-lg border-2 transition-all text-left',
                formData.diet_type === diet.value
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{diet.icon}</span>
                  <h3 className="font-medium text-gray-900 dark:text-gray-100">
                    {diet.label}
                  </h3>
                </div>
                <span className={cn('text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800', diet.color)}>
                  {diet.impact}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {diet.description}
              </p>
            </button>
          ))}
        </div>
        {errors.diet_type && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.diet_type}</p>
        )}
      </div>
      
      {/* Meal Frequency */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          How many meals do you typically eat per day?
        </label>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="1"
            max="6"
            value={formData.meal_frequency}
            onChange={(e) => updateField('meal_frequency', parseInt(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <div className="flex items-center justify-center w-16 h-12 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <span className="text-lg font-semibold text-green-600">{formData.meal_frequency}</span>
          </div>
        </div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>1 meal</span>
          <span>3 meals (typical)</span>
          <span>6+ meals</span>
        </div>
        {errors.meal_frequency && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.meal_frequency}</p>
        )}
      </div>
      
      {/* Meal Patterns */}
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <ChefHat className="w-4 h-4" />
          What are your typical meal patterns? (Select all that apply)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {mealPatterns.map((pattern) => (
            <button
              key={pattern}
              type="button"
              onClick={() => toggleArrayItem('meal_patterns', pattern)}
              className={cn(
                'p-3 rounded-lg border text-sm transition-all',
                formData.meal_patterns.includes(pattern)
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              {pattern.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>
      
      {/* Food Sourcing Preferences */}
      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <ShoppingCart className="w-4 h-4" />
          How do you prefer to source your food? (Select all that apply)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {sourcingPreferences.map((preference) => (
            <button
              key={preference}
              type="button"
              onClick={() => toggleArrayItem('food_sourcing_preferences', preference)}
              className={cn(
                'p-3 rounded-lg border text-sm transition-all',
                formData.food_sourcing_preferences.includes(preference)
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              {preference.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>
      
      {/* Local and Organic Preferences */}
      <div className="space-y-4">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Food Quality Preferences
        </label>
        <div className="space-y-3 bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Apple className="w-5 h-5 text-green-600" />
              <div>
                <div className="font-medium text-gray-900 dark:text-gray-100">Local Food</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Prefer locally sourced ingredients</div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => updateField('local_food_preference', !formData.local_food_preference)}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                formData.local_food_preference ? 'bg-green-600' : 'bg-gray-200 dark:bg-gray-700'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  formData.local_food_preference ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Leaf className="w-5 h-5 text-green-600" />
              <div>
                <div className="font-medium text-gray-900 dark:text-gray-100">Organic Food</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Prefer organic products when available</div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => updateField('organic_food_preference', !formData.organic_food_preference)}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                formData.organic_food_preference ? 'bg-green-600' : 'bg-gray-200 dark:bg-gray-700'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  formData.organic_food_preference ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>
        </div>
      </div>
      
      {/* Cooking Habits */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          What are your cooking habits? (Select all that apply)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {cookingHabits.map((habit) => (
            <button
              key={habit}
              type="button"
              onClick={() => toggleArrayItem('cooking_habits', habit)}
              className={cn(
                'p-3 rounded-lg border text-sm transition-all',
                formData.cooking_habits.includes(habit)
                  ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              {habit.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>
      
      {/* Food Waste Considerations */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          How do you handle food waste? (Select all that apply)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {wasteConsiderations.map((consideration) => (
            <button
              key={consideration}
              type="button"
              onClick={() => toggleArrayItem('food_waste_considerations', consideration)}
              className={cn(
                'p-3 rounded-lg border text-sm transition-all',
                formData.food_waste_considerations.includes(consideration)
                  ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              {consideration.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>
      
      {/* Summary */}
      {Object.keys(errors).length === 0 && formData.diet_type && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
          <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">
            Diet Profile Summary
          </h4>
          <div className="text-sm text-green-700 dark:text-green-300 space-y-1">
            <p>🍽️ Diet: {dietTypes.find(d => d.value === formData.diet_type)?.label}</p>
            <p>📊 Meals per day: {formData.meal_frequency}</p>
            <p>🥗 Meal patterns: {formData.meal_patterns.length} selected</p>
            <p>🛒 Sourcing preferences: {formData.food_sourcing_preferences.length} selected</p>
            <p>🌱 Local preference: {formData.local_food_preference ? 'Yes' : 'No'}</p>
            <p>🍃 Organic preference: {formData.organic_food_preference ? 'Yes' : 'No'}</p>
            <p>👨‍🍳 Cooking habits: {formData.cooking_habits.length} selected</p>
            <p>♻️ Waste considerations: {formData.food_waste_considerations.length} selected</p>
          </div>
        </div>
      )}
    </div>
  )
}