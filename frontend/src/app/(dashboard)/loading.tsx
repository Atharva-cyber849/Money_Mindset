export default function DashboardLoading() {
  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-pulse">
      {/* Banner Skeleton */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 h-48"></div>
      
      {/* Stats Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl p-6 h-32"></div>
        ))}
      </div>
      
      {/* Progress Card Skeleton */}
      <div className="bg-white rounded-xl p-6 h-32"></div>
      
      {/* Filter Buttons Skeleton */}
      <div className="flex gap-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg h-10 w-24"></div>
        ))}
      </div>
      
      {/* Simulations Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl p-6 h-64"></div>
        ))}
      </div>
    </div>
  )
}
