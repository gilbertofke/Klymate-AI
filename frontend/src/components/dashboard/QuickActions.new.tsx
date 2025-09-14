'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  MessageCircle, 
  Lightbulb, 
  BarChart3, 
  Plus, 
  Sparkles,
  History,
  Settings,
  TrendingUp
} from 'lucide-react'
import { DashboardData } from '@/types'
import { ThemeToggle } from '@/components/theme/ThemeToggle'
import { useState, useEffect } from 'react'

interface QuickActionsProps {
  data?: DashboardData
}

const onboardingSteps = [
  {
    id: 'survey',
    step: '01',
    name: 'Complete Survey',
    description: 'Tell us about your lifestyle to calculate your carbon baseline and get personalized insights',
    href: '/survey',
    icon: MessageCircle,
    color: 'from-cyan-500 to-blue-600',
    bgColor: 'bg-cyan-100 dark:bg-cyan-900/20',
    textColor: 'text-cyan-600'
  },
  {
    id: 'habits',
    step: '02',
    name: 'Track Habits',
    description: 'Log your eco-friendly activities and sustainable choices with our intuitive interface',
    href: '/habits',
    icon: BarChart3,
    color: 'from-emerald-500 to-green-600',
    bgColor: 'bg-emerald-100 dark:bg-emerald-900/20',
    textColor: 'text-emerald-600'
  },
  {
    id: 'coaching',
    step: '03',
    name: 'Get AI Coaching',
    description: 'Receive personalized recommendations from specialized AI agents to maximize your impact',
    href: '/coach',
    icon: Sparkles,
    color: 'from-violet-500 to-purple-600',
    bgColor: 'bg-violet-100 dark:bg-violet-900/20',
    textColor: 'text-violet-600'
  },
  {
    id: 'credits',
    step: '04',
    name: 'Earn Credits',
    description: 'Convert your verified carbon savings into real money through our credit system',
    href: '/credits',
    icon: TrendingUp,
    color: 'from-amber-500 to-yellow-600',
    bgColor: 'bg-amber-100 dark:bg-amber-900/20',
    textColor: 'text-amber-600'
  },
]

interface ActionCardProps {
  action: {
    id: string
    name: string
    description: string
    href: string
    icon: any
    color: string
    bgColor: string
    textColor: string
  }
}

function ActionCard({ action }: ActionCardProps) {
  const Icon = action.icon
  return (
    <div className="group relative p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/80 backdrop-blur-sm hover:border-primary transition-all duration-300">
      {/* Background Glow Effect */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-r opacity-0 group-hover:opacity-10 transition-opacity duration-300 blur"
        style={{
          background: `linear-gradient(135deg, var(--color-primary), var(--color-accent))`
        }}
      />
      
      {/* Content */}
      <div className="relative z-10 flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className={`p-3 rounded-lg ${action.bgColor} backdrop-blur-sm relative overflow-hidden group-hover:scale-110 transition-transform duration-300`}>
            <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-20 transition-opacity" 
              style={{ background: `linear-gradient(135deg, ${action.color.split(' ')[1]}, ${action.color.split(' ')[3]})` }} 
            />
            <Icon className={`w-6 h-6 ${action.textColor} relative z-10`} />
          </div>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary transition-colors">
            {action.name}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {action.description}
          </p>
        </div>
      </div>
    </div>
  )
}

export function QuickActions({ data }: QuickActionsProps) {
  const [showThemeToggle, setShowThemeToggle] = useState(false)

  return (
    <div className="relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 overflow-hidden">
      {/* Background Patterns */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 pointer-events-none" />
      
      {/* Theme Toggle Panel */}
      {showThemeToggle && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="mb-6 p-4 bg-gray-50/80 dark:bg-gray-700/80 rounded-xl backdrop-blur-sm border border-gray-200 dark:border-gray-600"
        >
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
              Theme Settings
            </h3>
            <button
              onClick={() => setShowThemeToggle(false)}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>
          <ThemeToggle />
        </motion.div>
      )}

      {/* Main Content */}
      <div className="relative">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
              Start Your Journey
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Four simple steps to start earning while saving the planet
            </p>
          </div>
          <Link
            href="/coach/chat"
            className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-primary to-accent text-white rounded-lg hover:shadow-lg transition-all transform hover:-translate-y-0.5"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Get Started
          </Link>
        </div>

        {/* Onboarding Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {onboardingSteps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
            >
              <Link href={step.href} className="block h-full">
                <ActionCard action={step} />
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <Link
            href="/rewards"
            className="inline-flex items-center justify-center px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-all group"
          >
            <div className="p-2 mr-2 rounded-lg bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
              <Sparkles className="w-4 h-4" />
            </div>
            Carbon Credits
          </Link>
          <Link
            href="/coach/chat"
            className="inline-flex items-center justify-center px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-all group"
          >
            <div className="p-2 mr-2 rounded-lg bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 group-hover:scale-110 transition-transform">
              <MessageCircle className="w-4 h-4" />
            </div>
            AI Coach
          </Link>
          <Link
            href="/insights"
            className="inline-flex items-center justify-center px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-all group"
          >
            <div className="p-2 mr-2 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform">
              <TrendingUp className="w-4 h-4" />
            </div>
            View Insights
          </Link>
        </div>
      </div>
    </div>
  )
}