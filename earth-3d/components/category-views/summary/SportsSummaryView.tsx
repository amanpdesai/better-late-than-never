"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Trophy, TrendingUp, ExternalLink, MessageSquare } from "lucide-react"
import { cn } from "@/lib/utils"
import type { SportsData } from "@/lib/types"

interface SportsSummaryViewProps {
  data: SportsData
}

export function SportsSummaryView({ data }: SportsSummaryViewProps) {
  const { items } = data

  if (!items || items.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-3">
        <p className="text-gray-400 text-center text-xs">No sports news available</p>
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
    .slice(0, 3)

  // Sort items by virality
  const sortedItems = [...items].sort((a, b) => b.virality_score - a.virality_score)

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
    <div className="space-y-2">
      {/* Sport Breakdown - Compact */}
      <Card className="bg-white/5 border-white/10 p-3">
        <div className="flex items-center gap-2 mb-2">
          <Trophy className="w-3 h-3 text-yellow-400" />
          <h3 className="text-xs font-semibold text-white uppercase">Top Sports</h3>
        </div>

        <div className="flex flex-wrap gap-1">
          {sportBreakdown.map(([sport, count]) => {
            const color = getSportColor(sport)
            return (
              <Badge
                key={sport}
                variant="outline"
                className={cn(
                  "text-xs border",
                  `bg-${color}-500/10 text-${color}-400 border-${color}-500/30`
                )}
              >
                {sport} ({count})
              </Badge>
            )
          })}
        </div>
      </Card>

      {/* Top Sports Stories - Compact */}
      <Card className="bg-white/5 border-white/10 p-3">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-white uppercase">Top Stories</h3>
          <Badge className="bg-green-600/20 text-green-300 border-green-500/30 text-xs">
            {items.length}
          </Badge>
        </div>

        <div className="space-y-1">
          {sortedItems.slice(0, 5).map((item, index) => (
            <div
              key={`${item.sport}-${index}`}
              className="p-2 bg-white/5 rounded border border-white/10 hover:bg-white/10 transition-colors group"
            >
              {/* Header with badges */}
              <div className="flex items-center gap-1 flex-wrap mb-1">
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

                {item.sport && (
                  <Badge variant="outline" className="text-xs bg-blue-500/10 text-blue-400 border-blue-500/30">
                    {item.sport}
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

              {/* Engagement - Compact */}
              {(item.engagement?.likes || item.engagement?.comments) && (
                <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                  {(item.engagement?.likes || 0) > 0 && (
                    <span className="flex items-center gap-1">
                      <TrendingUp className="w-2 h-2" />
                      <span className="text-gray-400">{(item.engagement?.likes || 0).toLocaleString()}</span>
                    </span>
                  )}
                  {(item.engagement?.comments || 0) > 0 && (
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-2 h-2" />
                      <span className="text-gray-400">{(item.engagement?.comments || 0).toLocaleString()}</span>
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
