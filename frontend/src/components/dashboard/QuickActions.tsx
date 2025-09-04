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

interface QuickActionsProps {
  data?: DashboardData
}

const quickActions = [
  {
    id: '1',
    name: 'Chat with AI Coach',
    description: 'Get personalized climate advice',
    href: '/coach/chat',
    icon: MessageCircle,
    color: 'from-green-500 to-green-600',
    bgColor: 'bg-green-100 dark:bg-green-900/20',
    textColor: 'text-green-600'
  },
  {
    id: '2',
    name: 'View AI Suggestions',
    description: 'See personalized recommendations',
    href: '/coach/suggestions',
    icon: Lightbulb,
    color: 'from-blue-500 to-blue-600',
    bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    textColor: 'text-blue-600'
  },
  {
    id: '3',
    name: 'Carbon Insights',
    description: 'Analyze your footprint trends',
    href: '/coach/insights',
    icon: BarChart3,
    color: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-100 dark:bg-purple-900/20',
    textColor: 'text-purple-600'
  },
]

export function QuickActions({ data }: QuickActionsProps) {

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            AI Coach Actions
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Quick access to your AI-powered climate tools
          </p>
        </div>
        <Link
          href="/coach/chat"
          className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg hover:from-green-600 hover:to-blue-600 transition-all shadow-sm"
        >
          <Sparkles className="w-4 h-4 mr-2" />
          Open Chat
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {quickActions.map((action, index) => {
          const Icon = action.icon
          
          return (
            <motion.div
              key={action.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <Link
                href={action.href}
                className="block p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-md transition-all group"
              >
                <div className="flex items-center space-x-3 mb-3">
                  <div className={`p-2 rounded-lg ${action.bgColor}`}>
                    <Icon className={`w-5 h-5 ${action.textColor}`} />
                  </div>
                  <h3 className="font-medium text-gray-900 dark:text-gray-100 group-hover:text-green-600 transition-colors">
                    {action.name}
                  </h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {action.description}
                </p>
              </Link>
            </motion.div>
          )
        })}
      </div>

      {/* Additional Actions */}
      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Link
            href="/coach/history"
            className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <History className="w-4 h-4 mr-2" />
            Chat History
          </Link>
          <Link
            href="/coach/settings"
            className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <Settings className="w-4 h-4 mr-2" />
            AI Settings
          </Link>
          <Link
            href="/analytics"
            className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            View Analytics
          </Link>
        </div>
      </div>
    </div>
  )
}