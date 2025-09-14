'use client'

import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/auth/AuthGuard'
import { useLogHabit, useHabits } from '@/lib/hooks/useApi'
import { motion } from 'framer-motion'

interface Habit {
  id: string
  type: 'transport' | 'energy' | 'diet' | 'waste'
  activity: string
  impact: number
  date: string
  notes?: string
}

const habitTypes = {
  transport: { icon: '🚗', label: 'Transportation', color: 'blue' },
  energy: { icon: '⚡', label: 'Energy', color: 'yellow' },
  diet: { icon: '🥗', label: 'Diet', color: 'green' },
  waste: { icon: '♻️', label: 'Waste', color: 'purple' }
}

const commonHabits = {
  transport: [
    { activity: 'Walked instead of driving', impact: -2.5 },
    { activity: 'Used public transport', impact: -1.8 },
    { activity: 'Biked to work', impact: -3.0 },
    { activity: 'Carpooled', impact: -1.2 },
    { activity: 'Worked from home', impact: -4.0 }
  ],
  energy: [
    { activity: 'Turned off lights when leaving room', impact: -0.5 },
    { activity: 'Used LED bulbs', impact: -0.8 },
    { activity: 'Unplugged devices when not in use', impact: -0.3 },
    { activity: 'Used natural light instead of artificial', impact: -0.4 },
    { activity: 'Adjusted thermostat by 2°C', impact: -2.0 }
  ],
  diet: [
    { activity: 'Had a plant-based meal', impact: -1.5 },
    { activity: 'Chose local/seasonal produce', impact: -0.8 },
    { activity: 'Reduced meat consumption', impact: -2.2 },
    { activity: 'Avoided food waste', impact: -0.6 },
    { activity: 'Brought lunch from home', impact: -0.4 }
  ],
  waste: [
    { activity: 'Recycled properly', impact: -0.3 },
    { activity: 'Used reusable water bottle', impact: -0.2 },
    { activity: 'Composted organic waste', impact: -0.5 },
    { activity: 'Used reusable shopping bags', impact: -0.1 },
    { activity: 'Repaired instead of replacing', impact: -1.0 }
  ]
}

export default function HabitsPage() {
  const [selectedType, setSelectedType] = useState<keyof typeof habitTypes>('transport')
  const [customActivity, setCustomActivity] = useState('')
  const [customImpact, setCustomImpact] = useState('')
  const [notes, setNotes] = useState('')
  const [showCustomForm, setShowCustomForm] = useState(false)

  const { logHabit, loading: logLoading, error: logError } = useLogHabit()
  const { data: todayHabits, loading: habitsLoading, refetch } = useHabits('today')

  const handleLogHabit = async (activity: string, impact: number) => {
    try {
      await logHabit({
        type: selectedType,
        activity,
        impact,
        date: new Date().toISOString().split('T')[0],
        notes: notes || undefined
      })
      
      setNotes('')
      setCustomActivity('')
      setCustomImpact('')
      setShowCustomForm(false)
      refetch()
      
      // Show success message
      alert(`✅ Habit logged: ${activity}`)
    } catch (error: any) {
      alert(`❌ Failed to log habit: ${error.message}`)
    }
  }

  const handleCustomSubmit = () => {
    if (!customActivity.trim() || !customImpact) return
    
    const impact = parseFloat(customImpact)
    if (isNaN(impact)) {
      alert('Please enter a valid number for CO2 impact')
      return
    }
    
    handleLogHabit(customActivity, impact)
  }

  const totalImpactToday = todayHabits?.reduce((sum: number, habit: any) => sum + (habit.impact || 0), 0) || 0

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              📝 Track Your Habits
            </h1>
            <p className="text-gray-600">
              Log your daily eco-friendly actions and see your impact
            </p>
          </div>

          {/* Today's Impact Summary */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Today's Impact</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {totalImpactToday.toFixed(1)} kg
                </div>
                <div className="text-gray-600">CO2 Saved Today</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {todayHabits?.length || 0}
                </div>
                <div className="text-gray-600">Habits Logged</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">
                  {Math.abs(totalImpactToday * 365).toFixed(0)} kg
                </div>
                <div className="text-gray-600">Annual Projection</div>
              </div>
            </div>
          </div>

          {/* Habit Type Selector */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Log a New Habit</h2>
            
            <div className="flex flex-wrap gap-4 mb-6">
              {Object.entries(habitTypes).map(([type, config]) => (
                <button
                  key={type}
                  onClick={() => setSelectedType(type as keyof typeof habitTypes)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    selectedType === type
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <span>{config.icon}</span>
                  <span>{config.label}</span>
                </button>
              ))}
            </div>

            {/* Common Habits for Selected Type */}
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              {commonHabits[selectedType].map((habit, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleLogHabit(habit.activity, habit.impact)}
                  disabled={logLoading}
                  className="p-4 text-left bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
                >
                  <div className="font-medium text-gray-900">{habit.activity}</div>
                  <div className="text-sm text-green-600">
                    {habit.impact > 0 ? '+' : ''}{habit.impact} kg CO2
                  </div>
                </motion.button>
              ))}
            </div>

            {/* Custom Habit Form */}
            <div className="border-t pt-6">
              <button
                onClick={() => setShowCustomForm(!showCustomForm)}
                className="text-green-600 hover:text-green-700 font-medium mb-4"
              >
                {showCustomForm ? '− Hide Custom Habit' : '+ Add Custom Habit'}
              </button>

              {showCustomForm && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Activity Description
                    </label>
                    <input
                      type="text"
                      value={customActivity}
                      onChange={(e) => setCustomActivity(e.target.value)}
                      placeholder="Describe your eco-friendly action..."
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      CO2 Impact (kg) - Use negative numbers for savings
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={customImpact}
                      onChange={(e) => setCustomImpact(e.target.value)}
                      placeholder="-1.5"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notes (optional)
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Any additional details..."
                      rows={2}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  </div>
                  
                  <button
                    onClick={handleCustomSubmit}
                    disabled={!customActivity.trim() || !customImpact || logLoading}
                    className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {logLoading ? 'Logging...' : 'Log Custom Habit'}
                  </button>
                </div>
              )}
            </div>

            {logError && (
              <div className="mt-4 p-3 bg-red-100 border border-red-200 rounded-lg text-red-700 text-sm">
                Error: {logError}
              </div>
            )}
          </div>

          {/* Today's Logged Habits */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Today's Habits</h2>
            
            {habitsLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                <p className="text-gray-600 mt-2">Loading habits...</p>
              </div>
            ) : todayHabits && todayHabits.length > 0 ? (
              <div className="space-y-3">
                {todayHabits.map((habit: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{habitTypes[habit.type as keyof typeof habitTypes]?.icon}</span>
                      <div>
                        <div className="font-medium text-gray-900">{habit.activity}</div>
                        {habit.notes && <div className="text-sm text-gray-600">{habit.notes}</div>}
                      </div>
                    </div>
                    <div className={`font-bold ${habit.impact < 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {habit.impact > 0 ? '+' : ''}{habit.impact} kg CO2
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No habits logged today yet.</p>
                <p className="text-sm">Start logging your eco-friendly actions above!</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}