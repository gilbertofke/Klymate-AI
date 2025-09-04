/**
 * Scroll utilities for ensuring proper page navigation behavior
 */

/**
 * Scroll to top of page smoothly
 */
export const scrollToTop = (behavior: 'smooth' | 'instant' = 'instant') => {
  if (typeof window !== 'undefined') {
    window.scrollTo({
      top: 0,
      left: 0,
      behavior
    })
  }
}

/**
 * Scroll to top immediately (for page loads)
 */
export const scrollToTopImmediate = () => {
  if (typeof window !== 'undefined') {
    // Use both methods to ensure it works across browsers
    window.scrollTo(0, 0)
    document.documentElement.scrollTop = 0
    document.body.scrollTop = 0
  }
}

/**
 * Hook to scroll to top on route changes
 */
export const useScrollToTop = () => {
  const scrollToTopOnNavigate = () => {
    scrollToTopImmediate()
  }

  return scrollToTopOnNavigate
}