'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Beef, Fish, Carrot, Egg, Coffee } from 'lucide-react'
import { useLogActivity } from '@/lib/hooks/useApi'
import { toast } from 'react-hot-toast'

type DietType = 'meat' | 'fish' | 'vegetarian' | 'dairy' | 'beverage'

interface DietOption {
  id: DietType
  name: string
  icon: React.ComponentType<any>
  co2PerServing: number
  color: string
}

const dietOptions: DietOption[] = [
  {
    id: 'meat',
    name: 'Meat',
    icon: Beef,
    co2PerServing: 6.0,
    color: 'bg-red-500'
  },
  {
    id: 'fish',
    name: 'Fish',
    icon: Fish,
    co2PerServing: 2.0,
    color: 'bg-blue-500'
  },
  {
    id: 'vegetarian',
    name: 'Plant-Based',
    icon: Carrot,
    co2PerServing: 0.5,
    color: 'bg-green-500'
  },
  {
    id: 'dairy',
    name: 'Dairy & Eggs',
    icon: Egg,
    co2PerServing: 1.5,
    color: 'bg-yellow-500'
  },
  {
    id: 'beverage',
    name: 'Beverages',
    icon: Coffee,
    co2PerServing: 0.2,
    color: 'bg-purple-500'
  }
]

export default function DietTrackingPage() {
  const [selectedType, setSelectedType] = useState<DietType | null>(null)
  const [servings, setServings] = useState<string>('')
  const { logActivity, loading } = useLogActivity()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedType || !servings) return

    const dietType = dietOptions.find(opt => opt.id === selectedType)
    if (!dietType) return

    try {
      const co2Impact = dietType.co2PerServing * parseFloat(servings)
      await logActivity({
        type: 'diet',
        foodType: selectedType,
        servings: parseFloat(servings),
        co2Impact,
        timestamp: new Date().toISOString()
      })

      toast.success('Diet activity logged successfully!')
      setSelectedType(null)
      setServings('')
    } catch (error) {
      toast.error('Failed to log diet activity')
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
            Track Your Diet
          </h1>
          <p className="text-gray-600 mb-6">
            Log your meals to understand and reduce your dietary carbon footprint
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Diet Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-4">
                Select food category
              </label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {dietOptions.map((option) => (
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
                      {`${option.co2PerServing} kg CO₂/serving`}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Servings Input */}
            {selectedType && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-xs"
              >
                <label htmlFor="servings" className="block text-sm font-medium text-gray-700 mb-2">
                  Number of servings
                </label>
                <input
                  type="number"
                  id="servings"
                  min="0.5"
                  step="0.5"
                  value={servings}
                  onChange={(e) => setServings(e.target.value)}
                  className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
                  placeholder="Enter number of servings"
                />
              </motion.div>
            )}

            {/* Submit Button */}
            {selectedType && servings && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full md:w-auto px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? 'Logging...' : 'Log Meal'}
                </button>

                {/* CO2 Impact Preview */}
                {selectedType && servings && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">
                      Estimated CO2 Impact:
                      <span className="ml-2 font-semibold text-gray-900">
                        {(dietOptions.find(opt => opt.id === selectedType)?.co2PerServing || 0 * parseFloat(servings)).toFixed(2)} kg CO₂
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