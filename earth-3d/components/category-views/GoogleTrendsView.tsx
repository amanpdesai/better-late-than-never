"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { TrendingUp, Search, ExternalLink, BarChart3, Zap, Filter } from "lucide-react"
import { cn } from "@/lib/utils"
import type { GoogleTrendsData } from "@/lib/types"
import { useState } from "react"

interface GoogleTrendsViewProps {
  data: GoogleTrendsData
}

type FilterType = 'all' | 'high' | 'medium' | 'low'

export function GoogleTrendsView({ data }: GoogleTrendsViewProps) {
  const { trending_searches, breakout_searches, summary } = data
  const [trendingFilter, setTrendingFilter] = useState<FilterType>('all')

  if (!trending_searches || trending_searches.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-5">
        <p className="text-gray-400 text-center">No trending searches available</p>
      </Card>
    )
  }

  // Sort trending searches by traffic volume (extract number from traffic_label)
  const sortedTrending = [...trending_searches].sort((a, b) => {
    const aVolume = parseInt(a.traffic_label.replace(/[^0-9]/g, "")) || 0
    const bVolume = parseInt(b.traffic_label.replace(/[^0-9]/g, "")) || 0
    return bVolume - aVolume
  })

  // Filter trending searches by traffic level
  const getTrafficLevel = (trafficLabel: string) => {
    const volume = parseInt(trafficLabel.replace(/[^0-9]/g, "")) || 0
    if (volume >= 100000) return 'high'
    if (volume >= 10000) return 'medium'
    return 'low'
  }

  const filteredTrending = sortedTrending.filter(search => {
    if (trendingFilter === 'all') return true
    return getTrafficLevel(search.traffic_label) === trendingFilter
  })

  const trafficCounts = {
    all: sortedTrending.length,
    high: sortedTrending.filter(s => getTrafficLevel(s.traffic_label) === 'high').length,
    medium: sortedTrending.filter(s => getTrafficLevel(s.traffic_label) === 'medium').length,
    low: sortedTrending.filter(s => getTrafficLevel(s.traffic_label) === 'low').length,
  }

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <Card className="bg-white/5 border-white/10 p-5">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-semibold text-white uppercase">Trending Overview</h3>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-3 bg-blue-500/10 rounded-lg border border-blue-500/30">
            <p className="text-2xl font-bold text-blue-400">{trending_searches.length}</p>
            <p className="text-xs text-blue-300 mt-1">Trending Searches</p>
          </div>
          <div className="text-center p-3 bg-green-500/10 rounded-lg border border-green-500/30">
            <p className="text-2xl font-bold text-green-400">{breakout_searches?.length || 0}</p>
            <p className="text-xs text-green-300 mt-1">Breakout Searches</p>
          </div>
          <div className="text-center p-3 bg-purple-500/10 rounded-lg border border-purple-500/30">
            <p className="text-2xl font-bold text-purple-400">
              {summary?.top_category || "General"}
            </p>
            <p className="text-xs text-purple-300 mt-1">Top Category</p>
          </div>
        </div>
      </Card>

      {/* Trending Searches */}
      <Card className="bg-white/5 border-white/10 p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-orange-400" />
          <h3 className="text-lg font-semibold text-white uppercase">Trending Searches</h3>
          <Badge className="bg-orange-600/20 text-orange-300 border-orange-500/30 text-xs">
            {filteredTrending.length} searches
          </Badge>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400 mr-2">Filter by traffic:</span>
          <div className="flex gap-2">
            <Button
              variant={trendingFilter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTrendingFilter('all')}
              className={cn(
                "text-xs",
                trendingFilter === 'all' 
                  ? "bg-blue-600 hover:bg-blue-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              All ({trafficCounts.all})
            </Button>
            <Button
              variant={trendingFilter === 'high' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTrendingFilter('high')}
              className={cn(
                "text-xs",
                trendingFilter === 'high' 
                  ? "bg-red-600 hover:bg-red-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              High ({trafficCounts.high})
            </Button>
            <Button
              variant={trendingFilter === 'medium' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTrendingFilter('medium')}
              className={cn(
                "text-xs",
                trendingFilter === 'medium' 
                  ? "bg-yellow-600 hover:bg-yellow-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              Medium ({trafficCounts.medium})
            </Button>
            <Button
              variant={trendingFilter === 'low' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTrendingFilter('low')}
              className={cn(
                "text-xs",
                trendingFilter === 'low' 
                  ? "bg-green-600 hover:bg-green-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              Low ({trafficCounts.low})
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTrending.map((search, index) => (
            <Card
              key={index}
              className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors group cursor-pointer"
              onClick={() => {
                if (search.share_url) {
                  window.open(search.share_url, '_blank', 'noopener,noreferrer')
                }
              }}
            >
              <div className="p-4 space-y-3">
                {/* Header with badges */}
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant="outline" className="text-xs bg-white/5 text-gray-300 border-gray-600">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    #{index + 1}
                  </Badge>

                  <Badge
                    variant="outline"
                    className={cn(
                      "text-xs border-white/20",
                      getTrafficLevel(search.traffic_label) === 'high' && "text-red-400 bg-red-500/10",
                      getTrafficLevel(search.traffic_label) === 'medium' && "text-yellow-400 bg-yellow-500/10",
                      getTrafficLevel(search.traffic_label) === 'low' && "text-green-400 bg-green-500/10"
                    )}
                  >
                    {getTrafficLevel(search.traffic_label).toUpperCase()}
                  </Badge>

                  <span className="text-xs text-gray-500 ml-auto">{search.traffic_label}</span>
                </div>

                {/* Query */}
                <h4 className="text-white text-sm font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                  {search.query}
                </h4>

                {/* Category */}
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs bg-gray-500/10 text-gray-400 border-gray-500/30">
                    {search.category}
                  </Badge>
                </div>

                {/* Click hint */}
                {search.share_url && (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <ExternalLink className="w-3 h-3" />
                    <span className="truncate">Click card to view on Google Trends</span>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </Card>

      {/* Breakout Searches */}
      {breakout_searches && breakout_searches.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-4 h-4 text-yellow-400" />
            <h3 className="text-lg font-semibold text-white uppercase">Breakout Searches</h3>
            <Badge className="bg-yellow-600/20 text-yellow-300 border-yellow-500/30 text-xs">
              {breakout_searches.length} breakouts
            </Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {breakout_searches.map((search, index) => (
              <Card
                key={index}
                className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors group cursor-pointer"
                onClick={() => {
                  if ((search as any).share_url) {
                    window.open((search as any).share_url, '_blank', 'noopener,noreferrer')
                  }
                }}
              >
                <div className="p-4 space-y-3">
                  {/* Header with badges */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className="text-xs bg-white/5 text-gray-300 border-gray-600">
                      <Zap className="w-3 h-3 mr-1" />
                      Breakout
                    </Badge>

                    {search.growth && (
                      <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/30 text-xs">
                        {search.growth}
                      </Badge>
                    )}
                  </div>

                  {/* Query */}
                  <h4 className="text-white text-sm font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                    {search.query}
                  </h4>

                  {/* Click hint */}
                  {(search as any).share_url && (
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <ExternalLink className="w-3 h-3" />
                      <span className="truncate">Click card to view on Google Trends</span>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </Card>
      )}

      {/* Notable Topics */}
      {summary?.notable_topics && summary.notable_topics.length > 0 && (
        <Card className="bg-white/5 border-white/10 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Search className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-semibold text-white uppercase">Notable Topics</h3>
          </div>

          <div className="flex flex-wrap gap-2">
            {summary.notable_topics.map((topic, index) => (
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
