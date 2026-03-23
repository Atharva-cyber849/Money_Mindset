'use client'

import { useState } from 'react'
import { ExternalLink, RefreshCw, AlertCircle, Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

interface Index {
  symbol: string
  name: string
  current_price: number
  previous_close: number
  percentage_change: number
  last_updated: string
  from_cache?: boolean
}

interface NewsArticle {
  title: string
  source: string
  url: string
  image: string
  published_date: string
  description: string
}

interface MarketData {
  indices: Index[]
  news: NewsArticle[]
  indices_cached: boolean
  news_cached: boolean
}

interface MarketWidgetProps {
  data?: MarketData
  loading?: boolean
  error?: string | null
  onRefresh?: () => void
}

export default function MarketWidget({
  data,
  loading = false,
  error = null,
  onRefresh,
}: MarketWidgetProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async () => {
    setIsRefreshing(true)
    if (onRefresh) {
      await onRefresh()
    }
    setTimeout(() => setIsRefreshing(false), 1000)
  }

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600'
    if (change < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString)
      const now = new Date()
      const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))

      if (diffHours < 1) return 'Just now'
      if (diffHours === 1) return '1 hour ago'
      if (diffHours < 24) return `${diffHours}h ago`

      const diffDays = Math.floor(diffHours / 24)
      if (diffDays === 1) return 'Yesterday'
      if (diffDays < 7) return `${diffDays}d ago`

      return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })
    } catch {
      return ''
    }
  }

  if (error) {
    return (
      <Card className="p-6 bg-red-50 border-red-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-900">Unable to load market data</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
          {onRefresh && (
            <Button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="ml-auto text-sm px-3 py-1"
              variant="outline"
            >
              {isRefreshing ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
              Retry
            </Button>
          )}
        </div>
      </Card>
    )
  }

  if (loading && !data) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
          <p className="text-gray-500">Loading market data...</p>
        </div>
      </Card>
    )
  }

  if (!data || !data.indices) {
    return null
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">📈 Market Overview</h2>
          <p className="text-sm text-gray-600 mt-1">Real-time Indian market indices and financial news</p>
        </div>
        {onRefresh && (
          <Button
            onClick={handleRefresh}
            disabled={isRefreshing}
            variant="outline"
            size="sm"
            className="text-xs"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Refreshing' : 'Refresh'}
          </Button>
        )}
      </div>

      {/* Indices Section */}
      <div>
        <div className="mb-3 flex items-center justify-between px-1">
          <h3 className="font-semibold text-gray-900">India Indices</h3>
          {data.indices_cached && (
            <span className="text-xs px-2 py-1 bg-cyan-100 text-cyan-700 rounded-full">From Cache</span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.indices.map((index) => (
            <div
              key={index.symbol}
              className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all duration-300 hover:-translate-y-1"
            >
              <div className="p-4">
                <p className="text-xs text-gray-600 mb-2 font-medium">{index.name}</p>
                <p className="text-2xl font-bold text-gray-900 mb-1">
                  {index.current_price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </p>
                <p className={`text-sm font-semibold ${getChangeColor(index.percentage_change)}`}>
                  {index.percentage_change > 0 ? '↑ +' : index.percentage_change < 0 ? '↓ ' : '→ '}
                  {Math.abs(index.percentage_change).toFixed(2)}%
                </p>
                <p className="text-xs text-gray-500 mt-2">{formatTime(index.last_updated)}</p>
              </div>
              <div className={`h-1 ${index.percentage_change > 0 ? 'bg-green-400' : index.percentage_change < 0 ? 'bg-red-400' : 'bg-gray-300'}`} />
            </div>
          ))}
        </div>
      </div>

      {/* News Section */}
      {data.news && data.news.length > 0 && (
        <div>
          <div className="mb-3 flex items-center justify-between px-1">
            <h3 className="font-semibold text-gray-900">Financial News</h3>
            {data.news_cached && (
              <span className="text-xs px-2 py-1 bg-cyan-100 text-cyan-700 rounded-full">From Cache</span>
            )}
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {data.news.map((article, index) => (
              <a
                key={index}
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-white rounded-xl shadow-sm border border-gray-100 p-3 hover:shadow-md hover:border-cyan-200 transition-all duration-300 group"
              >
                <div className="flex gap-3">
                  {article.image && (
                    <img
                      src={article.image}
                      alt={article.title}
                      className="w-14 h-14 rounded-lg object-cover flex-shrink-0 bg-gray-100"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-xs text-gray-900 line-clamp-2 group-hover:text-cyan-600">{article.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{article.source}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-gray-500">{formatTime(article.published_date)}</span>
                      <ExternalLink className="w-3.5 h-3.5 text-gray-400 group-hover:text-cyan-600" />
                    </div>
                  </div>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
