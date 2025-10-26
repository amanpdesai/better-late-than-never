"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Video, MessageSquare, TrendingUp, ExternalLink, Play, Image, Heart, Filter } from "lucide-react"
import { cn } from "@/lib/utils"
import type { MemesData } from "@/lib/types"
import { useState } from "react"

interface MemesViewProps {
  data: MemesData
}

type FilterType = 'all' | 'reddit' | 'youtube'

export function MemesView({ data }: MemesViewProps) {
  const { items, summary } = data
  const [filter, setFilter] = useState<FilterType>('all')

  if (!items || items.length === 0) {
    return (
      <Card className="bg-white/5 border-white/10 p-5">
        <p className="text-gray-400 text-center">No memes available</p>
      </Card>
    )
  }

  // Calculate platform breakdown from items
  const redditItems = items.filter(item => item.source_platform === 'reddit')
  const youtubeItems = items.filter(item => item.source_platform === 'youtube')
  const totalPosts = items.length
  const redditCount = redditItems.length
  const youtubeCount = youtubeItems.length

  // Calculate sentiment breakdown
  const sentimentCounts = items.reduce((acc, item) => {
    acc[item.sentiment] = (acc[item.sentiment] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  // Sort by virality score and apply filter
  const sortedItems = [...items]
    .filter(item => {
      if (filter === 'reddit') return item.source_platform === 'reddit'
      if (filter === 'youtube') return item.source_platform === 'youtube'
      return true // 'all'
    })
    .sort((a, b) => b.virality_score - a.virality_score)

  return (
    <div className="space-y-4">
      {/* Platform Stats */}
      <Card className="bg-white/5 border-white/10 p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-semibold text-white uppercase">Platform Breakdown</h3>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-3 bg-white/5 rounded-lg">
            <p className="text-2xl font-bold text-white">{totalPosts}</p>
            <p className="text-xs text-gray-400 mt-1">Total Memes</p>
          </div>
          <div className="text-center p-3 bg-orange-500/10 rounded-lg border border-orange-500/30">
            <p className="text-2xl font-bold text-orange-400">{redditCount}</p>
            <p className="text-xs text-orange-300 mt-1">Reddit Posts</p>
          </div>
          <div className="text-center p-3 bg-red-500/10 rounded-lg border border-red-500/30">
            <p className="text-2xl font-bold text-red-400">{youtubeCount}</p>
            <p className="text-xs text-red-300 mt-1">YouTube Videos</p>
          </div>
        </div>
      </Card>

      {/* Sentiment Overview */}
      <Card className="bg-white/5 border-white/10 p-5">
        <div className="flex items-center gap-2 mb-4">
          <Heart className="w-4 h-4 text-pink-400" />
          <h3 className="text-sm font-semibold text-white uppercase">Sentiment Overview</h3>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-3 bg-green-500/10 rounded-lg border border-green-500/30">
            <p className="text-2xl font-bold text-green-400">{sentimentCounts.positive || 0}</p>
            <p className="text-xs text-green-300 mt-1">Positive</p>
          </div>
          <div className="text-center p-3 bg-gray-500/10 rounded-lg border border-gray-500/30">
            <p className="text-2xl font-bold text-gray-400">{sentimentCounts.neutral || 0}</p>
            <p className="text-xs text-gray-300 mt-1">Neutral</p>
          </div>
          <div className="text-center p-3 bg-red-500/10 rounded-lg border border-red-500/30">
            <p className="text-2xl font-bold text-red-400">{sentimentCounts.negative || 0}</p>
            <p className="text-xs text-red-300 mt-1">Negative</p>
          </div>
        </div>
      </Card>

      {/* Memes Feed */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white uppercase">Trending Memes</h3>
          <Badge className="bg-purple-600/20 text-purple-300 border-purple-500/30 text-xs">
            {sortedItems.length} memes
          </Badge>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400 mr-2">Filter by platform:</span>
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
              All ({totalPosts})
            </Button>
            <Button
              variant={filter === 'reddit' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('reddit')}
              className={cn(
                "text-xs",
                filter === 'reddit' 
                  ? "bg-orange-600 hover:bg-orange-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              <MessageSquare className="w-3 h-3 mr-1" />
              Reddit ({redditCount})
            </Button>
            <Button
              variant={filter === 'youtube' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('youtube')}
              className={cn(
                "text-xs",
                filter === 'youtube' 
                  ? "bg-red-600 hover:bg-red-700 text-white" 
                  : "bg-white/5 text-gray-300 border-white/20 hover:bg-white/10"
              )}
            >
              <Video className="w-3 h-3 mr-1" />
              YouTube ({youtubeCount})
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedItems.map((item, index) => {
            const isReddit = item.source_platform === 'reddit'
            const isVideo = item.is_video || item.source_platform === 'youtube'

            return (
              <Card
                key={`${item.source_platform}-${index}`}
                className="bg-white/5 border-white/10 hover:bg-white/10 transition-colors group cursor-pointer"
                onClick={() => {
                  if (item.source_url) {
                    window.open(item.source_url, '_blank', 'noopener,noreferrer')
                  }
                }}
              >
                <div className="p-4 space-y-3">
                  {/* Header with platform badge */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge
                      variant="outline"
                      className={cn(
                        "text-xs border-white/20",
                        isReddit
                          ? "bg-orange-500/10 text-orange-400 border-orange-500/30"
                          : "bg-red-500/10 text-red-400 border-red-500/30"
                      )}
                    >
                      {isReddit ? (
                        <>
                          <MessageSquare className="w-3 h-3 mr-1" />
                          Reddit
                        </>
                      ) : (
                        <>
                          <Video className="w-3 h-3 mr-1" />
                          YouTube
                        </>
                      )}
                    </Badge>

                    {isReddit && item.source_name && (
                      <Badge variant="outline" className="text-xs bg-white/5 text-gray-300 border-gray-600">
                        r/{item.source_name}
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

                  {/* Media Preview */}
                  {(item.media?.thumbnail || item.media?.images?.[0]) && (
                    <div className="relative h-40 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg overflow-hidden">
                      <img
                        src={item.media.thumbnail || item.media.images?.[0]}
                        alt={item.title}
                        className="w-full h-full object-cover"
                      />
                      {isVideo && (
                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center group-hover:bg-black/30 transition-colors">
                          <div className="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center">
                            <Play className="w-6 h-6 text-white ml-1" fill="white" />
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Title */}
                  <h4 className="text-white text-sm font-medium leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                    {item.title}
                  </h4>

                  {/* Engagement Stats */}
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    {(item.engagement?.likes || 0) > 0 && (
                      <span className="flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        <span className="text-gray-400">{(item.engagement?.likes || 0).toLocaleString()}</span>
                      </span>
                    )}
                    {(item.engagement?.comments || 0) > 0 && (
                      <span className="flex items-center gap-1">
                        <MessageSquare className="w-3 h-3" />
                        <span className="text-gray-400">{(item.engagement?.comments || 0).toLocaleString()}</span>
                      </span>
                    )}
                    {(item.engagement?.shares || 0) > 0 && (
                      <span className="flex items-center gap-1">
                        <ExternalLink className="w-3 h-3" />
                        <span className="text-gray-400">{(item.engagement?.shares || 0).toLocaleString()}</span>
                      </span>
                    )}
                  </div>

                {/* Click hint */}
                {item.source_url && (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <ExternalLink className="w-3 h-3" />
                    <span className="truncate">Click card to view on {isReddit ? 'Reddit' : 'YouTube'}</span>
                  </div>
                )}
                </div>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}
