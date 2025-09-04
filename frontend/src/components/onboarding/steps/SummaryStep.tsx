'use client'

import { motion } from 'framer-motion'
import { CheckCircle } from 'lucide-react'

interface SummaryStepProps {
  data: any
  onNext: () => void
  onPrevious: () => void
  isLoading?: boolean
}

export function SummaryStep({ data, onNext, onPrevious, isLoading }: SummaryStepProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-text-primary mb-2">
          You're All Set!
        </h2>
        <p className="text-text-secondary">
          Review your information and complete your onboarding
        </p>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Summary</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-text-secondary">Transport Method:</span>
            <span className="text-text-primary font-medium">
              {data?.transport || 'Not specified'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-text-secondary">Energy Usage:</span>
            <span className="text-text-primary font-medium">
              {data?.energy || 'Not specified'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-text-secondary">Diet Type:</span>
            <span className="text-text-primary font-medium">
              {data?.diet || 'Not specified'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex space-x-4">
        <button
          type="button"
          onClick={onPrevious}
          className="flex-1 btn-secondary"
        >
          Previous
        </button>
        <button
          type="button"
          onClick={onNext}
          disabled={isLoading}
          className="flex-1 btn-primary"
        >
          {isLoading ? 'Completing...' : 'Complete Setup'}
        </button>
      </div>
    </motion.div>
  )
}