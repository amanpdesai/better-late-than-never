"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Newspaper, ExternalLink, TrendingUp, Building2 } from "lucide-react"
import { cn } from "@/lib/utils"
import type { NewsData } from "@/lib/types"

interface NewsSummaryViewProps {
  data: NewsData
}

export function NewsSummaryView({ data }: NewsSummaryViewProps) {
  const { items, summary } = data

  if (!items || items.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-3">
        <p className="text-gray-400 text-center text-xs">No news items available</p>
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
    .slice(0, 3)

  // Sort items by virality
  const sortedItems = [...items].sort((a, b) => b.virality_score - a.virality_score)

  return (
    <div className="space-y-2">
      {/* Sentiment Overview - Compact */}
      <Card className="bg-white/5 border-white/10 p-3">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-3 h-3 text-blue-400" />
          <h3 className="text-xs font-semibold text-white uppercase">Sentiment</h3>
        </div>

        <div className="grid grid-cols-3 gap-2">
          <div className="text-center p-2 bg-green-500/10 rounded border border-green-500/30">
            <p className="text-lg font-bold text-green-400">{sentimentCounts.positive || 0}</p>
            <p className="text-xs text-green-300">Positive</p>
          </div>
          <div className="text-center p-2 bg-gray-500/10 rounded border border-gray-500/30">
            <p className="text-lg font-bold text-gray-400">{sentimentCounts.neutral || 0}</p>
            <p className="text-xs text-gray-300">Neutral</p>
          </div>
          <div className="text-center p-2 bg-red-500/10 rounded border border-red-500/30">
            <p className="text-lg font-bold text-red-400">{sentimentCounts.negative || 0}</p>
            <p className="text-xs text-red-300">Negative</p>
          </div>
        </div>
      </Card>

      {/* Top Sources - Compact */}
      {topSources.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Building2 className="w-3 h-3 text-purple-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Top Sources</h3>
          </div>
          <div className="flex flex-wrap gap-1">
            {topSources.map(([source, count]) => (
              <Badge
                key={source}
                variant="outline"
                className="text-xs bg-purple-500/10 text-purple-300 border-purple-500/30"
              >
                {source} ({count})
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {/* Top News Articles - Compact */}
      <Card className="bg-white/5 border-white/10 p-3">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-white uppercase">Top Articles</h3>
          <Badge className="bg-blue-600/20 text-blue-300 border-blue-500/30 text-xs">
            {items.length}
          </Badge>
        </div>

        <div className="space-y-1">
          {sortedItems.slice(0, 5).map((item, index) => (
            <div
              key={index}
              className="p-2 bg-white/5 rounded border border-white/10 hover:bg-white/10 transition-colors group"
            >
              {/* Header with badges */}
              <div className="flex items-center gap-1 flex-wrap mb-1">
                {item.source_name && (
                  <Badge variant="outline" className="text-xs bg-white/5 text-gray-300 border-gray-600">
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
              <h4 className="text-white text-xs font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                {item.title}
              </h4>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
