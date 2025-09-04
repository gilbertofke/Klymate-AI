'use client'

import React, { useState, useEffect } from 'react'
import { Home, Zap, Thermometer, Wind, Sun, Lightbulb } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { OnboardingData } from '@/types'

interface EnergyStepProps {
  data: Partial<OnboardingData>
  onUpdate: (data: Partial<OnboardingData>) => void
  onValidChange: (isValid: boolean) => void
}

export function EnergyStep({ data, onUpdate, onValidChange }: EnergyStepProps) {
  const [formData, setFormData] = useState({
    home_type: data.home_type || '' as 'apartment' | 'house' | 'condo' | 'other' | '',
    home_size: data.home_size || '' as 'small' | 'medium' | 'large' | '',
    heating_type: data.heating_type || '' as 'gas' | 'electric' | 'renewable' | 'mixed' | '',
    cooling_preferences: data.cooling_preferences || [],
    appliance_usage: data.appliance_usage || {},
    renewable_energy_interest: data.renewable_energy_interest || false,
    energy_efficiency_goals: data.energy_efficiency_goals || []
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  useEffect(() => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.home_type) {
      newErrors.home_type = 'Please select your home type'
    }
    
    if (!formData.home_size) {
      newErrors.home_size = 'Please select your home size'
    }
    
    if (!formData.heating_type) {
      newErrors.heating_type = 'Please select your heating type'
    }
    
    setErrors(newErrors)
    
    const isValid = Object.keys(newErrors).length === 0
    onValidChange(isValid)
    
    if (isValid) {
      onUpdate({
        ...formData,
        home_type: formData.home_type as 'apartment' | 'house' | 'condo' | 'other' | undefined,
        home_size: formData.home_size as 'small' | 'medium' | 'large' | undefined,
        heating_type: formData.heating_type as 'gas' | 'electric' | 'renewable' | 'mixed' | undefined
      })
    }
  }, [formData, onUpdate, onValidChange])
  
  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }
  
  const toggleCoolingPreference = (preference: string) => {
    const current = formData.cooling_preferences
    const updated = current.includes(preference)
      ? current.filter(p => p !== preference)
      : [...current, preference]
    
    updateField('cooling_preferences', updated)
  }
  
  const toggleEfficiencyGoal = (goal: string) => {
    const current = formData.energy_efficiency_goals
    const updated = current.includes(goal)
      ? current.filter(g => g !== goal)
      : [...current, goal]
    
    updateField('energy_efficiency_goals', updated)
  }
  
  const updateApplianceUsage = (appliance: string, usage: string) => {
    updateField('appliance_usage', {
      ...formData.appliance_usage,
      [appliance]: usage
    })
  }
  
  const homeTypes = [
    { value: 'apartment', label: 'Apartment', description: 'Multi-unit building', icon: '🏢' },
    { value: 'house', label: 'House', description: 'Single-family home', icon: '🏠' },
    { value: 'condo', label: 'Condo', description: 'Condominium unit', icon: '🏘️' },
    { value: 'other', label: 'Other', description: 'Mobile home, etc.', icon: '🏡' },
  ]
  
  const homeSizes = [
    { value: 'small', label: 'Small', description: 'Under 1,000 sq ft', icon: '📐' },
    { value: 'medium', label: 'Medium', description: '1,000 - 2,500 sq ft', icon: '📏' },
    { value: 'large', label: 'Large', description: 'Over 2,500 sq ft', icon: '📊' },
  ]
  
  const heatingTypes = [
    { value: 'gas', label: 'Natural Gas', impact: 'Medium CO₂', color: 'text-yellow-600', icon: '🔥' },
    { value: 'electric', label: 'Electric', impact: 'Variable CO₂', color: 'text-blue-600', icon: '⚡' },
    { value: 'renewable', label: 'Renewable', impact: 'Low CO₂', color: 'text-green-600', icon: '🌱' },
    { value: 'mixed', label: 'Mixed Sources', impact: 'Variable', color: 'text-gray-600', icon: '🔄' },
  ]
  
  const coolingOptions = [
    'central_ac',
    'window_units',
    'fans_only',
    'natural_ventilation',
    'heat_pump',
    'evaporative_cooling'
  ]
  
  const appliances = [
    { key: 'refrigerator', label: 'Refrigerator', icon: '❄️' },
    { key: 'washing_machine', label: 'Washing Machine', icon: '🧺' },
    { key: 'dryer', label: 'Dryer', icon: '🌪️' },
    { key: 'dishwasher', label: 'Dishwasher', icon: '🍽️' },
    { key: 'water_heater', label: 'Water Heater', icon: '🚿' },
    { key: 'lighting', label: 'Lighting', icon: '💡' },
  ]
  
  const usageOptions = [
    { value: 'low', label: 'Low', description: 'Minimal use' },
    { value: 'medium', label: 'Medium', description: 'Regular use' },
    { value: 'high', label: 'High', description: 'Heavy use' },
  ]
  
  const efficiencyGoals = [
    'reduce_bills',
    'lower_carbon_footprint',
    'improve_comfort',
    'increase_home_value',
    'use_smart_technology',
    'renewable_energy'
  ]
  
  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-green-100 to-blue-100 dark:from-green-900/20 dark:to-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Zap className="w-8 h-8 text-blue-600" />
        </div>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Tell us about your home energy usage so we can provide personalized recommendations 
          to optimize your energy consumption and reduce costs.
        </p>
      </div>
      
      {/* Home Type */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          What type of home do you live in?
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {homeTypes.map((type) => (
            <button
              key={type.value}
              type="button"
              onClick={() => updateField('home_type', type.value)}
              className={cn(
                'p-4 rounded-lg border-2 transition-all text-left',
                formData.home_type === type.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">{type.icon}</span>
                <h3 className="font-medium text-gray-900 dark:text-gray-100">
                  {type.label}
                </h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {type.description}
              </p>
            </button>
          ))}
        </div>
        {errors.home_type && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.home_type}</p>
        )}
      </div>
      
      {/* Home Size */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          What's the size of your home?
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {homeSizes.map((size) => (
            <button
              key={size.value}
              type="button"
              onClick={() => updateField('home_size', size.value)}
              className={cn(
                'p-4 rounded-lg border-2 transition-all text-left',
                formData.home_size === size.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">{size.icon}</span>
                <h3 className="font-medium text-gray-900 dark:text-gray-100">
                  {size.label}
                </h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {size.description}
              </p>
            </button>
          ))}
        </div>
        {errors.home_size && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.home_size}</p>
        )}
      </div>
      
      {/* Heating Type */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          What type of heating do you use?
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {heatingTypes.map((heating) => (
            <button
              key={heating.value}
              type="button"
              onClick={() => updateField('heating_type', heating.value)}
              className={cn(
                'p-4 rounded-lg border-2 transition-all text-left',
                formData.heating_type === heating.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{heating.icon}</span>
                  <h3 className="font-medium text-gray-900 dark:text-gray-100">
                    {heating.label}
                  </h3>
                </div>
                <span className={cn('text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800', heating.color)}>
                  {heating.impact}
                </span>
              </div>
            </button>
          ))}
        </div>
        {errors.heating_type && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.heating_type}</p>
        )}
      </div>
      
      {/* Cooling Preferences */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          How do you cool your home? (Select all that apply)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {coolingOptions.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => toggleCoolingPreference(option)}
              className={cn(
                'p-3 rounded-lg border text-sm transition-all',
                formData.cooling_preferences.includes(option)
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              {option.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>
      
      {/* Appliance Usage */}
      <div className="space-y-4">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          How would you rate your usage of these appliances?
        </label>
        <div className="space-y-4">
          {appliances.map((appliance) => (
            <div key={appliance.key} className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xl">{appliance.icon}</span>
                <span className="font-medium text-gray-900 dark:text-gray-100">
                  {appliance.label}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {usageOptions.map((usage) => (
                  <button
                    key={usage.value}
                    type="button"
                    onClick={() => updateApplianceUsage(appliance.key, usage.value)}
                    className={cn(
                      'p-2 rounded-lg border text-sm transition-all',
                      formData.appliance_usage[appliance.key] === usage.value
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500'
                    )}
                  >
                    <div className="font-medium">{usage.label}</div>
                    <div className="text-xs text-gray-500">{usage.description}</div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Renewable Energy Interest */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Are you interested in renewable energy solutions?
        </label>
        <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
          <Sun className="w-6 h-6 text-yellow-500" />
          <div className="flex-1">
            <div className="font-medium text-gray-900 dark:text-gray-100">
              Renewable Energy Interest
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Solar panels, wind power, geothermal, etc.
            </div>
          </div>
          <button
            type="button"
            onClick={() => updateField('renewable_energy_interest', !formData.renewable_energy_interest)}
            className={cn(
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
              formData.renewable_energy_interest ? 'bg-green-600' : 'bg-gray-200 dark:bg-gray-700'
            )}
          >
            <span
              className={cn(
                'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                formData.renewable_energy_interest ? 'translate-x-6' : 'translate-x-1'
              )}
            />
          </button>
        </div>
      </div>
      
      {/* Energy Efficiency Goals */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          What are your energy efficiency goals? (Select all that apply)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {efficiencyGoals.map((goal) => (
            <button
              key={goal}
              type="button"
              onClick={() => toggleEfficiencyGoal(goal)}
              className={cn(
                'p-3 rounded-lg border text-sm transition-all',
                formData.energy_efficiency_goals.includes(goal)
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              {goal.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>
      
      {/* Summary */}
      {Object.keys(errors).length === 0 && formData.home_type && formData.home_size && formData.heating_type && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
          <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">
            Energy Profile Summary
          </h4>
          <div className="text-sm text-green-700 dark:text-green-300 space-y-1">
            <p>🏠 Home: {homeTypes.find(h => h.value === formData.home_type)?.label} ({homeSizes.find(s => s.value === formData.home_size)?.label})</p>
            <p>🔥 Heating: {heatingTypes.find(h => h.value === formData.heating_type)?.label}</p>
            <p>❄️ Cooling: {formData.cooling_preferences.length} methods selected</p>
            <p>🌱 Renewable interest: {formData.renewable_energy_interest ? 'Yes' : 'No'}</p>
            <p>🎯 Efficiency goals: {formData.energy_efficiency_goals.length} selected</p>
          </div>
        </div>
      )}
    </div>
  )
}