'use client'

import { useState } from 'react'
import { ProtectedRoute } from '@/components/auth/AuthGuard'
import { useCarbonCredits, useCreditHistory } from '@/lib/hooks/useApi'
import { motion } from 'framer-motion'

interface CreditTransaction {
    id: string
    type: 'earned' | 'redeemed'
    amount: number
    reason: string
    date: string
    status: 'completed' | 'pending'
}

export default function CreditsPage() {
    const [activeTab, setActiveTab] = useState<'overview' | 'history' | 'marketplace'>('overview')

    const { data: creditsData, loading: creditsLoading } = useCarbonCredits()
    const { data: creditHistory, loading: historyLoading } = useCreditHistory()

    // Mock data for demonstration
    const mockCredits = creditsData || {
        balance: 47.5,
        pending: 12.3,
        lifetime_earned: 156.8,
        lifetime_redeemed: 109.3
    }

    const mockHistory: CreditTransaction[] = creditHistory || [
        {
            id: '1',
            type: 'earned',
            amount: 2.5,
            reason: 'Walked to work instead of driving',
            date: '2024-02-15',
            status: 'completed'
        },
        {
            id: '2',
            type: 'earned',
            amount: 1.8,
            reason: 'Used public transport',
            date: '2024-02-14',
            status: 'completed'
        },
        {
            id: '3',
            type: 'redeemed',
            amount: -10.0,
            reason: 'Tree planting project donation',
            date: '2024-02-13',
            status: 'completed'
        },
        {
            id: '4',
            type: 'earned',
            amount: 3.2,
            reason: 'Plant-based meal choices',
            date: '2024-02-12',
            status: 'completed'
        },
        {
            id: '5',
            type: 'earned',
            amount: 1.5,
            reason: 'Energy conservation at home',
            date: '2024-02-11',
            status: 'pending'
        }
    ]

    const marketplaceItems = [
        {
            id: 1,
            title: 'Plant 10 Trees',
            description: 'Support reforestation efforts in the Amazon rainforest',
            cost: 25,
            impact: '250 kg CO2 offset over 10 years',
            image: '🌳',
            category: 'Reforestation'
        },
        {
            id: 2,
            title: 'Solar Panel Fund',
            description: 'Contribute to solar panel installation in rural communities',
            cost: 50,
            impact: '500 kg CO2 offset annually',
            image: '☀️',
            category: 'Renewable Energy'
        },
        {
            id: 3,
            title: 'Ocean Cleanup',
            description: 'Support ocean plastic removal and marine conservation',
            cost: 15,
            impact: 'Remove 50kg of ocean plastic',
            image: '🌊',
            category: 'Conservation'
        },
        {
            id: 4,
            title: 'Wind Farm Project',
            description: 'Invest in clean wind energy infrastructure',
            cost: 75,
            impact: '750 kg CO2 offset annually',
            image: '💨',
            category: 'Renewable Energy'
        },
        {
            id: 5,
            title: 'Eco-Friendly Products',
            description: 'Discount on sustainable products from partner brands',
            cost: 10,
            impact: '20% off eco-friendly purchases',
            image: '🛍️',
            category: 'Rewards'
        },
        {
            id: 6,
            title: 'Carbon Offset Certificate',
            description: 'Official certificate for your carbon neutrality efforts',
            cost: 30,
            impact: 'Verified 300 kg CO2 offset',
            image: '📜',
            category: 'Certification'
        }
    ]

    const handleRedeem = (item: any) => {
        if (mockCredits.balance >= item.cost) {
            alert(`🎉 Successfully redeemed: ${item.title}!\n\nYou spent ${item.cost} credits.\nImpact: ${item.impact}`)
        } else {
            alert(`❌ Insufficient credits!\n\nYou need ${item.cost} credits but only have ${mockCredits.balance.toFixed(1)}.`)
        }
    }

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
                <div className="max-w-6xl mx-auto px-4 py-8">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h1 className="text-4xl font-bold text-gray-900 mb-2">
                            🌱 Carbon Credits
                        </h1>
                        <p className="text-gray-600">
                            Earn credits through eco-friendly actions and redeem them for real impact
                        </p>
                    </div>

                    {/* Credits Overview */}
                    <div className="grid md:grid-cols-4 gap-6 mb-8">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white rounded-2xl shadow-lg p-6 text-center"
                        >
                            <div className="text-3xl font-bold text-green-600 mb-2">
                                {mockCredits.balance.toFixed(1)}
                            </div>
                            <div className="text-gray-600">Available Credits</div>
                            <div className="text-sm text-gray-500 mt-1">💰 Ready to use</div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="bg-white rounded-2xl shadow-lg p-6 text-center"
                        >
                            <div className="text-3xl font-bold text-orange-600 mb-2">
                                {mockCredits.pending.toFixed(1)}
                            </div>
                            <div className="text-gray-600">Pending Credits</div>
                            <div className="text-sm text-gray-500 mt-1">⏳ Processing</div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="bg-white rounded-2xl shadow-lg p-6 text-center"
                        >
                            <div className="text-3xl font-bold text-blue-600 mb-2">
                                {mockCredits.lifetime_earned.toFixed(1)}
                            </div>
                            <div className="text-gray-600">Total Earned</div>
                            <div className="text-sm text-gray-500 mt-1">🏆 All time</div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                            className="bg-white rounded-2xl shadow-lg p-6 text-center"
                        >
                            <div className="text-3xl font-bold text-purple-600 mb-2">
                                {mockCredits.lifetime_redeemed.toFixed(1)}
                            </div>
                            <div className="text-gray-600">Total Redeemed</div>
                            <div className="text-sm text-gray-500 mt-1">🌍 Impact made</div>
                        </motion.div>
                    </div>

                    {/* Tab Navigation */}
                    <div className="bg-white rounded-2xl shadow-lg mb-8">
                        <div className="flex border-b border-gray-200">
                            {[
                                { key: 'overview', label: 'Overview', icon: '📊' },
                                { key: 'history', label: 'Transaction History', icon: '📋' },
                                { key: 'marketplace', label: 'Marketplace', icon: '🛒' }
                            ].map((tab) => (
                                <button
                                    key={tab.key}
                                    onClick={() => setActiveTab(tab.key as any)}
                                    className={`flex-1 flex items-center justify-center space-x-2 py-4 px-6 transition-colors ${activeTab === tab.key
                                            ? 'border-b-2 border-green-500 text-green-600 bg-green-50'
                                            : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                                        }`}
                                >
                                    <span>{tab.icon}</span>
                                    <span className="font-medium">{tab.label}</span>
                                </button>
                            ))}
                        </div>

                        <div className="p-6">
                            {/* Overview Tab */}
                            {activeTab === 'overview' && (
                                <div className="space-y-6">
                                    <div>
                                        <h3 className="text-xl font-bold text-gray-900 mb-4">How Carbon Credits Work</h3>
                                        <div className="grid md:grid-cols-3 gap-6">
                                            <div className="text-center p-4">
                                                <div className="text-4xl mb-3">📝</div>
                                                <h4 className="font-semibold text-gray-900 mb-2">1. Log Eco Actions</h4>
                                                <p className="text-gray-600 text-sm">Track your sustainable habits and carbon-saving activities</p>
                                            </div>
                                            <div className="text-center p-4">
                                                <div className="text-4xl mb-3">🌱</div>
                                                <h4 className="font-semibold text-gray-900 mb-2">2. Earn Credits</h4>
                                                <p className="text-gray-600 text-sm">Get credits based on your verified CO2 savings</p>
                                            </div>
                                            <div className="text-center p-4">
                                                <div className="text-4xl mb-3">🌍</div>
                                                <h4 className="font-semibold text-gray-900 mb-2">3. Make Impact</h4>
                                                <p className="text-gray-600 text-sm">Redeem credits for real environmental projects</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Earnings</h3>
                                        <div className="space-y-3">
                                            {mockHistory.filter(t => t.type === 'earned').slice(0, 3).map((transaction) => (
                                                <div key={transaction.id} className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                                                    <div className="flex items-center space-x-3">
                                                        <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                                                            <span className="text-white font-bold">+</span>
                                                        </div>
                                                        <div>
                                                            <div className="font-medium text-gray-900">{transaction.reason}</div>
                                                            <div className="text-sm text-gray-600">{new Date(transaction.date).toLocaleDateString()}</div>
                                                        </div>
                                                    </div>
                                                    <div className="text-green-600 font-bold">+{transaction.amount} credits</div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* History Tab */}
                            {activeTab === 'history' && (
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-4">Transaction History</h3>
                                    {historyLoading ? (
                                        <div className="text-center py-8">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                                            <p className="text-gray-600 mt-2">Loading history...</p>
                                        </div>
                                    ) : (
                                        <div className="space-y-3">
                                            {mockHistory.map((transaction) => (
                                                <div key={transaction.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                                    <div className="flex items-center space-x-3">
                                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${transaction.type === 'earned' ? 'bg-green-500' : 'bg-blue-500'
                                                            }`}>
                                                            <span className="text-white font-bold">
                                                                {transaction.type === 'earned' ? '+' : '-'}
                                                            </span>
                                                        </div>
                                                        <div>
                                                            <div className="font-medium text-gray-900">{transaction.reason}</div>
                                                            <div className="text-sm text-gray-600">
                                                                {new Date(transaction.date).toLocaleDateString()} •
                                                                <span className={`ml-1 ${transaction.status === 'completed' ? 'text-green-600' : 'text-orange-600'}`}>
                                                                    {transaction.status}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className={`font-bold ${transaction.amount > 0 ? 'text-green-600' : 'text-blue-600'}`}>
                                                        {transaction.amount > 0 ? '+' : ''}{transaction.amount} credits
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Marketplace Tab */}
                            {activeTab === 'marketplace' && (
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-4">Redeem Your Credits</h3>
                                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {marketplaceItems.map((item) => (
                                            <motion.div
                                                key={item.id}
                                                whileHover={{ scale: 1.02 }}
                                                className="bg-gray-50 rounded-xl p-6 border border-gray-200 hover:border-green-300 transition-all"
                                            >
                                                <div className="text-center mb-4">
                                                    <div className="text-4xl mb-2">{item.image}</div>
                                                    <div className="text-xs text-gray-500 bg-gray-200 rounded-full px-2 py-1 inline-block">
                                                        {item.category}
                                                    </div>
                                                </div>

                                                <h4 className="font-bold text-gray-900 mb-2">{item.title}</h4>
                                                <p className="text-gray-600 text-sm mb-3">{item.description}</p>

                                                <div className="bg-green-100 rounded-lg p-3 mb-4">
                                                    <div className="text-sm font-medium text-green-800">Impact:</div>
                                                    <div className="text-sm text-green-700">{item.impact}</div>
                                                </div>

                                                <div className="flex items-center justify-between">
                                                    <div className="text-lg font-bold text-gray-900">
                                                        {item.cost} credits
                                                    </div>
                                                    <button
                                                        onClick={() => handleRedeem(item)}
                                                        disabled={mockCredits.balance < item.cost}
                                                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${mockCredits.balance >= item.cost
                                                                ? 'bg-green-500 text-white hover:bg-green-600'
                                                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                                            }`}
                                                    >
                                                        {mockCredits.balance >= item.cost ? 'Redeem' : 'Need More'}
                                                    </button>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    )
}