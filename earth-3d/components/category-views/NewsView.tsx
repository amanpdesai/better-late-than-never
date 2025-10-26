"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Newspaper, ExternalLink, TrendingUp, Building2, Filter, Clock, Eye } from "lucide-react"
import { cn } from "@/lib/utils"
import type { NewsData } from "@/lib/types"
import { useState } from "react"

interface NewsViewProps {
  data: NewsData
}

type FilterType = 'all' | 'positive' | 'negative' | 'neutral'

export function NewsView({ data }: NewsViewProps) {
  const { items } = data
  const [filter, setFilter] = useState<FilterType>('all')

  if (!items || items.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-5">
        <p className="text-gray-400 text-center">No news items available</p>
      </Card>
    )
  }

  // Calculate sentiment breakdown
  const sentimentCounts = items.reduce((acc, item) => {
    acc[item.sentiment] = (acc[item.sentiment] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  // Get top sources
  const sourceCounts = items.reduce((acc, item) => {
    const source = item.source_name || "Unknown"
    acc[source] = (acc[source] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const topSources = Object.entries(sourceCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)

  // Sort items by virality and apply filter
  const sortedItems = [...items]
    .filter(item => {
      if (filter === 'positive') return item.sentiment === 'positive'
      if (filter === 'negative') return item.sentiment === 'negative'
      if (filter === 'neutral') return item.sentiment === 'neutral'
      return true // 'all'
    })
    .sort((a, b) => b.virality_score - a.virality_score)

  return (
    <div className="space-y-4">
      {/* News Stats */}
      <Card className="bg-white/5 border-white/10 p-5">
        <div className="flex items-center gap-2 mb-4">
          <Newspaper className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-semibold text-white uppercase">News Overview</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Total Articles */}
          <div className="text-center p-3 bg-white/5 rounded-lg">
            <p className="text-2xl font-bold text-blue-400">{items.length}</p>
            <p className="text-xs text-gray-400 mt-1">Total Articles</p>
          </div>

          {/* Sentiment Breakdown */}
          <div className="text-center p-3 bg-white/5 rounded-lg">
            <div className="flex justify-center gap-2 mb-2">
              <span className="text-xs text-green-400">+{sentimentCounts.positive || 0}</span>
              <span className="text-xs text-gray-400">~{sentimentCounts.neutral || 0}</span>
              <span className="text-xs text-red-400">-{sentimentCounts.negative || 0}</span>
            </div>
            <p className="text-xs text-gray-400">Sentiment</p>
          </div>

          {/* Top Sources */}
          <div className="text-center p-3 bg-white/5 rounded-lg">
            <p className="text-2xl font-bold text-purple-400">{topSources.length}</p>
            <p className="text-xs text-gray-400 mt-1">Sources</p>
          </div>
        </div>

        {/* Top Sources */}
        <div className="mt-4">
          <h4 className="text-xs text-gray-400 mb-2">Top Sources</h4>
          <div className="flex flex-wrap gap-1">
            {topSources.map(([source, count], index) => (
              <Badge
                key={index}
                variant="outline"
                className="text-xs bg-white/5 text-gray-300 border-gray-600"
              >
                {source} ({count})
              </Badge>
            ))}
          </div>
        </div>
      </Card>

      {/* News Feed */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white uppercase">Latest News</h3>
          <Badge className="bg-blue-600/20 text-blue-300 border-blue-500/30 text-xs">
            {sortedItems.length} articles
          </Badge>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400 mr-2">Filter by sentiment:</span>
          <div className="flex gap-2">
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('all')}
              className={cn(
                "text-xs",
                filter === 'all' 
                  ? "bg-blue-600 hover:bg-blue-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              All ({items.length})
            </Button>
            <Button
              variant={filter === 'positive' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('positive')}
              className={cn(
                "text-xs",
                filter === 'positive' 
                  ? "bg-green-600 hover:bg-green-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              Positive ({sentimentCounts.positive || 0})
            </Button>
            <Button
              variant={filter === 'negative' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('negative')}
              className={cn(
                "text-xs",
                filter === 'negative' 
                  ? "bg-red-600 hover:bg-red-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              Negative ({sentimentCounts.negative || 0})
            </Button>
            <Button
              variant={filter === 'neutral' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('neutral')}
              className={cn(
                "text-xs",
                filter === 'neutral' 
                  ? "bg-gray-600 hover:bg-gray-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              Neutral ({sentimentCounts.neutral || 0})
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedItems.map((item, index) => (
            <Card
              key={index}
              className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors group cursor-pointer"
              onClick={() => {
                if (item.source_url) {
                  window.open(item.source_url, '_blank', 'noopener,noreferrer')
                }
              }}
            >
              <div className="p-4 space-y-3">
                {/* Header with badges */}
                <div className="flex items-center gap-2 flex-wrap">
                  {item.source_name && (
                    <Badge variant="outline" className="text-xs bg-white/5 text-gray-300 border-gray-600">
                      <Newspaper className="w-3 h-3 mr-1" />
                      {item.source_name}
                    </Badge>
                  )}

                  <Badge
                    variant="outline"
                    className={cn(
                      "text-xs border-white/20",
                      item.sentiment === "positive" && "text-green-400 bg-green-500/10",
                      item.sentiment === "negative" && "text-red-400 bg-red-500/10",
                      item.sentiment === "neutral" && "text-gray-400 bg-gray-500/10"
                    )}
                  >
                    {item.sentiment}
                  </Badge>

                  <span className="text-xs text-gray-500 ml-auto">★ {item.virality_score}</span>
                </div>

                {/* Title */}
                <h4 className="text-white text-sm font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                  {item.title}
                </h4>

                {/* Description */}
                {item.excerpt && (
                  <p className="text-gray-400 text-xs leading-relaxed line-clamp-3">
                    {item.excerpt}
                  </p>
                )}

                {/* Metadata */}
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  {item.created_at && (
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span className="text-gray-400">
                        {new Date(item.created_at).toLocaleDateString()}
                      </span>
                    </span>
                  )}
                  {item.engagement?.views && (
                    <span className="flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      <span className="text-gray-400">
                        {item.engagement.views > 1000 
                          ? `${(item.engagement.views / 1000).toFixed(1)}k` 
                          : item.engagement.views
                        }
                      </span>
                    </span>
                  )}
                </div>

                {/* Click hint */}
                {item.source_url && (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <ExternalLink className="w-3 h-3" />
                    <span className="truncate">Click card to read article</span>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}