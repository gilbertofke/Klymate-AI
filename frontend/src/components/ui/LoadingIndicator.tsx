'use client'

import React from 'react'
import { Loader2, CheckCircle, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LoadingIndicatorProps {
  isLoading?: boolean
  progress?: number
  message?: string
  stage?: string
  size?: 'sm' | 'md' | 'lg'
  variant?: 'spinner' | 'progress' | 'dots' | 'pulse'
  className?: string
}

export function LoadingIndicator({
  isLoading = true,
  progress,
  message,
  stage,
  size = 'md',
  variant = 'spinner',
  className,
}: LoadingIndicatorProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  }

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }

  if (!isLoading) {
    return null
  }

  const renderSpinner = () => (
    <Loader2 className={cn('animate-spin', sizeClasses[size])} />
  )

  const renderProgress = () => (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className={cn('font-medium', textSizeClasses[size])}>
          {stage || 'Loading...'}
        </span>
        {typeof progress === 'number' && (
          <span className={cn('text-gray-500', textSizeClasses[size])}>
            {Math.round(progress)}%
          </span>
        )}
      </div>
      
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div
          className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-300 ease-out"
          style={{
            width: `${typeof progress === 'number' ? Math.max(0, Math.min(100, progress)) : 0}%`
          }}
        />
      </div>
      
      {message && (
        <p className={cn('text-gray-600 dark:text-gray-400 mt-2', textSizeClasses[size])}>
          {message}
        </p>
      )}
    </div>
  )

  const renderDots = () => (
    <div className="flex items-center gap-1">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(
            'rounded-full bg-current animate-pulse',
            size === 'sm' ? 'w-1 h-1' : size === 'md' ? 'w-2 h-2' : 'w-3 h-3'
          )}
          style={{
            animationDelay: `${i * 0.2}s`,
            animationDuration: '1s',
          }}
        />
      ))}
    </div>
  )

  const renderPulse = () => (
    <div className={cn(
      'rounded-full bg-gradient-to-r from-green-500 to-blue-500 animate-pulse',
      sizeClasses[size]
    )} />
  )

  const renderIndicator = () => {
    switch (variant) {
      case 'progress':
        return renderProgress()
      case 'dots':
        return renderDots()
      case 'pulse':
        return renderPulse()
      default:
        return renderSpinner()
    }
  }

  return (
    <div className={cn(
      'flex flex-col items-center justify-center gap-3 text-gray-600 dark:text-gray-400',
      className
    )}>
      {variant !== 'progress' && renderIndicator()}
      {variant === 'progress' && renderIndicator()}
      
      {variant !== 'progress' && (message || stage) && (
        <div className="text-center">
          {stage && (
            <p className={cn('font-medium mb-1', textSizeClasses[size])}>
              {stage}
            </p>
          )}
          {message && (
            <p className={cn('text-gray-500 dark:text-gray-400', textSizeClasses[size])}>
              {message}
            </p>
          )}
          {typeof progress === 'number' && (
            <p className={cn('text-gray-500 dark:text-gray-400 mt-1', textSizeClasses[size])}>
              {Math.round(progress)}%
            </p>
          )}
        </div>
      )}
    </div>
  )
}

interface LoadingOverlayProps {
  isLoading: boolean
  progress?: number
  message?: string
  stage?: string
  className?: string
  children?: React.ReactNode
}

export function LoadingOverlay({
  isLoading,
  progress,
  message,
  stage,
  className,
  children,
}: LoadingOverlayProps) {
  return (
    <div className={cn('relative', className)}>
      {children}
      
      {isLoading && (
        <div className="absolute inset-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm flex items-center justify-center z-10">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 max-w-sm w-full mx-4">
            <LoadingIndicator
              isLoading={true}
              progress={progress}
              message={message}
              stage={stage}
              variant="progress"
              size="md"
            />
          </div>
        </div>
      )}
    </div>
  )
}

interface StageIndicatorProps {
  stages: Array<{
    key: string
    label: string
    completed?: boolean
    current?: boolean
    error?: boolean
  }>
  className?: string
}

export function StageIndicator({ stages, className }: StageIndicatorProps) {
  return (
    <div className={cn('flex items-center justify-between', className)}>
      {stages.map((stage, index) => (
        <React.Fragment key={stage.key}>
          <div className="flex flex-col items-center">
            <div
              className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all',
                stage.completed
                  ? 'bg-green-500 text-white'
                  : stage.current
                  ? 'bg-blue-500 text-white animate-pulse'
                  : stage.error
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
              )}
            >
              {stage.completed ? (
                <CheckCircle className="w-4 h-4" />
              ) : stage.current ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : stage.error ? (
                '!'
              ) : (
                index + 1
              )}
            </div>
            
            <span className={cn(
              'text-xs mt-1 text-center max-w-16',
              stage.current ? 'font-medium text-blue-600' : 'text-gray-500'
            )}>
              {stage.label}
            </span>
          </div>
          
          {index < stages.length - 1 && (
            <div className={cn(
              'flex-1 h-0.5 mx-2',
              stage.completed ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-700'
            )} />
          )}
        </React.Fragment>
      ))}
    </div>
  )
}