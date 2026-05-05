'use client'

import { useEffect, useMemo, useState } from 'react'
import { ExternalLink, RefreshCw, AlertCircle, Loader2, TrendingUp, TrendingDown } from 'lucide-react'
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
  trending?: {
    top_gainers: Array<{
      symbol: string
      company_name: string
      price: number
      percent_change: number
      net_change: number
      exchange_type: string
      volume: number
    }>
    top_losers: Array<{
      symbol: string
      company_name: string
      price: number
      percent_change: number
      net_change: number
      exchange_type: string
      volume: number
    }>
  }
  indices_cached: boolean
  news_cached: boolean
  trending_cached?: boolean
}

interface MarketWidgetProps {
  data?: MarketData
  loading?: boolean
  error?: string | null
  onRefresh?: () => void
}

type RangeKey = '1D' | '5D' | '1M' | '3M' | 'YTD' | '1Y' | '3Y' | '5Y' | 'Max'
type InsightTab = 'Summary' | 'Sentiment' | 'Related'

export default function MarketWidget({
  data,
  loading = false,
  error = null,
  onRefresh,
}: MarketWidgetProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [activeSymbol, setActiveSymbol] = useState<string | null>(null)
  const [activeRange, setActiveRange] = useState<RangeKey>('1D')
  const [activeInsightTab, setActiveInsightTab] = useState<InsightTab>('Summary')

  const handleRefresh = async () => {
    setIsRefreshing(true)
    if (onRefresh) {
      await onRefresh()
    }
    setTimeout(() => setIsRefreshing(false), 1000)
  }

  const sortedIndices = useMemo(() => {
    if (!data?.indices) return []
    return [...data.indices].sort((a, b) => b.percentage_change - a.percentage_change)
  }, [data?.indices])

  const activeIndex = useMemo(() => {
    if (!sortedIndices.length) return null
    if (!activeSymbol) return sortedIndices[0]
    return sortedIndices.find((item) => item.symbol === activeSymbol) || sortedIndices[0]
  }, [activeSymbol, sortedIndices])

  useEffect(() => {
    if (sortedIndices.length && !activeSymbol) {
      setActiveSymbol(sortedIndices[0].symbol)
    }
  }, [sortedIndices, activeSymbol])

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-emerald-400'
    if (change < 0) return 'text-rose-400'
    return 'text-slate-300'
  }

  const getChangeBadge = (change: number) => {
    if (change > 0) return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
    if (change < 0) return 'bg-rose-500/20 text-rose-300 border-rose-500/40'
    return 'bg-slate-600/40 text-slate-200 border-slate-500/40'
  }

  const rangeLabels: RangeKey[] = ['1D', '5D', '1M', '3M', 'YTD', '1Y', '3Y', '5Y', 'Max']

  const chartSeries = useMemo(() => {
    if (!activeIndex) return []

    const pointCountByRange: Record<RangeKey, number> = {
      '1D': 42,
      '5D': 56,
      '1M': 72,
      '3M': 84,
      'YTD': 96,
      '1Y': 110,
      '3Y': 130,
      '5Y': 150,
      'Max': 168,
    }

    const points = pointCountByRange[activeRange]
    const symbolSeed = activeIndex.symbol
      .split('')
      .reduce((acc, char) => acc + char.charCodeAt(0), 0)
    const drift = (activeIndex.percentage_change / 100) * activeIndex.current_price
    const baseline = activeIndex.current_price - drift

    return Array.from({ length: points }, (_, i) => {
      const progress = i / Math.max(points - 1, 1)
      const waveA = Math.sin((i + symbolSeed) * 0.2) * 0.006
      const waveB = Math.cos((i + symbolSeed * 0.3) * 0.11) * 0.003
      const trend = progress * (drift / activeIndex.current_price)
      const value = baseline * (1 + trend + waveA + waveB)
      return Number(value.toFixed(2))
    })
  }, [activeIndex, activeRange])

  const chartPath = useMemo(() => {
    if (!chartSeries.length) return ''

    const width = 920
    const height = 220
    const min = Math.min(...chartSeries)
    const max = Math.max(...chartSeries)
    const range = Math.max(max - min, 1)

    return chartSeries
      .map((point, index) => {
        const x = (index / Math.max(chartSeries.length - 1, 1)) * width
        const y = height - ((point - min) / range) * height
        return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
      })
      .join(' ')
  }, [chartSeries])

  const hasTrending = Boolean(
    data?.trending && ((data.trending.top_gainers?.length || 0) > 0 || (data.trending.top_losers?.length || 0) > 0)
  )

  const insightText = useMemo(() => {
    if (!activeIndex) return ''

    if (activeInsightTab === 'Summary') {
      return `${activeIndex.symbol} is ${activeIndex.percentage_change >= 0 ? 'holding above' : 'trading below'} the previous close with a ${Math.abs(activeIndex.percentage_change).toFixed(2)}% move. Intraday structure suggests ${activeIndex.percentage_change >= 0 ? 'buyers remain in control' : 'sellers are still dominant'} in this session.`
    }

    if (activeInsightTab === 'Sentiment') {
      return `Sentiment reads ${activeIndex.percentage_change >= 0 ? 'constructive' : 'defensive'}: momentum participants are ${activeIndex.percentage_change >= 0 ? 'adding on dips' : 'trimming exposure'} while long-horizon capital remains selective around macro headlines.`
    }

    return `Related moves: banking and IT baskets are showing the tightest correlation with ${activeIndex.symbol} right now. Watch volatility clusters around policy updates and earnings-linked names.`
  }, [activeIndex, activeInsightTab])

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
      <Card className="p-6 bg-rose-950/40 border-rose-800/50 text-rose-100">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-300 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-rose-100">Unable to load market data</p>
            <p className="text-sm text-rose-200/80 mt-1">{error}</p>
          </div>
          {onRefresh && (
            <Button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="ml-auto text-sm px-3 py-1 border-rose-700/50 text-rose-100 hover:bg-rose-800/40"
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
      <Card className="p-6 bg-slate-950 border-slate-800 text-slate-100">
        <div className="flex items-center justify-center gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-slate-300" />
          <p className="text-slate-300">Loading market data...</p>
        </div>
      </Card>
    )
  }

  if (!data || !data.indices) {
    return null
  }

  return (
    <Card className="p-0 overflow-hidden border-slate-800 bg-gradient-to-b from-slate-950 via-[#142640] to-[#111b31] text-slate-100">
      <div className="border-b border-slate-700/70 bg-slate-900/80 px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold tracking-tight text-slate-50">Global Market</h2>
            <p className="text-xs text-slate-300">Live-style market board with index movement and headlines</p>
          </div>
          {onRefresh && (
            <Button
              onClick={handleRefresh}
              disabled={isRefreshing}
              variant="outline"
              size="sm"
              className="border-slate-600 bg-slate-800/60 text-slate-100 hover:bg-slate-700"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing' : 'Refresh'}
            </Button>
          )}
        </div>
      </div>

      <div className="border-b border-slate-700/60 bg-[#0f223f] px-4 py-2">
        <div className="flex gap-4 overflow-x-auto whitespace-nowrap">
          {sortedIndices.map((index) => (
            <button
              key={index.symbol}
              onClick={() => setActiveSymbol(index.symbol)}
              className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm transition ${
                activeIndex?.symbol === index.symbol
                  ? 'border-cyan-400/70 bg-cyan-500/20 text-cyan-100'
                  : 'border-slate-600/60 bg-slate-800/40 text-slate-200 hover:bg-slate-700/60'
              }`}
            >
              <span className="font-semibold">{index.symbol}</span>
              <span className={getChangeColor(index.percentage_change)}>
                {index.percentage_change > 0 ? '+' : ''}
                {index.percentage_change.toFixed(2)}%
              </span>
            </button>
          ))}
        </div>
      </div>

      {activeIndex && (
        <div className="bg-cyan-700/90 px-4 py-2 text-sm text-cyan-50">
          {activeIndex.percentage_change >= 0 ? 'Price up' : 'Price down'} by {Math.abs(activeIndex.percentage_change).toFixed(2)}% from previous close {activeIndex.previous_close.toLocaleString('en-IN', { maximumFractionDigits: 2 })} as of {new Date(activeIndex.last_updated).toLocaleString('en-IN')}
        </div>
      )}

      <div className="grid gap-4 p-4 lg:grid-cols-[300px_1fr]">
        <div className="rounded-xl border border-slate-700/80 bg-slate-900/60 p-2">
          {hasTrending ? (
            <>
              <div className="mb-2 flex items-center justify-between px-2 py-1">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-300">Trending</p>
                {data.trending_cached && (
                  <span className="rounded-full border border-cyan-400/40 bg-cyan-500/10 px-2 py-0.5 text-[10px] text-cyan-100">Cached</span>
                )}
              </div>

              <div className="space-y-3">
                <div className="rounded-lg border border-emerald-700/40 bg-emerald-900/10 p-2">
                  <p className="mb-2 px-1 text-xs font-semibold uppercase tracking-wide text-emerald-300">Top Gainers</p>
                  <div className="space-y-2">
                    {(data.trending?.top_gainers || []).slice(0, 3).map((stock, index) => (
                      <div key={`${stock.symbol}-${index}`} className="rounded-md border border-emerald-600/20 bg-slate-900/40 p-2">
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-semibold text-slate-100">{stock.symbol}</p>
                            <p className="truncate text-xs text-slate-400">{stock.company_name}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-semibold text-slate-100">
                              {Number(stock.price || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                            </p>
                            <p className="text-xs font-medium text-emerald-300">
                              +{Number(stock.percent_change || 0).toFixed(2)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-lg border border-rose-700/40 bg-rose-900/10 p-2">
                  <p className="mb-2 px-1 text-xs font-semibold uppercase tracking-wide text-rose-300">Top Losers</p>
                  <div className="space-y-2">
                    {(data.trending?.top_losers || []).slice(0, 3).map((stock, index) => (
                      <div key={`${stock.symbol}-${index}`} className="rounded-md border border-rose-600/20 bg-slate-900/40 p-2">
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-semibold text-slate-100">{stock.symbol}</p>
                            <p className="truncate text-xs text-slate-400">{stock.company_name}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-semibold text-slate-100">
                              {Number(stock.price || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                            </p>
                            <p className="text-xs font-medium text-rose-300">
                              {Number(stock.percent_change || 0).toFixed(2)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="mb-2 flex items-center justify-between px-2 py-1">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-300">Indices</p>
                {data.indices_cached && (
                  <span className="rounded-full border border-cyan-400/40 bg-cyan-500/10 px-2 py-0.5 text-[10px] text-cyan-100">Cached</span>
                )}
              </div>
              <div className="space-y-2">
                {sortedIndices.map((index) => (
                  <button
                    key={index.symbol}
                    onClick={() => setActiveSymbol(index.symbol)}
                    className={`w-full rounded-lg border p-3 text-left transition ${
                      activeIndex?.symbol === index.symbol
                        ? 'border-cyan-400/70 bg-cyan-500/10'
                        : 'border-slate-700 bg-slate-800/30 hover:border-slate-500'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-100">{index.symbol}</p>
                        <p className="text-xs text-slate-400">{index.name}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-slate-100">
                          {index.current_price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                        </p>
                        <p className={`text-sm font-medium ${getChangeColor(index.percentage_change)}`}>
                          {index.percentage_change > 0 ? '+' : ''}
                          {index.percentage_change.toFixed(2)}%
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="rounded-xl border border-slate-700/80 bg-slate-900/50 p-4">
          {activeIndex && (
            <>
              <div className="mb-4 flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">{activeIndex.name}</p>
                  <h3 className="mt-1 text-3xl font-semibold text-white">{activeIndex.symbol}</h3>
                  <p className="mt-1 text-xs text-slate-400">As of {new Date(activeIndex.last_updated).toLocaleString('en-IN')}</p>
                </div>
                <div className="text-right">
                  <p className="text-5xl font-bold leading-none text-slate-50">
                    {activeIndex.current_price.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                  </p>
                  <div className={`mt-2 inline-flex items-center gap-1 rounded-full border px-3 py-1 text-sm font-medium ${getChangeBadge(activeIndex.percentage_change)}`}>
                    {activeIndex.percentage_change >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                    <span>
                      {activeIndex.percentage_change > 0 ? '+' : ''}
                      {activeIndex.percentage_change.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="mb-4 flex flex-wrap items-center gap-2">
                <button className="rounded-full border border-slate-600 bg-slate-800/70 px-3 py-1.5 text-sm text-slate-100 transition hover:bg-slate-700">+ Watchlist</button>
                <button className="rounded-full border border-slate-600 bg-slate-800/70 px-3 py-1.5 text-sm text-slate-100 transition hover:bg-slate-700">Share</button>
                <button className="rounded-full border border-slate-600 bg-slate-800/70 px-3 py-1.5 text-sm text-slate-100 transition hover:bg-slate-700">Compare</button>
                <button className="rounded-full border border-slate-600 bg-slate-800/70 px-3 py-1.5 text-sm text-slate-100 transition hover:bg-slate-700">Join discussion</button>
              </div>

              <div className="mb-4 rounded-xl border border-slate-700 bg-slate-900/60 p-3">
                <div className="mb-3 flex flex-wrap gap-2">
                  {rangeLabels.map((range) => (
                    <button
                      key={range}
                      onClick={() => setActiveRange(range)}
                      className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                        activeRange === range
                          ? 'bg-cyan-500 text-white'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      {range}
                    </button>
                  ))}
                </div>

                <div className="relative h-[220px] w-full overflow-hidden rounded-lg border border-slate-700 bg-gradient-to-b from-[#162b4d] to-[#101c33]">
                  <svg viewBox="0 0 920 220" className="h-full w-full">
                    <defs>
                      <linearGradient id="chartAreaGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#22c55e" stopOpacity="0.35" />
                        <stop offset="100%" stopColor="#22c55e" stopOpacity="0" />
                      </linearGradient>
                    </defs>
                    <line x1="0" y1="40" x2="920" y2="40" stroke="#334155" strokeDasharray="4 6" strokeWidth="1" />
                    <line x1="0" y1="110" x2="920" y2="110" stroke="#334155" strokeDasharray="4 6" strokeWidth="1" />
                    <line x1="0" y1="180" x2="920" y2="180" stroke="#334155" strokeDasharray="4 6" strokeWidth="1" />
                    {chartPath && (
                      <>
                        <path d={`${chartPath} L 920 220 L 0 220 Z`} fill="url(#chartAreaGradient)" />
                        <path d={chartPath} fill="none" stroke="#4ade80" strokeWidth="3" strokeLinecap="round" />
                      </>
                    )}
                  </svg>
                </div>
              </div>

              <div className="mb-4 flex items-center gap-2">
                {(['Summary', 'Sentiment', 'Related'] as InsightTab[]).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveInsightTab(tab)}
                    className={`rounded-full border px-4 py-1.5 text-sm transition ${
                      activeInsightTab === tab
                        ? 'border-cyan-400/70 bg-cyan-500/20 text-cyan-100'
                        : 'border-slate-600 bg-slate-800/60 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <div className="mb-4 rounded-lg border border-slate-700 bg-slate-800/50 p-3">
                <p className="text-sm leading-relaxed text-slate-200">{insightText}</p>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
                  <p className="text-xs text-slate-400">Previous Close</p>
                  <p className="mt-1 text-lg font-semibold text-slate-100">
                    {activeIndex.previous_close.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                  </p>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
                  <p className="text-xs text-slate-400">Movement</p>
                  <p className={`mt-1 text-lg font-semibold ${getChangeColor(activeIndex.percentage_change)}`}>
                    {activeIndex.percentage_change > 0 ? '+' : ''}
                    {activeIndex.percentage_change.toFixed(2)}%
                  </p>
                </div>
                <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
                  <p className="text-xs text-slate-400">Updated</p>
                  <p className="mt-1 text-lg font-semibold text-slate-100">{formatTime(activeIndex.last_updated)}</p>
                </div>
              </div>
            </>
          )}

          {data.news && data.news.length > 0 && (
            <div className="mt-5">
              <div className="mb-2 flex items-center justify-between">
                <h4 className="text-sm font-semibold uppercase tracking-wide text-slate-300">Market News</h4>
                {data.news_cached && (
                  <span className="rounded-full border border-cyan-400/40 bg-cyan-500/10 px-2 py-0.5 text-[10px] text-cyan-100">Cached</span>
                )}
              </div>
              <div className="space-y-2">
                {data.news.slice(0, 4).map((article, index) => (
                  <a
                    key={index}
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-start justify-between gap-3 rounded-lg border border-slate-700 bg-slate-800/40 p-3 transition hover:border-cyan-400/50 hover:bg-slate-800"
                  >
                    <div className="min-w-0">
                      <p className="line-clamp-2 text-sm font-medium text-slate-100 group-hover:text-cyan-100">{article.title}</p>
                      <p className="mt-1 text-xs text-slate-400">
                        {article.source} • {formatTime(article.published_date)}
                      </p>
                    </div>
                    <ExternalLink className="h-4 w-4 flex-shrink-0 text-slate-400 group-hover:text-cyan-200" />
                  </a>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </Card>
  )
}
