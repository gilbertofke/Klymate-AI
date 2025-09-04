'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  Leaf, 
  Zap, 
  Sun, 
  DollarSign, 
  Trophy, 
  Target,
  ArrowRight,
  Activity
} from 'lucide-react'
import { DashboardData } from '@/types'
import { formatDistanceToNow } from 'date-fns'

interface RecentActivityProps {
  data?: DashboardData
}

export function RecentActivity({ data }: RecentActivityProps) {
  const activities = data?.recent_activity || []

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'habit_logged':
        return Leaf
      case 'badge_earned':
        return Trophy
      case 'credits_earned':
        return DollarSign
      case 'ai_insight':
        return Target
      case 'milestone_reached':
        return Trophy
      case 'agent_interaction':
        return Activity
      default:
        return Activity
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'habit_logged':
        return 'bg-green-100 dark:bg-green-900/20 text-green-600'
      case 'badge_earned':
        return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-600'
      case 'credits_earned':
        return 'bg-blue-100 dark:bg-blue-900/20 text-blue-600'
      case 'ai_insight':
        return 'bg-purple-100 dark:bg-purple-900/20 text-purple-600'
      case 'milestone_reached':
        return 'bg-orange-100 dark:bg-orange-900/20 text-orange-600'
      case 'agent_interaction':
        return 'bg-gray-100 dark:bg-gray-900/20 text-gray-600'
      default:
        return 'bg-gray-100 dark:bg-gray-900/20 text-gray-600'
    }
  }

  const formatImpact = (impact?: number, category?: string) => {
    if (!impact) return null
    
    switch (category) {
      case 'transport':
      case 'energy':
        return `${impact}kg CO₂ saved`
      case 'credits':
        return `$${impact.toFixed(2)} earned`
      default:
        return `+${impact} points`
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Recent Activity
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Your latest climate actions and achievements
          </p>
        </div>
        <Link
          href="/activity"
          className="inline-flex items-center text-sm text-green-600 hover:text-green-700 transition-colors"
        >
          View All
          <ArrowRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="space-y-4">
        {activities.length > 0 ? (
          activities.slice(0, 5).map((activity, index) => {
            const Icon = getActivityIcon(activity.type)
            const colorClasses = getActivityColor(activity.type)
            const impactText = formatImpact(activity.impact, activity.category)
            
            return (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <div className={`p-2 rounded-lg flex-shrink-0 ${colorClasses}`}>
                  <Icon className="w-4 h-4" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {activity.title}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {activity.description}
                      </p>
                      {impactText && (
                        <p className="text-xs text-green-600 dark:text-green-400 mt-1 font-medium">
                          {impactText}
                        </p>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0 ml-2">
                      {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              </motion.div>
            )
          })
        ) : (
          <div className="text-center py-8">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">No recent activity</p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
              Start logging habits to see your activity here
            </p>
          </div>
        )}
      </div>

      {/* Activity Summary */}
      {activities.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="text-center">
              <p className="text-gray-600 dark:text-gray-400">Today's Actions</p>
              <p className="font-semibold text-gray-900 dark:text-gray-100">
                {activities.filter(a => {
                  const today = new Date()
                  const activityDate = new Date(a.timestamp)
                  return activityDate.toDateString() === today.toDateString()
                }).length}
              </p>
            </div>
            <div className="text-center">
              <p className="text-gray-600 dark:text-gray-400">Total Impact</p>
              <p className="font-semibold text-green-600">
                {activities.reduce((sum, a) => sum + (a.impact || 0), 0).toFixed(1)}kg CO₂
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}