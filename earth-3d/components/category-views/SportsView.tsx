"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Trophy, TrendingUp, ExternalLink, MessageSquare } from "lucide-react"
import { cn } from "@/lib/utils"
import type { SportsData } from "@/lib/types"

interface SportsViewProps {
  data: SportsData
}

export function SportsView({ data }: SportsViewProps) {
  const { items } = data

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

  // Group items by sport
  const itemsBySport = items.reduce((acc, item) => {
    const sport = item.sport || "Other"
    if (!acc[sport]) acc[sport] = []
    acc[sport].push(item)
    return acc
  }, {} as Record<string, typeof items>)

  // Sort items within each sport by virality
  Object.keys(itemsBySport).forEach(sport => {
    itemsBySport[sport].sort((a, b) => b.virality_score - a.virality_score)
  })

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

      {/* Sports Feed by Category */}
      {Object.entries(itemsBySport).map(([sport, sportItems]) => (
        <div key={sport} className="space-y-3">
          <div className="flex items-center gap-2">
            <Trophy className={cn("w-4 h-4", `text-${getSportColor(sport)}-400`)} />
            <h3 className="text-sm font-semibold text-white uppercase">{sport}</h3>
            <Badge className={cn(
              "text-xs border",
              `bg-${getSportColor(sport)}-600/20 text-${getSportColor(sport)}-300 border-${getSportColor(sport)}-500/30`
            )}>
              {sportItems.length} items
            </Badge>
          </div>

          {sportItems.slice(0, 5).map((item, index) => (
            <Card
              key={`${sport}-${index}`}
              className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors group"
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

                {/* Link */}
                {item.source_url && (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-gray-500 hover:text-blue-400 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span className="truncate">View source</span>
                  </a>
                )}
              </div>
            </Card>
          ))}
        </div>
      ))}
    </div>
  )
}
