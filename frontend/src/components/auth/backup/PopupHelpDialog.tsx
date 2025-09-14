'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { getPopupHelpContent } from '@/lib/auth/popupUtils'

interface PopupHelpDialogProps {
  isOpen: boolean
  onClose: () => void
}

export default function PopupHelpDialog({ isOpen, onClose }: PopupHelpDialogProps) {
  const helpContent = getPopupHelpContent()

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50"
            onClick={onClose}
          />
          
          {/* Dialog */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  {helpContent.title}
                </h3>
                <button
                  onClick={onClose}
                  className="text-text-secondary hover:text-text-primary transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <p className="text-text-secondary mb-4">
                {helpContent.message}
              </p>
              
              <ol className="list-decimal list-inside space-y-2 mb-4">
                {helpContent.instructions.map((instruction, index) => (
                  <li key={index} className="text-sm text-text-secondary">
                    {instruction}
                  </li>
                ))}
              </ol>
              
              <div className="bg-bg-secondary p-3 rounded-lg mb-4">
                <p className="text-sm text-text-secondary">
                  💡 <strong>Tip:</strong> {helpContent.fallbackMessage}
                </p>
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-sm font-medium text-text-primary bg-bg-secondary hover:bg-border-medium rounded-lg transition-colors"
                >
                  Got it
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

/**
 * Hook to manage popup help dialog state
 */
export function usePopupHelp() {
  const [isOpen, setIsOpen] = useState(false)
  
  const showHelp = () => setIsOpen(true)
  const hideHelp = () => setIsOpen(false)
  
  return {
    isOpen,
    showHelp,
    hideHelp,
    PopupHelpDialog: (props: Omit<PopupHelpDialogProps, 'isOpen' | 'onClose'>) => (
      <PopupHelpDialog {...props} isOpen={isOpen} onClose={hideHelp} />
    )
  }
}