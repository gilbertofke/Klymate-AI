'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  Sparkles, 
  Lightbulb, 
  TrendingUp, 
  ArrowRight,
  Brain,
  Target,
  Zap
} from 'lucide-react'

interface AIInsightsProps {
  userId?: string
}

const mockInsights = [
  {
    id: '1',
    title: 'Transportation Opportunity',
    description: 'You could save 15% more CO₂ by biking twice a week instead of driving. Based on your commute pattern, this could save 2.3kg CO₂ weekly.',
    type: 'suggestion',
    impact: 'medium',
    icon: 'lightbulb',
    confidence: 85,
    category: 'transport'
  },
  {
    id: '2',
    title: 'Excellent Progress!',
    description: 'Your consistency has improved 40% this month compared to last month. You\'re on track to exceed your monthly goal.',
    type: 'achievement',
    impact: 'high',
    icon: 'trending',
    confidence: 95,
    category: 'progress'
  },
  {
    id: '3',
    title: 'Energy Optimization',
    description: 'Peak usage detected 6-8 PM. Shifting dishwasher and laundry to off-peak hours could reduce your carbon footprint by 8%.',
    type: 'insight',
    impact: 'medium',
    icon: 'zap',
    confidence: 78,
    category: 'energy'
  }
]

export function AIInsights({ userId }: AIInsightsProps) {
  const insights = mockInsights

  const getInsightIcon = (iconType: string) => {
    switch (iconType) {
      case 'lightbulb':
        return Lightbulb
      case 'trending':
        return TrendingUp
      case 'zap':
        return Zap
      case 'target':
        return Target
      default:
        return Sparkles
    }
  }

  const getImpactStyles = (impact: string) => {
    switch (impact) {
      case 'high':
        return {
          bg: 'bg-green-100 dark:bg-green-900/20',
          text: 'text-green-600',
          badge: 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300'
        }
      case 'medium':
        return {
          bg: 'bg-yellow-100 dark:bg-yellow-900/20',
          text: 'text-yellow-600',
          badge: 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300'
        }
      default:
        return {
          bg: 'bg-blue-100 dark:bg-blue-900/20',
          text: 'text-blue-600',
          badge: 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
        }
    }
  }

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'suggestion':
        return 'AI Suggestion'
      case 'achievement':
        return 'Achievement'
      case 'insight':
        return 'Data Insight'
      default:
        return 'AI Analysis'
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-green-100 to-blue-100 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg">
            <Brain className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              AI Insights
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Personalized recommendations from your AI coach
            </p>
          </div>
        </div>
        <Link
          href="/coach/insights"
          className="inline-flex items-center text-sm text-green-600 hover:text-green-700 transition-colors"
        >
          View All
          <ArrowRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="space-y-4">
        {insights.map((insight, index) => {
          const Icon = getInsightIcon(insight.icon)
          const styles = getImpactStyles(insight.impact)
          
          return (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-sm transition-all cursor-pointer"
            >
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg flex-shrink-0 ${styles.bg}`}>
                  <Icon className={`w-4 h-4 ${styles.text}`} />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {insight.title}
                    </h3>
                    <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                      {insight.confidence}% confidence
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    {insight.description}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${styles.badge}`}>
                        {insight.impact} impact
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {getTypeLabel(insight.type)}
                      </span>
                    </div>
                    
                    <button className="text-xs text-green-600 hover:text-green-700 transition-colors">
                      Take Action →
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* AI Status */}
      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">AI Coach Active</span>
            <span className="text-xs text-gray-500 dark:text-gray-500">• Last analysis: 2 min ago</span>
          </div>
          <Link
            href="/coach/chat"
            className="inline-flex items-center text-sm text-green-600 hover:text-green-700 transition-colors"
          >
            <Sparkles className="w-4 h-4 mr-1" />
            Chat with AI
          </Link>
        </div>
      </div>
    </div>
  )
}