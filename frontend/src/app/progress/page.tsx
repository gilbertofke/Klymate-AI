'use client'

import { useState } from 'react'
import { ProtectedRoute } from '@/components/auth/AuthGuard'
import { useCarbonHistory, useUserStats, useUserProfile } from '@/lib/hooks/useApi'
import { motion } from 'framer-motion'

export default function ProgressPage() {
  const [timeframe, setTimeframe] = useState<'week' | 'month' | 'year'>('month')
  
  const { data: carbonHistory, loading: historyLoading } = useCarbonHistory(timeframe)
  const { data: userStats, loading: statsLoading } = useUserStats()
  const { data: userProfile } = useUserProfile()

  // Mock data for demonstration when backend is not available
  const mockData = {
    week: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      values: [12.5, 8.2, 15.1, 6.8, 11.3, 9.7, 14.2]
    },
    month: {
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      values: [85.2, 72.1, 68.5, 61.3]
    },
    year: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      values: [320, 285, 275, 260, 245, 230, 220, 210, 205, 195, 185, 180]
    }
  }

  const chartData = carbonHistory || mockData[timeframe]
  const stats = userStats || {
    current_streak: 7,
    co2_saved_total: 125.5,
    habits_logged_total: 42,
    eco_score: 78,
    badges_earned: 5,
    weekly_goal_progress: 85
  }

  const baseline = userProfile?.baseline_footprint || 8500
  const currentFootprint = baseline - (stats.co2_saved_total * 365 / 30) // Rough calculation

  const achievements = [
    { 
      title: 'First Steps', 
      description: 'Completed onboarding', 
      icon: '🎯', 
      earned: true,
      date: '2024-01-15'
    },
    { 
      title: 'Week Warrior', 
      description: 'Logged habits for 7 days straight', 
      icon: '🔥', 
      earned: stats.current_streak >= 7,
      date: stats.current_streak >= 7 ? new Date().toISOString().split('T')[0] : null
    },
    { 
      title: 'Carbon Saver', 
      description: 'Saved 100kg CO2', 
      icon: '🌱', 
      earned: stats.co2_saved_total >= 100,
      date: stats.co2_saved_total >= 100 ? '2024-02-01' : null
    },
    { 
      title: 'Habit Master', 
      description: 'Logged 50 habits', 
      icon: '⭐', 
      earned: stats.habits_logged_total >= 50,
      date: stats.habits_logged_total >= 50 ? '2024-02-10' : null
    },
    { 
      title: 'Eco Champion', 
      description: 'Reached 80+ Eco Score', 
      icon: '🏆', 
      earned: stats.eco_score >= 80,
      date: stats.eco_score >= 80 ? '2024-02-15' : null
    }
  ]

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
        <div className="max-w-6xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              📈 My Progress
            </h1>
            <p className="text-gray-600">
              Track your carbon reduction journey and celebrate achievements
            </p>
          </div>

          {/* Key Metrics */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-lg p-6 text-center"
            >
              <div className="text-3xl font-bold text-green-600 mb-2">
                {stats.current_streak}
              </div>
              <div className="text-gray-600">Day Streak</div>
              <div className="text-sm text-gray-500 mt-1">🔥 Keep it up!</div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-2xl shadow-lg p-6 text-center"
            >
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {stats.co2_saved_total.toFixed(1)}
              </div>
              <div className="text-gray-600">kg CO2 Saved</div>
              <div className="text-sm text-gray-500 mt-1">🌍 Great impact!</div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-2xl shadow-lg p-6 text-center"
            >
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {stats.eco_score}
              </div>
              <div className="text-gray-600">Eco Score</div>
              <div className="text-sm text-gray-500 mt-1">📊 {stats.eco_score >= 80 ? 'Excellent!' : stats.eco_score >= 60 ? 'Good job!' : 'Keep going!'}</div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-2xl shadow-lg p-6 text-center"
            >
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {stats.badges_earned}
              </div>
              <div className="text-gray-600">Badges Earned</div>
              <div className="text-sm text-gray-500 mt-1">🏆 Achievements</div>
            </motion.div>
          </div>

          {/* Carbon Footprint Reduction */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Carbon Footprint Reduction</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Your Progress</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Baseline (Annual)</span>
                    <span className="font-bold text-red-600">{baseline.toLocaleString()} kg CO2</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Current (Projected)</span>
                    <span className="font-bold text-orange-600">{currentFootprint.toLocaleString()} kg CO2</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Reduction</span>
                    <span className="font-bold text-green-600">
                      -{((baseline - currentFootprint) / baseline * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="mt-6">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progress to 50% reduction goal</span>
                    <span>{Math.min(((baseline - currentFootprint) / baseline * 100 / 50 * 100), 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(((baseline - currentFootprint) / baseline * 100 / 50 * 100), 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Weekly Goal Progress</h3>
                <div className="text-center">
                  <div className="relative inline-flex items-center justify-center w-32 h-32">
                    <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="text-gray-200"
                        stroke="currentColor"
                        strokeWidth="3"
                        fill="transparent"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className="text-green-500"
                        stroke="currentColor"
                        strokeWidth="3"
                        fill="transparent"
                        strokeDasharray={`${stats.weekly_goal_progress}, 100`}
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                    <div className="absolute text-center">
                      <div className="text-2xl font-bold text-gray-900">{stats.weekly_goal_progress}%</div>
                      <div className="text-sm text-gray-600">Complete</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Carbon History Chart */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Carbon History</h2>
              <div className="flex space-x-2">
                {(['week', 'month', 'year'] as const).map((period) => (
                  <button
                    key={period}
                    onClick={() => setTimeframe(period)}
                    className={`px-4 py-2 rounded-lg capitalize transition-colors ${
                      timeframe === period
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {period}
                  </button>
                ))}
              </div>
            </div>

            {historyLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                <p className="text-gray-600 mt-2">Loading chart data...</p>
              </div>
            ) : (
              <div className="h-64 flex items-end justify-between space-x-2">
                {chartData.values.map((value: number, index: number) => (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-gradient-to-t from-green-400 to-green-600 rounded-t-lg transition-all duration-500 hover:from-green-500 hover:to-green-700"
                      style={{ height: `${(value / Math.max(...chartData.values)) * 200}px` }}
                    ></div>
                    <div className="text-xs text-gray-600 mt-2 text-center">
                      {chartData.labels[index]}
                    </div>
                    <div className="text-xs font-medium text-gray-800">
                      {value.toFixed(1)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Achievements */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Achievements</h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {achievements.map((achievement, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    achievement.earned
                      ? 'border-green-200 bg-green-50'
                      : 'border-gray-200 bg-gray-50 opacity-60'
                  }`}
                >
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-2xl">{achievement.icon}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900">{achievement.title}</h3>
                      <p className="text-sm text-gray-600">{achievement.description}</p>
                    </div>
                  </div>
                  {achievement.earned && achievement.date && (
                    <div className="text-xs text-green-600 font-medium">
                      Earned on {new Date(achievement.date).toLocaleDateString()}
                    </div>
                  )}
                  {!achievement.earned && (
                    <div className="text-xs text-gray-500">
                      Not yet earned
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}