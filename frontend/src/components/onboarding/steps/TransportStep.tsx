'use client'

import React, { useEffect, useState } from 'react'
import { Car, Bus, Plane, Bike, MapPin, Gauge, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { OnboardingData } from '@/types'

interface TransportStepProps {
  data: Partial<OnboardingData>
  onUpdate: (data: Partial<OnboardingData>) => void
  onValidChange: (isValid: boolean) => void
}

export function TransportStep({ data, onUpdate, onValidChange }: TransportStepProps) {
  const [formData, setFormData] = useState({
    primary_transport: data.primary_transport || '' as 'car' | 'public_transport' | 'bike' | 'walk' | 'mixed' | '',
    commute_distance: data.commute_distance || 10,
    vehicle_type: data.vehicle_type || '' as 'none' | 'electric' | 'hybrid' | 'gas' | 'diesel' | '',
    public_transport_usage: data.public_transport_usage || '' as 'never' | 'rarely' | 'sometimes' | 'often' | 'always' | '',
    travel_frequency: data.travel_frequency || '' as 'low' | 'medium' | 'high' | '',
    transportation_preferences: data.transportation_preferences || []
  })
  
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  useEffect(() => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.primary_transport) {
      newErrors.primary_transport = 'Please select your primary transportation method'
    }
    
    if (formData.primary_transport === 'car' && !formData.vehicle_type) {
      newErrors.vehicle_type = 'Please specify your vehicle type'
    }
    
    if (!formData.public_transport_usage) {
      newErrors.public_transport_usage = 'Please indicate your public transport usage'
    }
    
    if (!formData.travel_frequency) {
      newErrors.travel_frequency = 'Please select your travel frequency'
    }
    
    setErrors(newErrors)
    
    const isValid = Object.keys(newErrors).length === 0
    onValidChange(isValid)
    
    if (isValid) {
      onUpdate({
        ...formData,
        primary_transport: formData.primary_transport as 'car' | 'public_transport' | 'bike' | 'walk' | 'mixed' | undefined,
        vehicle_type: formData.vehicle_type as 'none' | 'electric' | 'hybrid' | 'gas' | 'diesel' | undefined,
        public_transport_usage: formData.public_transport_usage as 'never' | 'rarely' | 'sometimes' | 'often' | 'always' | undefined,
        travel_frequency: formData.travel_frequency as 'low' | 'medium' | 'high' | undefined
      })
    }
  }, [formData, onUpdate, onValidChange])
  
  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }
  
  const togglePreference = (preference: string) => {
    const current = formData.transportation_preferences
    const updated = current.includes(preference)
      ? current.filter(p => p !== preference)
      : [...current, preference]
    
    updateField('transportation_preferences', updated)
  }
  
  const transportOptions = [
    {
      value: 'car',
      title: 'Car/Driving',
      description: 'I primarily drive a car',
      icon: Car,
      color: 'text-red-600',
      bgColor: 'bg-red-100 dark:bg-red-900/20',
      impact: 'High CO₂',
    },
    {
      value: 'public_transport',
      title: 'Public Transport',
      description: 'I use buses, trains, metro',
      icon: Bus,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
      impact: 'Low CO₂',
    },
    {
      value: 'bike',
      title: 'Cycling',
      description: 'I bike for transportation',
      icon: Bike,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
      impact: 'Zero CO₂',
    },
    {
      value: 'walk',
      title: 'Walking',
      description: 'I walk most places',
      icon: MapPin,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
      impact: 'Zero CO₂',
    },
    {
      value: 'mixed',
      title: 'Mixed Methods',
      description: 'I use multiple transportation methods',
      icon: Plane,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
      impact: 'Variable',
    },
  ]
  
  const vehicleTypes = [
    { value: 'electric', label: 'Electric Vehicle', impact: 'Low CO₂', color: 'text-green-600' },
    { value: 'hybrid', label: 'Hybrid Vehicle', impact: 'Medium CO₂', color: 'text-yellow-600' },
    { value: 'gas', label: 'Gasoline Vehicle', impact: 'High CO₂', color: 'text-red-600' },
    { value: 'diesel', label: 'Diesel Vehicle', impact: 'High CO₂', color: 'text-red-600' },
  ]
  
  const publicTransportOptions = [
    { value: 'never', label: 'Never', description: 'I don\'t use public transport' },
    { value: 'rarely', label: 'Rarely', description: 'A few times per year' },
    { value: 'sometimes', label: 'Sometimes', description: 'A few times per month' },
    { value: 'often', label: 'Often', description: 'A few times per week' },
    { value: 'always', label: 'Always', description: 'Daily or almost daily' },
  ]
  
  const travelFrequencyOptions = [
    { value: 'low', label: 'Low', description: 'Mostly local travel' },
    { value: 'medium', label: 'Medium', description: 'Some regional trips' },
    { value: 'high', label: 'High', description: 'Frequent long-distance travel' },
  ]
  
  const preferenceOptions = [
    'cost_effective',
    'time_efficient',
    'environmentally_friendly',
    'comfortable',
    'flexible_schedule',
    'exercise_opportunity'
  ]
  
  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-green-100 to-blue-100 dark:from-green-900/20 dark:to-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Car className="w-8 h-8 text-blue-600" />
        </div>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Help us understand your transportation habits so we can provide personalized recommendations 
          to reduce your carbon footprint.
        </p>
      </div>
      
      {/* Primary Transportation */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          What's your primary method of transportation?
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {transportOptions.map((option) => {
            const Icon = option.icon
            const isSelected = formData.primary_transport === option.value
            
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => updateField('primary_transport', option.value)}
                className={cn(
                  'p-4 rounded-lg border-2 transition-all text-left',
                  isSelected
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 hover:border-gray-300 dark:hover:border-gray-500'
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className={cn('p-2 rounded-lg', option.bgColor)}>
                      <Icon className={cn('w-5 h-5', option.color)} />
                    </div>
                    <h3 className="font-medium text-gray-900 dark:text-gray-100">
                      {option.title}
                    </h3>
                  </div>
                  <span className={cn('text-xs px-2 py-1 rounded-full', option.bgColor, option.color)}>
                    {option.impact}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {option.description}
                </p>
              </button>
            )
          })}
        </div>
        {errors.primary_transport && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.primary_transport}</p>
        )}
      </div>
      
      {/* Commute Distance */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          What's your typical daily commute distance? (one way)
        </label>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={formData.commute_distance}
            onChange={(e) => updateField('commute_distance', parseInt(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <div className="flex items-center justify-center w-20 h-12 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <span className="text-sm font-semibold text-blue-600">{formData.commute_distance} km</span>
          </div>
        </div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>0 km</span>
          <span>Work from home</span>
          <span>100+ km</span>
        </div>
      </div>
      
      {/* Vehicle Type (if car selected) */}
      {formData.primary_transport === 'car' && (
        <div className="space-y-3">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            What type of vehicle do you drive?
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {vehicleTypes.map((vehicle) => (
              <button
                key={vehicle.value}
                type="button"
                onClick={() => updateField('vehicle_type', vehicle.value)}
                className={cn(
                  'p-3 rounded-lg border-2 text-left transition-all',
                  formData.vehicle_type === vehicle.value
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 hover:border-gray-300 dark:hover:border-gray-500'
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {vehicle.label}
                  </span>
                  <span className={cn('text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800', vehicle.color)}>
                    {vehicle.impact}
                  </span>
                </div>
              </button>
            ))}
          </div>
          {errors.vehicle_type && (
            <p className="text-sm text-red-600 dark:text-red-400">{errors.vehicle_type}</p>
          )}
        </div>
      )}
      
      {/* Public Transport Usage */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          How often do you use public transportation?
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {publicTransportOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => updateField('public_transport_usage', option.value)}
              className={cn(
                'p-3 rounded-lg border-2 text-left transition-all',
                formData.public_transport_usage === option.value
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
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
        {errors.public_transport_usage && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.public_transport_usage}</p>
        )}
      </div>
      
      {/* Travel Frequency */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          How would you describe your travel frequency?
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {travelFrequencyOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => updateField('travel_frequency', option.value)}
              className={cn(
                'p-4 rounded-lg border-2 text-left transition-all',
                formData.travel_frequency === option.value
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
        {errors.travel_frequency && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.travel_frequency}</p>
        )}
      </div>
      
      {/* Transportation Preferences */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          What's important to you in transportation? (Optional)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {preferenceOptions.map((pref) => (
            <button
              key={pref}
              type="button"
              onClick={() => togglePreference(pref)}
              className={cn(
                'p-2 rounded-lg border text-sm transition-all',
                formData.transportation_preferences.includes(pref)
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                  : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-500'
              )}
            >
              {pref.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>
      
      {/* Summary */}
      {Object.keys(errors).length === 0 && formData.primary_transport && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
          <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">
            Transportation Summary
          </h4>
          <div className="text-sm text-green-700 dark:text-green-300 space-y-1">
            <p>🚗 Primary: {transportOptions.find(o => o.value === formData.primary_transport)?.title}</p>
            <p>📏 Commute: {formData.commute_distance} km daily</p>
            {formData.vehicle_type && (
              <p>⚡ Vehicle: {vehicleTypes.find(v => v.value === formData.vehicle_type)?.label}</p>
            )}
            <p>🚌 Public transport: {publicTransportOptions.find(o => o.value === formData.public_transport_usage)?.label}</p>
            <p>✈️ Travel frequency: {travelFrequencyOptions.find(o => o.value === formData.travel_frequency)?.label}</p>
          </div>
        </div>
      )}
    </div>
  )
}