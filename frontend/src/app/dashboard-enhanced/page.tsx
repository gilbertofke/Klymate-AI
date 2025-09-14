'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
    useDashboardData,
    useUserProfile,
    useAIInsight,
    useUserStats,
    useCarbonCredits,
    useRecommendations
} from '@/lib/hooks/useApi'

interface UserProfile {
    name: string
    location: string
    baseline_footprint: number
    primary_goals: string[]
    interests: string[]
    current_habits: string[]
    primary_transport: string
    diet_type: string
    onboarding_completed: boolean
}

interface DashboardMetrics {
    current_footprint: number
    co2_saved_today: number
    co2_saved_total: number
    current_streak: number
    carbon_credits_earned: number
    credits_pending: number
    eco_score: number
    habits_logged_today: number
    weekly_goal_progress: number
}

export default function EnhancedDashboardPage() {
    // Real API data hooks
    const { data: dashboardData, loading: dashboardLoading, error: dashboardError } = useDashboardData()
    const { data: userProfile, loading: profileLoading } = useUserProfile()
    const { data: userStats, loading: statsLoading } = useUserStats()
    const { data: carbonCredits, loading: creditsLoading } = useCarbonCredits()
    const { data: recommendations, loading: recommendationsLoading } = useRecommendations()

    // AI insight with user context
    const { data: aiInsightData, loading: aiLoading } = useAIInsight(
        userProfile ? {
            user_goals: userProfile.primary_goals,
            current_footprint: userProfile.baseline_footprint,
            interests: userProfile.interests
        } : undefined
    )

    // Try to get data from localStorage if backend is not available
    const getLocalStorageData = () => {
        if (typeof window !== 'undefined') {
            const stored = localStorage.getItem('klymate_onboarding_data')
            if (stored) {
                try {
                    return JSON.parse(stored)
                } catch (e) {
                    console.error('Failed to parse stored onboarding data')
                }
            }
        }
        return null
    }

    const localData = getLocalStorageData()

    // Fallback data for when backend is not available
    const fallbackProfile: UserProfile = localData || {
        name: "Demo User",
        location: "Your City",
        baseline_footprint: 8500,
        primary_goals: ["Reduce carbon footprint by 50%", "Earn carbon credits"],
        interests: ["Renewable energy", "Sustainable living"],
        current_habits: ["Recycling", "Energy saving"],
        primary_transport: "car",
        diet_type: "flexitarian",
        onboarding_completed: true
    }

    const fallbackMetrics: DashboardMetrics = {
        current_footprint: 8500,
        co2_saved_today: 0,
        co2_saved_total: 0,
        current_streak: 1,
        carbon_credits_earned: 0,
        credits_pending: 0,
        eco_score: 25,
        habits_logged_today: 0,
        weekly_goal_progress: 0
    }

    // Use real data if available, fallback otherwise
    const profile = userProfile || fallbackProfile
    const metrics = userStats || fallbackMetrics
    const credits = carbonCredits || { balance: 0, pending: 0 }
    const aiInsight = aiInsightData?.message || `Welcome ${profile.name}! Ready to start your climate journey?`

    // Generate fallback AI insight if backend is not available
    const generateFallbackInsight = (profile: UserProfile) => {
        const insights = [
            `Hi ${profile.name}! Based on your ${profile.primary_transport} commute in ${profile.location}, switching to public transport 2 days/week could save you 920 kg CO₂ annually - that's $46 in carbon credits!`,
            `Your ${profile.diet_type} diet is a great start! Try "Meatless Monday" to reduce your food footprint by 15% and earn an extra $23/month in credits.`,
            `I noticed you're interested in ${profile.interests[0]}. There's a solar panel program in ${profile.location} that could cut your energy footprint by 40%!`
        ]
        return insights[Math.floor(Math.random() * insights.length)]
    }

    const getTimeBasedGreeting = () => {
        const hour = new Date().getHours()
        if (hour < 12) return 'Good morning'
        if (hour < 17) return 'Good afternoon'
        return 'Good evening'
    }

    const targetFootprint = profile.baseline_footprint * 0.5 // 50% reduction goal
    const potentialCredits = (profile.baseline_footprint - targetFootprint) * 0.05 // $0.05 per kg saved

    // Show loading state while fetching data
    if (dashboardLoading || profileLoading || statsLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading your personalized dashboard...</p>
                    <p className="text-sm text-gray-500 mt-2">
                        {dashboardLoading && "Fetching dashboard data..."}
                        {profileLoading && "Loading your profile..."}
                        {statsLoading && "Getting your stats..."}
                    </p>
                </div>
            </div>
        )
    }

    // Just use fallback data when there's an error
    // No need to show an error message to the user

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
            <div className="container mx-auto px-4 py-8">
                <div className="max-w-7xl mx-auto">

                    {/* Welcome Header */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="relative overflow-hidden bg-gradient-to-br from-green-500 via-green-400 to-blue-500 rounded-2xl p-8 text-white mb-8"
                    >
                        <div className="relative z-10">
                            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                                <div className="mb-6 lg:mb-0">
                                    <h1 className="text-3xl lg:text-4xl font-bold mb-2">
                                        {getTimeBasedGreeting()}, {profile.name}! 🎉
                                    </h1>
                                    <p className="text-xl text-white/90 mb-2">
                                        Welcome to your personalized climate dashboard
                                    </p>
                                    <p className="text-white/80 max-w-2xl">
                                        Your AI coach has analyzed your profile and created a custom plan to help you reach your goals.
                                    </p>
                                </div>

                                {/* Quick Stats */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                                        <div className="text-2xl font-bold mb-1">{metrics.current_streak}</div>
                                        <div className="text-sm text-white/80">Day Streak</div>
                                    </div>
                                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                                        <div className="text-2xl font-bold mb-1">{metrics.eco_score}</div>
                                        <div className="text-sm text-white/80">Eco Score</div>
                                    </div>
                                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                                        <div className="text-2xl font-bold mb-1">${credits.balance || 0}</div>
                                        <div className="text-sm text-white/80">Credits</div>
                                    </div>
                                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                                        <div className="text-2xl font-bold mb-1">{profile.baseline_footprint.toLocaleString()}</div>
                                        <div className="text-sm text-white/80">kg CO₂/year</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>

                    {/* AI Coach Insight */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white mb-8"
                    >
                        <div className="flex items-start space-x-4">
                            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
                                <span className="text-2xl">🤖</span>
                            </div>
                            <div>
                                <h3 className="font-semibold text-lg mb-2">Your AI Coach Says:</h3>
                                <p className="text-white/90 leading-relaxed">{aiInsight}</p>
                                <button className="mt-3 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                                    Tell me more →
                                </button>
                            </div>
                        </div>
                    </motion.div>

                    {/* Main Dashboard Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                        {/* Left Column - Goals & Progress */}
                        <div className="lg:col-span-2 space-y-6">

                            {/* Your Goals */}
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.6, delay: 0.2 }}
                                className="bg-white rounded-xl shadow-lg p-6"
                            >
                                <h2 className="text-xl font-semibold text-gray-900 mb-4">🎯 Your Climate Goals</h2>
                                <div className="space-y-4">
                                    {profile.primary_goals.map((goal, index) => (
                                        <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                                                    <span className="text-green-600 font-semibold">{index + 1}</span>
                                                </div>
                                                <span className="font-medium text-gray-900">{goal}</span>
                                            </div>
                                            <div className="text-sm text-gray-500">In Progress</div>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>

                            {/* Carbon Footprint Tracker */}
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.6, delay: 0.3 }}
                                className="bg-white rounded-xl shadow-lg p-6"
                            >
                                <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Carbon Footprint Progress</h2>

                                <div className="grid grid-cols-3 gap-4 mb-6">
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-red-600">{profile.baseline_footprint.toLocaleString()}</div>
                                        <div className="text-sm text-gray-500">Baseline (kg/year)</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-blue-600">{metrics.current_footprint.toLocaleString()}</div>
                                        <div className="text-sm text-gray-500">Current (kg/year)</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-green-600">{targetFootprint.toLocaleString()}</div>
                                        <div className="text-sm text-gray-500">Target (kg/year)</div>
                                    </div>
                                </div>

                                <div className="bg-gray-200 rounded-full h-4 mb-4">
                                    <div
                                        className="bg-gradient-to-r from-green-500 to-blue-500 h-4 rounded-full transition-all duration-500"
                                        style={{ width: `${metrics.weekly_goal_progress}%` }}
                                    ></div>
                                </div>

                                <div className="flex justify-between text-sm text-gray-600">
                                    <span>Weekly Goal: {metrics.weekly_goal_progress}% complete</span>
                                    <span>Potential earnings: ${potentialCredits.toFixed(0)}/year</span>
                                </div>
                            </motion.div>

                            {/* Quick Actions */}
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.6, delay: 0.4 }}
                                className="bg-white rounded-xl shadow-lg p-6"
                            >
                                <h2 className="text-xl font-semibold text-gray-900 mb-4">⚡ Quick Actions</h2>
                                <div className="grid grid-cols-2 gap-4">
                                    <button className="flex items-center justify-center space-x-2 p-4 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors">
                                        <span className="text-xl">🚴</span>
                                        <span className="font-medium">Log Transport</span>
                                    </button>
                                    <button className="flex items-center justify-center space-x-2 p-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                        <span className="text-xl">⚡</span>
                                        <span className="font-medium">Track Energy</span>
                                    </button>
                                    <button className="flex items-center justify-center space-x-2 p-4 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors">
                                        <span className="text-xl">🥗</span>
                                        <span className="font-medium">Log Meals</span>
                                    </button>
                                    <button className="flex items-center justify-center space-x-2 p-4 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors">
                                        <span className="text-xl">🤖</span>
                                        <span className="font-medium">Ask AI Coach</span>
                                    </button>
                                </div>
                            </motion.div>
                        </div>

                        {/* Right Column - Insights & Recommendations */}
                        <div className="space-y-6">

                            {/* Today's Impact */}
                            <motion.div
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.6, delay: 0.2 }}
                                className="bg-white rounded-xl shadow-lg p-6"
                            >
                                <h2 className="text-xl font-semibold text-gray-900 mb-4">📅 Today's Impact</h2>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600">CO₂ Saved</span>
                                        <span className="font-semibold text-green-600">{metrics.co2_saved_today} kg</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600">Habits Logged</span>
                                        <span className="font-semibold text-blue-600">{metrics.habits_logged_today}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600">Credits Earned</span>
                                        <span className="font-semibold text-purple-600">${metrics.credits_pending}</span>
                                    </div>
                                </div>

                                <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
                                    <p className="text-sm text-yellow-800">
                                        🌟 <strong>First Day Bonus!</strong> Log your first activity to earn 10 bonus points and start your streak!
                                    </p>
                                </div>
                            </motion.div>

                            {/* Personalized Recommendations */}
                            <motion.div
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.6, delay: 0.3 }}
                                className="bg-white rounded-xl shadow-lg p-6"
                            >
                                <h2 className="text-xl font-semibold text-gray-900 mb-4">💡 Personalized for You</h2>
                                <div className="space-y-3">
                                    <div className="p-3 bg-green-50 rounded-lg">
                                        <div className="font-medium text-green-900">🚗 Transportation</div>
                                        <div className="text-sm text-green-700">Try biking once this week - save 4.6 kg CO₂</div>
                                    </div>
                                    <div className="p-3 bg-blue-50 rounded-lg">
                                        <div className="font-medium text-blue-900">🥗 Diet</div>
                                        <div className="text-sm text-blue-700">One plant-based meal today - save 2.3 kg CO₂</div>
                                    </div>
                                    <div className="p-3 bg-purple-50 rounded-lg">
                                        <div className="font-medium text-purple-900">⚡ Energy</div>
                                        <div className="text-sm text-purple-700">Unplug devices tonight - save 0.8 kg CO₂</div>
                                    </div>
                                </div>
                            </motion.div>

                            {/* Your Interests */}
                            <motion.div
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.6, delay: 0.4 }}
                                className="bg-white rounded-xl shadow-lg p-6"
                            >
                                <h2 className="text-xl font-semibold text-gray-900 mb-4">🔬 Based on Your Interests</h2>
                                <div className="space-y-3">
                                    {profile.interests.map((interest, index) => (
                                        <div key={index} className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer">
                                            <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                                                <span className="text-white text-sm font-bold">{interest[0]}</span>
                                            </div>
                                            <span className="text-gray-700">{interest}</span>
                                        </div>
                                    ))}
                                </div>
                                <button className="mt-4 w-full bg-gradient-to-r from-green-500 to-blue-500 text-white py-2 rounded-lg hover:from-green-600 hover:to-blue-600 transition-colors">
                                    Explore Learning Resources
                                </button>
                            </motion.div>
                        </div>
                    </div>

                    {/* Skip Onboarding Option for New Visitors */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.5 }}
                        className="mt-8 text-center"
                    >
                        <div className="bg-white/50 backdrop-blur-sm rounded-lg p-4">
                            <p className="text-gray-600 text-sm">
                                New visitor? You can explore the dashboard without onboarding.{' '}
                                <button
                                    onClick={() => window.location.href = '/onboarding-enhanced'}
                                    className="text-blue-600 hover:text-blue-800 font-medium underline"
                                >
                                    Complete your profile
                                </button>
                                {' '}for personalized recommendations.
                            </p>
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    )
}