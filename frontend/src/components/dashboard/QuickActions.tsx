'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { 
  MessageCircle, 
  Lightbulb, 
  BarChart3, 
  Plus, 
  Sparkles,
  History,
  Settings,
  TrendingUp,
  Loader2
} from 'lucide-react'
import { DashboardData } from '@/types'
import { ThemeToggle } from '@/components/theme/ThemeToggle'
import { useState, useEffect } from 'react'
import { useLogHabit, useCarbonCredits, useUserStats } from '@/lib/hooks/useApi'
import toast from 'react-hot-toast'

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

const quickActions = [
  {
    id: 'theme',
    name: 'Theme Settings',
    description: 'Customize your experience',
    href: '#',
    icon: Settings,
    color: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-100 dark:bg-purple-900/20',
    textColor: 'text-purple-600'
  },
  {
    id: '1',
    name: 'Track Transport',
    description: 'Log your daily transportation',
    href: '/track/transport',
    icon: MessageCircle,
    color: 'from-blue-500 to-blue-600',
    bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    textColor: 'text-blue-600'
  },
  {
    id: '2',
    name: 'Track Energy',
    description: 'Monitor home energy usage',
    href: '/track/energy',
    icon: Lightbulb,
    color: 'from-yellow-500 to-yellow-600',
    bgColor: 'bg-yellow-100 dark:bg-yellow-900/20',
    textColor: 'text-yellow-600'
  },
  {
    id: '3',
    name: 'Track Diet',
    description: 'Log your meals and food choices',
    href: '/track/diet',
    icon: BarChart3,
    color: 'from-green-500 to-green-600',
    bgColor: 'bg-green-100 dark:bg-green-900/20',
    textColor: 'text-green-600'
  },
]

export function QuickActions({ data }: QuickActionsProps) {
  const router = useRouter()
  const [showThemeToggle, setShowThemeToggle] = useState(false)
  const [loading, setLoading] = useState<string>('')
  
  const { logHabit, isLoading: isLoggingHabit } = useLogHabit()
  const { claimCredits, isLoading: isClaimingCredits } = useCarbonCredits()
  const { refreshStats, isLoading: isRefreshingStats } = useUserStats()

  const handleQuickAction = async (type: string) => {
    try {
      setLoading(type)
      
      switch (type) {
        case 'transport':
        case 'energy':
        case 'diet':
          await logHabit({ type, value: 1 })
          toast.success(`Successfully logged ${type} activity`)
          await refreshStats()
          break
        case 'credits':
          await claimCredits()
          toast.success('Carbon credits claimed successfully')
          break
      }
    } catch (error) {
      toast.error('Failed to perform action. Please try again.')
      console.error('Quick action error:', error)
    } finally {
      setLoading('')
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      {showThemeToggle && (
        <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg backdrop-blur-sm">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Theme Settings</h3>
            <button
              onClick={() => setShowThemeToggle(false)}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>
          <ThemeToggle />
        </div>
      )}

      {/* Main Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-500 to-blue-500">
            Start Earning Green
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Four simple steps to start earning while saving the planet
          </p>
        </div>
        <Link
          href="/coach/chat"
          className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg hover:from-green-600 hover:to-blue-600 transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
        >
          <Sparkles className="w-4 h-4 mr-2" />
          Start Now
        </Link>
      </div>

      {/* Onboarding Steps */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {onboardingSteps.map((step, index) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <Link
              href={step.href}
              className="group relative block h-full"
            >
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur"
                style={{
                  background: `linear-gradient(135deg, var(--color-primary), var(--color-accent))`,
                  opacity: 0.1
                }}
              />
              <div className="relative h-full p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/80 backdrop-blur-sm hover:border-primary transition-all duration-300 group-hover:shadow-lg group-hover:shadow-primary/5">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className={`p-3 rounded-lg ${step.bgColor} backdrop-blur-sm relative overflow-hidden group-hover:scale-110 transition-transform duration-300`}>
                      <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-20 transition-opacity" style={{ background: `linear-gradient(135deg, ${step.color.split(' ')[1]}, ${step.color.split(' ')[3]})` }} />
                      <step.icon className={`w-6 h-6 ${step.textColor} relative z-10`} />
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-primary mb-1">Step {step.step}</div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary transition-colors">
                      {step.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {step.description}
                    </p>
                  </div>
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {quickActions.map((action, index) => {
          const Icon = action.icon;
          const isThemeAction = action.id === 'theme';
          
          return (
            <motion.div
              key={action.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              {isThemeAction ? (
                <button
                  onClick={() => setShowThemeToggle(true)}
                  className="w-full text-left p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-md transition-all group"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`p-2 rounded-lg ${action.bgColor}`}>
                      <Icon className={`w-5 h-5 ${action.textColor}`} />
                    </div>
                    <span className="font-medium text-gray-900 dark:text-gray-100 group-hover:text-primary">
                      {action.name}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {action.description}
                  </p>
                </button>
              ) : (
                <button
                  onClick={() => handleQuickAction(action.id)}
                  className="w-full text-left p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-md transition-all group relative"
                  disabled={loading === action.id}
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`p-2 rounded-lg ${action.bgColor}`}>
                      {loading === action.id ? (
                        <Loader2 className={`w-5 h-5 ${action.textColor} animate-spin`} />
                      ) : (
                        <Icon className={`w-5 h-5 ${action.textColor}`} />
                      )}
                    </div>
                    <span className="font-medium text-gray-900 dark:text-gray-100 group-hover:text-primary">
                      {action.name}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {action.description}
                  </p>
                  {loading === action.id && (
                    <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 rounded-lg backdrop-blur-sm" />
                  )}
                </button>)
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Additional Actions */}
      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            onClick={() => handleQuickAction('credits')}
            disabled={loading === 'credits'}
            className="relative inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === 'credits' ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4 mr-2" />
            )}
            Carbon Credits
            {loading === 'credits' && (
              <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 rounded-lg backdrop-blur-sm" />
            )}
          </button>
          <button
            onClick={() => router.push('/ai-coach')}
            className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <MessageCircle className="w-4 h-4 mr-2" />
            AI Coach Chat
          </button>
          <button
            onClick={refreshStats}
            disabled={loading === 'refresh'}
            className="relative inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === 'refresh' ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <TrendingUp className="w-4 h-4 mr-2" />
            )}
            View Insights
            {loading === 'refresh' && (
              <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 rounded-lg backdrop-blur-sm" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}