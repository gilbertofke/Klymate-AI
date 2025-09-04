'use client'

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { scrollToTopImmediate } from '@/utils/scroll'

interface ScrollToTopLayoutProps {
  children: React.ReactNode
}

export default function ScrollToTopLayout({ children }: ScrollToTopLayoutProps) {
  const pathname = usePathname()

  useEffect(() => {
    // Scroll to top whenever the route changes
    scrollToTopImmediate()
  }, [pathname])

  useEffect(() => {
    // Also scroll to top on initial page load
    scrollToTopImmediate()
  }, [])

  return <>{children}</>
}