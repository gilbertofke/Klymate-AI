'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Lightbulb, Droplet, Flame, Thermometer, Power } from 'lucide-react'
import { useLogActivity } from '@/lib/hooks/useApi'
import { toast } from 'react-hot-toast'

type EnergyType = 'electricity' | 'water' | 'gas' | 'heating' | 'solar'

interface EnergyOption {
  id: EnergyType
  name: string
  icon: React.ComponentType<any>
  unit: string
  co2PerUnit: number
  color: string
}

const energyOptions: EnergyOption[] = [
  {
    id: 'electricity',
    name: 'Electricity',
    icon: Power,
    unit: 'kWh',
    co2PerUnit: 0.4,
    color: 'bg-yellow-500'
  },
  {
    id: 'water',
    name: 'Water',
    icon: Droplet,
    unit: 'm³',
    co2PerUnit: 0.2,
    color: 'bg-blue-500'
  },
  {
    id: 'gas',
    name: 'Natural Gas',
    icon: Flame,
    unit: 'm³',
    co2PerUnit: 2.0,
    color: 'bg-red-500'
  },
  {
    id: 'heating',
    name: 'Heating',
    icon: Thermometer,
    unit: 'kWh',
    co2PerUnit: 0.3,
    color: 'bg-orange-500'
  },
  {
    id: 'solar',
    name: 'Solar Power',
    icon: Lightbulb,
    unit: 'kWh',
    co2PerUnit: 0,
    color: 'bg-green-500'
  }
]

export default function EnergyTrackingPage() {
  const [selectedType, setSelectedType] = useState<EnergyType | null>(null)
  const [amount, setAmount] = useState<string>('')
  const { logActivity, loading } = useLogActivity()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedType || !amount) return

    const energyType = energyOptions.find(opt => opt.id === selectedType)
    if (!energyType) return

    try {
      const co2Impact = energyType.co2PerUnit * parseFloat(amount)
      await logActivity({
        type: 'energy',
        energyType: selectedType,
        amount: parseFloat(amount),
        unit: energyType.unit,
        co2Impact,
        timestamp: new Date().toISOString()
      })

      toast.success('Energy usage logged successfully!')
      setSelectedType(null)
      setAmount('')
    } catch (error) {
      toast.error('Failed to log energy usage')
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
            Track Your Energy Usage
          </h1>
          <p className="text-gray-600 mb-6">
            Monitor your home energy consumption to reduce your carbon footprint
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Energy Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-4">
                Select energy type
              </label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {energyOptions.map((option) => (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => setSelectedType(option.id)}
                    className={`p-4 rounded-lg border ${
                      selectedType === option.id
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
                      {option.co2PerUnit > 0 ? `${option.co2PerUnit} kg CO₂/${option.unit}` : 'Clean energy'}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Amount Input */}
            {selectedType && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-xs"
              >
                <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                  Usage amount ({energyOptions.find(opt => opt.id === selectedType)?.unit})
                </label>
                <input
                  type="number"
                  id="amount"
                  min="0"
                  step="0.1"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder={`Enter amount in ${energyOptions.find(opt => opt.id === selectedType)?.unit}`}
                />
              </motion.div>
            )}

            {/* Submit Button */}
            {selectedType && amount && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full md:w-auto px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? 'Logging...' : 'Log Energy Usage'}
                </button>

                {/* CO2 Impact Preview */}
                {selectedType && amount && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">
                      Estimated CO2 Impact:
                      <span className="ml-2 font-semibold text-gray-900">
                        {(energyOptions.find(opt => opt.id === selectedType)?.co2PerUnit || 0 * parseFloat(amount)).toFixed(2)} kg CO₂
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