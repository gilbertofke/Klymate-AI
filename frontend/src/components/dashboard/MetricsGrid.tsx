'use client'

import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown, 
  Leaf, 
  Zap, 
  Target, 
  Award 
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { DashboardData } from '@/types'

interface MetricsGridProps {
  data?: DashboardData
  isLoading?: boolean
}

export function MetricsGrid({ data, isLoading }: MetricsGridProps) {
  if (isLoading) {
    return <MetricsGridSkeleton />
  }

  // Extract metrics from real backend data structure
  const metrics_data = data?.metrics as any || {}
  const quick_stats = data?.quick_stats as any || {}
  
  const metrics = [
    {
      title: 'Total CO₂ Saved',
      value: metrics_data.co2_saved || quick_stats.total_co2_saved || 0,
      unit: 'kg',
      change: metrics_data.co2_saved_trend || 0,
      changeType: (metrics_data.co2_saved_trend || 0) >= 0 ? 'increase' : 'decrease',
      period: 'this month',
      icon: Leaf,
      iconColor: 'text-green-600',
      iconBg: 'bg-green-100 dark:bg-green-900/20',
      description: 'Carbon footprint reduction'
    },
    {
      title: 'Current Streak',
      value: metrics_data.current_streak || 0,
      unit: 'days',
      change: 0,
      changeType: 'increase',
      period: 'active streak',
      icon: Target,
      iconColor: 'text-blue-600',
      iconBg: 'bg-blue-100 dark:bg-blue-900/20',
      description: 'Consecutive active days'
    },
    {
      title: 'Habits This Week',
      value: metrics_data.habits_this_week || quick_stats.habits_this_month || 0,
      unit: 'habits',
      change: 0,
      changeType: 'increase',
      period: 'vs last week',
      icon: Zap,
      iconColor: 'text-yellow-600',
      iconBg: 'bg-yellow-100 dark:bg-yellow-900/20',
      description: 'Sustainable actions logged'
    },
    {
      title: 'Eco Score',
      value: data?.user?.eco_score || 0,
      unit: 'pts',
      change: 0,
      changeType: 'increase',
      period: 'this month',
      icon: Award,
      iconColor: 'text-purple-600',
      iconBg: 'bg-purple-100 dark:bg-purple-900/20',
      description: 'Overall sustainability score'
    },
  ]

  const formatValue = (value: number, unit: string) => {
    if (unit === 'kg' && value >= 1000) {
      return { value: (value / 1000).toFixed(1), unit: 't' }
    }
    return { value: value.toLocaleString(), unit }
  }

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : ''
    return `${sign}${change.toFixed(1)}%`
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metrics.map((metric, index) => {
        const formattedValue = formatValue(metric.value, metric.unit)
        const Icon = metric.icon
        const TrendIcon = metric.changeType === 'increase' ? TrendingUp : TrendingDown
        const trendColor = metric.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
        
        return (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className={cn('p-2 rounded-lg', metric.iconBg)}>
                <Icon className={cn('w-5 h-5', metric.iconColor)} />
              </div>
              
              {Math.abs(metric.change) > 0 && (
                <div className={cn('flex items-center text-sm font-medium', trendColor)}>
                  <TrendIcon className="w-4 h-4 mr-1" />
                  {formatChange(metric.change)}
                </div>
              )}
            </div>
            
            {/* Value */}
            <div className="space-y-1">
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {formattedValue.value}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {formattedValue.unit}
                </span>
              </div>
              
              <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {metric.title}
              </h3>
              
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {metric.description}
              </p>
              
              {metric.period && (
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  {metric.period}
                </p>
              )}
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

// Skeleton loader
export function MetricsGridSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {Array.from({ length: 4 }).map((_, index) => (
        <div
          key={index}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 animate-pulse"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-9 h-9 bg-gray-300 dark:bg-gray-600 rounded-lg" />
            <div className="w-12 h-4 bg-gray-300 dark:bg-gray-600 rounded" />
          </div>
          
          <div className="space-y-2">
            <div className="flex items-baseline space-x-2">
              <div className="w-16 h-8 bg-gray-300 dark:bg-gray-600 rounded" />
              <div className="w-8 h-4 bg-gray-300 dark:bg-gray-600 rounded" />
            </div>
            <div className="w-24 h-4 bg-gray-300 dark:bg-gray-600 rounded" />
            <div className="w-32 h-3 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="w-20 h-3 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        </div>
      ))}
    </div>
  )
}