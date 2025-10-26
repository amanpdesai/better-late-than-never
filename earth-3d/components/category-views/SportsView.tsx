"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Trophy, TrendingUp, ExternalLink, MessageSquare, Filter } from "lucide-react"
import { cn } from "@/lib/utils"
import type { SportsData } from "@/lib/types"
import { useState } from "react"

interface SportsViewProps {
  data: SportsData
}

type FilterType = 'all' | 'positive' | 'negative' | 'neutral'

export function SportsView({ data }: SportsViewProps) {
  const { items } = data
  const [filter, setFilter] = useState<FilterType>('all')

  if (!items || items.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-5">
        <p className="text-gray-400 text-center">No sports news available</p>
      </Card>
    )
  }

  // Calculate sport breakdown
  const sportCounts = items.reduce((acc, item) => {
    const sport = item.sport || "Other"
    acc[sport] = (acc[sport] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const sportBreakdown = Object.entries(sportCounts)
    .sort((a, b) => b[1] - a[1])

  // Calculate sentiment counts
  const sentimentCounts = items.reduce((acc, item) => {
    const sentiment = item.sentiment || 'neutral'
    acc[sentiment] = (acc[sentiment] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  // Sort items by virality and apply filter
  const sortedItems = [...items]
    .filter(item => {
      if (filter === 'positive') return item.sentiment === 'positive'
      if (filter === 'negative') return item.sentiment === 'negative'
      if (filter === 'neutral') return item.sentiment === 'neutral'
      return true // 'all'
    })
    .sort((a, b) => b.virality_score - a.virality_score)

  // Sport color mapping
  const getSportColor = (sport: string) => {
    const colors: Record<string, string> = {
      NFL: "blue",
      NBA: "orange",
      MLB: "red",
      NHL: "cyan",
      Soccer: "green",
      MLS: "green",
      Tennis: "yellow",
      Golf: "emerald",
      Boxing: "purple",
      MMA: "rose",
      Other: "gray"
    }
    return colors[sport] || "gray"
  }

  return (
    <div className="space-y-4">
      {/* Sport Breakdown */}
      <Card className="bg-white/5 border-white/10 p-5">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="w-4 h-4 text-yellow-400" />
          <h3 className="text-sm font-semibold text-white uppercase">Sport Breakdown</h3>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {sportBreakdown.map(([sport, count]) => {
            const color = getSportColor(sport)
            return (
              <div
                key={sport}
                className={cn(
                  "text-center p-3 rounded-lg border",
                  `bg-${color}-500/10 border-${color}-500/30`
                )}
              >
                <p className={cn("text-2xl font-bold", `text-${color}-400`)}>{count}</p>
                <p className={cn("text-xs mt-1", `text-${color}-300`)}>{sport}</p>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Sports Feed */}
      <Card className="bg-white/5 border-white/10 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="w-4 h-4 text-yellow-400" />
          <h3 className="text-lg font-semibold text-white uppercase">Sports News</h3>
          <Badge className="bg-yellow-600/20 text-yellow-300 border-yellow-500/30 text-xs">
            {sortedItems.length} articles
          </Badge>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-2 mb-4">
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
                  <Badge
                    variant="outline"
                    className={cn(
                      "text-xs border-white/20",
                      item.source_platform === "espn" && "bg-green-500/10 text-green-400 border-green-500/30",
                      item.source_platform === "youtube" && "bg-red-500/10 text-red-400 border-red-500/30",
                      item.source_platform === "reddit" && "bg-orange-500/10 text-orange-400 border-orange-500/30",
                      !["espn", "youtube", "reddit"].includes(item.source_platform || "") && "text-gray-300"
                    )}
                  >
                    {item.source_platform === "espn" ? "ESPN" :
                     item.source_platform === "youtube" ? "YouTube" :
                     item.source_platform === "reddit" ? "Reddit" :
                     item.source_name || "Article"}
                  </Badge>

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

                {/* Sport */}
                {item.sport && (
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={cn(
                      "text-xs",
                      `bg-${getSportColor(item.sport)}-500/10 text-${getSportColor(item.sport)}-400 border-${getSportColor(item.sport)}-500/30`
                    )}>
                      {item.sport}
                    </Badge>
                  </div>
                )}

                {/* Engagement */}
                {(item.engagement?.likes || item.engagement?.comments) && (
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    {(item.engagement?.likes || 0) > 0 && (
                      <span className="flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        <span className="text-gray-400">{(item.engagement?.likes || 0).toLocaleString()}</span> likes
                      </span>
                    )}
                    {(item.engagement?.comments || 0) > 0 && (
                      <span className="flex items-center gap-1">
                        <MessageSquare className="w-3 h-3" />
                        <span className="text-gray-400">{(item.engagement?.comments || 0).toLocaleString()}</span> comments
                      </span>
                    )}
                  </div>
                )}

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
      </Card>
    </div>
  )
}
