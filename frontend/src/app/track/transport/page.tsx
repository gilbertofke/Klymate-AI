'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Car, Bike, Train, Walk, Plane } from 'lucide-react'
import { useLogActivity } from '@/lib/hooks/useApi'
import { toast } from 'react-hot-toast'

type TransportMode = 'car' | 'bike' | 'public' | 'walk' | 'plane'

interface TransportOption {
  id: TransportMode
  name: string
  icon: React.ComponentType<any>
  co2PerKm: number
  color: string
}

const transportOptions: TransportOption[] = [
  {
    id: 'car',
    name: 'Car',
    icon: Car,
    co2PerKm: 0.2,
    color: 'bg-blue-500'
  },
  {
    id: 'bike',
    name: 'Bicycle',
    icon: Bike,
    co2PerKm: 0,
    color: 'bg-green-500'
  },
  {
    id: 'public',
    name: 'Public Transport',
    icon: Train,
    co2PerKm: 0.04,
    color: 'bg-purple-500'
  },
  {
    id: 'walk',
    name: 'Walking',
    icon: Walk,
    co2PerKm: 0,
    color: 'bg-yellow-500'
  },
  {
    id: 'plane',
    name: 'Plane',
    icon: Plane,
    co2PerKm: 0.9,
    color: 'bg-red-500'
  }
]

export default function TransportTrackingPage() {
  const [selectedMode, setSelectedMode] = useState<TransportMode | null>(null)
  const [distance, setDistance] = useState<string>('')
  const { logActivity, loading } = useLogActivity()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedMode || !distance) return

    const mode = transportOptions.find(opt => opt.id === selectedMode)
    if (!mode) return

    try {
      const co2Impact = mode.co2PerKm * parseFloat(distance)
      await logActivity({
        type: 'transport',
        mode: selectedMode,
        distance: parseFloat(distance),
        co2Impact,
        timestamp: new Date().toISOString()
      })

      toast.success('Transport activity logged successfully!')
      setSelectedMode(null)
      setDistance('')
    } catch (error) {
      toast.error('Failed to log transport activity')
    }
  }

  return (
    <DashboardLayout>
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Track Your Transport
          </h1>
          <p className="text-gray-600 mb-6">
            Log your daily transportation to track your carbon footprint
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Transport Mode Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-4">
                Choose your mode of transport
              </label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {transportOptions.map((option) => (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => setSelectedMode(option.id)}
                    className={`p-4 rounded-lg border ${
                      selectedMode === option.id
                        ? 'border-green-500 ring-2 ring-green-500 ring-opacity-50'
                        : 'border-gray-200 hover:border-gray-300'
                    } transition-all focus:outline-none`}
                  >
                    <div className={`w-12 h-12 rounded-full ${option.color} mx-auto flex items-center justify-center mb-2`}>
                      <option.icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="text-sm font-medium text-gray-900 text-center">
                      {option.name}
                    </div>
                    <div className="text-xs text-gray-500 text-center mt-1">
                      {option.co2PerKm > 0 ? `${option.co2PerKm} kg CO₂/km` : 'No emissions'}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Distance Input */}
            {selectedMode && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-xs"
              >
                <label htmlFor="distance" className="block text-sm font-medium text-gray-700 mb-2">
                  Distance traveled (km)
                </label>
                <input
                  type="number"
                  id="distance"
                  min="0"
                  step="0.1"
                  value={distance}
                  onChange={(e) => setDistance(e.target.value)}
                  className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="Enter distance in kilometers"
                />
              </motion.div>
            )}

            {/* Submit Button */}
            {selectedMode && distance && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full md:w-auto px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? 'Logging...' : 'Log Transport Activity'}
                </button>

                {/* CO2 Impact Preview */}
                {selectedMode && distance && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">
                      Estimated CO2 Impact:
                      <span className="ml-2 font-semibold text-gray-900">
                        {(transportOptions.find(opt => opt.id === selectedMode)?.co2PerKm || 0 * parseFloat(distance)).toFixed(2)} kg CO₂
                      </span>
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </form>
        </motion.div>
      </div>
    </DashboardLayout>
  )
}