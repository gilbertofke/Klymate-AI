'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  ChartBarIcon, 
  SparklesIcon, 
  CurrencyDollarIcon, 
  TrophyIcon,
  ArrowRightIcon,
  PlayIcon,
  StarIcon,
  CheckIcon,
  UserGroupIcon,
  GlobeAltIcon,
  BoltIcon
} from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid'
import KlymateLogoButton from '@/components/ui/KlymateLogoButton'

export default function LandingPage() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)

  const features = [
    {
      name: 'AI Coach',
      description: 'Get personalized recommendations from intelligent AI agents specialized in carbon tracking, energy optimization, and solar prediction.',
      icon: SparklesIcon,
      color: 'text-primary-blue',
      bgColor: 'bg-primary-blue/10'
    },
    {
      name: 'Carbon Tracking',
      description: 'Monitor your carbon footprint across transport, energy, diet, and lifestyle with detailed analytics and insights.',
      icon: ChartBarIcon,
      color: 'text-primary-green',
      bgColor: 'bg-primary-green/10'
    },
    {
      name: 'Gamification',
      description: 'Unlock badges, climb leaderboards, and maintain streaks while making a positive environmental impact.',
      icon: TrophyIcon,
      color: 'text-status-warning',
      bgColor: 'bg-status-warning/10'
    },
    {
      name: 'Carbon Credits',
      description: 'Earn real money through verified carbon savings. Your environmental impact has actual monetary value.',
      icon: CurrencyDollarIcon,
      color: 'text-status-success',
      bgColor: 'bg-status-success/10'
    }
  ]

  const stats = [
    { label: 'CO2 Saved', value: '2.4M tons', change: '+12%' },
    { label: 'Active Users', value: '50K+', change: '+25%' },
    { label: 'Credits Earned', value: '$125K', change: '+18%' },
    { label: 'Countries', value: '45', change: '+8%' }
  ]

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Environmental Consultant',
      avatar: '👩‍💼',
      rating: 5,
      text: 'My Klymate AI mate helped me reduce my carbon footprint by 40% in just 3 months. Having a personal climate companion makes all the difference!'
    },
    {
      name: 'Marcus Rodriguez',
      role: 'Software Engineer',
      avatar: '👨‍💻',
      rating: 5,
      text: 'My climate mate guides me through sustainable choices daily. It\'s like having a personal coach who truly cares about my impact and the planet.'
    },
    {
      name: 'Emma Thompson',
      role: 'Teacher',
      avatar: '👩‍🏫',
      rating: 5,
      text: 'Having a climate mate that understands my family\'s needs has been incredible. We\'re now carbon neutral and contributing to a safer Earth!'
    }
  ]

  return (
    <div className="min-h-screen bg-background-secondary">
      {/* Navigation */}
      <nav className="bg-background-primary border-b border-border-light sticky top-0 z-50 backdrop-blur-sm bg-background-primary/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <motion.div 
              className="flex items-center"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <KlymateLogoButton size="sm" showText={true} href="/" />
            </motion.div>
            <motion.div 
              className="flex items-center space-x-4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Link href="/auth/login" className="btn-ghost text-text-secondary hover:text-text-primary">
                Sign In
              </Link>
              <Link href="/auth/register" className="btn-primary">
                Get Started
              </Link>
            </motion.div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background with animated gradient */}
        <div className="absolute inset-0 bg-gradient-primary opacity-95"></div>
        <div className="absolute inset-0 bg-gradient-to-br from-primary-green/20 via-transparent to-primary-blue/20"></div>
        
        <div className="relative">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-center lg:text-left"
              >
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                  className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-white/90 text-sm font-medium mb-6"
                >
                  <BoltIcon className="w-4 h-4 mr-2" />
                  Your Personal Climate Companion
                </motion.div>
                
                <h1 className="text-4xl lg:text-6xl font-bold text-white mb-6 leading-tight">
                  Your Personal{' '}
                  <span className="text-yellow-300 relative">
                    Climate Mate
                    <motion.div
                      className="absolute -bottom-2 left-0 right-0 h-1 bg-yellow-300/50 rounded-full"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ duration: 0.8, delay: 0.8 }}
                    />
                  </span>
                </h1>
                
                <p className="text-xl text-white/90 mb-8 max-w-2xl">
                  Your AI companion for individual climate awareness and action. Get personalized guidance, track your impact, and contribute to a cleaner, safer, and sustainable Earth together.
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                  >
                    <Link href="/auth/register" className="inline-flex items-center px-8 py-4 bg-white text-primary-green font-semibold rounded-button hover:bg-gray-50 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
                      Meet Your Climate Mate
                      <ArrowRightIcon className="ml-2 w-5 h-5" />
                    </Link>
                  </motion.div>
                  
                  <motion.button
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.5 }}
                    onClick={() => setIsVideoPlaying(true)}
                    className="inline-flex items-center justify-center px-6 py-4 border-2 border-white/30 text-white rounded-button hover:bg-white/10 transition-all duration-200 backdrop-blur-sm"
                  >
                    <PlayIcon className="mr-2 w-5 h-5" />
                    Watch Demo
                  </motion.button>
                </div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, delay: 0.3 }}
                className="relative"
              >
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20 shadow-2xl">
                  <div className="text-center mb-6">
                    <h3 className="text-white font-semibold text-lg mb-2">Platform Impact</h3>
                    <p className="text-white/80 text-sm">Real results from our community</p>
                  </div>
                  <div className="grid grid-cols-2 gap-6">
                    {stats.map((stat, index) => (
                      <motion.div 
                        key={stat.label} 
                        className="text-center"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
                      >
                        <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
                        <div className="text-white/80 text-sm mb-1">{stat.label}</div>
                        <div className="text-green-300 text-xs font-medium">{stat.change}</div>
                      </motion.div>
                    ))}
                  </div>
                </div>
                
                {/* Floating elements for visual appeal */}
                <motion.div
                  className="absolute -top-4 -right-4 w-8 h-8 bg-yellow-300 rounded-full opacity-80"
                  animate={{ y: [-10, 10, -10] }}
                  transition={{ duration: 3, repeat: Infinity }}
                />
                <motion.div
                  className="absolute -bottom-4 -left-4 w-6 h-6 bg-white/30 rounded-full"
                  animate={{ y: [10, -10, 10] }}
                  transition={{ duration: 4, repeat: Infinity }}
                />
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-background-primary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-text-primary mb-4">
              Comprehensive Climate Intelligence
            </h2>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto">
              Our platform combines AI coaching, carbon tracking, gamification, and real rewards to make sustainable living both impactful and profitable.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="group"
              >
                <div className="card card-hover text-center h-full p-8 group-hover:shadow-gradient transition-all duration-300">
                  <div className={`w-16 h-16 ${feature.bgColor} rounded-xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className={`w-8 h-8 ${feature.color}`} />
                  </div>
                  <h3 className="text-xl font-semibold text-text-primary mb-3">
                    {feature.name}
                  </h3>
                  <p className="text-text-secondary leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-background-secondary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-text-primary mb-4">
              How Klymate AI Works
            </h2>
            <p className="text-xl text-text-secondary">
              Four simple steps to start earning money while saving the planet
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                step: '01',
                title: 'Complete Survey',
                description: 'Tell us about your lifestyle to calculate your carbon baseline and get personalized insights'
              },
              {
                step: '02',
                title: 'Track Habits',
                description: 'Log your eco-friendly activities and sustainable choices with our intuitive interface'
              },
              {
                step: '03',
                title: 'Get AI Coaching',
                description: 'Receive personalized recommendations from specialized AI agents to maximize your impact'
              },
              {
                step: '04',
                title: 'Earn Credits',
                description: 'Convert your verified carbon savings into real money through our credit system'
              }
            ].map((item, index) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center group"
              >
                <div className="w-20 h-20 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-6 shadow-gradient group-hover:scale-110 transition-transform duration-300">
                  <span className="text-white font-bold text-xl">{item.step}</span>
                </div>
                <h3 className="text-xl font-semibold text-text-primary mb-3">
                  {item.title}
                </h3>
                <p className="text-text-secondary leading-relaxed">
                  {item.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-24 bg-background-primary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl lg:text-4xl font-bold text-text-primary mb-4">
              Trusted by Climate Champions
            </h2>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto">
              Join thousands of users who are already making a difference and earning money through sustainable choices
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="group"
              >
                <div className="card card-hover h-full p-8 group-hover:shadow-gradient transition-all duration-300">
                  <div className="flex items-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <StarIconSolid key={i} className="w-5 h-5 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-text-secondary mb-6 leading-relaxed italic">
                    "{testimonial.text}"
                  </p>
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center text-white text-xl mr-4">
                      {testimonial.avatar}
                    </div>
                    <div>
                      <h4 className="font-semibold text-text-primary">{testimonial.name}</h4>
                      <p className="text-text-secondary text-sm">{testimonial.role}</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Social Proof Stats */}
          <motion.div 
            className="mt-16 text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            viewport={{ once: true }}
          >
            <div className="flex flex-wrap justify-center items-center gap-8 text-text-secondary">
              <div className="flex items-center">
                <UserGroupIcon className="w-5 h-5 mr-2" />
                <span className="font-medium">50,000+ Active Users</span>
              </div>
              <div className="flex items-center">
                <GlobeAltIcon className="w-5 h-5 mr-2" />
                <span className="font-medium">45 Countries</span>
              </div>
              <div className="flex items-center">
                <StarIconSolid className="w-5 h-5 mr-2 text-yellow-400" />
                <span className="font-medium">4.9/5 Rating</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-primary relative overflow-hidden">
        {/* Background decorative elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-20 h-20 bg-white rounded-full"></div>
          <div className="absolute top-32 right-20 w-16 h-16 bg-white rounded-full"></div>
          <div className="absolute bottom-20 left-1/4 w-12 h-12 bg-white rounded-full"></div>
          <div className="absolute bottom-32 right-10 w-24 h-24 bg-white rounded-full"></div>
        </div>
        
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8 relative">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl lg:text-5xl font-bold text-white mb-6">
              Ready to Meet Your{' '}
              <span className="text-yellow-300">Climate Mate?</span>
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Join thousands who have found their personal companion for climate awareness and sustainable living. Start your journey to a cleaner, safer Earth today.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                viewport={{ once: true }}
              >
                <Link href="/auth/register" className="inline-flex items-center px-8 py-4 bg-white text-primary-green font-semibold rounded-button hover:bg-gray-50 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 text-lg">
                  Meet Your Climate Mate
                  <ArrowRightIcon className="ml-2 w-5 h-5" />
                </Link>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                viewport={{ once: true }}
                className="text-white/80 text-sm"
              >
                <CheckIcon className="w-4 h-4 inline mr-1" />
                Free to start • No credit card required
              </motion.div>
            </div>

            {/* Quick benefits */}
            <motion.div 
              className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
            >
              {[
                { icon: SparklesIcon, text: 'AI-Powered Insights' },
                { icon: CurrencyDollarIcon, text: 'Real Money Rewards' },
                { icon: TrophyIcon, text: 'Gamified Experience' }
              ].map((benefit, index) => (
                <div key={benefit.text} className="flex items-center justify-center text-white/90">
                  <benefit.icon className="w-5 h-5 mr-2" />
                  <span className="font-medium">{benefit.text}</span>
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-text-primary text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-2">
              <div className="mb-6">
                <KlymateLogoButton size="sm" showText={true} href="/" theme="dark" />
              </div>
              <p className="text-gray-400 max-w-md leading-relaxed mb-6">
                Your personal AI companion for climate awareness and sustainable living. Together, we're building a cleaner, safer, and more sustainable Earth for everyone.
              </p>
              <div className="flex items-center space-x-4">
                <Link href="/auth/register" className="btn-primary bg-gradient-primary text-white px-6 py-2 text-sm">
                  Get Started
                </Link>
                <Link href="/auth/login" className="text-gray-400 hover:text-white transition-colors text-sm">
                  Sign In
                </Link>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4 text-white">Platform</h3>
              <ul className="space-y-3 text-gray-400">
                <li><Link href="#features" className="hover:text-white transition-colors">AI Coach</Link></li>
                <li><Link href="#features" className="hover:text-white transition-colors">Carbon Tracking</Link></li>
                <li><Link href="#features" className="hover:text-white transition-colors">Gamification</Link></li>
                <li><Link href="#features" className="hover:text-white transition-colors">Carbon Credits</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4 text-white">Support</h3>
              <ul className="space-y-3 text-gray-400">
                <li><Link href="#" className="hover:text-white transition-colors">Help Center</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Contact Us</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm">
                &copy; 2025 Klymate AI. Built with 💚 love for sustainable climate. All rights reserved.
              </p>
              <div className="flex items-center space-x-6 mt-4 md:mt-0">
                <div className="flex items-center text-gray-400 text-sm">
                  <CheckIcon className="w-4 h-4 mr-1 text-green-400" />
                  Carbon Neutral Platform
                </div>
                <div className="flex items-center text-gray-400 text-sm">
                  <CheckIcon className="w-4 h-4 mr-1 text-green-400" />
                  Verified Credits
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}