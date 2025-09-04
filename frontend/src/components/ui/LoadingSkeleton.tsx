'use client'

export default function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Hero Section Skeleton */}
      <div className="bg-gray-200 rounded-2xl h-64" />
      
      {/* Metrics Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg p-6 border border-border-light">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-gray-200 rounded-lg" />
              <div className="w-8 h-4 bg-gray-200 rounded" />
            </div>
            <div className="space-y-2">
              <div className="w-16 h-8 bg-gray-200 rounded" />
              <div className="w-24 h-4 bg-gray-200 rounded" />
            </div>
          </div>
        ))}
      </div>
      
      {/* Main Content Grid Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 bg-white rounded-lg p-6 border border-border-light">
          <div className="flex items-center justify-between mb-6">
            <div className="w-32 h-6 bg-gray-200 rounded" />
            <div className="w-24 h-8 bg-gray-200 rounded" />
          </div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-center space-x-4 p-4 border border-border-light rounded-lg">
                <div className="w-12 h-12 bg-gray-200 rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="w-32 h-4 bg-gray-200 rounded" />
                  <div className="w-48 h-3 bg-gray-200 rounded" />
                </div>
                <div className="w-6 h-6 bg-gray-200 rounded" />
              </div>
            ))}
          </div>
        </div>
        
        {/* Right Column */}
        <div className="bg-white rounded-lg p-6 border border-border-light">
          <div className="flex items-center justify-between mb-6">
            <div className="w-28 h-6 bg-gray-200 rounded" />
            <div className="w-16 h-4 bg-gray-200 rounded" />
          </div>
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gray-200 rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="w-24 h-4 bg-gray-200 rounded" />
                    <div className="w-16 h-3 bg-gray-200 rounded" />
                  </div>
                  <div className="w-40 h-3 bg-gray-200 rounded" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}