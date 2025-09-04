'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { scrollToTopImmediate } from '@/utils/scroll'

interface KlymateLogoButtonProps {
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
  className?: string
  href?: string
  theme?: 'light' | 'dark'
}

export default function KlymateLogoButton({ 
  size = 'md', 
  showText = false, 
  className = '',
  href = '/',
  theme = 'light'
}: KlymateLogoButtonProps) {
  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-16 h-16', 
    lg: 'w-20 h-20'
  }

  const textSizeClasses = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl'
  }

  const handleClick = () => {
    // Scroll to top when navigating to home
    if (href === '/') {
      scrollToTopImmediate()
    }
  }

  const logoContent = (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={`
        ${sizeClasses[size]} bg-gradient-primary rounded-2xl 
        flex items-center justify-center cursor-pointer
        shadow-lg hover:shadow-xl transition-all duration-200
        ${className}
      `}
    >
      <span className={`text-white font-bold ${textSizeClasses[size]}`}>K</span>
    </motion.div>
  )

  if (showText) {
    const textColorClass = theme === 'dark' ? 'text-white' : 'text-text-primary'
    const subtextColorClass = theme === 'dark' ? 'text-gray-400' : 'text-text-secondary'
    const hoverColorClass = theme === 'dark' ? 'group-hover:text-yellow-300' : 'group-hover:text-primary-green'
    
    return (
      <Link href={href} onClick={handleClick} className="flex items-center space-x-3 group">
        {logoContent}
        <div>
          <h1 className={`text-xl font-bold ${textColorClass} ${hoverColorClass} transition-colors`}>
            Klymate AI
          </h1>
          <p className={`text-xs ${subtextColorClass} font-medium`}>
            Your Personal Climate Mate
          </p>
        </div>
      </Link>
    )
  }

  return (
    <Link href={href} onClick={handleClick} className="inline-block">
      {logoContent}
    </Link>
  )
}