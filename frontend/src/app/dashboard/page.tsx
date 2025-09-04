'use client'

import { motion } from 'framer-motion'
import { useAuth } from '@/lib/auth/AuthProvider'
import { ProtectedRoute } from '@/components/auth/AuthGuard'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { MetricsGrid } from '@/components/dashboard/MetricsGrid'
import { QuickActions } from '@/components/dashboard/QuickActions'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { AIInsights } from '@/components/dashboard/AIInsights'

export default function DashboardPage() {
  const { user } = useAuth()

  // Mock data - in real app this would come from API
  const mockDashboardData = {
    user: user || {
      id: 1,
      name: 'Demo User',
      display_name: 'Demo User',
      email: 'demo@example.com',
      eco_score: 85,
      total_co2_saved: 2.4,
      current_streak: 7,
      onboarding_completed: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      firebase_uid: 'demo',
      email_verified: true
    },
    metrics: {
      co2_saved: 2.4,
      co2_saved_trend: 12.5,
      active_agents: 3,
      energy_optimized: 85,
      energy_efficiency: 78,
      carbon_credits: 125.50,
      credits_earning_rate: 15.2,
      habits_this_week: 12,
      current_streak: 7
    },
    active_agents: [
      {
        id: 'carbon-tracker',
        name: 'Carbon Tracker',
        description: 'Monitors your daily carbon footprint',
        specialization: 'Carbon Monitoring',
        status: 'active' as const,
        last_activity: new Date().toISOString(),
        capabilities: ['tracking', 'analysis'],
        avatar: '🌱'
      },
      {
        id: 'energy-optimizer',
        name: 'Energy Optimizer',
        description: 'Optimizes your energy consumption',
        specialization: 'Energy Efficiency',
        status: 'active' as const,
        last_activity: new Date().toISOString(),
        capabilities: ['optimization', 'recommendations'],
        avatar: '⚡'
      },
      {
        id: 'solar-predictor',
        name: 'Solar Predictor',
        description: 'Predicts solar energy potential',
        specialization: 'Renewable Energy',
        status: 'inactive' as const,
        last_activity: new Date().toISOString(),
        capabilities: ['prediction', 'analysis'],
        avatar: '☀️'
      }
    ],
    recent_activity: [
      {
        id: '1',
        user_id: 1,
        type: 'habit_logged' as const,
        title: 'Biked to work',
        description: 'Logged cycling habit - saved 2.3kg CO₂',
        icon: '🚴',
        color: 'green',
        timestamp: new Date().toISOString(),
        impact: 2.3,
        category: 'transport'
      },
      {
        id: '2',
        user_id: 1,
        type: 'badge_earned' as const,
        title: 'Eco Warrior Badge',
        description: 'Earned for 7-day streak!',
        icon: '🏆',
        color: 'yellow',
        timestamp: new Date().toISOString(),
        category: 'achievement'
      },
      {
        id: '3',
        user_id: 1,
        type: 'credits_earned' as const,
        title: 'Carbon Credits Earned',
        description: 'Earned $12.50 in carbon credits',
        icon: '💰',
        color: 'blue',
        timestamp: new Date().toISOString(),
        impact: 12.5,
        category: 'credits'
      }
    ],
    quick_stats: {
      total_co2_saved: 2.4,
      habits_this_month: 45,
      badges_earned: 8,
      leaderboard_position: 23
    },
    generated_at: new Date().toISOString()
  }

  const getTimeBasedGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 17) return 'Good afternoon'
    return 'Good evening'
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-8">
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative overflow-hidden bg-gradient-to-br from-green-500 via-green-400 to-blue-500 rounded-2xl p-8 text-white"
          >
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10">
              <div 
                className="absolute inset-0" 
                style={{
                  backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                  backgroundRepeat: 'repeat'
                }}
              />
            </div>

            <div className="relative z-10">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                <div className="mb-6 lg:mb-0">
                  <motion.h1
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="text-3xl lg:text-4xl font-bold mb-2"
                  >
                    {getTimeBasedGreeting()}, {user?.display_name || user?.name || 'there'}! 👋
                  </motion.h1>
                  <motion.p
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 }}
                    className="text-xl text-white/90 mb-4"
                  >
                    Welcome to your AI-powered climate dashboard
                  </motion.p>
                  <motion.p
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="text-white/80 max-w-2xl"
                  >
                    Track your carbon impact, earn credits, and get personalized AI insights 
                    to accelerate your journey toward a sustainable lifestyle.
                  </motion.p>
                </div>

                {/* Stats Cards */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: 0.5 }}
                  className="grid grid-cols-2 gap-4 lg:gap-6"
                >
                  <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                    <div className="text-2xl lg:text-3xl font-bold mb-1">
                      {mockDashboardData.metrics.current_streak}
                    </div>
                    <div className="text-sm text-white/80">Day Streak</div>
                  </div>
                  <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                    <div className="text-2xl lg:text-3xl font-bold mb-1">
                      {mockDashboardData.metrics.co2_saved}t
                    </div>
                    <div className="text-sm text-white/80">CO₂ Saved</div>
                  </div>
                  <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                    <div className="text-2xl lg:text-3xl font-bold mb-1">
                      ${mockDashboardData.metrics.carbon_credits}
                    </div>
                    <div className="text-sm text-white/80">Credits</div>
                  </div>
                  <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                    <div className="text-2xl lg:text-3xl font-bold mb-1">
                      {mockDashboardData.metrics.active_agents}
                    </div>
                    <div className="text-sm text-white/80">AI Agents</div>
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.div>

          {/* Metrics Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <MetricsGrid data={mockDashboardData} />
          </motion.div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Quick Actions & AI Insights */}
            <div className="lg:col-span-2 space-y-8">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <QuickActions data={mockDashboardData} />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <AIInsights />
              </motion.div>
            </div>

            {/* Right Column - Recent Activity */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              <RecentActivity data={mockDashboardData} />
            </motion.div>
          </div>

          {/* Refresh Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="text-center text-sm text-gray-500"
          >
            Last updated: {new Date().toLocaleTimeString()}
          </motion.div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}