'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sun, Moon, Laptop, Palette } from 'lucide-react'
import { useThemeStore, ThemeMode, ThemeAccent } from '@/lib/theme/themeStore'

export function ThemeToggle() {
  const { mode, accent, setMode, setAccent } = useThemeStore()
  const [showPalette, setShowPalette] = useState(false)

  const themeOptions: { value: ThemeMode; icon: React.ComponentType; label: string }[] = [
    { value: 'light', icon: Sun, label: 'Light' },
    { value: 'dark', icon: Moon, label: 'Dark' },
    { value: 'system', icon: Laptop, label: 'System' },
  ]

  const accentOptions: { value: ThemeAccent; label: string; color: string }[] = [
    { value: 'green', label: 'Green', color: 'bg-green-500' },
    { value: 'blue', label: 'Blue', color: 'bg-blue-500' },
    { value: 'purple', label: 'Purple', color: 'bg-purple-500' },
    { value: 'teal', label: 'Teal', color: 'bg-teal-500' },
  ]

  return (
    <div className="relative">
      <div className="flex items-center space-x-2">
        {/* Theme Mode Toggle */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex p-1 space-x-1">
            {themeOptions.map(({ value, icon: Icon, label }) => (
              <button
                key={value}
                onClick={() => setMode(value)}
                className={`
                  p-2 rounded-md transition-colors
                  ${mode === value 
                    ? 'bg-primary text-white' 
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }
                `}
                title={label}
              >
                <Icon className="w-4 h-4" />
              </button>
            ))}
          </div>
        </div>

        {/* Accent Color Toggle */}
        <button
          onClick={() => setShowPalette(!showPalette)}
          className={`
            p-2 rounded-md transition-colors
            ${showPalette 
              ? 'bg-primary text-white' 
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }
            border border-gray-200 dark:border-gray-700
          `}
          title="Change accent color"
        >
          <Palette className="w-4 h-4" />
        </button>
      </div>

      {/* Accent Color Palette */}
      <AnimatePresence>
        {showPalette && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            className="absolute right-0 mt-2 p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
          >
            <div className="grid grid-cols-2 gap-2">
              {accentOptions.map(({ value, label, color }) => (
                <button
                  key={value}
                  onClick={() => {
                    setAccent(value)
                    setShowPalette(false)
                  }}
                  className={`
                    flex items-center space-x-2 p-2 rounded-md transition-colors
                    ${accent === value 
                      ? 'bg-gray-100 dark:bg-gray-700' 
                      : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                    }
                  `}
                >
                  <div className={`w-4 h-4 rounded-full ${color}`} />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {label}
                  </span>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}