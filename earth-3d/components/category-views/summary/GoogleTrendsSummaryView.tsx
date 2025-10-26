"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, Search, ExternalLink, BarChart3, Zap } from "lucide-react"
import { cn } from "@/lib/utils"
import type { GoogleTrendsData } from "@/lib/types"

interface GoogleTrendsSummaryViewProps {
  data: GoogleTrendsData
}

export function GoogleTrendsSummaryView({ data }: GoogleTrendsSummaryViewProps) {
  const { trending_searches, breakout_searches, summary } = data

  if (!trending_searches || trending_searches.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-3">
        <p className="text-gray-400 text-center text-xs">No trending searches available</p>
      </Card>
    )
  }

  // Sort trending searches by traffic volume (extract number from traffic_label)
  const sortedTrending = [...trending_searches].sort((a, b) => {
    const aVolume = parseInt(a.traffic_label.replace(/[^0-9]/g, "")) || 0
    const bVolume = parseInt(b.traffic_label.replace(/[^0-9]/g, "")) || 0
    return bVolume - aVolume
  })

  return (
    <div className="space-y-2">
      {/* Summary Stats - Compact */}
      <Card className="bg-white/5 border-white/10 p-3">
        <div className="flex items-center gap-2 mb-2">
          <BarChart3 className="w-3 h-3 text-blue-400" />
          <h3 className="text-xs font-semibold text-white uppercase">Overview</h3>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="text-center p-2 bg-blue-500/10 rounded border border-blue-500/30">
            <p className="text-lg font-bold text-blue-400">{trending_searches.length}</p>
            <p className="text-xs text-blue-300">Trending</p>
          </div>
          <div className="text-center p-2 bg-green-500/10 rounded border border-green-500/30">
            <p className="text-lg font-bold text-green-400">{breakout_searches?.length || 0}</p>
            <p className="text-xs text-green-300">Breakout</p>
          </div>
        </div>
      </Card>

      {/* Top Trending Searches - Compact */}
      <Card className="bg-white/5 border-white/10 p-3">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp className="w-3 h-3 text-orange-400" />
          <h3 className="text-xs font-semibold text-white uppercase">Top Trends</h3>
        </div>

        <div className="space-y-1">
          {sortedTrending.slice(0, 5).map((search, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 bg-white/5 rounded border border-white/10 hover:bg-white/10 transition-colors group"
            >
              <div className="flex items-center gap-2">
                <div className="flex items-center justify-center w-5 h-5 rounded-full bg-orange-500/20 text-orange-400 font-bold text-xs">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium text-xs group-hover:text-blue-400 transition-colors line-clamp-1">
                    {search.query}
                  </p>
                  <div className="flex items-center gap-1 mt-0.5">
                    <Badge variant="outline" className="text-xs bg-gray-500/10 text-gray-400 border-gray-500/30">
                      {search.category}
                    </Badge>
                    <span className="text-xs text-gray-500">{search.traffic_label}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Breakout Searches - Compact */}
      {breakout_searches && breakout_searches.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-3 h-3 text-yellow-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Breakout</h3>
          </div>

          <div className="space-y-1">
            {breakout_searches.slice(0, 3).map((search, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-white/5 rounded border border-white/10 hover:bg-white/10 transition-colors group"
              >
                <div className="flex items-center gap-2">
                  <Zap className="w-3 h-3 text-yellow-400" />
                  <p className="text-white font-medium text-xs group-hover:text-blue-400 transition-colors line-clamp-1">
                    {search.query}
                  </p>
                </div>
                {search.growth && (
                  <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30 text-xs">
                    {search.growth}
                  </Badge>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Notable Topics - Compact */}
      {summary?.notable_topics && summary.notable_topics.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-3">
          <div className="flex items-center gap-2 mb-2">
            <Search className="w-3 h-3 text-purple-400" />
            <h3 className="text-xs font-semibold text-white uppercase">Notable Topics</h3>
          </div>

          <div className="flex flex-wrap gap-1">
            {summary.notable_topics.slice(0, 6).map((topic, index) => (
              <Badge
                key={index}
                variant="outline"
                className="text-xs bg-purple-500/10 text-purple-300 border-purple-500/30"
              >
                {topic}
              </Badge>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
